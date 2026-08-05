import pandas as pd
import numpy as np


SOLD_FILE = "week5_final_cleaned_sold_analysis_ready.csv"
LISTINGS_FILE = "week5_final_cleaned_listings_analysis_ready.csv"

SOLD_FEATURES_FILE = "week6_sold_feature_engineered.csv"
LISTINGS_FEATURES_FILE = "week6_listings_feature_engineered.csv"

SAMPLE_OUTPUT_FILE = "week6_sample_engineered_metrics.csv"
COUNTY_SUMMARY_FILE = "week6_county_market_summary.csv"
PROPERTY_TYPE_SUMMARY_FILE = "week6_property_type_summary.csv"
OFFICE_SUMMARY_FILE = "week6_office_competitive_summary.csv"


DATE_COLUMNS = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate"
]

NUMERIC_COLUMNS = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "DaysOnMarket",
    "rate_30yr_fixed"
]


def load_data():
    sold = pd.read_csv(SOLD_FILE, low_memory=False)
    listings = pd.read_csv(LISTINGS_FILE, low_memory=False)

    print("Loaded Week 5 sold dataset:", sold.shape)
    print("Loaded Week 5 listings dataset:", listings.shape)

    return sold, listings


def convert_columns(df, dataset_name):
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            print(f"{dataset_name}: converted {col} to datetime.")
        else:
            print(f"{dataset_name}: {col} not found.")

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            print(f"{dataset_name}: converted {col} to numeric.")
        else:
            print(f"{dataset_name}: {col} not found.")

    return df


def safe_divide(numerator, denominator):
    return np.where(
        (denominator.notna()) & (denominator != 0),
        numerator / denominator,
        np.nan
    )


def engineer_sold_metrics(sold):
    sold = convert_columns(sold, "Sold")

    if "ClosePrice" in sold.columns and "OriginalListPrice" in sold.columns:
        sold["price_ratio"] = safe_divide(
            sold["ClosePrice"],
            sold["OriginalListPrice"]
        )

        sold["close_to_original_list_ratio"] = safe_divide(
            sold["ClosePrice"],
            sold["OriginalListPrice"]
        )

    if "ClosePrice" in sold.columns and "LivingArea" in sold.columns:
        sold["price_per_sqft"] = safe_divide(
            sold["ClosePrice"],
            sold["LivingArea"]
        )

    if "CloseDate" in sold.columns:
        sold["year"] = sold["CloseDate"].dt.year
        sold["month"] = sold["CloseDate"].dt.month
        sold["YrMo"] = sold["CloseDate"].dt.to_period("M").astype(str)

    if "PurchaseContractDate" in sold.columns and "ListingContractDate" in sold.columns:
        sold["listing_to_contract_days"] = (
            sold["PurchaseContractDate"] - sold["ListingContractDate"]
        ).dt.days

    if "CloseDate" in sold.columns and "PurchaseContractDate" in sold.columns:
        sold["contract_to_close_days"] = (
            sold["CloseDate"] - sold["PurchaseContractDate"]
        ).dt.days

    print("\nSold feature engineering completed.")
    return sold


def engineer_listing_metrics(listings):
    listings = convert_columns(listings, "Listings")

    if "ListPrice" in listings.columns and "OriginalListPrice" in listings.columns:
        listings["list_to_original_list_ratio"] = safe_divide(
            listings["ListPrice"],
            listings["OriginalListPrice"]
        )

    if "ListPrice" in listings.columns and "LivingArea" in listings.columns:
        listings["list_price_per_sqft"] = safe_divide(
            listings["ListPrice"],
            listings["LivingArea"]
        )

    if "ListingContractDate" in listings.columns:
        listings["year"] = listings["ListingContractDate"].dt.year
        listings["month"] = listings["ListingContractDate"].dt.month
        listings["YrMo"] = listings["ListingContractDate"].dt.to_period("M").astype(str)

    print("\nListings feature engineering completed.")
    return listings


