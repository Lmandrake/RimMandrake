# FOUNDRY_REBOOT_HANDOFF_202610031504 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202610030327`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

Tonight's work was only partly features: the biggest finds came from LIVE LOADS and the live situational runs, not from building. A cold composed-deploy load (1) showed real defects the offline checks passed (invalid XML fields, a nonexistent `PatchOperationAddOrReplace`, a `CompProperties_Equippable` type that does not exist, misplaced `butcherProducts`, missing SoundDefs, TrainabilityDef `Simple`), and (2) the audit of `PatchOperationFindMod` found 12 guards that silently matched nothing (FindMod needs the exact About <name>; the folded biome mods are named by the composed mod 'RimMandrake: Baroque Biomes'; `Ludeon.RimWorld` must be `Core`). So: deploy a CLEAN tree (never while agents edit: a deploy copies half-written files and the launch gate then refuses), read the Player.log error classes, and run `situational_rerun --mods ...` before believing any offline PASS. `Transient/pass6_remaining_fails_20261003.txt` is the exact open list.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Your full mod list is restored (`modlist_swap --restore`, 610 mods from FULL.LATEST); CLAUDE.md says 631 active, so check whether FULL.LATEST is current before launching your campaign.
- Questions that are yours: the sando adult (MIASMA_ROUND2_IMPORTS_1); god choice for the Margin Bath, Ta'Baa (SCALD_BATHING_RITE_1); FINDMOD_ROT_SPORE_KIT_GUARD_1 (an inert guard); whether to tint the Jawa fallback hood (JAWA_SWIM_HOOD_KEEP_1: the 'pale blue blob' was probably that hood); `RUT_PropaneLake` density (frozen); the lacquer cloak/Chotrix art; fulgurite art acceptance; the Forge audio source (FORGE_VOICES_AUDIO_1 blocked on you).
- Design calls I made that you may veto (each in its work_*_20261003.md): braces add no SubstructureSupport; sealed dhuvvox stays a nodule drawing; sweetline visitors are abstract road-folk; vissler arms are rotting meat; mee/faa moved to Twilight; Gharrek/durrgak/etc. numbers are INVENTED.
- Everything built tonight is offline-proven only; nothing is play-tested. 36 mods now have a first script; none has a recorded live run yet (situational_rerun records from now on).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `ABYSS_DARK_BUILD_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `ABYSS_DURRGAK_BUILD_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `ABYSS_ETCHCAP_BUILD_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `ABYSS_ETCHFALL_BUILD_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `ABYSS_GHARREK_BUILD_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `ABYSS_HIDDEN_SHIP_PROBES_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `ABYSS_KRIZZAK_BUILD_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `ACOUSTIC_SCANNER_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `ASSAILANT_SALVAGE_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `BACTA_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `BLUE_DESERT_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `BRAIN_WORMS_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `CAULDRON_VENT_ENRICHMENT_HOOKS_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `CHILL_DIVE_DENSITY_SAMPLER_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `CHILL_FLOOR_CAST_TRIM_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `CHILL_FREE_TIER_CATCH_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `CHILL_NATIVE_COLD_TOLERANCE_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `CHILL_RETURN_COMB_LANDMARK_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `CHILL_WAX_PROCESSION_GIANT_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `CHILL_ZHIIL_FLOOR_BODY_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `CONTAGION_GROWN_LIMBS_ART_1` — Pillar Arm and Lash art wired (942c70af7), icons for Eyeburst/Caudal Spring/Bellows queued in artpipe; NEXT: collect the three finished icons from artpipe done/ and wire them, then check the render offsets in game with the owner
- `DROID_REPAIR_JOBS_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `EGG_RECKONING_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `ENVIRONMENTAL_HAZARDS_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `EXPLOSIVE_GROWTH_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `FEVERWOOD_TIER_LEAKS_FIX_1` — leaks 1, 4, 5 fixed and committed (16765aa02), 2 and 3 judged not leaks; live criteria unmeasured; NEXT: read the live roster/genstep state on a Feverwood map and close
- `FLOODED_CANYON_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `FOOTPRINT_TRACK_GRID_1` — the grid was already built at 84a377bf0; tonight's pass filled gaps and committed it (b398167660); NEXT: close it with --sha 84a377bf0 after reading its criteria, then unblock WARSCAR_CHOTRIX_SIGNS_1
- `FORGE_DHUVVOX_SWARM_REMAINDER_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `FORGE_KEELWORK_REMAINDER_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `FORGE_SKY_PASTURES_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `FORGE_WHITE_PLUME_FRONTS_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `GELATINOUSSLIME_ARCHIVE_RESURRECTION_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `GELATINOUSSLIME_DWOMMO_FLIER_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `GELATINOUSSLIME_FARM_RUINS_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `GELATINOUSSLIME_FUBBUM_HUNTER_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `GELATINOUSSLIME_GAPPO_FAMILY_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `GELATINOUSSLIME_GENE_TEXT_TIER_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `GELATINOUSSLIME_GLURRO_SALVE_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `GELATINOUSSLIME_KIT_ART_1` — finished art wired, 15 artpipe jobs queued (a54470352); NEXT: collect finished jobs with artpipe_state.py, repoint the vanilla stand-in texPaths, close
- `GELATINOUSSLIME_RAIN_STRIP_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `GELATINOUSSLIME_SETTINGS_SWITCHES_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `GELATINOUSSLIME_TITAN_CHUNK_BOMB_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `GELATINOUSSLIME_VAULT_SEAL_BREACH_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `GIZKA_STOWAWAY_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `GRAFFITI_IMPERIAL_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `GRAVSHIP_LANDING_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `GREENTIDE_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `HOSTILE_FLORA_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `JAWA_SWIM_HOOD_KEEP_1` — fix built and committed (cd444fe8c) in src/RimStarWars/JawaRules, never deployed or seen in game; NEXT: deploy JawaRules at the next game-down, send a hooded Jawa swimming, read the hood node's CanDrawNow (true; false with swimHoodEnabled off)
- `LEANINGSCRUB_SWEETLINE_VISITORS_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `LONG_SHADE_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `LORE_STAGES_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `LUMINOUS_PIGMENT_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `MIASMA_AMBUSH_FROG_REMAKE_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `MIASMA_ATTAR_STILL_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `MIASMA_FLOTSAM_YARD_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `MIASMA_FREE_NURSERY_YOUNG_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `MIASMA_FREE_SALT_CRUST_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `MIASMA_ROUND2_IMPORTS_1` — four RSW_ ports built in SWBestiary (fccf0f1b3); the sando adult is held by the item; NEXT: ask the owner about the sando adult, then close
- `MIASMA_SETTINGS_SWITCHES_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `MIASMA_SWARM_COMPOSTER_PORT_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `MIASMA_WARDEN_MOTHER_ART_1` — aged life-stage defs written, 6 art jobs queued (9ca6c487e); NEXT: collect the WardenMother art into Miasma/Textures/Things/Pawn/Animal/Miasma/WardenMother/ and close
- `MIASMA_YOUNG_CALL_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `MOVING_DUNES_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `NABOO_FISH_TO_TWILIGHT_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `NIGHTSIDE_ICE_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `OASIS_MAKER_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `PROXIMITY_HATCH_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `PYRINTH_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `RUST_CATHEDRAL_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `SARLACC_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `SCALD_BATHING_RITE_1` — pitched only (Ta'Baa, RUT tier, abd629726); nothing built: no cove, no found-rite machinery; NEXT: build the margin cove and the shared found-rite machinery, or block the item with that reason
- `SCALD_FLOOR_VENT_FIELDS_1` — gen step, forecast, sailors built (ad5afe347); listed only on the retiring hatch generator; NEXT: list the step on the seabed floor generator when SEABED_PER_SEA_FLOORS_1's floor generator exists; art jobs for glasskelle/pulsebead are queued
- `SCALD_IMMERSION_BERTH_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `SCALD_RETURN_GALLERY_1` — manifold, five outlets, locker built (a8a4998ec); schematic unlock is SCALD_GALLERY_SCHEMATIC_UNLOCK_1 (owner); NEXT: list the gen step on the seabed floor generator; art job scald_return_gallery_hub_v1 queued
- `SCALD_SAAL_ONE_NAME_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `SHIP_VERMIN_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `SHOKK_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `STILLSAND_CAVE_AS_PLACE_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `STILLSAND_CAVE_TIER_ROWS_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `STILLSAND_EVENT_CREATURES_REMAINDER_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `STILLSAND_GEOPHONE_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `STILLSAND_GLASS_CHAIN_REMAINDER_1` — krayt lens patch, goggles variant, art wired (0dd38e330); lens bench art job re-queued; NEXT: copy the finished RM_LensBench_v2 over Textures/Things/Building/Production/RM_LensBench.png; fulgurite swap waits on owner acceptance
- `STILLSAND_SAND_SIEVE_CHORE_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `STILLSAND_SAND_SWIM_REMAINDER_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `STILLSAND_SOLAR_STILL_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `STILLSAND_SUN_LANCE_1` — built, minifiedDef fix live-clean (b9ac773e4); no-ignite rests on the existing verb code; NEXT: run the lance live in a sun/no-sun pair and read that no fire spawns
- `TERMINAL_BIOMES_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `THE_BAZAAR_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `THE_ROT_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `THE_SUMP_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `TITANIC_CREATURES_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `TROPHY_CRAFT_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `WARCASKET_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `WARSCAR_CHOTRIX_BUILD_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `WARSCAR_FREE_TIER_BODY_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `WARSCAR_GEIGER_CHOIR_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `WARSCAR_HOSPICE_DESERTERS_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `WARSCAR_OLD_TONGUE_1` — panels, skill gate, unlock flags built (e95f75751); hospice/projector/pool effects belong to other items; NEXT: wire HospiceUnlocked consumers, close when live reads pass
- `WARSCAR_SETTLING_WEATHER_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `WARSCAR_TOTCHAK_WAKES_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `WARSCAR_TURRETS_TRACK_1` — aim comp built, patch rewritten as PatchOperationConditional (f5469f92d); tracking never seen live; NEXT: redeploy, then read RM_CompTurretAim state beside a walking pawn (the mover Goto must actually run)
- `WASTELAND_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `WEBWORK_FIRST_SCRIPT_1` — first script written and committed, static PASS, never run live; NEXT: run its suite live in a tier that contains the mod (situational_rerun --mods <Mod> now records through record_run), then close with the run id
- `WEEPINGSTONES_DEWSILK_COCOON_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `WEEPINGSTONES_MURRIN_CATCH_WIRING_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `WEEPINGSTONES_OASIS_MUTATOR_FLORA_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `WEEPINGSTONES_SETTINGS_SLIDERS_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `WEEPINGSTONES_TRUCE_HUNT_SUPPRESSION_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block
- `WEEPINGSTONES_WALKING_CONDENSER_1` — built offline and committed; live criteria unmeasured, art placeholders where noted in its work_*_20261003.md; NEXT: after the next clean composed deploy, run its mod's suite via situational_rerun, read the item's verify state, close or block

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `pkill -f` / `pgrep -f "<pattern>"` match my own shell and kill it (exit 144), and process-wait loops match themselves: use `ps -eo pid,args | grep "[p]attern"` and wait on a PID (see: lessons).
- Deploy from a tree agents are editing ships half-written files: `launch_gate` then refuses the map; deploy only from a clean tree (see: Transient/pass6_remaining_fails_20261003.txt).
- `get_defs` returns record lists and modExtensions as bare type names/field values unless `deep=True`: three suites misread a healthy patch as absent (see: DivingInteraction/validation.py sea_biomes_name_their_floor).
- A component that raises `ExpectationFailed('UNMEASURED: ...')` records FAIL; use the suite's `_unmeasured(t, why)` (see: Scarlands/validation.py).
- Site cells off the runner anchor can fall off the 250x250 map: re-base on the live `map_info` centre (see: Contagion/validation.py `_pad`, WeepingStones `_enter`).
- `deploy_custom_mods --compose` skips DEPLOY_HOLD files and keeps stale deleted-from-repo files in the deployed copy (remove them with a `${VAR:?}` guarded rm) (see: Transient/loadlog_errors_20261003.txt).
- `/tmp` is tmpfs: a full clone of this repo (8 GB .git) fills it; push through `./publish` or a `--depth 1` clone only (filed: lessons).

## Closed since the last handoff (2)

- `NORTHSTAR_BLAND_TILE_1` — 596735161
- `LIQUID_TYPES_MOD_1` — eaf0e96e4

## Filed and still open (7) — the next seat's queue

- `SILTTRAP_TERRAINS_UNBUILT_1` — TerminalBiomes silt-trap does nothing: the two terrains it converts to were never built (read from source 2026-10-02); weir and silt-trap also go dead
- `MINERAL_BIOME_LEAKS_1` — Our biome minerals leak planet-wide (read from defs 2026-10-02): Webwork silk knot scatters on every rocky map; deep drilling anywhere can hit lantern
- `GRAFFITI_WALL_LINKED_CROP_1` — Graffiti wall marks may draw only a 1/16 crop of their art: wall-linked graphics treat a texture as a 4x4 atlas and ours are single centred images (re
- `SCALD_GALLERY_SCHEMATIC_UNLOCK_1` — Return Gallery: what the immersion-engineering schematic unlocks (RM_ImmersionSchematic is an inert item today)
- `FINDMOD_ROT_SPORE_KIT_GUARD_1` — RotDecayHarvest_LivingProduce.xml guards on FindMod 'RimUtinni: Rot Spore Kit', which matches no mod (inert); which mod's name should it guard on, or 
- `WARSCAR_CHOTRIX_SIGNS_1` — Chotrix readable signs: track-grid prints and dragged-kill marks (needs FOOTPRINT_TRACK_GRID_1), tetchik silence ring (needs WARSCAR_GEIGER_CHOIR_1); 
- `SHIPVERMIN_MYNOCK_KIND_NAME_1` — Verify: ShipVermin wreck-nest roster names PawnKind 'Mynock' but the ported species is RSW_Mynock (script reports it red live; with the donor mod abse

## Commits

```
f8edd17d3 pass 6 live results (12 suites) and the 11 remaining FAILs; ledger
c3c448f95 ledger: BENCH seat ready
c51eed9a0 LongShade: RM_Shadespire_a replaced with rendered artpipe job RM_Shadespire_c
f6213df5b situational_rerun records each mod's run in the modcheck status record (record_run, never invents PASS, dry runs record nothing) + 4 selftest cases; Wasteland settings round-trip compares a bool restore as a bool (selftest was red from tonight's chain)
67ba08e0d First north-star scripts: DroidRepairJobs, EggReckoning (new, RimUtinni); TerminalBiomes suite extended to 61 chains (zero-chains cause: checks sat outside t.component), 38 settings flips, defs_resolve; none run live
dfeabbace First north-star scripts: Sarlacc, Shokk, TrophyCraft (new); Shokk skin patch labelPlural was a silent no-op (the def has no labelPlural node): nomatch Add fixes it; none run live; no modset tier exists for these mods
47459656b First north-star scripts: BrainWorms, GizkaStowaway, GraffitiImperial (new, RimStarWars layer); none run live; hediff/mental-state/modExtension read shapes unproven
fbcd54b32 file SHIPVERMIN_MYNOCK_KIND_NAME_1 (verify before fixing)
f1269cd75 First north-star scripts: ProximityHatch, ShipVermin, TitanicCreatures (new); none run live; ShipVermin nest roster may name 'Mynock' while the port is RSW_Mynock
de6bd80a3 First north-star scripts: TheBazaar (new, slice 1 only: unbuilt parts UNMEASURED); Warcasket and Bacta keep their suites plus a settings round-trip and static entry; none run live
d86360412 First north-star scripts: MovingDunes (4 Harmony rules, 6 slow chains), NightsideIce, OasisMaker (site growth on a staged pad) (new); none run live; debug-action path and Granite_Rough pad assumptions unproven
a2f23a998 First north-star scripts: RustCathedral, Webwork (new); Wasteland keeps its 1940-line suite plus a settings round-trip and static entry; none run live; Wasteland standalone modcheck run cannot find the biome (needs the composed route)
df8e3b7f3 First north-star scripts: TheRot (113 defs, 18 settings), TheSump (reads DEPLOY_HOLD: 18 live, 35 held reported UNMEASURED-by-hold), Pyrinth (dormant, no settings class); none run live
ec8fed3ef First north-star scripts: EnvironmentalHazards (95 components, 63 settings), GravshipLanding, LoreStages (new); none run live; no bridge tool drives LoreStages SetStage/Reapply
13f3e3845 First north-star scripts: FloodedCanyon, Greentide (new, 25/16 generated settings round-trips, behaviour chains, EXPECT_MODS = the composed biomes mod); ExplosiveGrowth keeps its 33-chain suite plus defs_resolve and static entry; none run live
478b504aa First north-star scripts: AcousticScanner, AssailantSalvage (new), BlueDesert (static entry added to its existing 59-component suite); none run live; several live tool shapes unproven (listed in the walks)
115b01a83 First north-star scripts: HostileFlora, LongShade (new), LuminousPigment (settings round-trip + static entry added to its 69-component suite); none run live; HostileFlora swarm check needs a mental-state read tool
8e5a6fec7 Load-log fixes (set E): chunk verb has no forcedMissRadius (projectile is not explosive) and Neolithic tech level; vissler arm socialPropernessMatters
f455cb8a3 TheForge: sky pastures (column haze section layer on an RM_SkyColumns mesh flag, ash spirals, prey score favouring columns + jossur stoop that only calls StartFlying, flier-selected column highlight), 5 toggles; owner question (which defs are aerofleets) open; live unproven
bada76fdf Slime chunk: CompEquippable declared the vanilla way (CompProperties_Equippable does not exist, so the whole chunk def was discarded live); Diving floor-wiring check reads modExtensions with deep=True (the patch was applied all along)
... 192 more: git log --oneline 3cd90f61f..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : UP  → corrected to DOWN, measured now
- Bridge: FREE    since 2026-10-03T15:04:09Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   mine: modset_builder tier-swap backups from tonight, derived, leave uncommitted
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   mine: modset_builder tier-swap backups from tonight, derived, leave uncommitted
?? deployed/config/ModsConfig.before-tier-flowworks.xml   mine: modset_builder tier-swap backups from tonight, derived, leave uncommitted
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   mine: modset_builder tier-swap backups from tonight, derived, leave uncommitted
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   mine: modset_builder tier-swap backups from tonight, derived, leave uncommitted
?? deployed/config/ns_flowworks_backup.20261002T070221.json   mine: modset_builder tier-swap backups from tonight, derived, leave uncommitted
```

