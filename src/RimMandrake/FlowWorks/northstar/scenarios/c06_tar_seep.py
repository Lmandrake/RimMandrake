"""C6 - The Tar Seep (map C, 40x36, look Scrapper): the viscous-liquids scenario.

A tar seep bleeds into a ditch that races a water ditch of the same length (both held at the start by a shut sluice:
opening both is the Start), a refinery at its three stages, a slime pit with a muffalo in it and a one-cell earth plank
across, a reaction vat between a tar tank and an acid tank, an acid canal with steel and wood in it, and tracked tar on
a footpath. Design §3 C6; GPT #9 (the corrosion switch and the vat's real per-batch numbers named).
"""
from .common import scenario, staged, deferred, TAR, W

SIZE = (40, 36)

SETUP = dict(
    terrain=[("RM_TarDeep", 0, 28, 4, 4), ("WaterDeep", 0, 22, 4, 4),         # the seep, and the water race's source
             ("RM_AcidDeep", 20, 1, 3, 4), ("Concrete", 10, 17, 10, 2)],
    dig=[(4, 30, 32, 1, 2), (4, 23, 32, 1, 2),                                 # tar ditch and water ditch, side by side
         (26, 11, 2, 4, 2), (29, 11, 2, 4, 2),                                 # slime pit halves; x 28 is the earth plank
         (23, 2, 12, 1, 2)],                                                   # acid canal
    fluid=[(26, 11, 2, 4, 2, "RM_Fluid_SlimeGreen"), (29, 11, 2, 4, 2, "RM_Fluid_SlimeGreen")],
    spawn=[("RM_Sluice", 4, 30, "WoodLog"), ("RM_Sluice", 4, 23, "WoodLog")],
    build=[("RM_LiquidDrill", 1, 33, None, None),
           ("RM_TarRefinery_Wrecked", 3, 13, None, None), ("RM_TarRefinery_Kludged", 9, 13, None, None),
           ("RM_TarRefinery_Repaired", 15, 13, None, None),
           ("RM_LiquidTank", 2, 5, None, None), ("RM_ReactionVat", 7, 5, None, None), ("RM_LiquidTank", 11, 5, None, None)],
    tank=[(2, 5, "Store", "RM_Liquid_Tar", 8000), (11, 5, "Store", "RM_Liquid_AcidWater", 8000)],
    items=[("Steel", 30, 27, 2), ("WoodLog", 30, 31, 2)],
    stuffed=[("RM_Filth_Tar", x, 18, 1, None) for x in range(11, 19)],
    pawns=[("Muffalo", 27, 12, "none", None)],
    keep=True,
)

SCENARIO = scenario(
    id="C6", n=6, slug="tar_seep", name="The Tar Seep", map="C", size=SIZE, look_style="Scrapper",
    purpose="Tar bleeds up, crawls down a ditch, is tracked in on boots, refined, and burns; slime and acid share the "
            "yard; water runs beside the tar so you can compare.",
    start="open both race sluices (the tar one and the water one, at the ditches' west ends), then unpause",
    try_=["START: open both sluices, unpause: the water front runs, the tar front crawls behind it (watch both)",
          "walk a colonist across the slime pit's edge: slow, nearly uncrossable; the muffalo sits below the surface; "
          "the earth plank (x middle) is the dry way over",
          "light the tar ditch: it burns for days; the refinery stops if its feed burns; dev weather Rain puts it out",
          "start the vat: 400 L tar + 200 L acid water per batch meter in; 200 L of product to a third tank if one is "
          "on its line, else 40 gas vented (RM_Reaction_TarAcid; the product thing is owed under SUMP_GASLIGHT_1: "
          "judge the metering and the vent)",
          "watch the acid canal: what lies in it loses health over hours (Mod Settings: Liquid corrosion, ships ON)",
          "colonists clean the tracked tar"],
    look_for="tar thick and slow beside water; slime reads viscous, the muffalo below its surface; the three refinery "
             "stages easy to tell apart",
    broken="the tar front level with the water's; slime that looks like coloured water; a muffalo standing on top of "
           "slime; tar filth with no art; a burning tar ditch out within an hour; corrosion while the switch is off",
    idle="both race ditches are dry behind shut sluices; the vat is not started; corrosion and the tracked tar DO "
         "change over two hours (the soak reads dug cells and buildings, not item health or filth)",
    setup=SETUP,
    parts=[(5, 31, "tar sluice"), (5, 24, "water sluice"), (36, 31, "tar front"), (36, 24, "water front"),
           (3, 12, "Wrecked"), (9, 12, "Kludged"), (15, 12, "Repaired"), (28, 16, "earth plank"),
           (8, 8, "reaction vat"), (2, 8, "tar"), (11, 8, "acid water"), (28, 4, "acid: steel, wood"),
           (14, 20, "tracked tar"), (1, 35, "drill")],
    pieces=[staged("tar seep (pond) + drill", "build", "RM_LiquidDrill", (1, 33), "look"),
            staged("tar ditch behind a shut sluice", "spawn", "RM_Sluice", (4, 30), "poked"),
            staged("water ditch behind a shut sluice (the race)", "spawn", "RM_Sluice", (4, 23), "poked"),
            staged("tar refinery Wrecked | Kludged | Repaired", "build", "RM_TarRefinery_Repaired", (15, 13), "look"),
            staged("green slime pit with a muffalo", "pawns", "Muffalo", (27, 12)),
            staged("one-cell earth plank across", "dig", None, (29, 11), "poked", "x 28 is left undug"),
            staged("reaction vat between tar and acid tanks", "build", "RM_ReactionVat", (7, 5), "poked"),
            staged("acid canal with steel and wood", "items", "Steel", (27, 2)),
            staged("tracked tar footpath", "stuffed", "RM_Filth_Tar", (11, 18), "look"),
            deferred("the vat's product thing", "owed under SUMP_GASLIGHT_1: judge metering and vent only",
                     "SUMP_GASLIGHT_1", (37, 34)),
            deferred("the drill on a survey hit", "no survey staging surface: the drill sits on the seep pond",
                     "FLOWWORKS_QUARRY_DIGGING_1", (37, 31))],
    exercises={"flow_identity": "poked", "flow_slime": "poked", "look_liquids": "look", "look_fire": "poked",
               "fire_lights": "poked", "fire_lasts": "poked", "fire_corrosion": "demonstrated", "liquid_spill": "look",
               "carry_drills": "look", "industry_stages": "look", "carry_industry": "look",
               "tar_fill_front_lags_water": "poked", "slime_reads_as_viscous_not_water": "look",
               "slime_occupant_below_surface": "look", "canal_reads_as_same_liquid_as_reservoir": "poked",
               "fill_fluid_distinct": "look", "canal_burning_reads_as_burning_liquid": "poked",
               "canal_fire_persists": "poked", "canal_spent_after_burn": "poked"},
    goal="live: both ditches dry at the start (excavation read f=0 east of the sluices); the slime pit's fill reads 2",
    branch={"days": "RM_fw_composite_days: the burning ditch a day later"},
)
