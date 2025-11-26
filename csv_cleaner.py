import pandas as pd
import os

# Configuration
FILE_PATH = r"C:\Users\fuatk\Desktop\CP.csv"
OUTPUT_PATH = r"C:\Users\fuatk\Desktop\CP_modified.csv"

def delete_columns():
    # 1. Load the CSV
    try:
        df = pd.read_csv(FILE_PATH, encoding='utf-8') 
    except FileNotFoundError:
        print(f"Error: File not found at {FILE_PATH}")
        return

    cols_to_drop = ["Item Code", "Element Code"]
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)
    print(f"Dropped columns: {cols_to_drop}")

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"File saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    delete_columns()