"""DRAWBRIDGE live proof (DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS phase 6b; design/RimMandrake/flowworks_drawbridge_design_2026-10-20.md
§Ruled design R13 and §Owner's follow-up answers; the debug_process rule: the functional script ships with the build item).

  python.exe src/RimMandrake/FlowWorks/northstar/drawbridge_proof.py [out.json] [--origin X,Z] [--fresh-map] [--only a,b]
  python3    src/RimMandrake/FlowWorks/northstar/drawbridge_proof.py --mock [--mock-faults a,b] [--only a,b]
             every path offline against FakeBridge (a small drawbridge world model, NOT the mod); every row is written SKIP
             with the verdict it would have reached kept under detail.mock (proves the script, never the game)

Run from the repo root with python.exe on the minimal list; the bridge must be held. Exit 0 = every row PASS; 1 = a FAIL;
2 = a row could not be measured. WRITTEN OFFLINE 2026-10-20 (BENCH, owner asleep): every row is OWED to its first live run.

The rows' C# proof class is RimMandrake.FlowWorks.Pits.RM_DrawbridgeProofs (FlowWorks Source/Pits/Drawbridge/
RM_DrawbridgeProofs.cs; contracts in OWED_PROOFS). A live run first asks it one question (ProofLeaf on an off-map cell);
if the loaded FlowWorks predates it, every row is written UNMEASURED/HARNESS naming it, and nothing is staged. Used as is
beside it: RM_SuspensionProofs (ProofBuild,
ProofPath, ProofPutUnder, ProofBand), jawa/static_call on RM_Drawbridges.RaisedAt / FreeHostileCount / Locked and
RM_SuperdeepTrap.IsTrapped (typed args, '|'-separated), jawa/mod_settings_field get/set on RM_Drawbridges' public static
counters and RM_DrawbridgeSettings.raiseSpeed, jawa/destroy_batch, jawa/kill_hostiles, jawa/lord_assault_spawn,
rimworld/save_game + rimworld/load_game_ready.

Owner rulings this proves (2026-10-20, by card unless quoted): raise from either side, lower only from the winch side; riders
*"tip towards hinged side, pulls enemies inside"*, overflow falls; underpass untouched; peace auto-lower, any FREE hostile
locks (trapped ones do not), lock cancels a pending auto-lower; timber by hand, steel powered, steel without power freezes;
a destroyed winch crashes its leaf down and hits what is under it (follow-up); two leaves
each tip to their own hinge; raiders use the trench rules + go for the winch + some bring planks laid exactly once.

Scenes (plot coords from --origin, default 140,140; dig by jawa/flowworks_excavation_drive, 8 notches = 4 m; hinge = bank A,
the drag's first end, unless said):
  A  z=0   timber 1-wide (0,0)-(5,0), trench 1..4          -> LOWER_ONLY_FROM_WINCH (WorkGiver asked per pawn and bank)
  B  z=6   steel  1-wide (0,6)-(7,6), trench 1..6, granite walls z=5/z=7 x=-2..9 (the deck is the only way over)
                                                           -> RAISE_PATH
  C  z=12  steel  1-wide (0,12)-(7,12), trench 1..6        -> STEEL_UNPOWERED_FREEZES
  E  z=24..26 steel 3-wide (0,24)-(5,26), trench 1..4 x 3 lanes; the hinge bank walled except ONE free square (-1,25)
                                                           -> RAISE_TIPS_RIDERS (six hostile riders)
  F  z=32  steel  1-wide (0,32)-(5,32), 4 m trench; a colonist put UNDER (2,32), a rider on (3,32)
                                                           -> RAISE_SPARES_UNDERPASS
  G  z=38  timber 1-wide (0,38)-(9,38), trench 1..8 (two leaves of 4, a winch on each bank)
                                                           -> TWO_LEAF_TIPS_OWN_HINGE
  H  z=44  steel  1-wide (0,44)-(5,44); a 2x2 4 m pit at (10..11, 44..45) to trap a hostile in
                                                           -> HOSTILE_LOCKS (raiseSpeed 0.25 for the section, restored)
  I  z=50  timber 1-wide (0,50)-(5,50), 4 m trench; leaf raised, a colonist in the hole under it, winch destroyed
                                                           -> WINCH_LOST_CRASHES
  J  z=56  a 2-square gap (1..2, 56) 4 m deep, two hostile carriers on the east bank -> RAID_PLANK
  K  island at origin+(30,70): ring at Chebyshev 5..6 dug 2 m (raid_trench_proof's scene), a steel drawbridge east across
     the ring (c+4,c)-(c+7,c) with its winch on the island, a player decoy (sandbags) outside at (c+14, c+4), the leaf
     raised, 4 assault raiders 25 east; 3,000 ticks sampled every 250 -> RAID_UP
  D  z=18  steel  1-wide (0,18)-(7,18), a drafted rider on (3,18); raiseSpeed 0.25; saved and loaded mid-raise
                                                           -> SAVE_MIDRAISE (runs LAST: the load replaces the map)

Each row: PROVE (the call) / EXPECT (the bar) / LIES (how it could pass falsely), written beside it below.

ANTI-GUESSING NOTES
- A leaf is one rigid plank (RM_DrawbridgeMath.IsRaised): the moment progress > 0 every square of it stops being ground, the
  riders tip (once per raise, tipCommitted is saved) and the squares are open hole. So a row can read "raised" 5 ticks in.
- Steel: PoweredTicksPerLeaf 120 ticks at raiseSpeed 1; timber: HandTicksPerSquare 240 per square, and moves only while a
  colonist works it (workedUntilTick). Rows that need timber up use ProofDevSet ...;instant (staging, never the claim).
- The drive steps every TickInterval = 5 ticks; ModeCheckInterval = 60 ticks between free-hostile recounts; TipReach = 3.
- The counters are process statics: a load does NOT reset them, so SAVE_MIDRAISE reads "tipped did not rise" across a load.
- A hostile spawned without a lord may not be an active threat (GenHostility.IsActiveThreatTo): hostiles that must LOCK are
  put in vanilla's LordJob_AssaultColony (jawa/lord_assault_spawn) and FreeHostileCount(fresh) must read >= 1 before a row
  leans on the lock.
- "Overflow falls": a faller lands in the hole through the ordinary descent event, so a faller's cell is a dug square of
  the leaf; a lander's cell is on the hinge bank. Positions are read from jawa/list_pawns, never inferred from counters.
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

DPROOF = "RimMandrake.FlowWorks.Pits.RM_DrawbridgeProofs"       # C#: contracts in OWED_PROOFS
SPROOF = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
DB = "RimMandrake.FlowWorks.Pits.RM_Drawbridges"
DBS = "RimMandrake.FlowWorks.Pits.RM_DrawbridgeSettings"
RAIDS = "RimMandrake.FlowWorks.Pits.RM_RaidPlanks"
RAIDW = "RimMandrake.FlowWorks.Pits.JobGiver_RM_DrawbridgeWinch"
TRAP = "RimMandrake.FlowWorks.RM_SuperdeepTrap"
DEEP = 8          # notches: 4 m
FULL_STEEL = 120  # RM_DrawbridgeMath.PoweredTicksPerLeaf at raiseSpeed 1

ROW_IDS = ["RAISE_PATH", "RAISE_TIPS_RIDERS", "RAISE_SPARES_UNDERPASS", "LOWER_ONLY_FROM_WINCH", "TWO_LEAF_TIPS_OWN_HINGE",
           "HOSTILE_LOCKS", "STEEL_UNPOWERED_FREEZES", "WINCH_LOST_CRASHES", "RAID_UP", "RAID_PLANK", "SAVE_MIDRAISE"]

# The C# the rows call (RM_DrawbridgeProofs; selftest_drawbridge_proof checks each method exists and answers its word). One
# string arg each (the RM_SuspensionProofs convention: ';' inside), one line out: a word then key=value tokens; "REFUSED: why"
# on bad args.
OWED_PROOFS = {
    "ProofMakeDrawbridge": "x1,z1;x2,z2;timber|steel;A|B;winch -> RM_SuspensionProofs.ProofBuild(god) then MakeDrawbridge(colony "
                           "bank A|B); 'winch' spawns one winch house per leaf beside its hinge anchor (LinkWinch). "
                           "'DRAW ok=True leaves=N tier=T hinges=A,B winchAt=x,z|x,z reason=-'",
    "ProofLeaf": "x,z (a deck square) -> 'LEAF leaf=k/n progress=P full=F target=raised|lowered raised=a/b frozen=T|F winch=T|F "
                 "powered=T|F hold=T|F auto=T|F pending=raise|lower|none tip=T|F hinge=A|B version=V'; 'LEAF none' off a leaf",
    "ProofDevSet": "x,z;raise|lower[;instant] -> RM_Drawbridges.DevSetTarget; 'instant' also sets progress to the target and runs "
                   "the production Tip/Apply/Fall once (staging only). 'DEVSET target=.. progress=..'",
    "ProofOrder": "x,z;raise|lower[;now] -> RM_Drawbridges.Order (the gizmo's action); 'now' also applies what the work job's "
                  "completion applies (target from pendingOrder) without a walk. 'ORDER pending=.. hold=.. locked=.. target=..'",
    "ProofWorkJob": "pawnId;x,z -> WorkGiver_Drawbridge.JobOnThing for that pawn on that leaf's winch and far anchor (forced). "
                    "'WORK job=T|F spot=winch|far|none raise=T|F why=..'",
    "ProofWinchPower": "x,z;on|off -> the leaf's winch CompPowerTrader.PowerOn forced (and held) on/off. 'POWER powered=T|F'",
    "ProofTipPreview": "x,z -> the R11 readout's tip preview for that leaf. 'PREVIEW riders=N land=L fall=F free=S'",
    "ProofGivePlank": "pawnId;lipx,z;farx,z -> give the pawn an RM_RaidPlank and start RM_LayRaidPlank over that gap (production "
                      "PlankJob). 'GIVE ok=T|F job=.. plank=thingId reserved=T|F'",
    "ProofInterrupt": "pawnId -> EndCurrentJob(InterruptForced); the carried plank is dropped. 'INT ended=T|F dropped=T|F'",
    "ProofPlankLedger": "lipx,z;farx,z -> the map's PlankLedger and laid things over that gap. 'PLEDGER crossings=N laidCells=K "
                        "reserved=R'",
}
COUNTERS = [(DB, "ToggleCount"), (DB, "RepathCount"), (DB, "HostileJobsEnded"), (DB, "TippedCount"), (DB, "PulledInside"),
            (DB, "FellCount"), (DB, "CrashCount"), (DB, "CrashHits"), (RAIDS, "PlanksGiven"), (RAIDS, "PlanksLaid"),
            (RAIDW, "WinchJobs")]


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


def pid_num(pid):
    """jawa/spawn_pawn answers 'Human41594'; the proofs and static_call take the thingIDNumber."""
    return re.sub(r"^(?:Thing_)?[A-Za-z]+_?(\d+)$", r"\1", str(pid))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="140,140")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--only", default="", help="comma list of rows: " + ",".join(ROW_IDS))
    ap.add_argument("--raid-ticks", type=int, default=3000)
    ap.add_argument("--mock", action="store_true", help="run every path against FakeBridge; rows are SKIP (mock verdict kept)")
    ap.add_argument("--mock-faults", default="", help="comma list of FakeBridge faults: " + ",".join(FakeBridge.FAULTS))
    a = ap.parse_args(argv)
    only = [x.strip().upper() for x in a.only.split(",") if x.strip()] or list(ROW_IDS)
    if set(only) - set(ROW_IDS):
        ap.error("unknown --only row(s) %s; known: %s" % (",".join(sorted(set(only) - set(ROW_IDS))), ",".join(ROW_IDS)))
    faults = [f for f in a.mock_faults.split(",") if f]
    if set(faults) - set(FakeBridge.FAULTS):
        ap.error("unknown --mock-faults %s" % ",".join(sorted(set(faults) - set(FakeBridge.FAULTS))))
    if a.mock:
        raw = FakeBridge(faults)
    else:
        import proof_hose as PH           # noqa: E402  (bridge-side imports only on a live run)
        raw = PH.PB()
    B = V.guard(raw)
    import tempfile
    out = a.out or (os.path.join(tempfile.gettempdir(), "drawbridge_mock_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
                    if a.mock else os.path.join(HERE, "drawbridge_result_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    rows = []
    res = {"script": "drawbridge_proof.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a),
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
        rows.append({"id": rid, "status": st, "class": cls, "detail": det})
        print("%-26s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    # ------------------------------------------------------------------ helpers (every reply reaches V.PRE through the guard)
    def dproof(method, arg, answer=False):
        """One RM_DrawbridgeProofs read. A refused static_call (the class not loaded), a REFUSED answer or a reply with no
        key=value is a HARNESS fault of the open scope, unless `answer=True` ('LEAF none' is a measurement)."""
        return _static(DPROOF, method, arg, answer)

    def sproof(method, arg, answer=False):
        return _static(SPROOF, method, ";".join(pid_num(t) for t in str(arg).split(";")), answer)

    def _static(ty, method, arg, answer):
        r = B.call("jawa/static_call", type=ty, method=method, args=arg) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        V.require(not txt.startswith("REFUSED"), "%s accepted its args" % method, txt[:200], cls="HARNESS")
        kv = parse(txt) if r.get("success") is True and not txt.startswith("REFUSED") else {}
        if not answer:
            V.require(kv, "%s answered" % method, txt[:200], cls="HARNESS")
        return kv, txt

    def typed(ty, method, args):
        """A production static read with typed args ('current|x,z'): the result text, or None when it could not be asked."""
        r = B.call("jawa/static_call", type=ty, method=method, args=args) or {}
        if r.get("success") is not True:
            V.require(False, "%s.%s answered" % (ty.rsplit(".", 1)[-1], method), str(r)[:200], cls="HARNESS")
            return None
        return str(r.get("result"))

    def counters():
        out_ = {}
        for ty, f in COUNTERS:
            r = B.call("jawa/mod_settings_field", typeName=ty, action="get", field=f) or {}
            try:
                out_[f] = int(r.get("value"))
            except (TypeError, ValueError):
                out_[f] = None
                V.require(False, "counter %s read" % f, str(r)[:160], cls="HARNESS")
        return out_

    def delta(c0, c1, f):
        return None if c0.get(f) is None or c1.get(f) is None else c1[f] - c0[f]

    @contextlib.contextmanager
    def setting(field, value):
        """An RM_DrawbridgeSettings field set and read back for the block; the prior value goes back whatever the block did."""
        r0 = B.call("jawa/mod_settings_field", typeName=DBS, action="get", field=field) or {}
        r = B.call("jawa/mod_settings_field", typeName=DBS, action="set", field=field, value=str(value)) or {}
        V.require(str(r.get("valueAfter")) == str(value) or _float_eq(r.get("valueAfter"), value), "%s set to %s" % (field, value), r)
        try:
            yield
        finally:
            if r0.get("value") is not None:
                B.call("jawa/mod_settings_field", typeName=DBS, action="set", field=field, value=str(r0["value"]), _answer=True)

    def dig(c, n=DEEP):
        return B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=-1) or {}

    def spawn(c, kind="Colonist", faction="player", draft=False):
        r = B.call("jawa/spawn_pawn", kindDef=kind, x=c[0], z=c[1], faction=faction, count=1) or {}
        pid = ((r.get("pawns") or [{}])[0]).get("id")
        if pid and draft:
            B.call("jawa/set_draft", pawnId=pid, drafted=True)
        return pid

    def walls(cells):
        if cells:
            B.call("jawa/spawn_batch", ops=";".join("Wall:%d,%d" % c for c in cells), stuff="BlocksGranite")

    def pawns():
        return {p.get("id"): p for p in (B.call("jawa/list_pawns", limit=400, includeHealth=True) or {}).get("pawns") or []}

    def at(p):
        return (p.get("x"), p.get("z")) if p else (None, None)

    def ticks(n):
        r = B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}
        V.require(r.get("success") is not False, "the clock moved %d ticks" % n, r, cls="HARNESS")
        return r

    def build(scene, a_, b_, tier, hinge="A"):
        kv, txt = dproof("ProofMakeDrawbridge", "%s;%s;%s;%s;winch" % (xz(a_), xz(b_), tier, hinge))
        V.require(kv.get("ok") == "True", "%s drawbridge built" % scene, txt)
        return kv, txt

    def leaf(c):
        kv, txt = dproof("ProofLeaf", xz(c))
        return kv, txt

    def power(c, on):
        kv, txt = dproof("ProofWinchPower", "%s;%s" % (xz(c), "on" if on else "off"))
        V.require(kv.get("powered") == str(bool(on)), "winch power %s" % ("on" if on else "off"), txt)
        return kv

    fac_cache = []

    def faction():
        """A hostile humanlike faction def, read from spawn_pawn's refusal of faction '?' (it lists `available`; nothing
        spawns). raid_trench_proof's recipe. Not found: a fault of the open scope (SITE), 'Pirate' tried anyway."""
        if not fac_cache:
            probe = B.call("jawa/spawn_pawn", kindDef="Mercenary_Gunner", x=0, z=0, faction="?", count=1, _answer=True) or {}
            avail = (probe.get("details") or {}).get("available") or []
            fac = next((f_["def"] for f_ in avail if f_.get("hostile") and str(f_.get("def")).startswith("Pirate")),
                       next((f_["def"] for f_ in avail if f_.get("hostile") and f_.get("def") not in ("Entities", "Mechanoid", "Insect")),
                            None))
            if fac is None:
                V.require(False, "a hostile humanlike faction to spawn", str(probe)[:200])
                return "Pirate"
            fac_cache.append(fac)
        return fac_cache[0]

    def assault(cells, kind="Mercenary_Gunner"):
        fac = faction()
        ids = [spawn(c, kind=kind, faction=fac) for c in cells]
        ids = [i for i in ids if i]
        if ids:
            B.call("jawa/lord_assault_spawn", pawns=",".join(str(i) for i in ids))
        return ids

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
    probe = B.call("jawa/static_call", type=DPROOF, method="ProofLeaf", args="-1,-1", _answer=True) or {}
    if probe.get("success") is not True:
        res["owedWhy"] = str(probe.get("error") or probe.get("message") or probe)[:300]
        for rid in only:
            row(rid, "UNMEASURED", {"why": "%s is not in the loaded FlowWorks (%s): deploy a FlowWorks built with it"
                                           % (DPROOF, res["owedWhy"][:120]), "owedProofs": sorted(OWED_PROOFS)}, cls="HARNESS")
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
        print("drawbridge proof: %s missing -> every row UNMEASURED/HARNESS -> %s" % (DPROOF, out))
        return 2
    if not a.mock:
        rect = (max(ox - 4, 1), max(oz - 2, 1), 50, 90)
        B.call("jawa/kill_hostiles")
        B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect",
               args="%d;%d;%d;%d" % rect)
        site_rows = []
        with V.scope("site"):
            V.prepare_site(B, rect, site_rows, "drawbridge_site")
        bad = [r for r in site_rows if r.get("status") not in (None, "PASS")]
        if bad:
            for rid in only:
                row(rid, "UNMEASURED", {"why": "site not prepared", "rect": rect, "site": bad[:3]}, cls="SITE")
            return 2
        B.call("rimworld/set_god_mode", enabled=True)

    ctx = dict(faction=faction, a=a, B=B, P=P, xz=xz, row=row, dproof=dproof, sproof=sproof, typed=typed, counters=counters, delta=delta,
               setting=setting, dig=dig, spawn=spawn, walls=walls, pawns=pawns, at=at, ticks=ticks, build=build, leaf=leaf,
               power=power, assault=assault, ox=ox, oz=oz, res=res, save=save)
    for rid in ROW_IDS:                 # SAVE_MIDRAISE is last in ROW_IDS: its load replaces the map
        if rid in only:
            print("== row %s" % rid, flush=True)
            with V.scope(rid):
                SCENES[rid](ctx)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    if a.mock:
        bad = [r["id"] for r in rows if r["detail"].get("mock") != "PASS"]
        print("MOCK: drawbridge proof: %d rows, mock verdicts not PASS: %s -> %s" % (len(rows), bad or "none", out))
        return 1 if any(r["detail"].get("mock") == "FAIL" for r in rows) else (2 if bad else 0)
    fails = [r for r in rows if r["status"] == "FAIL"]
    unm = [r for r in rows if r["status"] != "PASS"]
    print("drawbridge proof: %d rows, %d FAIL, %d not PASS -> %s" % (len(rows), len(fails), len(unm), out))
    return 1 if fails else (2 if unm else 0)


