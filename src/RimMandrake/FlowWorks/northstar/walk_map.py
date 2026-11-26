"""walk_map.py -- the FlowWorks walk map: every station shows ONE thing FlowWorks 0.1.0 must do, signed in plain words.

  python.exe src/RimMandrake/FlowWorks/northstar/walk_map.py --dry-run          the plan and the station list; no bridge
  python.exe src/RimMandrake/FlowWorks/northstar/walk_map.py --out DIR --save-name NAME
                                                                               LIVE: bridge held, a Playing map of 250x250
  options: --no-save  --no-shots  --only GROUP[,GROUP]  --mock (FakeGame)

RIMMANDRAKE_REBUILD_FLOWWORKS_WALK_MAP_OLD_CODED_AND_STRANGE (owner, 2026-11-25: "Please work to significantly enhance this
test map to expose as many explicit testing principles as FlowWorks really needs... many of them are old, coded, and
strange."). The list of what the map must show is walk_principles.py (page: design/concepts/FlowWorks/version/walk_brief/
station_principles.md, which also maps the old 79 stations of owner_review_stage.py onto it). Every station names the one
principle it shows (`shows`); its sign book says, in plain words and with no code name, what it shows (LOOK) and what to do
there (DO). `python3 src/RimMandrake/FlowWorks/review_map_coverage.py walk` checks the two against each other.

The stations stand in seven areas, one subject each, so the owner walks one subject at a time (GROUPS in walk_principles).
The staging calls of the kept stations are owner_review_stage.py's own rows (that file stays the builder of live_session B9);
this file gives them their place, their plain signs, and adds the new stations: the very large pit with many shapes, a
colonist walking under each pit cover kind, tar under a steel bridge lit by a colonist, the moat, the liquids side by side,
water running from a pond, a slime crossing, a hose, a geyser hot tub, a hole to dig yourself, and a walk under a bridge.

Every station is captured alone at one cell >= MIN_PX screen pixels (--out), uncompressed, as station_NN_<name>.png, and
stations.md beside the pictures lists each station with its sign. Then: kill hostiles, Clear weather locked, paused, ONE
save. Exit 0 staged and saved with no NOTE that says FAILED / NOT / REFUSED; 1 staged with such notes (read them); 4 refused
before staging (the map is too small, or a station would stand off the map or in its no-build edge); 3 the map's
biome is not one where water draws right; 5 no fresh map came up (--fresh-map).
"""
import argparse
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import owner_review_stage as R  # noqa: E402
import walk_principles as WP  # noqa: E402

MAP = (250, 250)
MIN_PX = 40                       # one cell at least this many screen pixels in every station capture (brief)
SHOT_H = 1351                     # ArchBig's screenshot height, measured 2026-11-25 (2285 x 1351; the 3467 x 1826 of
                                  # water_scenes_walk is an older screen): a capture of h cells shows 1351 / (h + 4) px a cell
TAR, WATER, SLIME = "RM_Fluid_Tar", "RM_Fluid_Water", "RM_Fluid_SlimeGreen"
FLUIDS = (("water", WATER), ("tar", TAR), ("oil", "RM_Fluid_Oil"), ("chemfuel", "RM_Fluid_Chemfuel"),
          ("green slime", SLIME), ("blood", "RM_Fluid_Blood"))
COVERS = (("woven scrap", "RM_PitCover_WovenScrap", "under scrap lid"), ("planks", "RM_PitCover_PlankLattice", "under plank lid"),
          ("reinforced", "RM_PitCover_ReinforcedFrame", "under frame lid"))
NPROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"
DP = "RimMandrake.FlowWorks.Pits.RM_DrawbridgeProofs"
FIRE_CLEAR = 15                   # brief: every other flammable thing at least 15 squares from the tar
CODE_WORD = re.compile(r"\bRM_|\bjawa/|\bProof[A-Z]|\b[a-z]+_[a-z_]+\b|\bdefName\b")


# ------------------------------------------------------------------ the stage: stations carry a principle and a DO line
class WalkStage(R.Stage):
    def station(self, row, rect, text, lane=0, short=None, shows=None, do=""):
        n = len(self.stations) + 1
        self.stations.append(dict(n=n, row=row, lane=lane, rect=tuple(rect), text=text, short=short or text, shows=shows,
                                  do=do, group=(WP.by_id().get(shows) or {}).get("group")))
        self.say("  station %d (%s) %s: %s" % (n, row, tuple(rect), short or text))
        return "%d  %s" % (n, short or text)

    def basin(self, x, z, w, h, levels):
        """Dig the rect to `levels` notches (0.5 m each) in one call (the engine's own Deepen, NorthstarProofs.ProofStageBasin)."""
        if levels <= 0:
            return
        self.proof(NPROOF, "ProofStageBasin", "%d;%d;%d;%d;%d;0;none" % (x, z, w, h, levels))

    def fluid(self, c, metres, fluid):
        """One square holding `metres` of `fluid` (RM_FluidIdentityProof.ProofFillWithFluid)."""
        self.proof(R.FLUIDID, "ProofFillWithFluid", "%d,%d,%g,%s" % (c[0], c[1], metres, fluid))


def retext(s, i0, texts, row):
    """Give the stations an old row just registered (s.stations[i0:]) their plain sign: (short, shows, look, do) each."""
    got = s.stations[i0:]
    if len(got) != len(texts):
        raise ValueError("row %s registered %d stations, its sign table has %d" % (row, len(got), len(texts)))
    for st, (short, shows, look, do) in zip(got, texts):
        st.update(short=short, shows=shows, text=look, do=do, group=WP.by_id()[shows]["group"], row=row)


def sign_ops(stations):
    """[place-op] one sign book per station: key = its number, name = its plain short name, LOOK = what it shows, DO = what to do."""
    um = os.path.join(HERE, "..", "..", "Utils", "modcheck")
    if um not in sys.path:
        sys.path.insert(0, um)
    import reviewmap as RMAP  # noqa: E402
    out = []
    for st in stations:
        x, z = R.station_label_cell(st)
        out.append(RMAP.sign_book(x, z, "%d" % st["n"], st["short"], look=st["text"], do=st.get("do", "")))
    return out


