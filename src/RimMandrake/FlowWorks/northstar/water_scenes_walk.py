"""water_scenes_walk.py -- the six water scenes (S1..S6), staged live one at a time for the owner to WATCH and judge.

Owner, 2026-10-17 (at the keyboard): *"Please just replicate [the six water scenes] in the walkthrough of FlowWorks and
I'll judge them there."*

Scenes: design/RimMandrake/vv_methods/water_scenes_2026-10-16.scenes.json (sealed; this script reads it, never edits it)
and the human copy water_scenes_for_approval_2026-10-16.md. Each scene is staged on its own plot of ONE quicktest map at
the SHIPPED FlowWorks settings, except the scene file's own global exceptions (rain fill off, refill off, weather clear).
The clock advances by real game ticks, one liquid pulse (pulseIntervalTicks, read live) per step, with a pause between
steps so the eye can follow; the camera is framed on the scene. At every milestone the script prints what the doc says
he should see beside what the game measures, and saves a screenshot under Transient/fw_scenes/live/.

  python.exe src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py prep            # quicktest map, calm, settings
  python.exe src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py stage S1        # build S1 at pulse 0, frame it
  python.exe src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py run S1          # advance S1 pulse by pulse
  python.exe src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py go S2           # stage + run in one
  python.exe src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py all [--from S2] # every scene; between scenes waits
                                                     for Transient/fw_scenes/live/CONTINUE to appear (then deletes it)
  python.exe src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py restore         # shipped settings back
  options: --pace 1.5 (wall seconds between pulses) --no-shots --fresh-map (go/all: a new quicktest map per scene)
           --no-wait (all: no CONTINUE file between scenes)
  python3 src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py all --mock --no-wait --pace 0 --no-shots [--mock-fail S4]
                                                     # OFFLINE: the script's own paths only (water_scenes_mock.py)
READINGS ARE DECILITRES (2026-10-17, P3 exact-level engine): a canal square holds a sheet that no whole notch counts, so
every dug square is also read through RM_NorthstarProofs.ProofReadout ("Hole 0.5 m . Water 0.24 m (474 L)", litres to the
whole litre) and a pond's stock in decilitres (stock * 10,000); tolerance TOL_DL per square read. Level rows (".lvl") ask
ProofLevelSurface for each body's surface gap (bar: 1 cm). The sealed scenes file's whole-notch wording stays printed as
"doc"; the level-water expectation (level_solution) is printed beside it as "level".
A crash in a scene is printed in full, kept at Transient/fw_scenes/live/<scene>_traceback_<stamp>.txt, recorded as a
CRASHED row, and the walk goes on. Colonists are fed every 5,000 ticks and a GovernorStop is printed and resumed once:
the 2026-10-17 S4/S5 tracebacks were the vitals latch stopping the clock on starving quicktest colonists.
Stage each scene ONCE per map: re-staging on the same plot keeps the old pond body's receded stock (measured: S6 run 2
started at pond 22, not 32). For a clean sitting: `prep --fresh-map`, then S1..S6 in order (S6 saves and reloads the map;
its saves RM_fw_scene_S6_* stay in the Saves folder).

Words the output uses: MATCHES (the game did what the doc says), DIFFERS (it did not), UNMEASURED (could not be asked or
not staged: the reason is printed), OPEN RULING (the doc's needs_ruling: the game's current behaviour is shown against
each option, never chosen). Nothing here is a verdict: the owner judges.
"""
import argparse
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
for _p in (UTILS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

SCENES_JSON = os.path.join(REPO, "design", "RimMandrake", "vv_methods", "water_scenes_2026-10-16.scenes.json")
OUT = os.path.join(REPO, "Transient", "fw_scenes", "live")
OUT_MOCK = os.path.join(REPO, "Transient", "fw_scenes", "mock")      # --mock output never lands beside live evidence
FLAG = os.path.join(OUT, "CONTINUE")
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
GATES = "RimMandrake.FlowWorks.RM_FlowDoorRules"   # RM_Sluice / RM_SecurityGrateDoor are Building_RM_FlowDoor
HPROBE = "RimMandrake.FlowWorks.Hose.HoseProbe"
WATER = "RM_Fluid_Water"
LEVEL_UNITS = 10000            # RM_Volume.UnitsPerLevel: tank/hose units (decilitres) per level
SETTLE_PULSES = 8              # S2.d: unchanged pulses in a row that make a state "settled"
# the scene file's global exceptions to shipped defaults ("rain off, refill/seepage off, fire off, weather clear")
SCENE_OVERRIDES = {"rainFillsExcavationsEnabled": False, "refillEnabled": False}
SHIPPED = {"rainFillsExcavationsEnabled": True, "refillEnabled": True, "deepBedsEnabled": True}
# SITE (v2 triage 2026-10-18, same fix as validation_v2): since P11 a LIMITED pond painted mid-game records a lake floor (0.5 m
# shore shelf on its outer ring) when first classified, so the ponds below no longer hold what level_solution (floors -2.0 /
# -0.5 m, the terrain rule) says. Whether painted ponds should get a floor is the owner's question
# P11_FLOOR_ON_PAINTED_PONDS and is NOT decided here: every scene RUN pins deepBedsEnabled off from staging to its end and
# puts the previous value back (try/finally, crash included), so the scenes are independent of the answer.
SCENE_PIN = {"deepBedsEnabled": False}

# ---------------------------------------------------------------- layout (map coords; west edge x = 0)
# Edge scenes: a WaterDeep lake 14 wide x 11 tall on the west edge (154 cells >= minLimitlessBodyCells 50, so LIMITLESS),
# the canal leaves its east shore along the lake's middle row. 14 wide, because a dug cell closer than
# GenGrid.NoBuildEdgeWidth (10) to an edge is an edge SINK (IsSinkCell): the first trial (lake 8 wide, canal at x 8..15)
# drained the canal's mouth into the sink every pulse (sinkTransferredTotal 13 in 15 pulses) and the canal stopped at
# cell 1 -- the scene file's own condition "every dug cell sits well outside the map-edge sink band". Interior scenes
# sit >= 30 cells from every edge.
LAKE_W, LAKE_H = 14, 11
BANDS = {"S1": 30, "S2": 50, "S4": 70, "S4g": 90, "S6g": 110, "S6g2": 130}     # lake bottom z per edge scene
INTERIOR = {"S3": (40, 30), "S3q": (40, 50), "S5": (70, 30), "S5e": (70, 60), "S5f": (70, 76), "S5g": (70, 90),
            "S6": (110, 30), "S6b": (110, 50)}


def mid(band):
    return BANDS[band] + LAKE_H // 2


def run(x0, z, n, d=1):
    return [(x0 + k, z) for k in range(n)]


# ---------------------------------------------------------------- decilitres (pure helpers, selftested offline)
# One square holds LEVEL_UNITS dL per 0.5 m notch (RM_Volume.UnitsPerLevel; 1 dL = 0.1 L), so a metre of water in one
# square is DL_PER_METRE dL. ProofReadout prints litres to the whole litre: one square is read to +-5 dL; TOL_DL = 10 is
# one litre of slack per square read, the width every level row uses (n squares read -> n * TOL_DL).
DL_PER_METRE = 2 * LEVEL_UNITS
TOL_DL = 10
SURFACE_BAR_M = 0.01
_READOUT_WATER = re.compile(r"Hole\s+([\d.,]+)\s*m\D+?Water\s+([\d.,]+)\s*m\s*\(\s*([\d,]+)\s*L\s*\)")


def parse_readout(txt):
    """ProofReadout answer -> dict(kind="water", hole_m, water_m, litres, dl) | dict(kind="limitless") | dict(kind="none")
    | None (refused / unreadable). dl = litres * 10 (the readout rounds to the whole litre)."""
    s = str(txt or "").strip()
    if s.startswith("OK"):
        s = s[2:].strip()
    elif s:
        return None
    if s in ("", "-"):
        return dict(kind="none") if s == "-" else None
    if s.startswith("Endless"):           # bar limitless_body_marked: he typed 2026-10-20, "it should simply say Endless"
        return dict(kind="limitless", text=s)
    if s.startswith("Open water"):        # the retired wording: still a limitless mark, but the bar's word is Endless
        return dict(kind="limitless", text=s, old_wording=True)
    m = _READOUT_WATER.search(s)
    if not m:
        return None
    lit = int(m.group(3).replace(",", ""))
    return dict(kind="water", hole_m=float(m.group(1).replace(",", "")), water_m=float(m.group(2).replace(",", "")),
                litres=lit, dl=lit * 10, text=s)


def level_solution(groups, total_dl):
    """The exact-level answer for water that stands at ONE surface over several groups of squares. groups = [(n_squares,
    floor_m)] (floor below ground, metres, negative); total_dl = decilitres in the whole connected body. Returns
    (surface_m, [dl per square of each group]); depth of a group = max(0, surface - floor). Units: DL_PER_METRE dL per
    metre of depth per square (P3 log: S5 A canal 0.237 m, B 4.5 cm, E 0.111 m, F 1 m)."""
    gs = [(int(n), float(f)) for n, f in groups]
    top = max(f for _, f in gs) + 1e6
    lo, hi = min(f for _, f in gs), 0.0
    cap = sum(n * (0.0 - f) * DL_PER_METRE for n, f in gs)
    if total_dl > cap + 1e-6:
        raise ValueError("body holds %s dL but its squares only %s dL to the brim" % (total_dl, cap))
    for _ in range(200):
        mid_ = (lo + hi) / 2.0
        have = sum(n * max(0.0, mid_ - f) * DL_PER_METRE for n, f in gs)
        if have < total_dl:
            lo = mid_
        else:
            hi = mid_
    s = (lo + hi) / 2.0
    return s, [max(0.0, s - f) * DL_PER_METRE for _, f in gs]


def near(a, b, n=1):
    """a and b agree within n squares' worth of readout slack (n * TOL_DL dL); None never agrees."""
    return a is not None and b is not None and abs(a - b) <= TOL_DL * max(1, n)


def settled_at(states, n, ok=None):
    """Index of the first state from which the next n states are all equal to it (n unchanged pulses in a row) AND ok(state)
    holds (default: any); None when there is none. S2.d took a 4-pulse plateau in the middle of the fill for 'settled'
    (live 2026-10-17: [3 3 3 3] at p7-p10, finished at p12); n=8 refuses it, `ok` (pond and trench full) refuses a
    settle on a half-filled state."""
    for i in range(len(states) - n):
        if all(states[i] == states[i + j] for j in range(1, n + 1)) and (ok is None or ok(states[i])):
            return i
    return None


def parse_surface(txt):
    """ProofLevelSurface answer "OK n worst G m;x,z:squares:gap:min:max;..." -> [dict(at, squares, gap_m, min_m, max_m)],
    largest gap first. ValueError when it is not an OK answer (a refusal or an older DLL is UNMEASURED, never a pass)."""
    s = str(txt or "").strip()
    if not s.startswith("OK "):
        raise ValueError("ProofLevelSurface did not answer OK: %r" % s[:160])
    out = []
    for part in [q for q in s.split(";")[1:] if q.strip()]:
        f = part.split(":")
        if len(f) != 5:
            raise ValueError("unparsed body entry %r" % part)
        out.append(dict(at=f[0], squares=int(f[1]), gap_m=float(f[2]), min_m=float(f[3]), max_m=float(f[4])))
    return out


def dl_of(m, c):
    """Decilitres read for cell c in a cells() reading; None when it was not read (older shape, failed call, undug)."""
    v = (m or {}).get(c)
    return v[2] if v is not None and len(v) > 2 else None


def dl_sum(m, cs):
    vals = [dl_of(m, c) for c in cs]
    return None if any(v is None for v in vals) else sum(vals)


def wet(m, c):
    """A square holds water: any decilitre when the readout is there, else a whole notch (a walk against an old DLL)."""
    d = dl_of(m, c)
    return d > 0 if d is not None else (m or {}).get(c, (0, 0))[1] > 0


def holds(m, c, levels):
    """A square holds `levels` full notches (to the brim of a depth-`levels` square) within the readout slack."""
    d = dl_of(m, c)
    return d >= levels * LEVEL_UNITS - TOL_DL if d is not None else (m or {}).get(c, (0, 0))[1] >= levels


def stock_dl(body):
    """A pond body's water in decilitres: the report's stock is notches as a float (dL / 10,000)."""
    try:
        return int(round(float((body or {}).get("stock")) * LEVEL_UNITS))
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- bridge
ROOT_FLOOR = 11.0       # rootSize below ~11 breaks the map mesh render (skills/rimbridge/references/traps.md)
ROOT_CEIL = 60.0        # the engine's far limit
SCREEN_ASPECT = 16.0 / 9.0     # width/height; the 3467x1826 shots are 1.90, so 16:9 errs toward a little extra margin


def fit_root_size(rect, pad=2, aspect=SCREEN_ASPECT, floor=ROOT_FLOOR, ceil=ROOT_CEIL):
    """The camera rootSize (half the visible height, in cells) that shows the whole rect plus pad cells on every side,
    clamped to [floor, ceil] (pure)."""
    _x, _z, w, h = rect
    need = max((h + 2 * pad) / 2.0, (w + 2 * pad) / (2.0 * aspect))
    return round(min(ceil, max(floor, need)), 1)


class Walk(object):
    def __init__(self, args):
        if getattr(args, "mock", False):
            import water_scenes_mock as M
            self.V = M.MockV()
            self.B = M.MockBridge(fail_scene=args.mock_fail)
        else:
            import validation_core as V
            self.V = V
            self.B = V.Bridge()
        self.args = args
        self.log_lines = []
        self.rows = []
        self.since_feed = 0
        self.terrain = {}
        self.refused = []              # [(what, cell)] excavation drives the bridge refused (see _drive)
        os.makedirs(OUT, exist_ok=True)

    def call(self, tool, **kw):
        return self.B.call(tool, **kw)

    def say(self, s=""):
        print(s)
        sys.stdout.flush()
        self.log_lines.append(s)

    def proof(self, typ, method, arg):
        r = self.call("jawa/static_call", type=typ, method=method, args=arg) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return r.get("success") is True and not txt.startswith("REFUSED"), txt

    def hp(self, cmd):
        return self.B.probe_of(HPROBE, cmd)

    def feed(self):
        """Top up every colonist's Food and Rest. WHY (2026-10-17): the S4 step-C and S5 tracebacks of the first live walk
        were clockgate.GovernorStop 'starving: food category Starving' (governor_stops.jsonl 16:28Z): the quicktest
        colonists starve over a long sitting, the vitals latch stops safe_advance, and the uncaught stop killed the scene.
        Upkeep, never a verdict: the scenes measure water, not pawns."""
        fed = []
        for c in self.hp("colonists").get("pawns") or []:
            good = True
            for need in ("Food", "Rest"):
                r = self.call("jawa/pawn_need", pawn=c["id"], action="need", need=need, level=1.0)
                if not isinstance(r, dict) or r.get("success") is False:
                    good = False
                    self.say("         FEED REFUSED %s %s: %s (the vitals latch may stop the clock)" % (c["id"], need, str(r)[:120]))
            if good:
                fed.append(c["id"])
        self.since_feed = 0
        return fed

    def ticks(self, n):
        """Game time through the governed clock. Colonists are fed every 5,000 ticks; a GovernorStop is printed in full,
        the colonists fed, and the REST of the step resumed once; a second stop in the same step raises."""
        if self.since_feed >= 5000:
            self.feed()
        self.since_feed += n
        try:
            self.B.ticks(n)
        except Exception as ex:  # noqa: BLE001 - clockgate.GovernorStop; anything else re-raises below
            if not getattr(ex, "is_surprise_abort", False):
                raise
            done = int((getattr(ex, "result", {}) or {}).get("executed") or 0)
            self.say("         GOVERNOR STOP (fed colonists, resuming the last %d tick(s) once): %s" % (n - done, ex))
            self.feed()
            if n - done > 0:
                self.B.ticks(n - done)

    def tick_now(self):
        return (self.call("jawa/flowworks_engine_state") or {}).get("ticksGame")

    def interval(self):
        v = (self.call("jawa/mod_settings_field", typeName=S_FW, action="get", field="pulseIntervalTicks") or {}).get("value")
        try:
            return int(float(v))
        except (TypeError, ValueError):
            # the shipped default stands in so the walk can step, but it is not a reading: say so where the eye is
            self.say("         PULSE INTERVAL UNREAD (%r): stepping the shipped default 250 ticks, NOT a measured interval" % (v,))
            return 250

    def readout(self, c):
        """ProofReadout over one square -> parse_readout dict, or None (refused / unreadable: never a silent zero)."""
        ok, txt = self.proof(NSP, "ProofReadout", "%d,%d" % (c[0], c[1]))
        return parse_readout(txt) if ok else None

    def readout_lines(self, cs):
        """['x,z: <the readout string verbatim>'] for the audit trail on a row (annotate_water_scenes prints them)."""
        out = []
        for c in cs:
            ok, txt = self.proof(NSP, "ProofReadout", "%d,%d" % (c[0], c[1]))
            out.append("%d,%d: %s" % (c[0], c[1], (txt[3:] if txt.startswith("OK ") else txt).strip() if ok else "UNREAD " + txt[:60]))
        return out

    def cells(self, cells, dl=True):
        """{(x,z): (depth, fill, dl)} plus the engine's pulse count, read in one ProofFluidRow over the bbox. dl = the
        decilitres in a DUG square (ProofReadout, litres * 10; None when unread), 0 for an undug one."""
        xs, zs = [c[0] for c in cells], [c[1] for c in cells]
        x0, z0 = min(xs), min(zs)
        w, h = max(xs) - x0 + 1, max(zs) - z0 + 1
        out, pulse = {}, None
        # ProofFluidRow caps w*h at 400: split tall boxes into row bands
        step = max(1, 400 // w)
        for zb in range(z0, z0 + h, step):
            arg = "%d,%d,%d,%d" % (x0, zb, w, min(step, z0 + h - zb))
            ok, txt = self.proof(PROMO, "ProofFluidRow", arg)
            if not ok:
                ok, txt = self.proof(PROMO, "ProofFluidRow", arg)       # one retry: a dropped call is not a reading
            if not ok:
                # never a silent None (the old code returned None and the caller crashed on m.get): print and go on
                self.say("         READ FAILED ProofFluidRow %s: %s (cells in it read as '?')" % (arg, txt[:200]))
                continue
            head = txt.split(" ", 3)
            for tok in head[1:3]:
                if tok.startswith("pulse="):
                    pulse = int(tok.split("=")[1])
            for t in (head[3] if len(head) > 3 else "").split(";"):
                if ":" in t:
                    xz, rest = t.split(":", 1)
                    x, z = map(int, xz.split(","))
                    parts = rest.split("/")
                    out[(x, z)] = (int(parts[0]), int(parts[1]))
                    if len(parts) > 3:
                        self.terrain[(x, z)] = parts[3]
        if dl:
            bad = []
            for c in list(out):
                d, f = out[c]
                if d <= 0:
                    out[c] = (d, f, 0)
                    continue
                r = self.readout(c)
                if r is not None and r["kind"] == "water":
                    out[c] = (d, f, r["dl"])
                else:
                    out[c] = (d, f, None)
                    bad.append(c)
            if bad:
                self.say("         READ FAILED ProofReadout at %s (decilitres unread there; whole notches stand in)" % bad[:4])
        return out, pulse

    def grid(self, sq, m=None):
        """Per-square 'depth/fill:terrain' of a pond, one row per z (south row first, west to east), read now unless a
        reading `m` is passed. For the 0/4/0 question: a level pond reads the same fill in every square."""
        if m is None:
            m, _ = self.cells(sq)
        zs = sorted({c[1] for c in sq})
        rows = [sorted([c for c in sq if c[1] == z]) for z in zs]
        return " | ".join(" ".join("%s/%s:%s" % (tuple(m.get(c, ("?", "?")))[:2] + (_tshort(self.terrain.get(c)),)) for c in r)
                          for r in rows)

    def body(self, c, classify=False):
        r = self.call("jawa/flowworks_body_report", x=c[0], z=c[1], classify=classify) or {}
        return r.get("body") or {}

    def _drive(self, what, c, **kw):
        """flowworks_excavation_drive, reply checked: a refusal is printed and counted (self.refused), never taken for a
        staged square. The reply is returned (a dict, {} when the bridge gave none) with its success key as the bridge set it."""
        r = self.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], **kw)
        if not isinstance(r, dict) or r.get("success") is False:
            self.refused.append((what, tuple(c)))
            self.say("         STAGING REFUSED: %s at %s: %s" % (what, tuple(c), str(r)[:160]))
            return {"success": False}
        return r

    def dig(self, c, n, fill=-1):
        return self._drive("dig", c, deepenLevels=n, setFill=fill)

    def set_fill(self, c, f):
        return self._drive("set_fill", c, deepenLevels=0, setFill=f)

    def fill_in(self, c, n=1):
        return self._drive("fill_in", c, deepenLevels=0, setFill=-1, fillInLevels=n)

    def build(self, ops, stuff=None):
        kw = dict(ops=ops, faction="player", wipeExisting=False)
        if stuff:
            kw["stuff"] = stuff
        return self.call("jawa/build_batch", **kw) or {}

    def clear_site(self, rect):
        """Soil, no things, no roof, no fog, and any old dug cells filled back in (ProofResetRect)."""
        x, z, w, h = rect
        ok, txt = self.proof(NSP, "ProofResetRect", "%d;%d;%d;%d" % rect)
        if not ok:
            self.say("         SITE RESET REFUSED %s: %s (old dug cells or things may remain)" % (rect, txt[:120]))
        return self.V.prepare_site(self.B, rect, self.rows, "site_%d_%d" % (x, z))

    def frame(self, rect):
        """Centre the camera on rect and zoom so ALL of it is in frame: fit_root_size, never below the engine floor.
        HARNESS (owner_review_stage 2026-10-23, WATER_LOOK_DIAGNOSE_GREY_ON_THE_ROT): the old rootSize 8 then
        frame_cell_rect left EVERY frame at the closest zoom (114 px a cell, ~16 cells tall) -- frame_cell_rect did not
        zoom OUT either -- so a 66-cell row showed 5 pits and the 64x70 overview a handful of squares; and 8 is below
        the ~11 floor where the map mesh render breaks (rimbridge traps.md). The zoom is now computed, not asked of a
        tool, and read back into self.last_cam."""
        x, z, w, h = rect
        self.call("jawa/clear_ui", all=True)
        self.call("rimworld/jump_camera_to_cell", x=int(x + w // 2), z=int(z + h // 2))
        self.call("rimworld/set_camera_zoom", rootSize=fit_root_size(rect))
        self.last_cam = self.call("rimworld/get_camera_state")

    def shot(self, name, rect):
        if self.args.no_shots:
            return None
        self.frame(rect)
        time.sleep(1.5)
        # a unique game-side name: with a reused one the copy below found LAST run's file already present and copied it
        r = self.call("jawa/take_screenshot", fileName="fwscene_%s_%d" % (name, int(time.time()))) or {}
        src = r.get("filePath")
        for _ in range(12):
            if src and os.path.exists(src):
                break
            time.sleep(0.5)
        try:
            dst = os.path.join(OUT, name + ".png")
            shutil.copyfile(src, dst)
            return os.path.relpath(dst, REPO)
        except Exception as ex:  # noqa: BLE001
            return "screenshot copy failed: %s (%s)" % (ex, src)

    def paint_lake(self, band):
        z0 = BANDS[band]
        self.call("jawa/set_terrain_batch", ops="WaterDeep:0,%d,%d,%d" % (z0, LAKE_W, LAKE_H))
        self.ticks(2)
        b = self.body((2, z0 + LAKE_H // 2), classify=True)
        return b

    def write_log(self, scene):
        p = os.path.join(OUT, "%s_%s.txt" % (scene, time.strftime("%Y%m%dT%H%M%S")))
        with open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(self.log_lines) + "\n")
        return os.path.relpath(p, REPO)


def fills_str(m, cells):
    """One token per square: LITRES (dL / 10, to the litre) when the engine's decilitres were read, else the whole notches."""
    m = m or {}
    out = []
    for c in cells:
        if c not in m:
            out.append("?")
        elif dl_of(m, c) is not None:
            out.append("%d" % round(dl_of(m, c) / 10.0))
        else:
            out.append("%d" % m[c][1])
    return " ".join(out)


def dl_str(m, cells):
    """The same squares in decilitres ('?' where unread)."""
    return " ".join(("%d" % dl_of(m, c)) if dl_of(m, c) is not None else "?" for c in cells)


def _tshort(t):
    """Terrain defName shortened for a grid: WaterDeep -> WD, WaterShallow -> WS, Soil -> So, RM_x -> its first 6."""
    if not t:
        return "?"
    if t.startswith("Water"):
        return "W" + "".join(ch for ch in t[5:] if ch.isupper())[:2]
    return t[:6]


def one_run(m, cells):
    """True when the wet cells are one unbroken run starting at cells[0]."""
    ws = [wet(m, c) for c in cells]
    if not any(ws):
        return True
    k = ws.index(False) if False in ws else len(ws)
    return all(ws[:k]) and not any(ws[k:])


def all_read(hist, cells):
    """True when every pulse's reading holds every cell in `cells`. A 'never wet' / 'none changed' row over squares the
    walk could not read is vacuous (wet() of a missing square is False), so such a row is UNMEASURED, not MATCHES."""
    return all(c in m for _, m, _ in hist for c in cells)


def verdict(ok):
    return "UNMEASURED" if ok is None else ("MATCHES" if ok else "DIFFERS")


def by_pulse(hist, cells, k, bound):
    """A 'first full at pulse k, by pulse `bound`' row: True/False, or None when it never read full AND some pulse could not
    read every square (holds() of a missing square is False, so an unread walk would otherwise read DIFFERS)."""
    if k is None and not all_read(hist, cells):
        return None
    return k is not None and k <= bound


def scene_doc(sid):
    with open(SCENES_JSON, encoding="utf-8") as f:
        doc = json.load(f)
    return next(s for s in doc["scenes"] if s["id"] == sid)


def expect_line(w, sid, eid, measured, ok, extra="", level="", readout=None, claim=None):
    """One expected row. `level` = what exact-level water predicts (printed beside the sealed doc's whole-notch wording and
    kept on the row); `readout` = ProofReadout strings verbatim for the audit trail; `claim` overrides the doc text."""
    s = scene_doc(sid)
    e = next((x for x in s["expected"] if x["id"] == eid), None)
    claim = claim or (e["claim"] if e else eid)
    w.say("  %-6s %-10s doc: %s" % (eid, verdict(ok), claim))
    if level:
        w.say("  %-6s %-10s level: %s" % ("", "", level))
    w.say("  %-6s %-10s game: %s%s" % ("", "", measured, (" | " + extra) if extra else ""))
    row = dict(id=eid, status=verdict(ok), doc=claim, game=str(measured))
    if level:
        row["level"] = level
    if readout:
        row["readout"] = list(readout)
        w.say("  %-6s %-10s readout: %s" % ("", "", " || ".join(readout)))
    w.rows.append(row)


def level_row(w, rid, rect, what):
    """The level-surface bar for the bodies in `rect` (x,z,w,h), read from game state by ProofLevelSurface: every body's
    surface gap must be <= SURFACE_BAR_M. UNMEASURED (never a pass) when the DLL predates the method, the answer is not OK,
    or no water was seen. The per-body gaps are kept on the row for annotate_water_scenes."""
    claim = "Every square of a connected body of still water stands at one surface height, to within 1 cm (owner R9, 2026-10-17)."
    arg = "%d,%d,%d,%d" % tuple(rect)
    ok, txt = w.proof(NSP, "ProofLevelSurface", arg)
    try:
        if not ok:
            raise ValueError(txt[:160])
        bodies = parse_surface(txt)
        if not bodies:
            raise ValueError("no still-water squares read in %s" % (arg,))
    except ValueError as ex:
        w.say("  %-6s %-10s doc: %s" % (rid, "UNMEASURED", claim))
        w.say("  %-6s %-10s game: %s (%s)" % ("", "", ex, what))
        w.rows.append(dict(id=rid, status="UNMEASURED", doc=claim, game="%s (%s)" % (ex, what)))
        return None
    worst = max(b["gap_m"] for b in bodies)
    gaps = ["body at %s: %d sq, gap %.4f m (surface %.4f..%.4f m)" % (b["at"], b["squares"], b["gap_m"], b["min_m"], b["max_m"])
            for b in bodies]
    st = verdict(worst <= SURFACE_BAR_M)
    w.say("  %-6s %-10s doc: %s" % (rid, st, claim))
    w.say("  %-6s %-10s game: %s: %d bod%s, worst gap %.4f m; %s" % ("", "", what, len(bodies), "y" if len(bodies) == 1 else "ies",
                                                                  worst, "; ".join(gaps[:6])))
    w.rows.append(dict(id=rid, status=st, doc=claim, game="%s: worst gap %.4f m in %d bodies" % (what, worst, len(bodies)), gaps=gaps))
    return worst


def ruling_line(w, sid, qid, observed):
    s = scene_doc(sid)
    q = next(x for x in s["needs_ruling"] if x["id"] == qid)
    w.say("  %-6s OPEN RULING  %s" % (qid, q["question"]))
    for k, v in sorted(q["options"].items()):
        w.say("         (%s) %s" % (k, v))
    w.say("         game today: %s" % observed)
    w.rows.append(dict(id=qid, status="OPEN RULING", game=observed))


# ---------------------------------------------------------------- the pulse loop
def pulse_loop(w, name, cells_all, n, tick_fn, rect, shots_at=(), stop_when=None):
    """Advance n pulses, one real pulse interval per step. tick_fn(pulse, m, w) prints the per-pulse line and returns a
    dict kept in the history. Returns the history [(pulse, m, extra)]."""
    iv = w.interval()
    m, p0 = w.cells(cells_all)
    m = m or {}
    hist = [(0, m, tick_fn(0, m, w))]
    for k in range(1, n + 1):
        w.ticks(iv)
        m, pc = w.cells(cells_all)
        m = m or {}
        hist.append((k, m, tick_fn(k, m, w)))
        if k in shots_at:
            w.say("         screenshot: %s" % w.shot("%s_p%02d" % (name, k), rect))
        if stop_when and stop_when(k, m):
            break
        time.sleep(w.args.pace)
    return hist


def first_pulse(hist, pred):
    for k, m, _ in hist:
        if pred(m):
            return k
    return None


# ---------------------------------------------------------------- S1
def s1_geom():
    z = mid("S1")
    return dict(lake=(2, z), canal=run(LAKE_W, z, 8), rect=(0, BANDS["S1"] - 2, LAKE_W + 14, LAKE_H + 4))


def stage_S1(w):
    g = s1_geom()
    w.clear_site(g["rect"])
    b = w.paint_lake("S1")
    for c in g["canal"]:
        w.dig(c, 1)
    w.say("S1 staged: lake %s (limitless=%s, %s cells); canal of 8 depth-1 cells %s..%s, dug dry" % (
        b.get("id"), b.get("limitless"), b.get("cellCount"), g["canal"][0], g["canal"][-1]))
    w.say("         screenshot: %s" % w.shot("S1_p00", g["rect"]))


def run_S1(w):
    g = s1_geom()
    canal = g["canal"]
    b0 = w.body(g["lake"])

    def tick(k, m, w_):
        b = w_.body(g["lake"])
        w_.say("  pulse %2d  canal [%s]  lake limitless=%s stock=%s" % (k, fills_str(m, canal), b.get("limitless"), b.get("stock")))
        return b
    h = pulse_loop(w, "S1", canal, 14, tick, g["rect"], shots_at=(3, 10, 14))
    full = first_pulse(h, lambda m: all(holds(m, c, 1) for c in canal))
    expect_line(w, "S1", "S1.a", "all 8 hold 1 level first at pulse %s" % full, by_pulse(h, canal, full, 10))
    broken = [k for k, m, _ in h if not one_run(m, canal)]
    expect_line(w, "S1", "S1.b", "pulses where the wet part was NOT one run from the lake: %s" % (broken or "none"),
                None if not all_read(h, canal) else not broken)
    dried = [k for i, (k, m, _) in enumerate(h) for c in canal
             if i and wet(h[i - 1][1], c) and not wet(m, c)]
    expect_line(w, "S1", "S1.c", "a wet cell went dry at pulses: %s" % (sorted(set(dried)) or "never"),
                None if not all_read(h, canal) else not dried)
    lim = [x.get("limitless") for _, _, x in h]
    expect_line(w, "S1", "S1.d", "lake limitless at every pulse: %s (stock %s -> %s)" % (
        all(lim), b0.get("stock"), h[-1][2].get("stock")), None if any(v is None for v in lim) else all(lim))   # an unread body is UNMEASURED, not DIFFERS


# ---------------------------------------------------------------- S2
def s2_geom():
    z = mid("S2")
    pond = [(LAKE_W, z), (LAKE_W + 1, z), (LAKE_W, z + 1), (LAKE_W + 1, z + 1)]
    return dict(lake=(2, z), pond=pond, trench=run(LAKE_W + 2, z, 6), rect=(0, BANDS["S2"] - 2, LAKE_W + 14, LAKE_H + 4))


def stage_S2(w):
    g = s2_geom()
    w.clear_site(g["rect"])
    b = w.paint_lake("S2")
    for c in g["pond"]:
        w.dig(c, 4)
    for c in g["trench"]:
        w.dig(c, 1)
    w.say("S2 staged: lake %s (limitless=%s); a dug 2x2 depth-4 pond touching it; a 6-cell depth-1 trench off its far side; all dry"
          % (b.get("id"), b.get("limitless")))
    w.say("         screenshot: %s" % w.shot("S2_p00", g["rect"]))


def run_S2(w):
    g = s2_geom()
    pond, trench = g["pond"], g["trench"]

    def tick(k, m, w_):
        w_.say("  pulse %2d  pond [%s]  trench [%s]  (litres)   pond squares (depth/fill:terrain, south row | north row): %s" % (
            k, fills_str(m, pond), fills_str(m, trench), w_.grid(pond, m)))
        return None
    h = pulse_loop(w, "S2", pond + trench, 60, tick, g["rect"], shots_at=(10, 30, 60))
    # plan P1's L2 bar (WATER_SCENES_PROVE_AFTER_THE_CREEP_FIX): every pulse, each pond square within one level (10,000 dL)
    # of the pond squares it touches (no [4 0 4 0])
    gaps, worst_all, unread = [], 0, []
    for k, m, _ in h:
        pairs = [(dl_of(m, a), dl_of(m, b)) for a in pond for b in pond if abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1]
        if any(None in pr for pr in pairs):
            unread.append(k)            # ignorance, not a gap: a pulse it could not read never counts as DIFFERS
            continue
        worst = max(abs(x - y) for x, y in pairs)
        worst_all = max(worst_all, worst)
        if worst > LEVEL_UNITS:
            gaps.append("p%d gap %d dL [%s]" % (k, worst, dl_str(m, pond)))
    claim = "Every pulse, each pond square holds within one level of the pond squares it touches (no [4 0 4 0])."
    lvl_ok = False if gaps else (None if unread else True)
    w.say("  %-6s %-10s doc: %s" % ("S2.lvl", verdict(lvl_ok), claim + " (plan P1 bar, not a scenes-file row)"))
    w.say("  %-6s %-10s game: pulses with a gap over 1 level (10,000 dL): %s; widest gap of any pulse %d dL (level water: the "
          "pond rises as ONE surface, so 0); pulses with pond squares unread: %s" % ("", "", gaps[:8] or "none", worst_all,
                                                                                   unread[:8] or "none"))
    w.rows.append(dict(id="S2.lvl", status=verdict(lvl_ok), doc=claim, game="%s; widest %d dL; unread at %s" % (
        gaps[:8] or "none", worst_all, unread[:8] or "none")))
    pf = first_pulse(h, lambda m: all(holds(m, c, 4) for c in pond))
    tf = first_pulse(h, lambda m: all(holds(m, c, 1) for c in trench))
    expect_line(w, "S2", "S2.a", "all 4 pond cells at 4 first at pulse %s (40,000 dL = 4,000 L each)" % pf, by_pulse(h, pond, pf, 30),
                level="each pond square holds 40,000 dL (2.00 m) within %d dL" % TOL_DL)
    expect_line(w, "S2", "S2.b", "all 6 trench cells at 1 first at pulse %s (10,000 dL = 1,000 L each)" % tf, by_pulse(h, trench, tf, 30),
                level="each trench square holds 10,000 dL (0.50 m, brim) within %d dL" % TOL_DL)
    broken = [k for k, m, _ in h if not one_run(m, trench)]
    expect_line(w, "S2", "S2.c", "pulses where the wet trench was NOT one run from the pond: %s" % (broken or "none"),
                None if not all_read(h, trench) else not broken)
    # S2.d: SETTLED = N unchanged pulses in a row with the scene FULL (a pause mid-fill is not settled; live 2026-10-17 the
    # old 3-pulse test took the [3 3 3 3] plateau at p7-p10 for it)
    states = [tuple(dl_of(m, c) if dl_of(m, c) is not None else m.get(c, (0, 0))[1] for c in pond + trench) for _, m, _ in h]
    full = lambda s: all(s[i] is not None and s[i] >= 4 * LEVEL_UNITS - TOL_DL for i in range(len(pond))) and \
        all(s[len(pond) + i] is not None and s[len(pond) + i] >= LEVEL_UNITS - TOL_DL for i in range(len(trench)))
    si = settled_at(states, SETTLE_PULSES, ok=full)
    settle = None if si is None else h[si][0]
    changed = [k for k, m, _ in h if settle is not None and k > settle and states[k] != states[si]]
    expect_line(w, "S2", "S2.d", "settled (full, %d unchanged pulses in a row) at pulse %s; changes after that: %s" % (
        SETTLE_PULSES, settle, changed or "none"), None if settle is None else not changed,
        level="a full pond and trench read the same decilitres for every later pulse")
    level_row(w, "S2.lvl.end", g["rect"], "S2 pond + trench after 60 pulses")


# ---------------------------------------------------------------- S3
def s3_geom():
    ox, oz = INTERIOR["S3"]
    pond = [(ox + 1 + i, oz + 1 + j) for i in range(4) for j in range(3)]
    canal = run(ox + 15, oz + 2, 6)
    return dict(pond=pond, canal=canal, pump=(ox + 9, oz + 2), reelA=(ox + 9, oz + 3), reelB=(ox + 9, oz),
                intake=(ox + 4, oz + 2), intake_alt=[(ox + 4, oz + 1), (ox + 4, oz + 3)], outflow=canal[0],
                battery=(ox + 12, oz + 6),
                gap=[(ox + 5 + i, oz + 2) for i in range(3)] + [(ox + 12 + i, oz + 2) for i in range(3)],
                rect=(ox - 4, oz - 6, 30, 16))


def _gizmo_cycle(w, cell, prefix, want, max_clicks=4):
    B = w.B
    B.call("rimworld/set_god_mode", enabled=True)
    try:
        B.call("rimworld/clear_selection")
        B.call("rimworld/click_cell", x=cell[0], z=cell[1])
        for _ in range(max_clicks + 1):
            gz = (B.call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
            g = next((q for q in gz if str(q.get("label") or "").startswith(prefix)), None)
            if g is None:
                return "no '%s' button (have %s)" % (prefix, [q.get("label") for q in gz][:8])
            if g.get("label") == want:
                return True
            B.call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id"))
        return "button never read %s" % want
    finally:
        B.call("rimworld/clear_selection")



def _reel_west(c):
    """validation_core.reel_west without the bridge-side import: the reel turns since a98046cbe9 and a bare op builds it
    NORTH; built West one square east keeps the 2x2 on [c, c+(1,1)] with the west outlet these scenes were proven with."""
    return "RM_HoseReel:%d,%d,3" % (c[0] + 1, c[1])

def _reel_toward(c, target):
    """SCENARIO_REELS_FIX_STILL_FACING_WEST: validation_core.reel_toward without the bridge-side import -- the 2x2 on
    [c, c+(1,1)] built facing its hose's target (the larger axis from the footprint centre; ties east/west), at the Position
    that keeps that footprint (N +0, E z+1, S x+1 z+1, W x+1). A reel staged West with its target behind it U-turns."""
    dx, dz = target[0] + 0.5 - (c[0] + 1), target[1] + 0.5 - (c[1] + 1)
    rot = (1 if dx > 0 else 3) if abs(dx) >= abs(dz) else (0 if dz > 0 else 2)
    sx, sz = {0: (0, 0), 1: (0, 1), 2: (1, 1), 3: (1, 0)}[rot]
    return "RM_HoseReel:%d,%d,%d" % (c[0] + sx, c[1] + sz, rot)

def _pump_rig(w, g):
    """Pump + battery + two hose reels: hose A from reelA to g["intake"] set Intake, hose B from reelB to g["outflow"]
    set Outflow. Shared by S3 and S5 part G. Returns staging notes (empty when every step read back right)."""
    notes = []
    r = w.build(";".join(["RM_LiquidPump:%d,%d" % g["pump"], _reel_toward(g["reelA"], g["intake"]), _reel_toward(g["reelB"], g["outflow"]),
                          "Battery:%d,%d" % g["battery"]]))
    if r.get("survived") is not None and r.get("survived") < 4:
        notes.append("build: %s" % str(r.get("failed"))[:200])
    w.ticks(2)
    lt = w.call("jawa/list_things", defName="Battery", rect="%d,%d,2,2" % g["battery"], limit=2) or {}
    bid = ((lt.get("things") or [{}])[0]).get("id")
    if bid is None:
        notes.append("no Battery found at %s: the pump may be unpowered" % (g["battery"],))
    else:
        bs = w.call("jawa/battery_set", thing=bid, mode="setPct", value=1.0)
        if not isinstance(bs, dict) or bs.get("success") is False:
            notes.append("battery_set refused: %s" % str(bs)[:120])
    la = w.hp("lay:%d,%d,%d,%d" % (g["reelA"] + g["intake"]))
    # LIVE 2026-10-17 (fresh map, S3): the lay to the pond's middle edge square refused "no room for the straight
    # lead-out from the nozzle" while the same call one square south laid at once; the earlier walk's S3.b "pulse None"
    # runs had the same unlaid intake. Any other edge square of the same pond is the same scene: try them in turn.
    for alt in g.get("intake_alt") or ():
        if la.get("success"):
            break
        notes.append("intake hose to %s refused (%s); tried %s" % (g["intake"], la.get("reason"), alt))
        la = w.hp("lay:%d,%d,%d,%d" % (g["reelA"] + alt))
    lb = w.hp("lay:%d,%d,%d,%d" % (g["reelB"] + g["outflow"]))
    if not la.get("success"):
        notes.append("intake hose not laid: %s" % la.get("reason"))
    if not lb.get("success"):
        notes.append("outflow hose not laid: %s" % lb.get("reason"))
    ra = _gizmo_cycle(w, g["reelA"], "Free end:", "Free end: Intake")
    rb = _gizmo_cycle(w, g["reelB"], "Free end:", "Free end: Outflow")
    for reel, want in ((g["reelA"], "Intake"), (g["reelB"], "Outflow")):
        rid = next((h.get("id") for h in w.hp("census").get("hoses") or [] if tuple(h.get("reel") or ()) in tuple((reel[0] + i, reel[1] + j) for i in (0, 1) for j in (0, 1))), None)
        got = ((w.call("jawa/comp_read", thing="RM_HoseReel%s" % rid, comp="CompHoseReel", members="freeEndRole") or {})
               .get("values") or {}).get("freeEndRole")
        if str(got) != want:
            notes.append("reel %s free end reads %s, wanted %s" % (reel, got, want))
    if ra is not True:
        notes.append("intake role: %s" % ra)
    if rb is not True:
        notes.append("outflow role: %s" % rb)
    return notes


def stage_S3(w):
    g = s3_geom()
    w.clear_site(g["rect"])
    xs = [c[0] for c in g["pond"]]
    zs = [c[1] for c in g["pond"]]
    w.call("jawa/set_terrain_batch", ops="WaterDeep:%d,%d,%d,%d" % (min(xs), min(zs), 4, 3))
    w.ticks(2)
    b = w.body(g["pond"][0], classify=True)
    for c in g["canal"]:
        w.dig(c, 1)
    notes = _pump_rig(w, g)
    fl = w.hp("flick:%d,%d=off" % g["pump"])
    w.say("S3 staged: enclosed pond of 12 deep squares (body %s limitless=%s stock=%s capacity=%s); pump %s on dry ground "
          "switched OFF (%s); hose A -> pond end Intake; hose B -> canal cell 1 end Outflow; 6-cell depth-1 canal dry" % (
              b.get("id"), b.get("limitless"), b.get("stock"), b.get("capacity"), g["pump"], fl.get("success")))
    for n in notes:
        w.say("  STAGING NOTE: " + n)
    w.say("         screenshot: %s" % w.shot("S3_p00", g["rect"]))


def _hose_held(w, g=None):
    """DECILITRES held inside the two hoses of a pump rig (S3 by default): CompHoseReel.heldUnits off each reel (NaN when a
    reel cannot be read)."""
    g = g or s3_geom()
    tot = 0.0
    for reel in (g["reelA"], g["reelB"]):
        lt = w.call("jawa/list_things", defName="RM_HoseReel", rect="%d,%d,2,2" % reel, limit=2) or {}
        tid = ((lt.get("things") or [{}])[0]).get("id")
        v = ((w.call("jawa/comp_read", thing=tid, comp="CompHoseReel", members="heldUnits") or {}).get("values") or {})
        try:
            tot += float(v.get("heldUnits"))
        except (TypeError, ValueError):
            return float("nan")
    return tot


def _s3_ledger(w, g):
    """Every counter that could hold water between pond and canal, read now: the pump's own moved/lastMoved (units), the
    liquid-net and spill counters (units), the engine's overflow/sink totals and the pond body's raw fields."""
    out = {}
    pp = w.hp("pump:%d,%d" % g["pump"])
    for k in ("moved", "lastMovedUnits", "pourMode"):
        out["pump." + k] = pp.get(k)
    nt = w.hp("net:%d,%d" % g["pump"])
    for k in ("settledUnits", "dumpedUnits", "spilledUnits", "hoseDrainedUnits", "moves", "putBacks"):
        out["net." + k] = nt.get(k)
    es = w.call("jawa/flowworks_engine_state") or {}
    for k, v in es.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool) and any(
                s in k.lower() for s in ("overflow", "sink", "destroy", "evap", "burn", "spill", "lost", "seep")):
            out["engine." + k] = v
    b = w.body(g["pond"][0])
    for k in ("stock", "capacity", "cellCount", "recededCount"):
        out["pond." + k] = b.get(k)
    return out


def run_S3(w):
    g = s3_geom()
    canal, pond = g["canal"], g["pond"]
    b0 = w.body(pond[0])
    s0 = stock_dl(b0)

    def tick(k, m, w_):
        b = w_.body(pond[0])
        held = _hose_held(w_)
        cf = dl_sum(m, canal)
        gapwet = [c for c in g["gap"] if wet(m, c)]
        d = _s3_ledger(w_, g)
        w_.say("  pulse %2d  canal [%s] L  pond %s dL  hoses hold %.0f dL  ground between wet: %s" % (
            k, fills_str(m, canal), stock_dl(b), held, gapwet or "none"))
        w_.say("            ledger: %s" % json.dumps(d, sort_keys=True))
        return dict(stock=stock_dl(b), held=held, canal=cf, gapwet=gapwet, ledger=d)
    w.say("  step A: pump OFF for 20 pulses")
    ha = pulse_loop(w, "S3A", canal + g["gap"], 20, tick, g["rect"], shots_at=(20,))
    wetA = [k for k, _, x in ha if (x["canal"] or 0) > TOL_DL * len(canal)]
    lostA = [k for k, _, x in ha if x["stock"] is not None and s0 is not None and x["stock"] < s0 - TOL_DL]
    expect_line(w, "S3", "S3.a", "canal wet at pulses %s; pond below its start (%s dL) at pulses %s" % (
        wetA or "never", s0, lostA or "never"),
        None if s0 is None or not all_read(ha, canal) or any(x["stock"] is None or x["canal"] is None for _, _, x in ha)
        else (not wetA and not lostA),
        level="canal 0 dL in every square, pond %s dL unchanged within %d dL" % (s0, TOL_DL))
    fl = w.hp("flick:%d,%d=on" % g["pump"])
    pw = w.hp("pump:%d,%d" % g["pump"])
    w.say("  step B: pump ON (%s; powered=%s)" % (fl.get("success"), pw.get("powered")))
    hb = pulse_loop(w, "S3B", canal + g["gap"], 16, tick, g["rect"], shots_at=(6, 16))
    full = first_pulse(hb, lambda m: all(holds(m, c, 1) for c in canal))
    expect_line(w, "S3", "S3.b", "all 6 canal cells at 1 first at pulse %s of step B (6 x 10,000 dL = 6,000 L to the brim)" % full,
                by_pulse(hb, canal, full, 16),
                level="a pump lifts: the canal fills to the brim, every square 10,000 dL within %d dL, and the squares match each other" % TOL_DL,
                readout=w.readout_lines([canal[0], canal[-1]]))
    sB = hb[0][2]["stock"]
    bad, audited = [], 0
    tolc = TOL_DL * (len(canal) + 1)
    for k, _, x in hb:
        if None in (x["stock"], sB, x["canal"]) or x["held"] != x["held"]:
            continue
        audited += 1
        lost = sB - x["stock"]
        gained = x["canal"] + x["held"]
        if abs(lost - gained) > tolc:
            bad.append("p%d lost %d gained %d dL" % (k, lost, gained))
    expect_line(w, "S3", "S3.c", "pulses where canal+hoses gain != pond loss (tolerance %d dL): %s" % (tolc, bad[:4] or "none"),
                None if sB is None or not audited else not bad,
                level="canal dL + hose dL = pond loss in dL at every pulse (no litre leaves the ledger as a spill)")
    # S3 mass audit: every counter that could hold the gap, first pulse of step B against the last (levels = 10,000 units)
    l0, l1 = hb[0][2]["ledger"], hb[-1][2]["ledger"]
    delta = {k: (round((_f(l1.get(k)) or 0) - (_f(l0.get(k)) or 0), 4)) for k in sorted(set(l0) | set(l1))
             if _f(l1.get(k)) is not None or _f(l0.get(k)) is not None}
    lost = None if None in (sB, hb[-1][2]["stock"]) else sB - hb[-1][2]["stock"]
    w.say("  S3 mass audit: pond lost %s dL; canal %s dL; hoses %.0f dL; counter deltas over step B: %s" % (
        lost, hb[-1][2]["canal"], hb[-1][2]["held"], json.dumps(delta, sort_keys=True)))
    w.rows.append(dict(id="S3.audit", status="MEASURED", game=dict(pondLostDl=lost, canalDl=hb[-1][2]["canal"],
                                                                   hosesDl=hb[-1][2]["held"], deltas=delta)))
    gw = sorted({c for _, _, x in ha + hb for c in x["gapwet"]})
    expect_line(w, "S3", "S3.d", "undug ground between pond and canal ever wet: %s" % (gw or "never"),
                None if not all_read(ha + hb, g["gap"]) else not gw)
    expect_line(w, "S3", "S3.e", "not staged in this walk (round trip A->tank->B->A needs tank jobs and two pump legs)", None)
    level_row(w, "S3.lvl", g["rect"], "S3 pond + canal after step B")


def stage_S3q(w):
    """S3.Q1: a mapmaker Source tap and a liquid tap, each beside a dry dug canal, NO hose and NO tank."""
    ox, oz = INTERIOR["S3q"]
    rect = (ox - 2, oz - 2, 18, 10)
    w.clear_site(rect)
    out = {}
    for name, d, z in (("RM_FlowSource", None, oz + 1), ("RM_LiquidTap", None, oz + 5)):
        canal = run(ox + 2, z, 4)
        for c in canal:
            w.dig(c, 1)
        r = w.build("%s:%d,%d" % (name, ox + 1, z))
        if not r.get("survived"):
            r = w.call("jawa/spawn_batch", ops="%s:%d,%d" % (name, ox + 1, z)) or {}
        out[name] = (canal, r)
    w.say("S3.Q1 staged: RM_FlowSource (mapmaker Source tap) and RM_LiquidTap each beside cell 1 of a dry 4-cell canal, "
          "no hose, no tank")
    return out, rect


def run_S3q(w):
    ox, oz = INTERIOR["S3q"]
    canals = {"RM_FlowSource": run(ox + 2, oz + 1, 4), "RM_LiquidTap": run(ox + 2, oz + 5, 4)}
    allc = canals["RM_FlowSource"] + canals["RM_LiquidTap"]
    rect = (ox - 2, oz - 2, 18, 10)

    def tick(k, m, w_):
        w_.say("  pulse %2d  beside Source tap [%s]   beside liquid tap [%s]" % (
            k, fills_str(m, canals["RM_FlowSource"]), fills_str(m, canals["RM_LiquidTap"])))
        return None
    h = pulse_loop(w, "S3q", allc, 10, tick, rect, shots_at=(10,))
    m = h[-1][1]
    obs = []
    for name, cs in canals.items():
        tot = dl_sum(m, cs)
        if tot is None and all(c in m for c in cs):
            tot = sum(m[c][1] for c in cs) * LEVEL_UNITS
        if tot is None:
            obs.append("%s: UNMEASURED (canal squares unread after 10 pulses)" % name)
            continue
        obs.append("%s: canal holds %d dL (%.0f L) after 10 pulses with no hose (%s)" % (
            name, tot, tot / 10.0, "pours straight into the touching dug cell - behaves as (a)/(c)" if tot > 0 else "nothing reached the canal - behaves as (b) or is not running (power/survey)"))
    ruling_line(w, "S3", "S3.Q1", "; ".join(obs))


def _hold_open_toggle(w, cell):
    w.call("rimworld/set_god_mode", enabled=True)
    w.call("rimworld/clear_selection")
    w.call("rimworld/click_cell", x=cell[0], z=cell[1])
    gz = (w.call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
    g = next((q for q in gz if q.get("label") == "Hold open"), None)
    ok = g is not None and (w.call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id")) or {}).get("success")
    w.call("rimworld/clear_selection")
    return ok


def _walk_in(w, cell):
    p = (w.hp("colonists").get("pawns") or [None])[0]
    if p is None:
        return False
    home = tuple(p.get("pos") or (0, 0))
    w.hp("pawn:%d=tp:%d,%d" % (p["id"], cell[0], cell[1] - 2))
    w.call("jawa/order_pawn", pawnId=p["id"], x=cell[0], z=cell[1], waitTicks=300, draft=True)
    w.hp("pawn:%d=tp:%d,%d" % ((p["id"],) + home))
    return True


def gate_open(w, cell):
    """The player's way: press the door's Hold open button, and a drafted colonist walks into the gate cell (that opens
    it; Hold open keeps it open), then is sent home. The walk itself spends game ticks: they are reported."""
    t0 = w.tick_now()
    tg = _hold_open_toggle(w, cell)
    wk = _walk_in(w, cell)
    _, st = w.proof(GATES, "ProofLiquid", "current|%d,%d" % cell)
    return "%s (opening took %s ticks: Hold open on [button %s] + a colonist walked in and left [%s])" % (
        st, (w.tick_now() or 0) - (t0 or 0), "pressed" if tg else "NOT PRESSED", "walked" if wk else "NO COLONIST")


def gate_shut(w, cell):
    """Hold open off, and a colonist passes through: vanilla closes a door by itself only shortly after a friendly
    touched it (Building_Door.CanTryCloseAutomatically), so without a passer-by it would stand open for ever."""
    t0 = w.tick_now()
    _hold_open_toggle(w, cell)
    _walk_in(w, cell)
    for _ in range(40):
        _, st = w.proof(GATES, "ProofLiquid", "current|%d,%d" % cell)
        if "open=False" in st:
            break
        w.ticks(10)
    return "%s (closing took %s ticks: Hold open off + a colonist passed through)" % (st, (w.tick_now() or 0) - (t0 or 0))

# ---------------------------------------------------------------- S4
def s4_geom(band="S4"):
    z = mid(band)
    canal = run(LAKE_W, z, 8)
    return dict(lake=(2, z), up=canal[:3], gate=canal[3], down=canal[4:], canal=canal,
                rect=(0, BANDS[band] - 2, LAKE_W + 14, LAKE_H + 4))


def stage_S4(w):
    for band, door, stuff in (("S4", "RM_Sluice", "WoodLog"), ("S4g", "RM_SecurityGrateDoor", "Steel")):
        g = s4_geom(band)
        w.clear_site(g["rect"])
        b = w.paint_lake(band)
        for c in g["canal"]:
            w.dig(c, 1)
        r = w.build("%s:%d,%d" % ((door,) + g["gate"]), stuff=stuff)
        st = w.proof(GATES, "ProofLiquid", "current|%d,%d" % g["gate"])
        w.say("%s staged: lake %s limitless=%s; canal 3 up + %s on cell 4 + 4 down, all depth 1, dry; built=%s %s" % (
            "S4" if band == "S4" else "S4 variant", b.get("id"), b.get("limitless"), door, r.get("survived"), st[1][:90]))
    both = (0, BANDS["S4"] - 2, LAKE_W + 14, BANDS["S4g"] + LAKE_H + 2 - BANDS["S4"])
    w.say("         screenshot: %s" % w.shot("S4_p00", both))


def run_S4(w):
    g, gg = s4_geom("S4"), s4_geom("S4g")
    both = (0, BANDS["S4"] - 2, LAKE_W + 14, BANDS["S4g"] + LAKE_H + 2 - BANDS["S4"])
    allc = g["canal"] + gg["canal"]
    state = {"step": "A"}

    def tick(k, m, w_):
        _, gs = w_.proof(GATES, "ProofLiquid", "current|%d,%d" % g["gate"])
        w_.say("  %s pulse %2d  sluice canal [%s | %s | %s]  grate canal [%s | %s | %s]  %s" % (
            state["step"], k, fills_str(m, g["up"]), fills_str(m, [g["gate"]]), fills_str(m, g["down"]),
            fills_str(m, gg["up"]), fills_str(m, [gg["gate"]]), fills_str(m, gg["down"]), gs.split("|")[0].strip()))
        return gs
    w.say("  step A: sluice SHUT, 20 pulses (the grate variant runs alongside, never opened)")
    ha = pulse_loop(w, "S4A", allc, 20, tick, both, shots_at=(6, 12, 20))
    up = first_pulse(ha, lambda m: all(holds(m, c, 1) for c in g["up"]))
    expect_line(w, "S4", "S4.a", "3 upstream cells at 1 first at pulse %s" % up, by_pulse(ha, g["up"], up, 6))
    leak = [k for k, m, _ in ha if any(wet(m, c) for c in g["down"])]
    expect_line(w, "S4", "S4.b", "downstream wet while shut at pulses: %s" % (leak or "never"),
                None if not all_read(ha, g["down"]) else not leak)
    gr = first_pulse(ha, lambda m: all(holds(m, c, 1) for c in gg["down"]))
    expect_line(w, "S4", "S4.e", "grate: 4 downstream cells at 1 first at pulse %s" % gr, by_pulse(ha, gg["down"], gr, 12))
    state["step"] = "B"
    w.say("  step B: sluice OPEN, 20 pulses -- %s" % gate_open(w, g["gate"]))
    hb = pulse_loop(w, "S4B", allc, 20, tick, both, shots_at=(8, 20))
    dn = first_pulse(hb, lambda m: all(holds(m, c, 1) for c in g["down"]))
    expect_line(w, "S4", "S4.c", "4 downstream cells at 1 first at pulse %s after opening" % dn, by_pulse(hb, g["down"], dn, 8))
    state["step"] = "C"
    w.say("  step C: sluice SHUT again, 40 pulses -- %s" % gate_shut(w, g["gate"]))
    hc = pulse_loop(w, "S4C", allc, 40, tick, both, shots_at=(20, 40))
    updry = [k for k, m, _ in hc if any(not holds(m, c, 1) for c in g["up"])]
    expect_line(w, "S4", "S4.d", "an upstream cell below 1 at pulses: %s" % (updry or "never"),
                None if not all_read(hc, g["up"]) else not updry)
    d0 = dl_sum(hc[0][1], g["down"])
    d1 = dl_sum(hc[-1][1], g["down"])
    if (d0 is None or d1 is None) and all(c in hc[i][1] for i in (0, -1) for c in g["down"]):
        d0 = sum(hc[0][1][c][1] for c in g["down"]) * LEVEL_UNITS
        d1 = sum(hc[-1][1][c][1] for c in g["down"]) * LEVEL_UNITS
    if d0 is None or d1 is None:
        ruling_line(w, "S4", "S4.Q1", "UNMEASURED: downstream squares unread at the start or end of step C")
    else:
        ruling_line(w, "S4", "S4.Q1", "downstream held %d dL when shut again and %d dL after 40 pulses (%s)" % (
            d0, d1, "stays put = (a)" if abs(d1 - d0) <= TOL_DL * len(g["down"]) else "it went down; whether back to the lake (b) or gone (c) needs the totals"))


# ---------------------------------------------------------------- S5
# Redrawn 2026-10-17 (scenes file re-sealed) per design/RimMandrake/flowworks_unified_depth_2026-10-17.md: water moves
# by the leveling law, so by gravity a 0.5 m canal takes only a pond's top 0.5 m (A, B); a 2 m canal levels with the
# pond (F); a pump moves the whole 4,000 L (G). Amounts below are DECILITRES (1 notch = 0.5 m in one square = 10,000 dL =
# 1,000 L), read per square through ProofReadout and per pond through its stock (notches * 10,000). Under exact-level water
# (P3) a body stands at ONE surface, so the sealed doc's whole-notch pictures (S5.a "at most 9 wet", S5.c "only cell 1",
# S5.i "never a 5th") are replaced by level_solution numbers, printed as "level:" beside the doc's wording.
def s5_geom():
    ox, oz = INTERIOR["S5"]
    pondA = [(ox + 1 + i, oz + 1 + j) for i in range(3) for j in range(3)]
    canalA = run(ox + 4, oz + 2, 10)
    pondB = [(ox + 1, oz + 10)]
    canalB = run(ox + 2, oz + 10, 10)
    runD = run(ox + 4, oz + 16, 3)
    return dict(pondA=pondA, canalA=canalA, pondB=pondB, canalB=canalB, runD=runD, rect=(ox - 3, oz - 3, 22, 24))


def s5e_geom():
    ox, oz = INTERIOR["S5e"]
    basin = [(ox + 1 + i, oz + 1 + j) for i in range(6) for j in range(6)]
    centre = [(ox + 3, oz + 3), (ox + 4, oz + 3), (ox + 3, oz + 4), (ox + 4, oz + 4)]
    return dict(basin=basin, centre=centre, rect=(ox - 2, oz - 2, 12, 12))


def s5f_geom():
    ox, oz = INTERIOR["S5f"]
    return dict(pond=(ox + 1, oz + 1), canal=(ox + 2, oz + 1), rect=(ox - 2, oz - 2, 8, 6))


def s5g_geom():
    """Part G: S3's pump rig, shrunk to a 1-square pond (same spacing: pump 5 east of the pond, canal 5 east of the pump)."""
    ox, oz = INTERIOR["S5g"]
    pond = (ox + 1, oz + 2)
    canal = run(ox + 11, oz + 2, 6)
    return dict(pond=pond, canal=canal, pump=(ox + 6, oz + 2), reelA=(ox + 6, oz + 3), reelB=(ox + 6, oz),
                intake=pond, outflow=canal[0], battery=(ox + 9, oz + 6),
                gap=[(ox + 2 + i, oz + 2) for i in range(3)] + [(ox + 8 + i, oz + 2) for i in range(3)],
                rect=(ox - 4, oz - 6, 24, 16))


def _overflow(w):
    return (w.call("jawa/flowworks_engine_state") or {}).get("overflowDestroyedTotal")


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def stage_S5(w):
    g, e, f, q = s5_geom(), s5e_geom(), s5f_geom(), s5g_geom()
    for rect in (g["rect"], e["rect"], f["rect"], q["rect"]):
        w.clear_site(rect)
    xs = [c[0] for c in g["pondA"]]
    zs = [c[1] for c in g["pondA"]]
    w.call("jawa/set_terrain_batch", ops="WaterDeep:%d,%d,3,3;WaterDeep:%d,%d,1,1;WaterDeep:%d,%d,1,1;WaterDeep:%d,%d,1,1" % (
        min(xs), min(zs), g["pondB"][0][0], g["pondB"][0][1], f["pond"][0], f["pond"][1], q["pond"][0], q["pond"][1]))
    w.ticks(2)
    bA = w.body(g["pondA"][4], classify=True)
    bB = w.body(g["pondB"][0], classify=True)
    bF = w.body(f["pond"], classify=True)
    bG = w.body(q["pond"], classify=True)
    for c in g["canalA"] + g["canalB"] + q["canal"]:
        w.dig(c, 1)
    w.dig(f["canal"], 4)
    for c in g["runD"]:
        w.dig(c, 1, fill=1)
    notes = _pump_rig(w, q)
    fl = w.hp("flick:%d,%d=off" % q["pump"])
    w.say("S5 staged: A = 3x3 pond (%s dL, limitless=%s) + 10-cell 0.5 m canal; B = 1-square pond (%s dL, limitless=%s) "
          "+ 10-cell 0.5 m canal; F = 1-square pond (%s dL) + one 2 m canal square; G = 1-square pond (%s dL) + pump "
          "(OFF until part G: %s) + 6-cell 0.5 m canal; D = isolated 3-cell run full (E, the basin, is dug when its turn comes)" % (
              stock_dl(bA), bA.get("limitless"), stock_dl(bB), bB.get("limitless"), stock_dl(bF), stock_dl(bG),
              fl.get("success")))
    for n in notes:
        w.say("  STAGING NOTE (part G): " + n)
    w.say("         screenshot: %s" % w.shot("S5_p00", g["rect"]))


def _expect(groups, total_dl):
    """level_solution -> (surface_m, [dl per square per group]), or (None, None) when the water cannot fit (never a guess)."""
    try:
        return level_solution(groups, total_dl)
    except ValueError:
        return None, [None] * len(groups)


def _r(v):
    return None if v is None else round(v)


def run_S5(w):
    g, e, f, q = s5_geom(), s5e_geom(), s5f_geom(), s5g_geom()
    TOT_A, TOT_B = 36 * LEVEL_UNITS, 4 * LEVEL_UNITS
    sA, (exA_pond, exA_can) = _expect([(9, -2.0), (10, -0.5)], TOT_A)
    sB, (exB_pond, exB_can) = _expect([(1, -2.0), (10, -0.5)], TOT_B)
    sA0 = stock_dl(w.body(g["pondA"][4]))
    sB0 = stock_dl(w.body(g["pondB"][0]))
    allc = g["canalA"] + g["canalB"] + g["runD"] + [f["canal"]]

    def tick(k, m, w_):
        a, b, fp = w_.body(g["pondA"][4]), w_.body(g["pondB"][0]), w_.body(f["pond"])
        w_.say("  pulse %2d  A canal [%s] pond %s dL   B canal [%s] pond %s dL   F canal [%s] pond %s dL   (canals in litres)" % (
            k, fills_str(m, g["canalA"]), stock_dl(a), fills_str(m, g["canalB"]), stock_dl(b),
            fills_str(m, [f["canal"]]), stock_dl(fp)))
        if k % 5 == 0 or k <= 3:
            w_.say("            pond A squares (depth/fill:terrain; body cells=%s receded=%s): %s" % (
                a.get("cellCount"), a.get("recededCount"), w_.grid(g["pondA"])))
        return dict(a=stock_dl(a), b=stock_dl(b), f=stock_dl(fp), aw=a.get("cellCount"), ar=a.get("recededCount"))
    w.say("  step AB: parts A, B and F together, 54 pulses (B and F by 10, A by 20, then B's front must hold 40 more)")
    h = pulse_loop(w, "S5AB", allc, 54, tick, g["rect"], shots_at=(10, 20, 54))
    # A: pond + canal hold 36,000 L every pulse; no canal square above its brim (10,000 dL); one run from the pond.
    totA = [(k, x["a"] + dl_sum(m, g["canalA"])) for k, m, x in h if x["a"] is not None and dl_sum(m, g["canalA"]) is not None]
    tolA = TOL_DL * (len(g["canalA"]) + 1)
    badA = [k for k, t_ in totA if abs(t_ - TOT_A) > tolA]
    over = [k for k, m, _ in h if any((dl_of(m, c) or 0) > LEVEL_UNITS + TOL_DL for c in g["canalA"])]
    brokenA = [k for k, m, _ in h if not one_run(m, g["canalA"])]
    wetA = [sum(1 for c in g["canalA"] if wet(m, c)) for _, m, _ in h]
    expect_line(w, "S5", "S5.a", "A: canal squares wet at once, most %d of 10; pulses where pond+canal != %d dL (+-%d): %s; a canal "
                "square above 10,000 dL at: %s; not one run at: %s" % (
                    max(wetA), TOT_A, tolA, badA[:8] or "none", over[:8] or "none", brokenA[:8] or "none"),
                None if not totA else (not badA and not over and not brokenA),
                level="the doc's 'at most 9 wet' is a whole-notch picture; level water wets all 10 at one depth (%s dL = 0.237 m each)" %
                _r(exA_can))
    stA = [x["a"] for _, _, x in h if x["a"] is not None]
    pondA20 = h[20][2]["a"] if len(h) > 20 else None
    expect_line(w, "S5", "S5.b", "pond A %s -> %s dL, lowest %s; at pulse 20 %s dL (doc: lower than at start, never below 270,000)" % (
        sA0, stA[-1] if stA else None, min(stA) if stA else None, pondA20),
        None if not stA or sA0 is None or exA_pond is None else (
            stA[-1] < sA0 and min(stA) >= 27 * LEVEL_UNITS - TOL_DL and near(pondA20, exA_pond * 9, 10)
            and all(near(dl_of(h[20][1], c), exA_can, 1) for c in g["canalA"])),
        level="pond %s dL (9 x %s), each canal square %s dL; surface -0.263 m" % (
            _r(None if exA_pond is None else exA_pond * 9), _r(exA_pond), _r(exA_can)),
        readout=w.readout_lines([g["canalA"][0], g["canalA"][-1], g["pondA"][0]]))
    level_row(w, "S5.lvl.A", g["rect"], "S5 A+B bodies at pulse 54")
    # B: total 4,000 L; pond keeps >= 3,000 L; level water spreads the sheet over all 10 squares (4.5 cm)
    stB = [x["b"] for _, _, x in h if x["b"] is not None]
    k10 = min(10, len(h) - 1)
    k14 = min(14, len(h) - 1)
    cB10 = dl_sum(h[k10][1], g["canalB"])
    totB10 = None if cB10 is None or h[k10][2]["b"] is None else h[k10][2]["b"] + cB10
    wetB_ever = sorted({i + 1 for _, m, _ in h for i, c in enumerate(g["canalB"]) if wet(m, c)})
    expect_line(w, "S5", "S5.c", "B canal cells ever wet %s; pond B lowest %s dL (start %s); total at pulse 10 = %s dL; at pulse 14 canal "
                "squares %s dL, pond %s dL" % (wetB_ever or "none", min(stB) if stB else None, sB0, totB10,
                                               dl_str(h[k14][1], g["canalB"]), h[k14][2]["b"]),
                None if not stB or totB10 is None or exB_can is None else (
                    min(stB) >= 3 * LEVEL_UNITS - TOL_DL and near(totB10, TOT_B, 11)
                    and all(near(dl_of(h[k14][1], c), exB_can, 1) for c in g["canalB"]) and near(h[k14][2]["b"], exB_pond, 1)),
                level="the doc's 'only cell 1 wet' is a whole-notch picture; level water lays %s dL (4.5 cm) on all 10 squares, pond %s dL" % (
                    _r(exB_can), _r(exB_pond)),
                readout=w.readout_lines([g["canalB"][0], g["canalB"][-1], g["pondB"][0]]))
    ref = h[14][1] if len(h) > 14 else None
    moved = [k for k, m, _ in h[14:] if ref is not None and any(
        not near(dl_of(m, c), dl_of(ref, c)) for c in g["canalB"])]
    # near(None, x) is False: an unread square would read as "moved"; no pulse 14, or any unread square, is UNMEASURED
    d_read = ref is not None and all(dl_of(m, c) is not None for _, m, _ in h[14:] for c in g["canalB"])
    expect_line(w, "S5", "S5.d", "B canal changed (more than %d dL a square) after pulse 14 at pulses: %s" % (TOL_DL, moved[:12] or "never"),
                not moved if d_read else None)
    # F: pond square + 2 m canal square settle to one surface: 2,000 L each
    exF = _expect([(1, -2.0), (1, -2.0)], 4 * LEVEL_UNITS)[1]
    fh = [(k, x["f"], dl_of(m, f["canal"])) for k, m, x in h[:21]]
    f10 = fh[min(10, len(fh) - 1)]
    fmoved = [k for k, s_, c_ in fh[10:] if not (near(s_, f10[1]) and near(c_, f10[2]))]
    expect_line(w, "S5", "S5.h", "pulse 10: pond F %s dL, 2 m canal %s dL (doc: 1 m each = 20,000 dL, total 40,000); changed after pulse 10 at: %s" % (
        f10[1], f10[2], fmoved or "never"),
        None if f10[1] is None or f10[2] is None or exF is None or any(None in (s_, c_) for _, s_, c_ in fh[10:]) else (
            near(f10[1], exF[0], 2) and near(f10[2], exF[1], 1) and not fmoved),
        level="each of the two squares holds 20,000 dL (1.00 m), surface -1.000 m",
        readout=w.readout_lines([f["canal"], f["pond"]]))
    level_row(w, "S5.lvl.F", f["rect"], "S5 F pond + 2 m canal square")
    # C: fill in canal B cell 1; destroys nothing: pond+canal still 4,000 L (the displaced sheet goes to the other squares)
    cB_end = dl_sum(h[-1][1], g["canalB"])
    pB0 = stock_dl(w.body(g["pondB"][0]))
    totB0 = None if cB_end is None or pB0 is None else cB_end + pB0
    ov0 = _overflow(w)
    fi_ok = w.fill_in(g["canalB"][0]).get("success") is not False
    w.say("  step C: canal B cell 1 filled in")
    hc = pulse_loop(w, "S5C", g["canalB"], 4, tick, g["rect"], shots_at=(1,))
    cB1 = dl_sum(hc[-1][1], g["canalB"][1:])
    pB1 = stock_dl(w.body(g["pondB"][0]))
    totB1 = None if cB1 is None or pB1 is None else cB1 + pB1
    ov1 = _overflow(w)
    destroyed = None if None in (ov0, ov1) else (float(ov1) - float(ov0)) * LEVEL_UNITS
    sC, (exC_pond, exC_can) = _expect([(1, -2.0), (9, -0.5)], TOT_B)
    expect_line(w, "S5", "S5.e", "B canal(2-10)+pond total %s -> %s dL; overflow destroyed %s dL (the 4 pulses after the fill-in; level "
                "prediction: canal squares %s dL, pond %s dL)" % (
                    totB0, totB1, None if destroyed is None else round(destroyed, 1),
                    _r(exC_can), _r(exC_pond)),
                None if totB0 is None or totB1 is None or destroyed is None or not fi_ok else (
                    near(totB0, totB1, 11) and destroyed <= TOL_DL),
                level="the 91 L sheet on cell 1 is displaced, not destroyed: total 40,000 dL, 0 dL overflowed",
                readout=w.readout_lines([g["canalB"][1], g["pondB"][0]]))
    # D: fill in the middle of the isolated run: exactly 10,000 dL (1,000 L) destroyed, ends keep 10,000 dL each
    m0, _ = w.cells(g["runD"])
    d0 = dl_sum(m0, g["runD"])
    ov0 = _overflow(w)
    fiD_ok = w.fill_in(g["runD"][1]).get("success") is not False
    w.say("  step D: middle cell of the isolated 3-cell run filled in (look top-left for the message)")
    w.say("         screenshot: %s" % w.shot("S5_D_message", g["rect"]))
    m1, _ = w.cells(g["runD"])
    d1 = dl_sum(m1, g["runD"])
    ov1 = _overflow(w)
    lostd = None if None in (ov0, ov1) else (float(ov1) - float(ov0)) * LEVEL_UNITS
    expect_line(w, "S5", "S5.f", "run held %s -> %s dL; the game's destroyed-overflow total rose by %s dL (the message text is in the "
                "screenshot)" % (d0, d1, None if lostd is None else round(lostd, 1)),
                None if lostd is None or d0 is None or d1 is None or not fiD_ok else (
                    near(lostd, LEVEL_UNITS, 1) and near(d0 - d1, LEVEL_UNITS, 3)),
                level="exactly 10,000 dL (1,000 L) destroyed and named in the message; the two end squares keep 10,000 dL each",
                readout=w.readout_lines([g["runD"][0], g["runD"][2]]))
    # E: the basin
    for c in e["basin"]:
        w.dig(c, 2)
    for c in e["centre"]:
        w.set_fill(c, 2)
    w.say("  step E: 6x6 basin 1 m deep dug now, 8 notches (80,000 dL = 8,000 L) heaped in the 4 centre cells, 20 pulses")
    exE = _expect([(36, -1.0)], 8 * LEVEL_UNITS)[1]

    def tickE(k, m, w_):
        row = lambda j: " ".join("%s" % (fills_str(m, [(e["basin"][0][0] + i, e["basin"][0][1] + j)])) for i in range(6))
        w_.say("  pulse %2d  basin rows (litres) %s  total %s dL" % (k, " | ".join(row(j) for j in range(6)), dl_sum(m, e["basin"])))
        return None
    he = pulse_loop(w, "S5E", e["basin"], 20, tickE, e["rect"], shots_at=(20,))
    mE = he[-1][1]
    deep = [c for c in e["basin"] if (dl_of(mE, c) or 0) >= 2 * LEVEL_UNITS - TOL_DL]
    dry = [c for c in e["basin"] if not wet(mE, c)]
    tot = dl_sum(mE, e["basin"])
    off = [c for c in e["basin"] if exE is None or not near(dl_of(mE, c), exE[0], 1)]
    expect_line(w, "S5", "S5.g", "pulse 20: %d cell(s) at 1 m while %d dry; total %s dL; %d square(s) off the level share by more than %d dL" % (
        len(deep), len(dry), tot, len(off), TOL_DL),
        None if tot is None or exE is None else (not (deep and dry) and near(tot, 8 * LEVEL_UNITS, 36) and not off),
        level="all 36 squares wet at one depth: %s dL (0.111 m, 222 L) each, total 80,000 dL, none dry" % _r(exE[0]),
        readout=w.readout_lines([e["basin"][0], e["centre"][0], e["basin"][-1]]))
    level_row(w, "S5.lvl.E", e["rect"], "S5 E basin after 20 pulses")
    # G: the pump moves the pond's 4,000 L (minus what the hoses hold) into the canal, level over its six squares
    sG0 = stock_dl(w.body(q["pond"]))
    fl = w.hp("flick:%d,%d=on" % q["pump"])
    pw = w.hp("pump:%d,%d" % q["pump"])
    w.say("  step G: pump ON (%s; powered=%s), pond G %s dL, 30 pulses" % (fl.get("success"), pw.get("powered"), sG0))

    def tickG(k, m, w_):
        st = stock_dl(w_.body(q["pond"]))
        held = _hose_held(w_, q)
        cf = dl_sum(m, q["canal"])
        gapwet = [c for c in q["gap"] if wet(m, c)]
        w_.say("  pulse %2d  canal [%s] L  pond %s dL  hoses hold %.0f dL  ground between wet: %s" % (
            k, fills_str(m, q["canal"]), st, held, gapwet or "none"))
        return dict(stock=st, held=held, canal=cf, gapwet=gapwet)
    hg = pulse_loop(w, "S5G", q["canal"] + q["gap"], 30, tickG, q["rect"], shots_at=(10, 30))
    tolG = TOL_DL * (len(q["canal"]) + 1)
    readG = [(k, x) for k, _, x in hg if None not in (x["stock"], x["canal"]) and x["held"] == x["held"]]
    badG = [k for k, x in readG if abs(x["stock"] + x["held"] + x["canal"] - (sG0 or 0)) > tolG]
    mG, xG = hg[-1][1], hg[-1][2]
    cG = [dl_of(mG, c) for c in q["canal"]]
    levelG = None not in cG and (max(cG) - min(cG)) <= TOL_DL
    gw = sorted({c for _, _, x in hg for c in x["gapwet"]})
    exG = None if sG0 is None or xG["held"] != xG["held"] else _expect([(6, -0.5)], max(0, sG0 - (xG["stock"] or 0) - xG["held"]))[1]
    expect_line(w, "S5", "S5.i", "end: canal squares %s dL (level: %s), pond %s dL, hoses %.0f dL; pulses where pond+hoses+canal != %s "
                "(+-%d): %s; undug ground wet: %s" % (cG, levelG, xG["stock"], xG["held"], sG0, tolG, badG[:6] or "none", gw or "never"),
                None if sG0 is None or None in cG or not readG else (not badG and levelG and (xG["stock"] or 0) <= TOL_DL * 2 and not gw),
                level="the doc's 'cells 1-4 at 0.5 m, never a 5th' is a whole-notch picture; level water spreads the pumped water over "
                "all 6 squares (4,000 L = %s dL each, 0.333 m), pond dry bar the hoses" % _r(exG[0] if exG else None),
                readout=w.readout_lines([q["canal"][0], q["canal"][-1], q["pond"]]))
    level_row(w, "S5.lvl.G", q["rect"], "S5 G canal after the pump")


# ---------------------------------------------------------------- S6
def s6_geom(run2=False):
    """Run 1 and run 2 each get a FRESH plot: re-staging on run 1's plot kept the pond body's receded stock
    (first trial: run 2 started at pond 22 instead of 32)."""
    ox, oz = INTERIOR["S6b" if run2 else "S6"]
    pond = [(ox + 1 + i, oz + 1 + j) for i in range(3) for j in range(3)]
    canal = run(ox + 4, oz + 2, 10)
    gg = s4_geom("S6g2" if run2 else "S6g")
    return dict(pond=pond, canal=canal, gate=gg, rect=(ox - 3, oz - 3, 20, 10), grect=gg["rect"])


def _s6_stage(w, run2=False):
    g = s6_geom(run2)
    w.clear_site(g["rect"])
    w.clear_site(g["grect"])
    xs = [c[0] for c in g["pond"]]
    zs = [c[1] for c in g["pond"]]
    w.call("jawa/set_terrain_batch", ops="WaterDeep:%d,%d,3,3" % (min(xs), min(zs)))
    w.paint_lake("S6g2" if run2 else "S6g")
    w.ticks(2)
    w.body(g["pond"][4], classify=True)
    for c in g["canal"]:
        w.dig(c, 1)
    gg = g["gate"]
    for c in gg["canal"]:
        w.dig(c, 1)
    w.build("RM_Sluice:%d,%d" % gg["gate"], stuff="WoodLog")      # a door is built shut
    for c in gg["up"]:
        w.set_fill(c, 1)
    for c in gg["down"][:2]:
        w.set_fill(c, 1)          # "the downstream half full"
    return g


def _s6_snap(w, g, with_grid=False):
    """Every compared field in DECILITRES: per canal square (depth, fill, dL), the pond's dL and the gate state."""
    cells = g["canal"] + g["gate"]["canal"]
    m, _ = w.cells(cells)
    _, gs = w.proof(GATES, "ProofLiquid", "current|%d,%d" % g["gate"]["gate"])
    s = dict(m=[list(m.get(c, (None, None, None))) for c in cells] if m else None,
             pond=stock_dl(w.body(g["pond"][4])), gate=gs.split("|")[0].strip())
    if with_grid:
        s["grid"] = w.grid(g["pond"])     # kept apart from the compared fields: a view, not part of the S6.a equality
    return s


def _s6_eq(a, b):
    return {k: v for k, v in a.items() if k != "grid"} == {k: v for k, v in b.items() if k != "grid"}


def _s6_dl(s):
    """Decilitres in a snapshot: canal + gate squares (None when any was unread) + the pond."""
    if not s["m"] or s["pond"] is None or any(v[2] is None for v in s["m"]):
        return None
    return sum(v[2] for v in s["m"]) + s["pond"]


def _s6_maxdiff(a, b):
    """Widest per-square / pond difference in dL between two snapshots (None when unreadable)."""
    if not a["m"] or not b["m"] or a["pond"] is None or b["pond"] is None:
        return None
    ds = [abs(x[2] - y[2]) for x, y in zip(a["m"], b["m"]) if x[2] is not None and y[2] is not None]
    return max(ds + [abs(a["pond"] - b["pond"])])


def stage_S6(w):
    _s6_stage(w)
    g = s6_geom()
    w.say("S6 staged (run 1, never saved): S5 part A (3x3 pond + 10-cell canal) and S4's gate scene shut with the downstream half full")
    w.say("         screenshot: %s" % w.shot("S6_p00", g["rect"]))


def _s6_line(k, s):
    return "  pulse %2d  canal [%s] dL  pond %s dL  gate %s%s" % (
        k, " ".join(str(v[2] if v[2] is not None else "?") for v in s["m"][:10]) if s["m"] else "?", s["pond"], s["gate"],
        ("\n            pond squares: %s" % s["grid"]) if s.get("grid") else "")


def run_S6(w):
    g = s6_geom()
    iv = w.interval()
    w.say("  run 1: uninterrupted to pulse 30")
    r1 = []
    for k in range(31):
        if k:
            w.ticks(iv)
        s = _s6_snap(w, g, with_grid=k in (0, 1, 2, 4, 10, 20, 30))
        r1.append(s)
        w.say(_s6_line(k, s))
        time.sleep(w.args.pace / 3)
    w.say("         screenshot: %s" % w.shot("S6_run1_p30", g["rect"]))
    ro1 = w.readout_lines([g["canal"][0], g["canal"][-1], g["pond"][4]])
    level_row(w, "S6.lvl.run1", g["rect"], "S6 run 1 pond + canal at pulse 30")
    w.say("  run 2: the same start again on a fresh twin plot just north; save at pulse 4, reload, continue to 30")
    g = s6_geom(True)
    _s6_stage(w, True)
    for k in range(5):
        if k:
            w.ticks(iv)
    pre = _s6_snap(w, g, with_grid=True)
    w.say(_s6_line(4, pre) + "   <- saving")
    name = "RM_fw_scene_S6_%s" % time.strftime("%Y%m%d%H%M%S")
    sv = w.call("rimworld/save_game", saveName=name) or {}
    ld = w.call("rimworld/load_game_ready", saveName=name, timeoutMs=240000) or {}
    ok, waited = w.V._wait_playing(w.B, leave_s=0)
    reloaded = bool(ok) and sv.get("success") is True and ld.get("success") is True    # else `post` is the unreloaded game
    post = _s6_snap(w, g, with_grid=True)
    w.say(_s6_line(4, post) + "   <- after reload (save %s, load %s, playing %s)" % (sv.get("success"), ld.get("success"), ok))
    same = _s6_eq(pre, post)
    md = _s6_maxdiff(pre, post)
    expect_line(w, "S6", "S6.a", "after reload: cells (dL), pond stock (dL) and gate %s the save; widest square/pond difference %s dL" % (
        "EQUAL" if same else "DIFFER FROM", md), same if pre["m"] and post["m"] and reloaded else None,
        "" if same else "pre %s / post %s" % (json.dumps(pre)[:200], json.dumps(post)[:200]),
        level="every square's decilitres, the pond's decilitres and the gate state are equal across the save (a long, not a rounded, stock)")
    expect_line(w, "S6", "S6.b", "total liquid before save %s dL, after reload %s dL" % (_s6_dl(pre), _s6_dl(post)),
                None if None in (_s6_dl(pre), _s6_dl(post)) or not reloaded else abs(_s6_dl(pre) - _s6_dl(post)) <= TOL_DL,
                level="conserved to the decilitre across the reload")
    r2 = [pre]
    for k in range(5, 31):
        w.ticks(iv)
        s = _s6_snap(w, g, with_grid=k in (10, 20, 30))
        r2.append(s)
        w.say(_s6_line(k, s))
        time.sleep(w.args.pace / 3)
    w.say("         screenshot: %s" % w.shot("S6_run2_p30", g["rect"]))
    ro2 = w.readout_lines([g["canal"][0], g["canal"][-1], g["pond"][4]])
    expect_line(w, "S6", "S6.c", "pulse 30: cells (dL) %s; pond run 1 %s dL, run 2 %s dL; widest difference %s dL" % (
        "equal" if r2[-1]["m"] == r1[-1]["m"] else "differ", r1[-1]["pond"], r2[-1]["pond"], _s6_maxdiff(r1[-1], r2[-1])),
                None if not r1[-1]["m"] or not r2[-1]["m"] or None in (r1[-1]["pond"], r2[-1]["pond"]) or not reloaded
                else (r2[-1]["m"] == r1[-1]["m"] and r2[-1]["pond"] == r1[-1]["pond"]),
                level="run 2 ends cell for cell and decilitre for decilitre as run 1 (run 1: %s; run 2: %s)" % (" || ".join(ro1[:1]), " || ".join(ro2[:1])),
                readout=ro1 + ro2)
    level_row(w, "S6.lvl.run2", g["rect"], "S6 run 2 pond + canal at pulse 30")
    diffs = [k for k in range(5, 31) if r1[k]["m"] != r2[k - 4]["m"]]
    ruling_line(w, "S6", "S6.Q1", "pulse-by-pulse after the reload, run 2 differed from run 1 at pulses: %s" % (diffs or "none"))


# ---------------------------------------------------------------- prep / settings
def prep(w):
    st = w.call("rimworld/get_ui_state").get("programState")
    made = st != "Playing" or bool(w.args.fresh_map)
    if made:
        if st == "Playing":
            w.call("rimworld/go_to_main_menu")     # start_debug_game_ready on a Playing game keeps the old map
            time.sleep(5)
        w.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
        ok, waited = w.V._wait_playing(w.B, leave_s=0)
        w.say("quicktest map up: %s (%s s)" % (ok, waited))
    w.call("rimworld/pause_game", pause=True)
    w.call("jawa/weather_set", weather="Clear", lockWeather=True)
    w.call("jawa/incident_queue_clear")
    # PROOF_SWEEPS_FIX_OTHER_ZOOS_STILL_OPEN: on a map we did not make keep its own non-colonists (staged animals, prisoners)
    w.say("  opening sweep: %s" % (w.V.sweep_at_start(w.B, made_map=made),))
    w.call("rimworld/set_god_mode", enabled=True)
    for c in w.hp("colonists").get("pawns") or []:
        w.hp("pawn:%d=draft" % c["id"])
    w.say("colonists fed (Food, Rest topped up; upkeep against the starving GovernorStop): %s" % w.feed())
    mi = w.call("jawa/map_info") or {}
    got = {}
    for f, v in SCENE_OVERRIDES.items():
        w.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))
        got[f] = w.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")
    off = {f: got[f] for f, v in SCENE_OVERRIDES.items() if str(got[f]).lower() != str(v).lower()}
    if off:
        w.say("  SETTING NOT TAKEN (read back differs): %s -- the scenes would run on the wrong settings" % off)
    w.say("map %sx%s; settings at shipped defaults except the scene file's: %s (read back)" % (
        mi.get("sizeX") or mi.get("width"), mi.get("sizeZ") or mi.get("height"), got))
    w.say("pulse interval %d ticks (shipped default 250)" % w.interval())
    e = w.call("jawa/flowworks_engine_state") or {}
    nd = e.get("excavatedCellCount")
    sd = e.get("superdeepCellCount")
    # "pristine" = NOTHING DUG (P11 forms every natural body at map load, so bodyCount > 0 on a fresh map is normal)
    pristine = None if nd is None or sd is None else (nd == 0 and sd == 0)
    w.say("site pristine (nothing dug: excavated %s, superdeep %s): %s; bodies %s (printed, not required to be 0)%s" % (
        nd, sd, pristine, e.get("bodyCount"),
        "" if pristine is not False or not w.args.fresh_map else "  <-- a --fresh-map site that is not pristine"))


def restore(w):
    got = {}
    for f, v in SHIPPED.items():
        w.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))
        got[f] = w.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")
    w.say("shipped settings restored: %s" % got)
    off = {f: got[f] for f, v in SHIPPED.items() if str(got[f]).lower() != str(v).lower()}
    if off:
        w.say("  RESTORE NOT TAKEN (read back differs): %s -- set them by hand" % off)


STAGE = {"S1": stage_S1, "S2": stage_S2, "S3": stage_S3, "S4": stage_S4, "S5": stage_S5, "S6": stage_S6}
RUN = {"S1": run_S1, "S2": run_S2, "S3": run_S3, "S4": run_S4, "S5": run_S5, "S6": run_S6}
ORDER = ["S1", "S2", "S3", "S4", "S5", "S6"]


def pin_scene_settings(w):
    """Set SCENE_PIN; return {field: value before} for unpin_scene_settings (the previous value, not the shipped one)."""
    before = {}
    for f, v in SCENE_PIN.items():
        before[f] = w.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")
        w.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))
        got = w.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")
        w.say("  site pin: %s %s -> %s (read back %s); P11_FLOOR_ON_PAINTED_PONDS stays the owner's" % (f, before[f], v, got))
    return before


