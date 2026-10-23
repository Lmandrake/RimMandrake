"""LEGACY FILL live check (EXCAVATION_LEGACY_MIGRATION_FLAG_1 A2: "filling in a channel with no recorded original terrain
hands back the surrounding ground, not channel terrain").

  python.exe src/RimMandrake/FlowWorks/northstar/legacy_fill_live.py [out.json] [--origin X,Z] [--fresh-map]

PROVE  on a cleared 11x11 Soil plot, RM_LegacyFillProof.ProofLegacyFill("x,z") digs one square a notch through the engine,
       forgets its original-terrain record (what a save older than the record leaves), fills it back to the surface through
       the engine's own FillIn and reads the ground. Run twice on two squares: legacyFillFallbackEnabled ON (shipped), then
       OFF (the can-fail control); the setting is restored after. Then (unless --skip-reload) the game is saved and
       loaded with the OFF square still channel terrain at D=0, the exact trigger of the old rehydration re-read.
EXPECT LF_fallback_hands_back_ground: forgot=True, dug=RM_Channel_*, after=Soil, afterIsChannel=False, depth=0.
       LF_fallback_off_leaves_trench: forgot=True, afterIsChannel=True, depth=0 (the old behaviour: proves the row can fail).
       LF_reload_trench_not_reread (A1): after the load that square is still D=0 and excavatedCellCount is unchanged.
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


def reload_row(B, V, row, trench):
    """LF_reload_trench_not_reread (A1): the OFF case left channel terrain at D=0 on `trench` -- exactly what the pre-flag
    rehydration re-read as an excavation on every load. Save, load, read again: the square is still D=0 and the map's
    excavated count is unchanged (RM_legacyRehydrationDone holds). Returns the exit-code contribution."""
    def depth():
        return (B.call("jawa/flowworks_excavation_drive", x=trench[0], z=trench[1], deepenLevels=0, setFill=-1) or {}).get("depth")

    def count():
        return (B.call("jawa/flowworks_engine_state") or {}).get("excavatedCellCount")
    terr = lambda: str((B.call("jawa/get_terrain_batch", rects="%d,%d,1,1" % trench) or {}).get("ops"))  # noqa: E731
    d0, n0, t0 = depth(), count(), terr()
    name = "RM_legacy_fill_reload_%s" % time.strftime("%Y%m%d_%H%M%S")
    sv = B.call("rimworld/save_game", saveName=name) or {}
    try:
        V._wait_saved(name)
    except Exception as ex:  # noqa: BLE001
        sv["wait_saved"] = str(ex)[:200]
    ld = B.call("rimworld/load_game_ready", saveName=name, timeoutMs=240000) or {}
    V._wait_playing(B, leave_s=0)
    d1, n1, t1 = depth(), count(), terr()
    det = {"save": name, "depth": [d0, d1], "excavatedCellCount": [n0, n1], "terrain": [t0[:120], t1[:120]],
           "saved": sv.get("success"), "loaded": ld.get("success")}
    if sv.get("success") is not True or ld.get("success") is not True or None in (d0, d1, n0, n1):
        row("LF_reload_trench_not_reread", "UNMEASURED", "HARNESS", dict(det, why="save/load failed or a read came back empty"))
        return 2
    if "RM_Channel_" not in t0:
        row("LF_reload_trench_not_reread", "UNMEASURED", "SITE", dict(det, why="no channel terrain at D=0 to tempt the rehydration"))
        return 2
    ok = d0 == 0 and d1 == 0 and n1 == n0
    row("LF_reload_trench_not_reread", "PASS" if ok else "FAIL", "MOD", det)
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,40")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--skip-reload", action="store_true", help="skip LF_reload_trench_not_reread (the save + load)")
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
        if not a.skip_reload:
            rc = max(rc, reload_row(B, V, row, (ox + 7, oz + 5)))
    finally:
        sset("legacyFillFallbackEnabled", before)
        # leave the plot pristine: the OFF square is a trench at D=0 by design; repaint it Soil
        B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,1,1" % (ox + 7, oz + 5))
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
    return rc


if __name__ == "__main__":
    sys.exit(main())
