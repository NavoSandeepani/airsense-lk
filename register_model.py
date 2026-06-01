import mlflow
from mlflow.tracking import MlflowClient

# must match train.py
mlflow.set_tracking_uri("sqlite:///mlruns/mlflow.db")

client = MlflowClient()

# find best run by accuracy
experiment = client.get_experiment_by_name("airsense-lk")
runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["metrics.accuracy DESC"]
)

best_run = runs[0]
best_accuracy = best_run.data.metrics['accuracy']
best_run_id = best_run.info.run_id

print(f"Best run ID: {best_run_id}")
print(f"Best accuracy: {best_accuracy:.4f}")

model_uri = f"runs:/{best_run_id}/model"
mlflow.register_model(model_uri, "AirSense-AQI-Predictor")

print("\n✅ Model registered as 'AirSense-AQI-Predictor'")
print(f"Use this Run ID in api.py: {best_run_id}")






import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# find best run by accuracy
experiment = client.get_experiment_by_name("airsense-lk")
runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["metrics.accuracy DESC"]
)

best_run = runs[0]
best_accuracy = best_run.data.metrics['accuracy']
best_run_id = best_run.info.run_id

print(f"Best run ID: {best_run_id}")
print(f"Best accuracy: {best_accuracy:.4f}")

# register it — tag it as your production model
model_uri = f"runs:/{best_run_id}/model"
mlflow.register_model(model_uri, "AirSense-AQI-Predictor")

print("\n✅ Model registered as 'AirSense-AQI-Predictor'")
print("Go to MLflow UI → Models tab to see it")