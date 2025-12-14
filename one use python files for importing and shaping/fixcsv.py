import pandas as pd

# Load the CSV files
prod_df = pd.read_csv(r"C:\Users\omerf\Desktop\prod.csv")
prod_val_df = pd.read_csv(r"C:\Users\omerf\Desktop\prod_val.csv")

# Strip whitespace from column names (CSVs can be finicky with headers)
prod_df.columns = prod_df.columns.str.strip()
prod_val_df.columns = prod_val_df.columns.str.strip()

# Strip quotes and whitespace from key columns to ensure matching
prod_df["Area Code (M49)"] = (
    prod_df["Area Code (M49)"].astype(str).str.replace("'", "").str.strip()
)
prod_val_df["Area Code (M49)"] = (
    prod_val_df["Area Code (M49)"].astype(str).str.replace("'", "").str.strip()
)

prod_df["Item Code"] = prod_df["Item Code"].astype(str).str.strip()
prod_val_df["Item Code"] = prod_val_df["Item Code"].astype(str).str.strip()

prod_df["Year"] = prod_df["Year"].astype(str).str.strip()
prod_val_df["Year"] = prod_val_df["Year"].astype(str).str.strip()

# Create production_ID for prod.csv (starting from 1)
prod_df["production_ID"] = range(1, len(prod_df) + 1)

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

# Create a mapping dictionary from composite_key to production_ID
key_to_id = dict(zip(prod_df["composite_key"], prod_df["production_ID"]))

# Map production_ID to prod_val_df
prod_val_df["production_ID"] = prod_val_df["composite_key"].map(key_to_id)

# Check for any unmatched rows in prod_val
unmatched = prod_val_df[prod_val_df["production_ID"].isna()]
if len(unmatched) > 0:
    print(
        f"Warning: {len(unmatched)} rows in prod_val.csv could not be matched to prod.csv"
    )
    print("First few unmatched rows:")
    print(unmatched[["Area Code (M49)", "Item Code", "Year"]].head())

# Create production_value_ID for prod_val.csv
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

# Remove rows with missing production_ID (unmatched rows)
prod_val_clean = prod_val_clean.dropna(subset=["production_ID"])

# Convert production_ID to integer
prod_val_clean["production_ID"] = prod_val_clean["production_ID"].astype(int)

# Export cleaned CSVs with explicit paths
output_dir = r"C:\Users\omerf\Desktop"
prod_clean.to_csv(f"{output_dir}\\prod_clean.csv", index=False)
prod_val_clean.to_csv(f"{output_dir}\\prod_val_clean.csv", index=False)

print(f"\nProcessing complete!")
print(f"Files saved to: {output_dir}")
print(f"prod_clean.csv: {len(prod_clean)} rows")
print(f"prod_val_clean.csv: {len(prod_val_clean)} rows")
