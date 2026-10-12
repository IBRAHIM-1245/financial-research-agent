# Step 5: Ask a question and see which chunks Pinecone finds.

import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
index = Pinecone(api_key=os.getenv("PINECONE_API_KEY")).Index("annual-reports")

question = input("Ask a question: ")
company = input("Company filter (TCS / Infosys / Wipro, or press Enter for all): ")

# turn the question into a vector, using the same model as the chunks
response = openai_client.embeddings.create(model="text-embedding-3-small", input=[question])
question_vector = response.data[0].embedding

# only filter by company if the user typed one
if company == "":
    results = index.query(vector=question_vector, top_k=5, include_metadata=True)
else:
    results = index.query(vector=question_vector, top_k=5, include_metadata=True,
                          filter={"company": company})

for match in results.matches:
    m = match.metadata
    print("\nScore:", round(match.score, 3), "|", m["company"], "| page", m["page"])
    print(m["text"][:200], "...")
