"""Download the provincial equalized assessment report PDFs and write a manifest.

Manual, reviewed input: run it, check the manifest diff, then parse.
Only re-downloads a file whose checksum changed.

Usage:
    python src/fetch_equalized.py [--out data/raw/equalized]
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

log = get_logger("fetch_equalized")

REPO = Path(__file__).resolve().parent.parent
CKAN = "https://open.alberta.ca/api/3/action/package_show?id=2368-657x"
NAME = re.compile(r"^Provincial (\d{4}) equalized assessment report$", re.I)


class FetchError(Exception):
    pass


def report_resources(package: dict) -> dict[int, dict]:
    """CKAN package → {report_year: resource}, failing on a duplicate year."""
    out = {}
    for r in package["resources"]:
        m = NAME.match(r["name"].strip())
        if not m:
            continue
        year = int(m.group(1))
        if year in out:
            raise FetchError(f"two resources claim report year {year}")
        out[year] = r
    return out


def check_no_year_vanished(listed: dict, previous_manifest: dict | None):
    if not previous_manifest:
        return
    gone = {e["report_year"] for e in previous_manifest["files"]} - set(listed)
    if gone:
        raise FetchError(f"report years in the manifest are no longer listed: {sorted(gone)}")


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "alberta-regional-viz"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=REPO / "data/raw/equalized")
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    mpath = args.out / "manifest.json"
    previous = json.loads(mpath.read_text()) if mpath.exists() else None
    old = {e["report_year"]: e for e in previous["files"]} if previous else {}

    package = json.loads(_get(CKAN))["result"]
    listed = report_resources(package)
    check_no_year_vanished(listed, previous)

    files = []
    for year, res in sorted(listed.items()):
        fname = f"equalized_{year}.pdf"
        body = _get(res["url"])
        sha = hashlib.sha256(body).hexdigest()
        changed = old.get(year, {}).get("sha256") != sha
        if changed:
            (args.out / fname).write_bytes(body)
        files.append({"report_year": year, "file": fname, "url": res["url"],
                      "bytes": len(body), "sha256": sha,
                      "publisher_last_modified": res.get("last_modified") or res.get("created"),
                      "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")
                      if changed else old[year]["retrieved_utc"]})
        event(log, "report", report_year=year, bytes=len(body), changed=changed)

    if len(files) != len(listed):
        raise FetchError(f"downloaded {len(files)} of {len(listed)} listed reports")
    mpath.write_text(json.dumps({"source": CKAN, "files": files}, indent=1) + "\n")
    event(log, "manifest written", path=str(mpath), reports=len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
