# Evidence-Calibrated Self-Correcting RAG for Hallucination-Resistant Question Answering

CPU-first undergraduate research artifact. The system retrieves from a bounded SQuAD 2.0 corpus, produces an extractive candidate, verifies answer-bearing evidence, performs at most one retrieval-changing correction, calibrates exact-answer correctness, and abstains.

```bash
python -m pip install -e .
python scripts/prepare_data.py
python scripts/run_all.py
streamlit run app/dashboard.py
```

See `docs/reproducibility.md` for Windows commands. The included measurements are a CPU pilot, not publication-level evidence or a claim that hallucinations are eliminated.

