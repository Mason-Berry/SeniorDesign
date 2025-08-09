# detailedHailData.py
from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from utility import engine

def get_kpi_summary_for_year(year, peril_type='HAIL'):
    """
    Get KPI summary data for a specific year and peril type
    This matches the structure expected by your React KPIContainer
    
    Args:
        year (int): Specific year to filter by (2025-2030)
        peril_type (str): 'HAIL' or 'THUNDERSTORM' (for future thunderstorm support)
    
    Returns:
        dict: KPI summary data matching your React component needs
    """
    try:
        with engine.connect() as conn:
            if peril_type == 'HAIL':
                # Get aggregated KPI data for hail
                kpi_query = text("""
                    SELECT 
                        SUM(Total_Hail_Events) as total_events,
                        MIN(Average_Hail_Magnitude) as lowest_magnitude,
                        AVG(Average_Hail_Magnitude) as avg_magnitude,
                        MAX(Maximum_Hail_Magnitude) as max_magnitude,
                        COUNT(*) as location_count
                    FROM hail_kpi_scorecards
                    WHERE year = :year
                """)
                
                result = conn.execute(kpi_query, {"year": year}).mappings().first()
                
                if not result or result["total_events"] is None:
                    return {
                        "success": True,
                        "year": year,
                        "peril_type": peril_type,
                        "total_events": "0.00",
                        "lowest_magnitude": "0.00",
                        "avg_magnitude": "0.00",
                        "max_magnitude": "0.00",
                        "location_count": 0
                    }
                
                return {
                    "success": True,
                    "year": year,
                    "peril_type": peril_type,
                    "total_events": f"{float(result['total_events']):.2f}",
                    "lowest_magnitude": f"{float(result['lowest_magnitude']):.2f}",
                    "avg_magnitude": f"{float(result['avg_magnitude']):.2f}",
                    "max_magnitude": f"{float(result['max_magnitude']):.2f}",
                    "location_count": result["location_count"]
                }
                
            elif peril_type == 'THUNDERSTORM':
                # Placeholder for future thunderstorm implementation

                kpi_query = text("""
                    SELECT 
                        SUM(total_thunderstorm_events) as total_events,
                        MIN(average_thunderstorm_magnitude) as lowest_magnitude,
                        AVG(average_thunderstorm_magnitude) as avg_magnitude,
                        MAX(maximum_thunderstorm_magnitude) as max_magnitude,
                        COUNT(*) as location_count
                    FROM thunderstorm_kpi_scorecards
                    WHERE year = :year
                """)

                result = conn.execute(kpi_query, {"year": year}).mappings().first()

                if not result or result["total_events"] is None:
                   return {
                        "success": True,
                        "year": year,
                        "peril_type": peril_type,
                        "total_events": "0.00",
                        "lowest_magnitude": "0.00",
                        "avg_magnitude": "0.00",
                        "max_magnitude": "0.00",
                        "location_count": 0
                    }

                return {
                    "success": True,
                    "year": year,
                    "peril_type": peril_type,
		    "total_events": f"{float(result['total_events']):.2f}",
                    "lowest_magnitude": f"{float(result['lowest_magnitude']):.2f}",
                    "avg_magnitude": f"{float(result['avg_magnitude']):.2f}",
                    "max_magnitude": f"{float(result['max_magnitude']):.2f}",
                    "location_count": result["location_count"]
                }

            else:
                return {
                    "success": False,
                    "error": "Invalid peril type. Use 'HAIL' or 'THUNDERSTORM'",
                    "year": year,
                    "peril_type": peril_type
                }
                
    except SQLAlchemyError as e:
        print(f"❌ Failed to fetch KPI summary data: {e}")
        return {
            "success": False,
            "error": "Query failed",
            "message": str(e),
            "year": year,
            "peril_type": peril_type
        }

def get_detailed_kpi_data(year, peril_type='HAIL'):
    """
    Get detailed location-level KPI data for mapping/visualization
    
    Args:
        year (int): Specific year to filter by (2025-2030)
        peril_type (str): 'HAIL' or 'THUNDERSTORM'
    
    Returns:
        dict: Detailed KPI data with coordinates
    """
    try:
        with engine.connect() as conn:
            if peril_type == 'HAIL':
                detail_query = text("""
                    SELECT 
                        year, long, lat,
                        Average_Hail_Magnitude,
                        Total_Hail_Events,
                        Maximum_Hail_Magnitude
                    FROM hail_kpi_scorecards
                    WHERE year = :year
                    ORDER BY Average_Hail_Magnitude DESC
                """)
                
                result = conn.execute(detail_query, {"year": year}).mappings().all()
                
                if not result:
                    return {
                        "success": True,
                        "year": year,
                        "peril_type": peril_type,
                        "data": []
                    }
                
                # Convert to list format
                detailed_data = []
                for row in result:
                    detailed_data.append({
                        "year": row["year"],
                        "longitude": row["long"],
                        "latitude": row["lat"],
                        "average_magnitude": float(row["Average_Hail_Magnitude"]) if row["Average_Hail_Magnitude"] else 0,
                        "total_events": row["Total_Hail_Events"],
                        "maximum_magnitude": float(row["Maximum_Hail_Magnitude"]) if row["Maximum_Hail_Magnitude"] else 0
                    })
                
                return {
                    "success": True,
                    "year": year,
                    "peril_type": peril_type,
                    "total_records": len(detailed_data),
                    "data": detailed_data
                }
                
            else:
                return {
                    "success": False,
                    "error": "Thunderstorm detailed data not implemented yet",
                    "year": year,
                    "peril_type": peril_type
                }
                
    except SQLAlchemyError as e:
        print(f"❌ Failed to fetch detailed KPI data: {e}")
        return {
            "success": False,
            "error": "Query failed",
            "message": str(e),
            "year": year,
            "peril_type": peril_type
        }

# Example usage functions
if __name__ == "__main__":
    # Get KPI summary for 2025 hail data (matches your React component needs)
    summary_2025 = get_kpi_summary_for_year(year=2025, peril_type='HAIL')
    print("2025 Hail KPI Summary:", summary_2025)
    
    for year in range(2026, 2031):
        summary = get_kpi_summary_for_year(year=year, peril_type='HAIL')
        print(f"{year} Hail KPI Summary:", summary)

    # Get detailed data for mapping
    detailed_2025 = get_detailed_kpi_data(year=2025, peril_type='HAIL')
    print("2025 Detailed Data Records:", detailed_2025["total_records"] if detailed_2025["success"] else "Failed")
    
    thunder_2025 = get_kpi_summary_for_year(year=2025, peril_type='THUNDERSTORM')
    print("2025 Hail KPI Summary:", thunder_2025)

    # Get top 3 countes
    top3_counties = get_top3_counties(year=2025, peril_type='HAIL')
    print("2025 top 3 hail counties: ", top3_counties)
