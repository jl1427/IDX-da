"""
IDX Exchange - Week 2 Deliverable
Dataset Structuring and Validation

This script:
1. Loads the Week 1 Residential-filtered datasets.
2. Documents unique property types.
3. Creates null-count and null-percentage reports.
4. Flags columns above 90% null.
5. Creates numeric distribution summaries.
6. Saves filtered datasets for the next step.
"""

from pathlib import Path
import pandas as pd


OUTPUT_FOLDER = Path("output")

SOLD_INPUT = OUTPUT_FOLDER / "combined_sold_residential.csv"
LISTINGS_INPUT = OUTPUT_FOLDER / "combined_listings_residential.csv"

SOLD_OUTPUT = OUTPUT_FOLDER / "sold_week2_filtered.csv"
LISTINGS_OUTPUT = OUTPUT_FOLDER / "listings_week2_filtered.csv"


def null_report(df):
    """Return a table with missing count and missing percentage by column."""
    report = pd.DataFrame({
        "column": df.columns,
        "missing_count": df.isna().sum().values,
        "missing_percent": (df.isna().mean().values * 100).round(2),
        "dtype": [str(dtype) for dtype in df.dtypes.values]
    })

    return report.sort_values("missing_percent", ascending=False)


def high_missing_columns(null_report_df, threshold=90):
    """Return columns above the missing percentage threshold."""
    return null_report_df[null_report_df["missing_percent"] > threshold].copy()


def unique_property_types(df):
    """Return unique PropertyType values and counts."""
    if "PropertyType" not in df.columns:
        return pd.DataFrame({"PropertyType": [], "count": []})

    return (
        df["PropertyType"]
        .fillna("Missing")
        .value_counts()
        .reset_index()
        .rename(columns={"index": "PropertyType", "PropertyType": "count"})
    )


def numeric_summary(df, columns):
    """Create numeric distribution summary for selected columns."""
    existing_columns = [col for col in columns if col in df.columns]

    if not existing_columns:
        return pd.DataFrame()

    numeric_df = df[existing_columns].copy()

    for col in existing_columns:
        numeric_df[col] = pd.to_numeric(numeric_df[col], errors="coerce")

    summary = numeric_df.describe(percentiles=[0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]).T
    summary = summary.rename(columns={
        "50%": "median",
        "25%": "p25",
        "75%": "p75",
        "1%": "p01",
        "5%": "p05",
        "95%": "p95",
        "99%": "p99"
    })

    return summary.reset_index().rename(columns={"index": "column"})


def print_basic_structure(name, df):
    """Print basic dataset structure."""
    print(f"\n{name} dataset structure")
    print("-" * 40)
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    print("\nColumn data types:")
    print(df.dtypes)


def main():
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    sold = pd.read_csv(SOLD_INPUT, low_memory=False)
    listings = pd.read_csv(LISTINGS_INPUT, low_memory=False)

    print_basic_structure("Sold", sold)
    print_basic_structure("Listings", listings)

    sold_property_types = unique_property_types(sold)
    listings_property_types = unique_property_types(listings)

    sold_null = null_report(sold)
    listings_null = null_report(listings)

    sold_high_missing = high_missing_columns(sold_null)
    listings_high_missing = high_missing_columns(listings_null)

    numeric_columns = ["ClosePrice", "LivingArea", "DaysOnMarket"]
    sold_numeric_summary = numeric_summary(sold, numeric_columns)

    listing_numeric_columns = ["ListPrice", "OriginalListPrice", "LivingArea", "DaysOnMarket"]
    listings_numeric_summary = numeric_summary(listings, listing_numeric_columns)

    sold_property_types.to_csv(OUTPUT_FOLDER / "week2_sold_unique_property_types.csv", index=False)
    listings_property_types.to_csv(OUTPUT_FOLDER / "week2_listings_unique_property_types.csv", index=False)

    sold_null.to_csv(OUTPUT_FOLDER / "week2_sold_null_report.csv", index=False)
    listings_null.to_csv(OUTPUT_FOLDER / "week2_listings_null_report.csv", index=False)

    sold_high_missing.to_csv(OUTPUT_FOLDER / "week2_sold_high_missing_columns.csv", index=False)
    listings_high_missing.to_csv(OUTPUT_FOLDER / "week2_listings_high_missing_columns.csv", index=False)

    sold_numeric_summary.to_csv(OUTPUT_FOLDER / "week2_sold_numeric_summary.csv", index=False)
    listings_numeric_summary.to_csv(OUTPUT_FOLDER / "week2_listings_numeric_summary.csv", index=False)

    sold.to_csv(SOLD_OUTPUT, index=False)
    listings.to_csv(LISTINGS_OUTPUT, index=False)

    print("\nWeek 2 validation complete.")
    print(f"Sold columns above 90% missing: {len(sold_high_missing)}")
    print(f"Listings columns above 90% missing: {len(listings_high_missing)}")
    print("\nSaved reports to the output folder.")


if __name__ == "__main__":
    main()
