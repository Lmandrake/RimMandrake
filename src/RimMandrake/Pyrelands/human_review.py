"""human_review.py -- the Pyrelands "for the human" review MAP: a station-by-station walk of everything the mod ships.

    python3    src/RimMandrake/Pyrelands/human_review.py --plan        # offline: layout check, KEYSHEET, COVERAGE
    python.exe src/RimMandrake/Pyrelands/human_review.py --build --load NS_Pyrelands_site_1_417df172fdb5_r7 | tr -d '\\r'
    python.exe src/RimMandrake/Pyrelands/human_review.py --goto N | tr -d '\\r'     # N = station, F free area,
                                                    # N0 natural ground, R scorched ruin, 0 overview
    python.exe src/RimMandrake/Pyrelands/human_review.py --weather RM_FE_BlackRain | tr -d '\\r'   # the one weather switch
    python.exe src/RimMandrake/Pyrelands/human_review.py --labels | tr -d '\\r'     # re-pin labels after a load
    python.exe src/RimMandrake/Pyrelands/human_review.py --signs | tr -d '\\r'      # re-place the in-save sign books
    python3    src/RimMandrake/Pyrelands/human_review.py --signs-for RM_pyre_review_YYYYMMDD  # offline: label sidecar
    python.exe src/RimMandrake/Pyrelands/human_review.py --clear | tr -d '\\r'
    python.exe src/RimMandrake/Pyrelands/human_review.py --save [--name RM_pyre_review_YYYYMMDD] | tr -d '\\r'

Owner, 2026-10-15 (typed): *"Not just a "hey look it's the Pyrelands" but a nice, orderly station-by-station
demonstration of the mechanics to test, the art to examine, etc. That showed more hidden bugs than anything."*
Method: design/RimMandrake/northstar_human_review.md (worked examples GimmeSomeSlack/human_review.py,
FlowWorks/review_map.py). Shared pieces: Utils/modcheck/reviewmap.py (LiveBridge, sweep_pawns, label_line,
save_keeper).

THE MAP IS A PYRELANDS MAP. A quicktest map is not the biome (no ash ground, no burn line, no natural cover, no
ruins), so --build runs on a Pyrelands site fixture (northstar_site.py makes them; --load loads one from the main
menu). Rows, north to south: A ground, B fire, C plants, D build and craft, E creatures, F the campaign cast.
Fire row B sits 36+ cells from the creature rows (the fire-hawk scans 18 cells for fire). The whole region is laid
with bare deep ash, which does not burn, so a fire can only walk through grass a station planted.

CALM WORLD: weather Clear and locked, clock pinned to noon, incident queue cleared, Peaceful, every non-colonist
swept before the pens are filled, every fire on the map put out (the standing burn line included), research
finished, god mode ON, game PAUSED, screenshot mode OFF. HEAT: the site is ~50 C at noon. The colonists are walked
into a cooled, roofed shelter in the free area and drafted there; nothing in the gallery needs a colonist.
FLYERS: the fire-hawk and fire-wasp are shown STANDING in roofed pens. No station plans a flight (owner:
"do not do live testing of flyers without a human present").

Mod Settings stay at shipped defaults; S on the key sheet names each setting and the station that shows it.
`human_review.py` is excluded from modcheck.status.mod_hash by basename; review/ is listed in .hashignore.
Selftest: review/selftest_pyre_review_map.py (offline, 0 game).
"""
import argparse
import html
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
from modcheck import reviewmap as RM  # noqa: E402

REVIEW = os.path.join(HERE, "review")                               # KEYSHEET.md + COVERAGE.md (never deployed: .md)
HTML_OUT = os.path.join(REPO, "Transient", "pyre_human_review")      # keysheet.html: read once, then binned
STATE = os.path.join(REPO, "Transient", "pyre_review_map_state.json")  # ruin position, weather, last verify
TAG = "pyre_review"
MAP_SIZE = 250
SW, SH = 12, 12                      # a station's footprint
PITCH = 16                           # 4 empty cells between stations: titles sit in the gap above
X0 = 8
ROWS = [("A", "GROUND", 84), ("B", "FIRE", 68), ("C", "PLANTS", 52),
        ("D", "BUILD AND CRAFT", 36), ("E", "CREATURES", 20), ("F", "CAMPAIGN CAST", 4)]
ASH = "RM_FE_Ash_Deep"
FIREBREAK = "RM_FE_FirebreakLine"
WALL_STUFF = "BlocksGranite"
FREE = dict(rect=(150, 104, 50, 28), shelter=(156, 108, 11, 9))
NATURAL = dict(rect=(50, 168, 40, 32))  # left untouched: the fixture's own ground round its pond (x 67-72, z 180-189)
TITLE_XZ = (100, 101)
FIRE_HAWK_SCAN = 18                  # Patches/RM_PyrelandsIgniters_Comps.xml scanRadius
CREATURE_FIRE_GAP = 30               # min distance from any burning station to any pen
BURN_TICKS = 8000                    # vanilla Fire.TryBurnFloor turns soil to its burnedDef (deep ash) only on a fire
                                     # alive >= 7500 ticks on that cell; 4000 left station 9 as soil (L2 2026-10-15)
NOW_TICKS = 300                      # BURNING NOW: flames established, then paused
WEATHERS = ("Clear", "RM_FE_Weather_AshDrift", "RM_FE_Weather_AshFall", "RM_FE_Weather_Cinderfall", "RM_FE_BlackRain",
            "DryThunderstorm")
GOLD, CREAM, TEAL, RUST = "#ffd27f", "#f2e6cf", "#8fd3c7", "#ff9a6b"
EMBER, QUICK, POD = "RM_FE_Plant_EmberGrass", "RM_FE_Plant_Quickgrass", "RM_FE_Plant_ScorchFruit"
CHILL_C = 10                         # stations 23-24 start here (the heat pusher works below 24 C; outside is ~55 C)
CAMPAIGN = ["RSW_Anooba", "RSW_Iriaz", "RSW_Nuna", "RSW_Orray", "RSW_Zeer", "RSW_Dalgo", "RSW_Gizka"]


# ------------------------------------------------------------------------------------------------ stations
def _pad(x=2, z=2, w=8, h=8):
    return (x, z, w, h)


FACINGS = ("South", "East", "North", "West")
FACING_SPOTS = ((3, 7), (8, 7), (3, 3), (8, 3))   # pen-local interior cells, one per facing


def _pen(kind, n=4, flyer=False, note=""):
    """A walled, roofed granite pen (make_empty_room) with deep-ash floor: wild animals cannot open its door.
    Owner, 2026-10-15: "You should put many creatures in each pen so they will have different facings to study."
    So every pen holds n (default 4) placed at FACING_SPOTS and turned S/E/N/W explicitly (jawa/artboard_stage
    gives each a long Wait job and sets its rotation after it), never left to wander into a facing.
    To watch them move on a loaded review save: --release-pens (and --pin-pens to put them back)."""
    return dict(room=(1, 1, 10, 10), pawns=[(kind, 6, 6, n)], keep=True, flyer=flyer, note=note, facings=True)


