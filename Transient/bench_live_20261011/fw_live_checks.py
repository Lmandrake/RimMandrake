"""BENCH ad hoc live checks, FlowWorks tier, 2026-10-11 (run from the HEAD export root with python.exe; bridge held).

  python.exe Transient/bench_live_20261011/fw_live_checks.py [out.json] [--only L1,L2,...] [--fresh-map] [--theft-day]

Map: a 250x250 dev quicktest (flowworks tier: bridge + FlowWorks + GSS + all DLCs, plain temperate). Every block has its
own disjoint site, cleared to Soil / unfogged / unroofed by validation_core.prepare_site (a site the quicktest terrain still
blocks is a SITE UNMEASURED row, never a mod result). Rows {id, status PASS|FAIL|UNMEASURED, class MOD|SITE|HARNESS|LOOK,
detail}; the result JSON is rewritten after every block; a block that raises records <BLOCK>_block HARNESS UNMEASURED and the
run goes on. "Could not ask" (tool success false, a precondition that never held) is UNMEASURED, never PASS.

Scenes reuse proof_hose.py's real-flow plot geometry (pump (3,7) on a 3-cell channel at (2..4,6), battery (6,6), reel (3,8)
coupled to what stands north/south of it, hose end (15|16,9), far tank (17,9)) and its probe channel (HoseProbe: lay / census /
tank / filltank / pump / net / colonists / pawn:). Tank jobs and hose free-end roles have NO probe verb: they are set through
the real gizmos (rimworld/click_cell + list_selected_gizmos + execute_gizmo) and read back (inspect_string "Job: X",
comp_read CompHoseReel.freeEndRole).

Blocks (order: the save+load of R1 runs last, after T1):
  L1  LIQUID_LEDGER A2: "lake" (a filled 3-cell channel) -> pump -> hose with an Outflow end -> a dry disconnected canal, no tank.
  L2  A3: a Dump tank drains through an Outflow end with no pump (slow); a pump on Pour drains a Dump tank fast (rates compared).
  L3  A4 + HOSE_RULINGS A3: an Intake end beside a pond moves nothing without a pump; the end's text names the pond + "needs a pump".
  L4  A5: a "ship" tank (RM_UniversalCargoTank, else RM_LiquidTank) set Fill loads from a Store tank over a hose; Empty unloads.
  L5  A6: a hose whose Outflow end is switched to Capped drains its held liquid at the open end (spill filth); a colonist
      cleans it once the cells are Home area.
  L6  A7 + HOSE A3: our Fill tank drawing a neutral faction's tank over a hose, a witness ~4 cells away -> "Liquid theft
      discovered" letter + RM_LiquidTheft.caught; the free end names the faction. --theft-day: one in-game day later goodwill
      fell by liquidTheftGoodwillPerDay (the foreign tank is refilled every 4000 ticks so it is touched all day).
  D1  ruling #18: a sluice blueprint on a WET canal cell is accepted (a natural WaterShallow cell is refused); a blueprint and a
      frame on a DRY cut survive the cut flooding.
  W1  ruling #19: a colonist walking through water, green slime and tar: terrain read under him + screenshots (LOOK).
  B1  bottles: no auto-pour into a Store tank; an ordered pour into it works; empty bottles fill from it; control: a Fill tank
      takes bottles unasked (without the control the negative proves nothing).
  P1  pit exposure: a colonist in a dug unroofed D=4 pit and a control on open ground (same xenotype, both stripped): the
      RM_PitExposure marker; comfort narrowed by pitExposureNarrowing; hot / cold / mild bands (outdoor temperature HAS NO
      SETTER: HeatWave / ColdSnap game conditions are used and each band row is UNMEASURED unless the outdoor temperature
      actually sat in it); sheltered (roofed) -> marker gone; the pit cell's room temperature vs open ground, coupling on/off,
      to decide whether RM_Patch_PitRoomCoupling is redundant.
  R1  RIGID_PIPE A2 / HOSE A2: the universal pipe's four looks through the real Architect designator (the style getter's
      default-look route: pipeDefaultLook set per look, because no verb drives PipeLook.Pick), blueprint -> frame -> building by
      a real colonist, raw CompStyleable.styleDef read at each stage; joined runs per look screenshotted (LOOK); then (last) a
      bridge save + load and the raw looks read again.
  T1  LIQUID_LEDGER A8: jawa/map_comp_timing over 1200 real ticks at Normal speed on the map all blocks left; every FlowWorks
      MapComponent's mean ms/tick and max single call (<= 1 ms).
"""
import argparse
import json
import os
import re
import sys
import time
import traceback

ROOT = os.getcwd()
NS_DIR = os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "northstar")
if NS_DIR not in sys.path:
    sys.path.insert(0, NS_DIR)
import proof_hose as PH  # noqa: E402  (puts FlowWorks/, Utils/ and northstar/ on sys.path; imports validation_core)

V = PH.V
WATER = PH.LIQUID_WATER                                   # RM_Liquid_FreshWater
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
S_HOSE = "RimMandrake.FlowWorks.Hose.RM_HoseSettings"
S_MACH = "RimMandrake.FlowWorks.Machinery.RM_MachinerySettings"
THEFT = "RimMandrake.FlowWorks.Machinery.RM_LiquidTheft"
NS_PROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
FW_PKG = "mandrake.rm.flowworks"
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
BLOCKS = ["L1", "L2", "L3", "L4", "L5", "L6", "D1", "W1", "B1", "P1", "R1", "T1"]
SHOTS = os.path.join(ROOT, "Transient", "bench_live_20261011", "shots")

