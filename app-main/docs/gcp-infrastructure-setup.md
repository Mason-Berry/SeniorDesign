# Google Cloud Platform Infrastructure Setup

## Overview
This guide provides comprehensive setup instructions for all Google Cloud Platform components required for the ForecastTX project, including PostgreSQL with PostGIS, materialized views, virtual machines, storage buckets, and service accounts with proper permissions.

---

## 1. Initial GCP Project Setup

### 1.1 Create and Configure Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project:
   - Click "Select a project" → "New Project"
   - Project name: `forecasttx-production` (or your choice)
   - **Note the Project ID** - you'll need this throughout setup
3. Enable billing (required for most services)
4. Set up billing alerts to monitor costs

### 1.2 Enable Required APIs
Navigate to "APIs & Services" → "Library" and enable these APIs:
```bash
# Essential APIs
gcloud services enable compute.googleapis.com
gcloud services enable storage.googleapis.com  
gcloud services enable sqladmin.googleapis.com
gcloud services enable servicenetworking.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
```

Or via Console:
- Compute Engine API
- Cloud Storage API  
- Cloud SQL Admin API
- Service Networking API
- Container Registry API
- Cloud Build API
- Secret Manager API
- Cloud Monitoring API
- Cloud Logging API

---

## 2. PostgreSQL with PostGIS Setup

### 2.1 Create Cloud SQL PostgreSQL Instance

#### Via Console:
1. Go to "SQL" in Cloud Console
2. Click "Create Instance" → "PostgreSQL"
3. Configure instance:
   - **Instance ID**: `forecasttx-postgres`
   - **Password**: Set a strong root password
   - **Version**: PostgreSQL 15 (latest stable)
   - **Region**: Choose closest to your users (e.g., `us-central1`)
   - **Zone**: `us-central1-a` (or your preferred zone)

#### Machine Configuration:
- **Machine type**: `db-custom-2-8192` (2 vCPU, 8GB RAM - adjust based on needs)
- **Storage**: 
  - Type: SSD
  - Size: 100GB (will auto-expand)
  - Enable automatic storage increases

#### Connectivity:
- **Private IP**: Enable (more secure)
- **Public IP**: Enable if you need external access
- **Authorized networks**: Add your development IP addresses

#### Backup:
- **Automated backups**: Enable
- **Point-in-time recovery**: Enable
- **Backup window**: Choose a low-traffic time (e.g., 3:00 AM)

#### Via gCloud CLI:
```bash
# Set variables
PROJECT_ID="your-project-id"
INSTANCE_NAME="forecasttx-postgres"
REGION="us-central1"
ZONE="us-central1-a"

# Create instance
gcloud sql instances create $INSTANCE_NAME \
    --database-version=POSTGRES_15 \
    --cpu=2 \
    --memory=8GB \
    --storage-size=100GB \
    --storage-type=SSD \
    --storage-auto-increase \
    --region=$REGION \
    --availability-type=zonal \
    --backup-start-time=03:00 \
    --enable-point-in-time-recovery \
    --project=$PROJECT_ID
```

### 2.2 Configure Database and PostGIS

#### Connect to PostgreSQL:
```bash
# Set root password
gcloud sql users set-password postgres \
    --instance=$INSTANCE_NAME \
    --password=YOUR_SECURE_PASSWORD

# Connect via Cloud Shell or psql
gcloud sql connect $INSTANCE_NAME --user=postgres
```

#### Create Database and Enable PostGIS:
```sql
-- Create main database
CREATE DATABASE forecasttx_db;

-- Connect to the database
\c forecasttx_db;

-- Enable PostGIS extension
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION postgis_raster;
CREATE EXTENSION fuzzystrmatch;
CREATE EXTENSION postgis_tiger_geocoder;

-- Verify PostGIS installation
SELECT PostGIS_Version();
```

#### Create Application User:
```sql
-- Create application user
CREATE USER forecasttx_app WITH ENCRYPTED PASSWORD 'your_app_password';

-- Grant necessary permissions
GRANT CONNECT ON DATABASE forecasttx_db TO forecasttx_app;
GRANT USAGE ON SCHEMA public TO forecasttx_app;
GRANT CREATE ON SCHEMA public TO forecasttx_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO forecasttx_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO forecasttx_app;

-- Grant permissions on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT ALL PRIVILEGES ON TABLES TO forecasttx_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT ALL PRIVILEGES ON SEQUENCES TO forecasttx_app;
```