def unpin_scene_settings(w, before):
    """Put the pinned settings back to what they were; a failure is printed, never raised over the scene's own outcome."""
    for f, v in before.items():
        try:
            if v is None:
                v = SHIPPED[f]
            w.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))
            got = w.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")
            w.say("  site pin released: %s back to %s (read back %s)" % (f, v, got))
        except Exception as ex:  # noqa: BLE001
            w.say("  SITE PIN NOT RELEASED: %s (%s); run `restore`" % (f, ex))


def do_scene(w, sid, stage=True, go=True):
    before = pin_scene_settings(w)
    try:
        return _do_scene(w, sid, stage, go)
    finally:
        unpin_scene_settings(w, before)


def _do_scene(w, sid, stage=True, go=True):
    """One scene. Never loses an error (WATER_SCENES_WALK_MEND_TRIPS_AFTER_S4): an exception anywhere in staging or the
    run is printed IN FULL, written to Transient/fw_scenes/live/<sid>_traceback_<stamp>.txt, recorded as a CRASHED row,
    and the log and rows are still written; the caller goes on to the next scene. Returns True when it ran clean."""
    import traceback
    s = scene_doc(sid)
    w.say("=" * 100)
    w.say("%s. %s" % (sid, s["title"]))
    for line in s["grid"]:
        w.say("    " + line)
    w.say("    readings: canal / pond squares are LITRES (to the litre, from ProofReadout) and ponds / hoses decilitres; 1 notch = 0.5 m "
          "in one square = 1,000 L = 10,000 dL; tolerance %d dL per square read" % TOL_DL)
    ok = True
    if hasattr(w.B, "scene"):            # the offline mock (--mock-fail) needs to know which scene it is in
        w.B.scene, w.B.ticks_in_scene = sid, 0
    try:
        if stage:
            STAGE[sid](w)
            if sid == "S3":
                stage_S3q(w)
        if go:
            w.say("  doc horizons are deadlines ('by pulse N'), never speeds; one pulse = %d ticks, stepped with a %.1f s pause" % (
                w.interval(), w.args.pace))
            RUN[sid](w)
            if sid == "S3":
                run_S3q(w)
    except Exception:  # noqa: BLE001 - the whole point: print it, keep it, carry on
        ok = False
        tb = traceback.format_exc()
        p = os.path.join(OUT, "%s_traceback_%s.txt" % (sid, time.strftime("%Y%m%dT%H%M%S")))
        with open(p, "w", encoding="utf-8") as f:
            f.write(tb)
        w.say("  CRASHED (traceback kept at %s):" % os.path.relpath(p, REPO))
        for line in tb.rstrip().splitlines():
            w.say("    " + line)
        w.rows.append(dict(id=sid + ".crash", status="CRASHED", game=tb.rstrip().splitlines()[-1], traceback=os.path.relpath(p, REPO)))
    if go or not ok:
        w.say("  log: %s" % w.write_log(sid))
        with open(os.path.join(OUT, "%s_rows.json" % sid), "w", encoding="utf-8") as f:
            json.dump(w.rows, f, indent=1)
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["prep", "stage", "run", "go", "all", "restore"])
    ap.add_argument("scene", nargs="?")
    ap.add_argument("--from", dest="start", default="S1")
    ap.add_argument("--pace", type=float, default=1.5)
    ap.add_argument("--no-shots", action="store_true")
    ap.add_argument("--fresh-map", action="store_true", help="with go/all: a new quicktest map before EACH scene")
    ap.add_argument("--no-wait", action="store_true", help="all: do not wait for the CONTINUE file between scenes")
    ap.add_argument("--mock", action="store_true", help="offline: a fake bridge (water_scenes_mock.py); proves the "
                    "script's own paths run to the end, never anything about the game")
    ap.add_argument("--mock-fail", default=None, help="with --mock: raise inside this scene's run to prove a crash is "
                    "printed in full and the walk continues")
    a = ap.parse_args(argv)
    if a.mock:                      # mock output never lands beside live evidence
        global OUT
        OUT = OUT_MOCK
        a.no_shots = True
    w = Walk(a)
    rc = 0
    if a.verb in ("stage", "run", "go", "all") and not a.fresh_map:
        # LIVE 2026-10-23 (BENCH round 3a, save d map C): the keep snapshot lives in THIS process; only `prep` took it, so a
        # separate `stage/go S1` had none and prepare_site's remove_intruders vanished a review save's wild boar 18 cells
        # off the site. A map this run did not make keeps its own non-colonists from the start of every verb.
        w.say("  keep snapshot (current map): %s" % (w.V.sweep_at_start(w.B, made_map=False),))
    if a.verb == "prep":
        prep(w)
    elif a.verb == "restore":
        restore(w)
    elif a.verb in ("stage", "run", "go"):
        sid = (a.scene or "").upper()
        if sid not in STAGE:
            ap.error("scene must be one of %s" % ORDER)
        if a.verb == "go" and a.fresh_map:
            prep(w)
        rc = 0 if do_scene(w, sid, stage=a.verb in ("stage", "go"), go=a.verb in ("run", "go")) else 1
    else:
        for sid in ORDER[ORDER.index(a.start.upper()):]:
            if a.fresh_map:
                prep(w)
            if not do_scene(w, sid):
                rc = 1
            if not a.no_wait:
                w.say("%s done. Waiting for %s (create it to continue)..." % (sid, os.path.relpath(FLAG, REPO)))
                while not os.path.exists(FLAG):
                    time.sleep(2)
                os.remove(FLAG)
            w.log_lines, w.rows = [], []
        restore(w)
    return rc


if __name__ == "__main__":
    sys.exit(main())
