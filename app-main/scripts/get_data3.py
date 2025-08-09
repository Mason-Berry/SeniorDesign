import os
import argparse
import json
import cdsapi

DEFAULT_VARIABLES = [
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "2m_dewpoint_temperature",
    "2m_temperature",
    "surface_pressure",
    "total_precipitation",
    "100m_u_component_of_wind",
    "100m_v_component_of_wind",
    "10m_wind_gust_since_previous_post_processing",
    "instantaneous_10m_wind_gust",
    "cloud_base_height",
    "high_cloud_cover",
    "low_cloud_cover",
    "medium_cloud_cover",
    "total_cloud_cover",
    "total_column_cloud_ice_water",
    "total_column_cloud_liquid_water",
    "convective_precipitation",
    "large_scale_precipitation",
    "precipitation_type",
    "vertical_integral_of_kinetic_energy",
    "vertical_integral_of_temperature",
    "vertical_integral_of_total_energy",
    "vertically_integrated_moisture_divergence",
    "convective_available_potential_energy",
    "convective_inhibition",
    "k_index",
    "total_totals_index"
]

DEFAULT_AREA = [36.5, -106.6, 25.8, -93.5]  # Texas

def parse_args():
    parser = argparse.ArgumentParser(description="Download ERA5 reanalysis data from CDS API.")
    parser.add_argument("--cdsapirc", type=str, required=True, help="Path to .cdsapirc file with API credentials")
    parser.add_argument("--year", type=int, required=True, help="Year to download (e.g., 2024)")
    parser.add_argument("--month", type=str, required=True, help="Month to download (e.g., 01)")
    parser.add_argument("--output_dir", type=str, default="data", help="Directory to save GRIB files")
    parser.add_argument("--area", type=str, default=json.dumps(DEFAULT_AREA), help="Bounding box area as JSON string")
    parser.add_argument("--variables", type=str, default=json.dumps(DEFAULT_VARIABLES), help="Variables to retrieve as JSON string")
    parser.add_argument("--days", type=str, default="all", help="Comma-separated list of days to download (e.g. 01,02,03). Default: full month")
    return parser.parse_args()

def parse_days_arg(days_arg):
    if days_arg == "all":
        return [f"{d:02d}" for d in range(1, 32)]
    else:
        return [day.zfill(2) for day in days_arg.split(",")]

def main():
    args = parse_args()

    # Validate and prepare area/variables
    try:
        area = json.loads(args.area)
        variables = json.loads(args.variables)
        assert isinstance(area, list) and len(area) == 4
        assert isinstance(variables, list) and len(variables) > 0
    except Exception as e:
        print(f"❌ Failed to parse area or variables: {e}")
        return

    # Parse days
    days = parse_days_arg(args.days)

    # Set environment variable so cdsapi uses custom config file
    # os.environ["CDSAPI_RC"] = args.cdsapirc

    # Create output dir
    os.makedirs(args.output_dir, exist_ok=True)

    filename_base = f"{args.year}{args.month}"
    target_file = os.path.join(args.output_dir, f"{filename_base}.grib")

    if os.path.exists(target_file):
        print(f"⏭️ Already exists: {target_file}. Skipping download.")
        return

    print(f"⬇️ Requesting {filename_base} for days {days}...")
    
    print("CDSAPIRC path:", os.path.expanduser("~/.cdsapirc"))
    print("CDSAPIRC contents:")
    with open(os.path.expanduser("~/.cdsapirc")) as f:
        print(f.read())


    try:
        c = cdsapi.Client()
        c.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "format": "grib",
                "variable": variables,
                "year": str(args.year),
                "month": args.month,
                "day": days,
                "time": [f"{h:02d}:00" for h in range(24)],
                "area": area,
                "download_format": "unarchived"
            },
            target_file
        )
        print(f"✅ Downloaded and saved to {target_file}")
    except Exception as e:
        print(f"❌ Download failed for {filename_base}: {e}")

if __name__ == "__main__":
    main()
