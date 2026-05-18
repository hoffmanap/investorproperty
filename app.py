import streamlit as st
import pandas as pd
import os

# 1. Clear Page Config (Keep this at the very top)
st.set_page_config(
    page_title="El Paso Housing Market Dynamics",
    page_icon="🏠",
    layout="wide"
)

# 2. Robust Data Loader with Built-in Fallbacks
def load_data_safely(file_path, default_cols):
    if not os.path.exists(file_path):
        # Instead of hanging, return an empty dataframe with structural columns
        st.sidebar.warning(f"⚠️ {os.path.basename(file_path)} not found yet.")
        return pd.DataFrame(columns=default_cols)
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            return pd.DataFrame(columns=default_cols)
        return df
    except Exception as e:
        st.sidebar.error(f"Error reading {os.path.basename(file_path)}: {e}")
        return pd.DataFrame(columns=default_cols)

# Define strict fallback columns based on expected pipeline schemas
INVESTOR_COLS = ['latitude', 'longitude', 'zipCode', 'owner']
STR_COLS = ['id', 'latitude', 'longitude', 'zipcode', 'price', 'snapshot_date']
DISPLACEMENT_COLS = ['latitude_corporate_buy', 'longitude_corporate_buy', 'zipcode']

# Execute the clean loads
df_investor = load_data_safely("data/investor_buys.csv", INVESTOR_COLS)
df_str = load_data_safely("data/active_str_listings.csv", STR_COLS)
df_displacement = load_data_safely("data/local_displacement_trends.csv", DISPLACEMENT_COLS)

# Quick UI Check to instantly reveal if datasets are completely empty strings
if df_investor.empty and df_str.empty:
    st.error("🚨 Critical Data Missing: Both dataframes initialized empty. Check your GitHub repo data folder!")
    st.stop() # Prevents downstream plotting engines from stalling out completely
