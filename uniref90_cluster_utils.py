#!/usr/bin/env python3
"""
Utility script for working with UniRef90 clustered data from HuggingFace.

The UniRef90 dataset is ALREADY ORGANIZED BY CLUSTER. Each row in the dataset
represents one UniRef90 cluster containing one or more protein sequences that
share ≥90% sequence identity.

Dataset structure:
- Each row = one cluster
- accession: list of UniRef90 IDs for all members
- sequence: list of protein sequences for all members
- description: list of descriptions for all members
- index: list of indices for all members

The cluster ID is the first accession in the accession list.
"""

from datasets import load_dataset
import pandas as pd
from typing import Dict, List, Optional, Iterator
import json


class UniRef90ClusterLoader:
    """Loader for UniRef90 clustered data from HuggingFace."""

    def __init__(self, split: str = "train", streaming: bool = True):
        """
        Initialize the loader.

        Args:
            split: Dataset split to load ('train', 'test', or 'valid')
            streaming: If True, load in streaming mode (recommended for large datasets)
        """
        self.split = split
        self.streaming = streaming
        self.dataset = None

    def load(self):
        """Load the dataset."""
        print(f"Loading UniRef90 {self.split} split (streaming={self.streaming})...")
        self.dataset = load_dataset(
            "microsoft/Dayhoff",
            "uniref90",
            split=self.split,
            streaming=self.streaming
        )
        print("Dataset loaded!")
        return self

    def iterate_clusters(self, max_clusters: Optional[int] = None) -> Iterator[Dict]:
        """
        Iterate through clusters.

        Args:
            max_clusters: Maximum number of clusters to return (None for all)

        Yields:
            Dictionary with cluster information:
            - cluster_id: The cluster ID (first accession)
            - cluster_size: Number of sequences in cluster
            - accessions: List of all accessions
            - sequences: List of all sequences
            - descriptions: List of all descriptions
            - indices: List of indices
        """
        if self.dataset is None:
            self.load()

        count = 0
        for example in self.dataset:
            yield {
                'cluster_id': example['accession'][0],
                'cluster_size': len(example['accession']),
                'accessions': example['accession'],
                'sequences': example['sequence'],
                'descriptions': example['description'],
                'indices': example['index']
            }

            count += 1
            if max_clusters is not None and count >= max_clusters:
                break

    def get_cluster_by_id(self, cluster_id: str, max_search: int = 10000) -> Optional[Dict]:
        """
        Find a cluster by its ID.

        Args:
            cluster_id: The UniRef90 cluster ID to search for
            max_search: Maximum number of clusters to search through

        Returns:
            Cluster dictionary or None if not found
        """
        for cluster in self.iterate_clusters(max_clusters=max_search):
            if cluster['cluster_id'] == cluster_id:
                return cluster
        return None

    def filter_by_size(
        self,
        min_size: int = 1,
        max_size: Optional[int] = None,
        max_clusters: Optional[int] = None
    ) -> Iterator[Dict]:
        """
        Filter clusters by size.

        Args:
            min_size: Minimum cluster size
            max_size: Maximum cluster size (None for unlimited)
            max_clusters: Maximum number of clusters to return

        Yields:
            Filtered clusters
        """
        for cluster in self.iterate_clusters():
            if cluster['cluster_size'] >= min_size:
                if max_size is None or cluster['cluster_size'] <= max_size:
                    yield cluster

                    if max_clusters is not None:
                        max_clusters -= 1
                        if max_clusters <= 0:
                            break

    def sample_clusters(self, n_samples: int = 100) -> List[Dict]:
        """
        Get a sample of clusters.

        Args:
            n_samples: Number of clusters to sample

        Returns:
            List of cluster dictionaries
        """
        clusters = []
        for cluster in self.iterate_clusters(max_clusters=n_samples):
            clusters.append(cluster)
        return clusters

    def get_statistics(self, n_samples: int = 1000) -> Dict:
        """
        Calculate statistics about the dataset.

        Args:
            n_samples: Number of clusters to sample for statistics

        Returns:
            Dictionary with statistics
        """
        clusters = self.sample_clusters(n_samples)
        sizes = [c['cluster_size'] for c in clusters]

        stats = {
            'total_clusters_sampled': len(clusters),
            'min_cluster_size': min(sizes),
            'max_cluster_size': max(sizes),
            'mean_cluster_size': sum(sizes) / len(sizes),
            'median_cluster_size': sorted(sizes)[len(sizes) // 2],
            'single_member_clusters': sum(1 for s in sizes if s == 1),
            'multi_member_clusters': sum(1 for s in sizes if s > 1),
            'large_clusters_100plus': sum(1 for s in sizes if s >= 100)
        }

        return stats


def export_clusters_to_jsonl(
    output_file: str,
    split: str = "train",
    max_clusters: Optional[int] = None,
    min_size: int = 1,
    max_size: Optional[int] = None
):
    """
    Export clusters to JSONL format.

    Args:
        output_file: Path to output JSONL file
        split: Dataset split to export
        max_clusters: Maximum number of clusters to export
        min_size: Minimum cluster size
        max_size: Maximum cluster size
    """
    loader = UniRef90ClusterLoader(split=split, streaming=True)
    loader.load()

    count = 0
    with open(output_file, 'w') as f:
        for cluster in loader.filter_by_size(min_size=min_size, max_size=max_size, max_clusters=max_clusters):
            f.write(json.dumps(cluster) + '\n')
            count += 1

            if count % 1000 == 0:
                print(f"Exported {count} clusters...")

    print(f"Exported {count} clusters to {output_file}")


def export_clusters_to_csv(
    output_file: str,
    split: str = "train",
    max_clusters: Optional[int] = None,
    flatten: bool = True
):
    """
    Export clusters to CSV format.

    Args:
        output_file: Path to output CSV file
        split: Dataset split to export
        max_clusters: Maximum number of clusters to export
        flatten: If True, export one row per sequence (flattened), otherwise one row per cluster
    """
    loader = UniRef90ClusterLoader(split=split, streaming=True)
    loader.load()

    if flatten:
        # One row per sequence
        rows = []
        for cluster in loader.iterate_clusters(max_clusters=max_clusters):
            cluster_id = cluster['cluster_id']
            for i in range(cluster['cluster_size']):
                rows.append({
                    'cluster_id': cluster_id,
                    'cluster_size': cluster['cluster_size'],
                    'accession': cluster['accessions'][i],
                    'sequence': cluster['sequences'][i],
                    'description': cluster['descriptions'][i],
                    'index': cluster['indices'][i]
                })

            if len(rows) % 1000 == 0:
                print(f"Processed {len(rows)} sequences...")

        df = pd.DataFrame(rows)
    else:
        # One row per cluster
        rows = []
        for cluster in loader.iterate_clusters(max_clusters=max_clusters):
            rows.append({
                'cluster_id': cluster['cluster_id'],
                'cluster_size': cluster['cluster_size'],
                'accessions': '|'.join(cluster['accessions']),
                'sequences': '|'.join(cluster['sequences']),
                'descriptions': '|'.join(cluster['descriptions'])
            })

            if len(rows) % 1000 == 0:
                print(f"Processed {len(rows)} clusters...")

        df = pd.DataFrame(rows)

    df.to_csv(output_file, index=False)
    print(f"Exported {len(df)} {'sequences' if flatten else 'clusters'} to {output_file}")


# Example usage
if __name__ == "__main__":
    print("="*100)
    print("UniRef90 Cluster Utility - Example Usage")
    print("="*100 + "\n")

    # Initialize loader
    loader = UniRef90ClusterLoader(split="train", streaming=True)
    loader.load()

    # Get statistics
    print("\n" + "="*100)
    print("DATASET STATISTICS (based on sample)")
    print("="*100 + "\n")

    stats = loader.get_statistics(n_samples=1000)
    for key, value in stats.items():
        print(f"{key}: {value}")

    # Sample some clusters
    print("\n" + "="*100)
    print("SAMPLE CLUSTERS")
    print("="*100 + "\n")

    sample_clusters = loader.sample_clusters(n_samples=5)
    for i, cluster in enumerate(sample_clusters, 1):
        print(f"\nCluster {i}:")
        print(f"  Cluster ID: {cluster['cluster_id']}")
        print(f"  Size: {cluster['cluster_size']} sequences")
        if cluster['cluster_size'] > 1:
            print(f"  First sequence: {cluster['sequences'][0][:50]}...")
            print(f"  Second sequence: {cluster['sequences'][1][:50]}...")
        else:
            print(f"  Sequence: {cluster['sequences'][0][:50]}...")

    # Filter by size
    print("\n" + "="*100)
    print("LARGE CLUSTERS (>100 members)")
    print("="*100 + "\n")

    large_clusters = list(loader.filter_by_size(min_size=100, max_clusters=3))
    for i, cluster in enumerate(large_clusters, 1):
        print(f"\nLarge cluster {i}:")
        print(f"  Cluster ID: {cluster['cluster_id']}")
        print(f"  Size: {cluster['cluster_size']} sequences")
        print(f"  Sample accessions: {cluster['accessions'][:3]}...")
