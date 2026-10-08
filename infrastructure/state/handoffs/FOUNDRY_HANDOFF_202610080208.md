# FOUNDRY_HANDOFF_202610080208 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610070549`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Every kernel/fuzz/lint/DLL pushed today is **unrun in game**: 40-odd mods now have pure kernels the mod calls, seeded fuzz with mutation checks, and a def lint, but the first live load after today will decide whether the extractions were truly behaviour-preserving. Pushed on origin/main (df37296d5), local main realigned to it; backup branch `backup/foundry-pre-realign-20261007` holds the old local history. FIRST live move: restart on a list that loads the biomes mod (`deploy_custom_mods.py --compose biomes --apply` is a SEPARATE step from plain `--apply`), then `rimflow next --acceptance --seat FOUNDRY` and run the L1 then L2 reads (details: Transient/green_min_runs2_20261007.md, live_recheck2_20261007.md).

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Pit sink clamp is now OFF by default** (`pitSinkClampEnabled`, FlowWorks) on your word "try it without the clamp, if not fixed let's reassess". Unverified live: load the muffalo repro save `RM_pitlip_muffalo_bug_20261006`; the rectangle should not return, and a hare at D=4 should read 1.2 mid-pit.
- **WeepingStones pool drying now follows `dryDays`** (about 12x slower than before; new Scribed `dryStartCount`, -1 on old saves): your card confirmed it.
- **MovingDunes: you chose "water banks the sand"; NOT IMPLEMENTED** (no new agents after "dont start new"). Mass check has a hole until it is.
- **ShipVermin** now ships 4 invented beasts (RM_Skivvik/Rattagh/Gorrud/Fethrik) on placeholder textures, art owed; canon swaps in via a SWBestiary patch. Needs your look (A4).
- **Direction-rule note:** UtinniPatches now hard-depends on mandrake.rm.biomes (your card).
- Defects fixed by builders worth a skim: Scarlands every-patch-applied-twice (glower damage was x0.25 not x0.5), DivingInteraction lost unique treasure + silver overflow, LanternDeeps sipper ratchet, KeelHoist desync tick throw, RimProperty fee paid at menu-build not click.
- Design observations left for you: Abyss exchange pays 99% at value 50 but 37% at 5000; Droidworks trade slider can profit at max; Warcasket Junker suit craftable/crackable; Webwork deconstructing six urraveth pieces opens the skull unread; Pyrelands diagonal fire fronts now ~1.8x wider (revert-able on its own).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `MOVINGDUNES_WATER_BANKS_SAND_1` (no item filed) — owner chose banking on non-holding cells; NEXT: file the item and make RM_DuneKernel bank sand that lands on water in a ledger, extend the fuzz mass-conservation invariant, rebuild and push.
- `FLOWWORKS_PIT_CLAMP_LIVE_1` — clamp default off, built and pushed, not seen live; NEXT: restart on the flowworks tier and run `validation_v2.py --live --fresh-map` (expect 59/0/0 except X-rows already fixed by ladder harness), then the muffalo repro save.
- `ACCEPTANCE_SITTING_RESUME` — about 175 built items still owe L1/L2/GREEN-MIN live checks; BENCH held the bridge idle for 139 min at last look; NEXT: `rimflow bridge who`, take it if stale, restart on `acc_harness`, rerun `modcheck run` for the five fixed mods (Droidworks, WreckedMachines, LuminousPigment, FallLineArrivals, UnfinishedLine).
- `UNPROVEN_LIVE_LEGS_TRIAGE_1` and eight other items filed today (Stillsand Muurrok/roof cover, forced pit-fall row, Titanic test race, Warcasket About URLs, Gizka unmeasured rows, acceptance mapping, bridge kill-hostiles tool) — all state proposed; NEXT: `rimflow next --seat FOUNDRY`.
- `ACCEPTANCE_MAP_TABLES` — 8 mods seeded (8 mapped rows, 16 unmapped); NEXT: extend tables as criteria come up (`acceptance_map.py check`, `apply --record`).
- `SHIPVERMIN_FREE_TIER_BEASTS_1` — built; NEXT: L1 load on the free-tier list then L2 with swbestiary, then owner look.
- `STARWARSRACES_ARMOURY_DEP` — MayRequire-guarded; NEXT: none unless a load shows the ionization hediff missing.
- `DEAD_OR_INERT_SETTINGS` — lints found unwired settings (Scarlands crossBiome*, biomeRarityFactor; TerminalBiomes 7; Wasteland brineDepositsEnabled; EmpirePursuit ionVolleyIntervalHours has no UI); NEXT: decide wire or delete per mod.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- Plain `deploy_custom_mods.py --apply` skips the composed mandrake.rm.biomes mod; a restart on stale files reads as 'the fix did nothing' (filed: LESSONS 20261007T220228Z-FOUNDRY-deploy-skips-composed-biomes)
- `PatchOperationAdd` of a whole `<modExtensions>` clobbers an earlier mod's extension (Desert dune binding lost) (filed: LESSONS patchadd-modextensions-clobbers)
- zsh does not word-split an unquoted variable: my `$P` path list built one path and the commit refused; use arrays (filed: memory zsh-does-not-word-split-unquoted-vars)
- A plumbing-built push (diff from the WRONG parent) once pushed an EMPTY commit with a misleading message because `git apply` failed inside `| tail`; always assert the patch applied and the tree differs (d8bf749e8 empty, 44de46280 real) (filed: LESSONS 20261008T020951Z-FOUNDRY-plumbing-built-push-patch-diffed-from)
- Kernel extraction moves text that older checks pin: run `run_selftests.py` after every extraction (TheForge validation parsed zero phases) (filed: lesson stamp/regression notes in Transient/selftest_regressions_20261007.md)
- dll_source_stamp.py did not understand `../Kernel/X.cs` includes in default-glob projects; fixed in df37296d5 (see: Utils/dll_source_stamp.py)
- A helper's dry-run default (`jawa/fire_incident` dryRun=true) and `CompTargetable` needing OrderForceTarget made two mod chains look broken (filed: LESSONS comptargetable-force-target-dryrun)
- Another window took the bridge after 45 idle minutes and relaunched the game on the full list under a helper's live session (filed: LESSONS bridge-hold-stale-45min)