def _float_eq(x, y):
    try:
        return abs(float(x) - float(y)) < 1e-6
    except (TypeError, ValueError):
        return False


def _c(ctx, *ks):
    return [ctx[k] for k in ks]


# ====================================================================== the rows
def raise_path(ctx):
    """PROVE ProofPath (production path finder) for a colonist from bank A to bank B before and right after a raise.
    EXPECT before: found, >= 6 decked squares; after (10 ticks): no decked square on the path, RaisedAt true, ToggleCount and
    RepathCount each rose. LIES: a path cached before the toggle (1.6 batched jobs) read as fresh; a walker that never held
    a path cannot be re-pathed, so RepathCount must rise for a pawn that was ordered across first."""
    B, P, xz, row, sproof, dproof, typed, ticks, spawn = _c(ctx, "B", "P", "xz", "row", "sproof", "dproof", "typed", "ticks", "spawn")
    for i in range(1, 7):
        ctx["dig"](P(i, 6))
    ctx["walls"]([P(x, z) for x in range(-2, 10) for z in (5, 7)])
    ctx["build"]("B", P(0, 6), P(7, 6), "steel")
    ctx["power"](P(3, 6), True)
    walker = spawn(P(-1, 6), draft=True)
    kv0, t0 = sproof("ProofPath", "%s;%s" % (walker, xz(P(8, 6))))
    V.require(kv0.get("found") == "True" and num(kv0, "decked", 0) >= 6, "lowered: the deck is the path", t0)
    c0 = ctx["counters"]()
    B.call("jawa/order_pawn", pawnId=walker, x=P(8, 6)[0], z=P(8, 6)[1], waitTicks=1, draft=True)   # holds a path now
    dproof("ProofDevSet", "%s;raise" % xz(P(3, 6)))
    ticks(10)
    raised = typed(DB, "RaisedAt", "current|%s" % xz(P(3, 6)))
    kv1, t1 = sproof("ProofPath", "%s;%s" % (walker, xz(P(8, 6))), answer=True)
    c1 = ctx["counters"]()
    tog, rep = ctx["delta"](c0, c1, "ToggleCount"), ctx["delta"](c0, c1, "RepathCount")
    V.require(raised is not None and tog is not None and rep is not None, "raise state and counters read", [raised, tog, rep],
              cls="HARNESS")
    good = raised == "True" and (kv1.get("found") == "False" or num(kv1, "decked", 1) == 0) and (tog or 0) >= 1 and (rep or 0) >= 1
    row("RAISE_PATH", "PASS" if good else "FAIL", {"before": t0, "after": t1, "raisedAt": raised, "toggles": tog, "repaths": rep})


