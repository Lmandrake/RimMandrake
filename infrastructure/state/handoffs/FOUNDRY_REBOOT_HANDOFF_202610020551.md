# FOUNDRY_REBOOT_HANDOFF_202610020551 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202610010319`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Test worlds must be static and boring, and every interference (naming dialogs, random events, focus theft, dirty maps, missing-type load errors) is fixed in the Northstar TOOLING with a selftest, never clicked past (owner 2026-10-01, memory static-boring-test-worlds). A clean 13-suite pass takes ~16 min; the 3.5 h lost was reruns (design/RimMandrake/northstar_time_ledger_2026-10-01.md). Publishing: use `./publish -m "subject" <paths>` (plumbing, no checkout) then `rimflow close <ID> --sha <PUBLISHED sha>`; hand-rolled worktrees/cherry-picks are what made git miserable.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1) Cindermare, Skarnix, Karrask, Tellurox each ship one texture with no facings; the seeded DRAFT northstar lines for them are guesses for you to rule on. 2) 37 walks now carry DRAFT `## north star` sections (nothing validated; `modcheck validate` needs your verbatim word). 3) JAWA_NAMEMAKER_NEVER_FIRES_1: RSW_MandrakeJawa sets a nameMaker with chanceToUseNameMaker unset (=0), so Jawa always get human names; 43 of 48 sibling xenotypes share the shape. 4) Motion-frames judge was built as a PROVISIONAL seed on your 2026-10-01 words; FlowWorks `(change)` bars now judge UNJUDGEABLE with a single screenshot.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `NORTHSTAR_SITUATIONAL_ROLLOUT_1` — 12/14 suites measured with 0 aborts; abort path proven live (6 hazards, J2); the 13-suite re-run from a saved bland world has NOT completed; NEXT: after step below, run `python.exe src/RimMandrake/Utils/modcheck/live_queue/run_next.py --all` on a freshly launched minimal list and record per-suite wall time and ticks/s
- `NORTHSTAR_BLAND_TILE_1` — J3 proved colony_found + destroy_bulk + ruin destroy_batch yields a bland map (10/10) but no BLAND_NORTHSTAR_BASE save exists yet; NEXT: run live_queue/j6_bland_base.py once (needs `jawa/name_colony` DLL, already deployed --gm) and prove a NEW save file with no existing save changed
- `NORTHSTAR_PASS3_PREP` — prep deployed stale DLLs because shared-tree src/ was ~304 commits behind (fixed by the checkout sync; Stillsand DLL now 140 KB); NEXT: add a stale-source gate to live_queue/prep_wsl.py and confirm `Player.log` has no 'Could not find type named RimMandrake' via launch_gate.py before any map starts
- `NORTHSTAR_TIME_LEDGER_FIXES` — ledger fixes not applied: summary written before verify and verify non-fatal (RIMFLOW_SEAT invisible to python.exe), relaunch between full runs, ticks/s per suite, Antiquities/FlowWorks waits, cache J0/J2-J5 by code hash, bigger idle chunks, save_base trips on Autosave-*.rws; NEXT: file these as items from design/RimMandrake/northstar_time_ledger_2026-10-01.md and work them in that order
- `GIT_WORKFLOW_FIX_1` — ./publish and --catchup shipped (6598ac41e, eca3d0aca); shared tree still ~300 commits behind because local e55ff18da and 4e2b103f3 are redundant locals (verified: their code, ledger events and lessons are all already on origin under other shas); NEXT: run `./publish --catchup` after retiring those two shas (ask the owner or use a private branch ref; never reset --hard here), then give the worktree janitor a time cap (its dry run over 124 worktrees took >10 min) and prune the ~124 stale `.claude/worktrees/agent-*`
- `NORTHSTAR_VALIDATION_SKILL_1` — filed only; NEXT: write the skill in a fresh-context curation session once the saved-world flow is proven live
- `NORTH_STAR_WALK_AUTHORING_1` — 37 DRAFT sections seeded (7ace61107, 021a7cbd1, 86744333e, b22eb4824); NEXT: continue seeding the remaining walks without a section (skip code-only mods), tag guesses `(guess)`
- `JAWA_NAMEMAKER_NEVER_FIRES_1` — filed from suite corrections; NEXT: show it and decide whether to set chanceToUseNameMaker on RSW_MandrakeJawa (owner-visible name change)
- `MODCHECK_SUITE_CORRECTIONS_1` — 20 suite bugs fixed offline (33574d7e4), proven offline only; NEXT: confirm each row on the next live run and close it
- `BLUEDESERT_GPT_ENRICHMENT_1` — carried over, untouched; NEXT: quicktest cold rack, three incident variants and vhaulk road after deploy
- `GRAVSHIP_ACOUSTIC_SCANNER_1` — carried over, untouched; NEXT: add mandrake.rm.acousticscanner to a test tier and quicktest on a landed powered gravship
- `SCALD_CROWNCARPET_NO_HABITAT_1` — carried over, untouched; NEXT: run rimflow show SCALD_CROWNCARPET_NO_HABITAT_1 and either work or block it
- `WASTELAND_GPT_ENRICHMENT_1` — carried over, untouched; NEXT: quicktest storms, Middenshell, WasteCaskBay and Rite of Tipping after deploy

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Naming dialogs re-raise every ~600 ticks until named; modal_open must ignore Dialog_NamePlayer* (filed: LESSONS_INBOX)
- A late step_game_ticks reply poisons the bridge socket with 'unexpected response id' for every later call (filed: LESSONS_INBOX)
- 'Error while generating map' = a def with null thingClass because composed biomes shipped XML without the owning mods' DLLs; stale shared-tree src/ made it worse (see: Transient/northstar_pass3_2026-10-01.md)
- `rimflow close --sha` with a failed commit silently falls back to HEAD and records the wrong sha (see: Transient/runner_windows_py_2026-10-01.md)
- cd persists between Bash calls and `$R file` word-splitting fails in zsh; use a script or full command (see: CLAUDE.md zsh note)
- git relativeworktrees extension breaks dotnet SourceLink: build with EnableSourceControlManagerQueries=false EnableSourceLink=false via WSLENV (see: design/RimMandrake/git_workflow_fix_2026-10-01.md)

## Closed since the last handoff (6)

- `FEVERWOOD_SAP_SUCKER_TUNING_1` — 9af41986b3207fec2ba2b8497210aa3ee06ca296
- `NORTHSTAR_SWEEP_BOMB_1` — b246bc43797b2fd8c180168eb7bc04027386a6f7
- `NORTHSTAR_RUNNER_WINDOWS_PY_1` — 0e4661a55404d573ab3ecbc2b75a935a5795fd8a
- `NORTHSTAR_ANTIQUITIES_TICK_CAP_1` — 0e4661a55404d573ab3ecbc2b75a935a5795fd8a
- `NORTHSTAR_COMPANION_LIVE_PROOF_1` — b1b1d98f7b1f312f840e81b0dc6acc3724355f90
- `NORTHSTAR_MOTION_FRAMES_1` — 8463a2734741e94146ef7214301421ed32780c51

## Filed and still open (9) — the next seat's queue

