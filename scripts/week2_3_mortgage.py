#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from pathlib import Path

# Load Week 2 Residential datasets
sold = pd.read_csv("../output/week2_sold_residential.csv", low_memory=False)
listings = pd.read_csv("../output/week2_listings_residential.csv", low_memory=False)

# Download weekly mortgage rates from FRED
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"

mortgage = pd.read_csv(url)

# Rename the columns
mortgage.columns = ["date", "rate_30yr_fixed"]

# Convert dates and rates to appropriate types
mortgage["date"] = pd.to_datetime(mortgage["date"], errors="coerce")
mortgage["rate_30yr_fixed"] = pd.to_numeric(
    mortgage["rate_30yr_fixed"], errors="coerce"
)

print("Mortgage records:", len(mortgage))
display(mortgage.head())


# In[2]:


# Extract year and month
mortgage["year_month"] = mortgage["date"].dt.to_period("M")

# Calculate average mortgage rate for each month
mortgage_monthly = mortgage.groupby(
    "year_month"
)["rate_30yr_fixed"].mean().reset_index()

print("Monthly mortgage rates:")
display(mortgage_monthly.tail(12))


# In[3]:


# Create year-month keys
sold["year_month"] = pd.to_datetime(
    sold["CloseDate"], errors="coerce"
).dt.to_period("M")

listings["year_month"] = pd.to_datetime(
    listings["ListingContractDate"], errors="coerce"
).dt.to_period("M")

# Merge mortgage rates with MLS datasets
sold_with_rates = sold.merge(
    mortgage_monthly, on="year_month", how="left"
)

listings_with_rates = listings.merge(
    mortgage_monthly, on="year_month", how="left"
)

print("Sold records:", len(sold_with_rates))
print("Listing records:", len(listings_with_rates))


# In[4]:


# Check for missing mortgage rates
sold_missing_rates = sold_with_rates["rate_30yr_fixed"].isnull().sum()
listing_missing_rates = listings_with_rates["rate_30yr_fixed"].isnull().sum()

print("Sold records without mortgage rates:", sold_missing_rates)
print("Listing records without mortgage rates:", listing_missing_rates)

# Make sure the merge didn't change the number of records
print("Sold row count matches:", len(sold) == len(sold_with_rates))
print("Listing row count matches:", len(listings) == len(listings_with_rates))

# Preview the results
display(sold_with_rates[
    ["CloseDate", "year_month", "ClosePrice", "rate_30yr_fixed"]
].head())

display(listings_with_rates[
    ["ListingContractDate", "year_month", "ListPrice", "rate_30yr_fixed"]
].head())

# Identify months that did not match a mortgage rate
print("Unmatched sold months:")
print(sold_with_rates.loc[
    sold_with_rates["rate_30yr_fixed"].isna(), "year_month"
].value_counts().sort_index())

print("Unmatched listing months:")
print(listings_with_rates.loc[
    listings_with_rates["rate_30yr_fixed"].isna(), "year_month"
].value_counts().sort_index())


# In[5]:


# Save datasets with mortgage rates included
Path("../output").mkdir(exist_ok=True)

sold_with_rates.to_csv(
    "../output/sold_with_mortgage_rates.csv",
    index=False
)

listings_with_rates.to_csv(
    "../output/listings_with_mortgage_rates.csv",
    index=False
)

print("Mortgage-enriched datasets saved!")


# ## Weeks 2–3: Mortgage Rate Enrichment
# 
# ### Goal
# Add national 30-year fixed mortgage rates to the Residential sold and listing datasets to support future housing market analysis.
# 
# ### Findings
# - Retrieved 2,899 weekly mortgage rate records from FRED (MORTGAGE30US).
# - Converted weekly rates into monthly averages.
# - Matched sold properties using CloseDate and listings using ListingContractDate.
# - Successfully merged mortgage rates into:
#   - 414,054 sold records.
#   - 547,162 listing records.
# - Found 0 missing mortgage rates in either dataset.
# - Row counts remained unchanged after both merges.
# - Example: January 2024 had an average 30-year mortgage rate of 6.6425%.
# - Saved both mortgage-enriched datasets as new CSV files.
# 
# ### Business Takeaway
# The datasets can now be used to explore how mortgage rates relate to housing prices, listing activity, and market demand. Adding monthly mortgage rates allows housing market trends to be compared with borrowing costs over time.
# 
# ### Note
# - Mortgage rates represent national monthly averages, not individual buyers' actual loan rates.
# - Sold properties use their closing month, while listings use their listing month.
# - The merge was validated successfully, but no relationship between mortgage rates and housing market activity has been established yet.
