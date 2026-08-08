# 🛰️ NASA EONET Global Wildfire Intelligence Hub

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://nasa-wildfire-tracker-3pfkr5zcs2jmze5dpknvet.streamlit.app/)

An open-source climate-tech intelligence dashboard that dynamically correlates active satellite natural disaster telemetry with real-time microclimate weather metrics to evaluate global wildfire spread risks.

🌐 **Live Web Application:** [nasa-wildfire-tracker.streamlit.app](https://nasa-wildfire-tracker-3pfkr5zcs2jmze5dpknvet.streamlit.app/)

---

## 🌟 Key Features

* **Real-Time Satellite Telemetry:** Ingests live wildfire coordinates directly from **NASA's Earth Observatory Natural Event Tracker (EONET) v3 API**.
* **Microclimate Risk Modeling:** Connects to the **Open-Meteo API** to fetch live localized temperature, relative humidity, wind speed, and wind direction.
* **Algorithmic Spread Index:** Computes a custom mathematical risk score ($R$) dynamically:
  $$\text{Risk Score} = \left(\frac{\text{Wind Speed}}{10}\right) \times \left(\frac{100 - \text{Relative Humidity}}{20}\right) \times \left(\frac{\text{Temperature}}{20}\right)$$
* **Proximity Engine:** Utilizes the **Haversine Distance Formula** to calculate precise mileage from user coordinates to the nearest active threat.
* **Data Intelligence Exports:** Built-in keyword filter engine and single-click CSV intelligence report generation.

---

## 🛠️ Tech Stack & Architecture

* **Frontend / Framework:** Streamlit (Python)
* **Geospatial Mapping:** Plotly Express (OpenStreetMap tiles)
* **Data Processing:** Pandas, Math module
* **APIs Integrated:** NASA EONET v3 REST API, Open-Meteo Global Forecast API
* **Deployment:** GitHub + Streamlit Community Cloud
