#!/usr/bin/env python3
"""LIVE: do the four painted species draw their own head at the size the def sets, in the running game?

Item HEADS_VERIFY_SHRUNK_TO_FIT_THE_HATS. Owner card 2026-10-20 ("How should head sizes be set?" -> "Tune in the
def"): the art stays in the canvas frame and the on-screen skull is Big and Small's head rule times
SM_HeadSize_Cosmetic, a statOffset on the species' head gene (src/RimStarWars/StarWarsRaces/Defs/GeneDefs/SW_Genes.xml).
The offline half (selftest_head_scale_from_defs.py) proves the DEFS say so; this reads the GAME.

A deterministic STATE read, not a picture: stage_xenotype_grid.py spawns a Baseliner and one pawn per species, then
for each subject
  - jawa/pawn_get: it draws headType RSW_<S>_Head (the Baseliner draws a vanilla head);
  - jawa/static_call RimWorld.StatExtension.GetStatValue on the live pawn: SM_HeadSize_Cosmetic, SM_BodySizeOffset,
    SM_Cosmetic_BodySizeOffset (render reads both offsets, BSCache.totalCosmeticSize);
  - engine head scale = fit_head_canvas.bs_render_size(offset sum, head size) must equal head_envelope.json
    species_render[S].engine_head_scale and its onscreen_skull_target within 0.01.
Sanity probe that the instrument can see: the Baseliner must read head size 1.0 and offset 0, AND at least one species
must read a head size other than 1.0 (Lasat 0.88), so a stat read that always answers the stat's base fails.

RUN WITH python.exe (the bridge binds Windows loopback), on a loaded Playing map with StarWarsRaces active:
    python.exe "$(wslpath -w src/RimMandrake/Utils/art/heads_live_scale_check.py)" [--at 70,70] [--no-stage]
Exit 0 = every clause holds, 1 = a clause failed (printed), 2 = UNMEASURED (no bridge, no map, staging failed,
a stat the game does not know).
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, UTILS)
import fit_head_canvas as F  # noqa: E402
import rimbridge_client as rc  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

SPECIES = ("Lasat", "Mimbanese", "Nelvaanian", "Ortolan")
XENO = {sp: "RSW_RimMandrake%s" % sp for sp in SPECIES}
STATS = ("SM_HeadSize_Cosmetic", "SM_BodySizeOffset", "SM_Cosmetic_BodySizeOffset")
TOL = 0.01


def species_of(xeno):
    for sp, x in XENO.items():
        if xeno == x:
            return sp
    return "Baseliner" if xeno in (None, "", "Baseliner") else None


def stat(b, pid, name):
    r = b.call("jawa/static_call", {"type": "RimWorld.StatExtension", "method": "GetStatValue",
                                    "args": "%s|%s|true|-1" % (pid, name)}, check=False)
    if not r.get("success"):
        return None, r.get("message")
    try:
        return float(r.get("result")), None
    except (TypeError, ValueError):
        return None, "non-numeric result %r" % (r.get("result"),)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--at", default="70,70", help="x,z of the line-up (stage_xenotype_grid.py --at)")
    ap.add_argument("--no-stage", action="store_true", help="read subjects already standing near --at")
    a = ap.parse_args()

    render = json.load(open(os.path.join(HERE, "head_envelope.json"), encoding="utf-8"))["species_render"]

    if not a.no_stage:
        args = [os.path.join(UTILS, "stage_xenotype_grid.py"), "--at", a.at, "--per", "1", "--cols", "5",
                "--shot", "heads_live_scale", "--xenotypes", ",".join(["Baseliner"] + [XENO[s] for s in SPECIES])]
        try:
            code = subprocess.run([sys.executable] + args, timeout=300).returncode
        except subprocess.TimeoutExpired:
            code = "timeout"
        if code != 0:
            print("UNMEASURED: staging exited %s" % code)
            return 2

    host, port, token = rc.resolve_endpoint()
    if not token:
        print("UNMEASURED: no bridge token in Player.log")
        return 2
    fails, reads = [], {}
    with rc.RimBridge(host=host, port=port, token=token) as b:
        cx, cz = (int(v) for v in a.at.split(","))
        pawns = b.call("jawa/list_pawns", {}, check=False).get("pawns") or []
        near = [p for p in pawns if not p.get("dead") and p.get("x") is not None
                and abs(p["x"] - cx) <= 24 and abs(p["z"] - cz) <= 12]
        for p in near:
            snap = (b.call("jawa/pawn_get", {"pawn": str(p["id"])}, check=False).get("pawns") or [{}])[0]
            sp = species_of(snap.get("xenotype"))
            if sp is None or sp in reads:
                continue
            row = {"id": p["id"], "xenotype": snap.get("xenotype"), "headType": snap.get("headType")}
            for s in STATS:
                v, err = stat(b, p["id"], s)
                if v is None:
                    print("UNMEASURED: %s %s: %s" % (sp, s, err))
                    return 2
                row[s] = v
            reads[sp] = row

    for sp in ("Baseliner",) + SPECIES:
        r = reads.get(sp)
        if r is None:
            print("UNMEASURED: no %s subject near %s" % (sp, a.at))
            return 2
        off = r["SM_BodySizeOffset"] + r["SM_Cosmetic_BodySizeOffset"]
        head = F.bs_render_size(off, r["SM_HeadSize_Cosmetic"])[1]
        r["engine_head_scale"] = round(head, 3)
        line = "%-10s headType=%s head_size=%.3f offset=%.3f -> head scale %.3f" % (
            sp, r["headType"], r["SM_HeadSize_Cosmetic"], off, head)
        if sp == "Baseliner":
            if abs(r["SM_HeadSize_Cosmetic"] - 1.0) > 1e-3 or abs(off) > 1e-3:
                fails.append("Baseliner reads head size %.3f offset %.3f, not 1/0 (instrument or stray gene)"
                             % (r["SM_HeadSize_Cosmetic"], off))
            if (r["headType"] or "").startswith("RSW_"):
                fails.append("Baseliner draws a species head %s" % r["headType"])
        else:
            want = render[sp]
            if r["headType"] != "RSW_%s_Head" % sp:
                fails.append("%s draws headType %s, not RSW_%s_Head" % (sp, r["headType"], sp))
            if abs(r["SM_HeadSize_Cosmetic"] - want["head_size_multiplier"]) > TOL:
                fails.append("%s head size %.3f, def says %.3f" % (sp, r["SM_HeadSize_Cosmetic"],
                                                                   want["head_size_multiplier"]))
            if abs(head - want["engine_head_scale"]) > TOL or abs(head - want["onscreen_skull_target"]) > TOL:
                fails.append("%s head scale %.3f, want %.3f (target %.2f)" % (
                    sp, head, want["engine_head_scale"], want["onscreen_skull_target"]))
        print(line)
    if all(abs(reads[s]["SM_HeadSize_Cosmetic"] - 1.0) < 1e-3 for s in SPECIES):
        fails.append("every species reads head size 1.0: the stat read sees only the base (sanity probe)")
    for f in fails:
        print("FAIL", f)
    print("PASS" if not fails else "FAIL (%d)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
