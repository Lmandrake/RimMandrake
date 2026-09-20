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
    'AB_FeraliskInfestedJungle': 'RUT_Webwork',
    'AB_GelatinousSuperorganism': 'RUT_Slime',
    'AB_MechanoidIntrusion': 'RUT_RustCathedral',
    'AB_MiasmicMangrove': 'RUT_Miasma',
    'AB_MycoticJungle': 'RUT_TheRot',
    'AB_OcularForest': 'RUT_Contagion',
    'AB_PropaneLakes': 'RUT_Umbra',
    'AB_PyroclasticConflagration': 'RUT_TheForge',
    'AB_RockyCrags': 'RUT_ForsakenCrags',
    'AB_TarPits': 'RUT_Sump',
    'AridShrubland': 'RUT_AridShrubland',
    'BiomeCypreJungle': 'RUT_Greentide',
    'COMIGO_GreaterSwamp_Tropical': 'RUT_FeverWood',
    'Desert': 'RUT_Desert',
    'ExtremeDesert': 'RUT_ExtremeDesert',
    'LavaField': 'RUT_TheForge',
    'PoisonForest': 'RUT_PoisonForest',
    'Scarlands': 'RUT_Scarlands',
    'Volcano': 'RUT_TheForge',
    'Wasteland': 'RUT_Wasteland',
    'ZBiome_Badlands': 'RUT_CrackedLands',
    'ZBiome_DesertOasis': 'RUT_WeepingStones',
    # ZBiome_Grasslands was never renamed - carried unchanged, not a dict entry.
}


def resolve(biome):
    """OLD_TO_NEW_BIOME[biome] if biome is a pre-migration name, else biome unchanged."""
    return OLD_TO_NEW_BIOME.get(biome, biome)
