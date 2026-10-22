"""CANAL OVERFLOW live proof -- the functional script of the sheet-water layer (CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED;
design/RimMandrake/canal_overflow_flooding_2026-10-21.md §4 Stage 4 as amended by §6 items 10 and 12; owner answers §5 D1-D10;
debug_process.md: every mod ships with its script and every live session writes what it learned back into it).

  python.exe src/RimMandrake/FlowWorks/northstar/sheet_overflow_proof.py [out.json] [--origin X,Z] [--fresh-map] [--only a,b]
             [--no-perf] [--cold-ticks N]
  python3    src/RimMandrake/FlowWorks/northstar/sheet_overflow_proof.py --mock [--mock-faults a,b] [--only a,b]
             every path offline against FakeBridge (a small sheet world model, NOT the mod); every row is written SKIP with the
             verdict it would have reached kept under detail.mock (proves the script, never the game)

Run from the repo root with python.exe on the minimal list (FlowWorks); the bridge must be held. Exit 0 = every acceptance row
PASS; 1 = a FAIL; 2 = a row could not be measured. Perf rows are recorded separately (res["perf"], §6 item 12) and never
decide the exit code: the 1 ms target is PROVISIONAL. WRITTEN OFFLINE 2026-10-22 (BENCH helper; the belt held the game):
every row is OWED to its first live run.

THE C# THESE ROWS CALL: RimMandrake.FlowWorks.Sheet.RM_SheetProofs (contracts in OWED_PROOFS) -- NOT BUILT when this was
written. Stage 1 exposes no bridge-readable sheet state: RM_NorthstarProofs.ProofReadout reads the engine's DepthReadoutAt
only, never RM_MapComponent_Sheet.ReadoutAt. A live run asks ProofSheetLedger first; if the loaded FlowWorks lacks the class,
every row is UNMEASURED/HARNESS naming it and nothing is staged. Used as is beside it: RM_LineProofs.ProofPitWater (dug water
in a rect, dL), RM_NorthstarProofs.ProofPump (pour mode) / ProofResetRect, the hose probe (proof_hose.PB.hp: filltank, tank,
pump), jawa/flowworks_excavation_drive, jawa/build_batch, jawa/weather_set, jawa/game_condition, jawa/cell_temperature,
jawa/mod_settings_field, jawa/set_plants, jawa/list_things, jawa/map_info, jawa/running_mods, jawa/map_comp_timing,
rimworld/save_game, rimworld/load_game_ready.

FEATURE GATE (rows whose feature is not built read UNMEASURED/NOT_BUILT with the reason, never PASS): RM_SheetProofs.
ProofSheetFeatures says which Stage 2/3 pieces the loaded build carries. Stage 1 (water-only engine layer, 6717cd7c12) carries
the spill hooks (pump, rain, fill-in), return, losses, door leak (Kind.Door), the ice tier (TempDeciC per cell), the master
switch and persistence. NOT in stage 1: crop drowning / irrigation (Stage 2, being built in Source/Sheet/ now) and any cap
setting (SheetCapDl and MaxWetCells are kernel Params constants; Stage 3 makes them settings).

Owner rulings this proves (by card 2026-10-21/22): D1 fill-in's homeless water spills; D2 pumps, rain, floods and a higher
gravity source overflow; D3 standing overflow kills a crop only after 1 week, before that it irrigates; D4 doors leak slowly;
D6 soak / evaporation / joined-the-lake are disclosed exits; D7 OFF stops new spills and existing sheets keep draining;
D10 a sheet below 0 C freezes into its own ice tier keeping its volume and thaws back; lowering the cap stops further filling
and deeper water drains by its normal exits.

Scenes (plot coords from --origin, default 30,30; dug by jawa/flowworks_excavation_drive, 1 notch = 0.5 m = 10,000 dL/square):
  A  z=0    canal x=1..6 brim full; pump (0,0) on Pour, tank (0,-2), battery (-3,0)  -> PUMP_FULL_CANAL_SPILLS_SHEET
  B  z=12   canal x=1..6 brim full, open sky; rain locked on                        -> RAIN_FULL_CANAL_SPILLS_SHEET
  C  z=22   one brim-full square (3,22) in a ring of brim-full squares; filled in    -> FILLIN_HOMELESS_SPILLS
  D  z=32   SUPERDEEP pit x=6..8, z=31..33 empty; 30,000 dL spilled at (2,32)       -> SHEET_RETURNS_TO_PIT
  E  z=46   open soil; 20,000 dL spilled at (8,46)                                  -> SPILL_EXTENT_FINITE
  F  z=60   wall ring x=0..5, z=58..62 (yard 4x3); canal square (2,60) brim full;
            3x the yard's room offered there                                       -> BACKPRESSURE_REFUSES_DESTROYS_NOTHING
  G  z=72   wall ring x=0..4, z=70..74, a door at (4,72); 30,000 dL inside; a twin ring at z=82 with a GAP at (4,82)
                                                                                   -> DOOR_LEAKS_SLOWLY
  I  z=94   20,000 dL on soil beside an empty dug square (6,94); the switch turned OFF -> SETTING_OFF_STOPS_NEW_KEEPS_DRAINING
  J  z=104  rice x=1..4, z=103..105; 60,000 dL spilled at (0,104) (sheet tier); crop delay COMPRESSED (debug_process
            "compress first": the kernel counts the D3 timer in PULSES, so a time_set_ticks clock jump runs no pulse and can
            never age a crop)                                                       -> CROPS_IRRIGATE_THEN_DROWN
  K  z=116  20,000 dL on soil; ColdSnap + DeepFreeze until the cell reads < 0 C, then ended -> SHEET_FREEZES_AND_THAWS
  L  z=128  wall ring as F; yard at 40 cm; the cap setting lowered to 20 cm         -> LOWERED_CAP_KEEPS_DEEPER_WATER
  M  (whole run) the sheet ledger and the engine's destroyed total, start to end    -> LEDGER_CONSERVES_TO_THE_DL
  H  z=140  20,000 dL on soil; save; continue 3 pulses vs load + the same 3 pulses  -> SAVE_LOAD_CONTINUES_IDENTICAL
            (runs LAST: the load replaces the map)
  perf z=150.. concentrated (200,000 dL at one point) and scattered (40 x 5,000 dL) spills; 250^2 / 325^2 / full modpack
            context read from the map and the running mod list (§6 item 12)

Each row: PROVE (the call) / EXPECT (the bar) / LIES (how it could pass falsely), written beside it below.

ANTI-GUESSING NOTES
- "Sheet" numbers are read off the kernel through RM_SheetProofs (whole dL), never off the overlay picture or terrain: §6 item 2
  makes every tier an overlay; get_terrain_batch sees no sheet at all.
- Conservation is read as DELTAS of disclosed totals across a row (source loss == canal gain + sheet in), plus the kernel's own
  LedgerCloses, plus RM_MapComponent_Excavation.OverflowDestroyedTotal (+0 over the whole run is the bar: D1 moved fill-in's
  homeless water from 'destroyed' to the sheet).
- The master switch ships OFF until Stage 4 signs off (RM_SheetSettings.sheetOverflowEnabled, D7). Preflight turns it ON and
  restores the read-back value at the end; a set that did not read back is UNMEASURED/HARNESS for every row.
- Rain adds whole levels to brim-full canal squares (RM_MapComponent_Sheet.RainOverflow, levels * U) only on UNROOFED squares.
- UNVERIFIED LAYOUT GUESSES (first live run decides): the pump's reach covers the canal square beside it; a tank 2x2 at (0,-2)
  touches the pump; setFill=1 after deepen 1 leaves the square brim full; a door built by build_batch stands closed.
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
import validation_core as V  # noqa: E402  (preconditions: scope / require / guard; pure python, no bridge at import)

SHEET = "RimMandrake.FlowWorks.Sheet.RM_SheetProofs"            # OWED C#: contracts in OWED_PROOFS
S_SHEET = "RimMandrake.FlowWorks.Sheet.RM_SheetSettings"
LPROOF = "RimMandrake.FlowWorks.Machinery.RM_LineProofs"         # ProofPitWater
NPROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"              # ProofPump, ProofResetRect
DL_PER_CM = 200      # RM_SheetMath.DlPerCm: 1 cm over one square = 20 L
U = 10000            # dL per notch-square (RM_Volume.UnitsPerLevel; read live from the ledger's cap/notch when given)
WATER = "Water"      # proof_hose.LIQUID_WATER on a live run
STAGE_SRC = "Flood"  # staged spills enter as the driver/kit source (D2), which no stage-1 hook uses: inPump/inRain stay clean
COLD = ("ColdSnap", "DeepFreeze")
CROP = "Plant_Rice"

ROW_IDS = ["PUMP_FULL_CANAL_SPILLS_SHEET", "RAIN_FULL_CANAL_SPILLS_SHEET", "FILLIN_HOMELESS_SPILLS", "SHEET_RETURNS_TO_PIT",
           "SPILL_EXTENT_FINITE", "BACKPRESSURE_REFUSES_DESTROYS_NOTHING", "DOOR_LEAKS_SLOWLY",
           "SETTING_OFF_STOPS_NEW_KEEPS_DRAINING", "CROPS_IRRIGATE_THEN_DROWN", "SHEET_FREEZES_AND_THAWS",
           "LOWERED_CAP_KEEPS_DEEPER_WATER", "LEDGER_CONSERVES_TO_THE_DL", "SAVE_LOAD_CONTINUES_IDENTICAL"]
ROW_ITEM = {r: "CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED" for r in ROW_IDS}
# rows whose feature a Stage-1 build does not carry: the FEATURES flag that must read True before the row may score
GATED = {"CROPS_IRRIGATE_THEN_DROWN": ("crops", "Stage 2 crop effects (D3 drowning after 1 week, irrigation before) are not "
                                                "in the loaded FlowWorks"),
         "LOWERED_CAP_KEEPS_DEEPER_WATER": ("capSetting", "the sheet cap is a kernel Params constant, not a setting, until "
                                                          "Stage 3 (D10 'lowering the sheet cap')")}
PERF_IDS = ["PERF_250_CONCENTRATED", "PERF_250_SCATTERED", "PERF_325", "PERF_FULL_MODPACK"]
PERF_BAR_MS = 1.0    # §4 Stage 4 item 7, PROVISIONAL (§6 item 12): recorded, never scored into the exit code
PERF_TICKS = 1250

# The C# the rows call (RM_SheetProofs; selftest_sheet_overflow_proof checks this table is what the rows use). One string arg
# each (';' inside), one line out: a word then key=value tokens; "REFUSED: why" on bad args.
OWED_PROOFS = {
    "ProofSheetLedger": "'-' -> 'SHEETLEDGER enabled=T|F in=N inPump=N inRain=N inFlood=N inFillIn=N inGravity=N standing=N "
                        "wet=N returned=N joined=N soaked=N evaporated=N burned=N purged=N closes=T|F destroyedDl=N pulse=N "
                        "pulseTicks=N retention=N minReceive=N cap=N maxWet=N' (all dL; destroyedDl = RM_MapComponent_"
                        "Excavation.OverflowDestroyedTotal x UnitsPerLevel; params = the kernel Params in force)",
    "ProofSheetRect": "x;z;w;h -> 'SHEETRECT dl=N wet=N maxDl=N edgeMaxDl=N ice=N film=N sheet=N pool=N' (edgeMaxDl = the "
                      "deepest wet square with a dry open neighbour: the frontier)",
    "ProofSheetCell": "x,z -> 'SHEETCELL dl=N tier=None|Film|Sheet|Pool|Ice kind=Open|Blocked|Door|Grate|Receiver|Sink stand=N'",
    "ProofSheetSpill": "x,z;dl;Pump|Rain|Flood|FillIn|Gravity -> STAGING through RM_MapComponent_Sheet.Offer (the production "
                       "entry, switch respected). 'SPILL offered=N accepted=N'",
    "ProofSheetFillIn": "x,z -> the engine's own fill-in of a wet dug square (the Displace path). 'FILLIN homeless=N spilled=N "
                        "destroyed=N' (homeless = the remainder no channel took)",
    "ProofSheetHash": "'-' -> 'SHEETHASH hash=H pulse=N' (hash of RM_SheetMath.Save(state): the whole continuation state, §6 item 4)",
    "ProofSheetFeatures": "'-' -> 'FEATURES crops=T|F soak=T|F capSetting=T|F capField=NAME cropDelayField=NAME' (what the "
                          "loaded build carries; NAME = the RM_SheetSettings field a row may set, '-' when absent: "
                          "capField in cm, cropDelayField in pulses)",
    "ProofSheetPerf": "'reset' | '-' -> 'SHEETPERF pulses=N kernelMs=F pulseMs=F maxPulseMs=F allocB=N dirtySections=N "
                      "terrainWrites=N active=N wetMax=N' (since the last reset; §6 item 12 records each separately)",
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


def fnum(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


LEDGER_INTS = ("in", "inPump", "inRain", "inFlood", "inFillIn", "inGravity", "standing", "wet", "returned", "joined", "soaked",
               "evaporated", "burned", "purged", "destroyedDl", "pulse", "pulseTicks", "retention", "minReceive", "cap", "maxWet")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="30,30")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--only", default="", help="comma list of rows: " + ",".join(ROW_IDS))
    ap.add_argument("--no-perf", action="store_true", help="skip the perf rows (§6 item 12; an --only run never takes them)")
    ap.add_argument("--cold-ticks", type=int, default=24000, help="tick budget for each of freeze and thaw (row K)")
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
    out = a.out or (os.path.join(tempfile.gettempdir(), "sheet_overflow_mock_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
                    if a.mock else os.path.join(HERE, "sheet_overflow_result_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    rows, perf = [], []
    res = {"script": "sheet_overflow_proof.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "perf": perf,
           "args": vars(a), "owedProofs": sorted(OWED_PROOFS), "balances": []}
    if a.mock:
        res["mode"] = "mock"              # never 'live': validation.py refuses a result no game produced
    else:
        import driver_stamp
        driver_stamp.stamp(res, raw.call)

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        try:
            os.replace(out + ".tmp", out)
        except OSError:
            with open(out, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=1, default=str)

    def _emit(lst, rid, st, det, cls):
        st, cls, det = V.PRE.judge(st, cls, det)
        if st == "FAIL" and cls != "MOD":
            st = "UNMEASURED"                   # a SITE/HARNESS fault is never scored as a mod FAIL
        if a.mock:
            det = dict(det, mock=st)
            st = "SKIP"
        lst.append({"id": rid, "status": st, "class": cls, "item": ROW_ITEM.get(rid, ROW_ITEM[ROW_IDS[0]]), "detail": det})
        print("%-40s %-10s %-9s %s" % (rid, st, cls, json.dumps(det, default=str)[:260]), flush=True)
        save()

    def row(rid, st, det, cls="MOD"):
        _emit(rows, rid, st, det, cls)

    def prow(rid, st, det, cls="MOD"):
        det = dict(det, provisional=True, barMs=PERF_BAR_MS)
        _emit(perf, rid, st, det, cls)

    # ------------------------------------------------------------------ helpers
    def _static(ty, method, arg, answer):
        r = B.call("jawa/static_call", type=ty, method=method, args=arg) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        V.require(not txt.startswith("REFUSED"), "%s accepted its args" % method, txt[:200], cls="HARNESS")
        kv = parse(txt) if r.get("success") is True and not txt.startswith("REFUSED") else {}
        if not answer:
            V.require(kv, "%s answered" % method, txt[:200], cls="HARNESS")
        return kv, txt

    def sp(method, arg="-", answer=False):
        return _static(SHEET, method, arg, answer)

    def ledger():
        kv, txt = sp("ProofSheetLedger")
        d = {k: num(kv, k) for k in LEDGER_INTS}
        d["closes"] = kv.get("closes") == "True"
        d["enabled"] = kv.get("enabled") == "True"
        d["_txt"] = txt
        return d

    def ld(l0, l1, f):
        return None if l0.get(f) is None or l1.get(f) is None else l1[f] - l0[f]

    def srect(x0, z0, w, h):
        kv, txt = sp("ProofSheetRect", "%d;%d;%d;%d" % (P(x0, z0) + (w, h)))
        return {k: num(kv, k) for k in ("dl", "wet", "maxDl", "edgeMaxDl", "ice", "film", "sheet", "pool")}, txt

    def scell(c):
        kv, txt = sp("ProofSheetCell", xz(c))
        return kv, txt

    def spill(c, dl, src=STAGE_SRC):
        kv, txt = sp("ProofSheetSpill", "%s;%d;%s" % (xz(c), dl, src))
        return num(kv, "accepted"), txt

    def pitwater(x0, z0, w, h):
        kv, txt = _static(LPROOF, "ProofPitWater", "%d,%d,%d,%d" % (P(x0, z0) + (w, h)), False)
        return num(kv, "dl"), txt

    def dig(c, n=1, fill=-1):
        return B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=fill) or {}

    def build(*ops):
        ops = [o for o in ops if o]
        return B.call("jawa/build_batch", ops=";".join(ops), faction="player", wipeExisting=False) or {}

    def ticks(n):
        r = B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}
        V.require(r.get("success") is not False, "the clock moved %d ticks" % n, r, cls="HARNESS")
        return r.get("success") is not False

    def pulses(n):
        return ticks(n * (CTX["pulseTicks"] or 250))

    def balance(rid, what, src_loss, sinks):
        """One transfer's books, kept for the whole-run row: what left the source == what arrived, to the dL."""
        got = None if src_loss is None or any(v is None for v in sinks.values()) else sum(sinks.values())
        ok = got is not None and src_loss == got
        res["balances"].append({"row": rid, "what": what, "sourceLoss": src_loss, "arrived": sinks, "ok": ok})
        return ok

    def sset(typ, field, value):
        r = B.call("jawa/mod_settings_field", typeName=typ, action="set", field=field, value=str(value)) or {}
        back = (B.call("jawa/mod_settings_field", typeName=typ, action="get", field=field) or {}).get("value")
        V.require(str(back).lower() == str(value).lower(), "%s.%s reads back %s" % (typ.split(".")[-1], field, value),
                  [r, back], cls="HARNESS")
        return str(back).lower() == str(value).lower()

    def sget(typ, field):
        return (B.call("jawa/mod_settings_field", typeName=typ, action="get", field=field, _answer=True) or {}).get("value")

    def ring(x0, z0, x1, z1, door=None, gap=None):
        cells = V.perimeter(*(P(x0, z0) + P(x1, z1)))
        ops = []
        for c in cells:
            if door is not None and c == P(*door):
                ops.append("Door:%d,%d" % c)
            elif gap is not None and c == P(*gap):
                continue
            else:
                ops.append("Wall:%d,%d" % c)
        return build(*ops)

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)        # noqa: E731
    xz = lambda c: "%d,%d" % c                   # noqa: E731
    CTX = {"pulseTicks": None}

    # ------------------------------------------------------------------ preflight
    if a.fresh_map and not a.mock:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok = True if a.mock else V._wait_playing(B, leave_s=0)[0]
    if not ok:
        for rid in only:
            row(rid, "UNMEASURED", {"why": "no game in Playing"}, cls="HARNESS")
        return 2
    probe = B.call("jawa/static_call", type=SHEET, method="ProofSheetLedger", args="-", _answer=True) or {}
    if probe.get("success") is not True:
        res["owedWhy"] = str(probe.get("error") or probe.get("message") or probe)[:300]
        for rid in only:
            row(rid, "UNMEASURED", {"why": "%s is not in the loaded FlowWorks (%s): deploy a FlowWorks built with it"
                                           % (SHEET, res["owedWhy"][:120]), "owedProofs": sorted(OWED_PROOFS)}, cls="HARNESS")
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
        print("sheet overflow proof: %s missing -> every row UNMEASURED/HARNESS -> %s" % (SHEET, out))
        return 2
    feats = parse((B.call("jawa/static_call", type=SHEET, method="ProofSheetFeatures", args="-", _answer=True) or {})
                  .get("result") or "")
    res["features"] = feats
    if not a.mock:
        rect = (max(ox - 8, 1), max(oz - 6, 1), 30, 200)
        res["site_calm"] = V.site_calm(B)
        B.call("jawa/kill_hostiles")
        B.call("jawa/static_call", type=NPROOF, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
        site_rows = []
        with V.scope("site"):
            V.prepare_site(B, rect, site_rows, "sheet_site")
        bad = [r for r in site_rows if r.get("status") not in (None, "PASS")]
        if bad:
            for rid in only:
                row(rid, "UNMEASURED", {"why": "site not prepared", "rect": rect, "site": bad[:3]}, cls="SITE")
            return 2
        B.call("rimworld/set_god_mode", enabled=True)
        B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    switch0 = sget(S_SHEET, "sheetOverflowEnabled")
    res["switchBefore"] = switch0
    with V.scope("switch"):
        on = sset(S_SHEET, "sheetOverflowEnabled", True)
    if not on:
        for rid in only:
            row(rid, "UNMEASURED", {"why": "the master switch did not read back ON", "before": switch0}, cls="HARNESS")
        return 2
    L_START = ledger()
    CTX["pulseTicks"] = L_START.get("pulseTicks") or 250
    res["ledgerStart"] = L_START["_txt"]

    ctx = dict(a=a, B=B, P=P, xz=xz, row=row, prow=prow, sp=sp, ledger=ledger, ld=ld, srect=srect, scell=scell, spill=spill,
               pitwater=pitwater, dig=dig, build=build, ticks=ticks, pulses=pulses, balance=balance, sset=sset, sget=sget,
               ring=ring, res=res, save=save, feats=feats, L_START=L_START, CTX=CTX, only=only)
    try:
        for rid in ROW_IDS:
            if rid == "SAVE_LOAD_CONTINUES_IDENTICAL" and not a.no_perf and not a.only.strip():
                with V.scope("perf"):
                    perf_rows(ctx)
            if rid not in only:
                continue
            print("== row %s" % rid, flush=True)
            with V.scope(rid):
                gate = GATED.get(rid)
                if gate and feats.get(gate[0]) != "True":
                    row(rid, "UNMEASURED", {"why": gate[1], "features": feats}, cls="NOT_BUILT")
                    continue
                SCENES[rid](ctx)
    finally:
        if switch0 is not None:
            B.call("jawa/mod_settings_field", typeName=S_SHEET, action="set", field="sheetOverflowEnabled", value=str(switch0),
                   _answer=True)
        if not a.mock:
            B.call("jawa/weather_set", weather="Clear", lockWeather=False, _answer=True)
            V.site_calm_restore(B)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    if a.mock:
        nb = [r["id"] for r in rows if r["class"] == "NOT_BUILT"]
        bad = [r["id"] for r in rows if r["detail"].get("mock") != "PASS" and r["class"] != "NOT_BUILT"]
        print("MOCK: sheet overflow proof: %d rows (%d NOT_BUILT: %s), %d perf; mock verdicts not PASS: %s -> %s"
              % (len(rows), len(nb), nb or "none", len(perf), bad or "none", out))
        return 1 if any(r["detail"].get("mock") == "FAIL" for r in rows) else (2 if bad else 0)
    fails = [r for r in rows if r["status"] == "FAIL"]
    unm = [r for r in rows if r["status"] != "PASS"]
    print("sheet overflow proof: %d rows, %d FAIL, %d not PASS (perf recorded separately: %d) -> %s"
          % (len(rows), len(fails), len(unm), len(perf), out))
    return 1 if fails else (2 if unm else 0)


def _c(ctx, *ks):
    return [ctx[k] for k in ks]


def _canal(ctx, x0, x1, z):
    """A brim-full one-notch canal on row z, read back: every square full to the dL (U each)."""
    for x in range(x0, x1 + 1):
        ctx["dig"](ctx["P"](x, z), 1, 1)
    dl, txt = ctx["pitwater"](x0, z, x1 - x0 + 1, 1)
    V.require(dl == U * (x1 - x0 + 1), "the canal is brim full (%d dL)" % (U * (x1 - x0 + 1)), txt)
    return dl


def _poll(ctx, fn, bound_pulses):
    waited, v = 0, fn()
    while not v and waited < bound_pulses:
        if not ctx["pulses"](1):
            return v, waited
        waited += 1
        v = fn()
    return v, waited


# ====================================================================== the rows
def pump_spill(ctx):
    """PROVE a brim-full 1-notch canal x=1..6; pump (0,0) beside it on Pour (ProofPump 'pour'), tank (0,-2) holding 3 levels,
    battery charged; poll pulse by pulse (<= 4) until the ledger's inPump rises.
    EXPECT inPump > 0 within 2 pulses of the pour starting (the canal is already full, so the first pour is the spill); wet
    squares beside the canal; tank loss == canal gain + inPump gain to the dL; destroyedDl +0; closes. LIES: a pump that never
    powered moves nothing (SITE: the hose probe's powered flag); a canal that was not full takes the pour (canal read back
    brim full first); water that arrived by some other source shows in inPump only if the hook is the pump's (per-source)."""
    B, P, xz, row, ledger, ld = _c(ctx, "B", "P", "xz", "row", "ledger", "ld")
    canal0 = _canal(ctx, 1, 6, 0)
    pump, tank, bat = P(0, 0), P(0, -2), P(-3, 0)
    ctx["build"]("RM_LiquidPump:%d,%d" % pump, "RM_LiquidTank:%d,%d" % tank, "Battery:%d,%d" % bat)
    ctx["ticks"](2)
    lt = B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % bat, limit=2) or {}
    bid = ((lt.get("things") or [{}])[0]).get("id")
    V.require(bid is not None, "the battery is on the map", lt)
    if bid is not None:
        B.call("jawa/battery_set", thing=bid, mode="setPct", value=1.0)
    B.hp("filltank:%d,%d=%s,%d" % (tank + (WATER, 3 * U)))
    u0 = B.hp("tank:%d,%d" % tank).get("units")
    V.require(u0 == 3 * U, "the tank holds 3 levels", u0)
    l0 = ledger()
    pp = B.call("jawa/static_call", type=NPROOF, method="ProofPump", args="%s;pour" % xz(pump)) or {}
    powered = B.hp("pump:%d,%d" % pump).get("powered")
    V.require(powered is True, "the pump powered", powered, cls="SITE")
    got, waited = _poll(ctx, lambda: (ld(l0, ledger(), "inPump") or 0) > 0, 4)
    l1 = ledger()
    u1 = B.hp("tank:%d,%d" % tank).get("units")
    canal1, tc = ctx["pitwater"](1, 0, 6, 1)
    lips, tl = ctx["srect"](1, -1, 6, 3)
    loss = None if not isinstance(u0, int) or not isinstance(u1, int) else u0 - u1
    books = ctx["balance"]("PUMP_FULL_CANAL_SPILLS_SHEET", "tank -> canal + sheet", loss,
                           {"canal": None if canal1 is None else canal1 - canal0, "sheetPump": ld(l0, l1, "inPump")})
    good = (got and waited <= 2 and (lips.get("wet") or 0) > 0 and books and ld(l0, l1, "destroyedDl") == 0 and l1["closes"])
    row("PUMP_FULL_CANAL_SPILLS_SHEET", "PASS" if good else "FAIL",
        {"pulsesWaited": waited, "tank": [u0, u1], "canal": [canal0, canal1], "inPump": ld(l0, l1, "inPump"),
         "lips": tl, "destroyed": ld(l0, l1, "destroyedDl"), "closes": l1["closes"], "pump": pp.get("result")})