def create_sample_output(sold):
    sample_columns = [
        "CloseDate",
        "ClosePrice",
        "OriginalListPrice",
        "LivingArea",
        "DaysOnMarket",
        "price_ratio",
        "close_to_original_list_ratio",
        "price_per_sqft",
        "YrMo",
        "listing_to_contract_days",
        "contract_to_close_days",
        "rate_30yr_fixed"
    ]

    available_columns = [col for col in sample_columns if col in sold.columns]

    sample = sold[available_columns].head(25)
    sample.to_csv(SAMPLE_OUTPUT_FILE, index=False)

    print("Sample engineered metrics saved to:", SAMPLE_OUTPUT_FILE)


def create_county_summary(sold):
    if "CountyOrParish" not in sold.columns:
        print("CountyOrParish not found. County summary not created.")
        return

    summary = sold.groupby("CountyOrParish").agg(
        closed_sales=("ClosePrice", "count"),
        median_close_price=("ClosePrice", "median"),
        average_close_price=("ClosePrice", "mean"),
        median_price_per_sqft=("price_per_sqft", "median"),
        average_days_on_market=("DaysOnMarket", "mean"),
        median_close_to_original_list_ratio=("close_to_original_list_ratio", "median"),
        average_mortgage_rate=("rate_30yr_fixed", "mean")
    ).reset_index()

    summary = summary.sort_values("closed_sales", ascending=False)
    summary.to_csv(COUNTY_SUMMARY_FILE, index=False)

    print("County market summary saved to:", COUNTY_SUMMARY_FILE)


def create_property_type_summary(sold):
    group_columns = []

    if "PropertyType" in sold.columns:
        group_columns.append("PropertyType")

    if "PropertySubType" in sold.columns:
        group_columns.append("PropertySubType")

    if not group_columns:
        print("PropertyType and PropertySubType not found. Property type summary not created.")
        return

    summary = sold.groupby(group_columns).agg(
        closed_sales=("ClosePrice", "count"),
        median_close_price=("ClosePrice", "median"),
        average_close_price=("ClosePrice", "mean"),
        median_price_per_sqft=("price_per_sqft", "median"),
        average_days_on_market=("DaysOnMarket", "mean"),
        median_close_to_original_list_ratio=("close_to_original_list_ratio", "median")
    ).reset_index()

    summary = summary.sort_values("closed_sales", ascending=False)
    summary.to_csv(PROPERTY_TYPE_SUMMARY_FILE, index=False)

    print("Property type summary saved to:", PROPERTY_TYPE_SUMMARY_FILE)


def create_office_summary(sold):
    office_col = None

    if "ListOfficeName" in sold.columns:
        office_col = "ListOfficeName"
    elif "BuyerOfficeName" in sold.columns:
        office_col = "BuyerOfficeName"

    if office_col is None:
        print("ListOfficeName or BuyerOfficeName not found. Office summary not created.")
        return

    summary = sold.groupby(office_col).agg(
        closed_sales_units=("ClosePrice", "count"),
        total_sales_volume=("ClosePrice", "sum"),
        median_close_price=("ClosePrice", "median"),
        average_days_on_market=("DaysOnMarket", "mean")
    ).reset_index()

    summary = summary.sort_values(
        ["total_sales_volume", "closed_sales_units"],
        ascending=[False, False]
    )

    summary.to_csv(OFFICE_SUMMARY_FILE, index=False)

    print("Office competitive summary saved to:", OFFICE_SUMMARY_FILE)


def main():
    sold, listings = load_data()

    sold_features = engineer_sold_metrics(sold)
    listings_features = engineer_listing_metrics(listings)

    sold_features.to_csv(SOLD_FEATURES_FILE, index=False)
    listings_features.to_csv(LISTINGS_FEATURES_FILE, index=False)

    create_sample_output(sold_features)
    create_county_summary(sold_features)
    create_property_type_summary(sold_features)
    create_office_summary(sold_features)

    print("\nSold feature-engineered dataset saved to:", SOLD_FEATURES_FILE)
    print("Listings feature-engineered dataset saved to:", LISTINGS_FEATURES_FILE)
    print("\nWeek 6 deliverable completed successfully.")


if __name__ == "__main__":
    main()
