# Step 2: Read each annual report PDF and save its text page by page.

import json          # to save each page as a JSON line
import os            # to create the output folder
import pdfplumber    # to read text from PDF pages

companies = {"tcs": "TCS", "infosys": "Infosys", "wipro": "Wipro"}

os.makedirs("data/processed", exist_ok=True)   # make the folder if it's missing

for key in companies:
    name = companies[key]
    pdf_file = "data/raw/" + key + "_ar.pdf"
    out_file = "data/processed/" + key + "_pages.jsonl"

    kept = 0
    skipped = 0

    pdf = pdfplumber.open(pdf_file)
    output = open(out_file, "w", encoding="utf-8")

    page_number = 1
    for page in pdf.pages:
        text = page.extract_text()          # get the text of this page
        if text is None:                    # image-only page has no text
            text = ""
        text = " ".join(text.split())       # remove extra spaces and line breaks

        if len(text) < 50:                  # almost empty page -> skip it
            skipped = skipped + 1
        else:
            record = {"company": name, "page": page_number, "text": text}
            output.write(json.dumps(record) + "\n")
            kept = kept + 1

        page_number = page_number + 1

    output.close()
    pdf.close()
    print(name, ":", len(pdf.pages), "pages, kept", kept, ", skipped", skipped)
