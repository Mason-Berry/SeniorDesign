import xarray as xr
import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime
import time
import argparse

# Setup logging with minimal output for array data
class LimitedArrayLogger(logging.Formatter):
    def format(self, record):
        msg = record.getMessage()
        if isinstance(msg, str) and len(msg) > 500:
            # Check if this is likely array data
            if ('[' in msg and ']' in msg) or ('array' in msg.lower()):
                # Truncate the content
                msg = msg[:200] + " ... [array data truncated] ... " + msg[-100:]
                record.args = ()
                record.msg = msg
        return super().format(record)

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(LimitedArrayLogger('%(asctime)s - %(levelname)s - %(message)s'))
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

def process_era5_variable(grib_file, output_dir, variable_name=None, 
                          compression=None, time_chunk_size=24,
                          remove_constant_cols=True, decimal_precision=None):
    """
    Process a single ERA5 variable from a GRIB file to CSV/Parquet with organized directory structure
    
    Args:
        grib_file: Path to GRIB file
        output_dir: Base directory to save output files
        variable_name: Specific variable to extract (shortName)
        compression: Compression to use (None, 'gzip', etc.)
        time_chunk_size: Size of time chunks to process
        remove_constant_cols: Whether to remove columns with constant values
        decimal_precision: Number of decimal places to keep for lat/lon coordinates
    """
    start_time = time.time()
    
    # Get base filename and extract year/month
    base_filename = os.path.splitext(os.path.basename(grib_file))[0]
    
    # Try to extract year and month from filename (assuming format like YYYYMM)
    try:
        year = base_filename[:4]
        month = base_filename[4:6]
        # Validate year and month are numeric
        int(year)
        int(month)
    except (ValueError, IndexError):
        logger.warning(f"Could not extract year/month from filename {base_filename}")
        # Default to current year/month if extraction fails
        current_date = datetime.now()
        year = str(current_date.year)
        month = f"{current_date.month:02d}"
    
    logger.info(f"Processing {grib_file} for year={year}, month={month}")
    
    # Attempt to load specific variable
    try:
        logger.info(f"Attempting to load {variable_name} from {grib_file}")
        backend_kwargs = {}
        
        # If specific variable is requested
        if variable_name:
            backend_kwargs['filter_by_keys'] = {'shortName': variable_name}
        
        # Set indexpath to empty to force re-indexing (helps with mixed dimensions)
        backend_kwargs['indexpath'] = ''
        
        # Open dataset - this only reads metadata until we access data
        ds = xr.open_dataset(grib_file, engine='cfgrib', backend_kwargs=backend_kwargs)
        
        # Log basic dataset info without printing arrays
        var_names = list(ds.data_vars)
        logger.info(f"Successfully opened dataset with variables: {var_names}")
        logger.info(f"Dimensions: {dict(ds.dims)}")
        
        # If we have multiple variables and want a specific one
        if variable_name and variable_name in var_names:
            var_data = ds[variable_name]
            process_variable_data(var_data, year, month, variable_name, output_dir, 
                                 compression, time_chunk_size, remove_constant_cols, decimal_precision)
        # If we loaded a dataset with a single variable
        elif len(var_names) == 1:
            var_name = var_names[0]
            var_data = ds[var_name]
            # Get the actual shortName from attributes if available
            short_name = var_data.attrs.get('GRIB_shortName', 
                                           var_data.attrs.get('shortName', var_name))
            process_variable_data(var_data, year, month, short_name, output_dir, 
                                 compression, time_chunk_size, remove_constant_cols, decimal_precision)
        # Multiple variables loaded
        else:
            logger.warning(f"Multiple variables found: {var_names}, but no specific variable requested")
            # Process each variable in the dataset
            for var_name in var_names:
                var_data = ds[var_name]
                # Get the actual shortName from attributes
                short_name = var_data.attrs.get('GRIB_shortName', 
                                              var_data.attrs.get('shortName', var_name))
                process_variable_data(var_data, year, month, short_name, output_dir, 
                                     compression, time_chunk_size, remove_constant_cols, decimal_precision)
        
        # Close dataset
        ds.close()
        
        end_time = time.time()
        logger.info(f"Completed processing in {end_time - start_time:.2f} seconds")
        return True
    
    except Exception as e:
        logger.error(f"Error processing {variable_name}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def process_variable_data(var_data, year, month, var_name, output_dir, 
                          compression, time_chunk_size, remove_constant_cols, decimal_precision):
    """Process a single variable's data with organized directory structure"""
    # Create output directory structure: output_dir/year/month/variable/
    var_output_dir = os.path.join(output_dir, year, month, var_name)
    os.makedirs(var_output_dir, exist_ok=True)
    
    # Check for time dimension
    if 'time' in var_data.dims:
        time_dim = 'time'
    elif 'time1' in var_data.dims:
        time_dim = 'time1'
    elif 'time2' in var_data.dims:
        time_dim = 'time2'
    else:
        # No time dimension found
        logger.warning(f"No time dimension found in {var_name}")
        time_dim = None
    
    # Process data by time chunks if time dimension exists
    if time_dim:
        time_steps = len(var_data[time_dim])
        logger.info(f"Variable {var_name} has {time_steps} time steps in dimension {time_dim}")
        
        # Process in time chunks
        for i in range(0, time_steps, time_chunk_size):
            chunk_start = i
            chunk_end = min(i + time_chunk_size, time_steps)
            
            # Select time slice
            chunk_selector = {time_dim: slice(chunk_start, chunk_end)}
            chunk_data = var_data.isel(**chunk_selector)
            
            # Convert to DataFrame - this will flatten the data properly
            df = chunk_data.to_dataframe().reset_index()
            
            # Print shape and columns without printing the data
            logger.info(f"Created DataFrame with shape {df.shape}")
            logger.info(f"Columns: {', '.join(df.columns)}")
            
            # Round latitude and longitude columns if precision specified
            if decimal_precision is not None:
                round_coordinates(df, decimal_precision)
            
            # Print time range if time column exists
            if time_dim in df.columns:
                min_time = df[time_dim].min()
                max_time = df[time_dim].max()
                logger.info(f"Time range: {min_time} to {max_time}")
            
            # Check and remove constant columns if requested
            if remove_constant_cols:
                cols_to_check = ['number', 'step', 'surface']
                cols_to_remove = []
                
                for col in cols_to_check:
                    if col in df.columns and df[col].nunique() == 1:
                        cols_to_remove.append(col)
                
                if cols_to_remove:
                    logger.info(f"Removing constant columns: {', '.join(cols_to_remove)}")
                    df = df.drop(columns=cols_to_remove)
            
            # Rename the variable column if needed
            if var_name in df.columns:
                df = df.rename(columns={var_name: 'value'})
            
            # Save chunk with organized filename
            output_filename = f"{year}{month}_{var_name}_chunk_{chunk_start}_{chunk_end}.csv"
            output_path = os.path.join(var_output_dir, output_filename)
            df.to_csv(output_path, index=False, compression=compression)
            
            # Log file size
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            logger.info(f"Saved chunk to {output_path} ({file_size_mb:.2f} MB)")
            
            # Clear memory
            del df
    else:
        # No time dimension, save entire variable
        df = var_data.to_dataframe().reset_index()
        
        logger.info(f"Created DataFrame with shape {df.shape}")
        logger.info(f"Columns: {', '.join(df.columns)}")
        
        # Round latitude and longitude columns if precision specified
        if decimal_precision is not None:
            round_coordinates(df, decimal_precision)
        
        # Check and remove constant columns if requested
        if remove_constant_cols:
            cols_to_check = ['number', 'step', 'surface']
            cols_to_remove = []
            
            for col in cols_to_check:
                if col in df.columns and df[col].nunique() == 1:
                    cols_to_remove.append(col)
            
            if cols_to_remove:
                logger.info(f"Removing constant columns: {', '.join(cols_to_remove)}")
                df = df.drop(columns=cols_to_remove)
        
        # Rename the variable column if needed
        if var_name in df.columns:
            df = df.rename(columns={var_name: 'value'})
        
        # Save data
        output_filename = f"{year}{month}_{var_name}.csv"
        output_path = os.path.join(var_output_dir, output_filename)
        df.to_csv(output_path, index=False, compression=compression)
        
        # Log file size
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"Saved to {output_path} ({file_size_mb:.2f} MB)")
        
        # Clear memory
        del df

