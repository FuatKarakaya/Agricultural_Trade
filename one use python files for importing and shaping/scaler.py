import pandas as pd

# Read the CSV file
df = pd.read_csv(
    r"C:\Users\omerf\Desktop\db\Agricultural_Trade\prod_val_reduced_clean.csv"
)

# Count how many values are >= 10^9 before modification
modified_count = (df["value"] >= 1e9).sum()
print(f"Number of rows with value >= 10^9: {modified_count}")


# Function to reduce values to less than 10^9
def reduce_to_threshold(value, threshold=1e9):
    while value >= threshold:
        value = value / 10
    return value


# Apply the function to the 'value' column
df["value"] = df["value"].apply(reduce_to_threshold)

# Save the modified dataframe back to CSV
df.to_csv(
    r"C:\Users\omerf\Desktop\db\Agricultural_Trade\prod_val_reduced_clean_scaled.csv",
    index=False,
)

print(f"Done! {modified_count} rows were modified.")
print(f"\nFirst few rows of modified data:")
print(df.head(10))
