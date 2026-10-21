# Streamlit chat UI for the Financial Research Agent.
# Sends each question to the n8n webhook, then shows the answer, the fact-check
# scores, a button for each annual report used, and source cards with the real
# report page and the number highlighted.
import base64
import io
import os
import re
import time
import uuid
import requests
import pdfplumber
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
CHAT_URL = os.getenv("CHAT_URL")

REFUSAL = "can only answer questions"       # text of the guardrail refusal
LOW_CONFIDENCE = "verify it confidently"    # text of the low-confidence message

PDF_FOLDER = "data/raw"                     # local copies of the reports (kept out of git)

# official investor pages where each company publishes its annual report
REPORT_LINKS = {
    "TCS": "https://www.tcs.com/investor-relations",
    "Infosys": "https://www.infosys.com/investors/reports-filings/annual-report.html",
    "Wipro": "https://www.wipro.com/investors/annual-reports/",
}

TOOL_NAMES = {
    "Financial_Metrics_SQL": "Searched the verified metrics (SQL)",
    "Annual_Report_Search": "Searched the annual reports",
    "Web_Search": "Searched recent news",
}

EXAMPLES = [
    "What is TCS revenue for 2025-26?",
    "Compare the attrition rate of TCS, Infosys and Wipro",
    "What risks does Wipro mention?",
    "Any recent news about Infosys?",
]

WAITING_STEPS = [
    "Checking your question (guardrail)",
    "Finding evidence in the reports and news",
    "Fact-checking the answer",
    "Collecting sources and page numbers",
]

# ---------- page setup and style ----------
st.set_page_config(page_title="Financial Research Agent", page_icon="📊", layout="wide")
st.markdown("""
<style>
footer {visibility: hidden;}
/* background: soft green glow + faint ledger lines, like accounting paper */
.stApp {
  background:
    repeating-linear-gradient(0deg, rgba(14,107,82,0.05) 0 1px, transparent 1px 28px),
    radial-gradient(circle at 85% 0%, #D6EBE1 0%, transparent 45%),
    radial-gradient(circle at 0% 100%, #E6F0EB 0%, transparent 40%),
    #F2F6F4;
}
/* each chat message on a clean white card so text stays easy to read */
[data-testid="stChatMessage"] {
  background: rgba(255,255,255,0.9);
  border: 1px solid #D3DDD8;
  border-radius: 14px;
  padding: 14px 18px;
  box-shadow: 0 6px 18px -12px rgba(10,40,30,0.35);
}
/* title in the brand green */
h1 {color: #0E6B52 !important;}
.block-container {max-width: 1150px;}
.tag {display:inline-block; padding:3px 12px; margin-right:6px; border-radius:999px;
      background:#DCEDE5; color:#0E6B52; font-size:13px; font-weight:600;}
.subtitle {color:#56675F; margin-top:-10px;}
.step {display:flex; align-items:center; gap:10px; margin:8px 0; color:#56675F;}
.spin {width:14px; height:14px; border:2px solid #CFE3D9; border-top-color:#0E6B52;
       border-radius:50%; animation:spin 0.8s linear infinite;}
@keyframes spin {to {transform: rotate(360deg);}}
</style>
""", unsafe_allow_html=True)

# ---------- memory for this browser tab ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = "ui-" + str(uuid.uuid4())


def ask_agent(question):
    # same request the n8n chat window sends
    body = {"action": "sendMessage", "sessionId": st.session_state.session_id, "chatInput": question}
    try:
        response = requests.post(CHAT_URL, json=body, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"output": "The agent took too long to answer. Please try again.", "error": True}
    except Exception:
        return {"output": "Could not reach the agent. Please check that n8n is running.", "error": True}


def find_pdf(company):
    # finds the PDF in data/raw whose file name contains the company name
    if not os.path.isdir(PDF_FOLDER):
        return ""
    for name in os.listdir(PDF_FOLDER):
        if name.lower().endswith(".pdf") and company.lower() in name.lower():
            return os.path.join(PDF_FOLDER, name)
    return ""


@st.cache_resource(show_spinner=False)
def pdf_bytes(pdf_path):
    # reads the PDF once and keeps it in memory for the download buttons
    with open(pdf_path, "rb") as file:
        return file.read()


