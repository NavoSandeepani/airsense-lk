# 🌬️ AirSense LK — Real-Time Air Quality Prediction System

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green?style=flat-square&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker)
![MLflow](https://img.shields.io/badge/MLflow-Tracked-orange?style=flat-square&logo=mlflow)
![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-black?style=flat-square&logo=github)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

> A production-grade MLOps pipeline that predicts Air Quality Index (AQI)
> for Sri Lankan cities in real time — built by a Computer Engineering student
> to help citizens protect themselves from dangerous pollution levels.

---

## 🎯 The Problem

Air pollution causes thousands of deaths across South Asia every year.
Most people in Sri Lanka have no way to know when the air outside is
dangerous — especially during monsoon season when pollution levels spike.

**AirSense LK solves this** by predicting AQI 24 hours in advance and
sending health advice automatically — completely free and open source.

---

## 🏙️ Cities Covered

| City | Latitude | Longitude |
|------|----------|-----------|
| 🏙️ Colombo | 6.9271 | 79.8612 |
| 🌿 Kandy | 7.2906 | 80.6337 |
| 🌊 Galle | 6.0535 | 80.2210 |
| 🕌 Jaffna | 9.6615 | 80.0255 |

---

## 🏗️ Full MLOps Architecture

```
OpenWeatherMap API
        ↓
  Data Collector          ← runs every hour automatically
  (collector.py)
        ↓
  SQLite Database         ← stores PM2.5, PM10, CO, NO2, O3...
        ↓
  Feature Engineering     ← rolling averages, rush hour flags,
  (features.py)              trend features
        ↓
  XGBoost Model           ← predicts AQI for next 3 hours
  Training (train.py)
        ↓
  MLflow Tracking         ← logs every experiment, compares runs,
                             registers best model
        ↓
  FastAPI Endpoint        ← REST API serving predictions
  (api.py)
        ↓
  Docker Container        ← runs identically on any machine
        ↓
  Streamlit Dashboard     ← live map, charts, health advice
  (streamlit_app.py)
        ↓
  GitHub Actions          ← auto test + auto build on every push
        ↓
  Evidently AI            ← detects data drift, triggers retraining
  (monitoring.py)
```

---

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Language** | Python 3.11 | Everything |
| **ML Model** | XGBoost | AQI classification |
| **Experiment Tracking** | MLflow | Track runs, register models |
| **API Framework** | FastAPI | Serve predictions |
| **Containerization** | Docker | Production deployment |
| **Dashboard** | Streamlit + Plotly | Live visualization |
| **CI/CD** | GitHub Actions | Auto test and deploy |
| **Monitoring** | Evidently AI | Data drift detection |
| **Database** | SQLite + SQLAlchemy | Store air quality data |
| **Data Source** | OpenWeatherMap API | Real-time air data |

---

## 📊 AQI Scale

| AQI Level | Category | Health Advice |
|-----------|----------|---------------|
| 1 🟢 | Good | Safe for everyone |
| 2 🟡 | Fair | Sensitive groups take care |
| 3 🟠 | Moderate | Reduce outdoor activity |
| 4 🔴 | Poor | Wear mask outdoors |
| 5 🟣 | Very Poor | Stay indoors |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker Desktop
- OpenWeatherMap API key (free at openweathermap.org)

### 1 — Clone the repository

```bash
git clone https://github.com/NavoSandeepani/airsense-lk.git
cd airsense-lk
```

### 2 — Set up environment

```bash
pip install -r requirements.txt
```

Create `.env` file:

```
OWM_API_KEY=your_openweathermap_api_key_here
```

### 3 — Collect data

```bash
python collector.py
```

Wait a few minutes for data to collect, then stop with Ctrl+C.

### 4 — Train model

```bash
python features.py
python train.py
python register_model.py
```

### 5 — Run with Docker

```bash
docker build -t airsense-api .
docker run -p 8000:8000 \
  -v ${PWD}/data:/app/data \
  -v ${PWD}/mlruns:/app/mlruns \
  -v ${PWD}/.env:/app/.env \
  airsense-api
```

### 6 — Launch dashboard

```bash
streamlit run streamlit_app.py
```

Open browser at `http://localhost:8501` 🎉

---

## 📁 Project Structure

```
airsense-lk/
│
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI/CD pipeline
│
├── tests/
│   └── test_api.py             # pytest tests for API endpoints
│
├── monitoring_reports/         # Evidently drift reports saved here
│
├── data/                       # SQLite database (gitignored)
├── mlruns/                     # MLflow experiments (gitignored)
│
├── collector.py                # Hourly data collection from API
├── features.py                 # Feature engineering pipeline
├── train.py                    # XGBoost model training + MLflow
├── register_model.py           # Register best model to MLflow
├── api.py                      # FastAPI prediction endpoint
├── streamlit_app.py            # Live dashboard
├── monitoring.py               # Evidently AI drift detection
│
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Multi-service orchestration
├── requirements.txt            # Python dependencies
└── .gitignore
```

---

## 🔌 API Endpoints

### Health Check
```
GET /health
```
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2026-06-01 12:00:00"
}
```

### List Cities
```
GET /cities
```
```json
{
  "cities": ["Colombo", "Kandy", "Galle", "Jaffna"]
}
```

### Predict AQI
```
POST /predict
Body: {"city": "Colombo"}
```
```json
{
  "city": "Colombo",
  "current_aqi": 1,
  "current_aqi_label": "Good",
  "predicted_aqi": 2,
  "predicted_aqi_label": "Fair",
  "main_pollutant": "PM2.5",
  "advice": "Acceptable air quality.",
  "pm2_5": 34.2,
  "pm10": 58.1,
  "temperature": 28.4,
  "humidity": 82.0
}
```

### City History
```
GET /history/{city}?hours=24
```

---

## 🧪 Run Tests

```bash
pytest tests/ -v
```

```
tests/test_api.py::test_health_endpoint          PASSED ✅
tests/test_api.py::test_cities_endpoint          PASSED ✅
tests/test_api.py::test_health_has_timestamp     PASSED ✅
tests/test_api.py::test_health_has_model_loaded  PASSED ✅
tests/test_api.py::test_predict_invalid_city     PASSED ✅
tests/test_api.py::test_predict_request_format   PASSED ✅
```

---

## 📈 MLflow Experiment Tracking

```bash
mlflow ui
```

Open `http://localhost:5000` to compare all training runs side by side.

