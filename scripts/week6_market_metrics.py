#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from pathlib import Path

# Load the cleaned Residential sold dataset from Weeks 4-5
sold = pd.read_csv(
    "../output/week4_5_cleaned_sold.csv",
    low_memory=False
)

print("Total records:", len(sold))
print("Total columns:", len(sold.columns))


# In[2]:


# Columns needed to calculate Week 6 market metrics
required_columns = [
    "ClosePrice",
    "OriginalListPrice",
    "LivingArea",
    "DaysOnMarket",
    "CloseDate",
    "ListingContractDate",
    "PurchaseContractDate",
    "PropertyType",
    "PropertySubType",
    "CountyOrParish",
    "MLSAreaMajor",
    "ListOfficeName",
    "BuyerOfficeName",
    "Latitude",
    "Longitude"
]

# Check which columns are available
missing_columns = [
    column for column in required_columns
    if column not in sold.columns
]

print("Missing required columns:", missing_columns)

# Check missing values in the available columns
available_columns = [
    column for column in required_columns
    if column in sold.columns
]

print("\nMissing values:")
print(sold[available_columns].isna().sum())


# In[3]:


# Check the data types before creating new metrics
print(sold[available_columns].dtypes)


# In[4]:


# Convert date columns back to datetime after loading the CSV
date_columns = [
    "CloseDate",
    "ListingContractDate",
    "PurchaseContractDate"
]

for column in date_columns:
    sold[column] = pd.to_datetime(
        sold[column],
        errors="coerce"
    )

# Make sure the numeric columns are numeric
numeric_columns = [
    "ClosePrice",
    "OriginalListPrice",
    "LivingArea",
    "DaysOnMarket"
]

for column in numeric_columns:
    sold[column] = pd.to_numeric(
        sold[column],
        errors="coerce"
    )

print("Date column types:")
print(sold[date_columns].dtypes)

print("\nNumeric column types:")
print(sold[numeric_columns].dtypes)


# In[5]:


# Create a separate dataset for Week 6
sold_metrics = sold.copy()

# Avoid dividing by zero or negative values
valid_list_price = sold_metrics["OriginalListPrice"] > 0
valid_living_area = sold_metrics["LivingArea"] > 0
valid_close_price = sold_metrics["ClosePrice"] > 0

# Calculate the selling price compared to the original list price
sold_metrics["PriceRatio"] = (
    sold_metrics["ClosePrice"] /
    sold_metrics["OriginalListPrice"].where(valid_list_price)
).where(valid_close_price)

# Same formula, kept as a separate column because the handbook requests both
sold_metrics["CloseToOriginalListRatio"] = sold_metrics["PriceRatio"]

# Calculate price per square foot
sold_metrics["PricePerSqFt"] = (
    sold_metrics["ClosePrice"] /
    sold_metrics["LivingArea"].where(valid_living_area)
).where(valid_close_price)

# Keep the existing DaysOnMarket field
# No new calculation is needed for this metric

# Create year, month, and year-month fields from the closing date
sold_metrics["Year"] = sold_metrics["CloseDate"].dt.year
sold_metrics["Month"] = sold_metrics["CloseDate"].dt.month
sold_metrics["YrMo"] = sold_metrics["CloseDate"].dt.strftime("%Y-%m")

# Calculate days between listing and purchase contract
sold_metrics["ListingToContractDays"] = (
    sold_metrics["PurchaseContractDate"] -
    sold_metrics["ListingContractDate"]
).dt.days

# Calculate days between purchase contract and closing
sold_metrics["ContractToCloseDays"] = (
    sold_metrics["CloseDate"] -
    sold_metrics["PurchaseContractDate"]
).dt.days

# Check how many values could be calculated
new_metrics = [
    "PriceRatio",
    "CloseToOriginalListRatio",
    "PricePerSqFt",
    "DaysOnMarket",
    "Year",
    "Month",
    "YrMo",
    "ListingToContractDays",
    "ContractToCloseDays"
]

print("Missing values in Week 6 metrics:")
print(sold_metrics[new_metrics].isna().sum())

print("\nNegative timeline values:")
print("Listing to contract:", (sold_metrics["ListingToContractDays"] < 0).sum())
print("Contract to close:", (sold_metrics["ContractToCloseDays"] < 0).sum())

print("\nMedian market metrics:")
print(
    sold_metrics[
        ["PriceRatio", "PricePerSqFt",
         "ListingToContractDays", "ContractToCloseDays"]
    ].median()
)


# In[6]:


# Keep negative timeline values out of market calculations
# The original date columns and issue flags are still preserved

sold_metrics.loc[
    sold_metrics["ListingToContractDays"] < 0,
    "ListingToContractDays"
] = np.nan

sold_metrics.loc[
    sold_metrics["ContractToCloseDays"] < 0,
    "ContractToCloseDays"
] = np.nan

