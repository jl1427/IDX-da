import pandas as pd
import numpy as np



INPUT_FILE = "week6_sold_feature_engineered.csv"

FULL_FLAGGED_FILE = "week7_full_flagged_sold_dataset.csv"
FILTERED_CLEAN_FILE = "week7_clean_filtered_sold_dataset.csv"

OUTLIER_BOUNDS_FILE = "week7_iqr_outlier_bounds.csv"
COMPARISON_REPORT_FILE = "week7_before_after_filtering_comparison.csv"
OUTLIER_COUNT_REPORT_FILE = "week7_outlier_flag_counts.csv"


OUTLIER_COLUMNS = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket"
]


def load_data():
    df = pd.read_csv(INPUT_FILE, low_memory=False)

    print("Loaded Week 6 sold feature-engineered dataset:", df.shape)

    return df


def convert_numeric_columns(df):
    for col in OUTLIER_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            print(f"Converted {col} to numeric.")
        else:
            print(f"{col} not found.")

    if "price_per_sqft" in df.columns:
        df["price_per_sqft"] = pd.to_numeric(df["price_per_sqft"], errors="coerce")

    if "close_to_original_list_ratio" in df.columns:
        df["close_to_original_list_ratio"] = pd.to_numeric(
            df["close_to_original_list_ratio"],
            errors="coerce"
        )

    return df


def calculate_iqr_bounds(df, column):
    values = df[column].dropna()

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    return q1, q3, iqr, lower_bound, upper_bound


def add_iqr_outlier_flags(df):
    bounds_rows = []

    for col in OUTLIER_COLUMNS:
        if col not in df.columns:
            print(f"{col} not found. Skipping IQR flag.")
            continue

        q1, q3, iqr, lower_bound, upper_bound = calculate_iqr_bounds(df, col)

        flag_col = f"{col}_iqr_outlier_flag"

        df[flag_col] = (
            (df[col] < lower_bound) |
            (df[col] > upper_bound)
        )

        bounds_rows.append({
            "column": col,
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "outlier_count": int(df[flag_col].sum()),
            "outlier_percent": round(df[flag_col].mean() * 100, 2)
        })

        print(f"\n{col} IQR bounds:")
        print("Q1:", q1)
        print("Q3:", q3)
        print("IQR:", iqr)
        print("Lower bound:", lower_bound)
        print("Upper bound:", upper_bound)
        print("Outlier count:", int(df[flag_col].sum()))

    bounds_report = pd.DataFrame(bounds_rows)
    bounds_report.to_csv(OUTLIER_BOUNDS_FILE, index=False)

    print("\nIQR outlier bounds saved to:", OUTLIER_BOUNDS_FILE)

    return df


def add_business_rule_flags(df):
    if "ClosePrice" in df.columns:
        df["invalid_close_price_business_rule_flag"] = df["ClosePrice"] <= 0
    else:
        df["invalid_close_price_business_rule_flag"] = False

    if "LivingArea" in df.columns:
        df["invalid_living_area_business_rule_flag"] = df["LivingArea"] <= 0
    else:
        df["invalid_living_area_business_rule_flag"] = False

    if "DaysOnMarket" in df.columns:
        df["invalid_days_on_market_business_rule_flag"] = df["DaysOnMarket"] < 0
    else:
        df["invalid_days_on_market_business_rule_flag"] = False

    df["any_business_rule_invalid_flag"] = (
        df["invalid_close_price_business_rule_flag"] |
        df["invalid_living_area_business_rule_flag"] |
        df["invalid_days_on_market_business_rule_flag"]
    )

    print("\nBusiness rule invalid counts:")
    print("Invalid ClosePrice:", int(df["invalid_close_price_business_rule_flag"].sum()))
    print("Invalid LivingArea:", int(df["invalid_living_area_business_rule_flag"].sum()))
    print("Invalid DaysOnMarket:", int(df["invalid_days_on_market_business_rule_flag"].sum()))
    print("Any business rule invalid:", int(df["any_business_rule_invalid_flag"].sum()))

    return df


