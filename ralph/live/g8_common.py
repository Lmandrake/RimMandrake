"""g8_common.py -- shared helpers for the pass-8 gallery (g8_site.py builds and saves the map, g8_depth.py is batch A,
g8_kit.py is batch B). Run every g8 script with python.exe from the repo root on SteveDesktop (ralph/steve.sh run).

Every run writes to Transient/ralph_fw/g8/<batch>_<tag>_<HHMMSS>/ in Steve's clone:
  log.txt        everything the script did, one line each
  results.jsonl  one JSON row per measurement/assert: {name, value, expected, pass, source, ...}
  shots/         every screenshot of the run (the game writes there through screenshot_cell_rect's outputDirectory;
                 if that ever fails the PNG is copied in from the game's Screenshots folder at the end)
Fetch a run with ralph/live/g8_fetch.sh <run dir name> <local dir> (tars on Steve, one fetch).

The fixture layout is a pure function of ORIGIN (layout() below); g8_site.py builds it there and every batch reads the
same coordinates, so nothing about the layout lives anywhere but this file and ralph/live/GALLERY8.md.
"""
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import fwb  # noqa: E402  (puts src/RimMandrake/Utils and FlowWorks/northstar on sys.path)

MODCHECK = os.path.join(fwb.UTILS, "modcheck")
if MODCHECK not in sys.path:
    sys.path.append(MODCHECK)

# ---------------------------------------------------------------------------------------------------------------- names
SAVE = "RM_FW_Gallery8"            # the gallery map; g8_site.py writes it, the batches load it
BASE_SITE = "calm"                 # test_site_saves.SITES key: RM_TestSite_calm_v3 (AridShrubland, 250x250, quiet)
SETTINGS = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"           # ProofPawnSink(ThingID), ProofLadder("x,z,op")
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"             # ProofClimb("pawn:<ThingID>") -> held / trapped
SUSP = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"      # ProofBuild, ProofReach("id;x,z"), ProofUnderPath
LADU = "RimMandrake.FlowWorks.RM_LadderUtility"              # Reaches(Thing ladder), MaxLevelsOf(BuildableDef)
WALLS = "RimMandrake.FlowWorks.SectionLayer_RMExcavationWalls"  # RedrawAll()
# Being added in pass 8 (absent on the old build: called if present, UNMEASURED if not). Names as briefed.
T_DRAW = "RimMandrake.FlowWorks.RM_PitDepthDraw"
M_STATE = "DepthDrawState"         # (int thingIDNumber) -> "cell=x,z depth=D sink=S drawnZ=Z lipZ=L face=F hold=H k=K"
M_SET_HOLD = "SetSinkHoldAbove"    # (float)
M_SET_K = "SetSinkPerLevel"        # (float)
T_HANG = "RimMandrake.FlowWorks.Pits.RM_SuspensionHang"
M_TREAT = "SetTreatment"           # (int 0 suspension | 1 rope walk | 2 cable-stayed) -> string

KIND = "Colonist"                  # every subject pawn is this PawnKindDef
UNIFORM = {"gender": "Male", "bodyType": "Male", "headType": "Male_AverageNormal", "hair": "Shaved", "beard": "NoBeard"}
DRESS = ("Apparel_BasicShirt", "Apparel_Pants")   # every subject wears exactly these (no hat to change the head line)
ROOT_PLAY = 7.2                    # ~64 px a cell on Steve's game window (CLAUDE.md "play zoom")
ROOT_WIDE = 20.0
LEVEL_M = 0.5                      # one excavation level

# The calm site's open ground for the gallery (chosen from g8_site.py probe; see GALLERY8.md). x grows east, z north.
ORIGIN = (60, 150)


