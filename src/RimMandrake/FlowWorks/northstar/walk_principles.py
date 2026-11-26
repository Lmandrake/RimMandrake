"""walk_principles.py -- what the FlowWorks walk map must show, one plain thing per principle (pure data).

Page: design/concepts/FlowWorks/version/walk_brief/station_principles.md (the same list in prose, with the map of the old
79 stations). The walk map builder (walk_map.py) gives every station exactly one principle id (`shows`); the check
`python3 src/RimMandrake/FlowWorks/review_map_coverage.py walk` reads both and fails on a principle with no station, a
station with no principle, a locked bar that a look can judge with no principle, or a sign that still carries a code name.

Each principle is a thing FlowWorks 0.1.0 must do that a person can judge by a look or by one act in the game, taken from
the locked bars (design/concepts/FlowWorks/version/locked_bars.json) and the vision, never from the old station list.
Fields: id, group (the map area it stands in), title (one plain line), do (what the owner does), see (what he must see),
bars (the locked bar ids it serves).
"""

GROUPS = (
    ("holes", "Holes and how deep they read"),
    ("water", "Water and other liquids in holes"),
    ("gates", "Gates and the moat"),
    ("pits", "Pits: traps and the ways in and out"),
    ("bridges", "Bridges"),
    ("fire", "Fire"),
    ("pipes", "Pipes, hoses and sprinklers"),
)

