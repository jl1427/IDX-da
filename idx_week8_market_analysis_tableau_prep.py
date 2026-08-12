import pandas as pd


SOLD_FILE = "week7_clean_filtered_sold_dataset.csv"
LISTINGS_FILE = "week6_listings_feature_engineered.csv"

MARKET_SOLD_FILE = "week8_market_analysis_sold_tableau.csv"
MARKET_LISTINGS_FILE = "week8_market_analysis_listings_tableau.csv"
MONTHLY_MARKET_SUMMARY_FILE = "week8_monthly_market_summary.csv"
CITY_MARKET_SUMMARY_FILE = "week8_city_market_summary.csv"
COUNTY_MARKET_SUMMARY_FILE = "week8_county_market_summary.csv"


def load_data():
    sold = pd.read_csv(SOLD_FILE, low_memory=False)
    listings = pd.read_csv(LISTINGS_FILE, low_memory=False)

    print("Loaded sold dataset:", sold.shape)
    print("Loaded listings dataset:", listings.shape)

    return sold, listings


def convert_sold_columns(sold):
    date_cols = ["CloseDate", "PurchaseContractDate", "ListingContractDate"]

    for col in date_cols:
        if col in sold.columns:
            sold[col] = pd.to_datetime(sold[col], errors="coerce")

    numeric_cols = [
        "ClosePrice",
        "OriginalListPrice",
        "LivingArea",
        "DaysOnMarket",
        "price_per_sqft",
        "close_to_original_list_ratio",
        "rate_30yr_fixed"
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

    return sold


def convert_listing_columns(listings):
    if "ListingContractDate" in listings.columns:
        listings["ListingContractDate"] = pd.to_datetime(
            listings["ListingContractDate"],
            errors="coerce"
        )

    numeric_cols = [
        "ListPrice",
        "OriginalListPrice",
        "LivingArea",
        "DaysOnMarket",
        "list_price_per_sqft",
        "rate_30yr_fixed"
    ]

    for col in numeric_cols:
        if col in listings.columns:
            listings[col] = pd.to_numeric(listings[col], errors="coerce")

    if "YrMo" not in listings.columns and "ListingContractDate" in listings.columns:
        listings["YrMo"] = listings["ListingContractDate"].dt.to_period("M").astype(str)

    if "year" not in listings.columns and "ListingContractDate" in listings.columns:
        listings["year"] = listings["ListingContractDate"].dt.year

    if "month" not in listings.columns and "ListingContractDate" in listings.columns:
        listings["month"] = listings["ListingContractDate"].dt.month

    return listings


def keep_market_columns_sold(sold):
    columns_to_keep = [
        "CloseDate",
        "YrMo",
        "year",
        "month",
        "ClosePrice",
        "OriginalListPrice",
        "LivingArea",
        "DaysOnMarket",
        "price_per_sqft",
        "close_to_original_list_ratio",
        "listing_to_contract_days",
        "contract_to_close_days",
        "CountyOrParish",
        "City",
        "PostalCode",
        "PropertyType",
        "PropertySubType",
        "Latitude",
        "Longitude",
        "rate_30yr_fixed"
    ]

    available_cols = [col for col in columns_to_keep if col in sold.columns]
    return sold[available_cols].copy()


def keep_market_columns_listings(listings):
    columns_to_keep = [
        "ListingContractDate",
        "YrMo",
        "year",
        "month",
        "ListPrice",
        "OriginalListPrice",
        "LivingArea",
        "DaysOnMarket",
        "list_price_per_sqft",
        "CountyOrParish",
        "City",
        "PostalCode",
        "PropertyType",
        "PropertySubType",
        "Latitude",
        "Longitude",
        "rate_30yr_fixed"
    ]

    available_cols = [col for col in columns_to_keep if col in listings.columns]
    return listings[available_cols].copy()


def create_monthly_market_summary(sold, listings):
    sold_summary = sold.groupby("YrMo").agg(
        closed_sales=("ClosePrice", "count"),
        median_close_price=("ClosePrice", "median"),
        average_close_price=("ClosePrice", "mean"),
        average_days_on_market=("DaysOnMarket", "mean"),
        median_price_per_sqft=("price_per_sqft", "median"),
        average_close_to_original_list_ratio=("close_to_original_list_ratio", "mean"),
        average_mortgage_rate=("rate_30yr_fixed", "mean")
    ).reset_index()

    if "YrMo" in listings.columns:
        listing_summary = listings.groupby("YrMo").agg(
            new_listings=("ListPrice", "count"),
            median_list_price=("ListPrice", "median")
        ).reset_index()

        monthly_summary = sold_summary.merge(listing_summary, on="YrMo", how="left")
    else:
        monthly_summary = sold_summary
        monthly_summary["new_listings"] = None
        monthly_summary["median_list_price"] = None

    monthly_summary = monthly_summary.sort_values("YrMo")
    monthly_summary.to_csv(MONTHLY_MARKET_SUMMARY_FILE, index=False)

    print("Monthly market summary saved to:", MONTHLY_MARKET_SUMMARY_FILE)


def create_city_market_summary(sold):
    if "City" not in sold.columns:
        print("City column not found. City summary not created.")
        return

    city_summary = sold.groupby("City").agg(
        closed_sales=("ClosePrice", "count"),
        median_close_price=("ClosePrice", "median"),
        average_days_on_market=("DaysOnMarket", "mean"),
        median_price_per_sqft=("price_per_sqft", "median"),
        average_close_to_original_list_ratio=("close_to_original_list_ratio", "mean")
    ).reset_index()

    city_summary = city_summary.sort_values("closed_sales", ascending=False)
    city_summary.to_csv(CITY_MARKET_SUMMARY_FILE, index=False)

    print("City market summary saved to:", CITY_MARKET_SUMMARY_FILE)


def create_county_market_summary(sold):
    if "CountyOrParish" not in sold.columns:
        print("CountyOrParish column not found. County summary not created.")
        return

    county_summary = sold.groupby("CountyOrParish").agg(
        closed_sales=("ClosePrice", "count"),
        median_close_price=("ClosePrice", "median"),
        average_days_on_market=("DaysOnMarket", "mean"),
        median_price_per_sqft=("price_per_sqft", "median"),
        average_close_to_original_list_ratio=("close_to_original_list_ratio", "mean")
    ).reset_index()

    county_summary = county_summary.sort_values("closed_sales", ascending=False)
    county_summary.to_csv(COUNTY_MARKET_SUMMARY_FILE, index=False)

    print("County market summary saved to:", COUNTY_MARKET_SUMMARY_FILE)


def main():
    sold, listings = load_data()

    sold = convert_sold_columns(sold)
    listings = convert_listing_columns(listings)

    market_sold = keep_market_columns_sold(sold)
    market_listings = keep_market_columns_listings(listings)

    market_sold.to_csv(MARKET_SOLD_FILE, index=False)
    market_listings.to_csv(MARKET_LISTINGS_FILE, index=False)

    create_monthly_market_summary(market_sold, market_listings)
    create_city_market_summary(market_sold)
    create_county_market_summary(market_sold)

    print("\nMarket sold Tableau file saved to:", MARKET_SOLD_FILE)
    print("Market listings Tableau file saved to:", MARKET_LISTINGS_FILE)
    print("\nWeek 8 market analysis prep completed successfully.")


if __name__ == "__main__":
    main()
