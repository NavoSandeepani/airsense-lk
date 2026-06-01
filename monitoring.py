import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import json
import os

# evidently imports
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.metrics import (
    ColumnDriftMetric,
    DatasetDriftMetric,
    DatasetMissingValuesMetric
)
engine = create_engine("sqlite:///data/airsense.db")

# columns to monitor for drift
MONITOR_COLS = [
    'pm2_5', 'pm10', 'co', 'no2', 'o3',
    'so2', 'temperature', 'humidity', 'wind_speed'
]

def load_reference_data():
    """load first 7 days of data as reference — what model was trained on"""
    query = """
        SELECT * FROM air_quality
        ORDER BY timestamp ASC
        LIMIT 200
    """
    df = pd.read_sql(query, engine)
    df = df[MONITOR_COLS].dropna()
    print(f"✅ Reference data: {len(df)} rows")
    return df

def load_current_data():
    """load most recent data — what's coming in now"""
    query = """
        SELECT * FROM air_quality
        ORDER BY timestamp DESC
        LIMIT 200
    """
    df = pd.read_sql(query, engine)
    df = df[MONITOR_COLS].dropna()
    print(f"✅ Current data: {len(df)} rows")
    return df

def run_drift_report(reference_df, current_df):
    """generate full drift report"""
    print("\nRunning drift analysis...")

    report = Report(metrics=[
        DatasetDriftMetric(),
        DataDriftPreset(),
        DataQualityPreset(),
    ])

    report.run(
        reference_data=reference_df,
        current_data=current_df
    )

    # save HTML report
    os.makedirs("monitoring_reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"monitoring_reports/drift_report_{timestamp}.html"
    report.save_html(report_path)
    print(f"✅ Report saved: {report_path}")

    return report

def check_drift_status(report):
    """check if drift was detected and print summary"""
    result = report.as_dict()

    # find drift metrics
    drift_detected = False
    drifted_columns = []
    drift_scores = {}

    for metric in result.get('metrics', []):
        metric_id = metric.get('metric', '')

        # dataset level drift
        if 'DatasetDriftMetric' in str(metric_id):
            result_data = metric.get('result', {})
            drift_detected = result_data.get('dataset_drift', False)
            n_drifted = result_data.get('number_of_drifted_columns', 0)
            n_total = result_data.get('number_of_columns', 0)
            drift_share = result_data.get('share_of_drifted_columns', 0)

            print(f"\n{'='*50}")
            print(f"DRIFT REPORT SUMMARY")
            print(f"{'='*50}")
            print(f"Dataset drift detected: {'⚠️  YES' if drift_detected else '✅ NO'}")
            print(f"Drifted columns: {n_drifted} / {n_total}")
            print(f"Drift share: {drift_share:.1%}")

        # column level drift
        if 'ColumnDriftMetric' in str(metric_id):
            result_data = metric.get('result', {})
            col_name = result_data.get('column_name', '')
            col_drift = result_data.get('drift_detected', False)
            drift_score = result_data.get('drift_score', 0)

            if col_drift:
                drifted_columns.append(col_name)
                drift_scores[col_name] = drift_score

    if drifted_columns:
        print(f"\n⚠️  Drifted columns:")
        for col in drifted_columns:
            score = drift_scores.get(col, 0)
            print(f"   - {col}: drift score = {score:.4f}")
    else:
        print("\n✅ No column drift detected")

    return drift_detected, drifted_columns

def save_monitoring_log(drift_detected, drifted_columns):
    """save monitoring result to JSON log"""
    os.makedirs("monitoring_reports", exist_ok=True)
    log_path = "monitoring_reports/monitoring_log.json"

    # load existing log
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            log = json.load(f)
    else:
        log = []

    # add new entry
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "drift_detected": drift_detected,
        "drifted_columns": drifted_columns,
        "action": "retrain_recommended" if drift_detected else "no_action_needed"
    }
    log.append(entry)

    with open(log_path, 'w') as f:
        json.dump(log, f, indent=2)

    print(f"\n✅ Log saved to {log_path}")
    return entry

def trigger_retraining_if_needed(drift_detected):
    """if drift detected — automatically retrain model"""
    if drift_detected:
        print("\n🔄 DRIFT DETECTED — Triggering automatic retraining...")
        print("Running features.py...")
        os.system("python features.py")
        print("Running train.py...")
        os.system("python train.py")
        print("Running register_model.py...")
        os.system("python register_model.py")
        print("✅ Model retrained and registered!")
    else:
        print("\n✅ No retraining needed — model is still accurate")

if __name__ == "__main__":
    print("🔍 AirSense LK — Model Monitoring")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)

    # load data
    reference_df = load_reference_data()
    current_df = load_current_data()

    if len(reference_df) < 10 or len(current_df) < 10:
        print("❌ Not enough data for monitoring. Keep collector running.")
        exit()

    # run drift report
    report = run_drift_report(reference_df, current_df)

    # check results
    drift_detected, drifted_columns = check_drift_status(report)

    # save log
    entry = save_monitoring_log(drift_detected, drifted_columns)

    # auto retrain if needed
    trigger_retraining_if_needed(drift_detected)

    print("\n" + "="*50)
    print("✅ Monitoring complete!")
    print(f"Result: {'⚠️  DRIFT DETECTED' if drift_detected else '✅ MODEL HEALTHY'}")
    print("="*50)