- `WARSCAR_CHOTRIX_BUILD_1` — Chotrix: the Warscar's invisible hunter (cloak-lacquer eater, prints on the track grid) + permanent cloak lacquer (owner card 2026-09-30)
- `FEVERWOOD_SAP_SUCKER_MISHANDLE_HOOK_1` — Harmony postfix on Pawn_MindState.CheckStartMentalStateBecauseRecruitAttempted so a failed tame triggers the sap-sucker refusal (opus; add Harmony ref
- `DEPLOYED_BIOME_REFS_ROTSPOREKIT_1` — selftest_deployed_biome_refs fails: 19 wildPlants/wildAnimals entries in deployed RUT_TheRot/RUT_Contagion/RUT_Miasma name defs absent because mandrak
- `PYRELANDS_WALKLINT_FINDINGS_1` — run_selftests reports 3 walklint findings in design/validation_walks/RimMandrake/Pyrelands.md (found by STILLSAND_SKELETONS_TRACKS_1 full run 2026-10-
- `NORTHSTAR_SITUATIONAL_ROLLOUT_1` — Flip modcheck --situational to default after an abort-only pass over every suite
- `NORTHSTAR_BLAND_TILE_1` — Generate a genuinely bland test map (flat dry tile, no ruins) via jawa/world_tile_map_generate instead of the random quicktest forest
- `NORTHSTAR_COMPANION_GAPS_1` — Companion tools: pawn census (mental state+job), incident-queue peek/selective remove, damage-event ring buffer, holder/stack lineage, pawn roles+lord
- `JEV_KEY_ARCHMAGI_1` — Provision TYPESAFE_API_KEY on Archmagi so northstar can run Jev (shadow mode ships without it)
- `NORTHSTAR_VALIDATION_SKILL_1` — Carve a northstar-validation skill out of rimworld-debug-testing: bland saved world, situational envelope, live_queue, companion detectors, interferen

## Commits

```
b246bc437 rimdrive sweep: kill test pawns by exact id, not Bomb 99999
e55ff18da Northstar: Jev shadow layer, vacuity lint, measured results; follow-up items filed
3d6c96389 Northstar: safe anchor away from colonists, resurrect between chains, wildlife removal without detonation
98c17b40f Northstar situational envelope: watch/surprise capture wired into suite+runner (--situational), measured fixes
7c64f84e6 Northstar helpers: clockgate, snapshot, detectors, helpers, fake world + live contract fixture
0a57346ff Northstar situational helpers: plan + GPT review revisions
89dd14144 Art-owed check: Forge/Warcasket subjects (5 of 6 already rendered)
9af41986b BENCH handoff 2026-10-01: Stillsand + Warscar bedazzled; Black Crags next
4e94a0e49 Art queue: RM_Chotrix
4e2b103f3 WARSCAR_CHOTRIX_BUILD_1: chotrix admitted, permanent cloak lacquer
65488c2a9 Ledger sync: Warscar volley turn 4 rulings
44ab4d560 Warscar bedazzle: volley turn 3 development
3431abc01 Docs: RM_PropaneLake -> RM_TheChill follow-through; artpipe registry union
f0e88429e Ledger sync: Warscar GPT refinements ruled
fcf4d0eee handoff.py: unpushed gate uses git cherry, not git log
27c9d8a83 GPT consult: Warscar enrichment answer
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-10-02T05:40:53Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M CLAUDE.md   a subagent or peer window (already published or not mine)
 M Transient/codebase_health.html   the health publisher (regenerated, not mine)
 M Transient/codebase_health.json   the health publisher (regenerated, not mine)
 M Transient/codebase_health_artifact.html   the health publisher (regenerated, not mine)
A  Transient/northstar_live_pass2_2026-10-01.md   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  Transient/world_reset_2026-10-01.md   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
 M deployed/config/ModsConfig.before-tier-pits.xml   BENCH's design work (not mine)
 M design/Jawa/worldbuilding/biomes/rosters/the_propane_lakes.json   BENCH's design work (not mine)
 M design/Jawa/worldbuilding/biomes/terminal_seas_cast_proposal_2026-09-25.md   BENCH's design work (not mine)
A  design/RimMandrake/northstar_live_queue_2026-10-01.md   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
 M design/RimMandrake/sea_dive_maps_spec.md   BENCH's design work (not mine)
 M design/RimMandrake/sea_shore_mutator_spec.md   BENCH's design work (not mine)
 M design/RimUtinni/vanilla_beast_excision_census.md   BENCH's design work (not mine)
 D infrastructure/artpipe/active/RM_Biosilica.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/active/RM_BloodyMess_v2_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/active/RM_Boilhide_v2_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/active/RM_Filth_MiddenshellFlakes.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/active/RM_GlassSand.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/active/RM_Gloomcast_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/active/RM_LensSand.json   the artpipe daemon (runtime churn, not mine)
 M infrastructure/artpipe/daemon_run_20260927_derivefacings.log   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/failed/rut_greentideant_carapacewall_atlas.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/failed/rut_greentideant_carapacewall_menuicon.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_AblationSilhouette.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Aurrok_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Aurrok_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Aurrok_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_BloodyMess_v2_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_BloodyMess_v2_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_BlueIceMeltwaterCan.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Boilhide_v2_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Boilhide_v2_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Chotrix_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Chotrix_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Chotrix_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_CloudRepulsor_v2.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_ColdSinkRack.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_CrestPlate.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_CrownVenomvine.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Cruststar.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Crustweevil_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Crustweevil_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Crustweevil_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_DebtStone.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_DewfringeSprig.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_DhokkurDormant.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Dhokkur_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Dhokkur_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Dhokkur_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_DhuvvoxNodule.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Dhuvvox_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Dhuvvox_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Dhuvvox_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Drazzik_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Drazzik_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Drazzik_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_DrippingVenomvine.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_DustDevil.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Dustflutter_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Dustflutter_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Dustflutter_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Eskith_v2_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Eskith_v2_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Eskith_v2_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Eyebark_v2.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_FE_Fulgurite_real.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Filth_DisturbedSand.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Filth_DragMark.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Filth_EruptionScar.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Filth_GlasscrustScar.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Filth_MiddenshellFootprint.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Filth_OommokPrint.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Filth_SandWake.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Fleshsop_v2_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Fleshsop_v2_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Fleshsop_v2_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Floatstone.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_FloatstoneGarden.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_FossilSkeleton_v2.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Fuzzrunner_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Fuzzrunner_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Fuzzrunner_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Fuzzviper_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Fuzzviper_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Fuzzviper_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Geophone.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Gloomcast_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Gloomcast_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_GreatDevourer_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_GreatDevourer_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_GreatDevourer_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Grimewing_v2_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Grimewing_v2_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Grimewing_v2_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Gristleswarm_v2_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Gristleswarm_v2_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Gristleswarm_v2_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Groundrunner_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Groundrunner_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Groundrunner_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_GuzzkaSkeleton.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Guzzka_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Guzzka_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Guzzka_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_HalfExtractedCore.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Hazebell.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Hazebell_Open.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_HollowVenomvine.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Jossur_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Jossur_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Jossur_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Julmox_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Julmox_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Julmox_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Krannock_v1_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Krannock_v1_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Krannock_v1_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_LensBench_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_LensBench_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_LensBench_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Longglass.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Maidenbloom.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_MatureFleshbeast_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_MatureFleshbeast_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_MatureFleshbeast_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_MiddenshellEdgeScar.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_MiddenshellTrack.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Middenshell_v2_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Middenshell_v2_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Middenshell_v2_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Milelace.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Mirrak_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Mirrak_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Mirrak_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Muttavaq_v2_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_MuurrokSkeleton.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Muurrok_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Muurrok_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Muurrok_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Nizzek_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Nizzek_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Nizzek_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_OommokSkeleton.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Parasol.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_ParasolWorn_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_ParasolWorn_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_ParasolWorn_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Pavecrust.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_PearlLens.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Pillowmoss.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_PrecisionLens.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_RawVenom.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Ribbonwhip_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Ribbonwhip_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Ribbonwhip_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Rollbug_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Rollbug_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Rollbug_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_SandSieve.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Scumslider_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Scumslider_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Scumslider_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_SealedWaterJar.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Seismograph_v2.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_ShadeTent.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Shadespire.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Shirrel_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Shirrel_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Shirrel_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Shokka_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Shokka_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Shokka_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Sippra_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Sippra_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Sippra_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Skarrok_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Skarrok_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Skarrok_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Slagmole_v2_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Slagmole_v2_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Slagmole_v2_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Sloghog_v2_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Sloghog_v2_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Sloghog_v2_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_SolarOven.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_SolarStill.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_SunFurnace.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_SunGlass.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_SunGoggles.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_SunGogglesWorn_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_SunGogglesWorn_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_SunGogglesWorn_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_SunLance_Base.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_SunLance_Top.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_SunShield_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_SunShield_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_SunShield_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Surrik_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Surrik_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Surrik_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Tanglefuzz.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Tazzok_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Tazzok_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Tazzok_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Thornhold_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Thornhold_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Thornhold_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Thumper.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Tikkit_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Tikkit_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Tikkit_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_TruffleMole_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_TruffleMole_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_TruffleMole_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_TwitcherVenomvine.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Vekka_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Vekka_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Vekka_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_VenomvineThicket_v2.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Vexxiss_v2_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Vexxiss_v2_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Vexxiss_v2_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Vhaulk_v2_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_VisslerArm.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Vissler_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Vissler_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Vissler_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_VozzikSkeleton.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Vozzik_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Vozzik_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Vozzik_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Vrekka_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Vrekka_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Vrekka_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_WasteCask.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_WasteCaskBay_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_WasteCaskBay_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_WasteCaskBay_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_WasteTippingPad.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Whipfuzz.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_WreckedCart.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Zellik_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Zellik_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RM_Zellik_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RSW_CrawlerTreadWreck.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RSW_Filth_CrawlerTread.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RSW_GreaterKraytSkeleton.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RSW_KraytHorn.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RSW_KraytLens.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RSW_KraytSkeleton.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RSW_WarWyrmSkeleton.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RSW_WreckedSkiff.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientAirlock.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientAirlock_Large.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientBlackBox_Off_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientBlackBox_Off_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientBlackBox_Off_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientBlackBox_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientBlackBox_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientBlackBox_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientFloorHeater.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientLandmine.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientShieldedTurret.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientShipLandingBeacon.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientSpacerAutocannon.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientTransmitterBeacon.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientWargamingTable_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientWargamingTable_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_AncientWargamingTable_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_BlueprintsBench_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_BlueprintsBench_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_BlueprintsBench_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_BustedShieldedTurret.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_BustedSpacerAutocannon.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_CryptoAncientTerminalBank_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_CryptoAncientTerminalBank_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_CryptoAncientTerminalBank_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_CryptoAncientTerminal_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_CryptoAncientTerminal_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_CryptoAncientTerminal_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_ForcedAncientAirlock.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_ForcedAncientAirlock_Large.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_FoundrySalvageCache.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_FoundryTowerEntrance.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_FrozenEmptyCryptosleepPod.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_JammedAncientAirlock.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_JammedAncientAirlock_Large.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_RuinedHospitalBed_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_RuinedHospitalBed_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_RuinedHospitalBed_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/RUT_TibannaGas.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/coalescence_stage2_v2.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/coalescence_stage3_v2.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/rsw_blurrg_v1_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/rsw_blurrg_v1_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/rsw_blurrg_v1_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/rsw_blurrg_v2_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/rsw_blurrg_v2_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/rsw_blurrg_v2_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/rsw_scrapnestbird_v1_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/rsw_scrapnestbird_v1_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/rsw_scrapnestbird_v1_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/rsw_shrublandgiant_v1_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/rsw_shrublandgiant_v1_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/rsw_shrublandgiant_v1_south.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/rsw_tunnelsnake_v1_east.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/rsw_tunnelsnake_v1_north.json   the artpipe daemon (runtime churn, not mine)
 D infrastructure/artpipe/pending/rsw_tunnelsnake_v1_south.json   the artpipe daemon (runtime churn, not mine)
 M infrastructure/artpipe/registry.jsonl   the artpipe daemon (runtime churn, not mine)
 M infrastructure/artpipe/throughput.jsonl   the artpipe daemon (runtime churn, not mine)
 M infrastructure/dashboards/hub/data/health.json   the health publisher (regenerated, not mine)
M  infrastructure/state/LESSONS_INBOX.md   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
 M infrastructure/state/codebase_health_last.json   the health publisher (regenerated, not mine)
 D infrastructure/state/items/NORTHSTAR_MOTION_FRAMES_1.md   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
 M infrastructure/state/ledger/events/BENCH.jsonl   BENCH/OWNER window's ledger writes (not mine)
MM infrastructure/state/ledger/events/FOUNDRY.jsonl   mine, FOUNDRY ledger/projection (local; published events via ./publish)
 M infrastructure/state/ledger/events/OWNER.jsonl   BENCH/OWNER window's ledger writes (not mine)
M  infrastructure/state/modcheck_status.json   mine, FOUNDRY ledger/projection (local; published events via ./publish)
 M infrastructure/state/queue/BENCH.md   BENCH/OWNER window's ledger writes (not mine)
 M infrastructure/state/queue/FOUNDRY.md   mine, FOUNDRY ledger/projection (local; published events via ./publish)
A  src/RimMandrake/Abyss/About/About.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Abyss/Assemblies/RimMandrake.Abyss.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Abyss/Assemblies/RimMandrake.Abyss.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Abyss/Defs/BiomeDefs/RM_Abyss.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Abyss/Source/RM_Abyss.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Abyss/Source/RM_AbyssBiome.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Abyss/Source/RM_AbyssMod.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Aftermath/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Biomes.compose.json   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/BiomesShell/Source/RM_Biomes.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/BlueDesert/Assemblies/RimMandrake.BlueDesert.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/BlueDesert/Assemblies/RimMandrake.BlueDesert.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/BlueDesert/Defs/BiomeDefs/RM_BlueDesert.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/BlueDesert/Source/RM_BlueDesert.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/BlueDesert/Source/RM_BlueDesertMod.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/BlueDesert/northstar_plan.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/BlueDesert/northstar_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/BlueDesert/selftest_bluedesert.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/BlueDesert/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Cauldron/Assemblies/RimMandrake.Cauldron.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Cauldron/Assemblies/RimMandrake.Cauldron.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Cauldron/Defs/ThingDefs_Plants/RM_CauldronFlora.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Cauldron/Defs/ThingDefs_Races/RM_CauldronFauna.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Cauldron/Source/RM_Cauldron.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Cauldron/Source/RM_CauldronBiome.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Cauldron/Source/RM_CauldronMod.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Cauldron/Source/RM_CompMetalYield.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Cauldron/Source/RM_CompVexxissBehaviour.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Cauldron/Source/RM_CondensateGardens.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Cauldron/northstar_plan.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Cauldron/northstar_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Cauldron/selftest_cauldron.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Cauldron/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Contagion/Assemblies/RimMandrake.Contagion.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Contagion/Assemblies/RimMandrake.Contagion.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Contagion/Defs/AbilityDefs/RM_GrownLimbAbilities.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Contagion/Defs/BiomeDefs/RM_Contagion.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Contagion/Defs/HediffDefs/RM_GrownLimbHediffs.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Contagion/Defs/PlantDefs/RM_ContagionFlora.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Contagion/Defs/RecipeDefs/RM_InstallMonstrousLimbs.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Contagion/Defs/ThingDefs/RM_MonstrousLimbs.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Contagion/Source/AmoebaHostUtility.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Contagion/Source/Building_RM_Coalescence.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Contagion/Source/CompGenomeSample.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Contagion/Source/FloatMenuOptionProvider_InjectGenomeSample.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Contagion/Source/HediffComp_UnfinishedEmerge.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Contagion/Source/Hediff_AmoebaGestation.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Contagion/Source/JobDriver_RM_InjectGenomeSample.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Contagion/Source/RM_Contagion.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Contagion/Source/RM_ContagionBiome.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Contagion/Source/RM_ContagionMod.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Contagion/northstar_plan.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Contagion/northstar_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Contagion/selftest_contagion.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Contagion/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Assemblies/RimMandrake.CreatureBehaviors.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Assemblies/RimMandrake.CreatureBehaviors.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Defs/GameConditionDefs/RM_Mirage_GameConditions.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Defs/GeneDefs/RM_GlareAdapted.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Defs/HediffDefs/RM_GlareBlind_Hediffs.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Defs/HediffDefs/RM_SandSwim_Hediffs.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Defs/MapMeshFlagDefs/RM_TrackPrints_MapMeshFlag.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Defs/MentalStateDefs/RM_ChasingWater_MentalStates.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Defs/ThingDefs_Misc/RM_KillSigns_Filth.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Defs/ThinkTreeDefs/RM_ThinkTree_ShadowFollow.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Patches/RM_Mirage_ThinkTree.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Source/RM_CompProperties_ShadowCaster.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Source/RM_CompSandSwim.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Source/RM_Comp_ShadowCaster.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Source/RM_CreatureBehaviors.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Source/RM_CreatureBehaviorsMod.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Source/RM_FlightJobStartGuard.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Source/RM_Gizmo_SunLoad.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Source/RM_GlareBlind.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Source/RM_HeatSoundscape.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_ProximitySoundscape.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_ShadeGrid.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_TrackGrid.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Source/RM_Mirage.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Source/RM_MovingShadeMath.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Source/RM_SandSwimExtension.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Source/RM_SectionLayer_TrackPrints.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Source/RM_ShadeHop.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Source/RM_SunHeatExtension.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Source/RM_SunHeatMath.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Source/RM_SunHeatPatches.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Source/RM_TrackGridPatches.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Source/RM_TrackPool.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Source/RM_TrackSurfaceExtension.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Source/RM_WeatherSenseExtension.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Source/SelfTest/Program.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/CreatureBehaviors/Source/SelfTest/RimMandrakeCreatureBehaviors.SunHeat.SelfTest.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Source/SelfTestTracks/Program.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Source/SelfTestTracks/RimMandrakeCreatureBehaviors.TrackGrid.SelfTest.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Textures/Things/Tracks/RM_TrackDrag.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Textures/Things/Tracks/RM_TrackPrint_Animal.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Textures/Things/Tracks/RM_TrackPrint_Human.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/CreatureBehaviors/Textures/Things/Tracks/RM_TrackPrint_Large.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/ExplosiveGrowth/About/About.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/ExplosiveGrowth/northstar_plan.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/ExplosiveGrowth/northstar_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/ExplosiveGrowth/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FeverWood/About/About.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FeverWood/Assemblies/RimMandrake.FeverWood.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FeverWood/Assemblies/RimMandrake.FeverWood.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FeverWood/Defs/HediffDefs/RM_SapSuckerGuild_Hediffs.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FeverWood/Defs/ThingDefs_Items/RM_SapSuckerGuildProducts.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FeverWood/Defs/ThingDefs_Races/RM_Kurreth_Race.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FeverWood/Defs/ThingDefs_Races/RM_SapSuckerGuild.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FeverWood/Source/RM_CompProperties_SapSuckerRefusal.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FeverWood/Source/RM_CompSapSuckerRefusal.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FeverWood/Source/RM_FeverWood.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FeverWood/Source/RM_FeverWoodMod.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/FeverWood/Source/RM_Patch_SapSuckerMishandle.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/FeverWood/northstar_plan.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/FeverWood/northstar_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/FeverWood/selftest_feverwood.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/FeverWood/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FloodedCanyon/Assemblies/RimMandrake.FloodedCanyon.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FloodedCanyon/Assemblies/RimMandrake.FloodedCanyon.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FloodedCanyon/Defs/BiomeDefs/RM_FloodedCanyon_Biome.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/FloodedCanyon/Defs/HediffDefs/RM_IrqitFloodBorn.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/FloodedCanyon/Defs/SoundDefs/RM_CanyonBeats.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FloodedCanyon/Defs/ThingDefs_Races/RM_IrqitTarruq.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FloodedCanyon/Defs/WeatherDefs/RM_PeakstormLight.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FloodedCanyon/Source/Debug/RM_FloodedCanyonDebugActions.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FloodedCanyon/Source/RM_FloodedCanyon.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FloodedCanyon/Source/RM_FloodedCanyonDefOf.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FloodedCanyon/Source/RM_FloodedCanyonMod.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FloodedCanyon/Source/RM_MapComponent_CanyonFlood.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/FloodedCanyon/Source/RM_MapComponent_RecedeAftermath.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/FloodedCanyon/Source/RM_TarruqHushPatch.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FlowWorks/Source/LiquidTypes/RM_LiquidProperties.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/FlowWorks/northstar/fakegame.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/FlowWorks/northstar/preflight_flowworks.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/FlowWorks/northstar/prep_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/FlowWorks/northstar/selftest_flowworks_northstar.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/FlowWorks/northstar/site_spec.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/FlowWorks/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/GelatinousSlime/northstar_mock.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/GelatinousSlime/northstar_plan.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/GelatinousSlime/northstar_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/GelatinousSlime/selftest_slime_suite.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/GelatinousSlime/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Graffiti/Assemblies/RimMandrakeGraffiti.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Assemblies/RimMandrakeGraffiti.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_CrossOut/crossout_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_AnimalPersonhood/animalpersonhood_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Blindsight/blindsight_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Cannibal/cannibal_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Collectivist/collectivist_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Darkness/darkness_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_FemaleSupremacy/femalesupremacy_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_FleshPurity/fleshpurity_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Guilty/guilty_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_HighLife/highlife_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_HumanPrimacy/humanprimacy_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Individualist/individualist_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Inhuman/inhuman_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Loyalist/loyalist_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_MaleSupremacy/malesupremacy_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_NaturePrimacy/natureprimacy_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Nudism/nudism_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_PainIsVirtue/painisvirtue_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Proselytizer/proselytizer_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Raider/raider_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Rancher/rancher_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Ritualist/ritualist_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Shipborn/shipborn_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Supremacist/supremacist_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Transhumanist/transhumanist_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_TreeConnection/treeconnection_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Tunneler/tunneler_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Paste_Flyer/paste_flyer_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Paste_Flyer/paste_flyer_1.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Paste_Wanted/paste_wanted_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Paste_Wanted/paste_wanted_1.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_SigilFrame_Halo/halo_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Stencil_Crown/stencil_crown_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Stencil_Fist/stencil_fist_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Stencil_Gear/stencil_gear_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Tag_A/tag_a_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Tag_A/tag_a_1.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Tag_B/tag_b_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Tag_B/tag_b_1.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Tag_C/tag_c_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Tag_C/tag_c_1.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_ThrowUp_A/throwup_a_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_ThrowUp_A/throwup_a_1.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_ThrowUp_B/throwup_b_0.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_ThrowUp_B/throwup_b_1.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/northstar_plan.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Graffiti/northstar_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Graffiti/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Greentide/Defs/BiomeDefs/RM_Greentide_Biome.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Greentide/Defs/ThingDefs/RM_GreatboleHarvest_Items.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Greentide/Defs/ThingDefs_Races/RM_GreatboleGrub.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Greentide/Defs/ThingDefs_Races/RM_Skerrel_Race.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/HostileFlora/About/About.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/HostileFlora/Defs/ThingDefs_Races/RM_Gallowroot.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Inhabited/Defs/CastRosters/CastRoster_DROIDS.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Inhabited/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LeaningScrub/Assemblies/RimMandrake.LeaningScrub.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LeaningScrub/Assemblies/RimMandrake.LeaningScrub.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LeaningScrub/Defs/BiomeDefs/RM_LeaningScrub_Biome.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/LeaningScrub/Defs/RulePackDefs/RM_LeaningScrub_Namers.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_LeaningScrubVenomvineForms.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_SweetlineTree.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LeaningScrub/Source/RM_LeaningScrub.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LeaningScrub/Source/RM_LeaningScrubMod.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/LeaningScrub/Source/RM_RunwayBloom.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/LeaningScrub/Source/RM_SweetlineStation.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/LeaningScrub/Source/RM_VenomvineRooms.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/LeaningScrub/northstar_plan.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/LeaningScrub/northstar_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/LeaningScrub/selftest_leaningscrub.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/LeaningScrub/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LongShade/About/About.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LongShade/Assemblies/RimMandrake.LongShade.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LongShade/Assemblies/RimMandrake.LongShade.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LongShade/Defs/BiomeDefs/RM_LongShade.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/LongShade/Defs/SoundDefs/RM_LongShade_HeatSounds.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LongShade/Defs/ThingDefs_Plants/RM_Ultracactus.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LongShade/Defs/ThingDefs_Races/RM_LongShade_Gloomcast.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LongShade/Defs/ThingDefs_Races/RM_LongShade_Mirrak.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/LongShade/Defs/ThinkTreeDefs/RM_LongShade_ShipfallCommons.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LongShade/Source/RM_LongShade.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/LongShade/Source/RM_LongShadeMod.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/LongShade/Source/RM_ShipfallCommons.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/LuminousPigment/northstar_plan.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/LuminousPigment/northstar_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/LuminousPigment/selftest_luminouspigment.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/LuminousPigment/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Miasma/Assemblies/RimMandrake.Miasma.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Miasma/Assemblies/RimMandrake.Miasma.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Miasma/Defs/BiomeDefs/RM_Miasma.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Miasma/Source/RM_MiasmaBiome.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/MovingDunes/Assemblies/RimMandrakeMovingDunes.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/MovingDunes/Assemblies/RimMandrakeMovingDunes.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/MovingDunes/Patches/BiomeBindings.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/MovingDunes/Source/DuneFieldExtension.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/MovingDunes/Source/DuneWindBearing.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/MovingDunes/Source/MapComponent_DuneField.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/MovingDunes/Source/MovingDunesMod.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/MovingDunes/Source/MovingDunesSettings.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/MovingDunes/Source/Patch_ClearSandYield.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/MovingDunes/Source/RM_DuneMaterialDef.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/MovingDunes/Source/RimMandrake_MovingDunes.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Ninefold/Source/God.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Ninefold/Source/Patch_FireStarted.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Ninefold/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Pyrelands/Assemblies/FireEcologyHook.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Pyrelands/Assemblies/FireEcologyHook.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Pyrelands/Source/RM_PyrelandsMod.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Pyrelands/northstar_plan.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Pyrelands/northstar_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Pyrelands/preflight_pyrelands.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Pyrelands/selftest_pyrelands_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Pyrelands/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/RustCathedral/Assemblies/RimMandrake.Utinni.RustCathedralHum.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/RustCathedral/Assemblies/RimMandrake.Utinni.RustCathedralHum.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/RustCathedral/Source/Hum/RM_MapComponent_BiomeAttitude.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/About/About.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Assemblies/RimMandrake.Stillsand.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Assemblies/RimMandrake.Stillsand.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Defs/BiomeDefs/RM_Stillsand_Biome.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/HediffDefs/RM_CoolingDraught.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/IncidentDefs/RM_SandLeviathanIncidents.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/JobDefs/RM_PourWaterIntoSand.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/MapGeneration/RM_GiantSkeletons.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/MapGeneration/RM_PreciousCaves.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/RecipeDefs/RM_GlassChain_Recipes.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/SoundDefs/RM_BoneHarp.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/ThingDefs_Apparel/RM_SunGoggles.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/ThingDefs_Buildings/RM_GiantSkeletons.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/ThingDefs_Buildings/RM_GlassChain_Buildings.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Defs/ThingDefs_Buildings/RM_SandBusterMound.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/ThingDefs_Items/RM_CrestPlate.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/ThingDefs_Items/RM_GlassChain_Items.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/ThingDefs_Items/RM_SandCatches.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/ThingDefs_Plants/RM_Stillsand_FilloutFlora.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Defs/ThingDefs_Plants/RM_Stillsand_SignatureFlora.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Aurrok.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Drazzik.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Guzzka.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Ikee.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Muurrok.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Oommok.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Qorrax.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_SandBusters.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_ShadeMite.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Siidda.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Stillsand_Fillout.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Vaalok.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Vekka.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Vozzik.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Zuurrik.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Defs/WeatherDefs/RM_DuneGale.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Patches/RM_GiantSkeletons_Wiring.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Patches/RM_GlassChain.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Patches/RM_PreciousCaves_BiomeGenSteps.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Patches/RM_SandRemembersWater_Stillsand.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/RM_DuneGale.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/RM_DustDevil.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/RM_GiantSkeletons.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/RM_GlassChainMod.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/RM_HorizonWarning.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Source/RM_IncidentWorker_SandBusterEruption.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/RM_MapComponent_Zuurrik.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/RM_PreciousCaveGeometry.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/RM_PreciousCaveSettings.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/RM_PreciousCaves.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/RM_SandLeviathan.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/RM_SkeletonSettings.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Source/RM_Stillsand.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/RM_StillsandEventsMod.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Stillsand/Source/RM_StillsandMod.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/RM_StillsandWater.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/RM_SunPowered.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/RM_Verb_MirrorBeam.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/RM_WaterLedger.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/SelfTest/Program.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Source/SelfTest/RimMandrakeStillsand.PreciousCaves.SelfTest.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Building/Natural/RM_SandBusterMound.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Ethereal/RM_DustDevil.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Item/Egg/RM_EggScaled/EggScaled_a.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Item/Egg/RM_EggScaled/EggScaled_b.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Item/Resource/RM_Biosilica.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Item/Resource/RM_DuneCrawler.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Item/Resource/RM_GlassPearl.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Item/Resource/RM_OllimWood.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Aurrok/RM_Aurrok_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Aurrok/RM_Aurrok_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Aurrok/RM_Aurrok_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Drazzik/RM_Drazzik_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Drazzik/RM_Drazzik_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Drazzik/RM_Drazzik_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Duumma/RM_Duumma_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Duumma/RM_Duumma_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Duumma/RM_Duumma_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Gaanok/RM_Gaanok_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Gaanok/RM_Gaanok_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Gaanok/RM_Gaanok_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Guzzka/RM_Guzzka_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Guzzka/RM_Guzzka_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Guzzka/RM_Guzzka_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Liikka/RM_Liikka_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Liikka/RM_Liikka_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Liikka/RM_Liikka_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Loomma/RM_Loomma_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Loomma/RM_Loomma_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Loomma/RM_Loomma_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Nizzek/RM_Nizzek_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Nizzek/RM_Nizzek_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Nizzek/RM_Nizzek_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Oommok/RM_Oommok_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Oommok/RM_Oommok_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Oommok/RM_Oommok_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Oorrik/RM_Oorrik_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Oorrik/RM_Oorrik_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Oorrik/RM_Oorrik_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Qorrax/RM_Qorrax_Dessicated_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Qorrax/RM_Qorrax_Dessicated_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Qorrax/RM_Qorrax_Dessicated_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Qorrax/RM_Qorrax_Swimming_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Qorrax/RM_Qorrax_Swimming_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Qorrax/RM_Qorrax_Swimming_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Qorrax/RM_Qorrax_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Qorrax/RM_Qorrax_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Qorrax/RM_Qorrax_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Ruukka/RM_Ruukka_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Ruukka/RM_Ruukka_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Ruukka/RM_Ruukka_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_ShadeMite/RM_ShadeMite_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_ShadeMite/RM_ShadeMite_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_ShadeMite/RM_ShadeMite_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Siidda/RM_Siidda_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Siidda/RM_Siidda_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Siidda/RM_Siidda_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Soorrak/RM_Soorrak_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Soorrak/RM_Soorrak_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Soorrak/RM_Soorrak_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Vaalok/RM_Vaalok_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Vaalok/RM_Vaalok_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Vaalok/RM_Vaalok_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Veessa/RM_Veessa_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Veessa/RM_Veessa_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Veessa/RM_Veessa_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Vekka/RM_Vekka_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Vekka/RM_Vekka_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Vekka/RM_Vekka_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Vozzik/RM_Vozzik_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Vozzik/RM_Vozzik_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Vozzik/RM_Vozzik_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Zuurrik/RM_Zuurrik_east.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Zuurrik/RM_Zuurrik_north.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Zuurrik/RM_Zuurrik_south.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Plant/RM_Glasscrust/RM_GlasscrustA.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Plant/RM_Hourbloom/RM_HourbloomA.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Plant/RM_KneelOllim/RM_KneelOllimA.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Plant/RM_LightPipeNub/RM_LightPipeNubA.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/Textures/Things/Plant/RM_Ollim/RM_OllimA.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/northstar_plan.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/northstar_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/selftest_stillsand.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Stillsand/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/StructureInjections/Assemblies/RimMandrakeStructureInjections.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/StructureInjections/Assemblies/RimMandrakeStructureInjections.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/StructureInjections/Source/GenStep_RimplacePlan.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TerminalBiomes/Assemblies/RimMandrake.TerminalBiomes.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TerminalBiomes/Assemblies/RimMandrake.TerminalBiomes.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TheScald.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Buildings/RM_ChillGrowers.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Buildings/RM_TwilightConstellation.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_TheChillFlora.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TerminalBiomes/Source/RM_Building_CryoGrower.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TerminalBiomes/Source/RM_Patch_ChillGrowers.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TerminalBiomes/Source/RM_PlaceWorker_ChillFloorOnly.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomes.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TerminalBiomes/Textures/Things/Building/Production/RM_ChillCryoponicsVat.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TerminalBiomes/Textures/Things/Building/Production/RM_ChillFloorBed.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TheForge/About/About.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TheForge/Assemblies/RimMandrake.TheForge.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TheForge/Assemblies/RimMandrake.TheForge.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TheForge/Defs/BiomeDefs/RM_TheForge_Biome.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TheForge/Defs/HediffDefs/RM_DhuvvoxRunSlowing.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TheForge/Defs/ResearchProjectDefs/RM_SpunstoneBonding.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TheForge/Defs/SoundDefs/RM_ForgeVoices.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TheForge/Defs/ThingDefs_Buildings/RM_FloatstoneKeelBrace.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TheForge/Defs/ThingDefs_Plants/RM_TheForge_Flora.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TheForge/Defs/ThingDefs_Races/RM_TheForgeNatives.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TheForge/Patches/RM_TheForge_KeelBraceLink.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TheForge/Source/RM_CompForgeCycleDormancy.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TheForge/Source/RM_ForgeCycleDebugActions.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TheForge/Source/RM_ForgeKeelwork.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TheForge/Source/RM_ForgeSpunstone.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TheForge/Source/RM_ForgeVoices.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TheForge/Source/RM_GameCondition_ForgeCycle.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TheForge/Source/RM_TheForge.csproj   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TheForge/Source/RM_TheForgeDefOf.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TheForge/Source/RM_TheForgeMod.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TheForge/northstar_plan.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TheForge/northstar_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TheForge/selftest_theforge.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/TheForge/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TheSump/Assemblies/RimMandrake.TheSump.dll   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TheSump/Assemblies/RimMandrake.TheSump.dll.srchash   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TheSump/Defs/ThingDefs_Races/RM_SumpFauna.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/TheSump/Source/RM_TheSumpBiome.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/game_focus.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/loadsweep/biome_load_proof.sh   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/modcheck/bland_world.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/modcheck/detectors.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/modcheck/helpers.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/modcheck/judge.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/modcheck/live_queue/common.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/modcheck/live_queue/j0_preflight.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/modcheck/live_queue/j1_situational_rerun.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/modcheck/live_queue/j2_abort_proof.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
AM src/RimMandrake/Utils/modcheck/live_queue/j3_bland_tile.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/modcheck/live_queue/j4_companion_live.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/modcheck/live_queue/j5_motion_frames.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/modcheck/live_queue/j6_bland_base.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/modcheck/live_queue/jobs.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
AM src/RimMandrake/Utils/modcheck/live_queue/prep_wsl.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/modcheck/live_queue/run_next.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/modcheck/live_queue/selftest_live_queue.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/modcheck/northstar.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/modcheck/runner.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/modcheck/saved_base.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/modcheck/selftest.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/modcheck/selftest_bland_world.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/modcheck/selftest_companion_detectors.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/modcheck/selftest_detectors.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/modcheck/selftest_motion_frames.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/modcheck/selftest_suite_corrections.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/modcheck/snapshot.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/modcheck/suite.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/modcheck/watch.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/modset_builder.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/northstar_driver/__init__.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/northstar_driver/bars.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/northstar_driver/cli.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/northstar_driver/judge_cli.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/northstar_driver/lint_calls.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/northstar_driver/live_session.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/northstar_driver/preflight.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/northstar_driver/selftest.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/northstar_driver/selftest_judge.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/northstar_driver/selftest_lint_calls.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/northstar_driver/session.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/northstar_driver/site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/northstar_driver/tool_schemas.json   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/northstar_driver/tool_schemas.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/northstar_driver/transport.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/rimbridge_client.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/rimdrive/fake.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/rimdrive/selftest.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/rimdrive/session.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/run_selftests.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/selftest_deployed_biome_refs.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/selftest_precious_caves.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Utils/selftest_sound_paths.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Utils/selftest_track_grid.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Warcasket/Defs/ThingDefs_Apparel/RM_Warcasket.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Warcasket/Defs/ThingDefs_Buildings/RM_CaskBay.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Warcasket/Defs/ThingDefs_Items/RM_HalfExtractedCore.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Warcasket/Textures/Things/Building/RM_CaskBay/RM_CaskBay.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Warcasket/Textures/Things/Item/Resource/RM_HalfExtractedCore/RM_HalfExtractedCore.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Warcasket/northstar_plan.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Warcasket/northstar_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Warcasket/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Wasteland/Defs/BiomeDefs/RM_Wasteland_Biome.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Wasteland/Defs/Quests/RM_RiteOfTipping.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Wasteland/Defs/SoundDefs/RM_WastelandSounds.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Wasteland/Defs/ThingDefs_Plants/RM_WastelandFlora.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Wasteland/northstar_plan.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Wasteland/northstar_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Wasteland/selftest_wasteland.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/Wasteland/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Webwork/Defs/ThingDefs_Races/RM_Ollathrix.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/Webwork/Defs/ThingDefs_Races/RM_WebworkFauna.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/WeepingStones/About/About.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/WeepingStones/Defs/BiomeDefs/RM_WeepingStones_Biome.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/WeepingStones/Defs/ThingDefs_Races/RM_StockedPoolFauna.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/WeepingStones/northstar_plan.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/WeepingStones/northstar_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/WeepingStones/selftest_weepingstones.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/WeepingStones/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchColonyNameTool.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFlowWorksNorthstarTools.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFlowWorksTools.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchInit.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchNorthstarTools.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchShadeGridTools.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSituationalTools.cs   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimStarWars/Armoury/Patches/Armoury_GlareProtection.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimStarWars/Bacta/northstar_mock.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimStarWars/Bacta/northstar_plan.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimStarWars/Bacta/northstar_site.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimStarWars/Bacta/selftest_bacta_mock.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimStarWars/Bacta/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/Cuisine/About/About.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/Droidworks/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/JawaIonWeapons/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/SWBestiary/About/About.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_Maguana.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_Ultracactus.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimStarWars/SWBestiary/Defs/Livestock/PawnKindDefs/PawnKindDefs_Abyss.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/SWBestiary/Defs/Livestock/PawnKindDefs/PawnKindDefs_Karrask.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimStarWars/SWBestiary/Defs/Livestock/ThingDefs_Animals/ThingDefs_Abyss.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/SWBestiary/Defs/Livestock/ThingDefs_Animals/ThingDefs_Moornak.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_NurseryJuveniles.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/SWBestiary/Defs/ShipVermin/ThingDefs_Races/RSW_Mynock.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimStarWars/SWBestiary/Defs/ThingDefs_Buildings/RSW_GiantSkeletons.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_GreaterKraytDragon.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_KraytDragon.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_SandStalker.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/SWBestiary/Defs/ThingSetMakerDefs/RSW_RareSandCatches.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimStarWars/SWBestiary/Patches/Livestock/Abyss_WildSpawns.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimStarWars/SWBestiary/Patches/RSW_GiantSkeletons_Remains.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/SWBestiary/art/Livestock/mockups/PICKS.md   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/SWBestiary/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/Sarlacc/About/About.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/Shokk/About/About.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimStarWars/StarWarsRaces/Patches/RSW_Jawa_GlareAdapted.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/StarWarsRaces/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/StructureInjectionsSW/Defs/TileMutatorDefs_Batch2.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/StructureInjectionsSW/Templates/krayt_graveyard.txt   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimStarWars/StructureInjectionsSW/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/Antiquities/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/EmpirePursuit/About/About.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/EmpirePursuit/Defs/Scenarios/ScenParts_EmpirePursuit.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/EmpirePursuit/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/PawnFlavor/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/Rites/About/About.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/Rites/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/ShipMemory/validation.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/About/About.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/Absorbed_Cephaloids/Absorbed_Cephaloids_Defs.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Abyss.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_AridShrubland.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_BlueDesert.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Cauldron.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Contagion.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_CrackedLands.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_ExtremeDesert.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_FuelSnows.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Greentide.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Miasma.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheForge.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheRot.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Umbra.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Wasteland.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Webwork.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/FactionDefs/JawaHuttCartel.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/HediffDefs/RUT_YearningFruit_Hediffs.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimUtinni/UtinniPatches/Defs/IncidentDefs/RUT_KraytAttack.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/LandmarkDefs/RUT_Lightfall.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/PawnKindDefs/JawaColonistPawnKinds.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/PawnKindDefs/JawaFactionRoster.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimUtinni/UtinniPatches/Defs/PreceptDefs/RUT_TheReturn.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/ScenarioDefs/Scenario_Utinni.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_WastelandBrineDeposits.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_CrackedLandsFish_Items.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_WeepingStonesFish_Items.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_YearningFruit.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_Ashwallow.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_BrineBattery.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_MortuaryCrawler.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_PyrelandsPortedFauna.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_Radiothermal.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_SlimeGrazer.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimUtinni/UtinniPatches/Patches/Abyss_Rename.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Patches/BiomeDescriptions_Ashkarr.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Patches/BiomeFlora_Ashkarr.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Patches/BiomeNames_Ashkarr.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Patches/FishTypesStrip_NoFishBiomes.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Patches/JawaTerrain_HorrorWastes.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Patches/JawaWorld_BiomeMix.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Patches/OasisMutator_DesertOasis.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimUtinni/UtinniPatches/Patches/RUT_TheReturn_KraytOpens.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Patches/SandFishing_CrackedLands.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Patches/WildAnimals_CrackedLands.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Patches/WildAnimals_LongShade.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Patches/WildAnimals_Stillsand.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
M  src/RimUtinni/UtinniPatches/Patches/WildAnimals_Warscar.xml   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
A  src/RimUtinni/UtinniPatches/Textures/Things/Building/RUT_DebtStone/RUT_DebtStone.png   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
?? deployed/config/ModsConfig.before-THEY_MOD_REPLICATION_1-retirement-write.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-baroque_wave0.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-baroque_wave0_control.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-firehawk.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-greentideant.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-leaningscrub.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-luminouspigment.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_bluedesert.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_contagion.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_feverwood.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_floodedcanyon.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_forsakencrags.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_gelatinousslime.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_greentide.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_leaningscrub.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_longshade.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_miasma.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_nightsideice.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_poisonforest.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_pyrelands.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_rustcathedral.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_stillsand.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_terminalbiomes.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_theforge.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_therot.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_thesump.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_wasteland.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_webwork.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-proof_weepingstones.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   BENCH's design work (not mine)
?? deployed/config/ModsConfig.pre-ns-graffiti.20261001.xml   BENCH's design work (not mine)
?? design/RimMandrake/git_workflow_fix_2026-10-01.md   a subagent or peer window (already published or not mine)
?? done.flag   a subagent or peer window (already published or not mine)
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Gennok_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Gennok_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Gennok_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Gennok_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Gennok_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Gennok_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Sollak_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Sollak_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Sollak_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Sollak_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Sollak_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Sollak_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/active/RM_Kethrel_Stage3_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_AblationSilhouette.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_AblationSilhouette.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_AbyssSalvageCache.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_AbyssSalvageCache.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_AbyssStockedDen.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_AbyssStockedDen.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_AerosolScreen.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_AerosolScreen.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_AncientServitor_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_AncientServitor_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_AncientServitor_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_AncientServitor_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_AncientServitor_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_AncientServitor_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Aurrok_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Aurrok_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Aurrok_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Aurrok_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Aurrok_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Aurrok_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Biosilica.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Biosilica.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Bleedleaf.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Bleedleaf.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Blinker_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Blinker_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Blinker_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Blinker_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Blinker_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Blinker_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Blisterfloat_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Blisterfloat_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Blisterfloat_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Blisterfloat_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Blisterfloat_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Blisterfloat_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Bloodlurk_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Bloodlurk_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Bloodlurk_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Bloodlurk_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Bloodlurk_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Bloodlurk_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BloodyFist.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BloodyFist.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BloodyMess_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BloodyMess_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BloodyMess_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BloodyMess_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BloodyMess_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BloodyMess_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BloodyMess_v2_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BloodyMess_v2_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BloodyMess_v2_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BloodyMess_v2_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BloodyMess_v2_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BloodyMess_v2_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BloomLiquor.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BloomLiquor.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BlueIce.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BlueIce.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BlueIceMeltwaterCan.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BlueIceMeltwaterCan.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Boilbulb.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Boilbulb.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Boilhide_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Boilhide_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Boilhide_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Boilhide_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Boilhide_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Boilhide_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Boilhide_v2_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Boilhide_v2_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Boilhide_v2_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Boilhide_v2_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Boilhide_v2_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Boilhide_v2_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BrinePlate.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BrinePlate.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BuriedOrdnance.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_BuriedOrdnance.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Candler_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Candler_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Candler_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Candler_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Candler_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Candler_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CaskBay.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CaskBay.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CauldronVent.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CauldronVent.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ChassisCore.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ChassisCore.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ChatrakPlatesLifted_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ChatrakPlatesLifted_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ChatrakPlatesLifted_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ChatrakPlatesLifted_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ChatrakPlatesLifted_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ChatrakPlatesLifted_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chatrak_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chatrak_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chatrak_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chatrak_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chatrak_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chatrak_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ChillCryoponicsVat.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ChillCryoponicsVat.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ChillFloorBed.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ChillFloorBed.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chiller_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chiller_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chiller_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chiller_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chiller_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chiller_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ChorusMass.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ChorusMass.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chotrix_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chotrix_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chotrix_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chotrix_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chotrix_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Chotrix_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Cinderfelt.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Cinderfelt.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Cleaver_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Cleaver_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Cleaver_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Cleaver_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Cleaver_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Cleaver_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CloudRepulsor.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CloudRepulsor.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CloudRepulsor_v2.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CloudRepulsor_v2.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ColdSinkRack.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ColdSinkRack.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ContaminantBezoar.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ContaminantBezoar.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CorrodedCondenserStack.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CorrodedCondenserStack.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CorrodedShrine.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CorrodedShrine.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CorrodedWellhead.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CorrodedWellhead.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CrackWaxSuit.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CrackWaxSuit.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CreepCrust.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CreepCrust.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CrestPlate.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CrestPlate.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Crispling_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Crispling_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Crispling_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Crispling_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Crispling_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Crispling_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CrownVenomvine.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_CrownVenomvine.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Cruststar.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Cruststar.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Crustweevil_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Crustweevil_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Crustweevil_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Crustweevil_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Crustweevil_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Crustweevil_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dakkra_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dakkra_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dakkra_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dakkra_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dakkra_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dakkra_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Danglemaw_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Danglemaw_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Danglemaw_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Danglemaw_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Danglemaw_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Danglemaw_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DebtStone.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DebtStone.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dewfringe.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dewfringe.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DewfringeSprig.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DewfringeSprig.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DhokkurDormant.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DhokkurDormant.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhokkur_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhokkur_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhokkur_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhokkur_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhokkur_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhokkur_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhorrumak_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhorrumak_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhorrumak_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhorrumak_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhorrumak_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhorrumak_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DhuvvoxNodule.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DhuvvoxNodule.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhuvvox_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhuvvox_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhuvvox_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhuvvox_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhuvvox_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dhuvvox_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DielectricGel.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DielectricGel.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Doublemaw_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Doublemaw_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Doublemaw_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Doublemaw_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Doublemaw_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Doublemaw_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drazz.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drazz.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drazzik_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drazzik_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drazzik_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drazzik_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drazzik_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drazzik_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drifter_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drifter_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drifter_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drifter_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drifter_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drifter_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DrippingVenomvine.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DrippingVenomvine.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drokattak_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drokattak_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drokattak_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drokattak_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drokattak_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Drokattak_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DurrgakCairn.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DurrgakCairn.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Durrgak_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Durrgak_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Durrgak_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Durrgak_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Durrgak_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Durrgak_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DuskRat_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DuskRat_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DuskRat_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DuskRat_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DuskRat_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DuskRat_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DustDevil.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_DustDevil.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dustflutter_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dustflutter_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dustflutter_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dustflutter_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dustflutter_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Dustflutter_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Duumma_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Duumma_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Duumma_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Duumma_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Duumma_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Duumma_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eskith_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eskith_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eskith_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eskith_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eskith_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eskith_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eskith_v2_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eskith_v2_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eskith_v2_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eskith_v2_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eskith_v2_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eskith_v2_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Etchant.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Etchant.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Etchcap.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Etchcap.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_EtchcapCap.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_EtchcapCap.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eyebark.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eyebark.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eyebark_v2.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eyebark_v2.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eyestinger_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eyestinger_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eyestinger_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eyestinger_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eyestinger_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Eyestinger_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FE_Fulgurite_real.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FE_Fulgurite_real.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FailedChassis.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FailedChassis.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FilterCartridge.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FilterCartridge.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FilterWorks.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FilterWorks.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_DisturbedSand.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_DisturbedSand.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_DragMark.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_DragMark.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_EruptionScar.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_EruptionScar.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_GlasscrustScar.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_GlasscrustScar.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_MiddenshellFlakes.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_MiddenshellFlakes.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_MiddenshellFootprint.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_MiddenshellFootprint.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_OommokPrint.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_OommokPrint.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_SandWake.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_SandWake.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_SettledFilm.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_SettledFilm.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_Tholin.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Filth_Tholin.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fleshsop_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fleshsop_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fleshsop_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fleshsop_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fleshsop_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fleshsop_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fleshsop_v2_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fleshsop_v2_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fleshsop_v2_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fleshsop_v2_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fleshsop_v2_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fleshsop_v2_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Floatstone.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Floatstone.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FloatstoneGarden.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FloatstoneGarden.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FoldLamp_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FoldLamp_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FoldLamp_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FoldLamp_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FoldLamp_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FoldLamp_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FossilDeepStratum.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FossilDeepStratum.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FossilDisplayMount.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FossilDisplayMount.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FossilDisplaySlab.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FossilDisplaySlab.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FossilImpression.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FossilImpression.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FossilSeam.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FossilSeam.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FossilSkeleton.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FossilSkeleton.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FossilSkeleton_v2.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FossilSkeleton_v2.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Frissim_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Frissim_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Frissim_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Frissim_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Frissim_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Frissim_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FurnaceBeast_Giant_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FurnaceBeast_Giant_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FurnaceBeast_Giant_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FurnaceBeast_Giant_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FurnaceBeast_Giant_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_FurnaceBeast_Giant_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fuzzrunner_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fuzzrunner_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fuzzrunner_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fuzzrunner_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fuzzrunner_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fuzzrunner_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fuzzviper_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fuzzviper_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fuzzviper_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fuzzviper_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fuzzviper_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Fuzzviper_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gaanok_b_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gaanok_b_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gaanok_b_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gaanok_b_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gaanok_b_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gaanok_b_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gaanok_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gaanok_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gaanok_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gaanok_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gaanok_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gaanok_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Galuush_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Galuush_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Galuush_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Galuush_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Galuush_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Galuush_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GasTapScaffold.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GasTapScaffold.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gawpsack_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gawpsack_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gawpsack_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gawpsack_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gawpsack_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gawpsack_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gennok_b_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gennok_b_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gennok_b_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gennok_b_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gennok_b_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gennok_b_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gennok_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gennok_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gennok_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gennok_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gennok_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gennok_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Geophone.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Geophone.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gharrek_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gharrek_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gharrek_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gharrek_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gharrek_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gharrek_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GillAsh.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GillAsh.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GlassSand.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GlassSand.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Glasscrust.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Glasscrust.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gloomcast_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gloomcast_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gloomcast_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gloomcast_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gloomcast_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gloomcast_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GlowerPlate.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GlowerPlate.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GlowerShieldPanel.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GlowerShieldPanel.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gnashling_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gnashling_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gnashling_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gnashling_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gnashling_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gnashling_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gorekite_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gorekite_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gorekite_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gorekite_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gorekite_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gorekite_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gorestalk.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gorestalk.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gravelgut_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gravelgut_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gravelgut_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gravelgut_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gravelgut_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gravelgut_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GreatDevourer_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GreatDevourer_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GreatDevourer_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GreatDevourer_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GreatDevourer_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GreatDevourer_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Grimewing_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Grimewing_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Grimewing_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Grimewing_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Grimewing_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Grimewing_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Grimewing_v2_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Grimewing_v2_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Grimewing_v2_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Grimewing_v2_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Grimewing_v2_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Grimewing_v2_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gristleswarm_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gristleswarm_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gristleswarm_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gristleswarm_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gristleswarm_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gristleswarm_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gristleswarm_v2_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gristleswarm_v2_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gristleswarm_v2_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gristleswarm_v2_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gristleswarm_v2_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Gristleswarm_v2_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Groundrunner_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Groundrunner_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Groundrunner_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Groundrunner_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Groundrunner_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Groundrunner_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GuzzkaSkeleton.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_GuzzkaSkeleton.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Guzzka_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Guzzka_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Guzzka_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Guzzka_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Guzzka_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Guzzka_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_HalfExtractedCore.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_HalfExtractedCore.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_HalfmadeTree.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_HalfmadeTree.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_HalfmadeTreeBlighted.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_HalfmadeTreeBlighted.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hazebell.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hazebell.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hazebell_Open.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hazebell_Open.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hessarund.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hessarund.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hoarfrost_BladeGrowth.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hoarfrost_BladeGrowth.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hoarfrost_CrystalGarden.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hoarfrost_CrystalGarden.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hoarfrost_DepthHoarColumn.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hoarfrost_DepthHoarColumn.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hoarfrost_FrostFlower.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hoarfrost_FrostFlower.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_HollowVenomvine.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_HollowVenomvine.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_HospiceCradle.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_HospiceCradle.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hourbloom.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hourbloom.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hush_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hush_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hush_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hush_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hush_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Hush_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ikee_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ikee_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ikee_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ikee_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ikee_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ikee_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_InscribedPanel_ChalkMark.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_InscribedPanel_ChalkMark.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_InscribedPanel_Hospice.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_InscribedPanel_Hospice.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_InscribedPanel_Pool.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_InscribedPanel_Pool.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_InscribedPanel_Projector.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_InscribedPanel_Projector.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Irqit_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Irqit_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Irqit_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Irqit_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Irqit_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Irqit_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Jossur_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Jossur_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Jossur_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Jossur_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Jossur_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Jossur_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Julmox_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Julmox_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Julmox_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Julmox_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Julmox_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Julmox_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage0_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage0_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage0_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage0_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage0_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage0_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage1_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage1_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage1_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage1_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage1_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage1_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage2_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage2_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage2_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage2_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage2_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kethrel_Stage2_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Khorrak_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Khorrak_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Khorrak_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Khorrak_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Khorrak_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Khorrak_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_KneelOllim.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_KneelOllim.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_KneelOllim_b.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_KneelOllim_b.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_KneelingChassis_Intact.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_KneelingChassis_Intact.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_KneelingChassis_Posed.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_KneelingChassis_Posed.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_KneelingChassis_Slagged.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_KneelingChassis_Slagged.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Knocker_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Knocker_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Knocker_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Knocker_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Knocker_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Knocker_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krannock_v1_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krannock_v1_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krannock_v1_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krannock_v1_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krannock_v1_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krannock_v1_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_1_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_1_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_1_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_1_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_1_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_1_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_2_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_2_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_2_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_2_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_2_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_2_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_3_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_3_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_3_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_3_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_3_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_3_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_4_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_4_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_4_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_4_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_4_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_4_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_5_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_5_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_5_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_5_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_5_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_Flying_5_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Krizzak_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kudda_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kudda_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kudda_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kudda_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kudda_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Kudda_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Lantern.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Lantern.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashA_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashA_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashA_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashA_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashA_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashA_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashB_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashB_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashB_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashB_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashB_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashB_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashC_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashC_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashC_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashC_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashC_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LashC_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Lashgrass.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Lashgrass.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LensSand.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LensSand.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LightningBreaker.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LightningBreaker.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Liikka_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Liikka_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Liikka_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Liikka_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Liikka_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Liikka_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Longglass.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Longglass.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Loomma_b_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Loomma_b_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Loomma_b_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Loomma_b_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Loomma_b_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Loomma_b_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Loomma_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Loomma_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Loomma_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Loomma_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Loomma_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Loomma_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LoosenedPanel.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_LoosenedPanel.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Maidenbloom.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Maidenbloom.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_MatureFleshbeast_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_MatureFleshbeast_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_MatureFleshbeast_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_MatureFleshbeast_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_MatureFleshbeast_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_MatureFleshbeast_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Meatvine.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Meatvine.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_MedicalCoagulant.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_MedicalCoagulant.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Meltgut_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Meltgut_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Meltgut_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Meltgut_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Meltgut_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Meltgut_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenbeetle_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenbeetle_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenbeetle_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenbeetle_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenbeetle_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenbeetle_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_MiddenshellEdgeScar.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_MiddenshellEdgeScar.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_MiddenshellTrack.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_MiddenshellTrack.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenshell_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenshell_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenshell_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenshell_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenshell_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenshell_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenshell_v2_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenshell_v2_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenshell_v2_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenshell_v2_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenshell_v2_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Middenshell_v2_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Milelace.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Milelace.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Mirrak_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Mirrak_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Mirrak_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Mirrak_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Mirrak_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Mirrak_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Murrek_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Murrek_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Murrek_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Murrek_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Murrek_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Murrek_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Muttavaq_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Muttavaq_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Muttavaq_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Muttavaq_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Muttavaq_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Muttavaq_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Muttavaq_v2_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Muttavaq_v2_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_MuurrokSkeleton.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_MuurrokSkeleton.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Muurrok_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Muurrok_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Muurrok_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Muurrok_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Muurrok_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Muurrok_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Nizzek_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Nizzek_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Nizzek_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Nizzek_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Nizzek_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Nizzek_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_OldLineTurret_Base.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_OldLineTurret_Base.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_OldLineTurret_Top.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_OldLineTurret_Top.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ommok_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ommok_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ommok_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ommok_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ommok_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ommok_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_OommokSkeleton.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_OommokSkeleton.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Oorrik_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Oorrik_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Oorrik_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Oorrik_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Oorrik_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Oorrik_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Orruhmu_b_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Orruhmu_b_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Orruhmu_b_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Orruhmu_b_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Orruhmu_b_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Orruhmu_b_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Orruhmu_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Orruhmu_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Orruhmu_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Orruhmu_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Orruhmu_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Orruhmu_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_OrunGhal_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_OrunGhal_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_OrunGhal_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_OrunGhal_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_OrunGhal_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_OrunGhal_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ossik_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ossik_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ossik_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ossik_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ossik_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ossik_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ossivel_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ossivel_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ossivel_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ossivel_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ossivel_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ossivel_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Parasol.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Parasol.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pavecrust.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pavecrust.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PearlLens.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PearlLens.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Peeper_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Peeper_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Peeper_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Peeper_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Peeper_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Peeper_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PillarArmA_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PillarArmA_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PillarArmA_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PillarArmA_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PillarArmA_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PillarArmA_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PillarArmB_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PillarArmB_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PillarArmB_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PillarArmB_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PillarArmB_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PillarArmB_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pillowmoss.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pillowmoss.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pirrik_b_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pirrik_b_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pirrik_b_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pirrik_b_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pirrik_b_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pirrik_b_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pirrik_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pirrik_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pirrik_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pirrik_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pirrik_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pirrik_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PoolPhaseIcon_Amber.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PoolPhaseIcon_Amber.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PoolPhaseIcon_Bloom.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PoolPhaseIcon_Bloom.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PoolPhaseIcon_Green.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PoolPhaseIcon_Green.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PoolPhaseIcon_Violet.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PoolPhaseIcon_Violet.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pooler_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pooler_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pooler_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pooler_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pooler_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pooler_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PrecisionLens.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_PrecisionLens.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ProjectorCore.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ProjectorCore.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pusberry.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Pusberry.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Qorrax_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Qorrax_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Qorrax_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Qorrax_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Qorrax_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Qorrax_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Rattlegrope.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Rattlegrope.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_RawVenom.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_RawVenom.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ReactionTap.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ReactionTap.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ribbonwhip_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ribbonwhip_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ribbonwhip_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ribbonwhip_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ribbonwhip_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ribbonwhip_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Rollbug_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Rollbug_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Rollbug_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Rollbug_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Rollbug_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Rollbug_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ruukka_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ruukka_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ruukka_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ruukka_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ruukka_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ruukka_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SandBusterMound_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SandBusterMound_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SandSieve.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SandSieve.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sapblister.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sapblister.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scabspinner_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scabspinner_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scabspinner_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scabspinner_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scabspinner_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scabspinner_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scaldhide_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scaldhide_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scaldhide_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scaldhide_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scaldhide_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scaldhide_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scorchpod_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scorchpod_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scorchpod_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scorchpod_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scorchpod_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scorchpod_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scumgrass.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scumgrass.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scumrat_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scumrat_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scumrat_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scumrat_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scumrat_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scumrat_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scumslider_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scumslider_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scumslider_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scumslider_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scumslider_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Scumslider_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SealedWaterJar.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SealedWaterJar.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Seismograph.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Seismograph.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Seismograph_v2.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Seismograph_v2.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ShadeTent.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ShadeTent.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shadespire.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shadespire.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shambles_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shambles_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shambles_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shambles_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shambles_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shambles_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ShardMind.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ShardMind.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shirrel_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shirrel_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shirrel_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shirrel_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shirrel_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shirrel_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ShivvenTell.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_ShivvenTell.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shivven_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shivven_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shivven_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shivven_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shivven_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shivven_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shoal_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shoal_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shoal_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shoal_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shoal_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shoal_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shokka_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shokka_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shokka_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shokka_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shokka_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Shokka_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sipper_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sipper_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sipper_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sipper_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sipper_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sipper_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sippra_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sippra_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sippra_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sippra_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sippra_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sippra_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Skarrok_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Skarrok_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Skarrok_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Skarrok_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Skarrok_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Skarrok_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Skinflap_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Skinflap_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Skinflap_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Skinflap_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Skinflap_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Skinflap_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slagmole_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slagmole_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slagmole_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slagmole_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slagmole_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slagmole_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slagmole_v2_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slagmole_v2_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slagmole_v2_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slagmole_v2_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slagmole_v2_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slagmole_v2_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slick_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slick_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slick_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slick_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slick_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Slick_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloghog_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloghog_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloghog_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloghog_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloghog_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloghog_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloghog_v2_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloghog_v2_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloghog_v2_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloghog_v2_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloghog_v2_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloghog_v2_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloshbelly_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloshbelly_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloshbelly_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloshbelly_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloshbelly_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sloshbelly_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Smolderback_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Smolderback_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Smolderback_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Smolderback_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Smolderback_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Smolderback_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sohl_Dormant.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sohl_Dormant.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sohl_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sohl_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sohl_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sohl_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sohl_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sohl_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SolarOven.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SolarOven.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SolarStill.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SolarStill.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sollak_b_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sollak_b_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sollak_b_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sollak_b_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sollak_b_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sollak_b_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sollak_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sollak_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sollak_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sollak_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sollak_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sollak_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Soorrak_b_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Soorrak_b_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Soorrak_b_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Soorrak_b_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Soorrak_b_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Soorrak_b_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Soorrak_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Soorrak_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Soorrak_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Soorrak_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Soorrak_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Soorrak_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SootBrick.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SootBrick.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SootGristleswarm_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SootGristleswarm_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SootGristleswarm_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SootGristleswarm_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SootGristleswarm_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SootGristleswarm_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sootgrazer_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sootgrazer_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sootgrazer_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sootgrazer_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sootgrazer_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sootgrazer_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SparkleechGrub_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SparkleechGrub_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SparkleechGrub_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SparkleechGrub_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SparkleechGrub_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SparkleechGrub_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sparkleech_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sparkleech_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sparkleech_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sparkleech_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sparkleech_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sparkleech_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_StruckGlassRing.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_StruckGlassRing.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Summ_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Summ_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Summ_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Summ_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Summ_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Summ_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Summing_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Summing_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Summing_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Summing_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Summing_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Summing_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SunFurnace.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SunFurnace.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SunGlass.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SunGlass.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SunGoggles.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SunGoggles.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SunGogglesWorn_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SunGogglesWorn_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SunGogglesWorn_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SunGogglesWorn_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SunGogglesWorn_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SunGogglesWorn_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SunLance_Base.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SunLance_Base.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SunLance_Top.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_SunLance_Top.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sunbeam.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Sunbeam.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Surrik_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Surrik_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Surrik_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Surrik_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Surrik_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Surrik_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Swale.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Swale.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Swale_v2.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Swale_v2.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TallScumgrass.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TallScumgrass.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tanglefuzz.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tanglefuzz.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tapper_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tapper_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tapper_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tapper_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tapper_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tapper_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TarBeast_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TarBeast_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TarBeast_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TarBeast_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TarBeast_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TarBeast_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tarruq_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tarruq_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tarruq_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tarruq_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tarruq_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tarruq_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tazzok_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tazzok_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tazzok_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tazzok_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tazzok_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tazzok_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tebbra_b_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tebbra_b_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tebbra_b_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tebbra_b_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tebbra_b_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tebbra_b_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tebbra_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tebbra_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tebbra_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tebbra_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tebbra_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tebbra_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tekk.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tekk.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TetchikJar.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TetchikJar.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tetchik_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tetchik_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tetchik_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tetchik_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tetchik_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tetchik_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tholin.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tholin.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Thornhold_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Thornhold_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Thornhold_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Thornhold_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Thornhold_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Thornhold_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Thumper.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Thumper.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Thurra_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Thurra_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Thurra_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Thurra_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Thurra_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Thurra_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tikkit_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tikkit_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tikkit_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tikkit_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tikkit_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Tikkit_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Toothmoss.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Toothmoss.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TotchakDormant.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TotchakDormant.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Totchak_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Totchak_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Totchak_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Totchak_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Totchak_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Totchak_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TrackDrag.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TrackDrag.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TrackPrint_Animal.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TrackPrint_Animal.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TrackPrint_Human.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TrackPrint_Human.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TrackPrint_Large.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TrackPrint_Large.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TruffleMole_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TruffleMole_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TruffleMole_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TruffleMole_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TruffleMole_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TruffleMole_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TwitcherVenomvine.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_TwitcherVenomvine.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ulgga_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ulgga_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ulgga_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ulgga_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ulgga_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ulgga_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ullai_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ullai_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ullai_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ullai_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ullai_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Ullai_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_UltracactusPad.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_UltracactusPad.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Uttaqar_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Uttaqar_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Uttaqar_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Uttaqar_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Uttaqar_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Uttaqar_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Veessa_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Veessa_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Veessa_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Veessa_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Veessa_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Veessa_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vekka_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vekka_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vekka_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vekka_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vekka_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vekka_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_VenomvineThicket_v2.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_VenomvineThicket_v2.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Veqma.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Veqma.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vexxiss_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vexxiss_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vexxiss_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vexxiss_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vexxiss_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vexxiss_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vexxiss_v2_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vexxiss_v2_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vexxiss_v2_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vexxiss_v2_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vexxiss_v2_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vexxiss_v2_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vexxith.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vexxith.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vhaulk_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vhaulk_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vhaulk_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vhaulk_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vhaulk_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vhaulk_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vhaulk_v2_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vhaulk_v2_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Virr.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Virr.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_VisslerArm.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_VisslerArm.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vissler_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vissler_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vissler_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vissler_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vissler_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vissler_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_VitrifiedBezoar.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_VitrifiedBezoar.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vosska_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vosska_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vosska_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vosska_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vosska_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vosska_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_VozzikSkeleton.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_VozzikSkeleton.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vozzik_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vozzik_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vozzik_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vozzik_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vozzik_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vozzik_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vrekka_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vrekka_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vrekka_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vrekka_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vrekka_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Vrekka_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WarDust.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WarDust.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Warcasket.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Warcasket.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WarcasketJunker.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WarcasketJunker.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WarscarProjector_Dead.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WarscarProjector_Dead.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WarscarProjector_Live.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WarscarProjector_Live.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Wartshrub.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Wartshrub.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WasteCask.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WasteCask.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WasteTippingPad.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WasteTippingPad.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Whipfuzz.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Whipfuzz.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Wombpod.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Wombpod.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WorkingDead_Slumped.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WorkingDead_Slumped.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WorkingDead_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WorkingDead_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WorkingDead_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WorkingDead_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WorkingDead_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WorkingDead_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WreckLichen.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WreckLichen.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WreckLichenScrapings.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WreckLichenScrapings.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WreckedCart.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_WreckedCart.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Wyrmlet_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Wyrmlet_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Wyrmlet_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Wyrmlet_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Wyrmlet_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Wyrmlet_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Xithess.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Xithess.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Zellik_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Zellik_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Zellik_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Zellik_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Zellik_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Zellik_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Zisska_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Zisska_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Zisska_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Zisska_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Zisska_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RM_Zisska_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RSW_CrawlerTreadWreck.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RSW_CrawlerTreadWreck.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RSW_Filth_CrawlerTread.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RSW_Filth_CrawlerTread.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RSW_GreaterKraytSkeleton.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RSW_GreaterKraytSkeleton.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RSW_KraytHorn.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RSW_KraytHorn.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RSW_KraytLens.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RSW_KraytLens.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RSW_KraytSkeleton.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RSW_KraytSkeleton.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RSW_WarWyrmSkeleton.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RSW_WarWyrmSkeleton.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RSW_WreckedSkiff.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RSW_WreckedSkiff.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_AncientAirlock.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_AncientAirlock.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_AncientAirlock_Large.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_AncientAirlock_Large.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_AncientFloorHeater.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_AncientFloorHeater.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_AncientLandmine.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_AncientLandmine.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_AncientShieldedTurret.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_AncientShieldedTurret.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_AncientShipLandingBeacon.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_AncientShipLandingBeacon.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_AncientSpacerAutocannon.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_AncientSpacerAutocannon.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_AncientTransmitterBeacon.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_AncientTransmitterBeacon.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_BroodBone.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_BroodBone.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_BroodRibArch.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_BroodRibArch.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_BustedShieldedTurret.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_BustedShieldedTurret.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_BustedSpacerAutocannon.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_BustedSpacerAutocannon.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_CrackWax.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_CrackWax.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_ForcedAncientAirlock.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_ForcedAncientAirlock.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_ForcedAncientAirlock_Large.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_ForcedAncientAirlock_Large.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_FoundrySalvageCache.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_FoundrySalvageCache.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_FoundryTowerEntrance.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_FoundryTowerEntrance.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_FrozenEmptyCryptosleepPod.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_FrozenEmptyCryptosleepPod.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_GreatBone.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_GreatBone.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_JammedAncientAirlock.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_JammedAncientAirlock.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_JammedAncientAirlock_Large.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_JammedAncientAirlock_Large.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_Mindstone.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_Mindstone.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_PilgrimJournal.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_PilgrimJournal.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_SummAllRender_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_SummAllRender_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_SummAllRender_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_SummAllRender_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_SummAllRender_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_SummAllRender_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_SummEgg.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_SummEgg.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_TibannaGas.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_TibannaGas.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_WallWreckHull.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_WallWreckHull.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_WreckDebris.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/RUT_WreckDebris.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_eldspar.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_eldspar.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_fuselight.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_fuselight.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_ghostpane.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_ghostpane.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_keelgrass.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_keelgrass.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_pitchpearl.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_pitchpearl.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_skyharp.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_skyharp.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_slackwax.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_slackwax.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_stillbloom.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_stillbloom.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_stonewater.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_stonewater.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_tarspool.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/chill_plant_tarspool.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/coalescence_stage1.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/coalescence_stage1.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/coalescence_stage2.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/coalescence_stage2.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/coalescence_stage2_v2.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/coalescence_stage2_v2.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/coalescence_stage3.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/coalescence_stage3.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/coalescence_stage3_v2.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/coalescence_stage3_v2.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rm_chillauroracollector_v1.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rm_chillauroracollector_v1.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rmshademite_v2_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rmshademite_v2_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rmshademite_v2_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rmshademite_v2_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rmshademite_v2_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rmshademite_v2_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_blurrg_v1_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_blurrg_v1_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_blurrg_v1_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_blurrg_v1_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_blurrg_v1_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_blurrg_v1_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_blurrg_v2_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_blurrg_v2_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_blurrg_v2_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_blurrg_v2_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_blurrg_v2_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_blurrg_v2_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_scrapnestbird_v1_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_scrapnestbird_v1_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_scrapnestbird_v1_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_scrapnestbird_v1_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_scrapnestbird_v1_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_scrapnestbird_v1_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_shrublandgiant_v1_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_shrublandgiant_v1_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_shrublandgiant_v1_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_shrublandgiant_v1_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_shrublandgiant_v1_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_shrublandgiant_v1_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_tunnelsnake_v1_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_tunnelsnake_v1_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_tunnelsnake_v1_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_tunnelsnake_v1_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_tunnelsnake_v1_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rsw_tunnelsnake_v1_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rut_greentideant_carapacewall_atlas.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rut_greentideant_carapacewall_atlas.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rut_greentideant_carapacewall_menuicon.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/done/rut_greentideant_carapacewall_menuicon.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_LensBench_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_LensBench_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_LensBench_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_LensBench_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_LensBench_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_LensBench_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_ParasolWorn_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_ParasolWorn_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_ParasolWorn_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_ParasolWorn_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_ParasolWorn_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_ParasolWorn_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_SunShield_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_SunShield_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_SunShield_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_SunShield_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_SunShield_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_SunShield_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_WasteCaskBay_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_WasteCaskBay_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_WasteCaskBay_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_WasteCaskBay_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_WasteCaskBay_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RM_WasteCaskBay_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_Off_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_Off_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_Off_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_Off_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_Off_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_Off_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientBlackBox_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientWargamingTable_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientWargamingTable_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientWargamingTable_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientWargamingTable_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientWargamingTable_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_AncientWargamingTable_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_BlueprintsBench_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_BlueprintsBench_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_BlueprintsBench_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_BlueprintsBench_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_BlueprintsBench_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_BlueprintsBench_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminalBank_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminalBank_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminalBank_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminalBank_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminalBank_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminalBank_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminal_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminal_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminal_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminal_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminal_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_CryptoAncientTerminal_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_RuinedHospitalBed_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_RuinedHospitalBed_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_RuinedHospitalBed_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_RuinedHospitalBed_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_RuinedHospitalBed_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/RUT_RuinedHospitalBed_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/rmshademite_v1_east.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/rmshademite_v1_east.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/rmshademite_v1_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/rmshademite_v1_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/rmshademite_v1_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/rmshademite_v1_south.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/rsw_blurrg_v2_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/failed/rsw_blurrg_v2_north.manifest.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/pending/RM_CapstanTurret_Base.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/pending/RM_CapstanTurret_Top.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/pending/RM_Kethrel_Stage3_north.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/artpipe/pending/RM_Kethrel_Stage3_south.json   the artpipe daemon (runtime churn, not mine)
?? infrastructure/dashboards/hub/tabs/maturity.html   the health publisher (regenerated, not mine)
?? infrastructure/dashboards/hub/utinni_control_room_standalone.html   the health publisher (regenerated, not mine)
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   a subagent or peer window (already published or not mine)
?? infrastructure/state/items/closed/NORTHSTAR_MOTION_FRAMES_1.md   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
?? infrastructure/state/logs/harvested/   a subagent or peer window (already published or not mine)
?? infrastructure/state/modlists/ModsConfig.FULL.PRECAPTURE.20260926_142047.xml   a subagent or peer window (already published or not mine)
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   a subagent or peer window (already published or not mine)
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   a subagent or peer window (already published or not mine)
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   a subagent or peer window (already published or not mine)
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_restoring_seashores_bacta_2026-09-25T175356.xml   a subagent or peer window (already published or not mine)
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_seashores_enable_2026-09-25T133443.xml   a subagent or peer window (already published or not mine)
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   a subagent or peer window (already published or not mine)
?? infrastructure/state/modlists/ModsConfig_before_miasma_predation_proof_2026-09-27.xml   a subagent or peer window (already published or not mine)
?? infrastructure/state/modlists/ModsConfig_before_pits_off_2026-09-30T235855.xml   a subagent or peer window (already published or not mine)
?? infrastructure/state/rescued/LanternDeeps_RUT/Assemblies/   a subagent or peer window (already published or not mine)
?? publish   a subagent or peer window (already published or not mine)
?? src/RimMandrake/Utils/firehawk_flight_probe.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
?? src/RimMandrake/Utils/publish.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
?? src/RimMandrake/Utils/selftest_publish.py   staged upstream content from this window's `git checkout origin/main -- src` sync + my northstar subagents; already on origin/main, not unpublished work
```