def station_defs():
    """The gallery, row by row. Each: row, short (in-world title), sub (one in-world clause), look (what to look for /
    suspected weak spot), poke (how to poke it), unpause (what unpausing does), setup (local cells, north up)."""
    S = []

    def add(row, short, sub, look, poke, unpause, **setup):
        S.append(dict(row=row, short=short, sub=sub, look=look, poke=poke, unpause=unpause, setup=setup))

    # ---- A GROUND
    add("A", "DEEP ASH", "the biome's ordinary ground",
        "Reads as grey-black ash, not dirt or concrete. Weak spot: the tile edges against vanilla terrain; the three "
        "retired ash rungs (trace/light/heavy) still ship PNGs no def points at.",
        ["Hover a cell: terrain 'deep ash', fertility 40% dry."], "Nothing changes on bare ash.",
        terrain=[(ASH, 2, 2, 8, 8)], expect_terrain={ASH: 60})
    add("A", "UNBURNED POCKETS", "soil, rich soil, gravel, sand: burn to ash",
        "Four pockets that have not burned. Weak spot: all four borrow the VANILLA textures, so nothing says Pyrelands "
        "until they burn.", ["Hover each: 'soil' 70%, 'rich soil' 140%, 'gravel' 28%, 'sand' 5%.",
                            "Start a fire on one (god mode: Dev > Debug actions > Fire): it burns to deep ash in one step."],
        "Nothing, unless fire reaches them.",
        terrain=[("RM_FE_Ground_Soil", 1, 6, 5, 5), ("RM_FE_Ground_SoilRich", 6, 6, 5, 5),
                 ("RM_FE_Ground_Gravel", 1, 1, 5, 5), ("RM_FE_Ground_Sand", 6, 1, 5, 5)],
        marks=[(3, 11, "soil"), (8, 11, "rich soil"), (3, 0, "gravel"), (8, 0, "sand")],
        expect_terrain={"RM_FE_Ground_Soil": 20, "RM_FE_Ground_SoilRich": 20, "RM_FE_Ground_Gravel": 20,
                        "RM_FE_Ground_Sand": 20})
    add("A", "WATER RING", "standing water ringed with rich ground",
        "The biome's terrain patch makers ring water with mud and rich soil. Compare N0 (the site's own pond).",
        ["Hover the rich soil: 140%. Plant something on it."], "Nothing.",
        terrain=[("RM_FE_Ground_SoilRich", 2, 2, 8, 8), ("Mud", 3, 3, 6, 6), ("WaterShallow", 4, 4, 4, 4)],
        expect_terrain={"WaterShallow": 16})
    add("A", "FIREBREAK LINE", "the buildable firebreak floor",
        "Architect > Floors > firebreak line. Weak spot: it borrows RoughHewnRock's texture; does it read as a "
        "deliberate firebreak beside grass?", ["Lay more of it yourself (god mode builds at once).",
                                              "Light the grass (Dev > Debug actions > Fire): the fire stops at the line."],
        "Nothing until you light the grass.",
        terrain=[(FIREBREAK, 2, 5, 8, 2)], plants=[(EMBER, 2, 7, 8, 3, 1.0, 1.0)],
        expect_terrain={FIREBREAK: 16}, burnable=True)
    add("A", "LOOSE ASH DRIFTS", "fire and ash fall leave loose ash",
        "RM_FE_Filth_LooseAsh at 1, 2, 3 and 4 passes, west to east. Weak spot: thick drifts may read as dirt.",
        ["Select the filth: cleaning removes it.", "--weather RM_FE_Weather_AshFall lays more over the whole map."],
        "Nothing; colonists may clean it if it is in the home area (it is not).",
        spawn=[("RM_FE_Filth_LooseAsh", 2 + 2 * i, z, i + 1) for i in range(4) for z in range(3, 9)],
        expect_things=["RM_FE_Filth_LooseAsh"])
    add("A", "HEAT: SUN VS SHADE", "overhead sun; a roof answers it",
        "West pad open sky, east pad under a roof on four granite posts. The cell temperature is the same; the "
        "difference is in a pawn's felt heat (the sun-heat kind 'overhead', +4..10 C, from the shared "
        "CreatureBehaviors engine). Weak spot: nothing on screen says which pad is shaded except the roof overlay.",
        ["Undraft a colonist, walk him to each pad, compare his Heatstroke climb (Health tab).",
         "Toggle the roof overlay (bottom-right) to see the shade."],
        "A pawn left in the open pad gains Heatstroke; in shade, slower.",
        terrain=[(ASH, 1, 3, 4, 5), (ASH, 7, 3, 4, 5)],
        build=[("Wall", 7, 3, None, WALL_STUFF), ("Wall", 10, 3, None, WALL_STUFF), ("Wall", 7, 7, None, WALL_STUFF),
               ("Wall", 10, 7, None, WALL_STUFF)],
        roof=[("RoofConstructed", 7, 3, 4, 5)], marks=[(3, 9, "open sun"), (9, 9, "shade")],
        probes=[("temp", 3, 5, "open"), ("temp", 8, 5, "shade")], expect_things=["Wall"])

    # ---- B FIRE (the ringed stations: a firebreak ring, the pad the 8x8 inside it; BURROWER is a walled pen and
    # FIREBREAK AND FOAM is unringed, held in by the bare deep ash round it)
    ring = dict(ring=True)
    add("B", "BEFORE THE BURN", "unburned grass on soil: light it",
        "The twin of the next station before fire: ember grass and quickgrass on an unburned soil pocket.",
        ["Light it: Dev > Debug actions > Fire on a grass cell, then unpause at 1x.",
         "Or equip the firefoam sprayer (D, items) and put it out half way."],
        "Paused: nothing. Lit: burns out in ~1-2 in-game hours inside the ring and leaves what the AFTER pad shows.",
        terrain=[("RM_FE_Ground_Soil", 2, 2, 8, 8)], plants=[(EMBER, 2, 2, 8, 8, 1.0, 0.75, 11), (QUICK, 2, 2, 8, 8, 1.0, 0.25, 12)],
        expect_terrain={"RM_FE_Ground_Soil": 50}, burnable=True, **ring)
    add("B", "AFTER THE BURN", "burned during the build, then put out",
        "The same pad burned for ~1.5 h: soil -> deep ash in one step, loose ash dusted on it, and maybe a "
        "scorch-fruit pod (1 in 20 burned cells). Weak spot: leafless (burnt) grass art; a pod that never appears.",
        ["Hover a burned cell: fertility shows the fresh-burn bonus (+50%, fading over 6 days).",
         "Unpause at 3x: ember grass re-greens within a few days, largely green in about a week."],
        "Regrowth over days; any scorch-fruit pod ripens and withers within ~a day.",
        terrain=[("RM_FE_Ground_Soil", 2, 2, 8, 8)], plants=[(EMBER, 2, 2, 8, 8, 1.0, 0.75, 21), (QUICK, 2, 2, 8, 8, 1.0, 0.25, 22)],
        burn=("after", (2, 2, 8, 8)), probes=[("fert", 6, 6, "burned")], expect_terrain={ASH: 30}, **ring)
    add("B", "BURNING NOW", "a live fire, paused mid-burn",
        "Ember grass on deep ash, lit along its west edge at the end of the build and paused ~300 ticks in. Look at the flames on the "
        "grass and the smoke. Weak spot: does fire on ash ground look right (the ground itself never burns)?",
        ["Unpause at 1x and watch it walk; it cannot cross the ring.", "Firefoam it, or Dev > Debug actions > "
         "extinguish."], "Burns out inside the ring in about an hour.",
        terrain=[(ASH, 2, 2, 8, 8)], plants=[(EMBER, 2, 2, 8, 8, 1.0, 1.0)], burn=("now", (2, 2, 1, 8)),
        expect_things=["Fire"], **ring)
    add("B", "BURN BONUS VS CONTROL", "burned ash feeds; unburned ash does not",
        "West 4x8: deep ash that burned during the build. East 4x8: the same deep ash, unburned. Weak spot: the bonus "
        "is invisible unless you hover; does a crop on the burned half grow visibly faster?",
        ["Hover both halves: fertility ~90% burned vs 40% control.", "--weather RM_FE_BlackRain and unpause ~15 h: "
         "the bonus washes away and the black rain waters the ash (both halves go up to 140%)."],
        "The bonus fades linearly over 6 days.",
        terrain=[(ASH, 2, 2, 8, 8)], plants=[(EMBER, 2, 2, 4, 8, 1.0, 1.0)], burn=("after", (2, 2, 4, 8)),
        marks=[(4, 11, "burned"), (8, 11, "control")], probes=[("fert", 3, 5, "burned"), ("fert", 8, 5, "control")],
        expect_terrain={ASH: 60, FIREBREAK: 80}, **ring)
    add("B", "BURROWER", "an ashwallow in grass: light it",
        "A wild ashwallow penned on a grass pad. When fire reaches it, it burrows (status 'burrowed') and comes up "
        "unharmed after the fire passes. Weak spot: is the burrowed state readable on screen?",
        ["Light the west edge (Dev > Debug actions > Fire), unpause at 1x, select the ashwallow."],
        "Paused: nothing. Lit: the burn crosses the pen; the ashwallow dives and surfaces.",
        room=(1, 1, 10, 10), plants=[(EMBER, 2, 2, 8, 8, 1.0, 1.0)], pawns=[("RM_Ashwallow", 6, 6, 1)], keep=True,
        burnable=True)
    add("B", "FIREBREAK AND FOAM", "lay your own firebreak, then light it",
        "An unringed grass pad: try the player's tools against fire.",
        ["Architect > Floors > firebreak line across the pad, then light one side.",
         "Equip a colonist with the firefoam sprayer (D, items) and spray the fire."],
        "Paused: nothing. The pad is surrounded by bare ash, so the fire cannot leave the station.",
        terrain=[(ASH, 1, 1, 10, 10)], plants=[(EMBER, 1, 2, 10, 8, 1.0, 1.0)], burnable=True,
        expect_things=[EMBER])

    # ---- C PLANTS
    add("C", "EMBER GRASS: GROWTH", "sprout to full, west to east",
        "Five strips at growth 5, 25, 50, 75 and 100%. Three random variants (A/B/C). Weak spot: young ember grass "
        "is only the full sprite shrunk (vanilla), so growth reads as size only.",
        ["Hover a strip: growth %.", "Unpause: it grows in under a day (growDays 0.8)."],
        "All strips reach full within a day.",
        plants=[(EMBER, 1 + 2 * i, 2, 2, 8, g, 1.0) for i, g in enumerate((0.05, 0.25, 0.5, 0.75, 1.0))],
        expect_things=[EMBER])
    add("C", "QUICKGRASS: 3 STAGES", "sprout, half, tall: three drawings",
        "Its own three-stage art (Plant_GrowthStaged): growth 20% sprout, 50% half, 90% tall. Weak spot: "
        "RM_FE_QuickgrassStages also holds stray copies of the sprout/half PNGs at its root, unused.",
        ["Hover each strip: growth %.", "Unpause: it reaches tall in about a day (growDays 1)."],
        "All strips grow to tall within a day.",
        plants=[(QUICK, 1 + 4 * i, 2, 3, 8, g, 1.0) for i, g in enumerate((0.2, 0.5, 0.9))],
        marks=[(2, 11, "sprout"), (6, 11, "half"), (10, 11, "tall")], expect_things=[QUICK])
    add("C", "GROUND COVER MIX", "ember and quick grass, carpeting ash",
        "The two grasses at about the biome's mix (3 ember : 1 quick), 10x10. PYRELANDS_GRASS_SATURATION_1 waits on "
        "your look: grass everywhere, ash where burned, no bare dirt. Compare N0 (the site's own ground).",
        ["Walk N0 too (--goto N0): that is what the biome itself grew."], "Nothing visible within hours.",
        terrain=[(ASH, 1, 1, 10, 10)], plants=[(EMBER, 1, 1, 10, 10, 1.0, 0.7, 31), (QUICK, 1, 1, 10, 10, 1.0, 0.25, 32)],
        expect_things=[EMBER, QUICK])
    add("C", "SCORCH-FRUIT PODS", "unripe, growing, ripe: four pod drawings",
        "Pods are fire-born (never wild): here planted by hand at growth 0.5%, 50% and 100%. Four random variants. "
        "Weak spot: a ripe pod and an unripe one may look the same.",
        ["Hover: growth and 'harvestable'.", "Unpause ~1 day: ripe pods wither (rotDestroys)."],
        "Ripe pods wither within about a day; that is the point of the fruit.",
        plants=[(POD, 1 + 4 * i, 3, 3, 6, g, 1.0) for i, g in enumerate((0.005, 0.5, 1.0))],
        marks=[(2, 11, "unripe"), (6, 11, "growing"), (10, 11, "ripe")], expect_things=[POD])
    add("C", "SCORCH-FRUIT HARVEST", "pick it, eat it, watch it rot",
        "Ripe pods plus a stack of 10 harvested scorch-fruit on the ground. Weak spot: rot timing (fruit ~4 days "
        "unrefrigerated) and whether eating it shows as food.",
        ["Designate the pods for harvest; a colonist walks out (heat!) and picks 5 a pod.",
         "Hover the stack: 'spoils in 4 days'. Force-feed a colonist (right-click > consume)."],
        "Pods wither in ~a day; the stack rots in ~4 days.",
        plants=[(POD, 2, 6, 6, 3, 1.0, 1.0)], items=[("RM_FE_ScorchFruitYield", 10, 4, 3)],
        expect_things=[POD, "RM_FE_ScorchFruitYield"])
    add("C", "ASH + WATER", "deep ash beside water feeds; dry ash starves",
        "A deep-ash strip with one water cell at its west end and a potato row along it. Watered ash reads 140%, "
        "dry ash 40% (radius 2 from water). Weak spot: nothing but the hover shows the watering; if the dry end "
        "refused the potatoes, the ash was too poor to sow, which is the point.",
        ["Hover the cell beside the water vs one 8 cells east.", "Unpause a few days: the potatoes near the water "
         "pull ahead."], "Crops beside the water grow clearly faster.",
        terrain=[(ASH, 1, 4, 10, 3), ("WaterShallow", 1, 5, 1, 1)], plants=[("Plant_Potato", 2, 4, 9, 3, 0.15, 1.0)],
        probes=[("fert", 2, 5, "beside water"), ("fert", 10, 5, "dry")], marks=[(1, 8, "water"), (10, 8, "dry")],
        expect_terrain={"WaterShallow": 1})

    # ---- D BUILD AND CRAFT
    add("D", "SHOVEL SAND", "an order: sand to glass sand, leaves gravel",
        "A Pyrelands sand patch. Orders > Shovel sand: a miner digs 5 glass sand a cell and the cell becomes gravel "
        "(a finite deposit). Weak spot: whether a miner takes the order at all (proven only by ProofShovel).",
        ["Orders > Shovel sand over the patch; undraft a colonist with Mining (heat!).", "Unpause."],
        "The colonist digs; glass sand piles up; gravel is left.",
        terrain=[("RM_FE_Ground_Sand", 2, 3, 8, 6)], expect_terrain={"RM_FE_Ground_Sand": 40})
    add("D", "PYRELANDS ITEMS", "hide, fruit, sprayer, glass sand",
        "Furnace hide, scorch-fruit, firefoam sprayer and glass sand, one stack each, "
        "west to east. Weak spot: the furnace hide has no texture of its own (it draws its parent leather).",
        ["Hover each: label and description.", "Equip the sprayer and aim it at BURNING NOW."], "Fruit rots in ~4 days.",
        items=[("RM_FurnaceHide", 20, 2, 6), ("RM_FE_ScorchFruitYield", 10, 6, 6),
               ("RM_FE_FirefoamSprayer", 1, 10, 6), ("RM_GlassSand", 30, 6, 3)],
        marks=[(2, 8, "hide"), (4, 8, "glass"), (6, 8, "fruit"), (10, 8, "sprayer")],
        expect_things=["RM_FurnaceHide", "RM_FE_FirefoamSprayer"])

    # ---- E CREATURES (the fire cast, each alone in a roofed pen)
    add("E", "FIRE-HAWK", "flyer, shown standing only",
        "Four standing, one per facing (S, E, N, W). Its five flying frames and its ember carrying are a FLIGHT: judged only with you "
        "present (FIREHAWK_FLIGHT_BEHAVIOR_1), never here.",
        ["Four of it, set facing S, E, N, W (west is east mirrored)."], "It stays in its roofed pen.",
        **_pen("RM_FireHawk", flyer=True))
    add("E", "FIRE-WASP", "flyer, shown standing only",
        "Standing art only; its eight fly frames are a flight (owner-present only).",
        ["Four of it, set facing S, E, N, W."], "It stays in its roofed pen.", **_pen("RM_FireWasp", flyer=True))
    s = _pen("RM_FurnaceBeast")
    s.update(probes=[("temp", 3, 3, "room")], chill=CHILL_C)
    add("E", "FURNACE-BEAST (GIANT)", "the walking hearth: it warms a cold room",
        "The giant (setting on by default; body size 6). Its pen and the CONTROL PEN east of it are the same room; the "
        "build chilled both to %d C, because outside is ~55 C and the beast's heat pusher stops at 24 C (a pen at the "
        "outdoor 56 C can never read warmer: the 2026-10-15 build measured 56.75 vs 56.68). Weak spot: its warmth/"
        "thermal comps attach by a patch that only applies when RimUtinni Patches is loaded "
        "(RM_PyrelandsIgniters_Comps.xml); standalone Pyrelands ships a plain beast." % CHILL_C,
        ["Hover the floor of both pens: room temperature.", "Unpause at 1x for an in-game hour: this pen should "
         "climb clearly faster than the control pen (both drift back toward the outdoor heat through the walls).",
         "Select the beast: 'Heat charge' in its inspect pane (it charges in heat above 35 C)."],
        "Its pen warms faster than the control pen; when it lies down it may smoulder its bed (the ash floor has "
        "nothing to burn).", **s)
    add("E", "CONTROL PEN: NO BEAST", "the same room with no beast in it",
        "Same walls, roof, floor and starting chill as the furnace-beast pen west of it, and nothing inside: it is the "
        "yardstick for the beast's heat, not a missing animal.", ["Hover the floor: room temperature, against the "
                                                                   "beast's pen."],
        "Warms only from the outdoor heat through its walls, slower than the beast's pen.",
        room=(1, 1, 10, 10), probes=[("temp", 3, 3, "room")], chill=CHILL_C, expect_things=["Wall", "Door"])
    add("E", "ULLAI HERD", "the ash grazer, four of a herd",
        "Four of a herd, one per facing (S, E, N, W). Its burn-following walk (to a two-day-old burn) needs days of roaming: the "
        "matrix's row, not this pen.", ["Four of it, set facing S, E, N, W; its size beside the others."],
        "They graze the pen.", **_pen("RM_Ullai"))
    add("E", "ASHWALLOW", "the burrowing grazer",
        "Standing art: four, one per facing (S, E, N, W). Its burrow is shown at B (BURROWER).", ["Four of it, set facing S, E, N, W."], "It grazes.",
        **_pen("RM_Ashwallow"))
    add("E", "EMBERSCYTHE", "predator; its dessicated art still borrows",
        "Four, one per facing (S, E, N, W) (emberscythe_v1). Weak spot: only its dessicated (rotted corpse) graphic is the Megascarab's.",
        ["Four of it, set facing S, E, N, W."], "It stays.", **_pen("RM_Emberscythe"))
    add("E", "SYTHECLAW", "predator", "Four, one per facing (S, E, N, W).", ["Four of it, set facing S, E, N, W."], "It stays.", **_pen("RM_Sytheclaw"))
    add("E", "BARBSLINGER", "predator with a tail gun",
        "Four, one per facing (S, E, N, W) (the scorpion redesign). Its spike projectile shows only in a fight.", ["Four of it, set facing S, E, N, W."],
        "It stays.", **_pen("RM_Barbslinger"))
    add("E", "FLAMEFANG", "predator; a venomous bite",
        "Four, one per facing (S, E, N, W). Its venom (RM_FlamefangVenom) shows only after a bite.", ["Four of it, set facing S, E, N, W."], "It stays.",
        **_pen("RM_Flamefang"))

    # ---- F CAMPAIGN CAST (Star Wars canon kinds UtinniPatches adds to the Pyrelands roster)
    for k in CAMPAIGN:
        add("F", k.replace("RSW_", "").upper(), "campaign roster (UtinniPatches)",
            "A canon kind the campaign adds to the Pyrelands roster (WildAnimals_Pyrelands.xml); its art is "
            "SWBestiary's, not this mod's. Here so the whole roster stands in one place.", ["Four of it, set facing S, E, N, W."], "It stays.",
            **_pen(k))
    return S


