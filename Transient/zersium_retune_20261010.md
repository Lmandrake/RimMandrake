# Zersium retune 2026-10-10

## Task A: ZERSIUM_FORGE_BIOME_1 (offline fix, L5 live re-read OWED with bridge)
Cause (from decompiled GenStep_ScatterLumpsMineable/Scatterer): count = RoundToInt(0.3~0.5 per 10k * 62500/10000) = 2 lumps;
each lump needs a random cell from CellFinderLoose.TryFindRandomNotEdgeCellWith (bounded random draws) whose edifice is
natural rock, and Generate RETURNS on the first failed draw, so sparse rock => 0 lumps (3 of 4 maps). Also ScatterAt can
spawn 0 cells (lump validator needs Caves==0) with no retry. Fix: RUT_GenStep_ZersiumForgeLumps now guarantees minLumps
(PROVISIONAL 2, def field) via exhaustive scan of eligible rock cells when the random draw fails, counts only lumps that
spawned ore, warns if under the floor. Guard: validation.py zersium_forge.zersium_min_lumps_guard (minLumps>=1 + fallback present).
Residual: a Forge map with literally no natural rock still gets 0 (warning logged).

## Task B: BRONZIUM_DROP_1 -- NOT built, blocked
Blockers: (1) runtime bronzium is the donor guy762.mm.kotorcore; the cut needs Cherry Picker entries whose config is not in-repo
(absorbed copies are DEPLOY_HOLD'd) plus a scoped patch for the junk pile mineableThing; (2) 4 placed things on the exported ship
(Gravship_v2_ring_2026-09-12.xml lines 25608,25643,35536,35553 stuffDef KOTOR_AlloyBronzium) need a replacement stuff chosen --
design says only "re-stuffed", target unspecified; alias via RM_DefAliasDef (EnvironmentalHazards). Files touched would be
Armoury Absorbed_KotorCore Metals2/JunkPile + Absorbed_KotorWeapons lgtbattlearmor (not Durasteel files).