def sign_problems(stations):
    """[str] every station whose sign breaks the plain-words rule (pure): no principle, an unknown principle, no LOOK or no DO
    line, or a code name (RM_..., jawa/..., Proof..., snake_case) in its name, LOOK or DO."""
    ids = WP.by_id()
    out = []
    for st in stations:
        if st.get("shows") not in ids:
            out.append("station %d %r shows no listed principle (%r)" % (st["n"], st["short"], st.get("shows")))
        if not st.get("text") or not st.get("do"):
            out.append("station %d %r has no LOOK or no DO line" % (st["n"], st["short"]))
        room = max(8, 3 * (st["rect"][2] + R.DENSE_GAP))
        if len(st["short"]) > room:
            out.append("station %d %r: its name is longer than its label's room (%d characters)" % (st["n"], st["short"], room))
        for part in (st["short"], st.get("text") or "", st.get("do") or ""):
            m = CODE_WORD.search(part)
            if m:
                out.append("station %d %r: code name %r on its sign" % (st["n"], st["short"], m.group(0)))
                break
    return out


# ------------------------------------------------------------------ kept rows of owner_review_stage, with plain signs
T_LADDERS = [("lowered %s" % d, "ladders",
              "A 1.5 m pit. The ladder on the %s wall is lowered; the one on the opposite wall is raised." % d,
              "Look at how each ladder hangs on its wall.") for d in ("north", "east", "south", "west")]
T_SPIKES = [("spikes, dry", "spikes", "Spikes on the floor of a dry 2 m pit.", "Look at the stakes."),
            ("spikes in water", "spikes", "Spikes on the floor of a 2 m pit holding 1 m of water.",
             "Look at the stakes under the water, and at the pit walls under the water.")]
T_SHALLOWS = [("0.2 m of water", "water_depth", "A strip of 0.2 m of water in a 0.5 m channel.", "Mouse over a square: it reads 0.2 m.")] + \
    [("%s m of water" % m, "water_depth", "A pit full to the brim: %s m of water." % m, "Mouse over a square: it reads %s m." % m)
     for m in ("0.5", "1", "1.5", "2", "5")] + \
    [("dry 1 m hole", "water_depth", "A 1 m hole with no water, beside the water row.", "Compare it with the 1 m of water.")]
T_SPRINKLERS = [("sprinkler, %s" % k, "sprinkler_looks",
                 "A tank, pipe, powered pump and sprinkler head, all in the %s look." % k,
                 "Unpause for a moment: the head sprays.") for k in R.LOOKS]
T_JOINT = [("1 m in 1 m hole", "how_full", "A 1 m hole full of water: no wall shows above the water.", "Compare it with its neighbours."),
           ("1 m in 2 m hole", "how_full", "A 2 m hole with 1 m of water: a dry wall band shows above the water.", "Compare it with its neighbours."),
           ("wades in 1 m", "pawn_in_water", "A colonist wading in 1 m of water in a 4 m hole.",
            "Look at her, cut at the water's surface; mouse over her."),
           ("0.5 m in 4 m", "how_full", "A 4 m hole with 0.5 m of water: a tall dry wall above it.", "Compare it with its neighbours."),
           ("1 m in 4 m hole", "how_full", "A 4 m hole with 1 m of water.", "Compare it with its neighbours."),
           ("swims in 2 m", "pawn_in_water", "A colonist swimming in 2 m of water in a 4 m hole.",
            "Look at her swimming; mouse over her.")]
T_DRY = [("dry %s m hole" % m, "depth_reads", "A dry %s m hole, a colonist standing in it." % m,
          "Compare its wall and how low she stands with the other holes.") for m in ("0.5", "1", "1.5", "2", "4", "8")]
T_TRENCH = [("%s in a trench" % w, "trench_cover", "A colonist %s in a trench against its east wall; a shooter 8 squares east." % w,
             "Draft the shooter and aim at her: the hit chance shows the trench's cover.") for w in ("waist-deep", "chest-deep")]
T_KINDS = [("steel grated bridge", "bridge_kinds", "A steel bridge with a grated deck, over a 4 m pit.", "Look at the deck and its anchors."),
           ("heavy grated bridge", "bridge_kinds", "A heavy bridge with a grated deck, over a 4 m pit.", "Look at the deck and its anchors."),
           ("steel jetty east", "jetties", "A steel jetty rooted west of a 4 m pit, reaching east over it.", "Look: one deck, not two blocks."),
           ("heavy jetty east", "jetties", "A heavy jetty rooted west of a 4 m pit, reaching east over it.", "Look: one deck, not two blocks.")] + \
    [("steel, %s" % k, "bridge_looks", "A steel bridge with railings over a 4 m pit, in the %s look." % k,
      "Compare the four looks.") for k in ("Scrapper", "Industrial", "Modern", "Futuristic")]


# ------------------------------------------------------------------ rows changed from owner_review_stage
def row_gates(s, o):
    """Sluices shut with water on ONE side (west or north), one sluice held open; grates with water on both sides."""
    ox, oz = o
    s.say("ROW gates: shut sluices with water on one side, an open sluice, two grates")
    plan = (("RM_Sluice", "WoodLog", "EW", 1, "shut"), ("RM_Sluice", "WoodLog", "NS", 0, "shut"), ("RM_Sluice", "WoodLog", "EW", 1, "open"),
            ("RM_SecurityGrateDoor", "Steel", "EW", 1, "grate"), ("RM_SecurityGrateDoor", "Steel", "NS", 0, "grate"))
    for k, (door, stuff, axis, rot, kind) in enumerate(plan):
        x0 = ox + k * 7
        cells = [(x0 + i, oz + 2) for i in range(5)] if axis == "EW" else [(x0 + 2, oz + i) for i in range(5)][::-1]
        for c in cells:          # NS cells run north first: the wet side is always cells[0..1]
            s.dig(c, 2)
        mid = cells[2]
        s.place(door, mid, rot=rot, stuff=stuff)
        wet = cells[:2] if kind == "shut" else cells
        s.fill_m(wet[0], 1.0)    # one body each side; a shut gate keeps the far side dry
        if kind != "shut" and kind != "grate":
            s.say("  hold open %s (the Hold open button and a colonist walks through)" % (mid,))
            if not s.dry:
                try:
                    import water_scenes_walk as m
                    got = str(m.gate_open(s.w, mid))
                    if "open=True" not in got:
                        s.notes.append("open sluice at %s NOT read open: %s" % (mid, got[:120]))
                except Exception as ex:  # noqa: BLE001
                    s.notes.append("hold-open of the sluice at %s FAILED: %s" % (mid, ex))
            s.fill_m(cells[-1], 1.0)
        side = "west" if axis == "EW" else "north"
        far = "east" if axis == "EW" else "south"
        way = "east-west" if axis == "EW" else "north-south"
        if kind == "shut":
            s.station("gates", (x0, oz, 5, 5), "", short="sluice shut %s" % ("E-W" if axis == "EW" else "N-S"), shows="sluice_holds",
                      do="Select it and open it, then unpause: the water runs %s." % far)
            s.stations[-1]["text"] = "A shut sluice gate in a %s canal: 1 m of water on its %s side, the %s side dry." % (way, side, far)
        elif kind == "open":
            s.station("gates", (x0, oz, 5, 5), "An open sluice gate in an east-west canal: water at one level on both sides.",
                      short="sluice open", shows="sluice_holds", do="Compare it with the shut ones.")
        else:
            s.station("gates", (x0, oz, 5, 5), "A grate gate in a %s canal: the water stands at one level on both sides." % way,
                      short="grate gate %s" % ("E-W" if axis == "EW" else "N-S"), shows="grate_passes", do="Look at the water on both sides.")


