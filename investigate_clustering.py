#!/usr/bin/env python3
"""
Investigate whether UniRef90 IDs in this dataset represent clusters or individual sequences
"""

from datasets import load_dataset
from collections import defaultdict

print("="*100)
print("INVESTIGATING UniRef90 CLUSTER STRUCTURE")
print("="*100 + "\n")

print("Loading larger sample to check for duplicate cluster IDs...\n")

dataset = load_dataset(
    "microsoft/Dayhoff",
    "uniref90",
    split="train",
    streaming=True
)

cluster_counts = defaultdict(int)
cluster_examples = defaultdict(list)

row_count = 0
total_sequences = 0
max_rows = 1000  # Process more rows

for example in dataset:
    accessions = example['accession']
    sequences = example['sequence']

    for i, cluster_id in enumerate(accessions):
        cluster_counts[cluster_id] += 1

        # Store first few examples for each cluster
        if len(cluster_examples[cluster_id]) < 3:
            cluster_examples[cluster_id].append({
                'sequence': sequences[i][:60] + '...',
                'full_id': cluster_id
            })

        total_sequences += 1

    row_count += 1

    if row_count % 200 == 0:
        duplicates = sum(1 for count in cluster_counts.values() if count > 1)
        print(f"Processed {row_count} rows, {total_sequences} sequences")
        print(f"  Unique clusters: {len(cluster_counts)}")
        print(f"  Clusters with >1 sequence: {duplicates}")

    if row_count >= max_rows:
        break

print(f"\n✓ Finished processing {row_count} rows")
print(f"✓ Total sequences: {total_sequences}")
print(f"✓ Unique cluster IDs: {len(cluster_counts)}")

# Find clusters with multiple members
multi_member_clusters = {
    cid: count for cid, count in cluster_counts.items() if count > 1
}

print(f"\n{'='*100}")
print(f"RESULTS")
print(f"{'='*100}\n")

if multi_member_clusters:
    print(f"✓ Found {len(multi_member_clusters)} clusters with multiple sequences!\n")

    print("Sample multi-member clusters:")
    for i, (cluster_id, count) in enumerate(list(multi_member_clusters.items())[:5]):
        print(f"\n{i+1}. Cluster: {cluster_id}")
        print(f"   Size: {count} sequences")
        print(f"   Examples:")
        for ex in cluster_examples[cluster_id]:
            print(f"     - {ex['sequence']}")

else:
    print("⚠️  No clusters with multiple sequences found in this sample!")
    print("\nPossible explanations:")
    print("1. The train/test/valid splits might already be deduplicated")
    print("2. UniRef90 IDs in this dataset might be unique sequence identifiers")
    print("3. Need to process more data or check different splits")

    print(f"\nSample of unique cluster IDs:")
    for i, cluster_id in enumerate(list(cluster_counts.keys())[:10]):
        print(f"  {i+1}. {cluster_id}")

print(f"\n{'='*100}")
print("CHECKING TEST SPLIT")
print(f"{'='*100}\n")

# Check test split
print("Loading test split sample...\n")

test_dataset = load_dataset(
    "microsoft/Dayhoff",
    "uniref90",
    split="test",
    streaming=True
)

test_cluster_counts = defaultdict(int)
test_row_count = 0
test_total_sequences = 0

for example in test_dataset:
    accessions = example['accession']

    for cluster_id in accessions:
        test_cluster_counts[cluster_id] += 1
        test_total_sequences += 1

    test_row_count += 1

    if test_row_count >= 100:
        break

test_multi_member = sum(1 for count in test_cluster_counts.values() if count > 1)

print(f"Test split sample:")
print(f"  Rows: {test_row_count}")
print(f"  Sequences: {test_total_sequences}")
print(f"  Unique clusters: {len(test_cluster_counts)}")
print(f"  Clusters with >1 sequence: {test_multi_member}")
