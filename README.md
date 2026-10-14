# financial-research-agent

Agentic RAG system that answers questions on the 2025-26 annual reports of TCS, Infosys and Wipro, with page-level citations.

## How it works
- **Ingestion (Python):** PDF → page text → 300-word overlapping chunks with metadata → OpenAI embeddings → Pinecone
- **Agent (n8n):** Input guardrail → AI Agent searches Pinecone, Cohere reranks 20 results to the best 5 → answer with (Company, page) citations → verifier checks every fact against the sources → low-confidence answers are replaced with an honest message

## Status
- [x] Ingestion pipeline (2,755 chunks)
- [x] n8n RAG agent with Cohere rerank
- [x] Input guardrails (jailbreak, PII, secret keys, topic)
- [x] Answer verification with confidence score (OpenAI JSON schema)
- [x] SQL tool on 24 human-verified metrics (read-only role, verified view)
- [ ] Langfuse tracing and evaluation

Setup: see `docs/SETUP.md`.

*For research and education only. Not investment advice. Not affiliated with the companies mentioned.*
