# Methodology

All SQuAD 2.0 dev context paragraphs form the bounded corpus; normal retrieval never receives the gold passage. The verifier target is an answer-bearing evidence proxy: a positive sentence contains an annotated answer span, while a weak negative is a sentence in that passage without an annotated answer. This is not entailment. The calibrator predicts exact-match correctness from a dedicated calibration split; the threshold is selected on validation.

B0 abstains without retrieval. B1 is word TF-IDF one-pass RAG. B2 adds latent-semantic retrieval and reciprocal-rank fusion. B3 adds verification and one correction. B4 adds correctness calibration and abstention.

