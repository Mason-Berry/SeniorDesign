#!/usr/bin/env python3

import os
import glob
import argparse
import logging
import subprocess
import time
from datetime import datetime
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
import re
import pandas as pd
import gc

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

# Default variables to exclude (those that don't have values at all common timeframes)
DEFAULT_EXCLUDE_VARS = ['10fg', 'cbh', 'cin', 'cp', 'i10fg', 'lsp', 'tp', 'vimd']


def setup_logging(log_dir, prefix):
    """Setup logging to both console and file"""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{prefix}_{timestamp}.log")

    # File handler for logging to file
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Add file handler to root logger
    logging.getLogger().addHandler(file_handler)

    logger.info(f"Logging to {log_file}")
    return log_file


def find_grib_files(input_dir, year_range=None):
    """
    Find all GRIB files in the input directory, optionally filtered by year range

    Args:
        input_dir: Directory containing GRIB files
        year_range: Tuple of (start_year, end_year) to filter files

    Returns:
        List of tuples (filepath, year, month) sorted by year and month
    """
    # Common GRIB file extensions
    grib_extensions = ['.grib', '.grb', '.grib2', '.grb2']

    # Find all files with GRIB extensions
    grib_files = []
    for ext in grib_extensions:
        grib_files.extend(glob.glob(os.path.join(input_dir, f"**/*{ext}"), recursive=True))

    logger.info(f"Found {len(grib_files)} total GRIB files in {input_dir}")

    # Process file information
    file_info = []

    # Common ERA5 filename patterns for year/month extraction
    # Pattern like YYYYMM_variable.grib or YYYYMM.grib
    basic_pattern = re.compile(r'(\d{4})(\d{2})')

    # Pattern like ERA5_YYYYMM.grib or era5_YYYY_MM.grib
    era5_pattern = re.compile(r'era5[_-](\d{4})[_-]?(\d{2})', re.IGNORECASE)

    for filepath in grib_files:
        filename = os.path.basename(filepath)
        year = None
        month = None

        # Try to extract year and month from filename
        basic_match = basic_pattern.search(filename)
        era5_match = era5_pattern.search(filename)

        if basic_match:
            year = int(basic_match.group(1))
            month = int(basic_match.group(2))
        elif era5_match:
            year = int(era5_match.group(1))
            month = int(era5_match.group(2))
        else:
            # If we can't extract from filename, try to get from directory structure
            parts = os.path.normpath(filepath).split(os.sep)
            for i, part in enumerate(parts[:-1]):  # Skip the filename
                if part.isdigit() and len(part) == 4:  # Potential year
                    year = int(part)
                    # Check if next part could be month
                    if i + 1 < len(parts) - 1 and parts[i + 1].isdigit() and 1 <= int(parts[i + 1]) <= 12:
                        month = int(parts[i + 1])
                    break

        # If we still don't have year/month, log a warning and skip
        if year is None or month is None:
            logger.warning(f"Could not determine year/month for {filepath}, skipping")
            continue

        # Filter by year range if specified
        if year_range and (year < year_range[0] or year > year_range[1]):
            continue

        file_info.append((filepath, year, month))

    # Sort by year and month
    file_info.sort(key=lambda x: (x[1], x[2]))

    logger.info(f"Found {len(file_info)} GRIB files matching criteria")
    return file_info


def run_converter(converter_script, grib_file, output_dir, variables=None, exclude_variables=None,
                  decimal_precision=None, compress=None, parquet=False, remove_csv=False):
    """
    Run the ERA5 converter script on a GRIB file

    Args:
        converter_script: Path to the converter script
        grib_file: Path to the GRIB file
        output_dir: Output directory for processed data
        variables: List of variables to include
        exclude_variables: List of variables to exclude
        decimal_precision: Decimal precision for lat/lon
        compress: Compression format
        parquet: Whether to convert to parquet
        remove_csv: Whether to remove CSV files after Parquet conversion

    Returns:
        Tuple of (success, log_output)
    """
    cmd = [sys.executable, converter_script, "--input", grib_file, "--output", output_dir]

    if variables:
        cmd.extend(["--variables"] + variables)

    if exclude_variables:
        cmd.extend(["--exclude-variables"] + exclude_variables)

    if decimal_precision is not None:
        cmd.extend(["--decimal-precision", str(decimal_precision)])

    if compress:
        cmd.extend(["--compress", compress])

    if parquet:
        cmd.append("--parquet")

    if remove_csv and parquet:
        cmd.append("--remove-csv")

    logger.info(f"Running converter: {' '.join(cmd)}")

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

        log_output = []
        for line in process.stdout:
            log_output.append(line.strip())

        process.wait()

        success = process.returncode == 0

        if success:
            logger.info(f"Converter completed successfully for {grib_file}")
        else:
            logger.error(f"Converter failed for {grib_file} with return code {process.returncode}")

        return success, log_output

    except Exception as e:
        logger.error(f"Error running converter for {grib_file}: {e}")
        return False, [str(e)]


