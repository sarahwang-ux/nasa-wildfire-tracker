import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NASA Earth Observatory | Wildfire Analytics",
    page_icon="🛰️",
    layout="wide"
)

# --- TITLE & HEADER ---
st.title("🛰️ NASA EONET Global Wildfire Intelligence Hub")
st.markdown("""
*Integrating **NASA Earth Observatory Natural Event Tracker (EONET)** & **Global Weather Telemetry** to evaluate active fire spread risks in real time.*
""")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🌍 Global Event Controls")
status_filter = st.sidebar.radio("Event Status", ["Active", "All Events (Including Historic)"])
days_back = st.sidebar.slider("Days Back to Scan NASA Satellite Feeds", 7, 365, 90)

# --- NASA API DATA FETCHING ---
@st.cache_data(ttl=3600)
def fetch_nasa_events(days):
    status_param = "open" if status_filter == "Active" else "all"
    url = f"https://eonet.gsfc.nasa.gov/api/v3/categories/wildfires?days={days}&status={status_param}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        events_list = []
        for event in data.get("events", []):
            title = event.get("title")
            category = event.get("categories")[0]["title"] if event.get("categories") else "Wildfire"
            
            geometries = event.get("geometry", [])
            for geo in geometries:
                date = geo.get("date")
                coords = geo.get("coordinates")
                if geo.get("type") == "Point" and coords:
                    lon, lat = coords[0], coords[1]
                    events_list.append({
                        "Event Name": title,
                        "Category": category,
                        "Latitude": lat,
                        "Longitude": lon,
                        "Date Recorded": date[:10] if date else "N/A"
                    })
        return pd.DataFrame(events_list)
    except Exception as e:
        st.error(f"Error fetching data from NASA EONET API: {e}")
        return pd.DataFrame()

# --- LIVE WEATHER TELEMETRY FUNCTION ---
def fetch_weather_risk(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
    try:
        res = requests.get(url, timeout=5).json()
        current = res.get("current", {})
        temp = current.get("temperature_2m", 20)
        humidity = current
