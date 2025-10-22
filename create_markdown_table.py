#!/usr/bin/env python3
"""
Create a nicely formatted markdown table from the sampled data
"""

import pandas as pd

# Read the CSV we created
df = pd.read_csv('proteingym_sample.csv')

# Create a markdown table with better formatting
print("# ProteinGym DMS Substitutions Dataset - Sample of 5 Rows\n")
print("## Dataset Information")
print(f"- **Dataset**: ProteinGym v1 - DMS Substitutions")
print(f"- **Source**: [Hugging Face Dataset](https://huggingface.co/datasets/OATML-Markslab/ProteinGym_v1)")
print(f"- **Total rows in first shard**: 493,154 rows")
print(f"- **Total shards**: 5\n")

print("## Column Descriptions")
print("- **DMS_score**: Deep Mutational Scanning score (fitness/activity measure)")
print("- **DMS_score_bin**: Binary version of DMS score (0.0 = low fitness, 1.0 = high fitness)")
print("- **mutated_sequence**: Full protein sequence after mutation")
print("- **target_seq**: Original wild-type protein sequence")
print("- **mutant**: Specific mutations in format position:mutation (e.g., H56D means Histidine at position 56 changed to Aspartate)")
print("- **DMS_id**: Identifier for the DMS experiment (protein_organism_study)\n")

print("## Sample Data (5 Randomly Selected Rows)\n")

# Create a simple table view
print("| Row | DMS_score | DMS_score_bin | Mutant | DMS_id |")
print("|-----|-----------|---------------|--------|--------|")
for idx, row in df.iterrows():
    mutant_short = row['mutant'][:50] + "..." if len(row['mutant']) > 50 else row['mutant']
    print(f"| {idx+1} | {row['DMS_score']:.6f} | {row['DMS_score_bin']:.1f} | {mutant_short} | {row['DMS_id']} |")

print("\n## Sequence Length Analysis\n")
for idx, row in df.iterrows():
    mut_len = len(row['mutated_sequence'])
    tgt_len = len(row['target_seq'])
    num_mutations = len(row['mutant'].split(':'))
    print(f"**Row {idx+1}:**")
    print(f"- Target sequence length: {tgt_len} amino acids")
    print(f"- Mutated sequence length: {mut_len} amino acids")
    print(f"- Number of mutations: {num_mutations}")
    print(f"- Mutations: `{row['mutant']}`")
    print()

print("## Example: Full Sequence Comparison for Row 3\n")
row3 = df.iloc[2]
print(f"**Target (wild-type):**")
print(f"```")
print(row3['target_seq'])
print(f"```\n")
print(f"**Mutated:**")
print(f"```")
print(row3['mutated_sequence'])
print(f"```\n")
print(f"**Mutations:** {row3['mutant']}")
print(f"**DMS Score:** {row3['DMS_score']}")