def row_access(s, o):
    """Portable ladders, climbing gear worn and not, a covered pit that passes for ground (old 42-45, 47; 46 removed)."""
    bx, bz = o
    s.say("ROW access: portable ladders, climbing gear, a covered pit")
    p2, p4, pg, pn, pc = (bx, bz), (bx + 5, bz), (bx + 10, bz), (bx + 15, bz), (bx + 20, bz)
    s.pit(p2, 3, 4)
    s.place("RM_LadderPortable", (p2[0] + 1, p2[1] + 2), rot=0)
    s.station("access", (p2[0], p2[1], 3, 3), "A portable ladder in a 2 m pit, leaning on the north wall.", short="ladder, 2 m pit",
              shows="portable_ladder", do="Look at how it leans.")
    s.pit(p4, 3, 8)
    s.place("RM_LadderPortable", (p4[0] + 1, p4[1] + 2), rot=0)
    s.station("access", (p4[0], p4[1], 3, 3), "A portable ladder in a 4 m pit: too short, it lies flat.", short="ladder, 4 m pit",
              shows="portable_ladder", do="Compare it with the 2 m pit.")
    s.pit(pg, 3, 8)
    s.pawn((pg[0] + 1, pg[1] + 1), "wears climbing gear, 4 m sheer pit", wear="RM_ClimbingGear")
    s.station("access", (pg[0], pg[1], 3, 3), "A colonist wearing climbing gear in a sheer 4 m pit.", short="climbing gear",
              shows="climbing_gear", do="Order her to the ground beside the pit and unpause: she climbs out.")
    s.pit(pn, 3, 8)
    s.pawn((pn[0] + 1, pn[1] + 1), "no gear, 4 m sheer pit")
    s.station("access", (pn[0], pn[1], 3, 3), "A colonist with no climbing gear in a sheer 4 m pit: he cannot climb the wall.",
              short="no gear", shows="climbing_gear",
              do="Order him to the ground beside the pit and unpause: he cannot climb out; the colony brings him a ladder in time.")
    s.pit(pc, 3, 4)
    for i in range(3):
        for j in range(3):
            s.place("RM_PitCover_PlankLattice", (pc[0] + i, pc[1] + j))
    s.station("access", (pc[0], pc[1], 3, 3), "A 2 m pit under a plank cover, on this square of ground.", short="covered pit",
              shows="cover_hides", do="Find the pit before you read the sign: it should pass for ground.")


def row_bridges(s, o):
    """Rope, timber, steel and heavy bridges, railings on (north lane) and off (south lane) (old 48-55; 56 removed)."""
    bx, bz = o
    s.say("ROW bridges: four kinds, railings on and off")
    for k, tier in enumerate(("rope", "timber", "steel", "heavy")):
        x0 = bx + k * R.BRIDGE_PITCH
        for lane, rails in ((0, "on"), (1, "off")):
            z = bz + 5 - lane * 4
            R.span_pit(s, x0, z)
            s.proof(R.SUSP, "ProofBuild", "%d,%d;%d,%d;%s;god" % (x0, z, x0 + 5, z, tier))
            s.proof(R.SUSP, "ProofRails", "%d,%d;%s" % (x0 + 2, z, rails))
            s.station("bridges", (x0, z - 1, 6, 3), "A %s bridge over a 4 m pit, railings %s." % (tier, rails),
                      lane=lane, short="%s, railings %s" % (tier, rails), shows="bridge_kinds",
                      do="Look at the deck, the anchors and the railings.")


def row_bridges_ns(s, o):
    """Every bridge kind, look and jetty laid north-south (old 65-68, 70-79; the fire under a deck, old 69, is removed)."""
    bx, bz = o
    s.say("ROW bridges north-south")
    slots = iter([(bx + 1 + k * R.NS_PITCH, bz + lane * 8, lane) for lane in range(3) for k in range(6)])

    regs = []

    def st(x, z0, lane, look, short, shows, do):
        regs.append(((x - 1, z0, 3, 6), look, lane, short, shows, do))

    look_slots = [next(slots) for _ in range(4)]
    for tier in ("rope", "timber", "steel", "heavy", "steel grated", "heavy grated"):
        x, z0, lane = next(slots)
        R.span_pit_ns(s, x, z0)
        s.proof(R.SUSP, "ProofBuild", "%d,%d;%d,%d;%s;god" % (x, z0, x, z0 + 5, tier.replace(" ", "")))
        if " " not in tier:
            s.proof(R.SUSP, "ProofRails", "%d,%d;on" % (x, z0 + 2))
        st(x, z0, lane, "A %s bridge laid north-south over a 4 m pit." % tier, "N-S %s" % tier.replace("grated", "grate"), "bridge_kinds",
           "Look at the deck and its anchors.")
    for tier in ("steel", "heavy"):
        for way in ("north", "south"):
            x, z0, lane = next(slots)
            R.span_pit_ns(s, x, z0)
            root, tip = ((x, z0), (x, z0 + 2)) if way == "north" else ((x, z0 + 5), (x, z0 + 3))
            ok, txt = s.proof(R.SUSP, "ProofJetty", "%d,%d;%d,%d;%s;god" % (root + tip + (tier,)))
            if ok and "ok=True" not in txt and not s.dry:
                s.notes.append("jetty %s %s at %s NOT built: %s" % (tier, way, root, txt[:160]))
            st(x, z0, lane, "A %s jetty rooted on the %s edge, reaching %s over a 4 m pit." % (
               tier, "south" if way == "north" else "north", way), "%s jetty %s" % (tier, way[0].upper()), "jetties",
               "Look: one deck, not two blocks.")
    for look, (x, z0, lane) in zip(("Scrapper", "Industrial", "Modern", "Futuristic"), look_slots):
        R.span_pit_ns(s, x, z0)
        s.proof(R.SUSP, "ProofLook", "%s;%d,%d;%d,%d" % (look, x, z0, x, z0 + 5))
        regs.insert(("Scrapper", "Industrial", "Modern", "Futuristic").index(look),
                    ((x - 1, z0, 3, 6), "A steel bridge laid north-south over a 4 m pit, in the %s look." % look, lane,
                     "N-S %s" % look, "bridge_looks", "Compare the four looks."))
    for rect, look, lane, short, shows, do in regs:
        s.station("bridges_ns", rect, look, lane=lane, short=short, shows=shows, do=do)


