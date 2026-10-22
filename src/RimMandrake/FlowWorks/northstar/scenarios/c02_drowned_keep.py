"""C2 - The Drowned Keep (map C, 44x44, look Industrial): the classic defence built only from FlowWorks parts.

A walled keep on an island inside a 2 m water moat (swimmable), a dry ditch beyond it, a drawbridge over the east arm
(raised, winch powered), a gatehouse pit inside the gate (4 m machine-dug, spikes, plank-lattice cover) that a channel
from the moat can flood through a grate and a sluice, a guardrail and a raised rail ladder at that pit, a south drain
grate, a chemfuel segment in the north arm behind two sluices, and a grated suspension bridge plus a jetty over the
west arm. Raiders live ONLY in the raid branch save (RM_fw_composite_raid); chemfuel is lit after the bridge inspection.
Design §3 C2; GPT #5, #9 (the cover's seam at max zoom is WANTED).

The moat, the dry ditch and the chemfuel segment are kept one UNDUG cell apart wherever their liquids must not meet.
Every dug cell the moat touches through a GRATE is poured full too (the channel grate 33,22 and the drain grate 20,8): a grate
lets water through, so a dry grate cell is room the 351-cell moat levels into, its surface sits a hair under 2 m (1.99 m in
the cell readout) and the bridge's whole-notch `f` floors every cell to 3 = "1.5 m" (MOAT_LEVEL_DIAGNOSE_HALF_METRE_VANISHES).
"""
from .common import (scenario, staged, deferred, perimeter, walls, W, SUSP, DPROOF, DEEP_DIG_ITEM)

SIZE = (44, 44)
DITCH = perimeter(1, 1, 42, 38)
MOAT_W = [(3, 3, 38, 3, 4), (3, 6, 3, 28, 4), (38, 6, 3, 28, 4), (3, 34, 18, 3, 4), (38, 34, 3, 3, 4)]
CHEM = (22, 34, 15, 3, 4)
NECKS = [(21, 35, 1, 1, 4), (37, 35, 1, 1, 4)]
GATEHOUSE = (29, 17, 3, 3, 8)
CHANNEL = [(34, 22, 4, 1, 4), (33, 22, 1, 1, 4), (32, 22, 1, 1, 4), (31, 20, 1, 3, 4)]
KEEP = perimeter(8, 8, 33, 29, gaps=[(33, 18), (33, 22), (20, 8), (8, 20)])
GUARD = [(28, 16), (29, 16), (30, 16), (31, 16), (28, 17), (28, 18), (28, 19), (28, 20), (29, 20), (30, 20)]
PEN = perimeter(14, 39, 26, 43, gaps=[(20, 39)])

SETUP = dict(
    dig=[(x, z, 1, 1, 3) for x, z in DITCH] + MOAT_W + [CHEM] + NECKS + [GATEHOUSE] + CHANNEL + [(20, 6, 1, 3, 4)],
    fluid=[(r[0], r[1], r[2], r[3], 4, W) for r in MOAT_W] + [(22, 34, 15, 3, 4, "RM_Fluid_Chemfuel"),
                                                               (33, 22, 5, 1, 4, W), (20, 6, 1, 3, 4, W)],
    build=walls(KEEP, "Steel") + walls(PEN, "Steel") + [("RM_DrawbridgeGate", 33, 18, None, "Steel"),
                                                        ("Door", 8, 20, None, "Steel")],
    spawn=[("RM_Spikes", 29 + i, 17 + j, None) for i in range(3) for j in range(3) if (i, j) != (1, 2)]
    + [("RM_PitCover_PlankLattice", 29 + i, 17 + j, None) for i in range(3) for j in range(3)]
    + [("RM_Sluice", 21, 35, "Steel"), ("RM_Sluice", 37, 35, "Steel"), ("RM_Sluice", 32, 22, "WoodLog"),
       ("RM_SecurityGrateDoor", 33, 22, "Steel"), ("RM_SecurityGrateDoor", 20, 8, "Steel"),
       ("RM_SecurityGrateDoor", 20, 39, "Steel"), ("RM_Ladder", 30, 19, None)]
    + [("RM_PitGuardrail", x, z, "Steel") for x, z in GUARD],
    ladder_dev=[(30, 19, "raise")],
    refill_after_pulse=True,
    calls=[dict(typ=DPROOF, method="ProofMakeDrawbridge", fmt="{0};{1};steel;A;winch", cells=[(37, 18), (41, 18)]),
           dict(typ=DPROOF, method="ProofWinchPower", fmt="{0};on", cells=[(39, 18)]),
           dict(typ=DPROOF, method="ProofDevSet", fmt="{0};raise;instant", cells=[(39, 18)]),
           dict(typ=SUSP, method="ProofBuild", fmt="{0};{1};steelgrated;god", cells=[(6, 24), (2, 24)]),
           dict(typ=SUSP, method="ProofJetty", fmt="{0};{1};steel;god", cells=[(6, 30), (4, 30)])],
    items=[("RM_RaidPlank", 1, 24, 41)],
    pawns=[("Colonist", 15, 15, "player", "drafted"), ("Colonist", 17, 15, "player", "drafted")],
    pens=[("Pirate", 16, 41, "hostile"), ("Pirate", 18, 41, "hostile"), ("Pirate", 20, 42, "hostile"),
          ("Pirate", 22, 41, "hostile")],
)

