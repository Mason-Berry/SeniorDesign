import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import os
import re
import time as pytime
import gc
import glob

# --- 1. Configuration for Local Training ---

# TODO: VERIFY THIS PATH - It MUST be the local path to your processed .npy files.
PROCESSED_DATA_DIR = "/home/seniordesign/Downloads/sd2_statefarmteam_ml/data/numpyfiles/"

# --- Define Year Ranges for Data Splits ---
TRAIN_YEARS_START = 1955
TRAIN_YEARS_END = 2015
VAL_YEARS_START = 2016
VAL_YEARS_END = 2019
TEST_YEARS_START = 2020 # Not used in this script, but defined for clarity
TEST_YEARS_END = 2024

# --- Grid Dimensions (loaded from local drive) ---
GRID_HEIGHT = len(np.load(os.path.join(PROCESSED_DATA_DIR, "global_unique_lats.npy")))
GRID_WIDTH = len(np.load(os.path.join(PROCESSED_DATA_DIR, "global_unique_lons.npy")))
NUM_FEATURES = 17

# --- Model & Training Parameters Optimized for RTX 4090 ---
SEQUENCE_LENGTH = 24
# Batch size suitable for a 24GB VRAM GPU.
BATCH_SIZE = 64
EPOCHS = 100
LEARNING_RATE = 0.001
# Mixed precision is highly recommended for RTX 40-series GPUs.
USE_MIXED_PRECISION = True 

MODEL_SAVE_PATH = os.path.join(PROCESSED_DATA_DIR, "local_model/convlstm_feature_predictor_full_dataset.keras")
# Ensure the directory for the saved model exists
os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)


# --- Helper functions ---
def get_year_month_from_filename(filename):
    basename = os.path.basename(filename)
    match = re.search(r'gridded_era5_(\d{4})_(\d{2})\.npy', basename)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def calculate_or_load_normalization_stats(training_files_list, num_features, stats_dir):
    mean_stats_path = os.path.join(stats_dir, 'train_mean_per_feature_float32.npy')
    std_stats_path = os.path.join(stats_dir, 'train_std_per_feature_float32.npy')
    
    if os.path.exists(mean_stats_path) and os.path.exists(std_stats_path):
        print("Loading pre-calculated normalization stats...")
        return np.load(mean_stats_path), np.load(std_stats_path)
    
    print("Calculating normalization statistics from training files (this WILL take a while)...")
    if not training_files_list:
        return np.zeros(num_features, dtype=np.float32), np.ones(num_features, dtype=np.float32)

    feature_sums = np.zeros(num_features, dtype=np.float64) 
    feature_sum_sqs = np.zeros(num_features, dtype=np.float64)
    total_counts = np.zeros(num_features, dtype=np.int64)

    for i, f_path in enumerate(training_files_list):
        print(f"  Stats calculation: Processing file {i+1}/{len(training_files_list)}: {os.path.basename(f_path)}")
        try:
            data_month = np.load(f_path).astype(np.float32) 
            data_reshaped = data_month.reshape(-1, num_features)
            del data_month; gc.collect()
            
            feature_sums += np.nansum(data_reshaped.astype(np.float64), axis=0) 
            feature_sum_sqs += np.nansum(data_reshaped.astype(np.float64)**2, axis=0) 
            total_counts += np.sum(~np.isnan(data_reshaped), axis=0)
            del data_reshaped; gc.collect()
        except Exception as e: print(f"    Error processing {f_path} for stats: {e}")

    valid_counts_mask = total_counts > 0
    calculated_mean = np.zeros(num_features, dtype=np.float32)
    calculated_std = np.ones(num_features, dtype=np.float32)

    calculated_mean[valid_counts_mask] = (feature_sums[valid_counts_mask] / total_counts[valid_counts_mask]).astype(np.float32)
    variance = np.zeros(num_features, dtype=np.float64)
    variance[valid_counts_mask] = (feature_sum_sqs[valid_counts_mask] / total_counts[valid_counts_mask]) - (calculated_mean[valid_counts_mask].astype(np.float64)**2)
    variance[variance < 1e-9] = 0 
    calculated_std[valid_counts_mask] = np.sqrt(variance[valid_counts_mask]).astype(np.float32)
    calculated_std[calculated_std < 1e-7] = 1.0 
    
    print("Saving normalization stats...")
    np.save(mean_stats_path, calculated_mean)
    np.save(std_stats_path, calculated_std)
    return calculated_mean, calculated_std