# ------------------------------------------------------------------ new stations
# The very large pit: two halves of 17 x 32 with the same shapes, split by a wall of ground left standing; the west half dry,
# the east half holding water to 3 m below the ground (so its 4, 6 and 8 m floors are under water and its 0.5-3 m floors dry).
BIG_W, BIG_H, BASE_M, DEEPEST_M, BIG_WATER_M = 17, 32, 4.0, 8.0, 3.0


def big_half():
    """{(u, v): metres} of one half (u 0..16 west to east, v 0..31 south to north; 0 = ground left standing), plus the notch
    cut 3 squares into the south rim at u 8 (v -3..-1) (pure)."""
    d = {(u, v): BASE_M for u in range(BIG_W) for v in range(BIG_H)}
    for i, m in enumerate((0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4)):            # long step run along the north edge
        for u in (2 * i, 2 * i + 1):
            for v in range(28, 32):
                d[(u, v)] = m
    for k, m in enumerate((1, 2, 3, 6)):                                 # floors at four depths side by side
        for u in range(4 * k, min(4 * k + 4, BIG_W)):
            for v in range(22, 28):
                d[(u, v)] = m
    for u in range(16, BIG_W):
        for v in range(22, 28):
            d[(u, v)] = 6
    for u in range(0, 7):                                                # island: 1 m top in a 6 m moat
        for v in range(14, 21):
            d[(u, v)] = 1 if (2 <= u <= 4 and 16 <= v <= 18) else 6
    for u in (10, 11):                                                   # pillar of ground
        for v in (16, 17):
            d[(u, v)] = 0
    for u in range(13, 16):                                              # inner pit, 8 m
        for v in range(15, 18):
            d[(u, v)] = 8
    for u in range(0, 5):                                                # peninsula of ground from the west rim
        for v in (10, 11):
            d[(u, v)] = 0
    for u in range(7, BIG_W):                                            # narrow 1 m ridge between two 6 m parts
        for v in range(10, 14):
            d[(u, v)] = 1 if u == 11 else 6
    for u in range(0, 7):                                                # L-shaped 2 m shelf: inside and outside corners
        for v in range(2, 9):
            if u < 3 or v < 5:
                d[(u, v)] = 2
    for u in range(8, BIG_W):                                            # diagonal edge between 2 m and 6 m
        for v in range(2, 9):
            d[(u, v)] = 6 if (u - 8) > (v - 2) else 2
    for v in (-3, -2, -1):                                               # a notch cut into the south rim
        d[(8, v)] = BASE_M
    return d


def big_cells(o):
    """{(x, z): metres} of the whole pit: west half at o, the wall of ground at x + 17, east half at x + 18 (pure)."""
    ox, oz = o
    out = {}
    for half in (0, 1):
        for (u, v), m in big_half().items():
            out[(ox + half * (BIG_W + 1) + u, oz + v)] = m
    return out


def runs(cells):
    """[(x, z, w, levels)] horizontal runs of equal depth (one basin call each; ground squares skipped) (pure)."""
    rows = {}
    for (x, z), m in cells.items():
        rows.setdefault(z, []).append((x, int(round(m * 2))))
    out = []
    for z, xs in sorted(rows.items()):
        xs.sort()
        start, lv, prev = None, None, None
        for x, l in xs + [(None, None)]:
            if start is not None and (x != prev + 1 or l != lv):
                if lv:
                    out.append((start, z, prev - start + 1, lv))
                start = None
            if x is not None and start is None:
                start, lv = x, l
            prev = x
    return out


def row_bigpit(s, o):
    ox, oz = o
    s.say("ROW big pit: %dx%d, two halves with the same shapes, the west dry, the east under %.0f m of water" % (2 * BIG_W + 1, BIG_H, BIG_WATER_M))
    for x, z, w, lv in runs(big_cells(o)):
        s.basin(x, z, w, 1, lv)
    east = (ox + BIG_W + 1, oz)
    s.fill_m((east[0] + 5, east[1] + 5), DEEPEST_M - BIG_WATER_M)    # metres above the deepest floor (the 8 m inner pit): surface 3 m down
    for half, base in ((0, (ox, oz)), (1, east)):                       # colonists for scale on several floors
        for (u, v), what in (((3, 17), "on the island, 1 m"), ((8, 19), "on the 4 m floor"), ((13, 25), "on the 6 m floor"),
                             ((7, 29), "on the 2 m step")):
            s.pawn((base[0] + u, base[1] + v), "%s half, %s" % ("west" if half == 0 else "east", what))
    s.station("bigpit", (ox, oz - 3, 2 * BIG_W + 1, BIG_H + 3),
              "One very large pit split by a wall of ground: the west half dry, the east half with the same shapes holding water "
              "3 m below the ground. Along the north, a long run of steps from 0.5 m to 4 m; below it floors of 1, 2, 3 and 6 m "
              "side by side; an island with a 1 m top in a 6 m moat; a pillar of ground; an inner pit 8 m deep; a peninsula of "
              "ground from the west rim; a 1 m ridge between two 6 m parts; an L-shaped 2 m shelf with inside and outside "
              "corners; a diagonal edge between 2 m and 6 m; and a notch cut into the south rim. The base floor is 4 m. "
              "Colonists stand on the island, the 4 m floor, the 6 m floor and the 2 m step in each half.",
              short="very large pit, many shapes", shows="complex_pit",
              do="For each shape, say which floor is higher from the picture alone, then mouse over to check.")


def row_dig(s, o):
    ox, oz = o
    s.pawn((ox, oz + 1), "ready to dig")
    s.station("dig", (ox, oz, 5, 3), "A colonist on bare soil, with three squares of soil east of her to dig.",
              short="dig a hole yourself", shows="dig_yourself",
              do="Select Dig canal in the Architect menu (FlowWorks), mark the three squares east of her, and unpause.")


def row_liquids(s, o):
    ox, oz = o
    s.say("ROW liquids: water, tar, oil, chemfuel, green slime, blood, 1 m each")
    for k, (name, fluid) in enumerate(FLUIDS):
        pit = (ox + k * 5, oz)
        s.pit(pit, 3, 2)
        for i in range(3):
            for j in range(3):
                s.fluid((pit[0] + i, pit[1] + j), 1.0, fluid)
    names = ", ".join(n for n, _ in FLUIDS)
    s.station("liquids", (ox, oz, 5 * len(FLUIDS) - 2, 3), "Six 1 m holes, each full of one liquid, west to east: %s." % names,
              short="six liquids side by side", shows="liquids_apart", do="Name each liquid by its look before you read the sign.")


