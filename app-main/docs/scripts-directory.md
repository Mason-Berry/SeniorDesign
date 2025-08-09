# Scripts Directory Documentation

## Overview
This directory contains utility scripts for ERA5 weather data processing, from download to organization and cloud storage upload.

## Files

### README
**Purpose**: Comprehensive setup and usage guide for the ERA5 data processing pipeline
**Usage**: Reference document containing:
- Required dependencies and setup instructions
- Command-line usage examples for all pipeline scripts
- Processing pipeline workflow documentation
- Memory optimization recommendations
- Troubleshooting guidance

**Key Information**:
- Documents multi-step processing: GRIB → CSV → joined data → sorted data
- Provides WSL/low-memory environment optimizations
- Contains working command examples for each script

### era5-chronological-sorter.py
**Purpose**: Sorts processed ERA5 joined files chronologically by time
**Usage**: Post-processing script to organize data temporally for efficient analysis

**Key Features**:
- Handles both CSV and Parquet formats
- Memory-efficient chunked processing
- Optional backup creation before sorting
- Parallel processing support (configurable workers)
- Comprehensive logging and error handling

**Command Example**:
```bash
python3 era5-chronological-sorter.py --input-dir processed/joined_data_1960 --backup --max-workers 1
```

**Performance Notes**:
- Processes large files (~5 minutes for 12 monthly files)
- Memory-safe for low-resource environments

### era5-data-joiner.py
**Purpose**: Joins multiple ERA5 variable files into unified datasets
**Usage**: Combines separate variable CSV files by time, latitude, and longitude coordinates

**Key Features**:
- Memory-efficient incremental joining
- Flexible variable inclusion/exclusion
- Automatic column detection and mapping
- Support for year/month filtering
- Output in CSV or Parquet format
- Chunked processing for large datasets

**Default Excluded Variables**: `['10fg', 'cbh', 'cin', 'cp', 'i10fg', 'lsp', 'tp', 'vimd']`

**Command Example**:
```bash
python era5-data-joiner.py --input processed --year 1960 --month 01 --output joined_196001.parquet --max-memory-rows 30000
```

**Data Processing**:
- Handles varying column naming conventions
- Creates temporary files for memory management
- Validates coordinate columns before joining

### era5-organized-converter.py
**Purpose**: Converts ERA5 GRIB files to organized CSV/Parquet structure
**Usage**: First stage of processing pipeline - extracts variables from GRIB format

**Key Features**:
- Processes individual variables separately
- Creates organized directory structure: `year/month/variable/`
- Time-chunked processing (default 24 hours)
- Coordinate precision control
- Optional constant column removal
- Automatic variable discovery from GRIB files
- Direct Parquet conversion support

**Directory Structure Created**:
```
output_dir/
├── YYYY/
│   └── MM/
│       ├── variable1/
│       ├── variable2/
│       └── ...
```

**Command Example**:
```bash
python era5-organized-converter.py --input data.grib --output ./processed --decimal-precision 4 --parquet
```

**Supported Variables**: Handles 40+ ERA5 variables including wind, temperature, precipitation, cloud data

### era5-processing-pipeline2.py
**Purpose**: Orchestrates the complete ERA5 data processing workflow
**Usage**: Master script that coordinates conversion, joining, and organization of GRIB files

**Key Features**:
- Batch processing of multiple GRIB files
- Automatic year/month extraction from filenames
- Configurable processing parameters
- Multi-worker parallel processing
- Comprehensive logging and error handling
- Memory optimization controls

**Pipeline Stages**:
1. GRIB file discovery and filtering
2. Variable conversion (using era5-organized-converter.py)
3. Data joining (using era5-data-joiner.py)
4. Optional sorting and cloud upload

**Command Example**:
```bash
python3 era5-processing-pipeline2.py --grib-dir data/ --output-dir processed/ --start-year 1960 --end-year 1970 --max-workers 2
```

### get_data3.py
**Purpose**: Enhanced ERA5 data downloader with flexible configuration
**Usage**: Downloads specific ERA5 data using CDS API with customizable parameters

**Key Features**:
- Configurable variable selection
- Custom geographical areas (default: Texas)
- Specific year/month targeting
- Day-level filtering support
- JSON-based configuration
- API credential management

**Default Coverage**: Texas bounding box `[36.5, -106.6, 25.8, -93.5]`

**Command Example**:
```bash
python get_data3.py --cdsapirc ~/.cdsapirc --year 2024 --month 01 --output_dir data/
```

### gha-service-account.json
**Purpose**: Google Cloud service account credentials
**Usage**: Authentication file for Google Cloud Storage operations
**Security Note**: Contains sensitive credentials - should be kept secure and not committed to version control

### upload_year_range_to_gcs.sh
**Purpose**: Bash script for bulk upload of processed data to Google Cloud Storage
**Usage**: Uploads multiple years of processed ERA5 data to GCS bucket

**Configuration**:
- Target bucket: `forecasttx-era5-data-bucket`
- Source directory: `$HOME/era5_postgres_test/processed/joined`
- Destination path: `era5_csv/YEAR/`

**Command Example**:
```bash
./upload_year_range_to_gcs.sh 1970 1975
```

**Features**:
- Year range processing
- Directory existence validation
- Progress indicators with emojis
- Individual file upload with confirmation

### data_joiner_output.png
**Purpose**: Visual output example from the data joining process
**Usage**: Reference image showing the structure or results of joined ERA5 data

### upload
**Purpose**: Additional upload utility (specific functionality not detailed in available files)

## Processing Workflow

The typical ERA5 data processing workflow using these scripts:

1. **Download**: Use `get_data3.py` or `get_data2.py` to download GRIB files
2. **Convert**: Use `era5-organized-converter.py` to extract variables into organized CSV structure
3. **Join**: Use `era5-data-joiner.py` to combine variables into unified datasets
4. **Sort**: Use `era5-chronological-sorter.py` to organize data chronologically
5. **Upload**: Use `upload_year_range_to_gcs.sh` to store processed data in cloud storage

## Memory Optimization

These scripts are optimized for low-memory environments (WSL, limited RAM):
- Chunked processing to avoid memory exhaustion
- Configurable memory limits
- Temporary file management
- Garbage collection integration
- Progress monitoring and error recovery

## Dependencies

Required Python packages:
- xarray, cfgrib, eccodes (GRIB file handling)
- pandas, numpy (data processing)
- pyarrow (Parquet support)
- google-cloud-storage (GCS integration)
- dask (parallel processing)
- netCDF4, matplotlib (additional format support)