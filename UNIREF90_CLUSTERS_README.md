# UniRef90 Clustered Dataset Guide

## Overview

The UniRef90 dataset from [microsoft/Dayhoff](https://huggingface.co/datasets/microsoft/Dayhoff) is **already organized by cluster**. Each row in the dataset represents one UniRef90 cluster containing protein sequences that share ≥90% sequence identity.

## Important Discovery

**The dataset files already indicate grouping by cluster ID!** You don't need to group the sequences yourself - they come pre-clustered.

## Dataset Structure

### Each Row = One Cluster

Each row in the dataset contains parallel lists with the following fields:

- **`accession`**: List of UniRef90 IDs for all cluster members
- **`sequence`**: List of protein sequences for all cluster members
- **`description`**: List of descriptions for all cluster members
- **`index`**: List of indices for all cluster members

**Cluster ID**: The first accession in the `accession` list serves as the cluster ID.

### Example

```python
{
    'index': [1, 2, 3],
    'accession': ['UniRef90_A0A123', 'UniRef90_B1B456', 'UniRef90_C2C789'],
    'sequence': ['MKAIAW...', 'MKTIAW...', 'MKVIAW...'],
    'description': ['Protein A...', 'Protein B...', 'Protein C...']
}
```

This represents a single cluster with ID `UniRef90_A0A123` containing 3 similar sequences.

## Dataset Statistics (from sample of 1000 clusters)

- **Single-member clusters**: ~64% (sequences with no similar sequences)
- **Multi-member clusters**: ~36%
- **Large clusters (≥100 members)**: ~0.5%
- **Average cluster size**: ~4.6 sequences
- **Median cluster size**: 1 sequence

## Available Scripts

### 1. `inspect_uniref90.py`

Quick inspection script to view sample data and understand the structure.

```bash
python inspect_uniref90.py
```

**Output**: Sample data, field analysis, and cluster information

### 2. `verify_uniref90_structure.py`

Verification script to confirm the clustering structure and statistics.

```bash
python verify_uniref90_structure.py
```

**Output**: Data structure verification, cluster statistics, and conclusions

### 3. `uniref90_cluster_utils.py` (Main Utility)

Comprehensive utility for working with clustered data.

## Usage Examples

### Basic Usage - Iterate Through Clusters

```python
from uniref90_cluster_utils import UniRef90ClusterLoader

# Initialize loader
loader = UniRef90ClusterLoader(split="train", streaming=True)
loader.load()

# Iterate through clusters
for cluster in loader.iterate_clusters(max_clusters=10):
    print(f"Cluster {cluster['cluster_id']}")
    print(f"  Size: {cluster['cluster_size']}")
    print(f"  Sequences: {len(cluster['sequences'])}")
```

### Filter Clusters by Size

```python
# Get only large clusters (>100 members)
for cluster in loader.filter_by_size(min_size=100, max_clusters=5):
    print(f"Large cluster: {cluster['cluster_id']} with {cluster['cluster_size']} members")

# Get small clusters (2-10 members)
for cluster in loader.filter_by_size(min_size=2, max_size=10, max_clusters=100):
    print(f"Small cluster: {cluster['cluster_id']}")
```

### Sample Random Clusters

```python
# Get 100 random clusters
sample = loader.sample_clusters(n_samples=100)

# Work with sampled data
for cluster in sample:
    for i in range(cluster['cluster_size']):
        accession = cluster['accessions'][i]
        sequence = cluster['sequences'][i]
        description = cluster['descriptions'][i]
        # Process each sequence...
```

### Get Dataset Statistics

```python
stats = loader.get_statistics(n_samples=1000)

print(f"Min cluster size: {stats['min_cluster_size']}")
print(f"Max cluster size: {stats['max_cluster_size']}")
print(f"Mean cluster size: {stats['mean_cluster_size']}")
print(f"Single-member clusters: {stats['single_member_clusters']}")
```

### Export to Different Formats

#### Export to JSONL (preserves cluster structure)

```python
from uniref90_cluster_utils import export_clusters_to_jsonl

export_clusters_to_jsonl(
    output_file="uniref90_clusters.jsonl",
    split="train",
    max_clusters=1000,  # Limit to first 1000 clusters
    min_size=2,  # Only multi-member clusters
    max_size=100  # Skip very large clusters
)
```

#### Export to CSV (flattened - one row per sequence)

```python
from uniref90_cluster_utils import export_clusters_to_csv

export_clusters_to_csv(
    output_file="uniref90_sequences.csv",
    split="train",
    max_clusters=1000,
    flatten=True  # One row per sequence
)
```

#### Export to CSV (one row per cluster)

```python
export_clusters_to_csv(
    output_file="uniref90_clusters.csv",
    split="train",
    max_clusters=1000,
    flatten=False  # One row per cluster (lists separated by |)
)
```

### Search for Specific Cluster

```python
# Find a specific cluster by ID
cluster = loader.get_cluster_by_id(
    cluster_id="UniRef90_A0A410P257",
    max_search=10000  # Search through first 10k clusters
)

if cluster:
    print(f"Found cluster with {cluster['cluster_size']} members")
```

## Working with Train and Test Splits

```python
# Train split
train_loader = UniRef90ClusterLoader(split="train", streaming=True)
train_loader.load()

# Test split
test_loader = UniRef90ClusterLoader(split="test", streaming=True)
test_loader.load()

# Validation split
valid_loader = UniRef90ClusterLoader(split="valid", streaming=True)
valid_loader.load()
```

## Memory Considerations

The datasets are large (train ~83GB, test ~90MB, valid ~87MB), so:

1. **Always use streaming mode** (`streaming=True`) to avoid loading everything into memory
2. **Use `max_clusters` parameter** to limit the number of clusters processed
3. **Sample data first** to test your code before processing the full dataset

### Example: Safe Sampling for Testing

```python
# Test your code on a small sample first
loader = UniRef90ClusterLoader(split="train", streaming=True)
loader.load()

# Process just 100 clusters to test
for cluster in loader.iterate_clusters(max_clusters=100):
    # Your processing code here
    pass
```

## Common Use Cases

### 1. Extract All Sequences with Their Cluster IDs

```python
loader = UniRef90ClusterLoader(split="train", streaming=True)
loader.load()

for cluster in loader.iterate_clusters():
    cluster_id = cluster['cluster_id']

    # Iterate through all sequences in this cluster
    for i in range(cluster['cluster_size']):
        seq_accession = cluster['accessions'][i]
        seq_sequence = cluster['sequences'][i]
        seq_description = cluster['descriptions'][i]

        # Process: (cluster_id, seq_accession, seq_sequence, seq_description)
```

### 2. Group Training Data by Cluster for ML

```python
# Get clusters with at least 2 members for training
train_clusters = []

for cluster in loader.filter_by_size(min_size=2, max_clusters=10000):
    train_clusters.append({
        'cluster_id': cluster['cluster_id'],
        'sequences': cluster['sequences']
    })

# Now each cluster has multiple similar sequences for contrastive learning
```

### 3. Stratified Sampling by Cluster

```python
# Sample sequences while maintaining cluster structure
small_clusters = list(loader.filter_by_size(min_size=1, max_size=5, max_clusters=100))
medium_clusters = list(loader.filter_by_size(min_size=6, max_size=50, max_clusters=100))
large_clusters = list(loader.filter_by_size(min_size=51, max_clusters=100))

# Balanced sample across cluster sizes
```

## Summary

- ✅ **Dataset is pre-clustered** - each row is a cluster
- ✅ **No additional clustering needed** - groups are already defined
- ✅ **Use streaming mode** - datasets are very large
- ✅ **Sample first** - test your code on small samples
- ✅ **Cluster ID** - first accession in the accession list
- ✅ **Parallel arrays** - accession, sequence, description lists are aligned

## Files in This Repository

1. **`inspect_uniref90.py`** - Quick data inspection
2. **`verify_uniref90_structure.py`** - Structure verification
3. **`uniref90_cluster_utils.py`** - Main utility library
4. **`UNIREF90_CLUSTERS_README.md`** - This documentation
5. **`uniref90_sample.csv`** - Sample data output (generated by scripts)

## Requirements

```bash
pip install datasets huggingface_hub pandas
```

## Questions?

The dataset comes from [microsoft/Dayhoff](https://huggingface.co/datasets/microsoft/Dayhoff) on HuggingFace.

For issues or questions about this utility, please refer to the dataset documentation or modify the utility scripts as needed.
