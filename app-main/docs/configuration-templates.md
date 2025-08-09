# Configuration Templates and Environment Variables

## Overview
This document provides templates for all configuration files and environment variables needed to run the ForecastTX project with your own accounts and credentials.

---

## 1. Environment Variables Template

### Create .env file in project root:
```bash
# ==========================================
# COPERNICUS CLIMATE DATA STORE (CDS) API
# ==========================================
# Get from: https://cds.climate.copernicus.eu/user
CDS_API_URL=https://cds.climate.copernicus.eu/api/v2
CDS_API_KEY=your_uid:your_api_key

# ==========================================
# GOOGLE CLOUD PLATFORM
# ==========================================
# Project ID from GCP Console
GCP_PROJECT_ID=your-project-id

# Path to your service account JSON file
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-service-account-key.json

# Cloud Storage bucket name (must be globally unique)
GCS_BUCKET_NAME=your-project-era5-data-bucket

# Compute Engine VM details
GCP_VM_ZONE=us-central1-a
GCP_VM_NAME=forecasttx-backend

# ==========================================
# FIREBASE CONFIGURATION
# ==========================================
# Get from Firebase Console > Project Settings > Web Apps
REACT_APP_FIREBASE_API_KEY=your-firebase-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
REACT_APP_FIREBASE_APP_ID=your-app-id
REACT_APP_FIREBASE_MEASUREMENT_ID=your-measurement-id

# ==========================================
# BACKEND API CONFIGURATION
# ==========================================
# Development
REACT_APP_API_BASE_URL=http://localhost:8000

# Production (update with your VM's external IP)
# REACT_APP_API_BASE_URL=http://YOUR-VM-EXTERNAL-IP:8000

# FastAPI server host and port
API_HOST=0.0.0.0
API_PORT=8000

# ==========================================
# DATA PROCESSING PATHS
# ==========================================
# Local data storage paths (adjust to your system)
RAW_DATA_DIR=/path/to/your/raw-grib-data
PROCESSED_DATA_DIR=/path/to/your/processed-data
MODEL_DATA_DIR=/path/to/your/model-data
API_DATA_DIR=/path/to/your/api-json-data

# ==========================================
# MODEL TRAINING CONFIGURATION
# ==========================================
# Hardware-specific settings
GPU_MEMORY_LIMIT=24000  # MB, adjust for your GPU
MAX_BATCH_SIZE=64       # Reduce if out of memory
USE_MIXED_PRECISION=true

# Training data years
TRAIN_START_YEAR=1955
TRAIN_END_YEAR=2015
VAL_START_YEAR=2016
VAL_END_YEAR=2019

# ==========================================
# DEVELOPMENT SETTINGS
# ==========================================
DEBUG=true
LOG_LEVEL=INFO
ENABLE_CORS=true
```

---

## 2. CDS API Configuration

### ~/.cdsapirc Template:
```ini
url: https://cds.climate.copernicus.eu/api/v2
key: YOUR_UID:YOUR_API_KEY
```

**How to get your key:**
1. Register at https://cds.climate.copernicus.eu/
2. Go to your user profile page
3. Copy the UID and API key
4. Replace YOUR_UID and YOUR_API_KEY above

---

## 3. Firebase Configuration Template

### webapp/React/forcasttx/src/firebase.js:
```javascript
// src/firebase.js
import { initializeApp } from "firebase/app";
import {
  getAuth,
  GoogleAuthProvider,
  OAuthProvider,
  connectAuthEmulator,
} from "firebase/auth";

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY || "your-api-key",
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN || "your-project.firebaseapp.com",
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID || "your-project-id",
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET || "your-project.firebasestorage.app",
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID || "your-sender-id",
  appId: process.env.REACT_APP_FIREBASE_APP_ID || "your-app-id",
  measurementId: process.env.REACT_APP_FIREBASE_MEASUREMENT_ID || "your-measurement-id"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Auth emulator for development
const useAuthEmulator =
  window.location.hostname === "localhost" &&
  process.env.REACT_APP_USE_AUTH_EMULATOR === "true";

if (useAuthEmulator) {
  connectAuthEmulator(auth, "http://localhost:9099");
}

// Providers
const googleProvider = new GoogleAuthProvider();
const microsoftProvider = new OAuthProvider("microsoft.com");

export {
  app,
  auth,
  googleProvider,
  microsoftProvider
};
```

