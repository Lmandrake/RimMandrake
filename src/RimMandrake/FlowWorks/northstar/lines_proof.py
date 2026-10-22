"""LINES live proof (PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 7 and POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS L2;
design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §Ruled design P1-P9; the debug_process rule: the functional
script ships with the build item).

  python.exe src/RimMandrake/FlowWorks/northstar/lines_proof.py [out.json] [--origin X,Z] [--fresh-map] [--only a,b]
  python3    src/RimMandrake/FlowWorks/northstar/lines_proof.py --mock [--mock-faults a,b] [--only a,b]
             every path offline against FakeBridge (a small line world model, NOT the mod); every row is written SKIP with
             the verdict it would have reached kept under detail.mock (proves the script, never the game)

Run from the repo root with python.exe on the minimal list (FlowWorks + Gimme Some Slack: pipe poles and the fallen wire are
GSS's); the bridge must be held. Exit 0 = every row PASS; 1 = a FAIL; 2 = a row could not be measured. WRITTEN OFFLINE
2026-10-21 (BENCH, owner asleep): every row is OWED to its first live run.

The rows' C# proof class is RimMandrake.FlowWorks.Machinery.RM_LineProofs (FlowWorks Source/Machinery/RM_LineProofs.cs;
contracts in OWED_PROOFS). A live run first asks it one question (ProofLineCounters); if the loaded FlowWorks predates it,
every row is written UNMEASURED/HARNESS naming it, and nothing is staged. Used as is beside it: RM_SuspensionProofs
(ProofBuild, ProofFell), RM_DrawbridgeProofs (ProofMakeDrawbridge, ProofDevSet), RM_PromotionProofs.ProofLadder, the hose
probe (proof_hose.PB.hp: lay, tank, filltank, net, pump), jawa/build_batch, jawa/flowworks_excavation_drive,
jawa/battery_set, jawa/destroy_batch, jawa/list_things, jawa/list_pawns, jawa/spawn_pawn, jawa/mod_settings_field.

Owner rulings this proves (2026-10-20, by card): rigid pipe and conduit never on a deck (rope included) and never on a dug
square; cords and hoses on any deck; covers carry nothing (answer 3); pipe poles carry a pipe across a pit (answer 8); digging
breaks lines at the commit (answer 2); a collapsing deck drops a live cord as a fallen wire, the net split once (P4); a hose
hangs down a ladder into a pit and a raised ladder leaves it hanging (answer 7); a dig under a laid hose re-routes it (P5);
a cord on a drawbridge leaf disconnects while raised and rejoins lowered (answer 6).

Scenes (plot coords from --origin, default 30,30; dug by jawa/flowworks_excavation_drive, 8 notches = 4 m, covers need it):
  A  z=0    rope bridge (0,0)-(5,0) over a trench x=1..4, z=-3..3; reel (-8,-1), hose to (10,0)  -> ROPE_DECK_RIGID_REFUSED_FLEX_OK
  B  z=12   trench x=1..4, z=9..15, plank-lattice covers on z=12; reel (-8,11), hose to (10,12)  -> COVER_CARRIES_NO_HOSE
  C  z=24   trench x=3..6, z=20..28; tank (-3,24), pipes (-1..0,24), poles (1,24) and (8,24), pipe (9,24), tank (10,24)
                                                                                                -> POLE_SPAN_CARRIES_LIQUID
  D  z=36   tank (-3,36), pipes (-1..6,36), tank (7,36); dig (3,36)                             -> DIG_UNDER_PIPE_SPLITS_NET
  E  z=48   timber bridge (0,48)-(5,48), trench x=1..4, z=46..50; battery (-4,48), cords (-3..7,48), lamp (8,48)
                                                                                                -> CORD_DECK_LAMP_LIT
  F  z=60   timber drawbridge (0,60)-(5,60) (winch), trench x=1..4, z=58..62; battery, cords, lamp as E
                                                                                                -> LEAF_RAISED_LAMP_DARK
  G  z=72   timber bridge (0,72)-(5,72), trench x=1..4, z=70..74; battery, cords, lamp as E; the span collapsed; a colonist
            spawned on a fallen square                                                           -> COLLAPSE_CORD_SHOCKS_ONCE
  H  z=84   pump (0,84), battery (3,83), reel (0,85) above the pump, tank (0,82) below it; a 3x3 pit x=8..10, z=84..86
            filled, a ladder (8,85) hung on the west wall; hose to (9,85), free end Intake         -> LADDER_HOSE_DRAINS_RAISED_STAYS
  I  z=100  reel (0,100), hose to (16,100) on open ground; a pit x=7..9, z=98..102 dug under it -> DIG_REROUTES_LAID_HOSE

Each row: PROVE (the call) / EXPECT (the bar) / LIES (how it could pass falsely), written beside it below.

ANTI-GUESSING NOTES
- The placement claim is read through GenConstruct.CanPlaceBlueprintAt (RM_LineProofs.ProofCanPlace), the gate a player's
  click goes through, never through build_batch: build_batch god-spawns and ignores placement.
- The hose claims are read off the LAY (ProofHoseLine counts lay cells on a deck / a cover / another band), never off the
  hose probe's success flag alone: a hose that routes round the deck also "succeeds".
- A pipe pole's span may already be strung by GSS's auto-link when the second pole spawns: ProofLinkPoles reports the verdict
  and strung=True either way; strung is what the row reads.
- Counters (RM_LineDigBreak, RM_DeckCollapseLines, RM_MapComponent_FallenCords, GSS RM_FallenWireShock.shocks) are process
  statics: read before and after, never absolute.
- A freshly built consumer reads unpowered for ~100-170 ticks on vanilla's net (proof_hose measured): lamp rows POLL.
- UNVERIFIED LAYOUT GUESSES (first live run decides): a 2x2 tank / reel occupies Position..Position+1 on both axes; a pit
  cover stands only on a superdeep (4 m) square; the collapse wreck may block spawning on a fallen square (then the row is
  UNMEASURED/SITE, never FAIL); setFill=4 on an 8-notch pit leaves water the intake can reach.
"""
import argparse
import contextlib
import copy
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

LPROOF = "RimMandrake.FlowWorks.Machinery.RM_LineProofs"       # C#: contracts in OWED_PROOFS
SPROOF = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
DPROOF = "RimMandrake.FlowWorks.Pits.RM_DrawbridgeProofs"
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
GSS_AERIAL = "RimMandrake.GimmeSomeSlack.Aerial.AerialSettings"
DEEP = 8           # notches: 4 m (a pit cover needs a superdeep square)
WATER = "Water"    # proof_hose.LIQUID_WATER on a live run (read there; the mock takes this)
COVER_DEF = "RM_PitCover_PlankLattice"
LAMP_DEF = "StandingLamp"
SHOCK_HEDIFF = "RM_FallenWireShock"

ROW_IDS = ["ROPE_DECK_RIGID_REFUSED_FLEX_OK", "COVER_CARRIES_NO_HOSE", "POLE_SPAN_CARRIES_LIQUID", "DIG_UNDER_PIPE_SPLITS_NET",
           "CORD_DECK_LAMP_LIT", "LEAF_RAISED_LAMP_DARK", "COLLAPSE_CORD_SHOCKS_ONCE", "LADDER_HOSE_DRAINS_RAISED_STAYS",
           "DIG_REROUTES_LAID_HOSE", "COVER_BREAK_DROPS_RIDER", "PITFALL_SAVED_ARRIVAL_FALLS"]
# which item's L2 each row closes (validation.py's lines chain and the ledger read this)
ROW_ITEM = {r: "PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE" for r in ROW_IDS}
ROW_ITEM.update({"CORD_DECK_LAMP_LIT": "POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS",
                 "LEAF_RAISED_LAMP_DARK": "POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS",
                 "COVER_BREAK_DROPS_RIDER": "FLOWWORKS_PITCOVER_FIX_BURNS_PAWN_UNHARMED",
                 "PITFALL_SAVED_ARRIVAL_FALLS": "FLOWWORKS_PITFALL_FIX_HISTORY_NOT_SAVED"})
NPROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"   # ProofTrap (trap state read), ProofShove (unjudged displacement)

# The C# the rows call (RM_LineProofs; selftest_lines_proof checks each method exists and answers its word). One string arg
# each (';' inside), one line out: a word then key=value tokens; "REFUSED: why" on bad args.
OWED_PROOFS = {
    "ProofCanPlace": "defName;x,z -> GenConstruct.CanPlaceBlueprintAt (the patched placement gate). 'PLACE ok=T|F kind=K "
                     "surface=S why=..'",
    "ProofSurface": "x,z -> RM_LineCrossing.SurfaceAt + RM_HoseBands. 'SURFACE s=S hoseClosed=T|F band=N rules=T|F'",
    "ProofNet": "x1,z1;x2,z2 (two tanks/machines) -> shared liquid-net component + the pole seam. 'NET same=T|F a=N b=N spans=S "
                "aerial=E fitting=F'",
    "ProofLinkPoles": "x1,z1;x2,z2 -> GSS CompAerialAnchor.TryLink by name. 'LINK verdict=V strung=T|F spans=N'",
    "ProofPower": "x,z -> the CompPowerTrader there (else a transmitter). 'POWER on=T|F net=N trader=T|F'",
    "ProofCord": "x,z -> the power cord there. 'CORD cut=T|F transmits=T|F net=N line=..'",
    "ProofHoseLine": "rx,rz -> the reel's laid hose. 'HOSELINE laid=T|F ramps=N ladders=N cut=T|F cells=N deck=N cover=N dug=N "
                     "geom=G retract=.. line=..'",
    "ProofHoseRole": "rx,rz;Capped|Intake|Outflow -> STAGING, the gizmo's write. 'ROLE role=R'",
    "ProofPitWater": "x,z,w,h -> dug water (dl). 'PITWATER dl=N wet=N cells=N'",
    "ProofLineCounters": "'' -> 'LINES broken=N commits=N cordsDropped=N hosesCut=N tore=N liveFalls=N liveHalves=N "
                         "leafReconnects=N netBumps=N shocks=N'",
}


