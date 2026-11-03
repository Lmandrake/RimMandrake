#!/usr/bin/env python3
"""Selftest for NS_CAPTURE_DOWN_FIX_OWN_PIRATE_TRIPS: the pit_prison_room capture and warden rows no longer go
UNMEASURED on hostile_arrival (the chain's own spawned Pirate), as measured by the test queue's records.

The records (TESTQ_QUEUE/done/J*.json, default /mnt/d/ClaudeWork/rimmandrake/testq) live on Archmagi only, so the
evidence is committed as a snapshot beside the item's live proofs:
  infrastructure/state/live_proofs/NS_CAPTURE_DOWN_FIX_OWN_PIRATE_TRIPS.rows.json
holding every pit_prison_room row of every done record from J20261025 through the snapshot's last file, every
hostile_arrival row of any other chain (the sanity probe: the instrument can see the string), and each contributing
record's sha256.

Reds on:
  - any pit_prison_room row in the window carrying hostile_arrival in its detail;
  - the sanity probe finding no hostile_arrival row in any other chain (a blind instrument);
  - jobs J20261026T082603Z-2edef1, J20261029T083002Z-af6894, J20261031T212349Z-3091f9 not holding PASS on
    capture_down_from_the_lip, capture_down_off, warden_served_from_lip and warden_lip_off;
  - fewer than 60 pit_prison_room rows (the window went empty or the parser stopped seeing rows);
  - when the records are reachable: the snapshot differing in any way from one re-derived from them
    (a hand-edited or stale snapshot);
  - any built-in mutant (each check fed a broken copy) staying green.

`--write` re-derives the snapshot from the records (a human or agent step, never run by the selftest).
Offline: no game, no bridge, no ledger write; reads only.
"""
import copy
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SNAPSHOT = os.path.join(REPO, "infrastructure", "state", "live_proofs",
                        "NS_CAPTURE_DOWN_FIX_OWN_PIRATE_TRIPS.rows.json")
QUEUE = os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq")
WINDOW_START = "J20261025"   # fix fa3926c5ae landed 2026-10-25T06:27Z
CHAIN = "pit_prison_room"
MARK = "hostile_arrival"
NAMED_JOBS = ("J20261026T082603Z-2edef1", "J20261029T083002Z-af6894", "J20261031T212349Z-3091f9")
NAMED_ROWS = ("capture_down_from_the_lip", "capture_down_off", "warden_served_from_lip", "warden_lip_off")
MIN_ROWS = 60


def derive(done_dir, last_file=None):
    """The snapshot, from the records in done_dir between WINDOW_START and last_file (inclusive)."""
    names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(done_dir, "J*.json")))
    names = [n for n in names if n >= WINDOW_START and (last_file is None or n <= last_file)]
    jobs, probe, shas = [], [], {}
    for n in names:
        path = os.path.join(done_dir, n)
        with open(path, "rb") as fh:
            raw = fh.read()
        rec = json.loads(raw)
        rows = ((rec.get("result") or {}).get("rows")) or []
        pit = [{"row": r.get("row"), "verdict": r.get("verdict"), "detail": r.get("detail") or ""}
               for r in rows if r.get("chain") == CHAIN]
        other = [{"chain": r.get("chain"), "row": r.get("row"), "verdict": r.get("verdict")}
                 for r in rows if r.get("chain") != CHAIN and MARK in (r.get("detail") or "")]
        job = n[:-5]
        if pit:
            jobs.append({"job": job, "host": (rec.get("result") or {}).get("host"), "rows": pit})
        if other:
            probe.append({"job": job, "rows": other})
        if pit or other:
            shas[job] = hashlib.sha256(raw).hexdigest()
    return {"item": "NS_CAPTURE_DOWN_FIX_OWN_PIRATE_TRIPS", "window_start": WINDOW_START,
            "last_file": names[-1] if names else None, "files_scanned": len(names),
            "jobs": jobs, "sanity_probe": probe, "record_sha256": shas}