def layout(o=None):
    """Every fixture of the gallery: cells (lists of (x,z)), depth in levels, and the rects shots frame.
    Rects are (x, z, w, h). Coordinates are absolute map cells for ORIGIN `o`."""
    ox, oz = o or ORIGIN
    L = {"origin": (ox, oz)}
    # A1: seven 3x3 holes at levels 0,1,2,3,4,8,16 (undug, 0.5, 1, 1.5, 2, 4, 8 m), 2-cell gaps; z = oz..oz+2
    a1 = []
    for k, d in enumerate((0, 1, 2, 3, 4, 8, 16)):
        x0 = ox + 5 * k
        a1.append({"k": k, "levels": d, "metres": d * LEVEL_M, "x0": x0, "z0": oz,
                   "cells": sq(x0, oz, 3, 3), "subject": (x0 + 1, oz + 2)})       # north row centre
    L["A1"] = a1
    L["A1_control"] = (ox - 3, oz + 2)                                             # undug ground west of the row
    L["A1_rects"] = {"west": (ox - 5, oz - 1, 19, 6), "east": (ox + 14, oz - 1, 20, 6), "all": (ox - 5, oz - 1, 39, 6)}
    # A2: two 3x3 holes at 4 m and 8 m; occupants on the south (west col), middle (centre col), north (east col) rows
    a2 = []
    for j, d in enumerate((8, 16)):
        x0 = ox + 5 * j
        z0 = oz + 7
        a2.append({"levels": d, "metres": d * LEVEL_M, "x0": x0, "z0": z0, "cells": sq(x0, z0, 3, 3),
                   "subjects": {"south": (x0, z0), "middle": (x0 + 1, z0 + 1), "north": (x0 + 2, z0 + 2)}})
    L["A2"] = a2
    L["A2_rect"] = (ox - 2, oz + 5, 12, 7)
    # A3: graded trench, 3 wide, running north-south: row r (z = z0+r) at min(r, 8) levels, rows 0..11
    x3, z3 = ox + 13, oz + 7
    L["A3"] = {"x0": x3, "z0": z3, "w": 3, "h": 12,
               "rows": [{"z": z3 + r, "levels": min(r, 8)} for r in range(12)],
               "walk": [(x3 + 1, z3 + r) for r in range(12)], "start": (x3 + 1, z3 - 1),
               "rect": (x3 - 2, z3 - 1, 7, 14)}
    # A4: the same strip running east-west: column c (x = x0+c) at min(c, 8) levels, columns 0..11
    x4, z4 = ox + 20, oz + 7
    L["A4"] = {"x0": x4, "z0": z4, "w": 12, "h": 3,
               "cols": [{"x": x4 + c, "levels": min(c, 8)} for c in range(12)],
               "walk": [(x4 + c, z4 + 1) for c in range(12)], "start": (x4 - 1, z4 + 1),
               "rect": (x4 - 2, z4 - 2, 16, 7)}
    # B1: 5x5 pit 2 m deep, a wall ladder (RM_Ladder) on the middle of each wall, facing its wall (rot N,E,S,W)
    bx, bz = ox, oz + 23
    L["B1"] = {"x0": bx, "z0": bz, "levels": 4, "cells": sq(bx, bz, 5, 5),
               "ladders": {0: (bx + 2, bz + 4), 1: (bx + 4, bz + 2), 2: (bx + 2, bz), 3: (bx, bz + 2)},
               "subject": (bx + 1, bz + 1), "outside": (bx + 2, bz - 2), "rect": (bx - 2, bz - 2, 9, 9)}
    # B2: 3x3 pits; a portable ladder on one wall each (N, E, S, W) at 2 m, a too-deep control (reach+1 levels) with a
    # portable on every wall, and a bare 2 m pit (no ladder) as the reachability baseline
    b2 = []
    for j, (tag, walls) in enumerate((("N", (0,)), ("E", (1,)), ("S", (2,)), ("W", (3,)), ("deep", (0, 1, 2, 3)),
                                      ("bare", ()))):
        x0, z0 = ox + 9 + 5 * j, oz + 24
        lad = {0: (x0 + 1, z0 + 2), 1: (x0 + 2, z0 + 1), 2: (x0 + 1, z0), 3: (x0, z0 + 1)}
        b2.append({"tag": tag, "x0": x0, "z0": z0, "cells": sq(x0, z0, 3, 3), "levels": None if tag == "deep" else 4,
                   "portables": {r: lad[r] for r in walls}, "subject": (x0 + 1, z0 + 1), "outside": (x0 + 1, z0 - 2)})
    L["B2"] = b2
    L["B2_rects"] = {"a": (ox + 7, oz + 22, 16, 7), "b": (ox + 22, oz + 22, 16, 7), "all": (ox + 7, oz + 22, 31, 7)}
    # B3: a dug hole 5 wide (x) by 9 long (z), 2 m deep; an east-west suspension bridge over its middle row
    hx, hz = ox + 42, oz + 19
    L["B3"] = {"x0": hx, "z0": hz, "w": 5, "h": 9, "levels": 4, "cells": sq(hx, hz, 5, 9),
               "anchors": ((hx - 1, hz + 4), (hx + 5, hz + 4)), "deck_z": hz + 4,
               "walk": [(hx + 2, hz + 7), (hx + 2, hz + 4), (hx + 2, hz + 1)],     # BEFORE (north), MID (under), AFTER
               "rect": (hx - 3, hz - 1, 11, 11)}
    # B4: climbing gear on the ground beside a vanilla jump pack; a colonist wearing the gear
    gx, gz = ox + 52, oz + 24
    L["B4"] = {"gear": (gx, gz), "vanilla": (gx + 1, gz), "vanillaDef": "Apparel_PackJump", "wearer": (gx + 3, gz),
               "rect": (gx - 2, gz - 2, 8, 5)}
    # everything the site touches (cleared, painted Soil, unfogged, unroofed), with a margin
    L["site_rect"] = (ox - 8, oz - 4, 72, 37)
    L["overview"] = (ox - 6, oz - 2, 68, 33)
    return L


