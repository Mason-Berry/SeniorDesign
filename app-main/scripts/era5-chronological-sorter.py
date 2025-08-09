#!/usr/bin/env python3

import os
import glob
import pandas as pd
import argparse
import logging
from datetime import datetime
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import gc  # For garbage collection

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)


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


def find_joined_files(input_dir, pattern="joined_*.{csv,parquet}"):
    """
    Find all joined ERA5 files in the input directory

    Args:
        input_dir: Directory containing joined files
        pattern: Glob pattern to match files

    Returns:
        List of file paths
    """
    # Handle both CSV and Parquet files
    joined_files = []

    # Support pattern with curly braces for multiple extensions
    if '{' in pattern and '}' in pattern:
        # Extract the extensions
        base_pattern = pattern.split('{')[0]
        extensions_part = pattern.split('{')[1].split('}')[0]
        extensions = extensions_part.split(',')

        # Search for each extension
        for ext in extensions:
            search_pattern = base_pattern + ext
            joined_files.extend(glob.glob(os.path.join(input_dir, "**", search_pattern), recursive=True))
    else:
        # Simple pattern
        joined_files = glob.glob(os.path.join(input_dir, "**", pattern), recursive=True)

    logger.info(f"Found {len(joined_files)} joined files in {input_dir}")
    return joined_files


def sort_file_chronologically(args):
    """
    Sort a joined ERA5 file chronologically by time

    Args:
        args: Tuple of (file_path, chunk_size, max_memory_rows, backup, log_dir)

    Returns:
        Dict with processing results
    """
    file_path, chunk_size, max_memory_rows, backup, log_dir = args

    start_time = time.time()
    file_name = os.path.basename(file_path)

    logger.info(f"Processing file: {file_path}")

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
            import shutil
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
            error_log_path = os.path.join(log_dir, f"error_{os.path.basename(file_path)}.log")
            with open(error_log_path, 'w') as f:
                f.write(f"Error sorting {file_path}:\n{error_details}")

        return {
            'file': file_path,
            'success': False,
            'error': str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Sort ERA5 joined files chronologically by time")

    # Required arguments
    parser.add_argument("--input-dir", required=True, help="Directory containing joined files")

    # Optional arguments
    parser.add_argument("--pattern", default="joined_*.{csv,parquet}",
                        help="File pattern to match (default: 'joined_*.{csv,parquet}')")
    parser.add_argument("--chunk-size", type=int, default=100000,
                        help="Chunk size for reading CSV files (default: 100000)")
    parser.add_argument("--max-memory-rows", type=int, default=500000,
                        help="Maximum rows to hold in memory (default: 500000)")
    parser.add_argument("--backup", action="store_true",
                        help="Create backups of files before sorting")
    parser.add_argument("--max-workers", type=int, default=1,
                        help="Maximum number of files to process in parallel (default: 1)")
    parser.add_argument("--log-dir", default=None,
                        help="Directory for logs (default: input_dir/logs)")

    args = parser.parse_args()

    # Setup log directory
    log_dir = args.log_dir if args.log_dir else os.path.join(args.input_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Setup logging
    log_file = setup_logging(log_dir, "era5_sorter")

    # Find joined files
    joined_files = find_joined_files(args.input_dir, args.pattern)

    if not joined_files:
        logger.error(f"No joined files found in {args.input_dir} matching pattern '{args.pattern}'")
        return

    # Process files
    successful = 0
    failed = 0

    with ProcessPoolExecutor(max_workers=args.max_workers) as executor:
        # Create tasks
        tasks = [(file_path, args.chunk_size, args.max_memory_rows, args.backup, log_dir)
                 for file_path in joined_files]

        # Submit tasks
        futures = {executor.submit(sort_file_chronologically, task): task[0] for task in tasks}

        # Process results
        for future in as_completed(futures):
            file_path = futures[future]
            try:
                result = future.result()
                if result['success']:
                    successful += 1
                else:
                    failed += 1
                    logger.error(f"Failed to sort {file_path}: {result.get('error', 'Unknown error')}")
            except Exception as e:
                failed += 1
                logger.error(f"Exception processing {file_path}: {e}")

    logger.info(f"Sorting complete. Successful: {successful}, Failed: {failed}")


if __name__ == "__main__":
    main()