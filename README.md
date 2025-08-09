# ForecastTX - Weather Forecasting Platform

## Portfolio Project Overview

This repository contains **ForecastTX**, a comprehensive weather forecasting and analysis platform that was developed as a senior capstone project for computer science students at The University of Texas at Dallas. The system combines machine learning, data processing, and web development to create an interactive weather prediction dashboard focused on severe weather events in Texas.

**⚠️ Important Disclaimer**: This repository represents a collaborative team project. While I contributed significantly to various components of the system, I am not the sole author of all code contained within this repository. This project is included in my portfolio to demonstrate my experience with large-scale software development, team collaboration, and full-stack development practices.

## My Contributions

As part of the development team, my primary responsibilities focused on **data acquisition, transformation, storage in Google Cloud, and preparation for model training**. My specific contributions included:

- **Data Processing Pipeline**: Development and optimization of Python scripts for processing ERA5 weather data
- **Data Acquisition & Transformation**: Implementation of automated systems for acquiring, cleaning, and transforming raw weather data
- **Cloud Infrastructure**: Google Cloud Platform integration and deployment configuration
- **Model Training Preparation**: Data preprocessing, feature engineering, and preparation of training datasets for machine learning models

## Project Purpose & Technical Scope

ForecastTX demonstrates enterprise-level software development practices across multiple domains:

### Technical Architecture
- **Data Engineering**: Automated processing of 70+ years of ERA5 climate reanalysis data
- **Machine Learning**: Deep learning models (ConvLSTM) for spatiotemporal weather prediction
- **Full-Stack Development**: React frontend with FastAPI backend services
- **Cloud Computing**: GCP integration with scalable storage and compute resources
- **DevOps**: Automated deployment pipelines and infrastructure management

### System Components
1. **Data Processing Pipeline** (`/scripts/`): Python-based ETL pipeline processing GRIB weather data
2. **Machine Learning Models** (`/model/`): TensorFlow/Keras models for weather forecasting
3. **Web Application** (`/webapp/React/`): Interactive React dashboard with real-time visualizations
4. **Backend API** (`/VMfiles/`): FastAPI server providing RESTful endpoints for data access
5. **Cloud Infrastructure**: GCP-hosted services with Firebase authentication

## Technology Stack

**Backend & Data Processing:**
- Python (pandas, numpy, xarray, tensorflow)
- FastAPI for REST API services
- Google Cloud Platform (Storage, Compute Engine)
- ERA5 climate data processing (GRIB format)

**Frontend & Web Development:**
- React 19 with modern hooks
- Chart.js and D3.js for data visualization
- Leaflet maps for geospatial display
- Firebase authentication and hosting

**Machine Learning & Analytics:**
- TensorFlow/Keras for deep learning
- ConvLSTM networks for spatiotemporal prediction
- Linear regression for statistical analysis
- GPU-optimized training on cloud instances

## Portfolio Relevance

This project showcases several key competencies valuable in professional software development:

- **Large-Scale Data Processing**: Handling and processing terabytes of climate data
- **Machine Learning Engineering**: Production-ready ML model development and deployment
- **Full-Stack Development**: End-to-end application development from data to user interface
- **Cloud Architecture**: Scalable cloud-native application design
- **Team Collaboration**: Working effectively in a multi-developer environment
- **Technical Documentation**: Comprehensive system documentation and user guides

## Academic Context

**Institution**: The University of Texas at Dallas  
**Course**: Senior Capstone Project  
**Duration**: Academic Year 2024-2025  
**Team Size**: 4-5 students  
**Industry Partner**: State Farm Insurance (project sponsor)

The project was developed in collaboration with State Farm to explore applications of machine learning in weather risk assessment and prediction.

## Repository Structure

```
├── app-main/
│   ├── scripts/          # Data processing pipeline
│   ├── model/           # Machine learning models
│   ├── webapp/React/    # Frontend application
│   ├── VMfiles/         # Backend API server
│   └── docs/            # Comprehensive documentation
```

## Documentation

The `/app-main/docs/` directory contains extensive documentation covering:
- System architecture and design decisions
- Setup and deployment instructions
- API documentation and usage examples
- Machine learning model specifications

For detailed technical information, see [`app-main/docs/project-overview.md`](app-main/docs/project-overview.md).

## Academic and Professional Use

This repository serves as a portfolio piece demonstrating:
- **Software Engineering**: Large-scale application architecture and development
- **Data Science**: Real-world application of ML to climate/weather data
- **Cloud Computing**: Production deployment of scalable web applications
- **Team Development**: Collaborative software development practices

## Additional Resources

For more information about this project, including a demo video and additional technical details, visit the [official school blog post](https://websites.uta.edu/cseseniordesign/2025/08/04/forecast-tx/).

---

*This project represents collaborative academic work and demonstrates technical competencies developed through hands-on experience with industry-relevant technologies and development practices.*