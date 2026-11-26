"""modcheck test environment for Armoury (mandrake.rsw.armoury) -- MODCHECK_DONOR_ENVIRONMENTS_1.

The packageIds `modcheck run Armoury` composes onto the MINIMAL list, read as data (ast, never imported) by
`src/RimMandrake/Utils/modset_builder.py` into TIERS["armoury"] (`modcheck_closure`, so the runner's
`closure_ids` appends them). It is the dependency CLOSURE of this mod's About.xml `<modDependencies>`, resolved
from the installed mods' About.xml files on 2026-11-02; `selftest_modcheck_donor_envs.py` re-checks that every
hard dependency named in About.xml is here.

Soft additions beyond the closure (ASTEROID_DESERT_ORES_1, 2026-11-26): RSW_Smelter_Alloys.xml adds the four ship-smelter
processes only when VFE Factory's VFEFactory_SmeltMetalFromSlag and RM_GlowerCrust exist, so without
vanillaexpanded.vfefactory and mandrake.rm.biomes the ores_and_smelts rows could only read UNMEASURED
(guard: src/RimMandrake/Utils/modcheck/selftest_live_defs_on_the_list.py).

Donors that are NOT in it, on purpose:
- kaitorisenkou.ModularWeapons2: cut (ARMOURY_MW2_CUT_1, 2026-09-13). A list carrying it would test the weapons
  beside an inert donor, so the tier FORBIDS it.
- guy762.MM.KotORCore: absorbed into this mod (Defs/Absorbed_KotorCore, WEAPONS_DONOR_RETIREMENT_1, 2026-09-19);
  every kotorsound_* SoundDef now lives in Defs/Absorbed_KotorCore/SoundDefs.
"""

EXTRA_IDS = [
    "mandrake.rm.gimmesomeslack",                   # JawaBench get_defs TypeLoad-fails without it (MEASURED 2026-10-07)
    "neronix17.toolbox",                            # dependency of Outer Rim - Core
    "neronix17.outerrim.core",
    "oskarpotocki.vanillafactionsexpanded.core",
    "ebsg.framework",
    "adaptive.storage.framework",
    "vanillaexpanded.vfefactory",                   # soft: ores_and_smelts' RSW_Smelt* processes need its smelter
    "mandrake.rm.flowworks",                        # dependency of mandrake.rm.biomes
    "mandrake.rm.luminouspigment",                  # dependency of mandrake.rm.biomes
    "mandrake.rm.hugethings",                       # dependency of mandrake.rm.biomes
    "mandrake.rm.biomes",                           # soft: RM_GlowerCrust (Scarlands), the doonium smelt's flux
    "mandrake.rsw.armoury",
]

FORBID = ["kaitorisenkou.modularweapons2"]