def rain_spill(ctx):
    """PROVE a brim-full canal x=1..6 on z=12 under open sky; jawa/weather_set Rain (locked); poll (<= 12 pulses) until inRain
    rises; then Clear.
    EXPECT inRain > 0; wet squares beside the canal; the canal still brim full (rain over a full canal goes to the sheet, never
    above the brim); destroyedDl +0; closes. LIES: rain on open soil makes no sheet in our model (only RainOverflow on a full
    canal does), so inRain is the bar, not wet squares alone; a roofed canal never rains (the plot is unroofed by the site)."""
    B, row, ledger, ld = _c(ctx, "B", "row", "ledger", "ld")
    canal0 = _canal(ctx, 1, 6, 12)
    l0 = ledger()
    w = B.call("jawa/weather_set", weather="Rain", lockWeather=True) or {}
    try:
        got, waited = _poll(ctx, lambda: (ld(l0, ledger(), "inRain") or 0) > 0, 12)
    finally:
        B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    l1 = ledger()
    canal1, _ = ctx["pitwater"](1, 12, 6, 1)
    lips, tl = ctx["srect"](1, 11, 6, 3)
    good = got and (lips.get("wet") or 0) > 0 and canal1 == canal0 and ld(l0, l1, "destroyedDl") == 0 and l1["closes"]
    row("RAIN_FULL_CANAL_SPILLS_SHEET", "PASS" if good else "FAIL",
        {"weather": w.get("success"), "pulsesWaited": waited, "inRain": ld(l0, l1, "inRain"), "canal": [canal0, canal1],
         "lips": tl, "destroyed": ld(l0, l1, "destroyedDl"), "closes": l1["closes"]})


