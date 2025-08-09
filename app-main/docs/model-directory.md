# Model Directory Documentation

## Overview
This directory contains machine learning models for weather forecasting, organized in development phases.

## Directory Structure

### model_code/
Contains the core machine learning model implementations for different phases of development.

### run_model/
Contains execution scripts for running trained models and generating forecasts.

### data/
Contains processed training data, model artifacts, and normalization statistics.

### model_keras/
Contains saved trained model files in Keras format.

## Files

### model_code/phase1_model.py
**Purpose**: TensorFlow/Keras ConvLSTM model for weather feature prediction
**Usage**: Trains a deep learning model to predict weather patterns using local ERA5 data

**Key Features**:
- **Model Architecture**: ConvLSTM2D layers with batch normalization
  - 3 ConvLSTM2D layers (64, 128, 64 filters)
  - Sequence-to-one prediction
  - Mixed precision training for RTX 4090 optimization

- **Data Processing**:
  - Loads gridded weather data from local numpy files
  - Processes 17 weather features (grid: 43x53)
  - Uses sequence length of 24 hours for prediction
  - Normalizes data using pre-calculated statistics

- **Training Configuration**:
  - Training period: 1955-2015
  - Validation period: 2016-2019
  - Batch size: 64 (optimized for RTX 4090 24GB VRAM)
  - Learning rate: 0.001
  - Max epochs: 100
  - Early stopping and learning rate reduction callbacks

- **Local Training Setup**:
  - Reads data from local processed .npy files
  - Mixed precision training for GPU optimization
  - Model saved locally as .keras file

**Dependencies**:
- TensorFlow/Keras for deep learning
- NumPy for data processing
- Mixed precision training support

**Usage Example**:
```bash
python model_code/phase1_model.py
```

**Model Output**: Saves trained model as `convlstm_feature_predictor_full_dataset.keras` locally

### model_code/phase2_model.py
**Purpose**: Multi-output event classification model for weather hazard prediction
**Usage**: Trains a deep learning classifier to predict weather event categories from Phase 1 features

**Key Features**:
- **Model Architecture**: Multi-output ConvLSTM classification
  - Predicts 4 different weather event classes
  - Uses Phase 1 model features as input
  - Class-weighted training for imbalanced datasets

- **Data Processing**:
  - Uses Phase 1 feature outputs as input
  - Loads target event data from separate numpy files
  - Handles multi-class weather event prediction
  - Sequence length: 24 hours matching Phase 1

- **Training Configuration**:
  - Training period: 1955-2015
  - Validation period: 2016-2019
  - Batch size: 32 (RTX 4090 optimized)
  - Learning rate: 0.001
  - Mixed precision: Disabled for stability

**Usage Example**:
```bash
python model_code/phase2_model.py
```

**Model Output**: Saves trained model as `multi_output_event_classifier_model.keras`

### run_model/p1/p1_run.py
**Purpose**: Forecasting script for Phase 1 model execution
**Usage**: Generates weather feature forecasts using trained Phase 1 ConvLSTM model

**Key Features**:
- Loads trained Phase 1 model for inference
- Generates multi-year weather forecasts (2025-2027)
- Uses historical data as seed sequence
- Outputs forecasted weather features as numpy arrays

**Configuration**:
- Sequence length: 24 hours
- Grid dimensions: 43x53
- Features: 17 weather variables
- Output: forecast_2025_to_2027.npy

**Usage Example**:
```bash
python run_model/p1/p1_run.py
```

### run_model/p1/p2_run.py
**Purpose**: Forecasting script for Phase 2 model execution
**Usage**: Generates weather event predictions using Phase 1 forecasts and trained Phase 2 model

**Key Features**:
- Uses Phase 1 forecast output as input
- Predicts weather event classifications
- Generates extended forecasts up to 2030
- Outputs event probability predictions

**Configuration**:
- Input: Phase 1 feature forecasts
- Output: Multi-class event predictions
- Classes: 4 weather event types
- Forecast period: Configurable (e.g., 2025-2030)

**Usage Example**:
```bash
python run_model/p1/p2_run.py
```

## Model Development Phases

### Phase 1: ConvLSTM Feature Prediction
- Focus on spatiotemporal weather pattern learning
- Uses convolutional LSTM for grid-based weather data
- Targets feature-level prediction for 17 weather variables
- Local training optimized for RTX 4090 GPU

### Phase 2: Multi-Output Event Classification
- Uses Phase 1 features as input for weather event prediction
- Multi-class classification for different weather hazards
- Class-weighted training for handling imbalanced event data
- Integrated forecasting pipeline with Phase 1

## Data Requirements
- Preprocessed ERA5 data in NumPy format stored locally
- Global grid dimension files (global_unique_lats.npy, global_unique_lons.npy)
- Pre-calculated normalization statistics for training efficiency
- Phase 2 target event data in NumPy format
- Seed sequences from most recent historical data

## Performance Considerations
- Optimized for RTX 4090 GPU (24GB VRAM)
- Memory-efficient data generators for large datasets
- GPU acceleration with mixed precision training (Phase 1)
- Checkpoint saving for training interruption recovery
- Local storage for models and training data
- Integrated forecasting pipeline between phases