# Check the results after cleaning
print("Negative listing-to-contract days:",
      (sold_metrics["ListingToContractDays"] < 0).sum())

print("Negative contract-to-close days:",
      (sold_metrics["ContractToCloseDays"] < 0).sum())

print("\nUpdated median durations:")
print(
    sold_metrics[
        ["ListingToContractDays", "ContractToCloseDays"]
    ].median()
)


# In[7]:


# Show a small sample of the engineered market metrics
sample_columns = [
    "PriceRatio",
    "CloseToOriginalListRatio",
    "PricePerSqFt",
    "DaysOnMarket",
    "Year",
    "Month",
    "YrMo",
    "ListingToContractDays",
    "ContractToCloseDays"
]

# Show five records where all new metrics are available
sample_metrics = sold_metrics[sample_columns].dropna().head(5)

print("Sample Week 6 market metrics:")
print(sample_metrics.to_string(index=False))


# In[8]:


# Summarize market metrics by property type
property_summary = (
    sold_metrics
    .groupby(["PropertyType", "PropertySubType"], dropna=False)
    .agg(
        SoldRecords=("ClosePrice", "size"),
        MedianClosePrice=("ClosePrice", "median"),
        MedianPriceRatio=("PriceRatio", "median"),
        MedianPricePerSqFt=("PricePerSqFt", "median"),
        MedianDaysOnMarket=("DaysOnMarket", "median"),
        MedianListingToContractDays=("ListingToContractDays", "median")
    )
    .reset_index()
    .sort_values("SoldRecords", ascending=False)
)

print("Property type summary:")
print(property_summary.head(10).to_string(index=False))

# Summarize market metrics by county and MLS area
county_summary = (
    sold_metrics
    .groupby(["CountyOrParish", "MLSAreaMajor"], dropna=False)
    .agg(
        SoldRecords=("ClosePrice", "size"),
        MedianClosePrice=("ClosePrice", "median"),
        MedianPriceRatio=("PriceRatio", "median"),
        MedianDaysOnMarket=("DaysOnMarket", "median")
    )
    .reset_index()
    .sort_values("SoldRecords", ascending=False)
)

print("\nCounty and MLS area summary:")
print(county_summary.head(10).to_string(index=False))


# In[9]:


# Compare listing offices
listing_office_summary = (
    sold_metrics
    .groupby("ListOfficeName", dropna=False)
    .agg(
        SoldRecords=("ClosePrice", "size"),
        TotalSalesVolume=("ClosePrice", "sum"),
        MedianClosePrice=("ClosePrice", "median"),
        MedianPriceRatio=("PriceRatio", "median")
    )
    .reset_index()
    .sort_values("TotalSalesVolume", ascending=False)
)

# Compare buyer offices
buyer_office_summary = (
    sold_metrics
    .groupby("BuyerOfficeName", dropna=False)
    .agg(
        SoldRecords=("ClosePrice", "size"),
        TotalSalesVolume=("ClosePrice", "sum"),
        MedianClosePrice=("ClosePrice", "median"),
        MedianPriceRatio=("PriceRatio", "median")
    )
    .reset_index()
    .sort_values("TotalSalesVolume", ascending=False)
)

print("Listing office summary:")
print(listing_office_summary.head(10).to_string(index=False))

print("\nBuyer office summary:")
print(buyer_office_summary.head(10).to_string(index=False))


# In[11]:


import geopandas as gpd

# Load California school district boundaries
districts = gpd.read_file(
    "../data/school_districts/DistrictAreas2425.shp"
)

# Check the number of districts and their coordinate system
print("Total district boundaries:", len(districts))
print("Coordinate system:", districts.crs)

# Check the available columns
print("\nDistrict columns:")
print(districts.columns.tolist())

# Preview district information without showing boundary coordinates
print("\nSample district information:")
print(districts.drop(columns="geometry").head(5).to_string(index=False))

# Check for invalid or empty boundary shapes
print("\nMissing geometries:", districts.geometry.isna().sum())
print("Empty geometries:", districts.geometry.is_empty.sum())


# In[12]:


# Only use properties with valid coordinates
valid_coords = (
    sold_metrics["Latitude"].notna() &
    sold_metrics["Longitude"].notna() &
    sold_metrics["Latitude"].between(32.5, 42.1) &
    sold_metrics["Longitude"].between(-124.5, -114.0)
)

# Create a smaller dataset for the geographic matching
property_locations = sold_metrics.loc[
    valid_coords, ["Latitude", "Longitude"]
].copy()

# Convert coordinates into geographic points
property_points = gpd.GeoDataFrame(
    property_locations,
    geometry=gpd.points_from_xy(
        property_locations["Longitude"],
        property_locations["Latitude"]
    ),
    crs="EPSG:4326"
)

# Convert property points to the same coordinate system as the districts
property_points = property_points.to_crs(districts.crs)