ap = argparse.ArgumentParser()
ap.add_argument("out", nargs="?", default=os.path.join(ROOT, "Transient", "bench_live_20261011",
                                                        "fw_live_checks_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
ap.add_argument("--only", default="", help="comma list of blocks, e.g. L1,L2,R1")
ap.add_argument("--fresh-map", action="store_true", help="main menu + start_debug_game_ready first (as proof_hose)")
ap.add_argument("--theft-day", action="store_true", help="L6: also tick one in-game day (~61k ticks) for the goodwill charge")
ARGS = ap.parse_args()
ONLY = [b.strip().upper() for b in ARGS.only.split(",") if b.strip()]
OUT = ARGS.out

B = PH.PB()


def _tg():
    g = B.call("rimworld/get_game_info")
    return g.get("ticksGame") or (g.get("state") or {}).get("tick")


_raw_ticks = B.ticks


def _ticks_checked(n):
    """step_game_ticks stops at its 120 s timeout (~1 tick/frame), silently short of n (BENCH 2026-10-11: a 60,500-tick
    step advanced ~7,200). Step in <=1500-tick chunks and verify ticksGame actually moved."""
    t0 = _tg()
    left, r = n, {}
    while left > 0:
        k = min(1500, left)
        r = _raw_ticks(k)
        left -= k
    t1 = _tg()
    if t0 is not None and t1 is not None and t1 - t0 < n:
        _raw_ticks(n - (t1 - t0))
    return r


B.ticks = _ticks_checked
rows = []
res = {"script": "fw_live_checks.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "only": ONLY, "rows": rows,
       "shots": [], "blocks": {}}
WORKERS = []          # colonists this script spawned and un-drafted; drafted again at each block's end
CUR = {"block": None}


# ============================================================================ plumbing
def row(rid, st, cls, det):
    rows.append({"id": rid, "status": st, "class": cls, "detail": det, "block": CUR["block"]})
    print("%-42s %-10s %-8s %s" % (rid, st, cls, json.dumps(_jsonable(det), default=str)[:300]), flush=True)


def verdict(ok, unmeasured=None):
    return "UNMEASURED" if unmeasured else ("PASS" if ok else "FAIL")


def _jsonable(o):
    if isinstance(o, dict):
        return {(k if isinstance(k, (str, int, float, bool)) or k is None else str(k)): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    return o


def save():
    res["saved"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(_jsonable(res), f, indent=1, default=str)
    os.replace(tmp, OUT)


def sget(typ, field):
    return B.call("jawa/mod_settings_field", typeName=typ, action="get", field=field).get("value")


def sset(typ, field, value):
    return B.call("jawa/mod_settings_field", typeName=typ, action="set", field=field, value=str(value))


def rs(rect):
    return "%d,%d,%d,%d" % tuple(rect)


def shot(name, rect):
    B.call("jawa/clear_ui", all=True)
    B.call("rimworld/frame_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=1)
    time.sleep(2.0)
    r = B.call("jawa/take_screenshot", fileName=name)
    src = r.get("filePath")
    for _ in range(10):
        if src and os.path.exists(src):
            break
        time.sleep(0.5)
    try:
        import shutil
        os.makedirs(SHOTS, exist_ok=True)
        dst = os.path.join(SHOTS, name + ".png")
        shutil.copyfile(src, dst)
    except Exception as ex:  # noqa: BLE001
        dst = "copy failed: %s (%s)" % (ex, src)
    res["shots"].append(dst)
    return dst


def site(rect, rid):
    return V.prepare_site(B, rect, rows, rid)


def build(*ops, faction="player", stuff=None):
    kw = {"ops": ";".join(o for o in ops if o), "faction": faction, "wipeExisting": False}
    if stuff:
        kw["stuff"] = stuff
    return B.call("jawa/build_batch", **kw)


def dig(c, depth, fill=-1):
    r = B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=depth, setFill=-1)
    if fill >= 0:
        r = B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=0, setFill=fill)
    return r


def proof(typ, method, arg):
    r = B.call("jawa/static_call", type=typ, method=method, args=arg)
    txt = str(r.get("result") or r.get("message") or r.get("error") or "")
    return r.get("success") is True and not txt.startswith("REFUSED"), txt


def fluid_row(cells):
    """{(x,z): {d, f, fluid, terrain}} over the cells' bbox (RM_PromotionProofs.ProofFluidRow, as validation_v2)."""
    xs, zs = [c[0] for c in cells], [c[1] for c in cells]
    ok, txt = proof(PROMO, "ProofFluidRow", "%d,%d,%d,%d" % (min(xs), min(zs), max(xs) - min(xs) + 1, max(zs) - min(zs) + 1))
    out = {}
    for tok in (txt.split(" ", 3)[3] if ok and txt.count(" ") >= 3 else "").split(";"):
        if ":" in tok:
            xz, rest = tok.split(":", 1)
            x, z = map(int, xz.split(","))
            d, f, fl, ter = rest.split("/", 3)
            out[(x, z)] = dict(d=int(d), f=int(f), fluid=fl, terrain=ter)
    return out


def fills(cells):
    fr = fluid_row(cells)
    return [fr.get(tuple(c), {}).get("f") for c in cells]


def fsum(lst):
    return sum(x or 0 for x in (lst or []))


def units(cell):
    return PH._tank(B, cell).get("units")


def things(rect, pred=None, limit=200):
    lt = B.call("jawa/list_things", rect=rs(rect), limit=limit, includePawns=False) or {}
    out = [t for t in lt.get("things") or []]
    return [t for t in out if pred is None or pred(t)]


def tdef(t):
    return str(t.get("def") or t.get("defName") or "")


def tpos(t):
    p = t.get("position")
    if isinstance(p, dict):
        return (p.get("x"), p.get("z"))
    if isinstance(p, (list, tuple)) and len(p) >= 2:
        return (p[0], p[-1]) if len(p) == 2 else (p[0], p[2])
    return (t.get("x"), t.get("z"))


def num(pid):
    m = re.search(r"(\d+)$", str(pid))
    return int(m.group(1)) if m else None


def spawn_colonist(x, z, worker=False):
    r = B.call("jawa/spawn_pawn", kindDef="Colonist", faction="player", x=x, z=z, count=1, xenotype="Baseliner")
    p = (r.get("pawns") or [{}])[0]
    pid = p.get("id")
    if pid and worker:
        WORKERS.append(pid)
    return pid, r


def draft(pid, on=True):
    n = num(pid)
    return B.hp("pawn:%d=%s" % (n, "draft" if on else "undraft")) if n is not None else {"success": False}


def pawn(pid):
    r = B.call("jawa/pawn_get", pawn=pid)
    return (r.get("pawns") or [{}])[0]


def hediffs(pid):
    return {h.get("def"): h.get("severity") for h in (pawn(pid).get("hediffs") or [])}


def comfy(pid):
    r = B.call("jawa/pawn_stats", pawn=pid, stats="ComfyTemperatureMin,ComfyTemperatureMax")
    st = {s.get("defName"): s.get("value") for s in r.get("stats") or []}
    return st.get("ComfyTemperatureMin"), st.get("ComfyTemperatureMax")


def outdoor():
    return B.call("jawa/map_info").get("outdoorTempNow")


def hose_id(reel):
    return PH._hose(B, reel).get("id")


def reel_comp(reel, members="freeEndRole,heldUnits,heldLiquid"):
    hid = hose_id(reel)
    if hid is None:
        return {}
    return (B.call("jawa/comp_read", thing="RM_HoseReel%d" % hid, comp="CompHoseReel", members=members) or {}).get("values") or {}


def inspect(thing_id):
    r = B.call("jawa/inspect_string", thingIds=thing_id) or {}
    for t in r.get("things") or r.get("results") or []:
        return t.get("inspect") or []
    return []


def tank_job(cell):
    tid = PH._tank(B, cell).get("id")
    if tid is None:
        return None
    for line in inspect("%s%d" % ("RM_LiquidTank", tid)) + inspect("%s%d" % ("RM_UniversalCargoTank", tid)):
        m = re.search(r"Job: (\w+)", str(line))
        if m:
            return m.group(1)
    return None


def gizmo_cycle(cell, prefix, want, max_clicks=4):
    """Click the thing at `cell`, then execute its gizmo whose label starts with `prefix` until the label reads `want`.
    The tank job (Store>Fill>Empty>Dump) and the reel's "Free end: Capped>Intake>Outflow" are cycle buttons with no probe verb."""
    out = {"clicks": 0, "ok": False}
    B.call("rimworld/set_god_mode", enabled=True)
    try:
        B.call("rimworld/clear_selection")
        B.call("rimworld/click_cell", x=cell[0], z=cell[1])
        for _ in range(max_clicks + 1):
            gz = (B.call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
            g = next((q for q in gz if str(q.get("label") or "").startswith(prefix)), None)
            if g is None:
                out["labels"] = [q.get("label") for q in gz][:20]
                return out
            out["label"] = g.get("label")
            if g.get("label") == want:
                out["ok"] = True
                return out
            r = B.call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id"))
            out["clicks"] += 1
            if r.get("success") is False:
                out["error"] = r
                return out
        return out
    finally:
        B.call("rimworld/set_god_mode", enabled=False)
        B.call("rimworld/clear_selection")


def set_role(reel, role):
    g = gizmo_cycle(reel, "Free end:", "Free end: " + role)
    g["readBack"] = reel_comp(reel).get("freeEndRole")
    g["ok"] = bool(g.get("ok")) and str(g["readBack"]) == role
    return g


def set_job(tank, job):
    g = gizmo_cycle(tank, "Job:", "Job: " + job)
    g["readBack"] = tank_job(tank)
    g["ok"] = bool(g.get("ok")) and g["readBack"] == job
    return g


def letters_matching(text):
    return [l for l in (B.call("jawa/letter_list").get("letters") or []) if text in json.dumps(l, default=str)]


def faction_goodwill(defname):
    return next((f.get("goodwill") for f in B.call("jawa/list_factions").get("factions") or [] if f.get("defName") == defname), None)


def find_designator(needles, exclude=()):
    """A live Architect designator id whose id/label contains one of `needles` (lowercase), searched in every category
    (bridge_latency.find_designator, widened: the id scheme is the live menu's, so it is discovered, never hardcoded)."""
    cats = B.call("rimworld/list_architect_categories") or {}
    cats = cats.get("categories") or (cats.get("raw") if isinstance(cats.get("raw"), list) else []) or []
    for c in cats:
        lst = (B.call("rimworld/list_architect_designators", categoryId=c.get("id")) or {}).get("designators") or []
        for d in lst:
            blob = json.dumps(d, default=str).lower()
            if any(n in blob for n in needles) and not any(e in blob for e in exclude):
                return d.get("id"), d
    return None, None


def raw_style(thing_id):
    r = B.call("jawa/comp_read", thing=thing_id, comp="CompStyleable", members="styleDef") or {}
    if not r.get("success"):
        return None, r.get("error") or r.get("message") or "comp_read failed"
    return str((r.get("values") or {}).get("styleDef")), None


class FW(PH.Scene):
    """proof_hose's real-flow plot (26 x 14 plus RF_WEST cells west of it) at an origin of this script's own."""

    def __init__(self, o):
        self.B = B
        self.o = o
        ox, oz = o
        self.channel = [(ox + 2 + k, oz + 6) for k in range(3)]
        self.pump = (ox + 3, oz + 7)
        self.battery = (ox + 6, oz + 6)
        self.reel = (ox + 3, oz + 8)
        self.end = (ox + 16, oz + 9)
        self.tank = (ox + 17, oz + 9)
        self.north_tank = (ox + 3, oz + 10)       # a tank north of the reel: the reel's port (proof_hose scene 3/6)

    def rect(self, extra_h=0):
        return (self.o[0] - PH.RF_WEST, self.o[1], PH.RF_PW + PH.RF_WEST, PH.RF_PH + extra_h)

    def ready(self, rid, extra_h=0):
        return site(self.rect(extra_h), rid)

    def power(self):
        B.ticks(2)
        self.charge()
        self.powered = PH._powered(B, self.pump)
        return self.powered


def watch(fn, total, step=250):
    """Tick `total` in `step`s, recording fn() after each step."""
    trace = [fn()]
    for _ in range(max(1, total // step)):
        B.ticks(step)
        trace.append(fn())
    return trace


# ============================================================================ preflight
def preflight():
    if ARGS.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, waited = V._wait_playing(B, leave_s=0)
    rm = B.call("jawa/running_mods", assembly="RimMandrakeFlowWorks", details=False) or {}
    running = [p.lower() for p in rm.get("packageIds") or []]
    mi = B.call("jawa/map_info") or {}
    res["preflight"] = {"playing": ok, "waited": waited, "flowworks": FW_PKG in running,
                        "gimmesomeslack": "mandrake.rm.gimmesomeslack" in running, "running": len(running),
                        "map": {k: mi.get(k) for k in ("sizeX", "sizeZ", "mapBiome", "outdoorTempNow", "season", "tile")}}
    res["log_revive"] = V.log_revive(B)
    V.tap_start(B)
    hd = B.hp("defaults")
    res["preflight"]["hoseProbe"] = hd.get("success")
    B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    B.call("jawa/incident_queue_clear")
    B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
    res["preflight"]["drafted"] = [p["id"] for p in (B.hp("colonists").get("pawns") or [])
                                   if B.hp("pawn:%d=draft" % p["id"]).get("success")]
    res["settings_before"] = {f: sget(t, f) for t, f in (
        (S_HOSE, "tankModesEnabled"), (S_HOSE, "freeEndRolesEnabled"), (S_HOSE, "hoseHoldsLiquid"),
        (S_HOSE, "tankUnitsPerCycle"), (S_HOSE, "dumpUnitsPerCycle"), (S_MACH, "liquidTheftEnabled"),
        (S_MACH, "liquidTheftSightRange"), (S_MACH, "liquidTheftGoodwillPerDay"), (S_MACH, "pipeDefaultLook"),
        (S_FW, "liquidWakesEnabled"), (S_FW, "pitExposureEnabled"), (S_FW, "pitExposureNarrowing"),
        (S_FW, "pitTemperatureCoupling"))}
    facs = B.call("jawa/list_factions").get("factions") or []
    nonhostile = [f for f in facs if not f.get("isPlayer") and not f.get("hostile") and not f.get("permanentEnemy")
                  and not f.get("hidden")]
    res["neutral"] = next((f for f in nonhostile if str(f.get("defName", "")).startswith("Outlander")), None) or \
        (nonhostile[0] if nonhostile else None)
    good = ok and FW_PKG in running and hd.get("success") and mi.get("sizeX") == 250 and mi.get("sizeZ") == 250
    row("PF_tier_probe_map", "PASS" if good else "UNMEASURED", "HARNESS", res["preflight"])
    save()
    return good


# ============================================================================ L1: lake -> pump -> Outflow -> canal, no tank
def blk_L1():
    s = FW((20, 150))
    if not s.ready("L1_site_ready"):
        return
    s.water()
    canal = [s.P(16 + k, 9) for k in range(3)]
    for c in canal:
        dig(c, 2)
    b = s.build("RM_LiquidPump:%d,%d" % s.pump, "Battery:%d,%d" % s.battery, "RM_HoseReel:%d,%d" % s.reel)
    pw = s.power()
    lay = s.lay(s.P(15, 9))
    role = set_role(s.reel, "Outflow")
    src0, f0 = fills(s.channel), fills(canal)
    trace = watch(lambda: {"canal": fills(canal), "src": fills(s.channel)}, 1250)
    f1 = trace[-1]["canal"]
    net = B.hp("net:%d,%d" % s.pump)
    h = PH._hose(B, s.reel)
    pre = None if (lay.get("success") and role["ok"] and pw is not None and None not in f0) else \
        "precondition: lay %s, role %s, pump powered after %s, canal read %s" % (lay.get("success"), role, pw, f0)
    row("L1_canal_from_lake_no_tank", verdict(fsum(f1) > fsum(f0) and not (net.get("tanks") or []), pre), "MOD",
        {"canalFill": [f0, f1], "sourceFill": [src0, trace[-1]["src"]], "trace": trace, "pump": B.hp("pump:%d,%d" % s.pump),
         "netTanks": net.get("tanks"), "lay": lay, "role": role, "pumpPoweredAfterTicks": pw, "build": b.get("failed"),
         "hose": {k: h.get(k) for k in ("freeEnd", "netLink", "credits", "creditedUnits", "state")},
         "note": "'lake' is a filled 3-cell channel (dug 2, fill 2), not a natural body"})
    shot("L1_lake_pump_outflow_canal", s.rect())


# ============================================================================ L2: Dump drains slow (no pump), pump Pour fast
def blk_L2():
    a = FW((60, 150))
    rate = {}
    if a.ready("L2a_site_ready"):
        canal = [a.P(16 + k, 9) for k in range(3)]
        for c in canal:
            dig(c, 2)
        a.build("RM_LiquidTank:%d,%d" % a.north_tank, "RM_HoseReel:%d,%d" % a.reel)
        B.ticks(2)
        ft = B.hp("filltank:%d,%d=%s,100" % (a.north_tank + (WATER,)))
        lay = a.lay(a.P(15, 9))
        role = set_role(a.reel, "Outflow")
        job = set_job(a.north_tank, "Dump")
        f0 = fills(canal)
        tr = watch(lambda: units(a.north_tank), 1000)
        f1 = fills(canal)
        drained = (tr[0] or 0) - (tr[-1] or 0)
        rate["dump_no_pump"] = drained
        pre = None if (ft.get("success") and lay.get("success") and role["ok"] and job["ok"] and tr[0]) else \
            "precondition: filltank %s, lay %s, role %s, job %s" % (ft.get("units"), lay.get("success"), role, job)
        row("L2_dump_tank_drains_without_pump", verdict(drained > 0 and fsum(f1) > fsum(f0), pre), "MOD",
            {"tankUnits": tr, "drainedPer1000": drained, "canalFill": [f0, f1], "lay": lay, "role": role, "job": job,
             "dumpUnitsPerCycle": res.get("settings_before", {}).get("dumpUnitsPerCycle")})
        shot("L2a_dump_tank_outflow_no_pump", a.rect())
    b = FW((100, 150))
    if b.ready("L2b_site_ready"):
        for c in b.channel:
            dig(c, 2)                                               # the pump's reach: a DRY channel to pour into
        b.build("RM_LiquidPump:%d,%d" % b.pump, "Battery:%d,%d" % b.battery, "RM_UniversalPipe:%d,%d" % b.P(3, 8),
                "RM_UniversalPipe:%d,%d" % b.P(3, 9), "RM_LiquidTank:%d,%d" % b.north_tank)
        pw = b.power()
        ft = B.hp("filltank:%d,%d=%s,100" % (b.north_tank + (WATER,)))
        job = set_job(b.north_tank, "Dump")
        ok_p, pour = proof(NS_PROOF, "ProofPump", "%d,%d;pour" % b.pump)
        f0 = fills(b.channel)
        tr = watch(lambda: units(b.north_tank), 1000)
        f1 = fills(b.channel)
        drained = (tr[0] or 0) - (tr[-1] or 0)
        rate["dump_pump_pour"] = drained
        net = B.hp("net:%d,%d" % b.pump)
        pre = None if (ft.get("success") and job["ok"] and ok_p and "pour=True" in pour and pw is not None and tr[0]) else \
            "precondition: filltank %s, job %s, pour %s, pump powered after %s" % (ft.get("units"), job, pour, pw)
        if "dump_no_pump" not in rate and not pre:
            pre = "the no-pump scene (L2a) did not run: no slow rate to compare"
        row("L2_pump_pour_drains_dump_fast", verdict(drained > rate.get("dump_no_pump", 10 ** 9) and drained > 0
                                                     and fsum(f1) > fsum(f0), pre), "MOD",
            {"tankUnits": tr, "drainedPer1000": drained, "vsNoPump": rate.get("dump_no_pump"), "reachFill": [f0, f1],
             "pumpProof": pour, "job": job, "netTanks": net.get("tanks"), "pumpPoweredAfterTicks": pw})
        shot("L2b_dump_tank_pump_pour", b.rect())
    res["L2_rates"] = rate


# ============================================================================ L3: Intake end in a pond, no pump
def blk_L3():
    s = FW((140, 150))
    if not s.ready("L3_site_ready"):
        return
    pond = [s.P(16 + k, 9) for k in range(3)]
    for c in pond:
        dig(c, 2, fill=2)
    s.build("RM_LiquidTank:%d,%d" % s.north_tank, "RM_HoseReel:%d,%d" % s.reel)
    B.ticks(2)
    lay = s.lay(s.P(15, 9))
    B.ticks(70)                                           # the free-end cache re-reads within 60 ticks
    capped = (PH._hose(B, s.reel).get("freeEnd") or {})
    role = set_role(s.reel, "Intake")
    hid = hose_id(s.reel)
    insp = inspect("RM_HoseReel%d" % hid) if hid is not None else []
    u0, p0 = units(s.north_tank), fills(pond)
    tr = watch(lambda: {"tank": units(s.north_tank), "pond": fills(pond)}, 1000)
    pre = None if (lay.get("success") and role["ok"] and u0 is not None and None not in p0) else \
        "precondition: lay %s, role %s, tank %s, pond %s" % (lay.get("success"), role, u0, p0)
    row("L3_intake_needs_pump", verdict(tr[-1]["tank"] == u0 and tr[-1]["pond"] == p0, pre), "MOD",
        {"trace": tr, "role": role, "lay": lay, "inspect": insp})
    desc = str(capped.get("describe") or "")
    row("L3_end_text_names_pond_needs_pump", verdict("lying" in desc and "needs a pump" in desc,
                                                     None if lay.get("success") else "hose not laid"), "MOD",
        {"describe": desc, "freeEnd": capped, "inspectIntake": insp,
         "inspectHasIntakeWarning": any("Intake needs a working pump" in str(l) for l in insp)})
    shot("L3_intake_in_pond_no_pump", s.rect())


# ============================================================================ L4: ship tank Fill / Empty over a hose
def blk_L4():
    s = FW((180, 150))
    if not s.ready("L4_site_ready"):
        return
    s.build("RM_LiquidTank:%d,%d" % s.north_tank, "RM_HoseReel:%d,%d" % s.reel)
    sb = s.build("RM_UniversalCargoTank:%d,%d" % s.tank)
    B.ticks(2)
    ship_def = "RM_UniversalCargoTank"
    if not PH._tank(B, s.tank):
        s.build("RM_LiquidTank:%d,%d" % s.tank)
        B.ticks(2)
        ship_def = "RM_LiquidTank"
    ft = B.hp("filltank:%d,%d=%s,100" % (s.north_tank + (WATER,)))
    lay = s.lay(s.P(16, 9))
    jf = set_job(s.tank, "Fill")
    tr1 = watch(lambda: [units(s.north_tank), units(s.tank)], 1000)
    je = set_job(s.tank, "Empty")
    tr2 = watch(lambda: [units(s.north_tank), units(s.tank)], 1000)
    h = PH._hose(B, s.reel)
    pre1 = None if (ft.get("success") and lay.get("success") and jf["ok"] and None not in tr1[0]) else \
        "precondition: filltank %s, lay %s, job %s, units %s" % (ft.get("units"), lay.get("success"), jf, tr1[0])
    row("L4_ship_tank_fill_loads", verdict((tr1[-1][1] or 0) - (tr1[0][1] or 0) >= 5 and (tr1[-1][0] or 0) < (tr1[0][0] or 0), pre1),
        "MOD", {"base_ship": tr1, "shipDef": ship_def, "cargoBuild": sb.get("failed"), "job": jf, "lay": lay,
                "hose": {k: h.get(k) for k in ("netLink", "credits", "creditedUnits")}})
    pre2 = None if (not pre1 and je["ok"]) else (pre1 or "precondition: Empty job %s" % je)
    row("L4_ship_tank_empty_unloads", verdict((tr2[-1][1] or 0) < (tr2[0][1] or 0) and (tr2[-1][0] or 0) > (tr2[0][0] or 0), pre2),
        "MOD", {"base_ship": tr2, "job": je})
    row("L4_on_a_real_gravship", "UNMEASURED", "SITE",
        "no gravship fixture on a quicktest map: a plain %s stands in for the ship's tank (no ship-tank def exists)" % ship_def)
    shot("L4_ship_tank_fill_empty", s.rect())


# ============================================================================ L5: switched-off hose spills; colonists clean
def blk_L5():
    s = FW((20, 172))
    if not s.ready("L5_site_ready"):
        return
    s.water()
    s.build("RM_LiquidPump:%d,%d" % s.pump, "Battery:%d,%d" % s.battery, "RM_HoseReel:%d,%d" % s.reel)
    pw = s.power()
    lay = s.lay(s.P(16, 9))
    role = set_role(s.reel, "Outflow")
    B.ticks(600)
    held = reel_comp(s.reel)
    filth_rect = (s.P(14, 7)[0], s.P(14, 7)[1], 5, 5)
    is_filth = (lambda t: "filth" in tdef(t).lower())
    n0 = len(things(filth_rect, is_filth))
    net0 = B.hp("net:%d,%d" % s.pump)
    off = set_role(s.reel, "Capped")                      # the switch: an Outflow end capped stops the hose carrying
    B.ticks(900)                                          # lease = now+375, drain checked once per 250-tick cycle (BENCH fix)
    held2 = reel_comp(s.reel)
    net1 = B.hp("net:%d,%d" % s.pump)
    n1 = len(things(filth_rect, is_filth))
    h0 = int(held.get("heldUnits") or 0) if str(held.get("heldUnits") or "").lstrip("-").isdigit() else None
    h1 = int(held2.get("heldUnits") or 0) if str(held2.get("heldUnits") or "").lstrip("-").isdigit() else None
    drained = (net1.get("hoseDrainedUnits") or 0) - (net0.get("hoseDrainedUnits") or 0)
    pre = None if (lay.get("success") and role["ok"] and off["ok"] and pw is not None and h0) else \
        "precondition: lay %s, Outflow %s, Capped %s, pump %s, heldUnits before %s" % (lay.get("success"), role, off, pw, h0)
    row("L5_switched_off_hose_spills", verdict(h1 == 0 and drained >= (h0 or 1) and n1 > 0, pre), "MOD",
        {"heldUnits": [h0, h1], "heldLiquid": held.get("heldLiquid"), "hoseDrainedUnits": [net0.get("hoseDrainedUnits"),
         net1.get("hoseDrainedUnits")], "spilledUnits": [net0.get("spilledUnits"), net1.get("spilledUnits")],
         "filthInRect": [n0, n1], "rect": filth_rect, "note": "filth before the cap is the Outflow end's own spill while carrying"})
    shot("L5_spill_at_open_end", filth_rect)
    if n1 == 0:
        row("L5_colonists_clean_spill", "UNMEASURED", "SITE", "no filth to clean")
        return
    pa = B.call("jawa/paint_area", area="Home", ops=rs(filth_rect), value=True, createIfMissing=True)
    cid, sp = spawn_colonist(s.P(12, 11)[0], s.P(12, 11)[1], worker=True)
    wp = B.call("jawa/set_work_priority", pawnId=cid, workType="Cleaning", priority=1) if cid else {}
    left, waited = n1, 0
    while left and waited < 3000:
        B.ticks(250)
        waited += 250
        left = len(things(filth_rect, is_filth))
    pre2 = None if (cid and pa.get("success") is not False and wp.get("readBack") == 1) else \
        "precondition: cleaner %s, home paint %s, Cleaning priority %s" % (cid, pa.get("setCount"), wp.get("readBack"))
    row("L5_colonists_clean_spill", verdict(left == 0, pre2), "MOD",
        {"filth": [n1, left], "ticks": waited, "cleaner": cid, "homeArea": {k: pa.get(k) for k in ("setCount", "failedVerify")},
         "workPriority": {k: wp.get(k) for k in ("readBack", "manualPrioritiesOn")}})


# ============================================================================ L6: liquid theft
def blk_L6():
    nb = res.get("neutral")
    if not nb:
        row("L6_theft_spotted_letter", "UNMEASURED", "SITE", "no non-hostile, non-hidden faction in this world")
        return
    nf = nb["defName"]
    s = FW((60, 172))
    if not s.ready("L6_site_ready", extra_h=6):
        return
    s.build("RM_LiquidTank:%d,%d" % s.north_tank, "RM_HoseReel:%d,%d" % s.reel)            # ours: the reel's port, set Fill
    fb = build("RM_LiquidTank:%d,%d" % s.tank, faction=nf)                                   # theirs: at the hose's free end
    B.ticks(2)
    ft = B.hp("filltank:%d,%d=%s,100" % (s.tank + (WATER,)))
    lay = s.lay(s.P(16, 9))
    B.ticks(70)
    fe = PH._hose(B, s.reel).get("freeEnd") or {}
    wit = B.call("jawa/spawn_pawn", kindDef="Villager", x=s.P(20, 13)[0], z=s.P(20, 13)[1], faction=nf, count=2)
    cc0, gw0 = sget(THEFT, "caught"), faction_goodwill(nf)
    l0 = len(letters_matching("Liquid theft"))
    job = set_job(s.north_tank, "Fill")
    tr = watch(lambda: [units(s.north_tank), units(s.tank)], 1000)
    cc1 = sget(THEFT, "caught")
    lets = letters_matching("Liquid theft")
    drawn = (tr[0][1] or 0) - (tr[-1][1] or 0)
    pre = None if (ft.get("success") and lay.get("success") and job["ok"] and wit.get("success")) else \
        "precondition: foreign filltank %s, lay %s, our job %s, witnesses %s" % (ft.get("units"), lay.get("success"), job,
                                                                                 wit.get("success"))
    row("L6_foreign_tank_drawn", verdict(drawn > 0, pre), "MOD",
        {"ours_theirs": tr, "foreignBuild": fb.get("failed"), "job": job, "theftEnabled": res["settings_before"].get("liquidTheftEnabled")})
    row("L6_theft_spotted_letter", verdict(len(lets) > l0 and (cc1 or 0) > (cc0 or 0), pre or (None if drawn > 0 else
        "nothing was taken from their tank, so there was no theft to spot")), "MOD",
        {"letters": lets[-1:], "caught": [cc0, cc1], "witnesses": wit.get("pawns"), "faction": nf,
         "sightRange": res["settings_before"].get("liquidTheftSightRange")})
    fname = str(nb.get("name") or "")
    row("L6_free_end_names_their_faction", verdict(fname and fname in str(fe.get("describe")) and fe.get("portFaction") == fname,
                                                   None if lay.get("success") else "hose not laid"), "MOD",
        {"freeEnd": fe, "factionName": fname})
    shot("L6_liquid_theft_witness", s.rect(6))
    if not ARGS.theft_day:
        row("L6_goodwill_after_a_day", "UNMEASURED", "HARNESS", "not run: pass --theft-day (ticks ~61,000)")
        return
    gc0 = sget(THEFT, "goodwillCharged")
    for _ in range(16):                                   # 16 x 4000 > one day; keep their tank touched every cycle
        B.hp("filltank:%d,%d=%s,100" % (s.tank + (WATER,)))
        B.hp("filltank:%d,%d=%s,0" % (s.north_tank + (WATER,)))
        B.ticks(4000)
    gw1, gc1 = faction_goodwill(nf), sget(THEFT, "goodwillCharged")
    per = res["settings_before"].get("liquidTheftGoodwillPerDay")
    row("L6_goodwill_after_a_day", verdict(gw0 is not None and gw1 is not None and int(gc1 or 0) - int(gc0 or 0) <= -int(per or 2)
                                           and gw1 < gw0, None if cc1 and cc1 > (cc0 or 0) else "the theft was never caught"),
        "MOD", {"goodwill": [gw0, gw1], "goodwillCharged": [gc0, gc1], "perDay": per,
                "situations": B.call("jawa/faction_goodwill_situations", faction=nf)})


# ============================================================================ D1: sluice on a wet canal cell (ruling #18)
def blk_D1():
    rect = (100, 40, 16, 8)
    if not site(rect, "D1_site_ready"):
        return
    wet, dry_bp, dry_fr, natural = (103, 43), (106, 43), (109, 43), (112, 43)
    dig(wet, 2, fill=2)
    dig(dry_bp, 2)
    dig(dry_fr, 2)
    B.call("jawa/set_terrain_batch", ops="WaterShallow:%d,%d,1,1" % natural)
    B.ticks(2)
    did, dd = find_designator(["rm_sluice", "build-sluice"], exclude=["sluicebox", "sluice box"])
    if not did:
        row("D1_sluice_on_wet_canal", "UNMEASURED", "HARNESS", "no Architect designator for RM_Sluice found in any category")
        return
    terr = fluid_row([wet, dry_bp, dry_fr, natural])
    dry_wet = B.call("rimworld/apply_architect_designator", designatorId=did, x=wet[0], z=wet[1], width=1, height=1, dryRun=True)
    dry_nat = B.call("rimworld/apply_architect_designator", designatorId=did, x=natural[0], z=natural[1], width=1, height=1, dryRun=True)
    real = B.call("rimworld/apply_architect_designator", designatorId=did, x=wet[0], z=wet[1], width=1, height=1)
    B.ticks(2)
    bp_wet = things((wet[0], wet[1], 1, 1), lambda t: "rm_sluice" in tdef(t).lower())
    row("D1_sluice_on_wet_canal", verdict(real.get("success") is not False and bool(bp_wet),
                                          None if terr.get(wet, {}).get("f") else "the wet cell read no fill: %s" % terr.get(wet)),
        "MOD", {"designator": did, "dryRunWet": dry_wet, "placed": real, "thingsAt": [tdef(t) for t in bp_wet], "cells": terr})
    nat_things = things((natural[0], natural[1], 1, 1), lambda t: "rm_sluice" in tdef(t).lower())
    row("D1_natural_water_still_refused", verdict(dry_nat.get("success") is False or "refus" in json.dumps(dry_nat).lower()
                                                  or "cannot" in json.dumps(dry_nat).lower(), None), "MOD",
        {"dryRunNatural": dry_nat, "thingsAt": [tdef(t) for t in nat_things],
         "note": "verdict reads the dryRun answer; check its wording live (the tool's refusal shape is unverified)"})
    # a blueprint (designator) and a frame (build_batch Frame_RM_Sluice, stuff WoodLog) on dry cuts, then flood both cuts
    pb = B.call("rimworld/apply_architect_designator", designatorId=did, x=dry_bp[0], z=dry_bp[1], width=1, height=1)
    fr = build("Frame_RM_Sluice:%d,%d" % dry_fr, stuff="WoodLog")
    B.ticks(2)
    before = {c: [tdef(t) for t in things((c[0], c[1], 1, 1), lambda t: "rm_sluice" in tdef(t).lower())] for c in (dry_bp, dry_fr)}
    for c in (dry_bp, dry_fr):
        dig(c, 0, fill=2)
    B.ticks(600)
    after = {c: [tdef(t) for t in things((c[0], c[1], 1, 1), lambda t: "rm_sluice" in tdef(t).lower())] for c in (dry_bp, dry_fr)}
    wet_now = fluid_row([dry_bp, dry_fr])
    for c, kind in ((dry_bp, "blueprint"), (dry_fr, "frame")):
        had = [d for d in before[c] if d.lower().startswith(kind)]
        pre = None if had else "no %s staged on the dry cut (%s)" % (kind, pb if kind == "blueprint" else fr)
        if not pre and not wet_now.get(c, {}).get("f"):
            pre = "the cut did not flood: %s" % wet_now.get(c)
        row("D1_%s_survives_cut_flooding" % kind, verdict(any(d.lower().startswith(kind) for d in after[c]), pre), "MOD",
            {"before": before[c], "after": after[c], "cell": wet_now.get(c)})
    shot("D1_sluice_wet_canal_and_flooded_cuts", rect)


# ============================================================================ W1: wakes in water, slime and tar (ruling #19)
def blk_W1():
    rect = (56, 40, 36, 9)
    if not site(rect, "W1_site_ready"):
        return
    z = 44
    strips = {"water": [(60 + k, z) for k in range(6)], "slime": [(70 + k, z) for k in range(6)],
              "tar": [(80 + k, z) for k in range(6)]}
    # BENCH fix: 5-row strips -- a 1-row strip was simply walked around (pathing avoids liquids; run 2 read Soil under him)
    for c in strips["water"]:
        for dz in (-2, -1, 0, 1, 2):
            dig((c[0], c[1] + dz), 1, fill=1)
    B.call("jawa/set_terrain_batch", ops="RM_SlimeGreenShallow:%d,%d,6,5" % (strips["slime"][0][0], z - 2))
    B.call("jawa/set_terrain_batch", ops="RM_TarShallow:%d,%d,6,5" % (strips["tar"][0][0], z - 2))
    B.ticks(2)
    terr = B.call("jawa/get_terrain_batch", rects="58,%d,30,1" % z).get("ops")
    pid, sp = spawn_colonist(57, z)
    if not pid:
        row("W1_wakes_terrain_walked", "UNMEASURED", "HARNESS", {"spawn": sp})
        return
    draft(pid)
    walked = {}
    for name, cells in strips.items():
        a, b = cells[0], cells[-1]
        B.hp("pawn:%d=tp:%d,%d" % (num(pid), a[0] - 2, a[1]))
        o = B.call("jawa/order_pawn", pawnId=pid, x=b[0] + 1, z=b[1], waitTicks=40, draft=True)   # BENCH: stop mid-strip
        p = pawn(pid)
        pos = (p.get("x"), p.get("z")) if p.get("x") is not None else tpos(p)
        under = B.call("jawa/get_terrain_batch", rects="%d,%d,1,1" % pos).get("ops") if None not in pos else None
        walked[name] = {"pos": pos, "terrainUnder": under, "ticks": o.get("ticksElapsed"), "accepted": o.get("orderAccepted")}
        shot("W1_wake_%s" % name, (a[0] - 3, a[1] - 3, 12, 7))
    want = {"water": "RM_Fill_Water", "slime": "RM_SlimeGreen", "tar": "RM_Tar"}
    ok = all(want[n] in str(w.get("terrainUnder")) for n, w in walked.items())
    row("W1_wakes_terrain_walked", verdict(ok and sget(S_FW, "liquidWakesEnabled") in (True, "True", "true"), None), "MOD",
        {"walked": walked, "row": terr, "liquidWakesEnabled": sget(S_FW, "liquidWakesEnabled"),
         "note": "PASS = the setting is on and the colonist was mid-strip on each liquid when the shot was taken"})
    row("W1_wakes_look", "UNMEASURED", "LOOK", {"shots": res["shots"][-3:], "bar": "a V of ripples behind him: broad in "
        "water (wake 1.0), smaller in green slime (0.4), barely a stir in tar (0.1)"})
    row("W1_wake_counter", "UNMEASURED", "HARNESS", "no instrument: RM_LiquidSurface.MapComponentTick spawns WaterRipple flecks "
        "without counting them, and no probe verb reads wakes (missing: a static wake-spawn counter)")
    draft(pid)


# ============================================================================ B1: bottles and tank jobs
def blk_B1():
    rect = (134, 40, 24, 14)
    if not site(rect, "B1_site_ready"):
        return
    tank = (140, 44)
    build("RM_LiquidTank:%d,%d" % tank)
    B.ticks(2)
    ft = B.hp("filltank:%d,%d=%s,50" % (tank + (WATER,)))
    tid = PH._tank(B, tank).get("id")
    hid, sp = spawn_colonist(147, 44, worker=True)
    wp = B.call("jawa/set_work_priority", pawnId=hid, workType="Hauling", priority=1) if hid else {}
    if not (ft.get("success") and tid is not None and hid and wp.get("readBack") == 1):
        row("B1_bottles_and_tank_jobs", "UNMEASURED", "HARNESS", {"filltank": ft, "tank": tid, "hauler": sp,
                                                                     "workPriority": wp})
        return
    is_full = (lambda t: tdef(t) == "RM_Bottle_FreshWater")
    is_empty = (lambda t: tdef(t) == "RM_BottleEmpty")

    def job_now():
        for p in B.hp("colonists").get("pawns") or []:
            if p.get("id") == num(hid):
                return p.get("job")
        return None

    # 1. no auto-pour into a Store tank
    B.call("jawa/spawn_batch", ops="RM_Bottle_FreshWater:144,48;RM_Bottle_FreshWater:145,48;RM_Bottle_FreshWater:146,48")
    B.ticks(2)
    full0 = len(things(rect, is_full))
    u0 = units(tank)
    jobs1 = watch(lambda: [units(tank), job_now()], 1500)
    u1 = units(tank)
    no_auto = u1 == u0 and not any(j[1] == "RM_EmptyIntoTankJob" for j in jobs1)
    # 2. an ordered pour into the Store tank works
    bottles = things(rect, is_full)
    oj = {}
    if bottles:
        oj = B.call("jawa/ordered_job", pawnId=hid, jobDef="RM_EmptyIntoTankJob", targetAId=bottles[0].get("id"),
                    targetBId="RM_LiquidTank%d" % tid, waitTicks=30)
    tr2 = watch(lambda: units(tank), 750, step=150)
    row("B1_ordered_pour_into_store", verdict((tr2[-1] or 0) > (u1 or 0), None if bottles else "no filled bottle left to order"),
        "MOD", {"orderedJob": {k: oj.get(k) for k in ("success", "accepted", "afterJobDef", "note")}, "units": [u1] + tr2})
    # 3. empty bottles still fill from a Store tank
    B.call("jawa/spawn_batch", ops="RM_BottleEmpty:144,50;RM_BottleEmpty:145,50")
    B.ticks(2)
    u3, full3, empty3 = units(tank), len(things(rect, is_full)), len(things(rect, is_empty))
    tr3 = watch(lambda: [units(tank), job_now()], 2000)
    u4, full4, empty4 = units(tank), len(things(rect, is_full)), len(things(rect, is_empty))
    row("B1_bottles_fill_from_store", verdict((u4 or 0) < (u3 or 0), None if empty3 else "no empty bottle staged"), "MOD",
        {"units": [u3, u4], "fullBottles": [full3, full4], "emptyBottles": [empty3, empty4], "trace": tr3})
    # 4. control: a Fill tank takes bottles UNASKED (else the step-1 negative proves nothing)
    job = set_job(tank, "Fill")
    u5 = units(tank)
    tr5 = watch(lambda: [units(tank), job_now()], 2000)
    took = (tr5[-1][0] or 0) > (u5 or 0)
    row("B1_control_fill_tank_takes_unasked", verdict(took, None if (job["ok"] and len(things(rect, is_full))) else
        "precondition: Fill job %s, filled bottles %s" % (job, full4)), "MOD", {"units": [u5, tr5[-1][0]], "trace": tr5, "job": job})
    row("B1_no_autopour_into_store", verdict(no_auto, None if took else
        "the control never poured into a Fill tank either: the hauler was not hauling, so 'no pour' proves nothing"), "MOD",
        {"units": [u0, u1], "filledBottles": full0, "trace": jobs1})
    shot("B1_bottles_store_tank", rect)


# ============================================================================ P1: pit exposure
def blk_P1():
    rect = (14, 40, 20, 12)
    if not site(rect, "P1_site_ready"):
        return
    pc, cc = (22, 46), (28, 46)
    d = dig(pc, 4)
    rp = B.call("jawa/flowworks_pit_report", x=pc[0], z=pc[1])
    a, ra = spawn_colonist(*pc)
    b, rb = spawn_colonist(*cc)
    if not (a and b):
        row("P1_pit_exposure", "UNMEASURED", "HARNESS", {"spawnPit": ra, "spawnControl": rb})
        return
    for pid, cell in ((a, pc), (b, cc)):
        B.call("jawa/pawn_gear", pawn=pid, action="clear", clearWhat="apparel")
        draft(pid)
        B.hp("pawn:%d=tp:%d,%d" % (num(pid), cell[0], cell[1]))
    B.ticks(260)
    rp = B.call("jawa/flowworks_pit_report", x=pc[0], z=pc[1])
    in_pit = any(str(p.get("id")) in (str(a), str(num(a))) for p in rp.get("pawns") or [])
    if not (rp.get("isSuperdeep") and in_pit):
        row("P1_pit_exposure", "UNMEASURED", "SITE", {"dig": d, "pitReport": {k: rp.get(k) for k in
            ("depthRaw", "fillRaw", "isSuperdeep", "pawns", "room")}, "pitPawn": a,
            "why": "the pit pawn is not standing in a D=4 cell"})
        return
    ha, hb = hediffs(a), hediffs(b)
    ca, cb = comfy(a), comfy(b)
    row("P1_exposed_marker", verdict("RM_PitExposure" in ha and "RM_PitExposure" not in hb, None), "MOD",
        {"pit": ha, "control": hb, "comfyPit": ca, "comfyControl": cb, "narrowingSetting": sget(S_FW, "pitExposureNarrowing")})
    # ---- the pit cell's room temperature vs open ground, coupling on / off (RM_Patch_PitRoomCoupling redundant?)
    def temps():
        tp, tc = B.call("jawa/cell_temperature", cell="%d,%d" % pc), B.call("jawa/cell_temperature", cell="%d,%d" % cc)
        rmp = (B.call("jawa/room_get", x=pc[0], z=pc[1], includeOutdoors=True).get("rooms") or [{}])[0]
        return {"pit": tp.get("temperature"), "open": tc.get("temperature"), "outdoor": tp.get("outdoorTemp"),
                "pitRoom": {k: rmp.get(k) for k in ("id", "cellCount", "temperature", "openRoofCount", "isOutdoors",
                                                    "psychologicallyOutdoors")}}
    coup0 = sget(S_FW, "pitTemperatureCoupling")
    t_on = temps()
    sset(S_FW, "pitTemperatureCoupling", 0)
    B.ticks(500)
    t_off = temps()
    sset(S_FW, "pitTemperatureCoupling", coup0)
    B.ticks(500)
    t_on2 = temps()
    okr, room = proof(NS_PROOF, "ProofRoom", "%d,%d;%d,%d" % (pc + cc))
    same = all(t["pit"] is not None and t["open"] is not None and abs(t["pit"] - t["open"]) <= 0.5 for t in (t_on, t_off, t_on2))
    row("P1_pitroom_coupling_redundant", verdict(same, None if t_on["pit"] is not None else "cell_temperature unreadable"),
        "MOD", {"couplingOn": t_on, "couplingOff": t_off, "couplingOnAgain": t_on2, "coupling": coup0, "proofRoom": room,
                "meaning": "PASS = an unroofed dug pit already reads open-ground temperature with or without the patch "
                           "(redundant for the exposed case); FAIL = the patch moves the pit's temperature"})
    save()

    def safe(cf):
        return (cf[0] - 10, cf[1] + 10) if None not in cf else (None, None)

    def heat(pid):
        h = hediffs(pid)
        return {"Heatstroke": h.get("Heatstroke"), "Hypothermia": h.get("Hypothermia"), "exposed": "RM_PitExposure" in h}

    sa, sb = safe(comfy(a)), safe(comfy(b))
    res["P1_safe"] = {"pit": sa, "control": sb}

    def band_window(lo, hi, label, cond, wait_max):
        """Start `cond`, wait (<= wait_max) for the outdoor temperature to sit in (lo, hi), then watch 2500 ticks."""
        trace, waited = [], 0
        if lo is None or hi is None:
            return None, {"band": [lo, hi], "why": "comfort range unreadable"}
        if cond:
            B.call("jawa/game_condition", action="start", condition=cond, durationTicks=60000)
        t = outdoor()
        while not (lo is not None and lo < (t or -999) < hi) and waited < wait_max:
            B.ticks(500)
            waited += 500
            t = outdoor()
            trace.append(t)
        if not (lo < (t or -999) < hi):
            return None, {"waited": waited, "temps": trace, "band": [lo, hi]}
        win = []
        for _ in range(5):
            B.ticks(500)
            win.append({"T": outdoor(), "pit": heat(a), "control": heat(b)})
        if cond:
            B.call("jawa/game_condition", action="end", condition=cond)
        return win, {"waited": waited, "temps": trace, "band": [lo, hi], "label": label}

    # ---- mild: the outdoor temperature inside the NARROWED safe range for 6 in-game hours: no temperature hediff on either
    mild = []
    for _ in range(6):
        B.ticks(2500)
        mild.append({"T": outdoor(), "pit": heat(a), "control": heat(b)})
    in_mild = all(sa[0] is not None and sa[0] < (m["T"] or -999) < sa[1] for m in mild)
    calm = all(not m["pit"]["Heatstroke"] and not m["pit"]["Hypothermia"] and not m["control"]["Heatstroke"]
               and not m["control"]["Hypothermia"] for m in mild)
    row("P1_mild_nothing_happens", verdict(calm, None if in_mild else "the outdoor temperature left the narrowed safe range %s"
                                           % (sa,)), "MOD", {"trace": mild, "safePit": sa, "safeControl": sb})
    # ---- hot: between the narrowed and the normal safe max
    win, info = band_window(sa[1], sb[1], "hot", "HeatWave", 15000)
    if win is None:
        row("P1_hot_pit_heatstroke_only", "UNMEASURED", "SITE", dict(info, why="no outdoor-temperature setter exists; the "
            "HeatWave condition did not put the outdoor temperature in the band"))
    else:
        hs = [w["pit"]["Heatstroke"] or 0 for w in win]
        row("P1_hot_pit_heatstroke_only", verdict(hs[-1] > 0 and hs[-1] >= hs[0] and not any(w["control"]["Heatstroke"] for w in win)
                                                  and all(sa[1] < (w["T"] or -999) < sb[1] for w in win), None), "MOD",
            dict(info, window=win))
    B.call("jawa/game_condition", action="end", condition="HeatWave")
    for pid in (a, b):
        B.call("jawa/pawn_health", pawn=pid, action="remove", hediff="Heatstroke")
    # ---- cold: between the normal and the narrowed safe min
    win, info = band_window(sb[0], sa[0], "cold", "ColdSnap", 20000)
    if win is None:
        row("P1_cold_pit_hypothermia_only", "UNMEASURED", "SITE", dict(info, why="no outdoor-temperature setter exists; the "
            "ColdSnap condition did not put the outdoor temperature in the band"))
    else:
        hy = [w["pit"]["Hypothermia"] or 0 for w in win]
        row("P1_cold_pit_hypothermia_only", verdict(hy[-1] > 0 and not any(w["control"]["Hypothermia"] for w in win)
                                                    and not any(w["pit"]["Heatstroke"] for w in win)
                                                    and all(sb[0] < (w["T"] or 999) < sa[0] for w in win), None), "MOD",
            dict(info, window=win))
    B.call("jawa/game_condition", action="end", condition="ColdSnap")
    # ---- sheltered: roof the pit cell -> the marker goes within one 250-tick interval; the same pawn's comfort widens by N
    exposed_cf = comfy(a)
    rf = B.call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,1,1" % pc)
    B.ticks(260)
    ha2, roofed_cf, cb2 = hediffs(a), comfy(a), comfy(b)
    n = sget(S_FW, "pitExposureNarrowing")
    try:
        nf = float(n)
        delta_ok = None not in exposed_cf + roofed_cf and abs((exposed_cf[0] - roofed_cf[0]) - nf) < 0.05 \
            and abs((roofed_cf[1] - exposed_cf[1]) - nf) < 0.05
    except (TypeError, ValueError):
        delta_ok = False
    row("P1_sheltered_marker_gone", verdict("RM_PitExposure" not in ha2, None if rf.get("cellsChanged") else
                                            "the roof did not land: %s" % rf), "MOD", {"hediffs": ha2, "roof": rf})
    row("P1_narrowing_is_the_setting", verdict(delta_ok, None), "MOD",
        {"samePawnExposed": exposed_cf, "samePawnRoofed": roofed_cf, "control": cb2, "narrowing": n,
         "controlEqualsRoofed": roofed_cf == cb2})
    shot("P1_pit_and_control", rect)


# ============================================================================ R1: the rigid pipe's four looks
R1S_STATE = {}


def blk_R1():
    rect = (176, 40, 30, 26)
    if not site(rect, "R1_site_ready"):
        return
    row("R1_menu_pick_verb", "UNMEASURED", "HARNESS",
        "no verb drives PipeLook.Pick (the build button's float menu): HoseStyleProbe.Place refuses defs HoseLook does not "
        "style ('not a styled def'), and GSS's cplace is for conduits. This block uses the SAME designator style getter "
        "through its default-look route (RM_MachinerySettings.pipeDefaultLook set per look, no pick stored)")
    did, dd = find_designator(["rm_universalpipe", "universal pipe", "universal-pipe", "universalpipe"],
                              exclude=["cargo"])
    if not did:
        row("R1_looks_survive_build", "UNMEASURED", "HARNESS", "no Architect designator for RM_UniversalPipe found")
        return
    orig = sget(S_MACH, "pipeDefaultLook")
    R1S_STATE["orig"] = orig
    B.call("rimworld/set_god_mode", enabled=False)
    cells = {L: (180 + 3 * i, 44) for i, L in enumerate(LOOKS)}
    stages = {L: {} for L in LOOKS}
    for L, c in cells.items():
        sset(S_MACH, "pipeDefaultLook", L)
        r = B.call("rimworld/apply_architect_designator", designatorId=did, x=c[0], z=c[1], width=1, height=1)
        bp = things((c[0], c[1], 1, 1), lambda t: tdef(t).startswith("Blueprint_"))
        st = raw_style(bp[0].get("id")) if bp else (None, "no blueprint: %s" % r)
        stages[L]["blueprint"] = {"id": bp[0].get("id") if bp else None, "style": st[0], "err": st[1]}
    sset(S_MACH, "pipeDefaultLook", "Futuristic" if orig != "Futuristic" else "Scrapper")   # a default that would mask a lost look
    B.call("jawa/spawn_batch", ops="Steel:182,47,60")
    bid, sp = spawn_colonist(186, 48, worker=True)
    wp = B.call("jawa/set_work_priority", pawnId=bid, workType="Construction", priority=1) if bid else {}
    waited = 0
    while waited < 6000:
        B.ticks(100)
        waited += 100
        done = 0
        for L, c in cells.items():
            for t in things((c[0], c[1], 1, 1)):
                d = tdef(t)
                if d.startswith("Frame_") and "frame" not in stages[L]:
                    s_ = raw_style(t.get("id"))
                    stages[L]["frame"] = {"id": t.get("id"), "style": s_[0], "err": s_[1], "tick": waited}
                if d == "RM_UniversalPipe":
                    if "building" not in stages[L]:
                        s_ = raw_style(t.get("id"))
                        stages[L]["building"] = {"id": t.get("id"), "style": s_[0], "err": s_[1], "tick": waited}
                    done += 1
        if done == len(cells):
            break
    R1S_STATE["built"] = {L: stages[L].get("building", {}).get("id") for L in LOOKS}
    for L in LOOKS:
        want = "RM_UniversalPipe_" + L
        st = stages[L]
        b_ = st.get("building") or {}
        pre = None
        if not (st.get("blueprint") or {}).get("id"):
            pre = "no blueprint placed"
        elif not b_.get("id"):
            pre = "not built within %d ticks (builder %s, Construction priority %s)" % (waited, bid, wp.get("readBack"))
        elif b_.get("style") is None:
            pre = "raw style unreadable: %s" % b_.get("err")
        ok = want in str(st["blueprint"].get("style")) and want in str(b_.get("style")) and \
            ("frame" not in st or want in str(st["frame"].get("style")))
        row("R1_%s_survives_blueprint_frame_building" % L, verdict(ok, pre), "MOD",
            dict(st, want=want, frameSeen="frame" in st))
    # joined runs, one per look, god mode (instant), for the LOOK row
    B.call("rimworld/set_god_mode", enabled=True)
    try:
        for i, L in enumerate(LOOKS):
            sset(S_MACH, "pipeDefaultLook", L)
            z = 50 + 4 * i
            B.call("rimworld/apply_architect_designator", designatorId=did, x=180, z=z, width=6, height=1)
            B.call("rimworld/apply_architect_designator", designatorId=did, x=185, z=z + 1, width=1, height=2)
    finally:
        B.call("rimworld/set_god_mode", enabled=False)
    B.ticks(2)
    run_styles = {L: sorted({str(raw_style(t.get("id"))[0]) for t in things((180, 50 + 4 * i, 6, 3), lambda t: tdef(t) == "RM_UniversalPipe")})
                  for i, L in enumerate(LOOKS)}
    sset(S_MACH, "pipeDefaultLook", orig)
    row("R1_joined_runs_look", "UNMEASURED", "LOOK", {"shot": shot("R1_pipe_four_looks_joined_runs", (178, 43, 14, 23)),
                                                       "rawStylesPerRun": run_styles, "bar": "each run joins seamlessly in its own look; corners join"})


def blk_R1S():
    """R1's save + load (destructive: run last)."""
    built = {L: i for L, i in (R1S_STATE.get("built") or {}).items() if i}
    if not built:
        row("R1_save_load_keeps_looks", "UNMEASURED", "SITE", "R1 built no pipe to carry across a save")
        return
    name = "RM_bench_fwpipes_%s" % time.strftime("%Y%m%d%H%M%S")
    before = V._saves_stat()
    B.call("rimworld/save_game", saveName=name)
    saved = V._wait_saved(name)
    new = sorted(set(V._saves_stat()) - set(before))
    B.call("rimworld/load_game", saveName=name)
    ok, waited = V._wait_playing(B)
    B.ticks(1)
    after = {L: raw_style(i)[0] for L, i in built.items()}
    good = all(("RM_UniversalPipe_" + L) in str(after[L]) for L in built)
    row("R1_save_load_keeps_looks", verdict(good, None if (saved and ok) else "save %s / load %s (%s)" % (saved, ok, waited)),
        "MOD", {"save": name, "newFiles": new, "loadedAfter": waited, "rawStyleAfter": after, "pipes": built,
                "pipeDefaultLookNow": sget(S_MACH, "pipeDefaultLook")})
    if R1S_STATE.get("orig") is not None:
        sset(S_MACH, "pipeDefaultLook", R1S_STATE["orig"])


# ============================================================================ T1: worst tick
def blk_T1():
    B.call("jawa/set_game_speed", speed="Normal")
    time.sleep(3)
    try:
        mct = B.call("jawa/map_comp_timing", ticks=1200, maxSeconds=240, top=80) or {}
    finally:
        B.call("jawa/set_game_speed", speed="Paused")
    comps = mct.get("components") or []
    fw = [c for c in comps if str(c.get("packageId") or "").lower() == FW_PKG or "FlowWorks" in str(c.get("type") or "")]
    rmc = [{k: c.get(k) for k in ("type", "msPerTick", "maxMs", "calls", "totalMs")} for c in fw]
    worst = max([c.get("maxMs") or 0 for c in fw] or [None]) if fw else None
    pre = None if (mct.get("success") and (mct.get("ticksElapsed") or 0) >= 600 and fw) else \
        "timing not usable: success %s, ticksElapsed %s, FlowWorks components %d" % (mct.get("success"), mct.get("ticksElapsed"), len(fw))
    row("T1_worst_tick_le_1ms", verdict(worst is not None and worst <= 1.0, pre), "MOD",
        {"flowworks": rmc, "worstMaxMs": worst, "ticksElapsed": mct.get("ticksElapsed"), "realSeconds": mct.get("realSeconds"),
         "sumMsPerTick": mct.get("sumMsPerTick"), "patchFailures": mct.get("patchFailures"),
         "top5": [{k: c.get(k) for k in ("type", "packageId", "msPerTick", "maxMs")} for c in comps[:5]],
         "note": "maxMs is each component's worst single MapComponentTick call; the fixture is this script's scenes, not "
                 "the design's §4 fixture"})


# ============================================================================ run
# 2026-10-16: this copy stages filltank 100 (= 10 L since the litres re-base cf4f24213d, a hundredth of one level), so L2/L4
# move nothing and read as MOD FAILs; its L6 spawns walk-off witnesses (THEFT_ROW_REPAIR_WITNESS_WALKS_OFF). Those blocks live
# in src/RimMandrake/FlowWorks/northstar/liquid_checks.py (--only L2,L4,L5,L6), litres-scaled. Here they refuse, UNMEASURED.
SUPERSEDED = {"L2", "L4", "L5", "L6"}


def run_block(name, fn):
    if ONLY and name not in ONLY and not (name == "R1S" and "R1" in ONLY):
        return
    if name in SUPERSEDED:
        row("%s_block" % name, "UNMEASURED", "HARNESS",
            "superseded: run src/RimMandrake/FlowWorks/northstar/liquid_checks.py --only %s (litres-scaled)" % name)
        return
    CUR["block"] = name
    t0 = time.time()
    n0 = len(rows)
    print("== %s" % name, flush=True)
    err = None
    try:
        B.call("jawa/incident_queue_clear")
        fn()
    except Exception as ex:  # noqa: BLE001
        err = repr(ex)
        row("%s_block" % name, "UNMEASURED", "HARNESS", {"raised": err, "trace": traceback.format_exc()[-1500:]})
    for pid in WORKERS:
        try:
            draft(pid)
        except Exception:  # noqa: BLE001
            pass
    if V.TAP:
        try:
            V.TAP[0].poll()
        except Exception:  # noqa: BLE001
            pass
    res["blocks"][name] = {"wall_s": round(time.time() - t0, 1), "rows": len(rows) - n0, "raised": err}
    save()


if preflight():
    for nm, f in (("L1", blk_L1), ("L2", blk_L2), ("L3", blk_L3), ("L4", blk_L4), ("L5", blk_L5), ("L6", blk_L6),
                  ("D1", blk_D1), ("W1", blk_W1), ("B1", blk_B1), ("P1", blk_P1), ("R1", blk_R1), ("T1", blk_T1),
                  ("R1S", blk_R1S)):
        run_block(nm, f)
    try:
        logs = V.TAP[0].since() if V.TAP else []
        res["log_warn_err_flowworks"] = [str(x.get("Message", ""))[:300] for x in logs
                                         if "FlowWorks" in str(x.get("Message", "")) + str(x.get("StackTrace", ""))][:40]
        res["log_lost"] = V.TAP[0].lost if V.TAP else None
    except Exception as ex:  # noqa: BLE001
        res["log_error"] = repr(ex)
res["ended"] = time.strftime("%Y-%m-%dT%H:%M:%S")
res["counts"] = {s: sum(1 for r in rows if r["status"] == s) for s in ("PASS", "FAIL", "UNMEASURED")}
save()
print("DONE", OUT, json.dumps(res["counts"]))
