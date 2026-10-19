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
  sprinklers four nets (tank, pipe run, pump over the pipe, power, head) with the pipe run restyled Futuristic / Industrial / Modern /
            Scrapper BEFORE the head is built (a head takes its pipe's look); ticks run past one hourly pulse so the spray shows.
Then: kill hostiles, Clear weather locked, stepped toward midday, camera framed, shots, ONE save.

Every action goes through Stage: --dry-run prints exactly the calls a live run would make.
Bridge tools used (all found in the repo): jawa/flowworks_excavation_drive, jawa/build_batch, jawa/battery_set, jawa/static_call (ProofLadder, ProofTank,
ProofReadout, ProofResetRect), jawa/list_things, jawa/kill_hostiles, jawa/weather_set, jawa/time_clock,
jawa/clear_ui, jawa/take_screenshot, rimworld/frame_cell_rect, rimworld/save_game, rimworld/click_cell, rimworld/execute_gizmo.
"""
import argparse
import os
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
ALL_ROWS = ("ladders", "spikes", "gates", "shallows", "sprinklers")


# ------------------------------------------------------------------ geometry (pure)
def wall_cell(pit, r, n=3):
    """Dug middle square of wall r (0=N,1=E,2=S,3=W) of an n x n pit with south-west corner `pit`."""
    px, pz = pit
    m = n // 2
    return {0: (px + m, pz + n - 1), 1: (px + n - 1, pz + m), 2: (px + m, pz), 3: (px, pz + m)}[r]


def opposite(r):
    return (r + 2) % 4


def layout(ox, oz):
    """Every row's origin. Site rect (x, z, w, h) covers all of it."""
    return dict(
        ladders=(ox, oz), spikes=(ox, oz + 8), gates_sluice=(ox, oz + 16), gates_grate=(ox, oz + 25),
        shallows=(ox, oz + 34), sprinklers=(ox, oz + 49), rect=(ox - 3, oz - 6, 64, 70))


# ------------------------------------------------------------------ Stage: plan + execution in ONE path
class Stage(object):
    def __init__(self, w, dry):
        self.w, self.dry, self.plan, self.notes = w, dry, [], []

    def say(self, s):
        self.plan.append(s)
        print(s, flush=True)

    def dig(self, c, n, fill=-1):
        self.say("  dig %s depth %d%s" % (c, n, "" if fill < 0 else " fill %d" % fill))
        if not self.dry:
            self.w.dig(c, n, fill)

    def fill(self, c, f):
        self.say("  fill %s = %d notches (%.1f m)" % (c, f, f * NOTCH_M))
        if not self.dry:
            self.w.set_fill(c, f)

    def pit(self, origin, n, depth, fill=-1):
        for i in range(n):
            for j in range(n):
                self.dig((origin[0] + i, origin[1] + j), depth, fill)

    def place(self, d, c, rot=None, stuff=None):
        self.say("  place %s at %s rot=%s%s" % (d, c, "-" if rot is None else "%d(%s)" % (rot, ROT[rot]), " stuff=%s" % stuff if stuff else ""))
        if self.dry:
            return dict(survived=True, rot_read=rot, note="")
        import fw_walk_common as C
        return C.place(self.w, d, c, rot=rot, stuff=stuff)

    def raise_ladder(self, c, up=True):
        self.say("  ladder %s -> %s (ProofLadder)" % (c, "RAISED" if up else "lowered"))
        if self.dry:
            return True
        ok, txt = self.w.proof(PROMO, "ProofLadder", "%d,%d,%s" % (c[0], c[1], "raise" if up else "lower"))
        if not ok or ("raised=%s" % up) not in txt:
            self.notes.append("ladder %s raise read: %s" % (c, txt[:90]))
        return ok

    def ticks(self, n):
        self.say("  advance %d ticks" % n)
        if not self.dry:
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
            s.w.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofTank",
                     args="%d,%d;Store;RM_Liquid_FreshWater;100000" % (ox, oz))
            got = O.choose_look(s.w, (ox + 2, oz), look, run=True)
            if got != look:
                s.notes.append("pipe look for net %d: asked %s, game reads %s" % (k, look, got))
        s.place("RM_SprinklerHead", (ox + 5, oz))
        cap.append("sprinkler %s: head at %s (look read back in notes)" % (look, (ox + 5, oz)))
    s.ticks(PULSE + 300)            # one hourly pulse so every head is mid-spray
    return cap


ROWS = dict(ladders=row_ladders, spikes=row_spikes, shallows=row_shallows, sprinklers=row_sprinklers)


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
        s.w.call("jawa/kill_hostiles")
        s.w.call("jawa/weather_set", weather="Clear", lockWeather=True)
        s.w.clear_site(L["rect"])
    else:
        s.say("  kill hostiles; Clear weather locked; clear_site %s" % (L["rect"],))
    caps = {}
    for row in only:
        if row == "gates":
            caps["gates_sluice"] = row_gates(s, L, "RM_Sluice", "gates_sluice", "WoodLog")
            caps["gates_grate"] = row_gates(s, L, "RM_SecurityGrateDoor", "gates_grate", "Steel")
        else:
            caps[row] = ROWS[row](s, L)
    s.say("FINISH: kill hostiles, Clear weather, step toward midday, frame, shoot, save '%s'" % name)
    if a.dry_run:
        print("DRY RUN: %d plan lines, no bridge touched." % len(s.plan))
        return 0
    s.w.call("jawa/kill_hostiles")
    s.w.call("jawa/weather_set", weather="Clear", lockWeather=True)
    # daytime: approximate local hour from ticksAbs (ignores longitude); step to 10:00-14:00. Judge it in the picture.
    for _ in range(12):
        t = s.w.call("jawa/time_clock") or {}
        hour = ((t.get("ticksAbs") or 0) % 60000) / 2500.0
        if 10 <= hour <= 14:
            break
        s.w.ticks(2000)
    s.notes.append("approx hour %.1f (ticksAbs mod day, longitude ignored)" % hour)
    import fw_walk_common as C
    shots = []
    for key, title in (("ladders", "Ladders: lowered (wall k) + raised (opposite)"), ("spikes", "RM_Spikes dry and under 1 m"),
                       ("gates_sluice", "RM_Sluice, 4 facings + held open"), ("gates_grate", "RM_SecurityGrateDoor, 4 facings + held open"),
                       ("shallows", "Water ladder 0.2 / 0.5 / 1 / 1.5 / 2 / 5 m"), ("sprinklers", "Sprinklers: Futuristic / Industrial / Modern / Scrapper")):
        if key not in caps:
            continue
        gx, gz = L[key]
        rect = (gx - 3, gz - 3, 66 if key != "sprinklers" else 60, 12 if key != "sprinklers" else 14)
        png = C.snap(w, "row_" + key, rect)
        if png:
            shots.append(C.label_image(png, os.path.join(os.path.dirname(png), "row_%s_labelled.png" % key), title, "", caps[key]))
    over = C.snap(w, "overview", L["rect"])
    if over:
        shots.append(over)
    s.w.call("jawa/clear_ui", all=True)
    s.w.call("rimworld/frame_cell_rect", x=L["rect"][0], z=L["rect"][1], width=L["rect"][2], height=L["rect"][3], paddingCells=2)
    if not a.no_save:
        r = s.w.call("rimworld/save_game", saveName=name) or {}
        time.sleep(2.0)
        p = r.get("path")
        s.say("SAVE reported %s -- VERIFY the file exists and is new (save_game has written the wrong slot before)" % (p,))
    for n in s.notes:
        print("NOTE:", n)
    for p in shots:
        print("SHOT:", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
