# belt bridge5 — full-list sitting, 2026-10-09 (helper #4)

## Status
- 20:44 started; bridge held by FOUNDRY; game UP full list (613), rehearsal COPY loaded (never save).

## SHOKKWEAVE_SOLE_SOURCE_1 A1 (ProofHarvest hook vs Real FoW)
- 20:55 hook rebuilt b09a57710: ProofHarvest + ProofHarvestDesignate step single ticks (DoSingleTick, max 250) until the RealFoW-prefixed Deconstruct designator accepts; output adds "(after T ticks)". Built clean. Deploy: the composed-biomes apply wrote 9 other files but the DLL STILL DIFFERS (locked by the running game) -> takes effect only after a game-down redeploy (`deploy_custom_mods.py --compose biomes --apply`) + load. A1 rerun is therefore owed next load; no in-game rerun possible now (no live public static reaches the RealFoW-patched designator on an existing thing).

## Acceptance sweep (rimflow next --acceptance --seat FOUNDRY)
- 21:05 DONOR_CODE_BURST_REBUILD_1 A1 PASS (full-613): get_defs deep=true reads race.deathAction on all 7: 6 AA goo/amoeba/spore/aerofleet = DeathActionWorker_ScaledExplosion, AcidBurn, Filth_SpentAcid, radius 1.5-3.5; AA_Thunderbeast = DeathActionWorker_SummonFlashstorm (radius 8-14). Player.log: 0 error lines naming any of them (2 hits are the VTE save's wool list). Evidence Transient/belt_bridge5_reads1_out_20261009k.txt. (Earlier partials: deathAction unreadable without deep=true.)
- 21:05 KINETIC_BLAST_WEAPONS_1 KA.load PASS (full-613): ruins maker resolves - MapGen_AncientTempleContents.root.options carries RM_ThingSetMaker_KineticRuins (deep read); FleckDef RM_Fleck_KineticRing found; 0 error lines naming KineticArms/ExplosiveKnockback in Player.log.
- 21:15 DONOR_CODE_BURST_REBUILD_1 A2 PASS (full-613, on the rehearsal COPY's map, unsaved): each of the 6 AA acid species killed (Crush) leaves its corpse + Filth_SpentAcid in the 9x9 around it (3/11/17/4/6/3 cells; RedGoo + RedSpore needed a second hit to die); AA_Thunderbeast death -> map condition Flashstorm (ticksLeft 3433). Radii stay PROVISIONAL (not judged here). Evidence Transient/belt_bridge5_burst_out_20261009k.txt.
- UNFINISHED_LINE_* rows: mandrake.rut.unfinishedline is NOT in the full list (type not found) -> minimal-list only, skipped this load.
- LASSO A2: AM settings class not reachable by name via mod_settings_field (AM.Core.Settings static field, type name unresolved); config file still carries no LassoSpawnChance -> unchanged FAIL, not re-recorded. Setting it is build work, not verification.

## Reload needs (batched)
- RUT_DyingCreep graphic type + 12 catch items Meat_Small: parse next load only.
