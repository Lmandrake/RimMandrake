#!/usr/bin/env python3
"""The build-menu half of PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES (owner by card 2026-10-21, "Their own switch."): a FlowWorks pipe
pole is in the architect menu by its own switch and a power mast by the power-lines master, each whatever the other says.

Reads whether each designator is drawn (jawa/architect_designator_visible) under three settings: both on; power master off, pipe poles on
(the pole stays, the mast goes); power master on, pipe poles off (the pole goes, the mast stays). Both are put back on at the end.

    python.exe src\\RimMandrake\\GimmeSomeSlack\\northstar\\live_pipe_pole_menu.py [--out result.json]

Game up with a map on tier gimmesomeslack_flowworks, bridge held. Exit 0 = PASS; UNMEASURED (exit 2) when no pipe pole or mast
is in any menu (FlowWorks not loaded).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Utils"))
AS = "RimMandrake.GimmeSomeSlack.Aerial.AerialSettings"
MS = "RimMandrake.FlowWorks.Machinery.RM_MachinerySettings"
PP = "RimMandrake.FlowWorks.Machinery.RM_PipePoles"


def verdict(cfg):
    """(status, why) from {"base"|"masterOff"|"polesOff": {buildable defName: visible}}."""
    def poles(v):
        return [k for k in v if k.startswith("RM_PipePole")]
    b, a2, a3 = cfg.get("base") or {}, cfg.get("masterOff") or {}, cfg.get("polesOff") or {}
    if not poles(b) or "RM_AerialMast" not in b or not all(isinstance(x, bool) for v in (b, a2, a3) for x in v.values()) or set(b) != set(a2) or set(b) != set(a3):
        return "UNMEASURED", "no pipe pole or no mast in the menus, or a reading is missing"
    if not all(b.values()):
        return "UNMEASURED", "with both switches on something is already hidden: the site is not the one this reads"
    bad = []
    if not all(a2[k] for k in poles(a2)):
        bad.append("power master off hid a pipe pole")
    if a2["RM_AerialMast"]:
        bad.append("power master off left the mast in the menu")
    if any(a3[k] for k in poles(a3)):
        bad.append("pipe poles off left a pipe pole in the menu")
    if not a3["RM_AerialMast"]:
        bad.append("pipe poles off hid the mast")
    return ("FAIL", "; ".join(bad)) if bad else ("PASS", "each menu entry follows its own switch")


def run(B):
    def vis():
        # jawa/architect_designator_visible reads what the menu DRAWS (Designator.Visible, which asks the PlaceWorker); the stock
        # list tool's "visible" is list membership only and reads true whatever the switches say (measured again 2026-11-17)
        out = {}
        for name in ("RM_PipePole", "RM_AerialMast", "RM_AerialLampMast"):
            L = B.call("jawa/architect_designator_visible", defName=name) or {}
            for d in L.get("rows") or []:
                b = str(d.get("buildDef") or "")
                if b.startswith("RM_PipePole") or b in ("RM_AerialMast", "RM_AerialLampMast"):
                    out[b] = d.get("drawn")
        return out

    def cfg(master, poles):
        B.call("jawa/mod_settings_field", typeName=AS, action="set", field="enabled", value=master)
        B.call("jawa/mod_settings_field", typeName=MS, action="set", field="pipePolesEnabled", value=poles)
        B.call("jawa/static_call", type=AS, method="Apply", args="")
        B.call("jawa/static_call", type=PP, method="RedrawSpans", args="")
        time.sleep(0.5)
        return vis()
    seen = {}
    # in god mode the game draws every build designator whatever its PlaceWorker says: the read is taken with god mode off
    god = {r["name"]: r["value"] for r in (B.call("jawa/debug_settings", action="list") or {}).get("fields") or []}.get("godMode")
    if god:
        B.call("jawa/debug_settings", action="set", field="godMode", value=False)
    try:
        seen["base"] = cfg("true", "true")
        seen["masterOff"] = cfg("false", "true")
        seen["polesOff"] = cfg("true", "false")
    finally:
        seen["restored"] = cfg("true", "true")
        if god:
            B.call("jawa/debug_settings", action="set", field="godMode", value=True)
    st, why = verdict(seen)
    return {"row": "live_pipe_pole_menu", "result": st, "why": why, "godModeWas": god, "seen": seen}


def main(argv):
    import validation_core as vc
    r = run(vc.Bridge())
    if "--out" in argv:
        with open(argv[argv.index("--out") + 1], "w", encoding="utf-8") as f:
            json.dump(r, f, indent=1)
    print(json.dumps(r)[:900])
    print("live_pipe_pole_menu " + r["result"])
    return {"PASS": 0, "UNMEASURED": 2}.get(r["result"], 1)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