def raise_tips_riders(ctx):
    """PROVE six hostile riders on a 3-wide steel leaf, the hinge bank walled to ONE free square (ProofTipPreview reads it),
    raised by ProofDevSet; positions from list_pawns 10 ticks later.
    EXPECT TippedCount +1 and FellCount +5; exactly one rider on the hinge bank (x <= 0), five on dug leaf squares, all six
    still hostile. LIES: a free square the tip rule cannot use (behind the anchor) leaves 0 landers and reads FAIL: the
    preview's free=1 is the precondition, so a site the mod rightly refuses is SITE, not MOD."""
    P, xz, row, dproof, ticks, spawn = _c(ctx, "P", "xz", "row", "dproof", "ticks", "spawn")
    for z in (24, 25, 26):
        for i in range(1, 5):
            ctx["dig"](P(i, z))
    ctx["build"]("E", P(0, 24), P(5, 26), "steel")
    ctx["power"](P(2, 25), True)
    bank = [P(x, z) for x in range(-4, 0) for z in range(22, 29) if (x, z) != (-1, 25)]
    ctx["walls"](bank + [P(x, z) for x in range(0, 6) for z in (23, 27)])
    riders = [spawn(P(i, z), kind="Mercenary_Gunner", faction=_hostile(ctx)) for i, z in ((1, 24), (1, 25), (1, 26), (2, 24),
                                                                                         (2, 25), (2, 26))]
    V.require(all(riders), "six riders spawned", riders)
    kvp, tp = dproof("ProofTipPreview", xz(P(2, 25)))
    V.require(num(kvp, "riders") == 6 and num(kvp, "free") == 1, "preview: six riders, one free bank square", tp)
    c0 = ctx["counters"]()
    dproof("ProofDevSet", "%s;raise" % xz(P(2, 25)))
    ticks(10)
    ps = ctx["pawns"]()
    c1 = ctx["counters"]()
    tipped, fell = ctx["delta"](c0, c1, "TippedCount"), ctx["delta"](c0, c1, "FellCount")
    V.require(all(r in ps for r in riders if r), "every rider in the read", [r for r in riders if r not in ps], cls="HARNESS")
    cells = [ctx["at"](ps.get(r)) for r in riders]
    on_bank = sum(1 for c in cells if c[0] is not None and c[0] <= P(0, 0)[0])
    in_hole = sum(1 for c in cells if c[0] is not None and P(1, 0)[0] <= c[0] <= P(4, 0)[0] and P(0, 24)[1] <= c[1] <= P(0, 26)[1])
    still = sum(1 for r in riders if (ps.get(r) or {}).get("hostile"))
    good = tipped == 1 and fell == 5 and on_bank == 1 and in_hole == 5 and still == 6
    row("RAISE_TIPS_RIDERS", "PASS" if good else "FAIL",
        {"preview": tp, "tipped": tipped, "fell": fell, "onBank": on_bank, "inHole": in_hole, "stillHostile": still, "cells": cells})


