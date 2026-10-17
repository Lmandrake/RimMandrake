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
  options: --pace 1.5 (wall seconds between pulses) --no-shots
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
FLAG = os.path.join(OUT, "CONTINUE")
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
GATES = "RimMandrake.FlowWorks.RM_FlowDoorRules"   # RM_Sluice / RM_SecurityGrateDoor are Building_RM_FlowDoor
HPROBE = "RimMandrake.FlowWorks.Hose.HoseProbe"
WATER = "RM_Fluid_Water"
LEVEL_UNITS = 10000            # RM_Volume.UnitsPerLevel: tank/hose units per level
# the scene file's global exceptions to shipped defaults ("rain off, refill/seepage off, fire off, weather clear")
SCENE_OVERRIDES = {"rainFillsExcavationsEnabled": False, "refillEnabled": False}
SHIPPED = {"rainFillsExcavationsEnabled": True, "refillEnabled": True}

# ---------------------------------------------------------------- layout (map coords; west edge x = 0)
# Edge scenes: a WaterDeep lake 14 wide x 11 tall on the west edge (154 cells >= minLimitlessBodyCells 50, so LIMITLESS),
# the canal leaves its east shore along the lake's middle row. 14 wide, because a dug cell closer than
# GenGrid.NoBuildEdgeWidth (10) to an edge is an edge SINK (IsSinkCell): the first trial (lake 8 wide, canal at x 8..15)
# drained the canal's mouth into the sink every pulse (sinkTransferredTotal 13 in 15 pulses) and the canal stopped at
# cell 1 -- the scene file's own condition "every dug cell sits well outside the map-edge sink band". Interior scenes
# sit >= 30 cells from every edge.
LAKE_W, LAKE_H = 14, 11
BANDS = {"S1": 30, "S2": 50, "S4": 70, "S4g": 90, "S6g": 110, "S6g2": 130}     # lake bottom z per edge scene
INTERIOR = {"S3": (40, 30), "S3q": (40, 50), "S5": (70, 30), "S5e": (70, 60), "S6": (110, 30), "S6b": (110, 50)}


def mid(band):
    return BANDS[band] + LAKE_H // 2


def run(x0, z, n, d=1):
    return [(x0 + k, z) for k in range(n)]


# ---------------------------------------------------------------- bridge
class Walk(object):
    def __init__(self, args):
        import validation_core as V
        self.V = V
        self.B = V.Bridge()
        self.args = args
        self.log_lines = []
        self.rows = []
        os.makedirs(OUT, exist_ok=True)

    def call(self, tool, **kw):
        return self.B.call(tool, **kw)

    def say(self, s=""):
        print(s)
        sys.stdout.flush()
        self.log_lines.append(s)

    def proof(self, typ, method, arg):
        r = self.call("jawa/static_call", type=typ, method=method, args=arg)
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return r.get("success") is True and not txt.startswith("REFUSED"), txt

    def hp(self, cmd):
        return self.B.probe_of(HPROBE, cmd)

    def ticks(self, n):
        self.B.ticks(n)

    def tick_now(self):
        return (self.call("jawa/flowworks_engine_state") or {}).get("ticksGame")

    def interval(self):
        v = self.call("jawa/mod_settings_field", typeName=S_FW, action="get", field="pulseIntervalTicks").get("value")
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return 250

    def cells(self, cells):
        """{(x,z): (depth, fill)} plus the engine's pulse count, read in one ProofFluidRow over the bbox."""
        xs, zs = [c[0] for c in cells], [c[1] for c in cells]
        x0, z0 = min(xs), min(zs)
        w, h = max(xs) - x0 + 1, max(zs) - z0 + 1
        out, pulse = {}, None
        # ProofFluidRow caps w*h at 400: split tall boxes into row bands
        step = max(1, 400 // w)
        for zb in range(z0, z0 + h, step):
            ok, txt = self.proof(PROMO, "ProofFluidRow", "%d,%d,%d,%d" % (x0, zb, w, min(step, z0 + h - zb)))
            if not ok:
                return None, None
            head = txt.split(" ", 3)
            for tok in head[1:3]:
                if tok.startswith("pulse="):
                    pulse = int(tok.split("=")[1])
            for t in (head[3] if len(head) > 3 else "").split(";"):
                if ":" in t:
                    xz, rest = t.split(":", 1)
                    x, z = map(int, xz.split(","))
                    d, f = rest.split("/")[:2]
                    out[(x, z)] = (int(d), int(f))
        return out, pulse

    def body(self, c, classify=False):
        r = self.call("jawa/flowworks_body_report", x=c[0], z=c[1], classify=classify) or {}
        return r.get("body") or {}

    def dig(self, c, n, fill=-1):
        return self.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=fill)

    def set_fill(self, c, f):
        return self.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=0, setFill=f)

    def fill_in(self, c, n=1):
        return self.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=0, setFill=-1, fillInLevels=n)

    def build(self, ops, stuff=None):
        kw = dict(ops=ops, faction="player", wipeExisting=False)
        if stuff:
            kw["stuff"] = stuff
        return self.call("jawa/build_batch", **kw) or {}

    def clear_site(self, rect):
        """Soil, no things, no roof, no fog, and any old dug cells filled back in (ProofResetRect)."""
        x, z, w, h = rect
        self.proof(NSP, "ProofResetRect", "%d;%d;%d;%d" % rect)
        return self.V.prepare_site(self.B, rect, self.rows, "site_%d_%d" % (x, z))

    def frame(self, rect):
        x, z, w, h = rect
        self.call("jawa/clear_ui", all=True)
        self.call("rimworld/frame_cell_rect", x=x, z=z, width=w, height=h, paddingCells=2)

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
    return " ".join(("%d" % m[c][1]) if c in m else "?" for c in cells)


