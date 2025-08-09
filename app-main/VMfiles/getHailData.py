
import csv
from typing import List, Dict
from datetime import datetime

def load_points_from_csv(filepath: str) -> List[Dict]:
    points = []
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                if int(row["Predicted_Event_Code"]) != 1:
                    continue  # skip rows where event code is not 1

                time_str = row[next(iter(row))].strip()
                time_obj = datetime.strptime(time_str.strip(), "%Y-%m-%d %H:%M:%S")
                time_iso = time_obj.isoformat() + "Z"
                lat = float(row["latitude"])
                lng = float(row["longitude"])
                time = time_iso
                points.append({
                    "lat": lat,
                    "lng": lng,
                    "time": time,
                    "Predicted_Event_Code": int(row["Predicted_Event_Code"]),
                    "Predicted_Hail_Magnitude": float(row["Predicted_Hail_Magnitude"]),
                    "Predicted_TSTM_Magnitude": float(row["Predicted_TSTM_Magnitude"])
                })
            except Exception as e:
                # skip rows with invalid data
                print("Error:", e)
                continue
    return points
