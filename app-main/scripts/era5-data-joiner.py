import os
import glob
import pandas as pd
import numpy as np
import argparse
from datetime import datetime
import logging
import time
import gc  # For explicit garbage collection

# Setup logging
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

# Variables to exclude (those that don't have values at all common timeframes)
DEFAULT_EXCLUDE_VARS = ['10fg', 'cbh', 'cin', 'cp', 'i10fg', 'lsp', 'tp', 'vimd']


def find_csv_files(base_dir, year=None, month=None):
    """
    Find all CSV files in the directory structure

    Args:
        base_dir: Base directory to search
        year: Specific year to filter (optional)
        month: Specific month to filter (optional)

    Returns:
        Dictionary mapping variable names to lists of file paths
    """
    # Build the search pattern based on provided filters
    if year and month:
        search_pattern = os.path.join(base_dir, str(year), str(month).zfill(2), "**", "*.csv")
    elif year:
        search_pattern = os.path.join(base_dir, str(year), "**", "*.csv")
    else:
        search_pattern = os.path.join(base_dir, "**", "*.csv")

    # Find all CSV files
    csv_files = glob.glob(search_pattern, recursive=True)
    logger.info(f"Found {len(csv_files)} CSV files in {base_dir}")

    # Group files by variable
    var_files = {}
    for file_path in csv_files:
        # Extract variable name from directory structure
        # Assuming path structure: base_dir/year/month/variable/files.csv
        parts = os.path.normpath(file_path).split(os.sep)
        if len(parts) >= 4:  # Ensure we have enough parts to extract variable
            var_name = parts[-2]  # Variable name is the directory name
            if var_name not in var_files:
                var_files[var_name] = []
            var_files[var_name].append(file_path)

    return var_files


def inspect_file_structure(file_path):
    """
    Inspect a file to determine its column structure and identify value column

    Args:
        file_path: Path to the CSV file

    Returns:
        Dictionary with column mapping information
    """
    try:
        # Read just a few rows to get column structure
        df_sample = pd.read_csv(file_path, nrows=5)
        columns = list(df_sample.columns)

        # Log the columns for debugging
        logger.debug(f"Columns in {file_path}: {columns}")

        # Try to identify key columns
        time_cols = [col for col in columns if col.lower() in ['time', 'time1', 'time2']]
        lat_cols = [col for col in columns if col.lower() in ['latitude', 'lat']]
        lon_cols = [col for col in columns if col.lower() in ['longitude', 'lon']]

        # Identify the variable/value column - more robust approach
        var_name = os.path.basename(os.path.dirname(file_path))  # Get variable from directory name

        # Look for variable name in columns, or "value" column
        value_col = None
        if 'value' in columns:
            value_col = 'value'
        # Try common variable column naming patterns
        elif var_name in columns:
            value_col = var_name
        elif var_name.lower() in columns:
            value_col = var_name.lower()
        # Check for common meteorological variable naming patterns
        elif f'{var_name}m' in columns:  # e.g., t2m for 2t
            value_col = f'{var_name}m'
        elif var_name[::-1] in columns:  # e.g., u10 for 10u
            value_col = var_name[::-1]
        else:
            # Try to find a column that's not time, lat, lon, or common metadata
            common_meta_cols = ['number', 'step', 'surface', 'valid_time', 'level']
            potential_value_cols = [col for col in columns
                                    if col not in time_cols + lat_cols + lon_cols + common_meta_cols]

            if potential_value_cols:
                # Typically the last remaining column is the value
                value_col = potential_value_cols[-1]
                logger.debug(f"Using {value_col} as value column for {var_name}")

        return {
            'time_col': time_cols[0] if time_cols else None,
            'lat_col': lat_cols[0] if lat_cols else None,
            'lon_col': lon_cols[0] if lon_cols else None,
            'value_col': value_col,
            'all_columns': columns
        }
    except Exception as e:
        logger.error(f"Error inspecting file {file_path}: {e}")
        return None


def get_variable_metadata(var_files):
    """
    Extract metadata for each variable to understand data structure

    Args:
        var_files: Dictionary mapping variable names to lists of file paths

    Returns:
        Dictionary with metadata for each variable
    """
    var_metadata = {}

    for var_name, files in var_files.items():
        if not files:
            continue

        # Sample the first file for this variable
        sample_file = files[0]
        try:
            # Inspect the file structure
            structure = inspect_file_structure(sample_file)
            if not structure:
                logger.warning(f"Could not determine structure for {var_name}, skipping")
                continue

            # Store metadata
            var_metadata[var_name] = {
                'columns': structure['all_columns'],
                'time_col': structure['time_col'],
                'lat_col': structure['lat_col'],
                'lon_col': structure['lon_col'],
                'value_col': structure['value_col'],
                'sample_file': sample_file
            }

            logger.info(f"Variable {var_name}: Time={structure['time_col']}, "
                        f"Lat={structure['lat_col']}, Lon={structure['lon_col']}, "
                        f"Value={structure['value_col']}")

        except Exception as e:
            logger.error(f"Error reading sample file for {var_name}: {e}")

    return var_metadata


