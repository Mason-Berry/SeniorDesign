# ForecastTX Project Documentation Overview

## Project Summary

ForecastTX is a comprehensive weather forecasting and analysis platform that combines historical ERA5 weather data processing, machine learning prediction models, and an interactive web dashboard. The system is designed to provide county-level weather predictions and analysis for Texas, with a focus on severe weather events like hail and thunderstorms.

## System Architecture

```
ForecastTX Platform
├── Data Pipeline (Python/Scripts)
│   ├── ERA5 Data Download → GRIB Processing → CSV Conversion → Data Joining
│   └── Google Cloud Storage Integration
├── Machine Learning (Python/TensorFlow)
│   ├── ConvLSTM Weather Prediction Models
│   └── Linear Regression County Analysis
├── Web Application (React/JavaScript)
│   ├── Interactive Dashboard
│   ├── User Authentication
│   └── Data Visualization
└── Cloud Infrastructure (GCP/Firebase)
    ├── Data Storage
    └── Web Hosting
```

## Core Components

### 1. Data Processing Pipeline (`/scripts/`)
**Purpose**: Automated ERA5 weather data processing from raw GRIB files to analysis-ready datasets

**Key Scripts**:
- `get_data2.py` / `get_data3.py`: Download ERA5 data from Copernicus Climate Data Store
- `era5-organized-converter.py`: Convert GRIB files to organized CSV structure
- `era5-data-joiner.py`: Join multiple weather variables into unified datasets
- `era5-chronological-sorter.py`: Sort data chronologically for analysis
- `era5-processing-pipeline2.py`: Orchestrate the complete processing workflow
- `upload_year_range_to_gcs.sh`: Upload processed data to Google Cloud Storage

**Data Flow**:
1. Download → Raw GRIB files (60+ weather variables)
2. Convert → Organized CSV files by year/month/variable
3. Join → Unified datasets with multiple weather parameters
4. Sort → Chronologically ordered data for time-series analysis
5. Upload → Cloud storage for model training and web access

### 2. Machine Learning Models (`/model/`)
**Purpose**: Weather prediction using deep learning and statistical methods

**Components**:
- **ConvLSTM Model** (`phase1/model1.py`): 
  - TensorFlow/Keras implementation
  - Spatiotemporal weather pattern learning
  - Grid-based weather feature prediction
  - Google Cloud Platform integration
  - Mixed precision training for GPU optimization

**Future Phases**: Additional model architectures and approaches

### 3. Statistical Analysis (`/lr.py`)
**Purpose**: County-level linear regression analysis for weather event prediction

**Features**:
- Processes county weather event data (1955-2024)
- Predicts future event counts and magnitudes
- Outputs 5-year forecasts by county
- Handles missing data and data quality validation

### 4. Web Application (`/webapp/React/forcasttx/`)
**Purpose**: Interactive dashboard for weather data visualization and prediction display

**Key Features**:
- **Authentication**: Firebase-based user management
- **Interactive Maps**: Leaflet-based Texas county visualization
- **Data Visualization**: Chart.js charts, heat maps, time-series plots
- **Export Capabilities**: PDF, DOCX, and image export
- **Real-time Analysis**: ML model integration for live predictions
- **Multi-peril Analysis**: Hail, wind, and other weather hazards

**Technology Stack**:
- React 19 with modern hooks
- Bootstrap + Tailwind CSS styling
- Firebase backend services
- Leaflet mapping with weather overlays
- D3.js custom visualizations

### 5. Backend API Server (`/VMfiles/`)
**Purpose**: FastAPI backend server providing data services and API endpoints

**Key Features**:
- **RESTful API**: Endpoints for weather data, statistics, and KPIs
- **Data Processing**: County-level analysis and regional rankings
- **Static File Serving**: Direct access to processed JSON datasets  
- **Cloud Integration**: Google Cloud Storage integration
- **CORS Configuration**: Frontend-backend communication support

**API Categories**:
- KPI summary endpoints for weather metrics
- County ranking and regional analysis
- Yearly summaries and occurrence statistics
- Static data file serving for large datasets

**Technology Stack**:
- FastAPI Python framework
- Google Cloud Platform deployment
- JSON data processing and serving
- Statistical analysis and aggregation

## Data Sources and Coverage

### Primary Data Source
- **ERA5 Reanalysis**: Copernicus Climate Data Store (CDS)
- **Temporal Coverage**: 1955-2024 (expandable)
- **Spatial Coverage**: Texas region (36.5°N, -106.6°W to 25.8°N, -93.5°W)
- **Variables**: 40+ atmospheric and surface parameters
- **Resolution**: Hourly timesteps, grid-based spatial data

