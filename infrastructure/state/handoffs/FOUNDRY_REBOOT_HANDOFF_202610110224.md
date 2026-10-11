# FOUNDRY_REBOOT_HANDOFF_202610110224 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610101111`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The bridge/TPS/awareness/health tooling is BUILT and pushed, but the game is DOWN and BENCH holds the bridge lock (live process, dead game) — nothing live can run until the lock frees (never --force). The next live session is the RETIREMENT WAVE 1 cold load: read `design/RimMandrake/mod_audit/RETIREMENT_WAVE_1_RUN_SHEET.md`, run `preflight_bridge.py` first, launch only via `launch_and_wait.sh`; that one 21-minute load also owes the face check, the remaining awareness live tests, the Cherry Picker SHIP swap and the 5 VWE relic repairs. Owner rulings for the whole mod audit live in `design/RimMandrake/mod_audit/OWNER_RULINGS.md` (append-only); decisions by card are recorded there as 'option click', typed write-ins as typed text.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Pick the 5 replacement relics for the VWE relic precepts** (`SAVE_RELIC_PRECEPTS_REPAIR_VWE_NULLS`): Hexlink, Loccorpus, Animal Blaster, Strong Rifle, Rifle of Self; otherwise the game re-rolls them at random on load.
- **Passion mapping default** in the wave-1 save-copy script: removing Vanilla Skills Expanded and Alpha Skills would reset 198 custom passions on 99 pawns (6 colonists); the script maps them to the nearest vanilla passion. Veto or change if wanted.
- **Yayo's Combat 3 and Stronger Quality Scaling are undecided.** The exhaustive analysis is `design/RimMandrake/mod_deepdive_yayo_full.md` (recommendation: remove; port hand/foot coverage and skill-weighted accuracy; rebuild armour wear as our own stat; or switch Yayo's engine off in its settings file to stop the side effects today). He asked for the deep dive; the decision is his.
- **Facial Animation probably draws human faces on every RSW_ xenotype** (its exclusion list has 156 keys, none RSW_). Not confirmed in game; the fix is a small shim in our races mod and changes how pawns look, so he gets screenshots first (`RSW_FACES_VERIFY_IN_GAME_BEFORE_SHIM`). He also wants a deep takeover analysis of the facial mods: `design/RimMandrake/mod_deepdive_faces.md` (13 mods; Facial Animation itself cannot be redistributed; only Genetic Heads Framework MIT and Face Addon Framework Apache-2.0 are reusable).
- **Cards still unasked or pending owner time:** Oracle study (card C23 'study first' — no study agent started yet), Ideology Virtues (41 precepts live in 11 of 13 Jawa ideoligions; waits on trait-virtue design), the bone-building 'lean port' scope, and the C13 industry decisions (smelter/granulator aboard are left until the remake by his ruling). Stranded quest is NOT retired (test quest, retune later).
- **Ruling conflict he should know about:** the 2026-09-11 'permanent residents' list is now overridden by 'port everything' (C01); the Cherry Picker doctrine is now 'temporary bridge, maintain only for mods we KNOW we keep' (memory note filed).
- **GPT/Codex is unavailable until 2026-10-13 20:28** (usage limit); reviews since were done by fresh Opus reviewers with RimSage. Saved GPT prompts for reruns: `Transient/foundry_event_wisdom_gpt_prompt_20261010.md`, and the convenience-replacements review is owed (`design/RimMandrake/convenience_replacements.md`).
- **HugeFootprints is fixed and proven** (62.6 -> 0.98 ms/tick, 13 -> 58 TPS on the Rot map); the 30 GB private memory and two unexplained 3–7 s stalls are separate open tickets (`FULL_LIST_MEMORY_AUDIT_THIRTY_GB_PRIVATE`, `GAMECOMP_STALL_HUNT_SEVEN_SECONDS`).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `AWARENESS_GENPAWN_TAME_ARM_BEFORE_USE` — built and pushed; deployed in the test profile on the 550 list; arm/lazy-install not yet exercised live; NEXT: run MAP_AWARENESS_PROVE_ON_A_QUIET_MAP check A4 (generation-early on, first-map origin) in the wave-1 session
- `BRIDGE_CALL_EVIDENCE_WIRE_LOST_REPLY_UNKNOWN` — implemented (87d8821c2); logs only under python.exe, read-only batches not logged; NEXT: force one lost-reply mutation in the next bridge session and run rimbridge_client.py --reconcile
- `BRIDGE_LOCK_HARDEN_ALIVE_MEANS_A_PID` — implemented (b82152044); model.bridge_gate does not check the new lock yet; BENCH's lock currently names a live process with a dead game; NEXT: wire model.bridge_gate to the lock, then verify BENCH's holder pid and have the owner free it with ./bridge free if it is stale
- `BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD` — built and unit-tested; not deployed live beyond the test-profile DLL; stale-call refusals unproven in a real game; NEXT: run the stale-epoch and map-removal refusals in the wave-1 session
- `BRIDGE_TPS_CAPTURE_FIXES_1` — implemented; C3/C4 proven on the minimal list and autostart on the 550 list; NEXT: verify the criteria on the full list (C3 matrix subset) with rimflow verify --criterion once the wave-1 session has the game up
- `BRIDGE_TPS_REGULAR_REPORT_1` — implemented; reader/belt_watchdog line works; TPS record explained the 70 ms HugeFootprints cost with no extra tooling; NEXT: close it with the HugeFootprints proof as evidence after the overnight reconstruction check
- `BRIDGE_TPS_REVIEW2_FIXES_1` — MUST 1-16 fixed and tested; MUST 17 partly done (autostart and overhead A/B on the 550 list: no measurable cost); overnight reconstruction and C0-C5 protocol owed; NEXT: run RECORDER_OVERHEAD_MEASURE_SIX_CONFIGS_DEEP and the overnight reconstruction, then verify and close
- `COMPANION_HANDSHAKE_BUILD_SAY_WHAT_LOADED` — built; handshake answered correctly on the 550 list (hash matches, test profile, hooks ok); NEXT: record the verify evidence and close; consume the schema in preflight_bridge.py --live every session
- `COMPANION_PROFILE_ENFORCE_SAFE_BY_DEFAULT` — built and unit-tested; test profile in use; no-profile campaign default not yet checked live; NEXT: launch once without companion_profile.json and confirm debug/test tools refuse while authoring tools work
- `EFFECTIVE_DEF_LINT_WIDEN_PAST_DURASTEEL` — built; ran clean on the 551/514/511 lists apart from two AncientsAreRakata.xml failures that predate the wave; NEXT: fold the two RAKATA failures into RAKATA_PATCHES_PROBE_THREE_OPS_MATCH_NOTHING and run the lint on the live list after wave 1
- `EXPERIMENT_MANIFEST_BUILD_FREEZE_SIX_CELLS` — built; the complete gate has never seen a real C0-C5 run; NEXT: use experiment_manifest.py when running RECORDER_OVERHEAD_MEASURE_SIX_CONFIGS_DEEP
- `FOCUS_HEAL_TAME_HANDS_OFF_HIS_WINDOWS` — implemented (f7b3b52c1); focus scripts touch no window without RM_FOCUS_OPT_IN; NEXT: confirm no focus steal during the wave-1 launch and close
- `FULL_LIST_LOAD_DIAGNOSE_MINIFY_SAYS_NO` — root cause fixed (67153b072) and proven: the 550-mod list cold-loaded in 20.7 min; NEXT: rimflow verify/close it citing 88cddfd92 and 63447a6db as the proof
- `GAME_OBSERVER_BUILD_OUTSIDE_LOOKING_IN` — built and measured (0.3% of a core); NOT installed as a standing task (it stopped at the 2 h background limit); NEXT: install it as a Windows scheduled task (like the TPS observer task) and verify it survives a relaunch
- `INCIDENT_JOURNAL_BUILD_CALLED_IS_NOT_FIRED` — built; live checks A3/A4 passed; NEXT: run the worker-false and queued-incident journal tests in the wave-1 session, then verify and close
- `KEEPER_SAVES_HARDEN_WRONG_SLOT_WRITES` — implemented (2a5b92fa5); reviewmap.save_keeper and ad-hoc save_game still bypass save_guard; NEXT: route reviewmap.save_keeper through save_guard and add the current-save argument
- `LAUNCHER_READY_HARDEN_OLD_LOG_LINES_LIE` — implemented (b1ed0965d) and used for the 550 launch; deadline numbers are guesses; NEXT: measure two more cold loads and set load_policy.json from the numbers
- `LOAD_SAVE_FORENSICS_BUILD_NO_GAME_NEEDED` — built; load-tree parser tested only on a fixture (no archived log held a verbose tree); NEXT: do one verbose launch in the wave-1 session and parse its tree
- `MOD_MANIFEST_BUILD_THREE_LISTS_ONE_TRUTH` — implemented (2e242df17); 38 of our mods are missing from FULL.LATEST, 14 proposed; NEXT: apply the 14-mod proposal only after a clean wave-1 load (owner ruling), then re-run modmanifest.py check
- `PAWN_ORIGIN_BUILD_SAY_ORIGIN_UNKNOWN` — built; origin chains for spawn and drop-pod raid passed live; first-map, caravan and save/load origin unproven; NEXT: run A2/A4 style origin tests in the wave-1 session
- `PREFLIGHT_BUILD_85_ROWS_OF_HINDSIGHT` — built; offline ran clean-with-waivers and --live ran clean on the 550 list; NEXT: run preflight_bridge.py --tier full against WAVE1_CANDIDATE before the wave-1 launch
- `PREFLIGHT_DOCS_WIRE_ONE_LINE_EACH` — done in docs; skills/rimbridge pointer needs the fold-in by a skill-curation session; NEXT: fold skills/rimbridge/references/preflight.md into the skill in a curation session
- `THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER` — built; thing_explain installed in the test profile; OBSERVED vs CANDIDATE texture provider unproven live; NEXT: run the multi-layer overridden-texture resolver test in the wave-1 session
- `TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS` — built and unit-tested (TPS group 25/25); all hooks reported coverage ok on the 550 list; NEXT: run the five acceptance checks in design/RimMandrake/companion_handshake.md section 5 live
- `VISITOR_DETECTORS_MEND_NAME_THE_STRANGER` — built (fadddb0dd), offline-tested; the CLEAN/DISRUPTED/INDETERMINATE logic ran live in abort_proof once; NEXT: re-run abort_proof and one validation suite and verify the substituted-spawn receipt when a substitution next happens

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- zsh treats `$C:refs/heads/main` as a `:r` modifier — use `${C}:refs/heads/main` or a literal sha when pushing a plumbing commit (see: `src/RimMandrake/Utils/land.sh`, which is the sanctioned way to publish from a dirty clone).
- Several agents share one scratchpad name; two assessors overwrote each other's scripts and duplicated rows — brief every agent to write only uniquely named scripts (see: `design/RimMandrake/mod_audit/README.md`).
- `./game` state can be stale (recorded UP while no RimWorldWin64 existed) and BENCH's bridge lock can name a live process whose game is gone — measure with bare `./game` before trusting `rimflow bridge who` (see: `design/RimMandrake/bridge_system.md`).
- The mod-audit facts file counted guarded references as dependants and credited Armoury with 72 false JecsTools edges; read edge KIND before treating a dependants list as a blocker (see: `design/RimMandrake/mod_audit/GPT_REVIEW_DISPOSITION.md`).
- Codex/GPT refuses all consults until 2026-10-13 20:28 (see: memory `gpt-codex-limit-until-2026-10-13`).
- `rimflow file` prints a refusal-looking tail even on success; confirm with `rimflow show <ID>` (see: `using-rimflow` skill).
- Mod removal order: the 11 minified stone walls must be removed from the canonical save BEFORE Minify Everything is unticked (see: `design/RimMandrake/mod_audit/RETIREMENT_WAVE_1_RUN_SHEET.md`).

