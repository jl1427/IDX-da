import pandas as pd

# =========================
# IDX Exchange - Week 9
# Competitive Analysis Tableau Prep
# =========================
# Purpose:
# This script prepares Tableau-ready files for the Week 9 competitive analysis meeting.
# It creates files for:
# 1. Top 100 listing agents by sales volume and units
# 2. Top 100 listing offices by sales volume and units
# 3. Zip code heat map of median close prices
# 4. Zip code heat map of homes sold
# 5. A Tableau-ready competitive transactions file

SOLD_FILE = "week7_clean_filtered_sold_dataset.csv"

COMPETITIVE_TRANSACTION_FILE = "week9_competitive_transactions_tableau.csv"
TOP_AGENTS_FILE = "week9_top_100_listing_agents.csv"
TOP_OFFICES_FILE = "week9_top_100_listing_offices.csv"
ZIP_PRICE_HEATMAP_FILE = "week9_zip_median_close_price_heatmap.csv"
ZIP_SALES_HEATMAP_FILE = "week9_zip_homes_sold_heatmap.csv"
WEEK9_SUMMARY_FILE = "week9_competitive_analysis_summary.csv"


def load_data():
    sold = pd.read_csv(SOLD_FILE, low_memory=False)
    print("Loaded Week 7 clean filtered sold dataset:", sold.shape)
    return sold


def pick_first_available_column(df, possible_columns):
    for col in possible_columns:
        if col in df.columns:
            return col
    return None


def prepare_columns(sold):
    if "CloseDate" in sold.columns:
        sold["CloseDate"] = pd.to_datetime(sold["CloseDate"], errors="coerce")

    numeric_cols = [
        "ClosePrice",
        "LivingArea",
        "DaysOnMarket",
        "price_per_sqft",
        "close_to_original_list_ratio",
        "Latitude",
        "Longitude"
    ]

    for col in numeric_cols:
        if col in sold.columns:
            sold[col] = pd.to_numeric(sold[col], errors="coerce")

    if "YrMo" not in sold.columns and "CloseDate" in sold.columns:
        sold["YrMo"] = sold["CloseDate"].dt.to_period("M").astype(str)

    if "year" not in sold.columns and "CloseDate" in sold.columns:
        sold["year"] = sold["CloseDate"].dt.year

    if "month" not in sold.columns and "CloseDate" in sold.columns:
        sold["month"] = sold["CloseDate"].dt.month

    agent_col = pick_first_available_column(
        sold,
        [
            "ListAgentFullName",
            "ListingAgentFullName",
            "ListAgentName",
            "ListingAgentName",
            "ListAgentFirstName"
        ]
    )

    office_col = pick_first_available_column(
        sold,
        [
            "ListOfficeName",
            "ListingOfficeName",
            "ListOfficeMlsId",
            "ListOfficeKey"
        ]
    )

    if agent_col is None:
        sold["listing_agent_name_for_analysis"] = "Unknown"
    else:
        sold["listing_agent_name_for_analysis"] = sold[agent_col].fillna("Unknown").astype(str).str.strip()

    if office_col is None:
        sold["listing_office_name_for_analysis"] = "Unknown"
    else:
        sold["listing_office_name_for_analysis"] = sold[office_col].fillna("Unknown").astype(str).str.strip()

    print("Agent column used:", agent_col)
    print("Office column used:", office_col)

    return sold


def create_competitive_transaction_file(sold):
    columns_to_keep = [
        "CloseDate",
        "YrMo",
        "year",
        "month",
        "ClosePrice",
        "LivingArea",
        "DaysOnMarket",
        "price_per_sqft",
        "close_to_original_list_ratio",
        "CountyOrParish",
        "City",
        "PostalCode",
        "PropertyType",
        "PropertySubType",
        "Latitude",
        "Longitude",
        "listing_agent_name_for_analysis",
        "listing_office_name_for_analysis"
    ]

    available_cols = [col for col in columns_to_keep if col in sold.columns]
    competitive = sold[available_cols].copy()
    competitive.to_csv(COMPETITIVE_TRANSACTION_FILE, index=False)

    print("Competitive transaction file saved to:", COMPETITIVE_TRANSACTION_FILE)
    return competitive


