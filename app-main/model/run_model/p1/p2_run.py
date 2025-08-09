import tensorflow as tf
from tensorflow import keras
import numpy as np
import os
import time
import gc
import pandas as pd

# --- 1. Configuration: Set Up Your Forecasting Job ---

# --- Paths ---
# TODO: VERIFY THESE PATHS - They should point to your local data directories.
# Path to the directory containing your Phase 1 model's output (normalization stats).
PHASE1_DATA_DIR = "/home/seniordesign/Downloads/sd2_statefarmteam_ml/phase2/P2_csv_to_numpy/"
# Path to the directory containing your Phase 2 model.
PHASE2_DATA_DIR = "/home/seniordesign/Downloads/sd2_statefarmteam_ml/phase2/P2_csv_to_numpy/output/"

# --- Input Files (MUST EXIST) ---
# Path to your trained Phase 2 multi-output model.
MODEL_PATH = os.path.join(PHASE2_DATA_DIR, "multi_output_event_classifier_model.keras")

# Path to the extended feature forecast from Phase 1 (e.g., up to 2030).
FEATURE_FORECAST_PATH = os.path.join(PHASE1_DATA_DIR, "forecast_2025_to_2030.npy") # Example name

# Path to the last real data file, needed for the initial seed sequence.
SEED_DATA_PATH = os.path.join(PHASE1_DATA_DIR, "gridded_era5_2024_12.npy")

# Paths to your global coordinate files.
LATS_PATH = os.path.join(PHASE1_DATA_DIR, "global_unique_lats.npy")
LONS_PATH = os.path.join(PHASE1_DATA_DIR, "global_unique_lons.npy")


# --- Output File ---
# Path where the final CSV forecast will be saved.
EVENT_FORECAST_CSV_PATH = os.path.join(PHASE2_DATA_DIR, "event_forecast_2025_to_2030.csv")

# --- Model and Data Parameters (MUST MATCH TRAINING) ---
SEQUENCE_LENGTH = 24
GRID_HEIGHT = 43
GRID_WIDTH = 53
NUM_FEATURES = 17
NUM_CLASSES = 4
# Use a batch size that fits comfortably in your GPU VRAM for inference.
INFERENCE_BATCH_SIZE = 64

# --- Forecasting Period ---
FORECAST_START_DATE = '2025-01-01 00:00:00'
FORECAST_END_DATE = '2030-12-31 23:00:00'


# --- 2. Main Forecasting Logic ---
if __name__ == "__main__":
    print("--- Starting Phase 2 Event & Magnitude Forecasting Script (Outputting to CSV) ---")

    # --- Load The Trained Phase 2 Model ---
    print(f"Loading trained model from: {MODEL_PATH}")
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}.")
    model = keras.models.load_model(MODEL_PATH, compile=False)
    model.summary()

    # --- Load Normalization Statistics and Coordinates ---
    print("Loading normalization statistics and coordinate data...")
    train_mean = np.load(os.path.join(PHASE1_DATA_DIR, 'train_mean_per_feature_float32.npy'))
    train_std = np.load(os.path.join(PHASE1_DATA_DIR, 'train_std_per_feature_float32.npy'))
    latitudes = np.load(LATS_PATH)
    longitudes = np.load(LONS_PATH)

    # --- Prepare the Full Input Data Sequence ---
    print("Loading and preparing input data sequence...")
    seed_data_raw = np.load(SEED_DATA_PATH)[-SEQUENCE_LENGTH:]
    feature_forecast_raw = np.load(FEATURE_FORECAST_PATH)
    full_input_series_raw = np.concatenate([seed_data_raw, feature_forecast_raw], axis=0)
    full_input_series_normalized = (full_input_series_raw - train_mean) / (train_std + 1e-7)
    
    print(f"Full input data prepared with shape: {full_input_series_normalized.shape}")
    del seed_data_raw, feature_forecast_raw; gc.collect()
    
    # --- Prepare for CSV Writing ---
    CSV_COLUMNS = ['time', 'latitude', 'longitude', 'Predicted_Event_Code', 'Predicted_Hail_Magnitude', 'Predicted_TSTM_Magnitude']
    header_written = False
    os.makedirs(os.path.dirname(EVENT_FORECAST_CSV_PATH), exist_ok=True)

    # --- Iterative Prediction and Writing Loop ---
    num_sequences = full_input_series_normalized.shape[0] - SEQUENCE_LENGTH
    prediction_dates = pd.date_range(start=FORECAST_START_DATE, end=FORECAST_END_DATE, freq='h')
    
    print(f"\nGenerating predictions for {num_sequences} time steps and writing to CSV...")
    start_time = time.time()

    for i in range(0, num_sequences, INFERENCE_BATCH_SIZE):
        # Create a batch of input sequences
        batch_sequences = []
        end_index = min(i + INFERENCE_BATCH_SIZE, num_sequences)
        for j in range(i, end_index):
            sequence = full_input_series_normalized[j : j + SEQUENCE_LENGTH]
            batch_sequences.append(sequence)
        
        if not batch_sequences: continue
        input_batch = np.array(batch_sequences)

        # Make predictions for the entire batch
        batch_predictions = model.predict(input_batch, verbose=0)
        
        # Access the prediction results using their dictionary keys
        class_probs = batch_predictions['classification_output']
        hail_mags = batch_predictions['hail_mag_output'].squeeze(axis=-1)
        tstm_mags = batch_predictions['tstm_mag_output'].squeeze(axis=-1)
        
        # Convert probability distributions to a single predicted class index
        predicted_classes = np.argmax(class_probs, axis=-1)
        
        # --- Format batch results for CSV ---
        batch_size_current = input_batch.shape[0]
        rows_for_csv = []
        
        # Create lat/lon grid that will be tiled for each timestamp in the batch
        lat_lon_grid = np.array(np.meshgrid(latitudes, longitudes)).T.reshape(-1, 2)
        
        for b_idx in range(batch_size_current):
            timestamp = prediction_dates[i + b_idx]
            
            # Flatten the spatial predictions for this timestamp
            pred_class_flat = predicted_classes[b_idx].flatten()
            hail_mag_flat = hail_mags[b_idx].flatten()
            tstm_mag_flat = tstm_mags[b_idx].flatten()
            
            # Combine into a structured array for this timestamp
            timestamp_data = np.column_stack([
                np.full(lat_lon_grid.shape[0], timestamp),
                lat_lon_grid,
                pred_class_flat,
                hail_mag_flat,
                tstm_mag_flat
            ])
            rows_for_csv.extend(timestamp_data)

        # Convert to DataFrame and write to CSV
        df_batch = pd.DataFrame(rows_for_csv, columns=CSV_COLUMNS)
        
        if not header_written:
            df_batch.to_csv(EVENT_FORECAST_CSV_PATH, index=False, header=True, mode='w', float_format='%.6f')
            header_written = True
        else:
            df_batch.to_csv(EVENT_FORECAST_CSV_PATH, index=False, header=False, mode='a', float_format='%.6f')

        # Print progress
        if (i + INFERENCE_BATCH_SIZE) % (INFERENCE_BATCH_SIZE * 10) == 0:
            steps_done = i + INFERENCE_BATCH_SIZE
            print(f"  -> Processed and wrote up to step {steps_done}/{num_sequences}...")

    print("Prediction and CSV writing complete.")
    
    total_time = time.time() - start_time
    print(f"--- Script Finished in {time.strftime('%H:%M:%S', time.gmtime(total_time))} ---")