def parse(txt):
    kv = {}
    for tok in str(txt).split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            kv[k] = v
    return kv


def num(kv, k, default=None):
    try:
        return int(str(kv.get(k)).split("/")[0])
    except (TypeError, ValueError):
        return default


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="30,30")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--only", default="", help="comma list of rows: " + ",".join(ROW_IDS))
    ap.add_argument("--drain-ticks", type=int, default=1500)
    ap.add_argument("--mock", action="store_true", help="run every path against FakeBridge; rows are SKIP (mock verdict kept)")
    ap.add_argument("--mock-faults", default="", help="comma list of FakeBridge faults: " + ",".join(FakeBridge.FAULTS))
    a = ap.parse_args(argv)
    only = [x.strip().upper() for x in a.only.split(",") if x.strip()] or list(ROW_IDS)
    if set(only) - set(ROW_IDS):
        ap.error("unknown --only row(s) %s; known: %s" % (",".join(sorted(set(only) - set(ROW_IDS))), ",".join(ROW_IDS)))
    faults = [f for f in a.mock_faults.split(",") if f]
    if set(faults) - set(FakeBridge.FAULTS):
        ap.error("unknown --mock-faults %s" % ",".join(sorted(set(faults) - set(FakeBridge.FAULTS))))
    global WATER
    if a.mock:
        raw = FakeBridge(faults)
    else:
        import proof_hose as PH           # noqa: E402  (bridge-side imports only on a live run)
        raw = PH.PB()
        WATER = PH.LIQUID_WATER
    B = V.guard(raw)
    import tempfile
    out = a.out or (os.path.join(tempfile.gettempdir(), "lines_mock_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
                    if a.mock else os.path.join(HERE, "lines_result_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    rows = []
    res = {"script": "lines_proof.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a),
           "owedProofs": sorted(OWED_PROOFS)}
    if a.mock:
        res["mode"] = "mock"              # never 'live': validation.py refuses a result no game produced
    else:
        import driver_stamp
        driver_stamp.stamp(res, raw.call)  # validation.py reads a result only at the current mod hash AND deployed DLL

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        try:
            os.replace(out + ".tmp", out)
        except OSError:          # Windows python over \\wsl.localhost: a replace can be refused while a reader holds the file
            with open(out, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=1, default=str)

    def row(rid, st, det, cls="MOD"):
        st, cls, det = V.PRE.judge(st, cls, det)
        if st == "FAIL" and cls != "MOD":
            st = "UNMEASURED"                   # a SITE/HARNESS fault is never scored as a mod FAIL
        if a.mock:
            det = dict(det, mock=st)
            st = "SKIP"
        rows.append({"id": rid, "status": st, "class": cls, "item": ROW_ITEM[rid], "detail": det})
        print("%-32s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    # ------------------------------------------------------------------ helpers (every reply reaches V.PRE through the guard)
    def _static(ty, method, arg, answer):
        r = B.call("jawa/static_call", type=ty, method=method, args=arg) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        V.require(not txt.startswith("REFUSED"), "%s accepted its args" % method, txt[:200], cls="HARNESS")
        kv = parse(txt) if r.get("success") is True and not txt.startswith("REFUSED") else {}
        if not answer:
            V.require(kv, "%s answered" % method, txt[:200], cls="HARNESS")
        return kv, txt

    def lproof(method, arg="", answer=False):
        return _static(LPROOF, method, arg, answer)

    def sproof(method, arg, answer=False):
        return _static(SPROOF, method, arg, answer)

    def dproof(method, arg, answer=False):
        return _static(DPROOF, method, arg, answer)

    def counters():
        kv, _ = lproof("ProofLineCounters", "-")   # jawa/static_call reads args="" as ZERO params (live 2026-10-21); the arg is ignored
        return {k: num(kv, k) for k in ("broken", "commits", "cordsDropped", "hosesCut", "tore", "liveFalls", "liveHalves",
                                        "leafReconnects", "netBumps", "shocks")}

    def delta(c0, c1, f):
        return None if c0.get(f) is None or c1.get(f) is None else c1[f] - c0[f]

    def dig(c, n=DEEP, fill=-1):
        return B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=fill) or {}

    def build(*ops):
        ops = [o for o in ops if o]
        return B.call("jawa/build_batch", ops=";".join(ops), faction="player", wipeExisting=False) or {}

    def ticks(n):
        r = B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}
        V.require(r.get("success") is not False, "the clock moved %d ticks" % n, r, cls="HARNESS")
        return r.get("success") is not False

    def poll(fn, bound, step=10):
        """Tick in steps until fn() is truthy; (value, ticks waited)."""
        waited, v = 0, fn()
        while not v and waited < bound:
            if not ticks(step):
                return v, waited
            waited += step
            v = fn()
        return v, waited

    def spawn(c, kind="Colonist", faction="player"):
        r = B.call("jawa/spawn_pawn", kindDef=kind, x=c[0], z=c[1], faction=faction, count=1) or {}
        return ((r.get("pawns") or [{}])[0]).get("id")

    def pawns():
        return {p.get("id"): p for p in (B.call("jawa/list_pawns", limit=400, includeHealth=True) or {}).get("pawns") or []}

    def things(defname, c):
        lt = B.call("jawa/list_things", defName=defname, rect="%d,%d,1,1" % c, limit=5) or {}
        return len(lt.get("things") or [])

    def lamp_on(c):
        kv, _ = lproof("ProofPower", xz(c), answer=True)
        return kv.get("on") == "True"

    def charge(c):
        lt = B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % c, limit=2) or {}
        bid = ((lt.get("things") or [{}])[0]).get("id")
        V.require(bid is not None, "the battery is on the map", lt)
        if bid is not None:
            B.call("jawa/battery_set", thing=bid, mode="setPct", value=1.0)

    def trench(x0, x1, z0, z1, n=DEEP):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                dig(P(x, z), n)

    def lay(reel, to):
        """The hose probe's instant staging lay (the production TryLay + EnsureLay); its refusal is a measurement."""
        return B.hp("lay:%d,%d,%d,%d" % (reel + to), answer=True)

    def hose(reel):
        kv, txt = lproof("ProofHoseLine", xz(reel))
        return kv, txt

    def power_line(z, battery_dx=-4, lamp_dx=8):
        """battery, a cord on every square from battery+1 to lamp-1 on row z, the lamp; the battery charged. Built by god
        spawn (build_batch): what the row tests is what a laid cord carries, not where a player may click."""
        bat, lamp = P(battery_dx, z), P(lamp_dx, z)
        build("Battery:%d,%d" % bat, *["RM_PowerCord:%d,%d" % P(x, z) for x in range(battery_dx + 1, lamp_dx)],
              "%s:%d,%d" % ((LAMP_DEF,) + lamp))
        ticks(2)
        charge(bat)
        return bat, lamp

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)        # noqa: E731
    xz = lambda c: "%d,%d" % c                   # noqa: E731

    # ------------------------------------------------------------------ preflight
    if a.fresh_map and not a.mock:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok = True if a.mock else V._wait_playing(B, leave_s=0)[0]
    if not ok:
        for rid in only:
            row(rid, "UNMEASURED", {"why": "no game in Playing"}, cls="HARNESS")
        return 2
    # the owed C# first: one question, answered or not. Missing, nothing is staged and every row names what is owed.
    probe = B.call("jawa/static_call", type=LPROOF, method="ProofLineCounters", args="-", _answer=True) or {}
    if probe.get("success") is not True:
        res["owedWhy"] = str(probe.get("error") or probe.get("message") or probe)[:300]
        for rid in only:
            row(rid, "UNMEASURED", {"why": "%s is not in the loaded FlowWorks (%s): deploy a FlowWorks built with it"
                                           % (LPROOF, res["owedWhy"][:120]), "owedProofs": sorted(OWED_PROOFS)}, cls="HARNESS")
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
        print("lines proof: %s missing -> every row UNMEASURED/HARNESS -> %s" % (LPROOF, out))
        return 2
    if not a.mock:
        rect = (max(ox - 14, 1), max(oz - 8, 1), 36, 116)
        res["site_calm"] = V.site_calm(B)   # TESTENV_PREFLIGHT_HARDEN_TRISPIKE_AT_ARM: map-gen hostiles/hives stop safe_advance at arm
        B.call("jawa/kill_hostiles")
        B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect",
               args="%d;%d;%d;%d" % rect)
        site_rows = []
        with V.scope("site"):
            V.prepare_site(B, rect, site_rows, "lines_site")
        bad = [r for r in site_rows if r.get("status") not in (None, "PASS")]
        if bad:
            for rid in only:
                row(rid, "UNMEASURED", {"why": "site not prepared", "rect": rect, "site": bad[:3]}, cls="SITE")
            return 2
        B.call("rimworld/set_god_mode", enabled=True)

    ctx = dict(a=a, B=B, P=P, xz=xz, row=row, lproof=lproof, sproof=sproof, dproof=dproof, counters=counters, delta=delta,
               dig=dig, build=build, ticks=ticks, poll=poll, spawn=spawn, pawns=pawns, things=things, lamp_on=lamp_on,
               trench=trench, lay=lay, hose=hose, power_line=power_line, res=res, save=save)
    for rid in ROW_IDS:
        if rid in only:
            print("== row %s" % rid, flush=True)
            with V.scope(rid):
                SCENES[rid](ctx)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    if a.mock:
        bad = [r["id"] for r in rows if r["detail"].get("mock") != "PASS"]
        print("MOCK: lines proof: %d rows, mock verdicts not PASS: %s -> %s" % (len(rows), bad or "none", out))
        return 1 if any(r["detail"].get("mock") == "FAIL" for r in rows) else (2 if bad else 0)
    fails = [r for r in rows if r["status"] == "FAIL"]
    unm = [r for r in rows if r["status"] != "PASS"]
    print("lines proof: %d rows, %d FAIL, %d not PASS -> %s" % (len(rows), len(fails), len(unm), out))
    return 1 if fails else (2 if unm else 0)