## Closed since the last handoff (6)

- `JEV_KEY_ARCHMAGI_1` — 07f05d3f5
- `LONGSHADE_SHADE_EXTRAS_1` — c53b73257
- `ROT_MAPCOMP_HUNT_FORTY_SEVEN_MS` — f3774dd15
- `FULL_LIST_TPS_DIAGNOSE_EIGHT_NOT_SIXTY` — f3774dd15
- `HUGE_FOOTPRINTS_FIX_PROVE_SIXTY_ON_ROT` — 5af889844
- `AWARENESS_METERS_DEPLOY_HOOK_BODY_ONLY` — 5af889844

## Filed and still open (61) — the next seat's queue

- `SHIPPING_NAME_CANDIDATES_1` — Draft 3 invented exotic names each for the 5 wasteland + 2 greentide working names (plus bezoar), put them on one question card for the owner; owner c
- `LASSO_CONFIG_UNSET_1` — Melee Animation config Mod_2944488802_Core.xml has no LassoSpawnChance element on the live profile; set 0 at game-down (LASSO_CHERRYPICKER_REMOVAL_1 A
- `BRIDGE_TPS_REGULAR_REPORT_1` — Bridge regularly samples and reports game TPS during use: continuous gathering, a rolling record on disk, and a one-line report in belt_watchdog and b
- `BRIDGE_TPS_CAPTURE_FIXES_1` — TPS record fixes from the Opus+GPT reviews: auto-start at load, keep stalls, correct window maths, dependable writer, attribution, incident context, q
- `PLANET_ATMOSPHERE_CLOUD_COST_1` — Measure Planet Atmosphere 8K cloud cost: load-time and VRAM A/B with and without the mod (owner Q2 = measure first; spec Transient/texture_mod_review_
- `SUMP_GLASSWALK_SPEED_RATIO_1` — Glasswalk measured 0.65 of granite speed (3 repeats, 9.8 ticks/cell pawn, glass 15) vs spec ~0.80 for pathCost 3; re-measure on a 13 ticks/cell pawn t
- `BRIDGE_TPS_REVIEW2_FIXES_1` — Repair TPS record build 2 per second GPT review: 17 MUST fixes (profiler skip-safety, measurement boundaries, commit-aware writer, game-scoped state, 
- `GAME_OBSERVER_BUILD_OUTSIDE_LOOKING_IN` — Persistent Windows-side health observer (python.exe, stdlib/ctypes): process identity pid+creation, process and main-thread CPU, working set/private b
- `HEALTH_BANDS_WIRE_QUEUED_BEHIND_OVERHEAD` — Minimal in-game health extension to the TPS record: frame-interval histogram from existing Root.Update timestamps (merge histograms, never average p99
- `LOAD_SAVE_FORENSICS_BUILD_NO_GAME_NEEDED` — Offline forensics: verbose load-tree parser for Player.log (truncated/incomplete trees flagged, nested phases not double-counted), streaming bounded-m
- `OPTIMISATION_TOOLS_BUILD_BY_NAME_NOT_BLAME` — Named optimisation tools: own-code counters for our mods' hot paths and an on-demand, expiring profiler over an exact target allowlist (no blanket Pat
- `GC_EARLYLOAD_DUMPS_PROBE_SHOW_VALUE_FIRST` — Conditional spikes, each kept unbuilt-by-default until it shows useful evidence on a known case: GC timing (gcCountChangedDuringGap is a coincidence l
- `TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS` — Fix the TPS-code hazards in GPT review 2.3: global state in TmuPrefix/Postfix, LePrefix/LeFinalizer and _tickId (reentrancy), TickPre writing state be
- `RECORDER_OVERHEAD_MEASURE_SIX_CONFIGS_DEEP` — Full-list overhead protocol C0-C5 (off; external collector only; sampler without attribution; full recorder; + minimal health bands; + frame-stage hoo
- `HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP` — Post-hoc review: evaluate each game-health metric's worth and measured cost from the metrics ledger in game_health_record.md and decommission (switch 
- `FULL_LIST_LOAD_DIAGNOSE_MINIFY_SAYS_NO` — Full 551-mod list fails play-data load: NRE in MinifyEverything.GenerateImpliedDefsPostfix, ModsConfig reset to Core
- `VISITOR_DETECTORS_MEND_NAME_THE_STRANGER` — Map awareness phase 1 (Python harness): per-test bounded expectation contract; detectors name exact pawn id/kind/faction/state; set-diff arrivals incl
- `THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER` — Map awareness phase 2 (companion C#): jawa/thing_explain (one selector, never silent pick; def/kind/race/modContentPack chain; appearance as CANDIDATE
- `INCIDENT_JOURNAL_BUILD_CALLED_IS_NOT_FIRED` — Map awareness phase 2 (companion C#): incident journal on IncidentWorker.TryExecute with honest outcome fields (called/outerBodyRan/exception/workerEn
- `PAWN_ORIGIN_BUILD_SAY_ORIGIN_UNKNOWN` — Map awareness phase 3 (companion C#): pawn origin recorder - context chain (bridge action -> incident -> generation) with explicit immutable tokens, G
- `MAP_AWARENESS_PROVE_ON_A_QUIET_MAP` — Deploy the map-awareness companion build (game down) and run the live acceptance tests of GPT review s7 phases 1-3 on a quiet quicktest map: substitut
- `LAUNCHER_READY_HARDEN_OLD_LOG_LINES_LIE` — launch_and_wait.sh succeeds only on a current-process readiness receipt (PID+start time, fresh token line after archived log, listener owned by PID, d
- `MOD_MANIFEST_BUILD_THREE_LISTS_ONE_TRUTH` — modmanifest.py check|diff: ordered intended manifest vs next-load ModsConfig vs loaded mods; flags Core-only reset, omitted shipping ids, reorders, du
- `FOCUS_HEAL_TAME_HANDS_OFF_HIS_WINDOWS` — focus_heal/game_focus never steal or minimise the foreground unless an explicit opt-in flag is set; Run-in-background pref is checked not healed; brid
- `KEEPER_SAVES_HARDEN_WRONG_SLOT_WRITES` — save-guard wrapper: hash-backup Saves keepers before any save-capable run, refuse current-slot overwrite, post-verify a new file and unchanged keepers
- `BRIDGE_LOCK_HARDEN_ALIVE_MEANS_A_PID` — exclusive driver lock keyed on process identity with O_EXCL acquisition, heartbeat/PID liveness, loud failure on unreadable lock; wired into rimflow b
- `BRIDGE_CALL_EVIDENCE_WIRE_LOST_REPLY_UNKNOWN` — rimbridge_client writes bounded per-call evidence for every caller; a mutating call with a lost reply is INDETERMINATE and blocks further mutations un
- `COMPANION_PROFILE_ENFORCE_SAFE_BY_DEFAULT` — Runtime safe profile for the JawaBench companion: every jawa tool not on a reviewed read-only allow-list refuses unless JawaBench/companion_profile.js
- `COMPANION_HANDSHAKE_BUILD_SAY_WHAT_LOADED` — jawa/companion_handshake: companion sha/MVID/file sha256, compile + runtime profile, hook install status per recorder, RimBridgeServer and Harmony ver
- `BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD` — Game/map epoch guards: reserved call arguments expectGameEpoch / expectMapId / expectCurrentMapId refused at the binder when stale (game identity by o
- `AWARENESS_GENPAWN_TAME_ARM_BEFORE_USE` — GeneratePawn awareness hook installs lazily (on arm, from the main thread) unless awareness_settings.json sets install.generation-early; world generat
- `PREFLIGHT_BUILD_85_ROWS_OF_HINDSIGHT` — preflight.py: ordered fail-fast pre-flight (offline before launch + --live first five minutes), PASS/FAIL/UNMEASURED/UNSUPPORTED per check with cost, 
- `EFFECTIVE_DEF_LINT_WIDEN_PAST_DURASTEEL` — effective_def_lint.py: costlist_resolve_check generalised to a cached patched-tree lint (cost/recipe/stuff refs, removed-def refs, known load killers)
- `EXPERIMENT_MANIFEST_BUILD_FREEZE_SIX_CELLS` — experiment_manifest.py: record/verify frozen inputs per C0-C5 cell; refuse complete on changed inputs or an open required safety FAIL (GPT review rank
- `PREFLIGHT_DOCS_WIRE_ONE_LINE_EACH` — Wire preflight into skills/rimbridge (references/preflight.md + pointer, fold-in owed) and GAME_STATE_WORKFLOW.md
- `RECLAMATION_TRIGGER_REWIRE_WOKEN_COUNT` — Reclamation trigger: rewire the built 45-day chain delay to a woken-ancients count (owner card 13, 2026-10-10)
- `RAKATA_PATCHES_PROBE_THREE_OPS_MATCH_NOTHING` — effective_def_lint failed_ops on FULL.LATEST: mandrake.rut.patches AncientsAreRakata.xml (Sequence + Ancient-urban-ruins FindMod) and VQEPatients_AreR
- `GSS_PROOF_ALL_RETRY_AFTER_THIRTY_FIXES` — GimmeSomeSlack: one live proof_all (carry, relay, maze, style) after the 10-06 and 10-09 fix waves; see Transient/unworked_items_2026-10-10.md
- `GSS_SWITCHES_PROVE_TWENTY_UNFLIPPED` — GimmeSomeSlack: settings-flip proofs for the ~20 untested aerial and hose settings; see Transient/unworked_items_2026-10-10.md
- `LAVA_LIQUID_BUILD_PROMISED_BY_CARD` — FlowWorks: add the lava liquid the owner promoted by card 2026-09-24 (missing from the liquid registry); see Transient/unworked_items_2026-10-10.md
- `RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED` — FlowWorks rivers: prove the 11 river settings toggles owed in validation.py, and the 10 untested river-walk lines (flier/flood lines need the owner wa
- `HOSE_REEL_MIGRATE_TO_FLOWWORKS_AT_LAST` — Move GimmeSomeSlack's hose reel code and behaviour into FlowWorks and reconcile it with RM_LiquidHose; GSS becomes cables, conduits and electricity on
- `POWER_THEFT_BUILD_SLOW_GOODWILL_LEAK` — GimmeSomeSlack power theft (GS-3 hook): when caught, a steady goodwill drain with the victim faction, like living too close to a settlement (owner 202
- `UNROUTABLE_CORD_BUILD_DIVE_THROUGH_WALLS` — GimmeSomeSlack: an unroutable cord draws diving into the wall and re-emerging (GPT read A7; decision taken by question card 2026-10-10); diagrams in T
- `FULL_LIST_MEMORY_AUDIT_THIRTY_GB_PRIVATE` — 550-list game holds 30.6 GB private / 18.3 GB working set with only ~5 GB managed heap: attribute the ~25 GB native share (textures/atlases/audio by m
- `WITCHES_OYSTER_MASK_RESTORE_PIN_DRIFTED` — selftest_hugethings_footprint.py FAILs measured_masks_are_pinned: AB_WitchesOyster masks moved (WitchesOyster vs WitchesOyster_A, 9 contact cells) aft
- `GAMECOMP_STALL_HUNT_SEVEN_SECONDS` — Name the GameComponent behind one-off stalls on the 550 list (Rot save): gameComp 6.76 s at tg 7501 and 2.88 s at tg 5821 (18 ticks after load) in the
- `GENERATOR_MODS_PROVE_INERT_AFTER_CREATION` — Prove Alien Worlds, Tidally Locked, My Little Planet, Sensible Factions and Faction Territories do nothing after world creation (load the saved world 
- `LANDFORMS_PROBE_REPLACE_OR_KEEP_EXPERIMENT` — Experiment: can we replicate Geological Landforms ourselves, or must it stay? Landforms looks like a big lift (owner C06 ruling 2026-10-10)
- `BIOME_TRANSITIONS_JUDGE_VS_BAROQUE` — Judge Biome Transitions against our Baroque Biomes: with baroque biomes it may no longer make sense and need to go (owner C06 ruling 2026-10-10)
- `HEAVY_TEXTURES_MEASURE_REAL_VRAM` — Measure real memory of Planet Atmosphere, EGI Holograms, Minerals Rock shapes and Glowing Bush in a live session (owner C18 ruling 2026-10-10); textur
- `WAVE1_FIXES_DEPLOY_BEFORE_THE_CUT` — Wave 1 W0-W1: back up, then deploy Armoury (durasteel 67153b072), StarWarsPatches, ResearchRetag, UtinniPatches, Doctrine, GreentideRaidAnt, LuminousP
- `CHERRY_PICKER_RESTORE_FROM_SHIP_PROFILE` — Wave 1 W2: make CherryPicker.SHIP.WAVE1_CANDIDATE.xml the SHIP profile and swap it live with the game down (live file lags SHIP by 184 keys incl. the 
- `WAVE1_MODLIST_RETIRE_37_IN_ONE_LOAD` — Wave 1 W3-W6: edited save copy, promote WAVE1_CANDIDATE to FULL.LATEST, one cold load, load the edited save, acceptance per the run sheet, re-save und
- `SAVE_RELIC_PRECEPTS_REPAIR_VWE_NULLS` — Owner choice before wave 1 W3: replacement relics for the 5 VWE relic precepts (Hexlink, Loccorpus, Animal Blaster, Strong Rifle, Rifle of Self) or ac
- `RSW_FACES_VERIFY_IN_GAME_BEFORE_SHIM` — In game: does Facial Animation draw human faces on RSW_ xenotypes? Spawn 2 Jawa + one of each RSW_ humanlike, verify actual kind, close screenshots to
- `REMAKE_CARRYOVER_VERIFY_SIX_ITEMS_ONLY` — C25: verify the remake carry-over is safely extracted: founders' bodies, genes, skills, ship hull, hull paint job, ideology file; done = each has a fi
- `HEALTH_CHECK_MONITOR_MEMORY_TPS_OVER_TIME` — C24 standing health check: memory (private, managed, native/GPU) and TPS as a function of time beside load-health and log-error counts, recorded every
- `BONES_LEAN_PORT_BUILD_TREELESS_WORLD` — Owner card: lean port of Bones to our own tier (bone as building stuff, our art and numbers, no fuel/plasteel routes), then retire sihv.rombonesPort; 
- `SALVAGE_YIELD_UNIFY_THREE_RULES_TODAY` — One salvage-yield rule for smelter tiers, crematorium and scavenging (Better Cremation retires in wave 1); apparel returns the same on every path; opt
- `SALVAGE_MINIFY_DESIGN_HAULER_OR_SCRAP` — After Minify Everything goes: which buildings the Salvage action may lift (minify and reinstall vs scrap for yield), the hauler droid's role, one list

## Commits

```
f12511920 FOUNDRY: HugeFootprints proof closed, awareness criteria verified, bridge released
2ee9fb6fb Ledger: OWNER shard sync (ROT_GIANTS_DENSITY_JUDGE close)
14fa9468a HugeFootprints fix proven live on the Rot (62.6 -> 0.98 ms/tick, 13 -> 58 TPS); awareness meters measured
0be88f8a6 Deploy log: health observer stopped at the 2 h background limit, not 16:42
b48bb636d Mod audit stage 0 progress log
9fc315f2e Mod audit stage 0: facts for 589 mods, 16 assessor batches, rubric with worked examples, README
1e7fc0876 HugeFootprints perf doc: code, 70 ms/tick issue, f3774dd15 fix, alternatives, test plan, GPT questions
e544ab528 FOUNDRY: claim HUGE_FOOTPRINTS_FIX_PROVE + AWARENESS_METERS_DEPLOY, bridge taken
46c194cac HugeFootprints: DebugCounts probe (giants/dirty/realized/pending) for the live fix proof
51d2d1102 Mod audit stage 0: disk/runtime/source evidence collectors, assembler, batcher, selftest
4abfab29e FOUNDRY: bridge released after TPS diagnosis
fd4b8f24b FOUNDRY: full-list TPS diagnosed (HugeFootprints 70 ms/tick), follow-ups filed
f3774dd15 HugeFootprints: stop re-planning every giant on every tick (~70 ms/tick on the Rot)
36c21478e Mod audit stage 0: universe resolver, offline def/patch census, scenario brief
dd73e8269 Ledger: owner-quoted items for hose migration and power theft
f48048b36 Ledger: owner rulings on hose home, power theft, stuck cords, liquid palette
91f9c0a14 jawa/map_comp_timing: per-MapComponent tick timing (test-only, one-off)
63447a6db FOUNDRY: bridge released after the 550 full-list session
88cddfd92 550-mod full list cold-loaded (20.7 min) + live proofs: awareness, abort_proof, TPS A/B
fb4735735 Awareness meters: charge only the hook bodies, not the wrapped original
... 197 more: git log --oneline 533da17f5..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : DOWN  → corrected to UP, measured now
- Bridge: FREE    since 2026-10-10T23:13:39Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M design/Jawa/research_review/build_retag_patches.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M design/RimMandrake/deepfire_luminous_pigment_spec.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M design/RimMandrake/mod_audit/README.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M design/RimMandrake/mod_audit/facts/mod_facts.csv   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M design/RimMandrake/mod_audit/facts/mod_facts.jsonl   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M design/RimMandrake/mod_audit/facts/session_context.json   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M design/validation_walks/RimMandrake/LuminousPigment.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M infrastructure/output/research_manifest_draft.csv   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M infrastructure/state/ledger/events/FOUNDRY.jsonl   FOUNDRY (ledger shard, to publish)
 M skills/README.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimMandrake/LuminousPigment/Assemblies/RimMandrakeLuminousPigment.dll   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimMandrake/LuminousPigment/Assemblies/RimMandrakeLuminousPigment.dll.srchash   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimMandrake/LuminousPigment/Source/DeepfireGodDeltaDebugActions.cs   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
D  src/RimMandrake/LuminousPigment/Source/DeepfireLightsOutCompat.cs   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimMandrake/LuminousPigment/Source/RM_LuminousPigment.csproj   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimMandrake/LuminousPigment/validation.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimMandrake/Utils/gen_pawnkind_roster.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimMandrake/Utils/gen_weapon_register.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimMandrake/Utils/modaudit/assemble.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimMandrake/Utils/modaudit/defscan.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimMandrake/Utils/modaudit/diskfacts.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimMandrake/Utils/modaudit/selftest_modaudit.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimMandrake/Utils/modaudit/sources.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimMandrake/Utils/modset_builder.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimMandrake/Utils/weapon_tag_audit.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimMandrake/bridgetools/prove_deepfire_god_deltas.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimStarWars/Armoury/About/About.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimStarWars/Armoury/Patches/Armoury_RangedDamage.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimStarWars/Armoury/Patches/Turrets_DamageDoctrine.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimStarWars/Armoury/Patches/Turrets_Renames.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimStarWars/Armoury/Source/gen_armoury_patch.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimStarWars/Armoury/Source/gen_turret_doctrine.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimStarWars/StarWarsPatches/Patches/WeaponTags_Renormalise.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimUtinni/Doctrine/Patches/MegafaunaYield.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimUtinni/Doctrine/Patches/MegafaunaYield_OwnedPorts.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimUtinni/Doctrine/Patches/MegafaunaYield_OwnedPorts_Warscar.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimUtinni/Doctrine/Source/gen_megafauna_yield.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimUtinni/GreentideRaidAnt/Defs/ThingDefs_Races/RUT_Race_GreentideAnt.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimUtinni/ResearchRetag/About/About.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimUtinni/ResearchRetag/Patches/RUT_ResearchRetag.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimUtinni/ResearchRetag/Patches/RUT_ResearchTabAssign.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimUtinni/UtinniPatches/About/About.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimUtinni/UtinniPatches/Defs/PawnKindDefs/JawaFactionRoster.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
 M src/RimUtinni/UtinniPatches/Patches/BiomeCastEvictions_WildBiomes.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? .claude/skills/rimworld-crew-and-nemesis-events   subagent (event-wisdom skills agent); symlinks to publish
?? .claude/skills/rimworld-custom-incidents   subagent (event-wisdom skills agent); symlinks to publish
?? conversations/   auto-saved transcripts; local artifact, not for the repo
?? deployed/config/ModsConfig.before-bridge4-fulllist_20261009.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-bridge6_20261009.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-bridge7_20261009.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-acc_20261009.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-acc_20261009b.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-acc_20261009d.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-acc_biomes.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-acc_green_min.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-acc_green_min2.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-acc_harness.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-acc_l1x.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-flowworks.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-ishko.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-live_20261008.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-live_20261008b.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.before-tier-watchers_live.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T142015.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T161529.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ModsConfig.pre-session.20261007T135600.xml   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ns_flowworks_backup.20261002T070221.json   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ns_flowworks_backup.20261005T142015.json   local ModsConfig backups from earlier sessions; local artifact
?? deployed/config/ns_flowworks_backup.20261005T161529.json   local ModsConfig backups from earlier sessions; local artifact
?? design/RimMandrake/convenience_replacements.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/event_quest_wisdom.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_audit/ACTIONS_NOW.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_audit/FACTS_REGEN_DELTA.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_audit/GPT_PACKAGE.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_audit/GPT_REVIEW_DISPOSITION.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_audit/MASTER_REGISTRY.csv   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_audit/MASTER_REGISTRY.jsonl   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_audit/OWNER_CARDS.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_audit/OWNER_RULINGS.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_audit/RETIREMENT_WAVE_1.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_audit/RETIREMENT_WAVE_1_RUN_SHEET.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_audit/assessments/   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_audit/checks/   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_audit/merge_inputs.json   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_audit/records/   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_audit/review_amendments.json   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_deepdive_art_rule.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_deepdive_faces.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_deepdive_industry.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_deepdive_offtone.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_deepdive_oldwhy_removal.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_deepdive_yayo.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_deepdive_yayo_acc_sim.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_deepdive_yayo_armor_sim.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_deepdive_yayo_full.md   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? design/RimMandrake/mod_deepdive_yayo_full_sim.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? infrastructure/state/cherrypicker/CherryPicker.SHIP.WAVE1_CANDIDATE.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? infrastructure/state/cherrypicker/CherryPicker.SHIP.WAVE1_CANDIDATE_PLUS_SHELLS.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? infrastructure/state/handoffs/FOUNDRY_HANDOFF_202610101109.md   FOUNDRY (this window)
?? infrastructure/state/items/ASHKARR_PAINTER_NAMES_DIVERGED_1.md   BENCH (item files filed by another window)
?? infrastructure/state/items/FALL_LINE_MAJOR_REGION_LABEL_1.md   BENCH (item files filed by another window)
?? infrastructure/state/items/TWILIGHT_ART_REUSE_ELSEWHERE_1.md   BENCH (item files filed by another window)
?? infrastructure/state/modlists/ModsConfig.WAVE1_CANDIDATE.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? infrastructure/state/modlists/ModsConfig.WAVE1_CANDIDATE_PLUS_SHELLS.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? infrastructure/state/modlists/manifest.WAVE1.json   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? skills/rimworld-crew-and-nemesis-events/   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? skills/rimworld-custom-incidents/   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261008T212615.json   GSS/FlowWorks run output from BENCH/earlier belt; local artifact
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_live_20261009T180159.json   GSS/FlowWorks run output from BENCH/earlier belt; local artifact
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_live_20261009T180402.json   GSS/FlowWorks run output from BENCH/earlier belt; local artifact
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_result_20261009T181630.json   GSS/FlowWorks run output from BENCH/earlier belt; local artifact
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_result_20261009T182325.json   GSS/FlowWorks run output from BENCH/earlier belt; local artifact
?? src/RimMandrake/Utils/modaudit/depgraph.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? src/RimMandrake/Utils/modaudit/dotnetmeta.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? src/RimMandrake/Utils/modaudit/facts_delta.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? src/RimMandrake/Utils/modaudit/gpt_package.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? src/RimMandrake/Utils/modaudit/merge_checks.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? src/RimMandrake/Utils/modaudit/selftest_merge_checks.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? src/RimMandrake/Utils/modaudit/wave1_save_preedit.py   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? src/RimUtinni/UtinniPatches/Patches/BetterInfestations_SilenceOwnEvents.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
?? src/RimUtinni/UtinniPatches/Patches/Bones_CutFuelAndPlasteelRecipes.xml   subagent of this FOUNDRY window; already published to origin via land.sh (clone is stale)
```

