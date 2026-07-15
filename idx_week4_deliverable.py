

import pandas as pd


SOLD_FILE = "week3_sold_with_mortgage_rates.csv"
LISTINGS_FILE = "week3_listings_with_mortgage_rates.csv"

CLEANED_SOLD_FILE = "week4_cleaned_sold_analysis_ready.csv"
CLEANED_LISTINGS_FILE = "week4_cleaned_listings_analysis_ready.csv"

CLEANING_SUMMARY_FILE = "week4_before_after_row_counts.csv"
DATE_FLAG_SUMMARY_FILE = "week4_date_consistency_flag_counts.csv"
GEO_FLAG_SUMMARY_FILE = "week4_geographic_quality_summary.csv"
DTYPE_REPORT_FILE = "week4_data_type_confirmation.csv"

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
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
    "Latitude",
    "Longitude",
    "rate_30yr_fixed"
]


def load_data():
    sold = pd.read_csv(SOLD_FILE, low_memory=False)
    listings = pd.read_csv(LISTINGS_FILE, low_memory=False)

    print("Loaded Week 3 sold dataset:", sold.shape)
    print("Loaded Week 3 listings dataset:", listings.shape)
    return sold, listings


def convert_date_columns(df, dataset_name):
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            print(f"{dataset_name}: converted {col} to datetime.")
        else:
            print(f"{dataset_name}: {col} not found.")
    return df


def convert_numeric_columns(df, dataset_name):
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            print(f"{dataset_name}: converted {col} to numeric.")
        else:
            print(f"{dataset_name}: {col} not found.")
    return df


def add_invalid_numeric_flags(df, dataset_name):
    df["invalid_close_price_flag"] = df["ClosePrice"] <= 0 if "ClosePrice" in df.columns else False
    df["invalid_living_area_flag"] = df["LivingArea"] <= 0 if "LivingArea" in df.columns else False
    df["invalid_days_on_market_flag"] = df["DaysOnMarket"] < 0 if "DaysOnMarket" in df.columns else False
    df["invalid_bedrooms_flag"] = df["BedroomsTotal"] < 0 if "BedroomsTotal" in df.columns else False
    df["invalid_bathrooms_flag"] = df["BathroomsTotalInteger"] < 0 if "BathroomsTotalInteger" in df.columns else False

    print(f"\n{dataset_name} invalid numeric flag counts:")
    print("invalid_close_price_flag:", int(df["invalid_close_price_flag"].sum()))
    print("invalid_living_area_flag:", int(df["invalid_living_area_flag"].sum()))
    print("invalid_days_on_market_flag:", int(df["invalid_days_on_market_flag"].sum()))
    print("invalid_bedrooms_flag:", int(df["invalid_bedrooms_flag"].sum()))
    print("invalid_bathrooms_flag:", int(df["invalid_bathrooms_flag"].sum()))

    return df


def add_date_consistency_flags(df, dataset_name):
    if "ListingContractDate" in df.columns and "CloseDate" in df.columns:
        df["listing_after_close_flag"] = df["ListingContractDate"] > df["CloseDate"]
    else:
        df["listing_after_close_flag"] = False

    if "PurchaseContractDate" in df.columns and "CloseDate" in df.columns:
        df["purchase_after_close_flag"] = df["PurchaseContractDate"] > df["CloseDate"]
    else:
        df["purchase_after_close_flag"] = False

    if "ListingContractDate" in df.columns and "PurchaseContractDate" in df.columns:
        df["negative_timeline_flag"] = df["ListingContractDate"] > df["PurchaseContractDate"]
    else:
        df["negative_timeline_flag"] = False

    print(f"\n{dataset_name} date consistency flag counts:")
    print("listing_after_close_flag:", int(df["listing_after_close_flag"].sum()))
    print("purchase_after_close_flag:", int(df["purchase_after_close_flag"].sum()))
    print("negative_timeline_flag:", int(df["negative_timeline_flag"].sum()))

    return df


def add_geographic_quality_flags(df, dataset_name):
    if "Latitude" in df.columns and "Longitude" in df.columns:
        df["missing_coordinates_flag"] = df["Latitude"].isna() | df["Longitude"].isna()
        df["zero_coordinates_flag"] = (df["Latitude"] == 0) | (df["Longitude"] == 0)
        df["positive_longitude_flag"] = df["Longitude"] > 0

        # Approximate California coordinate range used for quality checks.
        df["implausible_coordinates_flag"] = (
            (df["Latitude"] < 32) |
            (df["Latitude"] > 42) |
            (df["Longitude"] < -125) |
            (df["Longitude"] > -113)
        )
    else:
        df["missing_coordinates_flag"] = False
        df["zero_coordinates_flag"] = False
        df["positive_longitude_flag"] = False
        df["implausible_coordinates_flag"] = False

    print(f"\n{dataset_name} geographic quality flag counts:")
    print("missing_coordinates_flag:", int(df["missing_coordinates_flag"].sum()))
    print("zero_coordinates_flag:", int(df["zero_coordinates_flag"].sum()))
    print("positive_longitude_flag:", int(df["positive_longitude_flag"].sum()))
    print("implausible_coordinates_flag:", int(df["implausible_coordinates_flag"].sum()))

    return df


