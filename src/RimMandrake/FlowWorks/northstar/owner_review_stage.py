"""owner_review_stage.py -- ONE FlowWorks owner-review map: stage everything, shoot it, save ONE named savegame.

  python.exe src/RimMandrake/FlowWorks/northstar/owner_review_stage.py --dry-run     # prints the plan, no bridge, no game
  python.exe src/RimMandrake/FlowWorks/northstar/owner_review_stage.py               # LIVE: bridge held, a Playing disposable map
  python.exe src/RimMandrake/FlowWorks/northstar/owner_review_stage.py --only ladders,gates --no-save
  options: --origin X,Z (default 100,100)  --save-name NAME  --no-save  --no-shots  --mock (FakeGame, seconds)
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
  bars_bridges (default) suspension bridges rope/timber/steel/heavy over 4 m pits, railings on (north lane) and off (south lane), plus a
            pit cover beside them. Built with RM_SuspensionProofs.ProofBuild "...;god" and ProofRails (the proof script's own calls).
  bars_bridge_kinds (default) the other suspension parts: steel and heavy GRATED decks, steel and heavy JETTIES, and the steel bridge in
            each of the four looks (Scrapper/Industrial/Modern/Futuristic, railings on) via ProofLook. Own lane south of bars_bridges.
  Bars with NO site (no bridge tool can pose them): wall-climb mid-climb (RM_WallClimb has no pose call; the scale-a-built-wall build
  is in progress), raiders-never-shelter (a raid-run state read), jump-into-pit hurts nobody (state read; live_session g_pit_access).
  Site for all bars_* rows: east of the hoses, rect "bars_rect" (x = origin+150, 62 wide, 76 tall); live_session's owner zone is 216 wide.
Then: kill hostiles, Clear weather locked, stepped toward midday, camera framed, shots, ONE save.

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


# ------------------------------------------------------------------ geometry (pure)
def wall_cell(pit, r, n=3):
    """Dug middle square of wall r (0=N,1=E,2=S,3=W) of an n x n pit with south-west corner `pit`."""
    px, pz = pit
    m = n // 2
    return {0: (px + m, pz + n - 1), 1: (px + n - 1, pz + m), 2: (px + m, pz), 3: (px, pz + m)}[r]


def opposite(r):
    return (r + 2) % 4


BARS_Z = dict(bars_joint=(-1, 11), bars_dry=(13, 5), bars_trench=(21, 5), bars_access=(29, 8), bars_bridges=(39, 8),
              bars_bridge_kinds=(47, 11))     # (z offset from the bars origin, height) of each bars row, from its own staging


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


# ------------------------------------------------------------------ Stage: plan + execution in ONE path
class Stage(object):
    def __init__(self, w, dry):
        self.w, self.dry, self.plan, self.notes = w, dry, [], []

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
        pit = (ox + r * 6, oz)
        s.pit(pit, 3, 3)
        low, high = wall_cell(pit, r), wall_cell(pit, opposite(r))
        a = s.place("RM_Ladder", low, rot=r)
        b = s.place("RM_Ladder", high, rot=opposite(r))
        s.raise_ladder(high, True)
        cap.append("%s pit: lowered on %s wall (game reads %s), raised on %s wall (reads %s)" % (
            ROT[r], ROT[r], ROT[a["rot_read"]] if isinstance(a["rot_read"], int) else "?", ROT[opposite(r)],
            ROT[b["rot_read"]] if isinstance(b["rot_read"], int) else "?"))
    return cap


def row_spikes(s, L):
    s.say("ROW spikes: dry pit and pit with 1 m of water")
    ox, oz = L["spikes"]
    cap = []
    for k, (wet, label) in enumerate(((0, "dry pit floor"), (2, "under 1 m of water"))):
        pit = (ox + k * 6, oz)
        s.pit(pit, 3, 3)
        for i in range(3):
            for j in range(3):
                s.place("RM_Spikes", (pit[0] + i, pit[1] + j))
        if wet:
            for i in range(3):
                for j in range(3):
                    s.fill((pit[0] + i, pit[1] + j), wet)
        cap.append("RM_Spikes %s" % label)
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
        cap.append(label)
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
    cap.append("0.2 m: 5-square strip, 2 notches levelled over 5 squares")
    x = ox + 7
    for metres, notches in SHALLOWS:
        pit = (x, oz)
        s.pit(pit, 3, notches)
        for i in range(3):
            for j in range(3):
                s.fill((pit[0] + i, pit[1] + j), notches)
        cap.append("%s m: pit %d deep, %d notches" % (metres, notches, notches))
        x += 5
    s.pit((x, oz), 3, 2)            # the sixth look: a dry 1 m hole, no water
    cap.append("dry: 1 m hole, no water")
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
        ox = ox0 + k * 14
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
        cap.append("sprinkler %s: head at %s (look read back in notes)" % (look, (ox + 5, oz)))
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
    cap["lines"] = ["%s -- %s" % (k, v[4]) for k, v in scenes.items()]
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
    cap.append("faucet: tank -> 5 pipe squares -> RM_PipeFaucet on the last")
    # 2 guardrail: 5x5 pit 4 m deep, rails on the north and east lips, south and west lips bare
    gx, gz = px + 11, pz
    s.pit((gx, gz), 5, 8)
    for i in range(-1, 6):
        s.place("RM_PitGuardrail", (gx + i, gz + 5), stuff="Steel")
    for j in range(0, 5):
        s.place("RM_PitGuardrail", (gx + 5, gz + j), stuff="Steel")
    s.pawn((gx + 2, gz + 6), "behind the rail")
    s.pawn((gx + 2, gz - 1), "bare lip")
    cap.append("guardrail: 4 m pit, steel rails on N and E lips, S and W lips bare")
    # 3a canal into a painted vanilla lake, 2.5 m of water both sides
    lx, lz = px + 21, pz
    s.say("  paint WaterDeep lake %d,%d 8x6" % (lx, lz))
    if not s.dry:
        s.chk("paint lake", s.w.call("jawa/set_terrain_batch", ops="WaterDeep:%d,%d,8,6" % (lx, lz)))
    for x in range(lx + 8, lx + 15):
        s.dig((x, lz + 3), 5, 5)
    cap.append("canal 2.5 m of water joining a vanilla WaterDeep lake (one colour?)")
    # 3b canal into a dug pond, 1 m of water both sides
    dx, dz = px + 21, pz + 8
    for i in range(6):
        for j in range(5):
            s.dig((dx + i, dz + j), 2, 2)
    for x in range(dx + 6, dx + 13):
        s.dig((x, dz + 2), 2, 2)
    cap.append("canal 1 m of water joining a dug pond at 1 m (one colour?)")
    # 4 wall band: 3-wide canal 2 m deep with 1 m of water (the dry face above the water)
    bx, bz = px + 38, pz + 1
    for x in range(bx, bx + 10):
        for j in range(3):
            s.dig((x, bz + j), 4, 2)
    cap.append("wall band: 2 m canal, 1 m of water: the face between water and lip")
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
        cap.append("1 m of water in a %d m hole" % depth_m)
    for k, wet_m in enumerate((0.5, 1, 2)):
        pit = (bx + k * 5, bz)
        s.pit(pit, 3, 8, int(wet_m * 2))
        cap.append("%s m of water in a 4 m hole" % wet_m)
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
        cap.append("dry %s m hole, colonist standing in it" % m)
    return cap


def row_bars_trench(s, L):
    bx, bz = L["bars"]
    s.say("ROW bars_trench: waist-deep (1 m) and chest-deep (1.5 m) colonist, a shooter 8 squares east on flat ground")
    cap = []
    for k, (m, what) in enumerate(((1.0, "waist-deep"), (1.5, "chest-deep"))):
        pit = (bx + k * 5, bz + 22)
        s.pit(pit, 3, int(m * 2))
        tid = s.pawn((pit[0] + 1, pit[1] + 1), what)
        sid = s.pawn((pit[0] + 9, pit[1] + 1), "shooter")
        cap.append("%s colonist (%s m hole) with a shooter 8 squares east" % (what, m))
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
    cap.append("portable ladder leaning in a 2 m pit")
    s.pit(p4, 3, 8)
    s.place("RM_LadderPortable", (p4[0] + 1, p4[1] + 2), rot=0)
    cap.append("portable ladder against a 4 m wall (too short: lies flat)")
    s.pit(pg, 3, 8)
    s.pawn((pg[0] + 1, pg[1] + 1), "WEARS climbing gear, 4 m sheer pit", wear="RM_ClimbingGear")
    cap.append("climbing gear worn: colonist in a 4 m sheer pit")
    s.pit(pn, 3, 8)
    s.pawn((pn[0] + 1, pn[1] + 1), "no gear, 4 m sheer pit (control)")
    cap.append("no gear: control colonist in a 4 m sheer pit")
    s.item("RM_ClimbingGear", (bx + 20, bz + 34))
    cap.append("climbing gear item on the ground")
    s.pit((pc[0] + 4, pc[1]), 3, 4)
    s.place("RM_PitCover_PlankLattice", (pc[0] + 5, pc[1] + 1))
    cap.append("concealed pit (planks) over a 2 m pit")
    return cap


def row_bars_bridges(s, L):
    bx, bz = L["bars"]
    s.say("ROW bars_bridges: rope/timber/steel/heavy, railings on (north lane) and off (south lane), concealed pit beside")
    cap = []
    for k, tier in enumerate(("rope", "timber", "steel", "heavy")):
        x0 = bx + k * 13
        for lane, rails in ((0, "on"), (1, "off")):
            z = bz + 40 + lane * 4
            for x in range(x0 + 1, x0 + 5):
                s.dig((x, z), 8)
            s.proof(SUSP, "ProofBuild", "%d,%d;%d,%d;%s;god" % (x0, z, x0 + 5, z, tier))
            s.proof(SUSP, "ProofRails", "%d,%d;%s" % (x0 + 2, z, rails))
            cap.append("%s suspension bridge, railings %s (%s lane)" % (tier, rails, "north" if lane == 0 else "south"))
    s.pit((bx + 54, bz + 40), 3, 4)
    s.place("RM_PitCover_PlankLattice", (bx + 55, bz + 41))
    cap.append("concealed pit (planks, east end) beside the bridges: a concealed pit passes for ground, a bridge does not")
    return cap


def row_bars_bridge_kinds(s, L):
    bx, bz = L["bars"]
    s.say("ROW bars_bridge_kinds: grated steel/heavy, steel/heavy jetties, steel bridge in four looks")
    cap = []
    z = bz + 48
    for k, tier in enumerate(("steelgrated", "heavygrated")):
        x0 = bx + k * 13
        for x in range(x0 + 1, x0 + 5):
            s.dig((x, z), 8)
        s.proof(SUSP, "ProofBuild", "%d,%d;%d,%d;%s;god" % (x0, z, x0 + 5, z, tier))
        cap.append("%s suspension bridge over a 4 m pit" % tier)
    z = bz + 52
    for k, tier in enumerate(("steel", "heavy")):
        x0 = bx + k * 13
        for x in range(x0 + 1, x0 + 5):
            s.dig((x, z), 8)
        s.proof(SUSP, "ProofJetty", "%d,%d;%d,%d;%s;god" % (x0, z, x0 + 4, z, tier))
        cap.append("%s jetty reaching out over a 4 m pit" % tier)
    for k, look in enumerate(("Scrapper", "Industrial", "Modern", "Futuristic")):
        x0 = bx + k * 13
        z = bz + 56 + 0
        for x in range(x0 + 1, x0 + 5):
            s.dig((x, z), 8)
        s.proof(SUSP, "ProofLook", "%s;%d,%d;%d,%d" % (look, x0, z, x0 + 5, z))
        cap.append("steel bridge, %s look, railings on" % look)
    return cap


ROWS = dict(picks=row_picks, bars_joint=row_bars_joint, bars_dry=row_bars_dry, bars_trench=row_bars_trench, bars_access=row_bars_access,
            bars_bridges=row_bars_bridges, bars_bridge_kinds=row_bars_bridge_kinds, hoses=row_hoses, ladders=row_ladders, spikes=row_spikes, shallows=row_shallows, sprinklers=row_sprinklers)


# ------------------------------------------------------------------ driver
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--mock", action="store_true", help="FakeGame instead of the bridge (needs no game)")
    ap.add_argument("--only", default="")
    ap.add_argument("--origin", default="100,100")
    ap.add_argument("--save-name", default=None)
    ap.add_argument("--no-save", action="store_true")
    ap.add_argument("--no-shots", action="store_true")
    a = ap.parse_args(argv)
    only = [x for x in a.only.split(",") if x] or list(ALL_ROWS)
    for row in only:        # before any bridge call: an unknown row must not clear a site first
        if row not in ALL_ROWS + OPT_ROWS:
            ap.error("unknown row %r (rows: %s)" % (row, ", ".join(ALL_ROWS + OPT_ROWS)))
    ox, oz = map(int, a.origin.split(","))
    L = layout(ox, oz)
    name = a.save_name or "FLOWWORKS_OWNER_REVIEW_%s" % time.strftime("%Y%m%d_%H%M")
    w = None
    if not a.dry_run:
        import fw_walk_common as C
        out = os.path.join(C.REPO, "Transient", "owner_review_stage")
        w = C.make_walk(a, out)
    s = Stage(w, a.dry_run)
    s.say("OWNER REVIEW MAP %s  origin %s  rect %s  rows %s" % (name, (ox, oz), L["rect"], only))
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
        if [r for r in only if r not in ("hoses",) + BARS_ROWS]:      # the same three tests as the live branch above
            s.say("  clear_site %s" % (L["rect"],))
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
    s.say("FINISH: kill hostiles, Clear weather, step toward midday, frame, shoot, save '%s'" % name)
    if a.dry_run:
        if "hoses" in caps:
            s.say("SHOTS (per scene, wide + close) -> Transient/fw_hoses_walk/FlowWorks_HosePipeWalk_%s_<scene>_{wide,close}.png" % time.strftime("%Y%m%d"))
            for k, v in caps["hoses"]["scenes"].items():
                s.say("  scene %s wide %s close %s colonist %s" % (k, v[1], v[2], v[3]))
        print("DRY RUN: %d plan lines, no bridge touched." % len(s.plan))
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
        hdir = os.path.join(C.REPO, "Transient", "fw_hoses_walk")
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
        gx, gz = L[key]
        rect = (gx - 3, gz - 3, 66 if key != "sprinklers" else 60, 12 if key != "sprinklers" else 14)
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
    s.w.frame(L["rect"])            # clear_ui + closest zoom + frame (frame_cell_rect never zooms IN)
    if not a.no_save:
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
