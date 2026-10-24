#!/usr/bin/env python
# coding: utf-8

# # Weeks 4–5: Data Cleaning and Preparation
# 
# ## Goal
# Prepare Residential MLS data for analysis by checking date formats, identifying inconsistent transaction timelines, and flagging invalid records.

# In[1]:


import pandas as pd
from pathlib import Path

# Load the Residential sold dataset
sold = pd.read_csv(
    "../output/sold_with_mortgage_rates.csv",
    low_memory=False
)

# Record original dataset size
original_rows = len(sold)
original_columns = len(sold.columns)

print("Original sold records:", original_rows)
print("Columns:", len(sold.columns))


# In[2]:


# Date columns required by the handbook
date_columns = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate"
]

# Convert dates into datetime format
for column in date_columns:
    sold[column] = pd.to_datetime(
        sold[column],
        errors="coerce"
    )

# Confirm data types
print(sold[date_columns].dtypes)


# In[3]:


# Flag listings dated after their closing date
sold["listing_after_close_flag"] = (
    sold["ListingContractDate"] > sold["CloseDate"]
)

# Flag purchase contracts dated after closing
sold["purchase_after_close_flag"] = (
    sold["PurchaseContractDate"] > sold["CloseDate"]
)

# Flag purchase contracts dated before the listing date
sold["negative_timeline_flag"] = (
    sold["PurchaseContractDate"] < sold["ListingContractDate"]
)

# Count records with each issue
print("Listing after closing:",
      sold["listing_after_close_flag"].sum())

print("Purchase contract after closing:",
      sold["purchase_after_close_flag"].sum())

print("Purchase contract before listing:",
      sold["negative_timeline_flag"].sum())

# Count records with at least one timeline issue
timeline_flags = [
    "listing_after_close_flag",
    "purchase_after_close_flag",
    "negative_timeline_flag"
]

total_flagged = sold[timeline_flags].any(axis=1).sum()

print("Total records with timeline issues:", total_flagged)

# Missing dates are not counted as timeline issues because
# comparisons with missing dates return False.
# These missing dates will be checked separately.


# In[4]:


#Checking all invalid numeric values(prices, living areas, days on market, bedrooms/bathrooms)


# Numeric columns we want to clean and check
numeric_columns = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket",
    "BedroomsTotal",
    "BathroomsTotalInteger"
]

# Convert these columns to numbers
# Any values that cannot be converted become missing (NaN)
for column in numeric_columns:
    sold[column] = pd.to_numeric(
        sold[column],
        errors="coerce"
    )

# Flag homes with a close price of zero or less
sold["invalid_price_flag"] = sold["ClosePrice"] <= 0

# Flag homes with a living area of zero or less
sold["invalid_living_area_flag"] = sold["LivingArea"] <= 0

# Flag negative days on market
sold["negative_dom_flag"] = sold["DaysOnMarket"] < 0

# Flag negative bedrooms or bathrooms
sold["negative_bedrooms_flag"] = sold["BedroomsTotal"] < 0
sold["negative_bathrooms_flag"] = sold["BathroomsTotalInteger"] < 0

# Store all numeric issue flags in one list
numeric_flags = [
    "invalid_price_flag",
    "invalid_living_area_flag",
    "negative_dom_flag",
    "negative_bedrooms_flag",
    "negative_bathrooms_flag"
]

# Count how many records have each issue
print("Invalid numeric values:")
print(sold[numeric_flags].sum())

# Count records with at least one numeric issue
total_numeric_flagged = sold[numeric_flags].any(axis=1).sum()

print("\nTotal records with numeric issues:", total_numeric_flagged)

# Confirm the numeric columns have the correct data types
print("\nNumeric data types:")
print(sold[numeric_columns].dtypes)


# In[5]:


#Checking for any missing values and unecessary columns 

# Calculate the percentage of missing values in each column
missing_percent = sold.isnull().mean() * 100

# Sort columns from most missing to least missing
missing_percent = missing_percent.sort_values(ascending=False)

# Show columns with more than 90% missing values
high_missing = missing_percent[missing_percent > 90]

print("Columns with over 90% missing values:")
print(high_missing)

# Important columns we want to keep for future analysis
important_columns = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "Latitude",
    "Longitude",
    "rate_30yr_fixed"
]

# Find highly missing columns that are not in our important list
columns_to_review = [
    column for column in high_missing.index
    if column not in important_columns
    and not column.endswith("_flag")
]

print("\nColumns to review for removal:")
print(columns_to_review)

# Check for duplicate column names
print("\nDuplicate column names:",
      sold.columns.duplicated().sum())




# In[6]:


#Checking for missing, zero, positive, or unrealistic California coordinates

# Convert latitude and longitude to numbers
coordinate_columns = ["Latitude", "Longitude"]

for column in coordinate_columns:
    sold[column] = pd.to_numeric(
        sold[column],
        errors="coerce"
    )

# Flag missing latitude or longitude
sold["missing_coordinates_flag"] = (
    sold["Latitude"].isna() |
    sold["Longitude"].isna()
)

# Flag coordinates recorded as zero
sold["zero_coordinates_flag"] = (
    (sold["Latitude"] == 0) |
    (sold["Longitude"] == 0)
)

# California longitudes should be negative
sold["positive_longitude_flag"] = sold["Longitude"] > 0

