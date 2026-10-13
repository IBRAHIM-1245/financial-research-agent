# Financial metrics verification

24 values extracted by an LLM, each checked by hand against the PDF page.
8 extraction errors were found and fixed:

- Wipro net profit: reported in Rs million, stored as crore (10x too big) -> 13,265.5 crore
- Wipro revenue: not found by the extractor -> added manually (92,624 crore, p.96)
- Wipro EPS: 12.8 -> 12.60 (p.96)
- Wipro dividend: 6 -> 11 (p.17)
- Wipro employees and women %: round marketing numbers -> BRSR totals (246,990; 37.30%)
- Infosys dividend: final only (25) -> total (48)
- Infosys employees: permanent only -> total (352,095)
- TCS net profit: profit for the year -> attributable to shareholders, reported (49,210)

Definitions: employees and women % = BRSR "Total employees (D + E)";
net profit = reported, attributable to shareholders.
Caveat: operating margin definitions differ by company (TCS EBIT, Infosys adjusted, Wipro IT Services).
