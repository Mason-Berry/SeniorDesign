# ForecastTX Documentation

Welcome to the ForecastTX project documentation! This comprehensive documentation will guide you through setting up, configuring, and running the entire weather forecasting platform.

## 📋 Documentation Overview

This documentation is designed to help anyone recreate and run the ForecastTX project from scratch. The guides are organized from general overview to specific implementation details.

## 🚀 Getting Started - Read These First!

If you're new to this project, follow this sequence:

### 1. 📖 Start Here
- **[`project-overview.md`](project-overview.md)** - Read this first to understand the entire system

### 2. 🔧 Setup External Services  
- **[`external-services-setup.md`](external-services-setup.md)** - Set up all required accounts (CDS, Google Cloud, Firebase)
- **[`gcp-infrastructure-setup.md`](gcp-infrastructure-setup.md)** - Complete GCP infrastructure including PostgreSQL with PostGIS
- **[`configuration-templates.md`](configuration-templates.md)** - Configure all account-specific settings

### 3. 📚 Learn the System
- **[`root-directory.md`](root-directory.md)** - Understand the project structure
- **[`scripts-directory.md`](scripts-directory.md)** - Data processing pipeline
- **[`model-directory.md`](model-directory.md)** - Machine learning components  
- **[`webapp-directory.md`](webapp-directory.md)** - React frontend
- **[`vmfiles-directory.md`](vmfiles-directory.md)** - Backend API

### 4. 🛠️ Run the System
- **[`detailed-script-usage.md`](detailed-script-usage.md)** - Step-by-step instructions for every script

## 📁 Documentation Structure

```
docs/
├── README.md (this file)              # Documentation guide
├── project-overview.md                # High-level system overview
├── external-services-setup.md         # Account setup guide  
├── gcp-infrastructure-setup.md        # Complete GCP infrastructure setup
├── configuration-templates.md         # Configuration templates
├── detailed-script-usage.md          # Detailed usage instructions
├── root-directory.md                 # Root directory files
├── scripts-directory.md              # Data processing scripts
├── model-directory.md               # Machine learning models
├── webapp-directory.md              # React web application
└── vmfiles-directory.md             # Backend API server
```

## 🎯 Quick Navigation by Task

### I want to understand the project
👉 Start with [`project-overview.md`](project-overview.md)

### I want to set up accounts and services
👉 Follow [`external-services-setup.md`](external-services-setup.md)

### I want to download weather data
👉 See [`detailed-script-usage.md`](detailed-script-usage.md) Section 1

### I want to process weather data  
👉 See [`detailed-script-usage.md`](detailed-script-usage.md) Section 2

### I want to train machine learning models
👉 See [`detailed-script-usage.md`](detailed-script-usage.md) Section 3

### I want to run the web application
👉 See [`webapp-directory.md`](webapp-directory.md) and [`detailed-script-usage.md`](detailed-script-usage.md)

### I want to deploy the backend API
👉 See [`vmfiles-directory.md`](vmfiles-directory.md) and [`external-services-setup.md`](external-services-setup.md)

### I need to configure accounts and credentials  
👉 Use [`configuration-templates.md`](configuration-templates.md)

## ⚡ Quick Start Checklist

For a complete setup, you need to:

### External Accounts Setup
- [ ] Copernicus Climate Data Store (CDS) account for weather data
- [ ] Google Cloud Platform (GCP) account for storage and compute
- [ ] Firebase account for web hosting and authentication

### Local Environment Setup  
- [ ] Python environment with required packages
- [ ] Node.js environment for React development
- [ ] Git repository cloned locally

### Configuration Files
- [ ] CDS API credentials (`.cdsapirc`)
- [ ] Google Cloud service account key (JSON file)
- [ ] Firebase configuration updated in React app
- [ ] Environment variables configured (`.env` file)

### Data Directories
- [ ] Raw data directory for downloaded files
- [ ] Processed data directory for pipeline output
- [ ] Model data directory for training files
- [ ] API data directory for JSON files

## 🔍 Troubleshooting

### Common Issues

**"I can't download weather data"**
- Check CDS API setup in [`external-services-setup.md`](external-services-setup.md)
- Verify `.cdsapirc` configuration

**"Google Cloud authentication failed"**  
- Check service account setup in [`external-services-setup.md`](external-services-setup.md)
- Verify `GOOGLE_APPLICATION_CREDENTIALS` environment variable

**"React app won't connect to Firebase"**
- Check Firebase configuration in [`configuration-templates.md`](configuration-templates.md)
- Verify all Firebase environment variables

**"Backend API CORS errors"**
- Update CORS origins in VMfiles/main.py
- See [`vmfiles-directory.md`](vmfiles-directory.md) for details

**"Machine learning models out of memory"**
- Reduce batch sizes in model configuration
- See hardware optimization in [`detailed-script-usage.md`](detailed-script-usage.md)

### Getting Help

1. **Check the specific documentation** for the component you're working with
2. **Review error messages** against troubleshooting sections
3. **Verify configuration** using templates in [`configuration-templates.md`](configuration-templates.md)
4. **Check account setup** in [`external-services-setup.md`](external-services-setup.md)

## 📋 System Requirements

### Hardware Requirements
- **For data processing**: 8GB+ RAM, 100GB+ storage
- **For machine learning**: GPU with 8GB+ VRAM (RTX 4090 recommended)
- **For web development**: 4GB+ RAM, basic graphics

### Software Requirements  
- **Python 3.11+** with conda/pip
- **Node.js 18+** with npm
- **Git** for version control
- **Google Cloud SDK** (optional, for advanced features)

### Account Requirements
- **CDS API**: Free account for weather data access
- **Google Cloud**: Account with $300 free credits
- **Firebase**: Free tier sufficient for development

## 🎓 Learning Path

### For Students/Researchers
1. Read [`project-overview.md`](project-overview.md) to understand the science
2. Follow [`scripts-directory.md`](scripts-directory.md) to understand data processing
3. Study [`model-directory.md`](model-directory.md) for machine learning approaches

### For Developers
1. Read [`project-overview.md`](project-overview.md) for system architecture
2. Follow [`webapp-directory.md`](webapp-directory.md) for frontend details
3. Review [`vmfiles-directory.md`](vmfiles-directory.md) for backend API

### For System Administrators
1. Follow [`external-services-setup.md`](external-services-setup.md) for infrastructure
2. Use [`configuration-templates.md`](configuration-templates.md) for deployment
3. Review [`detailed-script-usage.md`](detailed-script-usage.md) for operations

## 📞 Support

This documentation is designed to be comprehensive and self-contained. If you follow the guides in order, you should be able to recreate the entire ForecastTX system successfully.

### Documentation Feedback
If you find gaps in the documentation or have suggestions for improvement, please note them for future updates.

---

**Happy forecasting! 🌩️⚡🌪️**