print("Total properties:", len(sold_metrics))
print("Properties with valid coordinates:", len(property_points))
print("Properties without usable coordinates:", (~valid_coords).sum())
print("Coordinate system:", property_points.crs)


# In[13]:


# Keep only the school district information we need
district_boundaries = districts[
    ["DistrictNa", "DistrictTy", "CDSCode", "geometry"]
].copy()

# Match each property point to the district boundary containing it
district_matches = gpd.sjoin(
    property_points,
    district_boundaries,
    how="left",
    predicate="within"
)

print("Property points before matching:", len(property_points))
print("Rows after spatial join:", len(district_matches))
print("Properties with a district match:",
      district_matches["DistrictNa"].notna().sum())

print("\nDistrict types in the matches:")
print(district_matches["DistrictTy"].value_counts(dropna=False))


# In[14]:


# Keep the property index so we can match districts back correctly
district_matches = district_matches.reset_index().rename(
    columns={"index": "property_index"}
)

# Keep only matched districts
matched_districts = district_matches.dropna(
    subset=["DistrictNa"]
).copy()

# Create one column for each school district type
district_table = (
    matched_districts
    .groupby(["property_index", "DistrictTy"])["DistrictNa"]
    .agg(lambda names: " | ".join(sorted(set(names))))
    .unstack()
)

# Rename columns for easier use
district_table = district_table.rename(columns={
    "Unified": "UnifiedDistrict",
    "Elementary": "ElementaryDistrict",
    "High": "HighSchoolDistrict"
})

print("Properties with district matches:", len(district_table))
print("\nDistrict columns:")
print(district_table.columns.tolist())

print("\nProperties matched by district type:")
print(district_table.notna().sum())


# In[16]:


# School district columns
district_columns = [
    "UnifiedDistrict",
    "ElementaryDistrict",
    "HighSchoolDistrict"
]

# Remove previously joined district columns if the cell was run before
sold_metrics = sold_metrics.drop(
    columns=district_columns,
    errors="ignore"
)

# Attach school district information to the full dataset
sold_metrics = sold_metrics.join(
    district_table,
    how="left",
    validate="one_to_one"
)

# Check that no property records were duplicated
print("Original records:", len(sold))
print("Week 6 records:", len(sold_metrics))

# Check how many properties have at least one district
has_district = sold_metrics[district_columns].notna().any(axis=1)

print("Properties with at least one district:", has_district.sum())
print("Properties without a district:", (~has_district).sum())

# Show a few school district assignments
print("\nSample district assignments:")
print(
    sold_metrics[district_columns]
    .dropna(how="all")
    .head(10)
    .to_string(index=False)
)


# In[17]:


# Check the final dataset before saving

print("Original rows:", len(sold))
print("Final Week 6 rows:", len(sold_metrics))

# Check for duplicate column names
print("\nDuplicate column names:",
      sold_metrics.columns.duplicated().sum())

# Check missing values in new market metrics
print("\nMissing values in market metrics:")
print(sold_metrics[new_metrics].isna().sum())

# Check negative timeline values
print("\nNegative timeline values:")
print("Listing to contract:",
      (sold_metrics["ListingToContractDays"] < 0).sum())
print("Contract to close:",
      (sold_metrics["ContractToCloseDays"] < 0).sum())

# Check school district coverage
print("\nSchool district coverage:")
print("Matched:", has_district.sum())
print("Unmatched:", (~has_district).sum())

# Confirm the original number of records was preserved
assert len(sold_metrics) == len(sold), "Row count changed!"
assert sold_metrics.columns.is_unique, "Duplicate column names found!"

print("\nWeek 6 validation passed!")


# In[18]:


# Save the final Week 6 dataset
output_path = Path("../output/week6_market_metrics.csv")

sold_metrics.to_csv(output_path, index=False)

# Confirm the file was saved
print("Week 6 dataset saved:", output_path)
print("Total records:", len(sold_metrics))
print("Total columns:", len(sold_metrics.columns))


# ## Week 6: Market Metrics and School District Matching
# 
# ### Goal
# Create new market metrics and match residential properties to California school districts for future analysis.
# 
# ### Findings
# - Created market metrics including price ratio, price per square foot, and transaction timelines.
# - The median price ratio was **99.57%**, and the median price per square foot was **$537.48**.
# - Properties had a median of **25 days from listing to contract** and **29 days from contract to closing**.
# - Matched **409,739 properties** to school districts using their coordinates.
# - Found **4,315 properties without a district match**, mostly because of missing or invalid coordinates.
# - Kept all **414,054 records** without creating duplicates.
# 
# ### Notes
# - Replaced negative timeline values with NaN so they would not affect the analysis.
# - Kept separate columns for unified, elementary, and high school districts.
# - Left missing values as NaN rather than filling them in.
