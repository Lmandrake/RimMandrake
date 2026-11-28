#!/usr/bin/env python3
"""Live scene (kind A): a colonist stranded ON HIS FEET in a sealed 4 m pit gets a rescue ladder queued.

RIMMANDRAKE_RESCUE_FLOWWORKS_STRANDED_COLONIST_REACHABLE_LADDER, half one (RIMMANDRAKE_FIX_STRANDED_COLONIST_READS_UNTRAPPED_NO_RESCUE):
live 2026-11-12 (run 18) a colonist in a sealed 4 m pit read trapped=False, could not leave, and no rescue was queued, because
RM_MapComponent_PitRescueLadder.TryQueueFor asked the captures-only IsTrapped. 5d9004b9ce made it ask HasNoWayOut.

Contract.
- claim: a free colonist standing in a 3x3 pit 4 m deep (8 notches), no ladder, no ramp, gets a ladder blueprint (portable or
  fixed) placed at the pit wall by FlowWorks' rescue component, within 1000 ticks (the component checks every 250).
- entry point: RM_MapComponent_PitRescueLadder.MapComponentTick (the mod's own tick; the scene calls nothing in it).
- valid opportunity: the colonist reads, by ProofClimb, in a pocket with no way out (the pit is sealed), not downed, and no
  ladder or blueprint stands on the map before the wait.
- success: a Blueprint of RM_LadderPortable or RM_Ladder exists on the map after the wait, in or beside the pit.
- control (run first): the same pit with pitRescueLadderEnabled off: no blueprint in the same wait (rules out a blueprint from any
  other source). The setting is restored to its shipped default (on) in finally.
- forbidden effects: the colonist hurt or dead; a blueprint before the wait.
- end: rows written to the out file; the setting restored.

Usage (Windows python, a game in Playing or --fresh-map):
  python.exe src/RimMandrake/FlowWorks/northstar/live_pit_rescue_stranded.py <out.json> [--fresh-map] [--origin X,Z]
Exit 0 PASS, 1 FAIL, 2 UNMEASURED (could not look; the reason is in the row).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))

ST = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
DEEP = 8          # notches: 4 m
WAIT = 1000       # ticks: four checks of the rescue component (CheckTicks 250)
LADDER_BLUEPRINTS = ("Blueprint_RM_LadderPortable", "Blueprint_RM_Ladder", "Blueprint_Install")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--origin", default="120,120")
    a = ap.parse_args(argv)
    import proof_hose as PH    # noqa: E402  (bridge-side import on a live run only)
    B = PH.PB()
    rows = []
    res = {"script": "live_pit_rescue_stranded.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}

    def save():
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    def row(rid, st, det):
        rows.append({"id": rid, "status": st, "detail": det})
        print("%-40s %-10s %s" % (rid, st, json.dumps(det, default=str)[:400]), flush=True)
        save()

    def call(tool, **kw):
        return B.call(tool, **kw) or {}

    def setting(field, value=None):
        if value is None:
            return call("jawa/mod_settings_field", typeName=ST, action="get", field=field).get("value")
        return call("jawa/mod_settings_field", typeName=ST, action="set", field=field, value=str(value)).get("success")

    def blueprints():
        out = []
        for d in LADDER_BLUEPRINTS:
            for t in call("jawa/list_things", defName=d, limit=50).get("things") or []:
                out.append({"def": d, "x": t.get("x"), "z": t.get("z"), "label": t.get("label")})
        return out

    def climb(pid):
        r = call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofClimb",
                 args="pawn:" + str(pid).lstrip("Human"))
        return str(r.get("result") or r.get("message") or r.get("error") or "")

    if a.fresh_map:
        call("rimworld/go_to_main_menu")
        call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    import validation_core as V    # noqa: E402
    if not V._wait_playing(B, leave_s=0)[0]:
        row("RESCUE_site", "UNMEASURED", {"why": "no game reached Playing"})
        return 2
    call("jawa/kill_hostiles")
    ox, oz = (int(v) for v in a.origin.split(","))
    pit = [(ox + dx, oz + dz) for dx in range(3) for dz in range(3)]
    mid = (ox + 1, oz + 1)
    prior = setting("pitRescueLadderEnabled")
    try:
        call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect",
             args="%d;%d;%d;%d" % (ox - 4, oz - 4, 11, 11))
        depths = [call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=DEEP, setBodyWaterM=-1).get("depth")
                  for c in pit]
        if any(d != DEEP for d in depths):
            row("RESCUE_site", "UNMEASURED", {"why": "the pit did not dig to 4 m", "depths": depths})
            return 2
        sp = call("jawa/spawn_pawn", kindDef="Colonist", x=mid[0], z=mid[1], faction="player", count=1)
        pid = ((sp.get("pawns") or [{}])[0]).get("id")
        if not pid:
            row("RESCUE_site", "UNMEASURED", {"why": "no colonist spawned in the pit", "reply": str(sp)[:200]})
            return 2
        call("rimworld/step_game_ticks", ticks=60, pauseFirst=True, timeoutMs=60000)
        c0 = climb(pid)
        bp0 = blueprints()
        row("RESCUE_site", "PASS" if ("cell=%d,%d" % mid) in c0 and not bp0 else "UNMEASURED",
            {"climb": c0[:300], "blueprintsBefore": bp0})
        if bp0 or ("cell=%d,%d" % mid) not in c0:
            return 2
        # control first: the rescue switched off, the same wait, no ladder
        setting("pitRescueLadderEnabled", False)
        call("rimworld/step_game_ticks", ticks=WAIT, pauseFirst=True, timeoutMs=120000)
        bpc = blueprints()
        row("RESCUE_control_setting_off", "PASS" if not bpc else "FAIL",
            {"blueprints": bpc, "why": "rescue off: nothing queues a ladder" if not bpc else "a ladder came from elsewhere"})
        setting("pitRescueLadderEnabled", True)
        call("rimworld/step_game_ticks", ticks=WAIT, pauseFirst=True, timeoutMs=120000)
        bp1 = blueprints()
        c1 = climb(pid)
        near = [b for b in bp1 if b["x"] is not None and abs(b["x"] - mid[0]) <= 3 and abs(b["z"] - mid[1]) <= 3]
        ok = bool(near) and not bpc
        row("RESCUE_stranded_colonist_gets_a_ladder", "PASS" if ok else "FAIL",
            {"blueprints": bp1, "near": near, "climbAfter": c1[:300],
             "why": "a ladder blueprint at the pit wall within %d ticks" % WAIT if ok else "no ladder queued for a colonist with no way out"})
        return 0 if ok else 1
    finally:
        if prior is not None:
            setting("pitRescueLadderEnabled", prior)
        save()


if __name__ == "__main__":
    sys.exit(main())
