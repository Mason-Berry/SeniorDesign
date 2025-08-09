from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from utility import engine

# Get top 3 counties for hail and thunderstorm
def top3_counties(year, peril_type='HAIL'):
    try:
        with engine.connect() as conn:
            if peril_type == 'HAIL':
                detail_query = text("""
                    SELECT
                        county,
                        state,
                        fips,
                        year,
                        occurrence_count,
                        avg_hail_magnitude,
                        max_hail_magnitude
                    FROM top3_hail_counties
                    WHERE year = :year
                    ORDER BY max_hail_magnitude DESC
                    LIMIT 3;
                """)
                result = conn.execute(detail_query, {"year": year}).mappings().all()

                return [dict(row) for row in result]

            elif peril_type == 'THUNDERSTORM':
                detail_query = text("""
                    SELECT 
                        county,
                        state,
                        fips,
                        year,
                        occurrence_count,
                        avg_tstm_magnitude,
                        max_tstm_magnitude
                    FROM top3_tstm_counties
                    WHERE year = :year
                    ORDER BY max_tstm_magnitude DESC
                    LIMIT 3;
                """)
                result = conn.execute(detail_query, {"year": year}).mappings().all()

                return [dict(row) for row in result]

            else:
                return {
                    "success": False,
                    "error": f"Unsupported peril_type: {peril_type}",
                    "counties": []
                }

    except SQLAlchemyError as e:
        print(f" Error fetching top 3 counties: {e}")
        return {
            "success": False,
            "error": "Query failed",
            "message": str(e),
            "year": year,
            "peril_type": peril_type,
            "counties": []
        }


# Example usage
if __name__ == "__main__":
    hail_top3 = top3_counties(year=2025, peril_type='HAIL')
    print("Top 3 Hail Counties (2025):", hail_top3)

    tstm_top3 = top3_counties(year=2025, peril_type='THUNDERSTORM')
    print("Top 3 Thunderstorm Counties (2025):", tstm_top3)