def run_joiner(joiner_script, input_dir, output_file, year, month,
               exclude_vars=None, include_vars=None,
               chunk_size=10000, max_memory_rows=30000):
    """
    Run the ERA5 joiner script on processed data

    Args:
        joiner_script: Path to the joiner script
        input_dir: Input directory with processed data
        output_file: Path to save joined data
        year: Year to process
        month: Month to process
        exclude_vars: Variables to exclude
        include_vars: Variables to include
        chunk_size: Chunk size for processing
        max_memory_rows: Maximum rows in memory

    Returns:
        Tuple of (success, log_output)
    """
    cmd = [
        sys.executable, joiner_script,
        "--input", input_dir,
        "--output", output_file,
        "--year", str(year),
        "--month", str(month).zfill(2),
        "--chunk-size", str(chunk_size),
        "--max-memory-rows", str(max_memory_rows)
    ]

    if exclude_vars:
        cmd.extend(["--exclude-vars"] + exclude_vars)

    if include_vars:
        cmd.extend(["--include-vars"] + include_vars)

    logger.info(f"Running joiner: {' '.join(cmd)}")

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

        log_output = []
        for line in process.stdout:
            log_output.append(line.strip())

        process.wait()

        success = process.returncode == 0

        if success:
            logger.info(f"Joiner completed successfully for {year}-{month}")
        else:
            logger.error(f"Joiner failed for {year}-{month} with return code {process.returncode}")

        return success, log_output

    except Exception as e:
        logger.error(f"Error running joiner for {year}-{month}: {e}")
        return False, [str(e)]