def _c(ctx, *ks):
    return [ctx[k] for k in ks]


# ====================================================================== the rows
def rope_deck(ctx):
    """PROVE ProofCanPlace (the production placement gate) for RM_UniversalPipe, PowerConduit and RM_PowerCord on a rope deck
    square, and a hose laid from a reel to the far bank of a 7-row trench whose only short way over is the rope deck.
    EXPECT pipe and conduit refused (kind RigidPipe / RigidConduit), cord accepted (FlexCord); the hose laid with >= 3 lay
    cells on the deck. LIES: a square that is not a rope deck refuses a pipe for another reason (surface must read RopeDeck,
    SITE); a placement gate that refuses everything also refuses the pipe (the cord's acceptance and a pipe accepted on
    solid ground are part of the bar); a hose that routed round the trench also 'succeeds' (deck cells are the bar)."""
    P, xz, row, lproof, sproof = _c(ctx, "P", "xz", "row", "lproof", "sproof")
    ctx["trench"](1, 4, -3, 3)
    kb, tb = sproof("ProofBuild", "%s;%s;rope;god" % (xz(P(0, 0)), xz(P(5, 0))))
    V.require(kb.get("ok") == "True", "rope bridge built", tb)
    ks, ts = lproof("ProofSurface", xz(P(2, 0)))
    V.require(ks.get("s") == "RopeDeck", "the square reads as a rope deck", ts)
    place = {}
    for d in ("RM_UniversalPipe", "PowerConduit", "RM_PowerCord"):
        kv, txt = lproof("ProofCanPlace", "%s;%s" % (d, xz(P(2, 0))))
        place[d] = (kv.get("ok"), kv.get("kind"), txt)
    kg, tg = lproof("ProofCanPlace", "RM_UniversalPipe;%s" % xz(P(-2, 4)))
    V.require(kg.get("ok") == "True", "control: a pipe is accepted on solid ground", tg)
    reel = P(-8, -1)
    ctx["build"](V.reel_west(reel))
    ctx["ticks"](2)
    ly = ctx["lay"](reel, P(10, 0))
    kh, th = ctx["hose"](reel)
    good = (place["RM_UniversalPipe"][0] == "False" and place["RM_UniversalPipe"][1] == "RigidPipe"
            and place["PowerConduit"][0] == "False" and place["PowerConduit"][1] == "RigidConduit"
            and place["RM_PowerCord"][0] == "True" and place["RM_PowerCord"][1] == "FlexCord"
            and kh.get("laid") == "True" and (num(kh, "deck") or 0) >= 3)
    row("ROPE_DECK_RIGID_REFUSED_FLEX_OK", "PASS" if good else "FAIL",
        {"surface": ts, "place": {k: v[2] for k, v in place.items()}, "control": tg, "lay": ly, "hose": th})


def cover_no_hose(ctx):
    """PROVE plank-lattice covers on the middle row of a 7-row 4 m trench; ProofSurface on a cover; a hose laid to the far bank.
    EXPECT the cover reads Cover with hoseClosed=True; the hose is laid with 0 lay cells on a cover (it goes round). LIES: a
    cover that never stood (build refused, the square still open) is 'not crossed' trivially (surface must read Cover, SITE);
    a hose that could not be laid at all is UNMEASURED/SITE (the claim is about the route it takes, not a refusal)."""
    P, xz, row, lproof = _c(ctx, "P", "xz", "row", "lproof")
    ctx["trench"](1, 4, 9, 15)
    ctx["build"](*["%s:%d,%d" % ((COVER_DEF,) + P(x, 12)) for x in range(1, 5)])
    ks, ts = lproof("ProofSurface", xz(P(2, 12)))
    V.require(ks.get("s") == "Cover", "the square reads as an intact pit cover", ts)
    reel = P(-8, 11)
    ctx["build"](V.reel_west(reel))
    ctx["ticks"](2)
    ly = ctx["lay"](reel, P(10, 12))
    kh, th = ctx["hose"](reel)
    V.require(kh.get("laid") == "True", "the hose was laid (round the trench)", [ly, th])
    good = ks.get("hoseClosed") == "True" and kh.get("laid") == "True" and num(kh, "cover") == 0
    row("COVER_CARRIES_NO_HOSE", "PASS" if good else "FAIL", {"surface": ts, "lay": ly, "hose": th})


def pole_span(ctx):
    """PROVE two tanks joined only by a pipe-pole span across a 4 m trench (poles strung through GSS's own TryLink); ProofNet;
    the hose probe's net store from tank A; then pole B destroyed.
    EXPECT strung=True; NET same=True aerial>=1; tank B listed in tank A's store; after the cut same=False. LIES: tanks joined
    some other way (a stray pipe round the trench) read same=True with no span: aerial>=1 and the cut's split are the bar; a
    span strung but carrying nothing (no pipe at a pole) reads same=False, which IS the failure."""
    B, P, xz, row, lproof = _c(ctx, "B", "P", "xz", "row", "lproof")
    ctx["trench"](3, 6, 20, 28)
    ta, tb = P(-3, 24), P(10, 24)
    ctx["build"]("RM_LiquidTank:%d,%d" % ta, "RM_UniversalPipe:%d,%d" % P(-1, 24), "RM_UniversalPipe:%d,%d" % P(0, 24),
                 "RM_PipePole:%d,%d" % P(1, 24), "RM_PipePole:%d,%d" % P(8, 24), "RM_UniversalPipe:%d,%d" % P(9, 24),
                 "RM_LiquidTank:%d,%d" % tb)
    ctx["ticks"](2)
    kl, tl = lproof("ProofLinkPoles", "%s;%s" % (xz(P(1, 24)), xz(P(8, 24))))
    ctx["ticks"](2)
    kn, tn = lproof("ProofNet", "%s;%s" % (xz(ta), xz(tb)))
    B.hp("filltank:%d,%d=%s,%d" % (ta + (WATER, 5000)))
    store = B.hp("net:%d,%d" % ta)
    listed = any(tuple(t.get("tank") or ()) == tb for t in store.get("tanks") or [])
    gone = B.call("jawa/destroy_batch", rects="%d,%d,1,1" % P(8, 24), categories="Building") or {}
    V.require(int(gone.get("destroyed") or 0) >= 1, "pole B destroyed", {k: gone.get(k) for k in ("success", "destroyed")})
    ctx["ticks"](5)
    kc, tc = lproof("ProofNet", "%s;%s" % (xz(ta), xz(tb)))
    good = (kl.get("strung") == "True" and kn.get("same") == "True" and (num(kn, "aerial") or 0) >= 1 and listed
            and kc.get("same") == "False")
    row("POLE_SPAN_CARRIES_LIQUID", "PASS" if good else "FAIL",
        {"link": tl, "net": tn, "tankBInStore": listed, "afterCut": tc})


def dig_pipe(ctx):
    """PROVE a pipe between two tanks; one square dug to 4 m under it (the Deepen commit); dug again (deeper).
    EXPECT before same=True; after: same=False, no pipe on the square, LinesBroken +1 and CommitsThatBroke +1; the second dig
    adds nothing. LIES: a net that was never joined splits trivially (same=True before is a SITE precondition); counters are
    statics (deltas only)."""
    P, xz, row, lproof = _c(ctx, "P", "xz", "row", "lproof")
    ta, tb = P(-3, 36), P(7, 36)
    ctx["build"]("RM_LiquidTank:%d,%d" % ta, *["RM_UniversalPipe:%d,%d" % P(x, 36) for x in range(-1, 7)] +
                 ["RM_LiquidTank:%d,%d" % tb])
    ctx["ticks"](2)
    k0, t0 = lproof("ProofNet", "%s;%s" % (xz(ta), xz(tb)))
    V.require(k0.get("same") == "True", "the two tanks share one net before the dig", t0)
    c0 = ctx["counters"]()
    ctx["dig"](P(3, 36))
    ctx["ticks"](2)
    k1, t1 = lproof("ProofNet", "%s;%s" % (xz(ta), xz(tb)))
    left = ctx["things"]("RM_UniversalPipe", P(3, 36))
    c1 = ctx["counters"]()
    ctx["dig"](P(3, 36), 2)
    ctx["ticks"](2)
    c2 = ctx["counters"]()
    d = ctx["delta"]
    good = (k1.get("same") == "False" and left == 0 and d(c0, c1, "broken") == 1 and d(c0, c1, "commits") == 1
            and d(c1, c2, "broken") == 0)
    row("DIG_UNDER_PIPE_SPLITS_NET", "PASS" if good else "FAIL",
        {"before": t0, "after": t1, "pipeLeft": left, "broken": d(c0, c1, "broken"), "commits": d(c0, c1, "commits"),
         "secondDig": d(c1, c2, "broken")})


