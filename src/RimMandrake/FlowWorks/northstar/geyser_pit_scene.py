"""RIMMANDRAKE_FIX_GEYSER_PIT_G2_SCENE_NEEDS_A_LADDER: the geyser pits a human LOOKS at, staged so a colonist can get in.

    python.exe geyser_pit_scene.py <out.json> plan|stage|read
    stage: spawn missing geysers, clear sky, dig each 6x6 pit 4 m round its geyser, fill it, hang a ladder on its north
           wall and lower it, then read reachability: a colonist's path to a pit-floor square beside the vent.
    read:  RM_GeyserPoolProof.Read on every geyser, and the reach read again.
    exit 0 PASS, 1 FAIL (a pit no colonist can reach, a ladder not down), 2 UNMEASURED (no colonist on the map).

Brought into the repo from the AFK night's tool (D:\\ClaudeWork\\rimmandrake\\conductor\\afk_20261112_night\\live\\tools\\
geyser_scene.py), which dug the same pits with no way in: the owner, 2026-11-13, at G2: "People can't seem to get into
this geyser pit. I added northern wall ladder." The pure half (plan, ladder_spot, staging_problems) is selftested by
selftest_geyser_pit_scene.py, no bridge.
"""
import json
import os
import sys

DEPTH = 8                     # dug notches (4 m)
PIT = 6                       # pit side, cells; the 2x2 vent sits in the middle (2 cells of floor round it)
LADDER = "RM_Ladder"
NORTH = 0                     # ladder rotation: hung on the north wall (it faces the wall it climbs)
# name, geyser x, z (its 2x2 is x..x+1, z..z+1), fill notches, fluid; the AFK 2026-11-12 night's coordinates
PITS = [("G1_dry", 21, 70, 0, None), ("G2_water1m", 64, 98, 2, "RM_Fluid_Water"), ("G2h_water2m", 36, 149, 4, "RM_Fluid_Water"),
        ("Gbrim_water4m", 111, 230, 8, "RM_Fluid_Water"), ("G8_gen_dry_then_water", 189, 171, 0, None),
        ("G3_tar1m", 12, 112, 2, "RM_Fluid_Tar"), ("G4_oil1m", 27, 112, 2, "RM_Fluid_Oil"), ("G5_blood1m", 42, 112, 2, "RM_Fluid_Blood"),
        ("G6_slime1m", 80, 112, 2, "RM_Fluid_SlimeGreen"), ("G7_acid1m", 95, 112, 2, "RM_Fluid_AcidWater"),
        ("G8b_water_then_gen", 150, 112, 2, "RM_Fluid_Water")]


def pit_rect(gx, gz):
    """(x0, z0, w, h) of the pit dug round a geyser at gx, gz."""
    return gx - 2, gz - 2, PIT, PIT


def ladder_spot(gx, gz):
    """The ladder: on the pit's north row, one square in from the west corner (clear of the vent's 2x2), hung on the north
    wall."""
    x0, z0, w, h = pit_rect(gx, gz)
    return x0 + 1, z0 + h - 1, NORTH


def reach_target(gx, gz):
    """A pit-floor square beside the vent (west of it, a soaker's square): what a colonist must be able to walk to."""
    return gx - 1, gz


def plan(pits=PITS):
    return [dict(name=n, geyser=(gx, gz), rect=pit_rect(gx, gz), fill=f, fluid=fl, ladder=ladder_spot(gx, gz),
                 target=reach_target(gx, gz)) for n, gx, gz, f, fl in pits]


def staging_problems(rows):
    """Every pit a colonist could not enter as planned: no ladder, a ladder off the pit's north row or outside it, on the
    vent, not facing the wall it hangs on, or a reach target off the pit floor or on the vent. [] = enterable as planned."""
    out = []
    for r in rows:
        x0, z0, w, h = r["rect"]
        gx, gz = r["geyser"]
        vent = {(gx + i, gz + j) for i in (0, 1) for j in (0, 1)}
        lad = r.get("ladder")
        if not lad:
            out.append("%s: no ladder (no way in)" % r["name"])
        else:
            lx, lz, rot = lad
            if not (x0 <= lx < x0 + w and lz == z0 + h - 1) or rot != NORTH:
                out.append("%s: ladder %s is not on the pit's north row facing the north wall" % (r["name"], lad))
            if (lx, lz) in vent:
                out.append("%s: ladder on the vent" % r["name"])
        tx, tz = r.get("target") or (None, None)
        if tx is None or not (x0 <= tx < x0 + w and z0 <= tz < z0 + h) or (tx, tz) in vent:
            out.append("%s: reach target %s is not pit floor beside the vent" % (r["name"], r.get("target")))
    return out