def identify_join_columns(var_metadata):
    """
    Identify the common columns to use for joining datasets

    Args:
        var_metadata: Dictionary with metadata for each variable

    Returns:
        Dictionary specifying the join columns for time, latitude, and longitude
    """
    # Initialize with default column names
    join_cols = {
        'time': 'time',
        'lat': 'latitude',
        'lon': 'longitude'
    }

    # Get a list of all time, lat, and lon columns across variables
    all_time_cols = [meta['time_col'] for meta in var_metadata.values() if meta.get('time_col')]
    all_lat_cols = [meta['lat_col'] for meta in var_metadata.values() if meta.get('lat_col')]
    all_lon_cols = [meta['lon_col'] for meta in var_metadata.values() if meta.get('lon_col')]

    # Count occurrences of each column name
    time_counts = {}
    for col in all_time_cols:
        time_counts[col] = time_counts.get(col, 0) + 1

    lat_counts = {}
    for col in all_lat_cols:
        lat_counts[col] = lat_counts.get(col, 0) + 1

    lon_counts = {}
    for col in all_lon_cols:
        lon_counts[col] = lon_counts.get(col, 0) + 1

    # Select the most common column names
    if time_counts:
        join_cols['time'] = max(time_counts.items(), key=lambda x: x[1])[0]
    if lat_counts:
        join_cols['lat'] = max(lat_counts.items(), key=lambda x: x[1])[0]
    if lon_counts:
        join_cols['lon'] = max(lon_counts.items(), key=lambda x: x[1])[0]

    logger.info(f"Using join columns: {join_cols}")
    return join_cols


