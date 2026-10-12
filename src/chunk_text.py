# Step 3: Split each page's text into smaller overlapping chunks for search.

import json

companies = ["tcs", "infosys", "wipro"]
CHUNK_WORDS = 300     # words per chunk
OVERLAP_WORDS = 50    # words repeated between chunks so ideas aren't cut in half

output = open("data/processed/chunks.jsonl", "w", encoding="utf-8")
total = 0

for key in companies:
    pages = open("data/processed/" + key + "_pages.jsonl", encoding="utf-8")
    for line in pages:
        record = json.loads(line)
        words = record["text"].split()
        start = 0
        chunk_number = 0
        while start < len(words):
            chunk_words = words[start:start + CHUNK_WORDS]
            chunk = {
                "id": key + "_p" + str(record["page"]) + "_c" + str(chunk_number),
                "company": record["company"],
                "page": record["page"],
                "text": " ".join(chunk_words),
            }
            output.write(json.dumps(chunk) + "\n")
            total = total + 1
            chunk_number = chunk_number + 1
            if start + CHUNK_WORDS >= len(words):   # reached end of page -> stop
                break
            start = start + CHUNK_WORDS - OVERLAP_WORDS
    pages.close()

output.close()
print("Total chunks:", total)
