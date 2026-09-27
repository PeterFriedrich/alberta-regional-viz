# DATA_ISSUES — defects in data we do not control, and what we've told the publisher

**What belongs here:** a defect in a source we consume — plus the evidence, what
it breaks on our side, and **whether anyone has been told**. One row per defect,
newest first.

**What does NOT belong here:**

| this file | where it goes instead |
|---|---|
| how a source is shaped, its columns, its quirks | `data/DATA.md` |
| our own build work and backlog | `TODO.md` |
| a locked decision + its reasoning | `docs/DECISIONS.md` |
| an audit we ran over our own pipeline | `docs/AUDIT_LEDGER.md` |

⚠️ **The point of the file is the last column.** Findings that never leave the
repo are the standing failure mode: a measured upstream defect can be archived
unsent as a sub-item of a closed parent and go invisible. Status must be one of
**NOT SENT · SENT (date) · ACKNOWLEDGED (date) · FIXED (date) · WONTFIX**, and
"the artifact exists" is **not** sent.

---

| Date found | Source / dataset | Defect | Evidence | What it breaks here | Status |
|------------|------------------|--------|----------|---------------------|--------|
| 2026-09-27 | Municipal Affairs, Provincial 2026 Equalized Assessment Report (PDF, publication `2368-657x`) | The subtotal on p. 7 (the section of municipal districts / counties ending with Yellowhead County) prints NR Linear Property as **71,671,452,040**. Its 63 member rows sum to **71,674,452,040**, a $3,000,000 difference. The subtotal's own classes therefore don't add to its printed grand total (264,149,313,168), while the member rows' grand totals do. | `src/parse_equalized.py` fails on this row without its registered correction (`KNOWN_DEFECTS`); a column-sum comparison of the 63 rows against the subtotal isolates the single cell. | Nothing: subtotals are checks, not output. The correction is logged as a WARNING on every parse. | NOT SENT |
| 2026-09-27 | Municipal Affairs, Provincial 2009 and 2010 Equalized Assessment Reports (PDF) | Scanned images with no text layer. The 2008 report in the older series (`1844032`) is the same. The 1998–2007 and 2011–2026 reports all have text. | `pypdf`/`pdfplumber` extract ≤ 20 characters from the 19-page documents. | Taxation years 2007–2009 are missing from the core-vs-ring series, and that gap holds the City of Edmonton's 72% anchor year (2008). | NOT SENT (a request for text-layer versions or the underlying tables) |
