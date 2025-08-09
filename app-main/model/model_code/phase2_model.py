import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.utils import to_categorical
import numpy as np
import os
import re
import time as pytime
import gc
import glob
from sklearn.utils.class_weight import compute_class_weight

# --- 1. Configuration for Local Training ---

# TODO: VERIFY THESE PATHS
# Path to the directory with your Phase 1 processed data (features and stats)
FEATURE_DATA_DIR = "/home/seniordesign/Downloads/sd2_statefarmteam_ml/data/numpyfiles/"
# Path to the directory with your Phase 2 processed data (targets)
TARGET_DATA_DIR = "/home/seniordesign/Downloads/sd2_statefarmteam_ml/phase2/P2_csv_to_numpy/output/"

# --- Data Split & Model Parameters ---
TRAIN_YEARS_START = 1955
TRAIN_YEARS_END = 2015
VAL_YEARS_START = 2016
VAL_YEARS_END = 2019

GRID_HEIGHT = 43
GRID_WIDTH = 53
NUM_FEATURES = 17
NUM_CLASSES = 4

# --- Parameters Optimized for a single RTX 4090 ---
SEQUENCE_LENGTH = 24
# BATCH_SIZE set to a safe and efficient value for a 24GB VRAM GPU.
BATCH_SIZE = 32
EPOCHS = 100
LEARNING_RATE = 0.001
# Set to False for maximum stability. Can be set to True on powerful GPUs if no errors occur.
USE_MIXED_PRECISION = False

MODEL_SAVE_PATH = os.path.join(TARGET_DATA_DIR, "multi_output_event_classifier_model.keras")
os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)


# --- Helper functions ---
def get_year_month_from_filename(filename, prefix="gridded_era5_"):
    basename = os.path.basename(filename)
    match = re.search(rf'{prefix}(\d{{4}})_(\d{{2}})\.npy', basename)
    if match: return int(match.group(1)), int(match.group(2))
    return None, None

def calculate_class_weights(target_files_list, num_classes):
    """Calculates class weights to handle imbalanced classification data."""
    print("Calculating class weights from training data...")
    all_labels = []
    for f_path in target_files_list:
        try:
            # Assumes event code is the first channel (index 0)
            data = np.load(f_path)[:, :, :, 0]
            all_labels.extend(data.flatten())
        except Exception as e:
            print(f"  Warning: Could not load target file {f_path} for weight calculation: {e}")
    
    all_labels = np.array(all_labels, dtype=np.int32)
    unique_classes, counts = np.unique(all_labels, return_counts=True)
    print("Class counts:", dict(zip(unique_classes, counts)))
    
    weights = compute_class_weight('balanced', classes=unique_classes, y=all_labels)
    class_weight_dict = dict(zip(unique_classes, weights))
    
    # Ensure all classes have a weight, even if not present in the sample data
    for i in range(num_classes):
        if i not in class_weight_dict:
            class_weight_dict[i] = 1.0 # Assign a default weight
            print(f"Warning: Class {i} not found in training data. Assigning default weight 1.0")
            
    print(f"Calculated class weights: {class_weight_dict}")
    return class_weight_dict

# --- Data Generator (Memory-safe, yields inputs, targets, and sample weights) ---
def data_generator_multi_output(feature_files, target_files, sequence_length, batch_size,
                                height, width, num_features, num_classes,
                                global_mean, global_std, class_weight_dict, is_training=True):
    target_file_map = {get_year_month_from_filename(f, prefix="multi_target_"): f for f in target_files}
    
    while True:
        current_feature_files = list(feature_files)
        if is_training:
            np.random.shuffle(current_feature_files)

        for feature_file_path in current_feature_files:
            year, month = get_year_month_from_filename(feature_file_path, prefix="gridded_era5_")
            if (year, month) not in target_file_map: continue
            target_file_path = target_file_map[(year, month)]

            try:
                feature_data = np.load(feature_file_path).astype(np.float32)
                multi_target_data = np.load(target_file_path).astype(np.float32)
            except Exception as e:
                print(f"  Generator: Error loading file pair: {e}. Skipping.")
                continue

            feature_data_normalized = (feature_data - global_mean) / (global_std + 1e-7)
            del feature_data; gc.collect()

            num_sequences = feature_data_normalized.shape[0] - sequence_length
            if num_sequences <= 0: continue

            # Create lists to hold a full batch
            batch_X_list, batch_y_class_list, batch_y_hail_list, batch_y_tstm_list = [], [], [], []
            batch_w_class_list, batch_w_hail_list, batch_w_tstm_list = [], [], []

            for i in range(num_sequences):
                batch_X_list.append(feature_data_normalized[i : i + sequence_length])
                
                y_target_full = multi_target_data[i + sequence_length]
                y_class_raw = y_target_full[:, :, 0].astype(np.int32)
                
                # Append targets
                batch_y_class_list.append(to_categorical(y_class_raw, num_classes=num_classes))
                batch_y_hail_list.append(y_target_full[:, :, 1])
                batch_y_tstm_list.append(y_target_full[:, :, 2])
                
                # Append sample weights for each of the three tasks
                batch_w_class_list.append(np.vectorize(class_weight_dict.get)(y_class_raw))
                batch_w_hail_list.append(np.isin(y_class_raw, [1, 3]).astype(np.float32)) # Weight is 1 only for hail events (1 or 3)
                batch_w_tstm_list.append(np.isin(y_class_raw, [2]).astype(np.float32))    # Weight is 1 only for tstm-only events (2)

                if len(batch_X_list) == batch_size:
                    yield (np.array(batch_X_list),
                           # Yield targets as a list in the correct order
                           [np.array(batch_y_class_list), np.expand_dims(np.array(batch_y_hail_list), axis=-1), np.expand_dims(np.array(batch_y_tstm_list), axis=-1)],
                           # Yield sample weights as a list in the same order
                           [np.array(batch_w_class_list), np.array(batch_w_hail_list), np.array(batch_w_tstm_list)])
                    
                    # Reset batch lists
                    batch_X_list, batch_y_class_list, batch_y_hail_list, batch_y_tstm_list = [], [], [], []
                    batch_w_class_list, batch_w_hail_list, batch_w_tstm_list = [], [], []
            
            # Yield any leftover samples from the file
            if batch_X_list:
                yield (np.array(batch_X_list),
                       [np.array(batch_y_class_list), np.expand_dims(np.array(batch_y_hail_list), axis=-1), np.expand_dims(np.array(batch_y_tstm_list), axis=-1)],
                       [np.array(batch_w_class_list), np.array(batch_w_hail_list), np.array(batch_w_tstm_list)])

            del feature_data_normalized, multi_target_data; gc.collect()

