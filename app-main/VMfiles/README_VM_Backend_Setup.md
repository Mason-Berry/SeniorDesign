# ForecastTX Backend Server Setup Guide

This guide outlines how to set up the backend FastAPI server for the ForecastTX project on a virtual machine (VM) using Google Cloud Platform (GCP). The server provides API endpoints for accessing weather prediction data.

---

## 🌐 Overview

- **Backend Framework**: FastAPI (Python)
- **Hosting**: Google Cloud VM
- **APIs Served**: Hail and thunderstorm statistics
- **Frontend**: Communicates via HTTP API requests
- **Storage**: JSON files and model outputs served from local disk or GCS

---

## 🔧 Step-by-Step VM Setup (GCP)

### 1. **Create a Virtual Machine**
Go to [GCP Console](https://console.cloud.google.com/), then:

- Navigate to **Compute Engine > VM Instances**
- Click **"Create Instance"**
- Recommended:
  - OS: Ubuntu 22.04 LTS
  - Machine type: `e2-medium` or higher
  - Boot disk: 20 GB minimum
  - Enable HTTP/HTTPS traffic if you want to expose the API
- Optionally assign a **static external IP**

---

### 2. **Connect to Your VM**
Use SSH from the Cloud Console or your terminal:

```bash
gcloud compute ssh <your-username>@<your-instance-name> --project=<your-gcp-project>
```

---

### 3. **Install System Dependencies**

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv unzip
```

---

## 📦 Python Environment Setup

### 1. **Create and Activate Virtual Environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. **Install Required Python Packages**

```bash
pip install fastapi uvicorn google-cloud-storage
```

If you have a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

---

## 🚀 Run the FastAPI Server

From the directory where `main.py` is located, run:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

To allow access from outside the VM, replace `127.0.0.1` with `0.0.0.0`:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

> You may need to configure your VM's firewall to allow TCP traffic on port 8000.

---

## 📁 Project Directory Structure

```
project/
│
├── main.py                      # FastAPI entrypoint
├── getHailData.py               # Load CSV/JSON weather data
├── detailedHailData.py          # KPI summary endpoints
├── detailedTop3Counties.py      # Top counties by events
├── detailedOccurence.py         # Yearly and county-level stats
├── utility.py                   # Misc helper functions
│
├── processed_json/              # Static files exposed at /data
├── modelOutput/                 # Model prediction output (optional)
├── testFolder/                  # Scripts for testing and exploration
│
├── venv/                        # Virtual environment (DO NOT COMMIT)
└── requirements.txt             # Python dependency list
```

---

## 🌐 CORS Configuration (in `main.py`)

FastAPI is configured to allow requests from:

- Your frontend domain (e.g., Firebase)
- `localhost:3000` for development

Update the `origins` list in `main.py` to reflect your deployment:

```python
origins = [
    "https://your-frontend.web.app",
    "http://localhost",
    "http://localhost:3000"
]
```

---

## 📤 Serving Static JSON Data

FastAPI mounts the `processed_json/` directory to be accessible at:

```
http://<your-vm-ip>:8000/data/yourfile.json
```

This is defined via:

```python
from fastapi.staticfiles import StaticFiles
app.mount("/data", StaticFiles(directory="processed_json"), name="data")
```

---

## 🧪 Example Endpoints

- `/api/kpi-summary?year=2025&peril_type=HAIL`
- `/api/top3-counties?year=2025`
- `/api/county-occurrences?min_events=50`
- `/api/yearly-summary?year=2026`
- `/api/top-counties-alltime?top_n=5`

---

## 📒 Notes

- Avoid uploading large files (e.g., virtual environments or SDKs) to version control.
- Always use `.gitignore` to exclude unnecessary files:
  ```
  __pycache__/
  *.pyc
  venv/
  *.tar.gz
  ```

---

## 📌 Deployment Tips

- Use `screen` or `tmux` if you need to keep `uvicorn` running after closing the terminal.
- Consider using a reverse proxy like **Nginx** for HTTPS access.
- Create a systemd service file if you want the server to start automatically on boot.

---

## 📞 Contact

For issues or setup questions, contact the ForecastTX backend team or consult FastAPI and GCP documentation.
