# Prompt changelog

## Research Agent system prompt
- v1: grounded answers with citations as "(Company, page X)".
- v2: model copied "Company" literally. Citation rule now uses real examples "(TCS, page 108)". Lesson: models follow examples more than instructions.

## Input Guardrail - topical alignment prompt
- v1: vague scope prompt. "Capital of France" scored 0 (allowed), reached the agent: ~10s, ~4,560 tokens.
- v2: added off-topic list, scoring direction and 6 examples. France and Apple now blocked in ~2s (~1,950 tokens); Wipro and follow-up questions still pass.

## Answer Verifier
- v1: Structured Output Parser + Auto-Fix -> frequent format errors, fixer received "[object Object]". Replaced with OpenAI native JSON Schema response format: format errors eliminated.
- Bug: prompt field in Fixed mode, so {{ }} variables were sent as literal text and the verifier judged invented claims (0.4). Switched to Expression mode.
- Bug: agent did not pass sources. Enabled Return Intermediate Steps.
- v2 rules: Indian/international number formats are equal; citations checked against metadata (company, page). Correct TCS answer now scores 1.0.

## Answer Verifier
- v1: Structured Output Parser + Auto-Fix -> frequent format errors, fixer received "[object Object]". Replaced with OpenAI native JSON Schema response format: format errors eliminated.
- Bug: prompt field in Fixed mode, so {{ }} variables were sent as literal text and the verifier judged invented claims (0.4). Switched to Expression mode.
- Bug: agent did not pass sources. Enabled Return Intermediate Steps.
- v2 rules: Indian/international number formats are equal; citations checked against metadata (company, page). Correct TCS answer now scores 1.0.

## Research Agent v3 + SQL tool
- Added Financial_Metrics_SQL tool (read-only agent_reader login, verified_metrics view only).
- Prompt v3: SQL first for the 8 numeric metrics, search for everything else; operating-margin definition caveat.
- Bug: agent selected no source_page and copied pages from conversation memory (attrition cited revenue pages). Fix: tool query must select source_page; verifier now rejects any cited page not in the sources.

## Observability (Step 10)
- n8n built-in OpenTelemetry -> Langfuse OTLP endpoint: one trace per run, one span per node with timing.
- "Log to Langfuse" HTTP node -> Langfuse ingestion API: question, answer, tools, SQL/search inputs, sources, cited pages, verifier result, plus scores (verifier_confidence, supported). On Error = continue, so logging never blocks answers.
- Lesson: a trace with no span was accepted but not listed; added a span-create.
- Found via traces: agent sometimes runs the SQL tool twice for one question; verifier rejected a correct Wipro risks answer once (0.4) after passing it earlier (1.0).

## Verifier v3 + Prepare Sources (2026-10-14/15)
- Bug: same answer scored 1.0 then 0.4. Cause: verifier read raw nested-JSON tool output.
- Fix: "Prepare Sources" code node builds clean "[Company, page N] text" sources and checks every cited page against retrieved pages (citations_ok, bad_citations). Verifier now judges facts only.
- Agent prompt v4: company + topic in every search; cite only matching-company sources. Pinecone metadata filter on company.
- Confidence Check requires confidence >= 0.7 AND citations_ok. New Langfuse score: citations_ok.
- Result: TCS ESG 0.4 -> 1.0; Infosys risks passes with varied, correct pages.

## Web Search + Agent v9 (2026-10-15)
- Added Web_Search tool (HTTP Request -> SerpAPI, Query Auth, optimized to organic_results title/link/source/date/snippet).
- Prepare Sources reads web results as "[Web: site, date]"; verifier checks web facts only against web sources.
- Bugs found: future event described as past; analyst "Buy" rating and price target repeated; web citations missing "Web:" and contradictory dates.
- Fixes: today's date injected at top of system prompt (Expression mode); skip ratings/price targets; date and publisher rules; ANSWER FORMAT with one full example answer (rules alone did not fix the format, the example did).

## Error handling (2026-10-15)
- Input Guardrail, Research Agent, Answer Verifier: On Error -> error output -> "Error Message" node (friendly text, no technical details).
- Tested by setting an invalid model: agent failure -> friendly message. Guard LLM failure -> guardrail "fails closed" (refuses) - safe by design.
- Bug found: wires first came from success outputs, so the error message replaced every answer. Fixed by wiring only the Error branches.
- Bug found: system prompt was in Fixed mode, so the {{ $now }} date was sent as literal text. Switched to Expression.
