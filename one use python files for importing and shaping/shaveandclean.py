import pandas as pd
import random

output_dir = r"C:\Users\omerf\Desktop"

# Load the original CSV files
print("Loading original CSV files...")
prod_df = pd.read_csv(r"C:\Users\omerf\Desktop\prod.csv")
prod_val_df = pd.read_csv(r"C:\Users\omerf\Desktop\prod_val.csv")

# Strip whitespace from column names
prod_df.columns = prod_df.columns.str.strip()
prod_val_df.columns = prod_val_df.columns.str.strip()

print(f"Original prod.csv rows: {len(prod_df)}")
print(f"Original prod_val.csv rows: {len(prod_val_df)}")

# Strip quotes and whitespace from key columns first
prod_df["Area Code (M49)"] = (
    prod_df["Area Code (M49)"].astype(str).str.replace("'", "").str.strip()
)
prod_df["Item Code"] = prod_df["Item Code"].astype(str).str.replace("'", "").str.strip()
prod_df["Year"] = prod_df["Year"].astype(str).str.strip()

# Make (Area Code M49, Item Code, Year) unique - keep first occurrence only
print(
    "\nRemoving duplicate (Area Code M49, Item Code, Year) combinations from prod.csv..."
)
prod_df = prod_df.drop_duplicates(
    subset=["Area Code (M49)", "Item Code", "Year"], keep="first"
)
print(f"After deduplication - prod.csv rows: {len(prod_df)}")

# Remove all rows with year < 1990 from both files
print("\nRemoving rows with Year < 1990...")
prod_df = prod_df[prod_df["Year"].astype(int) >= 1990]
prod_val_df = prod_val_df[prod_val_df["Year"] >= 1990]

print(f"After year filter - prod.csv rows: {len(prod_df)}")
print(f"After year filter - prod_val.csv rows: {len(prod_val_df)}")

# Strip quotes and whitespace from Item Code in prod_val
prod_val_df["Item Code"] = (
    prod_val_df["Item Code"].astype(str).str.replace("'", "").str.strip()
)

# Get all unique Item Codes from both files
all_item_codes = list(
    set(prod_df["Item Code"].unique()) | set(prod_val_df["Item Code"].unique())
)
random.shuffle(all_item_codes)

# Reduce prod.csv to under 3 million rows
items_to_remove_prod = []
for item_code in all_item_codes:
    if len(prod_df) < 1_000_000:
        break
    items_to_remove_prod.append(item_code)
    prod_df = prod_df[prod_df["Item Code"] != item_code]
    print(
        f"Removed Item Code {item_code} from prod.csv - remaining rows: {len(prod_df)}"
    )

# Reduce prod_val.csv to under 3 million rows
items_to_remove_val = []
for item_code in all_item_codes:
    if len(prod_val_df) < 1_000_000:
        break
    items_to_remove_val.append(item_code)
    prod_val_df = prod_val_df[prod_val_df["Item Code"] != item_code]
    print(
        f"Removed Item Code {item_code} from prod_val.csv - remaining rows: {len(prod_val_df)}"
    )

# Save reduced versions
prod_df.to_csv(f"{output_dir}\\prod_reduced.csv", index=False)
prod_val_df.to_csv(f"{output_dir}\\prod_val_reduced.csv", index=False)

print(f"\nReduced files saved!")
print(f"prod_reduced.csv: {len(prod_df)} rows")
print(f"prod_val_reduced.csv: {len(prod_val_df)} rows")

# Now clean the reduced files
print("\n--- Starting cleaning process ---\n")

# Strip quotes and whitespace from key columns to ensure matching
prod_val_df["Area Code (M49)"] = (
    prod_val_df["Area Code (M49)"].astype(str).str.replace("'", "").str.strip()
)

prod_val_df["Year"] = prod_val_df["Year"].astype(str).str.strip()

# Create a composite key for matching
prod_df["composite_key"] = (
    prod_df["Area Code (M49)"] + "_" + prod_df["Item Code"] + "_" + prod_df["Year"]
)

prod_val_df["composite_key"] = (
    prod_val_df["Area Code (M49)"]
    + "_"
    + prod_val_df["Item Code"]
    + "_"
    + prod_val_df["Year"]
)

# Create production_ID for prod.csv (starting from 1)
prod_df["production_ID"] = range(1, len(prod_df) + 1)

# Create a mapping dictionary from composite_key to production_ID
key_to_id = dict(zip(prod_df["composite_key"], prod_df["production_ID"]))

# Map production_ID to prod_val_df
prod_val_df["production_ID"] = prod_val_df["composite_key"].map(key_to_id)

# Check for any unmatched rows in prod_val
unmatched = prod_val_df[prod_val_df["production_ID"].isna()]
if len(unmatched) > 0:
    print(
        f"Warning: {len(unmatched)} rows in prod_val_reduced.csv could not be matched to prod_reduced.csv"
    )
    print("First few unmatched rows:")
    print(unmatched[["Area Code (M49)", "Item Code", "Year"]].head())

# Remove rows with missing production_ID (unmatched rows) BEFORE creating production_value_ID
prod_val_df = prod_val_df.dropna(subset=["production_ID"])

# Convert production_ID to integer
prod_val_df["production_ID"] = prod_val_df["production_ID"].astype(int)

# Create production_value_ID AFTER filtering unmatched rows
prod_val_df["production_value_ID"] = range(1, len(prod_val_df) + 1)

# Select and rename columns for prod.csv → Production table
prod_clean = prod_df[
    ["production_ID", "Area Code (M49)", "Item Code", "Item", "Year", "Unit", "Value"]
].copy()

prod_clean.columns = [
    "production_ID",
    "country_code",
    "commodity_code",
    "item_name",
    "year",
    "unit",
    "quantity",
]

# Select and rename columns for prod_val.csv → Production_Value table
prod_val_clean = prod_val_df[
    ["production_value_ID", "production_ID", "Element", "Year", "Unit", "Value"]
].copy()

prod_val_clean.columns = [
    "production_value_ID",
    "production_ID",
    "element",
    "year",
    "unit",
    "value",
]

# Export cleaned CSVs with explicit paths
prod_clean.to_csv(f"{output_dir}\\prod_reduced_clean.csv", index=False)
prod_val_clean.to_csv(f"{output_dir}\\prod_val_reduced_clean.csv", index=False)

print(f"\nAll processing complete!")
print(f"\nReduced files:")
print(f"  prod_reduced.csv: {len(prod_df)} rows")
print(f"  prod_val_reduced.csv: {len(prod_val_df)} rows")
print(f"\nCleaned files:")
print(f"  prod_reduced_clean.csv: {len(prod_clean)} rows")
print(f"  prod_val_reduced_clean.csv: {len(prod_val_clean)} rows")
print(f"\nAll files saved to: {output_dir}")
