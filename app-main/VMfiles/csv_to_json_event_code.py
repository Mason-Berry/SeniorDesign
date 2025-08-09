import csv
import json
from pathlib import Path

# === Configuration ===
INPUT_FILE = "modelOutput/event_forecast_2025_to_2030_FILTERED.csv"
OUTPUT_DIR = "processed_json"

# Texas bounds
TEXAS_BOUNDS = {
    "south": 25.8371,
    "north": 36.5007,
    "west": -106.6456,
    "east": -93.5080
}

def is_in_texas(lat, lng):
    return TEXAS_BOUNDS["south"] <= lat <= TEXAS_BOUNDS["north"] and \
           TEXAS_BOUNDS["west"] <= lng <= TEXAS_BOUNDS["east"]

def process_csv():
    grouped_data = {
        "1": [],
        "2": [],
        "3": []
    }

    with open(INPUT_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                code = str(int(row["Predicted_Event_Code"]))
                if code not in grouped_data:
                    continue

                lat = float(row["latitude"])
                lng = float(row["longitude"])

                if not is_in_texas(lat, lng):
                    continue

                point = {
                    "lat": lat,
                    "lng": lng,
                    "time": row[next(iter(row))].strip(),
                    "Predicted_Event_Code": int(row["Predicted_Event_Code"]),
                    "Predicted_Hail_Magnitude": float(row["Predicted_Hail_Magnitude"]),
                    "Predicted_TSTM_Magnitude": float(row["Predicted_TSTM_Magnitude"]),
                }

                grouped_data[code].append(point)
            except Exception:
                continue

    out_dir = Path(OUTPUT_DIR)
    out_dir.mkdir(exist_ok=True)

    for code, points in grouped_data.items():
        out_path = out_dir / f"event_code_{code}.json"
        with open(out_path, "w") as f:
            json.dump(points, f, indent=2)

    print(f"✅ Done! JSON files saved in: {out_dir.resolve()}")

if __name__ == "__main__":
    process_csv()
