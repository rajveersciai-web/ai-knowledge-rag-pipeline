import sqlite3
from datetime import datetime, timezone

# Connect to our AI Knowledge Warehouse database
conn = sqlite3.connect("knowledge_base.db")
cursor = conn.cursor()

# Create table storing cleaned document chunks + metadata for RAG retrieval
cursor.execute("""
CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_title TEXT NOT NULL,
    department TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    word_count INTEGER NOT NULL,
    ingested_at TEXT NOT NULL
)
""")

# Clear old chunks so re-running stays idempotent (zero duplicate chunks)
cursor.execute("DELETE FROM document_chunks")

# Realistic raw SaaS company knowledge documents (Policies, Billing, Security, Onboarding)
raw_documents = [
    {
        "title": "Enterprise Refund & Cancellation Policy",
        "department": "Billing",
        "content": (
            "Enterprise customers on annual contracts may cancel at any time with 30 days written notice before renewal. "
            "Full refunds are issued within 14 business days if requested within the first 30 days of initial activation. "
            "If an Enterprise invoice fails due to an expired card, the account enters a 14-day past_due grace period before suspension."
        )
    },
    {
        "title": "SOC2 Data Security & Encryption Standards",
        "department": "Security",
        "content": (
            "All customer production databases are encrypted at rest using AES-256 and in transit via TLS 1.3. "
            "API keys and database credentials must never be hardcoded in source repositories and must be stored in environment secrets. "
            "Automated daily backups are retained for 30 days across isolated cloud regions."
        )
    },
    {
        "title": "API Rate Limits & Webhook Retry Guide",
        "department": "Engineering",
        "content": (
            "Standard Pro tier workspaces are limited to 1,000 API requests per minute, while Enterprise workspaces receive 10,000 requests per minute. "
            "When an external webhook fails with HTTP 429 or 503, the ingestion pipeline automatically retries with exponential backoff up to 3 times. "
            "All failed payloads are logged to the dead-letter audit table for engineering inspection."
        )
    }
]

ingested_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
total_chunks = 0

# Split each document into sentence-level chunks with rich metadata
for doc in raw_documents:
    sentences = [s.strip() + "." for s in doc["content"].split(".") if s.strip()]
    for idx, sentence in enumerate(sentences, start=1):
        words = len(sentence.split())
        cursor.execute("""
        INSERT INTO document_chunks (doc_title, department, chunk_index, chunk_text, word_count, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (doc["title"], doc["department"], idx, sentence, words, ingested_time))
        total_chunks += 1

conn.commit()
conn.close()

print(f"SUCCESS: Ingested {len(raw_documents)} documents into {total_chunks} searchable RAG chunks in knowledge_base.db!")