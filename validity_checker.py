import os
import pandas as pd

# Find all CSV files containing "Valididitätskontrolle"
csv_files = [file for file in os.listdir('.') if 'Valididitätskontrolle' in file and file.endswith('.csv')]

# Read each CSV file and store as Series in a list
all_series = []
for file in csv_files:
    # Read CSV file - pandas handles comma-separated with newlines automatically
    df = pd.read_csv(file)
    
    # Check if the two boolean columns are equal for each row
    # Assuming columns are: filename, boolean1, boolean2
    equality_checks = df.iloc[:, 1] == df.iloc[:, 2]  # Compare column 1 and 2
    series = pd.Series(equality_checks.values, name=file.replace('.csv', ''))
    all_series.append(series)

# Create DataFrame from all Series
final_df = pd.DataFrame(all_series).T  # Transpose so each column is a file

print(f"Found {len(csv_files)} validation files")
print(f"Total files processed: {len(all_series)}")
print("\nDataFrame shape:", final_df.shape)
print("\nFirst few rows:")
print(final_df.head())
# ...existing code...

# Analysis commands
print("\n" + "="*50)
print("ANALYSIS RESULTS")
print("="*50)

# 1. Number of entries where each value is True (per column/file)
print("\n1. Number of True entries per file:")
true_counts = final_df.sum()
print(true_counts)

# Per column (across all images for each file)
avg_true_per_file = final_df.sum(axis=0).mean()
print(f"Average True values per file: {avg_true_per_file:.2f}")

# Overall average
overall_avg = final_df.sum().sum() / (final_df.shape[0] * final_df.shape[1])
print(f"Overall average True ratio: {overall_avg:.2f}")
print((final_df.sum() == 9).sum())
print((final_df.sum() == 10).sum())
print((final_df.sum() == 8).sum())