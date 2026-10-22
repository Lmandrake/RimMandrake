"""SUSPENSION BRIDGE live proof (SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS; design/RimMandrake/
suspension_bridge_construction_design_2026-10-18.md; the debug_process rule: the functional script ships with the build item
and grows with each later suspension item: underpass, grates, waters, jetty).

  python.exe src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py [out.json] [--origin X,Z] [--fresh-map]
                                                                          [--only posts,grate,...]
  python3    src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py --mock   # every path offline (FakeBridge);
             every row is written SKIP with the verdict it would have reached under "mock" (proves the script, never the game)

Run from the repo root with python.exe; the bridge must be held. Exit 0 = every MEASURED row PASS. NEVER RUN BY THE BUILD
ITEM: written offline 2026-10-18 while the game belonged to FOUNDRY; every row below is OWED to the first live run.

Owner rulings this proves (2026-10-18, by card unless quoted): name *"Suspension bridge"*; build = drag across like a wall,
1-3 wide, solid ground at both ends; a limit per type plus towers; railings an on/off switch per bridge; railings give no
cover; whole-span collapse with the load shown (parent Q3); vanilla bridges refused over dug ground (parent Q6).

Scenes (plot coords from --origin, default 140,140; dig by jawa/flowworks_excavation_drive, 8 notches = 4 m):
  T1 a 6-square trench (1..6, 0): timber bridge dragged (0,0)-(7,0), built at once (god)  -> rows BUILD, PATH, LOAD.
  T2 a 7-square trench (1..7, 4): timber drag (0,4)-(8,4), NOT god                        -> row REFUSED_LENGTH.
  T3 a 4-square trench (1..4, 8), z=9 dug beside it (the open edge): timber bridge (0,8)-(5,8) god; railings off then on
                                                                                          -> rows RAILS_OFF / RAILS_ON.
  T4 a 4-square trench (1..4, 12): timber bridge (0,12)-(5,12) god; anchor (0,12) destroyed -> row SWING.
  T5 one dug square (10, 0)                                                              -> row VANILLA_REFUSED.
GRATE (SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP), plot from origin + (0, 20):
  G1 a 4-square 2 m pit (1..4, 20) of chemfuel under a grated steel bridge, 3 colonists on it, lit; 2,500 ticks; then the
     same with a solid steel bridge at (1..4, 24)                                           -> row GRATE_FIRE.
  G2 a 2 m canal (1..4, 28) holding water under a grated steel bridge; 50 L poured on (2, 28) -> row GRATE_POUR.
  G3 a Steel bar dropped on the grate at (3, 28)                                             -> row GRATE_ITEM_STAYS.
UNDERPASS (SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD), plot from origin + (0, 40):
  U1 a 4 m trench (1..8, 40), a 2-wide steel bridge across it at x=4..5 ((4,39)-(5,41)); colonist A on the floor at (1,40) ordered to
     (8,40), colonist B at (4,38) ordered to (4,42)                                          -> rows UND_FLOOR_PATH, UND_BOTH_ARRIVE.
  U2 a 1.5 m trench (1..8, 46), the same bridge at x=4; colonist on the floor at (1,46)    -> row UND_SHALLOW_WALL.
  U3 colonist set under U1's deck (ProofPutUnder) drops a Steel there                      -> row UND_ITEM_SLIDES.
  U4 gunner under a solid steel deck (U1) vs a colonist on that deck, then the same under a grate (U5: (1..8, 50) 4 m,
     grated steel bridge at x=4)                                                             -> rows UND_SHOT_SOLID, UND_SHOT_GRATE.
  U6 a colonist under U1's deck, the span forced to give way (ProofFell)                     -> row UND_CRUSH_AND_WRECK.
  U7 a stepped pit: west ledge x=1 and east ledge x=4 (z 56..59) at 4 m, core x=2..3 at 7 m; sunken steel bridge (1,57)-(4,57);
     a colonist on the west ledge ordered to the east ledge; its path must stand on >= 2 deck squares -> row UND_SUNKEN_CROSS.
  owed: raiders in a 4 m moat walk under (modcheck record), the L4 picture of a pawn passing under a deck.
WATERS (SUSPENSION_WATERS_BUILD_MAY_BACKTRACK): natural water is wherever the map has it, so the sites are arguments
  (--river / --lake / --sea x1,z1,x2,z2: a straight drag from bank to bank; a row without its argument is UNMEASURED):
  W1 a steel bridge across the river; a colonist crosses (path read, arrival) and every deck square is exempt from the
     current                                                                                -> row WAT_RIVER_CROSS.
  W2 a steel bridge across the lake with one tower planned at the middle                     -> row WAT_LAKE_TOWER_SPANS.
  W3 timber and steel bridges over a 2 m water trench (1..4, 64)/(1..4, 68), a water flood released beside each, 5,000 ticks
     (2 in-game hours)                                                                      -> row WAT_FLOOD_DAMAGE.
  W4 a steel bridge across the sea: built and crossable, or the backtrack reason             -> row WAT_SEA_OR_BACKTRACK.
JETTY (SUSPENSION_JETTY_BUILD_WALK_THE_PLANK), plot from origin + (0, 72): a 4 m pit (1..4, 72..74).
  J1 a 2-square steel jetty (0,73)-(2,73): accepted; a 3-square one (0,72)-(3,72): refused with the reason -> rows JET_TWO_OK, JET_THREE_REFUSED.
  J2 one colonist on (2,73): stands (ProofSpan Ok); a second added: Over, then both jetty squares gone in one load pass and
     both pawns on the pit floor                                                            -> row JET_OVERLOAD_DROPS_WHOLE.
LOOKS (SUSPENSION_ART_RESKIN_HE_SEES_FIRST): a 2 m trench (1..3, 80+2k) per look k; a steel bridge built in that look, railed
  -> rows LOOK_<Look>_RESOLVES: every part styled in the look, no pink texture, graphic paths read (verify L2).
  J3 a new 1-square jetty (0,74)-(1,74), railings off: a colonist on it ordered to jump down (the jump order, an open edge) -> row JET_OPEN_EDGE_DROP (owed: needs the jump order's bridge call).
Every read is jawa/static_call RimMandrake.FlowWorks.Pits.RM_SuspensionProofs.<Proof*> (one line out; see that file).

ANTI-GUESSING NOTES
- A BUILD row reads things on the drag's own squares; a PATH row is the production path finder's answer for that pawn now.
- LOAD: colonists are spawned ON the deck until the span reads over 600 kg BEFORE any tick (ProofSpan state=Over), then
  120 ticks run (two load passes of 60); PASS needs every deck of the span gone AND each spawned pawn standing on a dug
  square AND an injury hediff added. A span that never read Over makes the row UNMEASURED, never PASS.
- GRATE_FIRE: PASS needs >= 1 Burn hediff among the grate's riders AND fewer on the solid deck's (both counts written);
  a run where EITHER pit was not alight (ProofIgnite not LIT: the solid deck's pit is the control and must burn) is
  UNMEASURED, its ignite text and fill replies attached.
- GRATE_POUR: the body read is the decilitres in every dug square within 12 (ProofPour, through RM_LiquidSpill.Spill, the
  production spill); PASS needs rise == 500 dL AND no new filth on the square.
- RAILS: 20 production TryKnockOff rolls at the stagger chance (25%); railings off must drop >= 1 (P(0 of 20) = 0.3%),
  railings on must drop 0.
First live run 2026-10-19 (SUSPENSION_LIVE_DIAGNOSE_FIRST_REAL_RUN), what it taught:
- Pawn injuries come from jawa/list_pawns includeHealth=True at row['health']['hediffs']; the flat 'hediffs' key is always
  empty. A row that sees no health block is UNMEASURED (hediffs_of / health_seen).
- RULED OUT: "rails-off never drops = TryKnockOff broken" - KNOCK read edge=False: no dug square beside a 1-wide deck over a
  1-wide trench. RULED OUT: "a gunner under a solid deck shoots through it" - the target stood on the anchor, not a deck.
- RULED OUT: "the path finder ignores decks" - it walked round a 1-wide trench at the same node count (corridor walls now).
- RULED OUT: "the four looks are a harness misread" - LOOK styled=0 was the MOD: the part defs lacked CompProperties_Styleable,
  so Thing.StyleDef = s was a no-op (selftest_flowworks_suspension_art.py styleable_fails now goes red for it).
- Runs a/b/c reused ONE map (no --fresh-map): each run inherits the last one's pawns, bridges and liquids. Prefer --fresh-map.
- RULED OUT: "LoadOn double-counts cells / counts the deck's own parts / Mass is not kg" - 816 kg with one rider was 14
  pawns of ~58 kg (Mass = kg, StatPart_BodySize): 12 riders of run a left in the bare trench, built over in run b, plus each
  run's rider. MOD: a deck completed over the hole did not put the pawns on its floor in the floor band (Notify_DeckBuilt
  now does, and slides items out). The "empty" read before riders shows any such leftover weight.
- RULED OUT: "destroying an anchor via the bridge bypasses the swing hook" - destroy_batch's Destroy(Vanish) reaches
  Building_SuspensionAnchor.Destroy. The script sent cells=/defName= (the tool takes rects=/categories=), got Fail
  "rects is required" and destroyed nothing. A not-destroyed anchor is UNMEASURED now.
- RULED OUT: "a solid deck stops the pit under it burning" - IgniteNow found no burnable liquid in the control pit (run c
  only; run b lit it). The cause was lost to a 60-char cut and unread fill replies; both are kept now.
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
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
import validation_core as V  # noqa: E402  (preconditions: scope / require / guard; pure python, no bridge at import)

PROOF = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
DEEP = 8   # notches: 4 m


def parse(txt):
    kv = {}
    for tok in txt.split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            kv[k] = v
    return kv


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="140,140")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--river", default="", help="x1,z1,x2,z2: a bank-to-bank drag across this map's river")
    ap.add_argument("--lake", default="", help="x1,z1,x2,z2: a bank-to-bank drag over 10 squares across a lake")
    ap.add_argument("--sea", default="", help="x1,z1,x2,z2: a drag across the sea from the shore")
    ap.add_argument("--only", default="", help="comma list of sections: " + ",".join(SECTIONS))
    ap.add_argument("--mock", action="store_true", help="run every path against FakeBridge; rows are SKIP (mock verdict kept)")
    a = ap.parse_args(argv)
    only = set(x for x in a.only.split(",") if x) or set(SECTIONS)
    if only - set(SECTIONS):
        ap.error("unknown --only section(s) %s; known: %s" % (",".join(sorted(only - set(SECTIONS))), ",".join(SECTIONS)))
    if a.mock:
        B = FakeBridge()
    else:
        import proof_hose as PH           # noqa: E402  (bridge-side imports only on a live run)
        B = PH.PB()
    # PRECONDITIONS (PROOF_VERDICTS_REPAIR_SAME_BUG_EVERY_ROUND): every reply reaches V.PRE through the guard; each section and
    # step runs in a V.scope, so a refused call, a dead read or a staging that did not take withholds its rows' PASS/FAIL
    raw = B
    B = V.guard(B)
    out = a.out or os.path.join(HERE, "suspension_bridge_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "suspension_bridge_proof.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}
    if not a.mock:
        import driver_stamp
        driver_stamp.stamp(res, raw.call)   # validation.py reads a result only at the current mod hash AND deployed DLL

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, det, cls="MOD"):
        st, cls, det = V.PRE.judge(st, cls, det)
        if a.mock:
            det = dict(det, mock=st)
            st = "SKIP"
        rows.append({"id": rid, "status": st, "class": cls, "detail": det})
        print("%-34s %-10s %s" % (rid, st, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def proof(method, arg, answer=False):
        """One RM_SuspensionProofs read. A refused static_call or a 'REFUSED' answer (bad args) is a fault of the open scope;
        so is a reply with no key=value in it, unless `answer=True` (a 'SPAN none' / 'SWING none' read is the measurement)."""
        # RM_SuspensionProofs.PawnById wants the thingIDNumber; jawa/spawn_pawn answers "Human41594": pass the number
        # (first live run 2026-10-19: every pawn-taking proof REFUSED 'arg must be pawnId;...')
        arg = ";".join(re.sub(r"^(?:Thing_)?[A-Za-z]+_?(\d+)$", r"\1", t) for t in str(arg).split(";"))
        r = B.call("jawa/static_call", type=PROOF, method=method, args=arg) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        V.require(not txt.startswith("REFUSED"), "%s accepted its args" % method, txt[:200], cls="HARNESS")
        kv = parse(txt) if r.get("success") is True and not txt.startswith("REFUSED") else {}
        if not answer:
            V.require(kv, "%s answered" % method, txt[:200], cls="HARNESS")
        return kv, txt

    def stage(method, arg):
        """A ProofBuild that is STAGING, not the claim: a bridge that did not stand withholds every row that stands on it."""
        kv, txt = proof(method, arg)
        V.require(kv.get("ok") == "True", "%s staged" % method, txt[:200])
        return kv, txt

    def dig(c, n=DEEP):
        return B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=-1) or {}

    def spawn(c, kind="Colonist", faction="player"):
        r = B.call("jawa/spawn_pawn", kindDef=kind, x=c[0], z=c[1], faction=faction, count=1) or {}
        return ((r.get("pawns") or [{}])[0]).get("id")

    def pawns_by_id():
        return pawns_of(B)

    def ticks(n):
        return B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40))

    ox, oz = (int(v) for v in a.origin.split(","))
    FakeBridge.ox, FakeBridge.floor_z = ox, oz
    P = lambda dx, dz: (ox + dx, oz + dz)                        # noqa: E731
    xz = lambda c: "%d,%d" % c                                   # noqa: E731
    if a.fresh_map and not a.mock:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok = True if a.mock else V._wait_playing(B, leave_s=0)[0]
    if not ok:
        row("SB_game_playing", "UNMEASURED", {"why": "no game in Playing"})
        return 2
    if a.mock:
        a.river = a.river or "%d,%d,%d,%d" % (ox + 30, oz, ox + 40, oz)
        a.lake = a.lake or "%d,%d,%d,%d" % (ox + 30, oz + 10, ox + 50, oz + 10)
        a.sea = a.sea or "%d,%d,%d,%d" % (ox + 30, oz + 20, ox + 36, oz + 20)
    if not a.mock:
        # the plots must be bare, undug, unroofed ground: on a fresh rainforest map every BUILD was refused 'must start on
        # solid, undug ground with nothing built on it' (trees/plants on the anchors) - live 2026-10-19, first live run
        rect = (max(ox - 2, 1), max(oz - 2, 1), 40, 94)
        res["site_calm"] = V.site_calm(B)   # TESTENV_PREFLIGHT_HARDEN_TRISPIKE_AT_ARM: map-gen hostiles/hives stop safe_advance at arm
        B.call("jawa/kill_hostiles")
        B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect", args="%d;%d;%d;%d" % rect)
        site_rows = []
        with V.scope("site"):
            V.prepare_site(B, rect, site_rows, "suspension_site")
        bad = [r for r in site_rows if r.get("status") not in (None, "PASS")]
        if bad:
            row("SB_site_ready", "UNMEASURED", {"rect": rect, "site": bad[:3]})
            only = set()            # unprepared ground: every section would measure the site, not the mod (review 2026-10-20)
    ctx = dict(args=a, B=B, P=P, xz=xz, row=row, proof=proof, stage=stage, dig=dig, spawn=spawn, pawns_by_id=pawns_by_id, ticks=ticks, ox=ox, oz=oz)
    for name in SECTIONS:
        if name in only:
            print("== section %s" % name, flush=True)
            with V.scope(name):
                SECTIONS[name](ctx) if name != "posts" else posts(ctx)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    bad = [r for r in rows if r["status"] == "FAIL"]
    if a.mock:
        mock_bad = [r["id"] for r in rows if r["detail"].get("mock") != "PASS" and not r["detail"].get("owed")]
        print("MOCK: suspension bridge proof: %d rows, mock verdicts not PASS: %s -> %s" % (len(rows), mock_bad or "none", out))
        return 1 if mock_bad else 0
    print("suspension bridge proof: %d rows, %d FAIL -> %s" % (len(rows), len(bad), out))
    return 1 if bad else 0


def posts(ctx):
    """SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS rows (T1-T5). Each step runs in its own V.scope: a refused call, a staging
    that did not take (stage(), V.require) or a probe that never answered withholds that step's verdicts, by construction."""
    B, P, xz, row, proof, stage, dig, spawn, pawns_by_id, ticks = (ctx[k] for k in ("B", "P", "xz", "row", "proof", "stage", "dig",
                                                                                   "spawn", "pawns_by_id", "ticks"))
    ox, oz = ctx["ox"], ctx["oz"]

    def trench(dz, n):
        for i in range(1, n + 1):
            dig(P(i, dz))

    # each step digs its own trench INSIDE its scope: a refused dig withholds the rows standing on that trench, not the others
    # T1: build, path, load
    with V.scope("T1_build") as t1:
        trench(0, 6)
        kv, txt = proof("ProofBuild", "%s;%s;timber;god" % (xz(P(0, 0)), xz(P(7, 0))))
        good = kv.get("ok") == "True" and kv.get("anchors") == "2" and kv.get("decks") == "6"
        row("SB_drag_6_timber_builds", "PASS" if good else "FAIL", {"read": txt})
        V.require(good, "T1 bridge built", txt)          # PATH and LOAD stand on it (adopted below)
    with V.scope("T1_path"):
        V.adopt(t1)
        # a 1-wide trench is walked round: live 2026-10-19 the path went (-1,0)->(0,1)..(7,1)->(8,0), 10 cells like the deck
        # route but without the deck's pathCost (SITE). Granite walls along z=-1 and z=+1 leave the deck the only short way over.
        wall = B.call("jawa/spawn_batch", ops=";".join("Wall:%d,%d" % P(x, dz) for x in range(-2, 10) for dz in (-1, 1)),
                      stuff="BlocksGranite") or {}
        walker = spawn(P(-1, 0))
        kv, txt = proof("ProofPath", "%s;%s" % (walker, xz(P(8, 0)))) if walker else ({}, "no pawn")
        good = kv.get("found") == "True" and int(kv.get("decked", "0")) >= 6
        row("SB_path_crosses_on_deck", "PASS" if good else "FAIL", {"read": txt, "walls": wall.get("success")})
    with V.scope("T1_load"):
        V.adopt(t1)
        # the span's load with nobody on it (live 2026-10-19 read 816 kg with ONE rider: what else weighs on the deck?)
        _, empty_txt = proof("ProofSpan", xz(P(3, 0)), answer=True)
        # pass 2 run 3 (2026-10-19, HARNESS): two drafted riders sharing a deck square shuffle apart, and 3 of 10 stepped off
        # the deck onto the anchor/ground inside the 60-tick load check (cells read before/after). Ballast the deck with a stack
        # of granite blocks per square (75 x 1 kg) and put at most ONE rider per square.
        ballast = B.call("jawa/spawn_batch", ops=";".join("BlocksGranite:%d,%d,75" % P(1 + k, 0) for k in range(6))) or {}
        riders = []
        for k in range(6):
            riders.append(spawn(P(1 + k, 0)))
            # pass 2 (2026-10-19, HARNESS): undrafted riders walked off inside the 60-tick load check: drafted, read back by
            # the harness (preconditions.NOOP_CHECKS jawa/set_draft)
            if riders[-1]:
                B.call("jawa/set_draft", pawnId=riders[-1], drafted=True)
            kv, txt = proof("ProofSpan", xz(P(3, 0)), answer=True)
            if kv.get("state") == "Over":
                break
        before = pawns_by_id()
        over = kv.get("state") == "Over"
        line = kv.get("line", "")
        V.require(over, "span read Over", txt)
        ticks(120)
        kv2, txt2 = proof("ProofSpan", xz(P(3, 0)), answer=True)
        after = pawns_by_id()
        V.require(health_seen(after), "pawn health read", "no health block in list_pawns: injuries unreadable")
        V.require(all(r in after for r in riders if r), "every rider still in the read", [r for r in riders if r and r not in after])
        fell, hurt = 0, 0
        for pid in riders:
            p0, p1 = before.get(pid) or {}, after.get(pid) or {}
            if not p1:
                continue
            if ox + 1 <= int(p1.get("x", -1)) <= ox + 6 and int(p1.get("z", -1)) == oz:
                fell += 1
            if len(hediffs_of(p1) or []) > len(hediffs_of(p0) or []):
                hurt += 1
        gone = txt2.startswith("SPAN none") or kv2.get("decks") == "0"
        st = "PASS" if gone and fell == len([r for r in riders if r]) and hurt >= 1 else "FAIL"
        row("SB_load_over_rating_whole_span_falls", st,
            {"empty": empty_txt, "before": txt, "inspect_line": line, "after": txt2, "riders": len(riders), "fell": fell, "hurt": hurt,
             "healthSeen": health_seen(after),
             # pass 2 trace: where each rider stood before/after the 120 ticks (load fell 608 -> 365 with no collapse)
             "cells": [[(before.get(pid) or {}).get("x"), (before.get(pid) or {}).get("z"), (after.get(pid) or {}).get("x"),
                        (after.get(pid) or {}).get("z")] for pid in riders if pid],
             "originZ": oz, "ballast": ballast.get("success"),
             "afterSpans": [proof("ProofSpan", xz(P(c, 0)), answer=True)[1][:120] for c in (1, 6)]})

    # T2: too long for timber (the refusal IS the claim: an ok=False answer is measured, never a fault)
    with V.scope("T2"):
        trench(4, 7)
        kv, txt = proof("ProofBuild", "%s;%s;timber" % (xz(P(0, 4)), xz(P(8, 4))))
        good = kv.get("ok") == "False" and "at most 6" in txt and kv.get("blueprints") == "0" and kv.get("anchors") == "0"
        row("SB_drag_7_timber_refused", "PASS" if good else "FAIL", {"read": txt})

    # T3: railings. A fall needs an open edge: a dug square BESIDE the deck (OpenEdgeBeside). Under a 1-wide bridge over a
    # 1-wide trench every dug square is decked, so live 2026-10-19 read edge=False and 0 of 20 fell (SITE): dig z=9 too.
    with V.scope("T3"):
        trench(8, 4)
        for i in range(1, 5):
            dig(P(i, 9))
        _, txt3b = stage("ProofBuild", "%s;%s;timber;god" % (xz(P(0, 8)), xz(P(5, 8))))
        with V.scope("T3_rails_off"):
            rider = spawn(P(2, 8))
            kvoff, _ = proof("ProofRails", "%s;off" % xz(P(2, 8)))
            V.require(kvoff.get("on") == "False", "railings switched off", kvoff)
            kv, txt = proof("ProofKnock", "%s;20" % rider) if rider else ({}, "no pawn")
            V.require(kv.get("edge") == "True", "open edge beside the rider", txt)
            row("SB_rails_off_some_fall", "PASS" if int(kv.get("fell", "0")) >= 1 else "FAIL", {"read": txt, "build": txt3b})
        with V.scope("T3_rails_on"):
            rider2 = spawn(P(3, 8))
            kv0, txt0 = proof("ProofRails", "%s;on" % xz(P(2, 8)))
            V.require(kv0.get("on") == "True", "railings switched on", txt0)
            kv, txt = proof("ProofKnock", "%s;20" % rider2) if rider2 else ({}, "no pawn")
            V.require(kv.get("edge") == "True", "open edge beside the rider", txt)
            good = kv.get("railed") == "True" and kv.get("fell") == "0"
            row("SB_rails_on_nobody_falls", "PASS" if good else "FAIL", {"rails": txt0, "read": txt, "build": txt3b})

    # T4: lose an anchor -> swing-down from that end
    # destroy_batch takes rects="x,z,w,h" and categories; live 2026-10-19 sent cells=/defName=, the tool answered Fail
    # "rects is required", nothing was destroyed and the SWING log read empty (HARNESS). Its Destroy(Vanish) reaches
    # Building_SuspensionAnchor.Destroy -> Notify_SupportLost, the production hook. 4 decks x SwingTicksPerCell 20 < 150 ticks.
    with V.scope("T4"):
        trench(12, 4)
        _, txtb = stage("ProofBuild", "%s;%s;timber;god" % (xz(P(0, 12)), xz(P(5, 12))))
        gone = B.call("jawa/destroy_batch", rects="%d,%d,1,1" % P(0, 12), categories="Building") or {}
        V.require(int(gone.get("destroyed") or 0) >= 1, "anchor destroyed", {k: gone.get(k) for k in ("success", "message", "destroyed")})
        ticks(150)
        kv, txt = proof("ProofSwing", "-", answer=True)   # an empty args string is a 0-param call; 'SWING none' is an answer
        stamps = []
        for tok in txt.split()[1:]:
            if "@" not in tok:          # 'SWING none' or a key=value token: not a stamp (live 2026-10-19 crashed here)
                continue
            c, t = tok.split("@", 1)
            x, z = (int(v) for v in c.split(","))
            if z == oz + 12:
                stamps.append((x, int(t)))
        xs = [x for x, _ in stamps]
        ts = [t for _, t in stamps]
        good = len(stamps) == 4 and xs == sorted(xs) and ts == sorted(ts) and len(set(ts)) == 4
        row("SB_anchor_lost_swings_from_that_end", "PASS" if good else "FAIL",
            {"read": txt, "lane": stamps, "build": txtb, "destroy": {k: gone.get(k) for k in ("success", "message", "destroyed")}})

    # T5: vanilla bridge refused on a dug square. The mod's postfix acts only where vanilla ACCEPTED: a dry dug square is
    # not Bridgeable terrain, so live 2026-10-19 read vanilla's own refusal and the ruled one never ran (SITE). Water in the
    # square makes it bridgeable terrain to vanilla.
    with V.scope("T5"):
        dig(P(10, 0))
        B.call("jawa/flowworks_excavation_drive", x=P(10, 0)[0], z=P(10, 0)[1], deepenLevels=0, setFill=2)
        kv, txt = proof("ProofVanillaBridge", xz(P(10, 0)))
        good = kv.get("accepted") == "False" and "Use a suspension bridge over dug ground" in txt
        V.require(good or not (kv.get("accepted") == "False" and "Bridgeable" in txt),
                  "vanilla judged the square bridgeable (the ruled refusal was asked)", txt)
        row("SB_vanilla_bridge_refused_over_dug", "PASS" if good else "FAIL", {"read": txt})

    row("SB_settings_off_no_button_never_breaks", "UNMEASURED",
        {"owed": True, "why": "OWED: toggle suspensionBridgesBuildable / suspensionWeightCollapse via jawa/mod_settings_field on "
                "RimMandrake.FlowWorks.Pits.RM_SuspensionSettings and re-run LOAD; not scripted yet"})


