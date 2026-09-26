# Retrieval results

Normal queries are the ones with labeled spans. Hard-negative queries are excluded from Recall@k, Precision@5, and MRR.

A hard-negative query passes when no top-5 chunk has `rerank_score >= -5.0`. A missing rerank score does not count as a confident hit.

Normal queries: 20. Hard-negative queries: 3.

## Normal queries

| mode | Recall@1 | Recall@3 | Recall@5 | Precision@5 | MRR | queries |
| --- | --- | --- | --- | --- | --- | --- |
| lexical | 0.200 | 0.550 | 0.600 | 0.140 | 0.373 | 20 |
| semantic | 0.500 | 0.750 | 0.900 | 0.260 | 0.650 | 20 |
| hybrid_rrf | 0.350 | 0.650 | 0.750 | 0.190 | 0.539 | 20 |
| hybrid | 0.450 | 0.750 | 0.800 | 0.230 | 0.596 | 20 |

## By query_type

### lexical

| query_type | Recall@1 | Recall@3 | Recall@5 | Precision@5 | MRR | queries |
| --- | --- | --- | --- | --- | --- | --- |
| cross_file | 0.000 | 0.000 | 0.000 | 0.000 | 0.056 | 2 |
| keyword | 0.250 | 0.875 | 0.875 | 0.225 | 0.516 | 8 |
| paraphrase | 0.222 | 0.444 | 0.556 | 0.111 | 0.358 | 9 |
| speaker_specific | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1 |

### semantic

| query_type | Recall@1 | Recall@3 | Recall@5 | Precision@5 | MRR | queries |
| --- | --- | --- | --- | --- | --- | --- |
| cross_file | 0.000 | 1.000 | 1.000 | 0.300 | 0.417 | 2 |
| keyword | 0.625 | 0.875 | 1.000 | 0.300 | 0.775 | 8 |
| paraphrase | 0.556 | 0.667 | 0.889 | 0.244 | 0.656 | 9 |
| speaker_specific | 0.000 | 0.000 | 0.000 | 0.000 | 0.071 | 1 |

### hybrid_rrf

| query_type | Recall@1 | Recall@3 | Recall@5 | Precision@5 | MRR | queries |
| --- | --- | --- | --- | --- | --- | --- |
| cross_file | 0.500 | 0.500 | 0.500 | 0.100 | 0.550 | 2 |
| keyword | 0.500 | 0.875 | 0.875 | 0.250 | 0.708 | 8 |
| paraphrase | 0.222 | 0.556 | 0.778 | 0.178 | 0.439 | 9 |
| speaker_specific | 0.000 | 0.000 | 0.000 | 0.000 | 0.071 | 1 |

### hybrid

| query_type | Recall@1 | Recall@3 | Recall@5 | Precision@5 | MRR | queries |
| --- | --- | --- | --- | --- | --- | --- |
| cross_file | 0.000 | 0.500 | 1.000 | 0.200 | 0.375 | 2 |
| keyword | 0.625 | 0.875 | 0.875 | 0.275 | 0.750 | 8 |
| paraphrase | 0.444 | 0.778 | 0.778 | 0.222 | 0.574 | 9 |
| speaker_specific | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1 |

## Hard negatives

| id | query_type | lexical | semantic | hybrid_rrf | hybrid |
| --- | --- | --- | --- | --- | --- |
| 8 | speaker_specific | PASS | PASS | PASS | FAIL |
| 22 | hard_negative | PASS | PASS | PASS | FAIL |
| 23 | hard_negative | PASS | PASS | PASS | FAIL |
