"""owner_review_stage.py -- ONE FlowWorks owner-review map: stage everything, shoot it, save ONE named savegame.

  python.exe src/RimMandrake/FlowWorks/northstar/owner_review_stage.py --dry-run     # prints the plan, no bridge, no game
  python.exe src/RimMandrake/FlowWorks/northstar/owner_review_stage.py               # LIVE: bridge held, a Playing disposable map
  python.exe src/RimMandrake/FlowWorks/northstar/owner_review_stage.py --only ladders,gates --no-save
  options: --origin X,Z (default 100,100, moved to fit the map)  --save-name NAME  --no-save  --no-shots  --mock (FakeGame, seconds)
  Wrap the live run in save_guard for the keeper-saves check:
  python3 src/RimMandrake/Utils/save_guard.py run --current-slot none -- python.exe <this script>

Rows (each gets a labelled picture; the overview picture carries all of them):
  ladders   four 3x3 pits, 3 deep. Pit k has its LOWERED ladder INSIDE the dug middle square of wall k (N,E,S,W) and a RAISED one
            on the opposite wall. Ladders are placed with the wall's own rotation INSIDE the dug square and hang on the wall
            (RM_LadderUtility.WallRotAt: the rotation faces the SHALLOWER neighbour). Raise = RM_PromotionProofs.ProofLadder "x,z,raise".
  spikes    RM_Spikes on every square of a dry 3-deep pit, and of a pit holding 1 m of water (fill 2 notches).
  gates     RM_Sluice and RM_SecurityGrateDoor in E-W and N-S canals, all four facings, closed; plus one of each HELD OPEN (the
            Hold open button + a colonist walking in, water_scenes_walk.gate_open; skipped with a reason when it cannot be done).
  shallows  six separate dug pits at 0.2 / 0.5 / 1 / 1.5 / 2 / 5 m of water. A driver sets WHOLE 0.5 m notches (fill 1..10), so the
            0.2 m square is a 5-square strip given 2 notches that LEVEL to 0.2 m each. The build picks the terrain (RM_WaterLadder).
  hoses     (--only hoses) pipe vs hose girth: RM_LiquidPump with a pipe W + hose E, pipe N + hose S, hoses W + E; a 2x2 tank, a tap and a
            sprinkler head each fed by a pipe AND a hose; a 6-square pipe run beside a hose run; a colonist beside each for scale.
            A hose is NOT a plain spawn: an RM_HoseReel is built touching the pump (it couples to it) and the hose is laid with the
            HoseProbe command "lay:reelx,reelz,endx,endz" (static_call-style probe, water_scenes_walk.Walk.hp). Shots land in
            Transient/fw_hoses_walk/FlowWorks_HosePipeWalk_<date>_<scene>_{wide,close}.png.
  sprinklers four nets (tank, pipe run, pump over the pipe, power, head) with the pipe run restyled Futuristic / Industrial / Modern /
            Scrapper BEFORE the head is built (a head takes its pipe's look); ticks run past one hourly pulse so the spray shows.
  bars_joint   (default) 1 m of water in 1/2/4 m holes, and 0.5/1/2 m of water in 4 m holes; a colonist in the 2 m+ water holes (swims).
  bars_dry     (default) dry holes 0.5/1/1.5/2/4/8 m, a colonist standing in each (pawn height ladder to 2 m and deeper).
  bars_trench  (default) a colonist waist-deep (1 m) and chest-deep (1.5 m) with a shooter on flat ground; ProofTrenchCover read into notes.
  bars_access  (default) portable ladder in a 2 m pit and against a 4 m wall; climbing gear on the ground; a geared and an ungeared
            colonist in 4 m sheer pits; a pit cover over a 2 m pit.
  bars_bridges (default) suspension bridges rope/timber/steel/heavy over 4 m pits, railings on (north lane, higher z) and off (south lane), plus a
            pit cover beside them. Built with RM_SuspensionProofs.ProofBuild "...;god" and ProofRails (the proof script's own calls).
  bars_bridge_kinds (default) the other suspension parts: steel and heavy GRATED decks, steel and heavy JETTIES, and the steel bridge in
            each of the four looks (Scrapper/Industrial/Modern/Futuristic, railings on) via ProofLook. Own lane south of bars_bridges.
  Bars with NO site (no bridge tool can pose them): wall-climb mid-climb (RM_WallClimb has no pose call; the scale-a-built-wall build
  is in progress), raiders-never-shelter (a raid-run state read), jump-into-pit hurts nobody (state read; live_session g_pit_access).
  Site for all bars_* rows: east of the hoses, rect "bars_rect" (x = origin+150, 62 wide, 76 tall); live_session's owner zone is 216 wide.
Every station is NUMBERED (standing rule, owner 2026-10-24): Stage.station gives it the next number, its caption line in the
row picture starts with it, and a world label with the same number sits just north of it; rows are dense (DENSE_GAP squares
between neighbours at most) and every bridge spans a 3-wide 4 m pit. layout_problems() reports a break of either as a NOTE.
Then: kill hostiles, Clear weather locked, stepped toward midday, camera framed, shots, ONE save.
Map: a vanilla biome only (WATER_TRUE_BIOMES; --any-biome overrides), and a 3x3 vanilla WaterShallow swatch south of the ladders
row is photographed and its mean colour measured: water that does not read blue over red WITHHOLDS the save
(WATER_LOOK_DIAGNOSE_GREY_ON_THE_ROT: on RM_TheRot every water square drew flat grey-brown). Every frame is zoomed to fit its
whole rect (water_scenes_walk.fit_root_size), never below the engine's rootSize floor.

Every action goes through Stage: --dry-run prints exactly the calls a live run would make.
Bridge tools used (all found in the repo): jawa/flowworks_excavation_drive, jawa/build_batch, jawa/battery_set, jawa/static_call (ProofLadder, ProofTank,
ProofReadout, ProofResetRect), jawa/list_things, jawa/kill_hostiles, jawa/weather_set, jawa/time_clock,
jawa/clear_ui, jawa/take_screenshot, rimworld/frame_cell_rect, rimworld/save_game, rimworld/click_cell, rimworld/execute_gizmo.
"""
import argparse
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
ROT = ("North", "East", "South", "West")
LOOKS = ("Futuristic", "Industrial", "Modern", "Scrapper")
PULSE = 2500
NOTCH_M = 0.5                      # one fill notch = 0.5 m of water over a square (RM_LevelSolve.MetresPerUnit * U)
SHALLOWS = ((0.5, 1), (1.0, 2), (1.5, 3), (2.0, 4), (5.0, 10))   # (metres, notches)
BARS_ROWS = ("bars_joint", "bars_dry", "bars_trench", "bars_access", "bars_bridges", "bars_bridge_kinds")
ALL_ROWS = ("ladders", "spikes", "gates", "shallows", "sprinklers") + BARS_ROWS
OPT_ROWS = ("hoses", "picks")            # run only when named in --only (own site east of the others; not in the default sweep)

# WATER_LOOK_DIAGNOSE_GREY_ON_THE_ROT (2026-10-23): on a biomes_sprint quicktest on RM_TheRot every dug water square AND a
# painted vanilla WaterDeep lake drew flat grey-brown (pit mean RGB 67,61,47 against soil 91,57,30; good water on a temperate
# map reads 83,93,97 -- blue over red). Not FlowWorks: RM_LiquidLooks never touches a base-game terrain (Owned() refuses
# official ones), so the vanilla lake drew the same with no FlowWorks look on it, and the mod sets no shader global. The
# map is the variable: the Rot is our night-shoulder biome (pinned low sun, its own sky targets). So the owner's map is a
# vanilla-biome map, and a vanilla shallow-water swatch is photographed and MEASURED before the save is kept.
WATER_TRUE_BIOMES = ("TemperateForest", "TemperateSwamp", "BorealForest", "TropicalRainforest", "TropicalSwamp",
                     "AridShrubland", "Desert", "Tundra", "ColdBog")
SWATCH = "WaterShallow"
SWATCH_BLUE_MARGIN = 5          # mean blue minus mean red over the swatch's centre: good 97-83 = +14, the grey Rot water -20


def swatch_rect(ox, oz):
    """The 3x3 vanilla water swatch: inside the cleared site rect, south of the ladders row (pure)."""
    return (ox - 2, oz - 5, 3, 3)


