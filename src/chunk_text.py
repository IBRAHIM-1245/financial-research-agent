# Step 3: Split each page's text into smaller overlapping chunks, with full metadata.

import json

companies = {
    "tcs": {"name": "TCS", "ticker": "TCS"},
    "infosys": {"name": "Infosys", "ticker": "INFY"},
    "wipro": {"name": "Wipro", "ticker": "WIPRO"},
}
REPORT_YEAR = "2025-26"
CHUNK_WORDS = 300     # words per chunk
OVERLAP_WORDS = 50    # words repeated between chunks so ideas aren't cut in half

output = open("data/processed/chunks.jsonl", "w", encoding="utf-8")
total = 0

for key in companies:
    info = companies[key]
    pages = open("data/processed/" + key + "_pages.jsonl", encoding="utf-8")
    for line in pages:
        record = json.loads(line)
        words = record["text"].split()
        start = 0
        chunk_index = 0
        while start < len(words):
            chunk_words = words[start:start + CHUNK_WORDS]
            chunk = {
                "id": key + "_p" + str(record["page"]) + "_c" + str(chunk_index),
                "company": info["name"],
                "ticker": info["ticker"],
                "report_year": REPORT_YEAR,
                "doc_type": "annual_report",
                "source_file": key + "_ar.pdf",
                "page": record["page"],
                "chunk_index": chunk_index,
                "word_count": len(chunk_words),
                "text": " ".join(chunk_words),
            }
            output.write(json.dumps(chunk) + "\n")
            total = total + 1
            chunk_index = chunk_index + 1
            if start + CHUNK_WORDS >= len(words):   # reached end of page -> stop
                break
            start = start + CHUNK_WORDS - OVERLAP_WORDS
    pages.close()

output.close()
print("Total chunks:", total)
