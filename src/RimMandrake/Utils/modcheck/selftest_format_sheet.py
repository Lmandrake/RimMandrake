#!/usr/bin/env python3
"""selftest_format_sheet.py -- format_sheet.py (MODCHECK_PITS_SHEET_REBUILD_DECAYED_UNSEEN).

Builds the ratification sheet into a temp dir and checks: the Pits fixture is the GREEN 3/3 pilot; every row is a
unique id carried by the decisions file; the sheet declares non-art and passes nonart_sheet.verify; verify() names
the missing owner pick while the decisions are a prefill and stops naming it once they are ruled; a rebuild never
overwrites his picks.
"""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import format_sheet as F  # noqa: E402


def main():
    fails = []

    def ok(cond, msg):
        print(("PASS " if cond else "FAIL ") + msg)
        if not cond:
            fails.append(msg)

    pits = json.loads(F.PITS_FIX.read_text())
    comps = [c for ch in pits["chains"] for c in ch["components"]]
    ok(pits["all_green"] and len(comps) == 3 and all(c["verdict"] == "PASS" for c in comps),
       "Pits fixture is the GREEN 3/3 pilot run")
    items = F.rows(pits)
    ids = [i["id"] for i in items]
    ok(len(ids) == len(set(ids)) == 9, "nine rows, unique ids")

    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        F.OUT_DIR = t
        F.SHEET = t / (F.STEM + ".html")
        F.DECISIONS = t / (F.STEM + ".decisions.json")
        F.PITS_REPORT = t / "Pits_pilot_report.html"
        F.FW_REPORT = t / "FlowWorks_appearance_excerpt.html"
        F.build()
        html = F.SHEET.read_text()
        ok('<meta name="sheet-kind" content="non-art">' in html, "sheet declares non-art")
        ok("Pits -- GREEN" in F.PITS_REPORT.read_text(), "Pits report renders GREEN")
        ok("must" in F.FW_REPORT.read_text() and "RED" in F.FW_REPORT.read_text(),
           "appearance excerpt renders its must-show lines and a RED title")
        dec = json.loads(F.DECISIONS.read_text())
        ok(set(dec["decisions"]) == set(ids), "decisions carry every row")
        import nonart_sheet
        good, msg = nonart_sheet.verify(F.SHEET, F.DECISIONS)
        ok(good, "nonart_sheet.verify: " + msg)
        probs = F.problems()
        ok(any("owner's pick is not recorded" in p for p in probs), "verify names the missing owner pick on a prefill")
        ok(not any("not today's build" in p or "not today's render" in p for p in probs),
           "a fresh build is today's build")
        dec["reviewStatus"] = {"state": "ruled"}
        dec["decisions"]["evidence_raw"] = {"decision": "change", "prefill": "keep", "note": "fold the dicts"}
        F.DECISIONS.write_text(json.dumps(dec))
        F.build()
        again = json.loads(F.DECISIONS.read_text())
        ok(again["decisions"]["evidence_raw"]["decision"] == "change", "a rebuild keeps his picks")
        ok(not any("owner's pick" in p for p in F.problems()), "a ruled decisions file clears the owner-pick line")

    print("%d failure(s)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
