"""Extract the Phase 2 FIR lines for every region member, 1994–2025, into one long table.

Lines: Schedule D provincial transfers (01910/01920 through 2022, 01912/01922
from 2023 — decision 9 as amended 2026-10-01), Schedule EA equalized
assessment subtotals (1997 onward), and Schedule POPL population.

Columns are found by FIR item code, never by position; 2001's files have no
code row, so their headers are mapped by name (NAME_TO_CODE). Rows are matched
to members on regions.csv `fir_code`, and the FIR name must be one of the
member's aliases. A municipality that dissolved into a member (decision 8) is
read under that member's `muni_id` from its own code in `absorbed_fir_codes`,
for every year it reports; its name must be one of the member's `+` parts. A row's own YEAR decides its year: rows whose YEAR differs
from their folder's (the 2002 files inside 2001/) are logged and not read.
A member missing a line in a year fails the run.

Usage:
    python src/parse_fir.py [--raw data/raw/fir] [--regions data/regions.csv] [--out data/processed/fir_long.csv]
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fingerprint_fir import _cell, _sheets, members  # noqa: E402
from jsonlog import event, get_logger  # noqa: E402

log = get_logger("parse_fir")

REPO = Path(__file__).resolve().parent.parent
FIRST, LAST = 1994, 2025
EA_FIRST = 1997

TRANSFERS_OLD = {"01910", "01920"}  # provincial unconditional / conditional, through 2022
TRANSFERS_NEW = {"01912", "01922"}  # provincial operating / capital, from 2023
EA_LINES = {"08260", "08265", "08270", "08275", "08280", "08285", "08290", "08295"}
POPL = "POPL"
# The 2020–2022 workbooks have no POPL sheet (data/fir_schema.json). Population
# is a cross-check here — decision 10's denominator is StatCan.
POPL_ABSENT = {2020, 2021, 2022}

# Schedule picked by the sheet's title rows (fingerprint_fir records them).
SCHEDULES = {
    "D": re.compile(r"Schedule D \| Financial Activities by Type/Object - Total$", re.I),
    "EA": re.compile(r"Equalized Assessment"),
    "POPL": re.compile(r"(Population of Alberta - Population of Alberta|^Population of Alberta)$"),
}
# The electric (-E) and gas (-G) function supplements reuse Schedule D's title
# in the per-schedule eras; they are a utility's slice, not the municipality.
SUPPLEMENT = re.compile(r"-[EG]\.xlsx$", re.I)
# 2001 only: no item-code row. Names as printed there; codes as every other year
# prints them under the same header.
NAME_TO_CODE = {
    "Provincial Government Unconditional Transfers": "01910",
    "Provincial Government Conditional Transfers": "01920",
    "GRAND TOTAL": "08260",
    "Linear Subtotal": "08265",
    "Mach & Equip Subtotal": "08270",
    "Non Residential Subtotal": "08275",
    "Residential Subtotal": "08280",
    "POPULATION": POPL,
}
FIELDS = ["fir_year", "muni_id", "fir_code", "fir_name", "schedule", "line_code", "line_name",
          "value", "source"]


class ParseError(Exception):
    pass


def norm(name: str) -> str:
    return " ".join(name.upper().replace(",", " ").replace("*", " ").split())


def wanted(schedule: str, year: int) -> set[str]:
    if schedule == "D":
        return TRANSFERS_NEW if year >= 2023 else TRANSFERS_OLD
    if schedule == "EA":
        return EA_LINES if year >= EA_FIRST else set()
    return {POPL}


def read_sheet(rows, year: int, schedule: str):
    """Yield (row_year, code, name, {line_code: (line_name, value)}) per municipality row."""
    header, codes = None, None
    for row in rows:
        cells = list(row)
        text = [_cell(c) for c in cells]
        if header is None:
            if text and text[0].upper() == "YEAR":
                header = text
            continue
        is_muni = len(text) > 3 and re.match(r"^\d{4}$", text[2])
        if codes is None:
            codes = [] if is_muni else text
            if not is_muni:
                continue
        if not is_muni:
            continue
        cols = {}
        for i, h in enumerate(header[4:], start=4):
            code = (codes[i] if i < len(codes) and codes[i] else NAME_TO_CODE.get(h))
            if code in wanted(schedule, year):
                v = cells[i] if i < len(cells) else None
                cols[code] = (h, None if v in (None, "") else float(v))
        yield text[0], text[2], text[3], cols


def absorbed(regions: list[dict]) -> dict[str, dict]:
    """{fir_code: absorbing member} for the dissolved municipalities."""
    return {c: r for r in regions for c in (r.get("absorbed_fir_codes") or "").split("|") if c}


def parse(raw: Path, regions: list[dict]):
    by_code = {r["fir_code"]: r for r in regions}
    aliases = {r["fir_code"]: {norm(a.lstrip("+")) for a in r["eq_aliases"].split("|")}
               for r in regions}
    for code, r in absorbed(regions).items():
        by_code[code] = r
        aliases[code] = {re.sub(r"^(CITY|TOWN|VILLAGE) OF ", "", norm(a[1:]))
                         for a in r["eq_aliases"].split("|") if a.startswith("+")}
    manifest = json.loads((raw / "manifest.json").read_text())
    out, stray = {}, set()
    for year, source, name, body in members(raw, manifest):
        if not isinstance(year, int) or not FIRST <= year <= LAST or SUPPLEMENT.search(name):
            continue
        for sheet, rows in _sheets_safe(name, body):
            title, rows = _title(rows)
            schedule = next((s for s, pat in SCHEDULES.items() if pat.search(title)), None)
            if schedule is None or not wanted(schedule, year):
                continue
            for row_year, code, fir_name, cols in read_sheet(rows, year, schedule):
                if row_year != str(year):
                    stray.add((year, source))
                    continue
                if code not in by_code:
                    continue
                if norm(fir_name) not in aliases[code]:
                    raise ParseError(f"{year} {source}: code {code} is {fir_name!r}, "
                                     f"not an alias of {by_code[code]['muni_id']}")
                for line, (line_name, value) in cols.items():
                    key = (year, code, line)
                    rec = {"fir_year": year, "muni_id": by_code[code]["muni_id"], "fir_code": code,
                           "fir_name": fir_name.strip(), "schedule": schedule, "line_code": line,
                           "line_name": line_name, "value": value, "source": f"{source}#{sheet}"}
                    if key in out:
                        if out[key]["value"] != value:
                            raise ParseError(f"{key}: {out[key]['source']} has {out[key]['value']}, "
                                             f"{rec['source']} has {value}")
                        continue
                    out[key] = rec
    for year, source in sorted(stray):
        event(log, "rows for another year not read", level=30, folder_year=year, source=source)
    check_complete(out, regions)
    return [out[k] for k in sorted(out)], sorted(stray)


def _sheets_safe(name, body):
    if not name.lower().endswith((".xlsx", ".xls")):
        return []
    try:
        return list(_sheets(name, body)) if name.lower().endswith(".xls") else _sheets(name, body)
    except Exception as e:  # noqa: BLE001 — the encrypted SIR forms, recorded by fingerprint_fir
        if "encrypted" in str(e).lower():
            return []
        raise


def _title(rows):
    """The first two non-empty rows joined, as fingerprint_fir records a title;
    returns the title and the rows with those two put back in front."""
    rows = iter(rows)
    head, title = [], []
    for row in rows:
        head.append(row)
        cells = [_cell(c) for c in row]
        if cells and cells[0].upper() == "YEAR":
            break
        if any(cells):
            title.append(" | ".join(c for c in cells if c))
        if len(head) > 6:
            break

    def chain():
        yield from head
        yield from rows
    return " | ".join(title[:2]), chain()


def check_complete(out: dict, regions: list[dict]):
    """Every member has every line in every year. An absorbed municipality has
    every line of a schedule in every year up to the last year it reports that
    schedule with a non-zero value. Its EA rows run past its D rows (FIR year Y
    carries report year Y), and EA keeps all-zero placeholder rows for some
    years after dissolution (Blackie, Entwistle to 2004)."""
    line_schedule = {line: sch for sch in ("D", "EA", "POPL") for y in (1994, 2023)
                     for line in wanted(sch, max(y, EA_FIRST) if sch == "EA" else y)}
    spans = [(r["muni_id"], r["fir_code"], {s: LAST for s in ("D", "EA", "POPL")}) for r in regions]
    for code, r in absorbed(regions).items():
        last = {}
        for (y, c, line), rec in out.items():
            if c == code and float(rec["value"] or 0):
                sch = line_schedule[line]
                last[sch] = max(last.get(sch, 0), y)
        if not last:
            raise ParseError(f"absorbed code {code} ({r['muni_id']}) has no rows")
        spans.append((f"{r['muni_id']}<{code}>", code, last))
    missing = []
    for muni, code, last in spans:
        for schedule, last_year in last.items():
            for year in range(FIRST, last_year + 1):
                for line in wanted(schedule, year):
                    if year == 2001 and line in ("08285", "08290", "08295"):
                        continue  # 2001's EQASSMT has no farmland/railway/co-gen column
                    if line == POPL and year in POPL_ABSENT:
                        continue
                    if (year, code, line) not in out:
                        missing.append((year, muni, line))
    if missing:
        raise ParseError(f"{len(missing)} member-year lines missing, e.g. {missing[:8]}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--raw", type=Path, default=REPO / "data/raw/fir")
    ap.add_argument("--regions", type=Path, default=REPO / "data/regions.csv")
    ap.add_argument("--out", type=Path, default=REPO / "data/processed/fir_long.csv")
    args = ap.parse_args(argv)
    regions = list(csv.DictReader(open(args.regions, newline="")))
    rows, stray = parse(args.raw, regions)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            v = r["value"]
            w.writerow({**r, "value": "" if v is None else (int(v) if v.is_integer() else v)})
    event(log, "written", path=str(args.out), rows=len(rows), stray_files=len(stray))
    return 0


if __name__ == "__main__":
    sys.exit(main())