def read_page(item):
    # turns a cited page like "TCS|35" into ("TCS", "35")
    found = re.search(r"(TCS|Infosys|Wipro)\D*(\d+)", str(item))
    if found:
        return found.group(1), found.group(2)
    return None, None


def find_excerpt(sources, company, page):
    # finds the text that came from this page in the sources
    label = "[" + company + ", page " + page + "]"
    start = sources.find(label)
    if start == -1:
        return ""
    text = sources[start + len(label):]
    end = text.find("\n[")
    if end != -1:
        text = text[:end]
    text = text.strip()
    if len(text) > 350:
        text = text[:350] + "..."
    return text


def numbers_in(answer):
    # numbers worth highlighting: ones with a comma or decimal point, like 2,67,021 or 13.7
    found = re.findall(r"\d[\d,]*\.?\d+", answer)
    numbers = []
    for number in found:
        if ("," in number or "." in number) and number not in numbers:
            numbers.append(number)
    return numbers


@st.cache_data(show_spinner=False)
def page_image(pdf_path, page, highlights):
    # renders one PDF page as an image and draws a yellow box around each number
    pdf = pdfplumber.open(pdf_path)
    pdf_page = pdf.pages[int(page) - 1]
    image = pdf_page.to_image(resolution=110)
    for text in highlights:
        for match in pdf_page.search(text):
            image.draw_rect(match, fill=(246, 226, 122, 110), stroke=(14, 107, 82), stroke_width=2)
    # put the picture straight into the page as base64 text
    # (Streamlit's separate /media image links are blocked in some Codespaces)
    buffer = io.BytesIO()
    image.annotated.save(buffer, format="PNG")
    pdf.close()
    return '<img src="data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode() + '" style="width:100%">'


def show_report_buttons(companies, cited, message_id):
    # for each report used: download the exact PDF the agent searched + the official website
    st.markdown("#### 📚 Reports used")
    columns = st.columns(len(companies))
    for i in range(len(companies)):
        company = companies[i]
        pages = []
        for cited_company, page in cited:
            if cited_company == company:
                pages.append(page)
        with columns[i]:
            st.markdown("**" + company + " Annual Report 2025-26**")
            st.caption("Pages cited: " + ", ".join(pages))
            pdf_path = find_pdf(company)
            if pdf_path:
                st.download_button("⬇️ Download full PDF", data=pdf_bytes(pdf_path),
                                   file_name=os.path.basename(pdf_path), mime="application/pdf",
                                   key="pdf-" + str(message_id) + "-" + company,
                                   use_container_width=True)
            if REPORT_LINKS.get(company):
                st.link_button("🌐 Official website", REPORT_LINKS[company], use_container_width=True)


def show_source_card(reply, company, page, highlights):
    with st.container(border=True):
        left, right = st.columns([2, 3])
        with left:
            st.markdown("**" + company + " Annual Report 2025-26**")
            st.markdown("📄 Page " + page)
            excerpt = find_excerpt(reply.get("sources", ""), company, page)
            if excerpt:
                st.caption("Text used: “" + excerpt + "”")
            if highlights:
                st.caption("🟨 Highlighted on the page: " + ", ".join(highlights))
            st.caption("The page on the right is from the same PDF the agent searched.")
        with right:
            pdf_path = find_pdf(company)
            if pdf_path:
                try:
                    st.markdown(page_image(pdf_path, page, highlights), unsafe_allow_html=True)
                except Exception:
                    st.caption("Could not show this page.")
            else:
                st.caption("Report file not found in " + PDF_FOLDER + ".")


