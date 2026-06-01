import pandas as pd
import numpy as np
import mlflow
import mlflow.xgboost
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_absolute_error
from xgboost import XGBClassifier
import warnings
import os
warnings.filterwarnings('ignore')

# SQLite backend
mlflow.set_tracking_uri("sqlite:///mlruns/mlflow.db")
mlflow.set_experiment("airsense-lk")

engine = create_engine("sqlite:///data/airsense.db")

FEATURE_COLS = [
    'pm2_5', 'pm10', 'co', 'no2', 'o3', 'so2',
    'temperature', 'humidity', 'wind_speed',
    'hour', 'day_of_week', 'is_rush_hour', 'is_night',
    'pm25_3hr_avg', 'pm25_24hr_avg', 'aqi_6hr_avg',
    'pm25_change', 'aqi_change'
]

def load_features():
    df = pd.read_sql("SELECT * FROM air_quality_features", engine)
    print(f"Loaded {len(df)} rows")
    return df

def train_model(df, n_estimators, max_depth, learning_rate):
    X = df[FEATURE_COLS]
    y = df['target_aqi'].astype(int) - 1

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    with mlflow.start_run() as run:
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("learning_rate", learning_rate)

        model = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=42,
            eval_metric='mlogloss'
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)

        mlflow.log_metric("accuracy", round(accuracy, 4))
        mlflow.log_metric("mae", round(mae, 4))

        # save model — this is the critical part
        model.save_model("best_model.ubj")
        mlflow.log_artifact("best_model.ubj", "model")

        run_id = run.info.run_id
        artifact_uri = run.info.artifact_uri

        print(f"  n_estimators={n_estimators} → accuracy={accuracy:.4f}")
        print(f"  Run ID: {run_id}")
        print(f"  Artifact URI: {artifact_uri}")

        return run_id, accuracy

if __name__ == "__main__":
    print("Loading features...")
    df = load_features()

    print("\nTraining models...\n")
    results = []

    run_id1, acc1 = train_model(df, n_estimators=100, max_depth=3, learning_rate=0.1)
    results.append((run_id1, acc1))

    run_id2, acc2 = train_model(df, n_estimators=200, max_depth=5, learning_rate=0.05)
    results.append((run_id2, acc2))

    run_id3, acc3 = train_model(df, n_estimators=300, max_depth=6, learning_rate=0.01)
    results.append((run_id3, acc3))

    # find best run
    best_run_id, best_acc = max(results, key=lambda x: x[1])

    print(f"\n✅ Training complete!")
    print(f"Best Run ID: {best_run_id}")
    print(f"Best Accuracy: {best_acc:.4f}")
    print(f"\nNow run: python register_model.py")