def sq(x0, z0, w, h):
    return [(x0 + i, z0 + k) for i in range(w) for k in range(h)]


# ------------------------------------------------------------------------------------------------------- the bridge
class G8(fwb.FW):
    """fwb.FW with the client's unknown-parameter guard ON for the g8 scripts' own calls (fwb/validation_core pass
    check=False, which lets a misspelt key run the tool on its defaults and report success). loose_call is the old
    behaviour, handed to the shared modcheck loaders (test_site_saves, quiet_site), whose calls are theirs to keep."""
    strict = True

    def _raw(self, tool, kw):
        return self.S.call(tool, kw, check=self.strict)

    def loose_call(self, tool, **kw):
        was, self.strict = self.strict, False
        try:
            return self.call(tool, **kw)
        finally:
            self.strict = was


class Run(object):
    """One run's folder, log, results and shot list."""

    def __init__(self, batch, tag):
        self.batch, self.tag = batch, tag
        self.stamp = time.strftime("%H%M%S")
        self.name = "%s_%s_%s" % (batch, tag, self.stamp)
        self.dir = os.path.join(fwb.OUT, "g8", self.name)
        self.shotdir = os.path.join(self.dir, "shots")
        os.makedirs(self.shotdir, exist_ok=True)
        self.logf = open(os.path.join(self.dir, "log.txt"), "a", encoding="utf-8")
        self.resf = open(os.path.join(self.dir, "results.jsonl"), "a", encoding="utf-8")
        self.shots = []
        self.nshot = 0
        self.counts = {"pass": 0, "fail": 0, "unmeasured": 0, "info": 0}
        self.harness = []
        self.t0 = time.time()
        self.copy_fallback = False
        self.log("RUN", self.name, "dir", self.dir)

    def log(self, *a):
        s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
        print(s, flush=True)
        self.logf.write(s + "\n")
        self.logf.flush()

    def result(self, name, value, expected=None, ok=None, source=None, **extra):
        """ok: True/False = an assert; None = info; 'UNMEASURED' = the reading could not be made."""
        row = {"name": name, "value": value, "expected": expected,
               "pass": ok if ok in (True, False) else (None if ok is None else str(ok)), "source": source}
        row.update(extra)
        row["t"] = round(time.time() - self.t0, 1)
        self.resf.write(json.dumps(row, default=str) + "\n")
        self.resf.flush()
        key = "pass" if ok is True else "fail" if ok is False else "info" if ok is None else "unmeasured"
        self.counts[key] += 1
        self.log("RESULT", name, "=", json.dumps(value, default=str)[:300], "| expected", expected, "| pass", row["pass"],
                 "| src", source)

    def harness_error(self, what):
        self.harness.append(what)
        self.log("HARNESS", what)

    def close(self):
        self.log("SUMMARY", self.name, json.dumps(self.counts), "shots", len(self.shots), "harness_errors",
                 len(self.harness), "elapsed_s", round(time.time() - self.t0))
        for h in self.harness:
            self.log("  harness:", h)
        self.logf.close()
        self.resf.close()


