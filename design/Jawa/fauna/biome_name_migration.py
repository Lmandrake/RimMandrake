#!/usr/bin/env python3
"""The pre-migration -> live BiomeDef defName table, shared.

`BIOME_OWNERSHIP_WAVE_1` (2026-09-09) renamed 22 of the biomes the fauna-cast pipeline
targets to `RUT_`-prefixed defNames (`ZBiome_Grasslands` alone was never renamed). Every
generator that still carries an OLD name — in a CSV column, a hardcoded set, a roster's
legacy `defNames` entry — needs this table to reach the live def. It was derived ONCE,
cross-checked by commonality-multiset match against the live rosters (not name-guessing),
at `366c278d6` (`BIOME_FLORA_GENERATOR_REPAIR_1`, `biome_flora.py`'s `FAMILIES` rekey) and
`9350e29a3` (`PROPANE_LAKES_ROSTER_STALE_1`, the one biome — `AB_PropaneLakes` -> `RUT_Umbra`
— that moved to a differently-named live biome outright), then re-derived independently by
`animal_tolerances.py` for `ANIMAL_TOLERANCES_JOIN_BROKEN_1` and found to agree byte-for-byte.
Factored out here for `ROSTERS_TO_CAST_BIOMECAST_DEFS_STALE_1` rather than copy-pasted a
third time.

🔴 Three old names collapsed onto ONE live biome: `AB_PyroclasticConflagration`,
`LavaField` and `Volcano` all map to `RUT_TheForge`. A caller building a *set* of live
biome defNames from `.values()` will see 20 unique entries from these 22 keys, not 22 -
correct, not a bug in this table.
"""

OLD_TO_NEW_BIOME = {
    'AB_FeraliskInfestedJungle': 'RUT_Webwork',  # NOT retargeted to RM_Webwork
                                                  # (WEBWORK_RM_MOD_BUILD_1, 2026-09-25): unlike the
                                                  # RM_Contagion/RM_TheSump rows below, RM_Webwork ships
                                                  # a vanilla-only placeholder — RUT_Webwork remains the
                                                  # only def with the real fauna cast until
                                                  # WEBWORK_FAUNA_ROSTER_1 lands. A caller resolving this
                                                  # old name for fauna data needs the twin, not the shell.
    'AB_GelatinousSuperorganism': 'RUT_Slime',
    'AB_MechanoidIntrusion': 'RUT_RustCathedral',
    'AB_MiasmicMangrove': 'RUT_Miasma',
    'AB_MycoticJungle': 'RM_TheRot',
    'AB_OcularForest': 'RM_Contagion',  # RM_ mod built 2026-09-25, CONTAGION_RM_MOD_BUILD_1
                                         # (RUT_Contagion frozen, world-carrying twin, identical content)
    'AB_PropaneLakes': 'RUT_FuelSnows',  # renamed from RUT_Umbra 2026-09-21,
                                          # UMBRA_IS_A_REGION_NOT_A_BIOME_1 (Umbra
                                          # now names the region, not this biome)
    'AB_PyroclasticConflagration': 'RUT_TheForge',
    'AB_RockyCrags': 'RM_ForsakenCrags',  # RM_ mod built 2026-09-25, FORSAKENCRAGS_RM_MOD_BUILD_1
    'AB_TarPits': 'RM_TheSump',  # RM_ mod built 2026-09-25, THESUMP_RM_MOD_BUILD_1
                                  # (RUT_Sump frozen, world-carrying twin, identical content)
    'AridShrubland': 'RUT_AridShrubland',
    'BiomeCypreJungle': 'RUT_Greentide',
    'COMIGO_GreaterSwamp_Tropical': 'RUT_FeverWood',
    'Desert': 'RUT_Desert',
    'ExtremeDesert': 'RM_Stillsand',  # RUT_ExtremeDesert frozen 2026-09-24,
                                       # STILLSAND_RM_MOD_BUILD_1 (same pattern as
                                       # AB_MycoticJungle -> RM_TheRot above)
    'LavaField': 'RUT_TheForge',
    'PoisonForest': 'RM_PoisonForest',  # RM_ mod built 2026-09-25, POISONFOREST_RM_MOD_BUILD_1
                                          # (RUT_PoisonForest still frozen, world-carrying twin,
                                          # identical content)
    'Scarlands': 'RUT_Scarlands',
    'Volcano': 'RUT_TheForge',
    'Wasteland': 'RM_Wasteland',  # RUT_Wasteland frozen 2026-09-24,
                                   # WASTELAND_RM_MOD_BUILD_1 (same pattern as
                                   # AB_MycoticJungle -> RM_TheRot above)
    'ZBiome_Badlands': 'RUT_CrackedLands',
    'ZBiome_DesertOasis': 'RUT_WeepingStones',
    # ZBiome_Grasslands was never renamed - carried unchanged, not a dict entry.
}


def resolve(biome):
    """OLD_TO_NEW_BIOME[biome] if biome is a pre-migration name, else biome unchanged."""
    return OLD_TO_NEW_BIOME.get(biome, biome)