def create_combined_outlier_flag(df):
    outlier_flag_columns = [
        f"{col}_iqr_outlier_flag"
        for col in OUTLIER_COLUMNS
        if f"{col}_iqr_outlier_flag" in df.columns
    ]

    if outlier_flag_columns:
        df["any_iqr_outlier_flag"] = df[outlier_flag_columns].any(axis=1)
    else:
        df["any_iqr_outlier_flag"] = False

    df["remove_from_filtered_analysis_flag"] = (
        df["any_iqr_outlier_flag"] |
        df["any_business_rule_invalid_flag"]
    )

    print("\nCombined outlier flag counts:")
    print("Any IQR outlier:", int(df["any_iqr_outlier_flag"].sum()))
    print("Remove from filtered analysis:", int(df["remove_from_filtered_analysis_flag"].sum()))

    return df


def create_filtered_dataset(df):
    filtered = df[df["remove_from_filtered_analysis_flag"] == False].copy()

    print("\nFiltering summary:")
    print("Rows before filtering:", len(df))
    print("Rows after filtering:", len(filtered))
    print("Rows removed:", len(df) - len(filtered))

    return filtered


def create_comparison_report(df_before, df_after):
    rows = []

    metrics = [
        "ClosePrice",
        "LivingArea",
        "DaysOnMarket",
        "price_per_sqft",
        "close_to_original_list_ratio"
    ]

    for col in metrics:
        if col in df_before.columns:
            before_median = df_before[col].median()
            after_median = df_after[col].median()

            rows.append({
                "metric": col,
                "before_count": int(df_before[col].count()),
                "after_count": int(df_after[col].count()),
                "before_median": before_median,
                "after_median": after_median,
                "median_change": after_median - before_median
            })

    row_summary = pd.DataFrame([
        {
            "metric": "row_count",
            "before_count": len(df_before),
            "after_count": len(df_after),
            "before_median": np.nan,
            "after_median": np.nan,
            "median_change": np.nan
        }
    ])

    comparison = pd.concat([row_summary, pd.DataFrame(rows)], ignore_index=True)
    comparison.to_csv(COMPARISON_REPORT_FILE, index=False)

    print("Before/after filtering comparison saved to:", COMPARISON_REPORT_FILE)


def create_outlier_count_report(df):
    flag_columns = [
        "ClosePrice_iqr_outlier_flag",
        "LivingArea_iqr_outlier_flag",
        "DaysOnMarket_iqr_outlier_flag",
        "invalid_close_price_business_rule_flag",
        "invalid_living_area_business_rule_flag",
        "invalid_days_on_market_business_rule_flag",
        "any_iqr_outlier_flag",
        "any_business_rule_invalid_flag",
        "remove_from_filtered_analysis_flag"
    ]

    rows = []

    for col in flag_columns:
        if col in df.columns:
            rows.append({
                "flag": col,
                "count": int(df[col].sum()),
                "percent": round(df[col].mean() * 100, 2)
            })

    report = pd.DataFrame(rows)
    report.to_csv(OUTLIER_COUNT_REPORT_FILE, index=False)

    print("Outlier flag count report saved to:", OUTLIER_COUNT_REPORT_FILE)


def main():
    df = load_data()

    df = convert_numeric_columns(df)

    df = add_iqr_outlier_flags(df)
    df = add_business_rule_flags(df)
    df = create_combined_outlier_flag(df)

    filtered = create_filtered_dataset(df)

    df.to_csv(FULL_FLAGGED_FILE, index=False)
    filtered.to_csv(FILTERED_CLEAN_FILE, index=False)

    create_comparison_report(df, filtered)
    create_outlier_count_report(df)

    print("\nFull flagged dataset saved to:", FULL_FLAGGED_FILE)
    print("Clean filtered dataset saved to:", FILTERED_CLEAN_FILE)
    print("\nWeek 7 deliverable completed successfully.")


if __name__ == "__main__":
    main()