def sort_file_chronologically(file_path, chunk_size=100000, max_memory_rows=500000,
                              backup=False, log_dir=None):
    """
    Sort a joined ERA5 file chronologically by time (integrated from sorter script)

    Args:
        file_path: Path to the file to sort
        chunk_size: Chunk size for reading CSV files
        max_memory_rows: Maximum rows to hold in memory
        backup: Whether to create backup before sorting
        log_dir: Directory for error logs

    Returns:
        Dict with processing results
    """
    start_time = time.time()
    file_name = os.path.basename(file_path)

    logger.info(f"Sorting file chronologically: {file_path}")

    # Create a backup if requested
    if backup:
        backup_dir = os.path.join(os.path.dirname(file_path), "backup")
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, file_name)
        logger.info(f"Creating backup at: {backup_path}")

        # Different copy approach for large files
        if os.path.getsize(file_path) > 1e9:  # If file is larger than 1GB
            with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                # Copy in chunks
                chunk = src.read(1024 * 1024)  # 1MB chunks
                while chunk:
                    dst.write(chunk)
                    chunk = src.read(1024 * 1024)
        else:
            shutil.copy2(file_path, backup_path)

    # Determine file type
    file_ext = os.path.splitext(file_path)[1].lower()
    is_parquet = file_ext == '.parquet'

    try:
        # Read the data
        if is_parquet:
            # For Parquet, we can read directly
            df = pd.read_parquet(file_path)
        else:
            # For CSV, read in chunks
            chunks = []
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                chunks.append(chunk)

            # Combine chunks
            df = pd.concat(chunks, ignore_index=True)
            del chunks
            gc.collect()  # Force garbage collection

        logger.info(f"Loaded file with shape: {df.shape}")

        # Check if 'time' column exists
        if 'time' not in df.columns:
            logger.error(f"No 'time' column found in {file_path}, skipping")
            return {
                'file': file_path,
                'success': False,
                'error': "No 'time' column found"
            }

        # Convert time to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df['time']):
            try:
                df['time'] = pd.to_datetime(df['time'])
                logger.info(f"Converted time column to datetime format for {file_path}")
            except Exception as e:
                logger.warning(f"Could not convert time column to datetime for {file_path}: {e}")
                # Continue anyway, sorting might still work with string times

        # Sort the data
        logger.info(f"Sorting {file_path} by time, latitude, longitude")
        df = df.sort_values(['time', 'latitude', 'longitude'])

        # Create a temporary file path
        temp_path = file_path + ".sorted"

        # Save the sorted data
        if is_parquet:
            df.to_parquet(temp_path, index=False)
        else:
            # Write CSV in chunks to save memory
            chunk_size = min(chunk_size, max_memory_rows)
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i:i + chunk_size]
                mode = 'w' if i == 0 else 'a'
                header = i == 0
                chunk.to_csv(temp_path, mode=mode, header=header, index=False)

        # Replace the original file
        os.replace(temp_path, file_path)

        end_time = time.time()
        logger.info(f"Successfully sorted {file_path} in {end_time - start_time:.2f} seconds")

        # Return success
        return {
            'file': file_path,
            'success': True,
            'time_taken': end_time - start_time
        }

    except Exception as e:
        logger.error(f"Error sorting {file_path}: {e}")
        import traceback
        error_details = traceback.format_exc()

        # Save error log
        if log_dir:
            error_log_path = os.path.join(log_dir, f"sort_error_{os.path.basename(file_path)}.log")
            with open(error_log_path, 'w') as f:
                f.write(f"Error sorting {file_path}:\n{error_details}")

        return {
            'file': file_path,
            'success': False,
            'error': str(e)
        }


def sort_batch_files(args):
    """Sort multiple files for multiprocessing"""
    file_paths, config = args

    results = []
    for file_path in file_paths:
        result = sort_file_chronologically(
            file_path=file_path,
            chunk_size=config.get('sort_chunk_size', 100000),
            max_memory_rows=config.get('sort_max_memory_rows', 500000),
            backup=config.get('sort_backup', False),
            log_dir=config.get('log_dir')
        )
        results.append(result)

    return results


def find_joined_files(joined_dir, pattern="joined_*.{csv,parquet}"):
    """
    Find all joined ERA5 files in the joined directory

    Args:
        joined_dir: Directory containing joined files
        pattern: Glob pattern to match files

    Returns:
        List of file paths
    """
    joined_files = []

    # Handle both CSV and Parquet files
    if '{' in pattern and '}' in pattern:
        # Extract the extensions
        base_pattern = pattern.split('{')[0]
        extensions_part = pattern.split('{')[1].split('}')[0]
        extensions = extensions_part.split(',')

        # Search for each extension
        for ext in extensions:
            search_pattern = base_pattern + ext
            joined_files.extend(glob.glob(os.path.join(joined_dir, "**", search_pattern), recursive=True))
    else:
        # Simple pattern
        joined_files = glob.glob(os.path.join(joined_dir, "**", pattern), recursive=True)

    logger.info(f"Found {len(joined_files)} joined files for sorting")
    return joined_files


def process_grib_file(args):
    """Process a single GRIB file (for use with multiprocessing)"""
    grib_file, year, month, config, converter_script = args

    # Create year/month specific output directory
    # The processed directory will be organized by year/month automatically by the converter script

    # Run the converter script
    success, log_output = run_converter(
        converter_script=converter_script,
        grib_file=grib_file,
        output_dir=config['processed_dir'],
        variables=config.get('variables'),
        exclude_variables=config.get('exclude_variables'),
        decimal_precision=config.get('decimal_precision'),
        compress=config.get('compress'),
        parquet=config.get('parquet'),
        remove_csv=config.get('remove_csv', False)
    )

    # Save log output
    log_path = os.path.join(config['log_dir'], f"convert_{year}_{month:02d}_{os.path.basename(grib_file)}.log")
    with open(log_path, 'w') as log_file:
        log_file.write('\n'.join(log_output))

    return {
        'grib_file': grib_file,
        'year': year,
        'month': month,
        'success': success
    }


