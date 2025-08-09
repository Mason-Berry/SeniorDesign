# VMfiles Directory Documentation

## Overview
This directory contains the backend API server implementation and data processing utilities for the ForecastTX web application. It provides RESTful API endpoints that serve weather data and statistics to the React frontend.

## Directory Structure

The VMfiles directory contains:
- **main.py**: FastAPI server entry point and routing
- **Data processing modules**: Scripts for loading, processing, and serving weather data
- **API endpoint handlers**: Modules that implement specific API functionality
- **Utility functions**: Helper functions for data manipulation and processing

## Core Files

### main.py
**Purpose**: FastAPI application entry point and main server configuration
**Usage**: Starts the backend server that provides API endpoints for the React frontend

**Key Features**:
- **CORS Configuration**: Allows requests from Firebase frontend and localhost
- **Static File Serving**: Mounts processed_json directory for direct file access
- **API Routing**: Defines endpoints for weather data retrieval
- **Cloud Integration**: Supports Google Cloud Storage operations

**CORS Origins**:
- Production: `https://argon-edge-455015-q8.web.app`
- Development: `http://localhost:3000`

**Static File Mount**: `/data` → `processed_json/` directory

**Usage Example**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### getHailData.py
**Purpose**: Core data loading functionality for weather event data
**Usage**: Loads and processes weather event data from CSV files

**Key Functions**:
- `load_points_from_csv()`: Loads weather event points from CSV files
- Data filtering and processing utilities
- Geographic coordinate handling

**Data Sources**: 
- Hail event data from CSV files
- Thunderstorm wind data
- County-level weather statistics

### detailedHailData.py
**Purpose**: KPI (Key Performance Indicator) calculation and summary endpoints
**Usage**: Provides detailed statistics and metrics for weather events

**API Endpoints**:
- `get_kpi_summary_for_year()`: Annual KPI summaries by peril type
- `get_detailed_kpi_data()`: Detailed KPI breakdowns

**Key Features**:
- Year-based filtering
- Peril type categorization (HAIL, WIND, etc.)
- Statistical aggregations and calculations
- Data validation and error handling

### detailedTop3Counties.py
**Purpose**: County ranking and regional analysis functionality
**Usage**: Identifies and ranks counties by weather event frequency and severity

**API Functions**:
- `top3_counties()`: Returns top 3 counties for specific criteria
- Regional analysis and ranking algorithms
- County-level data aggregation

**Analysis Types**:
- Event frequency rankings
- Severity-based rankings
- Temporal trend analysis

### detailedOccurence.py
**Purpose**: Occurrence statistics and temporal analysis
**Usage**: Provides comprehensive occurrence data and yearly summaries

**API Functions**:
- `get_county_occurrences()`: County-level occurrence statistics
- `top_counties_all_years()`: Multi-year county rankings
- `yearly_summary()`: Annual summary statistics

**Data Processing**:
- Minimum event threshold filtering
- Multi-year trend analysis
- County comparison metrics

## Data Processing Scripts

### combine_wind_data.py
**Purpose**: Wind data aggregation and processing
**Usage**: Combines multiple wind data sources into unified datasets

**Key Features**:
- Multi-source data merging
- Wind speed and direction processing
- Temporal alignment of wind measurements
- Data quality validation

### combine_wind_stage_data.py
**Purpose**: Staged wind data processing for large datasets
**Usage**: Processes wind data in stages to handle memory constraints

**Processing Stages**:
- Initial data loading and validation
- Intermediate processing and filtering
- Final aggregation and output generation

### csv_to_json_event_code.py
**Purpose**: Data format conversion utility
**Usage**: Converts CSV weather event data to JSON format for API consumption

**Conversion Features**:
- CSV to JSON transformation
- Event code standardization
- Data structure optimization for API responses
- Error handling for malformed data

### save_csvs_as_jsons.py
**Purpose**: Batch CSV to JSON conversion utility
**Usage**: Converts multiple CSV files to JSON format for web serving

**Batch Processing**:
- Directory-level CSV processing
- Automated file discovery and conversion
- Output organization and naming
- Progress tracking and logging