def round_coordinates(df, decimal_precision):
    """
    Round latitude and longitude coordinates to specified precision to reduce file size
    
    Args:
        df: DataFrame containing coordinates
        decimal_precision: Number of decimal places to keep
    """
    # List of possible latitude and longitude column names
    lat_cols = ['latitude', 'lat', 'Latitude', 'Lat']
    lon_cols = ['longitude', 'lon', 'Longitude', 'Lon']
    
    # Round latitude columns if found
    for col in lat_cols:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            original_size = df[col].memory_usage(deep=True)
            df[col] = df[col].round(decimal_precision)
            new_size = df[col].memory_usage(deep=True)
            reduction = (original_size - new_size) / original_size * 100 if original_size > 0 else 0
            logger.info(f"Rounded {col} to {decimal_precision} decimal places. "
                       f"Memory reduction: {reduction:.2f}%")
    
    # Round longitude columns if found
    for col in lon_cols:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            original_size = df[col].memory_usage(deep=True)
            df[col] = df[col].round(decimal_precision)
            new_size = df[col].memory_usage(deep=True)
            reduction = (original_size - new_size) / original_size * 100 if original_size > 0 else 0
            logger.info(f"Rounded {col} to {decimal_precision} decimal places. "
                       f"Memory reduction: {reduction:.2f}%")
    
    return df

