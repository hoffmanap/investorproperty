import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(
    page_title="El Paso Housing Market Dynamics",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Path Configurations
DATA_DIR = "data"
INVESTOR_PATH = os.path.join(DATA_DIR, "investor_buys.csv")
STR_PATH = os.path.join(DATA_DIR, "active_str_listings.csv")
DISPLACEMENT_PATH = os.path.join(DATA_DIR, "local_displacement_trends.csv")

# 3. Helper Function to Load Data Safely
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            st.error(f"Error loading {os.path.basename(file_path)}: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# Load datasets
df_investor = load_data(INVESTOR_PATH)
df_str = load_data(STR_PATH)
df_displacement = load_data(DISPLACEMENT_PATH)

# App Header Layout
st.title("🏠 El Paso Housing Market Dynamics Tracker")
st.markdown("""
This dashboard monitors the intersection of institutional/corporate property acquisitions and the short-term rental (STR) ecosystem across El Paso, Texas. 
By tracking these metrics, policymakers and housing advocates can evaluate how single-family housing stock shifts away from traditional residential uses.
""")
st.write("---")

# 4. Sidebar Controls & Global Filters
st.sidebar.header("📍 Global Dashboard Filters")

# Fallback safely if datasets are still generating from the workflow
available_zips = ["All ZIPs"]
if not df_investor.empty and 'zipCode' in df_investor.columns:
    # Ensure zip code values are handled clean as strings
    df_investor['zipCode'] = df_investor['zipCode'].astype(str).str.split('.').str[0]
    available_zips = ["All ZIPs"] + sorted(df_investor['zipCode'].unique().tolist())
elif not df_str.empty and 'zipcode' in df_str.columns:
    df_str['zipcode'] = df_str['zipcode'].astype(str).str.split('.').str[0]
    available_zips = ["All ZIPs"] + sorted(df_str['zipcode'].unique().tolist())

selected_zip = st.sidebar.selectbox("Filter Metrics by ZIP Code:", available_zips)

# Filter DataFrames based on sidebar selection
if selected_zip != "All ZIPs":
    if not df_investor.empty and 'zipCode' in df_investor.columns:
        df_investor = df_investor[df_investor['zipCode'] == selected_zip]
    if not df_str.empty and 'zipcode' in df_str.columns:
        df_str = df_str[df_str['zipcode'] == selected_zip]
    if not df_displacement.empty:
        # Check both naming conventions if present after the join merge
        zip_col = 'zipCode_corporate_buy' if 'zipCode_corporate_buy' in df_displacement.columns else 'zipcode'
        if zip_col in df_displacement.columns:
            df_displacement['zipCode_corporate_buy'] = df_displacement[zip_col].astype(str).str.split('.').str[0]
            df_displacement = df_displacement[df_displacement['zipCode_corporate_buy'] == selected_zip]

# 5. Core Navigation Structure Tabs
tab1, tab2 = st.tabs(["📊 2025 Corporate Acquisitions", "🏨 STR 'Scattered Hotel' Simulator"])

# ==========================================
# TAB 1: CORPORATE ACQUISITIONS & CONVERSIONS
# ==========================================
with tab1:
    st.header("Corporate Buying Trends & Pipeline Conversions")
    
    if df_investor.empty:
        st.warning("⚠️ Baseline file `investor_buys.csv` not found or empty. Please run your automated automation workflow to populate datasets.")
    else:
        # Compute Top-Level KPIs
        total_corporate_buys = len(df_investor)
        total_conversions = len(df_displacement) if not df_displacement.empty else 0
        conversion_rate = (total_conversions / total_corporate_buys * 100) if total_corporate_buys > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("2025 Corporate Purchases", f"{total_corporate_buys:,} Properties")
        col2.metric("Active STR Pipeline Conversions", f"{total_conversions:,} Units")
        col3.metric("Conversion Pipeline Rate", f"{conversion_rate:.1f}%")
        
        st.write("---")
        
        # Geospatial Map Display
        st.subheader("Geospatial Distribution of Corporate Ownership")
        
        # Build dynamic color mapping conditions for Map visualization
        # Properties that match our conversion pipeline display as Red, else standard Blue
        if 'latitude' in df_investor.columns and 'longitude' in df_investor.columns:
            map_df = df_investor.copy()
            map_df['Status'] = 'Traditional Housing / Long-Term Asset'
            
            if not df_displacement.empty and 'latitude_corporate_buy' in df_displacement.columns:
                converted_coords = set(zip(df_displacement['latitude_corporate_buy'].round(4), df_displacement['longitude_corporate_buy'].round(4)))
                map_df['coord_key'] = list(zip(map_df['latitude'].round(4), map_df['longitude'].round(4)))
                map_df.loc[map_df['coord_key'].isin(converted_coords), 'Status'] = '🚨 Converted to Short-Term Rental'
            
            fig_map = px.scatter_mapbox(
                map_df,
                lat="latitude",
                lon="longitude",
                color="Status",
                color_discrete_map={'Traditional Housing / Long-Term Asset': '#1f77b4', '🚨 Converted to Short-Term Rental': '#d62728'},
                zoom=10,
                mapbox_style="carto-positron",
                hover_name="owner" if "owner" in map_df.columns else None,
                height=550
            )
            fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("Ensure latitude and longitude columns exist to render map points.")

# ==========================================
# TAB 2: STR HOTEL EQUIVALENT & REVENUE SIMULATOR
# ==========================================
with tab2:
    st.header("The Decentralized 'Scattered-Site Hotel' Ecosystem")
    
    if df_str.empty:
        st.info("ℹ️ Active short-term rental snapshots will appear here once the weekly automation script is executed via GitHub Actions.")
    else:
        # Metric Calculations
        total_active_str = len(df_str)
        
        # Clean up pricing metrics safely handling currency strings if parsed poorly
        if 'price' in df_str.columns:
            if df_str['price'].dtype == object:
                df_str['price'] = df_str['price'].astype(str).str.replace('$', '').str.replace(',', '').astype(float)
            avg_adr = df_str['price'].mean()
        else:
            avg_adr = 150.0 # Standard local baseline estimation fallback
            
        col1_str, col2_str, col3_str = st.columns(3)
        col1_str.metric("Total Decentralized Rooms", f"{total_active_str:,} Units")
        col2_str.metric("Average Observed Daily Rate (ADR)", f"${avg_adr:.2f}")
        
        # 6. Interactive Local Policy Policy Simulator Widget
        st.write("---")
        st.subheader("💡 Municipal Policy & Tax Generation Simulator")
        st.markdown("Adjust parameters to simulate local Hotel Occupancy Tax (HOT) capturing capabilities from the decentralized market.")
        
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            est_occupancy = st.slider("Estimated Average Monthly Occupancy Rate (%):", min_value=10, max_value=100, value=60, step=5)
            local_tax_rate = st.slider("Target Hotel Occupancy Tax (HOT) Rate (%):", min_value=1.0, max_value=15.0, value=7.0, step=0.5)
            
        # Math calculation equations
        days_in_month = 30.4
        total_monthly_revenue = total_active_str * avg_adr * (est_occupancy / 100) * days_in_month
        simulated_tax_collected = total_monthly_revenue * (local_tax_rate / 100)
        
        with sim_col2:
            st.markdown("<br>", unsafe_allow_html=True) # Structural spacing buffer
            st.metric("Estimated Total Monthly Market Revenue", f"${total_monthly_revenue:,.2f}")
            col2_str.metric("Projected Monthly Tax Capture", f"${simulated_tax_collected:,.2f}")
            
        st.write("---")
        
        # Secondary Volumetric Visual Charting Slices
        if 'zipcode' in df_str.columns:
            st.subheader("STR Multi-Unit Spatial Density by Location")
            zip_counts = df_str['zipcode'].value_counts().reset_index()
            zip_counts.columns = ['ZIP Code', 'Active Listings']
            
            fig_bar = px.bar(
                zip_counts,
                x='ZIP Code',
                y='Active Listings',
                text_auto=True,
                color='Active Listings',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_bar, use_container_width=True)

# Footer Info
st.caption("Data sources: El Paso Corporate Transactions Baseline (2025 Calendar Snapshot) | Live Snapshots provided dynamically via RentCast API integrations.")
