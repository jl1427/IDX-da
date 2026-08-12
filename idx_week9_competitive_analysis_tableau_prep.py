import pandas as pd


SOLD_FILE = "week7_clean_filtered_sold_dataset.csv"

COMPETITIVE_TRANSACTION_FILE = "week9_competitive_transactions_tableau.csv"
TOP_AGENTS_FILE = "week9_top_100_listing_agents.csv"
TOP_OFFICES_FILE = "week9_top_100_listing_offices.csv"
ZIP_PRICE_HEATMAP_FILE = "week9_zip_median_close_price_heatmap.csv"
ZIP_SALES_HEATMAP_FILE = "week9_zip_homes_sold_heatmap.csv"


def load_data():
    sold = pd.read_csv(SOLD_FILE, low_memory=False)
    print("Loaded sold dataset:", sold.shape)
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
        sold["listing_agent_name_for_analysis"] = sold[agent_col].fillna("Unknown")

    if office_col is None:
        sold["listing_office_name_for_analysis"] = "Unknown"
    else:
        sold["listing_office_name_for_analysis"] = sold[office_col].fillna("Unknown")

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


def create_zip_heatmap_files(sold):
    required_cols = ["PostalCode", "ClosePrice"]

    for col in required_cols:
        if col not in sold.columns:
            print(f"{col} not found. Zip heatmap files not created.")
            return

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


def main():
    sold = load_data()
    sold = prepare_columns(sold)

    competitive = create_competitive_transaction_file(sold)

    create_top_agents(competitive)
    create_top_offices(competitive)
    create_zip_heatmap_files(competitive)

    print("\nWeek 9 competitive analysis prep completed successfully.")


if __name__ == "__main__":
    main()
