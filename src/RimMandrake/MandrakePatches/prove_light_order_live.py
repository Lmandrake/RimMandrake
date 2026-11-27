"""prove_light_order_live.py -- live proof of RIMMANDRAKE_ADD_LIGHT_ANYTHING_FLAMMABLE_ORDER_TO_ALL_COLONISTS.

    python.exe src/RimMandrake/MandrakePatches/prove_light_order_live.py < /dev/null
    python3 src/RimMandrake/MandrakePatches/prove_light_order_live.py --selftest    # offline: the judge goes red on mutants

Needs a started colony map whose load holds RimMandrake Patches AFTER its DLL was deployed and the game restarted, and a standing
colonist with hands. Through jawa/static_call to RimMandrake.Patches.LightOrderProof it stages each row next to that colonist,
builds the game's own right-click menu for the square (FloatMenuMakerMap.GetOptions: every provider, FlowWorks' too), clicks
our line when there is one (its own action, as a click does) and reads whether a Fire this colonist started stands on the target.
Rows:
  wall    a wood wall    -> "Set fire to ..." offered, the job is RM_LightFire, a fire by this colonist within LIT_TICKS
  hay     a hay stack    -> the same
  puddle  Filth_Fuel     -> the same
  steel   a steel wall   -> no line of ours at all (the wall row's line is the control that the instrument sees our lines)
  flow    hay on a FlowWorks chemfuel spill -> FlowWorks' "Toss a flame here" shows and ours does not (no duplicate);
          UNMEASURED when FlowWorks is not loaded
Exit 0 every row holds, 1 a row fails, 2 UNMEASURED (no bridge, no colonist, a row the game could not stage).
WRITES (spawns, fires); callers hold the bridge lock and save before / reload after (harness housekeeping). Never on ArchBig.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PASS, FAIL, UNMEASURED = 0, 1, 2
PROBE = "RimMandrake.Patches.LightOrderProof"
SHEET = "RimMandrake.FlowWorks.Sheet.RM_SheetProofs"
LIT_ROWS = ("wall", "hay", "puddle")
# Walk of at most 6 squares (FreeCellNear's radius; ~0.6 s/square at a colonist's base speed = ~220 ticks) + the 60-tick work
# (LightOrder.WorkTicks) + slack for a door or a detour: 900 ticks is 4x the expected time; POLL reads it every second.
LIT_TICKS = 900
POLL = 60
# FlowWorks' own c13_spill_yard stages a 3000 dl spill (northstar/scenarios/c13_spill_yard.py): a sheet it reads as wet.
SPILL_DL = 3000


def field(text, name):
    """'ours=[a|b]' -> ['a','b']; 'lit=True' -> 'True'; None when absent."""
    if not isinstance(text, str):
        return None
    m = re.search(r"\b" + name + r"=\[([^\]]*)\]", text)
    if m:
        return [x for x in m.group(1).split("|") if x]
    m = re.search(r"\b" + name + r"=(\S+)", text)
    return m.group(1) if m else None


def judge_row(name, stage, read):
    """Pure. One row -> (code, line)."""
    if not isinstance(stage, str) or not (stage.startswith("STAGED") or stage.startswith("MENU")):
        return UNMEASURED, "UNMEASURED %s: the row did not stage: %s" % (name, str(stage)[:160])
    ours = field(stage, "ours") or []
    flow = field(stage, "flow") or []
    if name in LIT_ROWS:
        offered = [o for o in ours if o.startswith("Set fire to ") and "(disabled)" not in o]
        if not offered:
            return FAIL, "FAIL %s: no offered line of ours (ours=%r)" % (name, ours)
        if field(stage, "job") != "RM_LightFire":
            return FAIL, "FAIL %s: the click gave job %r, not RM_LightFire" % (name, field(stage, "job"))
        if flow:
            return FAIL, "FAIL %s: FlowWorks' toss line also showed on dry ground: %r" % (name, flow)
        if field(read, "lit") != "True":
            return FAIL, "FAIL %s: no fire by this colonist on the target within %d ticks (%s)" % (name, LIT_TICKS, str(read)[:160])
        return PASS, "ok %s: '%s' -> RM_LightFire -> lit (%s)" % (name, offered[0], read.strip())
    if name == "steel":
        if ours:
            return FAIL, "FAIL steel: a line of ours on a steel wall: %r" % (ours,)
        if field(stage, "flammableNow") != "False":
            return UNMEASURED, "UNMEASURED steel: the wall reads flammableNow=%s (MetalNonFlammable not in this load?)" % field(stage, "flammableNow")
        return PASS, "ok steel: no line of ours (flammableNow=False, %s options)" % field(stage, "options")
    if name == "flow":
        if not flow:
            return UNMEASURED, "UNMEASURED flow: FlowWorks' toss line did not show on the spill (%s)" % stage[:160]
        if ours:
            return FAIL, "FAIL flow: both lines on one square: ours=%r flow=%r" % (ours, flow)
        return PASS, "ok flow: FlowWorks' '%s' only, ours stood aside" % flow[0]
    return UNMEASURED, "UNMEASURED unknown row " + name


def judge(rows):
    """Pure. rows: {name: (stage, read)} -> (code, lines). The steel row only counts when the wall row saw our line (the control)."""
    if not rows:
        return UNMEASURED, ["UNMEASURED no rows ran"]
    lines, codes = [], []
    for name in ("wall", "hay", "puddle", "steel", "flow"):
        if name not in rows:
            codes.append(UNMEASURED)
            lines.append("UNMEASURED %s: not run" % name)
            continue
        c, line = judge_row(name, *rows[name])
        wall_holds = "wall" in rows and judge_row("wall", *rows["wall"])[0] == PASS
        if name == "steel" and c == PASS and not wall_holds:
            c, line = UNMEASURED, "UNMEASURED steel: the wall control did not hold, so 'no line' proves nothing"
        codes.append(c)
        lines.append(line)
    code = FAIL if FAIL in codes else UNMEASURED if UNMEASURED in codes else PASS
    lines.append("rows read=%d worst=%s limit=all PASS" % (len(codes), {PASS: "PASS", FAIL: "FAIL", UNMEASURED: "UNMEASURED"}[max(codes)]))
    lines.append("VERDICT " + {PASS: "PASS", FAIL: "FAIL", UNMEASURED: "UNMEASURED"}[code])
    return code, lines


def selftest():
    def st(row, ours, job="RM_LightFire", flow="", fl="True"):
        return "STAGED row=%s cell=1,1 target=X flammableNow=%s ours=[%s] flow=[%s] options=5 job=%s" % (row, fl, ours, flow, job)
    lit = "READ lit=True fires=1 targetSpawned=True job=none"
    good = {
        "wall": (st("wall", "Set fire to wood wall"), lit),
        "hay": (st("hay", "Set fire to hay"), lit),
        "puddle": (st("puddle", "Set fire to chemfuel puddle"), lit),
        "steel": ("MENU row=steel cell=1,1 target=Wall/Steel flammableNow=False ours=[] flow=[] options=4", ""),
        "flow": ("MENU row=hay cell=1,1 target=Hay flammableNow=True ours=[] flow=[Toss a flame here] options=6", ""),
    }

    def mut(**kw):
        d = dict(good)
        d.update(kw)
        return judge(d)[0]
    steps = [
        ("good run holds", judge(good)[0] == PASS),
        ("wall not lit fails", mut(wall=(good["wall"][0], "READ lit=False fires=0 targetSpawned=True job=none")) == FAIL),
        ("hay line greyed fails", mut(hay=(st("hay", "Cannot set fire to hay: no path (disabled)"), lit)) == FAIL),
        ("puddle wrong job fails", mut(puddle=(st("puddle", "Set fire to chemfuel puddle", job="Goto"), lit)) == FAIL),
        ("steel with a line fails", mut(steel=("MENU row=steel flammableNow=False ours=[Cannot set fire to steel wall: x (disabled)] flow=[] options=4", "")) == FAIL),
        ("duplicate on the spill fails", mut(flow=("MENU row=hay flammableNow=True ours=[Set fire to hay] flow=[Toss a flame here] options=6", "")) == FAIL),
        ("toss line on dry hay fails", mut(hay=(st("hay", "Set fire to hay", flow="Toss a flame here"), lit)) == FAIL),
        ("steel without the wall control is unmeasured", mut(wall=("UNMEASURED: no usable square", "")) == UNMEASURED
         and judge_row("steel", *good["steel"])[0] == PASS),
        ("no FlowWorks line is unmeasured", mut(flow=("MENU row=hay flammableNow=True ours=[] flow=[] options=6", "")) == UNMEASURED),
        ("a burning steel wall is unmeasured", mut(steel=("MENU row=steel flammableNow=True ours=[] flow=[] options=4", "")) == UNMEASURED),
        ("nothing is unmeasured", judge({})[0] == UNMEASURED),
    ]
    for n, ok in steps:
        print(("ok   " if ok else "FAIL ") + n)
    bad = [n for n, ok in steps if not ok]
    print("selftest: %d cases read, %d wrong (limit 0)" % (len(steps), len(bad)))
    return 1 if bad else 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
    rows = {}
    try:
        import validation_core as VC
        B = VC.Bridge()

        def call(typ, method, arg=""):
            r = B.call("jawa/static_call", type=typ, method=method, args=arg)
            return str(r.get("result", r)).strip().strip('"') if isinstance(r, dict) else str(r)

        for name in LIT_ROWS:
            stage = call(PROBE, "Stage", name)
            read = ""
            if stage.startswith("STAGED"):
                for _ in range(LIT_TICKS // POLL):
                    B.ticks(POLL)
                    read = call(PROBE, "Read")
                    if field(read, "lit") == "True":
                        break
            rows[name] = (stage, read)
            print("%s: %s | %s | %s" % (name, stage, read, call(PROBE, "Clean")))
        stage = call(PROBE, "Stage", "steel")
        rows["steel"] = (stage, "")
        print("steel: %s | %s" % (stage, call(PROBE, "Clean")))
        pick = call(PROBE, "Pick")
        if pick.startswith("CELL "):
            xz = pick.split()[1]
            spill = call(SHEET, "ProofSheetSpill", "%s;%d;Flood;RM_Fluid_Chemfuel" % (xz, SPILL_DL))
            stage = call(PROBE, "Stage", "hay@" + xz) if spill.startswith("SPILL") else "UNMEASURED: FlowWorks spill: " + spill
        else:
            stage = pick
        rows["flow"] = (stage, "")
        print("flow: %s | %s" % (stage, call(PROBE, "Clean", "end")))
    except Exception as ex:   # no bridge, the governor stopped the clock, the game dropped: whatever ran is judged
        print("stopped early: %s: %s" % (type(ex).__name__, str(ex)[:200]))
    code, lines = judge(rows)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