def one_run(m, cells):
    """True when the wet cells are one unbroken run starting at cells[0]."""
    wet = [m.get(c, (0, 0))[1] > 0 for c in cells]
    if not any(wet):
        return True
    k = wet.index(False) if False in wet else len(wet)
    return all(wet[:k]) and not any(wet[k:])


def verdict(ok):
    return "UNMEASURED" if ok is None else ("MATCHES" if ok else "DIFFERS")


def scene_doc(sid):
    with open(SCENES_JSON, encoding="utf-8") as f:
        doc = json.load(f)
    return next(s for s in doc["scenes"] if s["id"] == sid)


def expect_line(w, sid, eid, measured, ok, extra=""):
    s = scene_doc(sid)
    e = next((x for x in s["expected"] if x["id"] == eid), None)
    claim = e["claim"] if e else eid
    w.say("  %-6s %-10s doc: %s" % (eid, verdict(ok), claim))
    w.say("  %-6s %-10s game: %s%s" % ("", "", measured, (" | " + extra) if extra else ""))
    w.rows.append(dict(id=eid, status=verdict(ok), doc=claim, game=str(measured)))


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
    hist = [(0, m, tick_fn(0, m, w))]
    for k in range(1, n + 1):
        w.ticks(iv)
        m, pc = w.cells(cells_all)
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
    full = first_pulse(h, lambda m: all(m.get(c, (0, 0))[1] >= 1 for c in canal))
    expect_line(w, "S1", "S1.a", "all 8 hold 1 level first at pulse %s" % full, full is not None and full <= 10)
    broken = [k for k, m, _ in h if not one_run(m, canal)]
    expect_line(w, "S1", "S1.b", "pulses where the wet part was NOT one run from the lake: %s" % (broken or "none"), not broken)
    dried = [k for i, (k, m, _) in enumerate(h) for c in canal
             if i and h[i - 1][1].get(c, (0, 0))[1] > 0 and m.get(c, (0, 0))[1] == 0]
    expect_line(w, "S1", "S1.c", "a wet cell went dry at pulses: %s" % (sorted(set(dried)) or "never"), not dried)
    lim = [x.get("limitless") for _, _, x in h]
    expect_line(w, "S1", "S1.d", "lake limitless at every pulse: %s (stock %s -> %s)" % (
        all(lim), b0.get("stock"), h[-1][2].get("stock")), all(bool(v) for v in lim))


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
        w_.say("  pulse %2d  pond [%s]  trench [%s]" % (k, fills_str(m, pond), fills_str(m, trench)))
        return None
    h = pulse_loop(w, "S2", pond + trench, 60, tick, g["rect"], shots_at=(10, 30, 60))
    pf = first_pulse(h, lambda m: all(m.get(c, (0, 0))[1] >= 4 for c in pond))
    tf = first_pulse(h, lambda m: all(m.get(c, (0, 0))[1] >= 1 for c in trench))
    expect_line(w, "S2", "S2.a", "all 4 pond cells at 4 first at pulse %s" % pf, pf is not None and pf <= 30)
    expect_line(w, "S2", "S2.b", "all 6 trench cells at 1 first at pulse %s" % tf, tf is not None and tf <= 30)
    broken = [k for k, m, _ in h if not one_run(m, trench)]
    expect_line(w, "S2", "S2.c", "pulses where the wet trench was NOT one run from the pond: %s" % (broken or "none"), not broken)
    settle = None
    for i in range(len(h) - 3):
        if all(h[i][1] == h[j][1] for j in (i + 1, i + 2, i + 3)):
            settle = h[i][0]
            break
    changed = [k for k, m, _ in h if settle is not None and k > settle and m != h[settle][1]]
    expect_line(w, "S2", "S2.d", "settled at pulse %s; changes after that: %s" % (settle, changed or "none"),
                None if settle is None else not changed)