# --- Multi-Output Model Architecture ---
def build_multi_output_model(seq_len, height, width, n_features, n_classes, learning_rate):
    if USE_MIXED_PRECISION:
        print("Using mixed_float16 precision policy.")
        keras.mixed_precision.set_global_policy('mixed_float16')

    input_layer = layers.Input(shape=(seq_len, height, width, n_features), name="input_features")
    
    # Shared Body
    shared_body = layers.ConvLSTM2D(filters=64, kernel_size=(3, 3), padding='same', return_sequences=True)(input_layer)
    shared_body = layers.BatchNormalization()(shared_body)
    shared_body = layers.ConvLSTM2D(filters=128, kernel_size=(3, 3), padding='same', return_sequences=True)(shared_body)
    shared_body = layers.BatchNormalization()(shared_body)
    shared_body = layers.ConvLSTM2D(filters=64, kernel_size=(3, 3), padding='same', return_sequences=False)(shared_body)
    shared_body = layers.BatchNormalization()(shared_body)

    # Output Head 1: Classification
    class_head = layers.Conv2D(filters=64, kernel_size=(3,3), padding='same', activation='relu')(shared_body)
    class_output = layers.Conv2D(filters=n_classes, kernel_size=(1, 1), activation='softmax', padding='same', name='classification_output', dtype='float32')(class_head)
    
    # Output Head 2: Hail Magnitude
    hail_head = layers.Conv2D(filters=32, kernel_size=(3,3), padding='same', activation='relu')(shared_body)
    hail_output = layers.Conv2D(filters=1, kernel_size=(1, 1), activation='linear', padding='same', name='hail_mag_output', dtype='float32')(hail_head)
    
    # Output Head 3: TSTM Magnitude
    tstm_head = layers.Conv2D(filters=32, kernel_size=(3,3), padding='same', activation='relu')(shared_body)
    tstm_output = layers.Conv2D(filters=1, kernel_size=(1, 1), activation='linear', padding='same', name='tstm_mag_output', dtype='float32')(tstm_head)
    
    # Define the model with one input and a LIST of three outputs
    model = keras.Model(inputs=input_layer, outputs=[class_output, hail_output, tstm_output])
    
    # Define losses and metrics using dictionaries for clarity
    losses = {
        'classification_output': 'categorical_crossentropy', 
        'hail_mag_output': 'mean_squared_error', 
        'tstm_mag_output': 'mean_squared_error'
    }
    loss_weights = {
        'classification_output': 1.0, 
        'hail_mag_output': 0.5, 
        'tstm_mag_output': 0.5
    }
    metrics = {
        'classification_output': ['accuracy', keras.metrics.Precision(name='precision'), keras.metrics.Recall(name='recall')],
        'hail_mag_output': ['mae'], 
        'tstm_mag_output': ['mae']
    }

    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(optimizer=optimizer, loss=losses, loss_weights=loss_weights, metrics=metrics)
    return model

