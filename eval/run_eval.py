# Step 11: Send each test question to the agent and score the answer.
import csv
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
CHAT_URL = os.getenv("CHAT_URL")

REFUSAL = "can only answer questions"        # text of the guardrail refusal
LOW_CONFIDENCE = "verify it confidently"    # text of the low-confidence message
CLARIFY = "which company"                   # text of the clarifying question


def ask_agent(question, session_id):
    # same request the chat window sends
    body = {"action": "sendMessage", "sessionId": session_id, "chatInput": question}
    response = requests.post(CHAT_URL, json=body, timeout=120)
    return response.json().get("output", "")


def answer_passed(row, answer):
    text = answer.lower()
    if row["type"] == "refuse":
        return REFUSAL in text
    if row["type"] == "clarify":
        return CLARIFY in text
    if row["type"] == "answer":
        # a real answer: not refused, not low confidence, not empty
        return REFUSAL not in text and LOW_CONFIDENCE not in text and len(text) > 50
    # type "fact": any one of the expected values must appear
    for option in row["expected"].split("|"):
        if option.lower() in text:
            return True
    return False


rows = []
file = open("eval/test_set.csv", encoding="utf-8")
for row in csv.DictReader(file):
    rows.append(row)
file.close()

results = []
for row in rows:
    start = time.time()
    # a new session for every question, so memory never affects the test
    answer = ask_agent(row["question"], "eval-" + row["id"] + "-" + str(int(start)))
    seconds = round(time.time() - start, 1)

    passed = answer_passed(row, answer)
    if row["page"] == "":
        page_ok = ""
    else:
        page_ok = ("page " + row["page"]) in answer

    results.append({"id": row["id"], "type": row["type"], "question": row["question"],
                    "passed": passed, "page_ok": page_ok, "seconds": seconds, "answer": answer})
    print(row["id"], "PASS" if passed else "FAIL", "| page ok:", page_ok, "|", seconds, "s")
    time.sleep(3)  # stay under the Cohere free-tier rate limit

# save every answer so failures can be inspected
output = open("eval/results.csv", "w", newline="", encoding="utf-8")
writer = csv.DictWriter(output, fieldnames=results[0].keys())
writer.writeheader()
writer.writerows(results)
output.close()

# summary
total_passed = 0
for r in results:
    if r["passed"]:
        total_passed = total_passed + 1

page_checked = 0
page_correct = 0
for r in results:
    if r["page_ok"] != "":
        page_checked = page_checked + 1
        if r["page_ok"]:
            page_correct = page_correct + 1

print("\nOverall accuracy:", total_passed, "/", len(results))
print("Citation accuracy:", page_correct, "/", page_checked)
for kind in ["fact", "answer", "clarify", "refuse"]:
    count = 0
    good = 0
    for r in results:
        if r["type"] == kind:
            count = count + 1
            if r["passed"]:
                good = good + 1
    print(" ", kind, ":", good, "/", count)
