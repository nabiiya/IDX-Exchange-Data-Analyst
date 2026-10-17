#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load Week 1 datasets
sold = pd.read_csv("../output/combined_sold_residential.csv", low_memory=False)
listings = pd.read_csv("../output/combined_listings_residential.csv", low_memory=False)

# Check dataset size and structure
print("Sold:", sold.shape)
print("Listings:", listings.shape)

sold.info()
print(sold.columns.tolist())


# In[2]:


# Confirm Residential filtering
print("Sold property types:", sold["PropertyType"].unique())
print("Listing property types:", listings["PropertyType"].unique())

# Create missing value reports
sold_missing = pd.DataFrame({
    "Missing Count": sold.isnull().sum(),
    "Missing Percent": sold.isnull().mean() * 100
})

listing_missing = pd.DataFrame({
    "Missing Count": listings.isnull().sum(),
    "Missing Percent": listings.isnull().mean() * 100
})

# Sort by missing percentage
sold_missing = sold_missing.sort_values("Missing Percent", ascending=False)
listing_missing = listing_missing.sort_values("Missing Percent", ascending=False)

print("Sold missing values:")
print(sold_missing.head(20))

print("Listing missing values:")
print(listing_missing.head(20))


# In[3]:


# Find columns with more than 90% missing values
sold_high_missing = sold_missing[sold_missing["Missing Percent"] > 90]
listing_high_missing = listing_missing[listing_missing["Missing Percent"] > 90]

print("Sold columns above 90% missing:")
print(sold_high_missing)

print("Listing columns above 90% missing:")
print(listing_high_missing)


# In[4]:


# Key numeric fields
numeric_columns = ["ClosePrice", "LivingArea", "DaysOnMarket"]

# Convert to numeric
for column in numeric_columns:
    sold[column] = pd.to_numeric(sold[column], errors="coerce")

# Calculate summary statistics
numeric_summary = sold[numeric_columns].describe(
    percentiles=[0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
)

print(numeric_summary)


# In[ ]:


# Save reports
Path("../reports").mkdir(exist_ok=True)

sold_missing.to_csv("../reports/sold_missing_report.csv")
listing_missing.to_csv("../reports/listings_missing_report.csv")
numeric_summary.to_csv("../reports/numeric_summary.csv")

print("Week 2 initial analysis saved!")


# ## Additional Numeric Distribution Review
# 
# Review all nine housing metrics to identify unusual values and potential data quality issues.

# In[6]:


#loking at spread of prices, bedrooms, home sizes, and other housing metrics to find unusual records


# Nine numeric fields required by the handbook
market_fields = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt"
]

# Convert fields to numeric values
for column in market_fields:
    sold[column] = pd.to_numeric(sold[column], errors="coerce")

# Calculate summary statistics
market_summary = sold[market_fields].describe(
    percentiles=[0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
)

display(market_summary)

# Create histograms and boxplots
for column in market_fields:
    values = sold[column].dropna()

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    axes[0].hist(values, bins=50)
    axes[0].set_title(column + " Distribution")
    axes[0].set_xlabel(column)

    axes[1].boxplot(values)
    axes[1].set_title(column + " Boxplot")

    plt.tight_layout()
    plt.show()


# ## Data Quality Checks
# 
# Identify potential outliers and decide which missing-data columns should be retained or reviewed for removal.

# In[7]:


# Check unusual values
print("Close prices at or below $0:",
      (sold["ClosePrice"] <= 0).sum())

print("Living areas at or below 0:",
      (sold["LivingArea"] <= 0).sum())

print("Negative days on market:",
      (sold["DaysOnMarket"] < 0).sum())

print("Year built after 2026:",
      (sold["YearBuilt"] > 2026).sum())

# Review columns with over 90% missing data
print("\nSold columns above 90% missing:")
display(sold_high_missing)

print("\nListing columns above 90% missing:")
display(listing_high_missing)

# Keep important fields even if they contain missing values
core_fields = [
    "ClosePrice", "ListPrice", "LivingArea",
    "DaysOnMarket", "CloseDate",
    "ListingContractDate", "PropertyType"
]

# Identify non-core columns for possible removal
review_for_removal = [
    column for column in sold_high_missing.index
    if column not in core_fields
]

print("\nNon-core columns to review for removal:")
print(review_for_removal)


# In[8]:


# Compare sold prices against list prices
valid_prices = sold[
    (sold["ClosePrice"] > 0) &
    (sold["ListPrice"] > 0)
].copy()

above_list = (valid_prices["ClosePrice"] > valid_prices["ListPrice"]).mean() * 100
below_list = (valid_prices["ClosePrice"] < valid_prices["ListPrice"]).mean() * 100
at_list = (valid_prices["ClosePrice"] == valid_prices["ListPrice"]).mean() * 100

print(f"Sold above list price: {above_list:.2f}%")
print(f"Sold below list price: {below_list:.2f}%")
print(f"Sold at list price: {at_list:.2f}%")

# Check date consistency
close_dates = pd.to_datetime(sold["CloseDate"], errors="coerce")
listing_dates = pd.to_datetime(sold["ListingContractDate"], errors="coerce")

invalid_dates = (close_dates < listing_dates).sum()

print("Close dates before listing dates:", invalid_dates)

# Compare median sold prices by county
if "CountyOrParish" in sold.columns:
    county_prices = sold[sold["ClosePrice"] > 0].groupby(
        "CountyOrParish"
    )["ClosePrice"].median().sort_values(ascending=False)

    print("\nMedian sold price by county:")
    display(county_prices.head(10))


# In[9]:


# Save reports
Path("../reports").mkdir(exist_ok=True)
Path("../output").mkdir(exist_ok=True)

market_summary.to_csv("../reports/week2_numeric_summary.csv")
sold_missing.to_csv("../reports/sold_missing_report.csv")
listing_missing.to_csv("../reports/listings_missing_report.csv")

# Save filtered Residential datasets
sold.to_csv("../output/week2_sold_residential.csv", index=False)
listings.to_csv("../output/week2_listings_residential.csv", index=False)

print("Week 2 reports and datasets saved!")


# ## Weeks 2–3: Data Exploration & Validation
# 
# ### Goal
# Check data quality, missing values, and housing market trends before further analysis.
# 
# ### Findings
# - Analyzed 414,054 sold records and 547,162 listing records, each with 84 columns.
# - Both datasets contain only Residential properties.
# - 15 sold columns and 13 listing columns have over 90% missing values.
# - Median sold price: $823,000; average sold price: approximately $1.19 million.
# - Median living area: 1,642 sq ft.
# - Median days on market: 18 days; average: 37 days.
# - 40.10% of homes sold above list price, 42.55% below, and 17.35% at list price.
# - Del Norte ($2.49M), San Mateo ($1.70M), and Santa Clara ($1.60M) had the highest median sold prices in the county summary.
# - Found potential data quality issues:
#   - 48 records with negative days on market.
#   - 150 records with zero or negative living area.
#   - 61 records with close dates before listing dates.
#   - 1 record with a zero or negative close price.
# 
# ### Business Takeaway
# The median sold price of $823K is more representative of a typical property than the $1.19M average, which may be influenced by extreme prices. Homes generally sold within a few weeks, and slightly more sold below list price than above. Data quality issues should be reviewed before using the dataset for market reporting.
# 
# ### Note
# - Columns with over 90% missing values should be reviewed for removal, while important market fields should be retained when possible.
# - Extreme values and inconsistent dates were flagged but not removed.
# - County comparisons may be affected by small sample sizes and should be validated before drawing conclusions.
