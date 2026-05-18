import os
import requests
import pandas as pd
from datetime import datetime

# 1. Configuration & Security Setup
API_KEY = os.getenv("RENTCAST_API_KEY")
BASE_URL = "https://api.rentcast.io/v1/listings/rental/long-term"

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
STR_OUTPUT_PATH = os.path.join(DATA_DIR, "active_str_listings.csv")
MERGED_OUTPUT_PATH = os.path.join(DATA_DIR, "local_displacement_trends.csv")
INVESTOR_DATA_PATH = os.path.join(DATA_DIR, "investor_buys.csv")

def fetch_el_paso_str_data():
    """Fetches active rental market payloads for El Paso using pagination"""
    print("Initiating RentCast STR Data Pull for El Paso...")
    headers = {"X-Api-Key": API_KEY, "accept": "application/json"}
    all_listings = []
    
    for offset in [0, 500]:
        params = {
            "city": "El Paso",
            "state": "TX",
            "status": "Active",
            "limit": 500,
            "offset": offset
        }
        
        try:
            response = requests.get(BASE_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
                
            all_listings.extend(data)
            print(f"Successfully retrieved batch starting at offset {offset} ({len(data)} records).")
            
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with RentCast API: {e}")
            break
            
    return pd.DataFrame(all_listings)

def main():
    if not API_KEY:
        print("CRITICAL: RENTCAST_API_KEY secret is not configured. Exiting script.")
        return

    # Fetch fresh STR snapshot
    new_str_df = fetch_el_paso_str_data()
    
    if new_str_df.empty:
        print("No listing data returned. Pipeline aborted.")
        return
        
    # Add a snapshot timestamp so you can track *when* this data was observed historically
    new_str_df['snapshot_date'] = datetime.now().strftime('%Y-%m-%d')

    # --- APPEND LOGIC FOR STR DATA ---
    if os.path.exists(STR_OUTPUT_PATH):
        print(f"Existing dataset found at {STR_OUTPUT_PATH}. Appending new snapshots...")
        existing_str_df = pd.read_csv(STR_OUTPUT_PATH)
        
        # Combine existing records with the new snapshot
        combined_str_df = pd.concat([existing_str_df, new_str_df], ignore_index=True)
        
        # Deduplicate to ensure you don't accidental log identical properties twice on the SAME day
        # (Allows the same property to exist across different weekly snapshot_dates)
        if 'id' in combined_str_df.columns:
            combined_str_df.drop_duplicates(subset=['id', 'snapshot_date'], keep='last', inplace=True)
        else:
            combined_str_df.drop_duplicates(subset=['id', 'latitude', 'longitude', 'snapshot_date'], keep='last', inplace=True)
    else:
        print(f"No existing dataset found. Creating a new repository baseline at {STR_OUTPUT_PATH}")
        combined_str_df = new_str_df

    # Save the cumulative data back down
    combined_str_df.to_csv(STR_OUTPUT_PATH, index=False)
    print(f"Total historical STR database size is now at {len(combined_str_df)} logged entries.")

    # --- DATA INTEGRATION BLOCK ---
    if os.path.exists(INVESTOR_DATA_PATH):
        print("Alternate investor file found. Running geospatial cross-match pipeline...")
        investor_df = pd.read_csv(INVESTOR_DATA_PATH)
        
        if 'latitude' in investor_df.columns and 'latitude' in combined_str_df.columns:
            # Round coordinates to 4 decimal places (~11 meters) to align spatial datasets
            investor_df['lat_match'] = investor_df['latitude'].round(4)
            investor_df['lon_match'] = investor_df['longitude'].round(4)
            combined_str_df['lat_match'] = combined_str_df['latitude'].round(4)
            combined_str_df['lon_match'] = combined_str_df['longitude'].round(4)
            
            displacement_events = pd.merge(
                investor_df, 
                combined_str_df, 
                on=['lat_match', 'lon_match'], 
                how='inner',
                suffixes=('_corporate_buy', '_str_listing')
            )
            
            # Save the matched pipeline file (Streamlit reads this for the displacement tab)
            displacement_events.to_csv(MERGED_OUTPUT_PATH, index=False)
            print(f"Stitched pipeline complete! Identified {len(displacement_events)} cumulative displacement occurrences.")
    else:
        print(f"No companion corporate file located at {INVESTOR_DATA_PATH}. Skipping dataset integration merge.")

if __name__ == "__main__":
    main()