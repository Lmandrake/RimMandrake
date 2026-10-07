#!/usr/bin/env python3
"""knockback_runner.py - in-game runner scenes for Explosive Knockback (design §8.2).

    python.exe src\\RimMandrake\\ExplosiveKnockback\\knockback_runner.py [--scenes a,b,...] [--ticks 300]

Needs python.exe (the bridge binds Windows loopback), a running game with a SCRATCH map (each scene clears a 15x15
patch), and the mod loaded (FlowWorks too, for the pit scenes). Per scene: jawa/static_call
RimMandrake.ExplosiveKnockback.RM_KnockbackProof.Stage("<scene>,x,z") builds it and sets the blast off,
rimworld/step_game_ticks advances time without unpausing, then .Verdict("<scene>") reads the knockback JOURNAL plus
map state and returns PASS/FAIL/INVALID/ERROR. The verdict is the game's; this script only records it, plus the
journal, to Transient/explosive_knockback/run_<stamp>.jsonl. Exit 0 only when every scene PASSed.
"""
import argparse
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))

PROOF = "RimMandrake.ExplosiveKnockback.RM_KnockbackProof"


def parse_verdict(text):
    """'PASS name detail...' -> (status, name, detail). Anything else is ERROR."""
    t = str(text or "").strip()
    head = t.split(" ", 2)
    if head and head[0] in ("PASS", "FAIL", "INVALID", "ERROR", "STAGED"):
        return head[0], head[1] if len(head) > 1 else "", head[2] if len(head) > 2 else ""
    return "ERROR", "", t


def overall(rows):
    if not rows:
        return "INCOMPLETE"
    st = [r["status"] for r in rows]
    if "FAIL" in st or "ERROR" in st:
        return "FAIL"
    if "INVALID" in st:
        return "INVALID"
    return "PASS"


def call(b, method, arg):
    r = b.call("jawa/static_call", {"type": PROOF, "method": method, "args": arg})
    if isinstance(r, dict):
        return str(r.get("result", r.get("value", r)))
    return str(r)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenes", default="")
    ap.add_argument("--ticks", type=int, default=300)
    ap.add_argument("--out", default=os.path.join(REPO, "Transient", "explosive_knockback"))
    a = ap.parse_args()
    from rimbridge_client import RimBridge, resolve_endpoint
    host, port, token = resolve_endpoint()
    os.makedirs(a.out, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    path = os.path.join(a.out, "run_%s.jsonl" % stamp)
    rows = []
    with RimBridge(host=host, port=port, token=token) as b:
        names = call(b, "Names", "x")
        print("scenes available:", names)
        scenes = [s for s in (a.scenes.split(",") if a.scenes else names.split(" ")[0].split(",")) if s]
        origins = call(b, "Origins", str(len(scenes))).split(";")
        if len(origins) < len(scenes):
            print("map too small for %d scenes (%d origins)" % (len(scenes), len(origins)))
            return 2
        call(b, "Settings", "reset")
        call(b, "Clear", "x")
        for name, org in zip(scenes, origins):
            staged = call(b, "Stage", "%s,%s" % (name, org))
            st, _, detail = parse_verdict(staged)
            if st != "STAGED":
                rows.append({"type": "scenario", "scene": name, "status": st, "detail": detail, "origin": org})
                print("%-16s %s %s" % (name, st, detail))
                continue
            b.call("rimworld/step_game_ticks", {"ticks": a.ticks})
            st, _, detail = parse_verdict(call(b, "Verdict", name))
            rows.append({"type": "scenario", "scene": name, "status": st, "detail": detail, "origin": org})
            print("%-16s %s %s" % (name, st, detail))
        call(b, "Settings", "reset")
        journal = call(b, "Journal", "4000")
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
        for line in journal.splitlines():
            if line.strip().startswith("{"):
                f.write(json.dumps({"type": "journal", "rec": line.strip()}) + "\n")
        v = overall(rows)
        f.write(json.dumps({"type": "run_end", "verdict": v, "scenes": len(rows)}) + "\n")
    print("VERDICT %s  (%d scenes) -> %s" % (v, len(rows), path))
    return 0 if v == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