---

## 4. Backend API Configuration Template

### VMfiles/main.py CORS Configuration:
```python
# Update origins with your domains
origins = [
    # Production Firebase hosting URLs
    f"https://{os.getenv('REACT_APP_FIREBASE_PROJECT_ID', 'your-project')}.web.app",
    f"https://{os.getenv('REACT_APP_FIREBASE_PROJECT_ID', 'your-project')}.firebaseapp.com",
    
    # Development servers
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    
    # Add your custom domains here
    # "https://your-custom-domain.com",
]

# Static files directory
static_files_dir = os.getenv('API_DATA_DIR', 'processed_json')
app.mount("/data", StaticFiles(directory=static_files_dir), name="data")
```

---

## 5. Google Cloud Service Account Template

### Creating and configuring service account:

1. **Create service account JSON template**:
```json
{
  "type": "service_account",
  "project_id": "YOUR_PROJECT_ID",
  "private_key_id": "GENERATED_KEY_ID",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com",
  "client_id": "GENERATED_CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs/your-service-account%40YOUR_PROJECT_ID.iam.gserviceaccount.com"
}
```

2. **Required IAM roles for service account**:
   - Storage Admin
   - Compute Engine Admin  
   - Editor

---

## 6. Model Configuration Templates

### model_code/phase1_model.py Configuration:
```python
# ===== CONFIGURATION SECTION - UPDATE THESE PATHS =====

# Path to your processed numpy data files
PROCESSED_DATA_DIR = os.getenv('MODEL_DATA_DIR', "/path/to/your/model/data/")

# Training parameters (adjust for your hardware)
BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', 64))
USE_MIXED_PRECISION = os.getenv('USE_MIXED_PRECISION', 'true').lower() == 'true'

# Data split years
TRAIN_YEARS_START = int(os.getenv('TRAIN_START_YEAR', 1955))
TRAIN_YEARS_END = int(os.getenv('TRAIN_END_YEAR', 2015))
VAL_YEARS_START = int(os.getenv('VAL_START_YEAR', 2016))
VAL_YEARS_END = int(os.getenv('VAL_END_YEAR', 2019))

# Model save path
MODEL_SAVE_PATH = os.path.join(PROCESSED_DATA_DIR, "local_model/convlstm_feature_predictor_full_dataset.keras")

# ===== END CONFIGURATION SECTION =====
```

### model_code/phase2_model.py Configuration:
```python
# ===== CONFIGURATION SECTION - UPDATE THESE PATHS =====

# Paths to data directories
FEATURE_DATA_DIR = os.getenv('MODEL_DATA_DIR', "/path/to/phase1/data/")
TARGET_DATA_DIR = os.getenv('MODEL_DATA_DIR', "/path/to/phase2/targets/")

# Training parameters
BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', 32))  # Smaller for Phase 2
USE_MIXED_PRECISION = False  # More stable for classification

# Model save path
MODEL_SAVE_PATH = os.path.join(TARGET_DATA_DIR, "multi_output_event_classifier_model.keras")

# ===== END CONFIGURATION SECTION =====
```

---

## 7. Data Processing Script Configuration Templates

### scripts/get_data3.py Custom Configuration:
```json
{
  "variables": [
    "2m_temperature",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "surface_pressure",
    "total_precipitation"
  ],
  "area": [36.5, -106.6, 25.8, -93.5],
  "time": ["00:00", "06:00", "12:00", "18:00"],
  "format": "grib",
  "output_dir": "data/custom/"
}
```

### scripts/era5-data-joiner.py Configuration:
```python
# Default excluded variables (customize as needed)
DEFAULT_EXCLUDED_VARS = [
    '10fg',    # 10m wind gust (if not needed)
    'cbh',     # Cloud base height (if problematic)
    'cin',     # Convective inhibition (if not used)
    'cp',      # Convective precipitation (if duplicate)
    'i10fg',   # Instantaneous 10m wind gust
    'lsp',     # Large-scale precipitation (if duplicate)
    'tp',      # Total precipitation (if using cp and lsp separately)
    'vimd'     # Vertically integrated moisture divergence
]

# Memory optimization settings
MAX_MEMORY_ROWS = int(os.getenv('MAX_MEMORY_ROWS', 30000))
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 10000))
```