def fillin_spill(ctx):
    """PROVE (D1) a 3x3 block of brim-full 1-notch squares x=2..4, z=21..23; the engine's own fill-in of the middle (3,22)
    through ProofSheetFillIn (the Displace path a player's fill-in job calls).
    EXPECT homeless > 0 (every neighbour is full, so the square's water has no channel home); spilled == homeless; destroyedDl
    +0 (the 2026-09-16 'destroyed' rule is superseded for fill-in); inFillIn rises by exactly spilled; closes. LIES: a block
    that was not full lets the water find a channel home (homeless 0 -> SITE, never a pass); a spill reported by the proof but
    not booked by the kernel (inFillIn is the second witness)."""
    row, ledger, ld, sp, P, xz = _c(ctx, "row", "ledger", "ld", "sp", "P", "xz")
    for z in (21, 22, 23):
        _canal(ctx, 2, 4, z)
    l0 = ledger()
    kv, txt = sp("ProofSheetFillIn", xz(P(3, 22)))
    homeless, spilled, destroyed = num(kv, "homeless"), num(kv, "spilled"), num(kv, "destroyed")
    V.require((homeless or 0) > 0, "the filled square's water had no channel home", txt)
    l1 = ledger()
    books = ctx["balance"]("FILLIN_HOMELESS_SPILLS", "homeless -> sheet", homeless, {"sheetFillIn": ld(l0, l1, "inFillIn")})
    good = (spilled == homeless and destroyed == 0 and books and ld(l0, l1, "destroyedDl") == 0 and l1["closes"])
    row("FILLIN_HOMELESS_SPILLS", "PASS" if good else "FAIL",
        {"fillin": txt, "inFillIn": ld(l0, l1, "inFillIn"), "destroyed": ld(l0, l1, "destroyedDl"), "closes": l1["closes"]})


