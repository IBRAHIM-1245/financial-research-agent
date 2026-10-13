# financial-research-agent

Agentic RAG system that answers questions on the 2025-26 annual reports of TCS, Infosys and Wipro, with page-level citations.

## How it works
- **Ingestion (Python):** PDF → page text → 300-word overlapping chunks with metadata → OpenAI embeddings → Pinecone
- **Agent (n8n):** AI Agent searches Pinecone, Cohere reranks 20 results to the best 5, and answers only from retrieved text with (Company, page) citations

## Status
- [x] Ingestion pipeline (2,755 chunks)
- [x] n8n RAG agent with Cohere rerank
- [ ] Input guardrails
- [ ] Answer verification and confidence score
- [ ] SQL tool for financial tables
- [ ] Langfuse tracing and evaluation

Setup: see `docs/SETUP.md`.

*For research and education only. Not investment advice. Not affiliated with the companies mentioned.*
