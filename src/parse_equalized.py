"""Parse the provincial equalized assessment report PDFs into a long table.

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
# A value cut off at the right edge of its cell, e.g. "5,671,306,0" with "53"
# on the next line (2011 report, a subtotal).
FRAG = re.compile(r"^\d{1,3}(?:,\d{3})*,\d{1,2}$")
ROW_TOL = 3.0      # pt: words within this vertical distance are one row
ALIGN_TOL = 3.0    # pt: a value's right edge must sit this close to its column's
# Bold (sub)total rows sit 3–5 pt left of their columns. Looser is safe for
# them only: a subtotal is reconciled column-by-column against the rows above.
SUB_TOL = 8.0
CONT_GAP = 14.0    # pt: a name-only line this close below a data row continues its name
PRE_GAP = 30.0     # pt: ...otherwise, one this close above the next data row prefixes it

CLASSES_RAIL = ["residential", "farmland", "nr", "nr_linear", "nr_railway",
                "nr_cogen_me", "me", "grand_total"]
CLASSES_NO_RAIL = [c for c in CLASSES_RAIL if c != "nr_railway"]

# Publisher errors in the PDFs, corrected by name, never by loosening a check.
# (report_year, class, printed value) -> value the rows above it sum to.
# Only ever a subtotal cell: subtotals are checks, not output. docs/DATA_ISSUES.md.
KNOWN_DEFECTS = {
    (2026, "nr_linear", 71_671_452_040): 71_674_452_040,
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
        r["words"].sort(key=lambda w: w["x0"])
    return rows


def _header_bottom(rows):
    """Top of the last header row (the one carrying 'Equipment'), or None."""
    for r in rows:
        if any(w["text"] == "Equipment" for w in r["words"]):
            return r["top"]
    return None


def _values_left(rows, hb):
    """x below which a number is part of a name ("No. 31"), not a value: a
    little left of the Residential header, since wide values overhang it."""
    xs = [w["x0"] for r in rows if r["top"] <= hb for w in r["words"]
          if w["text"] == "Residential"]
    if not xs:
        raise ParseError("header has no 'Residential' column")
    return min(xs) - 25


def _is_boilerplate(row):
    """Report-date / prepared-on / page-number lines, above or below the table."""
    t = [w["text"] for w in row["words"]]
    return (t[:2] == ["Report", "Date:"] or t[:1] in (["Prepared:"], ["Classification:"])
            or (len(t) == 2 and t[0] == "Page" and t[1].isdigit()))


TOTAL_WORDS = {"SUB", "TOTAL", "SUBTOTAL", "GRAND"}


def _is_subtotal(row):
    words = [t.upper() for t in row["type"] + row["name"]]
    return not row["name"] or (words and set(words) <= TOTAL_WORDS)


def _name_x0(body):
    """Left edge of the name column: the commonest x0 of a row's first word,
    over rows that carry values. Rows with a type label are the minority."""
    firsts = [round(r["words"][0]["x0"]) for r in body
              if r["words"] and not NUM.match(r["words"][0]["text"])]
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
    """The trailing run of numbers right of `left`; anything before is name."""
    out = []
    for w in reversed(row["words"]):
        if not (NUM.match(w["text"]) and w["x0"] > left):
            break
        out.append(w)
    return out[::-1]


def column_edges(pages_rows, n_cols):
    """Cluster the right edges of every value below the header, document-wide.

    Document-wide because a column can be entirely blank on one page (e.g.
    co-generating M&E in 2014), which would drop a cluster per page.
    """
    xs = sorted(w["x1"] for rows in pages_rows for r in rows
                if r["values"] and not _is_subtotal(r) for w in r["values"])
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
    for words in pages_words:
        rows = _rows(words)
        hb = _header_bottom(rows)
        if hb is None:
            pages_rows.append([])
            continue
        if any(w["text"] == "Railway" for r in rows if r["top"] <= hb for w in r["words"]):
            rail = True
        left = _values_left(rows, hb)
        body = _join_fragments([r for r in rows if r["top"] > hb and not _is_boilerplate(r)])
        type_x = _name_x0(body) - 3
        for r in body:
            r["values"] = _value_words(r, left)
            r["type"] = [w["text"] for w in r["words"] if w["x1"] < type_x]
            r["name"] = [w["text"] for w in r["words"]
                         if w["x1"] >= type_x and w not in r["values"]]
        pages_rows.append(body)
    if not any(pages_rows):
        raise ParseError("no page carries the table header — image-only or unknown layout")

    classes = CLASSES_RAIL if rail else CLASSES_NO_RAIL
    edges = column_edges(pages_rows, len(classes))

    records, section, subtotals = [], [], []
    n_rows = n_blank = 0
    muni_type = None
    for pno, rows in enumerate(pages_rows, start=1):
        last = pending = None
        for r in rows:
            nums, type_words, name_words = r["values"], r["type"], r["name"]
            if pending:
                if r["top"] - pending["top"] > PRE_GAP or not name_words:
                    raise ParseError(f"p{pno}: name-only line {pending['text']!r} "
                                     f"belongs to no data row")
                name_words = pending["text"].split() + name_words
                pending = None
            is_sub = _is_subtotal(r)
            tol = SUB_TOL if is_sub else ALIGN_TOL
            if not nums:
                if name_words and last is not None and r["top"] - last["line_top"] <= CONT_GAP:
                    last["muni_name_raw"] += " " + " ".join(name_words)
                    last["line_top"] = r["top"]
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
                i = min(range(len(edges)), key=lambda k: abs(edges[k] - w["x1"]))
                if abs(edges[i] - w["x1"]) > tol:
                    raise ParseError(f"p{pno}: value {w['text']} at x1={w['x1']:.1f} "
                                     f"matches no column")
                if classes[i] in vals:
                    raise ParseError(f"p{pno}: two values in column {classes[i]} "
                                     f"on one row")
                v = int(w["text"].replace(",", ""))
                fixed = KNOWN_DEFECTS.get((report_year, classes[i], v))
                if fixed is not None and is_sub:
                    event(log, "known publisher defect corrected", level=30,
                          report_year=report_year, page=pno, column=classes[i],
                          printed=v, corrected=fixed)
                    v = fixed
                vals[classes[i]] = v
            blanks = [c for c in classes if c not in vals]
            full = {c: vals.get(c, 0) for c in classes}
            parts = sum(full[c] for c in classes[:-1])
            if parts != full["grand_total"]:
                raise ParseError(f"p{pno}: row {' '.join(name_words) or 'subtotal'!r} classes "
                                 f"sum to {parts:,} but its total is {full['grand_total']:,}")
            if is_sub:
                _check_subtotal(full, section, subtotals, classes, pno)
                subtotals.append(full)
                section = []
                last = None
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
    if section:
        raise ParseError(f"{len(section)} rows after the last subtotal were never reconciled")

    out = []
    for rec in records:
        for c in classes[:-1]:
            out.append({"report_year": report_year, "taxation_year": report_year - 1,
                        "muni_type": rec["muni_type"], "muni_name_raw": rec["muni_name_raw"],
                        "class": c, "value": rec["values"][c],
                        "was_blank": c in rec["blanks"], "source_file": source_file,
                        "page": rec["page"]})
    stats = {"rows": n_rows, "blank_cells": n_blank, "subtotals": len(subtotals),
             "railway_column": rail}
    return out, stats


def _check_subtotal(sub, section, prior_subtotals, classes, pno):
    """A subtotal equals the rows since the previous subtotal; a final grand
    total equals the sum of the prior subtotals."""
    for rows in (section, prior_subtotals):
        if rows and all(sum(r[c] for r in rows) == sub[c] for c in classes):
            return
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