---

## 🔍 Run Monitoring

```bash
python monitoring.py
```

Generates an HTML drift report in `monitoring_reports/` showing:
- Distribution comparison for all 9 features
- Drift score per column
- Automatic retraining if drift detected

---

## ⚙️ CI/CD Pipeline

Every push to `main` branch automatically:

```
Push code to GitHub
        ↓
🧪 Run Tests (pytest)        ← ~54 seconds
        ↓
🐳 Build Docker Image        ← ~1 minute
        ↓
✅ Pipeline passes           ← ready to deploy
```

---

## 🌱 Why I Built This

I am a final-year Computer Engineering student from Sri Lanka.
During my research on predictive modelling of malnutrition and
anemia in children, I became passionate about using AI to solve
real health problems in my country.

Air pollution directly affects the health of millions of Sri Lankans
— especially children and elderly people. AirSense LK is my attempt
to use modern MLOps practices to build something genuinely useful
for my community.

---

## 🎓 What I Learned

Building this project taught me that training a model is only
30% of the work. The remaining 70% is:

- Serving it reliably through an API
- Containerizing it for consistent deployment
- Testing it automatically on every code change
- Monitoring it to detect when real-world data drifts
- Retraining it to stay accurate over time

This is what separates a data science notebook from a
production AI system.

---

## 📬 Connect

**Navodya Sandeepani**
Final Year Computer Engineering Student — Sri Lanka

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat-square&logo=linkedin)](https://linkedin.com/in/www.linkedin.com/in/navodya-mapa-684b83321)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat-square&logo=github)](https://github.com/NavoSandeepani)

> Currently seeking internship opportunities in AI/ML Engineering.
> Open to remote and local positions.

---

## 📄 License

MIT License — feel free to use, modify, and share.

---

<div align="center">
Built with ❤️ for Sri Lanka 🇱🇰
<br>
<sub>XGBoost · MLflow · FastAPI · Docker · Streamlit · GitHub Actions · Evidently AI</sub>
</div>