def bridge():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    return G8()


def j(o, n=400):
    return json.dumps(o, default=str)[:n]


def ok_(r):
    return isinstance(r, dict) and r.get("success") is True


def safe(B, R, tool, **kw):
    """A call whose failure is logged as a harness error instead of raised (the guard's raise included)."""
    try:
        r = B.call(tool, **kw)
    except Exception as e:  # noqa: BLE001
        R.harness_error("%s raised %s: %s" % (tool, type(e).__name__, str(e)[:300]))
        return {"success": False, "error": str(e)}
    return r or {}


def num(pid):
    m = re.search(r"(\d+)$", str(pid))
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------------------------------- static calls
def scall(B, typ, meth, args=""):
    """jawa/static_call -> (status, text). status: OK | MISSING (type or method absent on this build) | ERROR."""
    r = B.call("jawa/static_call", type=typ, method=meth, args="" if args is None else str(args)) or {}
    if r.get("success") is True:
        return "OK", str(r.get("result"))
    msg = str(r.get("error") or r.get("message") or r)
    if "Type not found" in msg or "No public static" in msg:
        return "MISSING", msg[:300]
    return "ERROR", msg[:600]


KV = re.compile(r"([A-Za-z]+)=(\S+)")


def kv(text):
    """'a=1 b=x,y c=0.3' -> {'a': '1', 'b': 'x,y', 'c': '0.3'}."""
    return dict(KV.findall(text or ""))


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def depth_state(B, pid):
    """The new DepthDrawState read (by thingIDNumber) -> (status, dict, raw)."""
    st, txt = scall(B, T_DRAW, M_STATE, num(pid))
    return st, (kv(txt) if st == "OK" else {}), txt


def legacy_sink(B, pid):
    """The old build's ProofPawnSink read (by ThingID) -> (status, dict, raw)."""
    st, txt = scall(B, PROMO, "ProofPawnSink", pid)
    if st == "OK" and txt.startswith("REFUSED"):
        st = "ERROR"
    return st, (kv(txt) if st == "OK" else {}), txt


def read_pawn(B, R, pid, label):
    """Both reads for one pawn, logged. -> {'state': dict|None, 'legacy': dict|None, 'sink': float|None, 'src': str}.
    sink comes from DepthDrawState when the build has it, else from ProofPawnSink (source 'legacy')."""
    st, d, raw = depth_state(B, pid)
    lst, ld, lraw = legacy_sink(B, pid)
    R.log("READ", label, pid, "| state", st, raw[:200], "| legacy", lst, lraw[:220])
    out = {"state": d if st == "OK" else None, "stateStatus": st, "legacy": ld if lst == "OK" else None,
           "sink": None, "src": None}
    if st == "OK" and fnum(d.get("sink")) is not None:
        out["sink"], out["src"] = fnum(d.get("sink")), "DepthDrawState"
    elif lst == "OK" and fnum(ld.get("sink")) is not None:
        out["sink"], out["src"] = fnum(ld.get("sink")), "ProofPawnSink(legacy)"
    return out


# ----------------------------------------------------------------------------------------------------- game control
def tick(B):
    gi = B.call("rimworld/get_game_info") or {}
    return (gi.get("state") or {}).get("tick") or gi.get("ticksGame") or gi.get("tick")


def pause(B, R=None):
    B.call("rimworld/set_time_speed", speed="Paused")
    a = tick(B)
    time.sleep(0.4)
    b = tick(B)
    if R is not None and a != b:
        R.harness_error("pause did not hold: tick %s -> %s" % (a, b))
    return a == b


def step(B, n):
    return B.call("rimworld/step_game_ticks", ticks=int(n), pauseFirst=True, timeoutMs=max(15000, int(n) * 60)) or {}


