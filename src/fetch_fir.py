"""Download the province's FIR/SIR workbooks (Municipal Financial and Statistical
Data) and write a manifest.

Manual, reviewed input: run it, check the manifest diff, then fingerprint.
Only rewrites a file whose checksum changed. Every resource the package lists
must match a known name pattern — an unrecognised one fails rather than being
skipped, so a new era or a renamed year is never silently missed.

Usage:
    python src/fetch_fir.py [--out data/raw/fir]
"""
import argparse
import hashlib
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jsonlog import event, get_logger  # noqa: E402

log = get_logger("fetch_fir")

REPO = Path(__file__).resolve().parent.parent
# The open.alberta.ca slug and the CKAN id cde4c4fd-a0b2-4816-af43-13de7a3fd3e3
# resolve to the same package (checked 2026-10-01).
CKAN = "https://open.alberta.ca/api/3/action/package_show?id=municipal-financial-and-statistical-data"

# Resource name → (kind, first year, last year). One workbook per financial year
# from 2017; earlier years arrive as three era zips; the newest year's Schedule MR
# is published early as a tax-rates workbook.
KINDS = [
    (re.compile(r"^(\d{4}) financial year$", re.I), "year"),
    (re.compile(r"^(\d{4})-(\d{4}) municipal financial data and statistics \(ZIP\)$", re.I), "zip"),
    (re.compile(r"^(\d{4})_Tax_Rates\.xlsx$", re.I), "tax_rates"),
]


class FetchError(Exception):
    pass


def classify(resources: list[dict]) -> list[dict]:
    """CKAN resources → entries with kind/years/file name; fails on an unknown
    name and on a financial year covered twice."""
    out, seen = [], {}
    for r in resources:
        name = r["name"].strip()
        for pat, kind in KINDS:
            m = pat.match(name)
            if m:
                break
        else:
            raise FetchError(f"unrecognised resource {name!r} — extend KINDS deliberately")
        first, last = int(m.group(1)), int(m.group(m.lastindex))
        first, last = min(first, last), max(first, last)
        if kind != "tax_rates":
            for y in range(first, last + 1):
                if y in seen:
                    raise FetchError(f"financial year {y} in both {seen[y]!r} and {name!r}")
                seen[y] = name
        ext = ".zip" if kind == "zip" else ".xlsx"
        fname = f"fir_{kind}_{first}{'' if first == last else f'_{last}'}{ext}"
        out.append({"name": name, "kind": kind, "first_year": first, "last_year": last,
                    "file": fname, "url": r["url"],
                    "publisher_last_modified": r.get("last_modified") or r.get("created")})
    years = sorted(seen)
    gaps = sorted(set(range(years[0], years[-1] + 1)) - set(years)) if years else []
    if gaps:
        raise FetchError(f"financial years missing from the package: {gaps}")
    return out


def check_nothing_vanished(listed: list[dict], previous: dict | None):
    if not previous:
        return
    gone = {e["file"] for e in previous["files"]} - {e["file"] for e in listed}
    if gone:
        raise FetchError(f"files in the manifest are no longer listed: {sorted(gone)}")


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "alberta-regional-viz"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        return resp.read()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=REPO / "data/raw/fir")
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    mpath = args.out / "manifest.json"
    previous = json.loads(mpath.read_text()) if mpath.exists() else None
    old = {e["file"]: e for e in previous["files"]} if previous else {}

    listed = classify(json.loads(_get(CKAN))["result"]["resources"])
    check_nothing_vanished(listed, previous)

    files = []
    for entry in listed:
        body = _get(entry["url"])
        sha = hashlib.sha256(body).hexdigest()
        changed = old.get(entry["file"], {}).get("sha256") != sha
        if changed:
            (args.out / entry["file"]).write_bytes(body)
        files.append({**entry, "bytes": len(body), "sha256": sha,
                      "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")
                      if changed else old[entry["file"]]["retrieved_utc"]})
        event(log, "resource", file=entry["file"], bytes=len(body), changed=changed)

    mpath.write_text(json.dumps({"source": CKAN, "files": files}, indent=1) + "\n")
    event(log, "manifest written", path=str(mpath), files=len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