### 2.3 Create Database Schema

#### Counties Table with PostGIS:
```sql
-- Texas counties table with geometry
CREATE TABLE tx_counties (
    id SERIAL PRIMARY KEY,
    county_name VARCHAR(100) NOT NULL,
    county_fips VARCHAR(5) NOT NULL UNIQUE,
    state_fips VARCHAR(2) DEFAULT '48', -- Texas FIPS code
    geometry GEOMETRY(MULTIPOLYGON, 4326),
    area_sq_km DECIMAL(10,2),
    population INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial index
CREATE INDEX idx_tx_counties_geometry ON tx_counties USING GIST (geometry);

-- Create regular indexes
CREATE INDEX idx_tx_counties_fips ON tx_counties (county_fips);
CREATE INDEX idx_tx_counties_name ON tx_counties (county_name);
```

#### Weather Data Tables:
```sql
-- Weather events table
CREATE TABLE weather_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL, -- 'HAIL', 'WIND', 'TORNADO', etc.
    event_date DATE NOT NULL,
    event_time TIME,
    county_fips VARCHAR(5) REFERENCES tx_counties(county_fips),
    location GEOMETRY(POINT, 4326),
    magnitude DECIMAL(6,2), -- hail size, wind speed, etc.
    damage_category VARCHAR(10), -- F0-F5 for tornadoes, etc.
    description TEXT,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Spatial and temporal indexes
CREATE INDEX idx_weather_events_location ON weather_events USING GIST (location);
CREATE INDEX idx_weather_events_date ON weather_events (event_date);
CREATE INDEX idx_weather_events_type ON weather_events (event_type);
CREATE INDEX idx_weather_events_county ON weather_events (county_fips);

-- ERA5 gridded weather data
CREATE TABLE era5_weather_data (
    id SERIAL PRIMARY KEY,
    data_date DATE NOT NULL,
    data_hour SMALLINT NOT NULL, -- 0-23
    grid_point GEOMETRY(POINT, 4326) NOT NULL,
    temperature_2m DECIMAL(5,2), -- Celsius
    wind_u_10m DECIMAL(6,3), -- m/s
    wind_v_10m DECIMAL(6,3), -- m/s
    surface_pressure DECIMAL(8,2), -- Pa
    total_precipitation DECIMAL(8,5), -- m
    -- Add other ERA5 variables as needed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient querying
CREATE INDEX idx_era5_date_hour ON era5_weather_data (data_date, data_hour);
CREATE INDEX idx_era5_location ON era5_weather_data USING GIST (grid_point);

-- Partitioning by year for performance (optional)
-- CREATE TABLE era5_weather_data_2024 PARTITION OF era5_weather_data
-- FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### 2.4 Create Materialized Views

#### County Weather Summary View:
```sql
-- Materialized view for county weather statistics
CREATE MATERIALIZED VIEW county_weather_summary AS
SELECT 
    c.county_name,
    c.county_fips,
    we.event_type,
    EXTRACT(YEAR FROM we.event_date) as year,
    COUNT(*) as event_count,
    AVG(we.magnitude) as avg_magnitude,
    MAX(we.magnitude) as max_magnitude,
    MIN(we.event_date) as first_event,
    MAX(we.event_date) as last_event
FROM tx_counties c
LEFT JOIN weather_events we ON c.county_fips = we.county_fips
WHERE we.event_date >= '1950-01-01'
GROUP BY c.county_name, c.county_fips, we.event_type, EXTRACT(YEAR FROM we.event_date)
ORDER BY c.county_name, year, we.event_type;

-- Create indexes on materialized view
CREATE INDEX idx_county_summary_county ON county_weather_summary (county_fips);
CREATE INDEX idx_county_summary_year ON county_weather_summary (year);
CREATE INDEX idx_county_summary_type ON county_weather_summary (event_type);