# ---------------------------------------------------------------- S3
def s3_geom():
    ox, oz = INTERIOR["S3"]
    pond = [(ox + 1 + i, oz + 1 + j) for i in range(4) for j in range(3)]
    canal = run(ox + 15, oz + 2, 6)
    return dict(pond=pond, canal=canal, pump=(ox + 9, oz + 2), reelA=(ox + 9, oz + 3), reelB=(ox + 9, oz),
                intake=(ox + 4, oz + 2), outflow=canal[0], battery=(ox + 12, oz + 6),
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
    notes = []
    r = w.build("RM_LiquidPump:%d,%d;RM_HoseReel:%d,%d;RM_HoseReel:%d,%d;Battery:%d,%d" % (
        g["pump"] + g["reelA"] + g["reelB"] + g["battery"]))
    if r.get("survived") is not None and r.get("survived") < 4:
        notes.append("build: %s" % str(r.get("failed"))[:200])
    w.ticks(2)
    lt = w.call("jawa/list_things", defName="Battery", rect="%d,%d,2,2" % g["battery"], limit=2) or {}
    bid = ((lt.get("things") or [{}])[0]).get("id")
    if bid is not None:
        w.call("jawa/battery_set", thing=bid, mode="setPct", value=1.0)
    la = w.hp("lay:%d,%d,%d,%d" % (g["reelA"] + g["intake"]))
    lb = w.hp("lay:%d,%d,%d,%d" % (g["reelB"] + g["outflow"]))
    if not la.get("success"):
        notes.append("intake hose not laid: %s" % la.get("reason"))
    if not lb.get("success"):
        notes.append("outflow hose not laid: %s" % lb.get("reason"))
    ra = _gizmo_cycle(w, g["reelA"], "Free end:", "Free end: Intake")
    rb = _gizmo_cycle(w, g["reelB"], "Free end:", "Free end: Outflow")
    for reel, want in ((g["reelA"], "Intake"), (g["reelB"], "Outflow")):
        rid = next((h.get("id") for h in w.hp("census").get("hoses") or [] if tuple(h.get("reel") or ()) == tuple(reel)), None)
        got = ((w.call("jawa/comp_read", thing="RM_HoseReel%s" % rid, comp="CompHoseReel", members="freeEndRole") or {})
               .get("values") or {}).get("freeEndRole")
        if str(got) != want:
            notes.append("reel %s free end reads %s, wanted %s" % (reel, got, want))
    if ra is not True:
        notes.append("intake role: %s" % ra)
    if rb is not True:
        notes.append("outflow role: %s" % rb)
    fl = w.hp("flick:%d,%d=off" % g["pump"])
    w.say("S3 staged: enclosed pond of 12 deep squares (body %s limitless=%s stock=%s capacity=%s); pump %s on dry ground "
          "switched OFF (%s); hose A -> pond end Intake; hose B -> canal cell 1 end Outflow; 6-cell depth-1 canal dry" % (
              b.get("id"), b.get("limitless"), b.get("stock"), b.get("capacity"), g["pump"], fl.get("success")))
    for n in notes:
        w.say("  STAGING NOTE: " + n)
    w.say("         screenshot: %s" % w.shot("S3_p00", g["rect"]))


def _hose_held(w):
    """Levels held inside the two S3 hoses: CompHoseReel.heldUnits (tank units) read off each reel."""
    g = s3_geom()
    tot = 0.0
    for reel in (g["reelA"], g["reelB"]):
        lt = w.call("jawa/list_things", defName="RM_HoseReel", rect="%d,%d,1,1" % reel, limit=2) or {}
        tid = ((lt.get("things") or [{}])[0]).get("id")
        v = ((w.call("jawa/comp_read", thing=tid, comp="CompHoseReel", members="heldUnits") or {}).get("values") or {})
        try:
            tot += float(v.get("heldUnits"))
        except (TypeError, ValueError):
            return float("nan")
    return tot / LEVEL_UNITS


def run_S3(w):
    g = s3_geom()
    canal, pond = g["canal"], g["pond"]
    b0 = w.body(pond[0])
    s0 = b0.get("stock")

    def tick(k, m, w_):
        b = w_.body(pond[0])
        held = _hose_held(w_)
        cf = sum(m.get(c, (0, 0))[1] for c in canal)
        gapwet = [c for c in g["gap"] if m.get(c, (0, 0))[1] > 0]
        w_.say("  pulse %2d  canal [%s]  pond stock=%s  hoses hold %.2f levels  ground between wet: %s" % (
            k, fills_str(m, canal), b.get("stock"), held, gapwet or "none"))
        return dict(stock=b.get("stock"), held=held, canal=cf, gapwet=gapwet)
    w.say("  step A: pump OFF for 20 pulses")
    ha = pulse_loop(w, "S3A", canal + g["gap"], 20, tick, g["rect"], shots_at=(20,))
    wetA = [k for k, _, x in ha if x["canal"] > 0]
    lostA = [k for k, _, x in ha if x["stock"] is not None and s0 is not None and float(x["stock"]) < float(s0) - 1e-6]
    expect_line(w, "S3", "S3.a", "canal wet at pulses %s; pond below its start (%s) at pulses %s" % (
        wetA or "never", s0, lostA or "never"), not wetA and not lostA)
    fl = w.hp("flick:%d,%d=on" % g["pump"])
    pw = w.hp("pump:%d,%d" % g["pump"])
    w.say("  step B: pump ON (%s; powered=%s)" % (fl.get("success"), pw.get("powered")))
    hb = pulse_loop(w, "S3B", canal + g["gap"], 16, tick, g["rect"], shots_at=(6, 16))
    full = first_pulse(hb, lambda m: all(m.get(c, (0, 0))[1] >= 1 for c in canal))
    expect_line(w, "S3", "S3.b", "all 6 canal cells at 1 first at pulse %s of step B" % full, full is not None and full <= 16)
    sB = hb[0][2]["stock"]
    bad = []
    for k, _, x in hb:
        if None in (x["stock"], sB):
            continue
        lost = float(sB) - float(x["stock"])
        gained = x["canal"] + x["held"]
        if abs(lost - gained) > 0.01:
            bad.append("p%d lost %.2f gained %.2f" % (k, lost, gained))
    expect_line(w, "S3", "S3.c", "pulses where canal+hoses gain != pond loss: %s" % (bad[:4] or "none"), not bad if sB is not None else None)
    gw = sorted({c for _, _, x in ha + hb for c in x["gapwet"]})
    expect_line(w, "S3", "S3.d", "undug ground between pond and canal ever wet: %s" % (gw or "never"), not gw)
    expect_line(w, "S3", "S3.e", "not staged in this walk (round trip A->tank->B->A needs tank jobs and two pump legs)", None)


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
        tot = sum(m.get(c, (0, 0))[1] for c in cs)
        obs.append("%s: canal holds %d level(s) after 10 pulses with no hose (%s)" % (
            name, tot, "pours straight into the touching dug cell - behaves as (a)/(c)" if tot else "nothing reached the canal - behaves as (b) or is not running (power/survey)"))
    ruling_line(w, "S3", "S3.Q1", "; ".join(obs))


def _hold_open_toggle(w, cell):
    w.call("rimworld/set_god_mode", enabled=True)
    w.call("rimworld/clear_selection")
    w.call("rimworld/click_cell", x=cell[0], z=cell[1])
    gz = (w.call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
    g = next((q for q in gz if q.get("label") == "Hold open"), None)
    ok = g is not None and w.call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id")).get("success")
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
    _hold_open_toggle(w, cell)
    _walk_in(w, cell)
    _, st = w.proof(GATES, "ProofLiquid", "current|%d,%d" % cell)
    return "%s (opening took %s ticks: Hold open on + a colonist walked in and left)" % (st, (w.tick_now() or 0) - (t0 or 0))


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
    up = first_pulse(ha, lambda m: all(m.get(c, (0, 0))[1] >= 1 for c in g["up"]))
    expect_line(w, "S4", "S4.a", "3 upstream cells at 1 first at pulse %s" % up, up is not None and up <= 6)
    leak = [k for k, m, _ in ha if any(m.get(c, (0, 0))[1] > 0 for c in g["down"])]
    expect_line(w, "S4", "S4.b", "downstream wet while shut at pulses: %s" % (leak or "never"), not leak)
    gr = first_pulse(ha, lambda m: all(m.get(c, (0, 0))[1] >= 1 for c in gg["down"]))
    expect_line(w, "S4", "S4.e", "grate: 4 downstream cells at 1 first at pulse %s" % gr, gr is not None and gr <= 12)
    state["step"] = "B"
    w.say("  step B: sluice OPEN, 20 pulses -- %s" % gate_open(w, g["gate"]))
    hb = pulse_loop(w, "S4B", allc, 20, tick, both, shots_at=(8, 20))
    dn = first_pulse(hb, lambda m: all(m.get(c, (0, 0))[1] >= 1 for c in g["down"]))
    expect_line(w, "S4", "S4.c", "4 downstream cells at 1 first at pulse %s after opening" % dn, dn is not None and dn <= 8)
    state["step"] = "C"
    w.say("  step C: sluice SHUT again, 40 pulses -- %s" % gate_shut(w, g["gate"]))
    hc = pulse_loop(w, "S4C", allc, 40, tick, both, shots_at=(20, 40))
    updry = [k for k, m, _ in hc if any(m.get(c, (0, 0))[1] < 1 for c in g["up"])]
    expect_line(w, "S4", "S4.d", "an upstream cell below 1 at pulses: %s" % (updry or "never"), not updry)
    d0 = sum(hc[0][1].get(c, (0, 0))[1] for c in g["down"])
    d1 = sum(hc[-1][1].get(c, (0, 0))[1] for c in g["down"])
    ruling_line(w, "S4", "S4.Q1", "downstream held %d level(s) when shut again and %d after 40 pulses (%s)" % (
        d0, d1, "stays put = (a)" if d1 == d0 else "it went down; whether back to the lake (b) or gone (c) needs the totals"))


# ---------------------------------------------------------------- S5
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


def _overflow(w):
    return (w.call("jawa/flowworks_engine_state") or {}).get("overflowDestroyedTotal")


def stage_S5(w):
    g, e = s5_geom(), s5e_geom()
    w.clear_site(g["rect"])
    w.clear_site(e["rect"])
    xs = [c[0] for c in g["pondA"]]
    zs = [c[1] for c in g["pondA"]]
    w.call("jawa/set_terrain_batch", ops="WaterDeep:%d,%d,3,3;WaterDeep:%d,%d,1,1" % (min(xs), min(zs), g["pondB"][0][0],
                                                                                      g["pondB"][0][1]))
    w.ticks(2)
    bA = w.body(g["pondA"][4], classify=True)
    bB = w.body(g["pondB"][0], classify=True)
    for c in g["canalA"] + g["canalB"]:
        w.dig(c, 1)
    for c in g["runD"]:
        w.dig(c, 1, fill=1)
    w.say("S5 staged: A = 3x3 enclosed pond (stock %s, limitless=%s) + 10-cell depth-1 canal; B = 1-square pond (stock %s, "
          "limitless=%s) + 10-cell canal; D = isolated 3-cell run at 1 level each (E, the basin, is dug when its turn comes)" % (
              bA.get("stock"), bA.get("limitless"), bB.get("stock"), bB.get("limitless")))
    w.say("         screenshot: %s" % w.shot("S5_p00", g["rect"]))


def run_S5(w):
    g, e = s5_geom(), s5e_geom()
    sA0 = w.body(g["pondA"][4]).get("stock")
    sB0 = w.body(g["pondB"][0]).get("stock")
    allc = g["canalA"] + g["canalB"] + g["runD"]

    def tick(k, m, w_):
        a, b = w_.body(g["pondA"][4]), w_.body(g["pondB"][0])
        w_.say("  pulse %2d  A canal [%s] pond %s   B canal [%s] pond %s" % (
            k, fills_str(m, g["canalA"]), a.get("stock"), fills_str(m, g["canalB"]), b.get("stock")))
        return dict(a=a.get("stock"), b=b.get("stock"), aw=a.get("cellCount"), ar=a.get("recededCount"))
    w.say("  parts A and B together, 54 pulses (A by 14, B by 10, then B's front must hold 40 more)")
    h = pulse_loop(w, "S5AB", allc, 54, tick, g["rect"], shots_at=(10, 14, 54))
    fa = first_pulse(h, lambda m: all(m.get(c, (0, 0))[1] >= 1 for c in g["canalA"]))
    sa = h[-1][2]["a"]
    expect_line(w, "S5", "S5.a", "A canal full first at pulse %s; pond A stock %s -> %s (doc wants 36 -> 26)" % (fa, sA0, sa),
                fa is not None and fa <= 14 and sa is not None and abs(float(sa) - 26) < 1e-3)
    expect_line(w, "S5", "S5.b", "pond A cells %s receded %s at the end (start stock %s, end %s)" % (
        h[-1][2]["aw"], h[-1][2]["ar"], sA0, sa), None if sa is None else float(sa) < float(sA0 or 0))
    mB = h[10][1] if len(h) > 10 else h[-1][1]
    wetB = [i + 1 for i, c in enumerate(g["canalB"]) if mB.get(c, (0, 0))[1] > 0]
    expect_line(w, "S5", "S5.c", "at pulse 10: B canal cells wet %s, pond B stock %s (start %s)" % (wetB, h[min(10, len(h) - 1)][2]["b"], sB0),
                wetB == [1, 2, 3, 4] and float(h[min(10, len(h) - 1)][2]["b"] or 0) == 0)
    ref = h[14][1] if len(h) > 14 else None
    moved = [k for k, m, _ in h[14:] if ref is not None and [m.get(c) for c in g["canalB"]] != [ref.get(c) for c in g["canalB"]]]
    flap = [k for k, _, x in h[14:] if x["b"] not in (None, 0, 0.0)]
    expect_line(w, "S5", "S5.d", "B canal changed after pulse 14 at pulses: %s%s" % (moved[:12] or "never", (
        " -- the pond and canal cell 1 trade one level back and forth (pond refills to 1 at pulses %s)" % flap[:8]) if flap else ""),
                not moved)
    # C: fill in canal B cell 1
    totB0 = sum(h[-1][1].get(c, (0, 0))[1] for c in g["canalB"]) + float(w.body(g["pondB"][0]).get("stock") or 0)
    ov0 = _overflow(w)
    w.fill_in(g["canalB"][0])
    w.say("  part C: canal B cell 1 filled in")
    hc = pulse_loop(w, "S5C", g["canalB"], 4, tick, g["rect"], shots_at=(1,))
    totB1 = sum(hc[-1][1].get(c, (0, 0))[1] for c in g["canalB"]) + float(w.body(g["pondB"][0]).get("stock") or 0)
    ov1 = _overflow(w)
    expect_line(w, "S5", "S5.e", "B canal+pond total %s -> %s; overflow destroyed %s -> %s" % (totB0, totB1, ov0, ov1),
                abs(totB0 - totB1) < 1e-3 and ov0 == ov1)
    # D: fill in the middle of the isolated run
    m0, _ = w.cells(g["runD"])
    d0 = sum(m0.get(c, (0, 0))[1] for c in g["runD"])
    ov0 = _overflow(w)
    w.fill_in(g["runD"][1])
    w.say("  part D: middle cell of the isolated 3-cell run filled in (look top-left for the message)")
    w.say("         screenshot: %s" % w.shot("S5_D_message", g["rect"]))
    m1, _ = w.cells(g["runD"])
    d1 = sum(m1.get(c, (0, 0))[1] for c in g["runD"])
    ov1 = _overflow(w)
    lost = None if None in (ov0, ov1) else float(ov1) - float(ov0)
    expect_line(w, "S5", "S5.f", "run held %s -> %s; game's destroyed-overflow total rose by %s (the message text is in the screenshot)" % (
        d0, d1, lost), None if lost is None else abs(lost - 1) < 1e-3 and d0 - d1 == 1)
    # E: the basin
    for c in e["basin"]:
        w.dig(c, 2)
    for c in e["centre"]:
        w.set_fill(c, 2)
    w.say("  part E: 6x6 depth-2 basin dug now, 8 levels heaped in the 4 centre cells, 20 pulses")

    def tickE(k, m, w_):
        row = lambda j: "".join(str(m.get((e["basin"][0][0] + i, e["basin"][0][1] + j), (0, 0))[1]) for i in range(6))
        w_.say("  pulse %2d  basin rows %s  total %d" % (k, " ".join(row(j) for j in range(6)), sum(m.get(c, (0, 0))[1] for c in e["basin"])))
        return None
    he = pulse_loop(w, "S5E", e["basin"], 20, tickE, e["rect"], shots_at=(20,))
    mE = he[-1][1]
    deep = [c for c in e["basin"] if mE.get(c, (0, 0))[1] >= 2]
    dry = [c for c in e["basin"] if mE.get(c, (0, 0))[1] == 0]
    tot = sum(mE.get(c, (0, 0))[1] for c in e["basin"])
    expect_line(w, "S5", "S5.g", "pulse 20: %d cell(s) at 2 while %d dry; total %d (doc: none at 2 while any dry; total 8)" % (
        len(deep), len(dry), tot), not (deep and dry) and tot == 8)
    ruling_line(w, "S5", "S5.Q1", "pond B (one square, stock %s at start) wet canal cells %s at pulse 10 -> %s" % (
        sB0, wetB, "(a) four" if len(wetB) == 4 else "(b) five" if len(wetB) == 5 else "%d cells" % len(wetB)))


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


def _s6_snap(w, g):
    cells = g["canal"] + g["gate"]["canal"]
    m, _ = w.cells(cells)
    _, gs = w.proof(GATES, "ProofLiquid", "current|%d,%d" % g["gate"]["gate"])
    return dict(m=[list(m.get(c, (None, None))) for c in cells] if m else None,
                pond=w.body(g["pond"][4]).get("stock"), gate=gs.split("|")[0].strip())


def stage_S6(w):
    _s6_stage(w)
    g = s6_geom()
    w.say("S6 staged (run 1, never saved): S5 part A (3x3 pond + 10-cell canal) and S4's gate scene shut with the downstream half full")
    w.say("         screenshot: %s" % w.shot("S6_p00", g["rect"]))


def _s6_line(k, s):
    return "  pulse %2d  canal [%s]  pond %s  gate %s" % (k, " ".join(str(v[1]) for v in s["m"][:10]) if s["m"] else "?",
                                                       s["pond"], s["gate"])


def run_S6(w):
    g = s6_geom()
    iv = w.interval()
    w.say("  run 1: uninterrupted to pulse 30")
    r1 = []
    for k in range(31):
        if k:
            w.ticks(iv)
        s = _s6_snap(w, g)
        r1.append(s)
        w.say(_s6_line(k, s))
        time.sleep(w.args.pace / 3)
    w.say("         screenshot: %s" % w.shot("S6_run1_p30", g["rect"]))
    w.say("  run 2: the same start again on a fresh twin plot just north; save at pulse 4, reload, continue to 30")
    g = s6_geom(True)
    _s6_stage(w, True)
    for k in range(5):
        if k:
            w.ticks(iv)
    pre = _s6_snap(w, g)
    w.say(_s6_line(4, pre) + "   <- saving")
    name = "RM_fw_scene_S6_%s" % time.strftime("%Y%m%d%H%M%S")
    sv = w.call("rimworld/save_game", saveName=name) or {}
    ld = w.call("rimworld/load_game_ready", saveName=name, timeoutMs=240000) or {}
    ok, waited = w.V._wait_playing(w.B, leave_s=0)
    post = _s6_snap(w, g)
    w.say(_s6_line(4, post) + "   <- after reload (save %s, load %s)" % (sv.get("success"), ld.get("success")))
    same = pre == post
    expect_line(w, "S6", "S6.a", "after reload: cells, pond stock and gate %s the save" % ("EQUAL" if same else "DIFFER FROM"),
                same if pre["m"] and post["m"] else None, "" if same else "pre %s / post %s" % (json.dumps(pre)[:200], json.dumps(post)[:200]))
    tot = lambda s: (sum(v[1] or 0 for v in s["m"]) + float(s["pond"] or 0)) if s["m"] else None
    expect_line(w, "S6", "S6.b", "total liquid before save %s, after reload %s" % (tot(pre), tot(post)),
                None if None in (tot(pre), tot(post)) else abs(tot(pre) - tot(post)) < 1e-3)
    r2 = [pre]
    for k in range(5, 31):
        w.ticks(iv)
        s = _s6_snap(w, g)
        r2.append(s)
        w.say(_s6_line(k, s))
        time.sleep(w.args.pace / 3)
    w.say("         screenshot: %s" % w.shot("S6_run2_p30", g["rect"]))
    expect_line(w, "S6", "S6.c", "pulse 30: cells %s; pond run 1 %s, run 2 %s" % (
        "equal" if r2[-1]["m"] == r1[-1]["m"] else "differ", r1[-1]["pond"], r2[-1]["pond"]),
                r2[-1]["m"] == r1[-1]["m"] and r2[-1]["pond"] == r1[-1]["pond"])
    diffs = [k for k in range(5, 31) if r1[k]["m"] != r2[k - 4]["m"]]
    ruling_line(w, "S6", "S6.Q1", "pulse-by-pulse after the reload, run 2 differed from run 1 at pulses: %s" % (diffs or "none"))


# ---------------------------------------------------------------- prep / settings
def prep(w):
    st = w.call("rimworld/get_ui_state").get("programState")
    if st != "Playing" or w.args.fresh_map:
        if st == "Playing":
            w.call("rimworld/go_to_main_menu")     # start_debug_game_ready on a Playing game keeps the old map
            time.sleep(5)
        w.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
        ok, waited = w.V._wait_playing(w.B, leave_s=0)
        w.say("quicktest map up: %s (%s s)" % (ok, waited))
    w.call("rimworld/pause_game", paused=True)
    w.call("jawa/weather_set", weather="Clear", lockWeather=True)
    w.call("jawa/incident_queue_clear")
    w.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
    w.call("rimworld/set_god_mode", enabled=True)
    for c in w.hp("colonists").get("pawns") or []:
        w.hp("pawn:%d=draft" % c["id"])
    mi = w.call("jawa/map_info") or {}
    got = {}
    for f, v in SCENE_OVERRIDES.items():
        w.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))
        got[f] = w.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")
    w.say("map %sx%s; settings at shipped defaults except the scene file's: %s (read back)" % (
        mi.get("sizeX") or mi.get("width"), mi.get("sizeZ") or mi.get("height"), got))
    w.say("pulse interval %d ticks (shipped default 250)" % w.interval())


