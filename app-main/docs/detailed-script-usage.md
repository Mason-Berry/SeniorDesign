# Detailed Script Usage Guide

## Overview
This guide provides comprehensive usage instructions for all major scripts in the ForecastTX project, including step-by-step examples, common use cases, and troubleshooting tips.

---

## 1. Data Download Scripts

### get_data2.py - ERA5 Data Downloader

#### Purpose
Downloads ERA5 reanalysis data from Copernicus Climate Data Store for years 1960-1964.

#### Prerequisites
- CDS API account and credentials configured (see external-services-setup.md)
- Python packages: `cdsapi`

#### Basic Usage
```bash
python get_data2.py
```

#### What It Does
1. Downloads 40+ weather variables for Texas region (36.5°N, -106.6°W to 25.8°N, -93.5°W)
2. Saves data as GRIB files in `data/` directory
3. Creates files named: `era5_data_YYYY_MM.grib`

#### Example Output
```
data/
├── era5_data_1960_01.grib
├── era5_data_1960_02.grib
├── ...
└── era5_data_1964_12.grib
```

#### Customization Options
To modify the script for different years or regions:

```python
# Change years (around line 70)
years = [str(y) for y in range(1965, 1970)]  # Download 1965-1969

# Change region (around line 100)
area = [40.0, -110.0, 20.0, -90.0]  # Larger Texas region
```

#### Common Issues and Solutions
- **Error**: "Invalid API key"
  - Check `.cdsapirc` configuration
- **Error**: "Download failed"
  - Server issues; retry after 30 minutes
- **Large files**: Each monthly file is ~2-5GB, ensure sufficient disk space

---

### scripts/get_data3.py - Enhanced ERA5 Downloader

#### Purpose
Flexible ERA5 downloader with customizable parameters for specific years and variables.

#### Prerequisites
- CDS API credentials
- Python packages: `cdsapi`, `argparse`, `json`

#### Basic Usage
```bash
python scripts/get_data3.py --year 2024 --month 01 --output_dir data/
```

#### Advanced Usage
```bash
# Download specific variables only
python scripts/get_data3.py \
    --year 2024 \
    --month 01 \
    --variables temperature,precipitation,wind \
    --output_dir data/custom/

# Download for custom region
python scripts/get_data3.py \
    --year 2024 \
    --month 01 \
    --area "40,-110,20,-90" \
    --output_dir data/
```

#### Configuration File
Create `config.json` for custom settings:
```json
{
    "variables": [
        "2m_temperature",
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "total_precipitation"
    ],
    "area": [36.5, -106.6, 25.8, -93.5],
    "time": ["00:00", "06:00", "12:00", "18:00"]
}
```

#### Use with configuration:
```bash
python scripts/get_data3.py --config config.json --year 2024 --month 01
```

---

## 2. Data Processing Pipeline Scripts

### scripts/era5-organized-converter.py - GRIB to CSV Converter

#### Purpose
Converts ERA5 GRIB files to organized CSV/Parquet structure, separating variables and organizing by time.

#### Prerequisites
- Python packages: `xarray`, `cfgrib`, `pandas`, `pyarrow`
- Downloaded GRIB files from data download scripts

#### Basic Usage
```bash
python scripts/era5-organized-converter.py \
    --input data/era5_data_1960_01.grib \
    --output processed/1960_01/ \
    --parquet
```

#### Advanced Usage
```bash
# Process with custom parameters
python scripts/era5-organized-converter.py \
    --input data/era5_data_1960_01.grib \
    --output processed/1960_01/ \
    --decimal-precision 4 \
    --time-chunk-hours 24 \
    --remove-constants \
    --parquet
```

#### Batch Processing
```bash
# Process all GRIB files in directory
for file in data/*.grib; do
    year_month=$(basename "$file" .grib | sed 's/era5_data_//')
    python scripts/era5-organized-converter.py \
        --input "$file" \
        --output "processed/$year_month/" \
        --parquet
done
```

