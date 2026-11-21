import sqlite3
from step2_semantic_retrieval import retrieve_top_chunks

conn = sqlite3.connect("knowledge_base.db")
cursor = conn.cursor()

print("\n=== RUNNING AI RAG PIPELINE QUALITY GATES ===\n")

# CHECK 1: Chunk Completeness — Verify chunks exist and none are empty
cursor.execute("SELECT COUNT(*) FROM document_chunks WHERE chunk_text IS NULL OR TRIM(chunk_text) = ''")
empty_chunks = cursor.fetchone()[0]
assert empty_chunks == 0, f"FAIL: Found {empty_chunks} empty document chunks!"

cursor.execute("SELECT COUNT(*) FROM document_chunks")
total_chunks = cursor.fetchone()[0]
assert total_chunks >= 9, f"FAIL: Expected at least 9 chunks, found {total_chunks}!"
print(f"[PASS] Check 1 — Chunk Completeness: {total_chunks} valid non-empty chunks verified.")

# CHECK 2: Metadata Integrity — Every chunk has a valid department tag
cursor.execute("SELECT COUNT(*) FROM document_chunks WHERE department IS NULL OR TRIM(department) = ''")
missing_dept = cursor.fetchone()[0]
assert missing_dept == 0, f"FAIL: Found {missing_dept} chunks missing department metadata!"
print("[PASS] Check 2 — Metadata Discovery Integrity: 100% of chunks have valid department tags.")

# CHECK 3: Retrieval Accuracy Test — Verify top-1 retrieval hits the exact expected department
test_hits = retrieve_top_chunks("How are customer databases encrypted?", top_k=1)
assert len(test_hits) > 0 and test_hits[0][1][2] == "Security", "FAIL: Retrieval engine missed Security chunk!"
print("[PASS] Check 3 — Top-1 Retrieval Recall: Query accurately retrieved 'Security' context chunk.")

conn.close()
print("\nALL AI RAG QUALITY GATES PASSED: Knowledge pipeline ready for production!")