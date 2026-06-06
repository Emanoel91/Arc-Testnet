import streamlit as st
import requests
import pandas as pd

# --------------------------------------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------------------------------------
st.set_page_config(page_title="Arc Testnet Dashboard", page_icon="https://pbs.twimg.com/profile_images/1955238194443849732/sHyVRItm_400x400.jpg", layout="wide")

# --------------------------------------------------------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------------------------------------------------------

st.markdown(
    """
    <style>

    div[data-testid="stMetricValue"] {
        font-size: 34px !important;
        font-weight: bold !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 16px !important;
        font-weight: bold !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# --- Title with Logo ---------------------------------------------------------------------------------------------------
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 15px;">
        <img src="https://pbs.twimg.com/profile_images/1955238194443849732/sHyVRItm_400x400.jpg" alt="Arc Logo" style="width:60px; height:60px;">
        <h1 style="margin: 0;">Arc Testnet Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Builder Info ---------------------------------------------------------------------------------------------------------
st.markdown(
    """
    <div style="margin-top: 20px; margin-bottom: 20px; font-size: 16px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="https://pbs.twimg.com/profile_images/2060406047391559681/sA9zPNKM_400x400.jpg" style="width:25px; height:25px; border-radius: 50%;">
            <span>Built by: <a href="https://x.com/0xeman_raz" target="_blank">Eman Raz</a></span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ===================
# Description
# ===================
st.info("Real-time statistics fetched from Arc Testnet.")

# --------------------------------------------------------------------------------------------------
# API
# --------------------------------------------------------------------------------------------------

API_URL = "https://testnet.arcscan.app/stats-service/api/v1/counters"

# --------------------------------------------------------------------------------------------------
# FETCH DATA
# --------------------------------------------------------------------------------------------------

@st.cache_data(ttl=300)
def fetch_stats():
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    data = response.json()

    return pd.DataFrame(
        data.get("counters", [])
    )

# --------------------------------------------------------------------------------------------------
# FORMAT VALUES
# --------------------------------------------------------------------------------------------------

def format_value(value):
    try:
        value = float(value)

        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"

        if value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"

        if value >= 1_000:
            return f"{value / 1_000:.2f}K"

        if value < 1:
            return f"{value:.4f}"

        if value.is_integer():
            return f"{int(value):,}"

        return f"{value:,.4f}"

    except Exception:
        return str(value)

# --------------------------------------------------------------------------------------------------
# KPI DISPLAY HELPER
# --------------------------------------------------------------------------------------------------

def show_metrics(df, metric_ids, columns_per_row=4):

    subset = df[df["id"].isin(metric_ids)]

    for start in range(0, len(subset), columns_per_row):

        cols = st.columns(columns_per_row)

        chunk = subset.iloc[start:start + columns_per_row]

        for col, (_, row) in zip(cols, chunk.iterrows()):

            value = format_value(row["value"])

            unit = row["units"]

            if pd.notna(unit) and str(unit).strip() != "":
                value = f"{value} {unit}"

            with col:
                st.metric(
                    label=row["title"],
                    value=value,
                    help=row["description"]
                )

# --------------------------------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------------------------------

try:

    df = fetch_stats()

    if df.empty:
        st.warning("No data returned from API.")
        st.stop()

    # ----------------------------------------------------------------------------------------------
    # NETWORK
    # ----------------------------------------------------------------------------------------------

    st.subheader("⛓ Network")

    show_metrics(
        df,
        [
            "averageBlockTime",
            "totalBlocks",
            "newTxns24h",
            "pendingTxns30m"
        ]
    )

    st.divider()

    # ----------------------------------------------------------------------------------------------
    # ACTIVITY
    # ----------------------------------------------------------------------------------------------

    st.subheader("📈 Activity")

    show_metrics(
        df,
        [
            "totalTxns",
            "completedTxns",
            "totalAccounts",
            "totalAddresses"
        ]
    )

    st.divider()

    # ----------------------------------------------------------------------------------------------
    # SMART CONTRACTS
    # ----------------------------------------------------------------------------------------------

    st.subheader("📑 Smart Contracts")

    show_metrics(
        df,
        [
            "totalContracts",
            "totalVerifiedContracts",
            "lastNewContracts",
            "lastNewVerifiedContracts"
        ]
    )

    st.divider()

    # ----------------------------------------------------------------------------------------------
    # TOKENS
    # ----------------------------------------------------------------------------------------------

    st.subheader("💎 Tokens")

    show_metrics(
        df,
        [
            "totalTokens",
            "totalNativeCoinTransfers"
        ]
    )

    st.divider()

    # ----------------------------------------------------------------------------------------------
    # ACCOUNT ABSTRACTION
    # ----------------------------------------------------------------------------------------------

    st.subheader("💼 Account Abstraction")

    show_metrics(
        df,
        [
            "totalUserOps",
            "totalAccountAbstractionWallets"
        ]
    )

    st.divider()

    # ----------------------------------------------------------------------------------------------
    # FEES
    # ----------------------------------------------------------------------------------------------

    st.subheader("⛽ Fees")

    show_metrics(
        df,
        [
            "txnsFee24h",
            "averageTxnFee24h"
        ]
    )

except Exception as e:
    st.error(f"Error loading data: {e}")