def _hostile(ctx):
    return ctx["faction"]()


def raise_spares_underpass(ctx):
    """PROVE a colonist put UNDER the deck (floor band, RM_SuspensionProofs.ProofPutUnder) and a drafted rider on it; raise.
    EXPECT the under-pawn's cell and hediffs unchanged and ProofBand still reads it below; the rider tipped to bank A.
    LIES: a pawn never put under (ProofPutUnder under=False) is untouched trivially: that is a SITE precondition."""
    P, xz, row, dproof, sproof, ticks, spawn = _c(ctx, "P", "xz", "row", "dproof", "sproof", "ticks", "spawn")
    for i in range(1, 5):
        ctx["dig"](P(i, 32))
    ctx["build"]("F", P(0, 32), P(5, 32), "steel")
    ctx["power"](P(2, 32), True)
    under = spawn(P(1, 32), draft=True)
    put, tput = sproof("ProofPutUnder", "%s;%s" % (under, xz(P(2, 32))))
    V.require(put.get("under") == "True", "pawn stands under the deck", tput)
    rider = spawn(P(3, 32), draft=True)
    ps0 = ctx["pawns"]()
    c0 = ctx["counters"]()
    dproof("ProofDevSet", "%s;raise" % xz(P(2, 32)))
    ctx["ticks"](10)
    ps1 = ctx["pawns"]()
    c1 = ctx["counters"]()
    kvb, tb = sproof("ProofBand", under, answer=True)
    u0, u1 = ps0.get(under) or {}, ps1.get(under) or {}
    V.require(_health(u0) is not None and _health(u1) is not None, "pawn health read", "no health block", cls="HARNESS")
    same = ctx["at"](u0) == ctx["at"](u1) and len(_health(u1) or []) == len(_health(u0) or [])
    rider_at = ctx["at"](ps1.get(rider))
    tipped = ctx["delta"](c0, c1, "TippedCount")
    good = same and kvb.get("view") != "deck" and tipped == 1 and rider_at[0] is not None and rider_at[0] <= P(0, 0)[0]
    row("RAISE_SPARES_UNDERPASS", "PASS" if good else "FAIL",
        {"underBefore": ctx["at"](u0), "underAfter": ctx["at"](u1), "band": tb, "riderAt": rider_at, "tipped": tipped})


def lower_only_from_winch(ctx):
    """PROVE the production WorkGiver asked per pawn (ProofWorkJob), a colonist on the winch bank A and one on the far bank B.
    EXPECT lowered leaf + raise order: far-bank pawn gets a job (raise from either side); raised leaf + lower order: far-bank
    pawn gets none, winch-bank pawn gets one. LIES: the far pawn refused for reach alone would also read 'none' (detail
    keeps why=); a winch pawn that gets no lower job at all (no order seen) would make the far 'none' vacuous, so the winch
    pawn's job is part of the bar."""
    P, xz, row, dproof, spawn = _c(ctx, "P", "xz", "row", "dproof", "spawn")
    for i in range(1, 5):
        ctx["dig"](P(i, 0))
    # a corridor walled edge to edge (z=-1/z=1 x=-2..9, capped at x=-3/x=10): the far bank reaches the winch side ONLY over the leaf
    ctx["walls"]([P(x, z) for x in range(-2, 10) for z in (-1, 1)] + [P(-3, 0), P(10, 0)])
    ctx["build"]("A", P(0, 0), P(5, 0), "timber")
    w = spawn(P(-2, 0))
    f = spawn(P(7, 0))
    dproof("ProofOrder", "%s;raise" % xz(P(2, 0)))
    fr, tfr = dproof("ProofWorkJob", "%s;%s" % (pid_num(f), xz(P(2, 0))))
    dproof("ProofDevSet", "%s;raise;instant" % xz(P(2, 0)))
    kl, tl = ctx["leaf"](P(2, 0))
    V.require(kl.get("target") == "raised" and num(kl, "progress", -1) == num(kl, "full", -2), "leaf staged raised", tl)
    # precondition (SITE, never a mod FAIL): with the leaf raised the far-bank pawn has no path to the winch side, else the real
    # scanner may rightly hand it the lower job by walking round and the 'none' below proves nothing
    kvp, tp = ctx["sproof"]("ProofPath", "%s;%s" % (f, xz(P(-2, 0))), answer=True)
    V.require(kvp.get("found") == "False", "far bank cannot reach the winch side with the leaf raised", tp, cls="SITE")
    dproof("ProofOrder", "%s;lower" % xz(P(2, 0)))
    fl, tfl = dproof("ProofWorkJob", "%s;%s" % (pid_num(f), xz(P(2, 0))))
    wl, twl = dproof("ProofWorkJob", "%s;%s" % (pid_num(w), xz(P(2, 0))))
    good = fr.get("job") == "True" and fl.get("job") == "False" and wl.get("job") == "True"
    row("LOWER_ONLY_FROM_WINCH", "PASS" if good else "FAIL", {"farRaise": tfr, "farLower": tfl, "winchLower": twl, "leaf": tl, "noWalkRound": tp})


def two_leaf_tips_own_hinge(ctx):
    """PROVE a timber bridge of 8 interior squares (two leaves of 4, a winch on each bank), a drafted rider on each leaf,
    both raised (ProofDevSet instant; staging, the drive is not the claim).
    EXPECT 2 leaves hinged A and B; rider 1 lands on bank A (x <= 0), rider 2 on bank B (x >= 9). LIES: both riders on bank A
    would mean 'tip to the colony bank', the ruled-out reading; a one-leaf split makes the row UNMEASURED (SITE)."""
    P, xz, row, dproof, spawn = _c(ctx, "P", "xz", "row", "dproof", "spawn")
    for i in range(1, 9):
        ctx["dig"](P(i, 38))
    kv, txt = ctx["build"]("G", P(0, 38), P(9, 38), "timber")
    V.require(kv.get("leaves") == "2" and kv.get("hinges") == "A,B", "two leaves, one hinge per bank", txt)
    r1, r2 = spawn(P(2, 38), draft=True), spawn(P(7, 38), draft=True)
    dproof("ProofDevSet", "%s;raise;instant" % xz(P(2, 38)))
    dproof("ProofDevSet", "%s;raise;instant" % xz(P(7, 38)))
    ps = ctx["pawns"]()
    a1, a2 = ctx["at"](ps.get(r1)), ctx["at"](ps.get(r2))
    V.require(a1[0] is not None and a2[0] is not None, "both riders in the read", [a1, a2], cls="HARNESS")
    good = a1[0] is not None and a2[0] is not None and a1[0] <= P(0, 0)[0] and a2[0] >= P(9, 0)[0]
    row("TWO_LEAF_TIPS_OWN_HINGE", "PASS" if good else "FAIL", {"build": txt, "rider1": a1, "rider2": a2})


def hostile_locks(ctx):
    """PROVE (a) a raise ordered while a free hostile is about; the hostiles killed: auto-lower starts; a new assault spawned:
    the pending auto-lower is cancelled (target raised again). (b) a hostile trapped in a 4 m pit: FreeHostileCount 0, not
    Locked. raiseSpeed 0.25 (480 ticks a steel leaf) so the auto-lower is still under way when the raid lands.
    EXPECT (a) auto=True target=lowered after the kill, then auto=False target=raised; (b) IsTrapped True, free 0, Locked
    False. LIES: an assault that is not an active threat never locks: FreeHostileCount(fresh) >= 1 is read first (SITE)."""
    with ctx["setting"]("raiseSpeed", 0.25):
        _hostile_locks(ctx)


