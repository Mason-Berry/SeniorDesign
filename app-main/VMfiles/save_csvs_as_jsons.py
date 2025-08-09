# save_csvs_as_jsons.py
from google.cloud import storage
import csv
import io
import json
from pathlib import Path

BUCKET_NAME = "forecasttx-era5-data-bucket"
KEEP_COLUMNS = ["time", "latitude", "longitude", "u10", "v10", "u100", "v100"]
OUTPUT_DIR = Path("json_files")
OUTPUT_DIR.mkdir(exist_ok=True)

def list_wind_csv_files(client):
    files = []
    for year in range(2025, 2031):
        for month in range(1, 13):
            prefix = f"p1_output_csv/monthly_forecasts/{year}/{month:02d}/"
            blobs = client.list_blobs(BUCKET_NAME, prefix=prefix)
            for blob in blobs:
                if blob.name.endswith(".csv"):
                    files.append(blob.name)
    return files

def fetch_and_convert_csv_to_json(client, file_path):
    blob = client.bucket(BUCKET_NAME).blob(file_path)
    content = blob.download_as_text()
    reader = csv.DictReader(io.StringIO(content))

    parsed_rows = []
    for row in reader:
        filtered = {}
        for col in KEEP_COLUMNS:
            val = row.get(col)
            if val is None:
                continue
            if col in ["latitude", "longitude", "u10", "v10", "u100", "v100"]:
                try:
                    val = float(val)
                except ValueError:
                    continue
            filtered[col] = val
        if filtered:
            parsed_rows.append(filtered)

    output_file = OUTPUT_DIR / (Path(file_path).stem + ".json")
    with open(output_file, "w") as f:
        json.dump(parsed_rows, f)
    print(f"✅ Saved: {output_file}")

def main():
    client = storage.Client()
    files = list_wind_csv_files(client)
    print(f"Found {len(files)} files.")

    for f in files:
        try:
            fetch_and_convert_csv_to_json(client, f)
        except Exception as e:
            print(f"❌ Failed to process {f}: {e}")

if __name__ == "__main__":
    main()
