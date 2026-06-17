import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Uber Analytics Dashboard",
    page_icon="🚖",
    layout="wide"
)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("uber_analytics_final.csv")
    return df

df = load_data()

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.title("🚖 Uber Analytics Dashboard")
st.markdown("### Business Insights from 100K+ Uber Booking Records")

st.markdown("---")

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

st.sidebar.header("Dashboard Filters")

vehicle_filter = st.sidebar.multiselect(
    "Vehicle Type",
    options=df["Vehicle_Type"].unique(),
    default=df["Vehicle_Type"].unique()
)

status_filter = st.sidebar.multiselect(
    "Booking Status",
    options=df["Booking_Status"].unique(),
    default=df["Booking_Status"].unique()
)

payment_filter = st.sidebar.multiselect(
    "Payment Method",
    options=df["Payment_Method"].unique(),
    default=df["Payment_Method"].unique()
)

weekday_filter = st.sidebar.multiselect(
    "Weekday",
    options=df["Weekday"].unique(),
    default=df["Weekday"].unique()
)

# ---------------------------------------------------
# FILTER DATA
# ---------------------------------------------------

filtered_df = df[
    (df["Vehicle_Type"].isin(vehicle_filter))
    & (df["Booking_Status"].isin(status_filter))
    & (df["Payment_Method"].isin(payment_filter))
    & (df["Weekday"].isin(weekday_filter))
]

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------

total_bookings = len(filtered_df)

total_revenue = filtered_df["Booking_Value"].sum()

avg_booking_value = filtered_df["Booking_Value"].mean()

success_rate = (
    (filtered_df["Booking_Status"] == "Success")
    .mean() * 100
)

cancel_rate = (
    filtered_df["Booking_Status"]
    .str.contains("Canceled", case=False)
    .mean() * 100
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Bookings",
    f"{total_bookings:,}"
)

col2.metric(
    "Revenue",
    f"₹{total_revenue:,.0f}"
)

col3.metric(
    "Avg Booking Value",
    f"₹{avg_booking_value:.0f}"
)

col4.metric(
    "Success Rate",
    f"{success_rate:.1f}%"
)

col5.metric(
    "Cancellation Rate",
    f"{cancel_rate:.1f}%"
)

st.markdown("---")

# ---------------------------------------------------
# REVENUE ANALYSIS
# ---------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("Revenue by Vehicle Type")

    vehicle_rev = (
        filtered_df
        .groupby("Vehicle_Type")["Booking_Value"]
        .sum()
        .reset_index()
        .sort_values("Booking_Value", ascending=False)
    )

    fig = px.bar(
        vehicle_rev,
        x="Vehicle_Type",
        y="Booking_Value",
        color="Vehicle_Type"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    st.subheader("Revenue by Weekday")

    weekday_rev = (
        filtered_df
        .groupby("Weekday")["Booking_Value"]
        .sum()
        .reset_index()
    )

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    weekday_rev["Weekday"] = pd.Categorical(
        weekday_rev["Weekday"],
        categories=weekday_order,
        ordered=True
    )

    weekday_rev = weekday_rev.sort_values("Weekday")

    fig = px.line(
        weekday_rev,
        x="Weekday",
        y="Booking_Value",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# BOOKING STATUS ANALYSIS
# ---------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("Booking Status Distribution")

    status_df = (
        filtered_df["Booking_Status"]
        .value_counts()
        .reset_index()
    )

    status_df.columns = [
        "Booking_Status",
        "Count"
    ]

    fig = px.pie(
        status_df,
        names="Booking_Status",
        values="Count"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    st.subheader("Booking Status Count")

    fig = px.bar(
        status_df,
        x="Booking_Status",
        y="Count",
        color="Booking_Status"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# PEAK HOUR ANALYSIS
# ---------------------------------------------------

st.subheader("Peak Booking Hours")

hourly = (
    filtered_df
    .groupby("Hour")
    .size()
    .reset_index(name="Bookings")
)

fig = px.line(
    hourly,
    x="Hour",
    y="Bookings",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# VEHICLE TYPE ANALYSIS
# ---------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("Vehicle Type Usage")

    vehicle_count = (
        filtered_df["Vehicle_Type"]
        .value_counts()
        .reset_index()
    )

    vehicle_count.columns = [
        "Vehicle_Type",
        "Count"
    ]

    fig = px.bar(
        vehicle_count,
        x="Vehicle_Type",
        y="Count",
        color="Vehicle_Type"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    st.subheader("Average Driver Ratings")

    rating_df = (
        filtered_df
        .groupby("Vehicle_Type")["Driver_Ratings"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        rating_df,
        x="Vehicle_Type",
        y="Driver_Ratings",
        color="Vehicle_Type"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# PAYMENT METHOD ANALYSIS
# ---------------------------------------------------

st.subheader("Payment Method Analysis")

payment_df = (
    filtered_df
    .groupby("Payment_Method")
    .agg(
        Revenue=("Booking_Value", "sum"),
        Bookings=("Booking_ID", "count")
    )
    .reset_index()
)

fig = px.bar(
    payment_df,
    x="Payment_Method",
    y="Revenue",
    color="Payment_Method"
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# PICKUP & DROP LOCATION ANALYSIS
# ---------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("Top 10 Pickup Locations")

    pickup_df = (
        filtered_df["Pickup_Location"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    pickup_df.columns = [
        "Pickup_Location",
        "Count"
    ]

    fig = px.bar(
        pickup_df,
        x="Pickup_Location",
        y="Count"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    st.subheader("Top 10 Drop Locations")

    drop_df = (
        filtered_df["Drop_Location"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    drop_df.columns = [
        "Drop_Location",
        "Count"
    ]

    fig = px.bar(
        drop_df,
        x="Drop_Location",
        y="Count"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# RAW DATA
# ---------------------------------------------------

with st.expander("View Dataset"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown("---")

st.markdown(
    """
    **Project Stack:** Python | Pandas | Plotly | Streamlit | GitHub
    
    Built using 100K+ Uber Booking Records for Business Analytics.
    """
)
