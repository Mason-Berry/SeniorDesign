# combine_wind_stage2.py

from google.cloud import storage
import json
from pathlib import Path

BUCKET_NAME = "forecasttx-era5-data-bucket"
OUTPUT_FILE = "processed_json/wind_data_stage1.json"

def main():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    all_data = []

    print("🚀 Starting Stage 2 (2028–2030)...")

    for year in range(2025, 2028):
        for month in range(1, 13):
            blob_name = f"processed_json/monthly_forecasts/{year}/wind_{year}_{month:02d}.json"
            blob = bucket.blob(blob_name)

            if blob.exists():
                print(f"📥 Downloading {blob_name}...")
                try:
                    content = blob.download_as_text()
                    data = json.loads(content)
                    all_data.extend(data)
                except Exception as e:
                    print(f"❌ Failed to process {blob_name}: {e}")
            else:
                print(f"⚠️ Missing blob: {blob_name}")

    # Ensure output directory exists
    Path("processed_json").mkdir(exist_ok=True)

    print(f"💾 Saving stage 2 data to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_data, f)

    print("✅ Stage 2 complete.")

if __name__ == "__main__":
    main()
