# Setup

Built and tested in GitHub Codespaces. You need free accounts for OpenAI, Pinecone, Cohere, Neon (Postgres), SerpAPI and Langfuse.

## 1. Reports
Download the 2025-26 annual reports from each company's investor-relations page and save them as `data/raw/tcs_ar.pdf`, `data/raw/infosys_ar.pdf` and `data/raw/wipro_ar.pdf`. This folder is git-ignored.

## 2. Ingestion (run once)
```bash
pip install -r requirements.txt
cp .env.example .env                  # add OPENAI_API_KEY and PINECONE_API_KEY
python ingestion/1_extract_text.py    # PDF -> page text
python ingestion/2_chunk_text.py      # page text -> 300-word chunks with metadata
python ingestion/3_embed_upload.py    # chunks -> embeddings -> Pinecone index "annual-reports"
```

## 3. Metrics database (Neon)
1. Create the table `financial_metrics` and the view `verified_metrics`.
2. Create a read-only role `agent_reader` that can only `SELECT` from the view.
3. Load the 24 values; see [METRICS_VERIFICATION.md](METRICS_VERIFICATION.md).

## 4. Agent (n8n)
```bash
npm install -g n8n
./scripts/start_n8n.sh                # port 5678, keep it Private
```
1. Import `n8n/Financial Research Agent.json`.
2. Add credentials in n8n: OpenAI, Pinecone, Cohere, Postgres (`agent_reader`), SerpAPI and Langfuse.
3. Publish the workflow, then put its chat webhook URL in `.env` as `CHAT_URL`.

API keys live only in n8n credentials, never in the repo.

## 5. App and evaluation
```bash
streamlit run app/streamlit_app.py    # port 8501
python eval/run_eval.py               # 20 test questions, results in eval/results.csv
```