def row_pond(s, o):
    """A dug pond (6x6, 1 m of water), a shut sluice, a dry 1 m canal and a dry 2 m pit at its end."""
    ox, oz = o
    s.say("ROW pond: pond, shut sluice, dry canal and pit")
    s.basin(ox, oz, 6, 6, 2)
    gate = (ox + 6, oz + 2)
    s.basin(gate[0], gate[1], 8, 1, 2)
    s.basin(ox + 14, oz + 1, 3, 3, 4)
    s.place("RM_Sluice", gate, rot=1, stuff="WoodLog")
    s.fill_m((ox + 2, oz + 2), 1.0)
    s.station("pond", (ox, oz, 17, 6), "A dug pond with 1 m of water, a shut sluice gate, then a dry canal and a dry 2 m pit.",
              short="water runs from a pond", shows="flow_from_pond",
              do="Select the sluice gate and open it, then unpause: the canal and pit fill and the pond drops.")


def row_slime(s, o):
    ox, oz = o
    s.say("ROW slime: a slime canal and a water canal, a colonist west of each")
    for k, (name, fluid) in enumerate((("water", WATER), ("slime", SLIME))):
        z0 = oz + k * 6
        s.basin(ox + 3, z0, 1, 5, 2)
        for j in range(5):
            if fluid == WATER:
                break
            s.fluid((ox + 3, z0 + j), 1.0, fluid)
        if fluid == WATER:
            s.fill_m((ox + 3, z0), 1.0)
        s.pawn((ox + 1, z0 + 2), "west of the %s" % name)
    s.station("slime", (ox, oz, 7, 11), "Two 1 m canals across the way: green slime (north) and water (south), a colonist "
              "west of each.", short="crossing slime and water", shows="slime_crossing",
              do="Order each colonist to the ground east of her canal and unpause: compare the two crossings.")


def row_moat(s, o):
    """A 4 m moat with 2 m of water running north-south, a raised timber drawbridge across it, a swimmer, and at its south end
    a shut sluice into an 8 m drain pit big enough to take all of its water."""
    ox, oz = o
    s.say("ROW moat: swimmer, raised drawbridge, shut sluice, drain pit")
    mx, mz = ox + 4, oz + 8
    s.basin(ox + 2, oz, 7, 6, 16)                   # the drain pit, 8 m: 42 squares x 4 m below the moat floor holds the moat
    s.basin(mx + 1, oz + 6, 1, 2, 8)                # the gate channel
    s.basin(mx, mz, 4, 18, 8)                       # the moat
    s.place("RM_Sluice", (mx + 1, oz + 7), rot=0, stuff="WoodLog")
    s.fill_m((mx + 1, mz + 10), 2.0)
    hz = mz + 9
    ok, txt = s.proof(DP, "ProofOneDrag", "%d,%d;%d,%d;timber" % (mx - 1, hz, mx + 4, hz + 1))
    s.proof(DP, "ProofDevSet", "%d,%d;raise;instant" % (mx, hz))
    s.pawn((mx + 2, mz + 4), "swims the moat")
    s.station("moat", (ox, oz, 12, 26), "A 4 m moat with 2 m of water, a raised timber drawbridge across it, a colonist "
              "swimming, and at its south end a shut sluice gate into a dry 8 m drain pit.", short="the moat",
              shows="moat", do="Select the sluice gate at the south end, open it, and unpause: the moat drains and she stands.")


def row_cover_walks(s, o):
    ox, oz = o
    s.say("ROW cover walks: a pit 3 x 9, a cover over its middle 3 x 3, one colonist under it, one in the open south end")
    for k, (name, d, short) in enumerate(COVERS):
        x0 = ox + k * 5
        s.basin(x0, oz, 3, 9, 6)
        s.pawn((x0 + 1, oz + 4), "already under the %s cover" % name)
        for i in range(3):
            for j in range(3, 6):
                s.place(d, (x0 + i, oz + j))
        s.pawn((x0 + 1, oz + 1), "in the open south end")
        s.station("covers", (x0, oz, 3, 9), "A 3 m pit with a %s cover over its middle, one colonist already under the cover, "
                  "one in the open south end." % name, short=short, shows="walk_under_cover",
                  do="Order the colonist in the south end to the north end of the pit floor and unpause: she walks under "
                     "the cover and it fades over her.")


def row_bridge_walk(s, o):
    ox, oz = o
    s.say("ROW walk under a bridge: steel bridge east-west over a 4 m pit 4 x 9")
    s.basin(ox + 1, oz, 4, 9, 8)
    s.proof(R.SUSP, "ProofBuild", "%d,%d;%d,%d;steel;god" % (ox, oz + 4, ox + 5, oz + 4))
    s.pawn((ox + 2, oz + 1), "in the pit, south of the deck")
    s.pawn((ox - 1, oz + 4), "west of the bridge")
    s.station("bridge_walk", (ox - 1, oz, 8, 9), "A steel bridge over a 4 m pit; one colonist on the pit floor south of the "
              "deck, one on the ground west of the bridge.", short="walk under and over a bridge", shows="walk_under_bridge",
              do="Order the one in the pit to its north end and the other to the ground east of the bridge; unpause.")


def row_fire(s, o):
    """Tar under a steel bridge, a colonist near to light it; nothing burnable within FIRE_CLEAR (the site is cleared first)."""
    ox, oz = o
    s.say("ROW fire: 1 m of tar in a 2 m pit 4 x 9 under a steel bridge; the colonist lights it")
    px, pz = ox + 5, oz + 3
    s.basin(px, pz, 4, 9, 4)
    for i in range(4):
        for j in range(9):
            s.fluid((px + i, pz + j), 1.0, TAR)
    s.proof(R.SUSP, "ProofBuild", "%d,%d;%d,%d;steel;god" % (px - 1, pz + 5, px + 4, pz + 5))
    s.pawn((px - 2, pz - 2), "ready to toss a flame")
    s.station("fire", (ox, oz, 14, 14), "1 m of tar in a 2 m pit under a steel bridge; a colonist beside it. No chemfuel, and "
              "nothing else that burns within 15 squares.", short="light tar under a steel bridge", shows="tar_fire",
              do="Select the colonist, right-click a tar square south of the bridge, choose Toss a flame here, and unpause.")


