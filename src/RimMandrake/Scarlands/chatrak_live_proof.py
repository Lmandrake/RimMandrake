#!/usr/bin/env python3
"""chatrak_live_proof.py -- read-only verdict on the newest modcheck Scarlands run of chain chatrak_snap.

SCARLANDS_CHATRAK_LIVE_RERUN_1 (origin SCARLANDS_CHATRAK_SNAP_STAGE_02_1, harness fix e0732bd98). The live half is
`modcheck run Scarlands --chains chatrak_snap` (infrastructure/state/live_proofs/SCARLANDS_CHATRAK_LIVE_RERUN_1.txt);
this script only READS the run's results JSON (Transient/modcheck/Scarlands_<stamp>.json, runner.write_sheet).

Exit 0 only when the newest Scarlands run, no older than --max-age-min, holds chain chatrak_snap with row
snap_stage_0_2 PASS and no FAIL row anywhere in that chain (no false FAIL from a missing colonist). Exit 1 otherwise:
a FAIL, an UNMEASURED row 0_2, a missing chain/row, no run, or a stale run all fail -- UNMEASURED is never a pass.

    python3 src/RimMandrake/Scarlands/chatrak_live_proof.py [--max-age-min 60] [--dir <Transient/modcheck>]
    python3 src/RimMandrake/Scarlands/chatrak_live_proof.py --selftest
"""
import argparse
import glob
import json
import os
import sys
import tempfile
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
SHEET_DIR = os.path.join(ROOT, "Transient", "modcheck")
CHAIN = "chatrak_snap"
ROW = "snap_stage_0_2"


def _verdict(c):
    return str(c.get("verdict") or "").split("(")[0].strip().upper()


def judge(data):
    """(ok, line) for one run's results JSON."""
    chains = [c for c in (data.get("summary") or {}).get("chains") or [] if c.get("name") == CHAIN]
    if not chains:
        return False, "chain %s not in the run" % CHAIN
    comps = chains[0].get("components") or []
    fails = ["%s: %s" % (c.get("name"), c.get("detail") or "") for c in comps if _verdict(c) == "FAIL"]
    row = [c for c in comps if c.get("name") == ROW]
    if not row:
        return False, "row %s not in chain %s (%d rows ran)" % (ROW, CHAIN, len(comps))
    v = str(row[0].get("verdict") or "").strip()   # exact: PASS(UNVERIFIED n) made an unverified call, not a pass
    if fails:
        return False, "FAIL row(s) in %s: %s" % (CHAIN, "; ".join(fails))
    if v != "PASS":
        return False, "%s/%s is %s: %s" % (CHAIN, ROW, v or "blank", row[0].get("detail") or "")
    return True, "%s/%s PASS, %d rows, no FAIL" % (CHAIN, ROW, len(comps))


def newest(sheet_dir):
    runs = sorted(glob.glob(os.path.join(sheet_dir, "Scarlands_*.json")), key=os.path.getmtime)
    return runs[-1] if runs else None


def check(sheet_dir, max_age_min):
    path = newest(sheet_dir)
    if not path:
        return 1, "no Scarlands run JSON under %s" % sheet_dir
    age = (time.time() - os.path.getmtime(path)) / 60.0
    if age > max_age_min:
        return 1, "newest run %s is %.0f min old (> %d): rerun the live half" % (path, age, max_age_min)
    with open(path, encoding="utf-8") as f:
        ok, line = judge(json.load(f))
    return (0 if ok else 1), "%s  %s" % ("PASS" if ok else "FAIL", line + "  [" + path + "]")


def selftest():
    def run(rows):
        return {"summary": {"chains": [{"name": CHAIN, "components": [
            {"name": n, "verdict": v, "detail": d} for n, v, d in rows]}]}}
    good = [("snap_defs_resolve", "PASS", ""), (ROW, "PASS", ""), ("snap_stage_0_4", "PASS", "")]
    cases = [
        ("all PASS", run(good), True),
        ("row FAIL", run([("snap_defs_resolve", "PASS", ""), (ROW, "FAIL", "severity 0.2")]), False),
        ("row UNMEASURED", run([(ROW, "UNMEASURED", "UNMEASURED: REFUSED: no free colonist")]), False),
        ("other row FAIL", run(good + [("snap_off_arms_nothing", "FAIL", "armed")]), False),
        ("row missing", run([("snap_defs_resolve", "PASS", "")]), False),
        ("chain missing", {"summary": {"chains": [{"name": "warscar_mark", "components": []}]}}, False),
        ("PASS unverified", run([(ROW, "PASS(UNVERIFIED 1)", "")]), False),
    ]
    bad = [n for n, d, want in cases if judge(d)[0] != want]
    with tempfile.TemporaryDirectory() as td:
        if check(td, 60)[0] != 1:
            bad.append("empty dir")
        p = os.path.join(td, "Scarlands_20261103T000000Z.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(run(good), f)
        if check(td, 60)[0] != 0:
            bad.append("fresh good run")
        old = time.time() - 3 * 3600
        os.utime(p, (old, old))
        if check(td, 60)[0] != 1:
            bad.append("stale run")
    print("selftest %s%s" % ("OK" if not bad else "FAILED: ", ", ".join(bad)))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--max-age-min", type=int, default=60)
    ap.add_argument("--dir", default=SHEET_DIR)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    code, line = check(a.dir, a.max_age_min)
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
