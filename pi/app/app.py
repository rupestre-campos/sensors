import streamlit as st
import pandas as pd
import requests
import datetime
from dateutil.relativedelta import relativedelta
import altair as alt

st.set_page_config(page_title="sensors", layout="wide")
# API URL
API_URL = "http://localhost:5000/sensor-data/"  # Replace with your FastAPI URL

def fetch_data(start_date: str, end_date: str, limit: int):
    response = requests.get(API_URL, params={"start_date": start_date, "end_date": end_date, "limit": limit})
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("Failed to fetch data from API")
        return pd.DataFrame()

def display_max_min(df, column_name):
    max_value = df[column_name].max()
    min_value = df[column_name].min()
    max_time = df[df[column_name] == max_value]['datetime'].iloc[0]
    min_time = df[df[column_name] == min_value]['datetime'].iloc[0]
    return max_value, min_value, max_time, min_time


def plot_altair_chart(df, column, y_min, y_max):
    # Define the date-time format for the tooltip
    datetime_format = "%Y-%m-%d %H:%M:%S"

    line = alt.Chart(df).mark_line().encode(
        x='datetime:T',
        y=alt.Y(column + ':Q', scale=alt.Scale(domain=[y_min, y_max])),
        tooltip=[alt.Tooltip('datetime:T', title='Time', format=datetime_format),
                 alt.Tooltip(column + ':Q', title=column.capitalize())]
    ).interactive()

    points = alt.Chart(df).mark_point(size=10, filled=True, color='red').encode(
        x='datetime:T',
        y=alt.Y(column + ':Q', scale=alt.Scale(domain=[y_min, y_max])),
        tooltip=[alt.Tooltip('datetime:T', title='Time', format=datetime_format),
                 alt.Tooltip(column + ':Q', title=column.capitalize())]
    )

    chart = line + points  # Overlay points on line chart
    return chart


def show_variable(df, column, st_column):
    column_scale = {
        "temperature": "°C",
        "pressure": "hPa",
        "humidity": "%"

    }
    current_data = df.iloc[0]
    with st_column:
        st.write(f"#### {column.capitalize()}")
        st.write(f"**{current_data[column]} {column_scale[column]}**")
        max_value, min_value, max_time, min_time = display_max_min(df, column)
        st.write(f'Max: **{max_value}** at {max_time.strftime("%Y-%m-%d T %H:%M:%S UTC")}')
        st.write(f'Min: **{min_value}** at {min_time.strftime("%Y-%m-%d T %H:%M:%S UTC")}')
        y_min = min_value - (0.1 * (max_value - min_value))  # Adding some padding
        y_max = max_value + (0.1 * (max_value - min_value))  # Adding some padding
        chart = plot_altair_chart(df, column, y_min, y_max)
        st.altair_chart(chart, use_container_width=True)

def main():
    st.title("Sensor Data")

    # Sidebar for user inputs
    st.sidebar.header("Filter Options")
    selected_date = st.sidebar.date_input("Select Date", value=datetime.date.today())
    time_period = st.sidebar.radio("Select Time Period", ("Day", "Week", "Month", "Year"))
    limit = None  # st.sidebar.number_input("Limit", min_value=1, max_value=1000, value=100)

    # Calculate start and end date based on the selected time period
    if time_period == "Day":
        start_date = datetime.datetime.combine(selected_date, datetime.time.min)
        end_date = datetime.datetime.combine(selected_date, datetime.time.max)
    elif time_period == "Week":
        start_date = selected_date - datetime.timedelta(days=7)
        end_date = datetime.datetime.combine(selected_date, datetime.time.max)
    elif time_period == "Month":
        start_date = selected_date - relativedelta(months=1)
        end_date = datetime.datetime.combine(selected_date, datetime.time.max)
    elif time_period == "Year":
        start_date = selected_date - relativedelta(years=1)
        end_date = datetime.datetime.combine(selected_date, datetime.time.max)

    # Fetch data based on user input
    df = fetch_data(start_date=start_date.isoformat(), end_date=end_date.isoformat(), limit=limit)
    if not df.empty:
        df['datetime'] = pd.to_datetime(df['datetime'])

        # Current data summary
        current_data = df.iloc[0]
        current_time = current_data['datetime']
        st.write(f'**Current Readings** at {current_time.strftime("%Y-%m-%d T %H:%M:%S UTC")}')
        col1, col2, col3 = st.columns(3)
        for column, st_col in zip(['temperature', 'pressure', 'humidity'], [col1, col2, col3]):
            show_variable(df, column, st_col)

    else:
        st.write("No data available for the selected period.")

if __name__ == "__main__":
    main()
