# External Services Setup Guide

## Overview
This guide provides step-by-step instructions for setting up all external service accounts and API keys required to replicate the ForecastTX project. These services are essential for data download, storage, authentication, and deployment.

---

## 1. Copernicus Climate Data Store (CDS) Setup

### Purpose
The CDS API is required for downloading ERA5 reanalysis weather data used in the project.

### Step-by-Step Setup

#### 1.1 Create CDS Account
1. Go to [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/)
2. Click "Register" and create a new account
3. Verify your email address
4. Accept the Terms and Conditions

#### 1.2 Get API Credentials
1. Log into your CDS account
2. Go to your [user profile page](https://cds.climate.copernicus.eu/user/)
3. Scroll down to the "API key" section
4. Copy your UID and API key

#### 1.3 Configure CDS API
1. Install the CDS API client:
   ```bash
   pip install cdsapi
   ```

2. Create a `.cdsapirc` file in your home directory:
   ```bash
   # Linux/Mac
   nano ~/.cdsapirc
   
   # Windows
   notepad %USERPROFILE%\.cdsapirc
   ```

3. Add your credentials to the file:
   ```
   url: https://cds.climate.copernicus.eu/api/v2
   key: {UID}:{API_KEY}
   ```
   Replace `{UID}` and `{API_KEY}` with your actual values from step 1.2

#### 1.4 Test CDS API
Test your setup with this Python script:
```python
import cdsapi

c = cdsapi.Client()
print("CDS API configured successfully!")
```

### Usage in Project Scripts
The CDS API is used in:
- `get_data2.py`: Downloads ERA5 data for 1960-1964
- `scripts/get_data3.py`: Enhanced downloader with flexible configuration

**Example Usage:**
```bash
# Download data for specific year/month
python get_data2.py  # Downloads 1960-1964 by default

# Or use the enhanced version
python scripts/get_data3.py --year 2024 --month 01 --output_dir data/
```

---

## 2. Google Cloud Platform (GCP) Setup

### Purpose
GCP provides comprehensive cloud infrastructure including PostgreSQL with PostGIS, compute instances, storage, and authentication services for the project.

### Important Note
**For complete GCP infrastructure setup including PostgreSQL with PostGIS, materialized views, VMs, and all service accounts, see the comprehensive guide:**
👉 **[`gcp-infrastructure-setup.md`](gcp-infrastructure-setup.md)**

This section provides a quick overview. For production deployment, follow the detailed infrastructure guide.

### Quick Setup Overview

#### 2.1 Create GCP Account and Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign up for GCP (requires credit card, includes $300 free credits)
3. Create a new project:
   - Click "Select a project" → "New Project"
   - Enter project name (e.g., "forecasttx-project")
   - Note the Project ID (used in configurations)

#### 2.2 Essential Components to Set Up
**📋 For each component, refer to [`gcp-infrastructure-setup.md`](gcp-infrastructure-setup.md) for detailed instructions:**

1. **PostgreSQL with PostGIS Database**
   - Cloud SQL PostgreSQL 15 instance
   - PostGIS extensions for spatial data
   - Materialized views for performance
   - Automated backups and point-in-time recovery

2. **Virtual Machines**
   - Backend API server VM
   - ML training VM with GPU support
   - Proper firewall rules and networking

3. **Cloud Storage**
   - Multiple buckets for different data types
   - Lifecycle policies for cost optimization
   - Proper permissions and security

4. **Service Accounts & IAM**
   - Application service account
   - ML training service account
   - Granular permissions matrix
   - Secure key management

5. **Monitoring & Security**
   - Cloud monitoring and logging
   - Alert policies and notifications
   - Secret Manager for sensitive data
   - Network security and SSL/TLS

### Configuration in Project

#### Update Scripts with Your Project Details
Replace account-specific values in these files:

**1. `scripts/upload_year_range_to_gcs.sh`:**
```bash
# Change this line:
BUCKET_NAME="your-project-era5-data-bucket"  # Replace with your bucket name
```

**2. `model/model_code/phase1_model.py` and `phase2_model.py`:**
```python
# Update paths to your local data directory
PROCESSED_DATA_DIR = "/path/to/your/processed/data/"
```

**3. Set Environment Variable:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

---

## 3. Firebase Setup

### Purpose
Firebase provides user authentication and web hosting for the React frontend.

### Step-by-Step Setup

#### 3.1 Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project"
3. Enter project name (can reuse GCP project)
4. Enable Google Analytics (optional)
5. Click "Create project"

#### 3.2 Enable Authentication
1. In Firebase Console, go to "Authentication"
2. Click "Get started"
3. Go to "Sign-in method" tab
4. Enable desired providers:
   - Email/Password
   - Google (recommended)
   - Microsoft (if needed)

#### 3.3 Set Up Web App
1. In Firebase Console, click "Add app" → Web (</> icon)
2. Enter app nickname: `forecasttx-web`
3. Enable Firebase Hosting
4. Copy the configuration object

#### 3.4 Configure React App
Replace the Firebase configuration in `webapp/React/forcasttx/src/firebase.js`:

```javascript
const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.firebasestorage.app",
  messagingSenderId: "your-sender-id",
  appId: "your-app-id",
  measurementId: "your-measurement-id"  // Optional
};
```

#### 3.5 Set Up Hosting
1. Install Firebase CLI:
   ```bash
   npm install -g firebase-tools
   ```

2. Login to Firebase:
   ```bash
   firebase login
   ```

3. Initialize Firebase in your React app directory:
   ```bash
   cd webapp/React/forcasttx
   firebase init hosting
   ```

4. Configure `firebase.json`:
   ```json
   {
     "hosting": {
       "public": "build",
       "ignore": [
         "firebase.json",
         "**/.*",
         "**/node_modules/**"
       ],
       "rewrites": [
         {
           "source": "**",
           "destination": "/index.html"
         }
       ]
     }
   }
   ```

---

## 4. Backend API Server Setup (VMfiles)

### Purpose
The FastAPI backend serves data to the React frontend and requires specific CORS configuration.

### Configuration Steps

#### 4.1 Update CORS Origins
In `VMfiles/main.py`, update the origins list:

```python
origins = [
    "https://your-project.web.app",      # Your Firebase hosting URL
    "https://your-project.firebaseapp.com",  # Alternative Firebase URL
    "http://localhost",                   # Local development
    "http://localhost:3000",             # React development server
]
```

#### 4.2 Set Up VM Instance (Google Cloud)
1. Go to Compute Engine → VM instances
2. Click "Create instance"
3. Configure:
   - Name: `forecasttx-backend`
   - Machine type: `e2-medium` (or higher)
   - Boot disk: Ubuntu 22.04 LTS, 20GB
   - Firewall: Allow HTTP and HTTPS traffic
4. Click "Create"

#### 4.3 Configure Firewall Rules
```bash
# Allow traffic on port 8000
gcloud compute firewall-rules create allow-fastapi \
    --allow tcp:8000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow FastAPI server"
```

#### 4.4 Deploy Backend
1. SSH into your VM
2. Clone your repository
3. Set up Python environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install fastapi uvicorn google-cloud-storage
   ```
4. Set environment variables:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
   ```
5. Start the server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

---

## 5. Development Environment Setup

### Local Development Configuration

#### 5.1 Environment Variables
Create a `.env` file in your project root:
```bash
# CDS API
CDS_API_URL=https://cds.climate.copernicus.eu/api/v2
CDS_API_KEY=your_uid:your_api_key

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GCP_PROJECT_ID=your-project-id
GCS_BUCKET_NAME=your-bucket-name

# Firebase
REACT_APP_FIREBASE_API_KEY=your-firebase-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id

# Backend API
REACT_APP_API_BASE_URL=http://localhost:8000  # Local development
# REACT_APP_API_BASE_URL=https://your-vm-ip:8000  # Production
```

#### 5.2 Git Configuration
Add to `.gitignore`:
```
# Environment files
.env
.env.local
.env.production

# Service account keys
*service-account*.json
*.cdsapirc

# Firebase config (if not committed)
firebase-config.js
```

---

## 6. Data Directory Structure

### Required Local Directories
Create this directory structure on your local machine:

```
project-data/
├── raw-grib/              # Downloaded GRIB files from CDS
├── processed/             # Processed CSV/Parquet files
│   ├── organized/         # Output from era5-organized-converter.py
│   ├── joined/           # Output from era5-data-joiner.py
│   └── sorted/           # Output from era5-chronological-sorter.py
├── model-data/           # Training data for ML models
│   ├── numpy-files/      # .npy format data
│   ├── normalization/    # Statistics files
│   └── models/          # Saved model files
└── api-data/            # JSON files for API serving
    └── processed_json/   # Files served by FastAPI
```

---

## 7. Complete Setup Verification

### Test Each Component

#### 7.1 Test CDS API
```python
import cdsapi
c = cdsapi.Client()
# Should not raise errors
```

#### 7.2 Test Google Cloud Storage
```python
from google.cloud import storage
client = storage.Client()
buckets = list(client.list_buckets())
print(f"Found {len(buckets)} buckets")
```

#### 7.3 Test Firebase
```bash
cd webapp/React/forcasttx
npm start
# Should start without Firebase connection errors
```

#### 7.4 Test Backend API
```bash
curl http://your-vm-ip:8000/docs
# Should return FastAPI documentation page
```

---

## 8. Troubleshooting Common Issues

### CDS API Issues
- **Error**: "Invalid API key"
  - **Solution**: Check `.cdsapirc` format and credentials
- **Error**: "Request timeout"
  - **Solution**: Large data downloads take time; increase timeout or download smaller chunks

### Google Cloud Issues
- **Error**: "Authentication failed"
  - **Solution**: Check `GOOGLE_APPLICATION_CREDENTIALS` path and service account permissions
- **Error**: "Bucket not found"
  - **Solution**: Verify bucket name and ensure it exists in the correct project

### Firebase Issues
- **Error**: "Project not found"
  - **Solution**: Check project ID in firebase configuration
- **Error**: "Authentication domain invalid"
  - **Solution**: Verify authDomain matches your Firebase project

### Backend API Issues
- **Error**: "CORS policy blocked"
  - **Solution**: Update origins list in `main.py` with your frontend URL
- **Error**: "Port 8000 not accessible"
  - **Solution**: Check firewall rules and VM external IP configuration

---

## Summary Checklist

Before running the project, ensure you have:

- [ ] CDS account and API key configured
- [ ] GCP project with required APIs enabled
- [ ] Service account with appropriate permissions
- [ ] Cloud Storage bucket created
- [ ] Firebase project with authentication enabled
- [ ] Firebase hosting configured
- [ ] VM instance for backend deployment
- [ ] All environment variables set
- [ ] Required directory structure created
- [ ] All configuration files updated with your account details

This setup guide ensures that anyone can replicate your project infrastructure and run all components successfully.