---

## 8. Development vs Production Configuration

### .env.development:
```bash
# Development settings
DEBUG=true
LOG_LEVEL=DEBUG
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_USE_AUTH_EMULATOR=true
USE_MIXED_PRECISION=false
MAX_BATCH_SIZE=32
```

### .env.production:
```bash
# Production settings
DEBUG=false
LOG_LEVEL=INFO
REACT_APP_API_BASE_URL=https://your-vm-ip:8000
REACT_APP_USE_AUTH_EMULATOR=false
USE_MIXED_PRECISION=true
MAX_BATCH_SIZE=64
```

---

## 9. Directory Structure Template

### Create this directory structure:
```bash
# Create all required directories
mkdir -p data/{raw-grib,processed,models}
mkdir -p processed_json
mkdir -p model-output/{phase1,phase2}
mkdir -p logs
mkdir -p backups

# Set permissions (Linux/Mac)
chmod 755 data/
chmod 755 processed_json/
chmod 700 service-account-keys/  # Secure credentials
```

---

## 10. Validation Scripts

### validate_config.py - Check Configuration:
```python
#!/usr/bin/env python3
"""
Configuration validation script
Run this to verify all configurations are correct before starting
"""

import os
import json
from pathlib import Path

def validate_cds_config():
    """Check CDS API configuration"""
    cdsapirc_path = Path.home() / '.cdsapirc'
    if not cdsapirc_path.exists():
        print("❌ CDS API config missing: ~/.cdsapirc not found")
        return False
    
    with open(cdsapirc_path) as f:
        content = f.read()
        if 'url:' in content and 'key:' in content:
            print("✅ CDS API config found")
            return True
    return False

def validate_gcp_config():
    """Check Google Cloud configuration"""
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path or not Path(creds_path).exists():
        print("❌ GCP credentials missing")
        return False
    
    try:
        with open(creds_path) as f:
            creds = json.load(f)
            if 'project_id' in creds and 'client_email' in creds:
                print(f"✅ GCP credentials valid for project: {creds['project_id']}")
                return True
    except json.JSONDecodeError:
        print("❌ GCP credentials file is invalid JSON")
    return False

def validate_firebase_config():
    """Check Firebase configuration"""
    required_vars = [
        'REACT_APP_FIREBASE_API_KEY',
        'REACT_APP_FIREBASE_AUTH_DOMAIN',
        'REACT_APP_FIREBASE_PROJECT_ID'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"❌ Missing Firebase config: {', '.join(missing)}")
        return False
    
    print("✅ Firebase configuration found")
    return True

def validate_data_paths():
    """Check required data directories"""
    paths = [
        os.getenv('RAW_DATA_DIR', 'data'),
        os.getenv('PROCESSED_DATA_DIR', 'processed'),
        os.getenv('API_DATA_DIR', 'processed_json')
    ]
    
    for path in paths:
        if not Path(path).exists():
            print(f"❌ Data directory missing: {path}")
            return False
    
    print("✅ Data directories exist")
    return True

if __name__ == '__main__':
    print("🔍 Validating ForecastTX Configuration...")
    print("=" * 50)
    
    checks = [
        validate_cds_config(),
        validate_gcp_config(),
        validate_firebase_config(),
        validate_data_paths()
    ]
    
    if all(checks):
        print("\n🎉 All configurations are valid!")
        print("You can now run the ForecastTX project.")
    else:
        print("\n❌ Configuration issues found.")
        print("Please fix the issues above before running the project.")
        print("Refer to external-services-setup.md for help.")
```

### Run validation:
```bash
python validate_config.py
```

---

## Quick Setup Checklist

Before running any scripts, ensure you have:

- [ ] Created and configured `.env` file with all required variables
- [ ] Set up `~/.cdsapirc` with valid CDS API credentials  
- [ ] Downloaded and configured Google Cloud service account JSON
- [ ] Updated Firebase configuration in React app
- [ ] Created all required data directories
- [ ] Updated CORS origins in backend API
- [ ] Set proper file permissions for credential files
- [ ] Tested configuration with validation script

This configuration template ensures consistent setup across different environments and makes it easy for others to replicate your project setup.