# ------------------------------------------------------------------------------------------------ signs
# What the in-world sign at each station says (owner, 2026-10-15: "I need text signs added to the savegame to tell me
# what to DO at each station"). Keyed by the station's short title: (look, do, decide), plain words, imperative. Drawn
# under the station's title by the JawaBench labeller and saved beside the save (modcheck/reviewmap.sign_sub /
# write_signs); also printed per station on the key sheet. layout_check refuses a station without one, or one too
# long for the sign (SIGN_MAX_LINES lines of SIGN_WIDTH).
SIGN_MAX_LINES = 5
SIGNS = {
    "DEEP ASH": ("grey-black ash ground, not dirt or concrete",
                 "hover a cell: it should say deep ash, 40%",
                 "does it read as ash? any ugly edge?"),
    "UNBURNED POCKETS": ("four pockets: soil, rich soil, gravel, sand",
                         "light one with Dev > Debug actions > Fire",
                         "does it turn to deep ash in one step?"),
    "WATER RING": ("water ringed with mud, then rich soil",
                   "hover the rich soil (140%); compare N0's pond",
                   "does it look like the biome's own pond?"),
    "FIREBREAK LINE": ("a stone firebreak strip beside grass",
                       "light the grass (Dev > Debug actions > Fire)",
                       "does the fire stop at the line? does it look deliberate?"),
    "LOOSE ASH DRIFTS": ("loose ash, 1 to 4 layers, west to east",
                         "select a drift; clean it if you like",
                         "do thick drifts read as ash, or as dirt?"),
    "HEAT: SUN VS SHADE": ("west pad open sky, east pad under a roof",
                           "walk a colonist onto each pad; watch his heatstroke",
                           "does the roofed pad clearly slow heatstroke?"),
    "BEFORE THE BURN": ("unburned grass on soil",
                        "light it (Dev > Debug actions > Fire), unpause at 1x",
                        "does it end up like the AFTER pad next door?"),
    "AFTER THE BURN": ("the same pad, burned during the build",
                       "hover a cell: fertility shows +50% burn bonus",
                       "ash, loose ash, maybe a pod: does it look burned?"),
    "BURNING NOW": ("a live fire, paused mid-burn",
                    "unpause at 1x and watch it walk",
                    "do fire and smoke look right on ash ground?"),
    "BURN BONUS VS CONTROL": ("west half burned, east half not",
                              "hover both halves: about 90% vs 40%",
                              "is the burned half visibly better?"),
    "BURROWER": ("an ashwallow in grass",
                 "light the west edge, unpause at 1x, select it",
                 "can you SEE that it has burrowed, and that it survives?"),
    "FIREBREAK AND FOAM": ("an open grass pad: your tools vs fire",
                           "lay a firebreak, light one side, spray firefoam",
                           "do the firebreak and the foam both stop it?"),
    "EMBER GRASS: GROWTH": ("ember grass at 5, 25, 50, 75, 100%",
                            "hover each strip for its growth",
                            "does young grass read as young, or just small?"),
    "QUICKGRASS: 3 STAGES": ("three drawings: sprout, half, tall",
                             "hover each strip for its growth",
                             "are the three stages clearly different?"),
    "GROUND COVER MIX": ("the two grasses mixed, 3 ember to 1 quick",
                         "compare with N0, the site's own ground",
                         "grass everywhere, ash where burned, no bare dirt?"),
    "SCORCH-FRUIT PODS": ("pods unripe, growing, ripe",
                          "hover each: growth and 'harvestable'",
                          "can you tell a ripe pod from an unripe one?"),
    "SCORCH-FRUIT HARVEST": ("ripe pods and a stack of fruit",
                             "designate harvest; hover the stack for spoil time",
                             "does it harvest, show as food, and rot in ~4 days?"),
    "ASH + WATER": ("ash strip, water at the west end, potatoes",
                    "hover beside the water, then the dry end",
                    "140% by water, 40% dry: do the crops show it?"),
    "SHOVEL SAND": ("a patch of Pyrelands sand",
                    "Orders > Shovel sand; undraft a miner; unpause",
                    "does he dig glass sand and leave gravel?"),
    "PYRELANDS ITEMS": ("hide, fruit, sprayer, glass sand",
                        "hover each item for its label and text",
                        "does each have its own look? (hide borrows leather)"),
    "FIRE-HAWK": ("a flyer, shown standing only",
                  "four of it: one faces each way",
                  "standing art right? (flight is judged with you live)"),
    "FIRE-WASP": ("a flyer, shown standing only",
                  "four of it: one faces each way",
                  "standing art right? (flight is judged with you live)"),
    "FURNACE-BEAST (GIANT)": ("this pen and the control pen east both start cold",
                              "hover both floors; unpause 1 hour at 1x; hover again",
                              "is this pen clearly warmer than the control pen?"),
    "CONTROL PEN: NO BEAST": ("EMPTY ON PURPOSE: the yardstick for the beast",
                              "hover its floor, then the furnace-beast pen west",
                              "after an hour unpaused, is this pen the cooler one?"),
    "ULLAI HERD": ("four ullai, the ash grazer",
                   "four: one faces each way; size beside the others",
                   "does it read as a herd grazer?"),
    "ASHWALLOW": ("the burrowing grazer, standing",
                  "four of it: one faces each way",
                  "is the art right? (its burrow is at BURROWER)"),
    "EMBERSCYTHE": ("a predator", "four of it: one faces each way",
                    "is the art right? (only its rotted corpse borrows)"),
    "SYTHECLAW": ("a predator", "four of it: one faces each way", "is the art right?"),
    "BARBSLINGER": ("a predator with a tail gun", "four of it: one faces each way",
                    "is the art right? (the spike shows only in a fight)"),
    "FLAMEFANG": ("a venomous predator", "four of it: one faces each way",
                  "is the art right? (the venom shows only after a bite)"),
}
CAMPAIGN_SIGN = ("a canon animal the campaign adds here", "four of it: one faces each way",
                 "does it belong in the Pyrelands?")
BOARD_SIGNS = {
    "N0": ("what the biome grew by itself", "walk it; compare station 15",
           "grass everywhere, ash where burned, no bare dirt?"),
    "R": ("the nearest ruin on the map", "look at the ground under and round it",
          "is the ruin blackened, or pristine?"),
    "G": ("weather is one switch for the map", "ask the agent: --weather NAME, then unpause",
          "does each weather read as itself?"),
    "S": ("every setting at its default", "Options > Mod Settings > Pyrelands",
          "are the toggles clear? anything missing?"),
    "E": ("fire-clock events (Peaceful keeps them off)", "save first; Dev > Incidents > RUT_FireRaid etc",
          "does each event make sense?"),
    "L": ("the burn line was put out for the calm", "unpause at 3x for ~2 days",
          "does a fire come back on its own?"),
    "W": ("the biome on the world map", "press the World tab",
          "does the Pyrelands patch look right?"),
}


def sign_of(s):
    return SIGNS.get(s["short"]) or (CAMPAIGN_SIGN if s["row"] == "F" else None)


def station_list():
    """Number the stations in row order and give each its origin."""
    S, n = [], 0
    rz = {r[0]: r[2] for r in ROWS}
    col = {}
    for d in station_defs():
        n += 1
        c = col.get(d["row"], 0)
        col[d["row"]] = c + 1
        S.append(dict(d, n=n, origin=(X0 + c * PITCH, rz[d["row"]])))
    return S


