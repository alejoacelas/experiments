# CORRECTED UniRef90 Dataset Analysis

## Critical Finding

You were **absolutely correct** to question the initial analysis! Here's what the dataset actually contains:

### The Truth About the Dataset Structure

1. **Each UniRef90 ID appears only ONCE** in the dataset (deduplicated)
2. **Rows are NOT grouped by UniRef90 cluster ID**
3. **Rows group DIFFERENT UniRef90 clusters** that share some higher-level similarity

## What We Found

### From analyzing 1000 rows (4584 sequences):
- **Every single UniRef90 ID is unique** - no duplicates found
- **4584 sequences = 4584 different UniRef90 clusters**

This means:
- The dataset is already deduplicated at the UniRef90 level
- Each sequence represents a different 90%-identity cluster
- You **cannot** group sequences by UniRef90 cluster ID because each cluster appears only once

## So What ARE the Rows?

Rows appear to group **related UniRef90 clusters** at a **higher level than 90% identity**. Patterns observed:

### Row Types:

**1. Single-sequence rows (~64%)**
- One UniRef90 cluster
- One protein sequence
- Example: `UniRef90_A0A410P257` - "Glycogen synthase"

**2. Multi-sequence rows (~36%)**
- Multiple DIFFERENT UniRef90 clusters
- Similar proteins (same family, different species/isoforms)
- Example row with 806 sequences:
  - `UniRef90_UPI00192F7BA0` - "titin isoform X48" (Crotalus tigris)
  - `UniRef90_UPI0023BAA08E` - "titin isoform X29" (Rissa tridactyla)
  - `UniRef90_A0A6J1TYV0` - "Titin isoform X16" (Notechis scutatus)
  - ... 803 more titin variants from different species

### Grouping Hypothesis

Rows likely represent one of:
1. **Protein families** (e.g., all titin variants)
2. **UniRef50 clusters** (50% identity - lower stringency than UniRef90)
3. **Functional groups** (proteins with similar function)
4. **Custom similarity grouping** by the dataset creators

The file `clustered_splits.json` (5.41 GB) mentioned in the repository likely contains information about this grouping criterion.

## Implications for Your Use Case

### If you want sequences grouped by UniRef90 cluster ID:

**Good news**: The dataset is already "grouped" - each UniRef90 cluster appears exactly once, so you can treat each sequence as representing its own cluster.

```python
from datasets import load_dataset

dataset = load_dataset("microsoft/Dayhoff", "uniref90", split="train", streaming=True)

for example in dataset:
    # Flatten the data - each sequence is its own UniRef90 cluster
    for i in range(len(example['accession'])):
        cluster_id = example['accession'][i]  # This IS the UniRef90 cluster ID
        sequence = example['sequence'][i]
        description = example['description'][i]

        # Process: one sequence per UniRef90 cluster
        print(f"Cluster: {cluster_id}, Sequence length: {len(sequence)}")
```

### If you want to understand the row-level grouping:

You need to investigate what criterion the dataset creators used. Options:

1. **Check the `clustered_splits.json` file** for grouping metadata
2. **Contact dataset creators** (Microsoft/Dayhoff team)
3. **Analyze protein families** using bioinformatics tools
4. **Treat rows as "related protein groups"** empirically

## Corrected Utility Script

Since each UniRef90 ID is unique, here's the appropriate utility:

