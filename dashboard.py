import streamlit as st
# MUST BE FIRST - NO EXCEPTIONS
st.set_page_config(layout="wide", page_title="Singapore Rainfall", page_icon="🌧️")

# Imports (AFTER set_page_config)
import pandas as pd
import plotly.express as px
import pydeck as pdk
from datetime import datetime, timedelta
import pytz
from src.queries import get_last_12hour_data, get_current_month_data

# Main dashboard
def get_latest_rainfall_data():
    data = get_last_12hour_data()
    latest_rainfall = data[data['timestamp'] == data['timestamp'].max()]
    return latest_rainfall

live_rainfall_data = get_latest_rainfall_data()

# Check if data exists
if live_rainfall_data.empty:
    st.error("No data found in database")
    st.stop()

# 0. Alert!!!
# def get_dummy_data():
#     return pd.DataFrame([{
#         'station_id': 'S123',
#         'station_name': 'Yio Chu Kang Road',
#         'timestamp': datetime.now().isoformat(),
#         'rainfall_mm': 5.7,  
#         'latitude': 1.3815,
#         'longitude': 103.8450
#     },
#     {
#         'station_id': 'S124',
#         'station_name': 'West Coast Road',
#         'timestamp': datetime.now().isoformat(),
#         'rainfall_mm': 15.7, 
#         'latitude': 1.3815,
#         'longitude': 103.8450
#     }
#     ])

# def get_monthly_average_dummy():
#     return {'S123': 4.2, 'S124': 12.2} 
current_month_data = get_current_month_data()
current_month_data = current_month_data.groupby('station_id')['rainfall_mm'].mean().to_dict()
# current_month_data = get_monthly_average_dummy()
# live_rainfall_data = get_dummy_data()

alert_live_rainfall_data = live_rainfall_data

alerts = alert_live_rainfall_data[
    alert_live_rainfall_data.apply(
        lambda row: row['rainfall_mm'] > current_month_data.get(row['station_id'], 0),
        axis=1
    )
][['station_id', 'station_name', 'rainfall_mm']] 
alerts['monthly_avg'] = alerts['station_id'].map(current_month_data)
alerts = alerts.sort_values('rainfall_mm', ascending=False)

if not alerts.empty:
    st.subheader("🆘 ALERT: Areas Exceeding Monthly Average")
    st.dataframe(
        alerts.rename(columns={
            'station_id': 'Station ID',
            'station_name': 'Location',
            'rainfall_mm': 'Current (mm)',
            'monthly_avg': 'Monthly Avg (mm)'
        }),
        hide_index=True,
        column_config={
            "Current (mm)": st.column_config.NumberColumn(
                format="%.1f mm",
                help="Current rainfall measurement"
            ),
            "Monthly Avg (mm)": st.column_config.NumberColumn(
                format="%.1f mm",
                help="Typical rainfall for this month"
            )
        }
    )
else:
    st.success("✅ All areas within normal ranges")
st.markdown('#')

# 1. Map Visualization
# Convert timestamp
live_rainfall_data['hour'] = live_rainfall_data['timestamp'].dt.hour
data = live_rainfall_data[live_rainfall_data['rainfall_mm'] > 0]

st.header("🔴 Live Rainfall Map")
st.pydeck_chart(pdk.Deck(
    # map_style='mapbox://styles/mapbox/light-v9',
    map_style='mapbox://styles/mapbox/dark-v10',
    initial_view_state=pdk.ViewState(
        latitude=1.3521,
        longitude=103.8198,
        zoom=10.5
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=data,
            get_position=['longitude', 'latitude'],
            get_fill_color='[255, 255 - rainfall_mm*10, 0, 200]',  # Yellow (low) -> Red (high)
            get_radius='rainfall_mm * 50 + 100',
            radius_scale=1,
            radius_min_pixels=5,
            radius_max_pixels=50,
            pickable=True,
            opacity=0.8
        )
    ],
    tooltip={
        "html": """
            <b>{station_name}</b><br>
            Rainfall: {rainfall_mm} mm<br>
            <div style="
                width: 100%; 
                height: 10px; 
                background: linear-gradient(to right, yellow, red);
                margin-top: 5px;
            "></div>
        """,
        "style": {
            "backgroundColor": "#333333",
            "color": "white",
            "padding": "10px"
        }
    }
))

# 2. Top/Low Tables
col1, col2 = st.columns(2)
top_10_data = live_rainfall_data
with col1:
    st.subheader("🚨 Top 10 Highest")
    st.dataframe(
        top_10_data[top_10_data['rainfall_mm'] > 0].nlargest(10, 'rainfall_mm')[['station_name', 'rainfall_mm']],
        column_config={"rainfall_mm": "Rainfall (mm)", "station_name": "Location"},
        hide_index=True
    )

with col2:
    st.subheader("🌤️ Top 10 Lowest")
    st.dataframe(
        top_10_data[top_10_data['rainfall_mm'] > 0].nsmallest(10, 'rainfall_mm')[['station_name', 'rainfall_mm']],
        column_config={"rainfall_mm": "Rainfall (mm)", "station_name": "Location"},
        hide_index=True
    )

# 3. Hourly Chart (Enhanced)
st.markdown('#')
st.subheader("🕒 Last 12 Hours Rainfall by Station")

hourly_df = get_last_12hour_data()

# Process data
hourly_df['hour'] = hourly_df['timestamp'].dt.strftime('%H:%M')


# Station filter
stations = sorted(hourly_df['station_name'].unique())
selected_stations = st.multiselect(
    "Select stations to display:",
    options=stations,
    default=stations[:5]  # Show first 3 by default
)

# Filter and reshape data
filtered_data = hourly_df[hourly_df['station_name'].isin(selected_stations)] \
                if selected_stations else hourly_df

# Create stacked line chart
chart = px.area(
    filtered_data,
    x='hour',
    y='rainfall_mm',
    color='station_name',
    labels={'hour': 'Time', 'rainfall_mm': 'Rainfall (mm)', 'station_name': 'Station'},
    title='Rainfall Accumulation by Station',
    line_shape='spline'
)

# Customize appearance
chart.update_layout(
    hovermode='x unified',
    yaxis_title='Rainfall (mm)',
    xaxis_title='Time (Last 12 Hours)',
    legend_title_text='Station',
    plot_bgcolor='rgba(0,0,0,0)'
)

# Show chart
st.plotly_chart(chart, use_container_width=True)
