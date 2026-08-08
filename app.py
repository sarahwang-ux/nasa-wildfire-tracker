import streamlit as st
import pandas as pd
import requests
import math
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NASA Earth Observatory | Wildfire Analytics",
    page_icon="🛰️",
    layout="wide"
)

# --- HAVERSINE DISTANCE FORMULA ---
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 3958.8  # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- TITLE & HEADER ---
st.title("🛰️ NASA EONET Global Wildfire Intelligence Hub")
st.markdown("""
*Integrating **NASA Earth Observatory Telemetry**, **Open-Meteo Microclimate Data**, and **Proximity Analysis** to evaluate wildfire threats globally.*
""")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🌍 Global Event Controls")
status_filter = st.sidebar.radio("Event Status", ["Active", "All Events (Including Historic)"])
days_back = st.sidebar.slider("Days Back to Scan NASA Satellite Feeds", 7, 365, 90)

# User Location Input in Sidebar
st.sidebar.markdown("---")
st.sidebar.header("📍 User Proximity Analysis")
user_lat = st.sidebar.number_input("Your Latitude", value=37.7749, format="%.4f")
user_lon = st.sidebar.number_input("Your Longitude", value=-122.4194, format="%.4f")

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

# --- LIVE WEATHER & ALGORITHMIC RISK TELEMETRY ---
def fetch_weather_risk(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"
    try:
        res = requests.get(url, timeout=5).json()
        current = res.get("current", {})
        temp = current.get("temperature_2m", 20)
        humidity = current.get("relative_humidity_2m", 50)
        wind = current.get("wind_speed_10m", 10)
        direction = current.get("wind_direction_10m", 0)
        
        # Algorithmic Weighted Risk Computation
        raw_score = (wind / 10.0) * ((100.0 - humidity) / 20.0) * (temp / 20.0)
        
        if raw_score >= 8.0:
            risk = "CRITICAL 🚨"
        elif raw_score >= 4.0:
            risk = "HIGH ⚠️"
        elif raw_score >= 2.0:
            risk = "MODERATE 🟡"
        else:
            risk = "LOW 🟢"
            
        return temp, humidity, wind, direction, risk, round(raw_score, 2)
    except Exception as e:
        return "N/A", "N/A", "N/A", "N/A", "Unknown", 0.0

# Fetch Main Data
with st.spinner("Fetching NASA Satellite Feeds..."):
    df = fetch_nasa_events(days_back)

# --- DASHBOARD LAYOUT ---
if not df.empty:
    # Calculate Distances to User Location
    df["Distance (Miles)"] = df.apply(
        lambda row: round(calculate_distance(user_lat, user_lon, row["Latitude"], row["Longitude"]), 1),
        axis=1
    )
    
    nearest_event = df.loc[df["Distance (Miles)"].idxmin()]

    # Top Metrics Bar
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Live Events Tracked", len(df))
    col2.metric("Nearest Active Threat", f"{nearest_event['Distance (Miles)']} mi")
    col3.metric("Primary Data Feed", "NASA EONET v3")
    col4.metric("Telemetry Engine", "Open-Meteo Sync ✅")

    st.markdown("---")

    # Search & Filter Engine
    st.subheader("🔍 Event Search & Filter Engine")
    search_query = st.text_input("Filter events by keyword/region (e.g., 'California', 'Canada'):", "")
    
    if search_query:
        filtered_df = df[df["Event Name"].str.contains(search_query, case=False, na=False)]
    else:
        filtered_df = df

    # Interactive Map
    st.subheader("🔥 Interactive Global Wildfire Telemetry Map")
    
    fig_map = px.scatter_map(
        filtered_df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Event Name",
        hover_data={"Distance (Miles)": ":.1f", "Date Recorded": True, "Latitude": ":.2f", "Longitude": ":.2f"},
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
    st.subheader("🔬 Atmospheric Threat & Risk Score Engine")
    st.write("Select an active event to stream microclimate conditions and run algorithmic risk modeling:")
    
    selected_event = st.selectbox("Select Wildfire Event", filtered_df["Event Name"].unique())
    
    if selected_event:
        event_data = filtered_df[filtered_df["Event Name"] == selected_event].iloc[0]
        
        # Fetch live weather for selected event
        temp, humidity, wind, direction, risk, raw_score = fetch_weather_risk(event_data["Latitude"], event_data["Longitude"])
        
        r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns(5)
        r_col1.metric("Local Temperature", f"{temp} °C")
        r_col2.metric("Relative Humidity", f"{humidity} %")
        r_col3.metric("Wind Speed (10m)", f"{wind} km/h")
        r_col4.metric("Wind Bearing", f"{direction}°")
        r_col5.metric("Algorithmic Risk Index", f"{raw_score} ({risk})")

    # Data Export & Table Section
    st.markdown("---")
    st.subheader("📊 Export & Raw Data Telemetry")
    
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Intelligence Report (CSV)",
        data=csv_data,
        file_name="nasa_wildfire_intelligence_report.csv",
        mime="text/csv",
    )
    
    with st.expander("📄 View Full Data Table with Proximity Metrics"):
        st.dataframe(filtered_df.sort_values(by="Distance (Miles)"))

else:
    st.warning("No active wildfire events returned. Adjust the sidebar settings!")
