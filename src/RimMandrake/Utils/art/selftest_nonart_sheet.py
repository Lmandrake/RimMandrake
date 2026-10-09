#!/usr/bin/env python3
"""selftest_nonart_sheet.py — the non-art route accepts a checked non-art sheet and still refuses every art-sheet shape."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nonart_sheet as NA  # noqa: E402

FAILS = []


def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        FAILS.append(m)


REAL = Path(__file__).resolve().parents[4] / "Transient"
SRC = REAL / "donor_code_creatures_sheet_2026-10-09.html"




def main():
    if not SRC.is_file() or not (NA.SKILL_ASSETS / "check_sheet.py").is_file():
        print("SKIP fixture sheet or check_sheet.py absent")
        return 0
    base = SRC.read_text()
    dec = json.loads(SRC.with_suffix(".decisions.json").read_text())
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)

        def put(name, html, d=None, sub=""):
            dd = td / sub
            dd.mkdir(exist_ok=True, parents=True)
            sp = dd / f"{name}.html"
            sp.write_text(html)
            dj = json.loads(json.dumps(d if d is not None else dec))
            dj["sheetId"] = name
            dp = dd / f"{name}.decisions.json"
            dp.write_text(json.dumps(dj))
            return sp, dp

        good = NA.declare(base)
        sp, dp = put("ok_sheet", good)
        check(NA.verify(sp, dp)[0], "declared non-art sheet with valid decisions passes")
        sp, dp = put("undeclared_sheet", base)
        ok, msg = NA.verify(sp, dp)
        check(not ok and "declaration" in msg, "undeclared sheet is refused by the non-art checks")
        sp, dp = put("stamped_sheet", NA.declare(base).replace("<head>", '<head>\n<meta name="scaled-review-gate" content="v1 sha256:00">', 1))
        ok, msg = NA.verify(sp, dp)
        check(not ok and "art sheet" in msg, "a stamped art sheet cannot be served as non-art")
        sp, dp = put("ffar_sheet", good, sub="biome_ffar")
        ok, msg = NA.verify(sp, dp)
        check(not ok and "biome_ffar" in msg, "a biome_ffar sheet cannot be served as non-art")
        bad = json.loads(json.dumps(dec))
        bad["decisions"]["NOT_A_ROW"] = {"decision": "x"}
        sp, dp = put("badrow_sheet", good, bad)
        ok, msg = NA.verify(sp, dp)
        check(not ok and "NOT_A_ROW" in msg, "decision row absent from the sheet is refused")
        bad = json.loads(json.dumps(dec))
        bad["reviewStatus"] = {}
        sp, dp = put("badstatus_sheet", good, bad)
        check(not NA.verify(sp, dp)[0], "missing reviewStatus.state is refused")
        sp, dp = put("badid_sheet", good)
        j = json.loads(dp.read_text())
        j["sheetId"] = "other"
        dp.write_text(json.dumps(j))
        check(not NA.verify(sp, dp)[0], "sheetId not matching the file stem is refused")
        sp, dp = put("broken_sheet", good.replace('<script id="ITEMS"', '<script id="XITEMS"'))
        check(not NA.verify(sp, dp)[0], "a sheet without ITEMS is refused")
        # serve_gated wiring: undeclared and stamp-less art-looking sheet still exits 4
        sp, dp = put("art_sheet", base)
        r = subprocess.run([sys.executable, str(HERE / "serve_gated.py"), "--no-open", "--sheet", str(sp), "--decisions", str(dp)],
                           capture_output=True, text=True, timeout=30)
        check(r.returncode == 4 and "gate stamp" in r.stderr, "serve_gated still refuses an undeclared, unstamped sheet (exit 4)")
        sp, dp = put("lying_sheet", NA.declare(base).replace("<head>", '<head>\n<meta name="scaled-review-gate" content="v1 sha256:00">', 1))
        r = subprocess.run([sys.executable, str(HERE / "serve_gated.py"), "--no-open", "--sheet", str(sp), "--decisions", str(dp)],
                           capture_output=True, text=True, timeout=30)
        check(r.returncode == 4, "serve_gated refuses a sheet with a bad art stamp even if it also claims non-art")
    print(f"{'FAILED' if FAILS else 'ALL PASS'} ({len(FAILS)} failing)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
