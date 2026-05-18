"""HYDRA API — RAG pipeline constants.

All constants are module-level and read-only.
No Settings, no environment reads, no import-time side effects.
"""

from __future__ import annotations

# Embedding dimension — must match document_chunks.embedding vector(4096).
EMBEDDING_DIMENSION: int = 4096

# Default number of top-k chunks to retrieve.
DEFAULT_TOP_K: int = 5

# Maximum character count for evidence snippets returned in RetrievedDocument.
EVIDENCE_SNIPPET_CHARS: int = 500
