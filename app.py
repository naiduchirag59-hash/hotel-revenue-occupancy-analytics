import io
import urllib.request
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Hotel Revenue & Occupancy Analytics", page_icon="🏨", layout="wide")
st.title("🏨 Hotel Revenue & Occupancy Analytics")
st.caption("CA4 Capstone · Project 37 · Business Analytics")

DATA_URL = "https://raw.githubusercontent.com/aaqibqadeer/Hotel-booking-demand/master/hotel_bookings.csv"
LOCAL_FILE = Path("data/hotel_bookings.csv")

@st.cache_data(show_spinner="Loading the public hotel booking dataset…")
def load_data():
    if LOCAL_FILE.exists():
        df = pd.read_csv(LOCAL_FILE)
    else:
        with urllib.request.urlopen(DATA_URL, timeout=45) as response:
            df = pd.read_csv(io.BytesIO(response.read()))
    # Clean column labels and normalize common missing-value encodings.
    df.columns = [c.strip() for c in df.columns]
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].replace(["", " "], pd.NA)
    # The source data encodes children as missing for a small number of rows.
    if "children" in df.columns:
        df["children"] = pd.to_numeric(df["children"], errors="coerce").fillna(0)
    for col in ["adults", "babies", "lead_time", "adr", "stays_in_weekend_nights",
                "stays_in_week_nights", "is_canceled", "arrival_date_year"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["arrival_date_month"] = pd.Categorical(
        df["arrival_date_month"],
        categories=["January","February","March","April","May","June","July","August",
                    "September","October","November","December"], ordered=True
    )
    df["total_nights"] = df["stays_in_weekend_nights"].fillna(0) + df["stays_in_week_nights"].fillna(0)
    df["guest_count"] = df[["adults", "children", "babies"]].fillna(0).sum(axis=1)
    # ADR is the dataset's average daily rate. Revenue below is a proxy, not audited accounting revenue.
    df["estimated_room_value"] = df["adr"].clip(lower=0) * df["total_nights"]
    df["booking_status"] = df["is_canceled"].map({0: "Not canceled", 1: "Canceled"}).fillna("Unknown")
    return df

try:
    raw = load_data()
except Exception as exc:
    st.error("The dataset could not be downloaded. Check your internet connection or place hotel_bookings.csv in data/.")
    st.exception(exc)
    st.stop()

st.sidebar.header("Dashboard filters")
hotels = sorted(raw["hotel"].dropna().unique().tolist())
selected_hotels = st.sidebar.multiselect("Hotel type", hotels, default=hotels)
years = sorted(raw["arrival_date_year"].dropna().astype(int).unique().tolist())
selected_years = st.sidebar.multiselect("Arrival year", years, default=years)
segments = sorted(raw["market_segment"].dropna().astype(str).unique().tolist())
selected_segments = st.sidebar.multiselect("Market segment", segments, default=segments)
statuses = st.sidebar.multiselect("Booking status", ["Not canceled", "Canceled"], default=["Not canceled", "Canceled"])

df = raw[
    raw["hotel"].isin(selected_hotels)
    & raw["arrival_date_year"].isin(selected_years)
    & raw["market_segment"].astype(str).isin(selected_segments)
    & raw["booking_status"].isin(statuses)
].copy()

if df.empty:
    st.warning("No records match these filters. Change the selections in the sidebar.")
    st.stop()

total_bookings = len(df)
cancel_rate = df["is_canceled"].mean() * 100
noncancel = df[df["is_canceled"] == 0]
avg_adr = noncancel["adr"].mean() if not noncancel.empty else 0
estimated_value = noncancel["estimated_room_value"].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Bookings in selection", f"{total_bookings:,}")
c2.metric("Cancellation rate", f"{cancel_rate:.1f}%")
c3.metric("Average ADR · non-canceled", f"{avg_adr:,.2f}")
c4.metric("Room-value proxy · non-canceled", f"{estimated_value:,.0f}")

st.info("Interpretation note: this dataset contains booking-level records, not each hotel's total room inventory. It supports booking-demand and cancellation analysis, but a true occupancy percentage cannot be calculated. ADR × nights is shown only as an estimated room-value proxy, not verified revenue.")

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Revenue & rates", "Cancellations", "Customer & channel mix"])

with tab1:
    left, right = st.columns(2)
    with left:
        monthly = df.groupby("arrival_date_month", observed=False).size().reset_index(name="Bookings")
        st.plotly_chart(px.bar(monthly, x="arrival_date_month", y="Bookings", title="Bookings by arrival month",
                               labels={"arrival_date_month":"Arrival month"}), use_container_width=True)
    with right:
        hotel_mix = df.groupby("hotel", dropna=False).size().reset_index(name="Bookings")
        st.plotly_chart(px.pie(hotel_mix, names="hotel", values="Bookings", title="Booking mix by hotel type"),
                        use_container_width=True)
    yearly = df.groupby(["arrival_date_year", "hotel"], dropna=False).size().reset_index(name="Bookings")
    st.plotly_chart(px.line(yearly, x="arrival_date_year", y="Bookings", color="hotel", markers=True,
                            title="Bookings by arrival year", labels={"arrival_date_year":"Arrival year"}),
                    use_container_width=True)

with tab2:
    completed = df[df["is_canceled"] == 0].copy()
    left, right = st.columns(2)
    with left:
        adr = completed.groupby(["arrival_date_month", "hotel"], observed=False)["adr"].mean().reset_index()
        st.plotly_chart(px.line(adr, x="arrival_date_month", y="adr", color="hotel", markers=True,
                                title="Average daily rate by arrival month (non-canceled bookings)",
                                labels={"arrival_date_month":"Arrival month","adr":"ADR"}), use_container_width=True)
    with right:
        value = completed.groupby("hotel", dropna=False)["estimated_room_value"].sum().reset_index()
        st.plotly_chart(px.bar(value, x="hotel", y="estimated_room_value",
                               title="Estimated room-value proxy by hotel type",
                               labels={"hotel":"Hotel type","estimated_room_value":"ADR × nights proxy"}),
                        use_container_width=True)
    st.plotly_chart(px.box(completed, x="hotel", y="adr", color="hotel",
                           title="ADR distribution by hotel type (non-canceled bookings)", points=False),
                    use_container_width=True)

with tab3:
    cancel_by_hotel = df.groupby("hotel", dropna=False)["is_canceled"].mean().mul(100).reset_index(name="Cancellation rate (%)")
    cancel_by_segment = df.groupby("market_segment", dropna=False)["is_canceled"].mean().mul(100).reset_index(name="Cancellation rate (%)")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.bar(cancel_by_hotel, x="hotel", y="Cancellation rate (%)",
                               title="Cancellation rate by hotel type"), use_container_width=True)
    with right:
        st.plotly_chart(px.bar(cancel_by_segment.sort_values("Cancellation rate (%)", ascending=False),
                               x="market_segment", y="Cancellation rate (%)",
                               title="Cancellation rate by market segment"), use_container_width=True)
    lead = df.groupby("booking_status")["lead_time"].median().reset_index(name="Median lead time (days)")
    st.plotly_chart(px.bar(lead, x="booking_status", y="Median lead time (days)",
                           title="Median booking lead time by cancellation status"), use_container_width=True)

