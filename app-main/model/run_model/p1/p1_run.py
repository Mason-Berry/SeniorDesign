import tensorflow as tf
from tensorflow import keras
import numpy as np
import os
import time
import pandas as pd
import gc

# --- 1. Configuration: Set Up Your Forecasting Job ---

# --- Paths ---
# TODO: VERIFY THIS PATH - This MUST be the local path to your processed .npy files, stats, and model folder.
# This path should point to the directory that contains your 'local_model', 'forecasts', and .npy files.
PROCESSED_DATA_DIR = "/home/kenilubt/sambashare/phase1/run_phase1/model_and_data/"

# Path to your saved and trained Phase 1 model file.
# Corrected to join the directory with the relative path to the model.
MODEL_PATH = os.path.join(PROCESSED_DATA_DIR, "/home/kenilubt/sambashare/phase1/run_phase1/model_and_data/convlstm_feature_predictor_full_dataset.keras")

# Path where the final forecast output will be saved.
FORECAST_OUTPUT_DIR = os.path.join(PROCESSED_DATA_DIR, "forecasts/")
FORECAST_OUTPUT_PATH = os.path.join(FORECAST_OUTPUT_DIR, "forecast_2025_to_2027.npy")

# --- Model and Data Parameters (MUST MATCH YOUR TRAINING SCRIPT) ---
SEQUENCE_LENGTH = 24  # The lookback window your model was trained with.
GRID_HEIGHT = 43      # The grid height of your data.
GRID_WIDTH = 53       # The grid width of your data.
NUM_FEATURES = 17     # The number of features your model predicts.

# --- Forecasting Period ---
# Defines the time range for which you want to generate predictions.
FORECAST_START_DATE = '2025-01-01 00:00:00'
FORECAST_END_DATE = '2027-12-31 23:00:00'


def denormalize_data(data, mean, std):
    """Denormalizes data using the mean and std from the training set."""
    return data * (std + 1e-7) + mean

# --- 2. Main Forecasting Logic ---
if __name__ == "__main__":
    print("--- Starting Phase 1 Feature Forecasting Script ---")

    # --- Load The Trained Model ---
    print(f"Loading trained model from: {MODEL_PATH}")
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Please ensure Phase 1 training is complete and the path is correct.")
    
    # We don't need to compile the model for inference, which can be faster.
    model = keras.models.load_model(MODEL_PATH, compile=False)
    model.summary()

    # --- Load Normalization Statistics ---
    # This is ESSENTIAL. The model predicts normalized data; we need these to convert it back to real-world values.
    # --- THIS SECTION HAS BEEN CORRECTED ---
    print("Loading normalization statistics...")
    # Using the correct, longer filenames you provided.
    mean_stats_path = os.path.join(PROCESSED_DATA_DIR, 'numpy_converted_era5_hourly_numpy_files_input_train_mean_per_feature_float32.npy')
    std_stats_path = os.path.join(PROCESSED_DATA_DIR, 'numpy_converted_era5_hourly_numpy_files_input_train_std_per_feature_float32.npy')
    # --- END OF CORRECTION ---
    
    if not os.path.exists(mean_stats_path) or not os.path.exists(std_stats_path):
        raise FileNotFoundError(f"Normalization stat files not found in {PROCESSED_DATA_DIR}. They are required for forecasting.")
    train_mean = np.load(mean_stats_path)
    train_std = np.load(std_stats_path)

    # --- Prepare the "Seed" Data ---
    # The model needs a starting sequence of real data to begin forecasting.
    # We load the last available real data (e.g., from December 2024) and take the last SEQUENCE_LENGTH hours.
    print("Preparing seed data for the forecast...")
    last_real_data_file = os.path.join(PROCESSED_DATA_DIR, 'gridded_era5_2024_12.npy')
    if not os.path.exists(last_real_data_file):
        raise FileNotFoundError(f"Last real data file ('gridded_era5_2024_12.npy') not found. This is required to start the forecast.")
    
    last_month_data = np.load(last_real_data_file)
    
    if len(last_month_data) < SEQUENCE_LENGTH:
        raise ValueError(f"The last data file has fewer than {SEQUENCE_LENGTH} time steps. Cannot create a seed sequence.")
        
    seed_sequence_raw = last_month_data[-SEQUENCE_LENGTH:]
    
    # IMPORTANT: The model works with normalized data, so we must normalize the seed sequence.
    seed_sequence_normalized = (seed_sequence_raw - train_mean) / (train_std + 1e-7)
    
    # Use a list to hold the sequence for easy appending.
    # This list will grow as we add new predictions.
    input_sequence_for_prediction = list(seed_sequence_normalized)
    
    print(f"Seed sequence prepared with shape: {np.array(input_sequence_for_prediction).shape}")

    # --- Iterative Forecasting Loop ---
    prediction_dates = pd.date_range(start=FORECAST_START_DATE, end=FORECAST_END_DATE, freq='h')
    num_predictions = len(prediction_dates)
    print(f"\nForecasting for {num_predictions} time steps from {FORECAST_START_DATE} to {FORECAST_END_DATE}...")

    # This list will store the final, real-world value predictions.
    all_forecasts_denormalized = []
    
    start_time = time.time()
    for i in range(num_predictions):
        # 1. Prepare the current input sequence for the model
        # Get the last `SEQUENCE_LENGTH` frames and add a batch dimension: (1, seq_len, H, W, F)
        current_input_tensor = np.array(input_sequence_for_prediction[-SEQUENCE_LENGTH:]).reshape(1, SEQUENCE_LENGTH, GRID_HEIGHT, GRID_WIDTH, NUM_FEATURES)

        # 2. Make a single prediction
        # The output will be the next normalized frame. Shape: (1, H, W, F)
        predicted_frame_normalized = model.predict(current_input_tensor, verbose=0)
        
        # 3. Denormalize the prediction to get real-world values for saving
        # Remove the batch dimension first. Shape: (H, W, F)
        predicted_frame_denormalized = denormalize_data(predicted_frame_normalized[0], train_mean, train_std)
        all_forecasts_denormalized.append(predicted_frame_denormalized)
        
        # 4. Append the *normalized* prediction back to our sequence for the next iteration
        # This is the crucial autoregressive step.
        input_sequence_for_prediction.append(predicted_frame_normalized[0])
        
        # Print progress
        if (i + 1) % 100 == 0 or (i + 1) == num_predictions:
            elapsed_time = time.time() - start_time
            steps_done = i + 1
            total_steps = num_predictions
            avg_time_per_step = elapsed_time / steps_done
            eta_seconds = avg_time_per_step * (total_steps - steps_done)
            print(f"  -> Predicted step {steps_done}/{total_steps}... ETA: {time.strftime('%H:%M:%S', time.gmtime(eta_seconds))}")

    print("Forecasting complete.")

    # --- Save the Final Forecast ---
    # Convert the list of forecasted frames into a single NumPy array
    final_forecast_array = np.array(all_forecasts_denormalized, dtype=np.float32)
    print(f"Final forecast array created with shape: {final_forecast_array.shape}")
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(FORECAST_OUTPUT_PATH), exist_ok=True)
    
    print(f"Saving final forecast to: {FORECAST_OUTPUT_PATH}")
    np.save(FORECAST_OUTPUT_PATH, final_forecast_array)
    
    print("--- Script Finished ---")