def join_data_incrementally(var_files, var_metadata, excluded_vars, join_cols, output_file,
                            chunk_size=100000, time_filter=None, include_vars=None,
                            max_rows_in_memory=1000000):
    """
    Join data from multiple variables incrementally to minimize memory usage

    Args:
        var_files: Dictionary mapping variable names to lists of file paths
        var_metadata: Dictionary with metadata for each variable
        excluded_vars: List of variables to exclude
        join_cols: Dictionary specifying the join columns
        output_file: Path to save the joined data
        chunk_size: Number of rows to process at once in each file
        time_filter: Optional function to filter timestamps
        include_vars: Optional list of variables to include
        max_rows_in_memory: Maximum rows to hold in memory before writing to disk
    """
    start_time = time.time()

    # Filter variables if include_vars is specified
    if include_vars is not None:
        var_files = {var: files for var, files in var_files.items() if var in include_vars}
        logger.info(f"Filtered to include only variables: {list(var_files.keys())}")

    # Remove excluded variables
    var_files = {var: files for var, files in var_files.items() if var not in excluded_vars}
    logger.info(f"Processing variables: {list(var_files.keys())}")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

    # Create intermediate directory for temp files
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(output_file)), "temp_joins")
    os.makedirs(temp_dir, exist_ok=True)

    # Process each variable separately into its own intermediate file
    var_output_files = {}

    for var_name, files in var_files.items():
        if var_name not in var_metadata:
            logger.warning(f"No metadata for variable: {var_name}")
            continue

        meta = var_metadata[var_name]
        logger.info(f"Processing variable: {var_name} with {len(files)} files")

        # Check if we have all necessary columns
        if not meta.get('time_col') or not meta.get('lat_col') or not meta.get('lon_col'):
            logger.warning(f"Variable {var_name} missing coordinate columns, skipping")
            continue

        if not meta.get('value_col'):
            logger.warning(f"Variable {var_name} missing value column, skipping")
            continue

        # Create intermediate file path
        var_output_file = os.path.join(temp_dir, f"{var_name}_data.csv")
        var_output_files[var_name] = var_output_file

        # Initialize a list to hold data chunks
        all_chunks = []
        total_rows = 0

        # Process each file for this variable
        for i, file_path in enumerate(files):
            try:
                # Read file
                df = pd.read_csv(file_path)

                # Verify the file has expected columns
                time_col = meta['time_col']
                lat_col = meta['lat_col']
                lon_col = meta['lon_col']
                value_col = meta['value_col']

                if time_col not in df.columns or lat_col not in df.columns or lon_col not in df.columns:
                    # Try to auto-detect columns in this specific file
                    file_structure = inspect_file_structure(file_path)
                    if file_structure:
                        time_col = file_structure['time_col'] or time_col
                        lat_col = file_structure['lat_col'] or lat_col
                        lon_col = file_structure['lon_col'] or lon_col
                        value_col = file_structure['value_col'] or value_col

                if time_col not in df.columns or lat_col not in df.columns or lon_col not in df.columns:
                    logger.warning(f"File {file_path} missing coordinate columns, skipping")
                    continue

                if value_col not in df.columns:
                    # Try to find an alternative value column
                    common_cols = [time_col, lat_col, lon_col, 'number', 'step', 'surface']
                    potential_val_cols = [col for col in df.columns if col not in common_cols]

                    if potential_val_cols:
                        value_col = potential_val_cols[-1]  # Use the last column as value
                        logger.info(f"Using alternative value column {value_col} for {var_name} in {file_path}")
                    else:
                        logger.warning(f"File {file_path} has no suitable value column, skipping")
                        continue

                # Select only required columns
                df = df[[time_col, lat_col, lon_col, value_col]].copy()

                # Apply time filter if provided
                if time_filter:
                    df = df[time_filter(df[time_col])].copy()

                # Rename columns for consistency
                rename_map = {
                    time_col: 'time',
                    lat_col: 'latitude',
                    lon_col: 'longitude',
                    value_col: 'value'  # Temporarily use 'value' as column name
                }
                df.rename(columns=rename_map, inplace=True)

                # Process DataFrame in chunks to save memory
                for chunk_start in range(0, len(df), chunk_size):
                    chunk_end = min(chunk_start + chunk_size, len(df))
                    df_chunk = df.iloc[chunk_start:chunk_end].copy()

                    # Add to the collection
                    all_chunks.append(df_chunk)
                    total_rows += len(df_chunk)

                    # Check if we need to write to disk
                    if total_rows >= max_rows_in_memory:
                        # Combine chunks
                        combined_df = pd.concat(all_chunks, ignore_index=True)

                        # Write to CSV, appending if file exists
                        if os.path.exists(var_output_file):
                            # Append without header
                            combined_df.to_csv(var_output_file, mode='a', header=False, index=False)
                        else:
                            # First write with header
                            combined_df.to_csv(var_output_file, index=False)

                        # Reset
                        all_chunks = []
                        total_rows = 0
                        del combined_df
                        gc.collect()  # Force garbage collection

                # Log progress periodically
                if (i + 1) % 10 == 0 or i == len(files) - 1:
                    logger.info(f"  Processed {i + 1}/{len(files)} files for {var_name}")

                # Clear memory
                del df
                gc.collect()  # Force garbage collection

            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                continue

        # Save any remaining chunks
        if all_chunks:
            combined_df = pd.concat(all_chunks, ignore_index=True)

            # Write to CSV, appending if file exists
            if os.path.exists(var_output_file):
                # Append without header
                combined_df.to_csv(var_output_file, mode='a', header=False, index=False)
            else:
                # First write with header
                combined_df.to_csv(var_output_file, index=False)

            # Clear memory
            del combined_df
            del all_chunks
            gc.collect()

    # Now merge all variable files into the final output
    logger.info("Merging all variable files into final output...")

    # First, create a base DataFrame with common coordinates by pulling a sample from one variable
    if not var_output_files:
        logger.error("No variable data to merge!")
        return False

    # Use the first variable as the base for coordinates
    base_var = next(iter(var_output_files.keys()))
    base_file = var_output_files[base_var]

    if not os.path.exists(base_file):
        logger.error(f"Base variable file {base_file} does not exist!")
        return False

    # Load only the coordinate columns from the base file
    try:
        # Read in chunks to save memory
        chunk_size = max_rows_in_memory
        base_chunks = []

        # Use pandas chunking to read large files
        for chunk in pd.read_csv(base_file, usecols=['time', 'latitude', 'longitude'], chunksize=chunk_size):
            base_chunks.append(chunk[['time', 'latitude', 'longitude']])

        # Combine chunks and drop duplicates
        base_df = pd.concat(base_chunks, ignore_index=True)
        base_df = base_df.drop_duplicates(['time', 'latitude', 'longitude'])
        logger.info(f"Created base coordinate frame with {len(base_df)} unique points")

        # Process each variable file and merge with base
        for var_name, var_file in var_output_files.items():
            if not os.path.exists(var_file):
                logger.warning(f"Variable file {var_file} does not exist, skipping")
                continue

            logger.info(f"Merging {var_name} data...")

            try:
                # Process variable data in chunks
                var_chunks = []
                for chunk in pd.read_csv(var_file, chunksize=chunk_size):
                    # Rename the value column to the variable name
                    chunk = chunk.rename(columns={'value': var_name})
                    var_chunks.append(chunk[['time', 'latitude', 'longitude', var_name]])

                # Combine variable chunks
                var_df = pd.concat(var_chunks, ignore_index=True)

                # Merge with base DataFrame on coordinates
                base_df = pd.merge(
                    base_df,
                    var_df,
                    on=['time', 'latitude', 'longitude'],
                    how='left'
                )

                logger.info(f"Added {var_name} data to merged dataset")

                # Clear memory
                del var_df
                del var_chunks
                gc.collect()

            except Exception as e:
                logger.error(f"Error merging {var_name}: {e}")
                import traceback
                logger.error(traceback.format_exc())

        # Save the final merged dataset
        logger.info(f"Saving final merged dataset to {output_file}...")

        # Determine file format based on extension
        file_ext = os.path.splitext(output_file)[1].lower()

        # Save in smaller chunks to reduce memory usage
        if file_ext == '.parquet':
            base_df.to_parquet(output_file, engine='pyarrow', index=False)
        elif file_ext == '.csv':
            # Write CSV in chunks
            chunk_size = max_rows_in_memory
            for i in range(0, len(base_df), chunk_size):
                chunk = base_df.iloc[i:i + chunk_size]
                # First chunk includes header, others don't
                if i == 0:
                    chunk.to_csv(output_file, index=False)
                else:
                    chunk.to_csv(output_file, mode='a', header=False, index=False)
        else:
            # Default to CSV if extension not recognized
            logger.warning(f"Unrecognized file extension: {file_ext}, saving as CSV")
            # Write CSV in chunks
            chunk_size = max_rows_in_memory
            for i in range(0, len(base_df), chunk_size):
                chunk = base_df.iloc[i:i + chunk_size]
                # First chunk includes header, others don't
                if i == 0:
                    chunk.to_csv(output_file, index=False)
                else:
                    chunk.to_csv(output_file, mode='a', header=False, index=False)

        # Report file size
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        logger.info(f"Final output file size: {file_size_mb:.2f} MB")

        # Clean up temp files
        logger.info("Cleaning up temporary files...")
        for var_file in var_output_files.values():
            if os.path.exists(var_file):
                os.remove(var_file)

        # Try to remove temp directory
        try:
            os.rmdir(temp_dir)
        except:
            pass  # Ignore errors if directory not empty

        end_time = time.time()
        logger.info(f"Join operation completed in {end_time - start_time:.2f} seconds")
        logger.info(f"Final dataset has {len(base_df)} rows and {len(base_df.columns)} columns")

        return True

    except Exception as e:
        logger.error(f"Error in final merge: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    parser = argparse.ArgumentParser(description="Join ERA5 data from multiple CSV/Parquet files")
    parser.add_argument("--input", required=True, help="Input directory containing ERA5 data files")
    parser.add_argument("--output", required=True, help="Output file path (.csv or .parquet)")
    parser.add_argument("--year", type=str, help="Specific year to process")
    parser.add_argument("--month", type=str, help="Specific month to process")
    parser.add_argument("--exclude-vars", nargs='+', default=DEFAULT_EXCLUDE_VARS,
                        help=f"Variables to exclude (default: {DEFAULT_EXCLUDE_VARS})")
    parser.add_argument("--include-vars", nargs='+',
                        help="Only include these variables (if specified, --exclude-vars is ignored)")
    parser.add_argument("--chunk-size", type=int, default=100000,
                        help="Number of rows to process at once (default: 100000)")
    parser.add_argument("--max-memory-rows", type=int, default=1000000,
                        help="Maximum rows to hold in memory before writing to disk (default: 1000000)")

    args = parser.parse_args()

    # Find all CSV files
    var_files = find_csv_files(args.input, args.year, args.month)

    if not var_files:
        logger.error(f"No files found in {args.input}")
        return

    # Get metadata for each variable
    var_metadata = get_variable_metadata(var_files)

    # Identify join columns
    join_cols = identify_join_columns(var_metadata)

    # Determine variables to process
    excluded_vars = []
    include_vars = None

    if args.include_vars:
        # If include_vars is specified, use it exclusively
        include_vars = args.include_vars
        logger.info(f"Only including variables: {include_vars}")
    else:
        # Otherwise, use the exclude list
        excluded_vars = args.exclude_vars
        logger.info(f"Excluding variables: {excluded_vars}")

    # Join the data incrementally
    join_data_incrementally(
        var_files=var_files,
        var_metadata=var_metadata,
        excluded_vars=excluded_vars,
        join_cols=join_cols,
        output_file=args.output,
        chunk_size=args.chunk_size,
        max_rows_in_memory=args.max_memory_rows,
        include_vars=include_vars
    )


if __name__ == "__main__":
    main()