#!/usr/bin/env python3
"""
Weather Forecast Data Processor - Wind Data Specialized

This script processes monthly weather forecast data from GCP bucket,
filters for Texas boundaries, and converts wind data (u100/v100) to
the specific JSON format required by Leaflet wind plugins.
"""

import os
import json
import csv
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import io
import pandas as pd
import numpy as np
from google.cloud import storage
from google.cloud.exceptions import NotFound
from shapely.geometry import Point, shape
from shapely.ops import transform
import requests


class TexasWindDataProcessor:
    def __init__(self, bucket_name: str = "forecasttx-era5-data-bucket"):
        """Initialize the processor with GCP bucket configuration."""
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

        # Texas bounds from your original data request
        self.TEXAS_BOUNDS = {
            'north': 36.5,
            'west': -106.6,
            'south': 25.8,
            'east': -93.5
        }

        # Grid parameters
        self.dx = 0.3
        self.dy = 0.3
        self.nx = int((self.TEXAS_BOUNDS['east'] - self.TEXAS_BOUNDS['west']) / self.dx) + 1
        self.ny = int((self.TEXAS_BOUNDS['north'] - self.TEXAS_BOUNDS['south']) / self.dy) + 1

        # Texas geometry for precise filtering
        self.texas_geometry = None
        self.texas_mask_geometry = None

        print(f"Grid dimensions: {self.nx} x {self.ny}")

    def load_texas_geometry(self) -> bool:
        """Load Texas geometry from a GeoJSON source."""
        try:
            # Try multiple GeoJSON sources
            sources = [
                {
                    "url": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson",
                    "name_fields": ["NAME", "name", "NAME_EN", "admin"]
                },
                {
                    "url": "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json",
                    "name_fields": ["NAME", "name", "STATE_NAME", "STUSPS"]
                },
                {
                    "url": "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
                    "name_fields": ["NAME", "name"]
                }
            ]

            print("Loading Texas geometry...")

            for source in sources:
                try:
                    print(f"Trying source: {source['url']}")
                    response = requests.get(source["url"], timeout=10)

                    if response.status_code != 200:
                        print(f"Failed to load from this source: {response.status_code}")
                        continue

                    states_data = response.json()

                    # Find Texas feature
                    texas_feature = None
                    possible_texas_names = ['Texas', 'TX', 'texas', 'TEXAS']

                    for feature in states_data['features']:
                        properties = feature.get('properties', {})

                        # Check all possible name fields
                        for name_field in source['name_fields']:
                            name_value = properties.get(name_field, '')
                            if name_value in possible_texas_names:
                                texas_feature = feature
                                print(f"Found Texas with field '{name_field}': {name_value}")
                                break

                        if texas_feature:
                            break

                    if texas_feature:
                        # Create Texas geometry
                        self.texas_geometry = shape(texas_feature['geometry'])
                        print("Texas geometry loaded successfully")
                        return True
                    else:
                        print(f"Texas not found in this source")

                except Exception as e:
                    print(f"Error with source {source['url']}: {e}")
                    continue

            # If all sources fail, try to create a simple Texas polygon from known coordinates
            print("All GeoJSON sources failed. Creating simplified Texas boundary...")
            return self.create_simplified_texas_geometry()

            print("Could not load Texas geometry from any source")
            return False

        except Exception as e:
            print(f"Error loading Texas geometry: {e}")
            return False

    def create_simplified_texas_geometry(self) -> bool:
        """Create a simplified Texas polygon from known coordinates."""
        try:
            from shapely.geometry import Polygon

            # Simplified Texas boundary (approximate)
            texas_coords = [
                [-106.6, 25.8],  # SW corner
                [-93.5, 25.8],  # SE corner
                [-93.5, 36.5],  # NE corner
                [-106.6, 36.5],  # NW corner
                [-106.6, 25.8]  # Close polygon
            ]

            self.texas_geometry = Polygon(texas_coords)
            print("Created simplified Texas boundary (bounding box)")
            return True

        except Exception as e:
            print(f"Error creating simplified geometry: {e}")
            return False

    def create_texas_mask_geometry(self, texas_feature):
        """Create a mask geometry similar to your JavaScript function."""
        from shapely.geometry import Polygon

        geom = texas_feature['geometry']

        # Extract holes (interior boundaries)
        if geom['type'] == 'MultiPolygon':
            holes = []
            for poly_coords in geom['coordinates']:
                if len(poly_coords) > 1:  # Has holes
                    holes.extend(poly_coords[1:])  # Skip exterior ring
        else:  # Polygon
            holes = geom['coordinates'][1:] if len(geom['coordinates']) > 1 else []

        # Create world polygon with Texas as holes
        world_exterior = [[-179.9, -89.9], [179.9, -89.9], [179.9, 89.9], [-179.9, 89.9], [-179.9, -89.9]]

        # Add Texas exterior as a hole
        texas_exterior = geom['coordinates'][0] if geom['type'] == 'Polygon' else geom['coordinates'][0][0]
        all_holes = [texas_exterior] + holes

        return Polygon(world_exterior, holes=all_holes)

    def is_point_in_texas(self, lat: float, lon: float) -> bool:
        """Check if a point is within Texas boundaries."""
        if self.texas_geometry is None:
            # Fallback to bounding box if geometry not loaded
            return (self.TEXAS_BOUNDS['south'] <= lat <= self.TEXAS_BOUNDS['north'] and
                    self.TEXAS_BOUNDS['west'] <= lon <= self.TEXAS_BOUNDS['east'])

        point = Point(lon, lat)
        return self.texas_geometry.contains(point)

    def file_exists_locally(self, filename: str) -> bool:
        """Check if file exists in current working directory."""
        return os.path.exists(filename)

    def download_file_from_gcp(self, gcp_path: str, local_filename: str) -> bool:
        """Download file from GCP bucket to local directory."""
        try:
            blob = self.bucket.blob(gcp_path)
            blob.download_to_filename(local_filename)
            print(f"Downloaded {gcp_path} to {local_filename}")
            return True
        except NotFound:
            print(f"File not found in bucket: {gcp_path}")
            return False
        except Exception as e:
            print(f"Error downloading {gcp_path}: {e}")
            return False

    def upload_file_to_gcp(self, local_filename: str, gcp_path: str) -> bool:
        """Upload file from local directory to GCP bucket."""
        try:
            blob = self.bucket.blob(gcp_path)
            blob.upload_from_filename(local_filename)
            print(f"Uploaded {local_filename} to {gcp_path}")
            return True
        except Exception as e:
            print(f"Error uploading {local_filename}: {e}")
            return False

    def convert_time_to_iso(self, time_str: str) -> str:
        """Convert time string to ISO 8601 UTC format."""
        try:
            # Try different parsing formats
            formats = [
                "%m/%d/%Y %H:%M",  # 1/1/2025 0:00
                "%Y-%m-%d %H:%M:%S",  # 2025-01-01 00:00:00
                "%Y-%m-%d %H:%M",  # 2025-01-01 00:00
                "%m/%d/%Y %H:%M:%S"  # 1/1/2025 0:00:00
            ]

            dt = None
            for fmt in formats:
                try:
                    dt = datetime.strptime(time_str, fmt)
                    break
                except ValueError:
                    continue

            if dt is None:
                raise ValueError(f"Could not parse time: {time_str}")

            # Convert to ISO 8601 UTC format
            return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        except Exception as e:
            print(f"Error converting time '{time_str}': {e}")
            return time_str

    def create_wind_data_object(self, ref_time: str, parameter_number: int,
                                wind_values: List[float]) -> Dict[str, Any]:
        """Create a wind data object in the required format."""
        return {
            "header": {
                "refTime": ref_time,
                "parameterCategory": 2,
                "parameterNumber": parameter_number,
                "nx": self.nx,
                "ny": self.ny,
                "lo1": self.TEXAS_BOUNDS['west'],
                "la1": self.TEXAS_BOUNDS['north'],
                "lo2": self.TEXAS_BOUNDS['east'],
                "la2": self.TEXAS_BOUNDS['south'],
                "dx": self.dx,
                "dy": self.dy
            },
            "data": wind_values
        }

    def process_csv_to_wind_data(self, csv_filename: str) -> List[Dict[str, Any]]:
        """Process CSV file and convert to wind data format."""
        wind_data_by_time = {}

        try:
            # Read CSV file
            df = pd.read_csv(csv_filename)

            # Check for required columns
            required_columns = ['time', 'latitude', 'longitude', 'u100', 'v100']
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                print(f"Error: Missing required columns in {csv_filename}: {missing_cols}")
                return []

            # Filter for Texas points
            texas_mask = df.apply(
                lambda row: self.is_point_in_texas(float(row['latitude']), float(row['longitude'])),
                axis=1
            )

            texas_df = df[texas_mask].copy()
            print(f"Filtered {len(texas_df)} Texas points from {len(df)} total points")

            if len(texas_df) == 0:
                print("No points found within Texas boundaries")
                return []

            # Group by time
            for time_str in texas_df['time'].unique():
                time_data = texas_df[texas_df['time'] == time_str]
                iso_time = self.convert_time_to_iso(str(time_str))

                # Create grid arrays initialized with NaN
                u_grid = np.full(self.nx * self.ny, np.nan)
                v_grid = np.full(self.nx * self.ny, np.nan)

                # Fill grid with data
                for _, row in time_data.iterrows():
                    lat, lon = float(row['latitude']), float(row['longitude'])
                    u_val, v_val = float(row['u100']), float(row['v100'])

                    # Calculate grid indices
                    i = int((lon - self.TEXAS_BOUNDS['west']) / self.dx)
                    j = int((self.TEXAS_BOUNDS['north'] - lat) / self.dy)

                    # Check bounds
                    if 0 <= i < self.nx and 0 <= j < self.ny:
                        grid_idx = j * self.nx + i
                        u_grid[grid_idx] = u_val
                        v_grid[grid_idx] = v_val

                # Convert NaN to None for JSON serialization
                u_data = [None if np.isnan(x) else x for x in u_grid]
                v_data = [None if np.isnan(x) else x for x in v_grid]

                # Create wind data objects
                u_object = self.create_wind_data_object(iso_time, 2, u_data)
                v_object = self.create_wind_data_object(iso_time, 3, v_data)

                # Store by time
                wind_data_by_time[iso_time] = {
                    "time": iso_time,
                    "data": [u_object, v_object]
                }

            # Convert to list sorted by time
            result = [wind_data_by_time[time] for time in sorted(wind_data_by_time.keys())]
            print(f"Created wind data for {len(result)} time steps")

            return result

        except Exception as e:
            print(f"Error processing {csv_filename}: {e}")
            return []

    def process_monthly_wind_data(self, start_year: int = 2025, end_year: int = 2030,
                                  specific_month: int = None) -> None:
        """Process monthly wind forecast data for specified year range."""

        # Load Texas geometry
        if not self.load_texas_geometry():
            print("Warning: Could not load Texas geometry. Using bounding box filtering.")

        if specific_month:
            print(f"\nProcessing wind data for month {specific_month} from {start_year} to {end_year}")
            month_range = [specific_month]
        else:
            print(f"\nProcessing wind data from {start_year} to {end_year}")
            month_range = range(1, 13)

        for year in range(start_year, end_year + 1):
            for month in month_range:
                # Generate filenames
                csv_filename = f"forecast_{year}_{month:02d}.csv"
                gcp_csv_path = f"p1_output_csv/monthly_forecasts/{year}/{month:02d}/{csv_filename}"

                # Check if file exists locally, download if not
                if not self.file_exists_locally(csv_filename):
                    print(f"\nDownloading {csv_filename}...")
                    if not self.download_file_from_gcp(gcp_csv_path, csv_filename):
                        print(f"Skipping {csv_filename} - file not found")
                        continue
                else:
                    print(f"\nUsing local file: {csv_filename}")

                # Process CSV to wind data
                print(f"Processing {csv_filename} for wind data...")
                wind_data = self.process_csv_to_wind_data(csv_filename)

                if not wind_data:
                    print(f"No wind data processed for {csv_filename}")
                    continue

                # Generate output filename
                output_filename = f"wind_{year}_{month:02d}.json"

                # Write JSON file
                try:
                    with open(output_filename, 'w') as f:
                        json.dump(wind_data, f, separators=(',', ':'))  # Compact format
                    print(f"Created {output_filename} with {len(wind_data)} time steps")
                except Exception as e:
                    print(f"Error writing {output_filename}: {e}")
                    continue

                # Upload to GCP
                gcp_output_path = f"processed_json/monthly_forecasts/{year}/{output_filename}"
                if self.upload_file_to_gcp(output_filename, gcp_output_path):
                    # Clean up local files to save space
                    try:
                        os.remove(csv_filename)
                        os.remove(output_filename)
                        print(f"Cleaned up local files")
                    except Exception as e:
                        print(f"Warning: Could not clean up files: {e}")

        print("\nWind data processing complete!")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Process wind forecast data from GCP bucket")
    parser.add_argument("--start-year", type=int, default=2025, help="Start year (default: 2025)")
    parser.add_argument("--end-year", type=int, default=2030, help="End year (default: 2030)")
    parser.add_argument("--month", type=int, help="Process only a specific month (1-12)")
    parser.add_argument("--bucket", type=str, default="forecasttx-era5-data-bucket",
                        help="GCP bucket name")

    args = parser.parse_args()

    # Validate month argument
    if args.month and not (1 <= args.month <= 12):
        print("Error: --month must be between 1 and 12")
        return

    # Initialize processor
    processor = TexasWindDataProcessor(bucket_name=args.bucket)

    # Process wind data
    processor.process_monthly_wind_data(
        start_year=args.start_year,
        end_year=args.end_year,
        specific_month=args.month
    )


if __name__ == "__main__":
    main()