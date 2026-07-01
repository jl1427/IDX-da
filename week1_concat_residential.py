
from pathlib import Path
import pandas as pd


CSV_FOLDER = Path("csv")
OUTPUT_FOLDER = Path("output")


def read_and_combine_files(file_pattern):
    """Read all matching CSV files and combine them into one DataFrame."""
    files = sorted(CSV_FOLDER.glob(file_pattern))

    if not files:
        raise FileNotFoundError(f"No files found for pattern: {file_pattern}")

    dataframes = []
    row_counts = []

    for file in files:
        df = pd.read_csv(file, low_memory=False)
        dataframes.append(df)
        row_counts.append({
            "file_name": file.name,
            "rows": len(df),
            "columns": len(df.columns)
        })

    combined = pd.concat(dataframes, ignore_index=True)

    return combined, files, pd.DataFrame(row_counts)


def filter_residential(df):
    """Filter the dataset to Residential property type only."""
    if "PropertyType" not in df.columns:
        raise KeyError("Column 'PropertyType' was not found in the dataset.")

    return df[df["PropertyType"] == "Residential"].copy()


def main():
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    listings, listing_files, listing_file_counts = read_and_combine_files("CRMLSListing*.csv")
    sold, sold_files, sold_file_counts = read_and_combine_files("CRMLSSold*.csv")

    listing_rows_before_filter = len(listings)
    sold_rows_before_filter = len(sold)

    listings_residential = filter_residential(listings)
    sold_residential = filter_residential(sold)

    listing_rows_after_filter = len(listings_residential)
    sold_rows_after_filter = len(sold_residential)

    listings_residential.to_csv(OUTPUT_FOLDER / "combined_listings_residential.csv", index=False)
    sold_residential.to_csv(OUTPUT_FOLDER / "combined_sold_residential.csv", index=False)

    counts_summary = pd.DataFrame([
        {
            "dataset": "listings",
            "files_combined": len(listing_files),
            "rows_before_residential_filter": listing_rows_before_filter,
            "rows_after_residential_filter": listing_rows_after_filter,
            "rows_removed_by_filter": listing_rows_before_filter - listing_rows_after_filter
        },
        {
            "dataset": "sold",
            "files_combined": len(sold_files),
            "rows_before_residential_filter": sold_rows_before_filter,
            "rows_after_residential_filter": sold_rows_after_filter,
            "rows_removed_by_filter": sold_rows_before_filter - sold_rows_after_filter
        }
    ])

    counts_summary.to_csv(OUTPUT_FOLDER / "week1_counts_summary.csv", index=False)
    listing_file_counts.to_csv(OUTPUT_FOLDER / "week1_listing_file_counts.csv", index=False)
    sold_file_counts.to_csv(OUTPUT_FOLDER / "week1_sold_file_counts.csv", index=False)

    print("Week 1 complete.")
    print()
    print("Listings:")
    print(f"  Files combined: {len(listing_files)}")
    print(f"  Rows before Residential filter: {listing_rows_before_filter}")
    print(f"  Rows after Residential filter: {listing_rows_after_filter}")
    print()
    print("Sold:")
    print(f"  Files combined: {len(sold_files)}")
    print(f"  Rows before Residential filter: {sold_rows_before_filter}")
    print(f"  Rows after Residential filter: {sold_rows_after_filter}")


if __name__ == "__main__":
    main()
