# Architecture

Question → word TF-IDF and latent-semantic SVD retrieval → reciprocal-rank fusion → sentence selection → deterministic extractive candidate → project-trained answer-bearing-evidence proxy → at most one expanded query and new retrieval → calibrated exact-match probability → answer with citation or abstention.

The dense channel is corpus-trained latent semantic indexing, not a sentence-transformer. Correction appends novel evidence terms and excludes the selected chunk. Decisions are logged without hidden chain-of-thought.