def water_verdict(rgb, margin=SWATCH_BLUE_MARGIN):
    """True when a mean (r, g, b) reads as water (blue over red by margin), False when grey/brown, None unread (pure)."""
    if not rgb or len(rgb) < 3 or any(v is None for v in rgb[:3]):
        return None
    return (rgb[2] - rgb[0]) >= margin


def centre_rgb(png, frac=0.06):
    """Mean RGB of the centre square (frac of the image height) of a screenshot; None when unreadable."""
    try:
        from PIL import Image, ImageStat
        im = Image.open(png).convert("RGB")
        W, H = im.size
        r = max(4, int(H * frac / 2))
        return [round(v, 1) for v in ImageStat.Stat(im.crop((W // 2 - r, H // 2 - r, W // 2 + r, H // 2 + r))).mean]
    except Exception:  # noqa: BLE001 - an unreadable picture is no verdict, never a pass
        return None


# ------------------------------------------------------------------ geometry (pure)
def wall_cell(pit, r, n=3):
    """Dug middle square of wall r (0=N,1=E,2=S,3=W) of an n x n pit with south-west corner `pit`."""
    px, pz = pit
    m = n // 2
    return {0: (px + m, pz + n - 1), 1: (px + n - 1, pz + m), 2: (px + m, pz), 3: (px, pz + m)}[r]


def opposite(r):
    return (r + 2) % 4


BARS_Z = dict(bars_joint=(-1, 11), bars_dry=(13, 5), bars_trench=(21, 5), bars_access=(29, 8), bars_bridges=(38, 9),
              bars_bridge_kinds=(46, 13))     # (z offset from the bars origin, height) of each bars row, from its own staging


def bars_row_rect(L, row):
    """Camera rect of ONE bars row (the whole 62x76 site would put every bars picture at the same far-off framing)."""
    bx, bz = L["bars"]
    dz, h = BARS_Z[row]
    return (bx, bz + dz, 62, h)


def layout(ox, oz):
    """Every row's origin. Site rect (x, z, w, h) covers all of it."""
    return dict(
        hoses=(ox + 70, oz), hoses_rect=(ox + 64, oz - 6, 84, 76),
        picks=(ox, oz + 72), picks_rect=(ox - 3, oz + 68, 56, 18),
        bars=(ox + 150, oz), bars_rect=(ox + 150, oz - 6, 62, 76),
        ladders=(ox, oz), spikes=(ox, oz + 8), gates_sluice=(ox, oz + 16), gates_grate=(ox, oz + 25),
        shallows=(ox, oz + 34), sprinklers=(ox, oz + 49), rect=(ox - 3, oz - 6, 64, 70))


SITE_KEYS = ("rect", "hoses_rect", "picks_rect", "bars_rect")
DEFAULT_MAP = (250, 250)          # a dry run has no map to ask: the debug quicktest size
FIT_MARGIN = 2


def site_extent(L):
    """(x0, z0, x1, z1) bounding every site rect of the layout, x1/z1 exclusive (pure)."""
    rs = [L[k] for k in SITE_KEYS]
    return (min(r[0] for r in rs), min(r[1] for r in rs), max(r[0] + r[2] for r in rs), max(r[1] + r[3] for r in rs))


def fit_origin(ox, oz, size, margin=FIT_MARGIN):
    """REVIEW_STAGER_FIX_BARS_OFF_SMALL_MAP: the origin nearest (ox, oz) at which the whole site lies inside a map of `size`
    (W, H) with `margin` to spare. Raises ValueError when the site is larger than the map (pure)."""
    x0, z0, x1, z1 = site_extent(layout(ox, oz))
    W, H = size
    if x1 - x0 + 2 * margin > W or z1 - z0 + 2 * margin > H:
        raise ValueError("the review site is %dx%d squares, the map %dx%d: it cannot fit" % (x1 - x0, z1 - z0, W, H))
    dx = max(margin - x0, 0) + min(W - margin - x1, 0)
    dz = max(margin - z0, 0) + min(H - margin - z1, 0)
    return ox + dx, oz + dz


def offmap_problems(stations, size):
    """[str] every station whose rect (or label cell) is not wholly on a map of `size` (pure). Never a note: a hard failure."""
    W, H = size
    out = []
    for st in stations:
        x, z, w, h = st["rect"]
        lx, lz = station_label_cell(st)
        if x < 0 or z < 0 or x + w > W or z + h > H or not (0 <= lx < W and 0 <= lz < H):
            out.append("station %s %r rect %s is off the %dx%d map" % (st["n"], st.get("short"), st["rect"], W, H))
    return out


# ------------------------------------------------------------------ Stage: plan + execution in ONE path
# REVIEW_STAGER_FIX_NUMBER_EVERY_STATION (owner 2026-10-24: "label and number these stations ... this is a standing
# requirement" and "the sprinkler stations could all be shown much closer to each other ... dense review rather than
# sparse"). Every row registers each station (Stage.station) with the rect it occupies: the station gets the next number,
# its caption line in the row picture starts with that number, and a world label carrying the same number is pinned just
# north of it (jawa/review_label, tag LABEL_TAG; the bridge writes the labels into the save's sidecar, so they come back
# with the save). Dense: neighbouring stations in one lane sit at most DENSE_GAP empty squares apart and never overlap.
DENSE_GAP = 2
LABEL_TAG = "owner_review_stage"
LABEL_GOLD = "#ffd27f"


def label_op(x, z, text, sub="", col=LABEL_GOLD, size="small", tag=LABEL_TAG):
    """One jawa/review_label add-op line, 'x|z|text|sub|#rrggbb|size|tag' (the format of modcheck/reviewmap.label_line)."""
    clean = lambda t: str(t).replace("|", "/").replace("\n", " ").replace("\r", " ")  # noqa: E731
    return "%d|%d|%s|%s|%s|%s|%s" % (x, z, clean(text), clean(sub), col, size, tag)


def station_label_cell(st):
    """The cell a station's number label is pinned to: its rect's middle column, the row just north of it (pure)."""
    x, z, w, h = st["rect"]
    return (x + w // 2, z + h)


def station_label_ops(stations):
    """[add-op] one per station: text = its number, sub = a short name clipped to the room over the station (pure)."""
    out = []
    for st in stations:
        x, z = station_label_cell(st)
        room = max(8, 3 * (st["rect"][2] + DENSE_GAP))
        short = st["short"] if len(st["short"]) <= room else st["short"][:room - 1].rstrip() + "~"
        out.append(label_op(x, z, "%d" % st["n"], short))
    return out


def _overlap(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def _inside(c, r):
    return r[0] <= c[0] < r[0] + r[2] and r[1] <= c[1] < r[1] + r[3]


def layout_problems(stations, rows=None, gap=DENSE_GAP):
    """[str] every way the station list breaks the standing rule (pure): numbers not 1..N in order, a station without a
    rect or a name, two stations overlapping, a label pinned inside another station, and -- for rows in `rows` (None =
    all) -- neighbouring stations of one lane more than `gap` empty squares apart (sparse)."""
    probs = []
    if [st["n"] for st in stations] != list(range(1, len(stations) + 1)):
        probs.append("station numbers not 1..%d in order: %s" % (len(stations), [st["n"] for st in stations]))
    for st in stations:
        r = st.get("rect")
        if not r or len(r) != 4 or r[2] < 1 or r[3] < 1 or not st.get("text"):
            probs.append("station %s has no rect or no name: %s" % (st.get("n"), st))
    for i, a in enumerate(stations):
        for b in stations[i + 1:]:
            if _overlap(a["rect"], b["rect"]):
                probs.append("stations %d and %d overlap: %s %s" % (a["n"], b["n"], a["rect"], b["rect"]))
        lc = station_label_cell(a)
        for b in stations:
            if b is not a and _inside(lc, b["rect"]):
                probs.append("label of station %d at %s sits inside station %d" % (a["n"], lc, b["n"]))
    lanes = {}
    for st in stations:
        if rows is None or st["row"] in rows:
            lanes.setdefault((st["row"], st["lane"]), []).append(st)
    for (row, lane), sts in lanes.items():
        sts = sorted(sts, key=lambda t: t["rect"][0])
        for a, b in zip(sts, sts[1:]):
            g = b["rect"][0] - (a["rect"][0] + a["rect"][2])
            if g > gap:
                probs.append("sparse: %s lane %s stations %d and %d are %d squares apart (dense = at most %d)" % (
                    row, lane, a["n"], b["n"], g, gap))
    return probs


def row_rect(stations, row, margin=2):
    """Camera rect fitting one row's stations and their labels (pure); None when the row has no station."""
    rs = [st["rect"] for st in stations if st["row"] == row]
    if not rs:
        return None
    x0 = min(r[0] for r in rs) - margin
    z0 = min(r[1] for r in rs) - margin
    x1 = max(r[0] + r[2] for r in rs) + margin
    z1 = max(r[1] + r[3] for r in rs) + margin + 1          # +1: the label row north of the stations
    return (x0, z0, x1 - x0, z1 - z0)


class Stage(object):
    def __init__(self, w, dry):
        self.w, self.dry, self.plan, self.notes = w, dry, [], []
        self.stations = []

    def station(self, row, rect, text, lane=0, short=None):
        """Register one station: the next number, the rect it occupies, its caption. Returns the caption line, numbered."""
        n = len(self.stations) + 1
        self.stations.append(dict(n=n, row=row, lane=lane, rect=tuple(rect), text=text, short=short or text))
        self.say("  station %d (%s) %s: %s" % (n, row, tuple(rect), text))
        return "%d  %s" % (n, text)

    def labels(self):
        """Pin every station's number label (jawa/review_label, cleared first). The ops are the plan in a dry run."""
        ops = station_label_ops(self.stations)
        self.say("  review_label clear tag=%s; add %d station labels" % (LABEL_TAG, len(ops)))
        for op in ops:
            self.say("    label %s" % op)
        if not self.dry:
            self.w.call("jawa/review_label", action="clear", tag=LABEL_TAG)
            r = self.w.call("jawa/review_label", action="add", ops="\n".join(ops), tag=LABEL_TAG) or {}
            if self.chk("review_label add", r) and r.get("refused"):
                self.notes.append("station labels refused: %s" % str(r.get("refused"))[:200])
        return ops

    def say(self, s):
        self.plan.append(s)
        print(s, flush=True)

    def chk(self, what, r):
        """Note a bridge reply that is empty or says success=false. Returns True when it looked fine (a picture of a failed
        stage is not a staged scene)."""
        if isinstance(r, dict) and r.get("success") is not False and r:
            return True
        self.notes.append("%s FAILED: %s" % (what, str(r)[:140]))
        return False

    def dig(self, c, n, fill=-1):
        self.say("  dig %s depth %d%s" % (c, n, "" if fill < 0 else " fill %d" % fill))
        if not self.dry:
            self.chk("dig %s depth %d" % (c, n), self.w.dig(c, n, fill))

    def fill(self, c, f):
        self.say("  fill %s = %d notches (%.1f m)" % (c, f, f * NOTCH_M))
        if not self.dry:
            self.chk("fill %s = %d" % (c, f), self.w.set_fill(c, f))

    def pit(self, origin, n, depth, fill=-1):
        for i in range(n):
            for j in range(n):
                self.dig((origin[0] + i, origin[1] + j), depth, fill)

    def place(self, d, c, rot=None, stuff=None):
        self.say("  place %s at %s rot=%s%s" % (d, c, "-" if rot is None else "%d(%s)" % (rot, ROT[rot]), " stuff=%s" % stuff if stuff else ""))
        if self.dry:
            return dict(survived=True, rot_read=rot, note="")
        import fw_walk_common as C
        r = C.place(self.w, d, c, rot=rot, stuff=stuff)
        if not r.get("survived"):
            self.notes.append("place %s at %s NOT on the map: %s" % (d, c, r.get("note")))
        return r

    def raise_ladder(self, c, up=True):
        self.say("  ladder %s -> %s (ProofLadder)" % (c, "RAISED" if up else "lowered"))
        if self.dry:
            return True
        ok, txt = self.w.proof(PROMO, "ProofLadder", "%d,%d,%s" % (c[0], c[1], "raise" if up else "lower"))
        if not ok or ("raised=%s" % up) not in txt:
            self.notes.append("ladder %s raise read: %s" % (c, txt[:90]))
        return ok

    def hp(self, cmd):
        self.say("  hose probe %s" % cmd)
        if self.dry:
            return {"success": True}
        return self.w.hp(cmd) or {}

    def charge(self, cell):
        self.say("  battery_set charge battery at %s to 100%%" % (cell,))
        if self.dry:
            return
        import fw_walk_common as C
        bat = [t for t in C.list_things(self.w, ["Battery"], (cell[0] - 2, cell[1] - 2, 5, 5)) if t["cell"] == cell]
        br = self.w.call("jawa/battery_set", thing=bat[0]["raw"].get("id"), mode="setPct", value=1.0) if bat else {}
        if not (br or {}).get("storedEnergyPctAfter"):
            self.notes.append("battery at %s NOT charged (%s): its pump will show no power" % (cell, str(br)[:120]))

    def store(self, cell, litres_dl=100000):
        self.say("  fill tank %s with RM_Liquid_FreshWater %d dL (ProofTank)" % (cell, litres_dl))
        if not self.dry:
            ok, txt = self.w.proof("RimMandrake.FlowWorks.RM_NorthstarProofs", "ProofTank",
                                   "%d,%d;Store;RM_Liquid_FreshWater;%d" % (cell[0], cell[1], litres_dl))
            if not ok:
                self.notes.append("tank at %s NOT filled: %s" % (cell, txt[:120]))

    def colonist(self, cell):
        self.say("  colonist stands at %s (scale)" % (cell,))
        if self.dry:
            return
        p = (self.w.hp("colonists").get("pawns") or [None])[0]
        if p is None:
            self.notes.append("no colonist to stand at %s for scale" % (cell,))
            return
        self.w.hp("pawn:%d=tp:%d,%d" % (p["id"], cell[0], cell[1]))

    def pawn(self, cell, label="", wear=None):
        """A drafted colonist standing at cell (spawn_pawn Colonist, as live_session.Run.spawn); wear = defName of apparel. Returns id or None."""
        self.say("  colonist at %s%s%s" % (cell, " (%s)" % label if label else "", " wearing %s" % wear if wear else ""))
        if self.dry:
            return 0
        r = self.w.call("jawa/spawn_pawn", kindDef="Colonist", x=cell[0], z=cell[1], faction="player", count=1) or {}
        pid = ((r.get("pawns") or [{}])[0]).get("id")
        if pid is None:
            self.notes.append("colonist at %s NOT spawned (%s)" % (cell, str(r)[:100]))
            return None
        if wear:
            g = self.w.call("jawa/pawn_gear", **{"pawn": pid, "action": "wear", "def": wear, "stuff": ""}) or {}
            if not g.get("success"):
                self.notes.append("%s NOT worn at %s (%s)" % (wear, cell, str(g)[:100]))
        # jawa/spawn_pawn answers ids like "Human41594": the probe wants the number (live 2026-10-19: TypeError killed B9)
        m = re.search(r"(\d+)$", str(pid))
        if m:
            self.w.hp("pawn:%d=draft" % int(m.group(1)))
        return pid

    def item(self, d, cell):
        self.say("  item %s at %s (spawn_batch)" % (d, cell))
        if not self.dry:
            self.chk("item %s at %s" % (d, cell), self.w.call("jawa/spawn_batch", ops="%s:%d,%d" % (d, cell[0], cell[1])))

    def proof(self, typ, method, arg):
        self.say("  proof %s.%s(%s)" % (typ.split(".")[-1], method, arg))
        if self.dry:
            return True, ""
        ok, txt = self.w.proof(typ, method, arg)
        if not ok:
            self.notes.append("proof %s.%s(%s) REFUSED/failed: %s" % (typ.split(".")[-1], method, arg, (txt or "")[:120]))
        return ok, txt

    def ticks(self, n):
        self.say("  advance %d ticks" % n)
        if not self.dry:
            try:
                self.w.ticks(n)
            except Exception as ex:  # noqa: BLE001 - a GovernorStop (hurt/starving) on a STAGING clock is not a verdict
                if type(ex).__name__ != "GovernorStop":
                    raise
                # this is a picture for the owner, not a health row: restore the colonists and finish the advance once
                # (live 2026-10-19: a raid-wounded colonist's blood loss killed the staging before the owner save)
                self.notes.append("governor stop while staging, colonists restored: %s" % str(ex)[:160])
                for c in (self.w.call("rimworld/list_colonists") or {}).get("colonists") or []:
                    if c.get("pawnId") and not c.get("dead"):
                        hr = self.w.call("jawa/pawn_health", pawn=c["pawnId"], action="healAll", confirmDestructive=True)
                        if not (isinstance(hr, dict) and hr.get("success")):
                            self.notes.append("healAll refused for %s: %s" % (c["pawnId"], str(hr)[:120]))
                        self.w.call("jawa/pawn_need", pawn=c["pawnId"], action="need", need="Food", level=1.0)
                self.w.ticks(n)


# ------------------------------------------------------------------ rows
def row_ladders(s, L):
    s.say("ROW ladders: 4 pits, lowered on wall k (N,E,S,W), raised on the opposite wall")
    cap = []
    ox, oz = L["ladders"]
    for r in range(4):
        pit = (ox + r * 5, oz)                      # 3-wide pits, 2 squares apart (dense)
        s.pit(pit, 3, 3)
        low, high = wall_cell(pit, r), wall_cell(pit, opposite(r))
        a = s.place("RM_Ladder", low, rot=r)
        b = s.place("RM_Ladder", high, rot=opposite(r))
        s.raise_ladder(high, True)
        cap.append(s.station("ladders", (pit[0], pit[1], 3, 3), "%s pit: lowered on %s wall (game reads %s), raised on %s wall (reads %s)" % (
            ROT[r], ROT[r], ROT[a["rot_read"]] if isinstance(a["rot_read"], int) else "?", ROT[opposite(r)],
            ROT[b["rot_read"]] if isinstance(b["rot_read"], int) else "?"), short="ladder low %s" % ROT[r][0]))
    return cap


def row_spikes(s, L):
    s.say("ROW spikes: dry pit and pit with 1 m of water")
    ox, oz = L["spikes"]
    cap = []
    for k, (wet, label) in enumerate(((0, "dry pit floor"), (2, "under 1 m of water"))):
        pit = (ox + k * 5, oz)
        s.pit(pit, 3, 3)
        for i in range(3):
            for j in range(3):
                s.place("RM_Spikes", (pit[0] + i, pit[1] + j))
        if wet:
            for i in range(3):
                for j in range(3):
                    s.fill((pit[0] + i, pit[1] + j), wet)
        cap.append(s.station("spikes", (pit[0], pit[1], 3, 3), "RM_Spikes %s" % label, short="spikes " + ("wet" if wet else "dry")))
    return cap


GATE_POSES = (("EW", 1), ("EW", 3), ("NS", 0), ("NS", 2), ("EW", 1))   # last one is held open


def row_gates(s, L, door, key, stuff):
    ox, oz = L[key]
    s.say("ROW gates: %s (E-W and N-S canals, four facings closed + one held open)" % door)
    cap = []
    for k, (axis, rot) in enumerate(GATE_POSES):
        held = k == 4
        x0 = ox + k * 7
        cells = [(x0 + i, oz + 3) for i in range(5)] if axis == "EW" else [(x0 + 1, oz + i) for i in range(5)]
        for c in cells:
            s.dig(c, 1)
        for i in (0, 1, 3, 4):
            s.fill(cells[i], 1)
        mid = cells[2]
        r = s.place(door, mid, rot=rot, stuff=stuff)
        label = "%s canal, %s, facing %s%s" % (axis, door, ROT[rot], ", HELD OPEN" if held else ", closed")
        if held:
            s.say("  hold open %s (Hold open button + a colonist walks in)" % (mid,))
            if not s.dry:
                try:
                    import water_scenes_walk as m
                    label += " [" + str(m.gate_open(s.w, mid))[:60] + "]"
                except Exception as ex:  # noqa: BLE001
                    s.notes.append("hold-open of %s at %s skipped: %s" % (door, mid, ex))
                    label += " [hold-open FAILED: closed]"
        cap.append(s.station(key, (x0, oz, 5, 5), label, short="%s %s%s" % (axis, ROT[rot][0], " OPEN" if held else "")))
    return cap


def row_shallows(s, L):
    ox, oz = L["shallows"]
    s.say("ROW shallows: 0.2 / 0.5 / 1 / 1.5 / 2 / 5 m")
    cap = []
    strip = [(ox + i, oz + 1) for i in range(5)]
    for c in strip:
        s.dig(c, 1)
    s.fill(strip[0], 1)
    s.fill(strip[1], 1)
    cap.append(s.station("shallows", (ox, oz + 1, 5, 1), "0.2 m: 5-square strip, 2 notches levelled over 5 squares", short="0.2 m"))
    x = ox + 7
    for metres, notches in SHALLOWS:
        pit = (x, oz)
        s.pit(pit, 3, notches)
        for i in range(3):
            for j in range(3):
                s.fill((pit[0] + i, pit[1] + j), notches)
        cap.append(s.station("shallows", (x, oz, 3, 3), "%s m: pit %d deep, %d notches" % (metres, notches, notches), short="%s m" % metres))
        x += 5
    s.pit((x, oz), 3, 2)            # the sixth look: a dry 1 m hole, no water
    cap.append(s.station("shallows", (x, oz, 3, 3), "dry: 1 m hole, no water", short="dry"))
    # The exact-level solver grows a body's dry rim ONE square per flow pulse (RM_FlowKernel.ExactDomain adds a dry square
    # only beside a wet one), so 2 notches in squares 0-1 read 0.33/0.33/0.33/0/0 after one pulse and level at 0.2 m after
    # three (measured live 2026-10-18). The 2026-10-18 run read after 300 ticks = one pulse and reported a false unlevel.
    pulses = len(strip) + 2
    if s.dry:
        s.ticks(250 * pulses)
    else:
        s.ticks(s.w.interval() * pulses)
        got = []
        for c in strip:
            rd = s.w.readout(c)
            got.append(None if rd is None else rd.get("dl"))
            s.notes.append("0.2 m strip %s readout %s" % (c, rd))
        if None in got or len(set(got)) != 1:
            s.notes.append("0.2 m strip NOT LEVEL after %d pulses: dl %s" % (pulses, got))
    return cap


def row_sprinklers(s, L):
    ox0, oz = L["sprinklers"]
    oz += 6                       # battery sits 4 south of the tank
    s.say("ROW sprinklers: four looks, pipe restyled before the head is built")
    cap = []
    for k, look in enumerate(LOOKS):
        ox = ox0 + k * 8                # a net is 6 wide (tank 2, pipe 4): 2 squares between nets (owner: dense)
        s.place("RM_LiquidTank", (ox, oz))
        for x in range(ox + 2, ox + 6):
            s.place("RM_UniversalPipe", (x, oz))
        s.place("RM_LiquidPump", (ox + 3, oz))
        s.place("PowerConduit", (ox + 3, oz - 1))
        s.place("PowerConduit", (ox + 3, oz - 2))
        s.place("Battery", (ox + 3, oz - 4))
        s.say("  battery_set charge battery at %s to 100%%" % ((ox + 3, oz - 4),))
        s.say("  fill tank %s with RM_Liquid_FreshWater 100000 dL (ProofTank)" % ((ox, oz),))
        s.say("  Choose style %s on the whole pipe run via the pipe's gizmo (objects_sheet.choose_look run=True)" % look)
        if not s.dry:
            import objects_sheet as O
            import fw_walk_common as C
            # jawa/battery_set, never jawa/gss_stage: gss_stage needs Gimme Some Slack loaded, refused on the minimal list,
            # and its refusal went unread, so the 2026-10-18 map shipped four dead batteries, four unpowered pumps, no spray.
            bat = [t for t in C.list_things(s.w, ["Battery"], (ox + 1, oz - 6, 5, 5)) if t["cell"] == (ox + 3, oz - 4)]
            br = s.w.call("jawa/battery_set", thing=bat[0]["raw"].get("id"), mode="setPct", value=1.0) if bat else {}
            if not (br or {}).get("storedEnergyPctAfter"):
                s.notes.append("battery for net %d NOT charged (%s): its pump will show no power" % (k, str(br)[:120]))
            s.store((ox, oz))
            got = O.choose_look(s.w, (ox + 2, oz), look, run=True)
            if got != look:
                s.notes.append("pipe look for net %d: asked %s, game reads %s" % (k, look, got))
        s.place("RM_SprinklerHead", (ox + 5, oz))
        cap.append(s.station("sprinklers", (ox, oz - 4, 6, 6), "sprinkler %s: head at %s (look read back in notes)" % (look, (ox + 5, oz)),
                             short=look))
    s.ticks(PULSE + 300)            # one hourly pulse so every head is mid-spray
    return cap


# ------------------------------------------------------------------ hoses vs pipes (HOSE_PIPE_WALK_JUDGE_GIRTH_IN_GAME)
DIRS = {"N": (0, 1), "E": (1, 0), "S": (0, -1), "W": (-1, 0)}
SIDE_FOR = {"N": "E", "E": "S", "S": "W", "W": "S"}       # a free side for the power conduit (pipes/hoses use the others)
HOSE_REACH = 11                                           # pump cell -> hose end cell, in the hose direction


def _edge_anchor(edge, d, size=2):
    """Anchor cell of a size x size thing that sits just beyond `edge` (the last open cell) in direction d (multi-cell things
    spawn CENTRED on the anchor and occupy anchor..anchor+size-1 for an even size)."""
    return (edge[0] + 1 if d[0] > 0 else edge[0] - (size - 1) - 1 if d[0] < 0 else edge[0],
            edge[1] + 1 if d[1] > 0 else edge[1] - (size - 1) - 1 if d[1] < 0 else edge[1])


def _reel_anchor(pump, d):
    """2x2 reel touching the pump on side d."""
    return (pump[0] + 1 if d[0] > 0 else pump[0] - 2 if d[0] < 0 else pump[0],
            pump[1] + 1 if d[1] > 0 else pump[1] - 2 if d[1] < 0 else pump[1])


def hose_pump(s, pump, side_in, kind_in, side_out, kind_out, pipe_len=6, out_target=None, out_size=2):
    """One RM_LiquidPump with its INPUT (kind_in = pipe|hose) on side_in and OUTPUT (kind_out) on side_out, powered from a free
    side. Input: a filled 2x2 tank at the far end. Output: a 2x2 tank at the far end, or `out_target` (cell) when the caller
    supplies the consumer. Returns dict of the notable cells."""
    di, do = DIRS[side_in], DIRS[side_out]
    s.place("RM_LiquidPump", pump)
    cells = dict(pump=pump, reels=[], ends=[], pipes=[], tanks=[])
    free = next(k for k in ("S", "W", "N", "E") if k not in (side_in, side_out))
    df = DIRS[free]
    s.place("PowerConduit", (pump[0] + df[0], pump[1] + df[1]))
    s.place("PowerConduit", (pump[0] + 2 * df[0], pump[1] + 2 * df[1]))
    bat = (pump[0] + 4 * df[0], pump[1] + 4 * df[1])
    s.place("Battery", bat)
    for kind, d, out in ((kind_in, di, False), (kind_out, do, True)):
        consumer = out and out_target is not None          # the caller supplies the far end of the output
        if kind == "pipe":
            far = None
            for k in range(1, pipe_len + 1):
                far = (pump[0] + d[0] * k, pump[1] + d[1] * k)
                s.place("RM_UniversalPipe", far)
                cells["pipes"].append(far)
            if not consumer:
                tk = _edge_anchor(far, d)
                s.place("RM_LiquidTank", tk)
                cells["tanks"].append(tk)
                if not out:
                    s.store(tk)
        else:
            reel = _reel_anchor(pump, d)
            s.place("RM_HoseReel", reel)
            end = (pump[0] + d[0] * HOSE_REACH, pump[1] + d[1] * HOSE_REACH)
            if not consumer:
                tk = _edge_anchor(end, d)
                s.place("RM_LiquidTank", tk)
                cells["tanks"].append(tk)
                if not out:
                    s.store(tk)
            cells["reels"].append((reel, end))
    cells["battery"] = bat
    return cells


def hose_lay_all(s, cells_list):
    for cells in cells_list:
        s.charge(cells["battery"])
    for cells in cells_list:
        for reel, end in cells["reels"]:
            r = s.hp("lay:%d,%d,%d,%d" % (reel + end))
            if not r.get("success", True):
                s.notes.append("hose lay %s -> %s refused: %s" % (reel, end, r.get("reason") or r))


def row_hoses(s, L):
    hx, hz = L["hoses"]
    s.say("ROW hoses: pipe vs hose girth (pump pipe+hose, tank/tap/sprinkler each fed by both, 6-square side-by-side run)")
    cap = {}
    nets = []
    scenes = {}
    # A: pipe W in, hose E out
    pa = (hx + 10, hz + 4)
    a = hose_pump(s, pa, "W", "pipe", "E", "hose")
    nets.append(a)
    scenes["pump_pipeW_hoseE"] = (pa, (hx + 1, hz + 1, 26, 10), (pa[0] - 4, pa[1] - 3, 12, 8), (pa[0] + 1, pa[1] - 1), "pump: pipe W (input), hose E (output)")
    # C: hose W in, hose E out
    pc = (hx + 14, hz + 16)
    c = hose_pump(s, pc, "W", "hose", "E", "hose")
    nets.append(c)
    scenes["pump_hoses_W_E"] = (pc, (hx + 1, hz + 12, 28, 10), (pc[0] - 4, pc[1] - 3, 12, 8), (pc[0] + 1, pc[1] - 1), "pump: hose W (input), hose E (output)")
    # B: pipe N in, hose S out (vertical)
    pb = (hx + 40, hz + 14)
    b = hose_pump(s, pb, "N", "pipe", "S", "hose")
    nets.append(b)
    scenes["pump_pipeN_hoseS"] = (pb, (hx + 34, hz, 10, 24), (pb[0] - 4, pb[1] - 4, 8, 12), (pb[0] - 2, pb[1] + 1), "pump: pipe N (input), hose S (output)")
    # D: one consumer fed by a pipe from one pump (W) and a hose from another (E)
    for k, (d, size, label) in enumerate((("RM_LiquidTank", 2, "2x2 tank"), ("RM_LiquidTap", 1, "bleed well"), ("RM_SprinklerHead", 1, "sprinkler head"))):
        t = (hx + 16, hz + 28 + 10 * k)
        s.place(d, t)
        p1, p2 = (t[0] - 6, t[1]), (t[0] + 14, t[1])
        n1 = hose_pump(s, p1, "W", "pipe", "E", "pipe", pipe_len=5, out_target=t)
        # pump 1's output pipe runs t.x-5 .. t.x-1, ending beside the consumer; its input tank is at the far west
        n2 = hose_pump(s, p2, "E", "pipe", "W", "hose", out_target=t)
        nets += [n1, n2]
        # the consumer's west edge is t.x, east edge t.x+size-1: re-aim pump 2's hose to the cell beside the consumer
        n2["reels"] = [(r, (t[0] + size, t[1])) for r, _e in n2["reels"]]
        key = "%s_pipeW_hoseE" % d
        scenes[key] = (t, (hx, t[1] - 5, 42, 9), (t[0] - 4, t[1] - 3, 12 if size == 2 else 10, 8), (t[0], t[1] - 1), "%s: pipe on W, hose on E" % label)
    # E: 6 squares of pipe (z = ez) beside 6 squares of hose (z = ez + 1), same x span
    ez = hz + 60
    s.place("RM_LiquidTank", (hx + 3, ez - 1))
    s.store((hx + 3, ez - 1))
    for x in range(hx + 5, hx + 11):
        s.place("RM_UniversalPipe", (x, ez))
    s.place("RM_LiquidTank", (hx + 11, ez - 1))
    pe = (hx, ez + 1)
    e = hose_pump(s, pe, "W", "pipe", "E", "hose", pipe_len=2)
    nets.append(e)
    scenes["pipe_beside_hose_6"] = (pe, (hx - 6, ez - 4, 24, 9), (hx + 3, ez - 2, 12, 5), (hx + 7, ez + 3), "6 squares of pipe (south) beside 6 of hose (north)")
    s.ticks(2)
    hose_lay_all(s, nets)
    s.ticks(700)                    # a pump cycle + discovery + settle: hoses plump, pipes tint
    if not s.dry:
        cen = s.hp("census")
        s.notes.append("hose census after settle: %s" % str(cen)[:300])
    cap["scenes"] = scenes
    cap["lines"] = [s.station("hoses", v[2], "%s -- %s" % (k, v[4]), lane=i, short=k) for i, (k, v) in enumerate(scenes.items())]
    return cap


def row_picks(s, L):
    """--only picks (FOUNDRY 2026-10-23, the owner's FlowWorks look list): a pipe faucet fed by a filled tank, a 4 m pit with
    guardrails on two lips (bare lips beside them), a dug canal joining a vanilla WaterDeep lake at 2.5 m of water and one
    joining a dug pond at 1 m (CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES L3: equal depth, one colour), and a 2 m canal holding 1 m
    of water (WATER_DEPTH_RESKIN wall band: the dry face between water and lip)."""
    px, pz = L["picks"]
    s.say("ROW picks: faucet, guardrail pit, canal vs lake (2.5 m, 1 m), wall depth band")
    cap = []
    # 1 faucet: 2x2 tank, 4 pipe squares east, faucet on the last
    s.place("RM_LiquidTank", (px, pz + 1))
    s.store((px, pz + 1))
    for x in range(px + 2, px + 7):
        s.place("RM_UniversalPipe", (x, pz + 1))
    s.place("RM_PipeFaucet", (px + 6, pz + 1))
    s.pawn((px + 6, pz), "at the faucet")
    cap.append(s.station("picks", (px, pz, 7, 2), "faucet: tank -> 5 pipe squares -> RM_PipeFaucet on the last", short="faucet"))
    # 2 guardrail: 5x5 pit 4 m deep, rails on the north and east lips, south and west lips bare
    gx, gz = px + 11, pz
    s.pit((gx, gz), 5, 8)
    for i in range(-1, 6):
        s.place("RM_PitGuardrail", (gx + i, gz + 5), stuff="Steel")
    for j in range(0, 5):
        s.place("RM_PitGuardrail", (gx + 5, gz + j), stuff="Steel")
    s.pawn((gx + 2, gz + 6), "behind the rail")
    s.pawn((gx + 2, gz - 1), "bare lip")
    cap.append(s.station("picks", (gx - 1, gz - 1, 7, 7), "guardrail: 4 m pit, steel rails on N and E lips, S and W lips bare", short="guardrail"))
    # 3a canal into a painted vanilla lake, 2.5 m of water both sides
    lx, lz = px + 21, pz
    s.say("  paint WaterDeep lake %d,%d 8x6" % (lx, lz))
    if not s.dry:
        s.chk("paint lake", s.w.call("jawa/set_terrain_batch", ops="WaterDeep:%d,%d,8,6" % (lx, lz)))
    for x in range(lx + 8, lx + 15):
        s.dig((x, lz + 3), 5, 5)
    cap.append(s.station("picks", (lx, lz, 15, 6), "canal 2.5 m of water joining a vanilla WaterDeep lake (one colour?)", short="canal+lake"))
    # 3b canal into a dug pond, 1 m of water both sides
    dx, dz = px + 21, pz + 8
    for i in range(6):
        for j in range(5):
            s.dig((dx + i, dz + j), 2, 2)
    for x in range(dx + 6, dx + 13):
        s.dig((x, dz + 2), 2, 2)
    cap.append(s.station("picks", (dx, dz, 13, 5), "canal 1 m of water joining a dug pond at 1 m (one colour?)", lane=1, short="canal+pond"))
    # 4 wall band: 3-wide canal 2 m deep with 1 m of water (the dry face above the water)
    bx, bz = px + 38, pz + 1
    for x in range(bx, bx + 10):
        for j in range(3):
            s.dig((x, bz + j), 4, 2)
    cap.append(s.station("picks", (bx, bz, 10, 3), "wall band: 2 m canal, 1 m of water: the face between water and lip", short="wall band"))
    s.ticks(600)
    return cap


# ------------------------------------------------------------------ FlowWorks north-star bars (flowworks_bars_sitting_2026-10-18.md)
SUSP = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
TRENCH = "RimMandrake.FlowWorks.RM_TrenchCover"


def row_bars_joint(s, L):
    bx, bz = L["bars"]
    s.say("ROW bars_joint: 1 m of water in 1/2/4 m holes (north); 0.5/1/2 m of water in 4 m holes (south)")
    cap = []
    for k, depth_m in enumerate((1, 2, 4)):                       # 1 m water = 2 notches
        pit = (bx + k * 5, bz + 6)
        s.pit(pit, 3, int(depth_m * 2), 2)
        cap.append(s.station("bars_joint", (pit[0], pit[1], 3, 3), "1 m of water in a %d m hole" % depth_m, short="1m in %dm" % depth_m))
    for k, wet_m in enumerate((0.5, 1, 2)):
        pit = (bx + k * 5, bz)
        s.pit(pit, 3, 8, int(wet_m * 2))
        cap.append(s.station("bars_joint", (pit[0], pit[1], 3, 3), "%s m of water in a 4 m hole" % wet_m, lane=1, short="%sm in 4m" % wet_m))
        if wet_m >= 2:
            s.pawn((pit[0] + 1, pit[1] + 1), "swims: 2 m of water")
    s.pawn((bx + 11, bz + 7), "swims in 1 m water in a 4 m hole")
    return cap


def row_bars_dry(s, L):
    bx, bz = L["bars"]
    s.say("ROW bars_dry: dry holes 0.5 / 1 / 1.5 / 2 / 4 / 8 m, a colonist in each")
    cap = []
    for k, m in enumerate((0.5, 1, 1.5, 2, 4, 8)):
        pit = (bx + k * 5, bz + 14)
        s.pit(pit, 3, int(m * 2))
        s.pawn((pit[0] + 1, pit[1] + 1), "stands in a %s m hole" % m)
        cap.append(s.station("bars_dry", (pit[0], pit[1], 3, 3), "dry %s m hole, colonist standing in it" % m, short="dry %s m" % m))
    return cap


def row_bars_trench(s, L):
    bx, bz = L["bars"]
    s.say("ROW bars_trench: waist-deep (1 m) and chest-deep (1.5 m) colonist, a shooter 8 squares east on flat ground")
    cap = []
    for k, (m, what) in enumerate(((1.0, "waist-deep"), (1.5, "chest-deep"))):
        pit = (bx + k * 12, bz + 22)        # pit + shooter 9 east = 10 wide: the old 5 pitch put shooter 1 inside station 2
        s.pit(pit, 3, int(m * 2))
        tid = s.pawn((pit[0] + 1, pit[1] + 1), what)
        sid = s.pawn((pit[0] + 9, pit[1] + 1), "shooter")
        cap.append(s.station("bars_trench", (pit[0], pit[1], 10, 3), "%s colonist (%s m hole) with a shooter 8 squares east" % (what, m), short=what))
        if not s.dry and tid is not None and sid is not None:
            ok, txt = s.proof(TRENCH, "ProofTrenchCover", "%s;%s" % (tid, sid))
            s.notes.append("trench cover %s: %s" % (what, (txt or "")[:160]))
    return cap


def row_bars_access(s, L):
    bx, bz = L["bars"]
    s.say("ROW bars_access: portable ladder (2 m pit, 4 m wall), climbing gear on the ground and worn, a concealed pit")
    cap = []
    p2, p4, pg, pn, pc = (bx, bz + 30), (bx + 5, bz + 30), (bx + 10, bz + 30), (bx + 15, bz + 30), (bx + 20, bz + 30)
    s.pit(p2, 3, 4)
    s.place("RM_LadderPortable", (p2[0] + 1, p2[1] + 2), rot=0)
    cap.append(s.station("bars_access", (p2[0], p2[1], 3, 3), "portable ladder leaning in a 2 m pit", short="ladder 2m"))
    s.pit(p4, 3, 8)
    s.place("RM_LadderPortable", (p4[0] + 1, p4[1] + 2), rot=0)
    cap.append(s.station("bars_access", (p4[0], p4[1], 3, 3), "portable ladder against a 4 m wall (too short: lies flat)", short="ladder 4m"))
    s.pit(pg, 3, 8)
    s.pawn((pg[0] + 1, pg[1] + 1), "WEARS climbing gear, 4 m sheer pit", wear="RM_ClimbingGear")
    cap.append(s.station("bars_access", (pg[0], pg[1], 3, 3), "climbing gear worn: colonist in a 4 m sheer pit", short="gear worn"))
    s.pit(pn, 3, 8)
    s.pawn((pn[0] + 1, pn[1] + 1), "no gear, 4 m sheer pit (control)")
    cap.append(s.station("bars_access", (pn[0], pn[1], 3, 3), "no gear: control colonist in a 4 m sheer pit", short="no gear"))
    s.item("RM_ClimbingGear", (pc[0], pc[1] + 1))
    cap.append(s.station("bars_access", (pc[0], pc[1] + 1, 1, 1), "climbing gear item on the ground", short="gear item"))
    s.pit((pc[0] + 3, pc[1]), 3, 4)
    s.place("RM_PitCover_PlankLattice", (pc[0] + 4, pc[1] + 1))
    cap.append(s.station("bars_access", (pc[0] + 3, pc[1], 3, 3), "concealed pit (planks) over a 2 m pit", short="planks"))
    return cap


BRIDGE_PITCH = 8          # a 6-square span (anchor, 4 over the pit, anchor): 2 squares between bridges (owner: dense)


def span_pit(s, x0, z, depth=8):
    """The pit a bridge spans (owner 2026-10-24: "Need to see these bridges over pits"): 4 squares long under the span,
    3 wide (the deck row and one either side), so the bridge reads as crossing a pit, not a one-square trench."""
    for x in range(x0 + 1, x0 + 5):
        for dz in (-1, 0, 1):
            s.dig((x, z + dz), depth)


def row_bars_bridges(s, L):
    bx, bz = L["bars"]
    s.say("ROW bars_bridges: rope/timber/steel/heavy, railings on (north lane) and off (south lane), concealed pit beside")
    cap = []
    for k, tier in enumerate(("rope", "timber", "steel", "heavy")):
        x0 = bx + k * BRIDGE_PITCH
        for lane, rails in ((0, "on"), (1, "off")):
            z = bz + 44 - lane * 4          # RimWorld z grows NORTH: lane 0 (railings on) is the north lane
            span_pit(s, x0, z)
            s.proof(SUSP, "ProofBuild", "%d,%d;%d,%d;%s;god" % (x0, z, x0 + 5, z, tier))
            s.proof(SUSP, "ProofRails", "%d,%d;%s" % (x0 + 2, z, rails))
            cap.append(s.station("bars_bridges", (x0, z - 1, 6, 3), "%s suspension bridge over a 4 m pit, railings %s (%s lane)" % (
                tier, rails, "north" if lane == 0 else "south"), lane=lane, short="%s rails %s" % (tier, rails)))
    px = bx + 4 * BRIDGE_PITCH
    s.pit((px, bz + 39), 3, 4)
    s.place("RM_PitCover_PlankLattice", (px + 1, bz + 40))
    cap.append(s.station("bars_bridges", (px, bz + 39, 3, 3), "concealed pit (planks, east end) beside the bridges: a concealed pit "
                         "passes for ground, a bridge does not", short="planks"))
    return cap


def row_bars_bridge_kinds(s, L):
    bx, bz = L["bars"]
    s.say("ROW bars_bridge_kinds: grated steel/heavy, steel/heavy jetties, steel bridge in four looks")
    cap = []
    z = bz + 48
    for k, tier in enumerate(("steelgrated", "heavygrated")):
        x0 = bx + k * BRIDGE_PITCH
        span_pit(s, x0, z)
        s.proof(SUSP, "ProofBuild", "%d,%d;%d,%d;%s;god" % (x0, z, x0 + 5, z, tier))
        cap.append(s.station("bars_bridge_kinds", (x0, z - 1, 6, 3), "%s suspension bridge over a 4 m pit" % tier, short=tier))
    z = bz + 52
    for k, tier in enumerate(("steel", "heavy")):
        x0 = bx + k * BRIDGE_PITCH
        span_pit(s, x0, z)
        s.proof(SUSP, "ProofJetty", "%d,%d;%d,%d;%s;god" % (x0, z, x0 + 4, z, tier))
        cap.append(s.station("bars_bridge_kinds", (x0, z - 1, 6, 3), "%s jetty reaching out over a 4 m pit" % tier, lane=1,
                             short="%s jetty" % tier))
    for k, look in enumerate(("Scrapper", "Industrial", "Modern", "Futuristic")):
        x0 = bx + k * BRIDGE_PITCH
        z = bz + 56
        span_pit(s, x0, z)
        s.proof(SUSP, "ProofLook", "%s;%d,%d;%d,%d" % (look, x0, z, x0 + 5, z))
        cap.append(s.station("bars_bridge_kinds", (x0, z - 1, 6, 3), "steel bridge over a 4 m pit, %s look, railings on" % look, lane=2,
                             short="steel %s" % look))
    return cap


ROWS = dict(picks=row_picks, bars_joint=row_bars_joint, bars_dry=row_bars_dry, bars_trench=row_bars_trench, bars_access=row_bars_access,
            bars_bridges=row_bars_bridges, bars_bridge_kinds=row_bars_bridge_kinds, hoses=row_hoses, ladders=row_ladders, spikes=row_spikes, shallows=row_shallows, sprinklers=row_sprinklers)


# ------------------------------------------------------------------ driver
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--mock", action="store_true", help="FakeGame instead of the bridge (needs no game)")
    ap.add_argument("--only", default="")
    ap.add_argument("--origin", default=None, help="X,Z (default 100,100 moved to fit the map; an explicit origin that does not fit is refused)")
    ap.add_argument("--save-name", default=None)
    ap.add_argument("--no-save", action="store_true")
    ap.add_argument("--no-shots", action="store_true")
    ap.add_argument("--any-biome", action="store_true", help="stage on a biome outside WATER_TRUE_BIOMES (the swatch still judges)")
    a = ap.parse_args(argv)
    only = [x for x in a.only.split(",") if x] or list(ALL_ROWS)
    for row in only:        # before any bridge call: an unknown row must not clear a site first
        if row not in ALL_ROWS + OPT_ROWS:
            ap.error("unknown row %r (rows: %s)" % (row, ", ".join(ALL_ROWS + OPT_ROWS)))
    msize = DEFAULT_MAP if a.dry_run else None
    ox, oz = map(int, (a.origin or "100,100").split(","))
    L = layout(ox, oz)
    name = a.save_name or "FLOWWORKS_OWNER_REVIEW_%s" % time.strftime("%Y%m%d_%H%M")
    w = None
    if not a.dry_run:
        import fw_walk_common as C
        # a mock run writes synthetic pictures: its own folder, so it never overwrites a live run's evidence (2026-10-23:
        # a --mock rehearsal replaced the grey-water row_shallows/overview captures WATER_LOOK_DIAGNOSE cited)
        out = os.path.join(C.REPO, "Transient", "owner_review_stage_mock" if a.mock else "owner_review_stage")
        w = C.make_walk(a, out)
    s = Stage(w, a.dry_run)
    if msize is None:
        msize = C.map_size(w)
    try:
        fit = fit_origin(ox, oz, msize)
    except ValueError as e:
        print("REFUSED: %s" % e)
        return 4
    if fit != (ox, oz):
        if a.origin:
            print("REFUSED: origin %s puts the site off the %dx%d map (it fits at %s); nothing was staged" % ((ox, oz), msize[0], msize[1], fit))
            return 4
        ox, oz = fit
        L = layout(ox, oz)
        s.notes.append("origin moved to %s to fit the %dx%d map" % (fit, msize[0], msize[1]))
    s.say("OWNER REVIEW MAP %s  origin %s  rect %s  rows %s" % (name, (ox, oz), L["rect"], only))
    if not a.dry_run and not a.mock:
        mi = s.w.call("jawa/map_info") or {}
        biome = mi.get("mapBiome") or (mi.get("tileInfo") or {}).get("biome")
        s.notes.append("map biome %s" % biome)
        if biome not in WATER_TRUE_BIOMES and not a.any_biome:
            print("REFUSED: map biome %s is not one where water is known to draw right (%s); load a vanilla-biome map "
                  "(e.g. a TemperateForest quicktest) or pass --any-biome" % (biome, ", ".join(WATER_TRUE_BIOMES)))
            return 3
    if not a.dry_run:
        s.chk("kill_hostiles", s.w.call("jawa/kill_hostiles"))
        s.chk("weather_set Clear", s.w.call("jawa/weather_set", weather="Clear", lockWeather=True))
        if [r for r in only if r not in OPT_ROWS + BARS_ROWS]:
            s.w.clear_site(L["rect"])
        if "picks" in only:
            s.w.clear_site(L["picks_rect"])
        if [r for r in only if r in BARS_ROWS]:
            s.w.clear_site(L["bars_rect"])
        if "hoses" in only:
            s.w.clear_site(L["hoses_rect"])
    else:
        s.say("  kill hostiles; Clear weather locked")
        if [r for r in only if r not in OPT_ROWS + BARS_ROWS]:      # the same four tests as the live branch above
            s.say("  clear_site %s" % (L["rect"],))
        if "picks" in only:
            s.say("  clear_site %s (picks)" % (L["picks_rect"],))
        if [r for r in only if r in BARS_ROWS]:
            s.say("  clear_site %s (bars)" % (L["bars_rect"],))
        if "hoses" in only:
            s.say("  clear_site %s (hoses)" % (L["hoses_rect"],))
    caps = {}
    for row in only:
        if row not in ALL_ROWS + OPT_ROWS:
            ap.error("unknown row %r (rows: %s)" % (row, ", ".join(ALL_ROWS + OPT_ROWS)))
        if row == "gates":
            caps["gates_sluice"] = row_gates(s, L, "RM_Sluice", "gates_sluice", "WoodLog")
            caps["gates_grate"] = row_gates(s, L, "RM_SecurityGrateDoor", "gates_grate", "Steel")
        else:
            caps[row] = ROWS[row](s, L)
    off = offmap_problems(s.stations, msize)
    if off:        # backstop: fit_origin above already refuses a site that does not fit; an off-map station is never a note
        print("REFUSED (not saved): %d station(s) off the map: %s" % (len(off), "; ".join(off[:3])))
        return 4
    s.labels()                       # every station numbered in the world, the same number as its caption line
    for p in layout_problems(s.stations, rows=ALL_ROWS):
        s.notes.append("LAYOUT: " + p)
    sw = swatch_rect(ox, oz)
    if [r for r in only if r not in OPT_ROWS + BARS_ROWS]:
        s.say("SWATCH: vanilla %s %s, photographed and measured before the save (water must read blue over red)" % (SWATCH, sw))
        if not a.dry_run:
            s.chk("swatch paint", s.w.call("jawa/set_terrain_batch", ops="%s:%d,%d,%d,%d" % ((SWATCH,) + sw)))
    else:
        sw = None
    s.say("FINISH: kill hostiles, Clear weather, step toward midday, frame, shoot, save '%s'" % name)
    if a.dry_run:
        if "hoses" in caps:
            s.say("SHOTS (per scene, wide + close) -> Transient/fw_hoses_walk/FlowWorks_HosePipeWalk_%s_<scene>_{wide,close}.png" % time.strftime("%Y%m%d"))
            for k, v in caps["hoses"]["scenes"].items():
                s.say("  scene %s wide %s close %s colonist %s" % (k, v[1], v[2], v[3]))
        for n in s.notes:
            print("NOTE:", n)
        print("DRY RUN: %d plan lines, %d stations, no bridge touched." % (len(s.plan), len(s.stations)))
        return 0
    s.chk("kill_hostiles (final)", s.w.call("jawa/kill_hostiles"))
    s.chk("weather_set Clear (final)", s.w.call("jawa/weather_set", weather="Clear", lockWeather=True))
    hour = None
    # daytime: approximate local hour from ticksAbs (ignores longitude); step to 10:00-14:00. Judge it in the picture.
    for _ in range(12):
        t = s.w.call("jawa/time_clock") or {}
        if t.get("ticksAbs") is None:       # an unread clock is not midnight: stop stepping, say so
            hour = None
            break
        hour = (t["ticksAbs"] % 60000) / 2500.0
        if 10 <= hour <= 14:
            break
        s.w.ticks(2000)
    s.notes.append("approx hour %s (ticksAbs mod day, longitude ignored)" % ("UNMEASURED: time_clock gave no ticksAbs"
                                                                             if hour is None else "%.1f" % hour))
    import fw_walk_common as C
    shots = []
    if "hoses" in caps:
        import shutil
        hdir = os.path.join(C.REPO, "Transient", "fw_hoses_walk_mock" if a.mock else "fw_hoses_walk")
        os.makedirs(hdir, exist_ok=True)
        day = time.strftime("%Y%m%d")
        for scene, (pump, wide, close, who, label) in caps["hoses"]["scenes"].items():
            s.colonist(who)
            for kind, rect in (("wide", wide), ("close", close)):
                png = C.snap(w, "hoses_%s_%s" % (scene, kind), rect)
                if png:
                    dst = os.path.join(hdir, "FlowWorks_HosePipeWalk_%s_%s_%s.png" % (day, scene, kind))
                    shutil.copyfile(png, dst)
                    shots.append(dst)
        over = C.snap(w, "hoses_overview", L["hoses_rect"])
        if over:
            dst = os.path.join(hdir, "FlowWorks_HosePipeWalk_%s_overview.png" % day)
            shutil.copyfile(over, dst)
            shots.append(dst)
    for key, title in (("ladders", "Ladders: lowered (wall k) + raised (opposite)"), ("spikes", "RM_Spikes dry and under 1 m"),
                       ("gates_sluice", "RM_Sluice, 4 facings + held open"), ("gates_grate", "RM_SecurityGrateDoor, 4 facings + held open"),
                       ("shallows", "Water ladder 0.2 / 0.5 / 1 / 1.5 / 2 / 5 m"), ("sprinklers", "Sprinklers: Futuristic / Industrial / Modern / Scrapper")):
        if key not in caps or key == "hoses" or key in BARS_ROWS:
            continue
        rect = row_rect(s.stations, key)          # the row's stations and their number labels, no wider
        png = C.snap(w, "row_" + key, rect)
        if png:
            shots.append(C.label_image(png, os.path.join(os.path.dirname(png), "row_%s_labelled.png" % key), title, "", caps[key]))
    if "picks" in caps:
        png = C.snap(w, "row_picks", L["picks_rect"])
        if png:
            shots.append(C.label_image(png, os.path.join(os.path.dirname(png), "row_picks_labelled.png"), "picks", "", caps["picks"]))
    for key in BARS_ROWS:
        if key in caps:
            png = C.snap(w, key, bars_row_rect(L, key))
            if png:
                shots.append(C.label_image(png, os.path.join(os.path.dirname(png), "row_%s_labelled.png" % key), key, "", caps[key]))
    over = C.snap(w, "overview", L["rect"])
    if over:
        shots.append(over)
    water_ok = None
    if sw and not a.no_shots:
        png = C.snap(w, "water_swatch", (sw[0] - 1, sw[1] - 1, sw[2] + 2, sw[3] + 2))
        rgb = centre_rgb(png) if png and not a.mock else None     # a synthetic mock picture is no water read
        water_ok = water_verdict(rgb)
        s.notes.append("water swatch %s mean RGB %s -> %s" % (sw, rgb, {True: "reads as water", False: "GREY/BROWN: water "
                       "does not draw right on this map", None: "UNMEASURED"}[water_ok]))
        if png:
            shots.append(png)
    s.w.frame(L["rect"])            # clear_ui + whole-site zoom (water_scenes_walk.fit_root_size)
    if water_ok is False and not a.no_save:
        s.notes.append("SAVE WITHHELD: the vanilla water swatch did not read as water (WATER_LOOK_DIAGNOSE_GREY_ON_THE_ROT); "
                       "stage again on a map where it does")
    elif not a.no_save:
        r = s.w.call("rimworld/save_game", saveName=name) or {}
        time.sleep(2.0)
        p = r.get("path")
        if not p or r.get("success") is False:
            s.notes.append("save_game gave no path / failed: %s" % str(r)[:140])
        s.say("SAVE reported %s -- VERIFY the file exists and is new (save_game has written the wrong slot before)" % (p,))
    for n in s.notes:
        print("NOTE:", n)
    for p in shots:
        print("SHOT:", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