if __name__ == "__main__":
    print("\n--- Phase 2: Multi-Output Event Classifier Training ---")
    
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus: tf.config.experimental.set_memory_growth(gpu, True)
            print(f"Running on GPU: {gpus[0].name if gpus else 'None'}")
        except RuntimeError as e: print(f"Error setting up GPU: {e}")
    else: print("No GPU detected. Running on CPU.")
    
    # --- Prepare File Lists ---
    all_feature_files = sorted(glob.glob(os.path.join(FEATURE_DATA_DIR, "gridded_era5_*.npy")))
    all_target_files = sorted(glob.glob(os.path.join(TARGET_DATA_DIR, "multi_target_*.npy")))
    train_feature_files = [f for f in all_feature_files if TRAIN_YEARS_START <= get_year_month_from_filename(f)[0] <= TRAIN_YEARS_END]
    val_feature_files = [f for f in all_feature_files if VAL_YEARS_START <= get_year_month_from_filename(f)[0] <= VAL_YEARS_END]
    train_target_files = [f for f in all_target_files if TRAIN_YEARS_START <= get_year_month_from_filename(f, prefix="multi_target_")[0] <= TRAIN_YEARS_END]
    val_target_files = [f for f in all_target_files if VAL_YEARS_START <= get_year_month_from_filename(f, prefix="multi_target_")[0] <= VAL_YEARS_END]
    
    if not all([train_feature_files, train_target_files]):
        print("FATAL: Missing training files in specified directories. Check paths."); import sys; sys.exit()
    
    # Load normalization stats and calculate class weights
    train_mean = np.load(os.path.join(FEATURE_DATA_DIR, 'train_mean_per_feature_float32.npy'))
    train_std = np.load(os.path.join(FEATURE_DATA_DIR, 'train_std_per_feature_float32.npy'))
    class_weights = calculate_class_weights(train_target_files, NUM_CLASSES)

    # --- Calculate Steps Per Epoch ---
    train_samples_count = 0
    for f_path in train_feature_files:
        try:
            with open(f_path, 'rb') as f:
                version = np.lib.format.read_magic(f)
                shape, _, _ = np.lib.format.read_array_header_1_0(f) if version < (3, 0) else np.lib.format.read_array_header_2_0(f)
            train_samples_count += max(0, shape[0] - SEQUENCE_LENGTH)
        except Exception as e: print(f"Warning: Could not read shape for {os.path.basename(f_path)}. Error: {e}")
    steps_per_epoch = max(1, train_samples_count // BATCH_SIZE) if train_samples_count > 0 else 1
    print(f"Total training sequences estimated: {train_samples_count}, Steps per epoch: {steps_per_epoch}")

    validation_steps = None
    if val_feature_files:
        val_samples_count = 0
        for f_path in val_feature_files:
            try:
                with open(f_path, 'rb') as f:
                    version = np.lib.format.read_magic(f)
                    shape, _, _ = np.lib.format.read_array_header_1_0(f) if version < (3, 0) else np.lib.format.read_array_header_2_0(f)
                val_samples_count += max(0, shape[0] - SEQUENCE_LENGTH)
            except Exception as e: print(f"Warning: Could not read shape for {os.path.basename(f_path)}. Error: {e}")
        validation_steps = max(1, val_samples_count // BATCH_SIZE) if val_samples_count > 0 else None
        print(f"Total validation sequences estimated: {val_samples_count}, Validation steps: {validation_steps}")

    # Create generators
    train_generator = data_generator_multi_output(train_feature_files, train_target_files, SEQUENCE_LENGTH, BATCH_SIZE, GRID_HEIGHT, GRID_WIDTH, NUM_FEATURES, NUM_CLASSES, train_mean, train_std, class_weights, is_training=True)
    val_generator = data_generator_multi_output(val_feature_files, val_target_files, SEQUENCE_LENGTH, BATCH_SIZE, GRID_HEIGHT, GRID_WIDTH, NUM_FEATURES, NUM_CLASSES, train_mean, train_std, class_weights, is_training=False) if val_target_files else None
    
    # Build model
    model = build_multi_output_model(SEQUENCE_LENGTH, GRID_HEIGHT, GRID_WIDTH, NUM_FEATURES, NUM_CLASSES, LEARNING_RATE)
    model.summary()
    
    callbacks = [
        keras.callbacks.ModelCheckpoint(MODEL_SAVE_PATH, save_best_only=True, monitor='val_loss', mode='min', verbose=1),
        keras.callbacks.EarlyStopping(monitor='val_loss', patience=20, mode='min', restore_best_weights=True, verbose=1),
        keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=8, min_lr=1e-6, mode='min', verbose=1)
    ]
    
    # Train model
    print("\nStarting Phase 2 model training...")
    if train_samples_count == 0:
        print("FATAL: No training samples. Cannot start training.")
    else:
        history = model.fit(
            train_generator,
            steps_per_epoch=steps_per_epoch,
            epochs=EPOCHS,
            validation_data=val_generator,
            validation_steps=validation_steps,
            callbacks=callbacks,
            verbose=1
        )
    
    print("\nTraining complete.")
    print(f"Phase 2 model saved to {MODEL_SAVE_PATH}")
    
    if USE_MIXED_PRECISION:
        keras.mixed_precision.set_global_policy('float32')
