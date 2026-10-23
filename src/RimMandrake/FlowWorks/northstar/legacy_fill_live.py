"""LEGACY FILL live check (EXCAVATION_LEGACY_MIGRATION_FLAG_1 A2: "filling in a channel with no recorded original terrain
hands back the surrounding ground, not channel terrain").

  python.exe src/RimMandrake/FlowWorks/northstar/legacy_fill_live.py [out.json] [--origin X,Z] [--fresh-map]

PROVE  on a cleared 11x11 Soil plot, RM_LegacyFillProof.ProofLegacyFill("x,z") digs one square a notch through the engine,
       forgets its original-terrain record (what a save older than the record leaves), fills it back to the surface through
       the engine's own FillIn and reads the ground. Run twice on two squares: legacyFillFallbackEnabled ON (shipped), then
       OFF (the can-fail control); the setting is restored after.
EXPECT LF_fallback_hands_back_ground: forgot=True, dug=RM_Channel_*, after=Soil, afterIsChannel=False, depth=0.
       LF_fallback_off_leaves_trench: forgot=True, afterIsChannel=True, depth=0 (the old behaviour: proves the row can fail).
LIES   a REFUSED answer (DLL without the surface, cell already dug, undiggable) is UNMEASURED(HARNESS/SITE), never PASS;
       forgot=False means the staging did not happen, so the read proves nothing -> UNMEASURED(HARNESS).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
LPROOF = "RimMandrake.FlowWorks.RM_LegacyFillProof"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
ITEM = "EXCAVATION_LEGACY_MIGRATION_FLAG_1"


def parse(rep):
    """'LEGACYFILL k=v k=v ...' -> {k: v} (None for a REFUSED or unreadable answer)."""
    rep = str(rep or "")
    if not rep.startswith("LEGACYFILL "):
        return None
    return dict(kv.split("=", 1) for kv in rep.split()[1:] if "=" in kv)


def judge(q, fallback_on):
    """(status, class, why) for one parsed answer."""
    if q is None:
        return "UNMEASURED", "HARNESS", "no LEGACYFILL answer"
    if q.get("forgot") != "True":
        return "UNMEASURED", "HARNESS", "the record was not forgotten: staging failed"
    if not str(q.get("dug") or "").startswith("RM_Channel_"):
        return "UNMEASURED", "SITE", "the cut did not lay channel terrain"
    if q.get("depth") != "0":
        return "FAIL", "MOD", "fill-in did not reach the surface"
    if fallback_on:
        ok = q.get("afterIsChannel") == "False" and q.get("after") == "Soil"
    else:
        ok = q.get("afterIsChannel") == "True"
    return ("PASS" if ok else "FAIL"), "MOD", ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,40")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "legacy_fill_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "legacy_fill_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-34s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:600]), flush=True)
        save()

    def sget(f):
        return (B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f) or {}).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v)) or {"success": False}

    ox, oz = (int(v) for v in a.origin.split(","))
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("LF_fallback_hands_back_ground", "UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    before = sget("legacyFillFallbackEnabled")
    if before is None:
        row("LF_fallback_hands_back_ground", "UNMEASURED", "HARNESS", {"why": "legacyFillFallbackEnabled unreadable"})
        return 2
    rect = (ox, oz, 11, 11)
    B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    site_rows = []
    V.prepare_site(B, rect, site_rows, "legacy_fill_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        row("LF_fallback_hands_back_ground", "UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
        return 2
    rc = 0
    try:
        for rid, on, cell in (("LF_fallback_hands_back_ground", True, (ox + 3, oz + 5)),
                              ("LF_fallback_off_leaves_trench", False, (ox + 7, oz + 5))):
            sset("legacyFillFallbackEnabled", on)
            rep = (B.call("jawa/static_call", type=LPROOF, method="ProofLegacyFill", args="%d,%d" % cell, _answer=True) or {}).get("result")
            q = parse(rep)
            st, cls, why = judge(q, on)
            row(rid, st, cls, {"report": rep, "setting": on, "cell": cell, "why": why})
            rc = max(rc, {"PASS": 0, "FAIL": 1}.get(st, 2))
    finally:
        sset("legacyFillFallbackEnabled", before)
        # leave the plot pristine: the OFF square is a trench at D=0 by design; repaint it Soil
        B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,1,1" % (ox + 7, oz + 5))
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
    return rc


if __name__ == "__main__":
    sys.exit(main())
