#!/usr/bin/env python3
"""map_agreement.py - how often the situation map's model agrees with the running game (Explosive Knockback).

The offline map (Source/SelfTest/KnockbackMap.cs, selftest_explosiveknockback_map.py) runs the shipped throw decision on a
MODEL of the map. This is the model's live check: each exported case is staged in the game from the same spec
(RM_KnockbackProof.MapCase), the blast set off, the clock advanced, and every thing's end cell read (MapRead) and compared with
where the model put it. A case agrees when every thing ends on a cell the model allows (it gives two where the game's
"place near" tie order decides) with the same in-pit state, and the same covers stand.

    1. export the cases (WSL):  python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_kernel.py is the build;
       the export is `--map-export <windows path>` on the SelfTest (see proof/map_agreement_export.sh)
    2. run them (python.exe: the bridge binds Windows loopback; proof build deployed; a scratch map; FlowWorks loaded):
       python.exe src\\RimMandrake\\ExplosiveKnockback\\proof\\map_agreement.py --cases <cases.jsonl> [--out <result.jsonl>] [--only N,M] [--ticks 300]

Exit 0 only when every case agrees. A disagreement is printed with the spec, what the model expected and what the game did:
explain each one before trusting the map around it.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(MOD, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
sys.path.insert(0, MOD)


def parse_read(text):
    """'READ a=4,0,0,ok;o=3,0,1,ok|covers=3,0/3,2' -> ({key: (cell+pit, state)}, covers set)."""
    body = text.split("READ ", 1)[1]
    things, covers = body.split("|covers=")
    got = {}
    for part in things.split(";"):
        if not part:
            continue
        key, val = part.split("=")
        x, z, pit, state = val.split(",")
        got[key] = ("%s,%s,%s" % (x, z, pit), state)
    return got, set(c for c in covers.strip().split("/") if c)


def compare(case, got, covers):
    """[] when the game agrees with the model, else one line per difference."""
    diffs = []
    for key, allowed in case["expect"].items():
        if key not in got:
            diffs.append("%s: not read" % key)
            continue
        cell, state = got[key]
        if state in ("air", "dead"):
            diffs.append("%s: %s at the read" % (key, state))
        elif cell not in allowed:
            diffs.append("%s: game %s, model %s" % (key, cell, " or ".join(allowed)))
    want = set(c for c in case["covers"].split("/") if c)
    if covers != want:
        diffs.append("covers: game %s, model %s" % (sorted(covers), sorted(want)))
    return diffs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cases", required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--only", default="", help="comma-separated case numbers (1-based)")
    ap.add_argument("--ticks", type=int, default=300)
    a = ap.parse_args()
    import knockback_runner as KR
    from rimbridge_client import RimBridge, resolve_endpoint
    from proof_build_gate import require_proof_build
    cases = [json.loads(l) for l in open(a.cases, encoding="utf-8") if l.strip()]
    only = set(int(n) for n in a.only.split(",") if n)
    host, port, token = resolve_endpoint()
    rows, agree = [], 0
    with RimBridge(host=host, port=port, token=token) as b:
        names = KR.call(b, "Names", "x")
        require_proof_build(names)
        origins = KR.call(b, "Origins", "6").split(";")
        snap = KR.snapshot_settings(b)
        try:
            KR.call(b, "Settings", "reset")
            for i, case in enumerate(cases, 1):
                if only and i not in only:
                    continue
                KR.call(b, "Clear", "x")
                staged = ""
                # the sites take turns: a gas cell bursts at most once in 600 ticks (GasCellOnceTicks), so two gas cases
                # 300 ticks apart on one cell would read the second as "nothing moved" (run 1: every other gas case)
                turn = origins[(i - 1) % len(origins):] + origins[:(i - 1) % len(origins)]
                for org in turn:                          # a site that reads a pond bed is skipped, the next one tried
                    staged = KR.call(b, "MapCase", "%s@%s" % (org, case["spec"]))
                    if staged.startswith("STAGED"):
                        break
                row = {"n": i, "spec": case["spec"], "expect": case["expect"], "covers": case["covers"], "map": case.get("map")}
                if not staged.startswith("STAGED"):
                    row.update(status="INVALID", detail=staged)
                else:
                    adv = KR.advance_scene(b, a.ticks)
                    read = KR.call(b, "MapRead", "x")
                    if not read.startswith("READ ") or not adv["reached"]:
                        row.update(status="INVALID", detail="read %r, advance %r" % (read[:200], adv))
                    else:
                        got, covers = parse_read(read)
                        diffs = compare(case, got, covers)
                        row.update(status="AGREE" if not diffs else "DISAGREE", detail="; ".join(diffs), got={k: v[0] for k, v in got.items()},
                                   gameCovers=sorted(covers))
                        if diffs:
                            row["journal"] = [l for l in KR.call(b, "Journal", "60").splitlines() if l.strip().startswith("{")]
                agree += row["status"] == "AGREE"
                rows.append(row)
                print("%3d %-8s %s%s" % (i, row["status"], case["spec"], ("  <- " + row["detail"]) if row["detail"] else ""), flush=True)
        finally:
            KR.restore_settings(b, snap)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    invalid = sum(1 for r in rows if r["status"] == "INVALID")
    print("MAP AGREEMENT %d of %d cases agree (%d disagree, %d invalid); model %s" % (
        agree, len(rows), len(rows) - agree - invalid, invalid, cases[0].get("map") if cases else "?"))
    return 0 if rows and agree == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
