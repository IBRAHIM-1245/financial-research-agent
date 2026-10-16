# Step 4: Turn each chunk into a vector (embedding) and upload it to Pinecone.

import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()   # read API keys from .env

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("annual-reports")

BATCH_SIZE = 100   # send 100 chunks per request


# every field except "id" becomes metadata
def make_metadata(chunk):
    metadata = {}
    for field in chunk:
        if field != "id":
            metadata[field] = chunk[field]
    return metadata


# read all chunks into a list
chunks = []
file = open("data/processed/chunks.jsonl", encoding="utf-8")
for line in file:
    chunks.append(json.loads(line))
file.close()
print("Chunks to upload:", len(chunks))

for start in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[start:start + BATCH_SIZE]

    # collect the texts of this batch
    texts = []
    for chunk in batch:
        texts.append(chunk["text"])

    # one API call turns all texts in the batch into vectors
    response = openai_client.embeddings.create(model="text-embedding-3-small", input=texts)

    # pair each vector with its id and full metadata
    vectors = []
    for i in range(len(batch)):
        chunk = batch[i]
        vectors.append({
            "id": chunk["id"],
            "values": response.data[i].embedding,
            "metadata": make_metadata(chunk),
        })

    index.upsert(vectors=vectors)
    print("Uploaded", start + len(batch), "of", len(chunks))

print("Done.")
print(index.describe_index_stats())
