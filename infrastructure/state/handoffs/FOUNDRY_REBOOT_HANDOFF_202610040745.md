# FOUNDRY_REBOOT_HANDOFF_202610040745 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202610040002`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
A 20-hour full-belt session (1 bridge agent + art pipe + 1 offline builder, defined in `infrastructure/agents/FOUNDRY.md` "Full belt") built ~250 items offline and proved almost none live: **required checks proven = 28 of 1690, owner bars 0 of 57** (the owner-ruled lead metric; `python3 src/RimMandrake/Utils/modcheck/required_checks_report.py`). The bottleneck is not building, it is validity of live runs: stale deploys (builders rebuild DLLs after each deploy), open modals, a log-blind session, and the unexplained 'Cut by nobody' 1.0 Cut every ~120 ticks on bland-world colonists (66 events, 6 mods) that leaves checks UNMEASURED. Next seat: deploy once, freeze DLL rebuilds, run the suites clean, read the new call-site stacks.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Decisions that unblock ~40 items: `Transient/owner_unblock_list_20261003.md` (Forge, Cracked Lands, Long Shade sittings; map-gen sheets; art sheets with agent prefill; salvation rites; Greentide illisk; quick picks). Answered 2026-10-03 by card: headline = required checks proven; provisional numbers OK; vanilla audio final; woolamander walking resident.
- New questions: may Sanguophage stay as an unreachable definition (Biotech binds to it)? Cut the 32 extra non-Star-Wars xenotypes (`NONSW_XENOTYPES_SCOPE_1`)? Five of our Inhabited characters are Hussar/Yttakin (`VANILLA_XENOTYPE_DEFCUT_1`).
- Art for his eye: `D:\Luke\dev\RimMandrake\Transient\owner_look_list_20261003.md` (Loohn south view; LongShade/Foundry/Dredgel newer renders).
- Numbers FOUNDRY chose that he may veto (all marked PROVISIONAL in items/tooltips): spike damage ~40, pit covers, Sump living-map pacing, Forge swarm 60, choir/fire-stamp constants, Chill dive 3, cartel quest weight 0.15, Gizka stage thresholds.
- Real content bug fixed: kurreth/Shokk hidden factions had no name maker, so no kurreth raid could ever arrive (fix not yet proven live).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `LOAD_15` — game was cold-loading at 00:42 (launched 00:23), bridge now FREE; NEXT: wait for 'Bridge token:' in Player.log, `rimflow bridge take`, then run `python3 Transient/belt_setbg.py` and the watchdog
- `CUT_BY_NOBODY_SOURCE` — companion now records a call-site stack per instigator-less damage hit; NEXT: run `situational_rerun.py --bland-world --retile --mods FeverWood` under python.exe and read the origin stacks in the surprise sidecars (also proves the kurreth faction fix, ProofRaid, ant_theft)
- `RERUNS_OWED` — tainted and never-rerun suites plus ~25 new proofs (MovingDunes, RaidRedesigner, SeaShores, RustChrome, RestrainingBolts, GravshipLanding, Sump living map, swale, LanternDeeps mechanics, Warscar, NightsideIce, UnfinishedLine, Keelhoist); NEXT: after ONE deploy with builders frozen, run each with `--retile` and record with `record_summaries.py`
- `GIZKASTOWAWAY_PLAGUE_FIX` — fixed in `4130b0d61`, DLL rebuilt, not deployed; NEXT: deploy GizkaStowaway and run its behaviour_rules chain live
- `VFET_RETAG_ROWS_NOT_HELD_1` — cause found: Research Reinvented SteppingStones patches our 13 rows; NEXT: add `PeteTimesSix.ResearchReinvented.SteppingStones` to `forceLoadAfter` in src/RimUtinni/ResearchRetag/About/About.xml, deploy, then drop the 13 rows from KNOWN_UNHELD in its validation.py
- `KEELHOIST_PROOFSELL` — proof bug fixed (`f4387d7f6`), silver 0 unexplained; NEXT: rerun KeelHoist and read `silverOnMap` and `sales=` in the ProofSell string
- `WEEPINGSTONES_JOBS_NEVER_RAN` — ordered_job accepted but feed/harvest/cull/stock deliver nothing in 1200 ticks; NEXT: run WeepingStones and read Player.log for the first job exception
- `DEEP_LAYER_BELT_HARNESS_1` — deep_proto.py never run; NEXT: run it and, if it works, build bland_world.enter_deep()
- `LEANINGSCRUB_GRELLSPINE` — RM_Grellspine won't stand after set_plants and the twitcher lash leaks a hediff with the toggle off; NEXT: rerun after the Cut source is known
- `OBSERVATORY_S3` — S0-S2 shipped (required_checks.py, run identity, call telemetry); NEXT: build S3 per design/RimMandrake/bridge_validation_observatory.md and make the watchdog print the efficiency line
- `ARTPIPE_PENDING` — ~13+30 jobs queued (Twilight Sea floor, Cauldron flora, sun shield); NEXT: wire landed renders (Aluun, Tikkarr, Vaalok missing views; RM_SlimeCompressor needs a wide canvas job) and check facings by eye
- `COVERAGE_GAPS_REMAINING` — CREATUREBEHAVIORS, DIVINGINTERACTION, ENVIRONMENTALHAZARDS, LONGSHADE, RIMPROPERTY, STRUCTUREINJECTIONSRUT open; NEXT: `rimflow claim CREATUREBEHAVIORS_COVERAGE_GAPS_1`
- `ANIMAL_TOLERANCES_DONOR_NOMATCH_1` — 4 bare nomatch Adds fail in generated AnimalTolerances_Ashkarr.xml; NEXT: fix the generator and regenerate

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `jawa/get_defs` cannot read Type fields, omits names/classes on BiomeAnimalRecord/modExtension entries and truncates every list at 64 items (it hid Bacta's rows) (see: Transient/belt_bridge_log_20261003.md 2026-10-03 17:51)
- `rimworld/search_debug_actions` hangs the main thread (it runs quest-gen tests); use jawa/pawn_health action=permanent instead (see: design/RimMandrake/live_test_hang_runbook.md)
- Verse.Log caps at 1000 messages so Player.log goes blind and the watchdog's 'frozen log' alarm lies; the session now resets it every 40 s (see: live_test_hang_runbook.md)
- A DLL rebuilt after a deploy leaves the game stale; builders log 'DLL REBUILT' and the bridge agent redeploys once with builders frozen (filed: lessons)
- A forcePause Dialog_NodeTree from Aftermath's raid letter and the colony-naming dialog taint runs; the modal sweep now covers both (see: required_checks.py taint rules)
- `./publish` autostashes and fails with 'multiple branches' when peers have dirty files; commit with `git commit <paths>` and plain git push, rebuilding on origin/main if non-fast-forward (see: FOUNDRY.md)
- The ledger-guard hook refuses a command where a ledger path follows an 'rm' path in one segment (e.g. scratchpad); keep ledger commits plain (see: CLAUDE.md Git)
- `MayRequire` on a whole `<Operation>` is inert AND red-errors; 43 guards were rewritten to FindMod (see: PATCH_MAYREQUIRE_RESIDUE_FINDMOD_1)
- A selftest that runs a legacy chain through t.screenshot() takes real desktop screenshots (see: Transient/belt_builder_log_20261003.md round 40)

## Closed since the last handoff (49)

- `MIASMA_ROTTING_BED_CORPSES_1` — 2232bce73
- `FEVERWOOD_ANT_THEFT_RAIDBACK_1` — 62913db1a
- `FEVERWOOD_DIANOGA_GIANT_MAP_1` — b1948944c
- `FEVERWOOD_OIL_BOIL_WEATHER_1` — a5ee4ec8a
- `WARSCAR_LOOSENED_PANEL_BUILD_1` — 5a97a2f21
- `WARSCAR_SNAP_MARK_1` — 5a97a2f21
- `MIASMA_ROTTING_BED_CUISINE_1` — 789046561
- `FEVERWOOD_KURRETH_COLUMN_RAIDBACK_1` — 9bfc5248e
- `MIASMA_MOTHERS_PRICE_1` — fdea7b0e2
- `EXPLOSIVE_GROWTH_PROBE_TOOL_1` — 777a0f61b
- `SLIME_SEEKER_LOAD_TOOL_1` — 9eb1e45ed
- `NORTHSTAR_COVERAGE_AUDIT_1` — 4be286a90
- `HUTT_SLAVE_PIT_SITE_BUILD_1` — 186d24833
- `HUTT_LOTTERY_CHUTE_BUILD_1` — 606792398
- `PYRELANDS_LIGHTNING_BREAKER_BUILD_1` — 24aeeb7eb
- `SUMP_CAPSTAN_TURRET_BUILD_1` — e263d1d13
- `SUMP_FREE_TIER_MOVE_BUILD_1` — 697cdc300
- `WRECKEDMACHINES_COVERAGE_GAPS_1` — 8f71cc4b9
- `MIASMA_COVERAGE_GAPS_1` — 05e0b2c27
- `THESUMP_COVERAGE_GAPS_1` — 526a4b6c1
- `SWBESTIARY_COVERAGE_GAPS_1` — 6fd805f4f
- `WEBWORK_COVERAGE_GAPS_1` — 2daab1f9a
- `RUSTCATHEDRAL_COVERAGE_GAPS_1` — 93d35e461
- `PYRELANDS_SAND_TERRAIN_YIELD_1` — 7d25fe8ac
- `PATCH_MAYREQUIRE_RESIDUE_FINDMOD_1` — 6b817126789c65fcab137446901a7deb6219f58f
- `CRACKEDLANDS_WOOLAMANDER_FLIGHT_1` — 589690135
- `FORGE_VOICES_AUDIO_1` — 3fce5edd0
- `SPIKE_DAMAGE_NUMBERS_RULING_1` — 3fce5edd0
- `ABYSS_FREE_TIER_BODY_1` — c0a26af6c1b52763980de79f355a28001e50a0f8
- `LORESTAGES_COVERAGE_GAPS_1` — 3825ecaeaac3a7de0527e469ed01144a9b7a81dd
- `LOAD13_CONFIGERRORS_TRIAGE_1` — ff19c2d44
- `VANILLA_XENOTYPE_CUT_SPAWNSETS_1` — ff934d915
- `VANILLA_XENOTYPE_REMOVAL_ASSESSMENT_1` — ff934d915
- `DEPTH_FILL_COST_MATRIX_1` — 575aea9f5
- `RESTRAININGBOLTS_COVERAGE_GAPS_1` — f774e1bf8
- `GRAVSHIPLANDING_COVERAGE_GAPS_1` — 036f8ba10
- `MOVINGDUNES_COVERAGE_GAPS_1` — 9bc1b83a2
- `RAIDREDESIGNER_COVERAGE_GAPS_1` — 6d0e7f477
- `SEASHORES_COVERAGE_GAPS_1` — 29700addd
- `RUSTCHROME_COVERAGE_GAPS_1` — 5f62af382
- `PYRINTH_COVERAGE_GAPS_1` — 783e0c758
- `PAWNFLAVOR_COVERAGE_GAPS_1` — 64e1fcb00
- `STARWARSPATCHES_COVERAGE_GAPS_1` — 3f4d5ac44
- `KEELHOIST_COVERAGE_GAPS_1` — fe2de69cb
- `GIZKASTOWAWAY_COVERAGE_GAPS_1` — b5fd8a7d3
- `RESEARCHRETAG_COVERAGE_GAPS_1` — 92f1e7191
- `UTINNIPATCHES_COVERAGE_GAPS_1` — 718d96fe8
- `MANDRAKEPATCHES_COVERAGE_GAPS_1` — 7fcf4b4f1
- `PLANETPRESETPRIME_COVERAGE_GAPS_1` — b9b18e365

## Filed and still open (21) — the next seat's queue

- `CREATUREBEHAVIORS_COVERAGE_GAPS_1` — CreatureBehaviors north-star script is THIN: add asserting bars for its uncovered behaviours (design/RimMandrake/northstar_coverage_audit_2026-10-03.m
- `DIVINGINTERACTION_COVERAGE_GAPS_1` — DivingInteraction north-star script is THIN: add asserting bars for its uncovered behaviours (design/RimMandrake/northstar_coverage_audit_2026-10-03.m
- `ENVIRONMENTALHAZARDS_COVERAGE_GAPS_1` — EnvironmentalHazards north-star script is THIN: add asserting bars for its uncovered behaviours (design/RimMandrake/northstar_coverage_audit_2026-10-0
- `LONGSHADE_COVERAGE_GAPS_1` — LongShade north-star script is THIN: add asserting bars for its uncovered behaviours (design/RimMandrake/northstar_coverage_audit_2026-10-03.md row)
- `RIMPROPERTY_COVERAGE_GAPS_1` — RimProperty north-star script is THIN: add asserting bars for its uncovered behaviours (design/RimMandrake/northstar_coverage_audit_2026-10-03.md row)
- `STRUCTUREINJECTIONSRUT_COVERAGE_GAPS_1` — StructureInjectionsRUT north-star script is THIN: add asserting bars for its uncovered behaviours (design/RimMandrake/northstar_coverage_audit_2026-10
- `NORTHSTAR_PARTIAL_GAPS_FILL_1` — Fill the coverage gaps of the 67 PARTIAL north-star scripts, a mod at a time beside its own build or live run (northstar_coverage_audit_2026-10-03.md)
- `SUMP_CAPSTAN_DRAWJOINT_RESEARCH_1` — Capstan turret spec 4: hidden research taught by studying two preserved draw-joints from the Sump dig strata (RUT_DigStratumTable gains the find), and
- `RUSTCATHEDRAL_GOODWILL_FLOOR_1` — Rust Cathedral hum reads a permanent-enemy faction's goodwill: calm bands may be unreachable
- `FEVERWOOD_OIL_FLASH_BARE_GROUND_1` — Oil-haze flash lights no fire on bare ground (TryStartFireIn needs ground fuel)
- `ARMOURY_PROJECTILE_DAMAGE_TOOL_1` — Bridge tool reading projectile damageAmountBase (private) so Armoury's ranged ladder can be asserted live
- `ARMOURY_KOTOR_BOLT_GUARD_1` — Armoury ranged patch: 5 absorbed KotOR bolt ops sit under the inactive donor's FindMod
- `BELT_WATER_HARNESS_1` — Bland-map water cell helper: Miasma return proof and Greentide vurrak need water; paint via set_terrain_batch in bland_world
- `BLUEDESERT_FLORA_PLANT_REFUSAL_1` — BlueDesert flora_spawns still refuses 8 plants at tile temp -5 (retile read back): read set_plants message, OutdoorTemp vs tile temp
- `DEEP_LAYER_BELT_HARNESS_1` — LanternDeeps Deep-layer proofs say comp only on a Deep: harness needs a Deep map; Nightside shivven needs a powered heater
- `ABYSS_CRAGS_ART_ON_PORTED_DEFS_1` — Wire the 12 done crags_* art sets (+ the dusk rat redo when commissioned) onto the Abyss's ported defs as DONOR_DEFS_PORT_TO_OURS_1 lands
- `VANILLA_XENOTYPE_DEFCUT_1` — Xenotype cut slice 2: typed Cherry Picker cuts of the 11 (XenotypeDef/Neanderthal collides with a BotR animal), delete their PawnFlavorPhase2_Xenotype
- `NONSW_XENOTYPES_SCOPE_1` — Owner: the cut-the-twelve ruling says only Star Wars xenotypes belong, but the load has 32 more non-SW XenotypeDefs (AlphaGenes 15, Phytokin 3, det.* 
- `CRACKEDLANDS_SWALE_CAMPAIGN_LOCK_1` — Utinni lock for RM_Swale: locked in the campaign until discovered in the Cracked Lands (first completed survey), world-level persistence (WorldCompone
- `ANIMAL_TOLERANCES_DONOR_NOMATCH_1` — AnimalTolerances_Ashkarr: bare nomatch Add on absent donor creatures logs failed patch ops
- `VFET_RETAG_ROWS_NOT_HELD_1` — 13 VFE Tribals retag rows (techLevel Neolithic, tab RUT_Tree_Scavenging) are unpatched in the load-14 dump

## Commits

```
3e3ace80e ledger: VFET_RETAG_ROWS_NOT_HELD_1 cause noted; builder log r42
edeabab6d handoff: belt bridge round 6 (deploy + load 15 launch, Cut-by-nobody origin instrument)
4130b0d61 GizkaStowaway: Plague reachable at caps 4-5 (bands clamped below the cap, no stage skips)
e09fec2a1 selftest_utinnipatches_dump: no deepcopy of the 26k-row ThingDef dump (flaked under 16 workers)
9bf470fef ledger: PLANETPRESETPRIME_COVERAGE_GAPS_1 closed
b9b18e365 PlanetPresetPrime: signatures_static against decompiled engine + MLP source (PLANETPRESETPRIME_COVERAGE_GAPS_1 offline)
0417d5c9d detectors: colonist_damaged evidence carries the call-site origin stack
10117344d ledger: MANDRAKEPATCHES_COVERAGE_GAPS_1 closed
7fcf4b4f1 MandrakePatches: fix_effects_vs_dump_static (MANDRAKEPATCHES_COVERAGE_GAPS_1 offline)
f4387d7f6 KeelHoist: rebuild DLL (ProofSell host-faction)
518858f65 KeelHoist ProofSell: a humanlike slave is held by the buyer as HostFaction (its Faction stays its own); report both
4b4d9878a JawaBench damage_log: origin call-site stack on instigator-less pawn hits (finds 'Cut by nobody')
66fdc4310 ledger: UTINNIPATCHES_COVERAGE_GAPS_1 closed
718d96fe8 UtinniPatches: shipped defs vs load-14 dump + greatbole ladder state machine (UTINNIPATCHES_COVERAGE_GAPS_1 offline)
0dfcec585 handoff: belt bridge round 5 (observatory hooks fixed, water harness proven, kurreth faction NRE found)
87f2e7a57 Aftermath script: close the raid letter's Dialog_NodeTree before ticks pass (it paused the game and ended the chain)
07cdb8596 ledger: RESEARCHRETAG_COVERAGE_GAPS_1 closed, VFET_RETAG_ROWS_NOT_HELD_1 filed
92f1e7191 ResearchRetag: retag_rows_vs_dump chain; forceLoadAfter gains the 15 missing owners
eadbaecb3 TheRot script: a navigator log that already holds pings is a precondition (UNMEASURED), not a FAIL on a rerun
9374dc55b ledger: GIZKASTOWAWAY_COVERAGE_GAPS_1 closed
... 248 more: git log --oneline f3c2ebd20..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running; BRIDGE NOT PROBED — no port found in the environment or in Player.log, so LOADING here is a DEFAULT, not a reading.)
- recorded  : UP
- Bridge: FREE    since 2026-10-04T07:45:27Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/belt_bridge_log_20261003.md   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/belt_rerun17d_20261003.txt   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/AcousticScanner_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/AssailantSalvage_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/Bacta_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/BlueDesert_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/BrainWorms_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/Cauldron_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/FallLineArrivals_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/FeverWood_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/Greentide_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/KeelHoist_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/LanternDeeps_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/LeaningScrub_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/Miasma_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/NightsideIce_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/RustCathedral_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/TheForge_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/TheRot_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/TheSump_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/Webwork_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue/situational_rerun/WeepingStones_summary.json   (FOUNDRY belt run artifact, untracked; keep or delete)
 M Transient/modcheck/live_queue_results.jsonl   (FOUNDRY belt run artifact, untracked; keep or delete)
 M infrastructure/state/ledger/events/FOUNDRY.jsonl   (FOUNDRY belt run artifact, untracked; keep or delete)
 M infrastructure/state/modcheck_status.json   (FOUNDRY belt run artifact, untracked; keep or delete)
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   (FOUNDRY belt run artifact, untracked; keep or delete)
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   (FOUNDRY belt run artifact, untracked; keep or delete)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   (FOUNDRY belt run artifact, untracked; keep or delete)
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   (FOUNDRY belt run artifact, untracked; keep or delete)
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   (FOUNDRY belt run artifact, untracked; keep or delete)
?? deployed/config/ns_flowworks_backup.20261002T070221.json   (FOUNDRY belt run artifact, untracked; keep or delete)
```

