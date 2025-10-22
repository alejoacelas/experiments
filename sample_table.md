# ProteinGym DMS Substitutions Dataset - Sample of 5 Rows

## Dataset Information
- **Dataset**: ProteinGym v1 - DMS Substitutions
- **Source**: [Hugging Face Dataset](https://huggingface.co/datasets/OATML-Markslab/ProteinGym_v1)
- **Total rows in first shard**: 493,154 rows
- **Total shards**: 5

## Column Descriptions
- **DMS_score**: Deep Mutational Scanning score (fitness/activity measure)
- **DMS_score_bin**: Binary version of DMS score (0.0 = low fitness, 1.0 = high fitness)
- **mutated_sequence**: Full protein sequence after mutation
- **target_seq**: Original wild-type protein sequence
- **mutant**: Specific mutations in format position:mutation (e.g., H56D means Histidine at position 56 changed to Aspartate)
- **DMS_id**: Identifier for the DMS experiment (protein_organism_study)

## Sample Data (5 Randomly Selected Rows)

| Row | DMS_score | DMS_score_bin | Mutant | DMS_id |
|-----|-----------|---------------|--------|--------|
| 1 | 0.000000 | 0.0 | H56D:I59V:L62F:S76N:L77I:I78R:E80Y:C81S:I82G | HIS7_YEAST_Pokusaeva_2019 |
| 2 | 0.000000 | 0.0 | N137S:Y140F:V142F:V143I:C157T:M159I:P161T:F163V | HIS7_YEAST_Pokusaeva_2019 |
| 3 | 0.981565 | 1.0 | L7F:V8I:I11V:I19V:I21L:L23I:K24E | HIS7_YEAST_Pokusaeva_2019 |
| 4 | 0.964665 | 1.0 | I66L:H67T:H86V:T92S:T93I | HIS7_YEAST_Pokusaeva_2019 |
| 5 | 0.000000 | 0.0 | H56E:G60A:L62F:S76N:L77I:I78V:V79L:C81A:I82V | HIS7_YEAST_Pokusaeva_2019 |

## Sequence Length Analysis

**Row 1:**
- Target sequence length: 220 amino acids
- Mutated sequence length: 220 amino acids
- Number of mutations: 9
- Mutations: `H56D:I59V:L62F:S76N:L77I:I78R:E80Y:C81S:I82G`

**Row 2:**
- Target sequence length: 220 amino acids
- Mutated sequence length: 220 amino acids
- Number of mutations: 8
- Mutations: `N137S:Y140F:V142F:V143I:C157T:M159I:P161T:F163V`

**Row 3:**
- Target sequence length: 220 amino acids
- Mutated sequence length: 220 amino acids
- Number of mutations: 7
- Mutations: `L7F:V8I:I11V:I19V:I21L:L23I:K24E`

**Row 4:**
- Target sequence length: 220 amino acids
- Mutated sequence length: 220 amino acids
- Number of mutations: 5
- Mutations: `I66L:H67T:H86V:T92S:T93I`

**Row 5:**
- Target sequence length: 220 amino acids
- Mutated sequence length: 220 amino acids
- Number of mutations: 9
- Mutations: `H56E:G60A:L62F:S76N:L77I:I78V:V79L:C81A:I82V`

## Example: Full Sequence Comparison for Row 3

**Target (wild-type):**
```
MTEQKALVKRITNETKIQIAISLKGGPLAIEHSIFPEKEAEAVAEQATQSQVINVHTGIGFLDHMIHALAKHSGWSLIVECIGDLHIDDHHTTEDCGIALGQAFKEALGAVRGVKRFGSGFAPLDEALSRAVVDLSNRPYAVVELGLQREKVGDLSCEMIPHFLESFAEASRITLHVDCLRGKNDHHRSESAFKALAVAIREATSPNGTNDVPSTKGVLM
```

**Mutated:**
```
MTEQKAFIKRVTNETKIQVALSIEGGPLAIEHSIFPEKEAEAVAEQATQSQVINVHTGIGFLDHMIHALAKHSGWSLIVECIGDLHIDDHHTTEDCGIALGQAFKEALGAVRGVKRFGSGFAPLDEALSRAVVDLSNRPYAVVELGLQREKVGDLSCEMIPHFLESFAEASRITLHVDCLRGKNDHHRSESAFKALAVAIREATSPNGTNDVPSTKGVLM
```

**Mutations:** L7F:V8I:I11V:I19V:I21L:L23I:K24E
**DMS Score:** 0.981565