def discover_variables(grib_file):
    """
    Discover all variables in a GRIB file without loading data
    
    Returns a list of shortNames if possible
    """
    try:
        # First try using xarray to discover variables
        ds = xr.open_dataset(grib_file, engine='cfgrib', 
                            backend_kwargs={'indexpath': ''})
        variables = []
        
        # Extract shortName from variable attributes
        for var_name in ds.data_vars:
            var_data = ds[var_name]
            short_name = var_data.attrs.get('GRIB_shortName', 
                                          var_data.attrs.get('shortName', var_name))
            variables.append(short_name)
        
        ds.close()
        
        # Return unique variable names
        return list(set(variables))
    except Exception as e:
        logger.error(f"Error discovering variables with xarray: {e}")
        
        try:
            # Try using ncdump if available
            import subprocess
            result = subprocess.run(['ncdump', '-h', grib_file], 
                                  capture_output=True, text=True)
            
            # This is a simple regex approach - not fully robust
            import re
            variables = re.findall(r':Grib1_Parameter_Name = "([^"]+)"', result.stdout)
            
            return list(set(variables))  # Return unique variable names
        except Exception as e2:
            logger.error(f"Error discovering variables with ncdump: {e2}")
            
            # Fallback to common ERA5 variable names
            return [
                'sp',   # Surface pressure
                'tp',   # Total precipitation
                'tcc',  # Total cloud cover
                '10u',  # 10m U wind component
                '10v',  # 10m V wind component
                '2t',   # 2m temperature
                '2d',   # 2m dewpoint temperature
                'cape', # Convective available potential energy
                'lsp',  # Large-scale precipitation
                'cp',   # Convective precipitation
                'cin',  # Convective inhibition
                'lcc',  # Low cloud cover
                'mcc',  # Medium cloud cover
                'hcc',  # High cloud cover
                'vimd', # Vertically integrated moisture divergence
                'tclw', # Total column liquid water
                'tciw', # Total column ice water
                'vit',  # Vertical integral of temperature
                'vike', # Vertical integral of kinetic energy
                'vitoe',# Vertical integral of total energy
                'cbh',  # Cloud base height
                '100u', # 100m U wind component
                '100v', # 100m V wind component
                'i10fg',# Instantaneous 10m wind gust
                '10fg', # 10m wind gust
            ]