def cord_deck_lamp(ctx):
    """PROVE a battery on one bank, a power cord on every square across a timber deck, a standing lamp on the far bank.
    EXPECT the lamp powered within 300 ticks; the cord on the deck reads 'Lying on a bridge deck.' (P9). LIES: a lamp lit by
    some other source (none in the plot; the net index of lamp and battery-side cord must match); a battery that never charged
    (SITE: charge read back by battery_set)."""
    P, xz, row, lproof = _c(ctx, "P", "xz", "row", "lproof")
    ctx["trench"](1, 4, 46, 50)
    kb, tb = ctx["sproof"]("ProofBuild", "%s;%s;timber;god" % (xz(P(0, 48)), xz(P(5, 48))))
    V.require(kb.get("ok") == "True", "timber bridge built", tb)
    ks, ts = lproof("ProofSurface", xz(P(2, 48)))
    V.require(ks.get("s") == "Deck", "the square reads as a deck", ts)
    bat, lamp = ctx["power_line"](48)
    on, waited = ctx["poll"](lambda: ctx["lamp_on"](lamp), 300)
    kc, tc = lproof("ProofCord", xz(P(2, 48)))
    kn, tn = lproof("ProofCord", xz(P(-3, 48)))
    kp, tp = lproof("ProofPower", xz(lamp))
    good = bool(on) and kc.get("line") == "Lying_on_a_bridge_deck." and kp.get("net") == kn.get("net") != "-1"
    row("CORD_DECK_LAMP_LIT", "PASS" if good else "FAIL",
        {"lampOn": bool(on), "poweredAfterTicks": waited, "deckCord": tc, "lamp": tp, "nearCord": tn})


def leaf_lamp(ctx):
    """PROVE the same power line across a timber drawbridge leaf; lamp lit; the leaf raised (ProofDevSet instant: staging, the
    production Apply/NotifyToggled runs); then lowered.
    EXPECT lit -> dark within 60 ticks of the raise, the cord on the leaf cut=True with the P9 'Disconnected:' line -> lit
    again within 300 ticks of the lower. LIES: a lamp that never lit is 'dark' trivially (lit before is a SITE precondition);
    a raise that did not happen (ProofDevSet refused) leaves it lit and reads FAIL only if the leaf really rose (LEAF
    progress read back)."""
    P, xz, row, lproof, dproof = _c(ctx, "P", "xz", "row", "lproof", "dproof")
    ctx["trench"](1, 4, 58, 62)
    kd, td = dproof("ProofMakeDrawbridge", "%s;%s;timber;A;winch" % (xz(P(0, 60)), xz(P(5, 60))))
    V.require(kd.get("ok") == "True", "drawbridge built", td)
    bat, lamp = ctx["power_line"](60, battery_dx=-5)
    lit0, w0 = ctx["poll"](lambda: ctx["lamp_on"](lamp), 300)
    V.require(lit0, "the lamp lit across the lowered leaf first", w0)
    dproof("ProofDevSet", "%s;raise;instant" % xz(P(2, 60)))
    kl, tl = dproof("ProofLeaf", xz(P(2, 60)))
    V.require(num(kl, "progress", 0) > 0, "the leaf rose", tl)
    dark, w1 = ctx["poll"](lambda: not ctx["lamp_on"](lamp), 60)
    kc, tc = lproof("ProofCord", xz(P(2, 60)))
    dproof("ProofDevSet", "%s;lower;instant" % xz(P(2, 60)))
    lit1, w2 = ctx["poll"](lambda: ctx["lamp_on"](lamp), 300)
    good = bool(dark) and kc.get("cut") == "True" and str(kc.get("line", "")).startswith("Disconnected:") and bool(lit1)
    row("LEAF_RAISED_LAMP_DARK", "PASS" if good else "FAIL",
        {"litFirstAfter": w0, "darkAfter": w1 if dark else None, "raisedCord": tc, "litAgainAfter": w2 if lit1 else None,
         "leaf": tl})


def collapse_cord(ctx):
    """PROVE a powered cord across a timber deck (lamp lit); the span collapsed (RM_SuspensionProofs.ProofFell, the production
    CollapseSpan); a colonist spawned on a fallen square; 60 ticks; then 300 more.
    EXPECT CordsDropped +>=4 (the deck squares' cords), LiveFalls +1 exactly and still +1 after 300 ticks (the net split ONCE),
    LiveHalves +>=1, GSS shocks +>=1 and the colonist carries RM_FallenWireShock; the lamp dark. LIES: a lamp never lit means
    the cord was dead before (SITE); GSS's fallenWireShock switched off shocks nobody (SITE: read first); a colonist the spawn
    put off the fallen squares (a wreck there) is never in contact (SITE, never a mod FAIL)."""
    B, P, xz, row, lproof = _c(ctx, "B", "P", "xz", "row", "lproof")
    ctx["trench"](1, 4, 70, 74)
    kb, tb = ctx["sproof"]("ProofBuild", "%s;%s;timber;god" % (xz(P(0, 72)), xz(P(5, 72))))
    V.require(kb.get("ok") == "True", "timber bridge built", tb)
    bat, lamp = ctx["power_line"](72)
    lit, w0 = ctx["poll"](lambda: ctx["lamp_on"](lamp), 300)
    V.require(lit, "the cord was live (lamp lit) before the collapse", w0)
    gs = B.call("jawa/mod_settings_field", typeName=GSS_AERIAL, action="get", field="fallenWireShock") or {}
    V.require(str(gs.get("value")) == "True", "Gimme Some Slack's fallen-wire shock is on", gs)
    c0 = ctx["counters"]()
    ctx["sproof"]("ProofFell", xz(P(2, 72)))
    ctx["ticks"](5)
    # FALLEN_CORD_BUILD_RUBBLE_IS_NO_SHIELD (owner card 2026-10-21: "A collapsed pole is not a solid barrier by any means."):
    # a square whose cord fell with the deck gets walkable rubble, never the impassable RM_SuspensionWreck, so the live cord
    # lies on top. The wreck is NOT cleared here: a wreck on a cord square is the MOD defect this row exists to catch. The
    # victim is still drafted so he holds the square through GSS's 20-tick checks (an undrafted spawn wanders).
    wrecks = [ctx["things"]("RM_SuspensionWreck", P(x, 72)) for x in range(1, 5)]
    if any(wrecks):
        row("COLLAPSE_CORD_SHOCKS_ONCE", "FAIL", {"wrecksOnCordSquares": wrecks,
                                                  "why": "an impassable wreck shields the fallen cord (MOD)"})
        return
    victim = ctx["spawn"](P(2, 72))
    B.call("jawa/set_draft", pawnId=victim, drafted=True)
    ps = ctx["pawns"]()
    vat = ((ps.get(victim) or {}).get("x"), (ps.get(victim) or {}).get("z"))
    V.require(vat[1] == P(0, 72)[1] and P(1, 0)[0] <= (vat[0] or -9999) <= P(4, 0)[0], "the colonist stands on a fallen square", vat)
    ctx["ticks"](60)                    # three GSS 20-tick checks while he holds the square
    c1 = ctx["counters"]()
    hed = [str(h.get("def") or h) for h in (((ctx["pawns"]().get(victim) or {}).get("health") or {}).get("hediffs") or [])]
    dark = not ctx["lamp_on"](lamp)
    ctx["ticks"](300)
    c2 = ctx["counters"]()
    d = ctx["delta"]
    good = ((d(c0, c1, "cordsDropped") or 0) >= 4 and d(c0, c1, "liveFalls") == 1 and d(c0, c2, "liveFalls") == 1
            and (d(c0, c1, "liveHalves") or 0) >= 1 and (d(c0, c1, "shocks") or 0) >= 1 and SHOCK_HEDIFF in hed and dark)
    row("COLLAPSE_CORD_SHOCKS_ONCE", "PASS" if good else "FAIL",
        {"cordsDropped": d(c0, c1, "cordsDropped"), "liveFalls60": d(c0, c1, "liveFalls"), "liveFalls360": d(c0, c2, "liveFalls"),
         "liveHalves": d(c0, c1, "liveHalves"), "shocks": d(c0, c1, "shocks"), "victimAt": vat, "hediffs": hed, "lampDark": dark})