-- Refresh schedule (run this periodically)
-- REFRESH MATERIALIZED VIEW CONCURRENTLY county_weather_summary;
```

#### Monthly Weather Aggregation View:
```sql
-- Monthly aggregated weather data
CREATE MATERIALIZED VIEW monthly_weather_stats AS
SELECT 
    EXTRACT(YEAR FROM data_date) as year,
    EXTRACT(MONTH FROM data_date) as month,
    ST_SnapToGrid(grid_point, 0.25) as grid_cell, -- 0.25 degree grid
    AVG(temperature_2m) as avg_temperature,
    AVG(surface_pressure) as avg_pressure,
    SUM(total_precipitation) as total_precipitation,
    AVG(SQRT(wind_u_10m^2 + wind_v_10m^2)) as avg_wind_speed,
    COUNT(*) as data_points
FROM era5_weather_data
GROUP BY year, month, ST_SnapToGrid(grid_point, 0.25)
ORDER BY year, month;

-- Indexes
CREATE INDEX idx_monthly_stats_year_month ON monthly_weather_stats (year, month);
CREATE INDEX idx_monthly_stats_grid ON monthly_weather_stats USING GIST (grid_cell);
```

#### Top Counties by Event Type View:
```sql
-- Top counties by weather events (for API endpoints)
CREATE MATERIALIZED VIEW top_counties_by_events AS
SELECT 
    event_type,
    county_fips,
    county_name,
    total_events,
    avg_magnitude,
    ROW_NUMBER() OVER (PARTITION BY event_type ORDER BY total_events DESC) as rank
FROM (
    SELECT 
        we.event_type,
        c.county_fips,
        c.county_name,
        COUNT(*) as total_events,
        AVG(we.magnitude) as avg_magnitude
    FROM weather_events we
    JOIN tx_counties c ON we.county_fips = c.county_fips
    WHERE we.event_date >= '1950-01-01'
    GROUP BY we.event_type, c.county_fips, c.county_name
) county_stats
ORDER BY event_type, rank;

CREATE INDEX idx_top_counties_type_rank ON top_counties_by_events (event_type, rank);
```

### 2.5 Set Up Automated Refresh Jobs

#### Create refresh function:
```sql
-- Function to refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_weather_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY county_weather_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_weather_stats;
    REFRESH MATERIALIZED VIEW CONCURRENTLY top_counties_by_events;
    
    -- Log refresh
    INSERT INTO view_refresh_log (refresh_time, status) 
    VALUES (CURRENT_TIMESTAMP, 'SUCCESS');
EXCEPTION
    WHEN OTHERS THEN
        INSERT INTO view_refresh_log (refresh_time, status, error_message) 
        VALUES (CURRENT_TIMESTAMP, 'ERROR', SQLERRM);
END;
$$ LANGUAGE plpgsql;

