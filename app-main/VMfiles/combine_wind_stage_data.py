import json

file1 = "processed_json/wind_data_stage1.json"
file2 = "processed_json/wind_data_stage2.json"
output_file = "processed_json/wind_all_years_combined.json"

with open(file1, "r") as f1, open(file2, "r") as f2:
    data1 = json.load(f1)
    data2 = json.load(f2)

# Combine and save
combined = data1 + data2

with open(output_file, "w") as out:
    json.dump(combined, out)

print(f"✅ Combined {len(data1)} + {len(data2)} records into {output_file}")