def ladder_drain(ctx):
    """PROVE proof_hose's pump plot (pump, battery, reel coupled to the pump, tank); a 3x3 4 m pit half filled; a ladder on its
    west wall; the hose laid to the pit floor (down the ladder); its free end set Intake (the gizmo's write); --drain-ticks;
    then the ladder raised (RM_PromotionProofs.ProofLadder) and 300 ticks (past one 250-tick corridor check).
    EXPECT the lay goes down >= 1 ladder; pit water falls and the tank gains; after the raise the hose is still laid, its
    geometry unchanged, not cut. LIES: a pump that never powered moves nothing (SITE: proof_hose._powered); water that left by
    evaporation or seepage is not the hose (the tank's gain is part of the bar); a hose that re-laid round a new obstacle reads
    laid=True but geom moved (geometry is the bar for 'stays')."""
    B, P, xz, row, lproof = _c(ctx, "B", "P", "xz", "row", "lproof")
    # SITE fix 2026-10-21 (LADDER_HOSE_DIAGNOSE_SIPS_NOTHING): the tank at (0,87) touched the reel, and HosePortRule ranks a
    # tank above a pump, so the reel coupled to the TANK; the pump was on no network with the Intake end and the reel read
    # "Intake needs a working pump on this network" (moved 0 in 1500 ticks). The tank now touches the PUMP (its own store),
    # never the reel, and the coupling is read back before the row may score.
    pump, bat, reel, tank = P(0, 84), P(3, 83), P(0, 85), P(0, 82)
    for x in range(8, 11):
        for z in range(84, 87):
            ctx["dig"](P(x, z))
            ctx["dig"](P(x, z), 0, 4)
    # the reel turns since a98046cbe9 (REEL_OUTLET_DECIDE_ALWAYS_GOES_WEST) and a bare op builds it NORTH: built West, one square
    # east, so the 2x2 keeps the footprint and the west outlet this row was proven with
    ctx["build"]("RM_LiquidPump:%d,%d" % pump, "Battery:%d,%d" % bat, V.reel_west(reel),
                 "RM_LiquidTank:%d,%d" % tank,
                 "RM_Ladder:%d,%d,3" % P(8, 85))
    ctx["ticks"](2)
    lt = B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % bat, limit=2) or {}
    bid = ((lt.get("things") or [{}])[0]).get("id")
    if bid is not None:
        B.call("jawa/battery_set", thing=bid, mode="setPct", value=1.0)
    ladder = B.call("jawa/static_call", type=PROMO, method="ProofLadder", args="%d,%d,read" % P(8, 85), _answer=True) or {}
    V.require(ladder.get("success") is True, "the ladder is on the pit floor", ladder)
    ly = ctx["lay"](reel, P(9, 85))
    kh0, th0 = ctx["hose"](reel)
    rl = B.call("jawa/list_things", defName="RM_HoseReel", rect="%d,%d,2,1" % reel, limit=1) or {}
    rid = ((rl.get("things") or [{}])[0]).get("id")
    ins = (B.call("jawa/inspect_string", thingIds=str(rid)) or {}) if rid else {}
    lines = [ln for t in (ins.get("things") or []) for ln in (t.get("inspect") or [])]
    V.require(any(ln.startswith("Connected to liquid pump") for ln in lines), "the reel is coupled to the pump", lines, cls="SITE")
    lproof("ProofHoseRole", "%s;Intake" % xz(reel))
    powered, pw = ctx["poll"](lambda: B.hp("pump:%d,%d" % pump).get("powered") is True, 400)
    V.require(powered, "the pump powered", pw)
    rect = "%d,%d,3,3" % P(8, 84)
    kw0, tw0 = lproof("ProofPitWater", rect)
    u0 = B.hp("tank:%d,%d" % tank).get("units")
    ctx["ticks"](ctx["a"].drain_ticks)
    kw1, tw1 = lproof("ProofPitWater", rect)
    u1 = B.hp("tank:%d,%d" % tank).get("units")
    drained = (num(kw0, "dl") or 0) > (num(kw1, "dl") or 0) and isinstance(u0, int) and isinstance(u1, int) and u1 > u0
    up = B.call("jawa/static_call", type=PROMO, method="ProofLadder", args="%d,%d,raise" % P(8, 85)) or {}
    ctx["ticks"](300)
    kh1, th1 = ctx["hose"](reel)
    stays = kh1.get("laid") == "True" and kh1.get("geom") == kh0.get("geom") and kh1.get("cut") == "False"
    good = kh0.get("laid") == "True" and (num(kh0, "ladders") or 0) >= 1 and drained and stays
    row("LADDER_HOSE_DRAINS_RAISED_STAYS", "PASS" if good else "FAIL",
        {"lay": ly, "hoseBefore": th0, "pumpPoweredAfterTicks": pw, "pit": [tw0, tw1], "tank": [u0, u1], "raise": up.get("result"),
         "hoseAfterRaise": th1})


def dig_reroute(ctx):
    """PROVE a hose laid 16 east over open ground; a 3x5 pit dug 2 m across its line; 300 ticks (past one 250-tick corridor
    check).
    EXPECT still laid, 0 lay cells on another band (round the pit), geometry changed. LIES: a pit dug off the hose's line
    changes nothing (the first lay must cross the pit's squares: SITE); a hose reeled in is not 're-routed' (laid is the bar)."""
    P, xz, row = _c(ctx, "P", "xz", "row")
    reel = P(0, 100)
    ctx["build"](V.reel_west(reel))
    ctx["ticks"](2)
    ly = ctx["lay"](reel, P(16, 100))
    kh0, th0 = ctx["hose"](reel)
    V.require(kh0.get("laid") == "True", "the hose was laid", [ly, th0])
    ctx["trench"](7, 9, 98, 102, 4)
    kx, tx = ctx["hose"](reel)          # read at once: the dig must have landed on the lay (before the 250-tick check)
    V.require((num(kx, "dug") or 0) > 0 or kx.get("geom") != kh0.get("geom"), "the pit is on the hose's line", tx)
    ctx["ticks"](300)
    kh1, th1 = ctx["hose"](reel)
    good = kh1.get("laid") == "True" and num(kh1, "dug") == 0 and kh1.get("geom") != kh0.get("geom")
    row("DIG_REROUTES_LAID_HOSE", "PASS" if good else "FAIL", {"lay": ly, "before": th0, "dugUnder": tx, "after": th1})


def raw_static(B, ty, method, arg):
    """An unguarded read for polling (a REFUSED reply while the load settles is not a fault)."""
    try:
        r = B.call("jawa/static_call", type=ty, method=method, args=arg, _answer=True) or {}
    except Exception as e:      # noqa: BLE001
        return "ERR %s" % e
    return str(r.get("result") or r.get("message") or r.get("error") or "")


def _trap(ctx, pid):
    r = ctx["B"].call("jawa/static_call", type=NPROOF, method="ProofTrap", args=pid) or {}
    txt = str(r.get("result") or r.get("message") or r.get("error") or "")
    V.require(r.get("success") is True and txt.startswith("TRAP"), "ProofTrap answered", txt[:200], cls="HARNESS")
    return parse(txt), txt


def cover_break(ctx):
    """FLOWWORKS_PITCOVER_FIX_BURNS_PAWN_UNHARMED. PROVE a 3x3 4 m pit with plank-lattice covers across its middle row; a
    drafted colonist standing on the middle cover; the cover destroyed by damage (KillFinalize, the way fire or a raid breaks
    it). EXPECT the trap counts one descent for that colonist on that square and holds him (he fell into the pit). LIES: a
    colonist the spawn put off the cover never rode it (SITE); a cover that never stood reads Excavated (SITE); a cover the
    damage did not destroy is no break (SITE)."""
    B, P, xz, row, lproof = _c(ctx, "B", "P", "xz", "row", "lproof")
    ctx["trench"](1, 3, 94, 96)
    ctx["build"](*["%s:%d,%d" % ((COVER_DEF,) + P(x, 95)) for x in range(1, 4)])
    ks, ts = lproof("ProofSurface", xz(P(2, 95)))
    V.require(ks.get("s") == "Cover", "the middle square reads as an intact pit cover", ts)
    victim = ctx["spawn"](P(2, 95))
    B.call("jawa/set_draft", pawnId=victim, drafted=True)
    ctx["ticks"](10)
    k0, t0 = _trap(ctx, victim)
    V.require(k0.get("pos") == xz(P(2, 95)) and k0.get("held") == "False", "the colonist stands on the cover, not held", t0)
    lt = B.call("jawa/list_things", defName=COVER_DEF, rect="%d,%d,1,1" % P(2, 95), limit=1) or {}
    cid = ((lt.get("things") or [{}])[0]).get("id")
    V.require(cid is not None, "the cover under him is listed", lt)
    dmg = B.call("jawa/damage", thingId=cid, damageDef="Blunt", amount=5000) or {}
    V.require(ctx["things"](COVER_DEF, P(2, 95)) == 0, "the damage destroyed the cover", dmg, cls="SITE")
    ctx["ticks"](5)
    k1, t1 = _trap(ctx, victim)
    fell = (num(k1, "descents") or 0) - (num(k0, "descents") or 0)
    good = fell >= 1 and k1.get("held") == "True" and str(victim).replace("Thing_", "") in str(k1.get("last"))
    row("COVER_BREAK_DROPS_RIDER", "PASS" if good else "FAIL", {"before": t0, "after": t1, "descents": fell, "damage": dmg})


