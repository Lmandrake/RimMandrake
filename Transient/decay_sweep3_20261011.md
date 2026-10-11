# Decay sweep 3 — FOUNDRY queue ranks 61-100 (2026-10-11)

Offline. origin/main 19ba7aff3 checked via scratch clone. Ranks 94, 95, 97, 99 duplicate IN PROGRESS rows (ASSAILANT_DUNGEON_BUILD_1, HELIX_TELLUROX_BUILD_1, PLOT_MECHANISM_MODS_WAVE_1, HORRORS_RAIDING_FACTION_1), so 36 unique items.

## Counts
closed 0 · dropped 0 · implemented 1 · left as-is 35

## Implemented
- GELATINOUSSLIME_VAULT_SEAL_BREACH_1: seal def + V5 placement shipped in GELATINOUSSLIME_VAULT_SEAL_PLUG_1 (closed 07bd43cb2); slime side already built. Only live proof owed (A1/A2, L2, bridge).

## Left, with the reason (none provably done or dead)
- Live/bridge/owner only: SOORRAK_INSTANT_JOB_LOOP_1, ART_OVERRIDE_FAMILY_SCRIPT_1 (live layer), RIVER_STEAM_ANIMATION_1, TREE_GRAPHICS_OWNERSHIP_1, UNUSED_MUTATORS_WORLD_ASSIGNMENT_1, STILLSAND_GLASS_CHAIN_REMAINDER_1, FORGE_DHUVVOX_SWARM_REMAINDER_1 and STARWARS_JUNK_RESKIN_1 (needs owner), BLUEDESERT_GPT_ENRICHMENT_1 (all offline done except part-3 art).
- Art-blocked: JOSSUR_FLIGHT_FRAMES_1 (artpipe has no frame jobs), MIASMA_WARDEN_MOTHER_ART_1 (Aged2 east/north failed jobs, only south done; owner eyes), GELATINOUSSLIME_KIT_ART_1, ALPHA_ANIMAL_PORTS_REHOME_1 (renames done 818c513d9; Chikka/Skorra/Vurra art does not exist), SWALE_CANAL_ART_REFERENCE_1.
- Partial, large offline builds (>20 min, C# or design): CONTAGION/BLUEDESERT/CAULDRON/CRACKEDLANDS_*/LEANINGSCRUB mechanics, FORGE_CYCLE_MECHANICS_1, FORGE_SKY_PASTURES_1, STILLSAND_SAND_SWIM_REMAINDER_1, STILLSAND_SOLAR_STILL_1, WARSCAR_HOSPICE_DESERTERS_1, WARSCAR_OLD_TONGUE_1, SCALD_WALKING_PASTURE_1 (trample ruling now owes C# + warning), SCALD_BATHING_RITE_1, SEABED_PER_SEA_FLOORS_1, SARLACC_SEEKER_ROOTING_1, ABYSS_HIDDEN_SHIP_PROBES_1, GELATINOUSSLIME_PIT_SOLVENT_1 ("Rot's finest" names no def; needs design), SUBSTRUCTURE_PROPS_LAYER_OOB_1 (nothing landed, needs live repro).
- CRACKEDLANDS_FULL_RENAME_1: not done — 164 files on origin/main still name FloodedCanyon (src, design, items); also gated on live-tile check.
- REPO_RENAME_SYMLINK_RETIRE_1: not done — Windows symlink D:\Luke\dev\Rimworld still present, csproj/Lodestar path lines outstanding; touches Windows and Lodestar state.
