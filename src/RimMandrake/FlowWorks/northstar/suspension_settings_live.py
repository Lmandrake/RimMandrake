"""SUSPENSION SETTINGS-OFF live check (SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS A7; suspension_bridge_proof's owed row
SB_settings_off_no_button_never_breaks; BENCH belt 2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/suspension_settings_live.py [out.json] [--origin X,Z] [--fresh-map]

Rows:
  SB_settings_off_no_button   PROVE RM_SuspensionProofs.ProofButtons (every designator placing an RM_Suspension* def, in
                              every category, read as the gizmo grid reads it: root.Visible && Designator.Visible), with
                              RM_SuspensionSettings.suspensionBridgesBuildable on, then off. EXPECT on: at least one shown (the
                              can-fail; up to 11: 6 bridges, 2 jetties, 2 drawbridges, the tower, less any held back by
                              research or the drawbridge switch); off: 0 shown. Restored after.
                              LIES (measured 2026-10-22, SUSPENSION_BUTTONS_DIAGNOSE_STILL_SHOWING): rimworld/list_architect_designators'
                              'visible' is membership of ResolvedAllowedDesignators (game rules), never Designator.Visible, so it
                              listed all 11 with the setting off. It is recorded as 'bridgeListOff', never graded. The one true
                              MOD half of that run: the tower was vanilla's generated button and ignored the setting (fixed).
  SB_settings_off_never_breaks PROVE suspensionWeightCollapse off; a timber span dragged over a 4 m trench (the proof's T1
                              scene: trench (1..6, 0), drag (0,0)-(7,0), god); drafted colonists spawned on the deck until
                              ProofSpan reads Over; 120 ticks (two load passes). EXPECT every deck still stands (graded: the
                              deck count before and after). The riders' cells are recorded, NOT graded: a pawn who fell
                              keeps his x,z. LIES: a span never Over (refused: the precondition is read back); restored after.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
SS = "RimMandrake.FlowWorks.Pits.RM_SuspensionSettings"
SPROOF = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
ITEM = "SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS"


def kv(txt):
    out = {}
    for tok in (txt or "").replace("|", " ").split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="100,30")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "suspension_settings_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "suspension_settings_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-30s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:400]), flush=True)
        save()

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=SS, action="set", field=f, value=str(v)) or {}

    def sget(f):
        return (B.call("jawa/mod_settings_field", typeName=SS, action="get", field=f) or {}).get("value")

    def proof(m, arg):
        r = B.call("jawa/static_call", type=SPROOF, method=m, args=arg, _answer=True) or {}
        t = str(r.get("result") or r.get("message") or "")
        return kv(t), t

    def shown_suspension():
        t = proof("ProofButtons", "")[1]
        if not t.startswith("BUTTONS"):
            return None, t
        k = kv(t)
        return [d for d in (k.get("shownDefs") or "").split(",") if d], t

    def visible_suspension():
        """Bridge-tool membership list: NOT visibility (see LIES above). Recorded, never graded."""
        cats = (B.call("rimworld/list_architect_categories") or {}).get("categories") or []
        hits = []
        for c in cats:
            off = 0
            while True:
                r = B.call("rimworld/list_architect_designators", categoryId=c.get("id"), includeHidden=False, offset=off) or {}
                for d in r.get("designators") or []:
                    if "suspension" in json.dumps(d).lower():
                        hits.append((c.get("id"), d.get("label") or d.get("id")))
                nxt = (r.get("page") or {}).get("nextOffset")
                if not nxt:
                    break
                off = nxt
        return hits

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)  # noqa: E731
    xz = lambda c: "%d,%d" % c  # noqa: E731
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("SB_settings_off_no_button", "UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    b0, w0 = sget("suspensionBridgesBuildable"), sget("suspensionWeightCollapse")
    res["settingsBefore"] = {"buildable": b0, "weight": w0}
    try:
        # --- buttons
        on, on_t = shown_suspension()
        sset("suspensionBridgesBuildable", False)
        off, off_t = shown_suspension()
        list_off = visible_suspension()
        sset("suspensionBridgesBuildable", True if b0 is None else b0)
        if on is None or off is None:
            row("SB_settings_off_no_button", "UNMEASURED", "HARNESS", {"why": "ProofButtons did not answer (old DLL?)", "on": on_t, "off": off_t})
        elif not on:
            row("SB_settings_off_no_button", "UNMEASURED", "HARNESS", {"why": "no suspension button shown even with the setting on", "on": on_t})
        else:
            row("SB_settings_off_no_button", "PASS" if not off else "FAIL", "MOD", {"shownOn": on, "shownOff": off, "readOff": off_t, "bridgeListOff": list_off})
        # --- weight
        res["site_calm"] = V.site_calm(B)
        B.call("jawa/kill_hostiles")
        rect = (ox - 2, oz - 3, 12, 7)
        B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
        site_rows = []
        V.prepare_site(B, rect, site_rows, "sbw_site")
        if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
            row("SB_settings_off_never_breaks", "UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
            return 2
        for i in range(1, 7):
            B.call("jawa/flowworks_excavation_drive", x=P(i, 0)[0], z=P(i, 0)[1], deepenLevels=8, setFill=-1)
        sset("suspensionWeightCollapse", False)
        kb, tb = proof("ProofBuild", "%s;%s;timber;god" % (xz(P(0, 0)), xz(P(7, 0))))
        if kb.get("ok") != "True":
            row("SB_settings_off_never_breaks", "UNMEASURED", "SITE", {"why": "the span did not build", "build": tb})
            return 2
        riders, k1, t1 = [], {}, ""
        for k in range(16):      # first run: 8 colonists read 474 / 600 kg, never Over
            r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=P(1 + k % 6, 0)[0], z=oz, faction="player", count=1) or {}
            pid = ((r.get("pawns") or [{}])[0]).get("id")
            if pid:
                B.call("jawa/set_draft", pawnId=pid, drafted=True)
                riders.append(pid)
            k1, t1 = proof("ProofSpan", xz(P(3, 0)))
            if k1.get("state") == "Over":
                break
        if k1.get("state") != "Over":
            row("SB_settings_off_never_breaks", "UNMEASURED", "SITE", {"why": "the span never read Over", "span": t1})
            return 2
        B.call("rimworld/step_game_ticks", ticks=120, pauseFirst=True, timeoutMs=60000)
        k2, t2 = proof("ProofSpan", xz(P(3, 0)))
        ps = {p.get("id"): p for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []}
        on_deck = [pid for pid in riders if (ps.get(pid) or {}).get("z") == oz and ox + 1 <= ((ps.get(pid) or {}).get("x") or -1) <= ox + 6]
        stands = k2.get("decks") == k1.get("decks") and k2.get("decks") not in (None, "0")
        row("SB_settings_off_never_breaks", "PASS" if stands else "FAIL", "MOD",
            {"overRead": t1, "after120": t2, "riders": riders, "ridersStillOnTheDeckRow": len(on_deck)})
        for pid in riders:
            B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
    finally:
        sset("suspensionBridgesBuildable", True if b0 is None else b0)
        sset("suspensionWeightCollapse", True if w0 is None else w0)
        res["settingsAfter"] = {"buildable": sget("suspensionBridgesBuildable"), "weight": sget("suspensionWeightCollapse")}
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