def _hostile_locks(ctx):
    P, xz, row, dproof, typed, ticks, spawn = _c(ctx, "P", "xz", "row", "dproof", "typed", "ticks", "spawn")
    B = ctx["B"]
    for i in range(1, 5):
        ctx["dig"](P(i, 44))
    for c in ((10, 44), (11, 44), (10, 45), (11, 45)):
        ctx["dig"](P(*c))
    ctx["build"]("H", P(0, 44), P(5, 44), "steel")
    ctx["power"](P(2, 44), True)
    with V.scope("HOSTILE_LOCKS_a") as sa:
        ctx["assault"]([P(25, 44)])
        free0 = typed(DB, "FreeHostileCount", "current|true")
        V.require(free0 not in (None, "0"), "a free hostile locks the map", free0)
        dproof("ProofOrder", "%s;raise;now" % xz(P(2, 44)))
        ticks(500)
        k1, t1 = ctx["leaf"](P(2, 44))
        V.require(k1.get("target") == "raised" and k1.get("hold") == "False", "raised under lock, not held", t1)
        B.call("jawa/kill_hostiles")
        ticks(70)
        k2, t2 = ctx["leaf"](P(2, 44))
        V.require(k2.get("auto") == "True" and k2.get("target") == "lowered", "peace: auto-lower under way", t2)
        ctx["assault"]([P(25, 44)])
        ticks(70)
        k3, t3 = ctx["leaf"](P(2, 44))
        cancelled = k3.get("auto") == "False" and k3.get("target") == "raised"
    with V.scope("HOSTILE_LOCKS_b") as sb:
        B.call("jawa/kill_hostiles")
        trapped = spawn(P(10, 44), kind="Mercenary_Gunner", faction=_hostile(ctx))
        ticks(5)
        it = typed(TRAP, "IsTrapped", pid_num(trapped)) if trapped else None
        V.require(it == "True", "the hostile is trapped in the pit", it)
        free1 = typed(DB, "FreeHostileCount", "current|true")
        locked = typed(DB, "Locked", "current")
        trapped_ok = free1 == "0" and locked == "False"
    V.adopt(sa, sb)
    good = cancelled and trapped_ok
    row("HOSTILE_LOCKS", "PASS" if good else "FAIL",
        {"freeBefore": free0, "raisedLocked": t1, "autoLowering": t2, "afterRaid": t3, "trappedFree": free1, "locked": locked})


def steel_unpowered_freezes(ctx):
    """PROVE a steel leaf raised under power (ProofDevSet), power cut part-way (ProofWinchPower off), 120 ticks, power back.
    EXPECT progress unchanged and frozen=True while off; moving again (to full) once on. LIES: a leaf already at full when the
    power is cut is 'unchanged' trivially: 0 < progress < full is the precondition."""
    P, xz, row, dproof, ticks = _c(ctx, "P", "xz", "row", "dproof", "ticks")
    for i in range(1, 7):
        ctx["dig"](P(i, 12))
    ctx["build"]("C", P(0, 12), P(7, 12), "steel")
    ctx["power"](P(3, 12), True)
    dproof("ProofDevSet", "%s;raise" % xz(P(3, 12)))
    ticks(30)
    k1, t1 = ctx["leaf"](P(3, 12))
    p1, full = num(k1, "progress"), num(k1, "full")
    V.require(p1 is not None and full is not None and 0 < p1 < full, "caught part-way up", t1)
    ctx["power"](P(3, 12), False)
    ticks(120)
    k2, t2 = ctx["leaf"](P(3, 12))
    ctx["power"](P(3, 12), True)
    ticks(full or 120)
    k3, t3 = ctx["leaf"](P(3, 12))
    good = num(k2, "progress") == p1 and k2.get("frozen") == "True" and num(k3, "progress") == full and k3.get("frozen") == "False"
    row("STEEL_UNPOWERED_FREEZES", "PASS" if good else "FAIL", {"partWay": t1, "unpowered": t2, "repowered": t3})


def winch_lost_crashes(ctx):
    """PROVE a raised timber leaf (ProofDevSet instant), a colonist spawned in the hole under it, the winch house destroyed
    (jawa/destroy_batch on ProofMakeDrawbridge's winchAt cell).
    EXPECT progress 0 (lowered) at once, CrashCount +1, CrashHits >= 1 and the colonist gained a hediff. LIES: a colonist
    standing on the bank is never under the leaf: ProofBand must read it below the deck (view != deck) first (SITE)."""
    P, xz, row, dproof, sproof, ticks, spawn = _c(ctx, "P", "xz", "row", "dproof", "sproof", "ticks", "spawn")
    B = ctx["B"]
    for i in range(1, 5):
        ctx["dig"](P(i, 50))
    kv, txt = ctx["build"]("I", P(0, 50), P(5, 50), "timber")
    winch = (kv.get("winchAt") or "").split("|")[0]
    V.require(re.match(r"^-?\d+,-?\d+$", winch or ""), "winch cell known", txt, cls="HARNESS")
    dproof("ProofDevSet", "%s;raise;instant" % xz(P(2, 50)))
    victim = spawn(P(2, 50), draft=True)
    kb, tb = sproof("ProofBand", victim, answer=True)
    V.require(kb and kb.get("view") != "deck", "victim is down in the hole", tb)
    ps0 = ctx["pawns"]()
    c0 = ctx["counters"]()
    wx, wz = (int(v) for v in winch.split(",")) if winch and "," in winch else (-1, -1)
    gone = B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (wx, wz), categories="Building") or {}
    V.require(int(gone.get("destroyed") or 0) >= 1, "winch destroyed", {k: gone.get(k) for k in ("success", "message", "destroyed")})
    ticks(10)
    k1, t1 = ctx["leaf"](P(2, 50))
    ps1 = ctx["pawns"]()
    c1 = ctx["counters"]()
    h0, h1 = _health(ps0.get(victim) or {}), _health(ps1.get(victim) or {})
    V.require(h0 is not None and h1 is not None, "pawn health read", "no health block", cls="HARNESS")
    crashes, hits = ctx["delta"](c0, c1, "CrashCount"), ctx["delta"](c0, c1, "CrashHits")
    good = num(k1, "progress") == 0 and crashes == 1 and (hits or 0) >= 1 and len(h1 or []) > len(h0 or [])
    row("WINCH_LOST_CRASHES", "PASS" if good else "FAIL",
        {"after": t1, "crashes": crashes, "hits": hits, "hediffs": [len(h0 or []), len(h1 or [])], "band": tb})


def raid_up(ctx):
    """PROVE raid_trench_proof's island (ring dug 2 m at Chebyshev 5..6), a steel drawbridge east across it with its winch on
    the island, raised; a player decoy outside; 4 raiders in LordJob_AssaultColony 25 east; --raid-ticks sampled every 250.
    EXPECT legal progress and no job loop: (WinchJobs + PlanksLaid rose, or a raider reached the decoy or the trench) AND
    HostileJobsEnded rose by <= 3 per raider. LIES: raiders that never come within 15 squares measure the storyteller, not
    the hand-off (SITE); a raider in the trench is legal (trench rules), never a breach."""
    B, P, xz, row, dproof, ticks, spawn = _c(ctx, "B", "P", "xz", "row", "dproof", "ticks", "spawn")
    c = P(30, 70)
    ring = [(x, z) for x in range(c[0] - 6, c[0] + 7) for z in range(c[1] - 6, c[1] + 7) if max(abs(x - c[0]), abs(z - c[1])) >= 5]
    for cell in ring:
        ctx["dig"](cell, 4)
    ctx["build"]("K", (c[0] + 4, c[1]), (c[0] + 7, c[1]), "steel")
    ctx["power"]((c[0] + 5, c[1]), True)
    B.call("jawa/spawn_batch", ops="Sandbags:%d,%d" % (c[0] + 14, c[1] + 4), stuff="BlocksGranite")
    for k in range(2):
        spawn((c[0] - 2 + k, c[1]), draft=True)
    dproof("ProofDevSet", "%s;raise;instant" % xz((c[0] + 5, c[1])))
    c0 = ctx["counters"]()
    ids = ctx["assault"]([(c[0] + 25, c[1] + k) for k in range(4)])
    V.require(len(ids) == 4, "four raiders spawned in an assault", ids)
    samples, came_near, reached = [], set(), set()
    t = 0
    while t < ctx["a"].raid_ticks:
        ticks(250)
        t += 250
        ps = ctx["pawns"]()
        snap = []
        for i in ids:
            p = ps.get(i) or {}
            x, z = p.get("x"), p.get("z")
            snap.append((i, x, z, p.get("dead"), p.get("downed")))
            if x is None:
                continue
            d = max(abs(x - c[0]), abs(z - c[1]))
            if d <= 15:
                came_near.add(i)
            if d <= 6 or (abs(x - (c[0] + 14)) <= 1 and abs(z - (c[1] + 4)) <= 1):
                reached.add(i)
        samples.append({"t": t, "raiders": snap})
    c1 = ctx["counters"]()
    V.require(len(came_near) >= 2, "two raiders came within 15 squares", sorted(came_near))
    ended = ctx["delta"](c0, c1, "HostileJobsEnded")
    winch_jobs, planks = ctx["delta"](c0, c1, "WinchJobs"), ctx["delta"](c0, c1, "PlanksLaid")
    progress = (winch_jobs or 0) + (planks or 0) > 0 or bool(reached)
    no_loop = ended is not None and ended <= 3 * len(ids)
    ctx["res"].setdefault("raidSamples", samples)
    row("RAID_UP", "PASS" if progress and no_loop else "FAIL",
        {"winchJobs": winch_jobs, "planksLaid": planks, "reached": sorted(reached), "cameNear": sorted(came_near),
         "hostileJobsEnded": ended, "ticks": t})


