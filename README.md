# El Paso Housing Market Dynamics Tracker
### Investor Buyouts & Short-Term Rental (STR) Impact Dashboard

## 📌 Project Purpose
In recent years, the intersection of corporate real estate investment and the short-term rental (STR) market has fundamentally transformed local housing ecosystems. In El Paso, Texas, these dynamics heavily influence housing availability, neighborhood stability, and long-term rental pricing. 

The purpose of this project is to bridge the gap between abstract real estate transactions and localized housing policy debates. By cross-referencing corporate single-family home acquisitions with active vacation rental listings (Airbnb/VRBO), this application acts as a **conversion detector**. It provides housing advocates, city planners, and community members with data-driven insights into how residential housing stock is shifting away from traditional primary homeownership into decentralized, "scattered-site" commercial hotel networks.

---

## 🛠️ How It Is Accomplished

This project splits the technical burden between a high-integrity, automated data pipeline and a lightweight, interactive frontend dashboard. To completely eliminate runtime API costs and ensure blazing-fast page load speeds, the architecture uses a **weekly offline synchronization pattern**.

### 1. Data Sources & Stitching Logic
The application relies on two primary datasets:
*   **Corporate Baseline (`investor_buys.csv`):** A pre-filtered, comprehensive dataset containing every residential property transaction involving a commercial entity (LLCs, corporations, trusts, or partnerships) across the entire calendar year of 2025 in El Paso.
*   **Active Hospitality Comps (`active_str_listings.csv`):** Live-updating active short-term rental metrics (nightly pricing, property attributes, coordinates) aggregated city-wide via the **RentCast API**.

Once a week, an automated Python data engine cross-references these datasets using a spatial coordinate join (latitude and longitude rounded to 4 decimal places, or roughly 11 meters). When a property from the 2025 corporate buying baseline appears in the active STR snapshot, the system logs it as a **"Local Displacement Event"** and calculates the exact velocity of the corporate-to-STR pipeline.

### 2. Automated Pipeline Workflow (GitHub Actions)
Rather than making expensive live API calls every time a user views the dashboard, a background workflow automates the collection process:
*   **The Trigger:** A GitHub Actions cron-job spins up a secure environment automatically every Sunday at midnight UTC.
*   **The Controlled Hit:** The runner executes `sync_data.py`, making a maximum of just 1–2 highly optimized, paginated API requests to grab the entire city's STR inventory in 500-record blocks.
*   **Append & Deduplicate:** The script reads the existing tracking history, appends the new weekly snapshot with a unique `snapshot_date` timestamp, and removes duplicates to allow for longitudinal tracking over time.
*   **The Safe Commit:** The updated files are safely committed back to the repository's `data/` folder, meaning the database builds a true historical timeline completely free of infrastructure costs.

### 3. Interactive Analytics Frontend (Streamlit)
The frontend dashboard (`app.py`) reads the flat, pre-compiled CSV files instantly to deliver two main interactive viewpoints:
*   **The Investor Buyout Tab:** Maps out the 2025 corporate purchases, highlighting which properties have successfully flipped into active STR pipelines, along with a calculated conversion rate scorecard.
*   **The STR "Hotel Equivalent" Tab:** Groups active listings by El Paso ZIP codes, scaling their average daily rates (ADR) into an executive-style metrics simulator showing estimated monthly revenue escaping the long-term residential housing market.

---

## 📂 Repository Structure

```text
el-paso-housing-tracker/
│
├── .github/
│   └── workflows/
│       └── weekly_sync.yml      # GitHub Actions cron-job configuration
│
├── data/                        # Project storage directory
│   ├── investor_buys.csv        # 2025 comprehensive corporate transactions baseline
│   ├── active_str_listings.csv  # Appended historical/weekly RentCast STR snapshots
│   └── local_displacement_trends.csv # Stitched spatial matches (pipeline conversions)
│
├── .gitignore                   # Prevents tracking caches and local environments
├── app.py                       # Streamlit web interface dashboard frontend
├── requirements.txt             # Deployment dependencies for hosting platforms
└── sync_data.py                 # Core automation script executing the batch data merge
