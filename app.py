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
    # Radius of the Earth in miles
    R = 3958.8
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
def fetch_nasa_
