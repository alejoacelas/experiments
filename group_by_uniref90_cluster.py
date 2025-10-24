#!/usr/bin/env python3
"""
Group UniRef90 sequences by their actual cluster ID.

IMPORTANT: The dataset rows are NOT organized by UniRef90 cluster ID.
Each row contains multiple DIFFERENT UniRef90 clusters. This script flattens
the data and reorganizes it by actual UniRef90 cluster ID.
"""

from datasets import load_dataset
from collections import defaultdict
from typing import Dict, List, Optional
import json
import pickle


class UniRef90ClusterGrouper:
    """Groups UniRef90 sequences by their cluster ID."""

    def __init__(self, split: str = "train"):
        """
        Initialize the grouper.

        Args:
            split: Dataset split to load ('train', 'test', or 'valid')
        """
        self.split = split
        self.clusters = defaultdict(lambda: {
            'accession': [],
            'sequence': [],
            'description': [],
            'index': []
        })

    def load_and_group(self, max_samples: Optional[int] = None):
        """
        Load dataset and group sequences by UniRef90 cluster ID.

        Args:
            max_samples: Maximum number of dataset rows to process (None for all)
                        Note: Each row contains multiple sequences

        Returns:
            Dictionary mapping cluster_id -> {accession, sequence, description, index lists}
        """
        print(f"Loading UniRef90 {self.split} split in streaming mode...")

        dataset = load_dataset(
            "microsoft/Dayhoff",
            "uniref90",
            split=self.split,
            streaming=True
        )

        print("Processing and grouping sequences by UniRef90 cluster ID...\n")

        row_count = 0
        total_sequences = 0

        for example in dataset:
            # Each row contains multiple sequences with different cluster IDs
            accessions = example['accession']
            sequences = example['sequence']
            descriptions = example['description']
            indices = example['index']

            # Flatten: process each sequence individually
            for i in range(len(accessions)):
                cluster_id = accessions[i]

                # Add this sequence to its cluster
                self.clusters[cluster_id]['accession'].append(accessions[i])
                self.clusters[cluster_id]['sequence'].append(sequences[i])
                self.clusters[cluster_id]['description'].append(descriptions[i])
                self.clusters[cluster_id]['index'].append(indices[i])

                total_sequences += 1

            row_count += 1

            if row_count % 100 == 0:
                print(f"Processed {row_count} rows, {total_sequences} sequences, "
                      f"{len(self.clusters)} unique clusters found")

            if max_samples is not None and row_count >= max_samples:
                break

        print(f"\n✓ Finished processing {row_count} rows")
        print(f"✓ Total sequences: {total_sequences}")
        print(f"✓ Unique UniRef90 clusters: {len(self.clusters)}")

        return dict(self.clusters)

    def get_cluster(self, cluster_id: str) -> Optional[Dict]:
        """
        Get all sequences for a specific cluster ID.

        Args:
            cluster_id: The UniRef90 cluster ID

        Returns:
            Dictionary with cluster data or None if not found
        """
        if cluster_id in self.clusters:
            cluster_data = self.clusters[cluster_id]
            return {
                'cluster_id': cluster_id,
                'cluster_size': len(cluster_data['accession']),
                **cluster_data
            }
        return None

    def get_statistics(self) -> Dict:
        """
        Calculate statistics about the clustered data.

        Returns:
            Dictionary with statistics
        """
        sizes = [len(data['accession']) for data in self.clusters.values()]

        if not sizes:
            return {
                'error': 'No data loaded yet. Call load_and_group() first.'
            }

        stats = {
            'total_clusters': len(self.clusters),
            'total_sequences': sum(sizes),
            'min_cluster_size': min(sizes),
            'max_cluster_size': max(sizes),
            'mean_cluster_size': sum(sizes) / len(sizes),
            'median_cluster_size': sorted(sizes)[len(sizes) // 2],
            'single_sequence_clusters': sum(1 for s in sizes if s == 1),
            'multi_sequence_clusters': sum(1 for s in sizes if s > 1)
        }

        return stats

    def save_clusters(self, output_file: str, format: str = 'pickle'):
        """
        Save clustered data to file.

        Args:
            output_file: Path to output file
            format: 'pickle', 'json', or 'jsonl'
        """
        if format == 'pickle':
            with open(output_file, 'wb') as f:
                pickle.dump(dict(self.clusters), f)
            print(f"Saved clusters to {output_file} (pickle format)")

        elif format == 'json':
            with open(output_file, 'w') as f:
                json.dump(dict(self.clusters), f)
            print(f"Saved clusters to {output_file} (JSON format)")

        elif format == 'jsonl':
            with open(output_file, 'w') as f:
                for cluster_id, data in self.clusters.items():
                    cluster_obj = {
                        'cluster_id': cluster_id,
                        'cluster_size': len(data['accession']),
                        **data
                    }
                    f.write(json.dumps(cluster_obj) + '\n')
            print(f"Saved clusters to {output_file} (JSONL format)")

        else:
            raise ValueError(f"Unknown format: {format}")

    def load_clusters(self, input_file: str, format: str = 'pickle'):
        """
        Load previously saved clustered data.

        Args:
            input_file: Path to input file
            format: 'pickle', 'json', or 'jsonl'
        """
        if format == 'pickle':
            with open(input_file, 'rb') as f:
                loaded = pickle.load(f)
                self.clusters = defaultdict(lambda: {
                    'accession': [],
                    'sequence': [],
                    'description': [],
                    'index': []
                }, loaded)
            print(f"Loaded {len(self.clusters)} clusters from {input_file}")

        elif format == 'json':
            with open(input_file, 'r') as f:
                loaded = json.load(f)
                self.clusters = defaultdict(lambda: {
                    'accession': [],
                    'sequence': [],
                    'description': [],
                    'index': []
                }, loaded)
            print(f"Loaded {len(self.clusters)} clusters from {input_file}")

        else:
            raise ValueError(f"Unknown format: {format}")

    def filter_by_size(self, min_size: int = 1, max_size: Optional[int] = None):
        """
        Get clusters filtered by size.

        Args:
            min_size: Minimum cluster size
            max_size: Maximum cluster size (None for unlimited)

        Returns:
            Dictionary of filtered clusters
        """
        filtered = {}
        for cluster_id, data in self.clusters.items():
            size = len(data['accession'])
            if size >= min_size:
                if max_size is None or size <= max_size:
                    filtered[cluster_id] = data

        return filtered


# Example usage
if __name__ == "__main__":
    print("="*100)
    print("UniRef90 Cluster Grouping Script")
    print("="*100 + "\n")

    print("IMPORTANT: Processing a sample of the dataset for demonstration.")
    print("For full dataset, remove max_samples parameter (will take much longer).\n")

    # Initialize grouper
    grouper = UniRef90ClusterGrouper(split="train")

    # Load and group a SAMPLE of the data
    # WARNING: Full dataset is very large! Start with a sample
    clusters = grouper.load_and_group(max_samples=100)

    # Get statistics
    print("\n" + "="*100)
    print("CLUSTERING STATISTICS")
    print("="*100 + "\n")

    stats = grouper.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

    # Show sample clusters
    print("\n" + "="*100)
    print("SAMPLE CLUSTERS")
    print("="*100 + "\n")

    # Find some multi-sequence clusters
    multi_clusters = grouper.filter_by_size(min_size=2, max_size=10)

    print(f"Found {len(multi_clusters)} clusters with 2-10 sequences\n")

    for i, (cluster_id, data) in enumerate(list(multi_clusters.items())[:3]):
        print(f"\nCluster {i+1}: {cluster_id}")
        print(f"  Size: {len(data['sequence'])} sequences")
        print(f"  Accessions: {data['accession']}")
        print(f"  First sequence: {data['sequence'][0][:60]}...")

    # Example: Save to file
    print("\n" + "="*100)
    print("SAVING CLUSTERED DATA")
    print("="*100 + "\n")

    grouper.save_clusters('uniref90_clustered_sample.pkl', format='pickle')
    print("\nYou can load this later with:")
    print("  grouper.load_clusters('uniref90_clustered_sample.pkl', format='pickle')")
