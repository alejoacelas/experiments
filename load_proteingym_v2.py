#!/usr/bin/env python3
"""
Load and sample the ProteinGym DMS substitutions dataset from Hugging Face
"""

from huggingface_hub import hf_hub_download
import pandas as pd
import pyarrow.parquet as pq

# Download the first parquet file from DMS_substitutions
print("Downloading ProteinGym DMS substitutions dataset...")
file_path = hf_hub_download(
    repo_id="OATML-Markslab/ProteinGym_v1",
    filename="DMS_substitutions/train-00000-of-00005.parquet",
    repo_type="dataset"
)

print(f"File downloaded to: {file_path}")

# Load the parquet file
print("\nLoading parquet file...")
df = pd.read_parquet(file_path)

print(f"\nDataset loaded with {len(df)} rows")
print(f"Columns: {list(df.columns)}")

# Sample 5 rows randomly
sampled_df = df.sample(n=min(5, len(df)), random_state=42)

print("\n" + "="*120)
print("SAMPLED 5 ROWS FROM THE DMS SUBSTITUTIONS DATASET")
print("="*120 + "\n")

# Display with all columns
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 80)
pd.set_option('display.width', None)

print(sampled_df.to_string(index=False))

# Also save to CSV for easy viewing
sampled_df.to_csv('proteingym_sample.csv', index=False)
print("\n\nSample also saved to 'proteingym_sample.csv'")

# Print column information
print("\n" + "="*120)
print("COLUMN INFORMATION")
print("="*120 + "\n")
print(df.dtypes)