# Only check California boundaries when both coordinates exist
has_coords = (
    sold["Latitude"].notna() &
    sold["Longitude"].notna()
)

# Flag existing coordinates that fall outside California
sold["outside_california_flag"] = has_coords & (
    ~sold["Latitude"].between(32.5, 42.1) |
    ~sold["Longitude"].between(-124.5, -114.0)
)

# Store geographic flags in one list
geo_flags = [
    "missing_coordinates_flag",
    "zero_coordinates_flag",
    "positive_longitude_flag",
    "outside_california_flag"
]

# Count each geographic issue
print("Geographic data quality checks:")
print(sold[geo_flags].sum())

# Count records with at least one geographic issue
total_geo_flagged = sold[geo_flags].any(axis=1).sum()

print("\nTotal records with geographic issues:", total_geo_flagged)


# In[7]:


#Making a separate cleaned dataset so original sold Dataframe doesn't get touched 

# Create a copy of the dataset for cleaning
sold_clean = sold.copy()

# Replace invalid numeric values with missing values (NaN)
# This keeps the property record without using incorrect numbers
sold_clean.loc[
    sold_clean["invalid_price_flag"], "ClosePrice"
] = float("nan")

sold_clean.loc[
    sold_clean["invalid_living_area_flag"], "LivingArea"
] = float("nan")

sold_clean.loc[
    sold_clean["negative_dom_flag"], "DaysOnMarket"
] = float("nan")

sold_clean.loc[
    sold_clean["negative_bedrooms_flag"], "BedroomsTotal"
] = float("nan")

sold_clean.loc[
    sold_clean["negative_bathrooms_flag"], "BathroomsTotalInteger"
] = float("nan")

# Replace invalid coordinates with missing values
# Keep the original geographic flags so we know what was wrong
invalid_coordinates = sold[geo_flags].any(axis=1)

sold_clean.loc[
    invalid_coordinates, coordinate_columns
] = float("nan")

# Remove columns with over 90% missing values and Also remove any unnecessary index columns
# These columns have very little usable data and are not needed
# for the main analysis, so removing them simplifies the dataset
unnecessary_columns = columns_to_review + [
    column for column in sold_clean.columns
    if column.startswith("Unnamed:")
]

# Remove these columns from the cleaned dataset
sold_clean = sold_clean.drop(columns=unnecessary_columns)
print("Removed unnecessary columns:", unnecessary_columns)


# Check how many missing dates remain
print("\nMissing dates:")
print(sold_clean[date_columns].isnull().sum())

# Confirm the final row count
print("\nOriginal rows:", original_rows)
print("Cleaned rows:", len(sold_clean))



# In[8]:


#Validating and cleaning the cleaned dataset 

# Compare the number of rows before and after cleaning
print("Original rows:", original_rows)
print("Cleaned rows:", len(sold_clean))

# Compare the number of columns before and after cleaning
print("\nColumns before cleaning:", original_columns)
print("Columns after cleaning:", len(sold_clean.columns))

# Confirm that the date columns are datetime
print("\nDate column types:")
print(sold_clean[date_columns].dtypes)

# Confirm that the numeric columns are numeric
print("\nNumeric column types:")
print(sold_clean[numeric_columns].dtypes)

# Check that invalid numeric values were cleaned
print("\nInvalid numeric values remaining:")
print("Invalid prices:", (sold_clean["ClosePrice"] <= 0).sum())
print("Invalid living areas:", (sold_clean["LivingArea"] <= 0).sum())
print("Negative days on market:", (sold_clean["DaysOnMarket"] < 0).sum())
print("Negative bedrooms:", (sold_clean["BedroomsTotal"] < 0).sum())
print("Negative bathrooms:", (sold_clean["BathroomsTotalInteger"] < 0).sum())

# Show how many date inconsistencies were flagged
print("\nDate issue counts:")
print(sold_clean[timeline_flags].sum())

# Show how many geographic issues were flagged
print("\nGeographic issue counts:")
print(sold_clean[geo_flags].sum())

# Check missing values in important columns after cleaning
# Leave missing values as NaN rather than filling them in
# This avoids affecting averages and medians with estimated values
print("\nMissing values in important columns:")
print(sold_clean[important_columns].isnull().sum())

# Save the cleaned dataset as a new CSV
Path("../output").mkdir(exist_ok=True)

sold_clean.to_csv("../output/week4_5_cleaned_sold.csv", index=False)

print("\nCleaned dataset saved successfully!")


# 
# 
# ## Weeks 4–5: Data Cleaning Summary
# 
# ### Goal
# Clean the Residential sold dataset by checking dates, numeric values, missing data, and coordinates.
# 
# ### Findings
# - Cleaned **414,054 sold records** without removing any rows.
# - Found **507 records with date inconsistencies**.
# - Found **199 records with invalid numeric values**, mostly living area.
# - Found **4,195 records with geographic issues**, including 4,104 with missing coordinates.
# - Removed **15 columns with over 90% missing values**.
# - Replaced invalid numeric values and coordinates with NaN.
# 
# ### Notes
# - Kept flags for date and geographic issues instead of deleting records.
# - Left missing values as NaN rather than filling them in.
# - Some missing dates could not be checked for timeline issues.
# - Saved the cleaned dataset as `week4_5_cleaned_sold.csv`.
# 
