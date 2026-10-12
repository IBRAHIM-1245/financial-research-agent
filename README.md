# financial-research-agent
Agentic RAG system that answers questions on Indian IT company annual reports (TCS, Infosys, Wipro). A LangGraph agent routes between Pinecone RAG with Cohere rerank, SQL on financial tables, and web search, then verifies answers with citations and confidence scores. Built with n8n, FastAPI, Streamlit and Langfuse.