def pitfall_saved(ctx):
    """FLOWWORKS_PITFALL_FIX_HISTORY_NOT_SAVED. PROVE a 3x3 4 m pit; a drafted colonist on its west lip, ticked so the detector
    remembers the lip; then, PAUSED, moved into the pit with no arrival handling (NorthstarProofs.ProofShove: a forced
    displacement the detector has not judged yet); saved; loaded; ticked. EXPECT the loaded detector still remembers the lip
    (lastCell scribed) and the first ticks count the forced arrival as a fall for that colonist. Before the fix lastCell was
    not saved: the arrival was never judged (no fall). LIES: a lip cell the detector never recorded proves nothing (SITE);
    a save or load the bridge refused is UNMEASURED. Runs LAST: the load replaces the map every later row would use."""
    B, P, xz, row = _c(ctx, "B", "P", "xz", "row")
    ctx["trench"](1, 3, 101, 103)
    lip, hole = P(0, 102), P(2, 102)
    victim = ctx["spawn"](lip)
    B.call("jawa/set_draft", pawnId=victim, drafted=True)
    ctx["ticks"](10)
    k0, t0 = _trap(ctx, victim)
    V.require(k0.get("lastCell") == xz(lip) and k0.get("pos") == xz(lip), "the detector remembers him on the lip", t0)
    sh = B.call("jawa/static_call", type=NPROOF, method="ProofShove", args="%s;%s" % (victim, xz(hole))) or {}
    k1, t1 = _trap(ctx, victim)
    V.require(k1.get("pos") == xz(hole) and k1.get("lastCell") == xz(lip), "moved into the pit, not judged yet", [sh, t1])
    if ctx["a"].mock:
        sv, ld = ctx["B"].call("rimworld/save_game", saveName="x"), ctx["B"].call("rimworld/load_game_ready", saveName="x")
    else:
        name = "RM_LINES_PITFALL_%s" % time.strftime("%Y%m%dT%H%M%S")
        sv = B.call("rimworld/save_game", saveName=name) or {}
        V.require(sv.get("success") is not False, "saved", sv, cls="HARNESS")
        ld = B.call("rimworld/load_game_ready", saveName=name, timeoutMs=280000) or {}
        V.require(ld.get("success") is not False, "loaded", str(ld)[:300], cls="HARNESS")
        V.require(V._wait_playing(B, leave_s=0)[0], "playing after the load", None, cls="HARNESS")
        for _ in range(60):             # load_game_ready can answer while the load's long event still runs (live 2026-10-22)
            r = raw_static(B, NPROOF, "ProofTrap", victim)
            if r.startswith("TRAP"):
                break
            time.sleep(2)
    k2, t2 = _trap(ctx, victim)
    ctx["ticks"](10)
    k3, t3 = _trap(ctx, victim)
    # DescentCount is not saved: the loaded state counts from 0, so any descent after the load naming him on the hole square
    # is the saved arrival judged (a tick may already have passed inside the load, so lastCell after it may read the hole).
    good = ((num(k3, "descents") or 0) >= 1 and k3.get("held") == "True"
            and str(k3.get("last", "")).startswith(str(victim).replace("Thing_", "") + "@" + xz(hole)))
    row("PITFALL_SAVED_ARRIVAL_FALLS", "PASS" if good else "FAIL",
        {"onLip": t0, "shoved": t1, "afterLoad": t2, "afterTicks": t3})


SCENES = {"ROPE_DECK_RIGID_REFUSED_FLEX_OK": rope_deck, "COVER_CARRIES_NO_HOSE": cover_no_hose,
          "POLE_SPAN_CARRIES_LIQUID": pole_span, "DIG_UNDER_PIPE_SPLITS_NET": dig_pipe, "CORD_DECK_LAMP_LIT": cord_deck_lamp,
          "LEAF_RAISED_LAMP_DARK": leaf_lamp, "COLLAPSE_CORD_SHOCKS_ONCE": collapse_cord,
          "LADDER_HOSE_DRAINS_RAISED_STAYS": ladder_drain, "DIG_REROUTES_LAID_HOSE": dig_reroute,
          "COVER_BREAK_DROPS_RIDER": cover_break, "PITFALL_SAVED_ARRIVAL_FALLS": pitfall_saved}