def raid_plank(ctx):
    """PROVE a 2-square gap (4 m), carrier R1 given a plank over it (ProofGivePlank), interrupted 60 ticks in (< the 180-tick
    lay), then carrier R2 given the same gap; 400 ticks.
    EXPECT ProofPlankLedger crossings == 1 and PlanksLaid +1 exactly. LIES: a lay that never started (GIVE ok=False, no job)
    lays nothing and 'no duplicate' holds trivially: R2's crossing must exist (crossings == 1, not <= 1)."""
    P, xz, row, dproof, ticks, spawn = _c(ctx, "P", "xz", "row", "dproof", "ticks", "spawn")
    for i in (1, 2):
        ctx["dig"](P(i, 56))
    lip, far = P(3, 56), P(0, 56)
    fac = _hostile(ctx)
    r1 = spawn(P(3, 56), kind="Mercenary_Gunner", faction=fac)
    r2 = spawn(P(4, 56), kind="Mercenary_Gunner", faction=fac)
    c0 = ctx["counters"]()
    g1, tg1 = dproof("ProofGivePlank", "%s;%s;%s" % (pid_num(r1), xz(lip), xz(far)))
    V.require(g1.get("ok") == "True", "carrier 1 started laying", tg1)
    ticks(60)
    i1, ti1 = dproof("ProofInterrupt", pid_num(r1))
    V.require(i1.get("ended") == "True", "carrier 1 interrupted", ti1)
    g2, tg2 = dproof("ProofGivePlank", "%s;%s;%s" % (pid_num(r2), xz(lip), xz(far)))
    V.require(g2.get("ok") == "True", "carrier 2 started laying", tg2)
    ticks(400)
    led, tled = dproof("ProofPlankLedger", "%s;%s" % (xz(lip), xz(far)))
    c1 = ctx["counters"]()
    laid = ctx["delta"](c0, c1, "PlanksLaid")
    good = num(led, "crossings") == 1 and laid == 1
    row("RAID_PLANK", "PASS" if good else "FAIL", {"give1": tg1, "interrupt": ti1, "give2": tg2, "ledger": tled, "laid": laid})


def save_midraise(ctx):
    """PROVE a steel leaf at raiseSpeed 0.25 (480 ticks) with a drafted rider, raised 100 ticks (tip done), saved, loaded.
    EXPECT after the load: progress within one drive step (5) of the save, tip=True, TippedCount unchanged (no replay), the
    rider where the tip left it; 500 ticks later the leaf is fully up and TippedCount still unchanged. LIES: the counters are
    process statics: one that FELL across the load was reset by something, not 'no replay' (HARNESS, never PASS)."""
    with ctx["setting"]("raiseSpeed", 0.25):
        _save_midraise(ctx)


def _save_midraise(ctx):
    B, P, xz, row, dproof, ticks, spawn = _c(ctx, "B", "P", "xz", "row", "dproof", "ticks", "spawn")
    for i in range(1, 7):
        ctx["dig"](P(i, 18))
    ctx["build"]("D", P(0, 18), P(7, 18), "steel")
    ctx["power"](P(3, 18), True)
    rider = spawn(P(3, 18), draft=True)
    dproof("ProofDevSet", "%s;raise" % xz(P(3, 18)))
    ticks(100)
    k1, t1 = ctx["leaf"](P(3, 18))
    c1 = ctx["counters"]()
    V.require(0 < (num(k1, "progress") or 0) < (num(k1, "full") or 0) and k1.get("tip") == "True", "mid-raise, tip done", t1)
    at1 = ctx["at"](ctx["pawns"]().get(rider))
    name = "RM_DRAWBRIDGE_MIDRAISE_%s" % time.strftime("%Y%m%dT%H%M%S")
    sv = B.call("rimworld/save_game", saveName=name) or {}
    V.require(sv.get("success") is not False, "saved", sv, cls="HARNESS")
    ld = B.call("rimworld/load_game_ready", saveName=name, timeoutMs=280000) or {}
    V.require(ld.get("success") is not False, "loaded", ld, cls="HARNESS")
    if not ctx["a"].mock:
        V.require(V._wait_playing(B, leave_s=0)[0], "playing after the load", None, cls="HARNESS")
    k2, t2 = ctx["leaf"](P(3, 18))
    c2 = ctx["counters"]()
    at2 = ctx["at"](ctx["pawns"]().get(rider))
    tip_delta = ctx["delta"](c1, c2, "TippedCount")
    V.require(tip_delta is not None and tip_delta >= 0, "counters survived the load (process statics)", tip_delta, cls="HARNESS")
    ticks(500)
    k3, t3 = ctx["leaf"](P(3, 18))
    c3 = ctx["counters"]()
    later = ctx["delta"](c1, c3, "TippedCount")
    good = (num(k2, "progress") is not None and abs(num(k2, "progress") - num(k1, "progress")) <= 5 and k2.get("tip") == "True"
            and tip_delta == 0 and at2 == at1 and num(k3, "progress") == num(k3, "full") and later == 0)
    ctx["res"]["midraiseSave"] = name
    row("SAVE_MIDRAISE", "PASS" if good else "FAIL",
        {"save": name, "before": t1, "afterLoad": t2, "end": t3, "tipDeltaLoad": tip_delta, "tipDeltaEnd": later,
         "rider": [at1, at2]})


def _health(p):
    h = p.get("health") if isinstance(p, dict) else None
    if not isinstance(h, dict):
        return None
    return h.get("hediffs") or []


SCENES = {"RAISE_PATH": raise_path, "RAISE_TIPS_RIDERS": raise_tips_riders, "RAISE_SPARES_UNDERPASS": raise_spares_underpass,
          "LOWER_ONLY_FROM_WINCH": lower_only_from_winch, "TWO_LEAF_TIPS_OWN_HINGE": two_leaf_tips_own_hinge,
          "HOSTILE_LOCKS": hostile_locks, "STEEL_UNPOWERED_FREEZES": steel_unpowered_freezes,
          "WINCH_LOST_CRASHES": winch_lost_crashes, "RAID_UP": raid_up, "RAID_PLANK": raid_plank, "SAVE_MIDRAISE": save_midraise}