#### Output Structure
```
processed/1960_01/
├── 1960/
│   └── 01/
│       ├── 2t/           # 2m temperature
│       │   ├── 2t_1960_01_01_00.parquet
│       │   ├── 2t_1960_01_01_06.parquet
│       │   └── ...
│       ├── 10u/          # 10m u-wind
│       ├── 10v/          # 10m v-wind
│       └── ...
```

#### Memory Optimization
For low-memory systems:
```bash
python scripts/era5-organized-converter.py \
    --input data/era5_data_1960_01.grib \
    --output processed/1960_01/ \
    --time-chunk-hours 6 \
    --max-memory-gb 4
```

---

### scripts/era5-data-joiner.py - Variable Data Joiner

#### Purpose
Joins separate variable files into unified datasets by combining weather parameters at each time/location.

#### Prerequisites
- Organized CSV/Parquet files from era5-organized-converter.py
- Python packages: `pandas`, `pyarrow`, `dask`

#### Basic Usage
```bash
python scripts/era5-data-joiner.py \
    --input processed/1960_01/ \
    --year 1960 \
    --month 01 \
    --output joined_data_1960_01.parquet
```

#### Advanced Options
```bash
# Join with custom variable exclusions
python scripts/era5-data-joiner.py \
    --input processed/1960_01/ \
    --year 1960 \
    --month 01 \
    --exclude-vars "10fg,cbh,cin" \
    --max-memory-rows 50000 \
    --output joined_data_1960_01.parquet
```

#### Batch Processing Script
Create `join_all_months.sh`:
```bash
#!/bin/bash
for year in {1960..1964}; do
    for month in {01..12}; do
        echo "Processing $year-$month"
        python scripts/era5-data-joiner.py \
            --input processed/${year}_${month}/ \
            --year $year \
            --month $month \
            --output joined_data_${year}_${month}.parquet \
            --max-memory-rows 30000
    done
done
```

#### Memory Management
- `--max-memory-rows`: Limits rows loaded at once
- `--chunk-size`: Process data in chunks
- Monitor memory usage: `htop` or `free -h`

#### Output Format
```
# joined_data_1960_01.parquet columns:
time, latitude, longitude, 2t, 10u, 10v, sp, tp, ...
2024-01-01 00:00:00, 36.5, -106.6, 273.15, 2.1, -1.3, 101325, 0.0, ...
```

---

### scripts/era5-chronological-sorter.py - Time Series Sorter

#### Purpose
Sorts joined data files chronologically for efficient time-series analysis and model training.

#### Prerequisites
- Joined data files from era5-data-joiner.py
- Python packages: `pandas`, `pyarrow`

#### Basic Usage
```bash
python scripts/era5-chronological-sorter.py \
    --input-dir processed/joined_data_1960/ \
    --backup \
    --max-workers 1
```

#### Advanced Usage
```bash
# Sort with parallel processing
python scripts/era5-chronological-sorter.py \
    --input-dir processed/joined_data_1960/ \
    --output-dir processed/sorted_data_1960/ \
    --file-pattern "joined*.parquet" \
    --max-workers 4 \
    --backup
```

#### Batch Processing
```bash
# Sort all years
for year in {1960..1964}; do
    python scripts/era5-chronological-sorter.py \
        --input-dir processed/joined_data_$year/ \
        --backup \
        --max-workers 2
done
```

#### Performance Tuning
- Low memory: `--max-workers 1`
- High memory: `--max-workers 4-8`
- SSD storage: Higher worker count
- HDD storage: Lower worker count

---

## 3. Machine Learning Model Scripts

### model_code/phase1_model.py - ConvLSTM Training

#### Purpose
Trains Phase 1 ConvLSTM model for weather feature prediction using local data.

#### Prerequisites
- Processed numpy data files
- Python packages: `tensorflow`, `numpy`, `gc`
- GPU with sufficient VRAM (recommended: RTX 4090, 24GB)

