#!/usr/bin/env python
# coding: utf-8

# # Weeks 4–5: Data Cleaning and Preparation
# 
# ## Goal
# Prepare Residential MLS data for analysis by checking date formats, identifying inconsistent transaction timelines, and flagging invalid records.

# In[ ]:


import pandas as pd
from pathlib import Path

# Load the Residential sold dataset
sold = pd.read_csv(
    "../output/sold_with_mortgage_rates.csv",
    low_memory=False
)

# Record original dataset size
original_rows = len(sold)

print("Original sold records:", original_rows)
print("Columns:", len(sold.columns))


# In[ ]:


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


# In[ ]:


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


# ## Week 4 Progress
# 
# ### Goal
# Identify inconsistent transaction dates before cleaning the MLS dataset.
# 
# ### Findings
# - Converted four transaction date columns to datetime format.
# - Created three flags to identify unusual transaction timelines.
# - Identified [INSERT COUNT] records with at least one timeline issue.
# 
# ### Business Takeaway
# Inconsistent transaction dates can affect market statistics, especially calculations involving how long properties take to sell. Flagging these records helps prevent inaccurate reporting.
# 
# ### Note
# Records have only been flagged, not removed. Next steps include checking missing values, invalid numeric fields, and geographic coordinates.