def return_pit(ctx):
    """PROVE an EMPTY SUPERDEEP pit (8 notches, fill 0) x=6..8, z=31..33; 30,000 dL spilled on soil at (2,32); poll (<= 16
    pulses) until the return has run and a pulse adds <= 1% more (a wait, not the bar: the tail trickles).
    EXPECT the pit gained exactly the ledger's 'returned' delta, and > 0 (§6 item 1: sheet -> canal is an internal transfer);
    the squares on the pit's lip (x=5) hold only held moisture (<= retention: §6 item 6, mobile water returns, moisture dries in
    place); closes. LIES: water that
    soaked in also leaves the sheet (the pit's gain, not the sheet's loss, is the bar); a spill that was refused never wet the
    ground (accepted read back first)."""
    row, ledger, ld, P = _c(ctx, "row", "ledger", "ld", "P")
    for x in range(6, 9):
        for z in range(31, 34):
            ctx["dig"](P(x, z), 8, 0)
    pit0, tp0 = ctx["pitwater"](6, 31, 3, 3)
    V.require(pit0 == 0, "the pit is dug and empty", tp0)
    l0 = ledger()
    acc, ts = ctx["spill"](P(2, 32), 30000)
    V.require(acc == 30000, "the staged spill was accepted whole", ts)
    ret = l0.get("retention") or 200
    seen = [0]

    def settled():
        r = ld(l0, ledger(), "returned") or 0
        step, seen[0] = r - seen[0], r
        return r > 0 and step * 100 <= r       # the return has run and this pulse added <= 1% more
    drained, waited = _poll(ctx, settled, 16)
    edge, te = ctx["srect"](5, 31, 1, 3)
    l1 = ledger()
    pit1, tp1 = ctx["pitwater"](6, 31, 3, 3)
    gain = None if pit1 is None or pit0 is None else pit1 - pit0
    books = ctx["balance"]("SHEET_RETURNS_TO_PIT", "sheet -> pit", ld(l0, l1, "returned"), {"pit": gain})
    left, tl = ctx["srect"](0, 28, 6, 9)
    good = (gain or 0) > 0 and books and (edge.get("maxDl") or 0) <= ret and l1["closes"]
    row("SHEET_RETURNS_TO_PIT", "PASS" if good else "FAIL",
        {"pulsesWaited": waited, "settled": drained, "pitEdge": te, "pit": [pit0, pit1], "returned": ld(l0, l1, "returned"), "left": tl, "retention": ret,
         "closes": l1["closes"]})


def extent(ctx):
    """PROVE 20,000 dL spilled on open soil at (8,46); read the wet count each pulse until it is unchanged for 3 pulses running
    (bound 24 pulses).
    EXPECT growth stops; the final wet count <= ceil(V / minReceive) (§6 item 6, the corrected bound: q_min, never retention).
    The frontier depth (edgeMaxDl) is RECORDED, not barred: RM_SheetMath.Relax refuses a dry receiver any flux under q_min, so a
    frontier donor may rest above retention (up to ~5 q_min). LIES: a spread that is merely slow reads 'unchanged' for one pulse (three in
    a row are the bar); a spill that went elsewhere (refused, or ran into a channel) shrinks the count (accepted read back, and
    no dug square within the read rect)."""
    row, ledger, P, srect = _c(ctx, "row", "ledger", "P", "srect")
    l0 = ledger()
    V_dl = 20000
    acc, ts = ctx["spill"](P(8, 46), V_dl)
    V.require(acc == V_dl, "the staged spill was accepted whole", ts)
    qmin = l0.get("minReceive") or 100
    ret = l0.get("retention") or 200
    bound = int(math.ceil(V_dl / float(qmin)))
    series, same = [], 0
    for _ in range(24):
        if not ctx["pulses"](1):
            break
        r, _t = srect(-6, 38, 30, 17)
        series.append(r.get("wet"))
        same = same + 1 if len(series) > 1 and series[-1] == series[-2] else 0
        if same >= 3:
            break
    fin, tf = srect(-6, 38, 30, 17)
    good = same >= 3 and 0 < (fin.get("wet") or 0) <= bound
    row("SPILL_EXTENT_FINITE", "PASS" if good else "FAIL",
        {"wetSeries": series, "bound": bound, "minReceive": qmin, "retention": ret, "final": tf, "stableFor": same})


def backpressure(ctx):
    """PROVE a wall ring x=0..5, z=58..62 (yard x=1..4, z=59..61, 12 squares); its middle-west square (2,60) dug 1 notch brim
    full (the 'canal'); 3x the yard's room (11 squares x cap) offered there; then the same offer again.
    EXPECT accepted <= the room and < offered (the rest is REFUSED back to the caller, never destroyed); the yard holds exactly
    what was accepted (sheet dl in the yard == accepted, read before a pulse runs; nothing outside the ring after 2 pulses); the second offer accepts 0; destroyedDl +0;
    closes. LIES: a ring with a hole leaks the 'refused' water outward (wet outside the ring is read, and must be 0); a cap
    that destroys the excess still reports accepted <= room (destroyedDl and the yard's dl are the bar)."""
    row, ledger, ld, P, ring, srect = _c(ctx, "row", "ledger", "ld", "P", "ring", "srect")
    ring(0, 58, 5, 62)
    _canal(ctx, 2, 2, 60)
    l0 = ledger()
    cap = l0.get("cap") or 5000
    room = 11 * cap
    acc1, t1 = ctx["spill"](P(2, 60), 3 * room)
    acc2, t2 = ctx["spill"](P(2, 60), room)
    yard, ty = srect(1, 59, 4, 3)          # read before any pulse: no loss has run yet, so the yard holds what was accepted
    pulses_ok = ctx["pulses"](2)
    l1 = ledger()
    outside, to = srect(-2, 56, 10, 9)
    yard2, _ = srect(1, 59, 4, 3)
    out_only = None if outside.get("dl") is None or yard2.get("dl") is None else outside["dl"] - yard2["dl"]
    books = ctx["balance"]("BACKPRESSURE_REFUSES_DESTROYS_NOTHING", "offer -> yard",
                           acc1 if acc1 is None or acc2 is None else acc1 + acc2,
                           {"yard": yard.get("dl")})
    good = (pulses_ok and acc1 is not None and 0 < acc1 <= room and acc1 < 3 * room and acc2 == 0 and out_only == 0 and books
            and ld(l0, l1, "destroyedDl") == 0 and l1["closes"])
    row("BACKPRESSURE_REFUSES_DESTROYS_NOTHING", "PASS" if good else "FAIL",
        {"room": room, "offer1": t1, "offer2": t2, "yard": ty, "outsideOnly": out_only,
         "destroyed": ld(l0, l1, "destroyedDl"), "closes": l1["closes"]})


def door_leak(ctx):
    """PROVE (D4) a wall ring x=0..4, z=70..74 with a Door at (4,72), 30,000 dL spilled inside at (2,72); a twin ring at z=80..84
    with a GAP at (4,82) instead of the door, the same spill; 6 pulses.
    EXPECT water outside the door ring > 0 (it leaks: doors do not seal) AND the door ring's inside lost less than a quarter of
    what the gap ring's inside lost (slowly); closes. LIES: a door that stood open passes the full flux (the cell's kind must
    read Door); a gap ring whose water stays put (nothing to compare) is SITE, never a pass."""
    row, ledger, P, ring, srect, scell = _c(ctx, "row", "ledger", "P", "ring", "srect", "scell")
    ring(0, 70, 4, 74, door=(4, 72))
    ring(0, 80, 4, 84, gap=(4, 82))
    ctx["ticks"](2)
    kd, td = scell(P(4, 72))
    V.require(kd.get("kind") == "Door", "the ring's opening is a closed door", td)
    a1, ta = ctx["spill"](P(2, 72), 30000)
    a2, tb = ctx["spill"](P(2, 82), 30000)
    V.require(a1 == 30000 and a2 == 30000, "both staged spills accepted whole", [ta, tb])
    d0, _ = srect(1, 71, 3, 3)
    g0, _ = srect(1, 81, 3, 3)
    ctx["pulses"](6)
    d1, td1 = srect(1, 71, 3, 3)
    g1, tg1 = srect(1, 81, 3, 3)
    outside_door, tod = srect(5, 69, 4, 7)
    l1 = ledger()
    dl_door = None if d0.get("dl") is None or d1.get("dl") is None else d0["dl"] - d1["dl"]
    dl_gap = None if g0.get("dl") is None or g1.get("dl") is None else g0["dl"] - g1["dl"]
    V.require((dl_gap or 0) > 0, "the gap ring drains (the comparison exists)", tg1)
    good = ((outside_door.get("dl") or 0) > 0 and dl_door is not None and dl_gap and dl_door * 4 < dl_gap and l1["closes"])
    row("DOOR_LEAKS_SLOWLY", "PASS" if good else "FAIL",
        {"door": td, "doorRingLost": dl_door, "gapRingLost": dl_gap, "outsideDoor": tod, "inside": [td1, tg1],
         "closes": l1["closes"]})