-- Create log table
CREATE TABLE view_refresh_log (
    id SERIAL PRIMARY KEY,
    refresh_time TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. Virtual Machine Setup

### 3.1 Create Compute Engine VM

#### Backend API Server VM:
```bash
# Set variables
VM_NAME="forecasttx-backend"
ZONE="us-central1-a"
MACHINE_TYPE="e2-standard-2"  # 2 vCPU, 8GB RAM

# Create VM instance
gcloud compute instances create $VM_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --boot-disk-size=50GB \
    --boot-disk-type=pd-ssd \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --metadata=enable-oslogin=true \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=http-server,https-server,fastapi-server
```

#### ML Training VM (with GPU):
```bash
# Create GPU-enabled VM for model training
VM_NAME_GPU="forecasttx-ml-training"

gcloud compute instances create $VM_NAME_GPU \
    --zone=$ZONE \
    --machine-type=n1-standard-4 \
    --accelerator=type=nvidia-tesla-t4,count=1 \
    --boot-disk-size=100GB \
    --boot-disk-type=pd-ssd \
    --image-family=pytorch-latest-gpu \
    --image-project=deeplearning-platform-release \
    --metadata="install-nvidia-driver=True" \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=ml-training \
    --preemptible  # Cost savings for training workloads
```

### 3.2 Configure VM Networking

#### Create firewall rules:
```bash
# Allow FastAPI server traffic
gcloud compute firewall-rules create allow-fastapi \
    --allow tcp:8000 \
    --source-ranges 0.0.0.0/0 \
    --target-tags fastapi-server \
    --description "Allow FastAPI server on port 8000"

# Allow HTTP/HTTPS traffic
gcloud compute firewall-rules create allow-web-traffic \
    --allow tcp:80,tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server,https-server \
    --description "Allow web traffic"

# Allow SSH (if not already enabled)
gcloud compute firewall-rules create allow-ssh \
    --allow tcp:22 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow SSH access"
```

### 3.3 VM Initialization Script

Create startup script for automatic VM configuration:

```bash
#!/bin/bash
# startup-script.sh - Run on VM startup

# Update system
apt-get update && apt-get upgrade -y

# Install Python and dependencies
apt-get install -y python3.11 python3.11-pip python3.11-venv
apt-get install -y git curl wget unzip

# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
source ~/.bashrc

# Install Docker (for containerized deployments)
apt-get install -y docker.io
systemctl enable docker
systemctl start docker
usermod -aG docker $USER

# Install PostgreSQL client tools
apt-get install -y postgresql-client-15

# Create application directory
mkdir -p /opt/forecasttx
chown $USER:$USER /opt/forecasttx

# Install NGINX for reverse proxy
apt-get install -y nginx
systemctl enable nginx

# Configure log rotation
cat > /etc/logrotate.d/forecasttx << EOF
/opt/forecasttx/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 $USER $USER
}
EOF

echo "VM initialization complete"
```

Apply startup script:
```bash
gcloud compute instances add-metadata $VM_NAME \
    --metadata-from-file startup-script=startup-script.sh
```

---

## 4. Cloud Storage Setup

### 4.1 Create Storage Buckets

#### Main data bucket:
```bash
# Set variables
BUCKET_PREFIX="forecasttx-$(date +%s)"  # Ensure uniqueness
REGION="us-central1"

# Create primary data bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://${BUCKET_PREFIX}-data

# Create backup bucket
gsutil mb -p $PROJECT_ID -c NEARLINE -l $REGION gs://${BUCKET_PREFIX}-backups

# Create model artifacts bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://${BUCKET_PREFIX}-models

# Create temporary processing bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://${BUCKET_PREFIX}-temp
```

### 4.2 Configure Bucket Structure

```bash
# Create directory structure in main data bucket
DATA_BUCKET="gs://${BUCKET_PREFIX}-data"

# ERA5 raw data
gsutil -m cp /dev/null $DATA_BUCKET/era5-raw/.keep
gsutil -m cp /dev/null $DATA_BUCKET/era5-processed/.keep

# API JSON data
gsutil -m cp /dev/null $DATA_BUCKET/api-json/.keep

# Database backups
gsutil -m cp /dev/null $DATA_BUCKET/db-backups/.keep

# Application logs
gsutil -m cp /dev/null $DATA_BUCKET/logs/.keep
```

### 4.3 Set Bucket Permissions and Lifecycle

#### Lifecycle configuration:
```json
# lifecycle.json
{
  "rule": [
    {
      "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
      "condition": {"age": 30, "matchesStorageClass": ["STANDARD"]}
    },
    {
      "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
      "condition": {"age": 90, "matchesStorageClass": ["NEARLINE"]}
    },
    {
      "action": {"type": "Delete"},
      "condition": {"age": 365, "matchesPrefix": ["temp/", "logs/"]}
    }
  ]
}
```

Apply lifecycle:
```bash
gsutil lifecycle set lifecycle.json $DATA_BUCKET
```

#### Bucket permissions:
```bash
# Make processed data publicly readable (for web access)
gsutil iam ch allUsers:objectViewer $DATA_BUCKET/api-json/

# Grant service account access
gsutil iam ch serviceAccount:forecasttx-service@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin $DATA_BUCKET
```

---

## 5. Service Accounts and IAM Setup

### 5.1 Create Service Accounts

#### Main application service account:
```bash
# Create service account
gcloud iam service-accounts create forecasttx-service \
    --display-name="ForecastTX Application Service Account" \
    --description="Service account for ForecastTX application components"

SA_EMAIL="forecasttx-service@$PROJECT_ID.iam.gserviceaccount.com"
```

#### ML training service account:
```bash
# Create ML service account
gcloud iam service-accounts create forecasttx-ml \
    --display-name="ForecastTX ML Training Service Account" \
    --description="Service account for machine learning training jobs"

ML_SA_EMAIL="forecasttx-ml@$PROJECT_ID.iam.gserviceaccount.com"
```

### 5.2 Assign IAM Roles

#### Main service account permissions:
```bash
# Storage permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.admin"

# Cloud SQL permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudsql.client"

# Compute Engine permissions (for VM management)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/compute.instanceAdmin"

# Monitoring and logging
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/monitoring.metricWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/logging.logWriter"

# Secret Manager (for storing sensitive config)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/secretmanager.secretAccessor"
```

#### ML service account permissions:
```bash
# Storage for training data and models
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$ML_SA_EMAIL" \
    --role="roles/storage.admin"

# Cloud SQL read access for training data
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$ML_SA_EMAIL" \
    --role="roles/cloudsql.client"

# AI Platform for model training
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$ML_SA_EMAIL" \
    --role="roles/aiplatform.user"

# Monitoring and logging
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$ML_SA_EMAIL" \
    --role="roles/monitoring.metricWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$ML_SA_EMAIL" \
    --role="roles/logging.logWriter"
```

### 5.3 Generate Service Account Keys

```bash
# Generate key for main service account
gcloud iam service-accounts keys create forecasttx-service-key.json \
    --iam-account=$SA_EMAIL

# Generate key for ML service account  
gcloud iam service-accounts keys create forecasttx-ml-key.json \
    --iam-account=$ML_SA_EMAIL

# Secure the key files
chmod 600 *.json
```

**⚠️ Important**: Store these JSON files securely and never commit them to version control.

---

## 6. Secrets Management

### 6.1 Store Sensitive Configuration

```bash
# Store database connection string
gcloud secrets create postgres-connection-string \
    --data-file=- <<< "postgresql://forecasttx_app:your_password@private-ip:5432/forecasttx_db"

# Store API keys
gcloud secrets create cds-api-key \
    --data-file=- <<< "your_uid:your_cds_api_key"

# Store Firebase configuration
cat > firebase-config.json << EOF
{
  "apiKey": "your-firebase-api-key",
  "authDomain": "your-project.firebaseapp.com",
  "projectId": "your-project-id"
}
EOF
gcloud secrets create firebase-config --data-file=firebase-config.json
rm firebase-config.json

# Grant access to service accounts
gcloud secrets add-iam-policy-binding postgres-connection-string \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding cds-api-key \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/secretmanager.secretAccessor"
```

---

## 7. Monitoring and Logging Setup

### 7.1 Create Monitoring Dashboard

```bash
# Create custom metrics for application monitoring
gcloud logging metrics create weather_api_requests \
    --description="Count of weather API requests" \
    --log-filter='resource.type="gce_instance" AND "FastAPI"'

gcloud logging metrics create database_connections \
    --description="Database connection count" \
    --log-filter='resource.type="cloudsql_database" AND "connection"'
```

### 7.2 Set Up Alerting

```bash
# Create notification channel (email)
gcloud alpha monitoring channels create \
    --display-name="ForecastTX Alerts" \
    --type=email \
    --channel-labels=email_address=your-email@example.com

# Create alert policy for high error rate
gcloud alpha monitoring policies create \
    --policy-from-file=alert-policy.yaml
```

Example alert policy (alert-policy.yaml):
```yaml
displayName: "High Error Rate Alert"
conditions:
  - displayName: "API Error Rate"
    conditionThreshold:
      filter: 'resource.type="gce_instance"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.1
notificationChannels:
  - projects/PROJECT_ID/notificationChannels/CHANNEL_ID
```

---

## 8. Backup and Disaster Recovery

### 8.1 Database Backup Strategy

```bash
# Automated database backup (already configured during instance creation)
# Manual backup for specific points in time:
gcloud sql backups create \
    --instance=$INSTANCE_NAME \
    --description="Pre-deployment backup"

# Export database to Cloud Storage
gcloud sql export sql $INSTANCE_NAME gs://${BUCKET_PREFIX}-backups/database-export-$(date +%Y-%m-%d).sql \
    --database=forecasttx_db
```

### 8.2 Application Data Backup

```bash
# Backup processed data
gsutil -m rsync -r -d gs://${BUCKET_PREFIX}-data gs://${BUCKET_PREFIX}-backups/data-backup-$(date +%Y-%m-%d)

# Backup application configuration
gsutil cp -r /opt/forecasttx/config gs://${BUCKET_PREFIX}-backups/config-backup-$(date +%Y-%m-%d)
```

---

## 9. Network Security

### 9.1 VPC and Private Network Setup

```bash
# Create custom VPC
gcloud compute networks create forecasttx-vpc \
    --subnet-mode=custom \
    --description="ForecastTX private network"

# Create subnet
gcloud compute networks subnets create forecasttx-subnet \
    --network=forecasttx-vpc \
    --range=10.0.0.0/24 \
    --region=$REGION

# Create private service connection for Cloud SQL
gcloud services vpc-peerings connect \
    --service=servicenetworking.googleapis.com \
    --ranges=google-managed-services-default \
    --network=forecasttx-vpc
```

### 9.2 SSL/TLS Configuration

```bash
# Create SSL certificate for domain
gcloud compute ssl-certificates create forecasttx-ssl-cert \
    --domains=your-domain.com \
    --global

# Create HTTPS load balancer (if needed)
gcloud compute url-maps create forecasttx-loadbalancer \
    --default-backend-bucket=your-static-bucket
```

---

## 10. Infrastructure Validation

### 10.1 Connection Testing

```bash
# Test database connection
gcloud sql connect $INSTANCE_NAME --user=forecasttx_app

# Test VM SSH access
gcloud compute ssh $VM_NAME --zone=$ZONE

# Test storage access
gsutil ls gs://${BUCKET_PREFIX}-data

# Test service account authentication
gcloud auth activate-service-account --key-file=forecasttx-service-key.json
gcloud projects describe $PROJECT_ID
```

### 10.2 Performance Testing

```sql
-- Test PostGIS functionality
SELECT PostGIS_Version();

-- Test spatial query performance
EXPLAIN ANALYZE SELECT * FROM tx_counties WHERE ST_Contains(geometry, ST_Point(-97.7431, 30.2672));

-- Test materialized view refresh time
\timing
REFRESH MATERIALIZED VIEW county_weather_summary;
```

---

## 11. Cost Optimization

### 11.1 Resource Right-Sizing

```bash
# Monitor resource usage
gcloud monitoring dashboards list
gcloud compute instances describe $VM_NAME --zone=$ZONE

# Set up preemptible instances for non-critical workloads
gcloud compute instances create forecasttx-batch-processor \
    --preemptible \
    --machine-type=n1-standard-2 \
    --zone=$ZONE
```

### 11.2 Budget Alerts

```bash
# Create budget with alerts
gcloud billing budgets create \
    --billing-account=BILLING_ACCOUNT_ID \
    --display-name="ForecastTX Monthly Budget" \
    --budget-amount=100USD \
    --threshold-rules-percent=50,80,100
```

---

## 12. Deployment Checklist

### ✅ Complete Infrastructure Setup Checklist:

#### GCP Project Setup:
- [ ] Project created with billing enabled
- [ ] All required APIs enabled
- [ ] Budget alerts configured

#### Database Setup:
- [ ] Cloud SQL PostgreSQL instance created
- [ ] PostGIS extensions installed
- [ ] Database schema deployed
- [ ] Materialized views created
- [ ] Automated backup configured

#### Compute Resources:
- [ ] Backend VM created and configured
- [ ] ML training VM created (if needed)
- [ ] Firewall rules configured
- [ ] SSH access verified

#### Storage:
- [ ] All required buckets created
- [ ] Bucket permissions configured
- [ ] Lifecycle policies applied
- [ ] Directory structure created

#### Security:
- [ ] Service accounts created
- [ ] IAM roles assigned correctly
- [ ] Service account keys generated
- [ ] Secrets stored in Secret Manager

#### Monitoring:
- [ ] Logging configured
- [ ] Monitoring dashboard created
- [ ] Alert policies configured
- [ ] Notification channels set up

#### Networking:
- [ ] VPC and subnets configured (if using private networking)
- [ ] Private service connection established
- [ ] SSL certificates created (if needed)

#### Backup & Recovery:
- [ ] Database backup verified
- [ ] Application data backup configured
- [ ] Disaster recovery plan documented

This comprehensive GCP infrastructure setup provides a production-ready environment for the ForecastTX weather forecasting platform with proper security, monitoring, and scalability considerations.