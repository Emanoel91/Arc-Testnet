import streamlit as st
import requests
import pandas as pd

# ----------------------------------------------------------------------------------------------------------------------
# Page Config
# ----------------------------------------------------------------------------------------------------------------------

st.set_page_config(
    page_title="Arc Testnet Dashboard",
    page_icon="⚡",
    layout="wide"
)

# ----------------------------------------------------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------------------------------------------------

st.title("⚡ Arc Testnet Dashboard")

st.markdown(
    """
    Real-time network statistics for Arc Testnet
    """
)

st.info(
    "Dashboard data is fetched directly from Arc Testnet Stats API. "
    "If values appear outdated, use 'Clear Cache' and rerun."
)

# ----------------------------------------------------------------------------------------------------------------------
# API
# ----------------------------------------------------------------------------------------------------------------------

API_URL = "https://testnet.arcscan.app/stats-service/api/v1/counters"

# ----------------------------------------------------------------------------------------------------------------------
# Fetch Data
# ----------------------------------------------------------------------------------------------------------------------

@st.cache_data(ttl=300)
def fetch_stats():
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    data = response.json()

    counters = data.get("counters", [])

    return pd.DataFrame(counters)

# ----------------------------------------------------------------------------------------------------------------------
# Formatting
# ----------------------------------------------------------------------------------------------------------------------

def format_value(value):

    try:
        value = float(value)

        if value >= 1_000_000_000:
            return f"{value/1_000_000_000:.2f}B"

        if value >= 1_000_000:
            return f"{value/1_000_000:.2f}M"

        if value >= 1_000:
            return f"{value/1_000:.2f}K"

        if value < 1:
            return f"{value:.4f}"

        if value.is_integer():
            return f"{int(value):,}"

        return f"{value:,.4f}"

    except:
        return str(value)

# ----------------------------------------------------------------------------------------------------------------------
# Load Data
# ----------------------------------------------------------------------------------------------------------------------

try:

    df = fetch_stats()

    if df.empty:
        st.warning("No data returned from API.")
        st.stop()

    # ------------------------------------------------------------------------------------------------------------------
    # KPI Cards
    # ------------------------------------------------------------------------------------------------------------------

    st.subheader("📊 Network Statistics")

    cols_per_row = 4

    for i in range(0, len(df), cols_per_row):

        cols = st.columns(cols_per_row)

        chunk = df.iloc[i:i + cols_per_row]

        for col, (_, row) in zip(cols, chunk.iterrows()):

            value = format_value(row["value"])

            if row["units"]:
                value = f"{value} {row['units']}"

            with col:
                st.metric(
                    label=row["title"],
                    value=value,
                    help=row["description"]
                )

    # ------------------------------------------------------------------------------------------------------------------
    # Detailed Table
    # ------------------------------------------------------------------------------------------------------------------

    st.divider()

    st.subheader("📋 Raw Metrics")

    table_df = df[[ 
        "id",
        "title",
        "value",
        "units",
        "description"
    ]].copy()

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.error(f"Error loading data: {e}")
