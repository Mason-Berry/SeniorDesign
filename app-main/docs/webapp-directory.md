# Webapp Directory Documentation

## Overview
This directory contains the web application frontend and related JavaScript utilities for the ForecastTX weather forecasting platform.

## Directory Structure

### React/forcasttx/
Main React application for the ForecastTX dashboard and user interface.

### js/
JavaScript utilities and tools for development support.

## React/forcasttx/ Application

### Core Application Files

#### README.md
**Purpose**: Documentation for the React application
**Content**: Setup instructions, project structure, and feature overview for the ForecastTX React app

#### package.json
**Purpose**: Node.js package configuration and dependencies
**Key Dependencies**:
- **UI Frameworks**: React 19.0.0, Bootstrap 5.3.6, Tailwind CSS 4.0.14
- **Mapping**: Leaflet 1.9.4, React-Leaflet 5.0.0, D3.js 7.9.0
- **Weather Visualization**: Various Leaflet plugins (heat maps, time dimension, velocity)
- **Charts**: Chart.js 4.4.8, React-ChartJS-2
- **Authentication**: Firebase 11.6.1
- **Export**: jsPDF, html2canvas, html-docx-js
- **AI Integration**: OpenAI 4.91.1

**Scripts**:
- `npm start`: Development server
- `npm build`: Production build
- `npm test`: Run tests
- `npm run lint`: Code linting

#### src/App.js
**Purpose**: Main application router and component orchestration
**Routes**:
- `/` - Landing page
- `/login` - User authentication
- `/create-account` - Account creation
- `/dashboard` - Main application dashboard

### Component Structure

#### src/Components/
**Purpose**: React components organized by functionality

**Main Components**:
- **Landing.jsx**: Welcome page with auto-redirect
- **Login.jsx**: User authentication interface
- **CreateAccount.jsx**: Account registration with email authorization
- **Dashboard.jsx**: Main application interface with tabbed sections
- **Profile.jsx**: User profile management

**Dashboard Components**:
- **Dashboard/OverviewSection.jsx**: High-level weather overview and predictions
- **Dashboard/DetailedSection.jsx**: Detailed weather analysis and metrics
- **Dashboard/Export/Export.jsx**: Data export functionality
- **Dashboard/TabSection.jsx**: Navigation between dashboard sections

**Dashboard Sub-components**:

*Overview Components*:
- **CitySelect.jsx**: City/location selection interface
- **FilterSection.jsx**: Data filtering controls
- **MLRegression.jsx**: Machine learning prediction display
- **MapContainer.jsx**: Interactive map container
- **OverviewCharts.jsx**: Summary charts and visualizations
- **TexasMap.jsx**: Texas-specific geographical display
- **PastVsAi.jsx**: Historical vs AI prediction comparison
- **PerilSelect.jsx**: Weather peril type selection
- **SeasonSelect.jsx**: Seasonal data filtering
- **YearSelect.jsx**: Temporal data selection

*Detailed Components*:
- **Analysis.jsx**: In-depth weather analysis
- **DetailedHeader.jsx**: Detailed section navigation
- **HeatmapChart.jsx**: Heat map visualizations
- **KPI.jsx**: Key performance indicators
- **KPIContainer.jsx**: KPI layout management
- **TopRegions.jsx**: Regional analysis display
- **TopRegionsContainer.jsx**: Regional data organization

#### src/styles/
**Purpose**: CSS modules and styling for components

**Organization**:
- **Dashboard/**: Dashboard-specific styles
- **auth.css**: Authentication page styling
- **landing.css**: Landing page styling
- **login.css**: Login form styling
- **Profile.css**: User profile styling

**Styling Approach**: CSS Modules for component-scoped styling with Bootstrap and Tailwind CSS utilities

#### src/assets/
**Purpose**: Static assets including images and animations

**Contents**:
- Weather-related GIF animations
- Logo files (ForecastTX.png, statefarm-logo.png)
- UI icons and graphics
- Menu and user interface elements

#### public/
**Purpose**: Static public assets and configuration

**Key Files**:
- **index.html**: Application entry point
- **counties.json**: County boundary data
- **texas.json**: Texas geographical data
- **tx_counties.geojson**: Texas county GeoJSON data
- **assets/Data/**: CSV data files for hail and thunderstorm wind data
- **favicon.ico**: Browser icon
- **manifest.json**: PWA configuration
- **firebase.json**: Firebase hosting configuration

### Build and Configuration

#### Build System
- **React Scripts 5.0.1**: Standard React build tooling
- **ESLint**: Code quality and consistency
- **Babel**: JavaScript transpilation
- **PostCSS/Autoprefixer**: CSS processing

#### Firebase Integration
- **firebase.js**: Firebase configuration for authentication and hosting
- **firebase.json**: Deployment configuration

#### Development Files
- **eslint.config.mjs**: ESLint configuration
- **try.js**: Development testing file

## js/ Directory

### reviewCode.js
**Purpose**: AI-powered code review utility using OpenAI GPT
**Usage**: Automated code analysis and improvement suggestions

**Features**:
- Integrates with OpenAI GPT-3.5-turbo
- Reads code files and provides analysis
- Suggests improvements and identifies issues
- Requires OPENAI_API_KEY environment variable

**Usage Example**:
```javascript
reviewCode('path/to/code/file.js')
```

## Application Features

### Weather Forecasting Dashboard
- Interactive Texas map with county-level data
- Historical weather data visualization
- Machine learning prediction displays
- Multi-peril analysis (hail, wind, etc.)
- Seasonal and temporal filtering
- Export capabilities (PDF, DOCX, images)

### User Management
- Firebase-based authentication
- Email authorization for account creation
- User profile management
- Session handling

### Data Visualization
- Chart.js integration for statistical displays
- Leaflet maps with weather overlays
- D3.js for custom visualizations
- Heat maps and geographical analysis
- Time-series data presentation

### Technical Architecture
- React 19 with hooks and modern patterns
- CSS Modules with Bootstrap/Tailwind integration
- Firebase backend services
- RESTful API integration
- Responsive design for multiple devices

## Development Workflow

1. **Setup**: `npm install` to install dependencies
2. **Development**: `npm start` for local development server
3. **Testing**: `npm test` for unit testing
4. **Linting**: `npm run lint` for code quality checks
5. **Build**: `npm run build` for production deployment
6. **Deploy**: Firebase hosting integration for deployment

## Future Enhancements (from README)
- Backend authentication improvements
- Enhanced ML algorithm integration
- Advanced dashboard features
- Improved UI/UX with animations
- Better mobile responsiveness