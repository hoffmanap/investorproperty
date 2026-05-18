import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration (Keep at the absolute top)
st.set_page_config(
    page_title="El Paso Housing Market Dynamics",
    page_icon="🏠",
    layout="wide"
)

# 2. Path Settings
DATA_DIR = "data"
INVESTOR_PATH = os.path.join(DATA_DIR, "investor_buys.csv")
STR_PATH = os.path.join(DATA_DIR, "active_str_listings.csv")
DISPLACEMENT_PATH = os.path.join(DATA_DIR, "local_displacement_trends.csv")

# 3. Simple, Non-Destructive Data Loader
def load_flat_csv(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
        # Drop rows where coordinates are fully missing to prevent map engine freezes
        if 'latitude' in df.columns and 'longitude' in df.columns:
            df = df.dropna(subset=['latitude', 'longitude'])
        return df
    except Exception as e:
        return pd.DataFrame()

# Load arrays plainly without active regex or column modifications on boot
df_investor = load_flat_csv(INVESTOR_PATH)
df_str = load_flat_csv(STR_PATH)
df_displacement = load_flat_csv(DISPLACEMENT_PATH)

# Header Structure
st.title("🏠 El Paso Housing Market Dynamics Tracker")
st.markdown("Monitoring corporate acquisitions and short-term rental market metrics across El Paso, Texas.")
st.write("---")

# 4. Global Structural Validation
if df_investor.empty:
    st.error("🚨 Configuration Warning: Could not read 'data/investor_buys.csv'. Verify your repository paths.")
    st.stop()

# 5. Core Interface Split via Left Navigation Sidebar
analysis_view = st.sidebar.radio(
    "Select Dashboard Perspective:",
    ["📊 2025 Corporate Ownership", "🏨 STR 'Scattered Hotel' Analysis"]
)

# ==========================================
# VIEW 1: CORPORATE OWNERSHIP METRICS
# ==========================================
if analysis_view == "📊 2025 Corporate Ownership":
    st.subheader("Corporate Acquisitions & Conversion Pipelines")
    
    # Compute Safe Counts
    total_buys = len(df_investor)
    total_conv = len(df_displacement)
    conv_rate = (total_conv / total_buys * 100) if total_buys > 0 else 0.0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("2025 Corporate Purchases", f"{total_buys:,} Properties")
    col2.metric("STR Conversion Matches", f"{total_conv:,} Units")
    col3.metric("Observed Conversion Pace", f"{conv_rate:.1f}%")
    
    st.write("---")
    
    # Render Map Layout
    st.subheader("Geospatial Distribution of Corporate Assets")
    fig_map = px.scatter_mapbox(
        df_investor,
        lat="latitude",
        lon="longitude",
        zoom=10,
        mapbox_style="carto-positron",
        height=500
    )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

# ==========================================
# VIEW 2: STR SCATTERED HOTEL SIMULATOR
# ==========================================
elif analysis_view == "🏨 STR 'Scattered Hotel' Analysis":
    st.subheader("Decentralized Hospitality Unit Sizing Analysis")
    
    if df_str.empty:
        st.info("ℹ️ RentCast STR tracking data layers are preparing to synchronize.")
    else:
        total_str = len(df_str)
        
        # Calculate pricing baseline safely
        avg_adr = 150.0  # Safe regional estimation fallback
        if 'price' in df_str.columns:
            # Drop string characters only if row objects are verified string instances
            try:
                sample_prices = df_str['price'].dropna()
                if not sample_prices.empty and isinstance(sample_prices.iloc[0], str):
                    df_str['price'] = df_str['price'].astype(str).str.replace('$', '').str.replace(',', '').astype(float)
                avg_adr = df_str['price'].mean()
            except:
                pass
                
        s1, s2 = st.columns(2)
        s1.metric("Active Monitored Vacation Rentals", f"{total_str:,} Units")
        s2.metric("Observed Market Average Daily Rate", f"${avg_adr:.2f}")
        
        st.write("---")
        
        # Policy Fee Simulator Frame
        st.subheader("💡 Municipal Fee & Tax Capture Simulator")
        slider_col, calculation_col = st.columns(2)
        
        with slider_col:
            occ_rate = st.slider("Assumed Occupancy Density Factor (%):", 10, 100, 60, 5)
            tax_rate = st.slider("Simulated Hotel Occupancy Tax (HOT) Rate (%):", 1.0, 15.0, 7.0, 0.5)
            
        monthly_rev = total_str * avg_adr * (occ_rate / 100) * 30.4
        monthly_tax = monthly_rev * (tax_rate / 100)
        
        with calculation_col:
            st.markdown("<br>", unsafe_allow_html=True)
            st.metric("Estimated Total Monthly Market Revenue", f"${monthly_rev:,.2f}")
            st.metric("Projected Monthly Tax Capture Potential", f"${monthly_tax:,.2f}")