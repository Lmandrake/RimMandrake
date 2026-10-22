"""C13 - The Spill Yard (map C, 44x32): canal overflow with its master switch ON, spill rows staged for one walk.

Owner by card 2026-10-22: ONE separate overflow scenario; the twelve review scenarios stay as built, with overflow at its
shipped default (switch OFF) and a pointer here. The build turns RM_SheetSettings.sheetOverflowEnabled ON and then offers
each spill through the production entry (RM_SheetProofs.ProofSheetSpill -> RM_MapComponent_Sheet.Offer, source Flood so
inPump/inRain stay clean). Both happen AFTER the build's two-hour soak (the key `after_soak`), so the walk starts on fresh
spills instead of what two hours already evaporated or soaked away. The switch is a mod setting (config, not the save):
it stays ON until he turns it off in Mod Settings.

Rows, west to east on the open soil north of a brim-full canal: R1 a film (3,000 dL), R2 a sheet (9,000), R3 a pool
(30,000), R4 chemfuel (9,000, the fuel spill D5), crops with a standing spill (D3: irrigates first, kills only after a
week), and a closed room with a door and a spill beside it (D4: leaks slowly under the door).
"""
from .common import scenario, staged, deferred, perimeter, walls, W, OVERFLOW_ITEM

SIZE = (44, 32)
S_SHEET = "RimMandrake.FlowWorks.Sheet.RM_SheetSettings"
PROOFS = "RimMandrake.FlowWorks.Sheet.RM_SheetProofs"
CANAL = (2, 26, 40, 1, 2)
ROOM = perimeter(33, 6, 41, 12, gaps=[(37, 12)])
SPILL = "{0};%d;Flood"
SPILL_FUEL = "{0};9000;Flood;RM_Fluid_Chemfuel"

SETUP = dict(
    dig=[CANAL],
    fluid=[(2, 26, 40, 1, 2, W)],                                               # brim-full: the source of the trouble
    build=walls(ROOM, "WoodLog", "Wall") + [("Door", 37, 12, None, "WoodLog")],
    spawn_plants=[("Plant_Rice", x, 18) for x in (26, 27, 28)],
    settings=[(S_SHEET, "sheetOverflowEnabled", True)],
    after_soak=[
        dict(typ=PROOFS, method="ProofSheetSpill", fmt=SPILL % 3000, cells=[(6, 22)]),
        dict(typ=PROOFS, method="ProofSheetSpill", fmt=SPILL % 9000, cells=[(12, 22)]),
        dict(typ=PROOFS, method="ProofSheetSpill", fmt=SPILL % 30000, cells=[(18, 22)]),
        dict(typ=PROOFS, method="ProofSheetSpill", fmt=SPILL_FUEL, cells=[(22, 22)]),
        dict(typ=PROOFS, method="ProofSheetSpill", fmt=SPILL % 20000, cells=[(27, 20)]),
        dict(typ=PROOFS, method="ProofSheetSpill", fmt=SPILL % 20000, cells=[(37, 14)]),
    ],
)

SCENARIO = scenario(
    id="C13", n=13, slug="spill_yard", name="The Spill Yard", map="C", size=SIZE, look_style="land and water bodies",
    purpose="Canal overflow switched ON: a brim-full canal and six staged spills (a film, a sheet, a pool, chemfuel, one "
            "on a crop row, one at a door) to watch spill, spread, soak and return.",
    start="read the sign (the overflow switch is ON for this plot), then unpause and watch the rows",
    try_=["START: unpause and watch R1-R3: the film thins and soaks or evaporates, the sheet spreads, the pool stands and "
          "drains back toward the canal",
          "R4 chemfuel: it spreads as fuel, does not soak like water, and burns if lit (light it only if you want the fire)",
          "crop row: the standing spill irrigates the rice first; it is killed only after about a week of standing water",
          "door room: the spill beside the door leaks slowly under it into the room",
          "fill the canal further (a pump or the fill tool) and see it overfill onto the soil",
          "then open Mod Settings, turn 'Overfilled channels spill water onto the ground' OFF and spill again: nothing spills"],
    look_for="spills that end somewhere readable (returned, soaked, evaporated, or standing); no water vanishing without a "
             "sign; the ledger of every litre closing",
    broken="a spill that disappears with no sign; a canal that never overfills; the switch ON yet nothing spills; the "
           "switch OFF yet water spills; a door that leaks fast or not at all; chemfuel soaking like water",
    idle="the canal sits brim-full and the sheet water is offered AFTER the two-hour soak, so the rows are fresh at the walk; "
         "time is paused until he unpauses. The switch stays ON in Mod Settings until he turns it off.",
    setup=SETUP,
    parts=[(2, 28, "brim-full canal"), (6, 20, "R1 film 3,000 dL"), (12, 20, "R2 sheet 9,000 dL"),
           (18, 20, "R3 pool 30,000 dL"), (22, 20, "R4 chemfuel 9,000 dL"), (27, 16, "rice + standing spill"),
           (37, 4, "door room + spill at the door")],
    pieces=[staged("overflow master switch turned ON", "settings", None, None, "poked",
                   "the build sets RM_SheetSettings.sheetOverflowEnabled; it is a mod setting, so it outlives the save"),
            staged("brim-full canal", "fluid", W, (2, 26), "poked"),
            staged("R1 film spill", "after_soak", None, (6, 22)),
            staged("R2 sheet spill", "after_soak", None, (12, 22)),
            staged("R3 pool spill", "after_soak", None, (18, 22)),
            staged("R4 chemfuel spill", "after_soak", None, (22, 22)),
            staged("rice row with a standing spill (D3)", "spawn_plants", "Plant_Rice", (26, 18), "look"),
            staged("door room with a spill at the door (D4)", "build", "Door", (37, 12), "poked"),
            deferred("a pump overfilling the canal as a staged source", "a pump and tank here would move water on their own "
                     "before his first poke", OVERFLOW_ITEM, (40, 20))],
    goal="live: the build's note shows each spill accepted > 0 and the switch read back True",
)