# ====================================================================== offline stand-in
class FakeBridge(object):
    """A small drawbridge world model answering in the shapes the live tools and the OWED proofs are specified to: leaves
    with progress, winches with power, pawns with cells and health, the counters. It knows nothing about the game; a mock
    verdict proves the script's control flow and its MOD/SITE/HARNESS split only. `faults` inject one wrong behaviour each:
      no_proofs        RM_DrawbridgeProofs is not loaded (an old deploy): every row UNMEASURED/HARNESS, none FAIL
      noclock          step_game_ticks refuses: every row that waits on the clock is UNMEASURED/HARNESS
      two_free         the tip preview reads free=2 (the site is not the scene): RAISE_TIPS_RIDERS UNMEASURED/SITE
      tip_all_fall     MOD: riders all fall though a bank square is free      -> RAISE_TIPS_RIDERS FAIL
      no_repath        MOD: a toggle re-paths nobody                           -> RAISE_PATH FAIL
      underpass_tipped MOD: the pawn under the deck is moved by the raise     -> RAISE_SPARES_UNDERPASS FAIL
      lower_from_far   MOD: the far-bank pawn gets a lower job                 -> LOWER_ONLY_FROM_WINCH FAIL
      tip_colony_bank  MOD: both leaves tip to bank A                          -> TWO_LEAF_TIPS_OWN_HINGE FAIL
      trapped_locks    MOD: a trapped hostile counts as free                   -> HOSTILE_LOCKS FAIL
      freeze_ignored   MOD: unpowered steel keeps moving                       -> STEEL_UNPOWERED_FREEZES FAIL
      no_crash         MOD: a destroyed winch leaves the leaf up               -> WINCH_LOST_CRASHES FAIL
      raid_loop        MOD: raider jobs are ended over and over, no progress   -> RAID_UP FAIL
      far_reaches_winch the far bank has a path round to the winch (SITE)     -> LOWER_ONLY_FROM_WINCH UNMEASURED/SITE
      far_raiders      the raiders never come near (SITE)                      -> RAID_UP UNMEASURED/SITE
      dup_plank        MOD: the interrupted carrier's plank is laid as well    -> RAID_PLANK FAIL
      replay_tip       MOD: the load replays the tip                           -> SAVE_MIDRAISE FAIL"""
    FAULTS = ("far_reaches_winch", "no_proofs", "noclock", "two_free", "tip_all_fall", "no_repath", "underpass_tipped", "lower_from_far",
              "tip_colony_bank", "trapped_locks", "freeze_ignored", "no_crash", "raid_loop", "far_raiders", "dup_plank",
              "replay_tip")

    def __init__(self, faults=()):
        self.f = set(faults)
        self.nid = 1000
        self.pawns = {}          # id -> dict(x, z, hostile, under, trapped, hediffs, lord)
        self.leaves = []         # dict(z0, z1, first, last (x), hinge 'A'|'B', ax, bx, tier, progress, full, target, hold, auto,
        #                              pending, tip, winch (x,z) or None, powered, frozen)
        self.cnt = {f: 0 for _, f in COUNTERS}
        self.walls = set()
        self.dug = set()
        self.speed = 1.0
        self.ledger = {}
        self.carrying = {}
        self.saves = {}

    # ---- helpers
    def _leaf_at(self, x, z):
        for l in self.leaves:
            if l["z0"] <= z <= l["z1"] and l["first"] <= x <= l["last"]:
                return l
        return None

    def _full(self, tier, n):
        return int((120 if tier == "steel" else 240 * n) / self.speed + 0.5)

    def _free_hostiles(self):
        return sum(1 for p in self.pawns.values() if p["hostile"] and not p.get("dead")
                   and (not p.get("trapped") or "trapped_locks" in self.f))

    def _tip(self, l):
        riders = [i for i, p in self.pawns.items() if l["z0"] <= p["z"] <= l["z1"] and l["first"] <= p["x"] <= l["last"]
                  and (not p.get("under") or "underpass_tipped" in self.f) and not p.get("dead")]
        bank_x = l["ax"] if (l["hinge"] == "A" or "tip_colony_bank" in self.f) else l["bx"]
        step = -1 if bank_x == l["ax"] else 1
        free = [(bank_x + step * k, z) for k in range(0, 4) for z in range(l["z0"] - 1, l["z1"] + 2)]
        free = [c for c in free if c not in self.walls and c[0] != l["ax"] and c[0] != l["bx"]]
        if "tip_all_fall" in self.f:
            free = []
        for i in sorted(riders, key=lambda i: abs(self.pawns[i]["x"] - bank_x)):
            p = self.pawns[i]
            if free:
                p["x"], p["z"] = free.pop(0)
                p["under"] = False
                self.cnt["TippedCount"] += 1
            else:
                p["hediffs"].append("Bruise")
                self.cnt["FellCount"] += 1

    def _toggle(self, l):
        self.cnt["ToggleCount"] += 1
        if "no_repath" not in self.f:
            self.cnt["RepathCount"] += sum(1 for p in self.pawns.values() if p.get("pathing"))
        for p in self.pawns.values():
            p["pathing"] = False

    def _step(self, l, n):
        for _ in range(n // 5):
            free = self._free_hostiles()
            if l["auto"] and free:
                l["target"], l["auto"] = "raised", False
            elif (not free and not l["hold"] and l["target"] == "raised" and l["progress"] == l["full"] and not l["auto"]
                  and l["pending"] != "raise"):
                l["target"], l["auto"] = "lowered", True
            l["frozen"] = l["tier"] == "steel" and not (l["winch"] and l["powered"]) and "freeze_ignored" not in self.f
            want = l["full"] if l["target"] == "raised" else 0
            if l["progress"] == want:
                if want == 0:
                    l["auto"] = False
                continue
            moves = (l["tier"] == "steel" and (l["powered"] or "freeze_ignored" in self.f)) or l.get("hands")
            if l["frozen"] or not moves:
                continue
            before = l["progress"]
            l["progress"] = min(want, before + 5) if want > before else max(want, before - 5)
            if before == 0 and l["progress"] > 0:
                if not l["tip"]:
                    self._tip(l)
                    l["tip"] = True
                self._toggle(l)
            if l["progress"] == 0:
                l["tip"] = False
                self._toggle(l)

    # ---- the bridge
    def call(self, tool, **kw):
        if tool == "jawa/static_call":
            ty, m, arg = kw.get("type"), kw.get("method"), kw.get("args") or ""
            if ty == DPROOF and "no_proofs" in self.f:
                return {"success": False, "error": "Type not found: " + ty}
            return {"success": True, "result": self.static(ty, m, arg)}
        if tool == "rimworld/step_game_ticks":
            if "noclock" in self.f:
                return {"success": False, "message": "clock refused"}
            n = int(kw.get("ticks") or 0)
            for l in self.leaves:
                self._step(l, n)
            self._raid(n)
            return {"success": True, "ticksAdvanced": n}
        if tool == "jawa/flowworks_excavation_drive":
            self.dug.add((kw.get("x"), kw.get("z")))
            return {"success": True}
        if tool == "jawa/spawn_batch":
            for op in str(kw.get("ops") or "").split(";"):
                if op.startswith("Wall:"):
                    x, z = op[5:].split(",")[:2]
                    self.walls.add((int(x), int(z)))
            return {"success": True, "survived": len([o for o in str(kw.get("ops")).split(";") if o])}
        if tool == "jawa/spawn_pawn":
            if kw.get("faction") == "?":
                return {"success": False, "details": {"available": [{"def": "Pirate", "hostile": True}]}}
            self.nid += 1
            pid = "Human%d" % self.nid
            x, z = kw.get("x"), kw.get("z")
            self.pawns[pid] = dict(x=x, z=z, hostile=kw.get("faction") not in ("player", None), hediffs=[], under=False,
                                   trapped=(x, z) in self.dug and self._leaf_at(x, z) is None, lord=False, pathing=False)
            # a pawn spawned on a raised leaf square is down in the hole
            l = self._leaf_at(x, z)
            if l and l["progress"] > 0:
                self.pawns[pid]["under"] = True
            return {"success": True, "pawns": [{"id": pid}]}
        if tool == "jawa/lord_assault_spawn":
            for i in str(kw.get("pawns") or "").split(","):
                if i in self.pawns:
                    self.pawns[i]["lord"] = True
            return {"success": True}
        if tool == "jawa/kill_hostiles":
            for p in self.pawns.values():
                if p["hostile"]:
                    p["dead"] = True
            return {"success": True}
        if tool == "jawa/set_draft":
            return {"success": True, "drafted": kw.get("drafted") is True}
        if tool == "jawa/order_pawn":
            p = self.pawns.get(kw.get("pawnId"))
            if p:
                p["pathing"] = True
            return {"success": True, "pawns": [{"id": kw.get("pawnId"), "end": {"x": p and p["x"], "z": p and p["z"]}}]}
        if tool == "jawa/list_pawns":
            return {"pawns": [dict(id=i, x=p["x"] if not p.get("dead") else None, z=p["z"] if not p.get("dead") else None,
                                   hostile=p["hostile"], dead=p.get("dead", False), downed=False,
                                   **({"health": {"hediffs": [{"def": h} for h in p["hediffs"]]}} if kw.get("includeHealth") else {}))
                              for i, p in self.pawns.items()]}
        if tool == "jawa/mod_settings_field":
            f = kw.get("field")
            if kw.get("typeName") == DBS and f == "raiseSpeed":
                if kw.get("action") == "set":
                    self.speed = float(kw.get("value"))
                    return {"success": True, "valueBefore": "1", "valueAfter": kw.get("value")}
                return {"success": True, "value": str(self.speed)}
            if f in self.cnt:
                return {"success": True, "value": str(self.cnt[f])}
            return {"success": False, "error": "no field %s" % f}
        if tool == "jawa/destroy_batch":
            x, z = (int(v) for v in str(kw.get("rects")).split(",")[:2])
            hit = [l for l in self.leaves if l["winch"] == (x, z)]
            for l in hit:
                l["winch"] = None
                if l["progress"] > 0 and "no_crash" not in self.f:
                    victims = [p for p in self.pawns.values() if p.get("under") and l["z0"] <= p["z"] <= l["z1"]
                               and l["first"] <= p["x"] <= l["last"]]
                    for p in victims:
                        p["hediffs"].append("Crush")
                    self.cnt["CrashHits"] += len(victims)
                    self.cnt["CrashCount"] += 1
                    l.update(progress=0, target="lowered", tip=False, auto=False, hold=False)
            return {"success": True, "destroyed": len(hit)}
        if tool == "rimworld/save_game":
            self.saves[kw.get("saveName")] = copy.deepcopy((self.leaves, self.pawns))
            return {"success": True}
        if tool == "rimworld/load_game_ready":
            self.leaves, self.pawns = copy.deepcopy(self.saves[kw.get("saveName")])
            if "replay_tip" in self.f:
                for l in self.leaves:
                    if l["progress"] > 0:
                        self.cnt["TippedCount"] += 1
            return {"success": True}
        return {"success": True}

    def _raid(self, n):
        raiders = [p for p in self.pawns.values() if p["hostile"] and p.get("lord") and not p.get("dead")]
        if not raiders or "far_raiders" in self.f or not hasattr(self, "_island"):
            return
        for p in raiders:
            p["x"] = p["x"] - min(n // 25, max(0, p["x"] - (self._island + 7)))
        if "raid_loop" in self.f:
            self.cnt["HostileJobsEnded"] += 5 * len(raiders)
        elif any(p["x"] <= self._island + 7 for p in raiders):
            self.cnt["WinchJobs"] += 1

    def static(self, ty, m, arg):
        if ty == DB:
            if m == "RaisedAt":
                x, z = (int(v) for v in arg.split("|")[1].split(","))
                l = self._leaf_at(x, z)
                return str(bool(l and l["progress"] > 0))
            if m == "FreeHostileCount":
                return str(self._free_hostiles())
            if m == "Locked":
                return str(self._free_hostiles() > 0)
        if ty == TRAP and m == "IsTrapped":
            p = self.pawns.get("Human" + arg) or {}
            return str(bool(p.get("trapped")))
        if ty == SPROOF:
            if m == "ProofPath":
                pid, dest = arg.split(";")
                l = self._leaf_at(*(int(v) for v in dest.split(","))) or next(
                    (q for q in self.leaves if q["z0"] == int(dest.split(",")[1])), None)
                if l and l["progress"] > 0 and "far_reaches_winch" not in self.f:
                    return "PATH found=False cells=0 decked=0"
                return "PATH found=True cells=9 decked=%d" % (l["last"] - l["first"] + 1 if l else 0)
            if m == "ProofPutUnder":
                pid, c = arg.split(";")
                p = self.pawns.get("Human" + pid)
                x, z = (int(v) for v in c.split(","))
                if p:
                    p.update(x=x, z=z, under=True)
                return "PUTUNDER under=True"
            if m == "ProofBand":
                p = self.pawns.get("Human" + arg) or {}
                return "BAND under=%s onDeck=%s view=%s" % (p.get("under"), not p.get("under"), "floor" if p.get("under") else "deck")
        if ty == DPROOF:
            return self.dproof(m, arg)
        return "OK"

    def dproof(self, m, arg):
        a = arg.split(";")
        cell = lambda s: tuple(int(v) for v in s.split(","))  # noqa: E731
        if m == "ProofMakeDrawbridge":
            (x1, z1), (x2, z2), tier = cell(a[0]), cell(a[1]), a[2]
            n = abs(x2 - x1) - 1
            mx = 4 if tier == "timber" else 8
            spans = [(x1 + 1, x2 - 1, "A")] if n <= mx else [(x1 + 1, x1 + n // 2, "A"), (x1 + n // 2 + 1, x2 - 1, "B")]
            winches = []
            for f_, l_, h in spans:
                w = (x1 - 1, z1) if h == "A" else (x2 + 1, z1)
                winches.append(w)
                self.leaves.append(dict(z0=min(z1, z2), z1=max(z1, z2), first=f_, last=l_, hinge=h, ax=x1, bx=x2, tier=tier,
                                        progress=0, full=self._full(tier, l_ - f_ + 1), target="lowered", hold=False, auto=False,
                                        pending="none", tip=False, winch=w, powered=False, frozen=False))
            if x2 - x1 == 3 and tier == "steel":
                self._island = x1 - 4             # scene K: the island's centre is 4 west of the first anchor
            return "DRAW ok=True leaves=%d tier=%s hinges=%s winchAt=%s reason=-" % (
                len(spans), tier, ",".join(h for _, _, h in spans), "|".join("%d,%d" % w for w in winches))
        if m == "ProofLeaf":
            x, z = cell(a[0])
            l = self._leaf_at(x, z)
            if l is None:
                return "LEAF none"
            n = l["last"] - l["first"] + 1
            return ("LEAF leaf=1/1 progress=%d full=%d target=%s raised=%d/%d frozen=%s winch=%s powered=%s hold=%s auto=%s "
                    "pending=%s tip=%s hinge=%s version=1" % (l["progress"], l["full"], l["target"], n if l["progress"] else 0, n,
                                                              l["frozen"], l["winch"] is not None, l["powered"], l["hold"],
                                                              l["auto"], l["pending"], l["tip"], l["hinge"]))
        l = self._leaf_at(*cell(a[0])) if a and "," in a[0] and m not in ("ProofWorkJob", "ProofGivePlank", "ProofInterrupt") else None
        if m == "ProofDevSet":
            if l is None:
                return "REFUSED: not a leaf"
            raise_ = a[1] == "raise"
            l.update(target="raised" if raise_ else "lowered", hold=raise_, pending="none")
            l["full"] = self._full(l["tier"], l["last"] - l["first"] + 1)
            if len(a) > 2 and a[2] == "instant":
                if raise_ and l["progress"] == 0 and not l["tip"]:
                    self._tip(l)
                    l["tip"] = True
                l["progress"] = l["full"] if raise_ else 0
                self._toggle(l)
            return "DEVSET target=%s progress=%d" % (l["target"], l["progress"])
        if m == "ProofOrder":
            if l is None:
                return "REFUSED: not a leaf"
            raise_ = a[1] == "raise"
            locked = self._free_hostiles() > 0
            l["hold"] = raise_ and not locked
            l["pending"] = a[1]
            l["auto"] = False
            if len(a) > 2 and a[2] == "now":
                l["target"] = "raised" if raise_ else "lowered"
                l["pending"] = "none"
            return "ORDER pending=%s hold=%s locked=%s target=%s" % (l["pending"], l["hold"], locked, l["target"])
        if m == "ProofWorkJob":
            p = self.pawns.get("Human" + a[0]) or {}
            l = self._leaf_at(*cell(a[1]))
            if l is None:
                return "REFUSED: not a leaf"
            raise_ = l["pending"] == "raise"
            winch_side = (p.get("x", 0) <= l["ax"]) == (l["hinge"] == "A")
            job = raise_ or winch_side or "lower_from_far" in self.f
            return "WORK job=%s spot=%s raise=%s why=%s" % (job, "winch" if winch_side else ("far" if job else "none"), raise_,
                                                           "-" if job else "lower_only_from_the_winch_bank")
        if m == "ProofWinchPower":
            if l is None:
                return "REFUSED: not a leaf"
            l["powered"] = a[1] == "on" and l["winch"] is not None
            return "POWER powered=%s" % l["powered"]
        if m == "ProofTipPreview":
            if l is None:
                return "REFUSED: not a leaf"
            riders = sum(1 for p in self.pawns.values() if l["z0"] <= p["z"] <= l["z1"] and l["first"] <= p["x"] <= l["last"])
            free = 2 if "two_free" in self.f else 1
            return "PREVIEW riders=%d land=%d fall=%d free=%d" % (riders, min(free, riders), max(0, riders - free), free)
        if m == "ProofGivePlank":
            gap = (a[1], a[2])
            self.carrying[a[0]] = gap
            self.ledger.setdefault(gap, {"crossings": 0, "reserved": 0})
            self.ledger[gap]["reserved"] = 1
            return "GIVE ok=True job=RM_LayRaidPlank plank=RM_RaidPlank%s reserved=True" % a[0]
        if m == "ProofInterrupt":
            gap = self.carrying.pop(a[0], None)
            if gap and "dup_plank" in self.f:
                self.ledger[gap]["crossings"] += 1
                self.cnt["PlanksLaid"] += 1
            return "INT ended=True dropped=%s" % bool(gap)
        if m == "ProofPlankLedger":
            gap = (a[0], a[1])
            for pid, g in list(self.carrying.items()):
                if g == gap:
                    self.ledger[gap]["crossings"] += 1
                    self.cnt["PlanksLaid"] += 1
                    del self.carrying[pid]
            d = self.ledger.get(gap) or {"crossings": 0, "reserved": 0}
            return "PLEDGER crossings=%d laidCells=%d reserved=%d" % (d["crossings"], 4 * d["crossings"], d["reserved"])
        return "REFUSED: unknown %s" % m


if __name__ == "__main__":
    sys.exit(main())
