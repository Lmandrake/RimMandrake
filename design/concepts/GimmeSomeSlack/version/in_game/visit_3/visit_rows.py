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
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import game_paths  # noqa: E402  (follows RM_GAME_INSTANCE: game b reads its own install)
GAME_VERSION = os.path.join(game_paths.GAME_DIR, "Version.txt")


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


IDENT = {}
HELD = []
SITE_CONDITIONS = "weather locked Clear, incident queue cleared (the proof's site pin); every part of the mod on"


def append(row):
    # the BUILD MATCH fields (build_match.py identity, run on the game machine after the deploy and the list swap) and
    # what the site held for this run (visit 2 and 3: the brief's row shape)
    row = dict(row, **IDENT)
    row.setdefault("held", list(HELD))
    row.setdefault("site_conditions", SITE_CONDITIONS)
    row.setdefault("game_instance", "ArchBig")
    if row["verdict"] == "PASS":
        row.setdefault("outcome", "SUCCESS")
        row.setdefault("forbidden", [])
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
    if a.identity:
        IDENT.update(json.load(open(a.identity)))
    if a.held:
        HELD.extend(h for h in a.held.split(",") if h)
    res = json.load(open(a.proof))
    over = {}
    for o in a.override or []:
        k, v = o.split("=", 1)
        st, why = v.split(":", 1)
        over[k] = (st, why)
    klass = {}
    for o in a.class_of or []:
        k, v = o.split("=", 1)
        c, why = v.split(":", 1)
        klass[k] = (c, why)
    rows = []
    for r in res.get("rows") or []:
        r2 = {"id": r["id"], "status": r["status"], "class": r.get("class"), "detail": str(r.get("detail"))[:600]}
        if r["id"] in over:
            r2["status_recorded"] = r2["status"]
            r2["status"], r2["override_why"] = over[r["id"]]
        rows.append(r2)
    # proof_all keeps some PASS rows of a shared session in its notes (S7_save_load_styles sits in d4_save_notes); a row-shaped
    # dict there is the same row, so it is read too (visit 1, 2026-11-16: sc_four_looks read S7 MISSING without this)
    have = {r["id"] for r in rows}
    for k, v in res.items():
        if k.endswith("_notes") and isinstance(v, list):
            for r in v:
                if isinstance(r, dict) and isinstance(r.get("id"), str) and r.get("status") in ("PASS", "FAIL", "UNMEASURED") \
                        and r["id"] not in have:
                    r2 = {"id": r["id"], "status": r["status"], "class": r.get("class"), "detail": str(r.get("detail"))[:600], "from_notes": k}
                    if r["id"] in over:
                        r2["status_recorded"] = r2["status"]
                        r2["status"], r2["override_why"] = over[r["id"]]
                    rows.append(r2)
                    have.add(r["id"])
    if a.gate:
        g = json.load(open(a.gate))
        st = ((g.get("steps") or {}).get("validation_offline") or {}).get("statuses") or {}
        have = {r["id"] for r in rows}
        rows += [{"id": k, "status": v, "class": "OFFLINE_GATE", "detail": "proof_all.py --offline-gate"} for k, v in sorted(st.items())
                 if k not in have]
    if a.only:                                # an excluded row is not this run's evidence: it must not feed a scene read either
        keep = set(a.only.split(","))         # (visit 2, 19:19: run 3's SL3, excluded as a harness split, still turned
        rows = [r for r in rows if r["id"] in keep or r.get("class") == "OFFLINE_GATE"]   # sc_true_to_grid FAIL via the slim)
    env = res.get("env") or {}
    if not env and a.env:                     # a one-row result (gravship_scene, --removal-check) records no env: the list it ran on, read at the run
        env = json.load(open(a.env))
    os.makedirs(EV, exist_ok=True)
    order = len(glob.glob(os.path.join(EV, "*.slim.json")))
    game = open(GAME_VERSION).read().strip() if os.path.exists(GAME_VERSION) else "UNMEASURED"
    slim = {"label": a.label, "order": order, "source": os.path.abspath(a.proof), "mode": res.get("mode"), "env": env,
            "active_mods": env.get("running"), "game_build": game, "run_identity": res.get("run_identity"),
            "mod_hash": res.get("mod_hash"), "rows": rows}
    ev = os.path.join(EV, a.label + ".slim.json")
    json.dump(slim, open(ev, "w"), indent=1)
    ident = res.get("run_identity") or {}
    sha = ((ident.get("git") or {}).get("sha") or a.sha or "UNMEASURED")[:10]
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
        if rid in klass:        # --class-of: names the class of a failed row and why; the verdict stays the proof's
            r = dict(r, **{"class": klass[rid][0], "override_why": klass[rid][1]})
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
        # a scene is written only from a run on the tier the table names for it (visit 2: scene rows written on the wrong
        # tier never counted at the build match); --scenes-tier names this run's tier
        if a.scenes_tier and (tests[tid].get("tier") or "gimmesomeslack") != a.scenes_tier:
            continue
        try:
            st, det = V.scene_verdict(tid, merged)
        except KeyError:                      # not a scenes.json scene (sc_stub_joins): its own command writes its row
            continue
        # an unchanged verdict on the SAME build adds nothing; on another build (a rerun after a change) it is that build's
        # row, or the build match keeps reading the old build's row (2026-11-22 rerun on 244ae76cdf)
        if tid in last and last[tid]["verdict"] == st and last[tid].get("detail") == det["rows"] \
                and last[tid].get("mod_hash") == IDENT.get("mod_hash"):
            continue
        # a scene whose rows have not all run yet is not a run of that scene: no row until they have (or --final)
        # (visit 1: interim MISSING-only rows read as UNMEASURED history to maturation.py next)
        if not a.final and any("MISSING" in v for v in det["rows"].values()):
            continue
        append({"test": tid, "verdict": st, "site_checked": tier_ok, "game": "archmagi", "mod_sha": sha,
                "command": "python3 src/RimMandrake/GimmeSomeSlack/validation.py --scenes-from <proof json> (scene_verdict over the latest row of each id across this visit's runs)",
                "evidence": rel_ev, "run": a.label, "detail": det["rows"]})
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
    p.add_argument("--class-of", dest="class_of", action="append", help="id=CLASS:why -- the class of a failed row, verdict unchanged")
    p.add_argument("--final", action="store_true", help="write scene rows even where an input row is MISSING (the visit's last add)")
    p.add_argument("--sha", help="the deployed source's sha, for a result that records no run_identity")
    p.add_argument("--env", help="JSON {running: [...], tier: {active_equals_running: bool}} for a result that records no env")
    p.add_argument("--identity", help="the one JSON line build_match.py identity printed for this run's deploy and list")
    p.add_argument("--scenes-tier", help="write scene rows only for scenes whose test-table tier is this (the run's tier)")
    p.add_argument("--held", help="comma list of what the site switched off or locked for this run (weather, fire, ...)")
    a = ap.parse_args()
    if a.cmd != "add":
        ap.print_help()
        return 2
    add(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
