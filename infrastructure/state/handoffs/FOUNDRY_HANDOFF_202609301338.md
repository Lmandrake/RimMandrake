# FOUNDRY_HANDOFF_202609301338 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202609300527`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**Before believing any "0 errors" reading, check that the game log is still writing.** RimWorld's `Verse.Log` stops completely after 10,000 messages. Tonight 8,994 of those were a mesh-count warning from eight of our plants, fixed at 136d7c228. Past the cap every quicktest reads clean and every mod `[DebugAction]` looks as if it never ran. The first round of quicktests tonight was taken that way and meant nothing. The check: a `Reached max messages limit` line in Player.log, or the absence of any log line after a known write.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Deepfire god deltas added an unlisted rule.** It is the spec's diminish rule: after 10 coats on the same kind of thing, each delta drops to ±1, with a slider (08541549d). Veto it if unwanted. The build also found and fixed a wrong spec claim: LightsOut would have switched off our light proxies.
- **The Chill's six bed plants grow only in liquid propane**, where the dive crew cannot stand. Filed as `CHILL_WALKABLE_BED_TERRAIN_1` (BENCH, needs owner).
- **Grown-limb review sheet is waiting for you:** `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\biomes\contagion_grown_limbs_2026-09-30.md`. It recommends Pillar Arm and Lash first. `CONTAGION_GROWN_LIMBS_BUILD_1` waits on your marks.
- **Conflict with your no-vanishing rule.** Six Contagion natives die with `DeathActionProperties_Vanish`: Skinflap, Gorekite, Danglemaw, Crispling, Sloshbelly and Ogleknot. `CONTAGION_GPT_ENRICHMENT_1`'s Bodyprints part owns converting them. That agent was stopped before writing any code.
- **Proven live on the full list tonight:**
  - Forge: lava plus the full six-phase cycle (freeze, cracks, melt, refreeze).
  - Contagion: the Burn.
  - Middenshell: 20×20, crawls, stays alive.
  - Deepfire: all six proofs pass (floor 22, firstcoat 10, worn glow 15, proxy 17, status 26, god deltas 25).
  - The map-gen scatter crash is gone.
  - Load errors naming our defs dropped from 208 to 38.
  - Grey Sea and Twilight Sea dive floors pass.
- **Placeholder numbers nobody has ruled on:** Middenshell speed, all Deepfire constants (now in Mod Settings), and the sea floor band shares.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `CONTAGION_GPT_ENRICHMENT_1` — claimed and blocked; stopped at your word with no code. NEXT: re-dispatch Opus with the same brief. It includes the vanish→Bodyprint conversion and reuses the SOLAR_HEAT shelter/pathing.
- `SUBSTRUCTURE_PROPS_LAYER_OOB_1` — claimed and blocked, no code. The trace points at GravTide's SectionLayer_GravshipHull corner check reading off-map on the 50×50 dive pocket maps. NEXT: re-dispatch Sonnet to decide whether our dive map puts substructure on its edge or the bug is GravTide's.
- Six more owner-picked enrichments plus `GRAVSHIP_ACOUSTIC_SCANNER_1` — offline and unclaimed: WASTELAND, BLUEDESERT, CRACKEDLANDS, CAULDRON and FORGE `_GPT_ENRICHMENT_1`. NEXT: work them one per agent slot after Contagion.
- `SEA_DIVE_FLOOR_TERRAIN_1` — blocked. The Scald and Chill dive floors have their habitat terrain but grew 0 plants. The likely cause: the pocket map inherits the test parent tile's temperate climate. NEXT: dive from a real Scald or Chill tile. `jawa/world_tile_set temperature=` does not take effect.
- `SWALE_CANAL_ART_REFERENCE_1` — blocked on the `RM_Swale_v2` render. NEXT: review the render, wire it, and drop the placeholder note from the cracked_lands sheet manifest.
- `WARCASKET_CASK_ART_1`, `FORGE_MISSING_ART_1` (CinderCrust needs an identity line) and `JOSSUR_FLIGHT_FRAMES_1` (artpipe has no frame sequences) — blocked. NEXT: wire the renders once `infrastructure/artpipe/done/RM_CaskBay.manifest.json` is ok.
- The mechanics tranches for Cauldron, Contagion, Wasteland, Blue Desert, Cracked Lands, Leaning Scrub, Long Shade and Forge — offline work is done, and the remainders need owner calls, art, audio or live looks, each listed in its ledger note. NEXT: `rimflow show <ID>` when a ruling or asset lands.
- Owner-gated: `ROTSPOREKIT_MAYREQUIRE_ORPHANED_1` (still the one known `selftest_deployed_biome_refs` failure), `FEVERWOOD_SAP_SUCKER_TUNING_1` and `WARCASKET_WASTE_RUN_REMAINDER_1`. NEXT: wait for rulings.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- The RimWorld log stops after 10,000 messages, so every later "no errors" check is false (see: skills/rimbridge/references/traps.md).
- In 1.6 our mods' [DebugAction]s appear flat under `Actions` with a `T: ` prefix, not in a category node (filed: LESSONS).
- `Actions\Regenerate Current Map` wipes colonists, and a generated side map with no colonists is culled. Test on the home map and respawn colonists with `src/RimMandrake/bridgetools/spawn_test_colonists.py`, which also closes the force-pausing faction-naming dialog (filed: LESSONS).
- `jawa/list_pawns` hediffs sit under `health.hediffs`, not `hediffs`. Reading the wrong key gives a confident "0 hediffs" (filed: LESSONS).
- `rimworld/screenshot_cell_rect` cropped the wrong region at far zoom. Crop from the full frame it saves beside the crop (filed: LESSONS).
- `shared_sync.py` replay conflicts when the shared tree created a file that origin already has. Commit such files from a private worktree, and never leave an unpublishable local commit on the shared tree (filed: LESSONS).

## Commits

