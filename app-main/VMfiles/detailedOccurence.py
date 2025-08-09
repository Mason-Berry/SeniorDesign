from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from utility import engine

# Get detailed occurrence data by county and year
def get_county_occurrences(year=None, county=None, top_n=None, min_events=None, event_code=None):
    """
    Get county event occurrence data with various filtering options.
    
    Args:
        year (int, optional): Filter by specific year
        county (str, optional): Filter by specific county name
        top_n (int, optional): Get top N counties by event count
        min_events (int, optional): Filter counties with at least this many events
        event_code (int, optional): Filter by specific event code (e.g., 1 for events)
    
    Returns:
        dict: Dictionary containing success status, data, and count
    """
    try:
        with engine.connect() as conn:
            # Base query using the new materialized view
            base_query = """
                SELECT
                    year,
                    county,
                    state,
                    fips,
                    predicted_event_code,
                    occurrence_count,
                    avg_hail_magnitude,
                    avg_tstm_magnitude,
                    max_hail_magnitude,
                    max_tstm_magnitude
                FROM county_event_summary_by_year
                WHERE 1=1
            """
            
            params = {}
            conditions = []
            
            # Add year filter if provided
            if year is not None:
                conditions.append("AND year = :year")
                params["year"] = year
            
            # Add county filter if provided
            if county is not None:
                conditions.append("AND UPPER(county) = UPPER(:county)")
                params["county"] = county
            
            # Add minimum events filter if provided
            if min_events is not None:
                conditions.append("AND occurrence_count >= :min_events")
                params["min_events"] = min_events
            
            # Add event code filter if provided
            if event_code is not None:
                conditions.append("AND predicted_event_code = :event_code")
                params["event_code"] = event_code
            
            # Build the complete query
            query = base_query + " ".join(conditions)
            
            # Add ordering and limit
            query += " ORDER BY occurrence_count DESC"
            
            if top_n is not None:
                query += f" LIMIT {top_n}"
            
            detail_query = text(query)
            result = conn.execute(detail_query, params).mappings().all()
            
            return {
                "success": True,
                "data": [dict(row) for row in result],
                "count": len(result)
            }
            
    except SQLAlchemyError as e:
        print(f"Error fetching county occurrences: {e}")
        return {
            "success": False,
            "error": "Query failed",
            "message": str(e),
            "data": []
        }

# Get top counties across all years
def top_counties_all_years(top_n=10, event_code=1):
    """
    Get top counties by total event count across all years.
    
    Args:
        top_n (int): Number of top counties to return
        event_code (int): Filter by specific event code (default: 1)
    
    Returns:
        dict: Dictionary containing aggregated county data
    """
    try:
        with engine.connect() as conn:
            detail_query = text("""
                SELECT
                    county,
                    state,
                    fips,
                    SUM(occurrence_count) as total_events,
                    COUNT(DISTINCT year) as years_active,
                    AVG(occurrence_count) as avg_events_per_year,
                    AVG(avg_hail_magnitude) as overall_avg_hail_magnitude,
                    AVG(avg_tstm_magnitude) as overall_avg_tstm_magnitude,
                    MAX(max_hail_magnitude) as peak_hail_magnitude,
                    MAX(max_tstm_magnitude) as peak_tstm_magnitude,
                    MIN(year) as first_year,
                    MAX(year) as last_year
                FROM county_event_summary_by_year
                WHERE predicted_event_code = :event_code
                GROUP BY county, state, fips
                ORDER BY total_events DESC
                LIMIT :top_n
            """)
            
            result = conn.execute(detail_query, {"top_n": top_n, "event_code": event_code}).mappings().all()
            
            return {
                "success": True,
                "data": [dict(row) for row in result],
                "count": len(result)
            }
            
    except SQLAlchemyError as e:
        print(f"Error fetching top counties across all years: {e}")
        return {
            "success": False,
            "error": "Query failed",
            "message": str(e),
            "data": []
        }

# Get yearly summary statistics
def yearly_summary(year=None, event_code=1):
    """
    Get summary statistics for a specific year or all years.
    
    Args:
        year (int, optional): Specific year to analyze
        event_code (int): Filter by specific event code (default: 1)
    
    Returns:
        dict: Summary statistics
    """
    try:
        with engine.connect() as conn:
            if year is not None:
                detail_query = text("""
                    SELECT
                        year,
                        COUNT(DISTINCT county) as total_counties,
                        SUM(occurrence_count) as total_events,
                        AVG(occurrence_count) as avg_events_per_county,
                        AVG(avg_hail_magnitude) as overall_avg_hail_magnitude,
                        AVG(avg_tstm_magnitude) as overall_avg_tstm_magnitude,
                        MIN(occurrence_count) as min_events,
                        MAX(occurrence_count) as max_events,
                        MAX(max_hail_magnitude) as peak_hail_magnitude,
                        MAX(max_tstm_magnitude) as peak_tstm_magnitude
                    FROM county_event_summary_by_year
                    WHERE year = :year AND predicted_event_code = :event_code
                    GROUP BY year
                """)
                result = conn.execute(detail_query, {"year": year, "event_code": event_code}).mappings().first()
            else:
                detail_query = text("""
                    SELECT
                        COUNT(DISTINCT county) as total_unique_counties,
                        COUNT(DISTINCT year) as total_years,
                        SUM(occurrence_count) as grand_total_events,
                        AVG(occurrence_count) as overall_avg_events,
                        AVG(avg_hail_magnitude) as overall_avg_hail_magnitude,
                        AVG(avg_tstm_magnitude) as overall_avg_tstm_magnitude,
                        MIN(occurrence_count) as overall_min_events,
                        MAX(occurrence_count) as overall_max_events,
                        MAX(max_hail_magnitude) as peak_hail_magnitude,
                        MAX(max_tstm_magnitude) as peak_tstm_magnitude
                    FROM county_event_summary_by_year
                    WHERE predicted_event_code = :event_code
                """)
                result = conn.execute(detail_query, {"event_code": event_code}).mappings().first()
            
            if result:
                return {
                    "success": True,
                    "data": dict(result)
                }
            else:
                return {
                    "success": False,
                    "error": "No data found",
                    "data": {}
                }
                
    except SQLAlchemyError as e:
        print(f"Error fetching yearly summary: {e}")
        return {
            "success": False,
            "error": "Query failed",
            "message": str(e),
            "data": {}
        }

