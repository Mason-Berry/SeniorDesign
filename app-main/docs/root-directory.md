# Root Directory Documentation

## Overview
This document describes the files and subdirectories in the root directory of the weather forecasting application project.

## Files

### environment.yml
**Purpose**: Conda environment configuration file
**Usage**: Defines Python 3.11 environment with weather data processing dependencies including:
- Data processing: xarray, pandas, numpy, netCDF4
- Weather data: cfgrib, eccodes, cdsapi
- Machine learning: scikit-learn
- Visualization: matplotlib
- Performance: dask, pyarrow

**Command to use**: `conda env create --file environment.yml --prefix ./venv`

### get_data readme.docx
**Purpose**: Documentation file for data retrieval process
**Usage**: Word document containing instructions for data collection (not analyzed in detail)

### get_data2.py
**Purpose**: ERA5 weather data downloader from Copernicus Climate Data Store
**Usage**: Downloads historical weather data for Texas region (1960-1964) including:
- Wind components (10m, 100m)
- Temperature and precipitation data
- Cloud cover and atmospheric variables
- Severe weather indices (CAPE, K-index, etc.)

**Key Features**:
- Downloads data for Texas bounding box: [36.5, -106.6, 25.8, -93.5]
- Saves data in GRIB format
- Handles existing file checks and error recovery
- Requires CDS API credentials

### lr.py
**Purpose**: Linear regression model for weather event prediction
**Usage**: Processes county-level weather event data to predict future occurrences
**Functionality**:
- Loads county weather event data from CSV
- Performs temporal linear regression analysis
- Predicts event counts and magnitudes for next 5 years
- Outputs predictions to 'county_predictions_combined.csv'

**Data Processing**:
- Filters data from 1955-2024
- Groups events by county and month
- Handles missing data with county-specific means
- Validates data quality before model training

### oryx-build-commands.txt
**Purpose**: Build configuration for deployment platform
**Usage**: Specifies Python platform and conda environment setup command for Oryx build system

## Subdirectories

### model/
Contains machine learning models, training scripts, and model execution utilities

### scripts/
Contains ERA5 data processing pipeline and utility scripts

### webapp/
Contains the React-based web application frontend

### VMfiles/
Contains the FastAPI backend server and API data processing modules

## Project Structure Summary
This is a weather forecasting application that:
1. Downloads historical weather data from ERA5
2. Processes and analyzes the data using machine learning
3. Provides predictions through a React web interface
4. Focuses on Texas weather events and county-level predictions