# --- Data Generator (Memory Optimized for Local Training) ---
def data_generator(file_paths_list, sequence_length, batch_size,
                   height, width, num_features,
                   global_mean, global_std, is_training=True):
    if not file_paths_list:
        print("CRITICAL WARNING: data_generator called with empty file_paths_list.")
        dummy_x = np.zeros((batch_size, sequence_length, height, width, num_features), dtype=np.float32)
        dummy_y = np.zeros((batch_size, height, width, num_features), dtype=np.float32)
        while True: yield dummy_x, dummy_y

    epoch_count = 0
    while True: 
        epoch_count += 1
        current_files = list(file_paths_list) 
        if is_training:
            np.random.shuffle(current_files)
        
        batch_X_list = []
        batch_y_list = []

        for file_path in current_files:
            try:
                month_data_raw = np.load(file_path).astype(np.float32)
            except Exception as e:
                print(f"  Generator: Error loading file {file_path}: {e}. Skipping.")
                continue
            
            month_data_normalized = (month_data_raw - global_mean) / (global_std + 1e-7)
            del month_data_raw 
            gc.collect()       
            
            num_possible_sequences = month_data_normalized.shape[0] - sequence_length
            if num_possible_sequences <= 0: 
                del month_data_normalized; gc.collect()
                continue

            for i in range(num_possible_sequences):
                X_seq = month_data_normalized[i : i + sequence_length]
                y_target = month_data_normalized[i + sequence_length]
                batch_X_list.append(X_seq)
                batch_y_list.append(y_target)

                if len(batch_X_list) == batch_size:
                    yield np.array(batch_X_list, dtype=np.float32), np.array(batch_y_list, dtype=np.float32)
                    batch_X_list = []
                    batch_y_list = []
            del month_data_normalized
            gc.collect()
        
        if batch_X_list:
            yield np.array(batch_X_list, dtype=np.float32), np.array(batch_y_list, dtype=np.float32)

def build_convlstm_model(seq_len, height, width, n_features, learning_rate):
    if USE_MIXED_PRECISION:
        print("Using mixed_float16 precision policy.")
        keras.mixed_precision.set_global_policy('mixed_float16')

    model = keras.Sequential(name="ERA5_Feature_Predictor_ConvLSTM")
    model.add(layers.Input(shape=(seq_len, height, width, n_features)))
    model.add(layers.ConvLSTM2D(filters=64, kernel_size=(3, 3), padding='same', return_sequences=True))
    model.add(layers.BatchNormalization())
    model.add(layers.ConvLSTM2D(filters=128, kernel_size=(3, 3), padding='same', return_sequences=True))
    model.add(layers.BatchNormalization())
    model.add(layers.ConvLSTM2D(filters=64, kernel_size=(3, 3), padding='same', return_sequences=False))
    model.add(layers.BatchNormalization())
    model.add(layers.Conv2D(filters=n_features, kernel_size=(3, 3), activation='linear', padding='same', dtype='float32' if USE_MIXED_PRECISION else None))

    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])
    return model

