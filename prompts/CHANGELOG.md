# Prompt changelog

## Research Agent system prompt
- v1: grounded answers with citations as "(Company, page X)".
- v2: model copied "Company" literally. Citation rule now uses real examples "(TCS, page 108)". Lesson: models follow examples more than instructions.

## Input Guardrail - topical alignment prompt
- v1: vague scope prompt. "Capital of France" scored 0 (allowed), reached the agent: ~10s, ~4,560 tokens.
- v2: added off-topic list, scoring direction and 6 examples. France and Apple now blocked in ~2s (~1,950 tokens); Wipro and follow-up questions still pass.
