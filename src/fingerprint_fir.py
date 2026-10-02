"""Fingerprint the downloaded FIR files: every sheet of every spreadsheet, per
financial year — its title, header row, item-code row, row count and the YEAR
values its rows carry.

Offline; reads data/raw/fir (written by fetch_fir.py) and writes the committed
data/fir_schema.json. Re-run after every fetch and review the diff: a header,
code or row-count change there is the publisher moving the schema under us.
tests/test_fir_schema.py pins what later parsers rely on.

The FIR arrives in four layouts, all read the same way here:
  2009+     one workbook per year (2009–2016 inside one zip), one sheet per schedule;
  2003–08,
  1994–2000 one file per schedule, ``YYYY/YYYY-<schedule>.xlsx``;
  2001–03   legacy .xls in their own folder layouts (2003 sits in both zips).

Usage:
    python src/fingerprint_fir.py [--raw data/raw/fir] [--out data/fir_schema.json]
"""
import argparse
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jsonlog import event, get_logger  # noqa: E402

log = get_logger("fingerprint_fir")

REPO = Path(__file__).resolve().parent.parent
MUNI_CODE = re.compile(r"^\d{4}$")
YEAR_DIR = re.compile(r"^(\d{4})(?:-EA-MR)?/")
YEAR_BOOK = re.compile(r"^(\d{4})_Financial_Year\.xlsx$", re.I)
SHEET_EXT = (".xlsx", ".xls")


