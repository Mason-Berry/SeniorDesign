import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import warnings


warnings.filterwarnings("ignore", category=RuntimeWarning)


input_filename = '/home/kenilubt/sd1/lr/all_county/all_county_transform.csv' 
output_filename = 'county_predictions_combined.csv'

year_month_col = 'BEGIN_YEARMONTH'
magnitude_col = 'MAGNITUDE'
county_col = 'CZ_NAME'
# event_type_col = 'EVENT_TYPE' # Removed for combined processing

start_year = 1955
end_year = 2024 
predict_years = 5

# --- 1. Load and Prepare Data ---
try:
    df = pd.read_csv(input_filename, low_memory=False)
    print(f"Data loaded successfully from '{input_filename}'.")
except FileNotFoundError:
    print(f"Error: '{input_filename}' not found. Please check the path.")
    exit()
except Exception as e:
    print(f"Error loading data from '{input_filename}': {e}")
    exit()


required_cols = [year_month_col, magnitude_col, county_col]
if not all(col in df.columns for col in required_cols):
    print(f"Error: Missing required columns. Ensure {required_cols} exist in the file.")
    exit()

# --- Robust Date Parsing ---
df['parsed_date'] = pd.to_datetime(df[year_month_col], format='%Y%m', errors='coerce')
original_rows = len(df)
df.dropna(subset=['parsed_date'], inplace=True)
removed_rows = original_rows - len(df)
if removed_rows > 0:
    print(f"Warning: Removed {removed_rows} rows with invalid date format in '{year_month_col}'.")

df['Year'] = df['parsed_date'].dt.year
df['Month'] = df['parsed_date'].dt.month

actual_end_year = df['Year'].max()
if actual_end_year < start_year:
     print(f"Error: No data found after start year {start_year}. Check date parsing and data.")
     exit()
if actual_end_year < end_year:
    print(f"Note: Data ends in {actual_end_year}, adjusting analysis period accordingly.")
    end_year = actual_end_year


df[county_col] = df[county_col].astype(str).str.strip().str.upper()
df.dropna(subset=[county_col], inplace=True)

# Filter data range 
df = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]
if df.empty:
    print(f"Error: No data found between {start_year} and {end_year} after cleaning.")
    exit()
print(f"Data filtered between {start_year}-{df[df['Year']==start_year]['Month'].min():02d} and {end_year}-{df[df['Year']==end_year]['Month'].max():02d}")

# Convert MAGNITUDE to numeric
df['Magnitude_Numeric'] = pd.to_numeric(df[magnitude_col], errors='coerce')
print(f"Processed {magnitude_col}. Found {df['Magnitude_Numeric'].isna().sum()} non-numeric values (will be ignored in avg calc).")

# --- 2. Process Each County (Combined Event Types) ---
all_predictions = []
unique_counties = sorted(df[county_col].unique()) # Sort counties
print(f"\nFound {len(unique_counties)} unique counties. Processing each (all event types combined)...") # Updated message

all_months_index = pd.MultiIndex.from_product(
    [range(start_year, end_year + 1), range(1, 13)],
    names=['Year', 'Month']
)

