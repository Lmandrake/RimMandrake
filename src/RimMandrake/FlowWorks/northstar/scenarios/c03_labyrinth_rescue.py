"""C3 - The Labyrinth Rescue (map C, 40x40, look Scrapper): the GSS hose maze grown up, with a stake.

Hobb has fallen into a machine-dug sheer pit (4 m) at the heart of a walled maze; no ladder reaches. Water from the pond
outside, through the maze by hose, into his pit until it is 2 m deep or more, and he swims up. Next door a boar in its
own pit shows what flooding does to a non-swimmer. Design §3 C3; GPT #2 (prove the swim-out first: stage0_swim_pit.py),
GPT #13 (misleading dead end, destination gauge, relay-loop poke).

Route lengths are MEASURED offline by route_len() in the selftest (never typed here): the short way through d1 must
fit one 40-cell hose, the long way (d1 walled) must need the relay and fit two.
"""
from .common import (scenario, staged, deferred, perimeter, walls, hline, vline, W, LPROOF, MAPCTL, DEEP_DIG_ITEM)

SIZE = (40, 40)
REEL_O1 = (6, 30)
HOSE_START = (8, 30)                # the first walkable cell east of the 2x2 reel o1
PIT_LIP = (23, 15)                  # hose end: the room cell on Hobb's pit's north lip
D1 = (22, 25)                       # the short way's door gap (he can wall it)
DEAD_END = (14, 25)                 # the gap that LOOKS shorter (GPT #13)
HOBB_PIT = (22, 13, 2, 2, 8)        # 4 m, sheer, machine-dug
BOAR_PIT = (26, 10, 2, 2, 8)
CHASM = (26, 21, 9, 3, 12)          # 6 m: impassable to walkers and hoses; the long way hugs its north edge (z 24)
RELAY_O2 = (36, 28)

MAZE_WALLS = (perimeter(10, 4, 39, 35, gaps=[(10, 30), (10, 31)])            # outer ring, entry on the west
              + hline(11, 34, 25, gaps=[D1, DEAD_END])                          # W1: north corridor / middle band
              + vline(17, 21, 24) + hline(11, 15, 20)                           # the dead-end pocket's east and south walls
              + perimeter(16, 8, 30, 20, gaps=[(23, 20)]))                      # the pit room, door on the north

SETUP = dict(
    terrain=[("WaterDeep", 0, 26, 5, 8)],                                    # the pond (limited: it shrinks as it pays out)
    dig=[HOBB_PIT, BOAR_PIT, CHASM],
    build=walls(MAZE_WALLS, "Steel")
    + [("RM_LiquidPump", 5, 30, None, None), ("RM_UniversalPipe", 5, 31, None, None), ("RM_LiquidTank", 5, 32, None, None),
       ("PowerConduit", 5, 29, None, None), ("PowerConduit", 5, 28, None, None), ("PowerConduit", 5, 27, None, None),
       ("Battery", 6, 27, 0, None),
       ("RM_HoseReel", 6, 30, None, None),                                    # o1, laid
       ("RM_HoseReel", 36, 28, None, None),                                   # o2, the relay, wound
       ("RM_AerialMast", 18, 26, None, None), ("RM_AerialMast", 18, 34, None, None)]   # the GSS wire span over the corridor
    # reel park (south-west strip): one reel per look, laid plump / filling / flat, one wound; a deploy order; a dropped carry
    + [("RM_HoseReel", 1, z, None, None) for z in (3, 7, 12, 17, 22)] + [("RM_HoseReel", 12, 0, None, None)]
    # three reels TURNED (reels turn 4 ways since 73b8805755; the park's reels face west): north, east, south, so he
    # judges the turned views (north/south = the west art turned until he picks drawn views, REEL_FACINGS_*)
    + [("RM_HoseReel", 27, 1, 0, None), ("RM_HoseReel", 31, 1, 1, None), ("RM_HoseReel", 35, 2, 2, None)],
    style=[("RM_HoseReel", 1, z, "RM_HoseReel_" + lk) for z, lk in zip((3, 7, 12, 17), ("Scrapper", "Industrial", "Modern",
                                                                                          "Futuristic"))]
    + [("RM_HoseReel", 6, 30, "RM_HoseReel_Scrapper"), ("RM_HoseReel", 36, 28, "RM_HoseReel_Scrapper")],
    batteries=[(6, 27)],
    tank=[(5, 32, "Store", "RM_Liquid_FreshWater", 4000)],
    pump=[(5, 30, "draw")],
    hose=[(6, 30, PIT_LIP[0], PIT_LIP[1], None),                              # o1 the short way; free end stays Capped
          (1, 3, 8, 3, None), (1, 7, 8, 7, None), (1, 12, 8, 12, None)],
    hose_flow=[(6, 30, "Plump"), (1, 3, "Plump"), (1, 7, "Filling")],
    hose_order=[(1, 22, 8, 22)],
    hose_trail=[(12, 0, [(x, 1) for x in range(14, 25)])],
    pawns=[("Colonist", 22, 13, "player", "drafted"),                          # Hobb: drafted, so no needs drift
           ("WildBoar", 26, 10, "none", None),
           ("Colonist", 5, 24, "player", "drafted")],                          # the deploy-order walker (undraft = Start)
    pawn_ops=[(22, 13, "name", "Hobb")],
    markers=[("PlaceMeter", 23, 13, "")],                                      # destination gauge on Hobb's pit floor
    keep=True,
)