def remove_core_invalid_records(df, dataset_name):
    before_rows = len(df)

    cleaned = df[
        (df["invalid_close_price_flag"] == False) &
        (df["invalid_living_area_flag"] == False) &
        (df["invalid_days_on_market_flag"] == False) &
        (df["invalid_bedrooms_flag"] == False) &
        (df["invalid_bathrooms_flag"] == False)
    ].copy()

    after_rows = len(cleaned)

    print(f"\n{dataset_name} row count summary:")
    print("Rows before cleaning:", before_rows)
    print("Rows after cleaning:", after_rows)
    print("Rows removed:", before_rows - after_rows)

    return cleaned, before_rows, after_rows


def create_summary_reports(sold, listings, sold_before, sold_after, listings_before, listings_after):
    cleaning_summary = pd.DataFrame([
        {
            "dataset": "sold",
            "rows_before_cleaning": sold_before,
            "rows_after_cleaning": sold_after,
            "rows_removed": sold_before - sold_after
        },
        {
            "dataset": "listings",
            "rows_before_cleaning": listings_before,
            "rows_after_cleaning": listings_after,
            "rows_removed": listings_before - listings_after
        }
    ])
    cleaning_summary.to_csv(CLEANING_SUMMARY_FILE, index=False)

    date_summary = pd.DataFrame([
        {
            "dataset": "sold",
            "listing_after_close_flag": int(sold["listing_after_close_flag"].sum()),
            "purchase_after_close_flag": int(sold["purchase_after_close_flag"].sum()),
            "negative_timeline_flag": int(sold["negative_timeline_flag"].sum())
        },
        {
            "dataset": "listings",
            "listing_after_close_flag": int(listings["listing_after_close_flag"].sum()),
            "purchase_after_close_flag": int(listings["purchase_after_close_flag"].sum()),
            "negative_timeline_flag": int(listings["negative_timeline_flag"].sum())
        }
    ])
    date_summary.to_csv(DATE_FLAG_SUMMARY_FILE, index=False)

    geo_summary = pd.DataFrame([
        {
            "dataset": "sold",
            "missing_coordinates_flag": int(sold["missing_coordinates_flag"].sum()),
            "zero_coordinates_flag": int(sold["zero_coordinates_flag"].sum()),
            "positive_longitude_flag": int(sold["positive_longitude_flag"].sum()),
            "implausible_coordinates_flag": int(sold["implausible_coordinates_flag"].sum())
        },
        {
            "dataset": "listings",
            "missing_coordinates_flag": int(listings["missing_coordinates_flag"].sum()),
            "zero_coordinates_flag": int(listings["zero_coordinates_flag"].sum()),
            "positive_longitude_flag": int(listings["positive_longitude_flag"].sum()),
            "implausible_coordinates_flag": int(listings["implausible_coordinates_flag"].sum())
        }
    ])
    geo_summary.to_csv(GEO_FLAG_SUMMARY_FILE, index=False)

    dtype_rows = []
    for dataset_name, df in [("sold", sold), ("listings", listings)]:
        for col in DATE_COLUMNS + NUMERIC_COLUMNS:
            if col in df.columns:
                dtype_rows.append({
                    "dataset": dataset_name,
                    "column": col,
                    "dtype_after_cleaning": str(df[col].dtype)
                })
    dtype_report = pd.DataFrame(dtype_rows)
    dtype_report.to_csv(DTYPE_REPORT_FILE, index=False)

    print("\nCleaning summary saved to:", CLEANING_SUMMARY_FILE)
    print("Date consistency flag summary saved to:", DATE_FLAG_SUMMARY_FILE)
    print("Geographic quality summary saved to:", GEO_FLAG_SUMMARY_FILE)
    print("Data type confirmation saved to:", DTYPE_REPORT_FILE)


def clean_dataset(df, dataset_name):
    df = convert_date_columns(df, dataset_name)
    df = convert_numeric_columns(df, dataset_name)
    df = add_invalid_numeric_flags(df, dataset_name)
    df = add_date_consistency_flags(df, dataset_name)
    df = add_geographic_quality_flags(df, dataset_name)
    cleaned, before_rows, after_rows = remove_core_invalid_records(df, dataset_name)
    return cleaned, before_rows, after_rows


def main():
    sold, listings = load_data()

    sold_cleaned, sold_before, sold_after = clean_dataset(sold, "Sold")
    listings_cleaned, listings_before, listings_after = clean_dataset(listings, "Listings")

    sold_cleaned.to_csv(CLEANED_SOLD_FILE, index=False)
    listings_cleaned.to_csv(CLEANED_LISTINGS_FILE, index=False)

    create_summary_reports(
        sold_cleaned,
        listings_cleaned,
        sold_before,
        sold_after,
        listings_before,
        listings_after
    )

    print("\nCleaned sold dataset saved to:", CLEANED_SOLD_FILE)
    print("Cleaned listings dataset saved to:", CLEANED_LISTINGS_FILE)
    print("\nWeek 4 deliverable completed successfully.")


if __name__ == "__main__":
    main()