SCENARIO = scenario(
    id="C2", n=2, slug="drowned_keep", name="The Drowned Keep", map="C", size=SIZE, look_style="Industrial",
    purpose="A walled keep inside a water moat: the classic defence, built only from FlowWorks parts, with a nasty "
            "gatehouse.",
    start="(raid branch save RM_fw_composite_raid) open the raiders' pen grate and unpause",
    try_=["main save: walk a colonist over the grated suspension bridge across the west moat arm and out the jetty; "
          "swim under the deck (live 2026-10-21: a span must cross dug ground only, so it cannot also span the dry ditch)",
          "RAID BRANCH START: open the pen grate, unpause: raiders reach the ditch and moat, lay the plank or swim (2 m: "
          "heads and shoulders up), climb, and try the gate (it stays shut to hostiles)",
          "lower the drawbridge (its winch) mid-raid: the leaf drops; the gate still refuses unless held open; raiders "
          "walk the gatehouse planks like floor: deconstruct (or blast) the cover under one and he drops onto the spikes",
          "open the gatehouse grate and sluice: the trapped raider's pit floods from the moat; read swim vs drown in "
          "the inspect pane",
          "light the chemfuel arm (dev fire at 'light here'): it goes up like gasoline; the grated deck lets the heat up",
          "cut the winch's power (ProofWinchPower off; the GSS cord is DEFERRED): the leaf holds where it is"],
    look_for="the concealed pit invisible at play zoom with a slight seam at max zoom; the bridge reads HUNG, not a pier; "
             "raiders swim, never walk the moat floor; the leaf, winch and gate draw the STEEL picture (material first, a look "
             "only as fallback); the spikes (lift a plank to see them) are his art call",
    broken="the concealed pit visible at play zoom, or NO seam at max zoom; the concealed pit reading like a bridge; raiders walking "
           "on the moat floor; the gate opening for raiders while the leaf is up; a raider unhurt on the spikes; the "
           "bridge drawn as a pier-on-pylons; the sluice open but the pit dry",
    idle="main save: no hostiles; the moat brim-full and closed; the leaf raised and held by a powered winch; every "
         "sluice and grate shut; nothing lit; the two defenders drafted",
    setup=SETUP,
    parts=[(20, 44, "raider pen (raid branch)"), (39, 20, "drawbridge (raised)"), (33, 20, "gate"),
           (30, 15, "gatehouse: concealed pit over spikes, 4 m"), (34, 23, "channel: grate + sluice"), (20, 5, "drain grate"),
           (8, 21, "postern"), (3, 26, "suspension bridge (grated)"), (5, 31, "jetty"), (29, 37, "light here"),
           (21, 37, "sluice"), (37, 37, "sluice"), (16, 13, "defenders"), (1, 39, "dry ditch"), (40, 10, "moat 2 m")],
    pieces=[staged("dry outer ditch", "dig", None, (1, 1), "look"),
            staged("2 m water moat ring", "fluid", W, (3, 3)),
            staged("keep walls", "build", "Wall", (8, 8), "look"),
            staged("drawbridge gate in the wall", "build", "RM_DrawbridgeGate", (33, 18), "poked"),
            staged("drawbridge leaf + winch over the east arm", "calls", "ProofMakeDrawbridge", (37, 18), "poked"),
            staged("winch powered", "calls", "ProofWinchPower", (39, 18)),
            staged("leaf raised", "calls", "ProofDevSet", (39, 18), "poked"),
            staged("gatehouse pit 3x3, 4 m, spikes", "spawn", "RM_Spikes", (29, 17), "poked"),
            staged("concealed pit (planks) over it", "spawn", "RM_PitCover_PlankLattice", (29, 17), "poked"),
            staged("channel from the moat: grate + sluice", "spawn", "RM_Sluice", (32, 22), "poked"),
            staged("guardrail on the gatehouse lip", "spawn", "RM_PitGuardrail", (28, 17), "look"),
            staged("rail ladder in the gatehouse pit, raised", "ladder_dev", "raise", (30, 19), "poked"),
            staged("south drain grate", "spawn", "RM_SecurityGrateDoor", (20, 8), "look"),
            staged("chemfuel north arm behind two sluices", "fluid", "RM_Fluid_Chemfuel", (22, 34), "poked"),
            staged("grated suspension bridge over the west arm", "calls", "ProofBuild", (6, 24), "poked"),
            staged("jetty over the west arm", "calls", "ProofJetty", (6, 30), "poked"),
            staged("two defenders, drafted", "pawns", "Colonist", (15, 15)),
            staged("raiders in a pen behind a shut grate (raid branch)", "pens", "Pirate", (16, 41), "poked"),
            staged("a raid plank in the pen", "items", "RM_RaidPlank", (24, 41), "poked"),
            deferred("doors leaking slowly under water (D4): the postern", "overflow is built (Stages 1-3) but its master switch ships OFF and this scenario does not turn it on; the postern sits "
                     "by the moat so it shows once the switch is on", "CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED", (10, 31)),
            deferred("the winch's GSS power cord (cut it)", "ProofWinchPower forces power; no script lays an "
                     "RM_PowerCord", "POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS", (12, 31)),
            deferred("machine digging the 4 m gatehouse pit", "past the 2 m colonist cap", DEEP_DIG_ITEM, (14, 31)),
            deferred("guardrail art", "a borrowed fence look; a cosmetic change needs his permission",
                     "GUARDRAIL_ART_RESKIN_BORROWED_FENCE", (16, 31)),
            deferred("defenders holding fire until drafted (raid branch)", "no bridge surface: owed", "owed C#",
                     (18, 31))],
    exercises={"pit_cover": "look", "pit_cover_drop": "poked", "pit_spikes": "poked", "look_parts": "look",
               "hold_gates": "poked", "look_sink": "look", "fire_chemfuel": "poked",
               "canal_dry_reads_as_obstacle": "poked", "deep_water_pawn_swims": "poked",
               "pawn_lowers_on_deeper_cell": "look", "spikes_read_distinct": "look", "pit_covered_invisible": "look",
               "pit_covered_seam_at_max_zoom": "look", "pit_cover_unlike_bridge": "look",
               "suspension_bridge_reads_hung": "look", "pawn_walks_under_deck": "poked",
               "sluice_gate_state_legible": "look", "pit_trapped_reads_as_trapped": "poked",
               "canal_burning_reads_as_burning_liquid": "poked"},
    goal="live: ProofLeaf on (39,18) reads raised=..., powered=True; ProofSpan on the west bridge reads hung",
    branch={"raid": "RM_fw_composite_raid: four raiders in the north pen, grate shut"},
    owed_cs=["a fire-at-will/hold-fire bridge surface (raid-branch defenders hold fire until drafted)"],
)
