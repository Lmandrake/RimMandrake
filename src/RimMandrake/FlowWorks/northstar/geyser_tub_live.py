#!/usr/bin/env python3
"""geyser_tub_live.py -- Stage 6 check sc_geyser_tub (inv_geyser_tub), FlowWorks 0.1.0 visit 1. Run AFTER
`geyser_pit_scene.py <out> stage` on the calm site (its G2_water1m pool: geyser 64,98, 1 m of water in a 4 m pit; G1_dry).

    python.exe src/RimMandrake/FlowWorks/northstar/geyser_tub_live.py <out.json>       exit 0 PASS, 1 FAIL, 2 UNMEASURED

Rows: TUB_reads_hot_tub (the player's terrain line, RM_Patch_MouseoverDepth.ProofPitLabel, says "Hot tub" on the water
pool), TUB_dry_pit_not_a_tub (G1 dry pit: no "Hot tub"), TUB_beside_stays_cold (a 2x2 water pit dug 4 squares off the
G2 pool: no "Hot tub"), TUB_pawn_soaks_bonus (an ordered RM_SoakInGeyserPool with target A the geyser: RM_HotPoolSoak
while in, RM_HotPoolAfterglow after). The draft scene_geyser_tub read inspect_string and a 'HotSpring' need, which the mod
never writes; this replaces it.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "Utils"))
import validation_core as V  # noqa: E402
from live_session import hediffs  # noqa: E402

LABEL = "RimMandrake.FlowWorks.RM_Patch_MouseoverDepth"
POOL = "RimMandrake.FlowWorks.RM_GeyserPoolProof"
G2, G2_FLOOR, G1_FLOOR = (64, 98), (63, 97), (20, 69)
BESIDE = [(70, 97), (71, 97), (70, 98), (71, 98)]


def main(argv):
    out_path = argv[1]
    B = V.Bridge()
    rows = []

    def row(i, ok, detail, unmeasured=False):
        rows.append({"id": i, "status": "UNMEASURED" if unmeasured else ("PASS" if ok else "FAIL"), "detail": str(detail)[:500]})

    def label(c):
        return str(B.call("jawa/static_call", type=LABEL, method="ProofPitLabel", args="%d,%d" % c).get("result"))

    gey = B.call("jawa/list_things", defName="SteamGeyser", rect="%d,%d,2,2" % G2).get("things") or []
    if not gey or not label(G2_FLOOR).startswith("line=Pit"):
        row("TUB_staging", False, "no G2 pool: run geyser_pit_scene.py <out> stage first (%s)" % gey, unmeasured=True)
    else:
        g = gey[0]["id"]
        t = label(G2_FLOOR)
        row("TUB_reads_hot_tub", "Hot tub" in t and "Water 1.00 m" in t, t)
        t = label(G1_FLOOR)
        row("TUB_dry_pit_not_a_tub", t.startswith("line=Pit") and "Hot tub" not in t, t)
        for x, z in BESIDE:
            B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=8, setBodyWaterM=1.0)
        t = label(BESIDE[0])
        row("TUB_beside_stays_cold", "water" in t and "Hot tub" not in t, t)
        r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=G2_FLOOR[0], z=G2_FLOOR[1], faction="player", count=1, xenotype="Baseliner")
        p = r["pawns"][0]["id"]
        o = B.call("jawa/ordered_job", pawnId=p, jobDef="RM_SoakInGeyserPool", targetAId=g, targetBX=G2_FLOOR[0], targetBZ=G2_FLOOR[1], waitTicks=1)
        B.ticks(600)
        mid = hediffs(B.call("jawa/pawn_get", pawn=p))
        proof = B.call("jawa/static_call", type=POOL, method="Read", args=g).get("result")
        B.ticks(2700)
        after = hediffs(B.call("jawa/pawn_get", pawn=p))
        if not o.get("accepted"):
            row("TUB_pawn_soaks_bonus", False, "soak order refused: %s" % o.get("note"), unmeasured=True)
        else:
            row("TUB_pawn_soaks_bonus", "RM_HotPoolSoak" in mid and "RM_HotPoolAfterglow" in after and "soakers=1" in str(proof),
                {"mid": mid, "after": after, "pool": proof})
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"script": __file__, "mode": "live", "rows": rows}, f, indent=1)
    for r in rows:
        print("%-10s %-24s %s" % (r["status"], r["id"], r["detail"][:200]))
    st = [r["status"] for r in rows]
    return 1 if "FAIL" in st else (2 if "UNMEASURED" in st else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
