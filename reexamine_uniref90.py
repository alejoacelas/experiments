#!/usr/bin/env python3
"""
Re-examine the UniRef90 dataset structure more carefully
"""

from datasets import load_dataset
import pandas as pd

print("Loading UniRef90 dataset samples...\n")

# Load in streaming mode
dataset = load_dataset(
    "microsoft/Dayhoff",
    "uniref90",
    split="train",
    streaming=True
)

# Get samples
samples = []
for i, example in enumerate(dataset):
    samples.append(example)
    if i >= 9:  # Get 10 samples
        break

print(f"Loaded {len(samples)} samples\n")

print("="*100)
print("DETAILED EXAMINATION OF ACCESSIONS")
print("="*100 + "\n")

# Look at a multi-member row
for idx, sample in enumerate(samples):
    acc_list = sample['accession']

    if len(acc_list) > 5:  # Focus on rows with multiple entries
        print(f"\nRow {idx} with {len(acc_list)} accessions:")
        print(f"First 10 accessions:")
        for i, acc in enumerate(acc_list[:10]):
            print(f"  {i+1}. {acc}")

        # Check if they all have UniRef90_ prefix
        all_uniref90 = all(acc.startswith('UniRef90_') for acc in acc_list)
        print(f"\nAll start with 'UniRef90_': {all_uniref90}")

        # Check if they're all different
        unique_count = len(set(acc_list))
        print(f"Unique accessions: {unique_count} out of {len(acc_list)}")

        if all_uniref90 and unique_count == len(acc_list):
            print("⚠️  THESE ARE DIFFERENT CLUSTER IDs, NOT MEMBERS OF THE SAME CLUSTER!")

        # Look at descriptions too
        print(f"\nFirst 3 descriptions:")
        for i, desc in enumerate(sample['description'][:3]):
            print(f"  {i+1}. {desc}")

        break  # Just examine one multi-member row in detail

print("\n" + "="*100)
print("CHECKING IF THERE'S A HIGHER-LEVEL GROUPING")
print("="*100 + "\n")

# Check what's common between sequences in the same row
for idx, sample in enumerate(samples):
    if len(sample['accession']) > 5:
        descs = sample['description']

        # Extract protein names from descriptions
        proteins = []
        for desc in descs[:10]:
            # Descriptions usually start with protein name
            protein_name = desc.split(' n=')[0] if ' n=' in desc else desc.split()[0]
            proteins.append(protein_name)

        print(f"Row {idx} - Protein names from descriptions:")
        print(f"  Unique protein names: {len(set(proteins))}")
        print(f"  Most common: {max(set(proteins), key=proteins.count)}")
        print(f"  Sample names: {proteins[:5]}")

        # Check if they're all the same protein type
        if len(set(proteins)) == 1:
            print("  ✓ All sequences appear to be the same protein type!")
        else:
            print(f"  ⚠️  Multiple protein types in same row")

        break

print("\n" + "="*100)
print("CONCLUSION")
print("="*100 + "\n")

print("Need to determine:")
print("1. What is the actual grouping criterion for rows?")
print("2. Are rows grouped by protein family, function, or similarity?")
print("3. If we want clustering by UniRef90 ID, we need to reorganize the data")
