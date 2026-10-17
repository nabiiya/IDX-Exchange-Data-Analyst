#!/usr/bin/env python
# coding: utf-8

# Goal: Combine all monthly sold files into one dataset, combine all monthly listing files into another dataset, and keep only Residential properties.

# In[41]:


import pandas as pd
from pathlib import Path

# Find monthly CSV files
data_folder = Path("../data")

sold_files = sorted(data_folder.glob("CRMLSSold*.csv"))
listing_files = sorted(data_folder.glob("CRMLSListing*.csv"))

print("Sold files:", len(sold_files))
print("Listing files:", len(listing_files))


# In[42]:


# Keep files from January 2024 through September 2026
start_month = "202401"
end_month = "202609"

sold_files = [
    file for file in sold_files
    if start_month <= file.stem.replace("CRMLSSold", "")[:6] <= end_month
]

listing_files = [
    file for file in listing_files
    if start_month <= file.stem.replace("CRMLSListing", "")[:6] <= end_month
]

print("Sold files in range:", len(sold_files))
print("Listing files in range:", len(listing_files))


# In[43]:


#checking for missing months

# Create a list of expected months
months = pd.period_range("2024-01", "2026-09", freq="M")

expected_months = []

for month in months:
    expected_months.append(month.strftime("%Y%m"))

# Find which months were downloaded
sold_months = []

for file in sold_files:
    sold_months.append(file.stem.replace("CRMLSSold", "")[:6])

listing_months = []

for file in listing_files:
    listing_months.append(file.stem.replace("CRMLSListing", ""))

# Compare expected and available months
missing_sold = set(expected_months) - set(sold_months)
missing_listings = set(expected_months) - set(listing_months)

print("Missing sold months:", sorted(missing_sold))
print("Missing listing months:", sorted(missing_listings))


# In[44]:


#combining the sold files

# Create an empty list
sold_data = []

# Read each monthly sold file
for file in sold_files:
    df = pd.read_csv(file, low_memory=False)
    print(file.name, "Rows:", len(df))
    sold_data.append(df)

# Combine into one DataFrame
sold = pd.concat(sold_data, ignore_index=True)

print("Combined sold rows:", len(sold))
print("Combined sold columns:", len(sold.columns))


# In[45]:


#combining the listing files

listing_data = []

for file in listing_files:
    df = pd.read_csv(file, low_memory=False)
    print(file.name, "Rows:", len(df))
    listing_data.append(df)

listings = pd.concat(listing_data, ignore_index=True)

print("Combined listing rows:", len(listings))
print("Combined listing columns:", len(listings.columns))


# In[46]:


#checking property types
# Count each property type
print(sold["PropertyType"].value_counts(dropna=False))

print(listings["PropertyType"].value_counts(dropna=False))


# In[47]:


#filtering residential properties (removes other property types)

# Save row counts before filtering
sold_before = len(sold)
listings_before = len(listings)

# Keep only Residential properties
sold = sold[sold["PropertyType"] == "Residential"].copy()
listings = listings[listings["PropertyType"] == "Residential"].copy()

# Save row counts after filtering
sold_after = len(sold)
listings_after = len(listings)

print("Sold before:", sold_before)
print("Sold after:", sold_after)

print("Listings before:", listings_before)
print("Listings after:", listings_after)


# In[48]:


#verifying the row counts + comparing monthly totals to combined totals
print("Sold monthly total:", sum(len(df) for df in sold_data))
print("Sold combined total:", sold_before)

print("Listing monthly total:", sum(len(df) for df in listing_data))
print("Listing combined total:", listings_before)


# In[ ]:


# Row Count Verification:
# Sold: 615,707 rows before filtering → 414,054 Residential rows after.
# Listings: 860,898 rows before filtering → 547,162 Residential rows after.
# Monthly row totals matched the combined row totals.
# Missing months: May–September 2026 for both datasets.

# Create output folder
Path("../output").mkdir(exist_ok=True)

# Save Residential datasets
sold.to_csv("../output/combined_sold_residential.csv", index=False)
listings.to_csv("../output/combined_listings_residential.csv", index=False)

print("Week 1 files saved!")


# ## Week 1: Monthly Dataset Aggregation
# 
# ### Goal
# Combine monthly MLS sold and listing files into two datasets and filter for Residential properties.
# 
# ### Findings
# - **Files Combined:** 28 sold files and 28 listing files.
# - **Sold Records:** 615,707 → 414,054 after Residential filtering.
# - **Listing Records:** 860,898 → 547,162 after Residential filtering.
# - **Dataset Structure:** Both datasets contain 84 columns.
# - **Row Verification:** Monthly row totals matched the combined datasets.
# - **Duplicate Months:** No duplicate months found.
# - **Missing Months:** May–September 2026 for both datasets.
# - **Output:** Saved two combined Residential CSV datasets.
# 
# ### Business Takeaway
# Combining monthly MLS files makes it easier to analyze residential housing market trends over time. Filtering for Residential properties ensures the analysis focuses only on the relevant housing market.
# 
# ### Note
# The datasets currently cover January 2024 through April 2026. The remaining months need to be added when available.
