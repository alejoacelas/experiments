#!/usr/bin/env python3
"""
Load and sample the ProteinGym DMS substitutions dataset from Hugging Face
"""

from datasets import load_dataset
import pandas as pd

# Load the ProteinGym DMS substitutions dataset
print("Loading ProteinGym DMS substitutions dataset...")
# The correct config name is "DMS_substitutions" (with underscore)
dataset = load_dataset("OATML-Markslab/ProteinGym_v1", "DMS_substitutions")

# Get the first available split (likely 'train' or similar)
print(f"Available splits: {list(dataset.keys())}")

# Get the first split
split_name = list(dataset.keys())[0]
data = dataset[split_name]

print(f"\nDataset loaded with {len(data)} rows")
print(f"Columns: {data.column_names}")

# Convert to pandas for easier manipulation
df = pd.DataFrame(data)

# Sample 5 rows randomly
sampled_df = df.sample(n=min(5, len(df)), random_state=42)

print("\n" + "="*100)
print("SAMPLED 5 ROWS FROM THE DATASET")
print("="*100 + "\n")

# Display with all columns
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', None)

print(sampled_df.to_string(index=False))

# Also save to CSV for easy viewing
sampled_df.to_csv('proteingym_sample.csv', index=False)
print("\n\nSample also saved to 'proteingym_sample.csv'")
