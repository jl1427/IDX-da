"""
IDX Exchange Data Analyst Internship
Weeks 2-3 Deliverable: Dataset Structuring, Validation, and Mortgage Rate Enrichment

This script performs the required Week 3 tasks:
1. Loads combined sold and listing datasets.
2. Documents unique PropertyType values.
3. Filters both datasets to PropertyType == 'Residential'.
4. Creates null-count and missing percentage reports.
5. Flags columns with more than 90% missing values.
6. Creates numeric distribution summaries for ClosePrice, LivingArea, and DaysOnMarket.
7. Fetches the FRED MORTGAGE30US mortgage rate series.
8. Resamples weekly mortgage rates to monthly averages.
9. Merges mortgage rates onto sold and listing datasets using year_month.
10. Saves all required output CSV files.

Expected input files in the same folder:
- combined_sold.csv
- combined_listings.csv
"""

import pandas as pd


SOLD_FILE = "combined_sold.csv"
LISTINGS_FILE = "combined_listings.csv"

FILTERED_SOLD_FILE = "week3_filtered_sold.csv"
FILTERED_LISTINGS_FILE = "week3_filtered_listings.csv"
SOLD_WITH_RATES_FILE = "week3_sold_with_mortgage_rates.csv"
LISTINGS_WITH_RATES_FILE = "week3_listings_with_mortgage_rates.csv"

NULL_REPORT_FILE = "week3_null_count_summary.csv"
HIGH_MISSING_FILE = "week3_columns_above_90_percent_missing.csv"
NUMERIC_SUMMARY_FILE = "week3_numeric_distribution_summary.csv"
PROPERTY_TYPE_REPORT_FILE = "week3_property_type_report.csv"


def load_data():
    sold = pd.read_csv(SOLD_FILE, low_memory=False)
    listings = pd.read_csv(LISTINGS_FILE, low_memory=False)

    print("Loaded sold dataset:", sold.shape)
    print("Loaded listings dataset:", listings.shape)
    return sold, listings


def create_property_type_report(sold, listings):
    report_frames = []

    if "PropertyType" in sold.columns:
        sold_counts = sold["PropertyType"].value_counts(dropna=False).reset_index()
        sold_counts.columns = ["PropertyType", "count"]
        sold_counts["dataset"] = "sold"
        report_frames.append(sold_counts)
        print("\nUnique PropertyType values in sold dataset:")
        print(sold["PropertyType"].dropna().unique())
    else:
        print("PropertyType column not found in sold dataset.")

    if "PropertyType" in listings.columns:
        listing_counts = listings["PropertyType"].value_counts(dropna=False).reset_index()
        listing_counts.columns = ["PropertyType", "count"]
        listing_counts["dataset"] = "listings"
        report_frames.append(listing_counts)
        print("\nUnique PropertyType values in listings dataset:")
        print(listings["PropertyType"].dropna().unique())
    else:
        print("PropertyType column not found in listings dataset.")

    if report_frames:
        report = pd.concat(report_frames, ignore_index=True)
        report = report[["dataset", "PropertyType", "count"]]
        report.to_csv(PROPERTY_TYPE_REPORT_FILE, index=False)
        print("\nProperty type report saved to:", PROPERTY_TYPE_REPORT_FILE)


def filter_residential(df, dataset_name):
    before_rows = len(df)

    if "PropertyType" in df.columns:
        filtered = df[df["PropertyType"] == "Residential"].copy()
    else:
        filtered = df.copy()
        print(f"{dataset_name}: PropertyType column not found. Residential filter not applied.")

    after_rows = len(filtered)
    print(f"\n{dataset_name} Residential filter:")
    print("Rows before filter:", before_rows)
    print("Rows after filter:", after_rows)
    print("Rows removed:", before_rows - after_rows)

    return filtered


def create_null_reports(sold, listings):
    sold_nulls = pd.DataFrame({
        "dataset": "sold",
        "column": sold.columns,
        "missing_count": sold.isna().sum().values,
        "missing_percent": (sold.isna().sum().values / len(sold)) * 100
    })

    listing_nulls = pd.DataFrame({
        "dataset": "listings",
        "column": listings.columns,
        "missing_count": listings.isna().sum().values,
        "missing_percent": (listings.isna().sum().values / len(listings)) * 100
    })

    null_report = pd.concat([sold_nulls, listing_nulls], ignore_index=True)
    null_report = null_report.sort_values(["dataset", "missing_percent"], ascending=[True, False])
    null_report.to_csv(NULL_REPORT_FILE, index=False)

    high_missing = null_report[null_report["missing_percent"] > 90].copy()
    high_missing.to_csv(HIGH_MISSING_FILE, index=False)

    print("\nNull-count summary saved to:", NULL_REPORT_FILE)
    print("Columns above 90% missing saved to:", HIGH_MISSING_FILE)