def create_top_agents(sold):
    summary = sold.groupby("listing_agent_name_for_analysis").agg(
        sales_units=("ClosePrice", "count"),
        sales_volume=("ClosePrice", "sum"),
        median_close_price=("ClosePrice", "median"),
        average_close_price=("ClosePrice", "mean"),
        average_days_on_market=("DaysOnMarket", "mean")
    ).reset_index()

    summary = summary.sort_values(
        ["sales_volume", "sales_units"],
        ascending=[False, False]
    )

    top_100 = summary.head(100)
    top_100.to_csv(TOP_AGENTS_FILE, index=False)
    print("Top 100 listing agents saved to:", TOP_AGENTS_FILE)

    return top_100


def create_top_offices(sold):
    summary = sold.groupby("listing_office_name_for_analysis").agg(
        sales_units=("ClosePrice", "count"),
        sales_volume=("ClosePrice", "sum"),
        median_close_price=("ClosePrice", "median"),
        average_close_price=("ClosePrice", "mean"),
        average_days_on_market=("DaysOnMarket", "mean")
    ).reset_index()

    summary = summary.sort_values(
        ["sales_volume", "sales_units"],
        ascending=[False, False]
    )

    top_100 = summary.head(100)
    top_100.to_csv(TOP_OFFICES_FILE, index=False)
    print("Top 100 listing offices saved to:", TOP_OFFICES_FILE)

    return top_100


def create_zip_heatmap_files(sold):
    if "PostalCode" not in sold.columns or "ClosePrice" not in sold.columns:
        print("PostalCode or ClosePrice not found. Zip heatmap files were not created.")
        return None

    group_cols = ["PostalCode"]

    optional_cols = ["YrMo", "City", "CountyOrParish", "PropertySubType"]
    for col in optional_cols:
        if col in sold.columns:
            group_cols.append(col)

    zip_summary = sold.groupby(group_cols).agg(
        homes_sold=("ClosePrice", "count"),
        median_close_price=("ClosePrice", "median"),
        average_close_price=("ClosePrice", "mean"),
        median_price_per_sqft=("price_per_sqft", "median"),
        average_days_on_market=("DaysOnMarket", "mean")
    ).reset_index()

    price_heatmap = zip_summary.sort_values("median_close_price", ascending=False)
    sales_heatmap = zip_summary.sort_values("homes_sold", ascending=False)

    price_heatmap.to_csv(ZIP_PRICE_HEATMAP_FILE, index=False)
    sales_heatmap.to_csv(ZIP_SALES_HEATMAP_FILE, index=False)

    print("Zip median close price heatmap file saved to:", ZIP_PRICE_HEATMAP_FILE)
    print("Zip homes sold heatmap file saved to:", ZIP_SALES_HEATMAP_FILE)

    return zip_summary


def create_week9_summary(competitive, top_agents, top_offices, zip_summary):
    summary_rows = [
        {
            "item": "competitive_transaction_rows",
            "value": len(competitive),
            "notes": "Rows available for Tableau competitive analysis."
        },
        {
            "item": "top_agent_rows",
            "value": len(top_agents),
            "notes": "Top listing agent rows created, capped at 100."
        },
        {
            "item": "top_office_rows",
            "value": len(top_offices),
            "notes": "Top listing office rows created, capped at 100."
        }
    ]

    if zip_summary is not None:
        summary_rows.append({
            "item": "zip_summary_rows",
            "value": len(zip_summary),
            "notes": "Zip-level rows for price and homes sold heat maps."
        })

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(WEEK9_SUMMARY_FILE, index=False)
    print("Week 9 summary saved to:", WEEK9_SUMMARY_FILE)


def main():
    sold = load_data()
    sold = prepare_columns(sold)

    competitive = create_competitive_transaction_file(sold)
    top_agents = create_top_agents(competitive)
    top_offices = create_top_offices(competitive)
    zip_summary = create_zip_heatmap_files(competitive)

    create_week9_summary(competitive, top_agents, top_offices, zip_summary)

    print("\nWeek 9 competitive analysis prep completed successfully.")
    print("Open Tableau and build competitive_analysis.twbx using the generated CSV files.")


if __name__ == "__main__":
    main()