def row_hose(s, o):
    ox, oz = o
    s.say("ROW hose: a pump fed by a pipe from a full tank, a hose from its reel to a tank 11 squares east")
    pump = (ox + 6, oz + 5)
    n = R.hose_pump(s, pump, "W", "pipe", "E", "hose", pipe_len=4)
    s.ticks(2)
    R.hose_lay_all(s, [n])
    s.ticks(700)
    s.station("hose", (ox, oz, 21, 11),           # 11 tall: the laid hose arcs about 3 squares north of its line (live 2026-11-25) "A powered pump: a pipe brings water from a full tank on the west; a hose runs from "
              "its reel to a tank on the east.", short="a hose beside a pipe", shows="hose",
              do="Compare the hose with the pipe: thicker, with fittings at the reel, plump while water flows.")


def row_geyser(s, o):
    ox, oz = o
    gx, gz = ox + 2, oz + 2
    s.say("ROW geyser: a 4 m pit round a geyser, 2 m of water over the vent, a ladder on its north wall")
    if not s.dry:
        r = s.w.call("rimworld/spawn_thing", defName="SteamGeyser", x=gx, z=gz) or {}
        if r.get("success") is False:
            s.notes.append("geyser at %s NOT spawned: %s" % ((gx, gz), str(r)[:140]))
    s.basin(ox, oz, 6, 6, 8)
    s.proof("RimMandrake.FlowWorks.RM_SubmergeDraw", "ProofFillRect", "%d,%d,6,6,2.00,%s" % (ox, oz, WATER))
    s.place("RM_Ladder", (ox + 1, oz + 5), rot=0)
    s.station("geyser", (ox, oz, 6, 6), "A 4 m pit dug round a steam geyser and filled with 2 m of water over the vent.",
              short="geyser hot tub", shows="geyser_tub", do="Mouse over the water: it reads Hot Tub, and the vent bubbles.")


# ------------------------------------------------------------------ the plan: (row, group, origin, stager)
def reuse(fn, texts, key, offset=(0, 0)):
    """A kept owner_review_stage row placed with its south-west corner at `origin`: L maps its own key to the origin less
    the offset that row adds itself."""
    def run(s, o):
        L = {key: (o[0] - offset[0], o[1] - offset[1])}
        i0 = len(s.stations)
        fn(s, L)
        retext(s, i0, texts, fn.__name__.replace("row_", ""))
    return run


ROWS = [
    # holes
    ("bigpit", (14, 18), row_bigpit),
    ("depth", (56, 18), reuse(R.row_bars_dry, T_DRY, "bars", (0, 14))),
    ("dig", (56, 26), row_dig),
    # water and liquids
    ("shallows", (92, 18), reuse(R.row_shallows, T_SHALLOWS, "shallows")),
    ("joint", (132, 18), reuse(R.row_bars_joint, T_JOINT, "bars")),
    ("liquids", (150, 18), row_liquids),
    ("geyser", (182, 18), row_geyser),
    ("pond", (92, 32), row_pond),
    ("slime", (114, 32), row_slime),
    # gates and the moat
    ("gates", (14, 58), row_gates),
    ("moat", (56, 52), row_moat),
    # pits
    ("ladders", (14, 92), reuse(R.row_ladders, T_LADDERS, "ladders")),
    ("spikes", (36, 92), reuse(R.row_spikes, T_SPIKES, "spikes")),
    ("access", (48, 92), row_access),
    ("covers", (14, 100), row_cover_walks),
    ("trench", (36, 100), reuse(R.row_bars_trench, T_TRENCH, "bars", (0, 22))),
    # bridges
    ("bridges", (14, 140), row_bridges),
    ("kinds", (14, 152), reuse(R.row_bars_bridge_kinds, T_KINDS, "bars", (0, 48))),
    ("bridges_ns", (52, 164), row_bridges_ns),     # z 164: the calm site's own steam geyser stands at (59, 141)
    ("bridge_walk", (86, 140), row_bridge_walk),
    # pipes
    ("sprinklers", (100, 136), reuse(R.row_sprinklers, T_SPRINKLERS, "sprinklers")),
    ("hose", (100, 150), row_hose),
    # fire, alone
    ("fire", (205, 205), row_fire),
]


TICK_ROWS = ("shallows", "sprinklers", "hose")     # the rows that advance the clock (a flow pulse, a sprinkler pulse, a hose settle)


def staging_order(rows):
    """The rows that advance the clock first: a colonist staged in deep water treads it on every tick until the owner looks
    (2026-11-25: after the staging ticks and 240 more, a swimmer was downed by drowning; and the colony's pit rescue had built
    ladders for the stranded colonists of stations 6 and 41 and carried one into a cover pit) (pure)."""
    return [r for r in rows if r[0] in TICK_ROWS] + [r for r in rows if r[0] not in TICK_ROWS]


def renumber(live, planned):
    """Give the live stations the numbers of the plan (area order), whatever order they were staged in; sorts `live`."""
    order = {(st["row"], st["short"]): st["n"] for st in planned}
    for st in live:
        st["n"] = order.get((st["row"], st["short"]), 10 ** 6)
    live.sort(key=lambda st: st["n"])


def group_of(row):
    return {"bigpit": "holes", "depth": "holes", "dig": "holes", "shallows": "water", "joint": "water", "liquids": "water",
            "geyser": "water", "pond": "water", "slime": "water", "gates": "gates", "moat": "gates", "ladders": "pits",
            "spikes": "pits", "access": "pits", "covers": "pits", "trench": "pits", "bridges": "bridges", "kinds": "bridges",
            "bridges_ns": "bridges", "bridge_walk": "bridges", "sprinklers": "pipes", "hose": "pipes", "fire": "fire"}[row]


def plan(rows=None):
    """A dry Stage with every row (or `rows`) staged: its stations are the map's stations (pure, prints nothing)."""
    import contextlib
    import io
    d = WalkStage(None, True)
    with contextlib.redirect_stdout(io.StringIO()):
        for name, o, fn in ROWS:
            if rows is None or name in rows:
                stage_row(d, name, o, fn)
    return d


def stage_row(s, name, o, fn):
    """Stage one row; every station it registers carries the row's name (the key of its cleared rect) and its area."""
    i0 = len(s.stations)
    fn(s, o)
    for st in s.stations[i0:]:
        st["row"] = name
        st["group"] = WP.by_id()[st["shows"]]["group"] if st.get("shows") in WP.by_id() else None


