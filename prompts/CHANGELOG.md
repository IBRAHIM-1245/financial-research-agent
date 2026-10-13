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
