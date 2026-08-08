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
        humidity = current.get("relative_humidity_2m", 50)
        wind = current.get("wind_speed_10m", 10)
        
        # Calculate Risk Index
        if wind > 30 and humidity < 25:
            risk = "CRITICAL 🚨"
        elif wind > 20 or humidity < 35:
            risk = "HIGH ⚠️"
        elif wind > 10:
            risk = "MODERATE 🟡"
        else:
            risk = "LOW 🟢"
            
        return temp, humidity, wind, risk
    except Exception as e:
        return "N/A", "N/A", "N/A", "Unknown"

# Fetch Main Data
with st.spinner("Fetching NASA Satellite Feeds..."):
    df = fetch_nasa_events(days_back)

# --- DASHBOARD LAYOUT ---
if not df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Live Wildfire Events Detected", len(df))
    col2.metric("Primary Data Source", "NASA EONET v3 API")
    col3.metric("Weather Telemetry", "Open-Meteo Synchronized ✅")

    st.markdown("---")

    # Interactive Map (OpenStreetMap Style)
    st.subheader("🔥 Interactive Global Wildfire Map")
    
    fig_map = px.scatter_map(
        df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Event Name",
        hover_data={"Date Recorded": True, "Latitude": ":.2f", "Longitude": ":.2f"},
        color_discrete_sequence=["#FF4B4B"],
        title="Active Coordinates Captured via NASA Satellite Network",
        zoom=1,
        map_style="open-street-map"
    )
    
    fig_map.update_traces(marker=dict(size=12, opacity=0.85))
    fig_map.update_layout(height=600, margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    # Risk Assessment Module
    st.markdown("---")
    st.subheader("🔬 Atmospheric Threat Analysis")
    st.write("Select an active event to stream atmospheric conditions and calculate real-time spread risk:")
    
    selected_event = st.selectbox("Select Wildfire Event", df["Event Name"].unique())
    event_data = df[df["Event Name"] == selected_event].iloc[0]
    
    # Fetch live weather for selected event
    temp, humidity, wind, risk = fetch_weather_risk(event_data["Latitude"], event_data["Longitude"])
    
    r_col1, r_col2, r_col3, r_col4 = st.columns(4)
    r_col1.metric("Local Temperature", f"{temp} °C")
    r_col2.metric("Relative Humidity", f"{humidity} %")
    r_col3.metric("Wind Speed (10m)", f"{wind} km/h")
    r_col4.metric("Calculated Spread Risk", risk)

    # Data Table View
    with st.expander("📄 View Raw Telemetry Data Table"):
        st.dataframe(df)

else:
    st.warning("No active wildfire events returned. Adjust the sidebar settings!")
