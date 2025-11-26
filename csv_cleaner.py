import pandas as pd
import os

# Configuration
FILE_PATH = r"C:\Users\fuatk\Desktop\CP.csv"
OUTPUT_PATH = r"C:\Users\fuatk\Desktop\CP_modified.csv"

def process_cp_data():
    try:
        df = pd.read_csv(FILE_PATH, encoding='utf-8')
    except FileNotFoundError:
        print(f"Error: File not found at {FILE_PATH}")
        return

    cols_to_drop = ["Area Code", "Area Code (M49)", "Months Code", "Unit"]
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)

    total_rows = len(df)
    print(f"Total rows: {total_rows}")

    def print_stat(label, count):
        percent = (count / total_rows) * 100 if total_rows > 0 else 0
        print(f"{label}: {count} ({percent:.2f}%)")

    val_count = len(df[df["Element"] == "Value"])
    print_stat('Rows with "Element" = "Value"', val_count)

    print("-" * 30)
    print("Item Column Analysis (Count & Percentage):")
    
    item_counts = df["Item"].value_counts()
    
    for item_name, count in item_counts.items():
        print_stat(f'Item: "{item_name}"', count)

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nModified file saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    process_cp_data()