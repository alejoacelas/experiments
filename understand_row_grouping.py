#!/usr/bin/env python3
"""
Understand what criterion is used to group sequences into rows
"""

from datasets import load_dataset
from collections import Counter
import re

print("="*100)
print("UNDERSTANDING ROW GROUPING CRITERION")
print("="*100 + "\n")

dataset = load_dataset(
    "microsoft/Dayhoff",
    "uniref90",
    split="train",
    streaming=True
)

print("Analyzing first 20 rows to understand grouping...\n")

for row_idx, example in enumerate(dataset):
    if row_idx >= 20:
        break

    accessions = example['accession']
    descriptions = example['description']
    sequences = example['sequence']

    print(f"\n{'='*100}")
    print(f"ROW {row_idx + 1}: {len(accessions)} sequences")
    print(f"{'='*100}")

    # Extract protein names/families from descriptions
    protein_names = []
    for desc in descriptions:
        # Extract protein name (before ' n=' or before 'TaxID')
        if ' n=' in desc:
            name = desc.split(' n=')[0].strip()
        elif 'TaxID=' in desc:
            name = desc.split('TaxID=')[0].strip()
        else:
            name = desc.split()[0] if desc else 'Unknown'

        protein_names.append(name.lower())

    # Check uniqueness
    unique_proteins = len(set(protein_names))
    most_common = Counter(protein_names).most_common(3)

    print(f"Unique protein names: {unique_proteins}")
    print(f"Most common: {most_common}")

    # Sample sequences to check similarity
    if len(sequences) > 1:
        seq_lengths = [len(s) for s in sequences]
        print(f"Sequence lengths: min={min(seq_lengths)}, max={max(seq_lengths)}, avg={sum(seq_lengths)/len(seq_lengths):.0f}")

        # Show first few protein names
        print(f"\nFirst 5 protein names:")
        for i, name in enumerate(protein_names[:5]):
            print(f"  {i+1}. {name}")

    # Check if they're all the same protein
    if unique_proteins == 1:
        print(f"  ✓ ALL sequences in this row are: {protein_names[0]}")
    elif len(set([p.split()[0] for p in protein_names])) == 1:
        print(f"  ✓ ALL sequences appear to be the same protein family: {protein_names[0].split()[0]}")
    else:
        print(f"  ⚠️  MIXED protein types in this row")

    # Show sample accessions
    print(f"\nSample UniRef90 IDs:")
    for i, acc in enumerate(accessions[:3]):
        print(f"  {i+1}. {acc}")

print("\n" + "="*100)
print("CONCLUSION")
print("="*100 + "\n")

print("Analyzing row grouping pattern...")
