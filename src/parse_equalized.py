"""Parse the provincial equalized assessment report PDFs into a long table.

Two layout families. Reports 2005 on carry 7 classes (+ total); reports
1998–2004 carry 4, and their column ORDER varies (M&E prints left of linear),
so those columns are named from the header's x-positions
(docs/SPEC_phase1.md §"Phase 1b").

Values are placed by x-position, never by order: the 2012–2016 layouts print
zero as a blank cell, so a row can have fewer numbers than columns
(docs/SPEC_phase1.md §"Parser approach"). A value in the wrong column still sums
to its row total, so column alignment is checked on its own.

Usage:
    python src/parse_equalized.py [--raw data/raw/equalized] [--out data/processed/equalized_long.csv]
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jsonlog import event, get_logger  # noqa: E402

log = get_logger("parse_equalized")

REPO = Path(__file__).resolve().parent.parent
NUM = re.compile(r"^\d{1,3}(?:,\d{3})*$")
# A value printed without thousands separators (2004, Strathcona County's row).
# Only ever accepted in the value zone, where no name can reach.
PLAIN = re.compile(r"^\d{4,}$")
# A value cut off at the right edge of its cell, e.g. "5,671,306,0" with "53"
# on the next line (2011 report, a subtotal).
FRAG = re.compile(r"^\d{1,3}(?:,\d{3})*,\d{1,2}$")
ROW_TOL = 3.0      # pt: words within this vertical distance are one row
DASH_TOL = 15.0    # pt: a printed "-" (zero) sits near, not on, its column's right edge
ALIGN_TOL = 3.0    # pt: a value's right edge must sit this close to its column's
# Bold (sub)total rows sit 3–5 pt left of their columns. Looser is safe for
# them only: a subtotal is reconciled column-by-column against the rows above.
SUB_TOL = 8.0
CONT_GAP = 14.0    # pt: a name-only line this close below a data row continues its name
PRE_GAP = 30.0     # pt: ...otherwise, one this close above the next data row prefixes it

CLASSES_RAIL = ["residential", "farmland", "nr", "nr_linear", "nr_railway",
                "nr_cogen_me", "me", "grand_total"]
CLASSES_NO_RAIL = [c for c in CLASSES_RAIL if c != "nr_railway"]
# Reports 1998–2004: residential includes farmland, and NR includes railway
# (docs/SPEC_phase1.md §"Phase 1b"). Header keyword -> class; order comes
# from where each keyword prints.
OLD_HEADER = [("RESIDENTIAL", "residential_incl_farmland"), ("NON", "nr_incl_railway"),
              ("MACHINERY", "me"), ("LINEAR", "nr_linear"), ("TOTAL", "grand_total")]
# Section headings of the 1998–2004 reports print in the NAME column
# ("CITIES", "Rural Municipalities", 1999's "SPECIAL AREAS & REDWOOD
# MEADOWS"); a line made only of these words is a heading, not a name prefix.
HEADING_WORDS = {"CITIES", "COUNTIES", "TOWNS", "VILLAGES", "SUMMER", "MUNICIPAL",
                 "RURAL", "SPECIALIZED", "MUNICIPALITIES", "IMPROVEMENT", "DISTRICTS",
                 "SPECIAL", "AREAS", "&", "REDWOOD", "MEADOWS"}
MONTHS = {"January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"}

# Publisher errors in the PDFs, corrected by name, never by loosening a check.
# (report_year, class, printed value) -> value the rows above it sum to.
# Only ever a subtotal cell: subtotals are checks, not output. docs/DATA_ISSUES.md.
KNOWN_DEFECTS = {
    (2026, "nr_linear", 71_671_452_040): 71_674_452_040,
    # 1999, every subtotal but one: residential & farmland off by 1–5 and the
    # total by the same amount — rows rounded, subtotals summed unrounded.
    (1999, "residential_incl_farmland", 71_558_683_055): 71_558_683_054,   # cities
    (1999, "grand_total", 98_436_727_789): 98_436_727_788,
    (1999, "residential_incl_farmland", 3_859_370_780): 3_859_370_781,     # specialized
    (1999, "grand_total", 8_700_256_547): 8_700_256_548,
    (1999, "residential_incl_farmland", 16_767_679_527): 16_767_679_524,   # rural
    (1999, "grand_total", 49_692_709_598): 49_692_709_595,
    (1999, "residential_incl_farmland", 11_889_537_834): 11_889_537_839,   # towns
    (1999, "grand_total", 17_185_573_731): 17_185_573_736,
    (1999, "residential_incl_farmland", 809_085_386): 809_085_388,         # villages
    (1999, "grand_total", 1_309_223_858): 1_309_223_860,
    (1999, "residential_incl_farmland", 106_278_622_081): 106_278_622_086,  # grand total
    (1999, "grand_total", 179_322_309_961): 179_322_309_966,
}
# A data row's printed total off by rounding. Totals are checks, not output,
# so correcting one moves no published number. docs/DATA_ISSUES.md.
KNOWN_TOTAL_DEFECTS = {
    (2006, "Bassano", 70_637_417): 70_637_416,
    (2006, "Swan Hills", 49_314_229): 49_314_230,
}


class ParseError(Exception):
    pass


def _rows(words):
    """Group words into rows by vertical position (sorted top to bottom)."""
    rows = []
    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if rows and abs(w["top"] - rows[-1]["top"]) <= ROW_TOL:
            rows[-1]["words"].append(w)
        else:
            rows.append({"top": w["top"], "words": [w]})
    for r in rows:
        r["words"] = _join_split_numbers(sorted(r["words"], key=lambda w: w["x0"]))
    return rows


def _join_split_numbers(words):
    """Re-join a number the PDF split into two words with no real gap, e.g.
    "7" + "32,059,142" or "2" + ",255,187,010" (1999 report, total column)."""
    out = []
    for w in words:
        prev = out[-1] if out else None
        if (prev and w["x0"] - prev["x1"] <= 1.0 and re.fullmatch(r"\d{1,3}", prev["text"])
                and NUM.match(prev["text"] + w["text"])):
            out[-1] = {**prev, "text": prev["text"] + w["text"], "x1": w["x1"]}
            continue
        out.append(w)
    return out


def _header_bottom(rows):
    """Top of the last header row, or None on a page with no table.

    The header is the row carrying 'Equipment' with 'Linear' and 'Residential'
    within 20 pt above it (prose mentioning "Machinery & Equipment and Linear
    Property" has no Residential beside it), plus any number-free header line
    wrapped just below it ("land)" in 2004)."""
    for i, r in enumerate(rows):
        if not any(w["text"].upper() == "EQUIPMENT" for w in r["words"]):
            continue
        near = {w["text"].upper() for q in rows if 0 <= r["top"] - q["top"] <= 20
                for w in q["words"]}
        if "LINEAR" not in near or "RESIDENTIAL" not in near:
            continue
        hb = r["top"]
        for q in rows[i + 1:]:
            if q["top"] - r["top"] > 12 or any(NUM.match(w["text"]) for w in q["words"]):
                break
            hb = q["top"]
        return hb
    return None


def _old_classes(rows, hb):
    """Class order of a 1998–2004 layout, read from the header's x-positions."""
    head = [w for r in rows if hb - 40 <= r["top"] <= hb for w in r["words"]]
    at = {}
    for key, cls in OLD_HEADER:
        xs = [w["x0"] for w in head if w["text"].upper().startswith(key)
              or (key == "TOTAL" and w["text"].upper() == "GRAND")]
        if not xs:
            raise ParseError(f"old-layout header has no {key!r} column")
        at[cls] = min(xs)
    order = sorted(at, key=at.get)
    if order[-1] != "grand_total":
        raise ParseError(f"old-layout header puts a column right of the total: {order}")
    return order


def _values_left(rows, hb):
    """x below which a number is part of a name ("No. 31"), not a value: a
    little left of the Residential header, since wide values overhang it."""
    xs = [w["x0"] for r in rows if r["top"] <= hb for w in r["words"]
          if w["text"].upper() == "RESIDENTIAL"]
    if not xs:
        raise ParseError("header has no 'Residential' column")
    return min(xs) - 25


def _is_boilerplate(row):
    """Report-date / prepared-on / page-number lines, above or below the table."""
    t = [w["text"] for w in row["words"]]
    return (t[:2] in (["Report", "Date:"], ["Calculation", "Date:"])
            or t[:1] in (["Prepared:"], ["Classification:"])
            or (len(t) == 2 and t[0] == "Page" and t[1].isdigit())
            # "December 1, 1997 1", "November 1, 2000 1 of 1" (1998–2001 footers)
            or (len(t) >= 3 and t[0] in MONTHS and re.fullmatch(r"\d{1,2},", t[1])
                and re.fullmatch(r"\d{4}", t[2]))
            # "2/25/99 8", "2/25/99", a garbled "44282<< :" (1999–2000 page
            # footers): no letters anywhere. A data row has a lettered name,
            # and an unnamed subtotal has 5+ values.
            or (len(t) <= 2 and not any(re.search(r"[A-Za-z]", x) for x in t)))


TOTAL_WORDS = {"SUB", "TOTAL", "SUBTOTAL", "GRAND", "TOTALS"}


def _is_subtotal(row):
    words = [t.upper() for t in row["type"] + row["name"]]
    return not row["name"] or (words and set(words) <= TOTAL_WORDS)


def _is_total_label(name_words):
    """A (sub)total whose label names its section: "TOTAL SPECIAL AREAS &"
    printed above its values (1999), "2003 GRAND TOTAL EQUALIZED". No
    municipality name contains the word TOTAL."""
    return any(t.upper() in ("TOTAL", "TOTALS", "SUBTOTAL") for t in name_words)


MIN_NAME_ROWS = 8  # fewer named rows than this and a page's mode is unreliable


def _first_x0s(body):
    return [round(r["words"][0]["x0"]) for r in body
            if r["words"] and not NUM.match(r["words"][0]["text"])]


def _name_x0(firsts):
    """Left edge of the name column: the commonest x0 of a row's first word.
    Rows with a type label are the minority — except on a short last page
    (2006: 4 rows, 3 with a type label), so there the caller passes the
    whole report's first words instead."""
    if not firsts:
        raise ParseError("no named rows on a table page")
    return max(set(firsts), key=firsts.count)


def _join_fragments(body):
    """Re-attach a value that wrapped onto the next line (see FRAG)."""
    out = []
    for r in body:
        prev = out[-1] if out else None
        if (prev and r["top"] - prev["top"] <= 16
                and all(w["text"].isdigit() for w in r["words"])
                and any(FRAG.match(w["text"]) for w in prev["words"])):
            frags = [w for w in prev["words"] if FRAG.match(w["text"])]
            if len(frags) == len(r["words"]) and all(
                    abs(f["x1"] - w["x1"]) <= ALIGN_TOL for f, w in zip(frags, r["words"])):
                for f, w in zip(frags, r["words"]):
                    f["text"] += w["text"]
                continue
        out.append(r)
    return out


def _value_words(row, left):
    """The trailing run of numbers right of `left`; anything before is name.
    "-" is a printed zero (1998–1999 reports)."""
    out = []
    for w in reversed(row["words"]):
        if not ((NUM.match(w["text"]) or PLAIN.match(w["text"]) or w["text"] == "-")
                and w["x0"] > left):
            break
        out.append(w)
    return out[::-1]


def _anchor_rows(body):
    """Give each value an x relative to its own row's total ("xa").

    One page of the 2000 report prints every column ~7 pt left of the other
    pages, and two 1998 rows sit 3 pt right of theirs. The total is printed on
    every row, so it anchors the row; a row whose last value is not really
    its total fails the row-sum check."""
    for r in body:
        for w in r["values"]:
            w["xa"] = w["x1"] - r["values"][-1]["x1"]


def column_edges(pages_rows, n_cols):
    """Cluster the right edges of every value below the header, document-wide.

    Document-wide because a column can be entirely blank on one page (e.g.
    co-generating M&E in 2014), which would drop a cluster per page.
    """
    xs = sorted(w["xa"] for rows in pages_rows for r in rows
                if r["values"] and not _is_subtotal(r) for w in r["values"] if w["text"] != "-")
    clusters = []
    for x in xs:
        if clusters and x - clusters[-1][-1] <= ALIGN_TOL:
            clusters[-1].append(x)
        else:
            clusters.append([x])
    edges = [sum(c) / len(c) for c in clusters]
    if len(edges) != n_cols:
        raise ParseError(f"expected {n_cols} value columns, found {len(edges)} "
                         f"right-edge clusters at {[round(e) for e in edges]}")
    return edges


def parse_pages(pages_words, report_year, source_file="?"):
    """pages_words: list (per page) of pdfplumber-style word dicts
    (text, x0, x1, top). Returns (records, stats)."""
    pages_rows = []
    rail = False
    old_classes = set()
    modern = False
    summary_pages = []
    bodies = []
    for pno, words in enumerate(pages_words, start=1):
        rows = _rows(words)
        hb = _header_bottom(rows)
        if hb is None:
            bodies.append(None)
            continue
        head = {w["text"].upper() for r in rows if r["top"] <= hb for w in r["words"]}
        if "DISTRIBUTION" in head:
            # 1999: totals by municipality type under a pie chart; not members.
            summary_pages.append(pno)
            bodies.append(None)
            continue
        if "RAILWAY" in head:
            rail = True
        if "CO-GENERATING" in head:
            modern = True
        else:
            old_classes.add(tuple(_old_classes(rows, hb)))
        left = _values_left(rows, hb)
        # Fragments first: a wrapped "53" (2011) looks like a footer on its own.
        body = [r for r in _join_fragments([r for r in rows if r["top"] > hb])
                if not _is_boilerplate(r)]
        bodies.append((body, left))
    all_firsts = [x for b in bodies if b for x in _first_x0s(b[0])]
    for b in bodies:
        if b is None:
            pages_rows.append([])
            continue
        body, left = b
        firsts = _first_x0s(body)
        type_x = _name_x0(firsts if len(firsts) >= MIN_NAME_ROWS else all_firsts) - 3
        for r in body:
            r["values"] = _value_words(r, left)
            r["type"] = [w["text"] for w in r["words"] if w["x1"] < type_x]
            r["name"] = [w["text"] for w in r["words"]
                         if w["x1"] >= type_x and w not in r["values"]]
        _anchor_rows(body)
        pages_rows.append(body)
    if not any(pages_rows):
        raise ParseError("no page carries the table header — image-only or unknown layout")

    if len(old_classes) > 1 or (old_classes and modern):
        raise ParseError(f"pages disagree on the layout: {sorted(old_classes)}, "
                         f"modern pages: {modern}")
    classes = (list(next(iter(old_classes))) if old_classes
               else CLASSES_RAIL if rail else CLASSES_NO_RAIL)
    edges = column_edges(pages_rows, len(classes))

    records, section, subtotals, loose = [], [], [], []
    n_rows = n_blank = 0
    muni_type = None
    for pno, rows in enumerate(pages_rows, start=1):
        last = pending = None
        for r in rows:
            nums, type_words, name_words = r["values"], r["type"], r["name"]
            if pending:
                # A label may sit alone above its values: "TOTAL SPECIALIZED" /
                # values / "MUNICIPALITIES" (1999–2000 subtotals).
                if r["top"] - pending["top"] > PRE_GAP:
                    raise ParseError(f"p{pno}: name-only line {pending['text']!r} "
                                     f"belongs to no data row")
                name_words = pending["text"].split() + name_words
                pending = None
            is_sub = _is_subtotal(r) or _is_total_label(name_words)
            tol = SUB_TOL if is_sub else ALIGN_TOL
            if not nums:
                # 1998–2004 print a wrapped name's values on its LAST line
                # ("Improvement District No. 13 - Elk" / "Island 458,750 ..."),
                # so there a name-only line continues only a subtotal's label.
                if (name_words and last is not None and r["top"] - last["line_top"] <= CONT_GAP
                        and (not old_classes or last.get("subtotal"))):
                    last["muni_name_raw"] += " " + " ".join(name_words)
                    last["line_top"] = r["top"]
                    continue
                if old_classes and name_words and {t.upper() for t in name_words} <= HEADING_WORDS:
                    muni_type = " ".join(name_words)
                    continue
                if name_words:
                    if pending:
                        raise ParseError(f"p{pno}: two name-only lines with no data row: "
                                         f"{pending['text']!r}, {' '.join(name_words)!r}")
                    pending = {"text": " ".join(name_words), "top": r["top"]}
                if type_words:
                    muni_type = " ".join(type_words)
                continue
            vals = {}
            for w in nums:
                i = min(range(len(edges)), key=lambda k: abs(edges[k] - w["xa"]))
                if abs(edges[i] - w["xa"]) > (DASH_TOL if w["text"] == "-" else tol):
                    raise ParseError(f"p{pno}: value {w['text']} at x1={w['x1']:.1f} "
                                     f"matches no column")
                if classes[i] in vals:
                    raise ParseError(f"p{pno}: two values in column {classes[i]} "
                                     f"on one row")
                v = 0 if w["text"] == "-" else int(w["text"].replace(",", ""))
                fixed = KNOWN_DEFECTS.get((report_year, classes[i], v))
                if fixed is not None and is_sub:
                    event(log, "known publisher defect corrected", level=30,
                          report_year=report_year, page=pno, column=classes[i],
                          printed=v, corrected=fixed)
                    v = fixed
                if classes[i] == "grand_total" and not is_sub:
                    fixed = KNOWN_TOTAL_DEFECTS.get((report_year, " ".join(name_words), v))
                    if fixed is not None:
                        event(log, "known publisher defect corrected", level=30,
                              report_year=report_year, page=pno, row=" ".join(name_words),
                              column="grand_total", printed=v, corrected=fixed)
                        v = fixed
                vals[classes[i]] = v
            blanks = [c for c in classes if c not in vals]
            full = {c: vals.get(c, 0) for c in classes}
            parts = sum(full[c] for c in classes[:-1])
            if parts != full["grand_total"]:
                raise ParseError(f"p{pno}: row {' '.join(name_words) or 'subtotal'!r} classes "
                                 f"sum to {parts:,} but its total is {full['grand_total']:,}")
            if is_sub:
                loose = _check_subtotal(full, section, subtotals, loose, classes, pno)
                subtotals.append(full)
                section = []
                # A label wrapped below the values ("REDWOOD MEADOWS", 1999)
                # continues this subtotal, not the next row's name.
                last = {"muni_name_raw": "", "line_top": r["top"], "subtotal": True}
                continue
            if type_words:
                muni_type = " ".join(type_words)
            row = {"muni_type": muni_type, "muni_name_raw": " ".join(name_words),
                   "values": full, "blanks": blanks, "page": pno, "line_top": r["top"]}
            records.append(row)
            section.append(full)
            last = row
            n_rows += 1
            n_blank += len(blanks)
    if pending:
        raise ParseError(f"name-only line {pending['text']!r} belongs to no data row")
    if section or loose:
        raise ParseError(f"{len(section) + len(loose)} rows were never reconciled "
                         f"against a subtotal or the grand total")

    out = []
    for rec in records:
        for c in classes[:-1]:
            out.append({"report_year": report_year, "taxation_year": report_year - 1,
                        "muni_type": rec["muni_type"], "muni_name_raw": rec["muni_name_raw"],
                        "class": c, "value": rec["values"][c],
                        "was_blank": c in rec["blanks"], "source_file": source_file,
                        "page": rec["page"]})
    stats = {"rows": n_rows, "blank_cells": n_blank, "subtotals": len(subtotals),
             "railway_column": rail, "layout": "1998-2004" if old_classes else "2005+",
             "summary_pages_skipped": summary_pages}
    return out, stats


def _check_subtotal(sub, section, prior_subtotals, loose, classes, pno):
    """Reconcile a subtotal row; return the rows still awaiting the grand total.

    A subtotal equals the rows since the previous subtotal, or only the last
    k of them: the 1998–2004 reports print Special Areas and Redwood Meadows
    outside any section (1998 first, 2002–2004 last). Those rows stay "loose"
    until a grand total, which must equal the prior subtotals plus every loose
    row."""
    def matches(rows):
        return all(sum(r[c] for r in rows) == sub[c] for c in classes)  # [] ok if all zero
    if matches(section):
        return loose
    if prior_subtotals and matches(prior_subtotals + loose + section):
        return []
    for k in range(len(section) - 1, 0, -1):
        if matches(section[-k:]):
            return loose + section[:-k]
    raise ParseError(f"p{pno}: subtotal row reconciles neither with the "
                     f"{len(section)} rows above it nor with the prior subtotals")


def parse_pdf(path: Path, report_year: int):
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        pages_words = [p.extract_words() for p in pdf.pages]
    return parse_pages(pages_words, report_year, source_file=path.name)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--raw", type=Path, default=REPO / "data/raw/equalized")
    ap.add_argument("--out", type=Path, default=REPO / "data/processed/equalized_long.csv")
    args = ap.parse_args(argv)

    manifest = json.loads((args.raw / "manifest.json").read_text())
    all_rows, failed = [], []
    for entry in sorted(manifest["files"], key=lambda e: e["report_year"]):
        year, path = entry["report_year"], args.raw / entry["file"]
        try:
            rows, stats = parse_pdf(path, year)
        except ParseError as e:
            failed.append(year)
            event(log, "report skipped", level=40, report_year=year, reason=str(e))
            continue
        all_rows.extend(rows)
        event(log, "report parsed", report_year=year, **stats)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0]))
        w.writeheader()
        w.writerows(all_rows)
    event(log, "wrote long table", path=str(args.out), rows=len(all_rows),
          skipped_years=failed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