```python
from datasets import load_dataset

class UniRef90DatasetLoader:
    """
    Loader for UniRef90 dataset where each sequence is a unique cluster.

    IMPORTANT: Each UniRef90 ID appears only once in the dataset.
    Rows group DIFFERENT UniRef90 clusters by some higher-level criterion.
    """

    def __init__(self, split="train"):
        self.split = split
        self.dataset = None

    def load(self):
        """Load dataset in streaming mode."""
        self.dataset = load_dataset(
            "microsoft/Dayhoff",
            "uniref90",
            split=self.split,
            streaming=True
        )
        return self

    def iterate_sequences(self, max_sequences=None):
        """
        Iterate through all sequences (flattened).

        Each sequence represents a unique UniRef90 cluster.

        Yields:
            dict with cluster_id, sequence, description, row_group_id
        """
        if self.dataset is None:
            self.load()

        count = 0
        for row_idx, example in enumerate(self.dataset):
            # Each row contains multiple DIFFERENT UniRef90 clusters
            for i in range(len(example['accession'])):
                yield {
                    'cluster_id': example['accession'][i],
                    'sequence': example['sequence'][i],
                    'description': example['description'][i],
                    'index': example['index'][i],
                    'row_group_id': row_idx  # The higher-level grouping
                }

                count += 1
                if max_sequences and count >= max_sequences:
                    return

    def get_row_groups(self, max_rows=None):
        """
        Get row-level groups (higher-level clustering).

        Each row contains multiple related UniRef90 clusters.

        Yields:
            dict with row_id, sequences (list), cluster_ids (list)
        """
        if self.dataset is None:
            self.load()

        for row_idx, example in enumerate(self.dataset):
            yield {
                'row_id': row_idx,
                'num_clusters': len(example['accession']),
                'cluster_ids': example['accession'],
                'sequences': example['sequence'],
                'descriptions': example['description']
            }

            if max_rows and row_idx >= max_rows - 1:
                return


# Example usage
if __name__ == "__main__":
    loader = UniRef90DatasetLoader(split="train")
    loader.load()

    # Example 1: Iterate through all sequences (each is a unique cluster)
    print("First 5 UniRef90 clusters:")
    for i, seq_data in enumerate(loader.iterate_sequences(max_sequences=5)):
        print(f"{i+1}. {seq_data['cluster_id']}: {seq_data['sequence'][:50]}...")

    # Example 2: Look at row-level groupings
    print("\n\nFirst 3 row groups (higher-level clustering):")
    for i, group in enumerate(loader.get_row_groups(max_rows=3)):
        print(f"\nRow {i+1}: {group['num_clusters']} UniRef90 clusters")
        print(f"  Sample cluster IDs: {group['cluster_ids'][:3]}")
```

## Summary - What You Should Know

✅ **Each UniRef90 ID is unique** - no duplicates in the dataset
✅ **Cannot group by UniRef90 cluster** - already one sequence per cluster
✅ **Rows = higher-level groups** - multiple different UniRef90 clusters
✅ **Row grouping criterion unknown** - likely protein family or UniRef50

### For Your Use Case:

**If you want UniRef90 clusters with their members:**
- This dataset won't help - it's already deduplicated
- You need the original UniRef90 database from UniProt
- Download from: https://www.uniprot.org/help/uniref

**If you want to work with unique protein sequences:**
- This dataset is perfect - already deduplicated
- Flatten the rows to get all sequences
- Each sequence is a representative of a 90%-identity cluster

**If you want the higher-level grouping:**
- Use the rows as-is
- Investigate `clustered_splits.json` for grouping metadata
- Or treat rows empirically as "related protein groups"

## Files Created

1. `reexamine_uniref90.py` - Corrected analysis
2. `investigate_clustering.py` - Proves no duplicate cluster IDs
3. `understand_row_grouping.py` - Analyzes row grouping patterns
4. `group_by_uniref90_cluster.py` - Grouping script (but finds no clusters with >1 member)
5. `CORRECTED_UNIREF90_ANALYSIS.md` - This document

## Next Steps

Please clarify what you actually need:

1. **UniRef90 clusters with multiple members?**
   → Use original UniRef90 from UniProt, not this dataset

2. **Deduplicated protein sequences?**
   → This dataset is perfect - flatten and use

3. **Understand row grouping?**
   → Need to investigate `clustered_splits.json` or contact dataset creators

4. **Something else?**
   → Let me know and I can help further!
