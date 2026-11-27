"""UNSET BRIDGE LOOK live check (RIMMANDRAKE_FIX_STEEL_BRIDGE_UNSET_STYLE_TAKES_LAST_CHOSEN). Kind A: one valid run decides.

  python.exe src/RimMandrake/FlowWorks/northstar/unset_bridge_look_live.py [out.json] [--origin X,Z] [--fresh-map]

Seen 2026-11-25 on the walk map: stations 52, 53, 70, 78 and 84 (steel bridges built with no look chosen) all came out
Futuristic, the last look picked on any steel bridge button, even one picked before the save was loaded. The cause was
_Shared/StylePicker: one remembered pick per ThingDef for the whole process. The fix keys a pick to the button that made it
and to the game it was made in (StylePickMemory.cs; offline: SelfTest StylePick_*).

Scene (from --origin, default 40,180; 12 x 7 cleared): two pits 3 x 2, 8 notches (4 m), at x 0..2 and 6..8, z 2..3. Each
gets a 1-wide steel bridge laid north-south across it at x 1 and x 7, z 1..4, built in god mode by
RM_SuspensionProofs.ProofUnsetLook. That proof picks a look that is not the default on the first bridge's button, builds
the first bridge, then builds the second bridge from a new button with nothing chosen. It reads the look stored on each
part of the second bridge (nothing stored = the default look).
EXPECT  UNSETLOOK ok=True: every part of the second bridge is in the default look.
FAILS   ok=False with parts>0 and reason=-: a part of the second bridge took the first bridge's pick (the reported fault).
LIES    no part built, or a refusal: UNMEASURED (SITE). The pick before a load is decided offline only
        (StylePick_pick_before_load_does_not_reach_the_loaded_game): a load makes a new Game object (SavedGameLoaderNow,
        read in the game source 2026-11-26), and a live load costs a cold map load for one bit the offline case decides.
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
SPROOF = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
ITEM = "RIMMANDRAKE_FIX_STEEL_BRIDGE_UNSET_STYLE_TAKES_LAST_CHOSEN"
ROW = "UNSET_bridge_takes_default_look"
NOTCHES = 8


def verdict(text):
    """ProofUnsetLook's line -> (status, class, fields). PASS only on ok=True with parts>0 and no refusal."""
    t = str(text or "")
    if not t.startswith("UNSETLOOK "):
        return "UNMEASURED", "HARNESS", {"read": t[:300]}
    f = dict(re.findall(r"(\w+)=(\S*)", t))
    parts = int(f.get("parts") or 0)
    if f.get("reason", "-") != "-" or parts == 0:
        return "UNMEASURED", "SITE", f
    return ("PASS", "MOD", f) if f.get("ok") == "True" else ("FAIL", "MOD", f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,180")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "unset_bridge_look_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    res = {"script": "unset_bridge_look_live.py", "item": ITEM, "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "args": vars(a)}

    def row(st, cls, det):
        res["row"] = {"id": ROW, "status": st, "class": cls, "item": ITEM, "detail": det}
        print("%-34s %-10s %-6s %s" % (ROW, st, cls, json.dumps(det, default=str)[:600]), flush=True)
        with open(out + ".tmp", "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, default=str)
        os.replace(out + ".tmp", out)
        return 0 if st == "PASS" else 1 if st == "FAIL" else 2

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)  # noqa: E731
    xz = lambda c: "%d,%d" % c  # noqa: E731
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        return row("UNMEASURED", "HARNESS", {"why": "no game in Playing"})
    rect = (ox - 1, oz, 12, 7)
    B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    site_rows = []
    V.prepare_site(B, rect, site_rows, "unset_look_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        return row("UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
    for x0 in (0, 6):
        for dx in range(3):
            for z in (2, 3):
                c = P(x0 + dx, z)
                B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=NOTCHES, setBodyWaterM=-1)
    r = B.call("jawa/static_call", type=SPROOF, method="ProofUnsetLook",
               args="%s;%s;%s;%s" % (xz(P(1, 1)), xz(P(1, 4)), xz(P(7, 1)), xz(P(7, 4))), _answer=True) or {}
    st, cls, det = verdict(r.get("result"))
    return row(st, cls, det)


if __name__ == "__main__":
    sys.exit(main())