def setting_off(ctx):
    """PROVE (D7) 20,000 dL spilled on soil at (2,94) beside an empty dug square (6,94) (1 notch); 1 pulse; the master switch set
    OFF (read back); a new 10,000 dL offer; 6 pulses; the switch back ON.
    EXPECT the offer accepts 0 (no new spill); standing falls and returned + soaked + evaporated rise over the 6 pulses (the
    existing sheet keeps draining); purged +0 (turning OFF never deletes water); closes. LIES: a switch that never turned off
    accepts 0 for another reason (read back is the gate); a sheet that 'drained' by a purge (purged is the bar)."""
    row, ledger, ld, P, sset = _c(ctx, "row", "ledger", "ld", "P", "sset")
    ctx["dig"](P(6, 94), 1, 0)
    acc, ts = ctx["spill"](P(2, 94), 20000)
    V.require(acc == 20000, "the staged spill was accepted whole", ts)
    ctx["pulses"](1)
    l0 = ledger()
    off = sset(S_SHEET, "sheetOverflowEnabled", False)
    try:
        acc2, t2 = ctx["spill"](P(2, 94), 10000)
        ctx["pulses"](6)
        l1 = ledger()
    finally:
        sset(S_SHEET, "sheetOverflowEnabled", True)
    exits = sum((ld(l0, l1, k) or 0) for k in ("returned", "soaked", "evaporated"))
    good = (off and acc2 == 0 and ld(l0, l1, "standing") is not None and ld(l0, l1, "standing") < 0 and exits > 0
            and ld(l0, l1, "purged") == 0 and ld(l0, l1, "in") == 0 and l1["closes"])
    row("SETTING_OFF_STOPS_NEW_KEEPS_DRAINING", "PASS" if good else "FAIL",
        {"offerWhileOff": t2, "standing": [l0.get("standing"), l1.get("standing")], "exits": exits,
         "purged": ld(l0, l1, "purged"), "in": ld(l0, l1, "in"), "closes": l1["closes"]})


def crops(ctx):
    """PROVE (D3) rice x=1..4, z=103..105 (growth 0.3); the crop-drowning delay setting (FEATURES cropDelayField) COMPRESSED to
    its smallest value and read back; 60,000 dL spilled at (0,104) so the rice squares stand at sheet tier; poll pulse by pulse.
    EXPECT before the compressed delay: every rice plant alive and the soak (irrigation) total risen; after it: every rice plant
    on a square read at sheet tier (or deeper) after the first pulse dead, every one on a film square alive (a film irrigates); then the shipped delay restored and read back as 1 week (60,000 x 7 ticks). LIES: a clock jump ages
    nothing (the kernel counts PULSES); a film that never reached sheet tier never drowns (tier read back first); rice that died
    of something else (cold, blight) dies with no sheet too (a dry control row x=1..4, z=108 must stay alive)."""
    B, row, ledger, ld, P, feats, sset, sget = _c(ctx, "B", "row", "ledger", "ld", "P", "feats", "sset", "sget")
    field = feats.get("cropDelayField")
    V.require(field and field != "-", "the build names its crop-delay setting", feats, cls="HARNESS")
    shipped = sget(S_SHEET, field)
    B.call("jawa/set_plants", ops="%s:%d,%d,4,3" % ((CROP,) + P(1, 103)), growth=0.3)
    B.call("jawa/set_plants", ops="%s:%d,%d,4,1" % ((CROP,) + P(1, 108)), growth=0.3)
    sset(S_SHEET, field, 2)
    try:
        l0 = ledger()
        acc, ts = ctx["spill"](P(0, 104), 60000)
        V.require(acc == 60000, "the staged spill was accepted whole", ts)
        ctx["pulses"](1)
        rice = [P(x, z) for x in range(1, 5) for z in range(103, 106)]
        tiers = {c: ctx["scell"](c)[0].get("tier") for c in rice}
        deep = [c for c in rice if tiers[c] in ("Sheet", "Pool")]
        film = [c for c in rice if tiers[c] in ("Film", "None")]
        tt = {"sheet": len(deep), "film": len(film)}
        V.require(deep, "some rice stands at sheet tier", tiers)

        def alive(rect):
            lt = B.call("jawa/list_things", defName=CROP, rect="%d,%d,%d,%d" % rect, limit=50) or {}
            return len(lt.get("things") or [])
        early = alive(P(1, 103) + (4, 3))
        soak_early = ld(l0, ledger(), "soaked")
        dead, waited = _poll(ctx, lambda: sum(alive(c + (1, 1)) for c in deep) == 0, 6)
        film_alive = sum(alive(c + (1, 1)) for c in film)
        control = alive(P(1, 108) + (4, 1))
    finally:
        if shipped is not None:
            sset(S_SHEET, field, shipped)
    good = early == 12 and (soak_early or 0) > 0 and dead and film_alive == len(film) and control == 4
    row("CROPS_IRRIGATE_THEN_DROWN", "PASS" if good else "FAIL",
        {"field": field, "shipped": shipped, "aliveEarly": early, "soakedEarly": soak_early, "drownedAfterPulses": waited,
         "filmAlive": film_alive, "control": control, "tiers": tt})


def freeze(ctx):
    """PROVE (D10) 20,000 dL on soil at (4,116); 2 pulses (it settles); ColdSnap + DeepFreeze started; poll in 500-tick steps
    (<= --cold-ticks) until the cell reads < 0 C and the rect reads ice > 0; then the conditions ended and poll (<= --cold-ticks)
    until ice == 0.
    EXPECT frozen: ice == wet (every wet square), the sheet's dL + its losses unchanged across the freeze (volume kept: standing
    falls only by soaked+evaporated, which are x0 at or below 0 C), wet count unchanged while frozen (ice does not flow);
    thawed: ice 0 and water standing again; closes. LIES: a map that never got cold (SITE: the cell temperature is read); a
    stale vanilla ThinIce is not our tier (our tier is read off the kernel, not terrain)."""
    B, row, ledger, ld, P, srect, a = _c(ctx, "B", "row", "ledger", "ld", "P", "srect", "a")
    acc, ts = ctx["spill"](P(4, 116), 20000)
    V.require(acc == 20000, "the staged spill was accepted whole", ts)
    ctx["pulses"](2)
    cell = "%d,%d" % P(4, 116)
    gcs = [B.call("jawa/game_condition", action="start", condition=n, durationTicks=60000) or {} for n in COLD]
    froze, temps, fr, thaw = None, [], {}, None
    try:
        l0, r0 = ledger(), srect(-2, 110, 14, 13)[0]
        for k in range(0, a.cold_ticks, 500):
            ctx["ticks"](500)
            temps.append(fnum((B.call("jawa/cell_temperature", cell=cell) or {}).get("temperature")))
            fr, _ = srect(-2, 110, 14, 13)
            if (fr.get("ice") or 0) > 0 and fr.get("ice") == fr.get("wet"):
                froze = k + 500
                break
        V.require(any(t is not None and t < 0 for t in temps), "the spill's square got below 0 C", temps[-6:])
        l1 = ledger()
        ctx["pulses"](2)
        fr2, _ = srect(-2, 110, 14, 13)
        l2 = ledger()
    finally:
        for n in COLD:
            B.call("jawa/game_condition", action="end", condition=n, _answer=True)
    for k in range(0, a.cold_ticks, 500):
        ctx["ticks"](500)
        th, _ = srect(-2, 110, 14, 13)
        if (th.get("ice") or 0) == 0:
            thaw = k + 500
            break
    l3 = ledger()
    th, tth = srect(-2, 110, 14, 13)
    kept = (ld(l1, l2, "standing") == 0 and ld(l1, l2, "soaked") == 0 and ld(l1, l2, "evaporated") == 0
            and (fr2.get("wet") == fr.get("wet")))
    vol = None if ld(l0, l1, "standing") is None else ld(l0, l1, "standing") + (ld(l0, l1, "soaked") or 0) + \
        (ld(l0, l1, "evaporated") or 0) + (ld(l0, l1, "returned") or 0)
    good = (froze is not None and kept and vol == 0 and thaw is not None and (th.get("dl") or 0) > 0
            and (th.get("ice") or 0) == 0 and l3["closes"])
    row("SHEET_FREEZES_AND_THAWS", "PASS" if good else "FAIL",
        {"conditions": [g.get("success") for g in gcs], "frozeAfterTicks": froze, "temps": temps[-8:], "frozen": fr,
         "frozenLater": fr2, "keptWhileFrozen": kept, "volumeDelta": vol, "thawAfterTicks": thaw, "thawed": tth,
         "closes": l3["closes"]})


def lowered_cap(ctx):
    """PROVE (D10) a wall ring x=0..5, z=126..130 (yard 4x3); 8,000 dL per yard square offered at (2,128) (40 cm); the cap
    setting (FEATURES capField, in cm) lowered to 20 cm (4,000 dL) and read back; a further 10,000 dL offered; 4 pulses; the shipped
    cap restored.
    EXPECT the further offer accepts 0 (no new filling above the lowered cap); the yard's water is NOT cut to the new cap (its
    dl falls by no more than the map's soaked+evaporated, and squares stay deeper than the new cap); purged and destroyedDl +0;
    closes. LIES: a yard whose water ran out through a gap
    (outside the ring reads 0); a cap setting that did not read back (HARNESS)."""
    row, ledger, ld, P, ring, srect, feats, sset, sget = _c(ctx, "row", "ledger", "ld", "P", "ring", "srect", "feats", "sset",
                                                             "sget")
    field = feats.get("capField")
    V.require(field and field != "-", "the build names its sheet-cap setting", feats, cls="HARNESS")
    ring(0, 126, 5, 130)
    acc, ts = ctx["spill"](P(2, 128), 12 * 40 * DL_PER_CM)
    V.require(acc == 12 * 40 * DL_PER_CM, "the yard filled to 40 cm", ts)
    ctx["pulses"](1)
    shipped = sget(S_SHEET, field)
    l0, y0 = ledger(), srect(1, 127, 4, 3)[0]
    sset(S_SHEET, field, 20)
    try:
        acc2, t2 = ctx["spill"](P(2, 128), 10000)
        ctx["pulses"](4)
        l1 = ledger()
        y1, ty1 = srect(1, 127, 4, 3)
    finally:
        if shipped is not None:
            sset(S_SHEET, field, shipped)
    fell = None if y0.get("dl") is None or y1.get("dl") is None else y0["dl"] - y1["dl"]
    losses = (ld(l0, l1, "soaked") or 0) + (ld(l0, l1, "evaporated") or 0)
    good = (acc2 == 0 and fell is not None and 0 <= fell <= losses and (y1.get("maxDl") or 0) > 20 * DL_PER_CM and ld(l0, l1, "purged") == 0
            and ld(l0, l1, "destroyedDl") == 0 and l1["closes"])
    row("LOWERED_CAP_KEEPS_DEEPER_WATER", "PASS" if good else "FAIL",
        {"field": field, "shipped": shipped, "offerAfterLower": t2, "yardFell": fell, "losses": losses, "yard": ty1,
         "closes": l1["closes"]})