def join_month_data(args):
    """Join data for a specific year/month (for use with multiprocessing)"""
    year, month, config, joiner_script = args

    # Define output file path
    output_dir = os.path.join(config['joined_dir'], str(year))
    os.makedirs(output_dir, exist_ok=True)

    # Determine output format based on config
    if config.get('output_format', 'parquet').lower() == 'csv':
        output_file = os.path.join(output_dir, f"joined_{year}{month:02d}.csv")
    else:
        output_file = os.path.join(output_dir, f"joined_{year}{month:02d}.parquet")

    # Run the joiner script
    success, log_output = run_joiner(
        joiner_script=joiner_script,
        input_dir=config['processed_dir'],
        output_file=output_file,
        year=year,
        month=month,
        exclude_vars=config.get('exclude_vars'),
        include_vars=config.get('include_vars'),
        chunk_size=config.get('chunk_size', 10000),
        max_memory_rows=config.get('max_memory_rows', 30000)
    )

    # Save log output
    log_path = os.path.join(config['log_dir'], f"join_{year}_{month:02d}.log")
    with open(log_path, 'w') as log_file:
        log_file.write('\n'.join(log_output))

    return {
        'year': year,
        'month': month,
        'success': success,
        'output_file': output_file if success else None
    }


def cleanup_processed_data(year, month, config):
    """
    Clean up processed data for a specific year/month after successful joining

    Args:
        year: Year to clean up
        month: Month to clean up
        config: Configuration settings
    """
    if config.get('keep_processed', False):
        logger.info(f"Keeping processed data for {year}-{month:02d} as requested")
        return

    # Check that joined data exists before removing processed data
    joined_file_pattern = os.path.join(
        config['joined_dir'],
        str(year),
        f"joined_{year}{month:02d}.*"
    )
    joined_files = glob.glob(joined_file_pattern)

    if not joined_files:
        logger.warning(f"No joined file found for {year}-{month:02d}, skipping cleanup")
        return

    # Path to the processed data for this year/month
    processed_dir = os.path.join(config['processed_dir'], str(year), f"{month:02d}")

    if not os.path.exists(processed_dir):
        logger.warning(f"Processed directory {processed_dir} not found, skipping cleanup")
        return

    logger.info(f"Removing processed data in {processed_dir}")

    try:
        # Remove the directory
        shutil.rmtree(processed_dir)
        logger.info(f"Successfully removed {processed_dir}")
    except Exception as e:
        logger.error(f"Error removing processed data: {e}")