PRINCIPLES = (
    dict(id="depth_reads", group="holes", title="How deep a dry hole is reads from its walls",
         do="Look along the six dry holes, from 0.5 m to 8 m.",
         see="Each deeper hole shows a taller wall face. The colonist in each stands lower, more hidden by the near edge.",
         bars=("inv_dig_depth", "pit_reads_as_hole", "canal_reads_as_dug", "pawn_height_follows_depth", "inv_looks")),
    dict(id="complex_pit", group="holes", title="In one very large pit, every shape and which floor is higher reads from the drawing alone",
         do="Look at the large pit. West of the wall of ground in its middle it is dry; east of it the same shapes hold water.",
         see="Steps, an island, a peninsula, a pillar, an inner pit, a notch, a diagonal edge, inside and outside corners and "
             "a narrow ridge, each readable; a higher floor always reads higher. In the east half the water covers the deep "
             "floors and leaves the high floors dry, at one level.",
         bars=("pit_reads_as_hole", "canal_reads_as_dug", "one_still_surface", "fill_level_legible", "inv_looks")),
    dict(id="dig_yourself", group="holes", title="You dig a hole yourself, and digging takes hours",
         do="Select Dig canal in the Architect menu (FlowWorks) and mark the three squares east of the colonist. Unpause.",
         see="The colonist walks over and digs. Each square takes some hours and opens into a dug channel.",
         bars=("inv_dig_depth",)),
    dict(id="water_depth", group="water", title="How deep the water is reads at a glance",
         do="Look along the row from 0.2 m to 5 m of water, and the dry hole at its end. Mouse over a square to read its depth.",
         see="Deeper water reads deeper, and the mouse-over depth is the depth on the sign.",
         bars=("fill_level_legible", "inv_flow_level", "inv_looks")),
    dict(id="how_full", group="water", title="How full a hole is: the dry wall shows above the water",
         do="Compare the holes: 1 m of water in a 1 m and a 2 m hole; 0.5 m and 1 m of water in a 4 m hole.",
         see="A full hole shows no wall above the water; a part-full hole shows a dry wall band above it.",
         bars=("fill_level_legible", "inv_looks")),
    dict(id="pawn_in_water", group="water", title="A colonist wades in shallow water and swims in deep water",
         do="Look at the two colonists in water. Mouse over each.",
         see="In 1 m of water she wades, cut at the surface; in 2 m she swims.",
         bars=("pawn_height_follows_depth", "inv_swim")),
    dict(id="liquids_apart", group="water", title="Each liquid looks like itself",
         do="Look along the six holes: water, tar, oil, chemfuel, green slime, blood, each 1 m deep.",
         see="You can name each liquid by its look; none reads as water but the water.",
         bars=("fill_level_legible", "inv_liquid_roster", "inv_looks")),
    dict(id="flow_from_pond", group="water", title="Water runs from a pond into what you dug, and the pond pays for it",
         do="Select the shut sluice between the pond and the dry canal and open it. Unpause.",
         see="Water runs along the canal and fills the dry pit at its end. The pond drops and its edge pulls back. No water "
             "spills onto the banks.",
         bars=("fill_flows_along_canal", "source_pays_and_refills", "no_liquid_on_open_ground", "no_full_source_after_draw",
               "inv_flow_level", "inv_stock")),
    dict(id="slime_crossing", group="water", title="Slime is thick: a colonist crossing it sinks and slips",
         do="Order each colonist to the far side of the canal in front of her (slime north, water south). Unpause.",
         see="The slime reads thick, not like water. The colonist in slime sinks, slips back on the climb out and takes much "
             "longer than the one in water.",
         bars=("slime_holds_the_crossing", "inv_slime")),
    dict(id="sluice_holds", group="gates", title="A shut sluice holds water on one side; open, it lets the water through",
         do="Look at the two shut sluices (water on one side only) and the open one. Then open a shut one and unpause.",
         see="Shut or open reads at a glance. A shut gate keeps the far side dry; opened, the water runs through.",
         bars=("sluice_drains_on_command", "inv_doors")),
    dict(id="grate_passes", group="gates", title="A grate gate always lets water through",
         do="Look at the two grate gates, east-west and north-south.",
         see="The water stands at one level on both sides of each grate.",
         bars=("sluice_drains_on_command", "inv_doors")),
    dict(id="moat", group="gates", title="The moat: a colonist swims under a raised drawbridge, and the sluice drains it",
         do="Select the shut sluice at the south end of the moat and open it. Unpause.",
         see="The swimmer tires in the deep moat. The moat drains fast into the drain pit, and she ends standing on its floor.",
         bars=("moat_drains_and_burns", "inv_bridges", "inv_swim", "inv_doors")),
    dict(id="ladders", group="pits", title="A wall ladder hangs on its wall, lowered or raised",
         do="Look at the four pits. In each, one wall ladder is lowered and the one on the opposite wall is raised.",
         see="Each ladder hangs on the wall it faces, in all four directions, and lowered reads apart from raised.",
         bars=("ways_in_and_out", "inv_pit_access")),
    dict(id="portable_ladder", group="pits", title="A portable ladder leans on a low wall and is too short for a deep one",
         do="Look at the two portable ladders: in a 2 m pit and in a 4 m pit.",
         see="In the 2 m pit it leans on the wall; in the 4 m pit it is too short and lies flat.",
         bars=("ways_in_and_out", "inv_pit_access")),
    dict(id="climbing_gear", group="pits", title="Climbing gear gets a colonist out of a sheer pit",
         do="Order each colonist out to the ground beside the pit. Unpause.",
         see="The colonist who wears climbing gear climbs the sheer 4 m wall; the one without gear cannot climb the wall and waits for the ladder the colony brings.",
         bars=("ways_in_and_out", "inv_pit_access")),
    dict(id="spikes", group="pits", title="Spikes read as spikes, on a dry floor and under water",
         do="Look at the two spiked pits.",
         see="Sharp stakes on the pit floor, dry in one and standing in 1 m of water in the other.",
         bars=("covered_pit_springs", "inv_pits")),
    dict(id="cover_hides", group="pits", title="A covered pit passes for ground",
         do="Find the covered pit on this station before you read where it is.",
         see="The cover reads as the ground around it, not as a hole.",
         bars=("covered_pit_springs", "inv_pits")),
    dict(id="walk_under_cover", group="pits", title="A colonist walks along a pit floor under a cover, and the cover fades over her",
         do="Order the colonist in the open south end to the open north end of the pit. Unpause.",
         see="She walks under the cover and out again. The cover fades see-through over her, as over the colonist already under it.",
         bars=("inv_pits", "hung_bridge_spans")),
    dict(id="trench_cover", group="pits", title="A colonist in a trench is covered by the ground beside her",
         do="Draft the shooter and aim at the colonist in the trench.",
         see="The hit chance shows cover from the trench wall, waist-deep and chest-deep.",
         bars=("trench_gives_cover", "inv_trench_cover")),
    dict(id="bridge_kinds", group="bridges", title="Each bridge kind reads as what it is made of, laid east-west and north-south",
         do="Look at rope, timber, steel and heavy bridges, with and without railings, the two grated decks, and the same "
            "bridges laid north-south.",
         see="Each bridge reads as its material; a deck hangs between two anchors over a pit; railings show where they are on.",
         bars=("inv_bridges", "hung_bridge_spans")),
    dict(id="jetties", group="bridges", title="A jetty reaches out over a pit from one side",
         do="Look at the steel and heavy jetties, reaching east, north and south.",
         see="Each jetty is one deck rooted on the ground and ending over the pit, not two blocks stuck together.",
         bars=("inv_bridges",)),
    dict(id="bridge_looks", group="bridges", title="The steel bridge in each of the four looks",
         do="Look at the steel bridge in the Scrapper, Industrial, Modern and Futuristic looks, east-west and north-south.",
         see="Four looks that read apart, each a steel bridge.",
         bars=("inv_looks", "inv_bridges")),
    dict(id="walk_under_bridge", group="bridges", title="A colonist walks along a pit under a bridge while another crosses over it",
         do="Order the colonist in the pit to its north end, and the colonist on the west anchor to the east anchor. Unpause.",
         see="One walks under the deck, the other over it, at the same time.",
         bars=("hung_bridge_spans", "inv_bridges")),
    dict(id="tar_fire", group="fire", title="A colonist lights tar under a steel bridge, and the tar burns where it lies",
         do="Select the colonist, right-click a tar square south of the bridge and choose Toss a flame here. Unpause.",
         see="She walks to the edge and tosses the flame; the tar catches and the fire runs under the steel deck; the steel "
             "does not burn. Nothing else burnable stands within 15 squares.",
         bars=("toss_flame_from_rim", "canal_fire_burns_back", "inv_fire", "inv_toss_flame")),
    dict(id="sprinkler_looks", group="pipes", title="A sprinkler sprays from its pipe, in each of the four looks",
         do="Unpause for a moment.",
         see="Each head sprays. The tank, pipe, pump and head of each net share one look: Futuristic, Industrial, Modern, Scrapper.",
         bars=("inv_sprinklers", "inv_looks", "inv_liquid_net")),
    dict(id="hose", group="pipes", title="A hose reads as a thick hose that plumps when water flows",
         do="Look at the hose from the pump to the tank, beside the pipe that feeds the pump.",
         see="The hose is thicker than a power line, with fittings at the reel, and plump while water flows.",
         bars=("hose_reads_as_hose", "inv_hoses")),
    dict(id="geyser_tub", group="water", title="A pit dug on a geyser and filled over the vent is a hot tub",
         do="Mouse over the water of the pit round the geyser.",
         see="The vent bubbles under the water, and the mouse-over reads Hot Tub.",
         bars=("inv_geyser_tub",)),
)

