import pandas as pd

file_path = r"C:\Users\omerf\Desktop\db\Agricultural_Trade\prod_clean.csv"

# Read CSV (avoid DtypeWarning)
df = pd.read_csv(file_path, low_memory=False)

# The index you asked for (0-based)
idx = 4
limit = 2050

# Check the index exists
if idx >= len(df.columns):
    print(f"Index {idx} out of range. File has {len(df.columns)} columns.")
    print("Columns (index : name):")
    for i, name in enumerate(df.columns):
        print(f"  {i} : {name}")
else:
    col_name = df.columns[idx]
    print(f"Using column index {idx} -> column name: '{col_name}'")

    # Convert to numeric (coerce invalids to NaN)
    years = pd.to_numeric(df.iloc[:, idx], errors="coerce")

    # Count rows where year < limit (NaN will be ignored)
    count_pre = (years < limit).sum()
    print(f"Rows with {col_name} < {limit}: {count_pre}")

    # Helpful diagnostics: how many NaNs after conversion and sample bad values
    n_na = years.isna().sum()
    print(f"Rows with non-numeric or missing {col_name} (converted to NaN): {n_na}")

    if n_na:
        bad_samples = df.iloc[:, idx][years.isna()].dropna().unique()[:20]
        print("Sample problematic values (up to 20):")
        for v in bad_samples:
            print(" ", repr(v))
