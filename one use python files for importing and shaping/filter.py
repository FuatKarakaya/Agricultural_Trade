import pandas as pd

# Read the CSV file
df = pd.read_csv(r"C:\Users\omerf\Desktop\prod_reduced_clean_scaled_filtered.csv")

# Show initial row count
print(f"Initial number of rows: {len(df)}")

# Specify the country code to remove
country_code_to_remove = 57  # Change this to the country code you want to remove

# Filter out rows with that country code
df_filtered = df[df["country_code"] != country_code_to_remove]

# Show how many rows were removed
rows_removed = len(df) - len(df_filtered)
print(f"Rows removed: {rows_removed}")
print(f"Remaining rows: {len(df_filtered)}")

# Save the filtered data
df_filtered.to_csv(
    r"C:\Users\omerf\Desktop\prod_reduced_clean_scaled_filtered.csv",
    index=False,
)

print("Done! Filtered CSV saved.")
