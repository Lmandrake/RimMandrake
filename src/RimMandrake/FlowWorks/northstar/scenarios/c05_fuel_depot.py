"""C5 - The Fuel Depot (map C, 40x36, look Industrial; cargo tanks Futuristic): the one place that must not burn.

Cargo tanks of chemfuel and propane on an Industrial pipe run (with the chemfuel adapter when Vanilla Chemfuel Expanded
is loaded), a filling bay of four tanks whose jobs he sets, a containment canal a pump pours the Dump tank into, our hose
coupled to THEIR tank, an astrofuel bund, a firefoam popper, and a water canal one wall from the chemfuel canal for the
no-mix poke. Design §3 C5; GPT #9 (canal start vs brim reconciled).

Idle-stable: every bay tank is staged in Store (a job set before he arrives would run on the first unpause and the soak
would fail); setting their jobs is the Start. The containment canal is a quarter full and its pump is unpowered-safe:
the Dump tank only flows once he sets it to Dump.
"""
from .common import scenario, staged, deferred, perimeter, walls, OVERFLOW_ITEM, GIRTH_NOTE

SIZE = (40, 36)
CANAL = (22, 21, 14, 2, 4)          # containment canal, 2 m, chemfuel 0.5 m (a quarter)
WATER = (22, 18, 14, 1, 2)          # water canal; z 19-20 is the shared earth wall (the no-mix dig is his)
BUND = (34, 30, 2, 2, 1)

SETUP = dict(
    dig=[CANAL, WATER, BUND],
    fluid=[(22, 21, 14, 2, 1, "RM_Fluid_Chemfuel"), (22, 18, 14, 1, 2, "RM_Fluid_Water"),
           (34, 30, 2, 2, 1, "RM_Fluid_Astrofuel")],
    terrain=[("Concrete", 2, 4, 12, 4)],                                   # the spill pad
    build=[("RM_UniversalCargoTank", 2, 30, None, None), ("RM_UniversalCargoTank", 7, 30, None, None),
           ("RM_UniversalCargoTankXTall", 12, 30, None, None)]
    + [("RM_UniversalPipe", x, 29, None, None) for x in range(2, 20)]
    + [("RM_LiquidTank", x, 14, None, None) for x in (2, 6, 10)] + [("RM_LiquidTank", 14, 21, None, None)]
    + [("RM_UniversalPipe", x, 22, None, None) for x in range(16, 21)]
    + [("RM_LiquidPump", 21, 22, None, None), ("PowerConduit", 21, 23, None, None), ("Battery", 20, 24, 0, None),
       ("PowerConduit", 21, 24, None, None), ("FirefoamPopper", 30, 25, None, None),
       ("RM_HoseReel", 20, 8, None, None)]
    + walls(perimeter(33, 29, 36, 32, gaps=[(34, 29), (35, 29)]), "Steel"),
    hostile=[("RM_LiquidTank", 30, 8, None, None)],
    style=[(d, x, 30, d + "_Futuristic") for d, x in (("RM_UniversalCargoTank", 2), ("RM_UniversalCargoTank", 7),
                                                       ("RM_UniversalCargoTankXTall", 12))]
    + [("RM_UniversalPipe", x, 29, "RM_UniversalPipe_Industrial") for x in range(2, 20)]
    + [("RM_HoseReel", 20, 8, "RM_HoseReel_Industrial")],
    tank=[(2, 30, "Store", "RM_Liquid_Chemfuel", 8000), (7, 30, "Store", "RM_Liquid_Propane", 8000),
          (12, 30, "Store", "RM_Liquid_Chemfuel", 16000),
          (2, 14, "Store", "RM_Liquid_Chemfuel", 4000), (6, 14, "Store", "RM_Liquid_Chemfuel", 4000),
          (10, 14, "Store", "RM_Liquid_Chemfuel", 8000), (14, 21, "Store", "RM_Liquid_Chemfuel", 6000),
          (30, 8, "Store", "RM_Liquid_Chemfuel", 8000)],
    pump=[(21, 22, "pour")],
    batteries=[(20, 24)],
    hose=[(20, 8, 29, 8, None)],
    hose_flow=[(20, 8, "Plump")],
    stuffed=[("RM_BarrelEmpty", 2 + i, 11, 1, "Steel") for i in range(3)]
    + [("RM_BottleEmpty", 6 + i, 11, 5, "Steel") for i in range(3)]
    + [("RM_Filth_LiquidSpill", x, z, 1, None) for x in (3, 4, 5) for z in (5, 6)]
    + [("RM_Filth_Tar", x, z, 1, None) for x in (9, 10, 11) for z in (5, 6)],
    optional_build=[("RM_PipeAdapter_Chemfuel", 20, 29, None, None, "RM_PipeAdapter_Chemfuel")],
)

