from fastapi import FastAPI,Query
from fastapi.middleware.cors import CORSMiddleware
from getHailData import load_points_from_csv
from fastapi.staticfiles import StaticFiles
from google.cloud import storage
from fastapi.responses import JSONResponse
import time
from detailedHailData import get_kpi_summary_for_year, get_detailed_kpi_data
from detailedTop3Counties import top3_counties
from detailedOccurence import get_county_occurrences, top_counties_all_years, yearly_summary

app = FastAPI()

# Allow requests from your Firebase frontend domain here kevin
origins = [
    "https://argon-edge-455015-q8.web.app",
    "http://localhost",           # for local testing
    "http://localhost:3000",      # adjust port if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # or use ["*"] to allow all (less secure)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/data", StaticFiles(directory="processed_json"), name="data")


@app.get("/")
def read_root():
    return {"message": "Hail Forecast API is running", "status": "healthy"}

# detailedHailData.py
# Updated KPI endpoint that uses your detailedHailData functions
@app.get("/api/kpi-summary")
def get_kpi_summary(
    year: int = Query(..., description="Year to get KPI data for (2025-2030)"),
    peril_type: str = Query("HAIL", description="Peril type: HAIL or THUNDERSTORM")
):
    """
    Get KPI summary data for a specific year and peril type
    """
    print(f"📊 Getting KPI summary for year: {year}, peril: {peril_type}")
    
    data = get_kpi_summary_for_year(year=year, peril_type=peril_type)
    
    print(f"📦 KPI summary result: {data}")
    return data

#Update top 3 counties endpoint to use 
@app.get("/api/top3-counties")
def get_top3_counties(
    year: int = Query(..., description="Year to get top3 counties data for (2025-2030)"),
    peril_type: str = Query("HAIL", description="Peril type: HAIL or THUNDERSTORM")
):
    """
    Get KPI summary data for a specific year and peril type
    """
    print(f" Getting Top 3 Counties summary for year: {year}, peril: {peril_type}")
    
    data = top3_counties(year=year, peril_type=peril_type)
    
    print(f"Top3 Counties summary result: {data}")
    return data


@app.get("/api/county-occurrences")
def get_county_occurrences_api(
    year: int = Query(None, description="Filter by specific year (optional)"),
    county: str = Query(None, description="Filter by specific county name (optional)"),
    top_n: int = Query(None, description="Get top N counties by event count (optional)"),
    min_events: int = Query(None, description="Filter counties with at least this many events (optional)")
):
    """
    Get county event occurrence data with various filtering options
    
    Examples:
    - /api/county-occurrences?year=2025&top_n=10 (Top 10 counties for 2025)
    - /api/county-occurrences?county=Harris (All years for Harris County)
    - /api/county-occurrences?min_events=50 (All counties with 50+ events)
    - /api/county-occurrences?year=2025&min_events=20 (Counties with 20+ events in 2025)
    """
    print(f"🏘️ Getting county occurrences - year: {year}, county: {county}, top_n: {top_n}, min_events: {min_events}")
    
    data = get_county_occurrences(
        year=year,
        county=county,
        top_n=top_n,
        min_events=min_events
    )
    
    print(f"📋 County occurrences result: Found {data.get('count', 0)} records")
    return data

# New endpoint for top counties across all years
@app.get("/api/top-counties-alltime")
def get_top_counties_alltime(
    top_n: int = Query(10, description="Number of top counties to return (default: 10)")
):
    """
    Get top counties by total event count across all years with aggregated statistics
    
    Returns counties with total events, years active, average events per year, etc.
    """
    print(f"🏆 Getting top {top_n} counties across all years")
    
    data = top_counties_all_years(top_n=top_n)
    
    print(f"🎯 Top counties all-time result: Found {data.get('count', 0)} records")
    return data

# New endpoint for yearly summary statistics
@app.get("/api/yearly-summary")
def get_yearly_summary_api(
    year: int = Query(None, description="Specific year to analyze (optional - if not provided, returns overall stats)")
):
    """
    Get summary statistics for a specific year or overall statistics
    
    Examples:
    - /api/yearly-summary?year=2025 (Summary for 2025)
    - /api/yearly-summary (Overall summary across all years)
    """
    print(f"📈 Getting yearly summary for year: {year if year else 'all years'}")
    
    data = yearly_summary(year=year)
    
    print(f"📊 Yearly summary result: {data}")
    return data