def create_numeric_summary(sold):
    required_columns = ["ClosePrice", "LivingArea", "DaysOnMarket"]
    summary_rows = []

    for col in required_columns:
        if col not in sold.columns:
            print(f"{col} not found in sold dataset.")
            continue

        values = pd.to_numeric(sold[col], errors="coerce")
        summary_rows.append({
            "column": col,
            "count": values.count(),
            "missing_count": values.isna().sum(),
            "min": values.min(),
            "max": values.max(),
            "mean": values.mean(),
            "median": values.median(),
            "p10": values.quantile(0.10),
            "p25": values.quantile(0.25),
            "p50": values.quantile(0.50),
            "p75": values.quantile(0.75),
            "p90": values.quantile(0.90),
            "p95": values.quantile(0.95),
            "p99": values.quantile(0.99)
        })

    numeric_summary = pd.DataFrame(summary_rows)
    numeric_summary.to_csv(NUMERIC_SUMMARY_FILE, index=False)
    print("Numeric distribution summary saved to:", NUMERIC_SUMMARY_FILE)


def fetch_monthly_mortgage_rates():
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"

    mortgage = pd.read_csv(url, parse_dates=["observation_date"])
    mortgage.columns = ["date", "rate_30yr_fixed"]
    mortgage["rate_30yr_fixed"] = pd.to_numeric(mortgage["rate_30yr_fixed"], errors="coerce")

    mortgage["year_month"] = mortgage["date"].dt.to_period("M").astype(str)

    mortgage_monthly = (
        mortgage.groupby("year_month", as_index=False)["rate_30yr_fixed"]
        .mean()
    )

    print("\nMonthly mortgage rate data preview:")
    print(mortgage_monthly.head())
    return mortgage_monthly


def merge_mortgage_rates(sold, listings, mortgage_monthly):
    if "CloseDate" in sold.columns:
        sold["CloseDate"] = pd.to_datetime(sold["CloseDate"], errors="coerce")
        sold["year_month"] = sold["CloseDate"].dt.to_period("M").astype(str)
    else:
        print("CloseDate column not found in sold dataset.")

    if "ListingContractDate" in listings.columns:
        listings["ListingContractDate"] = pd.to_datetime(listings["ListingContractDate"], errors="coerce")
        listings["year_month"] = listings["ListingContractDate"].dt.to_period("M").astype(str)
    else:
        print("ListingContractDate column not found in listings dataset.")

    sold_with_rates = sold.merge(mortgage_monthly, on="year_month", how="left")
    listings_with_rates = listings.merge(mortgage_monthly, on="year_month", how="left")

    sold_null_rates = sold_with_rates["rate_30yr_fixed"].isna().sum()
    listing_null_rates = listings_with_rates["rate_30yr_fixed"].isna().sum()

    print("\nMortgage rate merge validation:")
    print("Sold rows with null mortgage rate:", sold_null_rates)
    print("Listing rows with null mortgage rate:", listing_null_rates)

    sold_with_rates.to_csv(SOLD_WITH_RATES_FILE, index=False)
    listings_with_rates.to_csv(LISTINGS_WITH_RATES_FILE, index=False)

    print("Sold dataset with mortgage rates saved to:", SOLD_WITH_RATES_FILE)
    print("Listings dataset with mortgage rates saved to:", LISTINGS_WITH_RATES_FILE)


def main():
    sold, listings = load_data()

    create_property_type_report(sold, listings)

    sold_residential = filter_residential(sold, "Sold")
    listings_residential = filter_residential(listings, "Listings")

    sold_residential.to_csv(FILTERED_SOLD_FILE, index=False)
    listings_residential.to_csv(FILTERED_LISTINGS_FILE, index=False)
    print("\nFiltered sold dataset saved to:", FILTERED_SOLD_FILE)
    print("Filtered listings dataset saved to:", FILTERED_LISTINGS_FILE)

    create_null_reports(sold_residential, listings_residential)
    create_numeric_summary(sold_residential)

    mortgage_monthly = fetch_monthly_mortgage_rates()
    merge_mortgage_rates(sold_residential, listings_residential, mortgage_monthly)

    print("\nWeek 3 deliverable completed successfully.")


if __name__ == "__main__":
    main()
