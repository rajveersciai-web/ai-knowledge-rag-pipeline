# 🧠 AI-Ready Document & Knowledge RAG Pipeline

An end-to-end Retrieval-Augmented Generation (RAG) data engineering pipeline that ingests unstructured company policies, splits them into metadata-tagged chunks in SQL, ranks semantic relevance via TF-IDF scoring, and validates top-1 retrieval recall with automated quality gates.

## 🏗️ Pipeline Architecture
* **`step1_ingest_and_chunk.py`**: Parses unstructured company documents into clean sentence-level chunks with department and document metadata inside SQLite (`knowledge_base.db`).
* **`step2_semantic_retrieval.py`**: Implements a custom TF-IDF relevance ranking engine to retrieve the highest-scoring source context chunks for incoming queries.
* **`step3_rag_quality_check.py`**: Automated data quality and retrieval recall gatekeeper (`assert` checks) verifying chunk completeness, metadata tags, and top-1 retrieval accuracy.

## ▶️ Quick Start
```bash
python step1_ingest_and_chunk.py
python step2_semantic_retrieval.py
python step3_rag_quality_check.py