FIRE_TYPE = "RimMandrake.FlowWorks.RM_LiquidFireProof"
FLUIDID_TYPE = "RimMandrake.FlowWorks.RM_FluidIdentityProof"


def burns(p):
    return sum(1 for h in (hediffs_of(p) or []) if "Burn" in (h if isinstance(h, str) else str(h.get("def") or h.get("defName") or h)))


def grate(ctx):
    """SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP rows: verify L2 x3 (fire through a grate vs a solid deck; a pour drains to the
    body; an item stays on the grate)."""
    B, P, xz, row, proof, stage, dig, spawn, pawns_by_id, ticks = (ctx[k] for k in ("B", "P", "xz", "row", "proof", "stage", "dig",
                                                                                   "spawn", "pawns_by_id", "ticks"))
    def pit(dz):
        for i in range(1, 5):
            dig(P(i, dz), 4)                                     # 2 m
    counts, fills, builds = {}, {}, {}
    with V.scope("GRATE_fire"):
        pit(20)                                                  # each scope digs its own pits: a refused dig of one
        pit(24)                                                  # scene never withholds the other's row
        for dz, tier in ((20, "steelgrated"), (24, "steel")):
            # every fill reply is kept: live 2026-10-19 (run c, same map as runs a/b) the solid-deck CONTROL pit read "REFUSED:
            # fire off or nothing burnable" cut at 60 chars, the "(fluid X, F=n)" cause lost and the fill replies discarded
            fills[tier] = []
            for i in range(1, 5):
                fr = B.call("jawa/static_call", type=FLUIDID_TYPE, method="ProofFillWithFluid",
                            args="%d,%d,%d,RM_Fluid_Chemfuel" % (P(i, dz)[0], P(i, dz)[1], 2)) or {}
                fills[tier].append(str(fr.get("result") or fr.get("message") or fr.get("error") or ""))
            builds[tier] = stage("ProofBuild", "%s;%s;%s;god" % (xz(P(0, dz)), xz(P(5, dz)), tier))
            # drafted, as T1's riders: an undrafted colonist walks away from a lit pit and reads as "not burned" (review 2026-10-20)
            riders = [spawn(P(k, dz)) for k in (2, 3, 4)]
            for r in riders:
                if r:
                    B.call("jawa/set_draft", pawnId=r, drafted=True)
            before = pawns_by_id()
            lit = B.call("jawa/static_call", type=FIRE_TYPE, method="ProofIgnite", args=xz(P(1, dz))) or {}
            lit_txt = str(lit.get("result") or "")
            # a pit that never lit (no burnable liquid: a refused fill, a cell left by an earlier run) asks nothing of the mod
            V.require(lit_txt.startswith("LIT"), "%s pit lit" % tier, {"ignite": lit_txt[:200], "fills": fills[tier]})
            ticks(2500)
            after = pawns_by_id()
            # no health block, or a rider gone from the after-read (burned to death, despawned): burns read 0, which is ignorance
            V.require(health_seen(after), "pawn health read", "no health block in list_pawns")
            V.require(all(r in after for r in riders if r), "every rider still in the read", [r for r in riders if r and r not in after])
            n = sum(max(0, burns(after.get(r) or {}) - burns(before.get(r) or {})) for r in riders if r)
            counts[tier] = (n, lit_txt[:200], proof("ProofGrate", xz(P(3, dz)), answer=True)[1])
        g, s_ = counts["steelgrated"][0], counts["steel"][0]
        # intent: BOTH pits burn; the solid deck is the control whose riders stay unburnt
        row("GRATE_fire_burns_people_above", "PASS" if g >= 1 and g > s_ else "FAIL",
            {"grateBurns": g, "solidBurns": s_, "reads": counts, "builds": {t: b[1] for t, b in builds.items()}, "fills": fills})
    with V.scope("GRATE_pour_item"):
        pit(28)
        for i in range(1, 5):                                         # 1 m of water in the 2 m canal: room for the pour
            B.call("jawa/flowworks_excavation_drive", x=P(i, 28)[0], z=P(i, 28)[1], deepenLevels=0, setFill=2)
        _, txtb = stage("ProofBuild", "%s;%s;steelgrated;god" % (xz(P(0, 28)), xz(P(5, 28))))
        with V.scope("GRATE_pour"):       # the pour's own read must not withhold the item row below
            kv, txt = proof("ProofPour", "%s;50;RM_Liquid_FreshWater" % xz(P(2, 28)))
            good = kv.get("rise") == "500" and kv.get("filthAfter") == kv.get("filthBefore")
            row("GRATE_pour_drains_to_body", "PASS" if good else "FAIL", {"build": txtb, "read": txt})
        dropped = B.call("jawa/spawn_batch", ops="Steel:%d,%d" % P(3, 28)) or {}
        ticks(60)
        things = B.call("jawa/list_things", rect="%d,%d,1,1" % P(3, 28), limit=20, includePawns=False) or {}
        names = [t.get("def") or t.get("defName") for t in (things.get("things") or [])]
        row("GRATE_item_stays_on_deck", "PASS" if "Steel" in names else "FAIL",
            {"things": names, "build": txtb, "dropped": dropped.get("success")})