# Get event code comparison
def get_event_code_comparison(year=None, county=None):
    """
    Compare different event codes for analysis.
    
    Args:
        year (int, optional): Filter by specific year
        county (str, optional): Filter by specific county
    
    Returns:
        dict: Comparison data across event codes
    """
    try:
        with engine.connect() as conn:
            base_query = """
                SELECT
                    predicted_event_code,
                    COUNT(DISTINCT county) as counties_affected,
                    SUM(occurrence_count) as total_occurrences,
                    AVG(occurrence_count) as avg_occurrences,
                    AVG(avg_hail_magnitude) as avg_hail_mag,
                    AVG(avg_tstm_magnitude) as avg_tstm_mag
                FROM county_event_summary_by_year
                WHERE 1=1
            """
            
            params = {}
            conditions = []
            
            if year is not None:
                conditions.append("AND year = :year")
                params["year"] = year
            
            if county is not None:
                conditions.append("AND UPPER(county) = UPPER(:county)")
                params["county"] = county
            
            query = base_query + " ".join(conditions) + " GROUP BY predicted_event_code ORDER BY predicted_event_code"
            
            detail_query = text(query)
            result = conn.execute(detail_query, params).mappings().all()
            
            return {
                "success": True,
                "data": [dict(row) for row in result],
                "count": len(result)
            }
            
    except SQLAlchemyError as e:
        print(f"Error fetching event code comparison: {e}")
        return {
            "success": False,
            "error": "Query failed", 
            "message": str(e),
            "data": []
        }

# Example usage
if __name__ == "__main__":
    # Get top 5 counties for 2025 with event code 1
    print("=== Top 5 Counties for 2025 (Event Code 1) ===")
    top5_2025 = get_county_occurrences(year=2025, top_n=5, event_code=1)
    if top5_2025["success"]:
        for county in top5_2025["data"]:
            print(f"{county['county']}, {county['state']} (FIPS: {county['fips']}): {county['occurrence_count']} events")
            print(f"  Avg Hail: {county['avg_hail_magnitude']:.2f}, Avg Storm: {county['avg_tstm_magnitude']:.2f}")
    else:
        print(f"Error: {top5_2025['error']}")
    
    print("\n=== Counties with 50+ Events in 2025 (Event Code 1) ===")
    high_activity_2025 = get_county_occurrences(year=2025, min_events=50, event_code=1)
    if high_activity_2025["success"]:
        for county in high_activity_2025["data"]:
            print(f"{county['county']}, {county['state']}: {county['occurrence_count']} events")
    else:
        print(f"Error: {high_activity_2025['error']}")
    
    print("\n=== Top 10 Counties All Time (Event Code 1) ===")
    top10_alltime = top_counties_all_years(top_n=10, event_code=1)
    if top10_alltime["success"]:
        for county in top10_alltime["data"]:
            print(f"{county['county']}, {county['state']}: {county['total_events']} total events "
                  f"({county['years_active']} years, avg {county['avg_events_per_year']:.1f}/year)")
    else:
        print(f"Error: {top10_alltime['error']}")
    
    print("\n=== 2025 Summary Statistics (Event Code 1) ===")
    summary_2025 = yearly_summary(year=2025, event_code=1)
    if summary_2025["success"]:
        data = summary_2025["data"]
        print(f"Total Counties: {data['total_counties']}")
        print(f"Total Events: {data['total_events']}")
        print(f"Average Events per County: {data['avg_events_per_county']:.2f}")
        print(f"Min Events: {data['min_events']}")
        print(f"Max Events: {data['max_events']}")
        print(f"Peak Hail Magnitude: {data['peak_hail_magnitude']:.2f}")
    else:
        print(f"Error: {summary_2025['error']}")
    
    print("\n=== Event Code Comparison for 2025 ===")
    event_comparison = get_event_code_comparison(year=2025)
    if event_comparison["success"]:
        for event in event_comparison["data"]:
            print(f"Event Code {event['predicted_event_code']}: {event['total_occurrences']} total occurrences "
                  f"across {event['counties_affected']} counties")
    else:
        print(f"Error: {event_comparison['error']}")
