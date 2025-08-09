#!/bin/bash

# Usage: ./upload_year_range_to_gcs.sh 1970 1975

# === Config ===
BUCKET_NAME="forecasttx-era5-data-bucket"
BASE_LOCAL_DIR="$HOME/era5_postgres_test/processed/joined"
DEST_ROOT="era5_csv"

# === Input validation ===
START_YEAR=$1
END_YEAR=$2

if [ -z "$START_YEAR" ] || [ -z "$END_YEAR" ]; then
    echo "Usage: $0 <start_year> <end_year>"
    exit 1
fi

# === Loop through year range ===
for YEAR in $(seq $START_YEAR $END_YEAR); do
    LOCAL_DIR="$BASE_LOCAL_DIR/$YEAR"
    if [ ! -d "$LOCAL_DIR" ]; then
        echo "⚠️  Skipping $YEAR: directory not found at $LOCAL_DIR"
        continue
    fi

    echo "📤 Uploading files from: $LOCAL_DIR"

    # Upload each .csv file (ignore backup folder)
    for file in "$LOCAL_DIR"/*.csv; do
        if [[ -f "$file" ]]; then
            filename=$(basename "$file")
            gsutil cp "$file" "gs://$BUCKET_NAME/$DEST_ROOT/$YEAR/$filename"
            echo "✔ Uploaded: $filename to $DEST_ROOT/$YEAR/"
        fi
    done

    echo "✅ Finished uploading year $YEAR"
    echo
done

echo "🎉 All done!"
