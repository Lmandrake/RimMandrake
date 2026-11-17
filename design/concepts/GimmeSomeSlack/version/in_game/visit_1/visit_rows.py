#!/usr/bin/env python3
"""visit_rows.py -- append Stage 6 rows (rows.jsonl) from one live proof result, and re-read every scene.

    python3 visit_rows.py add <proof.json> --label <run label> [--gate <gate.json>] [--only id,id] [--override id=STATUS:why ...]

* Each P_<row> test of the test table found in the proof's rows gets a row with that row's status (PASS/FAIL/UNMEASURED).
* A slim copy of the proof (rows, env, identity; details cut to 600 chars) goes to evidence/<label>.slim.json beside the
  active mod list (env.running, in load order) and the game build, so each row names what it ran on.
* --gate: the offline gate's GATE_JSON (proof_all.py --offline-gate, same sha); its validation_offline.statuses join the
  scene reads as rows (RIMMANDRAKE_CARRY_GSS_GATE_ROWS_SCENES_NEVER_SAW).
* Then every sc_* scene of the test table is read with validation.scene_verdict over the LATEST status of each proof row
  across every slim evidence file added so far (a later run's row replaces an earlier one), and a scene row is appended
  whenever its verdict differs from its last row (or it has none).
* --override id=STATUS:why replaces the status of one proof row of THIS run before anything is written (a check judged
  wrong is UNMEASURED with its why; never used to upgrade a row).
Rows are append-only: an earlier FAIL stays as history; the pipeline reads each test's last row.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack")
sys.path.insert(0, GSS)
TABLE = os.path.join(REPO, "design", "concepts", "GimmeSomeSlack", "version", "test_table.json")
ROWS = os.path.join(HERE, "rows.jsonl")
EV = os.path.join(HERE, "evidence")
GAME_VERSION = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Version.txt"


def stage6():
    t = json.load(open(TABLE))["tests"]
    return {k: e for k, e in t.items() if str(e.get("stage")) == "6"}


def last_rows():
    out = {}
    if os.path.exists(ROWS):
        for ln in open(ROWS):
            if ln.strip():
                r = json.loads(ln)
                out[r["test"]] = r
    return out


def append(row):
    with open(ROWS, "a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def merged_proof_rows():
    """Latest status per proof row id over every slim evidence file, oldest first (by its 'order')."""
    slims = sorted((json.load(open(p)) for p in glob.glob(os.path.join(EV, "*.slim.json"))), key=lambda s: s["order"])
    got = {}
    for s in slims:
        for r in s["rows"]:
            got[r["id"]] = {"id": r["id"], "status": r["status"], "from": s["label"]}
    return got


def add(a):
    import validation as V
    res = json.load(open(a.proof))
    over = {}
    for o in a.override or []:
        k, v = o.split("=", 1)
        st, why = v.split(":", 1)
        over[k] = (st, why)
    rows = []
    for r in res.get("rows") or []:
        r2 = {"id": r["id"], "status": r["status"], "class": r.get("class"), "detail": str(r.get("detail"))[:600]}
        if r["id"] in over:
            r2["status_recorded"] = r2["status"]
            r2["status"], r2["override_why"] = over[r["id"]]
        rows.append(r2)
    if a.gate:
        g = json.load(open(a.gate))
        st = ((g.get("steps") or {}).get("validation_offline") or {}).get("statuses") or {}
        have = {r["id"] for r in rows}
        rows += [{"id": k, "status": v, "class": "OFFLINE_GATE", "detail": "proof_all.py --offline-gate"} for k, v in sorted(st.items())
                 if k not in have]
    env = res.get("env") or {}
    os.makedirs(EV, exist_ok=True)
    order = len(glob.glob(os.path.join(EV, "*.slim.json")))
    game = open(GAME_VERSION).read().strip() if os.path.exists(GAME_VERSION) else "UNMEASURED"
    slim = {"label": a.label, "order": order, "source": os.path.abspath(a.proof), "mode": res.get("mode"), "env": env,
            "active_mods": env.get("running"), "game_build": game, "run_identity": res.get("run_identity"),
            "mod_hash": res.get("mod_hash"), "rows": rows}
    ev = os.path.join(EV, a.label + ".slim.json")
    json.dump(slim, open(ev, "w"), indent=1)
    ident = res.get("run_identity") or {}
    sha = ((ident.get("git") or {}).get("sha") or "UNMEASURED")[:10]
    tier_ok = bool((env.get("tier") or {}).get("active_equals_running"))
    only = set(a.only.split(",")) if a.only else None
    tests = stage6()
    rel_ev = os.path.relpath(ev, REPO)
    cmd = a.command or "python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live"
    by_id = {r["id"]: r for r in rows}
    n = 0
    for tid in sorted(tests):
        if not tid.startswith("P_"):
            continue
        rid = tid[2:]
        if rid not in by_id or (only and rid not in only):
            continue
        r = by_id[rid]
        append({"test": tid, "verdict": r["status"], "site_checked": tier_ok, "game": "archmagi", "mod_sha": sha,
                "command": cmd, "evidence": rel_ev, "run": a.label, "class": r.get("class"),
                "why": r.get("override_why") or (r["detail"][:300] if r["status"] != "PASS" else None)})
        n += 1
    merged = list(merged_proof_rows().values())
    last = last_rows()
    m = 0
    for tid in sorted(tests):
        if not tid.startswith("sc_") or tests[tid].get("file", "").endswith("gss_playtest_runner.py"):
            continue
        st, det = V.scene_verdict(tid, merged)
        if tid in last and last[tid]["verdict"] == st and last[tid].get("detail") == det["rows"]:
            continue
        append({"test": tid, "verdict": st, "site_checked": tier_ok, "game": "archmagi", "mod_sha": sha,
                "command": "python3 src/RimMandrake/GimmeSomeSlack/validation.py --scenes-from <proof json> (scene_verdict over the latest row of each id across this visit's runs)",
                "evidence": os.path.relpath(EV, REPO), "run": a.label, "detail": det["rows"]})
        m += 1
    print("appended %d proof rows and %d scene rows (evidence %s)" % (n, m, rel_ev))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("add")
    p.add_argument("proof")
    p.add_argument("--label", required=True)
    p.add_argument("--gate")
    p.add_argument("--only")
    p.add_argument("--command")
    p.add_argument("--override", action="append")
    a = ap.parse_args()
    if a.cmd != "add":
        ap.print_help()
        return 2
    add(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
