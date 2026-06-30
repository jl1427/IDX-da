# Week 0 Deliverable - MLS Data Pipeline Orientation

## Student Name
Michael Liu

## Objective
The goal of Week 0 is to understand how the IDX Exchange MLS datasets are produced from the CoreLogic Trestle API and exported into monthly CSV files for analysis.

## Completed Items

- [ ] Installed or confirmed Python environment.
- [ ] Installed or confirmed Tableau Public / Tableau Desktop Public Edition.
- [ ] Downloaded the monthly CSV files from the FTP location.
- [ ] Confirmed the required file prefixes:
  - `CRMLSListingYYYYMM.csv`
  - `CRMLSSoldYYYYMM.csv`
- [ ] Confirmed that both listing and sold files are available starting from January 2024.
- [ ] Reviewed the Trestle Property Metadata document.
- [ ] Checked that core fields are available in the datasets.

## Core Fields to Review

Important sold dataset fields:
- `CloseDate`
- `ClosePrice`
- `OriginalListPrice`
- `ListPrice`
- `LivingArea`
- `DaysOnMarket`
- `PropertyType`
- `PropertySubType`
- `CountyOrParish`
- `City`
- `PostalCode`

Important listing dataset fields:
- `ListingContractDate`
- `ListPrice`
- `OriginalListPrice`
- `LivingArea`
- `PropertyType`
- `PropertySubType`
- `CountyOrParish`
- `City`
- `PostalCode`

## Week 0 Notes

The datasets are confidential MLS transaction records and should only be used for internship work. The Week 0 work prepares the data environment for later analysis by making sure the monthly CSV files are downloaded, organized, and ready for aggregation.