def play(B, ms):
    """Real Normal-speed time (the tween only converges while the game runs: PawnTweener scales by TickRateMultiplier)."""
    B.call("rimworld/play_for", durationMs=int(ms), speed="Normal", forceRequestedSpeed=True)
    B.call("rimworld/set_time_speed", speed="Paused")


def local_hour(B):
    # vanilla GenDate.HourOfDay: (TicksAbs + TimeZoneAt(longitude) * 2500) % 60000 / 2500, TimeZoneAt = round(lon / 15)
    r = B.call("jawa/time_date_at") or {}
    lon, ta = r.get("longitude"), r.get("absTicksUsed")
    if lon is None or ta is None:
        return None
    tz = int(round(max(-12.0, min(12.0, lon / 15.0))))
    return ((ta + tz * 2500) % 60000) / 2500.0


def quiet(B, R):
    """No raids, clear sky, nobody hostile: Phoebe/Peaceful, threat scale 0, queue cleared, Clear locked."""
    r = safe(B, R, "jawa/storyteller_swap", storytellerDef="Phoebe", difficultyDef="Peaceful")
    R.log("storyteller", j(r, 200))
    r = safe(B, R, "jawa/difficulty_tune", threatScale=0.0, allowBigThreats=False)
    R.log("difficulty", j(r, 200))
    safe(B, R, "jawa/incident_queue_clear")
    r = safe(B, R, "jawa/weather_set", weather="Clear", lockWeather=True)
    R.log("weather", r.get("success"), j(r.get("after") or r.get("message"), 120))
    r = safe(B, R, "jawa/kill_hostiles")
    R.log("kill_hostiles", j({k: r.get(k) for k in ("success", "killed", "count", "message") if k in r}, 200))


def colonists(B):
    cen = B.call("jawa/pawn_census", faction="player") or {}
    return [p for p in cen.get("pawns") or [] if p.get("isColonist")]


def census(B, ids):
    ids = [i for i in ids if i]
    if not ids:
        return []
    return (B.call("jawa/pawn_census", ids=",".join(ids)) or {}).get("pawns") or []


def where(B, pid):
    c = census(B, [pid])
    return (c[0].get("x"), c[0].get("z")) if c else None


def draft_all(B, R):
    for p in colonists(B):
        if not p.get("drafted"):
            safe(B, R, "jawa/set_draft", pawnId=p["id"], drafted=True)


def depths(B, x, z, w, h):
    ex = B.call("jawa/flowworks_excavation_rect", x=x, z=z, w=w, h=h, onlyNonZero=True, includeTerrain=False) or {}
    return {(c.get("x"), c.get("z")): c.get("d") for c in ex.get("cells") or ex.get("rows") or []}


def depth_at(B, c):
    return depths(B, c[0], c[1], 1, 1).get(tuple(c), 0) or 0


def subject(B, R, cell, label, uniform=True, face="south", draft=True):
    """Spawn one KIND colonist ON `cell` (jawa/spawn_pawn puts the first pawn exactly there), same look as every other
    subject, drafted, facing south and locked there. -> ThingID or None."""
    r = safe(B, R, "jawa/spawn_pawn", kindDef=KIND, x=cell[0], z=cell[1], faction="player", count=1)
    pid = ((r.get("pawns") or [{}])[0]).get("id")
    if not pid:
        R.harness_error("spawn %s at %s failed: %s" % (label, cell, j(r, 300)))
        return None
    if uniform:
        safe(B, R, "jawa/set_pawn_gender", pawn=pid, gender=UNIFORM["gender"])
        safe(B, R, "jawa/set_pawn_appearance", pawn=pid, bodyType=UNIFORM["bodyType"], headType=UNIFORM["headType"],
             hair=UNIFORM["hair"], beard=UNIFORM["beard"])
        safe(B, R, "jawa/pawn_gear", pawn=pid, action="clear", clearWhat="all")
        for d in DRESS:
            safe(B, R, "jawa/pawn_gear", pawn=pid, action="wear", **{"def": d})
    if draft:
        safe(B, R, "jawa/set_draft", pawnId=pid, drafted=True)
    if face:
        safe(B, R, "jawa/set_pawn_rotation", pawnId=pid, dir=face, lockRotation=True)
    at = where(B, pid)
    if at != tuple(cell):
        R.harness_error("subject %s %s landed at %s, wanted %s" % (label, pid, at, cell))
    R.log("subject", label, pid, "at", at)
    return pid


