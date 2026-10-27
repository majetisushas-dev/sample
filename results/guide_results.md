# Guide results handout

## Built and trained
CPU-local hybrid retrieval, extractive answer selection, project-trained evidence-proxy classifier, one correction, calibrated correctness, citations, and abstention.

## Data and scale
SQuAD 2.0; 1204 passages; 150 test questions; 50 controlled-withholding cases.

## Measured pilot

method=B0_closed_book, em=0.000, f1=0.020, coverage=0.000, selective_risk=nan, recall_at_5=0.000, median_latency_ms=0.000, p95_latency_ms=0.000, mean_retrieval_calls=0.000, mean_generation_calls=0.000
method=B1_bm25, em=0.020, f1=0.148, coverage=1.000, selective_risk=0.980, recall_at_5=0.587, median_latency_ms=1.471, p95_latency_ms=1.802, mean_retrieval_calls=1.000, mean_generation_calls=1.000
method=B2_hybrid, em=0.013, f1=0.126, coverage=1.000, selective_risk=0.987, recall_at_5=0.500, median_latency_ms=1.589, p95_latency_ms=2.165, mean_retrieval_calls=1.000, mean_generation_calls=1.000
method=B3_corrected, em=0.013, f1=0.130, coverage=1.000, selective_risk=0.987, recall_at_5=0.513, median_latency_ms=3.471, p95_latency_ms=4.224, mean_retrieval_calls=1.800, mean_generation_calls=1.800
method=B4_full, em=0.000, f1=0.020, coverage=0.000, selective_risk=nan, recall_at_5=0.513, median_latency_ms=3.548, p95_latency_ms=4.408, mean_retrieval_calls=1.800, mean_generation_calls=1.800

ECE=0.195, Brier=0.049, AURC=0.993. Descriptive pilot values only.

## Limitations
Extractive heuristic, support proxy rather than entailment, bounded corpus, no human labels, and Windows not executed.