# --- Loop through County ONLY ---
for county in unique_counties:
    if not county or county == 'NAN':
        print(f"    Skipping invalid county name: '{county}'")
        continue
    print(f"  Processing County: {county}...")

    # Filter data for the specific county ONLY
    df_county = df[df[county_col] == county].copy()

    if len(df_county) < 10:
         print(f"    Skipping {county} due to insufficient data points ({len(df_county)} found).")
         continue

    # Calculate overall mean magnitude for this county
    county_mean_magnitude = df_county['Magnitude_Numeric'].mean()
    magnitude_fill_value = 0 if pd.isna(county_mean_magnitude) else county_mean_magnitude

    # Aggregate monthly data (all event types combined)
    grouped = df_county.groupby(['Year', 'Month'])
    monthly_counts = grouped.size().rename('Monthly_Event_Count')
    monthly_avg_magnitude = grouped['Magnitude_Numeric'].mean().rename('Monthly_Average_Magnitude')
    df_monthly_county = pd.concat([monthly_counts, monthly_avg_magnitude], axis=1)

    # Align with full date range & Fill Gaps
    df_monthly_county = df_monthly_county.reindex(all_months_index)
    df_monthly_county['Monthly_Event_Count'] = df_monthly_county['Monthly_Event_Count'].fillna(0).astype(int)
    df_monthly_county['Monthly_Average_Magnitude'] = df_monthly_county['Monthly_Average_Magnitude'].fillna(magnitude_fill_value) # Use county mean for filling
    df_monthly_county = df_monthly_county.reset_index()

    # Sort
    df_monthly_county = df_monthly_county.sort_values(by=['Year', 'Month']).reset_index(drop=True)

    # Create time index
    total_hist_months = (end_year - start_year + 1) * 12
    df_monthly_county['Time_Index'] = np.arange(1, total_hist_months + 1)

    # Prepare data for regression
    X = df_monthly_county[['Time_Index']]
    y_count = df_monthly_county['Monthly_Event_Count']
    y_magnitude = df_monthly_county['Monthly_Average_Magnitude']

    # Diagnostic print (optional but kept for now)
    # print(f"    County {county}: Unique Counts = {y_count.unique()}, Unique Magnitudes = {np.round(y_magnitude.unique(), 2)}")

    # Check for constant values
    if y_count.nunique() <= 1 or y_magnitude.nunique() <= 1:
        print(f"    Skipping {county} due to constant values (<=1 unique) in aggregated data after filling gaps.")
        continue

    # --- Train Models (for this county) ---
    try:
        model_count = LinearRegression()
        model_count.fit(X, y_count)
        model_magnitude = LinearRegression()
        model_magnitude.fit(X, y_magnitude)
        print(f"    Successfully trained models for {county}.") # Added success message
    except ValueError as ve:
         print(f"    Skipping {county} due to ValueError during model training: {ve}")
         continue
    except Exception as e:
        print(f"    Skipping {county} due to other error during model training: {e}")
        continue

    # --- Predict (for this county) ---
    last_time_index = total_hist_months
    num_predict_months = predict_years * 12
    future_time_indices = np.arange(last_time_index + 1, last_time_index + num_predict_months + 1)
    X_future = future_time_indices.reshape(-1, 1)
    future_counts = model_count.predict(X_future)
    future_magnitudes = model_magnitude.predict(X_future)
    future_counts[future_counts < 0] = 0

    # --- Format Predictions (No Event_Type column) ---
    future_dates = pd.date_range(start=f'{end_year}-12-01', periods=num_predict_months + 1, freq='M')[1:]
    df_pred_county = pd.DataFrame({
        'County': county, # County name
        'Year': future_dates.year,
        'Month': future_dates.month,
        'Time_Index': future_time_indices,
        'Predicted_Event_Count': future_counts.round(2),
        'Predicted_Average_Magnitude': future_magnitudes.round(2)
    })
    all_predictions.append(df_pred_county)

# --- 3. Combine Predictions and SAVE TO CSV ---
if all_predictions:
    final_predictions = pd.concat(all_predictions, ignore_index=True)
    prediction_end_year = end_year + predict_years
    print(f"\n--- Combined Predictions (All Event Types) for {predict_years} Years ({end_year+1}-{prediction_end_year}) ---")

    # --- SAVE TO CSV ---
    try:
        final_predictions.to_csv(output_filename, index=False) # index=False prevents writing the DataFrame index as a column
        print(f"\nPredictions successfully saved to '{output_filename}'")
    except Exception as e:
        print(f"\nError saving predictions to CSV file '{output_filename}': {e}")
        print("\nDisplaying predictions on screen instead:")
        print(final_predictions.to_string()) # Fallback to printing if save fails

else:
    print("\nNo predictions were generated for any county.")
