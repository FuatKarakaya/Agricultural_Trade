import pandas as pd

# Read the CSV file
df = pd.read_csv(r"C:\Users\omerf\Desktop\db\Agricultural_Trade\prod_reduced_clean.csv")


# Function to reduce values to less than 10^9
def reduce_to_threshold(value, threshold=1e9):
    while value >= threshold:
        value = value / 10
    return value


# Apply the function to the '6h' column
df["quantity"] = df["quantity"].apply(reduce_to_threshold)

# Save the modified dataframe back to CSV (optional)
df.to_csv(
    r"C:\Users\omerf\Desktop\db\Agricultural_Trade\prod_reduced_clean_scaled.csv",
    index=False,
)

# Or just display the result
print(df)
