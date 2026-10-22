"""JETTY DROP live check (SUSPENSION_JETTY_BUILD_WALK_THE_PLANK A3: "railings off: a pawn ordered to drop off the open edge
lands in the pit"; suspension_bridge_proof's owed row JET_open_edge_drop_on_order; BENCH belt 2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/jetty_drop_live.py [out.json] [--origin X,Z] [--fresh-map]

Scene (plot from --origin, default 90,200; 10 x 8 cleared + read back): a 4 m pit x = 1..4, z = 1..3 (8 notches); a
1-square steel jetty (0,2)-(1,2) built at once (RM_SuspensionProofs.ProofJetty god), railings OFF (ProofRails); a
drafted colonist standing on the jetty square (1, 2).
PROVE the player's own route: rimworld/select_pawn, rimworld/list_selected_gizmos, the "Jump into pit" gizmo
      (RM_Patch_Pawn_JumpIntoPitGizmo) executed, its confirmation accepted (rimworld/press_accept), 240 ticks.
EXPECT the colonist ends on a pit floor square and the trap recorded a descent (RM_NorthstarProofs.ProofTrap pawn read
      or the excavation pit report's recentDescents).
LIES  a gizmo that is absent (no open edge, railings still on) -> FAIL with the gizmo list; a confirmation never accepted
      leaves the pawn on the deck -> recorded.
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
SPROOF = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
ITEM = "SUSPENSION_JETTY_BUILD_WALK_THE_PLANK"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="90,200")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "jetty_drop_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "jetty_drop_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(st, cls, det):
        rows.append({"id": "JET_open_edge_drop_on_order", "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-28s %-10s %-6s %s" % ("JET_open_edge_drop_on_order", st, cls, json.dumps(det, default=str)[:700]), flush=True)
        save()

    def sp(m, arg):
        r = B.call("jawa/static_call", type=SPROOF, method=m, args=arg, _answer=True) or {}
        return str(r.get("result") or r.get("message") or "")

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)  # noqa: E731
    xz = lambda c: "%d,%d" % c  # noqa: E731
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    res["site_calm"] = V.site_calm(B)
    rect = (ox - 2, oz - 2, 10, 8)
    B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    site_rows = []
    V.prepare_site(B, rect, site_rows, "jetty_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        row("UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
        return 2
    pit = {P(x, z) for x in range(1, 5) for z in range(1, 4)}
    for c in sorted(pit):
        B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=8, setFill=-1)
    jt = sp("ProofJetty", "%s;%s;steel;god" % (xz(P(0, 2)), xz(P(1, 2))))
    rails = sp("ProofRails", "%s;off" % xz(P(1, 2)))
    r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=P(1, 2)[0], z=P(1, 2)[1], faction="player", count=1) or {}
    pid = ((r.get("pawns") or [{}])[0]).get("id")
    B.call("jawa/set_draft", pawnId=pid, drafted=True)
    B.call("rimworld/step_game_ticks", ticks=5, pauseFirst=True, timeoutMs=60000)
    # rimworld/select_pawn wants list_colonists' "Thing_<ThingID>" form (first live run: bare ThingID refused)
    sel = B.call("rimworld/select_pawn", pawnId="Thing_%s" % pid) or {}
    if sel.get("success") is False:
        sel = B.call("jawa/select_things", ids=str(pid), action="select") or {}
    gz = B.call("rimworld/list_selected_gizmos") or {}
    gizmos = gz.get("gizmos") or []
    labels = [g.get("label") for g in gizmos]
    jump = next((g for g in gizmos if "pit" in str(g.get("label")).lower() and "jump" in str(g.get("label")).lower()), None)
    det = {"jetty": jt, "rails": rails, "pawn": pid, "select": str(sel)[:160], "gizmos": labels[:30]}
    if jump is None:
        row("FAIL" if gz.get("success") is not False else "UNMEASURED", "MOD" if gz.get("success") is not False else "HARNESS",
            dict(det, why="no 'Jump into pit' gizmo on the jetty colonist"))
        return 1
    ex = B.call("rimworld/execute_gizmo", gizmoId=jump.get("id") or jump.get("gizmoId")) or {}
    acc = B.call("rimworld/press_accept") or {}
    B.call("rimworld/step_game_ticks", ticks=240, pauseFirst=True, timeoutMs=60000)
    ps = {p.get("id"): p for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []}
    p = ps.get(pid) or {}
    end = (p.get("x"), p.get("z"))
    rep = B.call("jawa/flowworks_pit_report", x=P(2, 2)[0], z=P(2, 2)[1]) or {}
    desc = [str(d) for d in rep.get("recentDescents") or [] if str(d).startswith(str(pid) + "@")]
    det.update(execute=str(ex)[:200], accept=str(acc)[:200], end=end, descents=desc)
    row("PASS" if end in pit else "FAIL", "MOD", det)
    B.call("rimworld/clear_selection")
    B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    return 0 if end in pit else 1


if __name__ == "__main__":
    sys.exit(main())