def _cell(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return " ".join(str(v).split())


def _sheets(name: str, body: bytes):
    """Yield (sheet name, row iterator) for every sheet of an .xlsx or .xls."""
    if name.lower().endswith(".xlsx"):
        import openpyxl  # noqa: PLC0415 — dev-only dep, imported at use
        wb = openpyxl.load_workbook(io.BytesIO(body), read_only=True, data_only=True)
        try:
            for ws in wb.worksheets:
                yield ws.title, ws.iter_rows(values_only=True)
        finally:
            wb.close()
    else:
        import xlrd  # noqa: PLC0415
        book = xlrd.open_workbook(file_contents=body)
        for sh in book.sheets():
            yield sh.name, _xls_rows(sh)


def _xls_rows(sh):
    # A function, not an inline generator expression: that would bind `sh` late
    # and read the last sheet for every sheet once they are collected first.
    return (sh.row_values(i) for i in range(sh.nrows))


def fingerprint_sheet(rows) -> dict:
    """Title, header and code rows, and the shape of the municipality rows.

    The header is the first row whose first cell is YEAR; the code row is the
    next one when it holds FIR item codes. A sheet with no YEAR row (an index,
    a notes page) is recorded by title alone."""
    title, header, codes, munis, years = [], None, None, 0, set()
    for row in rows:
        cells = [_cell(c) for c in row]
        while cells and not cells[-1]:
            cells.pop()
        is_muni = len(cells) > 3 and bool(MUNI_CODE.match(cells[2]))
        if header is None:
            if cells and cells[0].upper() == "YEAR":
                header = cells
            elif cells and len(title) < 2:
                title.append(" | ".join(c for c in cells if c))
            continue
        if codes is None:
            codes = [] if is_muni else cells[4:]
            if not is_muni:
                continue
        if is_muni:
            munis += 1
            years.add(cells[0])
    out = {"title": title}
    if header is not None:
        out.update(header=header[4:], codes=codes or [], muni_rows=munis, row_years=sorted(years))
    return out


def members(raw: Path, manifest: dict):
    """Yield (financial year, source path, file name, bytes) for every spreadsheet."""
    for entry in manifest["files"]:
        path = raw / entry["file"]
        if entry["kind"] == "zip":
            with zipfile.ZipFile(path) as z:
                for info in z.infolist():
                    name = info.filename
                    if info.is_dir() or not name.lower().endswith(SHEET_EXT):
                        continue
                    m = YEAR_DIR.match(name) or YEAR_BOOK.match(name)
                    year = int(m.group(1)) if m else None
                    yield year, f"{entry['file']}:{name}", name, z.read(name)
        else:
            year = entry["first_year"]
            label = "tax_rates" if entry["kind"] == "tax_rates" else None
            yield (label or year), entry["file"], entry["file"], path.read_bytes()


def build(raw: Path) -> dict:
    manifest = json.loads((raw / "manifest.json").read_text())
    out, seen = {}, {}
    for year, source, name, body in members(raw, manifest):
        key = str(year) if year is not None else "unassigned"
        digest = hashlib.sha256(body).hexdigest()
        files = out.setdefault(key, {})
        # The 2003 folder ships in both era zips; keep one copy, and only when
        # the bytes match — a differing duplicate is a real conflict.
        rel = source.split(":", 1)[-1]
        if (key, rel) in seen:
            if seen[(key, rel)] != digest:
                raise ValueError(f"{rel} differs between zips")
            files[rel]["also_in"] = sorted({*files[rel].get("also_in", []), source.split(":", 1)[0]})
            continue
        seen[(key, rel)] = digest
        files[rel] = {"source": source.split(":", 1)[0], "sha256": digest[:16]}
        try:
            files[rel]["sheets"] = {s: fingerprint_sheet(rows) for s, rows in _sheets(name, body)}
        except Exception as e:  # noqa: BLE001 — recorded, not skipped: the SIR forms are encrypted
            if "encrypted" not in str(e).lower():
                raise
            files[rel]["unreadable"] = "encrypted"
            event(log, "unreadable file", level=30, year=key, file=rel, reason="encrypted")
            continue
        event(log, "file", year=key, file=rel, sheets=len(files[rel]["sheets"]))
    # Header + code rows repeat across years; store each distinct pair once and
    # point at it, so the committed file stays reviewable.
    layouts = {}
    for files in out.values():
        for f in files.values():
            for s in f.get("sheets", {}).values():
                if "header" in s:
                    pair = {"header": s.pop("header"), "codes": s.pop("codes")}
                    lid = hashlib.sha256(json.dumps(pair).encode()).hexdigest()[:10]
                    layouts[lid] = pair
                    s["layout"] = lid
    return {"note": "Generated by src/fingerprint_fir.py — do not edit by hand.",
            "years": {k: dict(sorted(v.items())) for k, v in sorted(out.items())},
            "layouts": dict(sorted(layouts.items()))}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--raw", type=Path, default=REPO / "data/raw/fir")
    ap.add_argument("--out", type=Path, default=REPO / "data/fir_schema.json")
    args = ap.parse_args(argv)
    fp = build(args.raw)
    # One sheet / one layout per line: diffable without one line per header cell.
    lines = ["{", f' "note": {json.dumps(fp["note"])},', ' "years": {']
    for i, (year, files) in enumerate(fp["years"].items()):
        lines.append(f"  {json.dumps(year)}: {{")
        for j, (rel, f) in enumerate(files.items()):
            sep = "," if j < len(files) - 1 else ""
            lines.append(f"   {json.dumps(rel, ensure_ascii=False)}: "
                         f"{json.dumps(f, ensure_ascii=False)}{sep}")
        lines.append("  }" + ("," if i < len(fp["years"]) - 1 else ""))
    lines += [" },", ' "layouts": {']
    items = list(fp["layouts"].items())
    for k, (lid, pair) in enumerate(items):
        lines.append(f"  {json.dumps(lid)}: {json.dumps(pair, ensure_ascii=False)}"
                     + ("," if k < len(items) - 1 else ""))
    lines += [" }", "}"]
    args.out.write_text("\n".join(lines) + "\n")
    json.loads(args.out.read_text())  # the hand-joined file must still be JSON
    event(log, "schema written", path=str(args.out), years=len(fp["years"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