def process_era5_data(grib_input_dir, base_dir, converter_script, joiner_script,
                      start_year=None, end_year=None, max_workers=None,
                      batch_size=10, config=None):
    """
    Process ERA5 data from GRIB files to joined datasets with chronological sorting

    Args:
        grib_input_dir: Directory containing GRIB files
        base_dir: Base directory for processed and joined data
        converter_script: Path to ERA5 converter script
        joiner_script: Path to ERA5 joiner script
        start_year: Start year to process
        end_year: End year to process
        max_workers: Maximum number of concurrent processes
        batch_size: Number of months to process in each batch
        config: Configuration settings
    """
    # Set default config if not provided
    if config is None:
        config = {}

    # Create output directories
    processed_dir = os.path.join(base_dir, "processed")
    joined_dir = os.path.join(base_dir, "joined")
    log_dir = os.path.join(base_dir, "logs")

    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(joined_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    # Set up logging
    log_file = setup_logging(log_dir, "era5_pipeline")

    # Add paths to config
    config.update({
        'processed_dir': processed_dir,
        'joined_dir': joined_dir,
        'log_dir': log_dir
    })

    # Find GRIB files that match year range
    year_range = None
    if start_year is not None and end_year is not None:
        year_range = (start_year, end_year)

    grib_files = find_grib_files(grib_input_dir, year_range)

    if not grib_files:
        logger.error(f"No GRIB files found in {grib_input_dir} matching criteria")
        return

    # Group files by year and month
    grouped_files = {}
    for filepath, year, month in grib_files:
        key = (year, month)
        if key not in grouped_files:
            grouped_files[key] = []
        grouped_files[key].append(filepath)

    # Create list of year/month tuples sorted chronologically
    month_keys = sorted(grouped_files.keys())

    logger.info(f"Processing data for {len(month_keys)} year-month combinations")

    # Track all successfully joined files for sorting
    all_joined_files = []

    # Process in batches
    for batch_start in range(0, len(month_keys), batch_size):
        batch_end = min(batch_start + batch_size, len(month_keys))
        current_batch = month_keys[batch_start:batch_end]

        logger.info(f"Processing batch {batch_start // batch_size + 1}: {current_batch[0]} to {current_batch[-1]}")

        # Track which months were successfully processed
        successful_months = []

        # STEP 1: Convert GRIB files to CSV/Parquet for this batch
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Create list of tasks for each GRIB file in the batch
            tasks = []
            for year, month in current_batch:
                for grib_file in grouped_files[(year, month)]:
                    tasks.append((grib_file, year, month, config, converter_script))

            # Submit all tasks to the executor
            futures = {executor.submit(process_grib_file, task): task for task in tasks}

            # Process completed tasks
            for future in as_completed(futures):
                task = futures[future]
                try:
                    result = future.result()
                    if result['success']:
                        successful_months.append((result['year'], result['month']))
                except Exception as e:
                    logger.error(f"Error processing {task[0]}: {e}")

        # Group successful months by year
        successful_months_set = set(successful_months)

        # STEP 2: Join data for successfully processed months
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Create list of tasks for each successfully processed month
            join_tasks = []
            for year, month in current_batch:
                if (year, month) in successful_months_set:
                    join_tasks.append((year, month, config, joiner_script))

            if not join_tasks:
                logger.warning("No months were successfully processed in this batch, skipping join stage")
                continue

            # Submit all join tasks to the executor
            join_futures = {executor.submit(join_month_data, task): task for task in join_tasks}

            # Process completed join tasks
            successful_joins = []
            for future in as_completed(join_futures):
                task = join_futures[future]
                try:
                    result = future.result()
                    if result['success']:
                        successful_joins.append((result['year'], result['month']))
                        all_joined_files.append(result['output_file'])

                        # Clean up processed data if requested
                        if not config.get('keep_processed', False):
                            cleanup_processed_data(result['year'], result['month'], config)
                except Exception as e:
                    logger.error(f"Error joining data for {task[0]}-{task[1]}: {e}")

        logger.info(f"Batch processing complete. Joined data for {len(successful_joins)}/{len(join_tasks)} months")

        # Optional: add a delay between batches to allow system recovery
        if batch_end < len(month_keys) and config.get('batch_delay', 0) > 0:
            delay = config.get('batch_delay')
            logger.info(f"Waiting {delay} seconds before processing next batch...")
            time.sleep(delay)

    # STEP 3: Sort all joined files chronologically (if enabled)
    if config.get('sort_chronologically', False) and all_joined_files:
        logger.info(f"Starting chronological sorting of {len(all_joined_files)} joined files")

        # Group files for batch processing to avoid memory issues
        sort_batch_size = config.get('sort_batch_size', 1)  # Default to 1 file per worker
        sort_max_workers = min(max_workers or 1, len(all_joined_files))

        successful_sorts = 0
        failed_sorts = 0

        with ProcessPoolExecutor(max_workers=sort_max_workers) as executor:
            # Group files into batches
            file_batches = []
            for i in range(0, len(all_joined_files), sort_batch_size):
                batch = all_joined_files[i:i + sort_batch_size]
                file_batches.append((batch, config))

            # Submit sorting tasks
            sort_futures = {executor.submit(sort_batch_files, batch_args): batch_args[0]
                            for batch_args in file_batches}

            # Process results
            for future in as_completed(sort_futures):
                file_batch = sort_futures[future]
                try:
                    results = future.result()
                    for result in results:
                        if result['success']:
                            successful_sorts += 1
                        else:
                            failed_sorts += 1
                            logger.error(f"Failed to sort {result['file']}: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    failed_sorts += len(file_batch)
                    logger.error(f"Exception during sorting batch: {e}")

        logger.info(f"Chronological sorting complete. Successful: {successful_sorts}, Failed: {failed_sorts}")

    logger.info("ERA5 processing pipeline complete")


def main():
    parser = argparse.ArgumentParser(description="ERA5 data processing pipeline with chronological sorting")

    # Required arguments
    parser.add_argument("--grib-dir", required=True, help="Directory containing GRIB files")
    parser.add_argument("--output-dir", required=True, help="Base directory for output data")
    parser.add_argument("--converter-script", required=True, help="Path to ERA5 converter script")
    parser.add_argument("--joiner-script", required=True, help="Path to ERA5 joiner script")

    # Optional filters
    parser.add_argument("--start-year", type=int, help="Start year to process")
    parser.add_argument("--end-year", type=int, help="End year to process")

    # Conversion options
    parser.add_argument("--variables", nargs='+', help="Variables to extract (space-separated)")
    parser.add_argument("--exclude-variables", nargs='+', default=DEFAULT_EXCLUDE_VARS,
                        help=f"Variables to exclude (default: {DEFAULT_EXCLUDE_VARS})")
    parser.add_argument("--decimal-precision", type=int, default=4,
                        help="Number of decimal places for lat/long (default: 4)")
    parser.add_argument("--compress", choices=['gzip', 'bz2', 'zip', 'xz'],
                        help="Compression format for CSV files")

    # Join options
    parser.add_argument("--chunk-size", type=int, default=10000,
                        help="Chunk size for joiner (default: 10000)")
    parser.add_argument("--max-memory-rows", type=int, default=30000,
                        help="Max memory rows for joiner (default: 30000)")

    # Output options
    parser.add_argument("--output-format", choices=['csv', 'parquet'], default='parquet',
                        help="Output format for joined data (default: parquet)")
    parser.add_argument("--parquet", action="store_true",
                        help="Convert processed files to Parquet")
    parser.add_argument("--remove-csv", action="store_true",
                        help="Remove CSV files after Parquet conversion")

    # Processing options
    parser.add_argument("--keep-processed", action="store_true",
                        help="Keep processed data after joining")
    parser.add_argument("--max-workers", type=int,
                        help="Maximum number of concurrent processes")
    parser.add_argument("--batch-size", type=int, default=10,
                        help="Number of months to process in each batch (default: 10)")
    parser.add_argument("--batch-delay", type=int, default=0,
                        help="Delay in seconds between batches (default: 0)")

    # Chronological sorting options
    parser.add_argument("--sort-chronologically", action="store_true",
                        help="Sort joined files chronologically after processing")
    parser.add_argument("--sort-chunk-size", type=int, default=100000,
                        help="Chunk size for sorting CSV files (default: 100000)")
    parser.add_argument("--sort-max-memory-rows", type=int, default=500000,
                        help="Maximum rows in memory during sorting (default: 500000)")
    parser.add_argument("--sort-backup", action="store_true",
                        help="Create backups before sorting files")
    parser.add_argument("--sort-batch-size", type=int, default=1,
                        help="Number of files to sort per worker (default: 1)")

    args = parser.parse_args()

    # Create config dictionary from arguments
    config = {
        'variables': args.variables,
        'exclude_variables': args.exclude_variables,
        'decimal_precision': args.decimal_precision,
        'compress': args.compress,
        'parquet': args.parquet,
        'remove_csv': args.remove_csv,
        'exclude_vars': args.exclude_variables,
        'chunk_size': args.chunk_size,
        'max_memory_rows': args.max_memory_rows,
        'output_format': args.output_format,
        'keep_processed': args.keep_processed,
        'batch_delay': args.batch_delay,
        'sort_chronologically': args.sort_chronologically,
        'sort_chunk_size': args.sort_chunk_size,
        'sort_max_memory_rows': args.sort_max_memory_rows,
        'sort_backup': args.sort_backup,
        'sort_batch_size': args.sort_batch_size
    }

    # Run the pipeline
    process_era5_data(
        grib_input_dir=args.grib_dir,
        base_dir=args.output_dir,
        converter_script=args.converter_script,
        joiner_script=args.joiner_script,
        start_year=args.start_year,
        end_year=args.end_year,
        max_workers=args.max_workers,
        batch_size=args.batch_size,
        config=config
    )


if __name__ == "__main__":
    main()