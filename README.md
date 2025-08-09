# ForecastTX – Weather Forecasting Platform

## 📑 Table of Contents
- [Overview](#overview)
- [⚠️ Collaboration & Disclaimer](#️-collaboration--disclaimer)
- [📌 My Contributions](#-my-contributions)
- [Project Purpose & Scope](#project-purpose--scope)
- [🛠 Technology Stack](#-technology-stack)
- [🎯 Portfolio Relevance](#-portfolio-relevance)
- [🎓 Academic Context](#-academic-context)
- [📂 Repository Structure](#-repository-structure)
- [📄 Documentation](#-documentation)
- [📺 Additional Resources](#-additional-resources)

---

## Overview

**ForecastTX** is a collaborative senior capstone project developed at The University of Texas at Arlington. The system integrates **machine learning**, **data engineering**, and **full-stack web development** to create an interactive dashboard for severe weather prediction in Texas.  

This project is included in my portfolio as a case study in **large-scale software development**, **team collaboration**, and **end-to-end delivery of cloud-based applications**.

---

## ⚠️ Collaboration & Disclaimer

This repository contains **team-developed academic work**. While I made substantial contributions, I am **not** the sole author of all code contained here.

- My specific work is detailed in the [My Contributions](#my-contributions) section below.
- No **State Farm proprietary data**, source code, or confidential business logic is included.
- All sensitive credentials have been removed; any datasets used are publicly available.
- State Farm served as the **project sponsor**, providing product requirements and feedback during weekly presentations, but did not contribute code or proprietary assets.

---

## 📌 My Contributions

As part of a 5-member team, my primary responsibilities included:

- **Data Processing Pipeline** – Developed and optimized Python scripts for processing ERA5 weather data.
- **Data Acquisition & Transformation** – Implemented automated retrieval, cleaning, and transformation of raw weather data.
- **Cloud Infrastructure** – Configured and deployed Google Cloud Platform services (storage, compute).
- **Comprehensive Documentation** – Authored and reviewed technical and project documentation.

---

## Project Purpose & Scope

ForecastTX demonstrates enterprise-level development practices across multiple domains:

### **Technical Architecture**
- **Data Engineering** – Automated processing of 70+ years of ERA5 reanalysis climate data.
- **Machine Learning** – ConvLSTM deep learning models for spatiotemporal weather prediction.
- **Full-Stack Development** – React frontend, FastAPI backend.
- **Cloud Computing** – GCP-hosted services with scalable storage and compute resources.
- **DevOps** – Automated deployment pipelines and infrastructure configuration.

### **System Components**
1. **Data Processing Pipeline** (`/scripts/`) – Python-based ETL pipeline for GRIB weather data.
2. **Machine Learning Models** (`/model/`) – TensorFlow/Keras models for severe weather forecasting.
3. **Web Application** (`/webapp/React/`) – Interactive dashboard with real-time visualizations.
4. **Backend API** (`/VMfiles/`) – FastAPI server with REST endpoints for frontend access.
5. **Cloud Infrastructure** – Hosted on Google Cloud; Firebase for authentication & hosting.

---

## 🛠 Technology Stack

**Backend & Data Processing:**
- Python (`pandas`, `numpy`, `xarray`, `tensorflow`)
- FastAPI for REST APIs
- Google Cloud Platform (Storage, Compute Engine)
- ERA5 climate data (GRIB format)

**Frontend & Visualization:**
- React 19 with hooks
- Chart.js and D3.js for visualizations
- Leaflet for geospatial mapping
- Firebase authentication and hosting

**Machine Learning:**
- TensorFlow/Keras
- ConvLSTM networks for spatiotemporal modeling
- Linear regression for statistical analysis
- GPU-optimized cloud training

---

## 🎯 Portfolio Relevance

This project highlights:
- **Large-Scale Data Processing** – Managing and transforming terabytes of climate data.
- **ML Engineering** – Building and deploying production-ready ML models.
- **Full-Stack Web Development** – End-to-end application delivery.
- **Cloud Architecture** – Designing scalable cloud-native solutions.
- **Team Collaboration** – Working in a multi-developer environment.
- **Technical Documentation** – Producing thorough, structured documentation.

---

## 🎓 Academic Context

| Attribute         | Details |
|-------------------|---------|
| **Institution**   | The University of Texas at Arlington |
| **Course**        | Senior Capstone Project |
| **Academic Year** | 2024–2025 |
| **Team Size**     | 5 students |
| **Sponsor**       | State Farm Insurance |

The project was sponsored by **State Farm** to explore the application of machine learning to weather risk assessment and prediction.

---

## 📂 Repository Structure

├── app-main/
│ ├── scripts/ # Data processing pipeline
│ ├── model/ # Machine learning models
│ ├── webapp/React/ # Frontend dashboard
│ ├── VMfiles/ # Backend API server
│ └── docs/ # Documentation

---