def walk_to(B, R, pid, cell, wait_ticks=90, tries=6):
    """One drafted Goto to `cell`, at Normal speed (order_pawn unpause), re-issued until the pawn stands there.
    -> (arrived, position)."""
    at = None
    for k in range(tries):
        o = safe(B, R, "jawa/order_pawn", pawnId=pid, x=cell[0], z=cell[1], draft=True, waitTicks=wait_ticks,
                 timeoutSeconds=20)
        at = where(B, pid)
        if at == tuple(cell):
            return True, at
        if k == 0:
            R.log("walk", pid, "->", cell, "not yet at", at, j({kk: o.get(kk) for kk in ("success", "message", "rows")
                                                                  if kk in o}, 300))
    return False, at


def settle(B, ms=500):
    """Let a standing pawn's tween converge for real (Normal speed `ms`), pause, then snap every tween to its root
    (jawa/settle_tweens, paused, no tick) so the frame shows the resting draw."""
    if ms:
        play(B, ms)
    B.call("jawa/settle_tweens", pauseFirst=True)


def redraw(B, R):
    st, txt = scall(B, WALLS, "RedrawAll", "")
    if st != "OK":
        R.log("redraw", st, txt[:120])


# ------------------------------------------------------------------------------------------------------- settings
def setting(B, field, value=None):
    if value is None:
        r = B.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field) or {}
        return r.get("value") if r.get("success") else None
    r = B.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field, value=str(value)) or {}
    return r.get("valueAfter") if r.get("success") else None


def set_sink(B, R, k=None, hold=None):
    """Apply a depth-draw setting pair. The pass-8 setters when the build has them; otherwise k falls back to the
    pitSinkPerLevel settings field (same number), and hold is UNMEASURED. -> {'k': how, 'hold': how}."""
    how = {}
    if k is not None:
        st, txt = scall(B, T_DRAW, M_SET_K, "%g" % k)
        if st == "OK":
            how["k"] = "SetSinkPerLevel -> %s" % txt[:80]
        else:
            got = setting(B, "pitSinkPerLevel", "%g" % k)
            how["k"] = "pitSinkPerLevel field -> %s (setter %s)" % (got, st)
    if hold is not None:
        st, txt = scall(B, T_DRAW, M_SET_HOLD, "%g" % hold)
        if st == "OK":
            how["hold"] = "SetSinkHoldAbove -> %s" % txt[:80]
        else:
            got = setting(B, "pitSinkHoldAbove", "%g" % hold)
            how["hold"] = ("pitSinkHoldAbove field -> %s" % got) if got is not None else "UNMEASURED (setter %s)" % st
    redraw(B, R)
    R.log("SETTING", "k=%s hold=%s" % (k, hold), j(how, 300))
    return how


# --------------------------------------------------------------------------------------------------------- shots
def _win_dir(p):
    return os.path.abspath(p)


def shot(B, R, name, rect, root, frame=True, wait=1.2, pad=0):
    """A unique-named screenshot of rect (x,z,w,h) at camera root `root`, written into the run's shots/ folder.
    frame=True moves the camera first and waits `wait` s for the draw; frame=False keeps the camera where the last shot
    left it (a FIXED camera for a walk: the same rect and root give the same view)."""
    R.nshot += 1
    fname = "g8%s_%s_%02d_%s_r%g" % (R.batch[:1].upper(), R.stamp, R.nshot, name, root)
    kw = dict(x=int(rect[0]), z=int(rect[1]), width=int(rect[2]), height=int(rect[3]), paddingCells=pad,
              rootSize=float(root), doNotResetCamera=True)
    try:
        B.call("jawa/clear_ui", hideHudSeconds=30)
        if frame:
            B.call("rimworld/frame_cell_rect", x=kw["x"], z=kw["z"], width=kw["width"], height=kw["height"],
                   paddingCells=pad, rootSize=float(root))
            time.sleep(wait)
        else:
            time.sleep(0.25)
        extra = {} if R.copy_fallback else {"outputDirectory": _win_dir(R.shotdir)}
        r = B.call("rimworld/screenshot_cell_rect", fileName=fname, **dict(kw, **extra)) or {}
    except Exception as e:  # noqa: BLE001
        R.harness_error("shot %s raised %s: %s" % (name, type(e).__name__, str(e)[:200]))
        return None
    path = r.get("path") or r.get("filePath") or r.get("imagePath")
    if not ok_(r) or not path:
        R.harness_error("shot %s failed: %s" % (name, j(r, 300)))
        return None
    R.shots.append({"name": name, "file": os.path.basename(str(path)), "path": path, "rect": rect, "root": root})
    R.log("SHOT", name, "r%g" % root, os.path.basename(str(path)))
    return path


