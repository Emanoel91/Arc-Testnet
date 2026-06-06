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
# APIs
# --------------------------------------------------------------------------------------------------

COUNTERS_API = "https://testnet.arcscan.app/stats-service/api/v1/counters"
CONTRACTS_API = "https://testnet.arcscan.app/stats-service/api/v1/pages/contracts"

# --------------------------------------------------------------------------------------------------
# FETCH DATA
# --------------------------------------------------------------------------------------------------

@st.cache_data(ttl=300)
def fetch_counters():
    r = requests.get(COUNTERS_API, timeout=30)
    r.raise_for_status()
    return pd.DataFrame(r.json().get("counters", []))


@st.cache_data(ttl=300)
def fetch_contract_page():
    r = requests.get(CONTRACTS_API, timeout=30)
    r.raise_for_status()
    data = r.json()

    # flatten dict response into dataframe
    rows = []
    for k, v in data.items():
        rows.append(v)

    return pd.DataFrame(rows)

# --------------------------------------------------------------------------------------------------
# FORMATTER
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

    except:
        return str(value)

# --------------------------------------------------------------------------------------------------
# KPI RENDER FUNCTION
# --------------------------------------------------------------------------------------------------

def show_metrics(df, ids, cols=4):

    df = df[df["id"].isin(ids)]

    for i in range(0, len(df), cols):

        cols_ui = st.columns(cols)

        chunk = df.iloc[i:i + cols]

        for col, (_, row) in zip(cols_ui, chunk.iterrows()):

            value = format_value(row["value"])

            unit = row.get("units")

            if pd.notna(unit) and str(unit).strip() != "":
                value = f"{value} {unit}"

            with col:
                st.metric(
                    label=row["title"],
                    value=value,
                    help=row["description"]
                )

# --------------------------------------------------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------------------------------------------------

try:

    counters_df = fetch_counters()
    contracts_df = fetch_contract_page()

    if counters_df.empty:
        st.warning("No counters data found.")
        st.stop()

    if contracts_df.empty:
        st.warning("No contracts page data found.")
        st.stop()

    # --------------------------------------------------------------------------------------------------
    # NETWORK
    # --------------------------------------------------------------------------------------------------

    st.subheader("⛓ Network")

    show_metrics(
        counters_df,
        [
            "averageBlockTime",
            "totalBlocks",
            "newTxns24h",
            "pendingTxns30m"
        ]
    )

    st.divider()

    # --------------------------------------------------------------------------------------------------
    # ACTIVITY
    # --------------------------------------------------------------------------------------------------

    st.subheader("📈 Activity")

    show_metrics(
        counters_df,
        [
            "totalTxns",
            "completedTxns",
            "totalAccounts",
            "totalAddresses"
        ]
    )

    st.divider()

    # --------------------------------------------------------------------------------------------------
    # SMART CONTRACTS (MERGED API)
    # --------------------------------------------------------------------------------------------------

    st.subheader("📑 Smart Contracts")

    show_metrics(
        counters_df,
        [
            "totalContracts",
            "totalVerifiedContracts",
            "lastNewContracts",
            "lastNewVerifiedContracts"
        ]
    )

    show_metrics(
        contracts_df,
        [
            "totalContracts",
            "newContracts24h",
            "totalVerifiedContracts",
            "newVerifiedContracts24h"
        ]
    )

    st.divider()

    # --------------------------------------------------------------------------------------------------
    # TOKENS
    # --------------------------------------------------------------------------------------------------

    st.subheader("💎 Tokens")

    show_metrics(
        counters_df,
        [
            "totalTokens",
            "totalNativeCoinTransfers"
        ]
    )

    st.divider()

    # --------------------------------------------------------------------------------------------------
    # ACCOUNT ABSTRACTION
    # --------------------------------------------------------------------------------------------------

    st.subheader("💼 Account Abstraction")

    show_metrics(
        counters_df,
        [
            "totalUserOps",
            "totalAccountAbstractionWallets"
        ]
    )

    st.divider()

    # --------------------------------------------------------------------------------------------------
    # FEES
    # --------------------------------------------------------------------------------------------------

    st.subheader("⛽ Fees")

    show_metrics(
        counters_df,
        [
            "txnsFee24h",
            "averageTxnFee24h"
        ]
    )

except Exception as e:
    st.error(f"Error loading data: {e}")
