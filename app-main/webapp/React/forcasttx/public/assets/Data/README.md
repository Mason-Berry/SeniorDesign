# Processed Weather Prediction CSVs

This folder contains separated and pre-processed CSV datasets derived from the original county prediction data. These files are specifically filtered by **event type** to support visualization, analysis, and modeling in the State Farm Weather Prediction project.

---

## Files

- **`hail_data.csv`**  
  Contains all predicted hail-related events across all counties.

- **`thunderstorm_wind_data.csv`**  
  Contains all predicted thunderstorm wind-related events across all counties.

---

## CSV Format

Each CSV file contains the following columns:

| Column Name                | Description                                            | Type    |
|---------------------------|--------------------------------------------------------|---------|
| `County`                  | Name of the county                                     | `string`|
| `Event_Type`              | Weather event type (either `HAIL` or `THUNDERSTORM WIND`) | `string`|
| `Year`                    | Year of prediction                                     | `int`   |
| `Month`                   | Month of prediction                                    | `int`   |
| `Time_Index`              | Sequential time index (used for time series modeling)  | `int`   |
| `Predicted_Event_Count`   | Predicted number of weather events                     | `float` |
| `Predicted_Average_Magnitude` | Predicted average magnitude of the event           | `float` |

---

## Source

The data in these files is programmatically extracted from the original CSV files stored in Teams(for now).