with tab4:
    left, right = st.columns(2)
    with left:
        channel = df.groupby("distribution_channel", dropna=False).size().reset_index(name="Bookings").sort_values("Bookings", ascending=False)
        st.plotly_chart(px.bar(channel, x="distribution_channel", y="Bookings",
                               title="Bookings by distribution channel"), use_container_width=True)
    with right:
        segment = df.groupby("market_segment", dropna=False).size().reset_index(name="Bookings").sort_values("Bookings", ascending=False)
        st.plotly_chart(px.bar(segment, x="market_segment", y="Bookings",
                               title="Bookings by market segment"), use_container_width=True)
    cust = df.groupby("customer_type", dropna=False).size().reset_index(name="Bookings").sort_values("Bookings", ascending=False)
    st.plotly_chart(px.bar(cust, x="customer_type", y="Bookings", title="Bookings by customer type"), use_container_width=True)

st.subheader("Filtered data preview")
st.dataframe(df.head(100), use_container_width=True)
st.download_button("Download filtered records as CSV", data=df.to_csv(index=False).encode("utf-8"),
                   file_name="filtered_hotel_bookings.csv", mime="text/csv")

with st.expander("Dataset and method notes"):
    st.markdown("""
    - Source dataset: Hotel Booking Demand, described by Antonio, de Almeida and Nunes (2019).
    - Unit of observation: one hotel booking; includes canceled and non-canceled reservations.
    - Missing `children` values are set to zero for the calculated guest count; this assumption should be checked and documented in the report.
    - Negative ADR values are excluded from the estimated room-value proxy by clipping them to zero; the raw ADR field is otherwise retained.
    - The dataset covers a limited historical period and two hotel types. Results should not be presented as current hotel-market performance.
    - Occupancy requires rooms available (inventory) and rooms actually occupied by date. Those fields are not present in this booking-level dataset.
    """)