def check(snap):
    """Problems with a snapshot; empty means green."""
    bad = []
    rows = [(j["job"], r) for j in snap.get("jobs", []) for r in j["rows"]]
    if len(rows) < MIN_ROWS:
        bad.append("only %d %s rows in the window (< %d): window empty or parser blind" % (len(rows), CHAIN, MIN_ROWS))
    for job, r in rows:
        if MARK in r["detail"]:
            bad.append("%s %s %s carries %s: %s" % (job, r["row"], r["verdict"], MARK, r["detail"][:160]))
    if not any(p["rows"] for p in snap.get("sanity_probe", [])):
        bad.append("sanity probe: no %s row in any other chain; the instrument cannot see the string" % MARK)
    by_job = {j["job"]: {r["row"]: r["verdict"] for r in j["rows"]} for j in snap.get("jobs", [])}
    for job in NAMED_JOBS:
        got = by_job.get(job)
        if got is None:
            bad.append("named job %s absent from the snapshot" % job)
            continue
        for row in NAMED_ROWS:
            if got.get(row) != "PASS":
                bad.append("%s %s is %s, not PASS" % (job, row, got.get(row)))
    return bad


def mutants(snap):
    """(name, broken copy): every one must make check() red."""
    out = []
    m = copy.deepcopy(snap)
    for j in m["jobs"]:
        for r in j["rows"]:
            if r["row"] == "warden_lip_off":
                r["detail"] = "surprise: safe_advance stopped after 60 of 900 tick(s): hostile_arrival: Pirate"
                break
        else:
            continue
        break
    out.append(("pit row carrying hostile_arrival", m))
    m = copy.deepcopy(snap)
    m["sanity_probe"] = []
    out.append(("sanity probe blind", m))
    for job in NAMED_JOBS:
        for row in NAMED_ROWS:
            m = copy.deepcopy(snap)
            for j in m["jobs"]:
                if j["job"] == job:
                    for r in j["rows"]:
                        if r["row"] == row:
                            r["verdict"] = "UNMEASURED"
            out.append(("%s %s UNMEASURED" % (job, row), m))
    m = copy.deepcopy(snap)
    m["jobs"] = [j for j in m["jobs"] if j["job"] != NAMED_JOBS[1]]
    out.append(("named job dropped", m))
    m = copy.deepcopy(snap)
    m["jobs"] = m["jobs"][:2]
    out.append(("window nearly empty", m))
    return out


def main(argv):
    if "--write" in argv:
        snap = derive(os.path.join(QUEUE, "done"))
        with open(SNAPSHOT, "w") as fh:
            json.dump(snap, fh, indent=1, sort_keys=True)
            fh.write("\n")
        print("wrote %s: %d files, %d jobs with %s rows" % (SNAPSHOT, snap["files_scanned"], len(snap["jobs"]), CHAIN))
        return 0
    fails = []
    with open(SNAPSHOT) as fh:
        snap = json.load(fh)
    nrows = sum(len(j["rows"]) for j in snap["jobs"])
    bad = check(snap)
    fails += ["snapshot: " + b for b in bad]
    print("snapshot: %d files, %d %s rows, %d probe rows elsewhere, %d problems"
          % (snap["files_scanned"], nrows, CHAIN, sum(len(p["rows"]) for p in snap["sanity_probe"]), len(bad)))
    done = os.path.join(QUEUE, "done")
    if os.path.isdir(done) and glob.glob(os.path.join(done, "J*.json")):
        fresh = derive(done, snap["last_file"])
        if fresh != snap:
            diff = [k for k in sorted(set(fresh) | set(snap)) if fresh.get(k) != snap.get(k)]
            fails.append("snapshot differs from the records in %s on: %s" % (done, ", ".join(diff)))
        else:
            print("records reachable at %s: snapshot re-derived identically" % done)
        tampered = copy.deepcopy(snap)
        tampered["jobs"][0]["rows"][0]["verdict"] = "FAIL" if tampered["jobs"][0]["rows"][0]["verdict"] != "FAIL" else "PASS"
        if fresh == tampered:
            fails.append("mutant 'hand-edited snapshot' not caught by the re-derivation")
    else:
        print("records not reachable at %s: snapshot checked on its own" % done)
    for name, m in mutants(snap):
        if not check(m):
            fails.append("mutant '%s' stayed green" % name)
    for f in fails:
        print("FAIL " + f)
    print("RESULT: %s" % ("FAIL" if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
