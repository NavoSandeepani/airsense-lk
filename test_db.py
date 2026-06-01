from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("sqlite:///data/airsense.db")

# get only Colombo data — database finds it instantly
colombo = pd.read_sql(
    "SELECT * FROM air_quality WHERE city='Colombo' ORDER BY timestamp DESC",
    engine
)
print("Colombo only:")
print(colombo)

# get average AQI per city
avg_aqi = pd.read_sql(
    "SELECT city, ROUND(AVG(aqi), 2) as avg_aqi FROM air_quality GROUP BY city",
    engine
)
print("\nAverage AQI per city:")
print(avg_aqi)

# get only dangerous readings
dangerous = pd.read_sql(
    "SELECT * FROM air_quality WHERE aqi >= 4",
    engine
)
print(f"\nDangerous readings found: {len(dangerous)}")