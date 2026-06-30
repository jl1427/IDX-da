# IDX Exchange Week 0-2 Deliverables

This package is for the IDX Exchange MLS Analytics internship Week 0-2 work.

## Folder setup

Put all monthly CSV files in one folder named:

```text
csv/
```

The scripts expect files like:

```text
CRMLSListing202401.csv
CRMLSListing202402.csv
CRMLSSold202401.csv
CRMLSSold202402.csv
```

## Deliverables included

### Week 0
- `week0_checklist.md`
- Use this to confirm you downloaded the CRMLSListing and CRMLSSold CSV files and reviewed the metadata.

### Week 1
- `week1_concat_residential.py`
- Combines all monthly listing files into one listings dataset.
- Combines all monthly sold files into one sold dataset.
- Filters both datasets to `PropertyType == "Residential"`.
- Saves:
  - `output/combined_listings_residential.csv`
  - `output/combined_sold_residential.csv`
  - `output/week1_counts_summary.csv`

### Week 2
- `week2_structuring_validation.py`
- Documents property types, null counts, columns above 90% null, and numeric summaries.
- Saves:
  - `output/week2_sold_unique_property_types.csv`
  - `output/week2_listings_unique_property_types.csv`
  - `output/week2_sold_null_report.csv`
  - `output/week2_listings_null_report.csv`
  - `output/week2_sold_high_missing_columns.csv`
  - `output/week2_listings_high_missing_columns.csv`
  - `output/week2_sold_numeric_summary.csv`
  - `output/week2_listings_numeric_summary.csv`
  - `output/sold_week2_filtered.csv`
  - `output/listings_week2_filtered.csv`

### Week 2 mortgage enrichment
- `week2_mortgage_enrichment.py`
- Fetches FRED `MORTGAGE30US`.
- Converts weekly mortgage rates to monthly averages.
- Merges mortgage rates onto sold and listings datasets.
- Saves:
  - `output/sold_week2_with_mortgage_rates.csv`
  - `output/listings_week2_with_mortgage_rates.csv`
  - `output/mortgage_rate_monthly.csv`
  - `output/week2_mortgage_validation.txt`

## How to run

From this folder:

```bash
python week1_concat_residential.py
python week2_structuring_validation.py
python week2_mortgage_enrichment.py
```

If your CSV folder is in a different place, edit the `CSV_FOLDER` variable at the top of each script.
