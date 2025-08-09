import os
import cdsapi
import calendar

# Output directory for downloaded GRIB files.
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

# Updated variables to be retrieved from CDS.
# Desired variables:
# - 10m u-component of wind, 10m v-component of wind,
# - 2m dewpoint temperature, 2m temperature,
# - Surface pressure,
# - Total precipitation,
# - 100m u-component of wind, 100m v-component of wind,
# - 10m wind gust since previous post-processing, Instantaneous 10m wind gust,
# - Cloud base height,
# - High cloud cover, Low cloud cover, Medium cloud cover, Total cloud cover,
# - Total column cloud ice water, Total column cloud liquid water,
# - Convective precipitation, Large-scale precipitation, Precipitation type,
# - Vertical integral of kinetic energy, Vertical integral of temperature,
# - Vertical integral of total energy, Vertically integrated moisture divergence,
# - Convective available potential energy, Convective inhibition,
# - K index, Total totals index.
variables = [
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

# Bounding box for Texas [North, West, South, East].
area = [36.5, -106.6, 25.8, -93.5]

# Setup CDS API client.
c = cdsapi.Client()

# Define range: For example, years 1960 to 1964 (5 years).
years = range(1960, 1965)
months = [f"{m:02d}" for m in range(1, 13)]

for year in years:
    for month in months:
        filename_base = f"{year}{month}"
        target_file = os.path.join(data_dir, f"{filename_base}.grib")

        # Skip if file already exists.
        if os.path.exists(target_file):
            print(f"⏭️ Already exists: {target_file}. Skipping.")
            continue

        print(f"⬇️ Downloading {filename_base}...")
        try:
            c.retrieve(
                "reanalysis-era5-single-levels",
                {
                    "product_type": "reanalysis",
                    "format": "grib",
                    "variable": variables,
                    "year": str(year),
                    "month": month,
                    "day": [f"{d:02d}" for d in range(1, 32)],
                    "time": [f"{h:02d}:00" for h in range(24)],
                    "area": area,
                    "download_format": "unarchived"
                },
                target_file
            )
            print(f"✅ Saved to {target_file}")
        except Exception as e:
            print(f"❌ Failed to download {filename_base}: {e}")
