"""SUSPENSION BRIDGE live proof (SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS; design/RimMandrake/
suspension_bridge_construction_design_2026-10-18.md; the debug_process rule: the functional script ships with the build item
and grows with each later suspension item: underpass, grates, waters, jetty).

  python.exe src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py [out.json] [--origin X,Z] [--fresh-map]

Run from the repo root with python.exe; the bridge must be held. Exit 0 = every MEASURED row PASS. NEVER RUN BY THE BUILD
ITEM: written offline 2026-10-18 while the game belonged to FOUNDRY; every row below is OWED to the first live run.

Owner rulings this proves (2026-10-18, by card unless quoted): name *"Suspension bridge"*; build = drag across like a wall,
1-3 wide, solid ground at both ends; a limit per type plus towers; railings an on/off switch per bridge; railings give no
cover; whole-span collapse with the load shown (parent Q3); vanilla bridges refused over dug ground (parent Q6).

Scenes (plot coords from --origin, default 140,140; dig by jawa/flowworks_excavation_drive, 8 notches = 4 m):
  T1 a 6-square trench (1..6, 0): timber bridge dragged (0,0)-(7,0), built at once (god)  -> rows BUILD, PATH, LOAD.
  T2 a 7-square trench (1..7, 4): timber drag (0,4)-(8,4), NOT god                        -> row REFUSED_LENGTH.
  T3 a 4-square trench (1..4, 8): timber bridge (0,8)-(5,8) god; railings off then on     -> rows RAILS_OFF / RAILS_ON.
  T4 a 4-square trench (1..4, 12): timber bridge (0,12)-(5,12) god; anchor (0,12) destroyed -> row SWING.
  T5 one dug square (10, 0)                                                              -> row VANILLA_REFUSED.
Every read is jawa/static_call RimMandrake.FlowWorks.Pits.RM_SuspensionProofs.<Proof*> (one line out; see that file).

ANTI-GUESSING NOTES
- A BUILD row reads things on the drag's own squares; a PATH row is the production path finder's answer for that pawn now.
- LOAD: colonists are spawned ON the deck until the span reads over 600 kg BEFORE any tick (ProofSpan state=Over), then
  120 ticks run (two load passes of 60); PASS needs every deck of the span gone AND each spawned pawn standing on a dug
  square AND an injury hediff added. A span that never read Over makes the row UNMEASURED, never PASS.
- RAILS: 20 production TryKnockOff rolls at the stagger chance (25%); railings off must drop >= 1 (P(0 of 20) = 0.3%),
  railings on must drop 0.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

PROOF = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
DEEP = 8   # notches: 4 m


def parse(txt):
    kv = {}
    for tok in txt.split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            kv[k] = v
    return kv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="140,140")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH           # noqa: E402  (bridge-side imports only on a live run)
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "suspension_bridge_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "suspension_bridge_proof.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, det):
        rows.append({"id": rid, "status": st, "detail": det})
        print("%-34s %-10s %s" % (rid, st, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def proof(method, arg):
        r = B.call("jawa/static_call", type=PROOF, method=method, args=arg) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return (parse(txt) if r.get("success") is True and not txt.startswith("REFUSED") else {}), txt

    def dig(c, n=DEEP):
        return B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=-1) or {}

    def spawn(c, kind="Colonist", faction="player"):
        r = B.call("jawa/spawn_pawn", kindDef=kind, x=c[0], z=c[1], faction=faction, count=1) or {}
        return ((r.get("pawns") or [{}])[0]).get("id")

    def pawns_by_id():
        return {p.get("id"): p for p in (B.call("jawa/list_pawns", limit=300) or {}).get("pawns") or []}

    def ticks(n):
        return B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40))

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)                        # noqa: E731
    xz = lambda c: "%d,%d" % c                                   # noqa: E731
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("SB_game_playing", "UNMEASURED", {"why": "no game in Playing"})
        return 2

    for dz, n in ((0, 6), (4, 7), (8, 4), (12, 4)):
        for i in range(1, n + 1):
            dig(P(i, dz))
    dig(P(10, 0))

    # T1: build, path, load
    kv, txt = proof("ProofBuild", "%s;%s;timber;god" % (xz(P(0, 0)), xz(P(7, 0))))
    good = kv.get("ok") == "True" and kv.get("anchors") == "2" and kv.get("decks") == "6"
    row("SB_drag_6_timber_builds", "PASS" if good else ("FAIL" if kv else "UNMEASURED"), {"read": txt})
    walker = spawn(P(-1, 0))
    kv, txt = proof("ProofPath", "%s;%s" % (walker, xz(P(8, 0)))) if walker else ({}, "no pawn")
    good = kv.get("found") == "True" and int(kv.get("decked", "0")) >= 6
    row("SB_path_crosses_on_deck", "PASS" if good else ("FAIL" if kv else "UNMEASURED"), {"read": txt})

    riders = []
    for k in range(12):
        riders.append(spawn(P(1 + k % 6, 0)))
        kv, txt = proof("ProofSpan", xz(P(3, 0)))
        if kv.get("state") == "Over":
            break
    before = pawns_by_id()
    over = kv.get("state") == "Over"
    line = kv.get("line", "")
    ticks(120)
    kv2, txt2 = proof("ProofSpan", xz(P(3, 0)))
    after = pawns_by_id()
    fell, hurt = 0, 0
    for pid in riders:
        p0, p1 = before.get(pid) or {}, after.get(pid) or {}
        if not p1:
            continue
        if ox + 1 <= int(p1.get("x", -1)) <= ox + 6 and int(p1.get("z", -1)) == oz:
            fell += 1
        if len(p1.get("hediffs") or []) > len(p0.get("hediffs") or []):
            hurt += 1
    gone = txt2.startswith("SPAN none") or kv2.get("decks") == "0"
    st = "PASS" if over and gone and fell == len([r for r in riders if r]) and hurt >= 1 else "FAIL"
    if not over:
        st = "UNMEASURED"
    row("SB_load_over_rating_whole_span_falls", st,
        {"before": txt, "inspect_line": line, "after": txt2, "riders": len(riders), "fell": fell, "hurt": hurt})

    # T2: too long for timber
    kv, txt = proof("ProofBuild", "%s;%s;timber" % (xz(P(0, 4)), xz(P(8, 4))))
    good = kv.get("ok") == "False" and "at most 6" in txt and kv.get("blueprints") == "0" and kv.get("anchors") == "0"
    row("SB_drag_7_timber_refused", "PASS" if good else ("FAIL" if kv else "UNMEASURED"), {"read": txt})

    # T3: railings
    proof("ProofBuild", "%s;%s;timber;god" % (xz(P(0, 8)), xz(P(5, 8))))
    rider = spawn(P(2, 8))
    proof("ProofRails", "%s;off" % xz(P(2, 8)))
    kv, txt = proof("ProofKnock", "%s;20" % rider) if rider else ({}, "no pawn")
    row("SB_rails_off_some_fall", "PASS" if kv and int(kv.get("fell", "0")) >= 1 else ("FAIL" if kv else "UNMEASURED"), {"read": txt})
    rider2 = spawn(P(3, 8))
    kv0, txt0 = proof("ProofRails", "%s;on" % xz(P(2, 8)))
    kv, txt = proof("ProofKnock", "%s;20" % rider2) if rider2 else ({}, "no pawn")
    good = kv and kv.get("railed") == "True" and kv.get("fell") == "0"
    row("SB_rails_on_nobody_falls", "PASS" if good else ("FAIL" if kv else "UNMEASURED"), {"rails": txt0, "read": txt})

    # T4: lose an anchor -> swing-down from that end
    proof("ProofBuild", "%s;%s;timber;god" % (xz(P(0, 12)), xz(P(5, 12))))
    B.call("jawa/destroy_batch", cells=[{"x": P(0, 12)[0], "z": P(0, 12)[1]}], defName="RM_SuspensionAnchor_Timber")
    ticks(150)
    kv, txt = proof("ProofSwing", "")
    stamps = []
    for tok in txt.split()[1:]:
        c, t = tok.split("@")
        x, z = (int(v) for v in c.split(","))
        if z == oz + 12:
            stamps.append((x, int(t)))
    xs = [x for x, _ in stamps]
    ts = [t for _, t in stamps]
    good = len(stamps) == 4 and xs == sorted(xs) and ts == sorted(ts) and len(set(ts)) == 4
    row("SB_anchor_lost_swings_from_that_end", "PASS" if good else ("FAIL" if stamps else "UNMEASURED"), {"read": txt, "lane": stamps})

    # T5: vanilla bridge refused on a dug square
    kv, txt = proof("ProofVanillaBridge", xz(P(10, 0)))
    good = kv.get("accepted") == "False" and "Use a suspension bridge over dug ground" in txt
    row("SB_vanilla_bridge_refused_over_dug", "PASS" if good else ("FAIL" if kv else "UNMEASURED"), {"read": txt})

    row("SB_settings_off_no_button_never_breaks", "UNMEASURED",
        {"why": "OWED: toggle suspensionBridgesBuildable / suspensionWeightCollapse via jawa/mod_settings_field on "
                "RimMandrake.FlowWorks.Pits.RM_SuspensionSettings and re-run LOAD; not scripted yet"})
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    bad = [r for r in rows if r["status"] == "FAIL"]
    print("suspension bridge proof: %d rows, %d FAIL -> %s" % (len(rows), len(bad), out))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