## Utility Functions

### utility.py
**Purpose**: Common utility functions and helper methods
**Usage**: Provides shared functionality across the backend application

**Common Functions**:
- Data validation utilities
- Geographic coordinate processing
- Date/time manipulation functions
- File I/O helper methods
- Error handling utilities

## API Endpoint Reference

The FastAPI server provides the following endpoints (examples):

### KPI Endpoints
- `GET /api/kpi-summary?year=2025&peril_type=HAIL`
  - Returns KPI summary for specified year and peril type
  - Parameters: year (int), peril_type (string)

- `GET /api/detailed-kpi?year=2025`
  - Returns detailed KPI data for specified year
  - Parameters: year (int)

### County Analysis Endpoints
- `GET /api/top3-counties?year=2025`
  - Returns top 3 counties by event frequency for specified year
  - Parameters: year (int)

- `GET /api/county-occurrences?min_events=50`
  - Returns counties with minimum event threshold
  - Parameters: min_events (int)

### Summary Endpoints
- `GET /api/yearly-summary?year=2026`
  - Returns comprehensive yearly summary statistics
  - Parameters: year (int)

- `GET /api/top-counties-alltime?top_n=5`
  - Returns top N counties across all years
  - Parameters: top_n (int)

### Static Data Access
- `GET /data/{filename}.json`
  - Direct access to processed JSON files
  - Served from processed_json/ directory

## Deployment Configuration

### Virtual Machine Setup
The backend is designed to run on Google Cloud Platform VMs:

**Recommended Specifications**:
- OS: Ubuntu 22.04 LTS
- Machine type: e2-medium or higher
- Boot disk: 20 GB minimum
- Network: HTTP/HTTPS traffic enabled

### Dependencies
```bash
pip install fastapi uvicorn google-cloud-storage
```

### Environment Variables
- Google Cloud credentials for storage access
- Firebase frontend URL for CORS configuration

### Running the Server
```bash
# Development (local access only)
uvicorn main:app --host 127.0.0.1 --port 8000

# Production (external access)
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Data Flow Architecture

1. **Data Processing Pipeline**:
   - Raw weather data → Processing scripts → Processed JSON files
   - CSV files → Conversion utilities → JSON format
   - Wind data → Aggregation scripts → Combined datasets

2. **API Request Flow**:
   - React frontend → HTTP requests → FastAPI server
   - API endpoints → Data processing modules → Database/file access
   - Processed data → JSON response → Frontend display

3. **Static File Serving**:
   - Direct file access via `/data/` mount point
   - Processed JSON files served without API processing
   - Optimized for large dataset downloads

## Integration with Frontend

The VMfiles backend integrates with the React application through:

### Authentication
- CORS configuration for Firebase-hosted frontend
- Support for localhost development servers

### Data Formats
- Standardized JSON response formats
- GeoJSON support for mapping components
- Time-series data structures for charts

### Performance Optimization
- Static file serving for large datasets
- Efficient API endpoints for real-time queries
- Caching-friendly response structures

## Development and Testing

### Local Development
1. Set up Python virtual environment
2. Install dependencies from requirements.txt
3. Configure Google Cloud credentials
4. Run FastAPI server with auto-reload

### Testing
- API endpoint testing with FastAPI's built-in documentation
- Integration testing with React frontend
- Data validation and error handling tests

### Monitoring
- FastAPI automatic API documentation at `/docs`
- Request logging and error tracking
- Performance monitoring for data processing

## Maintenance Notes

### Data Updates
- Regular updates to processed JSON files
- Batch processing for large dataset updates
- Version control for data processing scripts

### API Versioning
- Endpoint versioning strategy for frontend compatibility
- Backward compatibility considerations
- API documentation maintenance

### Security Considerations
- CORS origin validation
- Input parameter validation
- File access security for static serving
- Google Cloud credential management

---

*This documentation covers the VMfiles backend API server that provides data services for the ForecastTX weather forecasting platform. For frontend integration details, refer to webapp-directory.md.*