```
682d9c50a Sea dive live proof round 2 output
f652f0a3c Deepfire round-2 live proof outputs
bbdd49d96 Ledger sync: FOUNDRY live game-up wave - load-error rounds, Forge lava + cycle proven, Deepfire proven, Middenshell, renames, sea bands
84b55e39f SWALE_CANAL_ART_REFERENCE_1: live FlowWorks canal shots, RM_Swale art spec, v2 regen queued
d42de033e terrain_census bridge helper; biome quicktest takes BIOME@tempC; Scald live census
e85d789f2 Deepfire live proof outputs 2026-09-30 + regen_current_map helper for clean-map proofs
4a3b54f88 Live-test harnesses and results from the 2026-09-30 FOUNDRY game-up wave
396bf8d29 Load-round error digest 2026-09-30b (after load-error fixes; log no longer capped)
12d35e601 BENCH handoff 202609300751: Long Shade ticketed, Stillsand turn 3 pending, GPT enrichment items; one-kind-of-heat law in CLAUDE.md
a9844f4fc GPT biome enrichment: owner picks for Cracked Lands, Cauldron, Forge; acoustic scanner cross-biome; rest parked for review
b95259e5b GPT biome enrichment: owner-picked items for Contagion, Wasteland, Blue Desert; consult answers in Transient
75de3cdd3 Ledger sync: Stillsand volley turn 2 rulings
56b08a7d0 Load-round error digest 2026-09-30 (cold load of origin/main 7443a66d7)
fe48c30fd Ledger sync: STILLSAND_BEDAZZLE_SITTING_1 filed and started (program row 9)
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/codebase_health.html     # health publisher (selftest/code-review regen)
 M Transient/codebase_health.json     # health publisher (selftest/code-review regen)
 M Transient/codebase_health_artifact.html     # health publisher (selftest/code-review regen)
 M deployed/config/ModsConfig.before-tier-pits.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
 M design/Jawa/worldbuilding/biomes/_def_bindings_2026-09-09.md     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
 M design/Jawa/worldbuilding/biomes/rosters/the_propane_lakes.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
 M design/Jawa/worldbuilding/biomes/terminal_seas_cast_proposal_2026-09-25.md     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
 M design/RimMandrake/flowworks_liquid_matrix.md     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
 M design/RimMandrake/sea_dive_maps_spec.md     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
 M design/RimMandrake/sea_shore_mutator_spec.md     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
 M design/RimUtinni/vanilla_beast_excision_census.md     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
 D infrastructure/artpipe/active/RM_BloodyMess_v2_east.json     # artpipe daemon
 D infrastructure/artpipe/active/RM_Boilhide_v2_east.json     # artpipe daemon
 D infrastructure/artpipe/active/RM_Gloomcast_east.json     # artpipe daemon
 M infrastructure/artpipe/daemon_run_20260927_derivefacings.log     # artpipe daemon
 D infrastructure/artpipe/failed/rut_greentideant_carapacewall_atlas.json     # artpipe daemon
 D infrastructure/artpipe/failed/rut_greentideant_carapacewall_menuicon.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_BloodyMess_v2_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_BloodyMess_v2_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Boilhide_v2_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Boilhide_v2_south.json     # artpipe daemon
AD infrastructure/artpipe/pending/RM_CaskBay.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_CloudRepulsor_v2.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_CrownVenomvine.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Cruststar.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Crustweevil_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Crustweevil_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Crustweevil_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_DewfringeSprig.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_DhokkurDormant.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Dhokkur_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Dhokkur_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Dhokkur_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_DhuvvoxNodule.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Dhuvvox_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Dhuvvox_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Dhuvvox_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_DrippingVenomvine.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Dustflutter_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Dustflutter_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Dustflutter_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Eskith_v2_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Eskith_v2_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Eskith_v2_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Eyebark_v2.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Filth_DisturbedSand.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Filth_DragMark.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Fleshsop_v2_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Fleshsop_v2_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Fleshsop_v2_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Floatstone.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_FloatstoneGarden.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_FossilSkeleton_v2.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Fuzzrunner_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Fuzzrunner_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Fuzzrunner_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Fuzzviper_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Fuzzviper_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Fuzzviper_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Gloomcast_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Gloomcast_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_GreatDevourer_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_GreatDevourer_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_GreatDevourer_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Grimewing_v2_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Grimewing_v2_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Grimewing_v2_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Gristleswarm_v2_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Gristleswarm_v2_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Gristleswarm_v2_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Groundrunner_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Groundrunner_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Groundrunner_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_HalfExtractedCore.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_HollowVenomvine.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Jossur_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Jossur_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Jossur_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Julmox_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Julmox_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Julmox_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Krannock_v1_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Krannock_v1_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Krannock_v1_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Maidenbloom.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_MatureFleshbeast_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_MatureFleshbeast_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_MatureFleshbeast_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Middenshell_v2_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Middenshell_v2_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Middenshell_v2_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Mirrak_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Mirrak_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Mirrak_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Muttavaq_v2_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Parasol.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_ParasolWorn_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_ParasolWorn_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_ParasolWorn_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Pavecrust.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Pillowmoss.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Ribbonwhip_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Ribbonwhip_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Ribbonwhip_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Rollbug_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Rollbug_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Rollbug_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Scumslider_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Scumslider_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Scumslider_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Seismograph_v2.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_ShadeTent.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Shadespire.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Shirrel_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Shirrel_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Shirrel_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Shokka_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Shokka_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Shokka_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Sippra_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Sippra_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Sippra_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Skarrok_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Skarrok_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Skarrok_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Slagmole_v2_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Slagmole_v2_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Slagmole_v2_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Sloghog_v2_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Sloghog_v2_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Sloghog_v2_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_SunShield_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_SunShield_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_SunShield_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Surrik_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Surrik_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Surrik_south.json     # artpipe daemon
AD infrastructure/artpipe/pending/RM_Swale_v2.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Tanglefuzz.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Tazzok_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Tazzok_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Tazzok_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Thornhold_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Thornhold_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Thornhold_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Tikkit_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Tikkit_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Tikkit_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_TruffleMole_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_TruffleMole_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_TruffleMole_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_TwitcherVenomvine.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_VenomvineThicket_v2.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Vexxiss_v2_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Vexxiss_v2_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Vexxiss_v2_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Vhaulk_v2_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_VisslerArm.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Vissler_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Vissler_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Vissler_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Vrekka_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Vrekka_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Vrekka_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Whipfuzz.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_WreckedCart.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Zellik_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Zellik_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RM_Zellik_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RSW_CrawlerTreadWreck.json     # artpipe daemon
 D infrastructure/artpipe/pending/RSW_WreckedSkiff.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientAirlock.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientAirlock_Large.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientBlackBox_Off_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientBlackBox_Off_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientBlackBox_Off_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientBlackBox_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientBlackBox_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientBlackBox_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientFloorHeater.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientLandmine.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientShieldedTurret.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientShipLandingBeacon.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientSpacerAutocannon.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientTransmitterBeacon.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientWargamingTable_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientWargamingTable_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_AncientWargamingTable_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_BlueprintsBench_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_BlueprintsBench_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_BlueprintsBench_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_BustedShieldedTurret.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_BustedSpacerAutocannon.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_CryptoAncientTerminalBank_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_CryptoAncientTerminalBank_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_CryptoAncientTerminalBank_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_CryptoAncientTerminal_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_CryptoAncientTerminal_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_CryptoAncientTerminal_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_ForcedAncientAirlock.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_ForcedAncientAirlock_Large.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_FrozenEmptyCryptosleepPod.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_JammedAncientAirlock.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_JammedAncientAirlock_Large.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_RuinedHospitalBed_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_RuinedHospitalBed_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/RUT_RuinedHospitalBed_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/coalescence_stage2_v2.json     # artpipe daemon
 D infrastructure/artpipe/pending/coalescence_stage3_v2.json     # artpipe daemon
 D infrastructure/artpipe/pending/rsw_blurrg_v1_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/rsw_blurrg_v1_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/rsw_blurrg_v1_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/rsw_scrapnestbird_v1_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/rsw_scrapnestbird_v1_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/rsw_scrapnestbird_v1_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/rsw_shrublandgiant_v1_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/rsw_shrublandgiant_v1_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/rsw_shrublandgiant_v1_south.json     # artpipe daemon
 D infrastructure/artpipe/pending/rsw_tunnelsnake_v1_east.json     # artpipe daemon
 D infrastructure/artpipe/pending/rsw_tunnelsnake_v1_north.json     # artpipe daemon
 D infrastructure/artpipe/pending/rsw_tunnelsnake_v1_south.json     # artpipe daemon
 M infrastructure/artpipe/registry.jsonl     # artpipe daemon
 M infrastructure/artpipe/throughput.jsonl     # artpipe daemon
 M infrastructure/dashboards/hub/data/health.json     # health publisher (selftest/code-review regen)
 M infrastructure/state/codebase_health_last.json     # health publisher (selftest/code-review regen)
 M infrastructure/state/ledger/events/BENCH.jsonl     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
M  infrastructure/state/ledger/events/FOUNDRY.jsonl     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
 M infrastructure/state/ledger/events/OWNER.jsonl     # OWNER ledger shard (not FOUNDRY)
M  infrastructure/state/queue/BENCH.md     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
M  infrastructure/state/queue/FOUNDRY.md     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
 M src/RimMandrake/bridgetools/prove_biome_timelapse.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/ModsConfig.FULL_plus_bacta_2026-09-24.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/Player.log.before_COLD_LOAD_RUN_SHEET_4_2026-09-23     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/Player.log.geneticrim_ctor_nre_2026-09-25     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/Player.log.pre-scald-round-20260926     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_facing_contradiction_manifests/     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Ashworm_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Ashworm_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Ashworm_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Barbthorn_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Barbthorn_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Barbthorn_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_EmberCarpet.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Korrum_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Korrum_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Korrum_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Scrubgrass.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Spinerat_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Spinerat_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Spinerat_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Sporemass_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Sporemass_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Sporemass_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Sporepaw_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Sporepaw_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Sporepaw_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Starvine.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Stoneback_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Stoneback_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Stoneback_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/RSW_Whirlbloom.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_chimeglobe.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_chimeglobe_b.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_dorrak_dessicated.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_dorrak_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_dorrak_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_dorrak_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_glassfern.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_glassfern_b.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_glassfern_c.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_krissek_dessicated.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_krissek_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_krissek_halo_mote.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_krissek_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_krissek_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_palefloss.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_palefloss_b.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_palefloss_c.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_vekkit_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_vekkit_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/bluedesert_vekkit_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/canon_dewback_v1_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/canon_insectomorph_v1_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_brekkugar_east.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_brekkugar_north.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_brekkugar_south.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_dhukk_east.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_dhukk_north.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_dhukk_south.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_ghorrumak_east.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_ghorrumak_north.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_ghorrumak_south.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_gruzz_east.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_gruzz_north.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_gruzz_south.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_hulggarok_east.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_hulggarok_north.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_hulggarok_south.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_kessik_east.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_kessik_north.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_kessik_south.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_shekkur_east.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_shekkur_north.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_shekkur_south.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_thrizzik_east.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_thrizzik_north.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_thrizzik_south.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_ulkhorr_east.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_ulkhorr_north.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_ulkhorr_south.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_vrakk_east.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_vrakk_north.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_vrakk_south.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_zekkra_east.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_zekkra_north.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_zekkra_south.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_zhurrakor_east.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_zhurrakor_north.manifest.1790311643.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/crags_zhurrakor_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_falumpaset_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_feralgrazer_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_feralgrazer_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_feralgrazer_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_feralnerf_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_feralnerf_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_feralnerf_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_graniteslug_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_graniteslug_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_graniteslug_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_grank_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_grank_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_grank_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_greaterkraytdragon_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_greaterkraytdragon_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_greaterkraytdragon_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_horax_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_horax_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_horax_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_jakobeast_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_jakobeast_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_jakobeast_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_kowakianmonkeylizard_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_kowakianmonkeylizard_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_kowakianmonkeylizard_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_kraytdragon_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_kraytdragon_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_kraytdragon_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_krykna_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_krykna_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_krykna_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_mossbeetle_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_mossbeetle_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_mossbeetle_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_mossbeetlepupa_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_mossbeetlepupa_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_mossbeetlepupa_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_nerf_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_nerf_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_nerf_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_pikobis_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_pikobis_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_pikobis_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_plant_bloddle.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_plant_chakroot_wild.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_plant_hubbagourd_wild.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_plant_nysyllin_wild.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_porg_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_porg_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_porg_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_qormot_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_qormot_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_qormot_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_runyip_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_runyip_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_runyip_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_shaak_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_shaak_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_shaak_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_strill_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_strill_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_strill_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_teemuss_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_teemuss_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_teemuss_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_uvak_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_uvak_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_uvak_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_varactyl_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_varactyl_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_varactyl_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_voorpak_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_voorpak_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_voorpak_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_vulptex_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_vulptex_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_vulptex_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_warwyrm_east.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_warwyrm_north.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_warwyrm_south.manifest.1790254960.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_whisperbird_east.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_whisperbird_north.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_whisperbird_south.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_zeer_east.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_zeer_north.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/desertportb_zeer_south.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_brathek_east.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_brathek_north.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_brathek_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_chellow_east.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_chellow_north.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_chellow_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_drommath_east.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_drommath_north.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_drommath_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_gorrameth_east.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_gorrameth_north.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_gorrameth_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_grolth_east.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_grolth_north.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_grolth_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_kurreth_east.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_kurreth_north.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_kurreth_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_lommerel_east.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_lommerel_north.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_lommerel_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_murrelith_east.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_murrelith_north.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_murrelith_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_nemmel_east.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_nemmel_north.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_nemmel_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_ollareth_east.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_ollareth_north.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_ollareth_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_plant_ossagrel.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_plant_skethral.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_plant_thulvane.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_plant_tullick.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_plant_verrow.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_silloch_east.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_silloch_north.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_silloch_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_skellick_east.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_skellick_north.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_skellick_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_skreth_east.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_skreth_north.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_skreth_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_thavrik_east.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_thavrik_north.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_thavrik_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_thornbug_east.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_thornbug_north.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_thornbug_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_vaulm_east.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_vaulm_north.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/feverwood_vaulm_south.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_animalpersonhood.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_blindsight.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_bloodfeeding.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_cannibal.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_collectivist.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_darkness.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_femalesupremacy.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_fleshpurity.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_guilty.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_highlife.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_humanprimacy.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_individualist.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_inhuman.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_loyalist.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_malesupremacy.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_natureprimacy.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_nudism.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_painisvirtue.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_proselytizer.manifest.1790311644.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_raider.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_rancher.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_ritualist.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_shipborn.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_supremacist.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_transhumanist.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_treeconnection.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/glyph_tunneler.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_crossout.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_paste_flyer_p1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_paste_flyer_p2.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_paste_wanted_p1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_paste_wanted_p2.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_sigilframe_dripframe.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_sigilframe_halo.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_sigilframe_stencilbox.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_stencil_crown.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_stencil_fist.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_stencil_gear.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_tag_a_p1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_tag_a_p2.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_tag_b_p1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_tag_b_p2.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_tag_c_p1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_tag_c_p2.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_throwup_a_p1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_throwup_a_p2.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_throwup_b_p1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/graffiti_throwup_b_p2.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/nightside_mahllik_east.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/nightside_mahllik_north.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/nightside_mahllik_south.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/nightside_zhissa_east.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/nightside_zhissa_north.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/nightside_zhissa_south.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_brakkel_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_brunnock_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_cundral_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_gorbeleth_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_kaddrath_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_maddrick_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_mirrelbole_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_mourvel_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_phorrik_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_phorrik_v1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_quathis_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_quathis_v1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_sarnstilt_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_sarnstilt_v1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_sarquin_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_sarquin_v1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_thalquith_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_thalquith_v1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_tumbel_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_tumbel_v1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_vurmeloth_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_vurmeloth_v1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_wollick_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_wollick_v1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_zhorrel_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rm_zhorrel_v1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rmleachmoss_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rmleachmoss_v1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rmtitanoslime_v1_east.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rmtitanoslime_v1_east.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rmtitanoslime_v1_north.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rmtitanoslime_v1_north.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rmtitanoslime_v1_south.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rmtitanoslime_v1_south.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rmvenomvine_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rmvenomvine_v1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_brogg_east.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_brogg_north.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_brogg_south.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_brullith_east.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_brullith_north.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_brullith_south.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_illoth_east.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_illoth_north.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_illoth_south.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_skerrith_east.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_skerrith_north.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_skerrith_south.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_thozzik_east.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_thozzik_north.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_thozzik_south.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_thozzikqueen_east.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_thozzikqueen_north.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rot_thozzikqueen_south.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rsw_graffiti_stencil_imperialcog.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rsw_zakkro_dessicated_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rsw_zakkro_dessicated_v1.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rsw_zakkro_v1_east.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rsw_zakkro_v1_east.manifest.1790311645.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rsw_zakkro_v1_north.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rsw_zakkro_v1_north.manifest.1790311646.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rsw_zakkro_v1_south.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rsw_zakkro_v1_south.manifest.1790311646.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rsw_zakkroegg_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rsw_zakkroegg_v1.manifest.1790311646.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rswrawultracactus_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rswrawultracactus_v1.manifest.1790311646.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rswultracactus_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rswultracactus_v1.manifest.1790311646.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rut_grellbush.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rut_grellbush.manifest.1790311646.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rut_grellspine.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rut_grellspine.manifest.1790311646.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rut_wildhealroot.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rutfuzz_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rutstaggerseed_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_quota_failures/rutstaggerseeddish_v1.manifest.1790254961.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/artpipe_sizemismatch_control_manifests/     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/baroque_biomes_toggle_verify_poll.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/baroque_biomes_toggle_verify_start_quicktest.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/bedazzle_gpt_enrich_2026-09-30/bluedesert.raw.txt     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/bedazzle_gpt_enrich_2026-09-30/cauldron.raw.txt     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/bedazzle_gpt_enrich_2026-09-30/contagion.raw.txt     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/bedazzle_gpt_enrich_2026-09-30/crackedlands.raw.txt     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/bedazzle_gpt_enrich_2026-09-30/forge.raw.txt     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/bedazzle_gpt_enrich_2026-09-30/leaningscrub.raw.txt     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/bedazzle_gpt_enrich_2026-09-30/longshade.raw.txt     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/bedazzle_gpt_enrich_2026-09-30/wasteland.raw.txt     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/biome_load_proof/     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/biome_round_sentinels.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/bmt_verify/     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/cellcheck.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/coldload_wait_2026-09-23.sh     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/configerror_dump.txt     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/cryptoforge_retire_load_check.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/deepfire_new4_contact.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/deepfire_pigment_review_assets/deepfire_crowncarpet_a.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/deepfire_pigment_review_assets/deepfire_crowncarpet_b.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/deepfire_pigment_review_assets/deepfire_pigmentjar_a.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/deepfire_pigment_review_assets/deepfire_pigmentjar_b.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/deepfire_sheet_serve.log     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/desert_fillout_art_review/img/     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/desk_after_click_check.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/desk_check_20260926.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/directional_probe.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/eg_check_state.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/eg_soak_test_plants.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/eg_spawn_test_plants.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/eg_step_and_report.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/events_resolved_2026-09-23.jsonl     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/game_state_check.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/game_state_check.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/game_state_check2.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/game_state_check2_crop.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/game_state_check2_dialog.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/game_state_check3.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/game_state_check3_crop.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/jawa_swim_ocean_20260926.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/jawa_swim_selected_20260926.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/jawa_swim_shallow_20260926a.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/jawa_swimjob_20260926.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/jawa_swimjob_close_20260926.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/jawa_swimpose_final_20260926.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/logs_2026-09-24/     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/menu1.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/menu1.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/menu2.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/menu2.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/menu3.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/menu3.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/menu4.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/menu4.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/menu5.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/menu5.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/menu6.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/menu6.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/menu7.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/menu7.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/nightside_ice_research_rimworld_prior_art.md     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/nightside_ice_research_starwars_canon.md     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/pawn_survey.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/pigment_research/     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/poll_bridge_ready.sh     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/poll_game_loaded.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/quicktest_bluedesert_cold_2026-09-30.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/quicktest_timelapse_RM_BlueDesert_2026-09-30.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/quicktest_timelapse_RM_Cauldron_2026-09-30.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/quicktest_timelapse_RM_LeaningScrub_2026-09-30.json     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/rw_state1.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/rw_state1_small.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/rw_state2.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/rw_state2_small.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/rw_state3.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/rw_state3_small.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/rw_win_capture.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald1.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald1.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald2.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald2.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald3.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald3.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald5.bmp     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald5.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald_floor/     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald_renders_20260925.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald_showcase2_clear.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald_showcase2_close.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald_showcase2_steam.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald_showcase3_cast.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald_showcase3_clear.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald_showcase3_closeL.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald_showcase3_closeR.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald_showcase3_steam.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald_showcase_clear.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/scald_showcase_steam.png     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/swimcheck.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/swimcheck2.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/week_summary_art.md     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/week_summary_challenges.md     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/week_summary_design.md     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/week_summary_mechanics.md     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/world_label_sizes/CANONICAL_ASHKARR_START_2026-09-12.biome.equirect.svg     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? Transient/zoomprobe.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-THEY_MOD_REPLICATION_1-retirement-write.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-baroque_wave0.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-baroque_wave0_control.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-firehawk.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-greentideant.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-leaningscrub.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-luminouspigment.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_bluedesert.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_contagion.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_feverwood.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_floodedcanyon.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_forsakencrags.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_gelatinousslime.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_greentide.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_leaningscrub.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_longshade.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_miasma.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_nightsideice.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_poisonforest.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_pyrelands.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_rustcathedral.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_stillsand.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_terminalbiomes.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_theforge.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_therot.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_thesump.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_wasteland.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_webwork.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-proof_weepingstones.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? deployed/config/ModsConfig.before-tier-weepingstones.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_east.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_north.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_south.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Gennok_east.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Gennok_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Gennok_north.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Gennok_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Gennok_south.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Gennok_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_east.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_north.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_south.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_east.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_north.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_south.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Sollak_east.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Sollak_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Sollak_north.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Sollak_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Sollak_south.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Sollak_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_east.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_north.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_south.json     # artpipe daemon
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Bleedleaf.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Bleedleaf.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Blisterfloat_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Blisterfloat_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Blisterfloat_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Blisterfloat_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Blisterfloat_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Blisterfloat_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Bloodlurk_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Bloodlurk_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Bloodlurk_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Bloodlurk_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Bloodlurk_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Bloodlurk_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BloodyFist.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BloodyFist.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BloodyMess_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BloodyMess_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BloodyMess_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BloodyMess_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BloodyMess_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BloodyMess_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BloodyMess_v2_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BloodyMess_v2_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BloodyMess_v2_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BloodyMess_v2_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BloodyMess_v2_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BloodyMess_v2_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BlueIce.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BlueIce.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Boilbulb.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Boilbulb.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Boilhide_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Boilhide_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Boilhide_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Boilhide_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Boilhide_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Boilhide_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Boilhide_v2_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Boilhide_v2_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Boilhide_v2_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Boilhide_v2_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Boilhide_v2_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Boilhide_v2_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BrinePlate.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_BrinePlate.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CaskBay.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CaskBay.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CauldronVent.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CauldronVent.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Cinderfelt.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Cinderfelt.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CloudRepulsor.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CloudRepulsor.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CloudRepulsor_v2.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CloudRepulsor_v2.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_ContaminantBezoar.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_ContaminantBezoar.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CorrodedCondenserStack.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CorrodedCondenserStack.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CorrodedShrine.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CorrodedShrine.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CorrodedWellhead.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CorrodedWellhead.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CrackWaxSuit.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CrackWaxSuit.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Crispling_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Crispling_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Crispling_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Crispling_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Crispling_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Crispling_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CrownVenomvine.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_CrownVenomvine.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Cruststar.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Cruststar.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Crustweevil_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Crustweevil_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Crustweevil_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Crustweevil_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Crustweevil_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Crustweevil_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dakkra_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dakkra_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dakkra_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dakkra_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dakkra_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dakkra_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Danglemaw_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Danglemaw_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Danglemaw_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Danglemaw_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Danglemaw_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Danglemaw_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dewfringe.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dewfringe.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_DewfringeSprig.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_DewfringeSprig.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_DhokkurDormant.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_DhokkurDormant.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dhokkur_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dhokkur_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dhokkur_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dhokkur_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dhokkur_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dhokkur_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_DhuvvoxNodule.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_DhuvvoxNodule.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dhuvvox_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dhuvvox_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dhuvvox_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dhuvvox_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dhuvvox_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dhuvvox_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Doublemaw_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Doublemaw_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Doublemaw_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Doublemaw_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Doublemaw_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Doublemaw_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Drazz.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Drazz.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_DrippingVenomvine.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_DrippingVenomvine.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dustflutter_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dustflutter_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dustflutter_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dustflutter_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dustflutter_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Dustflutter_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Duumma_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Duumma_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Duumma_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Duumma_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Duumma_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Duumma_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eskith_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eskith_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eskith_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eskith_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eskith_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eskith_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eskith_v2_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eskith_v2_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eskith_v2_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eskith_v2_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eskith_v2_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eskith_v2_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eyebark.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eyebark.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eyebark_v2.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eyebark_v2.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eyestinger_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eyestinger_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eyestinger_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eyestinger_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eyestinger_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Eyestinger_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FilterCartridge.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FilterCartridge.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FilterWorks.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FilterWorks.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Filth_DisturbedSand.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Filth_DisturbedSand.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Filth_DragMark.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Filth_DragMark.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fleshsop_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fleshsop_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fleshsop_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fleshsop_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fleshsop_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fleshsop_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fleshsop_v2_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fleshsop_v2_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fleshsop_v2_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fleshsop_v2_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fleshsop_v2_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fleshsop_v2_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Floatstone.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Floatstone.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FloatstoneGarden.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FloatstoneGarden.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FossilDeepStratum.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FossilDeepStratum.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FossilDisplayMount.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FossilDisplayMount.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FossilDisplaySlab.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FossilDisplaySlab.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FossilImpression.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FossilImpression.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FossilSeam.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FossilSeam.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FossilSkeleton.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FossilSkeleton.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FossilSkeleton_v2.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_FossilSkeleton_v2.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fuzzrunner_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fuzzrunner_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fuzzrunner_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fuzzrunner_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fuzzrunner_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fuzzrunner_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fuzzviper_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fuzzviper_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fuzzviper_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fuzzviper_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fuzzviper_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Fuzzviper_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gaanok_b_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gaanok_b_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gaanok_b_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gaanok_b_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gaanok_b_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gaanok_b_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gaanok_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gaanok_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gaanok_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gaanok_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gaanok_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gaanok_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_GasTapScaffold.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_GasTapScaffold.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gawpsack_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gawpsack_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gawpsack_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gawpsack_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gawpsack_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gawpsack_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gennok_b_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gennok_b_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gennok_b_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gennok_b_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gennok_b_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gennok_b_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gennok_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gennok_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gennok_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gennok_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gennok_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gennok_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Glasscrust.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Glasscrust.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gloomcast_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gloomcast_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gloomcast_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gloomcast_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gloomcast_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gloomcast_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gnashling_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gnashling_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gnashling_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gnashling_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gnashling_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gnashling_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gorekite_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gorekite_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gorekite_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gorekite_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gorekite_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gorekite_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gorestalk.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gorestalk.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gravelgut_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gravelgut_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gravelgut_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gravelgut_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gravelgut_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gravelgut_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_GreatDevourer_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_GreatDevourer_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_GreatDevourer_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_GreatDevourer_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_GreatDevourer_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_GreatDevourer_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Grimewing_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Grimewing_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Grimewing_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Grimewing_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Grimewing_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Grimewing_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Grimewing_v2_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Grimewing_v2_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Grimewing_v2_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Grimewing_v2_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Grimewing_v2_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Grimewing_v2_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gristleswarm_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gristleswarm_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gristleswarm_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gristleswarm_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gristleswarm_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gristleswarm_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gristleswarm_v2_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gristleswarm_v2_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gristleswarm_v2_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gristleswarm_v2_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gristleswarm_v2_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Gristleswarm_v2_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Groundrunner_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Groundrunner_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Groundrunner_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Groundrunner_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Groundrunner_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Groundrunner_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_HalfExtractedCore.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_HalfExtractedCore.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_HalfmadeTree.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_HalfmadeTree.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_HalfmadeTreeBlighted.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_HalfmadeTreeBlighted.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_HollowVenomvine.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_HollowVenomvine.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Hourbloom.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Hourbloom.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ikee_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ikee_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ikee_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ikee_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ikee_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ikee_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Irqit_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Irqit_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Irqit_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Irqit_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Irqit_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Irqit_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Jossur_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Jossur_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Jossur_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Jossur_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Jossur_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Jossur_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Julmox_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Julmox_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Julmox_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Julmox_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Julmox_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Julmox_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_KneelOllim.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_KneelOllim.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_KneelOllim_b.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_KneelOllim_b.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Krannock_v1_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Krannock_v1_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Krannock_v1_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Krannock_v1_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Krannock_v1_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Krannock_v1_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Lashgrass.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Lashgrass.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Liikka_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Liikka_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Liikka_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Liikka_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Liikka_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Liikka_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Loomma_b_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Loomma_b_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Loomma_b_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Loomma_b_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Loomma_b_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Loomma_b_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Loomma_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Loomma_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Loomma_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Loomma_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Loomma_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Loomma_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Maidenbloom.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Maidenbloom.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_MatureFleshbeast_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_MatureFleshbeast_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_MatureFleshbeast_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_MatureFleshbeast_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_MatureFleshbeast_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_MatureFleshbeast_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Meatvine.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Meatvine.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Meltgut_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Meltgut_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Meltgut_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Meltgut_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Meltgut_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Meltgut_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenbeetle_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenbeetle_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenbeetle_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenbeetle_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenbeetle_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenbeetle_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenshell_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenshell_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenshell_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenshell_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenshell_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenshell_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenshell_v2_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenshell_v2_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenshell_v2_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenshell_v2_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenshell_v2_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Middenshell_v2_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Mirrak_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Mirrak_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Mirrak_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Mirrak_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Mirrak_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Mirrak_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Murrek_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Murrek_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Murrek_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Murrek_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Murrek_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Murrek_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Muttavaq_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Muttavaq_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Muttavaq_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Muttavaq_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Muttavaq_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Muttavaq_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Muttavaq_v2_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Muttavaq_v2_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Oorrik_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Oorrik_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Oorrik_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Oorrik_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Oorrik_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Oorrik_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Orruhmu_b_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Orruhmu_b_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Orruhmu_b_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Orruhmu_b_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Orruhmu_b_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Orruhmu_b_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Orruhmu_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Orruhmu_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Orruhmu_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Orruhmu_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Orruhmu_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Orruhmu_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ossivel_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ossivel_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ossivel_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ossivel_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ossivel_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ossivel_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Parasol.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Parasol.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pavecrust.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pavecrust.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Peeper_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Peeper_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Peeper_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Peeper_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Peeper_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Peeper_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pillowmoss.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pillowmoss.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pirrik_b_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pirrik_b_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pirrik_b_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pirrik_b_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pirrik_b_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pirrik_b_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pirrik_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pirrik_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pirrik_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pirrik_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pirrik_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pirrik_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pusberry.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Pusberry.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Qorrax_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Qorrax_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Qorrax_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Qorrax_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Qorrax_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Qorrax_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Rattlegrope.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Rattlegrope.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_RawVenom.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_RawVenom.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ribbonwhip_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ribbonwhip_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ribbonwhip_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ribbonwhip_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ribbonwhip_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ribbonwhip_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Rollbug_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Rollbug_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Rollbug_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Rollbug_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Rollbug_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Rollbug_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ruukka_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ruukka_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ruukka_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ruukka_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ruukka_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Ruukka_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_SandBusterMound_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_SandBusterMound_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sapblister.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sapblister.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scabspinner_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scabspinner_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scabspinner_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scabspinner_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scabspinner_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scabspinner_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scaldhide_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scaldhide_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scaldhide_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scaldhide_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scaldhide_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scaldhide_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scorchpod_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scorchpod_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scorchpod_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scorchpod_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scorchpod_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scorchpod_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scumgrass.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scumgrass.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scumrat_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scumrat_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scumrat_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scumrat_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scumrat_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scumrat_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scumslider_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scumslider_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scumslider_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scumslider_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scumslider_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Scumslider_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Seismograph.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Seismograph.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Seismograph_v2.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Seismograph_v2.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_ShadeTent.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_ShadeTent.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shadespire.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shadespire.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shambles_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shambles_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shambles_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shambles_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shambles_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shambles_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shirrel_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shirrel_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shirrel_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shirrel_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shirrel_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shirrel_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shokka_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shokka_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shokka_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shokka_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shokka_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Shokka_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sippra_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sippra_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sippra_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sippra_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sippra_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sippra_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Skarrok_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Skarrok_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Skarrok_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Skarrok_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Skarrok_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Skarrok_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Skinflap_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Skinflap_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Skinflap_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Skinflap_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Skinflap_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Skinflap_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Slagmole_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Slagmole_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Slagmole_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Slagmole_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Slagmole_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Slagmole_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Slagmole_v2_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Slagmole_v2_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Slagmole_v2_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Slagmole_v2_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Slagmole_v2_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Slagmole_v2_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloghog_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloghog_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloghog_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloghog_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloghog_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloghog_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloghog_v2_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloghog_v2_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloghog_v2_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloghog_v2_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloghog_v2_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloghog_v2_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloshbelly_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloshbelly_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloshbelly_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloshbelly_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloshbelly_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sloshbelly_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Smolderback_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Smolderback_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Smolderback_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Smolderback_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Smolderback_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Smolderback_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sollak_b_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sollak_b_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sollak_b_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sollak_b_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sollak_b_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sollak_b_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sollak_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sollak_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sollak_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sollak_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sollak_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sollak_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Soorrak_b_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Soorrak_b_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Soorrak_b_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Soorrak_b_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Soorrak_b_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Soorrak_b_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Soorrak_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Soorrak_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Soorrak_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Soorrak_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Soorrak_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Soorrak_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_SootBrick.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_SootBrick.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_SootGristleswarm_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_SootGristleswarm_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_SootGristleswarm_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_SootGristleswarm_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_SootGristleswarm_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_SootGristleswarm_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sootgrazer_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sootgrazer_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sootgrazer_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sootgrazer_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sootgrazer_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sootgrazer_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_SparkleechGrub_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_SparkleechGrub_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_SparkleechGrub_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_SparkleechGrub_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_SparkleechGrub_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_SparkleechGrub_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sparkleech_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sparkleech_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sparkleech_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sparkleech_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sparkleech_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sparkleech_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sunbeam.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Sunbeam.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Surrik_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Surrik_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Surrik_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Surrik_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Surrik_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Surrik_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Swale.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Swale.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Swale_v2.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Swale_v2.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_TallScumgrass.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_TallScumgrass.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tanglefuzz.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tanglefuzz.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tarruq_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tarruq_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tarruq_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tarruq_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tarruq_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tarruq_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tazzok_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tazzok_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tazzok_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tazzok_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tazzok_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tazzok_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tebbra_b_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tebbra_b_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tebbra_b_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tebbra_b_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tebbra_b_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tebbra_b_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tebbra_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tebbra_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tebbra_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tebbra_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tebbra_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tebbra_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tekk.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tekk.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Thornhold_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Thornhold_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Thornhold_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Thornhold_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Thornhold_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Thornhold_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tikkit_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tikkit_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tikkit_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tikkit_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tikkit_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Tikkit_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Toothmoss.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Toothmoss.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_TruffleMole_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_TruffleMole_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_TruffleMole_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_TruffleMole_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_TruffleMole_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_TruffleMole_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_TwitcherVenomvine.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_TwitcherVenomvine.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_UltracactusPad.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_UltracactusPad.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Uttaqar_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Uttaqar_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Uttaqar_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Uttaqar_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Uttaqar_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Uttaqar_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Veessa_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Veessa_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Veessa_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Veessa_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Veessa_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Veessa_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_VenomvineThicket_v2.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_VenomvineThicket_v2.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Veqma.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Veqma.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vexxiss_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vexxiss_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vexxiss_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vexxiss_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vexxiss_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vexxiss_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vexxiss_v2_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vexxiss_v2_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vexxiss_v2_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vexxiss_v2_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vexxiss_v2_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vexxiss_v2_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vexxith.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vexxith.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vhaulk_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vhaulk_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vhaulk_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vhaulk_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vhaulk_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vhaulk_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vhaulk_v2_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vhaulk_v2_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Virr.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Virr.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_VisslerArm.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_VisslerArm.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vissler_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vissler_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vissler_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vissler_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vissler_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vissler_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_VitrifiedBezoar.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_VitrifiedBezoar.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vrekka_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vrekka_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vrekka_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vrekka_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vrekka_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Vrekka_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Warcasket.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Warcasket.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_WarcasketJunker.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_WarcasketJunker.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Wartshrub.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Wartshrub.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Whipfuzz.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Whipfuzz.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Wombpod.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Wombpod.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_WreckedCart.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_WreckedCart.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Xithess.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Xithess.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Zellik_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Zellik_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Zellik_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Zellik_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Zellik_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Zellik_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Zisska_east.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Zisska_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Zisska_north.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Zisska_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Zisska_south.json     # artpipe daemon
?? infrastructure/artpipe/done/RM_Zisska_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RSW_CrawlerTreadWreck.json     # artpipe daemon
?? infrastructure/artpipe/done/RSW_CrawlerTreadWreck.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RSW_WreckedSkiff.json     # artpipe daemon
?? infrastructure/artpipe/done/RSW_WreckedSkiff.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_AncientAirlock.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_AncientAirlock.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_AncientAirlock_Large.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_AncientAirlock_Large.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_AncientFloorHeater.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_AncientFloorHeater.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_AncientLandmine.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_AncientLandmine.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_AncientShieldedTurret.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_AncientShieldedTurret.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_AncientShipLandingBeacon.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_AncientShipLandingBeacon.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_AncientSpacerAutocannon.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_AncientSpacerAutocannon.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_AncientTransmitterBeacon.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_AncientTransmitterBeacon.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_BustedShieldedTurret.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_BustedShieldedTurret.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_BustedSpacerAutocannon.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_BustedSpacerAutocannon.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_CrackWax.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_CrackWax.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_ForcedAncientAirlock.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_ForcedAncientAirlock.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_ForcedAncientAirlock_Large.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_ForcedAncientAirlock_Large.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_FoundrySalvageCache.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_FoundrySalvageCache.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_FoundryTowerEntrance.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_FoundryTowerEntrance.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_FrozenEmptyCryptosleepPod.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_FrozenEmptyCryptosleepPod.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_JammedAncientAirlock.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_JammedAncientAirlock.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_JammedAncientAirlock_Large.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_JammedAncientAirlock_Large.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_TibannaGas.json     # artpipe daemon
?? infrastructure/artpipe/done/RUT_TibannaGas.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_eldspar.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_eldspar.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_fuselight.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_fuselight.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_ghostpane.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_ghostpane.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_keelgrass.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_keelgrass.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_pitchpearl.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_pitchpearl.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_skyharp.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_skyharp.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_slackwax.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_slackwax.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_stillbloom.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_stillbloom.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_stonewater.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_stonewater.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_tarspool.json     # artpipe daemon
?? infrastructure/artpipe/done/chill_plant_tarspool.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/coalescence_stage1.json     # artpipe daemon
?? infrastructure/artpipe/done/coalescence_stage1.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/coalescence_stage2.json     # artpipe daemon
?? infrastructure/artpipe/done/coalescence_stage2.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/coalescence_stage2_v2.json     # artpipe daemon
?? infrastructure/artpipe/done/coalescence_stage2_v2.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/coalescence_stage3.json     # artpipe daemon
?? infrastructure/artpipe/done/coalescence_stage3.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/coalescence_stage3_v2.json     # artpipe daemon
?? infrastructure/artpipe/done/coalescence_stage3_v2.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rm_chillauroracollector_v1.json     # artpipe daemon
?? infrastructure/artpipe/done/rm_chillauroracollector_v1.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rmshademite_v2_east.json     # artpipe daemon
?? infrastructure/artpipe/done/rmshademite_v2_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rmshademite_v2_north.json     # artpipe daemon
?? infrastructure/artpipe/done/rmshademite_v2_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rmshademite_v2_south.json     # artpipe daemon
?? infrastructure/artpipe/done/rmshademite_v2_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_blurrg_v1_east.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_blurrg_v1_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_blurrg_v1_north.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_blurrg_v1_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_blurrg_v1_south.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_blurrg_v1_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_blurrg_v2_east.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_blurrg_v2_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_blurrg_v2_north.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_blurrg_v2_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_blurrg_v2_south.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_blurrg_v2_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_scrapnestbird_v1_east.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_scrapnestbird_v1_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_scrapnestbird_v1_north.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_scrapnestbird_v1_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_scrapnestbird_v1_south.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_scrapnestbird_v1_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_shrublandgiant_v1_east.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_shrublandgiant_v1_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_shrublandgiant_v1_north.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_shrublandgiant_v1_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_shrublandgiant_v1_south.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_shrublandgiant_v1_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_tunnelsnake_v1_east.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_tunnelsnake_v1_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_tunnelsnake_v1_north.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_tunnelsnake_v1_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_tunnelsnake_v1_south.json     # artpipe daemon
?? infrastructure/artpipe/done/rsw_tunnelsnake_v1_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rut_greentideant_carapacewall_atlas.json     # artpipe daemon
?? infrastructure/artpipe/done/rut_greentideant_carapacewall_atlas.manifest.json     # artpipe daemon
?? infrastructure/artpipe/done/rut_greentideant_carapacewall_menuicon.json     # artpipe daemon
?? infrastructure/artpipe/done/rut_greentideant_carapacewall_menuicon.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RM_ParasolWorn_east.json     # artpipe daemon
?? infrastructure/artpipe/failed/RM_ParasolWorn_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RM_ParasolWorn_north.json     # artpipe daemon
?? infrastructure/artpipe/failed/RM_ParasolWorn_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RM_ParasolWorn_south.json     # artpipe daemon
?? infrastructure/artpipe/failed/RM_ParasolWorn_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RM_SunShield_east.json     # artpipe daemon
?? infrastructure/artpipe/failed/RM_SunShield_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RM_SunShield_north.json     # artpipe daemon
?? infrastructure/artpipe/failed/RM_SunShield_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RM_SunShield_south.json     # artpipe daemon
?? infrastructure/artpipe/failed/RM_SunShield_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_Off_east.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_Off_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_Off_north.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_Off_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_Off_south.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_Off_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_east.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_north.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_south.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientWargamingTable_east.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientWargamingTable_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientWargamingTable_north.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientWargamingTable_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientWargamingTable_south.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_AncientWargamingTable_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_BlueprintsBench_east.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_BlueprintsBench_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_BlueprintsBench_north.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_BlueprintsBench_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_BlueprintsBench_south.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_BlueprintsBench_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminalBank_east.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminalBank_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminalBank_north.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminalBank_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminalBank_south.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminalBank_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminal_east.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminal_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminal_north.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminal_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminal_south.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminal_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_RuinedHospitalBed_east.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_RuinedHospitalBed_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_RuinedHospitalBed_north.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_RuinedHospitalBed_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_RuinedHospitalBed_south.json     # artpipe daemon
?? infrastructure/artpipe/failed/RUT_RuinedHospitalBed_south.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/rmshademite_v1_east.json     # artpipe daemon
?? infrastructure/artpipe/failed/rmshademite_v1_east.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/rmshademite_v1_north.json     # artpipe daemon
?? infrastructure/artpipe/failed/rmshademite_v1_north.manifest.json     # artpipe daemon
?? infrastructure/artpipe/failed/rmshademite_v1_south.json     # artpipe daemon
?? infrastructure/artpipe/failed/rmshademite_v1_south.manifest.json     # artpipe daemon
?? infrastructure/dashboards/hub/tabs/maturity.html     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? infrastructure/dashboards/hub/utinni_control_room_standalone.html     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? infrastructure/state/logs/harvested/     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? infrastructure/state/modlists/ModsConfig.FULL.PRECAPTURE.20260926_142047.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_restoring_seashores_bacta_2026-09-25T175356.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_seashores_enable_2026-09-25T133443.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? infrastructure/state/modlists/ModsConfig_before_miasma_predation_proof_2026-09-27.xml     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? infrastructure/state/rescued/LanternDeeps_RUT/Assemblies/     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
?? src/RimMandrake/Utils/firehawk_flight_probe.py     # not FOUNDRY - a peer window (BENCH) or the daemon; FOUNDRY did not touch it
```

