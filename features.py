import pandas as pd
import numpy as np
from sqlalchemy import create_engine

engine = create_engine("sqlite:///data/airsense.db")

def load_data():
    """load all data from database"""
    df = pd.read_sql("SELECT * FROM air_quality ORDER BY city, timestamp", engine)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def engineer_features(df):
    """create meaningful features from raw data"""
    result = []

    # process each city separately
    for city in df['city'].unique():
        city_df = df[df['city'] == city].copy()
        city_df = city_df.sort_values('timestamp').reset_index(drop=True)

        # --- time features ---
        # what hour of day? morning rush = more pollution
        city_df['hour'] = city_df['timestamp'].dt.hour

        # what day of week? weekday = more traffic
        city_df['day_of_week'] = city_df['timestamp'].dt.dayofweek

        # is it rush hour? 7-9am or 5-7pm
        city_df['is_rush_hour'] = city_df['hour'].apply(
            lambda h: 1 if (7 <= h <= 9) or (17 <= h <= 19) else 0
        )

        # is it night? less traffic, different patterns
        city_df['is_night'] = city_df['hour'].apply(
            lambda h: 1 if (22 <= h) or (h <= 5) else 0
        )

        # --- rolling averages (trend features) ---
        # average PM2.5 over last 3 hours — is pollution building up?
        city_df['pm25_3hr_avg'] = city_df['pm2_5'].rolling(window=3, min_periods=1).mean()

        # average PM2.5 over last 24 hours — daily pattern
        city_df['pm25_24hr_avg'] = city_df['pm2_5'].rolling(window=24, min_periods=1).mean()

        # average AQI over last 6 hours
        city_df['aqi_6hr_avg'] = city_df['aqi'].rolling(window=6, min_periods=1).mean()

        # --- change features (is it getting worse?) ---
        # how much did PM2.5 change from last hour?
        city_df['pm25_change'] = city_df['pm2_5'].diff().fillna(0)

        # how much did AQI change from last reading?
        city_df['aqi_change'] = city_df['aqi'].diff().fillna(0)

        # --- target variable ---
        # predict AQI 3 hours from now
        city_df['target_aqi'] = city_df['aqi'].shift(-3)

        result.append(city_df)

    final_df = pd.concat(result, ignore_index=True)

    # remove rows where we cant predict (last 3 rows per city)
    final_df = final_df.dropna(subset=['target_aqi'])

    return final_df

def save_features(df):
    """save engineered features back to database"""
    df.to_sql("air_quality_features", engine, if_exists="replace", index=False)
    print(f"✅ Saved {len(df)} rows with features to database")

if __name__ == "__main__":
    print("Loading raw data...")
    df = load_data()
    print(f"Loaded {len(df)} rows")

    print("Engineering features...")
    df_features = engineer_features(df)
    print(f"Created {len(df_features)} rows with {len(df_features.columns)} columns")

    print("\nNew features created:")
    new_cols = ['hour', 'day_of_week', 'is_rush_hour', 'is_night',
                'pm25_3hr_avg', 'pm25_24hr_avg', 'aqi_6hr_avg',
                'pm25_change', 'aqi_change', 'target_aqi']
    print(df_features[new_cols].head(10).to_string(index=False))

    save_features(df_features)