# ====================================================================== offline stand-in
class FakeBridge(object):
    """A small line world model answering in the shapes the live tools and the OWED proofs are specified to: dug squares,
    decks, covers, leaves, pipes, tanks, poles and spans, cords, batteries and lamps, hose reels with a straight-line lay,
    pawns and the counters. It knows nothing about the game; a mock verdict proves the script's control flow and its
    MOD/SITE/HARNESS split only. `faults` inject one wrong behaviour each:
      no_proofs          RM_LineProofs is not loaded (an old deploy): every row UNMEASURED/HARNESS, none FAIL
      noclock            step_game_ticks refuses: every row that waits on the clock is UNMEASURED/HARNESS
      rope_is_timber     the drag made a timber deck (the site is not the scene)  -> ROPE_DECK... UNMEASURED/SITE
      pipe_on_rope       MOD: a rigid pipe is accepted on a rope deck            -> ROPE_DECK... FAIL
      hose_avoids_deck   MOD: the hose router refuses a deck (goes round)        -> ROPE_DECK... FAIL
      no_cover           a cover never stood (the site is not the scene)          -> COVER_CARRIES_NO_HOSE UNMEASURED/SITE
      cover_open         MOD: the pre-phase-7 gap: a hose lies over a cover      -> COVER_CARRIES_NO_HOSE FAIL
      span_no_join       MOD: a strung pipe span does not join the liquid net    -> POLE_SPAN_CARRIES_LIQUID FAIL
      dig_no_break       MOD: a committed dig leaves the pipe                    -> DIG_UNDER_PIPE_SPLITS_NET FAIL
      dig_breaks_twice   MOD: a second dig counts a second break                 -> DIG_UNDER_PIPE_SPLITS_NET FAIL
      deck_cord_dead     MOD: a cord on a deck carries no power                  -> CORD_DECK_LAMP_LIT FAIL
      leaf_no_cut        MOD: a raised leaf leaves its cord carrying             -> LEAF_RAISED_LAMP_DARK FAIL
      leaf_stays_dark    MOD: the lowered leaf's cord never rejoins              -> LEAF_RAISED_LAMP_DARK FAIL
      double_split       MOD: the fallen cord's net is split twice               -> COLLAPSE_CORD_SHOCKS_ONCE FAIL
      no_shock           MOD: a live fallen cord shocks nobody                   -> COLLAPSE_CORD_SHOCKS_ONCE FAIL
      shock_off          GSS's fallenWireShock is off (SITE)                     -> COLLAPSE_CORD_SHOCKS_ONCE UNMEASURED/SITE
      wreck_blocks       the spawn lands off the fallen squares (SITE)           -> COLLAPSE_CORD_SHOCKS_ONCE UNMEASURED/SITE
      wreck_shields      MOD: an impassable wreck lands on a fallen cord square  -> COLLAPSE_CORD_SHOCKS_ONCE FAIL
      cover_no_fall      MOD: a destroyed cover leaves its rider unharmed        -> COVER_BREAK_DROPS_RIDER FAIL
      history_lost       MOD: lastCell is not saved (the pre-fix gap)            -> PITFALL_SAVED_ARRIVAL_FALLS FAIL
      no_drain           MOD: the Intake end moves nothing                       -> LADDER_HOSE_DRAINS_RAISED_STAYS FAIL
      raise_cuts         MOD: raising the ladder reels the hose in               -> LADDER_HOSE_DRAINS_RAISED_STAYS FAIL
      no_power           the pump never powers (SITE)                            -> LADDER_HOSE_DRAINS_RAISED_STAYS UNMEASURED/SITE
      no_reroute         MOD: a dig under a laid hose changes nothing            -> DIG_REROUTES_LAID_HOSE FAIL
      reroute_retracts   MOD: the hose is reeled in though a way round exists    -> DIG_REROUTES_LAID_HOSE FAIL"""
    FAULTS = ("no_proofs", "noclock", "rope_is_timber", "pipe_on_rope", "hose_avoids_deck", "no_cover", "cover_open",
              "span_no_join", "dig_no_break", "dig_breaks_twice", "deck_cord_dead", "leaf_no_cut", "leaf_stays_dark",
              "double_split", "no_shock", "shock_off", "wreck_blocks", "wreck_shields", "cover_no_fall", "history_lost", "no_drain", "raise_cuts", "no_power", "no_reroute",
              "reroute_retracts")

    def __init__(self, faults=()):
        self.f = set(faults)
        self.nid = 1000
        self.dug = {}          # cell -> notches
        self.surf = {}         # cell -> Deck | RopeDeck | Cover | DrawbridgeLeaf
        self.raised = set()    # leaf squares raised
        self.things = {}       # cell -> [defName]
        self.spans = set()     # frozenset(pole cells)
        self.water = {}        # cell -> dl
        self.tankunits = {}    # tank root -> units
        self.reels = {}        # root -> dict(laid, cells, geom, role, target, retract)
        self.pawns = {}
        self.cnt = {"broken": 0, "commits": 0, "cordsDropped": 0, "hosesCut": 0, "tore": 0, "liveFalls": 0, "liveHalves": 0,
                    "leafReconnects": 0, "netBumps": 0, "shocks": 0}
        self.fallen = set()    # fallen live squares
        self.last = {}         # pawn -> detector's lastCell (trap model)
        self.descents = []     # pawn ids that fell
        self.split_pending = False
        self.ladders = {}      # cell -> raised
        self.batteries = set()

    # ---- the world
    def _defs(self, c):
        return self.things.get(c, [])

    def _has(self, c, d):
        return d in self._defs(c)

    def _surface(self, c):
        if c in self.surf and c not in self.raised:
            return self.surf[c]
        return "Excavated" if self.dug.get(c) else "SolidGround"

    def _band(self, c):
        return self.dug.get(c, 0) if self._surface(c) in ("Excavated",) else 0

    def _closed(self, c):
        return self._surface(c) == "Cover" and "cover_open" not in self.f

    def _tank_cells(self, root):
        return [(root[0] + dx, root[1] + dz) for dx in (0, 1) for dz in (0, 1)]

    def _tanks(self):
        return [c for c, ds in self.things.items() if "RM_LiquidTank" in ds]

    def _net_nodes(self, start):
        """Liquid-net BFS: pipes and tank cells join cardinally; a pole joins 8-way pipes; a strung span joins its poles."""
        seen, todo = set(), list(self._tank_cells(start))
        while todo:
            c = todo.pop()
            if c in seen:
                continue
            seen.add(c)
            if not (self._has(c, "RM_UniversalPipe") or self._has(c, "RM_PipePole") or any(c in self._tank_cells(t) for t in self._tanks())):
                continue
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                n = (c[0] + dx, c[1] + dz)
                diag = dx != 0 and dz != 0
                if diag and not (self._has(c, "RM_PipePole") or self._has(n, "RM_PipePole")):
                    continue
                todo.append(n)
            if self._has(c, "RM_PipePole") and "span_no_join" not in self.f:
                for s in self.spans:
                    if c in s:
                        todo.extend(x for x in s if x != c)
        return seen

    def _cords_live(self, battery, lamp):
        z = lamp[1]
        for x in range(battery[0] + 1, lamp[0]):
            c = (x, z)
            if not self._has(c, "RM_PowerCord"):
                return False
            if c in self.raised and "leaf_no_cut" not in self.f:
                return False
            if getattr(self, "_stuck_dark", None) and c in self._stuck_dark:
                return False
            if self._surface(c) == "Deck" and "deck_cord_dead" in self.f:
                return False
        return True

    def _lamp_on(self, lamp):
        return any(b[1] == lamp[1] and self._cords_live(b, lamp) for b in self.batteries)

    def _line(self, reel, to):
        x0 = reel[0] + 2
        return [(x, to[1]) for x in range(min(x0, to[0]), max(x0, to[0]) + 1)]

    def _plan(self, reel, to):
        """The mock router: straight along the target row; a closed square (cover) or a band change without a ladder is
        detoured round (dropped from the lay); a deck is crossed unless hose_avoids_deck."""
        cells, ladders = [], 0
        for c in self._line(reel, to):
            s = self._surface(c)
            if self._closed(c) or (s in ("Deck", "RopeDeck") and "hose_avoids_deck" in self.f):
                continue
            if self._band(c):
                if any(l[1] == to[1] for l in self.ladders) and self._band(to):
                    ladders = 1
                else:
                    continue
            cells.append(c)
        return cells, ladders

    # ---- the bridge
    def hp(self, cmd, wait_s=20.0):
        verb, _, arg = cmd.partition(":")
        if verb == "lay":
            rx, rz, x, z = (int(v) for v in arg.split(","))
            cells, ladders = self._plan((rx, rz), (x, z))
            self.reels[(rx, rz)] = dict(laid=True, cells=cells, geom=1, role="Capped", target=(x, z), retract=None, ladders=ladders)
            return {"success": True, "reason": None, "layOk": True}
        if verb in ("filltank", "tank", "net", "pump"):
            cell = tuple(int(v) for v in arg.split("=")[0].split(","))
            if verb == "filltank":
                self.tankunits[cell] = int(arg.split("=")[1].split(",")[1])
                return {"success": True, "units": self.tankunits[cell]}
            if verb == "tank":
                return {"success": True, "units": self.tankunits.get(cell, 0)}
            if verb == "pump":
                return {"success": True, "powered": "no_power" not in self.f and bool(self.batteries)}
            nodes = self._net_nodes(cell)
            return {"success": True, "tanks": [{"tank": list(t)} for t in self._tanks() if t in nodes]}
        return {"success": True}

    def call(self, tool, **kw):
        if tool == "jawa/static_call":
            ty, m, arg = kw.get("type"), kw.get("method"), kw.get("args") or ""
            if ty == LPROOF and "no_proofs" in self.f:
                return {"success": False, "error": "Type not found: " + ty}
            return {"success": True, "result": self.static(ty, m, arg)}
        if tool == "rimworld/step_game_ticks":
            if "noclock" in self.f:
                return {"success": False, "message": "clock refused"}
            self._tick(int(kw.get("ticks") or 0))
            return {"success": True}
        if tool == "jawa/flowworks_excavation_drive":
            c = (kw.get("x"), kw.get("z"))
            n = int(kw.get("deepenLevels") or 0)
            if kw.get("setFill", -1) not in (-1, None):
                self.water[c] = int(kw["setFill"]) * 500
            if n > 0:
                self.dug[c] = self.dug.get(c, 0) + n
                if self._has(c, "RM_UniversalPipe") and "dig_no_break" not in self.f:
                    self.things[c].remove("RM_UniversalPipe")
                    self.cnt["broken"] += 1
                    self.cnt["commits"] += 1
                elif "dig_breaks_twice" in self.f and c in getattr(self, "_broke", set()):
                    self.cnt["broken"] += 1
                self._broke = getattr(self, "_broke", set()) | {c}
            return {"success": True}
        if tool == "jawa/build_batch":
            ops = [o for o in str(kw.get("ops") or "").split(";") if o]
            survived = 0
            for op in ops:
                d, _, rest = op.partition(":")
                p = rest.split(",")
                c = (int(p[0]), int(p[1]))
                if d.startswith("RM_PitCover"):
                    if "no_cover" in self.f or not self.dug.get(c):
                        continue
                    self.surf[c] = "Cover"
                if d == "Battery":
                    self.batteries.add(c)
                if d == "RM_Ladder":
                    self.ladders[c] = False
                if d == "RM_HoseReel":
                    # built West (rot 3) one square east of its staged cell: the probe names the footprint's west square
                    rc = (c[0] - 1, c[1]) if len(p) > 2 and int(p[2]) % 4 == 3 else c
                    self.reels.setdefault(rc, dict(laid=False, cells=[], geom=0, role="Capped", target=None, retract=None, ladders=0))
                self.things.setdefault(c, []).append(d)
                survived += 1
            return {"success": True, "survived": survived}
        if tool == "jawa/list_things":
            x, z = (int(v) for v in str(kw.get("rect")).split(",")[:2])
            d = kw.get("defName")
            w = int(str(kw.get("rect")).split(",")[2]) if len(str(kw.get("rect")).split(",")) > 2 else 1
            cells = [(x, z), (x, z + 1)] if d == "Battery" else [(x + i, z) for i in range(max(1, w))]   # a battery is 1x2
            got = [{"id": "%s%d%d" % (d, x, z)} for c in cells if self._has(c, d)]
            return {"success": True, "things": got[:1]}
        if tool == "jawa/battery_set":
            return {"success": True}
        if tool == "jawa/inspect_string":
            return {"success": True, "things": [{"id": kw.get("thingIds"), "inspect": ["Connected to liquid pump (pump)."]}]}
        if tool == "jawa/destroy_batch":
            x, z = (int(v) for v in str(kw.get("rects")).split(",")[:2])
            c = (x, z)
            n = len(self._defs(c))
            self.things[c] = []
            self.spans = {s for s in self.spans if c not in s}
            return {"success": True, "destroyed": n}
        if tool == "jawa/spawn_pawn":
            self.nid += 1
            pid = "Human%d" % self.nid
            x, z = kw.get("x"), kw.get("z")
            if "wreck_blocks" in self.f and (x, z) in self.fallen:
                x = x - 3
            self.pawns[pid] = dict(x=x, z=z, hediffs=[])
            return {"success": True, "pawns": [{"id": pid}]}
        if tool == "jawa/damage":
            for c, ds in self.things.items():
                for d in list(ds):
                    if "%s%d%d" % (d, c[0], c[1]) == kw.get("thingId"):
                        ds.remove(d)
                        self.surf.pop(c, None)
                        for pid, p in self.pawns.items():
                            if (p["x"], p["z"]) == c and "cover_no_fall" not in self.f:
                                self.descents.append(pid)
                                self.last[pid] = c
            return {"success": True}
        if tool == "rimworld/load_game_ready":
            self.descents = []          # DescentCount is not saved: the loaded state counts from 0
            if "history_lost" in self.f:
                self.last = {}
            return {"success": True}
        if tool == "jawa/list_pawns":
            return {"pawns": [dict(id=i, x=p["x"], z=p["z"], health={"hediffs": [{"def": h} for h in p["hediffs"]]})
                              for i, p in self.pawns.items()]}
        if tool == "jawa/mod_settings_field":
            if kw.get("field") == "fallenWireShock":
                return {"success": True, "value": str("shock_off" not in self.f)}
            return {"success": False, "error": "no field"}
        return {"success": True}

    def _tick(self, n):
        for pid, p in self.pawns.items():
            c = (p["x"], p["z"])
            prev = self.last.get(pid)
            if prev is not None and prev != c and self.dug.get(c) and not self.dug.get(prev):
                self.descents.append(pid)
            self.last[pid] = c
        if self.split_pending and "double_split" in self.f:
            self.cnt["liveFalls"] += 1
            self.split_pending = False
        if n >= 20 and "no_shock" not in self.f:
            for p in self.pawns.values():
                if (p["x"], p["z"]) in self.fallen and SHOCK_HEDIFF not in p["hediffs"]:
                    p["hediffs"].append(SHOCK_HEDIFF)
                    self.cnt["shocks"] += 1
        for root, r in self.reels.items():
            if not r["laid"]:
                continue
            if r["role"] == "Intake" and r["target"] in self.water and "no_drain" not in self.f and "no_power" not in self.f:
                moved = min(self.water[r["target"]], 50 * (n // 50))
                self.water[r["target"]] -= moved
                tank = (root[0], root[1] - 3)   # the tank below the pump below the reel (scene H, fixed 2026-10-21)
                self.tankunits[tank] = self.tankunits.get(tank, 0) + moved
            if any(self._band(c) for c in r["cells"]) and not r["ladders"] and n >= 250:
                if "reroute_retracts" in self.f:
                    r.update(laid=False, retract="no_route")
                elif "no_reroute" not in self.f:
                    cells, ladders = self._plan(root, r["target"])
                    r.update(cells=cells, geom=r["geom"] + 1, ladders=ladders)
            if r["ladders"] and any(self.ladders.values()) and "raise_cuts" in self.f and n >= 250:
                r.update(laid=False, retract="ladder_raised")

    def static(self, ty, m, arg):
        a = arg.split(";")
        cell = lambda s: tuple(int(v) for v in s.split(",")[:2])  # noqa: E731
        if ty == NPROOF and m == "ProofShove":
            p = self.pawns[a[0]]
            p["x"], p["z"] = cell(a[1])
            return "SHOVE at=%s" % a[1]
        if ty == NPROOF and m == "ProofTrap":
            p = self.pawns[arg]
            c = (p["x"], p["z"])
            lc = self.last.get(arg)
            held = arg in self.descents and self.dug.get(c) and not self._closed(c)
            return "TRAP descents=%d lastCell=%s pos=%d,%d held=%s last=%s" % (
                len(self.descents), "%d,%d" % lc if lc else "none", c[0], c[1], bool(held),
                ("%s@%d,%d_t=1" % ((self.descents[-1],) + c)) if self.descents else "-")
        if ty == SPROOF and m == "ProofBuild":
            (x1, z1), (x2, z2), tier = cell(a[0]), cell(a[1]), a[2]
            kind = "RopeDeck" if tier == "rope" and "rope_is_timber" not in self.f else "Deck"
            for x in range(x1 + 1, x2):
                self.surf[(x, z1)] = kind
            return "BUILD ok=True anchors=2 decks=%d blueprints=0 reason=-" % (x2 - x1 - 1)
        if ty == SPROOF and m == "ProofFell":
            x, z = cell(a[0])
            sq = [c for c, s in self.surf.items() if c[1] == z and s == "Deck"]
            cords = 0
            for c in sq:
                del self.surf[c]
                if self._has(c, "RM_PowerCord"):
                    self.things[c].remove("RM_PowerCord")
                    cords += 1
                    self.fallen.add(c)
                    if "wreck_shields" in self.f:
                        self.things[c].append("RM_SuspensionWreck")
            self.cnt["cordsDropped"] += cords
            self.cnt["tore"] += len(sq)
            if cords:
                self.cnt["liveFalls"] += 1
                self.cnt["liveHalves"] += 2
                self.split_pending = True
            return "FELL crushed=0 wrecks=%d slid=0" % len(sq)
        if ty == DPROOF:
            if m == "ProofMakeDrawbridge":
                (x1, z1), (x2, z2) = cell(a[0]), cell(a[1])
                for x in range(x1 + 1, x2):
                    self.surf[(x, z1)] = "DrawbridgeLeaf"
                self._leaf_row = z1
                return "DRAW ok=True leaves=1 tier=timber hinges=A winchAt=%d,%d firstAt=%d,%d reason=-" % (x1 - 1, z1, x1, z1)
            if m == "ProofDevSet":
                x, z = cell(a[0])
                sq = [c for c, s in self.surf.items() if c[1] == z and s == "DrawbridgeLeaf"]
                if a[1] == "raise":
                    self.raised |= set(sq)
                    self.cnt["leafReconnects"] += sum(1 for c in sq if self._has(c, "RM_PowerCord"))
                else:
                    self.raised -= set(sq)
                    if "leaf_stays_dark" in self.f:
                        self._stuck_dark = set(sq)
                return "DEVSET target=%s progress=%d" % ("raised" if a[1] == "raise" else "lowered", 240 if a[1] == "raise" else 0)
            if m == "ProofLeaf":
                c = cell(a[0])
                return "LEAF leaf=1/1 progress=%d full=240 target=x" % (240 if c in self.raised else 0)
        if ty == PROMO and m == "ProofLadder":
            p = arg.split(",")
            c = (int(p[0]), int(p[1]))
            if p[2] == "raise":
                self.ladders[c] = True
            return "LADDER x,z raised=%s" % self.ladders.get(c)
        if ty == LPROOF:
            return self.lproof(m, a, cell)
        return "OK"

    def lproof(self, m, a, cell):
        if m == "ProofLineCounters":
            return "LINES " + " ".join("%s=%d" % kv for kv in self.cnt.items())
        if m == "ProofSurface":
            c = cell(a[0])
            return "SURFACE s=%s hoseClosed=%s band=%d rules=True" % (self._surface(c), self._closed(c), self._band(c))
        if m == "ProofCanPlace":
            d, c = a[0], cell(a[1])
            kind = {"RM_UniversalPipe": "RigidPipe", "PowerConduit": "RigidConduit", "RM_PowerCord": "FlexCord"}.get(d, "none")
            s = self._surface(c)
            if s == "SolidGround":
                ok = True
            elif s in ("Deck", "RopeDeck", "DrawbridgeLeaf"):
                ok = kind == "FlexCord" or (kind == "RigidPipe" and s == "RopeDeck" and "pipe_on_rope" in self.f)
            else:
                ok = False
            return "PLACE ok=%s kind=%s surface=%s why=%s" % (ok, kind, s, "-" if ok else "refused")
        if m == "ProofNet":
            c1, c2 = cell(a[0]), cell(a[1])
            same = c2 in self._net_nodes(c1)
            aerial = 0 if "span_no_join" in self.f else len(self.spans)
            return "NET same=%s a=1 b=1 spans=%d aerial=%d fitting=0" % (same, len(self.spans), aerial)
        if m == "ProofLinkPoles":
            c1, c2 = cell(a[0]), cell(a[1])
            if not (self._has(c1, "RM_PipePole") and self._has(c2, "RM_PipePole")):
                return "REFUSED: no pipe pole"
            self.spans.add(frozenset((c1, c2)))
            return "LINK verdict=Ok strung=True spans=%d" % len(self.spans)
        if m == "ProofPower":
            c = cell(a[0])
            if self._has(c, LAMP_DEF):
                return "POWER on=%s net=%d trader=True" % (self._lamp_on(c), 3 if self._lamp_on(c) else -1)
            return "POWER on=%s net=3 trader=False" % self._has(c, "RM_PowerCord")
        if m == "ProofCord":
            c = cell(a[0])
            if not self._has(c, "RM_PowerCord"):
                return "REFUSED: no power cord"
            cut = c in self.raised and "leaf_no_cut" not in self.f
            line = ("Disconnected:_the_drawbridge_leaf_under_it_is_raised._It_rejoins_when_the_leaf_is_lowered." if cut else
                    {"Deck": "Lying_on_a_bridge_deck.", "RopeDeck": "Lying_on_a_rope_bridge_deck.",
                     "DrawbridgeLeaf": "Lying_on_a_lowered_drawbridge_leaf."}.get(self._surface(c), "-"))
            return "CORD cut=%s transmits=%s net=3 line=%s" % (cut, not cut, line)
        if m == "ProofHoseLine":
            r = self.reels.get(cell(a[0]))
            if r is None:
                return "REFUSED: no hose reel"
            cells = r["cells"] if r["laid"] else []
            deck = sum(1 for c in cells if self._surface(c) in ("Deck", "RopeDeck", "DrawbridgeLeaf"))
            cover = sum(1 for c in cells if self._surface(c) == "Cover")
            dug = sum(1 for c in cells if self._band(c))
            return "HOSELINE laid=%s ramps=0 ladders=%d cut=False cells=%d deck=%d cover=%d dug=%d geom=%d retract=%s line=-" % (
                r["laid"], r["ladders"] if r["laid"] else 0, len(cells), deck, cover, dug, r["geom"], r["retract"] or "-")
        if m == "ProofHoseRole":
            r = self.reels.get(cell(a[0]))
            if r is None:
                return "REFUSED: no hose reel"
            r["role"] = a[1]
            return "ROLE role=%s" % a[1]
        if m == "ProofPitWater":
            x, z, w, h = (int(v) for v in a[0].split(","))
            cells = [(i, j) for i in range(x, x + w) for j in range(z, z + h)]
            dl = sum(self.water.get(c, 0) for c in cells)
            return "PITWATER dl=%d wet=%d cells=%d" % (dl, sum(1 for c in cells if self.water.get(c)), len(cells))
        return "REFUSED: unknown %s" % m


if __name__ == "__main__":
    sys.exit(main())