def conserve(ctx):
    """PROVE the ledger at the start of the run (after preflight) and now, plus every transfer balance the rows booked.
    EXPECT the kernel's LedgerCloses (In == Standing + every disclosed exit, to the dL); the run's In delta == Standing delta +
    the exits' deltas; destroyedDl +0 over the whole run (no undisclosed exit); every booked balance ok. LIES: a ledger read
    that failed reads None, never 0 (None is UNMEASURED); a run that measured no transfer proves nothing (>= 1 balance)."""
    row, ledger, ld, res, L0 = _c(ctx, "row", "ledger", "ld", "res", "L_START")
    l1 = ledger()
    exits = ("returned", "joined", "soaked", "evaporated", "burned", "purged")
    d_in, d_st = ld(L0, l1, "in"), ld(L0, l1, "standing")
    d_out = None if any(ld(L0, l1, k) is None for k in exits) else sum(ld(L0, l1, k) for k in exits)
    V.require(d_in is not None and d_st is not None and d_out is not None, "the ledger read both ends", l1["_txt"],
              cls="HARNESS")
    bal = res["balances"]
    V.require(len(bal) >= 1, "at least one transfer was booked this run", bal)
    bad = [b for b in bal if not b["ok"]]
    good = l1["closes"] and d_in == (d_st or 0) + (d_out or 0) and ld(L0, l1, "destroyedDl") == 0 and not bad
    row("LEDGER_CONSERVES_TO_THE_DL", "PASS" if good else "FAIL",
        {"in": d_in, "standing": d_st, "exits": d_out, "destroyed": ld(L0, l1, "destroyedDl"), "closes": l1["closes"],
         "balances": len(bal), "badBalances": bad[:4], "ledgerEnd": l1["_txt"]})


def save_load(ctx):
    """PROVE (§6 item 4) 20,000 dL on soil at (4,140); 2 pulses; hash h0; save; 3 pulses -> hash hA; load; hash h0'; the same 3
    pulses -> hash hB.
    EXPECT h0' == h0 (the save holds the whole state) and hB == hA (continue-uninterrupted == save/load-then-continue: the
    future trajectory, not just the hash); closes after the load. LIES: a hash of the dl grid alone misses loss remainders and
    hysteresis (the owed hash is of RM_SheetMath.Save: the whole continuation state); a save or load the bridge refused is
    UNMEASURED. Runs LAST: the load replaces the map every later row would use."""
    B, row, ledger, P, sp, a = _c(ctx, "B", "row", "ledger", "P", "sp", "a")
    acc, ts = ctx["spill"](P(4, 140), 20000)
    V.require(acc == 20000, "the staged spill was accepted whole", ts)
    ctx["pulses"](2)
    h0 = sp("ProofSheetHash")[0].get("hash")
    name = "RM_SHEET_OVERFLOW_%s" % time.strftime("%Y%m%dT%H%M%S")
    sv = B.call("rimworld/save_game", saveName=name) or {}
    V.require(sv.get("success") is not False, "saved", sv, cls="HARNESS")
    ctx["pulses"](3)
    ha = sp("ProofSheetHash")[0].get("hash")
    ldr = B.call("rimworld/load_game_ready", saveName=name, timeoutMs=280000) or {}
    V.require(ldr.get("success") is not False, "loaded", str(ldr)[:300], cls="HARNESS")
    if not a.mock:
        V.require(V._wait_playing(B, leave_s=0)[0], "playing after the load", None, cls="HARNESS")
        for _ in range(60):             # load_game_ready can answer while the load's long event still runs (live 2026-10-22)
            r = B.call("jawa/static_call", type=SHEET, method="ProofSheetHash", args="-", _answer=True) or {}
            if str(r.get("result") or "").startswith("SHEETHASH"):
                break
            time.sleep(2)
    h0b = sp("ProofSheetHash")[0].get("hash")
    ctx["pulses"](3)
    hb = sp("ProofSheetHash")[0].get("hash")
    l1 = ledger()
    good = h0 is not None and h0b == h0 and ha is not None and hb == ha and l1["closes"]
    row("SAVE_LOAD_CONTINUES_IDENTICAL", "PASS" if good else "FAIL",
        {"h0": h0, "h0AfterLoad": h0b, "hContinued": ha, "hLoadedContinued": hb, "closes": l1["closes"], "save": name})


