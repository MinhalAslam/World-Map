import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

st.set_page_config(layout="wide")
st.title("🌍 Interactive Global Weather Map")

# ---------- Step 1: Detect user's location ----------
def get_user_location():
    try:
        res = requests.get("https://ipinfo.io/json")
        data = res.json()
        lat, lon = map(float, data["loc"].split(","))
        return lat, lon, data.get("city", ""), data.get("country", "")
    except Exception:
        return 20.0, 0.0, "", ""

lat, lon, user_city, user_country = get_user_location()
st.success(f"📍 You are near: **{user_city}, {user_country}**")

# ---------- Step 2: Weather fetch function ----------
def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    return response.json()

# ---------- Step 3: Create map ----------
m = folium.Map(location=[lat, lon], zoom_start=3)

# Add user location marker
folium.Marker(
    [lat, lon],
    tooltip="Your Location",
    popup=f"{user_city}, {user_country}"
).add_to(m)

# ---------- Step 4: Map Interaction ----------
st.markdown("### 🔍 Click on any location to view weather conditions")

# This renders the map and returns data about click
map_data = st_folium(m, width=800, height=500)

coords = map_data.get("last_clicked")
if coords:
    click_lat, click_lon = coords["lat"], coords["lng"]
    weather = get_weather(click_lat, click_lon)

    if weather.get("cod") == 200:
        city = weather.get("name", "Unknown")
        country = weather["sys"].get("country", "")
        description = weather["weather"][0]["description"].capitalize()
        temp = weather["main"]["temp"]

        # Show weather info below map
        st.subheader("📌 Weather at Selected Location")
        st.markdown(f"""
        - **Location**: {city}, {country}
        - **Condition**: {description}
        - **Temperature**: {temp}°C
        """)

        # Re-render the map with weather popup
        m = folium.Map(location=[click_lat, click_lon], zoom_start=4)
        folium.Marker(
            [click_lat, click_lon],
            tooltip=f"{city}, {country}",
            popup=f"{description}, {temp}°C"
        ).add_to(m)
        st_folium(m, width=800, height=500)
    else:
        st.error("Weather data not found for this point.")