# --- 4. Main Training Execution ---
if __name__ == "__main__":
    print("\nVerifying TensorFlow GPU availability...")
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus: tf.config.experimental.set_memory_growth(gpu, True)
            print(f"Running on GPU: {gpus[0].name if gpus else 'None'}")
        except RuntimeError as e: print(f"Error setting up GPU: {e}")
    else: print("No GPU detected. Running on CPU.")

    all_processed_files = sorted(glob.glob(os.path.join(PROCESSED_DATA_DIR, "gridded_era5_*.npy")))
    train_files, val_files = [], []
    for f_path in all_processed_files:
        year, month = get_year_month_from_filename(f_path)
        if year is not None:
            if TRAIN_YEARS_START <= year <= TRAIN_YEARS_END:
                train_files.append(f_path)
            elif VAL_YEARS_START <= year <= VAL_YEARS_END:
                val_files.append(f_path)
    print(f"Total training files found: {len(train_files)}")
    print(f"Total validation files found: {len(val_files)}")
    if not train_files:
        print("FATAL: No training files found."); import sys; sys.exit()

    train_mean, train_std = calculate_or_load_normalization_stats(train_files, NUM_FEATURES, PROCESSED_DATA_DIR)

    print("\nCalculating total samples for epoch steps...")
    train_samples_count = 0
    for f_path in train_files:
        try:
            with open(f_path, 'rb') as f:
                version = np.lib.format.read_magic(f)
                shape, _, _ = np.lib.format.read_array_header_1_0(f) if version < (3,0) else np.lib.format.read_array_header_2_0(f)
            train_samples_count += max(0, shape[0] - SEQUENCE_LENGTH)
        except Exception as e: print(f"Warning: Could not read shape for {f_path}: {e}")
    steps_per_epoch = max(1, train_samples_count // BATCH_SIZE) if train_samples_count > 0 else 1
    print(f"Total training sequences estimated: {train_samples_count}, Steps per epoch: {steps_per_epoch}")

    validation_steps = None
    if val_files:
        val_samples_count = 0
        for f_path in val_files:
            try:
                with open(f_path, 'rb') as f:
                    version = np.lib.format.read_magic(f)
                    shape, _, _ = np.lib.format.read_array_header_1_0(f) if version < (3,0) else np.lib.format.read_array_header_2_0(f)
                val_samples_count += max(0, shape[0] - SEQUENCE_LENGTH)
            except Exception as e: print(f"Warning: Could not read shape for {f_path}: {e}")
        validation_steps = max(1, val_samples_count // BATCH_SIZE) if val_samples_count > 0 else 1
        print(f"Total validation sequences estimated: {val_samples_count}, Validation steps: {validation_steps}")
    
    train_generator = data_generator(train_files, SEQUENCE_LENGTH, BATCH_SIZE, GRID_HEIGHT, GRID_WIDTH, NUM_FEATURES, train_mean, train_std, is_training=True)
    val_generator = data_generator(val_files, SEQUENCE_LENGTH, BATCH_SIZE, GRID_HEIGHT, GRID_WIDTH, NUM_FEATURES, train_mean, train_std, is_training=False) if val_files else None

    model = build_convlstm_model(SEQUENCE_LENGTH, GRID_HEIGHT, GRID_WIDTH, NUM_FEATURES, LEARNING_RATE)
    model.summary()
    callbacks = [
        keras.callbacks.ModelCheckpoint(MODEL_SAVE_PATH, save_best_only=True, monitor='val_loss' if val_files else 'loss', mode='min', verbose=1),
        keras.callbacks.EarlyStopping(monitor='val_loss' if val_files else 'loss', patience=15, mode='min', restore_best_weights=True, verbose=1),
        keras.callbacks.ReduceLROnPlateau(monitor='val_loss' if val_files else 'loss', factor=0.2, patience=7, min_lr=1e-6, mode='min', verbose=1)
    ]

    print(f"\nStarting model training with data from {TRAIN_YEARS_START}-{TRAIN_YEARS_END}")
    if train_samples_count == 0:
        print("FATAL: No training samples. Cannot start training.")
    else:
        history = model.fit(
            train_generator, steps_per_epoch=steps_per_epoch, epochs=EPOCHS,
            validation_data=val_generator, validation_steps=validation_steps,
            callbacks=callbacks, verbose=1
        )
        print("\nTraining complete.")
        print(f"Model saved to {MODEL_SAVE_PATH}")
    
    if USE_MIXED_PRECISION:
        keras.mixed_precision.set_global_policy('float32')