def restore(w):
    got = {}
    for f, v in SHIPPED.items():
        w.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))
        got[f] = w.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")
    w.say("shipped settings restored: %s" % got)


STAGE = {"S1": stage_S1, "S2": stage_S2, "S3": stage_S3, "S4": stage_S4, "S5": stage_S5, "S6": stage_S6}
RUN = {"S1": run_S1, "S2": run_S2, "S3": run_S3, "S4": run_S4, "S5": run_S5, "S6": run_S6}
ORDER = ["S1", "S2", "S3", "S4", "S5", "S6"]


def do_scene(w, sid, stage=True, go=True):
    s = scene_doc(sid)
    w.say("=" * 100)
    w.say("%s. %s" % (sid, s["title"]))
    for line in s["grid"]:
        w.say("    " + line)
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
        w.say("  log: %s" % w.write_log(sid))
        with open(os.path.join(OUT, "%s_rows.json" % sid), "w", encoding="utf-8") as f:
            json.dump(w.rows, f, indent=1)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["prep", "stage", "run", "go", "all", "restore"])
    ap.add_argument("scene", nargs="?")
    ap.add_argument("--from", dest="start", default="S1")
    ap.add_argument("--pace", type=float, default=1.5)
    ap.add_argument("--no-shots", action="store_true")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args(argv)
    w = Walk(a)
    if a.verb == "prep":
        prep(w)
    elif a.verb == "restore":
        restore(w)
    elif a.verb in ("stage", "run", "go"):
        sid = (a.scene or "").upper()
        if sid not in STAGE:
            ap.error("scene must be one of %s" % ORDER)
        do_scene(w, sid, stage=a.verb in ("stage", "go"), go=a.verb in ("run", "go"))
    else:
        for sid in ORDER[ORDER.index(a.start.upper()):]:
            do_scene(w, sid)
            w.say("%s done. Waiting for %s (create it to continue)..." % (sid, os.path.relpath(FLAG, REPO)))
            while not os.path.exists(FLAG):
                time.sleep(2)
            os.remove(FLAG)
            w.log_lines, w.rows = [], []
        restore(w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