#### Data Preparation
Before running, ensure you have:
```
/path/to/data/
├── global_unique_lats.npy
├── global_unique_lons.npy
├── gridded_era5_YYYY_MM.npy (for each year/month)
├── numpy_converted_era5_hourly_numpy_files_input_train_mean_per_feature_float32.npy
└── numpy_converted_era5_hourly_numpy_files_input_train_std_per_feature_float32.npy
```

#### Configuration
Edit the script to set your paths:
```python
# Line 14: Update to your data directory
PROCESSED_DATA_DIR = "/path/to/your/processed/data/"

# Line 29-36: Adjust for your hardware
BATCH_SIZE = 64  # Reduce if out of memory
USE_MIXED_PRECISION = True  # Set False if GPU issues
```

#### Basic Usage
```bash
# Ensure GPU is available
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# Run training
cd model/
python model_code/phase1_model.py
```

#### Training Monitoring
The script outputs training progress:
```
Epoch 1/100
Loading data for year 1955, month 1...
Training batch 1/150...
Epoch 1 - Loss: 0.0234, Val Loss: 0.0198
...
Model saved to: /path/to/data/local_model/convlstm_feature_predictor_full_dataset.keras
```

#### Memory Optimization
For limited VRAM:
```python
# Reduce batch size
BATCH_SIZE = 32  # or 16

# Disable mixed precision
USE_MIXED_PRECISION = False

# Add memory growth
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    tf.config.experimental.set_memory_growth(gpus[0], True)
```

#### Common Issues
- **CUDA out of memory**: Reduce `BATCH_SIZE`
- **Missing data files**: Check `PROCESSED_DATA_DIR` path
- **Slow training**: Ensure GPU usage with `nvidia-smi`

---

### model_code/phase2_model.py - Event Classification Training

#### Purpose
Trains Phase 2 multi-output classifier for weather event prediction using Phase 1 features.

#### Prerequisites
- Phase 1 trained model and data
- Phase 2 target event data
- Python packages: `tensorflow`, `scikit-learn`

#### Data Structure Required
```
/path/to/phase2/data/
├── feature_data/           # Phase 1 outputs
├── target_data/           # Event classification targets
│   ├── event_class_YYYY_MM.npy
│   └── ...
└── output/               # Model output directory
```

#### Configuration
```python
# Lines 17-19: Update paths
FEATURE_DATA_DIR = "/path/to/phase1/data/"
TARGET_DATA_DIR = "/path/to/phase2/targets/"

# Lines 34-39: Adjust training parameters
BATCH_SIZE = 32  # Smaller than Phase 1
USE_MIXED_PRECISION = False  # More stable for classification
```

#### Usage
```bash
cd model/
python model_code/phase2_model.py
```

#### Expected Output
```
Phase 2 Model Training Started...
Loading feature data from Phase 1...
Loading target event data...
Class distribution: [0.45, 0.30, 0.15, 0.10]
Training with class weights: [1.0, 1.5, 3.0, 4.5]
...
Model saved: multi_output_event_classifier_model.keras
```

---

### run_model/p1/p1_run.py - Phase 1 Forecasting

#### Purpose
Generates weather feature forecasts using trained Phase 1 model.

#### Prerequisites
- Trained Phase 1 model file
- Historical data for seeding
- Normalization statistics

#### Configuration
```python
# Line 14: Data directory with model and stats
PROCESSED_DATA_DIR = "/path/to/model/data/"

# Line 18: Path to trained model
MODEL_PATH = "/path/to/trained/model.keras"

# Line 30-36: Forecast parameters
FORECAST_START_YEAR = 2025
FORECAST_END_YEAR = 2027
SEQUENCE_LENGTH = 24  # Must match training
```

#### Usage
```bash
cd model/run_model/p1/
python p1_run.py
```

#### Output
Creates forecast file: `forecast_2025_to_2027.npy`
- Shape: (forecast_hours, grid_height, grid_width, num_features)
- Contains: Predicted weather features for each hour