SCENARIO = scenario(
    id="C5", n=5, slug="fuel_depot", name="The Fuel Depot", map="C", size=SIZE, look_style="Industrial",
    purpose="A caravan fuel stop: cargo tanks, a filling bay, a tapped neighbour's tank, a bunded canal and a fire "
            "plan - the place that must not burn shows every fire rule by being dangerous.",
    start="set the bay tanks' Job buttons: Store / Fill / Empty (west to east) and the tank by the pump to Dump",
    try_=["START: bay jobs Store, Fill, Empty; the pump-side tank Dump; unpause: colonists fill barrels from Empty and "
          "pour only into Fill; the Dump tank empties into the containment canal through the pump",
          "cycle the adapter Send > Take > Shut and watch the run's stock (needs Vanilla Chemfuel Expanded)",
          "select our hose on THEIR tank: tinted chemfuel; its inspect names nobody's faction",
          "light the containment canal (dev fire at 'light here'): burns like gasoline, keeps burning, reaches the "
          "tank end, leaves the canal spent; pop the firefoam: foamed cells stay out while foam lies",
          "light the astrofuel bund: it detonates, not burns",
          "dig the marked cell in the earth wall between the water and chemfuel canals: they meet and do NOT mix"],
    look_for="chemfuel, propane and water each their own colour; pipes rise onto each tank's flange; the Fill tank is "
             "never emptied by colonists",
    broken="chemfuel, propane and water hoses all one colour; a tank drawn bridging two pipe runs; the Fill tank "
           "emptied; water and chemfuel mixing; a burnt canal that looks fresh; foamed cells relighting under foam; "
           "litres from nowhere",
    idle="every bay tank in Store; the pump is set to Pour but its Dump-side tank is in Store, so nothing flows; the "
         "hose to their tank is Plump with its free end Capped; nothing is lit",
    setup=SETUP,
    parts=[(4, 33, "cargo chemfuel"), (8, 33, "cargo propane"), (13, 34, "XTall chemfuel"), (21, 30, "adapter"),
           (2, 16, "bay: Store"), (6, 16, "bay: Fill"), (10, 16, "bay: Empty"), (14, 23, "set Dump"),
           (21, 20, "pump (Pour)"), (36, 22, "light here"), (28, 19, "dig here: no-mix"), (30, 10, "THEIR tank"),
           (35, 33, "astrofuel bund"), (30, 26, "firefoam"), (4, 3, "spill"), (10, 3, "tracked tar")],
    pieces=[staged("cargo tanks (Futuristic): chemfuel, propane, XTall chemfuel", "style", None, (2, 30), "look"),
            staged("Industrial pipe run", "style", "RM_UniversalPipe_Industrial", (2, 29), "look"),
            staged("chemfuel adapter on the run (VCHE)", "optional_build", "RM_PipeAdapter_Chemfuel", (20, 29), "poked",
                   "built only when Vanilla Chemfuel Expanded's def is loaded (live get_defs)"),
            staged("filling bay: four tanks", "tank", "Store", (2, 14), "poked"),
            staged("empty barrels and bottles", "stuffed", "RM_BarrelEmpty", (2, 11), "look"),
            staged("containment canal, chemfuel a quarter", "fluid", "RM_Fluid_Chemfuel", (22, 21)),
            staged("pump set to Pour", "pump", "pour", (21, 22), "poked"),
            staged("our hose on THEIR tank, Plump", "hose", None, (20, 8), "look"),
            staged("their tank (hostile faction)", "hostile", "RM_LiquidTank", (30, 8), "look"),
            staged("astrofuel bund, walled", "fluid", "RM_Fluid_Astrofuel", (34, 30), "poked"),
            staged("firefoam popper by the canal", "build", "FirefoamPopper", (30, 25), "poked"),
            staged("water canal one wall from the chemfuel", "fluid", "RM_Fluid_Water", (22, 18), "poked"),
            staged("spill pad: liquid spill + tracked tar", "stuffed", "RM_Filth_Tar", (9, 5), "look"),
            deferred("fuel overflow spreads and burns (D5)", "overflow Stage 1+ is unbuilt (only the Stage 0 offline "
                     "kernel exists); the canal stands below its brim so a second Dump will spill once it lands",
                     OVERFLOW_ITEM, (37, 2)),
            deferred("an acid canal beside the chemfuel", "moved to C6 (where corrosion lives); the no-mix poke needs "
                     "only water against chemfuel", "design §3 C5 layout", (37, 5)),
            deferred("joint fittings art at the tanks", GIRTH_NOTE, "PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID", (37, 8))],
    exercises={"carry_tanks": "poked", "tank_styles_cargo": "look", "tank_modes": "poked", "pipe_adapter": "poked",
               "hose_their_tank": "look", "carry_bottles": "poked", "carry_containers": "look",
               "containers_styles": "look", "fire_chemfuel": "poked", "fire_astrofuel": "poked", "fire_out": "poked",
               "fire_lights": "poked", "liquid_spill": "look", "canal_fluids_more": "look", "flow_no_mix": "poked",
               "fill_fluid_distinct": "look", "hose_tint_is_carried_liquid": "look",
               "never_external_pipe_carries": "poked", "never_tank_bridges_pipe_runs": "look",
               "canal_burning_reads_as_burning_liquid": "poked", "canal_fire_persists": "poked",
               "canal_spent_after_burn": "poked", "canal_fire_reaches_reservoir": "poked",
               "pipe_meets_building_centre": "look"},
    goal="live: the containment canal's chemfuel litres (ProofReadout) and the Dump tank's stock read; their sum is "
         "the canal's brim minus one notch",
)