# ------------------------------------------------------------------------------------------------ the inventory
# Every feature Pyrelands ships (dev folders src/RimMandrake/Pyrelands + src/RimUtinni/PyrelandsMechanics), with the
# station that shows it, or why none does. A station key is a number, or a board: N0 natural ground, R scorched
# ruin (found at build), G the weather switch, S the settings sheet, W the world map, E the fire-clock events,
# L the standing burn line, F the free area.
FEATURES = [
    # terrain
    ("terrain", "Deep ash (RM_FE_Ash_Deep): ordinary ground, art", "Defs/TerrainDefs/AshField.xml", "1 N0"),
    ("terrain", "Unburned pockets: soil, rich soil, gravel, sand (RM_FE_Ground_*)", "ScorchableGround.xml", "2"),
    ("terrain", "Every ground burns to deep ash in one step (burnedDef)", "ScorchableGround.xml", "7 8"),
    ("terrain", "Water ringed with mud and rich soil (terrainPatchMakers)", "BiomeDefs/Pyrelands.xml", "3 N0"),
    ("terrain", "Firebreak line: buildable floor that stops fire", "TerrainDefs/Firebreak.xml", "4 12"),
    ("terrain", "Retired ash rungs trace/light/heavy (hidden aliases, re-laid on load)", "AshField.xml", None,
     "they never stand on a loaded map (re-laid to deep ash at load); the matrix's ground_deep_ash checks none "
     "remain. Their three PNGs are orphaned (named on station 1's card)."),
    # plants
    ("plant", "Ember grass: three drawings, fast growth (growDays 0.8)", "ThingDefs_Plants/EmberGrass.xml", "13 15"),
    ("plant", "Ember grass leafless (burnt) drawings, 4 variants", "EmberGrass.xml", "8",
     "only a plant made leafless shows them; 8 shows any survivor of the burn, else they stay unseen"),
    ("plant", "Quickgrass: three growth stages (Plant_GrowthStaged, PlantGrowthStages.cs)", "Quickgrass.xml", "14"),
    ("plant", "Quickgrass leafless drawing", "Quickgrass.xml", "8",
     "as ember grass: shown only on a leafless survivor at 8"),
    ("plant", "Ground cover saturation (PYRELANDS_GRASS_SATURATION_1, owner look owed)", "BiomeDefs/Pyrelands.xml", "15 N0"),
    ("plant", "Only RM_FE grasses grow wild (WildPlantAllowlist.cs)", "Source/WildPlantAllowlist.cs", "N0",
     "a property of days of wild spawning: N0 shows the result; the matrix's plant_distribution_correct counts it"),
    ("plant", "Plant density enforcer (RM_PyrelandsDensityEnforcer.cs)", "Source", "N0",
     "shows only as the natural cover at N0; the matrix's grass_chokes_ground measures it"),
    ("plant", "Scorch-fruit pod: growth, four drawings", "ThingDefs_ScorchFruit/ScorchFruit.xml", "16"),
    ("plant", "Scorch-fruit is fire-born: seeded on burned cells (1 in 20, map cap 40)", "FireEcologyHook.cs", "8"),
    ("plant", "Scorch-fruit harvest yields food; eating feeds", "ScorchFruit.xml", "17"),
    ("plant", "Scorch-fruit spoils: fruit ~4 days, ripe pod withers ~1 day", "ScorchFruit.xml", "16 17"),
    ("plant", "Thornvine made edible for the furnace-beast (RUT_Thornvine_Edible.xml)", "PyrelandsMechanics/Patches",
     None, "thornvine is another mod's plant and the beast must roam free to eat it; no review map can pen both"),
    # ground mechanics
    ("mechanic", "Watered deep ash is fertile (0.40 dry -> 1.40 within 2 cells of water)", "PyrelandsAshField.cs", "18"),
    ("mechanic", "Fresh-burn bonus (+0.50 fading over 6 days)", "PyrelandsAshField.cs", "8 10"),
    ("mechanic", "Black rain washes the bonus away and waters the field", "PyrelandsAshField.cs", "10 G"),
    ("mechanic", "Fire dusts loose ash (RM_FE_Filth_LooseAsh)", "FireEcologyHook.cs", "5 8"),
    ("mechanic", "Ash fall lays drifts that keep accumulating", "PyrelandsAshField.cs", "5 G"),
    ("mechanic", "Ambient ash drift is the commonest weather", "PyrelandsAshField.cs", "G"),
    ("mechanic", "Standing burn line: the map is never fireless for 2 days (MapComponent_BurnLine)", "Source", "L",
     "the calm world puts it out; L's card says how it relights (2 quiet days at 3x)"),
    ("mechanic", "Fire front: a grass line goes up every 2-4 days (PyrelandsFireFront.cs)", "Source", "L",
     "a clock over days; L's card warns that it can light station grass once you unpause"),
    ("mechanic", "Fire burns on deep ash and stamps the burn (fire-tick gate)", "FireEcologyHook.cs", "9 10"),
    ("mechanic", "Ruins generate scorched and burned (GenStep RM_FE_ScorchRuins)", "GenStepDefs", "R"),
    ("mechanic", "Overhead sun heat kind (+10 C at the substellar point; roofs answer it)", "BiomeDefs/Pyrelands.xml", "6"),
    ("mechanic", "Arrival letter on a new Pyrelands map", "BiomeDefs/Pyrelands.xml", None,
     "fires once when a colony first arrives; the review map is an already-settled site"),
    ("mechanic", "Acoustic-scanner payload for the biome", "Patches/RM_AcousticPayload_Pyrelands.xml", None,
     "needs the Acoustic Scanner mod and a gravship scan; neither is on the ratchet_pilot tier"),
    ("mechanic", "Mapgen raises no errors; plant and animal populations are the roster's", "validation.py", None,
     "a mapgen census, not a look: the matrix's mapgen_log_clean / *_distribution_correct; N0 shows the result"),
    # creatures
    ("animal", "Fire-hawk: four standing, one per facing", "RM_PyrelandsFauna.xml", "21"),
    ("animal", "Fire-hawk flying frames (5) and ember carrying (CompFireHawkSpread)", "RM_PyrelandsFauna.xml", None,
     "a flight: judged only with the owner present (FIREHAWK_FLIGHT_BEHAVIOR_1), never staged here"),
    ("animal", "Fire-wasp: four standing, one per facing", "RM_PyrelandsPortedFauna.xml", "22"),
    ("animal", "Fire-wasp fly frames (8)", "RM_PyrelandsPortedFauna.xml", None, "a flight: owner-present only"),
    ("animal", "Furnace-beast, giant art (setting furnaceBeastGiant, default on)", "RM_PyrelandsGiants.cs", "23"),
    ("animal", "Furnace-beast classic (non-giant) art", "RM_PyrelandsFauna.xml", None,
     "only with furnaceBeastGiant off and a restart; settings stay at shipped defaults here"),
    ("animal", "Furnace-beast heats an enclosed room (vanilla heat pusher, to 24 C, + its charged radiant push)",
     "RM_PyrelandsIgniters_Comps.xml + CompFurnaceThermalCharge.cs", "23 24"),
    ("animal", "Furnace-beast warmth aura (felt temperature near it)", "CompFurnaceWarmthAura.cs", "23"),
    ("animal", "Furnace-beast bed-down ignition", "CompFurnaceBedIgnition.cs", "23"),
    ("animal", "Furnace-beast thermal cycle: walks into fire to charge", "JobGiver_RUT_FurnaceThermalCycle.cs", None,
     "needs a free beast and a live fire for hours; penned here (fire row is 36+ cells away); matrix row"),
    ("animal", "Furnace-beast heat immunity (Patch_FurnaceBeastHeatImmunity.cs)", "Source", None,
     "visible only as it surviving its own fire (a bed it smoulders); not staged: nothing on the ash floor burns"),
    ("animal", "Ullai herd: four, one per facing, herd size", "RM_Ullai.xml", "25"),
    ("animal", "Ullai follow a two-day-old burn (RM_JobGiver_FollowBurn)", "RM_Ullai.xml", None,
     "needs days of free roaming after a burn; UNMEASURED in the matrix too (no drive yet)"),
    ("animal", "Ashwallow: four, one per facing", "RM_Ashwallow.xml", "26"),
    ("animal", "Burrow ahead of the fire (RM_Burrowed status)", "RM_JobGiver_BurrowOnFire.cs", "11"),
    ("animal", "Emberscythe: four, one per facing", "RM_Emberscythe.xml", "27"),
    ("animal", "Sytheclaw: four, one per facing", "RM_PyrelandsPortedFauna.xml", "28"),
    ("animal", "Barbslinger: four, one per facing", "RM_PyrelandsPortedFauna.xml", "29"),
    ("animal", "Barbslinger tail gun and spike projectile art", "RM_PyrelandsPortedFauna.xml", None,
     "a fight, not a look: draft a colonist at 29 in god mode to see it"),
    ("animal", "Flamefang: four, one per facing", "RM_PyrelandsPortedFauna.xml", "30"),
    ("animal", "Flamefang venom bite (RM_FlamefangVenom)", "HediffDefs", None,
     "a fight, not a look: let it bite a god-mode colonist at 30"),
    ("animal", "Dessicated (rotted corpse) drawings, five animals", "Textures/Things/Pawn/Animal/Pyrelands", None,
     "needs a fully rotted corpse (days of sim); kill one in its pen and run 3x for a few days to check by hand"),
    ("animal", "Campaign cast on the Pyrelands roster (7 RSW_ kinds, UtinniPatches)", "WildAnimals_Pyrelands.xml", "31-37"),
    # buildings and items
    ("building", "Shovel sand order (sand -> 5 glass sand, leaves gravel)", "RM_TerrainDig.cs", "19"),
    ("item", "Firefoam sprayer and its splash", "ThingDefs_Sprayer/FirefoamSprayer.xml", "20 9 12"),
    ("item", "Furnace hide", "ThingDefs_Items/RM_FurnaceHide.xml", "20"),
    ("item", "Scorch-fruit (the harvested food)", "ScorchFruit.xml", "17 20"),
    # weather
    ("weather", "Ash fall", "WeatherDefs/AshFall.xml", "G"),
    ("weather", "Ash drift", "WeatherDefs/AshFall.xml", "G"),
    ("weather", "Cinderfall (distinct from ash fall)", "WeatherDefs/Cinderfall.xml", "G"),
    ("weather", "Black rain (visibly dark)", "WeatherDefs/BlackRain.xml", "G"),
    ("weather", "Dry thunderstorm in the table; no ordinary rain", "BiomeDefs/Pyrelands.xml", "G"),
    # events (RimUtinni PyrelandsMechanics)
    ("event", "Flame-harvest visit (RUT_FlameHarvest)", "PyrelandsMechanics", "E"),
    ("event", "Fire raid / arson justice (RUT_FireRaid)", "PyrelandsMechanics", "E"),
    ("event", "The Tribes light the burn: fire rite (LordJob_RUT_FireRite)", "PyrelandsMechanics", "E"),
    # world
    ("world", "Biome generates on new worlds; world-map drawing", "Textures/World/Biomes/RM_Pyrelands.png", "W"),
    ("world", "Cross-biome mechanics (off by default)", "RM_PyrelandsMod.cs", "S",
     "off by default; turning it on changes other biomes, outside this map"),
    # settings
    ("setting", "Mod Settings: every toggle and tuning (RM_PyrelandsSettings and PyrelandsMechanicsSettings)",
     "RM_PyrelandsMod.cs", "S"),
    ("setting", "Mechanics gate: 'Mod enabled' and the Baroque Biomes 'Pyrelands' toggle", "PyrelandsMechanicsGate.cs", "S"),
]

BOARDS = {
    "N0": ("NATURAL GROUND", "the site's own cover round its pond: untouched",
           "What the biome grew by itself: the two grasses, deep ash, a pond ringed with rich ground and mud. "
           "PYRELANDS_GRASS_SATURATION_1 asks for your look here: grass everywhere, ash where burned, no bare dirt."),
    "R": ("SCORCHED RUIN", "the nearest ruin the build found",
          "Ruins on a Pyrelands map stand blackened: deep ash under and round them, loose ash filth, burned stuff. "
          "Weak spot: a pristine ruin (PYRE_RUINS_DIAGNOSE_JUNKYARD_STAYS_PRISTINE)."),
    "G": ("WEATHER SWITCH", "one global switch: --weather NAME",
          "Weather is global, so it is one switch, not stations. RM_FE_Weather_AshDrift: free-flying ash like snow "
          "(the commonest). RM_FE_Weather_AshFall: the map dims, loose-ash drifts pile up. RM_FE_Weather_Cinderfall: "
          "glowing cinders, must not read as ash fall renamed. RM_FE_BlackRain: dark rain, washes the burn bonus at 10, "
          "waters ash. DryThunderstorm: lightning without rain; a strike on "
          "station grass starts a fire there. There is no "
          "ordinary rain here. Unpause to see it fall; --weather Clear puts the calm back."),
    "S": ("MOD SETTINGS", "Options > Mod Settings > Pyrelands",
          "Every toggle at its shipped default. Station by setting: fire dusts ash 5, 8; scorch-fruit "
          "seeding 8, 16; ash-fall drifts 5, G; watered ash 18; fresh-burn bonus 8, 10; rain fades bonus 10; ambient "
          "drift G; growth stages 14; wild allowlist N0; scorched ruins R; standing burn line L; fire-hawk carrying "
          "21 (flight, owner-present); furnace thermal 23-24; fire clock E; giant furnace-beast 23 "
          "(restart); ullai herds 25 (restart); burrowing 11; shovel sand 19; cross-biome (off). "
          "PyrelandsMechanics: arson-justice raids, flame-harvest visits, the tribes' fire rite: E."),
    "W": ("WORLD MAP", "press the World tab",
          "The site sits in a 2-ring Pyrelands patch: the biome's world drawing. Pyrelands has 0 tiles on Ash'karr by design "
          "(painted once at the end)."),
    "E": ("FIRE-CLOCK EVENTS", "Dev > Incidents: RUT_FlameHarvest, RUT_FireRaid",
          "Storyteller events from RimUtinni PyrelandsMechanics: a flame-harvest visit, an arson-justice fire raid, "
          "and the tribes' fire rite (they light the burn themselves). Peaceful keeps them away; fire one from the "
          "Dev menu to see it. A fire raid is hostile: save first."),
    "L": ("BURN LINE AND FIRE FRONT", "put out by the calm world; it comes back",
          "A Pyrelands map is never fireless: after 2 quiet days the standing burn relights one smoulder, and every "
          "2-4 days a fire front sends a grass line up. Unpause at 3x for ~2 days to see it return. Once wild grass "
          "regrows between stations (days), a front can reach station grass."),
}


# ------------------------------------------------------------------------------------------------ geometry checks
def footprint(s):
    x, z = s["origin"]
    return (x, z, SW, SH)


def pen_stations(S):
    """Stations whose animals are held on the map (pawns + keep): the pens --release-pens / --pin-pens act on."""
    return [s for s in S if s["setup"].get("pawns") and s["setup"].get("keep")]


def pen_rects(S):
    """The 'x,z,w,h;...' rects string the companion's pen_release / pen_pin take: one footprint per pen station."""
    return ";".join("%d,%d,%d,%d" % footprint(s) for s in pen_stations(S))


def _overlap(a, b, pad=0):
    ax, az, aw, ah = a
    bx, bz, bw, bh = b
    return ax - pad < bx + bw and bx - pad < ax + aw and az - pad < bz + bh and bz - pad < az + ah


