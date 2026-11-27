import os

import requests
import streamlit as st

API_URL = os.environ["API_URL"]

st.title("NYC Taxi Fare")


with st.form("trip"):
    pickup_datetime = st.text_input(
        "Pickup date and time (UTC)", "2013-07-06 17:18:00 UTC"
    )
    pickup_longitude = st.number_input(
        "Pickup longitude", value=-73.950655, format="%.6f"
    )
    pickup_latitude = st.number_input("Pickup latitude", value=40.783282, format="%.6f")
    dropoff_longitude = st.number_input(
        "Dropoff longitude", value=-73.984365, format="%.6f"
    )
    dropoff_latitude = st.number_input(
        "Dropoff latitude", value=40.769802, format="%.6f"
    )
    passenger_count = st.number_input("Passengers", min_value=1, max_value=8, value=1)
    submitted = st.form_submit_button("Estimate fare")

if submitted:
    params = {
        "pickup_datetime": pickup_datetime,
        "pickup_longitude": pickup_longitude,
        "pickup_latitude": pickup_latitude,
        "dropoff_longitude": dropoff_longitude,
        "dropoff_latitude": dropoff_latitude,
        "passenger_count": passenger_count,
    }

    try:
        response = requests.get(f"{API_URL}/predict", params=params, timeout=10)
        response.raise_for_status()
        fare = float(response.json()["fare"])
    except requests.RequestException as error:
        st.error(f"Could not get a prediction from the API. {error}")
    except (KeyError, TypeError, ValueError):
        st.error("The API response did not contain a valid fare.")
    else:
        st.success(f"Estimated fare: ${fare:.2f}")