def row_rects(stations, margin=3):
    """{row: (x, z, w, h)} each row's stations, their labels and `margin` squares round them: the rect cleared before it is
    staged (pure). The fire row's rect reaches FIRE_CLEAR squares further, so nothing burnable stands near the tar."""
    out = {}
    for st in stations:
        x, z, w, h = st["rect"]
        a = out.get(st["row"])
        box = (x, z, x + w, z + h + 1)
        out[st["row"]] = box if a is None else (min(a[0], box[0]), min(a[1], box[1]), max(a[2], box[2]), max(a[3], box[3]))
    res = {}
    for row, (x0, z0, x1, z1) in out.items():
        m = FIRE_CLEAR + 2 if row == "fire" else margin
        res[row] = (x0 - m, z0 - m, x1 - x0 + 2 * m, z1 - z0 + 2 * m)
    return res


def fire_problems(stations):
    """[str] every station other than the fire station whose rect comes within FIRE_CLEAR squares of the fire station (pure)."""
    fire = [st for st in stations if st["shows"] == "tar_fire"]
    out = []
    for f in fire:
        fx, fz, fw, fh = f["rect"]
        for st in stations:
            if st is f:
                continue
            x, z, w, h = st["rect"]
            gap = max(fx - (x + w), x - (fx + fw), fz - (z + h), z - (fz + fh))
            if gap < FIRE_CLEAR:
                out.append("station %d %r stands %d squares from the tar (want >= %d)" % (st["n"], st["short"], gap, FIRE_CLEAR))
    return out


def clear_problems(stations):
    """[str] every row whose cleared rect reaches a station (or its label row) of another row (pure): rows are cleared one
    by one just before each is staged, so such a clear would wipe what an earlier row built."""
    out = []
    for row, rect in row_rects(stations).items():
        for st in stations:
            x, z, w, h = st["rect"]
            if st["row"] != row and R._overlap(rect, (x, z, w, h + 1)):
                out.append("the clear of row %s %s reaches station %d %r of row %s" % (row, rect, st["n"], st["short"], st["row"]))
    return out


def problems(d, size=MAP):
    """Every way the plan breaks a rule of the map (pure): layout (numbers, overlaps, labels in stations), off the map or in
    its no-build edge, a sign not in plain words or with no principle, a station too large to capture at MIN_PX, a station
    near the tar, and two rows' cleared rects that overlap (a later clear would wipe an earlier row)."""
    out = [p for p in R.layout_problems(d.stations, rows=()) if not p.startswith("sparse")]
    out += R.offmap_problems(d.stations, size) + R.edgeband_problems(d.stations, size)
    out += sign_problems(d.stations) + fire_problems(d.stations)
    for st in d.stations:
        for k, tile in enumerate(shot_tiles(st["rect"])):
            px = px_per_cell(tile)
            if px < MIN_PX:
                out.append("station %d %r: its capture %d would show a cell at %.0f px (want >= %d)" % (st["n"], st["short"], k, px, MIN_PX))
    out += clear_problems(d.stations)
    return out


def px_per_cell(rect):
    """Screen pixels per cell of the capture of `rect` (the camera zoom fit_root_size gives it; SHOT_H tall) (pure)."""
    import water_scenes_walk as WSW
    return SHOT_H / (2.0 * WSW.fit_root_size(rect))


