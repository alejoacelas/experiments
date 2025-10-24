#!/usr/bin/env python3
"""
Inspect the UniRef90 dataset structure from HuggingFace
"""

from datasets import load_dataset
import pandas as pd

print("Loading UniRef90 dataset (streaming mode for efficiency)...")
print("This will download only a small sample to understand the structure.\n")

# Load in streaming mode to avoid downloading entire dataset
dataset = load_dataset(
    "microsoft/Dayhoff",
    "uniref90",
    split="train",
    streaming=True
)

# Get first 100 examples
samples = []
for i, example in enumerate(dataset):
    samples.append(example)
    if i >= 99:  # Get 100 samples (0-99)
        break

print(f"Loaded {len(samples)} samples")
print(f"Fields available: {list(samples[0].keys())}\n")

# Convert to pandas for easier analysis
df = pd.DataFrame(samples)

print("="*100)
print("FIRST 5 EXAMPLES (BASIC INFO)")
print("="*100 + "\n")

# Display settings
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 80)
pd.set_option('display.width', None)

# Show basic info for first 5 examples
for i, row in df.head().iterrows():
    print(f"\nExample {i+1}:")
    print(f"  Index: {row['index']}")
    print(f"  Accession type: {type(row['accession'])}")
    if isinstance(row['accession'], list):
        print(f"  Accession (list with {len(row['accession'])} items): {row['accession'][:3]}...")
    else:
        print(f"  Accession: {row['accession']}")
    print(f"  Sequence length: {len(row['sequence'])}")
    print(f"  Description (first 100 chars): {row['description'][:100]}...")

print("\n" + "="*100)
print("ACCESSION FIELD ANALYSIS")
print("="*100 + "\n")

# Check accession format
if isinstance(df['accession'].iloc[0], list):
    print("Accession field contains LISTS of accession IDs")
    print(f"\nFirst few accession lists:")
    for i, acc_list in enumerate(df['accession'].head(10)):
        print(f"  Example {i+1}: {len(acc_list)} accessions - First: {acc_list[0] if acc_list else 'N/A'}")

    # Extract first accession from each list for pattern analysis
    first_accessions = [acc[0] if acc else None for acc in df['accession']]
    uniref_count = sum(1 for acc in first_accessions if acc and 'UniRef90_' in acc)
    print(f"\nFirst accessions matching 'UniRef90_' pattern: {uniref_count}/{len(df)}")
else:
    print("Accession field contains STRING values")
    print(f"Number of unique accessions in sample: {df['accession'].nunique()}")
    print(f"Total samples: {len(df)}")
    print(f"\nSample accession values:")
    for acc in df['accession'].head(10):
        print(f"  {acc}")

    # Check if accessions are UniRef90 cluster IDs
    uniref_pattern = df['accession'].str.contains('UniRef90_', na=False).sum()
    print(f"\nAccessions matching 'UniRef90_' pattern: {uniref_pattern}/{len(df)}")

print("\n" + "="*100)
print("DESCRIPTION FIELD SAMPLE")
print("="*100 + "\n")

# Check descriptions for cluster info
for i, desc in enumerate(df['description'].head(5)):
    print(f"{i+1}. {desc}\n")

print("="*100)
print("SEQUENCE LENGTH STATISTICS")
print("="*100 + "\n")

df['seq_length'] = df['sequence'].str.len()
print(df['seq_length'].describe())

# Save sample for reference
df.to_csv('uniref90_sample.csv', index=False)
print(f"\nSample saved to 'uniref90_sample.csv'")

# Check for test split
print("\n" + "="*100)
print("CHECKING TEST SPLIT")
print("="*100 + "\n")

try:
    test_dataset = load_dataset(
        "microsoft/Dayhoff",
        "uniref90",
        split="test",
        streaming=True
    )

    test_samples = []
    for i, example in enumerate(test_dataset):
        test_samples.append(example)
        if i >= 9:  # Get 10 test samples
            break

    print(f"Test split exists with {len(test_samples)} samples checked")
    print(f"Test sample accessions:")
    test_df = pd.DataFrame(test_samples)
    for acc in test_df['accession'].head(5):
        print(f"  {acc}")
except Exception as e:
    print(f"Error loading test split: {e}")
