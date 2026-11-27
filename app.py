from datetime import datetime

import pydeck as pdk
import requests
import streamlit as st

API_URL = st.secrets["API_URL"]


def ask_user_() -> dict[str, str]:
    """_summary_

    Returns:
        dict[str, str]: _description_
    """
    pickup_datetime = st.datetime_input(
        "Pickup date and time (UTC)",
        datetime(2009, 11, 19, 16, 45),
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

    params = {
        "pickup_datetime": pickup_datetime,
        "pickup_longitude": pickup_longitude,
        "pickup_latitude": pickup_latitude,
        "dropoff_longitude": dropoff_longitude,
        "dropoff_latitude": dropoff_latitude,
        "passenger_count": passenger_count,
    }
    return params


def get_route_(
    pickup_lon: float, pickup_lat: float, dropoff_lon: float, dropoff_lat: float
) -> dict | list:
    """_summary_

    Args:
        pickup_lon (float): _description_
        pickup_lat (float): _description_
        dropoff_lon (float): _description_
        dropoff_lat (float): _description_

    Returns:
        dict | list: _description_
    """
    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{pickup_lon},{pickup_lat};{dropoff_lon},{dropoff_lat}"
    )
    try:
        res = requests.get(
            url,
            params={"overview": "full", "geometries": "geojson"},
            timeout=5,
        )
        res.raise_for_status()
        return res.json()["routes"][0]["geometry"]["coordinates"]
    except (requests.RequestException, KeyError, IndexError):
        return [[pickup_lon, pickup_lat], [dropoff_lon, dropoff_lat]]


def main() -> None:
    try:
        st.title("NYC Taxi Fare")
        with st.form("trip"):
            params = ask_user_()
            submitted = st.form_submit_button("Get Fare")

        if submitted:
            try:
                draw_map_(params)
            except requests.RequestException as error:
                st.error(f"Could not get a prediction from the API. {error}")
    except (KeyError, TypeError, ValueError):
        st.error("The API response did not contain a valid fare.")


def draw_map_(params: dict) -> None:
    """_summary_

    Args:
        params (dict): _description_
    """
    response = requests.get(f"{API_URL}/predict", params=params, timeout=10)
    response.raise_for_status()
    fare = float(response.json()["fare"])
    st.success(f"Estimated fare: ${fare:.2f}")
    pickup_longitude = params["pickup_longitude"]
    pickup_latitude = params["pickup_latitude"]
    dropoff_longitude = params["dropoff_longitude"]
    dropoff_latitude = params["dropoff_latitude"]
    points = [
        {
            "name": "Pickup",
            "lon": pickup_longitude,
            "lat": pickup_latitude,
            "color": [0, 200, 100],
        },
        {
            "name": "Dropoff",
            "lon": dropoff_longitude,
            "lat": dropoff_latitude,
            "color": [220, 50, 50],
        },
    ]
    path = get_route_(
        pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude
    )

    route = [{"path": path, "fare": f"${fare:.2f}"}]

    st.pydeck_chart(
        pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=(pickup_latitude + dropoff_latitude) / 2,
                longitude=(pickup_longitude + dropoff_longitude) / 2,
                zoom=12,
            ),
            layers=[
                pdk.Layer(
                    "PathLayer",
                    data=route,
                    get_path="path",
                    get_color=[30, 144, 255],
                    width_min_pixels=4,
                    pickable=True,
                ),
                pdk.Layer(
                    "ScatterplotLayer",
                    data=points,
                    get_position=["lon", "lat"],
                    get_fill_color="color",
                    get_radius=120,
                    pickable=True,
                ),
            ],
        )
    )


main()