PX_PER_CELL_AT_1 = 458.0   # measured on Steve's window 2026-11-08: 63.6 px a cell at root 7.2, 22.9 at root 20


def png_size(path):
    import struct
    try:
        with open(path, "rb") as f:
            head = f.read(24)
        return struct.unpack(">II", head[16:24])
    except (OSError, struct.error):
        return None


def finish_shots(R, wait_s=20):
    """The screenshot is written asynchronously: wait until every shot of the run exists in shots/ (copying any the game
    wrote elsewhere), then list what is missing as a harness error."""
    t0 = time.time()
    missing = []
    while time.time() - t0 < wait_s:
        missing = []
        for s in R.shots:
            dst = os.path.join(R.shotdir, s["file"])
            if os.path.exists(dst):
                continue
            src = str(s["path"])
            if os.path.exists(src):
                try:
                    shutil.copy2(src, dst)
                    continue
                except OSError:
                    pass
            missing.append(s["file"])
        if not missing:
            break
        time.sleep(1.0)
    for m in missing:
        R.harness_error("shot file never appeared: %s" % m)
    for s in R.shots:
        sz = png_size(os.path.join(R.shotdir, s["file"]))
        s["px"] = sz
        want = (s["rect"][2] * PX_PER_CELL_AT_1 / float(s["root"]), s["rect"][3] * PX_PER_CELL_AT_1 / float(s["root"]))
        if sz and (sz[0] < 0.9 * want[0] or sz[1] < 0.9 * want[1]):
            R.harness_error("shot %s is %s px, the rect wants about %d x %d: clipped by the window" % (
                s["file"], sz, want[0], want[1]))
    with open(os.path.join(R.dir, "shots.json"), "w", encoding="utf-8") as f:
        json.dump(R.shots, f, indent=1, default=str)
    R.log("shots in", R.shotdir, ":", len(R.shots) - len(missing), "of", len(R.shots))


# ----------------------------------------------------------------------------------------------------- the save
def saves_dir():
    if os.name == "nt":
        return os.path.join(os.environ.get("USERPROFILE", r"C:\Users\sjlewis"), "AppData", "LocalLow", "Ludeon Studios",
                            "RimWorld by Ludeon Studios", "Saves")
    return "/mnt/c/Users/sjlewis/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves"


def load_gallery(B, R, save=None):
    """Load the gallery save from the main menu through test_site_saves.load_site (the calm site's loader: menu first,
    load, Playing + map, the map-only quiet profile, the calm sky, queue cleared), then quiet() and draft everyone."""
    import test_site_saves as TS
    save = save or SAVE
    if not os.path.exists(os.path.join(saves_dir(), save + ".rws")):
        R.harness_error("no %s.rws in %s: build it with g8_site.py first" % (save, saves_dir()))
        return False
    t = time.time()
    try:
        rec = TS.load_site(B.loose_call, BASE_SITE, name=save, check=False)
    except Exception as e:  # noqa: BLE001
        R.harness_error("load_site raised %s: %s" % (type(e).__name__, str(e)[:300]))
        return False
    R.log("LOAD", save, "%.0f s" % (time.time() - t), j({k: rec.get(k) for k in ("verified", "problems", "load_s")}, 400))
    if not rec.get("verified"):
        R.harness_error("load of %s not verified: %s" % (save, rec.get("problems")))
        return False
    pause(B, R)
    quiet(B, R)
    draft_all(B, R)
    h = local_hour(B)
    R.log("hour", h, "tick", tick(B))
    return True
