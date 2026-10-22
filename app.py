
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

CSV_FILE = Path(__file__).parent / "sensor_data.csv"

st.set_page_config(
    page_title="AI Environment Monitor",
    page_icon="🌡️",
    layout="wide",
)

st.title("AI Environment Monitor")
st.caption("Arduino Uno · DHT11 · LDR")

# Refresh the dashboard every 2 seconds.
st_autorefresh(interval=2000, key="dashboard_refresh")


@st.cache_data(ttl=1)
def load_data(file_path, modified_time):
    return pd.read_csv(file_path)


if not CSV_FILE.exists() or CSV_FILE.stat().st_size == 0:
    st.warning("No sensor data found. Start monitor.py first.")
    st.stop()

try:
    df = load_data(str(CSV_FILE), CSV_FILE.stat().st_mtime)
except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as error:
    st.error(f"Could not read sensor data: {error}")
    st.stop()

required_columns = [
    "timestamp",
    "temperature_c",
    "humidity_percent",
    "light_raw",
]

if not all(column in df.columns for column in required_columns):
    st.error("The CSV file does not have the expected columns.")
    st.stop()

for column in ["temperature_c", "humidity_percent", "light_raw"]:
    df[column] = pd.to_numeric(df[column], errors="coerce")

df["timestamp"] = pd.to_datetime(
    df["timestamp"], errors="coerce", utc=True
)

df = df.dropna(subset=required_columns)
df = df.sort_values("timestamp")

if df.empty:
    st.warning("No valid sensor readings are available yet.")
    st.stop()

latest = df.iloc[-1]
seconds_old = (
    pd.Timestamp.now(tz="UTC") - latest["timestamp"]
).total_seconds()

if seconds_old <= 10:
    st.success("Receiving recent sensor data")
else:
    st.warning(
        f"Data may be stale. Last reading was "
        f"{max(0, int(seconds_old))} seconds ago."
    )

st.caption(
    "Last reading: "
    + latest["timestamp"].strftime("%Y-%m-%d %H:%M:%S UTC")
)

temperature_col, humidity_col, light_col = st.columns(3)

temperature_col.metric(
    "Temperature",
    f"{latest['temperature_c']:.1f} °C",
)

humidity_col.metric(
    "Humidity",
    f"{latest['humidity_percent']:.1f}%",
)

light_col.metric(
    "Light level",
    f"{int(latest['light_raw'])}",
)

st.divider()
st.subheader("Sensor history")

# Show the most recent 100 measurements.
recent = df.tail(100).set_index("timestamp")

st.markdown("**Temperature (°C)**")
st.line_chart(recent[["temperature_c"]], height=220)

st.markdown("**Humidity (%)**")
st.line_chart(recent[["humidity_percent"]], height=220)

st.markdown("**Light level (raw analog value)**")
st.line_chart(recent[["light_raw"]], height=220)

with st.expander("View recent measurements"):
    display_df = df.tail(20).sort_values(
        "timestamp", ascending=False
    ).copy()

    display_df["timestamp"] = display_df["timestamp"].dt.strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    st.dataframe(display_df, use_container_width=True)

st.caption(
    f"Showing up to 100 recent readings · "
    f"{len(df)} total records in the CSV"
)
