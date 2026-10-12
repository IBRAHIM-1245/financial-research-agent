# Setup

## Python (data ingestion, evaluation)
pip install -r requirements.txt

## n8n (agent workflow) - Node.js app, not a Python library
Requires Node.js 20+.
npm install -g n8n
n8n start            # opens on port 5678; keep the port Private
Import: n8n/financial_research_agent_v1.json
Then select your own credentials: OpenAI, Pinecone, Cohere.
