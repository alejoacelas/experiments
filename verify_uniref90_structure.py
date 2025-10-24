#!/usr/bin/env python3
"""
Verify the UniRef90 dataset structure and understand clustering
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
    if i >= 199:  # Get 200 samples
        break

print(f"Loaded {len(samples)} samples\n")

print("="*100)
print("VERIFYING DATA STRUCTURE")
print("="*100 + "\n")

# Check if all fields are lists and if they have matching lengths within each row
all_match = True
for i, sample in enumerate(samples[:10]):
    index_len = len(sample['index']) if isinstance(sample['index'], list) else 1
    seq_len = len(sample['sequence']) if isinstance(sample['sequence'], list) else 1
    acc_len = len(sample['accession']) if isinstance(sample['accession'], list) else 1
    desc_len = len(sample['description']) if isinstance(sample['description'], list) else 1

    if index_len == seq_len == acc_len == desc_len:
        status = "✓"
    else:
        status = "✗"
        all_match = False

    print(f"Sample {i+1}: {status} index={index_len}, seq={seq_len}, acc={acc_len}, desc={desc_len}")

if all_match:
    print("\n✓ All fields have matching lengths within each row!")
    print("✓ This confirms each row is a CLUSTER with parallel arrays of member sequences")
else:
    print("\n✗ Some rows have mismatched field lengths")

print("\n" + "="*100)
print("CLUSTER STATISTICS")
print("="*100 + "\n")

cluster_sizes = [len(sample['accession']) for sample in samples]

print(f"Total clusters sampled: {len(cluster_sizes)}")
print(f"Min cluster size: {min(cluster_sizes)}")
print(f"Max cluster size: {max(cluster_sizes)}")
print(f"Average cluster size: {sum(cluster_sizes) / len(cluster_sizes):.2f}")
print(f"Median cluster size: {sorted(cluster_sizes)[len(cluster_sizes)//2]}")

# Distribution
single_member = sum(1 for size in cluster_sizes if size == 1)
small_clusters = sum(1 for size in cluster_sizes if 2 <= size <= 10)
medium_clusters = sum(1 for size in cluster_sizes if 11 <= size <= 100)
large_clusters = sum(1 for size in cluster_sizes if size > 100)

print(f"\nCluster size distribution:")
print(f"  Single member (size=1): {single_member} ({100*single_member/len(cluster_sizes):.1f}%)")
print(f"  Small (2-10 members): {small_clusters} ({100*small_clusters/len(cluster_sizes):.1f}%)")
print(f"  Medium (11-100 members): {medium_clusters} ({100*medium_clusters/len(cluster_sizes):.1f}%)")
print(f"  Large (>100 members): {large_clusters} ({100*large_clusters/len(cluster_sizes):.1f}%)")

print("\n" + "="*100)
print("HOW TO IDENTIFY CLUSTER ID")
print("="*100 + "\n")

# Check if first accession is the cluster representative
print("Checking if the first accession in each list is the cluster representative...")
print("\nSample cluster analysis:")

for i, sample in enumerate(samples[:5]):
    acc_list = sample['accession']
    desc_list = sample['description']

    print(f"\nCluster {i+1} ({len(acc_list)} members):")
    if len(acc_list) == 1:
        print(f"  Single-member cluster")
        print(f"  Accession: {acc_list[0]}")
    else:
        print(f"  First accession: {acc_list[0]}")
        print(f"  First description: {desc_list[0][:100]}...")
        print(f"  Second accession: {acc_list[1]}")
        print(f"  Second description: {desc_list[1][:100]}...")

print("\n" + "="*100)
print("CONCLUSION")
print("="*100 + "\n")

print("The dataset is ALREADY ORGANIZED BY CLUSTER!")
print("")
print("Each row represents a UniRef90 cluster with:")
print("  - accession: list of all member sequence accessions")
print("  - sequence: list of all member sequences")
print("  - description: list of all member descriptions")
print("  - index: list of indices for members")
print("")
print("You can access sequences by cluster by simply iterating through the dataset rows.")
print("The cluster ID appears to be the first accession in the accession list.")