def process_era5_file(grib_file, output_dir, variables=None, exclude_variables=None,
                     compression=None, time_chunk_size=24,
                     remove_constant_cols=True, decimal_precision=None):
    """
    Process an ERA5 GRIB file by extracting each variable separately
    
    Args:
        grib_file: Path to GRIB file
        output_dir: Base directory to save output files
        variables: List of variables to extract (if None, discover all variables)
        exclude_variables: List of variables to exclude from processing
        compression: Compression to use (None, 'gzip', etc.)
        time_chunk_size: Size of time chunks to process
        remove_constant_cols: Whether to remove columns with constant values
        decimal_precision: Number of decimal places for lat/lon coordinates
    """
    start_time = time.time()
    logger.info(f"Processing ERA5 file: {grib_file}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Discover all variables if none provided
    all_variables = None
    if variables is None or exclude_variables is not None:
        try:
            from netCDF4 import Dataset
            # Try using netCDF4 to discover variables
            with Dataset(grib_file) as nc:
                all_variables = list(nc.variables.keys())
                # Filter out dimension variables
                dimensions = list(nc.dimensions.keys())
                all_variables = [v for v in all_variables if v not in dimensions]
                logger.info(f"Discovered {len(all_variables)} variables: {all_variables}")
        except Exception:
            # Fall back to alternative discovery methods
            all_variables = discover_variables(grib_file)
            logger.info(f"Using discovered variables: {all_variables}")
    
    # Determine which variables to process based on include/exclude lists
    if variables is None:
        # Use all discovered variables if no specific variables requested
        variables_to_process = all_variables
    else:
        # Use only specified variables
        variables_to_process = variables
    
    # Apply exclusion list if provided
    if exclude_variables is not None and variables_to_process is not None:
        original_count = len(variables_to_process)
        variables_to_process = [v for v in variables_to_process if v not in exclude_variables]
        excluded_count = original_count - len(variables_to_process)
        logger.info(f"Excluded {excluded_count} variables: {exclude_variables}")
    
    if not variables_to_process:
        logger.warning("No variables to process after applying include/exclude filters")
        return [], []
    
    # Process each variable separately
    successful = []
    failed = []
    
    for var_name in variables_to_process:
        logger.info(f"Processing variable: {var_name}")
        success = process_era5_variable(
            grib_file, output_dir, var_name, compression, time_chunk_size, 
            remove_constant_cols, decimal_precision
        )
        
        if success:
            successful.append(var_name)
        else:
            failed.append(var_name)
    
    # Log summary
    end_time = time.time()
    logger.info(f"Processing completed in {end_time - start_time:.2f} seconds")
    logger.info(f"Successfully processed: {successful}")
    if failed:
        logger.warning(f"Failed to process: {failed}")
    
    return successful, failed

def convert_directory_to_parquet(csv_dir, remove_csv=False):
    """
    Convert all CSV files in a directory structure to Parquet format
    
    Args:
        csv_dir: Base directory containing CSV files
        remove_csv: Whether to remove original CSV files after conversion
    """
    import glob
    
    # Find all CSV files
    csv_files = glob.glob(os.path.join(csv_dir, "**/*.csv"), recursive=True)
    
    if not csv_files:
        logger.warning(f"No CSV files found in {csv_dir}")
        return
    
    logger.info(f"Found {len(csv_files)} CSV files to convert to Parquet")
    
    # Process each file
    for csv_file in csv_files:
        parquet_file = csv_file.replace('.csv', '.parquet')
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file)
            
            # Convert to Parquet
            df.to_parquet(parquet_file, index=False)
            
            # Log file sizes
            csv_size_mb = os.path.getsize(csv_file) / (1024 * 1024)
            parquet_size_mb = os.path.getsize(parquet_file) / (1024 * 1024)
            compression_ratio = csv_size_mb / parquet_size_mb if parquet_size_mb > 0 else 0
            
            logger.info(f"Converted {csv_file} ({csv_size_mb:.2f} MB) to {parquet_file} "
                       f"({parquet_size_mb:.2f} MB), compression ratio: {compression_ratio:.2f}x")
            
            # Remove original CSV if requested
            if remove_csv:
                os.remove(csv_file)
                logger.info(f"Removed original CSV file: {csv_file}")
        
        except Exception as e:
            logger.error(f"Error converting {csv_file} to Parquet: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert ERA5 GRIB file to CSV/Parquet files with organized directory structure")
    parser.add_argument("--input", required=True, help="Input GRIB file")
    parser.add_argument("--output", required=True, help="Output base directory")
    parser.add_argument("--variables", nargs='+', help="Variables to extract (space-separated)")
    parser.add_argument("--exclude-variables", nargs='+', help="Variables to exclude from processing (space-separated)")
    parser.add_argument("--compress", choices=['gzip', 'bz2', 'zip', 'xz'], 
                        help="Compress CSV files")
    parser.add_argument("--chunk", type=int, default=24, help="Time chunk size (hours)")
    parser.add_argument("--keep-constants", action="store_true", 
                        help="Keep constant columns like number, step, surface")
    parser.add_argument("--parquet", action="store_true",
                        help="Convert to Parquet format after CSV creation")
    parser.add_argument("--remove-csv", action="store_true",
                        help="Remove CSV files after Parquet conversion")
    parser.add_argument("--decimal-precision", type=int, default=None,
                        help="Number of decimal places to keep for latitude/longitude coordinates")
    
    args = parser.parse_args()
    
    # Process the GRIB file
    process_era5_file(
        args.input, 
        args.output, 
        variables=args.variables,
        exclude_variables=args.exclude_variables,
        compression=args.compress,
        time_chunk_size=args.chunk,
        remove_constant_cols=not args.keep_constants,
        decimal_precision=args.decimal_precision
    )
    
    # Convert to Parquet if requested
    if args.parquet:
        convert_directory_to_parquet(args.output, remove_csv=args.remove_csv)
