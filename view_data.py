import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///data/airsense.db")
df = pd.read_sql("SELECT * FROM air_quality", engine)
print(df)