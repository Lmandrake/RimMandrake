#!/usr/bin/env python3
"""chatrak_live_proof.py -- read-only verdict on the newest modcheck Scarlands run of chain chatrak_snap.

SCARLANDS_CHATRAK_LIVE_RERUN_1 (origin SCARLANDS_CHATRAK_SNAP_STAGE_02_1, harness fix e0732bd98). The live half is
`modcheck run Scarlands --chains chatrak_snap` (infrastructure/state/live_proofs/SCARLANDS_CHATRAK_LIVE_RERUN_1.txt);
this script only READS the run's results JSON (Transient/modcheck/Scarlands_<stamp>.json, runner.write_sheet).

Exit 0 only when the newest Scarlands run, no older than --max-age-min, holds chain chatrak_snap with row
snap_stage_0_2 PASS and no FAIL row anywhere in that chain (no false FAIL from a missing colonist). Exit 1 otherwise:
a FAIL, an UNMEASURED row 0_2, a missing chain/row, no run, or a stale run all fail -- UNMEASURED is never a pass.
Exit 2 UNMEASURED when modcheck REFUSED the run (summary.refused, e.g. stale_load: the game is up on another mod list):
nothing ran, so it is neither PASS nor FAIL (OPS_CHURN_DIAGNOSE_SCARLANDS_WYBF_YVLI: a refusal read as "chain not in
the run" was scored FAIL on the item).

--biome RM_Warscar: the criterion is "PASS on RM_Warscar", and every stage proof runs on the CURRENT map without
reporting its biome, so the reader also reads the bridge's jawa/map_info `mapBiome` (one read-only call; Windows Python,
RimBridge binds Windows loopback) and exits 1 unless it is that biome. An unreadable biome is never a pass.

    python.exe src/RimMandrake/Scarlands/chatrak_live_proof.py --biome RM_Warscar [--max-age-min 60] [--dir <dir>]
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


def refused(data):
    """modcheck's own refusal of the run ('' when it ran): summary.refused (its kind, e.g. stale_load, is summary.unmeasured)."""
    summ = data.get("summary") or {}
    return str(summ.get("refused") or "").strip()


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


def judge_biome(info, want):
    """(ok, line) for one jawa/map_info reply against the wanted BiomeDef. Pure."""
    if not isinstance(info, dict) or info.get("success") is False:
        return False, "map biome UNMEASURED: map_info replied %s" % str(info)[:200]
    have = info.get("mapBiome")
    if not have:
        return False, "map biome UNMEASURED: map_info has no mapBiome"
    if have != want:
        return False, "the run's map is %s, not %s" % (have, want)
    return True, "map %s" % have


def bridge_map_info():
    """One read-only jawa/map_info call on the running game; an error is returned as the reply, never raised."""
    try:
        sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
        import rimbridge_client as rc
        host, port, token = rc.resolve_endpoint(None, None, None, None)
        with rc.RimBridge(host, port, token, timeout=60) as rb:
            return rb.call("jawa/map_info", {})
    except Exception as e:  # noqa: BLE001 -- any bridge failure is an unreadable biome, never a pass
        return {"success": False, "error": "%s: %s" % (type(e).__name__, e)}


def check(sheet_dir, max_age_min, biome=None, map_info=None):
    path = newest(sheet_dir)
    if not path:
        return 1, "no Scarlands run JSON under %s" % sheet_dir
    age = (time.time() - os.path.getmtime(path)) / 60.0
    if age > max_age_min:
        return 1, "newest run %s is %.0f min old (> %d): rerun the live half" % (path, age, max_age_min)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    why = refused(data)
    if why:
        return 2, "UNMEASURED  modcheck refused the run (%s): %s  [%s]" % (
            (data.get("summary") or {}).get("unmeasured") or "refused", why[:300], path)
    ok, line = judge(data)
    if ok and biome:
        ok, bline = judge_biome((map_info or bridge_map_info)(), biome)
        line = "%s; %s" % (line, bline)
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
        os.utime(p, None)
        with open(p, "w", encoding="utf-8") as f:     # stale_load refusal (2026-11-05T23:44 run): UNMEASURED, not FAIL
            json.dump({"summary": {"chains": [], "refused": "UNMEASURED: the running load is not the composed list",
                                   "unmeasured": "stale_load"}}, f)
        if check(td, 60, "RM_Warscar", lambda: {"mapBiome": "RM_Warscar"})[0] != 2:
            bad.append("refused run is not UNMEASURED")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(run(good), f)
        for name, info, want in [
                ("warscar map", {"mapBiome": "RM_Warscar", "tile": 7}, 0),
                ("non-Warscar map", {"mapBiome": "AridShrubland", "tile": 7}, 1),
                ("no mapBiome", {"tile": 7}, 1),
                ("bridge refused", {"success": False, "error": "no game"}, 1),
                ("bridge unreachable", None, 1)]:
            if check(td, 60, "RM_Warscar", lambda i=info: i)[0] != want:
                bad.append(name)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(run([(ROW, "FAIL", "")]), f)
        if check(td, 60, "RM_Warscar", lambda: {"mapBiome": "RM_Warscar"})[0] != 1:
            bad.append("Warscar map, row FAIL")
        with open(p, "w", encoding="utf-8") as f:     # the command line: --biome must reach the bridge read
            json.dump(run(good), f)
        global bridge_map_info
        real = bridge_map_info
        try:
            bridge_map_info = lambda: {"mapBiome": "AridShrubland"}
            if main(["--dir", td, "--biome", "RM_Warscar"]) != 1:
                bad.append("main --biome on a non-Warscar map")
            bridge_map_info = lambda: {"mapBiome": "RM_Warscar"}
            if main(["--dir", td, "--biome", "RM_Warscar"]) != 0:
                bad.append("main --biome on a Warscar map")
        finally:
            bridge_map_info = real
    print("selftest %s%s" % ("OK" if not bad else "FAILED: ", ", ".join(bad)))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--max-age-min", type=int, default=60)
    ap.add_argument("--dir", default=SHEET_DIR)
    ap.add_argument("--biome", help="BiomeDef the running game's current map must be (bridge jawa/map_info)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    code, line = check(a.dir, a.max_age_min, a.biome)
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