def show_answer(reply, seconds, message_id):
    answer = reply.get("output", "Sorry, no answer came back.")

    if reply.get("error"):
        st.error(answer)
        return
    if REFUSAL in answer:
        st.markdown(answer)
        st.caption("🛡️ Blocked by the input guardrail: off-topic or unsafe question.")
        return

    # 1. the answer
    st.markdown(answer)
    if LOW_CONFIDENCE in answer:
        st.warning("The fact-checker could not confirm the answer, so it was withheld.")

    # 2. score cards
    left, middle, right = st.columns(3)
    confidence = reply.get("confidence")
    if confidence is not None:
        left.metric("Fact-check confidence", str(round(float(confidence) * 100)) + "%")
    if "citations_ok" in reply:
        middle.metric("Citations verified", "Yes ✅" if reply["citations_ok"] else "No ⚠️")
    right.metric("Time taken", str(seconds) + " s")

    # 3. which companies and pages were cited (no repeats)
    companies = []
    cited = []
    for item in reply.get("cited_pages", []):
        company, page = read_page(item)
        if company is None or (company, page) in cited:
            continue
        cited.append((company, page))
        if company not in companies:
            companies.append(company)

    # 4. one button per report, then a card per page
    if companies:
        show_report_buttons(companies, cited, message_id)
        st.markdown("#### 📄 Check it yourself")
        highlights = numbers_in(answer)
        for company, page in cited:
            show_source_card(reply, company, page, highlights)

    # 5. news cards
    news = reply.get("web_sources", [])
    if news:
        st.markdown("#### 🌐 Recent news used")
    for item in news:
        with st.container(border=True):
            st.markdown(item.get("title", "News"))
            if item.get("link"):
                st.link_button("Read article", item["link"])

    # 6. process steps
    with st.expander("How this answer was made"):
        st.markdown("✅ Question checked by the guardrail: on topic")
        tools = []
        for tool in reply.get("tools_used", []):
            if tool not in tools:
                tools.append(tool)
        if len(tools) == 0:
            st.markdown("✅ Answered without a tool call")
        for tool in tools:
            st.markdown("✅ " + TOOL_NAMES.get(tool, tool))
        st.markdown("✅ Answer fact-checked against the sources")


# ---------- sidebar ----------
with st.sidebar:
    st.header("📊 Financial Research Agent", anchor=False)
    if st.button("➕ New chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = "ui-" + str(uuid.uuid4())
        st.rerun()

    st.subheader("Try asking", anchor=False)
    for example in EXAMPLES:
        if st.button(example, key="side-" + example, use_container_width=True):
            st.session_state.pending = example

    st.subheader("About", anchor=False)
    st.caption("Answers come from the 2025-26 annual reports of TCS, Infosys and Wipro, "
               "a table of 24 hand-verified metrics, and recent news. Every answer is "
               "fact-checked and shows the report page it came from.")
    st.caption("For research and education only. Not investment advice. "
               "Not affiliated with the companies mentioned.")

# ---------- header ----------
st.title("Financial Research Agent", anchor=False)
st.markdown('<p class="subtitle">Ask about the 2025-26 annual reports. Every number comes with its page.</p>',
            unsafe_allow_html=True)
st.markdown('<span class="tag">TCS</span><span class="tag">Infosys</span><span class="tag">Wipro</span>',
            unsafe_allow_html=True)
st.write("")

# ---------- welcome screen ----------
if len(st.session_state.messages) == 0 and "pending" not in st.session_state:
    st.success("👋 Hi! Pick a question below or type your own.")
    left, right = st.columns(2)
    for i in range(len(EXAMPLES)):
        column = left if i % 2 == 0 else right
        if column.button(EXAMPLES[i], key="main-" + str(i), use_container_width=True):
            st.session_state.pending = EXAMPLES[i]
            st.rerun()

# ---------- chat so far ----------
for i in range(len(st.session_state.messages)):
    message = st.session_state.messages[i]
    with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "📊"):
        if message["role"] == "user":
            st.markdown(message["content"])
        else:
            show_answer(message["reply"], message["seconds"], i)

# ---------- new question ----------
question = st.chat_input("Ask about TCS, Infosys or Wipro...")
if "pending" in st.session_state:
    question = st.session_state.pop("pending")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="📊"):
        # every step gets its own spinner while the agent works
        waiting = st.empty()
        html = ""
        for step in WAITING_STEPS:
            html = html + '<div class="step"><div class="spin"></div>' + step + '</div>'
        waiting.markdown(html, unsafe_allow_html=True)

        start = time.time()
        reply = ask_agent(question)
        seconds = round(time.time() - start, 1)

        waiting.empty()   # remove the spinners
        show_answer(reply, seconds, len(st.session_state.messages))

    st.session_state.messages.append({"role": "assistant", "content": question,
                                      "reply": reply, "seconds": seconds})