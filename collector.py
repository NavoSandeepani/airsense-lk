import requests
import pandas as pd
import schedule
import time
import os
import logging

from datetime import datetime
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("OWM_API_KEY")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/collector.log"),
        logging.StreamHandler()
    ]
)

# Sri Lankan cities
CITIES = [
    {"name": "Colombo", "lat": 6.9271, "lon": 79.8612},
    {"name": "Kandy", "lat": 7.2906, "lon": 80.6337},
    {"name": "Galle", "lat": 6.0535, "lon": 80.2210},
    {"name": "Jaffna", "lat": 9.6615, "lon": 80.0255},
]

# Database connection
engine = create_engine("sqlite:///data/airsense.db")


def fetch_air_quality(city):
    """Fetch air quality data"""

    url = (
        f"http://api.openweathermap.org/data/2.5/air_pollution"
        f"?lat={city['lat']}&lon={city['lon']}&appid={API_KEY}"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    return response.json()


def fetch_weather(city):
    """Fetch weather data"""

    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?lat={city['lat']}&lon={city['lon']}"
        f"&appid={API_KEY}&units=metric"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    return response.json()


def parse_and_save():
    """Fetch and save data"""

    logging.info("Starting data collection...")

    records = []

    for city in CITIES:

        try:
            # Air quality data
            air_data = fetch_air_quality(city)

            components = air_data["list"][0]["components"]
            aqi = air_data["list"][0]["main"]["aqi"]

            # Weather data
            weather_data = fetch_weather(city)

            weather = weather_data["main"]
            wind = weather_data["wind"]

            # Create record
            record = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "city": city["name"],
                "aqi": aqi,
                "pm2_5": components["pm2_5"],
                "pm10": components["pm10"],
                "co": components["co"],
                "no2": components["no2"],
                "o3": components["o3"],
                "so2": components["so2"],
                "temperature": weather["temp"],
                "humidity": weather["humidity"],
                "wind_speed": wind["speed"]
            }

            records.append(record)

            logging.info(
                f"{city['name']} - AQI: {aqi} - PM2.5: {components['pm2_5']}"
            )

        except Exception as e:
            logging.error(f"Failed for {city['name']}: {e}")

    # Save to database
    if records:
        df = pd.DataFrame(records)

        df.to_sql(
            "air_quality",
            engine,
            if_exists="append",
            index=False
        )

        logging.info(f"Saved {len(records)} records to database")


def view_saved_data():
    """View saved database data"""

    query = """
    SELECT *
    FROM air_quality
    ORDER BY timestamp DESC
    LIMIT 20
    """

    df = pd.read_sql(query, engine)

    print("\nLatest readings:\n")
    print(df.to_string(index=False))


# Run once immediately
parse_and_save()

# Schedule every hour
schedule.every(1).hours.do(parse_and_save)

logging.info("Scheduler started - collecting every hour")
logging.info("Press Ctrl + C to stop")

# Keep running
while True:
    schedule.run_pending()
    time.sleep(60)