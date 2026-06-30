"""
IDX Exchange - Week 2 Deliverable Continued
Mortgage Rate Enrichment

This script:
1. Fetches the FRED MORTGAGE30US series.
2. Converts weekly mortgage rates into monthly averages.
3. Creates year_month join keys on sold and listings datasets.
4. Merges mortgage rates onto both datasets.
5. Saves enriched CSV files and validation output.
"""

from pathlib import Path
import pandas as pd


OUTPUT_FOLDER = Path("output")

SOLD_INPUT = OUTPUT_FOLDER / "sold_week2_filtered.csv"
LISTINGS_INPUT = OUTPUT_FOLDER / "listings_week2_filtered.csv"

SOLD_OUTPUT = OUTPUT_FOLDER / "sold_week2_with_mortgage_rates.csv"
LISTINGS_OUTPUT = OUTPUT_FOLDER / "listings_week2_with_mortgage_rates.csv"


def fetch_mortgage_rates():
    """Fetch FRED MORTGAGE30US and return monthly average rates."""
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"

    mortgage = pd.read_csv(url, parse_dates=["observation_date"])
    mortgage.columns = ["date", "rate_30yr_fixed"]

    mortgage["rate_30yr_fixed"] = pd.to_numeric(mortgage["rate_30yr_fixed"], errors="coerce")
    mortgage["year_month"] = mortgage["date"].dt.to_period("M").astype(str)

    mortgage_monthly = (
        mortgage
        .dropna(subset=["rate_30yr_fixed"])
        .groupby("year_month", as_index=False)["rate_30yr_fixed"]
        .mean()
    )

    return mortgage_monthly


def add_year_month(df, date_column):
    """Create year_month key from a date column."""
    if date_column not in df.columns:
        raise KeyError(f"Column '{date_column}' was not found.")

    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
    df["year_month"] = df[date_column].dt.to_period("M").astype(str)

    return df


def main():
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    sold = pd.read_csv(SOLD_INPUT, low_memory=False)
    listings = pd.read_csv(LISTINGS_INPUT, low_memory=False)

    mortgage_monthly = fetch_mortgage_rates()
    mortgage_monthly.to_csv(OUTPUT_FOLDER / "mortgage_rate_monthly.csv", index=False)

    sold = add_year_month(sold, "CloseDate")
    listings = add_year_month(listings, "ListingContractDate")

    sold_with_rates = sold.merge(mortgage_monthly, on="year_month", how="left")
    listings_with_rates = listings.merge(mortgage_monthly, on="year_month", how="left")

    sold_null_rates = sold_with_rates["rate_30yr_fixed"].isna().sum()
    listings_null_rates = listings_with_rates["rate_30yr_fixed"].isna().sum()

    sold_with_rates.to_csv(SOLD_OUTPUT, index=False)
    listings_with_rates.to_csv(LISTINGS_OUTPUT, index=False)

    validation_text = f"""Week 2 Mortgage Rate Merge Validation

Sold dataset:
Rows: {len(sold_with_rates)}
Null mortgage rate rows: {sold_null_rates}

Listings dataset:
Rows: {len(listings_with_rates)}
Null mortgage rate rows: {listings_null_rates}

Validation note:
The deliverable asks to confirm no null mortgage rate values after the merge.
If null rows appear, check that CloseDate and ListingContractDate are valid and that the transaction month exists in the FRED mortgage rate series.
"""

    (OUTPUT_FOLDER / "week2_mortgage_validation.txt").write_text(validation_text, encoding="utf-8")

    print("Week 2 mortgage enrichment complete.")
    print(f"Sold null mortgage rates: {sold_null_rates}")
    print(f"Listings null mortgage rates: {listings_null_rates}")


if __name__ == "__main__":
    main()
