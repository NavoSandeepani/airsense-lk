import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# ── page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="AirSense LK",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #020818 0%, #0a1628 40%, #0d2137 100%);
    min-height: 100vh;
}

.hero-title {
    font-family: 'Orbitron', monospace;
    font-size: 52px;
    font-weight: 900;
    background: linear-gradient(90deg, #00d4ff, #00ff88, #00d4ff);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    animation: shimmer 3s linear infinite;
    letter-spacing: 4px;
    margin-bottom: 0;
}

@keyframes shimmer {
    0% { background-position: 0% center; }
    100% { background-position: 200% center; }
}

.hero-sub {
    font-size: 15px;
    color: #4a9eff;
    text-align: center;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 6px;
    opacity: 0.8;
}

.hero-line {
    width: 200px;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00d4ff, #00ff88, transparent);
    margin: 16px auto;
}

.status-bar {
    background: rgba(0, 212, 255, 0.05);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: 50px;
    padding: 8px 24px;
    text-align: center;
    font-size: 13px;
    color: #00d4ff;
    margin: 10px auto;
    max-width: 500px;
    letter-spacing: 1px;
}

.section-title {
    font-family: 'Orbitron', monospace;
    font-size: 18px;
    font-weight: 700;
    color: #00d4ff;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin: 30px 0 20px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(0,212,255,0.4), transparent);
}

.city-card {
    background: linear-gradient(135deg, rgba(10,22,40,0.9), rgba(15,35,60,0.9));
    border-radius: 20px;
    padding: 24px 16px;
    text-align: center;
    border: 1px solid rgba(0,212,255,0.15);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.city-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 20px 20px 0 0;
}

.city-card-good::before { background: linear-gradient(90deg, #00ff88, #00d4ff); }
.city-card-fair::before { background: linear-gradient(90deg, #ffe600, #ffaa00); }
.city-card-moderate::before { background: linear-gradient(90deg, #ff7e00, #ff4400); }
.city-card-poor::before { background: linear-gradient(90deg, #ff0000, #cc0000); }
.city-card-verypoor::before { background: linear-gradient(90deg, #8f3f97, #5c1a63); }

.city-name-card {
    font-family: 'Orbitron', monospace;
    font-size: 15px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 2px;
    margin-bottom: 12px;
}

.aqi-number {
    font-family: 'Orbitron', monospace;
    font-size: 64px;
    font-weight: 900;
    line-height: 1;
    margin: 8px 0;
    text-shadow: 0 0 30px currentColor;
}

.aqi-badge {
    display: inline-block;
    padding: 4px 16px;
    border-radius: 50px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin: 8px 0;
}

.pollutant-row {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: rgba(255,255,255,0.5);
    margin: 4px 0;
    padding: 0 8px;
}

.pollutant-value { color: rgba(255,255,255,0.8); font-weight: 600; }

.main-pollutant-badge {
    background: rgba(255,170,50,0.15);
    border: 1px solid rgba(255,170,50,0.3);
    color: #ffaa32;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 11px;
    margin-top: 8px;
    display: inline-block;
    letter-spacing: 1px;
}

.advice-card {
    background: rgba(0,212,255,0.05);
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 16px;
    padding: 20px;
    margin: 16px 0;
}

.advice-title {
    font-family: 'Orbitron', monospace;
    font-size: 12px;
    color: #00d4ff;
    letter-spacing: 2px;
    margin-bottom: 8px;
}

.advice-text {
    font-size: 14px;
    color: rgba(255,255,255,0.8);
    line-height: 1.6;
}

.stat-pill {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 12px;
    text-align: center;
    margin: 4px;
}

.stat-pill-label {
    font-size: 10px;
    color: rgba(255,255,255,0.4);
    letter-spacing: 1px;
    text-transform: uppercase;
}

.stat-pill-value {
    font-family: 'Orbitron', monospace;
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
    margin-top: 4px;
}

.ref-card {
    border-radius: 12px;
    padding: 14px;
    text-align: center;
    border-top: 3px solid;
    background: rgba(255,255,255,0.03);
}

.ref-label {
    font-family: 'Orbitron', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}

.ref-desc {
    font-size: 11px;
    color: rgba(255,255,255,0.5);
    margin-top: 6px;
    line-height: 1.4;
}

.timestamp-badge {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 50px;
    padding: 6px 20px;
    font-size: 12px;
    color: rgba(255,255,255,0.4);
    text-align: center;
    margin: 8px auto;
    max-width: 320px;
}

/* hide streamlit defaults */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ── config ───────────────────────────────────────────────────
API_URL = "http://localhost:8000"
CITIES = ["Colombo", "Kandy", "Galle", "Jaffna"]

CITY_COORDS = {
    "Colombo": (6.9271, 79.8612),
    "Kandy":   (7.2906, 80.6337),
    "Galle":   (6.0535, 80.2210),
    "Jaffna":  (9.6615, 80.0255),
}

AQI_COLORS = {1: "#00ff88", 2: "#ffe600", 3: "#ff7e00", 4: "#ff2200", 5: "#8f3f97"}
AQI_GLOW   = {1: "rgba(0,255,136,0.3)", 2: "rgba(255,230,0,0.3)",
              3: "rgba(255,126,0,0.3)", 4: "rgba(255,34,0,0.3)",
              5: "rgba(143,63,151,0.3)"}
AQI_CLASS  = {1: "good", 2: "fair", 3: "moderate", 4: "poor", 5: "verypoor"}
AQI_LABELS = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
AQI_ADVICE = {
    1: "🌿 Air quality is excellent. Perfect for all outdoor activities.",
    2: "😐 Acceptable air quality. Unusually sensitive individuals should limit prolonged outdoor exertion.",
    3: "😷 Moderate pollution detected. Sensitive groups should reduce outdoor activity.",
    4: "⚠️ Poor air quality. Everyone should reduce outdoor activity and wear a mask.",
    5: "🚨 Hazardous conditions. Avoid all outdoor activity. Keep windows closed."
}

# ── helpers ──────────────────────────────────────────────────
def get_prediction(city):
    try:
        r = requests.post(f"{API_URL}/predict", json={"city": city}, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def get_history(city, hours=24):
    try:
        r = requests.get(f"{API_URL}/history/{city}?hours={hours}", timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def check_api():
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.json().get("model_loaded", False)
    except:
        return False

# ── hero header ──────────────────────────────────────────────
st.markdown("""
<div style='padding: 20px 0 10px 0;'>
    <div class='hero-title'>🌬️ AIRSENSE LK</div>
    <div class='hero-sub'>Real-Time Air Quality Intelligence · Sri Lanka</div>
    <div class='hero-line'></div>
</div>
""", unsafe_allow_html=True)

# ── status ───────────────────────────────────────────────────
api_ok = check_api()
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if api_ok:
    st.markdown(f"""
    <div class='status-bar'>
        ● SYSTEM ONLINE &nbsp;|&nbsp; MODEL ACTIVE &nbsp;|&nbsp; {now}
    </div>
    """, unsafe_allow_html=True)
else:
    st.error("❌ API Offline — Start Docker container on port 8000")
    st.stop()

# ── fetch data ───────────────────────────────────────────────
predictions = {}
with st.spinner(""):
    for city in CITIES:
        d = get_prediction(city)
        if d:
            predictions[city] = d

# ── city cards ───────────────────────────────────────────────
st.markdown("<div class='section-title'>📡 Live Air Quality Index</div>",
            unsafe_allow_html=True)

cols = st.columns(4)
for i, city in enumerate(CITIES):
    with cols[i]:
        if city in predictions:
            d = predictions[city]
            aqi = d['predicted_aqi']
            color = AQI_COLORS.get(aqi, "#ffffff")
            glow = AQI_GLOW.get(aqi, "rgba(255,255,255,0.1)")
            cls = AQI_CLASS.get(aqi, "good")
            label = AQI_LABELS.get(aqi, "Unknown")

            st.markdown(f"""
            <div class='city-card city-card-{cls}'
                 style='box-shadow: 0 8px 32px {glow};'>
                <div class='city-name-card'>📍 {city.upper()}</div>
                <div class='aqi-number' style='color:{color}'>{aqi}</div>
                <div class='aqi-badge'
                     style='background:{glow}; border:1px solid {color}66;
                            color:{color};'>
                    {label}
                </div>
                <div style='margin: 12px 0; border-top: 1px solid rgba(255,255,255,0.05);
                            padding-top: 12px;'>
                    <div class='pollutant-row'>
                        <span>PM2.5</span>
                        <span class='pollutant-value'>{d['pm2_5']} μg/m³</span>
                    </div>
                    <div class='pollutant-row'>
                        <span>PM10</span>
                        <span class='pollutant-value'>{d['pm10']} μg/m³</span>
                    </div>
                    <div class='pollutant-row'>
                        <span>🌡️ Temp</span>
                        <span class='pollutant-value'>{d['temperature']}°C</span>
                    </div>
                    <div class='pollutant-row'>
                        <span>💧 Humidity</span>
                        <span class='pollutant-value'>{d['humidity']}%</span>
                    </div>
                </div>
                <div class='main-pollutant-badge'>⚠ {d['main_pollutant']}</div>
            </div>
            """, unsafe_allow_html=True)

# ── map + detail ─────────────────────────────────────────────
st.markdown("<div class='section-title'>🗺️ Sri Lanka Air Quality Map</div>",
            unsafe_allow_html=True)

map_col, detail_col = st.columns([1.2, 1])

with map_col:
    if predictions:
        lats, lons, names, aqis, colors_list, sizes, texts = [], [], [], [], [], [], []

        for city, d in predictions.items():
            lat, lon = CITY_COORDS[city]
            aqi = d['predicted_aqi']
            lats.append(lat)
            lons.append(lon)
            names.append(city)
            aqis.append(aqi)
            colors_list.append(AQI_COLORS.get(aqi, "#ffffff"))
            sizes.append(30 + aqi * 8)
            texts.append(
                f"<b>{city}</b><br>"
                f"AQI: {aqi} — {AQI_LABELS.get(aqi)}<br>"
                f"PM2.5: {d['pm2_5']} μg/m³<br>"
                f"Temp: {d['temperature']}°C"
            )

        fig_map = go.Figure()

        # glow rings
        for lat, lon, color, size in zip(lats, lons, colors_list, sizes):
            fig_map.add_trace(go.Scattermapbox(
                lat=[lat], lon=[lon],
                mode='markers',
                marker=dict(size=size + 20, color=color, opacity=0.15),
                hoverinfo='skip', showlegend=False
            ))

        # main markers
        fig_map.add_trace(go.Scattermapbox(
            lat=lats, lon=lons,
            mode='markers+text',
            marker=dict(size=sizes, color=colors_list, opacity=0.95),
            text=names,
            textposition='top right',
            textfont=dict(size=13, color='white'),
            customdata=texts,
            hovertemplate='%{customdata}<extra></extra>',
            showlegend=False
        ))

        fig_map.update_layout(
            mapbox=dict(
                style="carto-darkmatter",
                center=dict(lat=7.8731, lon=80.7718),
                zoom=6.2
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=480,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_map, use_container_width=True)

with detail_col:
    st.markdown("<br>", unsafe_allow_html=True)
    selected = st.selectbox("", CITIES, label_visibility="collapsed")

    if selected in predictions:
        d = predictions[selected]
        aqi = d['predicted_aqi']
        color = AQI_COLORS.get(aqi, "#fff")
        glow = AQI_GLOW.get(aqi, "rgba(255,255,255,0.1)")

        # gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=aqi,
            title={'text': f"{selected}", 'font': {'color': 'white', 'size': 18,
                                                    'family': 'Orbitron'}},
            gauge={
                'axis': {'range': [0, 5], 'tickcolor': 'rgba(255,255,255,0.3)',
                         'tickfont': {'color': 'white'}},
                'bar': {'color': color, 'thickness': 0.3},
                'bgcolor': 'rgba(255,255,255,0.03)',
                'bordercolor': 'rgba(255,255,255,0.05)',
                'steps': [
                    {'range': [0, 1], 'color': 'rgba(0,255,136,0.08)'},
                    {'range': [1, 2], 'color': 'rgba(255,230,0,0.08)'},
                    {'range': [2, 3], 'color': 'rgba(255,126,0,0.08)'},
                    {'range': [3, 4], 'color': 'rgba(255,34,0,0.08)'},
                    {'range': [4, 5], 'color': 'rgba(143,63,151,0.08)'},
                ],
                'threshold': {
                    'line': {'color': color, 'width': 4},
                    'thickness': 0.8,
                    'value': aqi
                }
            },
            number={'font': {'color': color, 'size': 52,
                             'family': 'Orbitron'}, 'suffix': ''}
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white'},
            height=260,
            margin=dict(l=20, r=20, t=40, b=10)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # stats row
        s1, s2, s3, s4 = st.columns(4)
        stats = [
            (s1, "PM2.5", f"{d['pm2_5']}"),
            (s2, "TEMP", f"{d['temperature']}°"),
            (s3, "HUM", f"{d['humidity']}%"),
            (s4, "PM10", f"{d['pm10']}"),
        ]
        for col, label, val in stats:
            with col:
                st.markdown(f"""
                <div class='stat-pill'>
                    <div class='stat-pill-label'>{label}</div>
                    <div class='stat-pill-value' style='color:{color}'>{val}</div>
                </div>
                """, unsafe_allow_html=True)

        # advice
        st.markdown(f"""
        <div class='advice-card' style='border-color:{color}33; margin-top:12px;'>
            <div class='advice-title'>HEALTH ADVISORY</div>
            <div class='advice-text'>{AQI_ADVICE.get(aqi, '')}</div>
        </div>
        """, unsafe_allow_html=True)

# ── history chart ────────────────────────────────────────────
st.markdown("<div class='section-title'>📈 24-Hour Trend Analysis</div>",
            unsafe_allow_html=True)

h_col1, h_col2 = st.columns([3, 1])
with h_col2:
    hist_city = st.selectbox("City", CITIES, key="hist")
    show_pm25 = st.checkbox("PM2.5", value=True)
    show_pm10 = st.checkbox("PM10", value=False)
    show_temp = st.checkbox("Temperature", value=False)

history = get_history(hist_city, hours=24)
with h_col1:
    if history and history['readings']:
        df_h = pd.DataFrame(history['readings'])
        df_h['timestamp'] = pd.to_datetime(df_h['timestamp'])
        df_h = df_h.sort_values('timestamp')

        fig_line = go.Figure()

        fig_line.add_trace(go.Scatter(
            x=df_h['timestamp'], y=df_h['aqi'],
            mode='lines+markers',
            name='AQI',
            line=dict(color='#00d4ff', width=2.5),
            marker=dict(size=7, color='#00d4ff',
                        line=dict(color='white', width=1)),
            fill='tozeroy',
            fillcolor='rgba(0,212,255,0.06)'
        ))

        if show_pm25:
            fig_line.add_trace(go.Scatter(
                x=df_h['timestamp'], y=df_h['pm2_5'],
                mode='lines', name='PM2.5',
                line=dict(color='#00ff88', width=1.5, dash='dot')
            ))

        if show_pm10:
            fig_line.add_trace(go.Scatter(
                x=df_h['timestamp'], y=df_h['pm10'],
                mode='lines', name='PM10',
                line=dict(color='#ff7e00', width=1.5, dash='dash')
            ))

        if show_temp and 'temperature' in df_h.columns:
            fig_line.add_trace(go.Scatter(
                x=df_h['timestamp'], y=df_h['temperature'],
                mode='lines', name='Temp °C',
                line=dict(color='#ff4488', width=1.5, dash='longdash')
            ))

        fig_line.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white', 'family': 'Inter'},
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)',
                       title='', showgrid=True,
                       tickfont=dict(color='rgba(255,255,255,0.4)')),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)',
                       title='',
                       tickfont=dict(color='rgba(255,255,255,0.4)')),
            legend=dict(bgcolor='rgba(0,0,0,0)',
                        font=dict(color='rgba(255,255,255,0.7)')),
            height=320,
            margin=dict(l=10, r=10, t=10, b=10),
            hovermode='x unified'
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Keep collector.py running to build history data.")

# ── city comparison ──────────────────────────────────────────
st.markdown("<div class='section-title'>🔄 City Comparison</div>",
            unsafe_allow_html=True)

if predictions:
    cities_l = list(predictions.keys())
    aqi_vals = [predictions[c]['predicted_aqi'] for c in cities_l]
    col_list = [AQI_COLORS.get(v, '#fff') for v in aqi_vals]

    fig_bar = go.Figure()
    for city, aqi_v, color in zip(cities_l, aqi_vals, col_list):
        fig_bar.add_trace(go.Bar(
            x=[city], y=[aqi_v],
            marker=dict(
                color=color,
                opacity=0.85,
                line=dict(color=color, width=1)
            ),
            text=[f"{aqi_v} — {AQI_LABELS.get(aqi_v)}"],
            textposition='outside',
            textfont=dict(color='white', size=12),
            showlegend=False
        ))

    fig_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)',
                   tickfont=dict(color='white', size=13)),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)',
                   range=[0, 7], title='AQI Level',
                   tickfont=dict(color='rgba(255,255,255,0.5)')),
        height=280,
        margin=dict(l=10, r=10, t=30, b=10),
        bargap=0.4
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ── AQI reference ────────────────────────────────────────────
st.markdown("<div class='section-title'>📊 AQI Reference Scale</div>",
            unsafe_allow_html=True)

ref_data = [
    ("1", "GOOD",      "#00ff88", "Safe for all"),
    ("2", "FAIR",      "#ffe600", "Sensitive groups"),
    ("3", "MODERATE",  "#ff7e00", "Reduce outdoor"),
    ("4", "POOR",      "#ff2200", "Wear mask"),
    ("5", "VERY POOR", "#8f3f97", "Stay indoors"),
]
rc = st.columns(5)
for col, (num, label, color, desc) in zip(rc, ref_data):
    with col:
        st.markdown(f"""
        <div class='ref-card' style='border-color:{color};
             box-shadow: 0 4px 20px {color}22;'>
            <div style='font-family:Orbitron; font-size:28px;
                        font-weight:900; color:{color};
                        text-shadow: 0 0 20px {color};'>{num}</div>
            <div class='ref-label' style='color:{color};
                 margin-top:4px;'>{label}</div>
            <div class='ref-desc'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── footer ───────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style='text-align:center; padding:20px 0;
            border-top: 1px solid rgba(255,255,255,0.05);'>
    <div style='font-family:Orbitron; font-size:11px; color:rgba(255,255,255,0.2);
                letter-spacing:3px;'>
        AIRSENSE LK · BUILT WITH MLOPS · POWERED BY REAL-TIME DATA
    </div>
    <div style='font-size:11px; color:rgba(255,255,255,0.15);
                margin-top:6px; letter-spacing:1px;'>
        Data: OpenWeatherMap API · Model: XGBoost · Stack: FastAPI + Docker + Streamlit
    </div>
</div>
""", unsafe_allow_html=True)

# ── auto refresh ─────────────────────────────────────────────
# ── auto refresh ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    auto = st.checkbox("Auto Refresh", value=True)

    if auto:
        # countdown timer
        countdown = st.empty()
        refresh_every = 300  # 5 minutes

        for remaining in range(refresh_every, 0, -1):
            mins = remaining // 60
            secs = remaining % 60
            countdown.markdown(f"""
            <div style='background:rgba(0,212,255,0.05);
                        border:1px solid rgba(0,212,255,0.2);
                        border-radius:10px; padding:10px;
                        text-align:center;'>
                <div style='font-size:10px; color:rgba(255,255,255,0.4);
                            letter-spacing:2px;'>NEXT REFRESH</div>
                <div style='font-family:Orbitron; font-size:22px;
                            color:#00d4ff; font-weight:700;'>
                    {mins:02d}:{secs:02d}
                </div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1)

        st.rerun()
    else:
        if st.button("🔄 Refresh Now"):
            st.rerun()

    st.markdown("---")
    st.markdown("**API Status**")
    st.markdown(f"{'🟢 Online' if api_ok else '🔴 Offline'}")
    st.markdown(f"**Endpoint:** `localhost:8000`")
    st.markdown("---")
    st.markdown("**Cities Monitored**")
    for city in CITIES:
        if city in predictions:
            aqi = predictions[city]['predicted_aqi']
            st.markdown(f"📍 {city} — AQI **{aqi}**")