#### Verification
```python
import numpy as np
forecast = np.load("forecast_2025_to_2027.npy")
print(f"Forecast shape: {forecast.shape}")
print(f"Forecast period: {forecast.shape[0]} hours")
print(f"Grid size: {forecast.shape[1]}x{forecast.shape[2]}")
print(f"Features: {forecast.shape[3]}")
```

---

### run_model/p1/p2_run.py - Phase 2 Event Forecasting

#### Purpose
Generates weather event predictions using Phase 1 forecasts and trained Phase 2 model.

#### Prerequisites
- Trained Phase 2 model
- Phase 1 forecast output
- Grid coordinate files

#### Configuration
```python
# Lines 14-16: Data directories
PHASE1_DATA_DIR = "/path/to/phase1/data/"
PHASE2_DATA_DIR = "/path/to/phase2/model/"

# Line 23: Input forecast from Phase 1
FEATURE_FORECAST_PATH = "forecast_2025_to_2030.npy"
```

#### Usage
```bash
cd model/run_model/p1/
python p2_run.py
```

#### Output
Creates event prediction files:
- Event class probabilities by location and time
- Regional event summaries
- Statistical confidence intervals

---

## 4. Backend API Scripts (VMfiles)

### VMfiles/main.py - FastAPI Server

#### Purpose
Serves weather data and statistics through RESTful API endpoints.

#### Prerequisites
- Processed JSON data files
- Python packages: `fastapi`, `uvicorn`
- Google Cloud credentials (if using GCS)

#### Development Usage
```bash
cd VMfiles/
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fastapi uvicorn google-cloud-storage

# Start development server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

#### Production Usage
```bash
# Start production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Configuration
Update `main.py` for your setup:
```python
# Lines 15-19: Update CORS origins
origins = [
    "https://your-project.web.app",
    "http://localhost:3000",
]

# Line 29: Update static files directory
app.mount("/data", StaticFiles(directory="your_json_directory"), name="data")
```

#### API Testing
```bash
# Test endpoints
curl http://localhost:8000/docs  # API documentation
curl http://localhost:8000/api/kpi-summary?year=2025&peril_type=HAIL
curl http://localhost:8000/data/your-file.json  # Static files
```

---

## 5. Data Processing Utilities (VMfiles)

### VMfiles/combine_wind_data.py - Wind Data Aggregation

#### Purpose
Combines multiple wind data sources into unified datasets for API serving.

#### Usage
```bash
cd VMfiles/
python combine_wind_data.py --input_dir data/wind/ --output combined_wind.json
```

### VMfiles/csv_to_json_event_code.py - Format Converter

#### Purpose
Converts CSV weather event data to JSON format for web serving.

#### Usage
```bash
cd VMfiles/
python csv_to_json_event_code.py --input events.csv --output events.json
```

### VMfiles/save_csvs_as_jsons.py - Batch Converter

#### Purpose
Batch converts multiple CSV files to JSON format.

#### Usage
```bash
cd VMfiles/
python save_csvs_as_jsons.py --input_dir csv_data/ --output_dir processed_json/
```

---

## 6.Troubleshooting Common Issues

### Memory Issues
- Reduce batch sizes in ML scripts
- Use chunked processing in data scripts
- Monitor memory with `htop` or Task Manager

### GPU Issues
- Check CUDA installation: `nvidia-smi`
- Verify TensorFlow GPU: `tf.config.list_physical_devices('GPU')`
- Reduce model complexity if out of VRAM

### File Path Issues
- Use absolute paths in configuration
- Check file permissions: `ls -la`
- Ensure directories exist before running scripts

### API Connection Issues
- Check firewall settings
- Verify CORS configuration
- Test with `curl` before browser testing

### Data Format Issues
- Verify input file formats match expected
- Check column names and data types
- Use data validation scripts before processing

---

This comprehensive guide should enable anyone to run each script successfully with proper configuration and troubleshooting support.