def perf_rows(ctx):
    """§6 item 12: kernel time, total pulse time, frame spikes (maxPulseMs), allocations, dirty sections and terrain writes, each
    recorded SEPARATELY, on concentrated and scattered spills, with the map size and the mod list named. The 1 ms target is
    PROVISIONAL: these rows never decide the exit code. 325^2 and the full modpack are recorded only when the map / mod list IS
    that (else UNMEASURED/SITE naming what it is)."""
    B, P, sp, prow, a = _c(ctx, "B", "P", "sp", "prow", "a")
    mi = B.call("jawa/map_info", _answer=True) or {}
    size = mi.get("size") or [mi.get("width"), mi.get("height")]
    rm = B.call("jawa/running_mods", _answer=True) or {}
    nmods = len(rm.get("mods") or []) or None

    def sample(stage):
        sp("ProofSheetPerf", "reset")
        stage()
        tm = B.call("jawa/map_comp_timing", ticks=PERF_TICKS, _answer=True) or {}
        kv, txt = sp("ProofSheetPerf", "-")
        comp = [t for t in (tm.get("types") or []) if "RM_MapComponent_Excavation" in str(t.get("type"))]
        return kv, txt, (comp[0].get("sumMsPerTick") if comp else None)

    def verdict(kv):
        ms = fnum(kv.get("pulseMs"))
        return "UNMEASURED" if ms is None else ("PASS" if ms < PERF_BAR_MS else "FAIL")

    def conc():
        ctx["spill"](P(8, 160), 200000)

    def scat():
        for i in range(40):
            ctx["spill"](P(-4 + (i % 8) * 3, 150 + (i // 8) * 6), 5000)
    for rid, stage in (("PERF_250_CONCENTRATED", conc), ("PERF_250_SCATTERED", scat)):
        kv, txt, comp = sample(stage)
        V.require(kv.get("pulses") not in (None, "0"), "pulses ran while sampling", txt, cls="HARNESS")
        prow(rid, verdict(kv), {"sheetPerf": txt, "excavationMsPerTick": comp, "map": size, "mods": nmods,
                                "ticks": PERF_TICKS})
    for rid, want, have in (("PERF_325", "a 325x325 map", size and size[0] == 325),
                            ("PERF_FULL_MODPACK", "the owner's full mod list", nmods is not None and nmods > 100)):
        if not have:
            prow(rid, "UNMEASURED", {"why": "this run is not on %s" % want, "map": size, "mods": nmods}, cls="SITE")
            continue
        kv, txt, comp = sample(conc)
        prow(rid, verdict(kv), {"sheetPerf": txt, "excavationMsPerTick": comp, "map": size, "mods": nmods})


SCENES = {"PUMP_FULL_CANAL_SPILLS_SHEET": pump_spill, "RAIN_FULL_CANAL_SPILLS_SHEET": rain_spill,
          "FILLIN_HOMELESS_SPILLS": fillin_spill, "SHEET_RETURNS_TO_PIT": return_pit, "SPILL_EXTENT_FINITE": extent,
          "BACKPRESSURE_REFUSES_DESTROYS_NOTHING": backpressure, "DOOR_LEAKS_SLOWLY": door_leak,
          "SETTING_OFF_STOPS_NEW_KEEPS_DRAINING": setting_off, "CROPS_IRRIGATE_THEN_DROWN": crops,
          "SHEET_FREEZES_AND_THAWS": freeze, "LOWERED_CAP_KEEPS_DEEPER_WATER": lowered_cap,
          "LEDGER_CONSERVES_TO_THE_DL": conserve, "SAVE_LOAD_CONTINUES_IDENTICAL": save_load}


# ====================================================================== offline stand-in
class FakeBridge(object):
    """A small sheet world answering in the shapes the live tools and the OWED proofs are specified to: dug squares (depth,
    water dL), the sheet (dL per undug square), walls and doors, a pump with its tank, rain, temperature, the master switch, a
    250-tick pulse (pump, rain, relax, return, soak, freeze), a save slot. It knows nothing about the game; a mock verdict proves
    the script's control flow and its MOD/SITE/HARNESS/NOT_BUILT split only. `faults` inject one wrong behaviour each:
      no_proofs          RM_SheetProofs is not loaded: every row UNMEASURED/HARNESS, none FAIL
      noclock            step_game_ticks refuses: rows that wait on the clock are UNMEASURED/HARNESS
      canal_not_full     the canal staging leaves the squares short (SITE)      -> PUMP_FULL... UNMEASURED/SITE
      pump_no_spill      MOD: a backed-up pump offers nothing to the sheet      -> PUMP_FULL_CANAL_SPILLS_SHEET FAIL
      pump_leaks         MOD: the tank is debited 1 dL more than arrived        -> PUMP_FULL_CANAL_SPILLS_SHEET FAIL
      rain_no_spill      MOD: rain on a full canal is skipped                    -> RAIN_FULL_CANAL_SPILLS_SHEET FAIL
      fillin_destroys    MOD: fill-in's homeless water is destroyed (pre-D1)    -> FILLIN_HOMELESS_SPILLS FAIL
      no_return          MOD: a sheet beside an empty pit never runs in         -> SHEET_RETURNS_TO_PIT FAIL
      unbounded          MOD: dust-thin squares are wetted (no q_min)           -> SPILL_EXTENT_FINITE FAIL
      cap_destroys       MOD: an offer past the cap is accepted and destroyed   -> BACKPRESSURE... FAIL
      door_seals         MOD: a door passes nothing                             -> DOOR_LEAKS_SLOWLY FAIL
      door_open          MOD: a door passes the full flux                       -> DOOR_LEAKS_SLOWLY FAIL
      off_still_spills   MOD: the switch OFF still accepts new spills           -> SETTING_OFF... FAIL
      off_purges         MOD: the switch OFF deletes standing water             -> SETTING_OFF... FAIL
      no_freeze          MOD: the sheet never freezes                           -> SHEET_FREEZES_AND_THAWS FAIL
      ice_loses          MOD: frozen squares keep soaking                       -> SHEET_FREEZES_AND_THAWS FAIL
      never_cold         the map never gets below 0 C (SITE)                    -> SHEET_FREEZES_AND_THAWS UNMEASURED/SITE
      ledger_open        MOD: every 7th soaked dL goes uncounted                -> LEDGER_CONSERVES_TO_THE_DL FAIL
      load_drift         MOD: the load drops the loss remainders                -> SAVE_LOAD_CONTINUES_IDENTICAL FAIL
      crops_built        Stage 2 crops present (FEATURES crops=True)           -> CROPS_IRRIGATE_THEN_DROWN measured
      crop_never_dies    MOD (with crops_built): standing water never drowns   -> CROPS_IRRIGATE_THEN_DROWN FAIL
      cap_setting_built  Stage 3 cap setting present (FEATURES capSetting=True) -> LOWERED_CAP... measured
      cap_lower_cuts     MOD (with cap_setting_built): lowering cuts the water -> LOWERED_CAP_KEEPS_DEEPER_WATER FAIL"""
    FAULTS = ("no_proofs", "noclock", "canal_not_full", "pump_no_spill", "pump_leaks", "rain_no_spill", "fillin_destroys",
              "no_return", "unbounded", "cap_destroys", "door_seals", "door_open", "off_still_spills", "off_purges",
              "no_freeze", "ice_loses", "never_cold", "ledger_open", "load_drift", "crops_built", "crop_never_dies",
              "cap_setting_built", "cap_lower_cuts")
    RET, QMIN, PULSE, SOAK = 200, 100, 250, 3   # dL (the kernel Params: retention 1 cm, q_min 0.5 cm); soak a pulse

    def __init__(self, faults=()):
        self.f = set(faults)
        self.dug = {}           # cell -> [depth notches, water dL]
        self.sheet = {}         # cell -> dL
        self.walls, self.doors = set(), set()
        self.tanks, self.pumps, self.batteries = {}, {}, set()
        self.led = {k: 0 for k in ("inPump", "inRain", "inFlood", "inFillIn", "inGravity", "returned", "joined", "soaked",
                                   "evaporated", "burned", "purged", "destroyedDl", "unbooked")}
        self.rem = 0            # soak remainder (continuation state the save must keep)
        self.tick, self.pulse = 0, 0
        self.rain, self.cold_since, self.warm_since, self.temp = False, None, None, 20.0
        self.settings = {"sheetOverflowEnabled": "False", "cropDrownPulses": "2016", "sheetCapCm": "50"}
        self.cap_cm = 50
        self.plants = {}        # cell -> stand pulses
        self.saved = None
        self.nid = 1000

    # ---- the world
    def _open(self, c):
        return c not in self.walls and c not in self.dug

    def _cap(self):
        return self.cap_cm * DL_PER_CM

    def _nbrs(self, c):
        x, z = c
        return [(x, z + 1), (x + 1, z), (x, z - 1), (x - 1, z)]

    def _enabled(self):
        return self.settings["sheetOverflowEnabled"] == "True"

    def _lips(self, origin):
        """origin's channel body walked outward, its open undug neighbours nearest first (or origin itself when undug), then
        open squares outward from those, 16 at most (the kernel's MaxLips)."""
        if origin in self.dug:
            body, q, seen = [], [origin], {origin}
            while q:
                c = q.pop(0)
                body.append(c)
                for n in self._nbrs(c):
                    if n in self.dug and n not in seen:
                        seen.add(n)
                        q.append(n)
            start = []
            for c in body:
                for n in self._nbrs(c):
                    if self._open(n) and n not in start:
                        start.append(n)
        else:
            start = [origin] if self._open(origin) else []
        out, q, seen = [], list(start), set(start)
        while q and len(out) < 16:
            c = q.pop(0)
            out.append(c)
            for n in self._nbrs(c):
                if self._open(n) and n not in seen:
                    seen.add(n)
                    q.append(n)
        return out

    def offer(self, origin, dl, src):
        if not self._enabled() and "off_still_spills" not in self.f:
            return 0
        got = 0
        for c in self._lips(origin):
            room = max(0, self._cap() - self.sheet.get(c, 0))
            k = min(room, dl - got)
            if k > 0:
                self.sheet[c] = self.sheet.get(c, 0) + k
                got += k
            if got >= dl:
                break
        if "cap_destroys" in self.f and got < dl:
            self.led["destroyedDl"] += dl - got
            self.led["in" + src] += got
            return dl
        self.led["in" + src] += got
        return got

    def _flux(self, a, b, f):
        if a in self.doors or b in self.doors:
            if "door_seals" in self.f:
                return 0
            if "door_open" not in self.f:
                return f * 50 // 1000
        return f

    def _pulse(self):
        self.pulse += 1
        frozen = self.temp < 0 and "no_freeze" not in self.f
        for root, p in self.pumps.items():
            if not p["pour"] or self.tanks.get(p["tank"], 0) < U:
                continue
            canal = [c for c in self.dug if max(abs(c[0] - root[0]), abs(c[1] - root[1])) <= 1]
            roomy = [c for c in canal if self.dug[c][1] < self.dug[c][0] * U]
            if roomy:
                c = roomy[0]
                k = min(U, self.dug[c][0] * U - self.dug[c][1])
                self.dug[c][1] += k
                self.tanks[p["tank"]] -= k
            elif canal and "pump_no_spill" not in self.f:
                got = self.offer(canal[0], U, "Pump")
                if got == U:
                    self.tanks[p["tank"]] -= U + (1 if "pump_leaks" in self.f else 0)
        if self.rain and "rain_no_spill" not in self.f:
            for c, (d, w) in list(self.dug.items()):
                if d == 1 and w >= U:
                    self.offer(c, 500, "Rain")
        if not frozen:
            for _ in range(3):
                snap = dict(self.sheet)
                moves = []
                for c, h in snap.items():
                    if h <= self.RET:
                        continue
                    outs = []
                    for n in self._nbrs(c):
                        if not self._open(n):
                            continue
                        hn = snap.get(n, 0)
                        f = self._flux(c, n, max(0, h - hn) // 5)
                        f = 1 if f < 1 and h - hn >= 2 else f
                        door = c in self.doors or n in self.doors
                        if hn == 0 and f < (1 if door else self.QMIN) and "unbounded" not in self.f:
                            f = 0
                        f = min(f, self._cap() - hn)
                        if f > 0:
                            outs.append((n, f))
                    tot = sum(f for _, f in outs)
                    lim = h - self.RET
                    for n, f in outs:
                        moves.append((c, n, f if tot <= lim else f * lim // tot))
                for c, n, f in moves:
                    if f > 0:
                        self.sheet[c] -= f
                        self.sheet[n] = self.sheet.get(n, 0) + f
                if "unbounded" in self.f:     # no q_min: every wet square dusts its dry neighbours, so the spread never stops
                    for c, h in list(self.sheet.items()):
                        for n in self._nbrs(c):
                            if self._open(n) and self.sheet.get(n, 0) == 0 and self.sheet.get(c, 0) > 20:
                                self.sheet[c] -= 10
                                self.sheet[n] = 10
            if "no_return" not in self.f:
                for c in list(self.sheet):
                    for n in self._nbrs(c):
                        if n in self.dug and self.sheet.get(c, 0) > self.RET:
                            room = self.dug[n][0] * U - self.dug[n][1]
                            k = min(room, self.sheet[c] - self.RET)
                            if k > 0:
                                self.dug[n][1] += k
                                self.sheet[c] -= k
                                self.led["returned"] += k
        for c in list(self.sheet):
            if frozen and "ice_loses" not in self.f:
                break
            k = min(self.SOAK, self.sheet[c])
            self.sheet[c] -= k
            self.rem += 1
            if "ledger_open" in self.f and self.rem % 7 == 0:
                self.led["unbooked"] += k
            else:
                self.led["soaked"] += k
        for c, d in list(self.plants.items()):
            if self.sheet.get(c, 0) >= 600 and "crop_never_dies" not in self.f:
                self.plants[c] = d + 1
                if self.plants[c] > int(self.settings["cropDrownPulses"]):
                    del self.plants[c]
        self.sheet = {c: h for c, h in self.sheet.items() if h > 0}

    def _advance(self, n):
        for _ in range(n):
            self.tick += 1
            if self.cold_since is not None:
                self.temp = 20.0 - 40.0 * min(1.0, (self.tick - self.cold_since) / 6000.0)
                if "never_cold" in self.f:
                    self.temp = max(self.temp, 2.0)
            elif self.warm_since is not None:
                self.temp = min(20.0, self.temp + 0.02)
            if self.tick % self.PULSE == 0:
                self._pulse()

    def _ledger(self):
        L = self.led
        ins = sum(L[k] for k in ("inPump", "inRain", "inFlood", "inFillIn", "inGravity"))
        st = sum(self.sheet.values())
        outs = sum(L[k] for k in ("returned", "joined", "soaked", "evaporated", "burned", "purged"))
        return ("SHEETLEDGER enabled=%s in=%d inPump=%d inRain=%d inFlood=%d inFillIn=%d inGravity=%d standing=%d wet=%d "
                "returned=%d joined=%d soaked=%d evaporated=%d burned=%d purged=%d closes=%s destroyedDl=%d pulse=%d "
                "pulseTicks=%d retention=%d minReceive=%d cap=%d maxWet=4000"
                % (self._enabled(), ins, L["inPump"], L["inRain"], L["inFlood"], L["inFillIn"], L["inGravity"], st,
                   len(self.sheet), L["returned"], L["joined"], L["soaked"], L["evaporated"], L["burned"], L["purged"],
                   ins == st + outs, L["destroyedDl"], self.pulse, self.PULSE, self.RET, self.QMIN, self._cap()))

    def _rect(self, x, z, w, h):
        cells = [(i, j) for i in range(x, x + w) for j in range(z, z + h)]
        wet = [c for c in cells if self.sheet.get(c, 0) > 0]
        edge = [self.sheet[c] for c in wet if any(self._open(n) and self.sheet.get(n, 0) == 0 for n in self._nbrs(c))]
        frozen = self.temp < 0 and "no_freeze" not in self.f
        return ("SHEETRECT dl=%d wet=%d maxDl=%d edgeMaxDl=%d ice=%d film=0 sheet=0 pool=0"
                % (sum(self.sheet[c] for c in wet), len(wet), max([self.sheet[c] for c in wet] or [0]), max(edge or [0]),
                   len(wet) if frozen else 0))

    def _hash(self):
        return "%x" % (hash((tuple(sorted(self.sheet.items())), self.rem, tuple(sorted(self.led.items())))) & 0xffffffff)

    def _snapshot(self):
        return json.loads(json.dumps({"sheet": [[list(c), h] for c, h in self.sheet.items()], "rem": self.rem, "led": self.led,
                                      "dug": [[list(c), v] for c, v in self.dug.items()], "pulse": self.pulse,
                                      "tick": self.tick}))

    def _restore(self, s):
        self.sheet = {tuple(c): h for c, h in s["sheet"]}
        self.rem = 0 if "load_drift" in self.f else s["rem"]
        self.led = dict(s["led"])
        self.dug = {tuple(c): list(v) for c, v in s["dug"]}
        self.pulse, self.tick = s["pulse"], s["tick"]

    @staticmethod
    def _xz(s):
        x, z = s.split(",")[:2]
        return int(x), int(z)

    def _static(self, ty, method, arg):
        if ty == SHEET:
            if "no_proofs" in self.f:
                return {"success": False, "error": "type %s not found" % SHEET}
            if method == "ProofSheetLedger":
                return self._ledger()
            if method == "ProofSheetFeatures":
                return ("FEATURES crops=%s soak=%s capSetting=%s capField=%s cropDelayField=%s"
                        % ("crops_built" in self.f, "crops_built" in self.f, "cap_setting_built" in self.f,
                           "sheetCapCm" if "cap_setting_built" in self.f else "-",
                           "cropDrownPulses" if "crops_built" in self.f else "-"))
            if method == "ProofSheetRect":
                x, z, w, h = (int(v) for v in arg.split(";"))
                return self._rect(x, z, w, h)
            if method == "ProofSheetCell":
                c = self._xz(arg)
                h = self.sheet.get(c, 0)
                tier = "Ice" if h and self.temp < 0 else ("Pool" if h >= 3000 else "Sheet" if h >= 600 else "Film" if h else "None")
                kind = "Door" if c in self.doors else "Blocked" if c in self.walls else "Receiver" if c in self.dug else "Open"
                return "SHEETCELL dl=%d tier=%s kind=%s stand=0" % (h, tier, kind)
            if method == "ProofSheetSpill":
                c, dl, src = arg.split(";")
                got = self.offer(self._xz(c), int(dl), src)
                return "SPILL offered=%s accepted=%d" % (dl, got)
            if method == "ProofSheetFillIn":
                c = self._xz(arg)
                if c not in self.dug:
                    return "REFUSED: not dug"
                w = self.dug.pop(c)[1]
                for n in self._nbrs(c):           # a neighbour channel with room takes it first
                    if n in self.dug and w > 0:
                        k = min(w, self.dug[n][0] * U - self.dug[n][1])
                        self.dug[n][1] += k
                        w -= k
                if "fillin_destroys" in self.f:
                    self.led["destroyedDl"] += w
                    return "FILLIN homeless=%d spilled=0 destroyed=%d" % (w, w)
                got = self.offer(c, w, "FillIn")
                self.led["destroyedDl"] += w - got
                return "FILLIN homeless=%d spilled=%d destroyed=%d" % (w, got, w - got)
            if method == "ProofSheetHash":
                return "SHEETHASH hash=%s pulse=%d" % (self._hash(), self.pulse)
            if method == "ProofSheetPerf":
                return "SHEETPERF pulses=5 kernelMs=0.20 pulseMs=0.40 maxPulseMs=0.90 allocB=0 dirtySections=3 " \
                       "terrainWrites=0 active=%d wetMax=%d" % (len(self.sheet), len(self.sheet))
        if ty == LPROOF and method == "ProofPitWater":
            x, z, w, h = (int(v) for v in arg.split(","))
            return "PITWATER dl=%d wet=0 cells=0" % sum(v[1] for c, v in self.dug.items()
                                                         if x <= c[0] < x + w and z <= c[1] < z + h)
        if ty == NPROOF and method == "ProofPump":
            c, verb = arg.split(";")
            p = self.pumps.get(self._xz(c))
            if p is None:
                return "REFUSED: no RM_LiquidPump at %s" % c
            p["pour"] = verb == "pour"
            return "PUMP running=True moved=0 pour=%s tank=Water:%d" % (p["pour"], self.tanks.get(p["tank"], 0))
        return {"success": False, "error": "FakeBridge: no %s.%s" % (ty, method)}

    def call(self, tool, **kw):
        if tool == "jawa/static_call":
            r = self._static(kw.get("type"), kw.get("method"), kw.get("args") or "")
            return r if isinstance(r, dict) else {"success": True, "result": r}
        if tool == "rimworld/step_game_ticks":
            if "noclock" in self.f:
                return {"success": False, "error": "clock refused (fault)"}
            self._advance(int(kw.get("ticks") or 0))
            return {"success": True}
        if tool == "jawa/flowworks_excavation_drive":
            c = (kw["x"], kw["z"])
            d = self.dug.setdefault(c, [0, 0])
            d[0] += int(kw.get("deepenLevels") or 0)
            fill = int(kw.get("setFill", -1))
            if fill >= 0:
                d[1] = fill * U - (1 if "canal_not_full" in self.f and fill > 0 else 0)
            self.sheet.pop(c, None)
            return {"success": True, "depth": d[0]}
        if tool == "jawa/build_batch":
            for op in str(kw.get("ops") or "").split(";"):
                if not op:
                    continue
                d, at = op.split(":")
                c = self._xz(at)
                if d == "Wall":
                    self.walls.add(c)
                elif d == "Door":
                    self.doors.add(c)
                elif d == "RM_LiquidTank":
                    self.tanks[c] = 0
                elif d == "RM_LiquidPump":
                    self.pumps[c] = {"pour": False, "tank": None}
                elif d == "Battery":
                    self.batteries.add(c)
            for p, v in self.pumps.items():
                v["tank"] = next((t for t in self.tanks if abs(t[0] - p[0]) <= 2 and abs(t[1] - p[1]) <= 2), None)
            return {"success": True, "built": len(str(kw.get("ops")).split(";"))}
        if tool == "jawa/list_things":
            x, z, w, h = (int(v) for v in str(kw.get("rect")).split(","))
            inr = lambda c: x <= c[0] < x + w and z <= c[1] < z + h   # noqa: E731
            if kw.get("defName") == "Battery":
                return {"success": True, "things": [{"id": "Battery1"} for c in self.batteries if inr(c)]}
            if kw.get("defName") == CROP:
                return {"success": True, "things": [{"id": "Rice%d_%d" % c} for c in self.plants if inr(c)]}
            return {"success": True, "things": []}
        if tool == "jawa/set_plants":
            d, at = str(kw.get("ops")).split(":")
            x, z, w, h = (int(v) for v in at.split(","))
            for i in range(x, x + w):
                for j in range(z, z + h):
                    self.plants[(i, j)] = 0
            return {"success": True}
        if tool == "jawa/weather_set":
            self.rain = kw.get("weather") == "Rain"
            return {"success": True}
        if tool == "jawa/game_condition":
            if kw.get("action") == "start":
                self.cold_since = self.tick if self.cold_since is None else self.cold_since
                self.warm_since = None
            else:
                if self.cold_since is not None:
                    self.warm_since = self.tick
                self.cold_since = None
            return {"success": True}
        if tool == "jawa/cell_temperature":
            return {"success": True, "temperature": round(self.temp, 2)}
        if tool == "jawa/mod_settings_field":
            f = kw.get("field")
            if f not in self.settings:
                return {"success": False, "error": "no field %s" % f}
            if kw.get("action") == "set":
                v = str(kw.get("value"))
                if f == "sheetOverflowEnabled" and v == "False" and "off_purges" in self.f:
                    self.led["purged"] += sum(self.sheet.values())
                    self.sheet = {}
                if f == "sheetCapCm":
                    self.cap_cm = int(v)
                    if "cap_lower_cuts" in self.f:
                        for c in list(self.sheet):
                            cut = max(0, self.sheet[c] - self._cap())
                            self.sheet[c] -= cut
                            self.led["purged"] += cut
                self.settings[f] = v
                return {"success": True}
            return {"success": True, "value": self.settings[f]}
        if tool == "rimworld/save_game":
            self.saved = self._snapshot()
            return {"success": True}
        if tool == "rimworld/load_game_ready":
            if self.saved is None:
                return {"success": False, "error": "no save"}
            self._restore(self.saved)
            return {"success": True}
        if tool == "jawa/map_info":
            return {"success": True, "size": [250, 250]}
        if tool == "jawa/running_mods":
            return {"success": True, "mods": [{"packageId": "mandrake.rimmandrake.flowworks"}] * 14}
        if tool == "jawa/map_comp_timing":
            self._advance(int(kw.get("ticks") or 0))
            return {"success": True, "types": [{"type": "RimMandrake.FlowWorks.RM_MapComponent_Excavation",
                                                "sumMsPerTick": 0.004}]}
        if tool in ("jawa/battery_set", "rimworld/set_god_mode", "jawa/kill_hostiles"):
            return {"success": True}
        return {"success": False, "error": "FakeBridge: tool %s not modelled" % tool}

    def hp(self, cmd, wait_s=20.0):
        verb, _, rest = cmd.partition(":")
        if verb == "filltank":
            at, _, what = rest.partition("=")
            c = self._xz(at)
            if c not in self.tanks:
                return {"success": False, "error": "no tank"}
            self.tanks[c] = int(what.split(",")[1])
            return {"success": True}
        if verb == "tank":
            c = self._xz(rest)
            return {"success": c in self.tanks, "units": self.tanks.get(c)}
        if verb == "pump":
            return {"success": True, "powered": bool(self.batteries)}
        return {"success": False, "error": "unknown verb %s" % verb}


if __name__ == "__main__":
    sys.exit(main())
