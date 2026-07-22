import pandas as pd


SOLD_FILE = "week4_cleaned_sold_analysis_ready.csv"
LISTINGS_FILE = "week4_cleaned_listings_analysis_ready.csv"

FINAL_SOLD_FILE = "week5_final_cleaned_sold_analysis_ready.csv"
FINAL_LISTINGS_FILE = "week5_final_cleaned_listings_analysis_ready.csv"

ROW_COUNT_REPORT_FILE = "week5_before_after_row_counts.csv"
MISSING_CORE_FIELDS_REPORT_FILE = "week5_core_field_missing_summary.csv"
DUPLICATE_REPORT_FILE = "week5_duplicate_record_summary.csv"
FINAL_DTYPE_REPORT_FILE = "week5_final_data_type_confirmation.csv"


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

CORE_SOLD_FIELDS = [
    "CloseDate",
    "ClosePrice",
    "OriginalListPrice",
    "LivingArea",
    "DaysOnMarket",
    "CountyOrParish",
    "City",
    "PostalCode"
]

CORE_LISTING_FIELDS = [
    "ListingContractDate",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "DaysOnMarket",
    "CountyOrParish",
    "City",
    "PostalCode"
]


def load_data():
    sold = pd.read_csv(SOLD_FILE, low_memory=False)
    listings = pd.read_csv(LISTINGS_FILE, low_memory=False)

    print("Loaded Week 4 sold dataset:", sold.shape)
    print("Loaded Week 4 listings dataset:", listings.shape)

    return sold, listings


def reconvert_dates_and_numbers(df, dataset_name):
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    print(f"{dataset_name}: date and numeric columns confirmed.")
    return df


def clean_string_columns(df, dataset_name):
    object_columns = df.select_dtypes(include=["object"]).columns

    for col in object_columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": pd.NA, "None": pd.NA, "": pd.NA})

    print(f"{dataset_name}: text columns stripped and blank strings converted to missing values.")
    return df


def remove_duplicates(df, dataset_name):
    before_rows = len(df)

    possible_id_columns = [
        "ListingKey",
        "ListingId",
        "ListingID",
        "PropertyID",
        "PropertyId"
    ]

    id_column = None
    for col in possible_id_columns:
        if col in df.columns:
            id_column = col
            break

    if id_column:
        duplicate_count = df.duplicated(subset=[id_column]).sum()
        cleaned = df.drop_duplicates(subset=[id_column]).copy()
        duplicate_basis = id_column
    else:
        duplicate_count = df.duplicated().sum()
        cleaned = df.drop_duplicates().copy()
        duplicate_basis = "full row"

    after_rows = len(cleaned)

    print(f"\n{dataset_name} duplicate check:")
    print("Duplicate basis:", duplicate_basis)
    print("Rows before duplicate removal:", before_rows)
    print("Duplicate rows found:", duplicate_count)
    print("Rows after duplicate removal:", after_rows)

    return cleaned, before_rows, after_rows, duplicate_count, duplicate_basis


def add_core_missing_flags(df, dataset_name, core_fields):
    for col in core_fields:
        if col in df.columns:
            flag_col = f"missing_{col}_flag"
            df[flag_col] = df[col].isna()

    print(f"{dataset_name}: core missing-value flags created.")
    return df


def create_missing_core_report(sold, listings):
    rows = []

    for dataset_name, df, fields in [
        ("sold", sold, CORE_SOLD_FIELDS),
        ("listings", listings, CORE_LISTING_FIELDS)
    ]:
        for col in fields:
            if col in df.columns:
                rows.append({
                    "dataset": dataset_name,
                    "column": col,
                    "missing_count": int(df[col].isna().sum()),
                    "missing_percent": round(df[col].isna().mean() * 100, 2)
                })

    report = pd.DataFrame(rows)
    report.to_csv(MISSING_CORE_FIELDS_REPORT_FILE, index=False)

    print("Core field missing summary saved to:", MISSING_CORE_FIELDS_REPORT_FILE)


def create_dtype_report(sold, listings):
    rows = []

    for dataset_name, df in [("sold", sold), ("listings", listings)]:
        for col in DATE_COLUMNS + NUMERIC_COLUMNS:
            if col in df.columns:
                rows.append({
                    "dataset": dataset_name,
                    "column": col,
                    "final_dtype": str(df[col].dtype)
                })

    report = pd.DataFrame(rows)
    report.to_csv(FINAL_DTYPE_REPORT_FILE, index=False)

    print("Final data type confirmation saved to:", FINAL_DTYPE_REPORT_FILE)


def create_row_count_and_duplicate_reports(
    sold_before,
    sold_after,
    listings_before,
    listings_after,
    sold_duplicate_count,
    listings_duplicate_count,
    sold_duplicate_basis,
    listings_duplicate_basis
):
    row_report = pd.DataFrame([
        {
            "dataset": "sold",
            "rows_before_week5_cleaning": sold_before,
            "rows_after_week5_cleaning": sold_after,
            "rows_removed": sold_before - sold_after
        },
        {
            "dataset": "listings",
            "rows_before_week5_cleaning": listings_before,
            "rows_after_week5_cleaning": listings_after,
            "rows_removed": listings_before - listings_after
        }
    ])

    row_report.to_csv(ROW_COUNT_REPORT_FILE, index=False)

    duplicate_report = pd.DataFrame([
        {
            "dataset": "sold",
            "duplicate_basis": sold_duplicate_basis,
            "duplicate_records_found": sold_duplicate_count
        },
        {
            "dataset": "listings",
            "duplicate_basis": listings_duplicate_basis,
            "duplicate_records_found": listings_duplicate_count
        }
    ])

    duplicate_report.to_csv(DUPLICATE_REPORT_FILE, index=False)

    print("Before/after row count report saved to:", ROW_COUNT_REPORT_FILE)
    print("Duplicate record summary saved to:", DUPLICATE_REPORT_FILE)


def prepare_dataset(df, dataset_name, core_fields):
    df = reconvert_dates_and_numbers(df, dataset_name)
    df = clean_string_columns(df, dataset_name)

    df, before_rows, after_rows, duplicate_count, duplicate_basis = remove_duplicates(
        df,
        dataset_name
    )

    df = add_core_missing_flags(df, dataset_name, core_fields)

    return df, before_rows, after_rows, duplicate_count, duplicate_basis


def main():
    sold, listings = load_data()

    sold_final, sold_before, sold_after, sold_dup_count, sold_dup_basis = prepare_dataset(
        sold,
        "Sold",
        CORE_SOLD_FIELDS
    )

    listings_final, listings_before, listings_after, listings_dup_count, listings_dup_basis = prepare_dataset(
        listings,
        "Listings",
        CORE_LISTING_FIELDS
    )

    sold_final.to_csv(FINAL_SOLD_FILE, index=False)
    listings_final.to_csv(FINAL_LISTINGS_FILE, index=False)

    create_missing_core_report(sold_final, listings_final)
    create_dtype_report(sold_final, listings_final)

    create_row_count_and_duplicate_reports(
        sold_before,
        sold_after,
        listings_before,
        listings_after,
        sold_dup_count,
        listings_dup_count,
        sold_dup_basis,
        listings_dup_basis
    )

    print("\nFinal Week 5 sold dataset saved to:", FINAL_SOLD_FILE)
    print("Final Week 5 listings dataset saved to:", FINAL_LISTINGS_FILE)
    print("\nWeek 5 deliverable completed successfully.")


if __name__ == "__main__":
    main()