# Locked bars that no walk station decides, each with why (a look or one act cannot judge it on this map).
NOT_ON_THE_WALK = {
    "one_liquid_network": "litres a tester reads, not a look (proved by the hose and network scripts)",
    "no_impossible_plumbing": "a refusal a tester reads, not a look (proved by the network script)",
    "ice_cuts_and_melts": "needs a frozen map; the walk map is warm",
    "river_flows_endless": "needs a river from map generation; the river site is its own map",
    "inv_rivers": "needs a river from map generation; the river site is its own map",
    "drained_hole_is_a_prison": "needs a downed raider; the walk map holds no hostile",
    "inv_prison_no_bed": "needs a downed raider; the walk map holds no hostile",
    "no_snared_standing": "needs a trapped raider; the walk map holds no hostile",
    "island_bridges_trap_and_fail": "needs a winch destroyed under a pawn; proved by the drawbridge scene",
    "walk_moat_season": "a season of play on the full list, not a walk",
    "inv_overflow_sheet": "the overflow sheet ships off",
    "inv_converters": "a machine's litres over time, not a look",
    "inv_bottles_thirst": "thirst over hours, not one act (the thirst scene decides it)",
    "inv_drilling": "needs a subsurface survey map",
    "inv_map_controls": "map-maker tools a player never sees",
    "inv_quarry": "a dig find is random; one dig need not show one",
    "inv_settings": "the Mod Settings screen, not the map",
    "inv_liquid_coating": "not built in this version (record.json: impl absent)",
}


def by_id():
    return {p["id"]: p for p in PRINCIPLES}


def bars_judged():
    """Every locked bar id that some principle serves."""
    return {b for p in PRINCIPLES for b in p["bars"]}