def judge_reach(answers):
    """answers: name -> the ProofReach / ProofLadder line pair. PASS when every ladder is down and every target found."""
    bad = []
    for name, a in answers.items():
        if "raised=False" not in a.get("ladder", ""):
            bad.append("%s: ladder not down (%s)" % (name, a.get("ladder", "")[:80]))
        if "found=True" not in a.get("reach", "") or "reach=True" not in a.get("reach", ""):
            bad.append("%s: no colonist route into the pit (%s)" % (name, a.get("reach", "")[:120]))
    return bad


def main(argv):
    out, step = argv[1], argv[2] if len(argv) > 2 else "plan"
    rows = plan()
    res = {"step": step, "problems": staging_problems(rows)}
    if step == "plan" or res["problems"]:
        json.dump(dict(res, plan=rows), open(out, "w"), indent=1)
        print(json.dumps(res["problems"]) if res["problems"] else "PLAN ok: %d pits, each with a ladder" % len(rows))
        return 1 if res["problems"] else 0
    sys.path.insert(0, os.path.join(os.environ.get("RM_REPO", r"D:\Luke\dev\RimMandrake"), "src", "RimMandrake", "Utils"))
    import validation_core as V
    B = V.Bridge()

    def static(t, m, a):
        r = B.call("jawa/static_call", type=t, method=m, args=a) or {}
        return str(r.get("result") or r.get("error") or r.get("message") or r)

    def geysers():
        return {(t["x"], t["z"]): t["id"] for t in (B.call("jawa/list_things", defName="SteamGeyser", limit=50).get("things") or [])}

    G = geysers()
    if step == "stage":
        for r in rows:
            (gx, gz), (x0, z0, w, h) = r["geyser"], r["rect"]
            row = res.setdefault(r["name"], {})
            if (gx, gz) not in G:
                row["spawn"] = str(B.call("rimworld/spawn_thing", defName="SteamGeyser", x=gx, z=gz))[:160]
            row["sky"] = V.open_sky_site(B, (x0 - 3, z0 - 3, w + 6, h + 6)).get("ok")
            for i in range(w):
                for j in range(h):
                    # idempotent: dig only the notches still missing (a restage on a saved scene must not dig 8 m)
                    have = B.call("jawa/flowworks_excavation_drive", x=x0 + i, z=z0 + j, deepenLevels=0, setBodyWaterM=-1.0,
                                  fillInLevels=0) or {}
                    need = max(0, DEPTH - int(have.get("depth") or 0))
                    if need:
                        B.call("jawa/flowworks_excavation_drive", x=x0 + i, z=z0 + j, deepenLevels=need, setBodyWaterM=-1.0,
                               fillInLevels=0)
        B.ticks(70)
        for r in rows:
            x0, z0, w, h = r["rect"]
            lx, lz, rot = r["ladder"]
            row = res[r["name"]]
            if r["fill"]:
                # ProofFillRect takes METRES since the one water number (8734f51181); r["fill"] is notches (0.5 m)
                row["fill"] = static("RimMandrake.FlowWorks.RM_SubmergeDraw", "ProofFillRect",
                                     "%d,%d,%d,%d,%.2f,%s" % (x0, z0, w, h, r["fill"] * 0.5, r["fluid"]))
            row["ladder_spawn"] = str(B.call("jawa/spawn_batch", ops="%s:%d,%d,%d" % (LADDER, lx, lz, rot)))[:160]
        B.ticks(30)
        for r in rows:
            lx, lz, _ = r["ladder"]
            static("RimMandrake.FlowWorks.RM_PromotionProofs", "ProofLadder", "%d,%d,lower" % (lx, lz))
        G = geysers()
    colonists = (B.call("rimworld/list_colonists") or {}).get("colonists") or []
    pid = str(colonists[0].get("thingIdNumber") or colonists[0].get("pawnId") or colonists[0].get("id") or "").replace("Thing_Human", "").replace("Thing_", "") if colonists else ""
    answers = {}
    for r in rows:
        lx, lz, _ = r["ladder"]
        tx, tz = r["target"]
        gid = G.get(r["geyser"])
        a = answers.setdefault(r["name"], {})
        a["ladder"] = static("RimMandrake.FlowWorks.RM_PromotionProofs", "ProofLadder", "%d,%d,read" % (lx, lz))
        a["reach"] = static("RimMandrake.FlowWorks.Pits.RM_SuspensionProofs", "ProofReach", "%s;%d,%d" % (pid, tx, tz)) if pid else "UNMEASURED: no colonist"
        a["proof"] = static("RimMandrake.FlowWorks.RM_GeyserPoolProof", "Read", gid) if gid else "no geyser at %d,%d" % r["geyser"]
    res["answers"] = answers
    res["bad"] = judge_reach(answers) if pid else []
    json.dump(res, open(out, "w"), indent=1, default=str)
    for name, a in answers.items():
        print(name, a["ladder"][:70], "|", a["reach"][:90])
    if not pid:
        print("UNMEASURED: no colonist to read reachability for")
        return 2
    print("PASS: every pit has a lowered ladder and a colonist route in" if not res["bad"] else "FAIL %s" % res["bad"])
    return 1 if res["bad"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