## Commits

```
df37296d5 Oracle, Pyrelands(+Mechanics), RimProperty, SolarMirrors, Stillsand, Warcasket, Webwork, Armoury, SWBestiary, JawaRules, JawaIonWeapons: pure kernels with seeded fuzz, mutation sets and def lints; lint-only Graffiti family; defects fixed per reports; DLLs rebuilt with clean stamps; dll_source_stamp now understands ../ includes; rimflow ledgers. Unrun in game.
2c5e2f4c4 Wreck, FlowWorks, SlimeGrass/Thumbstalk, Duumma textures referenced by defs; grey_floor live run JSONs
8b1f1aa42 BENCH handoff 2026-10-07: Huge Things save ready, tooke-trap requeued, do not fetch from capped seat
3f5701d45 LeaningScrub, Greentide, MovingDunes, BlueDesert, FloodedCanyon: pure kernels with seeded fuzz, mutation sets and def lints; text-scan checks repointed; defects fixed per reports; DLLs rebuilt with clean stamps; unrun in game
d670d2c72 LuminousPigment, GelatinousSlime, TerminalBiomes: pure kernels with seeded fuzz, mutation sets and def lints; shared lint/mutation tool fixes; defects fixed per reports; DLLs rebuilt with clean stamps; unrun in game
05294a0b6 Huge Things Rot walk save: grid key
546c0f7cc Selftest regressions from today's kernel extractions fixed: FeverWood broodcampaign, TheForge validation phase parse, modcheck suite_corrections Droidworks mock
d01f9729a ExplosiveGrowth, EmpirePursuit, KeelHoist, TheSump: pure kernels with seeded fuzz, mutation runners and def lints; defects fixed per reports; DLLs rebuilt with clean stamps; unrun in game
210639c82 Droidworks, Abyss, Miasma, TheRot: pure kernels with seeded fuzz and def lints; defects fixed per reports; DLLs rebuilt with clean stamps; unrun in game
a33f7ffaf ShipVermin free-tier beasts (SHIPVERMIN_FREE_TIER_BEASTS_1), no swbestiary dependency; canon creatures patched into the same nest slots from SWBestiary; FlowWorks northstar baseline and selftest count for the new pitSinkClampEnabled setting; unloaded in game
69378ce3b acceptance_map: one table per mod mapping validation components to acceptance criteria (owner card 2026-10-07), tool records only clean PASSes, 8 mods seeded, selftest
44de46280 Six biome mods (Wasteland, WeepingStones, Contagion, FeverWood, TheForge, Cauldron) get pure kernels with seeded fuzz and def lints, defects fixed per the reports, DLLs rebuilt with clean stamps; StarWarsRaces ionization entry MayRequire-guarded. This is the content the previous commit d8bf749e8 claimed and did not contain (empty by accident). Unrun in game.
d8bf749e8 Six biome mods get pure kernels with seeded fuzz and def lints; defects fixed (see per-mod reports); StarWarsRaces ionization entry MayRequire-guarded; ShipVermin free-tier item filed; DLLs rebuilt with clean stamps; unrun in game
6487451e0 Agent_Policy: 2026-10-07 gateway re-measure (Opus 5.5 added, haiku -> Sonnet 4.5)
29a2336f1 Inhabited and LanternDeeps kernels with seeded fuzz and lints; four LanternDeeps/Inhabited defects fixed; DLLs rebuilt with clean stamps; unrun in game
faecd78c8 Dependency lint classifies guarded/intra-composition refs (172 warnings to 1 real); UtinniPatches hard-depends on mandrake.rm.biomes; reported not fixed: ShipVermin (RM) depends on swbestiary (RSW), StarWarsRaces uses an armoury type unguarded
c40901029 EnvironmentalHazards and Scarlands kernels with seeded fuzz; def-type-ref lint; DLLs rebuilt with clean stamps; unrun in game
6bbaca7d5 CreatureBehaviors: moving-shade layer and sand-swim kernels with seeded fuzz, def-vs-source lint; DLL rebuilt with clean stamp; unrun in game
a0b5f4616 DivingInteraction: garden-defense and elder-economy kernels with seeded fuzz and lint; fixes unique treasure claimed before its def resolved and float-to-int overflow in payout; DLL rebuilt with clean stamp; unrun in game
2ba4a08d4 Webwork sheet: redo renders (Dulloth, Vennick, Kollavane x3, Norrveth x2) beside current art, not installed
... 238 more: git log --oneline e5bdb4b99..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
?? Transient/ModsConfig_before_bridge4.xml   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/ModsConfig_before_d.xml   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/ModsConfig_before_foundry_green_20261007.xml   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/ModsConfig_before_foundry_l2_20261007.xml   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/ModsConfig_before_fwfinal.xml   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/ModsConfig_before_fwmap.xml   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/Player_load13_20261004.log   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/acceptance_map_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/aerosol_build_wave_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/aerosol_rings_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/aerosol_salvage_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/aerosol_wave2_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/aerosol_wave3_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/belt_bridge4_deploy_plan.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_bridge4_progress.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_bridge_log_20261004d.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_deep_proto.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_deploy_d_biomes.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_deploy_d_plain.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_deploy_done   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_deploy_plan_d.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_deploy_prune.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_deploy_prune_c.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_deploy_r5_biomes.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_deploy_r5_plain.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_deploy_r5_plain2.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_deploy_r5_plain3.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_deploy_r6_biomes.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_deploy_r6_done   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_deploy_r6_plain.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_first_errors_d.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_flowworksNS_preflight2_20261005.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_flowworksNS_prep2_20261005.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_burn.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_ext.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_foam.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_fx.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_fwfinal_probe_p3.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_fwfinal_v2live_20261005.txt   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/belt_fwkits_20261005.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_fwliquids_20261005.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_fwlogistics_20261005.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_fwsheet_20261005.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_gitprobe.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_harvest10_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_harvest11_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_harvest3_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_harvest5_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_harvest6_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_harvest7_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_harvest8_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_harvest9_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_probe.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_probe2.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_probe_kits.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_probe_pawns.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_probe_rr.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_probe_ruins.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_probe_size.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_rerun19a_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_rerun19b_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_rerun20a_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_rerun20b_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_rerun20c_20261003.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_rerun_TheSump_20261004i.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_rerun_TheSump_20261004j.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_rerun_b1_20261004k.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_rerun_b2_20261004l.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_rerun_b3_20261004m.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_rerun_kits_Forge_20261006.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_rerun_kits_batch1_20261006.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_rerun_kits_batch2_20261006.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_reviewFW4_20261005.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_setbg.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/belt_sum.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/biome_ffar/abyss_v4_requeue_jobs_2026-10-06.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_Player.log   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_accept.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_c1.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_c4.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_c5.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_calls2.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_calls3.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_harvest.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_in1.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_map.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_modscfg.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_o1.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_o4.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_o5.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_out1.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_out2.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_out3.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_schemas.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/bs_sum.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/config_error_fixes_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/desk_muffalo.bmp   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/desk_muffalo.png   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/desk_muffalo_crop.png   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/droidworks_triage_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/fallline_gate_proof_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/flowworks_playtest/fwpt_20261007T122418_s1.jsonl   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/flowworks_regression_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/flowworks_repro_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/flowworks_v2_harness_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/foundry_doing_offline_20261006.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/foundry_doing_slice_00   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/foundry_doing_slice_01   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/foundry_doing_slice_02   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/foundry_doing_slice_03   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/foundry_fw_reviewmap_20261006.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/foundry_fw_v2_20261006.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/foundry_green_ph_20261007.txt   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/foundry_gss_proof_20261006.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/foundry_kits_rerun_20261006.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/foundry_modcheck_CreatureBehaviors_20261007.txt   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/foundry_modcheck_L2_run1_20261007.txt   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/foundry_modcheck_L2_run2_20261007.txt   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/foundry_modcheck_L2_run4_20261007.txt   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/foundry_modcheck_L2_run5_20261007.txt   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/foundry_modcheck_NightsideIce_20261007.txt   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/foundry_modcheck_NightsideIce_20261007b.txt   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/foundry_modcheck_NightsideIce_20261007c.txt   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/foundry_record_builds_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/fuzz_validation_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/fw_ovn_A.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_ALL.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_ALL2.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_B.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_EXT.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_RES.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_boot.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_boot2.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_boot3.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_boot4.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_chainsA.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_chainsA2.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_chainsB.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_cover.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_drysite.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_drysite2.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_ext1.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_ext2.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_ext3.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_ext4.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_ext5.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_ext6.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_iso1.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_iso2.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_iso3.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_iso4.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_iso5.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_plotA.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_plots.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_probe.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_probe2.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_probe3.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_riv1.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_riv2.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_riv3.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_riv4.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_rivercount.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_riversite.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_riversite2.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_riversite3.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_runA.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_runA.progress   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_runB.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_runB.progress   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_runC.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_runC.progress   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_settings.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_weir.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_ovn_works.out   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/fw_review_map_build_log.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/fwrepro_run1.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/fwrepro_run1.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/fwrepro_run2.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/fwrepro_wrap.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/fwvisuals_serve.log   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/glower_shielding_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/gpt_rimflow_review_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/green_min_flowworks_20261007.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/green_min_ishko2_20261007.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/green_min_ishko_20261007.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/green_min_runs2_20261007.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/green_min_runs2_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/green_min_runs2b_20261007.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/green_min_runs_20261007.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/green_min_runs_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/harness_fixes2_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/harness_fixes_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l1sweep_call.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l1sweep_calls.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l1sweep_calls_out.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l1sweep_get.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l1sweep_in.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l1sweep_out.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l1sweep_q.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l1sweep_qin.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l1sweep_qout.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l1sweep_toolnames.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l1sweep_tools.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l1sweep_tools2.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2.sh   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_Abyss.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_BlueDesert.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_Cauldron.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_Contagion.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_FeverWood.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_GelatinousSlime.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_GimmeSomeSlack.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_LeaningScrub.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_LuminousPigment.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_Miasma.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_MovingDunes.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_NightsideIce.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_Pyrelands.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_TerminalBiomes.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_TheForge.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_TheRot.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_Wasteland.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_Webwork.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_WeepingStones.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2_get.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p2sum.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p3.sh   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p3_json.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p3_probe.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p3_reset.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p3_start.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2p3_summ.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sum.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sum2.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_Abyss.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_Cauldron.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_DroidRepairJobs.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_Droidworks.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_Droidworks.prev.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_EggReckoning.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_FallLineArrivals.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_FloodedCanyon.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_Greentide.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_LanternDeeps.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_LuminousPigment.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_LuminousPigment.prev.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_Miasma.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_MovingDunes.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_NightsideIce.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_Pyrelands.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_RustCathedral.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_ShipShields.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_Stillsand.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_TerminalBiomes.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_TheForge.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_TheRot.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_TheSump.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_TitanicCreatures.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_TrophyCraft.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_UnfinishedLine.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_UnfinishedLine.prev.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_Webwork.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_WreckedMachines.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_WreckedMachines.prev.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_prev_20261007/   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_run.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/l2sweep_sum.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/lc/   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/list_tools.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/live_biomes_sweep_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/live_criteria_sweep_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/live_harness_rerun_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/live_l1_sweep_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/live_l2_biomes_part2_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/live_l2_biomes_part3_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/live_l2_sweep_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/live_recheck2_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/luminous_triage_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/mc_art_poles_20261004/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_densify_human_review_notes.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/mc_full_plan_run2_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_full_plan_run3_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_full_plan_run_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_live_run2_20261004.txt   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/mc_matrix_fast_20261004.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_matrix_fast_run_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_matrix_live_20261002/shots/   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/mc_matrix_live_20261002/shots_pass1/   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/mc_matrix_noshots2_run_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_matrix_noshots3_20261004.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_matrix_noshots3_run_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_matrix_noshots_run_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_matrix_rec2_20261004.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_matrix_rec3_20261004.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_matrix_rec4_20261004.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_matrix_rec_20261004.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_matrix_run_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_owner_shots_r4/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_owner_shots_r5/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_owner_shots_r6/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_owner_shots_r7/   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_probe_aerial_after_load.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_read_settings.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_relaunch2_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_relaunch_20261004.txt   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_scenes_20261004.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_time_calls.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/mc_time_calls2.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/messy_conduit_live_20261002/maze_01_open.png   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/messy_conduit_live_20261002/maze_02_gap_walled.png   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/messy_conduit_live_20261002/maze_04_unreachable.png   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/messy_conduit_live_20261002/ports_01_reel_tank.png   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261007T190620Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261007T190620Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261007T190743Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Abyss_20261007T190743Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/CreatureBehaviors_20261007T203753Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/CreatureBehaviors_20261007T203753Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/GelatinousSlime_20261007T193712Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/GelatinousSlime_20261007T193712Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/GizkaStowaway_20261007T191543Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/GizkaStowaway_20261007T191543Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/GravshipLanding_20261007T193717Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/GravshipLanding_20261007T193717Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261007T203123Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Greentide_20261007T203123Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/LeaningScrub_20261007T193012Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/LeaningScrub_20261007T193012Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261007T200805Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261007T200805Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261007T204156Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/LuminousPigment_20261007T204156Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261007T191720Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/OasisMaker_20261007T191720Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/PyrelandsMechanics_20261007T202903Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/PyrelandsMechanics_20261007T202903Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/PyrelandsMechanics_20261007T204247Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/PyrelandsMechanics_20261007T204247Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261007T193746Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Pyrinth_20261007T193746Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/RiverColors_20261007T191723Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/RiverColors_20261007T191723Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/ScarlandsLadder_20261007T191726Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/ScarlandsLadder_20261007T191726Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Scarlands_20261007T190646Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Scarlands_20261007T190646Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Scarlands_20261007T190810Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Scarlands_20261007T190810Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261007T190657Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261007T190657Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261007T190817Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/ShipVermin_20261007T190817Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/ShokkweaveEconomy_20261007T191730Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/ShokkweaveEconomy_20261007T191730Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261007T193741Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261007T193741Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261007T201757Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261007T201757Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261007T205531Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Stillsand_20261007T205531Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/TitanicCreatures_20261007T190704Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/TitanicCreatures_20261007T190704Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/TitanicCreatures_20261007T190833Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/TitanicCreatures_20261007T190833Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261007T191536Z.html   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/modcheck/Warcasket_20261007T191536Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/muffalo_rect_trace_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/northstar/ArtOverrideFamily_static_20261004T101503Z.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/northstar/ExplosiveGrowth_20261003T101654Z.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/northstar/FloodedCanyon_20261003T101943Z.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/northstar/Greentide_20261003T102251Z.json   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/northstar/IshkoDarkLandmarks_20261007T205638Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/northstar/IshkoDarkLandmarks_20261007T205744Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/northstar/IshkoDarkLandmarks_20261007T205850Z.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/northstar/IshkoDarkLandmarks_session_20261007T135638.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/northstar/IshkoDarkLandmarks_session_20261007T135744.log   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/overwritten_20261007/   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/rc2_FallLineArrivals.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/rc2_TitanicCreatures_patched.json   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/rc2_call.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/rc2_dbg.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/rc2_menu.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/rc2_run.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/rc2_sess.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/rc2_titanic/   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/rc2_wake.py   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/refused_toll_rite_20261006.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/review_kernels_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/review_pyrelands_20261006.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/review_scarlands_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/selftest_regressions_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/shipshields_derive_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/shipvermin_free_tier_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/slime_antidote_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/titanic_harness_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/unfinished_line_world_20261006.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? Transient/validation_Armoury_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_EmpirePursuit_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_ExplosiveGrowth_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_JawaIonWeapons_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_JawaRules_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_KeelHoist_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_RimProperty_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_SWBestiary_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_TheSump_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_Warcasket_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_Webwork_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_abyss_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_bluedesert_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_cauldron_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_contagion_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_creaturebehaviors_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_depsweep_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_divinginteraction_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_droidworks_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_environmentalhazards_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_feverwood_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_floodedcanyon_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_gelatinousslime_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_graffiti_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_greentide_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_inhabited_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_lanterndeeps_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_leaningscrub_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_luminouspigment_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_miasma_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_movingdunes_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_oracle_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_pyrelands_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_sacredgraffiti_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_scarlands_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_solarmirrors_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_stillsand_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_structureinjections_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_terminalbiomes_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_theforge_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_therot_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_visibility_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_wasteland_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_watchers_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_weepingstones_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/validation_wreckage_20261007.md   this session's helper/sweep output (FOUNDRY 2026-10-07), scratch; Transient shelf life ~14 days
?? Transient/venomvine_forms_20261006.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? conversations/   Lodestar conversation record, generated
?? deployed/config/ModsConfig.before-tier-acc_biomes.xml   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ModsConfig.before-tier-acc_green_min.xml   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ModsConfig.before-tier-acc_green_min2.xml   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ModsConfig.before-tier-acc_harness.xml   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ModsConfig.before-tier-acc_l1x.xml   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ModsConfig.before-tier-flowworks.xml   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ModsConfig.before-tier-ishko.xml   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T142015.xml   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T161529.xml   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ModsConfig.pre-session.20261007T135600.xml   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ns_flowworks_backup.20261002T070221.json   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ns_flowworks_backup.20261005T142015.json   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? deployed/config/ns_flowworks_backup.20261005T161529.json   tier-swap backup written by modset_builder --apply (FOUNDRY 2026-10-07), local only
?? infrastructure/state/items/SHIPVERMIN_FREE_TIER_BEASTS_1.md   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_dry_dirt.png   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_dry_stone.png   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_scorched_dirt.png   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/structure_scorched_stone.png   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261005T232949.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261005T233603.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T000710.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T001245.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T002141.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003132.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003420.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003624.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003701.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T003821.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T004655.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T010918.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T011022.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T011246.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T020515.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021000.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021144.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021337.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T021908.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261006T033840.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261007T140351.json   older untracked FlowWorks run output, not mine (BELT/BENCH earlier), leave
?? src/RimMandrake/SacredGraffiti/Assemblies/SacredGraffiti.dll.srchash   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? src/RimMandrake/Visibility/Assemblies/RimMandrakeVisibility.dll.srchash   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
?? src/RimMandrake/selftest_weepingstones_fuzz.py   another window's or earlier session's scratch output (BELT/bridge runs), not mine; Transient shelf life ~14 days
```