def _dist(a, b):
    """Shortest cell distance between two rects (0 when they touch or overlap)."""
    ax, az, aw, ah = a
    bx, bz, bw, bh = b
    dx = max(0, max(ax, bx) - min(ax + aw, bx + bw))
    dz = max(0, max(az, bz) - min(az + ah, bz + bh))
    return (dx * dx + dz * dz) ** 0.5


def region_rect(S):
    xs = [s["origin"][0] for s in S]
    zs = [s["origin"][1] for s in S]
    return (min(xs) - 2, min(zs) - 2, max(xs) + SW + 4 - min(xs), max(zs) + SH + 4 - min(zs))


def fire_stations(S):
    return [s for s in S if s["setup"].get("burn") or s["setup"].get("burnable")]


def ring_cells(s):
    """The firebreak ring: the outer 2 cells of the footprint."""
    return [(0, 0, SW, 2), (0, SH - 2, SW, 2), (0, 2, 2, SH - 4), (SW - 2, 2, 2, SH - 4)]


def _inside(rect, w=SW, h=SH):
    x, z, rw, rh = rect
    return 0 <= x and 0 <= z and x + rw <= w and z + rh <= h


def layout_check(S, defs_known=None):
    """-> [problem, ...]: every station inside the map and its own footprint, no overlaps, short in-world text, the
    free area and the natural window clear of the gallery, pens far from any fire, fire pads inside their ring,
    every def named by a station known (when defs_known is given)."""
    P = []
    for s in S:
        x, z, w, h = footprint(s)
        if not (0 <= x and 0 <= z and x + w <= MAP_SIZE and z + h + 3 <= MAP_SIZE):
            P.append("station %d outside the map: %s" % (s["n"], footprint(s)))
        if len(s["short"]) > 24:
            P.append("station %d title too long for the world label (%d > 24): %s" % (s["n"], len(s["short"]), s["short"]))
        if len(s["sub"]) > 56:
            P.append("station %d sub line too long (%d > 56)" % (s["n"], len(s["sub"])))
        for k in ("look", "poke", "unpause"):
            if not s.get(k):
                P.append("station %d has no %s" % (s["n"], k))
        sg = sign_of(s)
        if not sg:
            P.append("station %d (%s) has no sign in SIGNS" % (s["n"], s["short"]))
        elif RM.sign_sub(s["sub"], *sg, max_lines=99).count(RM.SIGN_BREAK) + 1 > SIGN_MAX_LINES:
            P.append("station %d sign runs past %d lines" % (s["n"], SIGN_MAX_LINES))
        u = s["setup"]
        for key in ("terrain", "plants", "roof"):
            for op in u.get(key, []):
                if not _inside(op[1:5]):
                    P.append("station %d %s op %s leaves the footprint" % (s["n"], key, op))
        cells = [(op[0], op[1], op[2]) for k in ("build", "spawn", "pawns") for op in u.get(k, [])]
        cells += [(op[0], op[2], op[3]) for op in u.get("items", [])]
        cells += [("probe " + op[3], op[1], op[2]) for op in u.get("probes", [])]
        for d, cx, cz in cells:
            if not (0 <= cx < SW and 0 <= cz < SH):
                P.append("station %d places %s outside its footprint at (%s, %s)" % (s["n"], d, cx, cz))
        if u.get("room") and not _inside(u["room"]):
            P.append("station %d room leaves the footprint" % s["n"])
        if u.get("ring"):
            for op in u.get("plants", []):
                if not _inside((op[1] - 2, op[2] - 2, op[3], op[4]), SW - 4, SH - 4):
                    P.append("station %d plants %s on its firebreak ring" % (s["n"], op[0]))
        for o in S:
            if o["n"] < s["n"] and _overlap(footprint(o), footprint(s), pad=2):
                P.append("stations %d and %d closer than 2 cells" % (o["n"], s["n"]))
        if not (u.get("expect_things") or u.get("expect_terrain") or u.get("pawns")):
            P.append("station %d expects nothing: its verify would read 'as built' with nothing read" % s["n"])
        if u.get("pawns") and not (u.get("room") or u.get("keep")):
            P.append("station %d holds animals with no pen" % s["n"])
        if u.get("flyer") and not u.get("room"):
            P.append("station %d flyer without a roofed pen" % s["n"])
    for k in BOARDS:
        if k not in BOARD_SIGNS:
            P.append("board %s has no sign in BOARD_SIGNS" % k)
    reg = region_rect(S)
    for name, rect in (("free area", FREE["rect"]), ("natural window", NATURAL["rect"])):
        if _overlap(reg, rect, pad=2):
            P.append("%s %s overlaps the gallery region %s" % (name, rect, reg))
        x, z, w, h = rect
        if not (0 <= x and 0 <= z and x + w <= MAP_SIZE and z + h <= MAP_SIZE):
            P.append("%s outside the map" % name)
    sx, sz, sw, sh = FREE["shelter"]
    fx, fz, fw, fh = FREE["rect"]
    if not (fx <= sx and fz + 2 <= sz and sx + sw <= fx + fw and sz + sh + 6 <= fz + fh):
        P.append("the shelter (with its batteries and panel north of it, and the stock row south) is not inside the "
                 "free area")
    fires = fire_stations(S)
    for p in [s for s in S if s["setup"].get("pawns") and s["row"] in ("E", "F")]:
        for f in fires:
            d = _dist(footprint(p), footprint(f))
            if d < CREATURE_FIRE_GAP:
                P.append("pen %d (%s) only %.0f cells from fire station %d (< %d; fire-hawk scans %d)"
                         % (p["n"], p["short"], d, f["n"], CREATURE_FIRE_GAP, FIRE_HAWK_SCAN))
    for f in fires:
        if _overlap(footprint(f), FREE["rect"], pad=10):
            P.append("fire station %d within 10 cells of the free area" % f["n"])
    if defs_known is not None:
        for s in S:
            for d in station_def_names(s):
                if d not in defs_known:
                    P.append("station %d names %s, which no known def file defines" % (s["n"], d))
    return P


def station_def_names(s):
    u = s["setup"]
    out = set()
    for key in ("terrain", "plants", "build", "items", "spawn", "pawns", "roof"):
        for op in u.get(key, []):
            out.add(op[0])
    out.update(u.get("expect_things", []))
    out.update(u.get("expect_terrain", {}))
    out.discard("Fire")
    return out


# Defs a station names that this repo does not define (vanilla Core / DLC). Anything else must be found in src/.
VANILLA = {"WaterShallow", "Mud", "Wall", "Door", "RoofConstructed", "Battery", "PowerConduit", "FueledSmithy", "Steel",
           "WoodLog", "Plant_Potato", "BlocksGranite", "Cooler", "SolarGenerator", "MealSurvivalPack",
           "MedicineIndustrial", "ComponentIndustrial"}


def defs_in_repo(names):
    """-> the subset of `names` some XML under src/ defines as a <defName>. Offline."""
    want, found = set(names), set()
    pat = re.compile(r"<defName>([^<]+)</defName>")
    for root in ("RimMandrake", "RimUtinni", "RimStarWars"):
        for dp, dn, fn in os.walk(os.path.join(REPO, "src", root)):
            dn[:] = [d for d in dn if d not in ("bin", "obj", "Source", "__pycache__", "art_source", "Textures", "Assemblies")]
            for f in fn:
                if not f.endswith(".xml"):
                    continue
                try:
                    with open(os.path.join(dp, f), encoding="utf-8", errors="ignore") as fh:
                        found.update(m for m in pat.findall(fh.read()) if m in want)
                except OSError:
                    pass
                if want <= found:
                    return found
    return found


def known_defs(S):
    names = set()
    for s in S:
        names |= station_def_names(s)
    names |= {"RM_FE_Filth_LooseAsh", ASH, FIREBREAK}
    return (names & VANILLA) | defs_in_repo(names - VANILLA)


# ------------------------------------------------------------------------------------------------ coverage
def coverage_check(S, features=None):
    """-> [problem]: every feature has a station key or a reason; every key names a station or a board."""
    features = FEATURES if features is None else features
    nums = {s["n"] for s in S}
    P = []
    for f in features:
        kind, what, src, where = f[0], f[1], f[2], f[3]
        reason = f[4] if len(f) > 4 else ""
        if not where and not reason:
            P.append("feature has neither a station nor a reason: %s" % what)
        for k in (where or "").split():
            if "-" in k and k.replace("-", "").isdigit():
                a, b = k.split("-")
                bad = [n for n in range(int(a), int(b) + 1) if n not in nums]
            elif k.isdigit():
                bad = [] if int(k) in nums else [k]
            else:
                bad = [] if k in BOARDS or k == "F" else [k]
            if bad:
                P.append("feature %r points at unknown station(s) %s" % (what, bad))
    return P


def build_command():
    return ("python.exe src/RimMandrake/Pyrelands/human_review.py --build --load NS_Pyrelands_site_1_417df172fdb5_r7 "
            "| tr -d '\\r'")


def coverage_md(S):
    E = lambda t: str(t).replace("|", "/")  # noqa: E731
    nostation = [f for f in FEATURES if not f[3]]
    md = ["# Pyrelands human-review map: coverage", "",
          "Generated by `python3 src/RimMandrake/Pyrelands/human_review.py --plan` from the script's own FEATURES and "
          "station list; edit the script, not this file.", "",
          "## Live build (one driver, all three mods' maps)", "",
          "Tier: the 22-mod `ratchet_pilot` list (Pyrelands ships inside `mandrake.rm.biomes`; the fire-clock events "
          "need `mandrake.rut.pyrelandsmechanics`, the campaign cast `mandrake.rut.patches` + "
          "`mandrake.rsw.swbestiary`, all on that tier). Bridge held, game up at the main menu or in any game:", "",
          "```", build_command(), "```", "",
          "- **The map must be a Pyrelands map.** A quicktest map is not the biome. `--load <save>` loads a "
          "`NS_Pyrelands_site_*` fixture from the main menu (the newest is `NS_Pyrelands_site_1_417df172fdb5_r7`, "
          "2026-10-15 01:31, 250x250; its name carries the def fingerprint it was made under). If it is missing or "
          "will not load, make a fresh one with "
          "`python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --fingerprint <fp>` (it saves and "
          "reloads the fixture), then run the build without `--load`. Without `--load` the build uses the current "
          "map and refuses one that is not RM_Pyrelands or not 250x250.",
          "- **Expected runtime: about 6-8 minutes** after the game is up (an ESTIMATE; no live build has run): save "
          "load ~2-3 min on the 22-mod tier, ~400 bridge calls ~2 min, %d ticks of burn at the ~60 ticks/s MEASURED "
          "for short waits (northstar_plan.py) ~2.5 min, verify + labels ~1 min. "
          "Then `--save` (~30 s) writes the keeper `RM_pyre_review_YYYYMMDD`." % (BURN_TICKS + NOW_TICKS),
          "- Exit code 0 only when every station verified as built; refusals land in "
          "`Transient/pyre_review_map_state.json` and the key sheet's agent block.", "",
          "## Feature inventory -> station", "",
          "%d features, %d stations (%d numbered + %d boards: %s). Stations: see `review/KEYSHEET.md`."
          % (len(FEATURES), len(S) + len(BOARDS), len(S), len(BOARDS), ", ".join(BOARDS)), "",
          "| kind | feature | source | station | note |", "|---|---|---|---|---|"]
    for f in FEATURES:
        md.append("| %s | %s | %s | %s | %s |" % (f[0], E(f[1]), E(f[2]), E(f[3] or "none"), E(f[4] if len(f) > 4 else "")))
    md += ["", "## Features with no station (%d)" % len(nostation), ""]
    md += ["- **%s**: %s" % (f[1], f[4]) for f in nostation]
    md += ["", "## Stations", ""]
    for r, name, _ in ROWS:
        md.append("- **%s %s:** %s" % (r, name, ", ".join("%d %s" % (s["n"], s["short"]) for s in S if s["row"] == r)))
    md.append("- **Boards:** " + ", ".join("%s %s" % (k, v[0]) for k, v in BOARDS.items()) + ", F free area + shelter")
    return "\n".join(md) + "\n"