def underpass(ctx):
    """SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD rows (verify L2 x7; raiders and the picture owed)."""
    B, P, xz, row, proof, stage, dig, spawn, ticks = (ctx[k] for k in ("B", "P", "xz", "row", "proof", "stage", "dig", "spawn", "ticks"))
    def trench(z, depth):
        for i in range(1, 9):
            dig(P(i, z), depth)

    # U1 and U5 are 2 wide (x=4..5): the shot rows need a colonist ON a deck square beside the one the gunner is under. Live
    # 2026-10-19 the target stood on (4,41), the ANCHOR (solid ground), so no deck was between them (HARNESS).
    # Each bridge is staged in its own scope and adopted by exactly the rows that stand on it (a vacuous shallow-trench path or
    # an item that "slides" off nothing is withheld, never PASS).
    with V.scope("U1_build") as u1:       # each bridge's trench is dug inside its own scope, adopted by the rows standing on it
        trench(40, 8)
        stage("ProofBuild", "%s;%s;steel;god" % (xz(P(4, 39)), xz(P(5, 41))))
    with V.scope("U2_build") as u2:
        trench(46, 3)
        stage("ProofBuild", "%s;%s;steel;god" % (xz(P(4, 45)), xz(P(4, 47))))
    with V.scope("U5_build") as u5:
        trench(50, 8)
        stage("ProofBuild", "%s;%s;steelgrated;god" % (xz(P(4, 49)), xz(P(5, 51))))
    with V.scope("U_pawn_a") as fa:
        a_ = spawn(P(1, 40))
    with V.scope("U_pawn_b") as fb:
        b_ = spawn(P(4, 38))
    with V.scope("UND_floor"):
        V.adopt(u1, fa)
        kv, txt = proof("ProofUnderPath", "%s;%s" % (a_, xz(P(8, 40)))) if a_ else ({}, "no pawn")
        good = kv.get("found") == "True" and int(kv.get("decked", "0")) >= 1 and kv.get("view") == "floor"
        row("UND_floor_path_walks_under", "PASS" if good else "FAIL", {"read": txt})
    with V.scope("UND_both"):
        V.adopt(u1, fa, fb)
        oa = B.call("jawa/order_pawn", pawnId=a_, x=P(8, 40)[0], z=P(8, 40)[1], waitTicks=900, draft=True) or {}
        ob = B.call("jawa/order_pawn", pawnId=b_, x=P(4, 42)[0], z=P(4, 42)[1], waitTicks=600, draft=True) or {}
        # pass 2 (2026-10-19, HARNESS): jawa/order_pawn reports the READ-BACK cell under end{x,z} (null when despawned), not at the
        # pawn's top level: the old read gave (None, None) for both pawns and scored FAIL
        at = {p.get("id"): ((p.get("end") or {}).get("x"), (p.get("end") or {}).get("z")) for o in (oa, ob) for p in (o.get("pawns") or [])}
        V.require(a_ in at and b_ in at, "order_pawn read back both pawns", {"a": oa, "b": ob})
        good = at.get(a_) == P(8, 40) and at.get(b_) == P(4, 42)
        row("UND_both_arrive", "PASS" if good else "FAIL", {"a": at.get(a_), "b": at.get(b_)})
    with V.scope("UND_shallow"):
        V.adopt(u2)
        c_ = spawn(P(1, 46))
        kv, txt = proof("ProofUnderPath", "%s;%s" % (c_, xz(P(8, 46)))) if c_ else ({}, "no pawn")
        good = kv.get("found") == "False" or kv.get("decked") == "0"
        row("UND_shallow_trench_is_a_wall", "PASS" if good else "FAIL", {"read": txt})
    with V.scope("UND_item"):
        V.adopt(u1)
        d_ = spawn(P(2, 40))
        put_d, _ = proof("ProofPutUnder", "%s;%s" % (d_, xz(P(4, 40)))) if d_ else ({}, "no pawn")
        V.require(put_d.get("under") == "True", "pawn stands under the deck", put_d)      # else DropUnder reads under=False: the harness
        kv, txt = proof("ProofDropUnder", "%s;Steel" % d_)
        good = kv.get("under") == "True" and kv.get("underDeck") == "False"
        row("UND_item_slides_to_open_floor", "PASS" if good else "FAIL", {"read": txt})
    for tag, z, want, deck in (("solid", 40, "False", u1), ("grate", 50, "True", u5)):
        with V.scope("UND_shot_%s" % tag):
            V.adopt(deck)                   # the deck the shot should cross
            g = B.call("jawa/spawn_pawn", kindDef="Mercenary_Gunner", x=P(3, z)[0], z=P(3, z)[1], faction="player", count=1) or {}
            gid = ((g.get("pawns") or [{}])[0]).get("id")
            tgt = spawn(P(5, z))                                       # ON the deck square beside the one the gunner is under
            proof("ProofPutUnder", "%s;%s" % (gid, xz(P(4, z))))
            kvb, txtb = proof("ProofBand", tgt) if tgt else ({}, "no pawn")
            kv, txt = proof("ProofShot", "%s;%s" % (gid, tgt)) if gid and tgt else ({}, "no pawns")
            # the target not on a deck or the gunner not under one: no deck between them (SITE)
            V.require(kvb.get("onDeck") == "True" and kv.get("shooterUnder") == "True", "a deck between gunner and target",
                      {"band": txtb, "shot": txt})
            row("UND_shot_%s_deck" % tag, "PASS" if kv.get("can") == want else "FAIL", {"want": want, "read": txt, "target": txtb})
    with V.scope("UND_crush"):
        V.adopt(u1)                         # no deck over the pawn: nothing could fall on it
        e_ = spawn(P(2, 40))
        put_e, _ = proof("ProofPutUnder", "%s;%s" % (e_, xz(P(4, 40)))) if e_ else ({}, "no pawn")
        V.require(put_e.get("under") == "True", "pawn stands under the deck", put_e)
        kv0, _ = proof("ProofFell", "-1,-1")   # an off-map square: the counters only (live 2026-10-19: "" was REFUSED -> {})
        hb = hediffs_of(pawns_of(B).get(e_) or {})
        kv, txt = proof("ProofFell", xz(P(4, 40)))
        ha = hediffs_of(pawns_of(B).get(e_) or {})
        V.require(ha is not None and hb is not None, "pawn health read", "no health block in list_pawns")
        hb, ha = hb or [], ha or []
        good = int(kv.get("crushed", "0")) > int(kv0.get("crushed", "0")) and len(ha) > len(hb)
        row("UND_crush_below_and_wreck", "PASS" if good else "FAIL",
            {"before": kv0, "after": txt, "hediffs": [len(hb), len(ha)],
             "owed": "wreck blocks the floor until a clear job runs: read RM_SuspensionWreck on (4,40) and its deconstruct"})
    with V.scope("UND_sunken"):
        for zz in range(56, 60):
            dig(P(1, zz), 8)
            dig(P(4, zz), 8)
            dig(P(2, zz), 14)
            dig(P(3, zz), 14)
        kv, txt = proof("ProofBuild", "%s;%s;steel;god" % (xz(P(1, 57)), xz(P(4, 57))))
        kvs, txts = proof("ProofSpan", xz(P(2, 57)))
        f_ = spawn(P(1, 59))
        # the WALK reader (ProofPath: squares of the path that carry a deck), not ProofUnderPath (squares a deck passes OVER):
        # "crossed" means the pawn's path stands on the sunken deck's two core squares (2,57),(3,57). A path found by any other
        # way (round, or down the 7 m core) is not this row's PASS (review 2026-10-20).
        kvp, txtp = proof("ProofPath", "%s;%s" % (f_, xz(P(4, 59)))) if f_ else ({}, "no pawn")
        good = (kv.get("ok") == "True" and kvs.get("deckNotches") == "8" and kvp.get("found") == "True"
                and int(kvp.get("decked", "0")) >= 2)
        row("UND_sunken_bridge_crossed", "PASS" if good else "FAIL", {"build": txt, "span": txts, "path": txtp})
    row("UND_raiders_walk_under_moat", "UNMEASURED", {"owed": True, "why": "OWED: a raid into a 4 m moat with a bridge over it, "
        "recorded with modcheck (behaviour is the ruling, not a bug)"})
    row("UND_L4_picture_pawn_under_deck", "UNMEASURED", {"owed": True, "why": "OWED: one joint screenshot of a pawn passing under a deck"})