SCENARIO = scenario(
    id="C3", n=3, slug="labyrinth_rescue", name="The Labyrinth Rescue", map="C", size=SIZE, look_style="Scrapper",
    purpose="Hobb is in a 4 m sheer pit in the middle of a maze. Float him out: pond water, by hose, through the maze.",
    start="press reel o1's 'Free end' button until it reads Outflow, then unpause",
    try_=["START: reel o1 > Free end: Outflow; unpause: the pond shrinks, Hobb's pit fills; at 2 m he swims but is still "
          "2 m below the lip; only near the BRIM (4 m of water) can he swim out (Stage 0 live, 2026-10-21: "
          "PASS_AT_BRIM). Select the meter on the pit floor: litres in.",
          "BEFORE that: wall the gap d1 (the short way): the hose must re-route the long way (over 40 cells): it reels in "
          "with a message naming the cells needed; fix it by laying onto relay reel o2",
          "lay o2's hose back onto o1: refused (a relay chain may not loop)",
          "try a portable ladder into Hobb's pit: refused, too deep (3 m reach) - that is why the maze exists",
          "move o1's hose end to the boar's pit instead: the boar starts drowning (a non-swimmer); draft and cancel",
          "cut the pump's power: the hose goes flat; rotate the pump: the hose follows the port",
          "reel park (west): choose a style, undraft the colonist to deploy one by hand, retract one; TURN a reel "
          "(rotate it): the outlet and the hose follow, four ways (north/south art is the west art turned for now)"],
    look_for="the hose takes the SHORT way through d1 and passes UNDER the wire span; litres out of the pond = litres "
             "into the pit; Hobb rises with the water and leaves only when it nears the brim; an EMPTY hose (the dropped "
             "carry) casts a darker, wider shadow than a full one",
    broken="the hose through a wall, over the chasm or on top of the wire span; the long way chosen while d1 is open; "
           "a hose that never plumps; Hobb standing on the floor under 2 m of water; the boar swimming; a relay loop "
           "accepted",
    idle="pump on and Drawing into a tank, hose Plump, but o1's free end is Capped: nothing leaves the hose until he "
         "sets Outflow; Hobb and the walker are drafted; the boar is penned by its pit",
    setup=SETUP,
    parts=[(D1[0], D1[1] + 1, "d1 short way (wall it?)"), (DEAD_END[0], DEAD_END[1] + 1, "dead end (looks shorter)"),
           (6, 33, "reel o1"), (RELAY_O2[0], RELAY_O2[1] + 2, "relay o2"), (22, 16, "Hobb (trapped, 4 m)"),
           (26, 12, "boar pit"), (30, 22, "chasm 6 m"), (18, 35, "wire span overhead"), (2, 34, "pond"),
           (5, 25, "pump power"), (23, 12, "meter"), (3, 5, "plump"), (3, 9, "filling"), (3, 14, "flat"),
           (3, 19, "wound"), (3, 24, "deploy order"), (18, 2, "dropped carry"), (31, 3, "turned reels: N  E  S")],
    pieces=[staged("pond (limited)", "terrain", "WaterDeep", (0, 26)),
            staged("pump on the pond edge, Drawing", "pump", "draw", (5, 30)),
            staged("small tank beside the pump", "tank", "Store", (5, 32)),
            staged("battery, charged", "batteries", None, (6, 27)),
            staged("reel o1 laid the short way, Plump, end Capped", "hose", None, REEL_O1, "poked"),
            staged("maze walls (Steel)", "build", "Wall", (10, 4), "look"),
            staged("door gap d1 (short way)", "build", "Wall", (21, 25), "poked", "the gap is the cell east of this wall"),
            staged("misleading dead end", "build", "Wall", (17, 22), "look"),
            staged("Hobb's pit 2x2, 4 m sheer", "dig", None, (22, 13)),
            staged("Hobb, drafted, in his pit", "pawns", "Colonist", (22, 13), "poked"),
            staged("boar's pit 2x2, 4 m", "dig", None, (26, 10)),
            staged("boar (non-swimmer)", "pawns", "WildBoar", (26, 10), "poked"),
            staged("chasm (impassable, 6 m)", "dig", None, (26, 21), "look"),
            staged("GSS wire span on two masts (auto-linked by GSS)", "build", "RM_AerialMast", (18, 26), "look"),
            staged("relay reel o2, wound", "build", "RM_HoseReel", RELAY_O2, "poked"),
            staged("destination gauge (flow meter) in Hobb's pit", "markers", "PlaceMeter", (23, 13)),
            staged("reel park: four looks", "style", None, (1, 3), "look"),
            staged("three reels turned north / east / south", "build", "RM_HoseReel", (27, 1), "look"),
            staged("reel park: deploy order + walker", "hose_order", None, (1, 22), "poked"),
            staged("reel park: dropped carry", "hose_trail", None, (12, 0), "look"),
            deferred("pump power as a GSS power cord", "a vanilla conduit stands in: no staging surface lays an "
                     "RM_PowerCord from a script yet", "POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS", (1, 37)),
            staged("swim-out of a flooded sheer pit (Stage 0 live: out only at the brim)", "pawns", "Colonist",
                   (22, 13), "poked", "Stage 0 live 2026-10-21: 2 m FAIL, brim PASS (PASS_AT_BRIM)"),
            deferred("machine digging Hobb's pit", "4 m is past the 2 m colonist cap (owner 2026-10-21); the pit is "
                     "staged, a machine dig order is not built", DEEP_DIG_ITEM, (7, 37))],
    exercises={"hose_maze": "poked", "hose_maze_walled": "poked", "hose_relay": "poked", "hose_states": "look",
               "hose_reel": "look", "hose_styles": "look", "hose_reels_laid": "look", "hose_deploy_by_hand": "poked",
               "hose_dropped": "look", "hose_into_pond": "poked", "pit_flood": "poked", "pump_pour": "poked",
               "flow_shrinks": "poked", "hose_plump_when_flowing_flat_when_not": "poked",
               "hose_plumps_only_from_powered_pump": "poked", "hose_carries_real_units": "poked",
               "hose_dropped_carries_nothing": "look", "hose_follows_port_changes": "poked",
               "hose_joiner_reads_brass_screwed_together": "look", "reel_hose_leaves_brass_outlet_nozzle": "look",
               "reel_laid_and_wound_look_differ": "look", "reel_offers_choose_style": "poked",
               "four_reel_looks_distinguishable": "look", "relay_chain_carries_liquid": "poked",
               "relay_chain_reads_connected": "look", "never_hose_across_impassable": "look",
               "hose_drawn_under_overhead_span": "look", "pump_hose_joins_at_side_port": "look",
               "hose_thicker_stiffer_than_cord": "look", "deep_water_pawn_swims": "poked",
               "pit_trapped_reads_as_trapped": "look", "reservoir_fill_visibly_drops": "poked"},
    goal="route lengths: short way (d1 open) <= 40 cells, long way (d1 walled) > 40 and <= 80; live: ProofReadout on "
         "Hobb's pit for litres-to-2 m, never typed",
    prove_first="stage0_swim_pit",
)

# offline goal read (selftest and --plan): the cells a hose may not cross
BLOCKED = set(MAZE_WALLS) | {(x, z) for r in (HOBB_PIT, BOAR_PIT, CHASM) for x in range(r[0], r[0] + r[2])
                             for z in range(r[1], r[1] + r[3])} \
    | {(x, z) for x in range(0, 5) for z in range(26, 34)} | {(5, 30), (5, 31), (5, 32), (6, 32), (5, 33), (6, 33)} \
    | {(6, 30), (7, 30), (6, 31), (7, 31), (36, 28), (37, 28), (36, 29), (37, 29), (18, 26), (18, 34)}