### Weather Variables Processed
- Wind components (surface, 10m, 100m levels)
- Temperature and humidity (2m levels)
- Precipitation (total, convective, large-scale)
- Cloud properties (coverage, liquid/ice water)
- Atmospheric stability indices (CAPE, K-index, etc.)
- Pressure and moisture fields

## Development Environment Setup

### Data Processing Requirements
```bash
# Python Environment
conda env create --file environment.yml --prefix ./venv

# Key Dependencies
- xarray, cfgrib, eccodes (GRIB processing)
- pandas, numpy (data manipulation)
- google-cloud-storage (cloud integration)
- scikit-learn (statistical analysis)
- tensorflow (deep learning)
```

### Web Application Setup
```bash
# React Application
cd webapp/React/forcasttx
npm install
npm start  # Development server
npm run build  # Production build
```

## Deployment Architecture

### Cloud Infrastructure
- **Google Cloud Platform**: Primary cloud provider
- **Data Storage**: Google Cloud Storage buckets
- **Compute**: Cloud instances for model training
- **Web Hosting**: Firebase hosting for React application

### Data Pipeline Deployment
- **Processing**: Cloud-based batch processing
- **Storage**: Organized GCS bucket structure
- **Models**: Containerized model training and serving

## Project Status and Roadmap

### Current Capabilities
✅ **Data Pipeline**: Complete ERA5 processing workflow  
✅ **Statistical Models**: County-level linear regression predictions  
✅ **Deep Learning**: ConvLSTM architecture implementation  
✅ **Web Dashboard**: Interactive Texas weather visualization  
✅ **User Management**: Firebase authentication system  
✅ **Export Features**: Multi-format data export  

### Future Enhancements
🔄 **Enhanced ML Models**: Additional deep learning architectures  
🔄 **Real-time Data**: Live weather data integration  
🔄 **Advanced Analytics**: More sophisticated statistical analysis  
🔄 **Mobile App**: Native mobile application  
🔄 **API Development**: RESTful APIs for external integration  

## Documentation Structure

This documentation is organized into the following files:

### Core Documentation
1. **`project-overview.md`** (this file): High-level project summary
2. **`root-directory.md`**: Root-level files and configuration
3. **`scripts-directory.md`**: Data processing pipeline documentation
4. **`model-directory.md`**: Machine learning model documentation
5. **`webapp-directory.md`**: Web application structure and components
6. **`vmfiles-directory.md`**: Backend API server documentation

### Setup and Usage Guides
7. **`external-services-setup.md`**: Complete guide for setting up all external service accounts (CDS, GCP, Firebase)
8. **`gcp-infrastructure-setup.md`**: Comprehensive Google Cloud Platform infrastructure setup including PostgreSQL with PostGIS, VMs, storage, and service accounts
9. **`detailed-script-usage.md`**: Step-by-step usage instructions for all major scripts with examples and troubleshooting
10. **`configuration-templates.md`**: Templates for all configuration files, environment variables, and account-specific settings

## Getting Started

**🚀 Quick Start for New Users:**
1. **First, read `external-services-setup.md`** to set up all required external accounts (CDS, GCP, Firebase)
2. **Then, follow `detailed-script-usage.md`** for step-by-step instructions on running each component

### For Data Processing
1. Set up conda environment: `conda env create --file environment.yml`
2. **Configure external services**: Follow CDS API setup in `external-services-setup.md`
3. **Run data pipeline**: Use examples in `detailed-script-usage.md` sections 1-2

### For Model Development
1. **Set up GCP**: Follow Google Cloud setup in `external-services-setup.md`
2. **Prepare data**: Use data processing scripts with detailed instructions
3. **Train models**: Follow Phase 1 and Phase 2 training guides in `detailed-script-usage.md` section 3

### For Web Development
1. **Configure Firebase**: Follow Firebase setup in `external-services-setup.md`
2. Navigate to `webapp/React/forcasttx/`
3. Install dependencies: `npm install`
4. Update configuration with your Firebase credentials
5. Start development server: `npm start`

### For Backend API Server
1. **Set up GCP VM**: Follow VM setup in `external-services-setup.md`
2. Navigate to `VMfiles/`
3. **Configure environment**: Follow detailed backend setup instructions
4. Start FastAPI server with your configuration

## Support and Maintenance

### Data Pipeline
- Scripts are optimized for low-memory environments (WSL, limited RAM)
- Comprehensive error handling and logging
- Configurable processing parameters for different hardware setups

### Model Training
- GPU-optimized for Google Cloud Platform T4 instances
- Mixed precision training for performance
- Checkpoint saving for training interruption recovery

### Web Application
- Modern React development practices
- Responsive design for multiple devices
- Progressive Web App (PWA) capabilities

---

*This documentation provides a comprehensive overview of the ForecastTX weather forecasting platform. For detailed implementation information, refer to the specific directory documentation files.*