# ------------------------------------------------------------------------------------------------ labels
def label_ops(S, weather="Clear", ruin=None):
    L = []

    def add(x, z, text, sub="", col=GOLD, size="small"):
        L.append(RM.label_line(x, z, text, sub, col, size, TAG))
    tx, tz = TITLE_XZ
    add(tx, tz, "PYRELANDS REVIEW MAP", "weather now: %s  |  settings: shipped defaults  |  key sheet: "
        "src/RimMandrake/Pyrelands/review/KEYSHEET.md" % weather, CREAM, "medium")
    for r, name, z in ROWS:
        n = sum(1 for s in S if s["row"] == r)
        add(X0 + n * PITCH + 8, z + SH // 2, "%s  %s" % (r, name), "", TEAL, "small")
    for s in S:
        x, z = s["origin"]
        u = s["setup"]
        add(x + SW // 2, z + SH + 2, "%d  %s" % (s["n"], s["short"]), RM.sign_sub(s["sub"], *sign_of(s)),
            RUST if u.get("flyer") else GOLD)
        for dx, dz, text in u.get("marks", []):
            add(x + dx, z + dz, text, "", CREAM, "tiny")
    fx, fz, fw, fh = FREE["rect"]
    add(fx + fw // 2, fz + fh + 1, "F  FREE AREA + COOL SHELTER", "colonists drafted in the shelter; stock on the "
        "south edge; outside is ~50 C", RUST)
    nx, nz, nw, nh = NATURAL["rect"]
    add(nx + nw // 2, nz + nh + 1, "N0  " + BOARDS["N0"][0], RM.sign_sub(BOARDS["N0"][1], *BOARD_SIGNS["N0"]), TEAL)
    if ruin:
        add(ruin[0], ruin[1] + 3, "R  " + BOARDS["R"][0], RM.sign_sub(BOARDS["R"][1], *BOARD_SIGNS["R"]), TEAL)
    for i, k in enumerate(("G", "S", "E", "L", "W")):
        add(20 + 30 * i, 108, "%s  %s" % (k, BOARDS[k][0]), RM.sign_sub(BOARDS[k][1], *BOARD_SIGNS[k]), CREAM, "small")
    return "\n".join(L)


def sign_ops(S, ruin=None):
    """The signs that live IN the save: one vanilla Novel per station on the first gap cell north of its NW corner, and
    one per board (modcheck/reviewmap.sign_book; jawa/review_sign places them). A plain load shows them with no agent:
    mouse over one for its DO line, press i for the whole sign."""
    L = []
    for s in S:
        x, z = s["origin"]
        L.append(RM.sign_book(x, z + SH, s["n"], s["short"], s["sub"], *sign_of(s), more="Key sheet: station %d." % s["n"]))
    nx, nz, nw, nh = NATURAL["rect"]
    L.append(RM.sign_book(nx + nw // 2, nz + nh, "N0", BOARDS["N0"][0], BOARDS["N0"][1], *BOARD_SIGNS["N0"]))
    if ruin:
        L.append(RM.sign_book(ruin[0], ruin[1] + 2, "R", BOARDS["R"][0], BOARDS["R"][1], *BOARD_SIGNS["R"]))
    for i, k in enumerate(("G", "S", "E", "L", "W")):
        L.append(RM.sign_book(20 + 30 * i, 106, k, BOARDS[k][0], BOARDS[k][1], *BOARD_SIGNS[k]))
    return L


# ------------------------------------------------------------------------------------------------ key sheet
NO_SAVE = "(no keeper saved yet: build, then --save)"


def keysheet(S, live=None, save=None, weather="Clear"):
    os.makedirs(REVIEW, exist_ok=True)
    os.makedirs(HTML_OUT, exist_ok=True)
    E = html.escape
    md = ["# Pyrelands review map - key sheet", "",
          "Load %s in RimWorld. Paused, god mode on, research finished, %s weather locked, noon, Peaceful. Mod "
          "Settings are the shipped defaults. Every station carries an in-world sign: its number, a short name, one "
          "clause, then LOOK / DO / DECIDE (zoom in to read the last three); this sheet repeats each sign and has the "
          "rest. Each station also has a SIGN BOOK in the save itself, on the cell just north of its west corner: "
          "mouse over it for the DO line, press i for the whole sign; it needs no agent and no mod. The floating "
          "labels return with the save when the JawaBench companion is awake; if they are missing, `--labels` "
          "re-pins them. Colonists are drafted inside the cool shelter at F: outside is "
          "~50 C, so anything that sends a colonist out costs Heatstroke." % (save or NO_SAVE, weather), "",
          "Navigate: `--goto N` (station), `--goto F`, `--goto N0`, `--goto R`, `--goto 0`. Rows run north to south: "
          + ", ".join("%s %s" % (r, n.lower()) for r, n, _ in ROWS) + ".", ""]
    for r, name, _ in ROWS:
        md += ["## %s - %s" % (r, name.capitalize()), ""]
        for s in [s for s in S if s["row"] == r]:
            lk, do, dec = sign_of(s)
            md += ["### %d. %s" % (s["n"], s["short"].capitalize()), "", "*%s.*" % s["sub"].capitalize(), "",
                   "**Sign:** LOOK: %s. DO: %s. DECIDE: %s" % (lk, do, dec), "",
                   "**Look for:** " + s["look"], "", "**Poke it:**", ""] + ["- " + p for p in s["poke"]] + [
                   "", "**If you unpause:** " + s["unpause"], ""]
    md += ["## Boards (labels, no build)", ""]
    for k, (t, sub, body) in BOARDS.items():
        lk, do, dec = BOARD_SIGNS[k]
        md += ["### %s. %s" % (k, t.capitalize()), "", "*%s.*" % sub, "",
               "**Sign:** LOOK: %s. DO: %s. DECIDE: %s" % (lk, do, dec), "", body, ""]
    md += ["### F. Free area and shelter", "", "A roofed granite shelter with two coolers on a solar + battery net "
           "(two batteries, no conduits). Colonists stand drafted inside; undraft one to "
           "use him. Stock on the south edge: steel, wood, granite blocks, components, glass sand, survival meals, "
           "medicine, two firefoam sprayers.", ""]
    if live:
        md += ["<details><summary>For the agent: this build</summary>", "", "```",
               json.dumps(live, indent=1, default=str), "```", "", "</details>", ""]
    with open(os.path.join(REVIEW, "KEYSHEET.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    cards = []
    for r, name, _ in ROWS:
        cs = []
        for s in [s for s in S if s["row"] == r]:
            sg = "LOOK: %s. DO: %s. DECIDE: %s" % sign_of(s)
            cs.append("<section class='st'><div class='num'>%d</div><div><h3>%s</h3><p class='sub'>%s</p>"
                      "<p class='sign'><b>Sign:</b> %s</p>"
                      "<p><b>Look for:</b> %s</p><p><b>Poke it:</b></p><ul>%s</ul><p><b>If you unpause:</b> %s</p>"
                      "</div></section>" % (s["n"], E(s["short"]), E(s["sub"]), E(sg), E(s["look"]),
                                            "".join("<li>%s</li>" % E(p) for p in s["poke"]), E(s["unpause"])))
        cards.append("<h2>%s &mdash; %s</h2><div class='grid'>%s</div>" % (r, E(name.capitalize()), "".join(cs)))
    boards = "".join("<section class='st'><div class='num'>%s</div><div><h3>%s</h3><p class='sub'>%s</p><p>%s</p>"
                     "</div></section>" % (k, E(t), E(sub), E(body)) for k, (t, sub, body) in BOARDS.items())
    page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pyrelands Review Map</title><style>
:root{--bg:#2a1d14;--panel:#3a291c;--ink:#f2e6cf;--muted:#c9b79a;--gold:#ffd27f;--teal:#8fd3c7;--rust:#ff9a6b;--line:#5a4230}
body{margin:0;background:var(--bg);color:var(--ink);font:18px/1.5 Georgia,serif;padding:20px 16px;overflow-x:hidden}
h1{color:var(--gold);margin:0 0 6px;font-size:28px}h2{color:var(--teal);border-bottom:1px solid var(--line);padding-bottom:4px;margin-top:30px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(340px,100%%),1fr));gap:12px}
.st{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px;display:flex;gap:12px}
.num{font-size:28px;color:var(--gold);min-width:42px;text-align:center;font-weight:bold}
h3{margin:0 0 4px;color:var(--gold);font-size:20px}.sub{color:var(--muted);margin:4px 0;font-style:italic}
.sign{color:var(--teal)}.box{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px}ul{margin:4px 0;padding-left:20px}
</style></head><body>
<h1>Pyrelands &mdash; review map</h1>
<div class="box">Load <b>%s</b>. Paused, god mode on, %s weather locked, noon, Peaceful, Mod Settings at shipped defaults.
Colonists wait drafted in the cool shelter at F: outside is about 50&nbsp;C.</div>
%s<h2>Boards</h2><div class='grid'>%s</div></body></html>""" % (E(save or NO_SAVE), E(weather), "\n".join(cards), boards)
    with open(os.path.join(HTML_OUT, "keysheet.html"), "w", encoding="utf-8") as f:
        f.write(page)


def write_coverage(S):
    os.makedirs(REVIEW, exist_ok=True)
    with open(os.path.join(REVIEW, "COVERAGE.md"), "w", encoding="utf-8") as f:
        f.write(coverage_md(S))


# ------------------------------------------------------------------------------------------------ live build
def build_exit(n_ok, n_want, blind):
    """-> (rc, text). rc 0 only when every station read as built and none was left unread."""
    bad = n_ok < n_want or blind
    return (1 if bad else 0), "stations %d/%d as built%s" % (n_ok, n_want, ", %d unread" % blind if blind else "")


def station_verdict(want_things, got_things, want_kinds, got_kinds, want_terrain, got_terrain):
    """True when every expected def stands in the footprint, every expected pawn kind is there in number, and every
    expected terrain covers at least its minimum cells; None when nothing is expected (nothing was read, so never "as
    built"). Pure: the selftest drives it."""
    from collections import Counter
    if not (want_things or want_kinds or want_terrain):
        return None
    if any(d not in got_things for d in want_things):
        return False
    if Counter(want_kinds) - Counter(got_kinds):
        return False
    return all(got_terrain.get(d, 0) >= n for d, n in want_terrain.items())


def ops_counts(ops):
    """jawa/get_terrain_batch `ops` ('Def:x,z,w,h;...') -> {defName: cells} (validation.py _ops_counts)."""
    out = {}
    for op in (ops or "").replace("\n", ";").split(";"):
        if ":" not in op:
            continue
        d, nums = op.split(":", 1)
        p = [int(v) for v in nums.split(",") if v.strip().lstrip("-").isdigit()]
        w = p[2] if len(p) > 2 else 1
        h = p[3] if len(p) > 3 else 1
        out[d.strip()] = out.get(d.strip(), 0) + w * h
    return out


def parse_kv(text):
    out = {}
    for kv in str(text or "").split(";"):
        if "=" in kv:
            k, v = kv.split("=", 1)
            out[k.strip()] = v.strip()
    return out


class Review(object):
    def __init__(self, B, log=None):
        self.B, self.log = B, log
        self.notes, self.verify, self.probes = [], {}, {}

    def say(self, msg):
        ln = "%s %s" % (time.strftime("%H:%M:%S"), msg)
        print(ln, flush=True)
        if self.log:
            with open(self.log, "a", encoding="utf-8") as f:
                f.write("- " + ln + "\n")

    def call(self, tool, **kw):
        r = self.B.call(tool, **kw)
        if not isinstance(r, dict) or r.get("success") is False:
            self.notes.append("%s %s refused: %s" % (tool, json.dumps(kw)[:140], json.dumps(r)[:220]))
        return r if isinstance(r, dict) else {}

    # ---- the map
    def load(self, name, budget_s=600):
        """Load a save from the main menu (loading over a live game NREs, northstar_site.reload_fixture)."""
        B = self.B
        B.call("rimworld/go_to_main_menu")
        for _ in range(120):
            if B.call("rimworld/get_ui_state").get("programState") == "Entry":
                break
            time.sleep(0.5)
        B.call("rimworld/load_game", saveName=name)
        t0 = time.time()
        time.sleep(5)
        while time.time() - t0 < budget_s:
            if B.call("rimworld/get_ui_state").get("programState") == "Playing" and B.call("jawa/map_info").get("success"):
                time.sleep(3)
                return True
            time.sleep(2)
        raise SystemExit("load %s: not Playing after %ds" % (name, budget_s))

    def require_site(self):
        mi = self.B.call("jawa/map_info")
        tile = mi.get("tile") if isinstance(mi.get("tile"), dict) else {}
        biome = mi.get("mapBiome") or mi.get("biome") or tile.get("biome") or ""
        if mi.get("sizeX") != MAP_SIZE:
            raise SystemExit("expected a %dx%d Pyrelands site, got %s" % (MAP_SIZE, MAP_SIZE, mi.get("sizeX")))
        if biome and "RM_Pyrelands" not in str(biome):
            raise SystemExit("the current map is %s, not RM_Pyrelands: --load an NS_Pyrelands_site_* fixture" % biome)
        if not biome:
            self.notes.append("map_info names no biome: RM_Pyrelands not confirmed (%s)" % sorted(mi)[:20])
        return mi

    def calm(self, mi):
        B = self.B
        self.call("jawa/weather_set", weather="Clear", lockWeather=True)
        clk = B.call("jawa/time_clock")
        lon = mi.get("longitude")
        if isinstance(clk.get("ticksAbs"), int) and isinstance(lon, (int, float)):
            local = (clk["ticksAbs"] + int(round(lon / 360.0 * 60000))) % 60000
            add = (12 * 2500 - local) % 60000
            if add:
                self.call("jawa/time_set_ticks", ticks=clk["ticksGame"] + add, timeException=True,
                          why="Pyrelands review map: noon pin for the look, nothing simulated")
        self.call("jawa/incident_queue_clear")
        self.peaceful = B.call("jawa/storyteller_swap", difficultyDef="Peaceful").get("success")
        RM.sweep_pawns(B)
        self.call("jawa/research_bulk", mode="finish_all")
        self.call("rimworld/set_god_mode", enabled=True)
        self.call("jawa/screenshot_mode", enabled=False)
        self.call("jawa/map_fire", action="extinguish", rect="0,0,%d,%d" % (MAP_SIZE, MAP_SIZE))

    def region(self, S):
        return region_rect(S)

    def clear(self, S):
        """Wipe the gallery region and the free area: labels, every thing, deep ash, unfogged, unroofed. A colonist
        standing inside is walked out first; if one is still inside after that, it refuses (destroy_batch would take
        him)."""
        B = self.B
        B.call("jawa/review_label", action="clear", tag=TAG)
        for rect in (self.region(S), FREE["rect"]):
            rr = "%d,%d,%d,%d" % rect
            pw = [p for p in B.call("jawa/list_pawns", rect=rr, limit=200).get("pawns") or []
                  if p.get("isPlayer") and p.get("intelligence") == "Humanlike"]
            if pw:
                ids = ",".join(str(p.get("id")) for p in pw)
                B.call("jawa/order_pawn", pawnId=ids, x=125, z=140)
                self.notes.append("colonists %s stood in %s: walked out first" % (ids, rr))
                self.ticks(600)
                if [p for p in B.call("jawa/list_pawns", rect=rr, limit=200).get("pawns") or []
                        if p.get("isPlayer") and p.get("intelligence") == "Humanlike"]:
                    raise SystemExit("a colonist is still inside %s after the walk: not clearing it" % rr)
            for p in B.call("jawa/list_pawns", rect=rr, limit=300).get("pawns") or []:
                if not (p.get("isPlayer") and p.get("intelligence") == "Humanlike"):
                    B.call("jawa/set_pawn_faction", pawn=str(p.get("id")), faction="none")
            B.call("jawa/destroy_batch", rects=rr, categories="All")
            B.call("jawa/set_terrain_batch", ops="%s:%s" % (ASH, rr))
            B.call("jawa/set_fog", action="unfog", rect=rr)
            B.call("jawa/set_roof_batch", ops="None:" + rr)
            for area in ("home", "roof"):
                B.call("jawa/paint_area", area=area, ops=rr, value=False)
        RM.sweep_pawns(B)

    def ticks(self, n):
        """Advance through jawa/safe_advance (stops on a hurt or downed colonist). A STOP is respected and recorded; only
        a companion without the tool falls back to plain stepping."""
        r = self.B.call("jawa/safe_advance", action="start", ticks=n, timeoutMs=180000)
        state = r.get("state")
        if r.get("success") and state == "done":
            return r
        self.notes.append("safe_advance %d: state %s (%s)" % (n, state, json.dumps(r)[:240]))
        if state in ("stopped", "aborted", "cancelled", "refused", "running"):
            return r
        return self.B.ticks(n)

    # ---- the shelter
    def shelter(self):
        x, z, w, h = FREE["shelter"]
        self.call("jawa/make_empty_room", rect="%d,%d,%d,%d" % (x, z, w, h), wallDef="Wall", stuffDef=WALL_STUFF,
                  doorDef="Door", floorDef="WoodPlankFloor", roofDef="RoofConstructed")
        top = z + h - 1
        # coolers in the north wall, rot 0: the cold side (South.RotatedBy(rot)) faces into the room
        self.call("jawa/build_batch", ops="Cooler:%d,%d,0;Cooler:%d,%d,0" % (x + 3, top, x + 7, top), faction="player",
                  wipeExisting=True)
        if not self.B.call("jawa/list_things", defName="Door", rect="%d,%d,%d,%d" % (x, z, w, h), limit=2).get("things"):
            # make_empty_room puts its door on a random edge cell: a cooler may have taken it
            self.call("jawa/build_batch", ops="Door:%d,%d" % (x + w // 2, z), stuff=WALL_STUFF, faction="player",
                      wipeExisting=True)
            self.notes.append("shelter door re-made at the south wall (a cooler took the random one)")
        # two batteries side by side (one net), the panel touching the east one; no conduit anywhere: the coolers join
        # the net by their own connector wire (vanilla PowerConnectionMaker links a consumer to a transmitter <= 6 cells)
        self.call("jawa/build_batch", ops="Battery:%d,%d,0;Battery:%d,%d,0" % (x + 4, top + 2, x + 5, top + 2),
                  faction="player", wipeExisting=False)
        self.call("jawa/build_batch", ops="SolarGenerator:%d,%d" % (x + 7, top + 3), faction="player", wipeExisting=False)
        for bx in (x + 4, x + 5):
            for t in self.B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % (bx, top + 2), limit=3).get("things") or []:
                self.call("jawa/battery_set", thing=str(t.get("id") or t.get("thingId")), mode="setPct", value=1.0)
        self.call("jawa/room_heat", x=x + w // 2, z=z + h // 2, mode="set", value=21.0)
        fx, fz, fw, fh = FREE["rect"]
        stock = [("Steel", 75), ("WoodLog", 75), ("BlocksGranite", 75), ("ComponentIndustrial", 20), ("RM_GlassSand", 60),
                 ("MealSurvivalPack", 20), ("MedicineIndustrial", 10), ("RM_FE_FirefoamSprayer", 1), ("RM_FE_FirefoamSprayer", 1)]
        for i, (d, n_) in enumerate(stock):
            self.call("rimworld/spawn_thing", defName=d, stackCount=n_, x=fx + 2 + 2 * i, z=fz + 1)

    def colonists_in(self):
        x, z, w, h = FREE["shelter"]
        cx, cz = x + w // 2, z + h // 2
        rows = self.B.call("jawa/list_pawns", faction="player", limit=50).get("pawns") or []
        ids = [str(p.get("id")) for p in rows if p.get("intelligence") == "Humanlike" and not p.get("dead")]
        if ids:
            self.call("jawa/order_pawn", pawnId=",".join(ids), x=cx, z=cz)
        return ids

    def draft_in(self, ids):
        x, z, w, h = FREE["shelter"]
        inside = [str(p.get("id")) for p in self.B.call("jawa/list_pawns", rect="%d,%d,%d,%d" % (x + 1, z + 1, w - 2, h - 2),
                                                        limit=50).get("pawns") or [] if p.get("isPlayer")]
        for pid in ids:
            self.call("jawa/set_draft", pawnId=pid, drafted=True)
        out = sorted(set(ids) - set(inside))
        if out:
            self.notes.append("colonists not inside the shelter after the walk: %s" % out)
        return inside

    # ---- the gallery
    def build(self, S):
        for s in S:
            ox, oz = s["origin"]
            u = s["setup"]
            g = lambda x, z: (ox + x, oz + z)  # noqa: E731
            if u.get("ring"):
                self.call("jawa/set_terrain_batch", ops=";".join("%s:%d,%d,%d,%d" % ((FIREBREAK,) + g(x, z) + (w, h))
                                                                  for x, z, w, h in ring_cells(s)))
            terr = ["%s:%d,%d,%d,%d" % ((d,) + g(x, z) + (w, h)) for d, x, z, w, h in u.get("terrain", [])]
            if terr:
                self.call("jawa/set_terrain_batch", ops=";".join(terr))
            if u.get("room"):
                x, z, w, h = u["room"]
                self.call("jawa/make_empty_room", rect="%d,%d,%d,%d" % (g(x, z) + (w, h)), wallDef="Wall",
                          stuffDef=WALL_STUFF, doorDef="Door", floorDef=ASH, roofDef="RoofConstructed")
            for d, x, z, rot, stuff in u.get("build", []):
                kw = dict(ops="%s:%d,%d" % ((d,) + g(x, z)) + ("" if rot is None else ",%d" % rot), faction="player",
                          wipeExisting=False)
                if stuff:
                    kw["stuff"] = stuff
                r = self.call("jawa/build_batch", **kw)
                if r.get("survived") == 0:
                    self.notes.append("station %d: %s not built %s" % (s["n"], d, (r.get("failed") or [])[:1]))
            for d, x, z, w, h in u.get("roof", []):
                self.call("jawa/set_roof_batch", ops="%s:%d,%d,%d,%d" % ((d,) + g(x, z) + (w, h)))
            for d, x, z, n_ in u.get("spawn", []):
                self.call("jawa/spawn_batch", ops="%s:%d,%d,%d" % ((d,) + g(x, z) + (n_,)))
            for d, n_, x, z in u.get("items", []):
                self.call("rimworld/spawn_thing", defName=d, stackCount=n_, x=ox + x, z=oz + z)
        self.say("gallery: %d stations laid" % len(S))

    def plant(self, S, which):
        """which: 'fire' plants the pads that burn (before the burn), 'rest' everything else (after it)."""
        for s in S:
            u = s["setup"]
            burns = bool(u.get("burn"))
            if (which == "fire") != burns:
                continue
            ox, oz = s["origin"]
            for k, op in enumerate(u.get("plants", [])):
                d, x, z, w, h, growth = op[:6]
                dens = op[6] if len(op) > 6 else 1.0
                seed = op[7] if len(op) > 7 else s["n"]
                # only a station's FIRST planting clears: set_plants clearFirst wipes the WHOLE rect, so a second
                # overlapping mix (ember then quick) used to replace the first (the ground-cover mix showed quickgrass only, L2)
                r = self.call("jawa/set_plants", ops="%s:%d,%d,%d,%d" % (d, ox + x, oz + z, w, h), growth=growth,
                              density=dens, seed=seed, clearFirst=(k == 0))
                if r.get("planted") == 0:
                    self.notes.append("station %d: set_plants %s planted 0 (%s)" % (s["n"], d, r.get("rejectionReasons")))

    def pawns(self, S):
        for s in S:
            ox, oz = s["origin"]
            for kind, x, z, n_ in s["setup"].get("pawns", []):
                if s["setup"].get("facings"):
                    ops = []
                    for i in range(n_):
                        fx, fz = FACING_SPOTS[i % len(FACING_SPOTS)]
                        if i >= len(FACING_SPOTS):
                            fx, fz = fx + 1, fz - 1
                        ops.append("id=s%d_%d|kind=pawn|x=%d|z=%d|def=%s|rot=%s|faction=none"
                                   % (s["n"], i, ox + fx, oz + fz, kind, FACINGS[i % 4]))
                    r = self.call("jawa/artboard_stage", phase="subjects", ops="\n".join(ops), killHostiles=False,
                                  pause=True)
                    for i, o in enumerate(r.get("ops") or []):   # male/female alternate where the race has sexes
                        if not (o.get("ok") and o.get("thingId")):
                            continue
                        g = ((self.call("jawa/pawn_get", pawn=str(o["thingId"])).get("pawns") or [{}])[0]).get("gender")
                        if g in ("Male", "Female"):     # a race without sexes ("None") is left alone
                            self.call("jawa/set_pawn_gender", pawn=str(o["thingId"]), gender=("Male", "Female")[i % 2])
                    bad = [o for o in (r.get("ops") or []) if not o.get("ok")]
                    if bad or not r.get("ops"):
                        self.notes.append("station %d: facings %s refused %s" % (s["n"], kind, json.dumps(bad or r)[:200]))
                    continue
                r = self.call("jawa/spawn_pawn", kindDef=kind, x=ox + x, z=oz + z, faction="none", count=n_)
                if not (r.get("pawns") or r.get("id") or r.get("pawnId")):
                    self.notes.append("station %d: no %s spawned (%s)" % (s["n"], kind, json.dumps(r)[:160]))

    def pens(self, S, release):
        """Release (end the pinning 60000-tick Wait job, so they wander in their pens) or re-pin every pen animal.
        Returns the tool's reply; a selection that changes nobody is reported, never read as success."""
        if release:
            return self.call("jawa/pen_release", rects=pen_rects(S))
        return self.call("jawa/pen_pin", rects=pen_rects(S), restore=True)

    def burn(self, S, phase):
        rects = []
        for s in S:
            b = s["setup"].get("burn")
            if b and b[0] == phase:
                ox, oz = s["origin"]
                x, z, w, h = b[1]
                rr = "%d,%d,%d,%d" % (ox + x, oz + z, w, h)
                r = self.call("jawa/map_fire", action="start", rect=rr, fireSize=1.2)
                if not r.get("firesStarted"):
                    self.notes.append("station %d: map_fire started no fire in %s (%s)" % (s["n"], rr, json.dumps(r)[:160]))
                rects.append((s["n"], rr))
        return rects

    def put_out(self, rects):
        for n, rr in rects:
            ox, oz, w, h = [int(v) for v in rr.split(",")]
            self.call("jawa/map_fire", action="extinguish", rect="%d,%d,%d,%d" % (ox - 2, oz - 2, w + 4, h + 4))

    def keep_rects(self, S):
        return [footprint(s) for s in S if s["setup"].get("keep")]

    def find_ruin(self, S):
        """The nearest non-player BuildingArtificial whose cell, board book (z+2) and label (z+3) all clear the gallery,
        the free area and the natural window: the scorched-ruin board."""
        rows = self.B.call("jawa/list_things", group="BuildingArtificial", limit=2000).get("things") or []
        reg = self.region(S)
        best = None
        for t in rows:
            if t.get("faction") or (t.get("def") or t.get("defName")) in ("SteamGeyser", "VHGE_GasGeyser"):
                continue
            pos = t.get("position") or t.get("pos") or {}
            x, z = RM.pawn_xz({"position": pos}) if pos else (t.get("x"), t.get("z"))
            # its board book (z+2) and label (z+3) must clear the gallery, the free area and the natural window too
            if x is None or z is None or z + 4 >= MAP_SIZE or any(
                    _overlap(r, (x - 1, z - 1, 3, 6)) for r in (reg, FREE["rect"], NATURAL["rect"])):
                continue
            d = (x - 125) ** 2 + (z - 125) ** 2
            if best is None or d < best[0]:
                best = (d, x, z, t.get("def") or t.get("defName"))
        if best is None:
            self.notes.append("no ruin found on the map: board R has no target")
            return None
        return [best[1], best[2], best[3]]

    def verify_all(self, S):
        B = self.B
        ok = blind = 0
        for s in S:
            u = s["setup"]
            rr = "%d,%d,%d,%d" % footprint(s)
            things = B.call("jawa/list_things", rect=rr, limit=600)
            got = {t.get("def") or t.get("defName") for t in things.get("things") or []}
            if not got and things.get("perDef"):
                got = set(things["perDef"])
            pw = B.call("jawa/list_pawns", rect=rr, limit=50).get("pawns") or []
            kinds = [p.get("kind") or p.get("kindDef") for p in pw]
            terr = {}
            if u.get("expect_terrain"):
                terr = ops_counts(B.call("jawa/get_terrain_batch", rects=rr).get("ops"))
                if not terr:
                    blind += 1
            want_kinds = [k for k, _x, _z, n_ in u.get("pawns", []) for _ in range(n_)]
            good = station_verdict(u.get("expect_things", []), got, want_kinds, kinds, u.get("expect_terrain", {}), terr)
            pr = {}
            for kind, x, z, label in u.get("probes", []):
                cx, cz = s["origin"][0] + x, s["origin"][1] + z
                if kind == "fert":
                    r = B.call("jawa/static_call", type="RimMandrake.Pyrelands.MapComponent_PyrelandsAshField",
                               method="ProbeCell", args="%d,%d" % (cx, cz))
                    kv = parse_kv(r.get("result"))
                    pr[label] = {k: kv.get(k) for k in ("terrain", "fertility", "bonus", "watered", "burnTick")} if kv \
                        else "UNMEASURED: %s" % str(r)[:120]
                else:
                    r = B.call("jawa/cell_temperature", cell="%d,%d" % (cx, cz))
                    pr[label] = r.get("temperature", r.get("tempC", "UNMEASURED: %s" % str(r)[:120]))
            self.verify[s["n"]] = dict(ok=good, missing=[d for d in u.get("expect_things", []) if d not in got],
                                       pawns=sorted(map(str, kinds)), want_pawns=sorted(want_kinds),
                                       terrain={k: terr.get(k) for k in u.get("expect_terrain", {})}, probes=pr)
            ok += good is True
            blind += good is None
        self.say("verified: %d of %d stations as built" % (ok, len(S)))
        return ok, blind

    def labels(self, S, weather, ruin):
        self.B.call("jawa/review_label", action="clear", tag=TAG)
        r = self.B.call("jawa/review_label", action="add", ops=label_ops(S, weather, ruin), tag=TAG)
        if not r.get("success"):
            self.notes.append("labels: %s" % json.dumps(r)[:300])
        return r

    def chill(self, S):
        """Set the room temperature of every station with setup 'chill' (the furnace-beast pen and its control pen)."""
        for s in S:
            c = s["setup"].get("chill")
            if c is not None:
                ox, oz = s["origin"]
                self.call("jawa/room_heat", x=ox + 3, z=oz + 3, mode="set", value=float(c))

    def goto(self, S, which, ruin=None):
        w = which.upper()
        if w == "F":
            x, z, ww, h = FREE["rect"]
        elif w == "N0":
            x, z, ww, h = NATURAL["rect"]
        elif w == "R":
            if not ruin:
                raise SystemExit("--goto R: no ruin recorded (build first)")
            x, z, ww, h = ruin[0] - 8, ruin[1] - 8, 16, 16
        elif w == "0":
            x, z, ww, h = region_rect(S)
        else:
            s = next((s for s in S if str(s["n"]) == which), None)
            if s is None:
                raise SystemExit("--goto %s: unknown; valid: F, N0, R, 0, 1..%d" % (which, len(S)))
            x, z, ww, h = s["origin"][0] - 2, s["origin"][1] - 2, SW + 4, SH + 5
        return self.B.call("rimworld/frame_cell_rect", x=x, z=z, width=ww, height=h, paddingCells=2)


def read_state():
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def write_state(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=1, default=str)


# ------------------------------------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--load", default=None, help="save to load from the main menu first (an NS_Pyrelands_site_* fixture)")
    ap.add_argument("--goto", default=None)
    ap.add_argument("--labels", action="store_true")
    ap.add_argument("--clear", action="store_true")
    ap.add_argument("--weather", choices=WEATHERS, default=None)
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--signs", action="store_true", help="re-place the in-save sign books (live)")
    ap.add_argument("--signs-for", default=None, metavar="SAVE",
                    help="offline: write the sign sidecar for an existing keeper SAVE (no game needed)")
    ap.add_argument("--release-pens", action="store_true",
                    help="live: end every pen animal's pinning Wait job so it wanders in its pen (unpause to watch)")
    ap.add_argument("--pin-pens", action="store_true",
                    help="live: pin the pen animals again, back on their release cell and facing where known")
    ap.add_argument("--name", default="RM_pyre_review_%s" % time.strftime("%Y%m%d"))
    ap.add_argument("--log", default=os.path.join(REPO, "Transient", "pyre_review_map_build_log.md"))
    a = ap.parse_args(argv)
    if a.release_pens and a.pin_pens:
        ap.error("give one of --release-pens / --pin-pens")
    S = station_list()
    probs = layout_check(S, known_defs(S) if a.plan else None) + coverage_check(S)
    if probs:
        print("LAYOUT PROBLEMS:\n  " + "\n  ".join(probs))
        return 2
    if a.signs_for:
        st = read_state()
        print("signs -> %s" % RM.write_signs(a.signs_for, label_ops(S, st.get("weather", "Clear"), st.get("ruin"))))
        return 0
    if a.plan:
        keysheet(S)
        write_coverage(S)
        nost = sum(1 for f in FEATURES if not f[3])
        print("layout ok: %d stations + %d boards; %d features (%d with no station, each with its reason); "
              "KEYSHEET + COVERAGE -> %s; keysheet.html -> %s" % (len(S), len(BOARDS), len(FEATURES), nost, REVIEW, HTML_OUT))
        return 0
    st = read_state()
    R = Review(RM.LiveBridge(), a.log if a.build else None)
    if a.clear:
        R.clear(S)
        print("cleared")
        return 0
    rc = 0
    if a.build:
        t0 = time.time()
        if a.load:
            R.say("loading %s" % a.load)
            R.load(a.load)
        mi = R.require_site()
        R.call("jawa/clear_ui", all=True)
        R.calm(mi)
        R.say("calm world (peaceful=%s)" % R.peaceful)
        R.clear(S)
        R.say("cleared")
        R.shelter()
        ids = R.colonists_in()
        R.build(S)
        R.plant(S, "fire")
        R.pawns(S)
        R.say("pawns placed; burning the AFTER pads for %d ticks" % BURN_TICKS)
        lit = R.burn(S, "after")
        R.ticks(BURN_TICKS)
        R.put_out(lit)
        R.plant(S, "rest")
        R.sweep_keep = RM.sweep_pawns(R.B, R.keep_rects(S))
        inside = R.draft_in(ids)
        R.call("jawa/room_heat", x=FREE["shelter"][0] + 5, z=FREE["shelter"][1] + 4, mode="set", value=21.0)
        R.chill(S)
        now = R.burn(S, "now")
        R.ticks(NOW_TICKS)
        R.call("rimworld/pause_game", pause=True)
        ruin = R.find_ruin(S)
        n_ok, blind = R.verify_all(S)
        weather = "Clear"
        R.labels(S, weather, ruin)
        sg = RM.place_signs(R.B, sign_ops(S, ruin))
        if not sg.get("success") or sg.get("count") != len(sign_ops(S, ruin)):
            R.notes.append("signs: %s" % json.dumps({k: sg.get(k) for k in ("count", "refused", "message")})[:300])
        R.B.call("jawa/clear_ui", all=True)
        R.goto(S, "0")
        chilled = {s["n"]: R.verify.get(s["n"], {}).get("probes", {}).get("room") for s in S
                   if s["setup"].get("chill") is not None}
        R.say("chilled pens after %d ticks (station: C): %s" % (NOW_TICKS, chilled))
        R.chill(S)   # re-chill: four furnace-beasts warm their pen ~11 C in those ticks; the save starts both at CHILL_C
        live = dict(stations_ok=n_ok, verify=R.verify, notes=R.notes, ruin=ruin, colonists=ids, in_shelter=inside,
                    chilled_pens_c=chilled,
                    burned=lit, burning_now=now, wall_s=round(time.time() - t0, 1))
        st.update(ruin=ruin, weather=weather, live=live)
        write_state(st)
        keysheet(S, live, weather=weather)
        rc, vtxt = build_exit(n_ok, len(S), blind)
        R.say("DONE in %ss; %s; %d notes (%s)" % (live["wall_s"], vtxt, len(R.notes), STATE))
        if not a.save:
            return rc
    if a.weather:
        R.call("jawa/weather_set", unlock=True)
        R.call("jawa/weather_set", weather=a.weather, lockWeather=True)
        st["weather"] = a.weather
        write_state(st)
        R.labels(S, a.weather, st.get("ruin"))
        print("weather locked to %s (unpause to see it fall)" % a.weather)
    if a.save:
        R.call("rimworld/pause_game", pause=True)
        R.B.call("jawa/clear_ui", all=True)
        name = RM.free_save_name(a.name, RM.saves_stat())
        r = RM.save_keeper(R.B, name, signs=label_ops(S, st.get("weather", "Clear"), st.get("ruin")))
        print("save %s: ok=%s new=%s changed=%s gone=%s signs=%s" % (name, r["ok"], r["new"], r["changed"], r["gone"],
                                                                     r.get("signs")))
        if r["ok"]:
            keysheet(S, st.get("live"), save=name, weather=st.get("weather", "Clear"))
        return rc if r["ok"] else 1
    if a.release_pens or a.pin_pens:
        r = R.pens(S, a.release_pens)
        keys = ("selected", "released", "notReleased", "pinned", "returnedHome", "jobsAfter", "message")
        print("%s pens (%d): %s; skipped %d" % ("release" if a.release_pens else "pin", len(pen_stations(S)),
                                               {k: r.get(k) for k in keys if k in r}, len(r.get("skipped") or [])))
        if not r.get("success"):
            rc = 1
    if a.signs:
        r = RM.place_signs(R.B, sign_ops(S, st.get("ruin")))
        print("signs: %s" % {k: r.get(k) for k in ("count", "refused", "message")})
    if a.labels:
        r = R.labels(S, st.get("weather", "Clear"), st.get("ruin"))
        print("labels: %s" % {k: r.get(k) for k in ("added", "refused", "count")})
    if a.goto:
        print("framed %s: %s" % (a.goto, R.goto(S, a.goto, st.get("ruin")).get("success")))
    return rc


if __name__ == "__main__":
    sys.exit(main())
