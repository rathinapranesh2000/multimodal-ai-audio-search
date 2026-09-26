# Known failures

Measured on the hybrid + rerank review and the follow-up score dump. No new search was run for this note.

## Query 17 — reranker failure

Query: How should a chatbot maintain conversation history?

Correct-file chunks had higher cosine similarity (0.777, 0.757) than the wrongly-promoted chunk (0.723). The reranker scored the wrong chunk 0.500, against 0.047 and 0.015 for those two.

| | file | speaker | start | end | cosine similarity | rerank score |
| --- | --- | --- | --- | --- | --- | --- |
| Promoted to hybrid rank 1 | AI_Engineering_Mock_Interview.wav | SPEAKER_01 | 450.02 | 479.96 | 0.722741 | 0.500 |
| Higher cosine, System_Design_of_ChatGPT.wav | System_Design_of_ChatGPT.wav | SPEAKER_00 | 0.00 | 38.14 | 0.777368 | 0.047 |
| Higher cosine, System_Design_of_ChatGPT.wav | System_Design_of_ChatGPT.wav | SPEAKER_01 | 231.28 | 246.94 | 0.756799 | 0.015 |

Chunk ids: `3ea4963a-5148-42eb-a9ea-a5aa1211fc23`, `a6dd2e05-3dd8-4c4e-9f6f-319417d74884`, `c5e1bd40-b690-4058-828a-0146acbfdb0d`.

## Query 20 — retrieval-stage miss

Query: How can a chatbot provide factual and reliable information?

Correct chunk: `System_Design_of_ChatGPT.wav`, SPEAKER_01, 299.62–323.48, `b4b46b6c-603b-490e-ab55-a757dfb5ae34`.

That chunk ranked 30th semantically in the full corpus. Reciprocal rank fusion placed it 7th of the fused 20 (`rrf` 0.026984, from lexical rank 3 and semantic rank 30, `k` 60). The reranker scored it 0.000156, rank 11 of those 20, so it stayed outside the returned top 5. The returned rank-5 rerank score was 0.001601.

## Query 21 — semantic embedding drift

Query: How can a retrieval system combine exact matching with meaning-based matching?

Correct chunk (hybrid search, rank fusion): `AI_Engineering_Mock_Interview.wav`, SPEAKER_00, 111.83–142.10, `250d3c66-3029-413e-b113-b2810af8e1fa`, cosine similarity 0.660679, semantic rank 5.

It ranked below these two chunks:

| semantic rank | cosine similarity | file | start | end |
| --- | --- | --- | --- | --- |
| 1 | 0.683568 | Google_Coding_Interview.wav | 197.21 | 228.77 |
| 2 | 0.683203 | AI_Engineering_Mock_Interview.wav | 79.36 | 111.83 |

Hybrid + rerank top 5 for this query did not include `250d3c66-3029-413e-b113-b2810af8e1fa`.