def waters(ctx):
    """SUSPENSION_WATERS_BUILD_MAY_BACKTRACK rows (verify L2 x4)."""
    B, P, xz, row, proof, stage, dig, spawn, ticks, a = (ctx[k] for k in ("B", "P", "xz", "row", "proof", "stage", "dig", "spawn",
                                                                         "ticks", "args"))

    def site(spec):
        if not spec:
            return None
        v = [int(t) for t in spec.split(",")]
        return (v[0], v[1]), (v[2], v[3])

    def lane(s0, s1):
        dx, dz = (s1[0] > s0[0]) - (s1[0] < s0[0]), (s1[1] > s0[1]) - (s1[1] < s0[1])
        n = max(abs(s1[0] - s0[0]), abs(s1[1] - s0[1]))
        return [(s0[0] + dx * i, s0[1] + dz * i) for i in range(n + 1)]

    r = site(a.river)
    if r:
        with V.scope("WAT_river"):
            kv, txt = proof("ProofBuild", "%s;%s;steel;god" % (xz(r[0]), xz(r[1])))
            cells = lane(*r)[1:-1]
            ex = [proof("ProofWater", xz(c))[0].get("exempt") for c in cells]
            before = (r[0][0] - (r[1][0] > r[0][0]) + (r[1][0] < r[0][0]), r[0][1] - (r[1][1] > r[0][1]) + (r[1][1] < r[0][1]))
            w = spawn(before)
            kvp, txtp = proof("ProofPath", "%s;%s" % (w, xz(r[1]))) if w else ({}, "no pawn")
            o = (B.call("jawa/order_pawn", pawnId=w, x=r[1][0], z=r[1][1], waitTicks=1500, draft=True) or {}) if w else {}
            at = {p.get("id"): ((p.get("end") or {}).get("x"), (p.get("end") or {}).get("z"))   # read-back cell is end{x,z}
                  for p in (o.get("pawns") or [])}.get(w)
            V.require(at is not None, "order_pawn read back the walker", o)
            V.require(bool(ex), "the river drag has interior deck squares to read", {"drag": r})
            good = bool(ex) and kv.get("ok") == "True" and all(e == "True" for e in ex) and kvp.get("found") == "True" and at == r[1]
            row("WAT_river_cross_no_drift", "PASS" if good else "FAIL", {"build": txt, "exempt": ex, "path": txtp, "arrived": at})
    else:
        row("WAT_river_cross_no_drift", "UNMEASURED", {"why": "no --river x1,z1,x2,z2 given (this map's river crossing)"})
    lk = site(a.lake)
    if lk:
        with V.scope("WAT_lake"):
            cells = lane(*lk)
            mid = cells[len(cells) // 2]
            tw = B.call("jawa/spawn_batch", ops="RM_SuspensionTower:%d,%d" % mid) or {}     # a tower that never spawned: SITE
            kv, txt = proof("ProofBuild", "%s;%s;steel;god" % (xz(lk[0]), xz(lk[1])))
            k1, t1 = proof("ProofSpan", xz(cells[1]))
            k2, t2 = proof("ProofSpan", xz(cells[-2]))
            cap = 10
            good = (kv.get("ok") == "True" and k1.get("span") == "1/2" and k2.get("span") == "2/2"
                    and int(k1.get("decks", "99")) <= cap and int(k2.get("decks", "99")) <= cap)
            row("WAT_lake_tower_two_spans", "PASS" if good else "FAIL", {"build": txt, "span1": t1, "span2": t2, "tower": str(tw)[:160]})
    else:
        row("WAT_lake_tower_two_spans", "UNMEASURED", {"why": "no --lake x1,z1,x2,z2 given (a crossing longer than 10 squares)"})
    with V.scope("WAT_flood"):
        hp = {}
        for tier, z in (("timber", 64), ("steel", 68)):
            for i in range(1, 5):
                dig(P(i, z), 4)
                B.call("jawa/flowworks_excavation_drive", x=P(i, z)[0], z=P(i, z)[1], deepenLevels=0, setFill=3)
            stage("ProofBuild", "%s;%s;%s;god" % (xz(P(0, z)), xz(P(5, z)), tier))   # a deck that never stood: hp 0 == 0
            hp[tier] = [proof("ProofDeckHp", xz(P(2, z)))[0]]
            B.call("jawa/flowworks_spawn_flood", x=P(2, z - 1)[0], z=P(2, z - 1)[1], fluidDefName="RM_Fluid_Water", volume=30)
        ticks(5000)                                                  # a clock that never moved floods nothing
        for tier, z in (("timber", 64), ("steel", 68)):
            hp[tier].append(proof("ProofDeckHp", xz(P(2, z)))[0])
        t0, t1 = hp["timber"]
        s0, s1 = hp["steel"]
        # both decks must be awash: a timber deck the flood never reached keeps full hp and would read FAIL (SITE, not mod)
        V.require(int(t1.get("awash", "0")) > 0 and int(s1.get("awash", "0")) > 0, "both decks awash", hp)
        good = int(t1.get("hp", "0")) < int(t0.get("max", "0")) and s1.get("hp") == s0.get("hp")
        row("WAT_flood_damages_timber_not_steel", "PASS" if good else "FAIL", {"timber": hp["timber"], "steel": hp["steel"]})
    sea = site(a.sea)
    if sea:
        with V.scope("WAT_sea"):
            kv, txt = proof("ProofBuild", "%s;%s;steel;god" % (xz(sea[0]), xz(sea[1])))
            w = spawn(sea[0])
            kvp, txtp = proof("ProofPath", "%s;%s" % (w, xz(sea[1]))) if w else ({}, "no pawn")
            # HARNESS (belt live 2026-10-22): a path found AROUND a small sea patch read PASS with decked=0 -- crossable means
            # the path stands on the deck
            good = kv.get("ok") == "True" and kvp.get("found") == "True" and int(kvp.get("decked") or 0) > 0
            row("WAT_sea_or_backtrack", "PASS" if good else "FAIL",
                {"build": txt, "path": txtp, "ifFail": "record the measured reason on FLOWWORKS_BRIDGES_DESIGN_SPAN_ANYTHING and set "
                 "suspensionOverSea off (the backtrack rule)"})
    else:
        row("WAT_sea_or_backtrack", "UNMEASURED", {"why": "no --sea x1,z1,x2,z2 given (a coast crossing)"})


def jetty(ctx):
    """SUSPENSION_JETTY_BUILD_WALK_THE_PLANK rows (verify L2 x3)."""
    B, P, xz, row, proof, dig, spawn, ticks = (ctx[k] for k in ("B", "P", "xz", "row", "proof", "dig", "spawn", "ticks"))
    with V.scope("JET_pit") as pit:
        for z in (72, 73, 74):
            for i in range(1, 5):
                dig(P(i, z), 8)
    with V.scope("JET_two"):
        V.adopt(pit)
        kv, txt = proof("ProofJetty", "%s;%s;steel;god" % (xz(P(0, 73)), xz(P(2, 73))))
        good = kv.get("ok") == "True" and kv.get("anchors") == "1" and kv.get("decks") == "2"
        row("JET_two_square_steel_accepted", "PASS" if good else "FAIL", {"read": txt})
    with V.scope("JET_three"):
        kv3, txt3 = proof("ProofJetty", "%s;%s;steel" % (xz(P(0, 72)), xz(P(3, 72))))
        good = kv3.get("ok") == "False" and "at most 2" in txt3 and kv3.get("blueprints") == "0"
        row("JET_three_square_refused", "PASS" if good else "FAIL", {"read": txt3})
    with V.scope("JET_overload"):
        V.adopt(pit)
        # drafted, as T1's riders: an undrafted rider walks off before the 120-tick check and the overload never fires (SITE)
        def rider(c):
            pid = spawn(c)
            if pid:
                B.call("jawa/set_draft", pawnId=pid, drafted=True)
            return pid
        p1 = rider(P(2, 73))
        k1, t1 = proof("ProofSpan", xz(P(2, 73)), answer=True)
        p2 = rider(P(1, 73))
        k2, t2 = proof("ProofSpan", xz(P(2, 73)), answer=True)
        # the claim is "an overloaded jetty drops whole": a span that never read Ok then Over (leftover weight, riders under the
        # rating) asked nothing of the load pass, as T1's LOAD row (review 2026-10-20)
        V.require(k1.get("state") == "Ok" and k2.get("state") == "Over", "jetty read Ok then Over", [t1, t2])
        ticks(120)
        k3, t3 = proof("ProofSpan", xz(P(2, 73)), answer=True)
        ps = pawns_of(B)
        on_floor = [ps.get(p) and (ps[p].get("x"), ps[p].get("z")) in (P(1, 73), P(2, 73)) for p in (p1, p2)]
        good = (t3.startswith("SPAN none") or k3.get("decks") == "0") and all(on_floor)
        row("JET_overload_drops_whole_at_root", "PASS" if good else "FAIL", {"one": t1, "two": t2, "after": t3, "onFloor": on_floor})
    row("JET_open_edge_drop_on_order", "UNMEASURED", {"owed": True, "why": "OWED: railings off, order the 'Jump into pit' float-menu "
        "job on a pawn on the jetty (no bridge call drives that menu yet); the rail-off knock row (SB_rails_off_some_fall) proves the edge"})


def looks(ctx):
    """SUSPENSION_ART_RESKIN_HE_SEES_FIRST rows (verify L2: each look's deck, railing and anchor resolve, no pink)."""
    P, xz, row, proof, dig = (ctx[k] for k in ("P", "xz", "row", "proof", "dig"))
    for k, look in enumerate(("Scrapper", "Industrial", "Modern", "Futuristic")):
        with V.scope("LOOK_%s" % look):
            z = 80 + 2 * k
            for i in range(1, 4):
                dig(P(i, z), 4)
            kv, txt = proof("ProofLook", "%s;%s;%s" % (look, xz(P(0, z)), xz(P(4, z))))
            parts = int(kv.get("parts", "0"))
            good = parts >= 5 and kv.get("styled") == str(parts) and kv.get("pink") == "0" and ("/%s/" % look) in txt
            row("LOOK_%s_resolves" % look, "PASS" if good else "FAIL", {"read": txt})


def pawns_of(B):
    # includeHealth: without it list_pawns sends no hediffs at all, and with it they sit at row['health']['hediffs'], never
    # row['hediffs'] (first live run 2026-10-19: LOAD hurt=0, crush hediffs [0,0], grate burns 0 - all read an empty list)
    return {p.get("id"): p for p in (B.call("jawa/list_pawns", limit=300, includeHealth=True) or {}).get("pawns") or []}


def hediffs_of(p):
    """The pawn row's hediff list (jawa/list_pawns includeHealth=True nests it under 'health'); None when the row carries no
    health block at all - the caller cannot see injuries and its row is UNMEASURED, never a clean zero."""
    h = p.get("health") if isinstance(p, dict) else None
    if not isinstance(h, dict):
        return None
    return h.get("hediffs") or []


def health_seen(rows):
    return any(hediffs_of(p) is not None for p in rows.values())


SECTIONS = {"posts": None, "grate": grate, "underpass": underpass, "waters": waters, "jetty": jetty, "looks": looks}


class FakeBridge(object):
    """Offline stand-in for the RimBridge client: every call answers in the shape the live mod would on a PASS, so --mock
    walks every path of this script. It knows nothing about the game; a mock verdict proves the script only."""

    def __init__(self):
        self.next_id, self.calls, self.reads, self.tags, self.last_tier, self.span = 1000, [], 0, {}, "", 0
        self.shot, self.fell, self.under_shallow, self.dug, self.hp = 0, 0, {}, {}, 0

    def call(self, tool, **kw):
        method = tool
        self.calls.append(method)
        if method == "jawa/static_call":
            return {"success": True, "result": self.static(kw.get("method"), kw.get("args") or "")}
        if method == "jawa/flowworks_excavation_drive":
            self.dug[(kw.get("x"), kw.get("z"))] = kw.get("deepenLevels")
            return {"success": True}
        if method == "jawa/order_pawn":
            # the real shape (JawaBenchTerrainTools OrderPawn): the read-back cell under end{x,z}
            return {"pawns": [{"id": kw.get("pawnId"), "end": {"x": kw.get("x"), "z": kw.get("z")}}], "ticksElapsed": kw.get("waitTicks")}
        if method == "jawa/set_draft":
            return {"success": True, "drafted": kw.get("drafted") is True, "wasDrafted": False, "changed": True}
        if method == "jawa/spawn_pawn":
            self.next_id += 1
            self.tags[self.next_id] = self.last_tier
            self.under_shallow[self.next_id] = self.dug.get((kw.get("x"), kw.get("z"))) == 3
            return {"pawns": [{"id": self.next_id}]}
        if method == "jawa/list_pawns":
            self.reads += 1
            late = self.reads % 2 == 0
            # the real shape: hediffs only with includeHealth, nested at row['health']['hediffs'] (JawaBenchTerrainTools)
            hl = (lambda hs: {"health": {"hediffs": [{"def": h} for h in hs]}}) if kw.get("includeHealth") else (lambda hs: {})
            if self.last_tier == "jetty":
                return {"pawns": [dict({"id": i, "x": FakeBridge.ox + 1 + (i % 2), "z": FakeBridge.floor_z + 73}, **hl([]))
                                  for i in range(1001, self.next_id + 1)]}
            return {"pawns": [dict({"id": i, "x": FakeBridge.ox + 1 + (i % 6), "z": FakeBridge.floor_z},
                                   **hl(([] if not late else ["Burn", "Bruise"] if self.tags.get(i) == "steelgrated" else ["Bruise"])
                                        + (["Crush"] * self.fell)))
                              for i in range(1001, self.next_id + 1)]}
        if method == "jawa/destroy_batch":
            ok = bool(kw.get("rects")) and kw.get("categories") == "Building"   # the real tool Fails without rects
            return {"success": ok, "destroyed": 1 if ok else 0, "message": "Destroyed 1 thing(s)" if ok else "rects is required"}
        if method == "jawa/list_things":
            return {"success": True, "things": [{"def": "Steel"}]}
        return {"success": True}

    ox, floor_z = 140, 140
    tier_decks = {"timber": 6}

    def static(self, m, arg):
        if m == "ProofBuild":
            self.last_tier = arg.split(";")[2]
            if arg.split(";")[2] == "timber" and "god" not in arg:
                return "BUILD ok=False anchors=0 decks=0 blueprints=0 reason=A timber suspension bridge spans at most 6 squares"
            return "BUILD ok=True anchors=2 decks=6 blueprints=0 reason=-"
        if m == "ProofPath":
            return "PATH found=True cells=9 decked=6"
        if m == "ProofSpan" and self.last_tier == "jetty":
            self.jet += 1
            return ["SPAN tier=steel load=70.0 rating=120 state=Ok decks=2 line=Load 70 / 120 kg",
                    "SPAN tier=steel load=140.0 rating=120 state=Over decks=2 line=Load 140 / 120 kg", "SPAN none"][min(self.jet, 3) - 1]
        if m == "ProofSpan":
            self.span += 1
            if self.last_tier == "steel":
                return ("SPAN tier=steel load=0.0 rating=2000 state=Ok decks=2 railings=False deckNotches=8 span=%d/2 line=Load 0 / 2,000 kg"
                        % (1 + self.span % 2))
            return "SPAN none" if self.span % 2 == 0 else "SPAN tier=timber load=640.0 rating=600 state=Over decks=6 line=Load 640 / 600 kg"
        if m == "ProofRails":
            on = arg.endswith("on")
            return "RAILS on=%s railed=%d" % (on, 4 if on else 0)
        if m == "ProofKnock":
            self.knock = getattr(self, "knock", 0) + 1
            return "KNOCK trials=20 fell=%d railed=%s edge=True" % ((5, "False") if self.knock == 1 else (0, "True"))
        if m == "ProofSwing":
            z = FakeBridge.ox + 12
            return "SWING " + " ".join("%d,%d@%d" % (FakeBridge.ox + i, z, 100 + 20 * i) for i in range(1, 5))
        if m == "ProofVanillaBridge":
            return "VANILLA accepted=False reason=Use a suspension bridge over dug ground"
        if m == "ProofFillWithFluid":
            return "FILLED (1, 0, 1) F=2 fluid=RM_Fluid_Chemfuel"
        if m == "ProofIgnite":
            return "LIT 1 cell"
        if m == "ProofUnderPath":
            pid = int(arg.split(";")[0])
            shallow = self.under_shallow.get(pid)
            return "UNDERPATH found=True cells=8 decked=%d view=floor" % (0 if shallow else 1)
        if m == "ProofPutUnder":
            return "PUTUNDER under=True"
        if m == "ProofBand":
            return "BAND under=False onDeck=True passes=True view=deck deckNotches=0"
        if m == "ProofDropUnder":
            return "DROPUNDER under=True at=1,1 underDeck=False slid=1"
        if m == "ProofShot":
            grate = self.last_tier == "steelgrated" and self.shot > 0
            self.shot += 1
            return "SHOT can=%s shooterUnder=True targetUnder=False ranged=True" % grate
        if m == "ProofFell":
            self.fell += 1 if arg else 0
            return "FELL crushed=%d wrecks=%d slid=1" % (self.fell, self.fell)
        if m == "ProofJetty":
            if "%d," % (FakeBridge.ox + 3) in arg.split(";")[1]:
                return "JETTY ok=False anchors=0 decks=0 blueprints=0 railed=0 reason=A jetty reaches at most 2 squares out (this one: 3)."
            self.last_tier, self.jet = "jetty", 0
            return "JETTY ok=True anchors=1 decks=2 blueprints=0 railed=2 reason=-"
        if m == "ProofLook":
            look = arg.split(";")[0]
            return ("LOOK look=%s parts=8 styled=8 pink=0 paths=RimMandrake/FlowWorks/SuspensionBridge/%s/RM_SuspensionDeck|"
                    "RimMandrake/FlowWorks/SuspensionBridge/%s/RM_SuspensionAnchor" % (look, look, look))
        if m == "ProofWater":
            return "WATER terrain=WaterMovingChestDeep water=True ocean=False river=True spannable=True decked=True exempt=True walkable=True swim=False"
        if m == "ProofDeckHp":
            self.hp += 1
            timber = "64" in arg.split(",")[1][-2:] or self.hp % 2 == 1
            return "HP hp=%d max=480 decks=4 awash=%d floodHits=24" % (480 if self.hp <= 2 or not timber else 456, 0 if self.hp <= 2 else 2)
        if m == "ProofGrate":
            return "GRATE grated=True deck=True fire=True attach=0.75 splash=0.50 scorches=3 drainedDl=500"
        if m == "ProofPour":
            return "POUR dl=500 bodyBefore=4000 bodyAfter=4500 rise=500 filthBefore=0 filthAfter=0"
        return "OK"


if __name__ == "__main__":
    sys.exit(main())
