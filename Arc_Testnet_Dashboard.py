import streamlit as st
import requests
import pandas as pd

# ----------------------------------------------------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------------------------------------------------
st.set_page_config(page_title="Arc Testnet Dashboard",page_icon="⚡",layout="wide")

# ----------------------------------------------------------------------------------------------------------------------
# CUSTOM CSS
# ----------------------------------------------------------------------------------------------------------------------
st.markdown("""

<style>

@font-face {
    font-family: 'Britannic';
    src: url('BritannicBold.ttf');
}

div[data-testid="stMetricValue"] {
    font-family: 'Britannic', sans-serif !important;
    font-size: 34px !important;
    font-weight: bold !important;
}

div[data-testid="stMetricLabel"] {
    font-family: 'Britannic', sans-serif !important;
    font-size: 16px !important;
    font-weight: bold !important;
}

h2, h3 {
    padding-top: 15px;
}

</style>

""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------------------------------------------------
st.title("⚡ Arc Testnet Dashboard")
st.info("Real-time statistics from Arc Testnet.")

# ----------------------------------------------------------------------------------------------------------------------
# API
# ----------------------------------------------------------------------------------------------------------------------
API_URL = "https://testnet.arcscan.app/stats-service/api/v1/counters"

# ----------------------------------------------------------------------------------------------------------------------
# FETCH DATA
# ----------------------------------------------------------------------------------------------------------------------
@st.cache_data(ttl=300)
def fetch_stats():
response = requests.get(API_URL, timeout=30)
response.raise_for_status()
return pd.DataFrame(
    response.json().get("counters", [])
)

# ----------------------------------------------------------------------------------------------------------------------
# FORMATTER
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
# KPI HELPER
# ----------------------------------------------------------------------------------------------------------------------
def show_metrics(df, metric_ids, cols_per_row=4):
subset = df[df["id"].isin(metric_ids)]
for i in range(0, len(subset), cols_per_row):
    cols = st.columns(cols_per_row)
    chunk = subset.iloc[i:i+cols_per_row]
    for col, (_, row) in zip(cols, chunk.iterrows()):
        value = format_value(row["value"])
        unit = row["units"]
        if pd.notna(unit) and str(unit).strip():
            value = f"{value} {unit}"
        with col:
            st.metric(
                label=row["title"],
                value=value,
                help=row["description"]
            )
# ----------------------------------------------------------------------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------------------------------------------------------------------
try:
df = fetch_stats()
if df.empty:
    st.warning("No data returned from API.")
    st.stop()
# ------------------------------------------------------------------------------------------------------------------
# NETWORK
# ------------------------------------------------------------------------------------------------------------------
st.subheader("⚡ Network")
show_metrics(df,["averageBlockTime","totalBlocks","newTxns24h","pendingTxns30m"])
st.divider()

# ------------------------------------------------------------------------------------------------------------------
# ACTIVITY
# ------------------------------------------------------------------------------------------------------------------
st.subheader("📈 Activity")
show_metrics(df,["totalTxns","completedTxns","totalAccounts","totalAddresses"])
st.divider()

# ------------------------------------------------------------------------------------------------------------------
# SMART CONTRACTS
# ------------------------------------------------------------------------------------------------------------------

st.subheader("📜 Smart Contracts")
show_metrics(df,["totalContracts","totalVerifiedContracts","lastNewContracts","lastNewVerifiedContracts"])
st.divider()

# ------------------------------------------------------------------------------------------------------------------
# TOKENS
# ------------------------------------------------------------------------------------------------------------------
st.subheader("🪙 Tokens")
show_metrics(df,["totalTokens","totalNativeCoinTransfers"])
st.divider()
# ------------------------------------------------------------------------------------------------------------------
# ACCOUNT ABSTRACTION
# ------------------------------------------------------------------------------------------------------------------
st.subheader("👛 Account Abstraction (ERC-4337)")
show_metrics(df,["totalUserOps","totalAccountAbstractionWallets"])
st.divider()
# ------------------------------------------------------------------------------------------------------------------
# FEES
# ------------------------------------------------------------------------------------------------------------------
st.subheader("💸 Fees")
show_metrics(df,["txnsFee24h","averageTxnFee24h"])
except Exception as e:
st.error(f"Error loading data: {e}")

