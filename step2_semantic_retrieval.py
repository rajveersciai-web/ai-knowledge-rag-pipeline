import sqlite3
import math
import re
from collections import Counter

# Connect to our AI Knowledge Warehouse
conn = sqlite3.connect("knowledge_base.db")
cursor = conn.cursor()

# Fetch all stored document chunks + metadata
cursor.execute("SELECT chunk_id, doc_title, department, chunk_index, chunk_text FROM document_chunks")
chunks = cursor.fetchall()
conn.close()

def tokenize(text):
    # Lowercase and extract clean words (ignoring common filler words)
    stop_words = {"the", "a", "an", "is", "are", "to", "of", "in", "for", "on", "with", "and", "or", "if", "at", "by"}
    words = re.findall(r"[a-z0-9_]+", text.lower())
    return [w for w in words if w not in stop_words]

# Build IDF (Inverse Document Frequency) weights so rare, specific keywords score higher
total_docs = len(chunks)
doc_freq = Counter()
tokenized_chunks = []

for row in chunks:
    tokens = tokenize(row[4])
    tokenized_chunks.append(tokens)
    for unique_word in set(tokens):
        doc_freq[unique_word] += 1

def retrieve_top_chunks(question, top_k=2):
    q_tokens = tokenize(question)
    scored_results = []

    for idx, row in enumerate(chunks):
        c_tokens = tokenized_chunks[idx]
        if not c_tokens:
            continue
        term_counts = Counter(c_tokens)
        score = 0.0
        for word in q_tokens:
            if word in term_counts:
                tf = term_counts[word] / len(c_tokens)
                idf = math.log((total_docs + 1) / (doc_freq[word] + 1)) + 1.0
                score += tf * idf
        if score > 0:
            scored_results.append((score, row))

    scored_results.sort(key=lambda x: x[0], reverse=True)
    return scored_results[:top_k]

# Test our AI Retrieval Engine on 3 realistic startup questions
sample_questions = [
    "What happens if an Enterprise customer credit card fails?",
    "How are customer databases encrypted and backed up?",
    "What is the API rate limit for Enterprise workspaces?"
]

print("=== AI RAG KNOWLEDGE RETRIEVAL ENGINE ===\n")
for q in sample_questions:
    print(f"QUESTION: {q}")
    matches = retrieve_top_chunks(q, top_k=1)
    for score, row in matches:
        print(f" -> TOP MATCH [Score: {score:.3f}] | Dept: {row[2]} | Doc: '{row[1]}' (Chunk #{row[3]})")
        print(f" CONTEXT: \"{row[4]}\"\n")