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
| 2026-09-28 | Municipal Affairs, Equalized Assessment Reports 1999, 2001, 2003, 2017 (PDF, `1844032` / `2368-657x`) | Four one-year values that revert the next year, each printed with a consistent row total. **Airdrie NR = 0** in the 2017 report (1,478M the year before, 1,598M the year after). This is almost certainly an omission. **Sturgeon County NR 647.6M** in 2001 (289M / 287M on either side). **Devon NR 99.8M** in 1999 (43M / 39M), with M&E and linear also out of line. **Calgary linear 1,860M** in 2003 (1,003M / 1,142M). The last three may be genuine one-year rolls; the report can't tell. | `docs/FINDINGS_quick_audits_2026-09-28.md` §#4: continuity scan of `member_assessment.csv`, PDF lines quoted. | Replacing each with its neighbours' midpoint moves the core share: Calgary `nr` 2016 by −1.9 pp, Edmonton `nr` 2000 by +2.4 pp, Devon +0.5 pp, Calgary linear −0.3 pp. These account for most of the sawtooth in both series. Kept as printed until Peter decides how to treat them. | NOT SENT (ask whether amended figures exist) |
| 2026-09-28 | Municipal Affairs, 1999 Equalized Assessment Report (PDF, publication `1844032`) | Six of the report's subtotals, the grand total among them, print the Residential & Farmland column off by 1–5 dollars from the sum of their rows, with Total Equalized off by the same amount. For example, TOTAL CITIES prints 71,558,683,055 while its 14 rows sum to 71,558,683,054. The rows look rounded individually while the subtotals were summed unrounded. | `src/parse_equalized.py` `KNOWN_DEFECTS` names all twelve cells; each correction logs a WARNING on every parse. | Nothing: subtotals are checks, not output. | NOT SENT (low value, since the report is 27 years old; list it with the other sends, don't send it alone) |
| 2026-09-28 | Municipal Affairs, 2006 Equalized Assessment Report (PDF, publication `1844032`) | Two municipality rows print a Grand Total that is 1 dollar off their own classes: Bassano (printed 70,637,417; classes sum to 70,637,416) and Swan Hills (49,314,229; classes sum to 49,314,230). | `KNOWN_TOTAL_DEFECTS` in `src/parse_equalized.py`. | Nothing: a row's total is a check, and only its classes are output. | NOT SENT (as above) |
| 2026-09-28 | Municipal Affairs, 2001–2004 Equalized Assessment Reports (PDF, publication `1844032`) | Name typos. "Airdire" appears for Airdrie in the 2001–2004 reports. "Foothills No. 32, M.D. of" appears for No. 31 in 2001. | `data/regions.csv` carries both as aliases (in the notes column). | Nothing: matched by alias. | WONTFIX (historical documents; recorded so nobody "corrects" the alias away) |
| 2026-09-27 | Municipal Affairs, Provincial 2026 Equalized Assessment Report (PDF, publication `2368-657x`) | The subtotal on p. 7 (the section of municipal districts / counties ending with Yellowhead County) prints NR Linear Property as **71,671,452,040**. Its 63 member rows sum to **71,674,452,040**, a $3,000,000 difference. The subtotal's own classes therefore don't add to its printed grand total (264,149,313,168), while the member rows' grand totals do. | `src/parse_equalized.py` fails on this row without its registered correction (`KNOWN_DEFECTS`); a column-sum comparison of the 63 rows against the subtotal isolates the single cell. | Nothing: subtotals are checks, not output. The correction is logged as a WARNING on every parse. | NOT SENT |
| 2026-09-27 | Municipal Affairs, Provincial 2009 and 2010 Equalized Assessment Reports (PDF) | Scanned images with no text layer. The 2008 report in the older series (`1844032`) is the same. The 1998–2007 and 2011–2026 reports all have text. | `pypdf`/`pdfplumber` extract ≤ 20 characters from the 19-page documents. | Taxation years 2007–2009 are missing from the core-vs-ring series, and that gap holds the City of Edmonton's 72% anchor year (2008). | NOT SENT (a request for text-layer versions or the underlying tables) |
