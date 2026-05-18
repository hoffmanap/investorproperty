import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration (Must remain the absolute first Streamlit execution line)
st.set_page_config(
    page_title="El Paso Housing Market Dynamics",
    page_icon="🏠",
    layout="wide"
)

# 2. Path Configurations
DATA_DIR = "data"
INVESTOR_PATH = os.path.join(DATA_DIR, "investor_buys.csv")
STR_PATH = os.path.join(DATA_DIR, "active_str_listings.csv")
DISPLACEMENT_PATH = os.path.join(DATA_DIR, "local_displacement_trends.csv")

# 3. Defensive Data Processing Wrapper
def initialize_datasets():
    # Structural column definitions to protect chart components from failing on load
    investor_defaults = pd.DataFrame(columns=['latitude', 'longitude', 'zipCode', 'owner'])
    str_defaults = pd.DataFrame(columns=['id', 'latitude', 'longitude', 'zipcode', 'price', 'snapshot_date'])
    displacement_defaults = pd.DataFrame(columns=['latitude_corporate_buy', 'longitude_corporate_buy', 'zipcode'])
    
    # Core Data Extraction and Parsing Blocks
    if os.path.exists(INVESTOR_PATH):
        try:
            df_i = pd.read_csv(INVESTOR_PATH)
            if not df_i.empty:
                # Force case-insensitive matching standard for ZIP parameters
                zip_col = [c for c in df_i.columns if c.lower() == 'zipcode']
                if zip_col:
                    df_i = df_i.rename(columns={zip_col[0]: 'zipCode'})
                df_i['zipCode'] = df_i['zipCode'].astype(str).str.split('.').str[0]
            else:
                df_i = investor_defaults
        except Exception as e:
            st.sidebar.error(f"Error parsing investor_buys.csv: {e}")
            df_i = investor_defaults
    else:
        df_i = investor_defaults

    if os.path.exists(STR_PATH):
        try:
            df_s = pd.read_csv(STR_PATH)
            if not df_s.empty:
                df_s.columns = df_s.columns.str.lower()
                df_s['zipcode'] = df_s['zipcode'].astype(str).str.split('.').str[0]
                if 'price' in df_s.columns and df_s['price'].dtype == object:
                    df_s['price'] = df_s['price'].astype(str).str.replace('$', '').str.replace(',', '').astype(float)
            else:
                df_s = str_defaults
        except Exception as e:
            st.sidebar.error(f"Error parsing active_str_listings.csv: {e}")
            df_s = str_defaults
    else:
        df_s = str_defaults

    if os.path.exists(DISPLACEMENT_PATH):
        try:
            df_d = pd.read_csv(DISPLACEMENT_PATH)
        except Exception as e:
            st.sidebar.error(f"Error parsing local_displacement_trends.csv: {e}")
            df_d = displacement_defaults
    else:
        df_d = displacement_defaults

    return df_i, df_s, df_d

# Load standardized arrays
df_investor, df_str, df_displacement = initialize_datasets()

# 4. Core UI Header Frame
st.title("🏠 El Paso Housing Market Dynamics Tracker")
st.markdown("""
This platform monitors corporate acquisition footprints and decentralized short-term rental conversions across El Paso, Texas.
""")

# 5. Global Filter Sidebar Construction
st.sidebar.header("📍 Navigation Parameters")
unique_zips = ["All ZIPs"]
if 'zipCode' in df_investor.columns and len(df_investor) > 0:
    unique_zips = ["All ZIPs"] + sorted([z for z in df_investor['zipCode'].unique() if str(z) != 'nan'])

selected_zip = st.sidebar.selectbox("Filter Target Neighborhood Profile:", unique_zips)

# Apply Slicing Modifications
if selected_zip != "All ZIPs":
    df_investor = df_investor[df_investor['zipCode'] == selected_zip]
    if not df_str.empty and 'zipcode' in df_str.columns:
        df_str = df_str[df_str['zipcode'] == selected_zip]

# 6. Safe Tab Execution Wrapper Layout
# Isolating contents using standard conditions blocks completely prevents browser UI stalls
tab_selection = st.radio("Select Analysis Dashboard Perspective:", ["📊 2025 Corporate Ownership Metrics", "🏨 STR 'Scattered Hotel' Allocation Metrics"], horizontal=True)

st.write("---")

if tab_selection == "📊 2025 Corporate Ownership Metrics":
    st.subheader("Corporate Property Acquisitions & Conversion Metrics")
    
    if len(df_investor) == 0:
        st.info("No corporate acquisitions match the requested filtering slice parameters.")
    else:
        total_buys = len(df_investor)
        total_conv = len(df_displacement) if not df_displacement.empty else 0
        conv_rate = (total_conv / total_buys * 100) if total_buys > 0 else 0
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("2025 Corporate Single-Family Buys", f"{total_buys:,} Parcels")
        m_col2.metric("Identified STR Pipeline Matches", f"{total_conv:,} Units")
        m_col3.metric("Observed Market Conversion Pace", f"{conv_rate:.1f}%")
        
        st.write("<br>", unsafe_allow_html=True)
        
        # Spatial Layer Rendering Block
        if 'latitude' in df_investor.columns and 'longitude' in df_investor.columns:
            fig_map = px.scatter_mapbox(
                df_investor,
                lat="latitude",
                lon="longitude",
                zoom=10,
                mapbox_style="carto-positron",
                hover_name="owner" if "owner" in df_investor.columns else None,
                height=500
            )
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.error("Spatial Coordinates (latitude/longitude) mismatch detected inside the input file.")

elif tab_selection == "🏨 STR 'Scattered Hotel' Allocation Metrics":
    st.subheader("Decentralized Hospitality Unit Sizing Analysis")
    
    if len(df_str) == 0:
        st.warning("No active STR components matched your request or data synchronization records are building.")
    else:
        total_str = len(df_str)
        avg_price = df_str['price'].mean() if 'price' in df_str.columns and not df_str['price'].empty else 0.0
        
        s_col1, s_col2 = st.columns(2)
        s_col1.metric("Active Monitored Vacation Rental Units", f"{total_str:,} Properties")
        s_col2.metric("Observed Local Average Daily Rate", f"${avg_price:.2f}" if avg_price > 0 else "Pending Scrapes")
        
        st.write("---")
        
        # Simulation Tool Parameters
        st.subheader("💡 Revenue Capture Metric Matrix Options")
        slider_col, calculation_col = st.columns(2)
        
        with slider_col:
            occ_rate = st.slider("Assumed Occupancy Density Scaling Factor (%):", 10, 100, 60, 5)
            tax_rate = st.slider("Simulated Local Hotel Occupancy Levy (%):", 1.0, 15.0, 7.0, 0.5)
            
        monthly_rev = total_str * avg_price * (occ_rate / 100) * 30.4
        monthly_tax = monthly_rev * (tax_rate / 100)
        
        with calculation_col:
            st.markdown("<br>", unsafe_allow_html=True)
            st.metric("Estimated Volume Generated Cash Flow (Monthly)", f"${monthly_rev:,.2f}")
            st.metric("Projected Capture Potential (HOT Local Pool)", f"${monthly_tax:,.2f}")
