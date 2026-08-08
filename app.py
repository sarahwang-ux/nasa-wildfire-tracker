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
*Integrating **NASA Earth Observatory Natural Event Tracker (EONET) API** to monitor live active wildfires, thermal anomalies, and climate risks worldwide.*
""")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🌍 Global Event Controls")
status_filter = st.sidebar.radio("Event Status", ["Active", "All Events (Including Historic)"])
days_back = st.sidebar.slider("Days Back to Scan NASA Satellite Feeds", 7, 365, 60)

# --- NASA API DATA FETCHING ---
@st.cache_data(ttl=3600)
def fetch_nasa_events(days):
    # Category 8 in NASA EONET is Wildfires
    status_param = "open" if status_filter == "Active" else "all"
    url = f"https://eonet.gsfc.nasa.gov/api/v3/categories/wildfires?days={days}&status={status_param}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        events_list = []
        for event in data.get("events", []):
            title = event.get("title")
            category = event.get("categories")[0]["title"] if event.get("categories") else "Wildfire"
            
            # Extract coordinates and date from geometry
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

with st.spinner("Connecting to NASA Earth Observatory API..."):
    df = fetch_nasa_events(days_back)

# --- METRICS & VISUALS ---
if not df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Live Wildfire Events Detected", len(df))
    col2.metric("Data Source", "NASA EONET v3 API")
    col3.metric("Telemetry Status", "ONLINE ✅")

    st.markdown("---")

    # Fully Interactive Global Map (Scatter Geo)
    st.subheader("🔥 Global Wildfire Satellite Telemetry")
    
    fig_map = px.scatter_geo(
        df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Event Name",
        hover_data={"Date Recorded": True, "Latitude": ":.2f", "Longitude": ":.2f"},
        color_discrete_sequence=["#FF4B4B"],
        title="Active Wildfire Coordinates Captured via NASA Satellite Network",
        projection="natural earth"
    )
    
    # Styling and enabling interactive controls
    fig_map.update_traces(marker=dict(size=10, opacity=0.85, symbol="circle"))
    fig_map.update_geos(
        showcountries=True, 
        countrycolor="lightgray",
        showcoastlines=True,
        coastlinecolor="gray",
        showland=True,
        landcolor="#F0F2F6",
        fitbounds="locations"
    )
    fig_map.update_layout(height=650, margin={"r":0,"t":40,"l":0,"b":0})
    
    st.plotly_chart(fig_map, use_container_width=True)

    # Data Table View
    with st.expander("📄 View Raw Telemetry Data Table"):
        st.dataframe(df)

else:
    st.warning("No active wildfire events returned from NASA for the selected timeframe. Try increasing the 'Days Back' slider in the sidebar!")