def shot_tiles(rect):
    """[(x, z, w, h)] the capture rects of a station: the station and its label row whole when one capture shows a cell at
    >= MIN_PX; else the fewest equal tiles that each do, north row first (pure). Each tile is its own picture."""
    x, z, w, h = rect
    h += 1                                  # the label row north of the station
    if px_per_cell((x, z, w, h)) >= MIN_PX:
        return [(x, z, w, h)]
    for n in range(2, 13):
        for nx in [a for a in range(1, n + 1) if n % a == 0]:
            nz = n // nx
            tw, th = -(-w // nx), -(-h // nz)
            if px_per_cell((x, z, tw, th)) >= MIN_PX:
                return [(x + i * tw, z + j * th, min(tw, w - i * tw), min(th, h - j * th))
                        for j in range(nz - 1, -1, -1) for i in range(nx)]
    raise ValueError("station rect %s cannot be captured at %d px a cell in 12 tiles" % (rect, MIN_PX))


def slug(t):
    return re.sub(r"[^a-z0-9]+", "_", t.lower()).strip("_")[:48]


def stations_md(stations, save=None):
    """stations.md: every station, area by area, with its sign (pure)."""
    lines = ["# FlowWorks walk map: the stations and their signs", ""]
    if save:
        lines += ["Save: `%s`" % save, ""]
    lines += ["Each station's sign book carries the same text. `station_NN_<name>.png` beside this file is its capture.", ""]
    for g, title in WP.GROUPS:
        sts = [st for st in stations if st["group"] == g]
        if not sts:
            continue
        lines += ["## %s" % title, "", "| station | name | what it shows | what to do |", "|---|---|---|---|"]
        for st in sts:
            lines.append("| %d | %s | %s | %s |" % (st["n"], st["short"], st["text"].replace("|", "/"), st["do"].replace("|", "/")))
        lines.append("")
    return "\n".join(lines)


PARK = (118, 118)                 # the site's own colonists wait here, drafted, away from every station


def geyser_problems(stations, geysers):
    """[str] every station (other than the geyser station) whose rect or label row meets a geyser's 2x2 (pure). The site clear
    does not remove a geyser (live 2026-11-25: the calm site's geyser at 59,141 stood in a north-south bridge pit)."""
    out = []
    for st in stations:
        if st["shows"] == "geyser_tub":
            continue
        x, z, w, h = st["rect"]
        for gx, gz in geysers:
            if gx is not None and R._overlap((x, z, w, h + 1), (gx, gz, 2, 2)):
                out.append("geyser at %s in station %d %r" % ((gx, gz), st["n"], st["short"]))
    return out


def park_colonists(s, w):
    """The site's own colonists, drafted in a row at PARK: undrafted, they wandered into stations during the staging ticks
    (live 2026-11-25: two stood in the moat and bridge frames)."""
    pawns = (w.hp("colonists") or {}).get("pawns") or []
    for k, p in enumerate(pawns):
        w.hp("pawn:%d=tp:%d,%d" % (p["id"], PARK[0] + k, PARK[1]))
        w.hp("pawn:%d=draft" % p["id"])
    s.say("  parked %d site colonists at %s, drafted" % (len(pawns), PARK))
    if not pawns:
        s.notes.append("no site colonist read to park (hose probe colonists): stray colonists may stand in stations")


# ------------------------------------------------------------------ live
def place_signs(s, w):
    s.chk("review_label clear", w.call("jawa/review_label", action="clear", tag=R.LABEL_TAG))
    s.chk("review_label add", w.call("jawa/review_label", action="add", ops="\n".join(R.station_label_ops(s.stations)), tag=R.LABEL_TAG))
    w.call("jawa/review_sign", action="clear", prefix="SIGN ")
    r = w.call("jawa/review_sign", action="place", ops="\n".join(sign_ops(s.stations))) or {}
    if r.get("refused") or r.get("success") is False:
        s.notes.append("station signs REFUSED: %s" % str(r.get("refused") or r)[:200])
    s.chk("kill_hostiles (final)", w.call("jawa/kill_hostiles"))
    s.chk("weather_set Clear (final)", w.call("jawa/weather_set", weather="Clear", lockWeather=True))


def capture(s, w, a, C, out):
    """Every station alone, each tile at >= MIN_PX a cell, copied uncompressed to out/station_NN_<name>[_part_K].png."""
    shots = []
    if a.no_shots:
        return shots
    os.makedirs(out, exist_ok=True)
    for st in s.stations:
        tiles = shot_tiles(st["rect"])
        for k, rect in enumerate(tiles):
            tag = "" if len(tiles) == 1 else "_part_%d" % (k + 1)
            png = C.snap(w, "station_%02d%s" % (st["n"], tag), rect)
            if not png:
                s.notes.append("station %d capture%s FAILED" % (st["n"], tag))
                continue
            dst = os.path.join(out, "station_%02d_%s%s.png" % (st["n"], slug(st["short"]), tag))
            shutil.copyfile(png, dst)
            shots.append(dst)
    return shots


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default=None, help="folder for the station captures and stations.md")
    ap.add_argument("--save-name", default=None)
    ap.add_argument("--no-save", action="store_true")
    ap.add_argument("--no-shots", action="store_true")
    ap.add_argument("--fresh-map", action="store_true", help="go to the main menu and start a debug quicktest map first")
    ap.add_argument("--shots-only", default="", help="N,M,... or all: capture those stations of the map staged now; no staging, no save")
    a = ap.parse_args(argv)
    only = [x for x in a.only.split(",") if x] or None
    names = [r[0] for r in ROWS]
    for x in only or ():
        if x not in names:
            ap.error("unknown row %r (rows: %s)" % (x, ", ".join(names)))
    d = plan(only)
    probs = problems(d)
    if probs:
        print("REFUSED: the plan breaks %d rule(s):" % len(probs))
        for p in probs:
            print("  " + p)
        return 4
    if a.dry_run:
        for st in d.stations:
            print("%3d  %-9s %-34s %s" % (st["n"], st["group"], st["short"], st["rect"]))
        print("DRY RUN: %d stations in %d areas, no bridge touched." % (len(d.stations), len({st["group"] for st in d.stations})))
        return 0
    import fw_walk_common as C
    out = a.out or os.path.join(C.REPO, "Transient", "walk_map_mock" if a.mock else "walk_map")
    w = C.make_walk(a, os.path.join(out, "_work"))
    s = WalkStage(w, False)
    if a.fresh_map and not a.mock:
        w.call("rimworld/go_to_main_menu")
        w.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
        from await_lifecycle import await_lifecycle  # noqa: E402  (Utils is on sys.path through validation_core)
        lc = await_lifecycle(w.call, "map_ready", 240, poll_s=0.5)
        if not lc.ok:
            print("COULD NOT LOOK: no fresh map: %s" % lc.reason)
            return 5
        w.call("jawa/clear_ui", all=True)
    msize = C.map_size(w)
    if tuple(msize) != MAP and not a.mock:
        print("REFUSED: the walk map is laid out for a %dx%d map; this map is %dx%d" % (MAP + tuple(msize)))
        return 4
    if not a.mock:
        mi = w.call("jawa/map_info") or {}
        biome = mi.get("mapBiome") or (mi.get("tileInfo") or {}).get("biome")
        if biome not in R.WATER_TRUE_BIOMES:
            print("REFUSED: map biome %s is not one where water is known to draw right (%s)" % (biome, ", ".join(R.WATER_TRUE_BIOMES)))
            return 3
    name = a.save_name or "FLOWWORKS_WALK_%s" % time.strftime("%Y%m%d_%H%M")
    s.chk("kill_hostiles", w.call("jawa/kill_hostiles"))
    s.chk("weather_set Clear", w.call("jawa/weather_set", weather="Clear", lockWeather=True))
    for _ in range(0 if a.shots_only else 12):           # morning first, so the staging ticks end near midday
        t = w.call("jawa/time_clock") or {}
        if t.get("ticksAbs") is None or 8 <= (t["ticksAbs"] % 60000) / 2500.0 <= 10:
            break
        w.ticks(2000)
    if a.shots_only:
        want = None if a.shots_only == "all" else {int(n) for n in a.shots_only.split(",")}
        s.stations = [st for st in d.stations if want is None or st["n"] in want]
        a.no_save = True
    if not a.shots_only and not a.mock:
        gx = [(t.get("x"), t.get("z")) for t in ((w.call("jawa/list_things", defName="SteamGeyser", limit=50) or {}).get("things") or [])]
        hit = geyser_problems(d.stations, gx)
        if hit:
            print("REFUSED: the map's own geysers stand in stations (move the row): " + "; ".join(hit))
            return 4
        park_colonists(s, w)
    rects = row_rects(d.stations)
    for row, o, fn in ([] if a.shots_only else staging_order(ROWS)):
        if only and row not in only:
            continue
        s.say("CLEAR %s %s" % (row, rects[row]))
        w.clear_site(rects[row])
        stage_row(s, row, o, fn)
    if not a.shots_only:
        renumber(s.stations, d.stations)
        if [st["n"] for st in s.stations] != [st["n"] for st in d.stations]:
            s.notes.append("LIVE stations FAILED to match the plan: %d live, %d planned" % (len(s.stations), len(d.stations)))
        place_signs(s, w)
    shots = capture(s, w, a, C, out)
    w.frame((14, 14, 222, 222))
    if not a.no_save:
        r = w.call("rimworld/save_game", saveName=name) or {}
        time.sleep(2.0)
        if not r.get("path") or r.get("success") is False:
            s.notes.append("save_game gave no path or FAILED: %s" % str(r)[:140])
        s.say("SAVE %s -> %s" % (name, r.get("path")))
    if a.out and not a.shots_only:
        with open(os.path.join(out, "stations.md"), "w", encoding="utf-8") as f:
            f.write(stations_md(s.stations, None if a.no_save else name + ".rws"))
    for n in s.notes:
        print("NOTE:", n)
    for p in shots:
        print("SHOT:", p)
    bad = [n for n in s.notes if re.search(r"FAILED|NOT |REFUSED", n)]
    print("WALK MAP %s: %d stations, %d notes, %d that say a thing was not done" % (name, len(s.stations), len(s.notes), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
