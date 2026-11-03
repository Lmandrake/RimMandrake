#!/usr/bin/env python3
"""perceived_beauty_live_proof.py -- read-only verdict on the newest modcheck CreatureBehaviors run of chain perceived_beauty.

OLLOPOM_BEAUTY_VERIFY_DEPLOYED_NOT_SEEN. The live half is `modcheck run CreatureBehaviors --chains perceived_beauty`
(infrastructure/state/live_proofs/OLLOPOM_BEAUTY_VERIFY_DEPLOYED_NOT_SEEN.txt); this script only READS that run's results
JSON (Transient/modcheck/CreatureBehaviors_<stamp>.json, runner.write_sheet).

Exit 0 only when the newest CreatureBehaviors run, no older than --max-age-min, holds chain perceived_beauty with row
ollopom_outdoors_adds_beauty_and_toggle_removes_it exactly PASS and no FAIL row in that chain. That row (validation.py)
asserts: the ollopom outdoors with the mechanic on contributes > 0, a control muffalo 0, the mechanic off 0, and the
perceived beauty beside it rises with the mechanic on. Exit 1 otherwise: FAIL, UNMEASURED (e.g. an indoor cell, a spawn
refused), PASS(UNVERIFIED n), a missing chain/row, no run, or a stale run. modcheck itself exits 0 on UNMEASURED, so its
exit code alone is not the proof.

    python3 src/RimMandrake/CreatureBehaviors/perceived_beauty_live_proof.py [--max-age-min 30] [--dir <dir>]
    python3 src/RimMandrake/CreatureBehaviors/perceived_beauty_live_proof.py --selftest
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
MOD = "CreatureBehaviors"
CHAIN = "perceived_beauty"
ROW = "ollopom_outdoors_adds_beauty_and_toggle_removes_it"


def _verdict(c):
    return str(c.get("verdict") or "").split("(")[0].strip().upper()


def judge(data):
    """(ok, line) for one run's results JSON. Pure."""
    chains = [c for c in (data.get("summary") or {}).get("chains") or [] if c.get("name") == CHAIN]
    if not chains:
        return False, "chain %s not in the run" % CHAIN
    comps = chains[0].get("components") or []
    fails = ["%s: %s" % (c.get("name"), c.get("detail") or "") for c in comps if _verdict(c) == "FAIL"]
    row = [c for c in comps if c.get("name") == ROW]
    if fails:
        return False, "FAIL row(s) in %s: %s" % (CHAIN, "; ".join(fails))
    if not row:
        return False, "row %s not in chain %s (%d rows ran)" % (ROW, CHAIN, len(comps))
    v = str(row[0].get("verdict") or "").strip()      # exact: PASS(UNVERIFIED n) is not a pass
    if v != "PASS":
        return False, "%s/%s is %s: %s" % (CHAIN, ROW, v or "blank", row[0].get("detail") or "")
    return True, "%s/%s PASS, %d rows, no FAIL" % (CHAIN, ROW, len(comps))


def newest(sheet_dir):
    runs = sorted(glob.glob(os.path.join(sheet_dir, MOD + "_*.json")), key=os.path.getmtime)
    return runs[-1] if runs else None


def check(sheet_dir, max_age_min):
    path = newest(sheet_dir)
    if not path:
        return 1, "FAIL no %s run JSON under %s" % (MOD, sheet_dir)
    age = (time.time() - os.path.getmtime(path)) / 60.0
    if age > max_age_min:
        return 1, "FAIL newest run %s is %.0f min old (> %d): rerun the live half" % (path, age, max_age_min)
    try:
        with open(path, encoding="utf-8") as f:
            ok, line = judge(json.load(f))
    except (OSError, ValueError) as e:
        return 1, "FAIL unreadable run JSON %s: %s" % (path, e)
    return (0 if ok else 1), "%s  %s  [%s]" % ("PASS" if ok else "FAIL", line, path)


def selftest():
    def run(rows, chain=CHAIN):
        return {"summary": {"chains": [{"name": chain, "components": [
            {"name": n, "verdict": v, "detail": d} for n, v, d in rows]}]}}
    cases = [
        ("row PASS", run([(ROW, "PASS", "")]), True),
        ("row FAIL", run([(ROW, "FAIL", "control muffalo contributed 2.0")]), False),
        ("row UNMEASURED", run([(ROW, "UNMEASURED", "UNMEASURED: not psychologically outdoors")]), False),
        ("PASS unverified", run([(ROW, "PASS(UNVERIFIED 1)", "")]), False),
        ("row missing", run([("other", "PASS", "")]), False),
        ("other row FAIL", run([(ROW, "PASS", ""), ("x", "FAIL", "")]), False),
        ("chain missing", run([(ROW, "PASS", "")], chain="track_grid"), False),
        ("empty summary", {}, False),
    ]
    bad = [n for n, d, want in cases if judge(d)[0] != want]
    with tempfile.TemporaryDirectory() as td:
        if check(td, 60)[0] != 1:
            bad.append("empty dir")
        p = os.path.join(td, MOD + "_20261103T000000Z.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(run([(ROW, "PASS", "")]), f)
        if check(td, 60)[0] != 0:
            bad.append("fresh good run")
        old = time.time() - 3 * 3600
        os.utime(p, (old, old))
        if check(td, 60)[0] != 1:
            bad.append("stale run")
        newer = os.path.join(td, MOD + "_20261103T010000Z.json")      # newest wins: a later UNMEASURED is not a pass
        with open(newer, "w", encoding="utf-8") as f:
            json.dump(run([(ROW, "UNMEASURED", "")]), f)
        os.utime(p, None)
        os.utime(newer, (time.time() + 5, time.time() + 5))
        if check(td, 60)[0] != 1:
            bad.append("newest UNMEASURED over older PASS")
        with open(newer, "w", encoding="utf-8") as f:
            f.write("{not json")
        if check(td, 60)[0] != 1:
            bad.append("corrupt JSON")
        other = os.path.join(td, "Stillsand_20261103T020000Z.json")  # another mod's run is never read
        with open(other, "w", encoding="utf-8") as f:
            json.dump(run([(ROW, "PASS", "")]), f)
        os.remove(newer)
        os.remove(p)
        if check(td, 60)[0] != 1:
            bad.append("other mod's run read")
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
