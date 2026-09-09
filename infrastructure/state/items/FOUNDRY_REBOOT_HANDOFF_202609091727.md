# FOUNDRY_REBOOT_HANDOFF_202609091727 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609090517`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

A dispatched agent's own output can be genuinely dangerous even when it compiles clean, and only a human-level review catches it: BIOME_OWNERSHIP_WAVE_1's first pass authored 22 BiomeDef files whose `<defName>` was IDENTICAL to the vanilla/donor def each was meant to replace. That is not a silent no-op — `DefDatabase<T>.Add` (Source/Verse/DefDatabase.cs) logs a red error AND randomizes the NEW def's name on every load, so it would have thrown 22 load errors on every launch while the "ownership" itself never took effect anywhere (the donor def keeps its clean name and stays what every tile actually resolves to). Caught by grepping every new file's actual `<defName>` against its filename before staging — never trust that a file named `RUT_Foo.xml` necessarily declares `defName RUT_Foo`. Sent back, fixed, re-verified two ways (repo-wide grep + against the live 590-mod def dump) before commit. Generalizes: any BELT wave that authors many similarly-shaped new defs needs this exact check before staging, every time.

## What the owner should see

- Four candidate-review contact sheets are waiting on his pick, already sent to him as files this session: desert-wrap style candidates (DESERT_WRAPS_ART_COMMISSION_1, `Transient/art_review_desert_wraps/`), planetary beauty shots for load screens (PLANETARY_BEAUTY_LOADSCREENS_1, `Transient/planetary_beauty_loadscreens_contact_sheet_2026-09-09.png`), the Blue Desert world-switch render (post-hoc — the item wanted a mock BEFORE painting, but the live paint had already happened before I picked the item back up; sent as a look-and-object check instead), and the generic Graffiti marks contact sheet.
- `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1`: a Fable design pass (`design/RM_GRAFFITI_SCOPE_WIDENING.md`) is ready with 10 named open forks (F1-F10) for his ruling — nothing built yet, by design.
- `BIOMESKIT_RENDER_LAYER_MISSING_1`: a live worldmap screenshot taken this session shows biome decoration icons ARE rendering right now, contradicting a decompile finding that the loaded 1.6 BiomesKit.dll is missing its render class entirely. Genuinely unresolved which mechanism is drawing them — filed as its own item, needs a fresh hunt.
- Droid personality chain (B1/E1/E2) all landed this wave, but every live-verify checkbox on all three items is still unticked — nothing has been proven running in an actual game yet, only against decompiled source and static analysis.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `DESERT_WRAPS_ART_COMMISSION_1` — candidates stage delivered (4 wrap styles, 2 head shapes, `Transient/art_review_desert_wraps/`), sent to the owner. Next action: his pick, then full body-type-matrix production art (separate pass).
- `GAPING_DOOM_SITE_1` — offline half (art + LandmarkDef) was already complete from a prior session before I picked it up this wave; confirmed, nothing new built. Next action: live placement at tile 2403 + display-name set to "The Gaping Doom" — but the rename tool may not exist yet (LANDMARK_NAMING_PASS_1 found `jawa/world_landmarks_set` has no name param). Check/add the rename route via rimbridge-companion before attempting placement.
- `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1` — Fable design doc delivered (`design/RM_GRAFFITI_SCOPE_WIDENING.md`), 10 open forks (F1-F10) named for the owner. Next action: his ruling on the forks, then a build pass.
- `KOTOR_CRYSTAL_GENSTEP_DRIFT_1` — NOT touched this session (pre-existing `doing`, filed 2026-09-08, no state carried in my context). Needs=deploy. Whoever picks this back up should treat it as cold — read the item fresh.
- `PITCELL_PRISONER_BED_BRIDGE_GAP_1` — NOT touched this session either. The bridge tool it needed (`jawa/set_bed_owner_type`) was built and committed in a PRIOR session (before my window), per that session's own resume note ("deploys next game-down window") — whether it's actually deployed/verified live is unknown to me. Read fresh.
- `PLANETARY_BEAUTY_LOADSCREENS_1` — 5 candidate orbital shots delivered (`Transient/planetary_beauty_shots_2026-09-09/`), contact sheet sent to the owner. Next action: his framing pick, then wiring to an actual load-screen def (not done — these are unwired candidates).
- `W9_RUN_STAGE_RESULTS_UNCHECKED_1` — NOT touched this session (pre-existing `doing`, filed 2026-09-08). Needs=bridge. Read fresh.

## Traps learned

- **A subagent given a same-defName-collision task will not catch it itself.** BIOME_OWNERSHIP_WAVE_1's first pass produced 22 files whose defName duplicated the vanilla/donor def — see "the one thing to carry forward" above. Filed to LESSONS_INBOX.md.
- **`git commit -m "..."` with no pathspec commits the WHOLE staged index, not just what you just `git add`ed.** In a shared worktree, another window's `git add` can land in your index between your add and your commit. One commit this session (`9411247f`) accidentally swept up 4 unrelated BENCH state files this way. Fix: always pass explicit paths to `git commit` itself (`git commit -m "..." -- path1 path2`), not just to `git add`. Already the documented rule (`git-commit-scope-is-the-whole-index-not-your-add`); this is a second, independent confirmation.
- **`rimflow close --sha <a made-up short name>` silently accepts a non-resolved string.** Closed `DROID_SUICIDE_CHARGE_STATE_1` against the literal string `"c1"` (typed the packet's own short name instead of running `git rev-parse`) — same trap the existing `rimflow-close-sha-head-literal` lesson names for the literal `"HEAD"`. The tool doesn't validate that `--sha` resolves to a real commit. Corrected via a follow-up note (real sha `5c80b179`) since a closed item's own sha can't be edited.
- **A raw hediff-severity poke via `jawa/pawn_health` does not trigger vanilla's needs recompute.** `Hediff.Severity`'s setter dirties the disabled-needs CACHE (`HediffSet.DirtyCache`) but never calls `pawn.needs.AddOrRemoveNeedsAsAppropriate()` — that only fires from `HediffSet.AddDirect`, once, at whatever stage the hediff was at when first added. DROIDWORKS_FORMAT_TIERS_1's 2026-09-08 live-quicktest FAIL was entirely this artifact, not a real defect — the shipped mechanism (`DroidFormatTierUtility.SetTier`) already calls the recompute correctly. Any future bridge-driven "change a hediff stage and check needs/behavior" test needs the real player-facing path (a bench recipe, `jawa/bill_add`), not a raw severity write.

## Closed since the last handoff (26)

- `DROIDWORKS_WIP_SWEPT_NOTICE_1` — 8028b3166224dcc0640bd5d558c2f25a830c8154
- `DROIDWORKS_MODULE_SMELT_CONFIG_1` — 671ff569f5ab9505ea7f8919892adaaf9105e83a
- `MOD_LICENSE_PERMISSIVE_1` — af0f1280270b1ec9c19686c5a0442c281ae0dcdf
- `MANYWATERS_GENERIC_SPLIT_1` — bc990fe952e57be39ddba79c1b95cade915e8c74
- `OASIS_MUTATOR_PATCH_1` — c9af67d3e6abc8e8c0292319a459a7759e6efd10
- `CHRONICLE_EVENT_SPINE_1` — 2502b4013cce72583c0df39a0768b52ddcc3abc7
- `EGG_PROXIMITY_HATCH_TRIGGER_1` — 757b3dd9003925b256386df78114eb69bf6d1b51
- `RIMPROPERTY_ANIMAL_THEFT_1` — fc173df3141b5bb9c30d7484342f1b66130f8d27
- `WORLD_RIVER_COLORS_1` — 6b41346e146a23d70a790d3faf98f673c6b665d2
- `BLUE_DESERT_WORLD_SWITCH_1` — c3e1dcb9fe19e7da4e08f2f42c7f90e1c72b41fa
- `MOISTURE_FARM_TEMPLATES_1` — 5b34a08c704a94c2a5df158278a24881d71e1330
- `GEOTHERMAL_DENSITY_FIELD_1` — a56f62036b79c6296006cb6047a907ac72f9ba91
- `FUNGAL_SOIL_TRADE_1` — ebde00db13689662d7c68f9851d92480c0accff5
- `GRAFFITI_GENERIC_MARKS_1` — b9ac45cbeb32eff068a0eca0ac1ca32055b8eb65
- `UNDERWATER_BIOME_SUPPORT_1` — 8e4bce2b
- `SAND_SWIMMERS_MOD_1` — 9f8bc41f51704e8e22d32c9fed08cd8dacb7a092
- `SCALD_DARK_TOWER_1` — da71770dcf5dca487185b6a99cdb1e04b5e6399a
- `VFEPD_HORSECART_IDENTITY_LEAK_1` — 0a34f66f1eb2af734c0872a694bdbb413eca5e30
- `ASHKARR_REGATE_RAIN_DEAD_1` — 58464a319e64dfdc21e0b2d55c2df800c2849750
- `TITANIC_CREATURES_MOD_1` — 0c8238cb454739a499a4cde68a034b94faf57b08
- `WORLDMAP_BIOME_ICONS_REGEN_1` — 025218df
- `BIOME_OWNERSHIP_WAVE_1` — cc11aee6e5ed391ed0b79d1299f9bec0d3bd562e
- `DROID_SUICIDE_CHARGE_STATE_1` — c1
- `PYRELANDS_GENERIC_TEXT_1` — a3e5ba3d711acf1348ee56792a44335e23c23ca9
- `DROIDWORKS_CHASSIS_PERSONALITY_1` — a64a10221bab7be5bb7cd8b6ba07d269c1c24d56
- `DROIDWORKS_SERVICE_RECORD_DRIFT_1` — a6a74c7abf09ea3b20bae549935bd6751a9d660a

## Filed and still open (4) — the next seat's queue

- `MANYWATERS_COLOR_SUPPORT_1` — ManyWaters: support many colors of water and many colors of slime
- `PLANETARY_BEAUTY_LOADSCREENS_1` — Render realistic planetary beauty shots from space for load screens (graphics pipeline)
- `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1` — Widen base RM Graffiti scope: punk/urban graffiti register + ideoligion-inspired sigils (vanilla ideos), RUT fills in richly after
- `BIOMESKIT_RENDER_LAYER_MISSING_1` — BiomesKit's 1.6 DLL dropped BiomesKitWorldLayer entirely -- worldmap decoration icons' current source unknown

## Commits

```
a6a74c7a Droid service-record drift (E2): idiosyncrasies accrete unwiped, wipe erases them
a64a1022 Droidworks chassis personality (E1): per-family forced traits + protocol pedantry
a1715336 BENCH reboot handoff 202609091702: assignment pass complete end-to-end, verdict sitting staged, worldmap final review deferred until the ownership switches settle
5c4f237d ALPHA_FAMILY_SOURCE_REVIEW_1: Alpha family mechanics inventory (DRAFT, needs-owner)
672051c9 STAGED_LORE_DESCRIPTIONS_1: feasibility half executed — every display path traced to 1.6 source
10170354 FISH_BY_BIOME_1: fishTypes patch for weeping_stones/ZBiome_DesertOasis
0d59c15a CREATURE_ART_REVIEW_SHEET_1: full 277-row true-scale sheet built (b459ec0a); four of six 09-06 art subjects are already off-planet — flagged for the owner
b459ec0a CREATURE_ART_REVIEW_SHEET_1: full creature-art register at true in-game scale (277 rows, 25 biomes)
46a11b2d Live worldmap screenshot: biome decoration icons ARE rendering right now
a3e5ba3d Fix stale Pyrelands text drift after the R9 self-contained biome build
cc11aee6 Own 20 more BiomeDefs (BIOME_OWNERSHIP_WAVE_1): 22 donor-painted defs to our own control
248c7121 Close BIOME_FAUNA_ASSIGNMENT_SITTING_1 — solo pass complete end-to-end; successor is the owner verdict sitting
d19997bd Assignment pass: deploy deliberately held — plan entangled with the other window's ownership-wave files; rides the next load round
9bf47100 Flora portfolio: correction note on figF2's stale-source 46 (6 real against the live dump); lesson filed
9e2fad92 Regenerate the flora review sheet after the roster edits; record the fix wave's outcomes on the item
e0983a4f Flora fix wave: ban 9 zeroed (10 kept, no donor exists), and plant_tolerances.py stops dissolving its own output
d627a0ce Planetary beauty shots: 5 orbital load-screen candidates (PLANETARY_BEAUTY_LOADSCREENS_1)
9574513a A liquid-propane sea grows nothing: flora_def_exclusions, and RUT_PropaneLake loses its four inherited flora rows
0c8238cb Titanic Creatures: multi-cell footprint, destruction wake, tiering, T3 corpse-as-site
025218df animalDensity: the four water/ice biomes could never spawn their landed fauna (0 -> designed interim)
58464a31 Delete ashkarr_regate_rain.py: confirmed permanently non-viable dead file
8be234dd FungalSoilTrade: fix a silently-blanking quest description + comment drift
9411247f ProximityHatch: don't aggro a bystander pawn of the same kindDef
0a34f66f DesertVehicleReskin: fix the 4 VFEPD prop identity leaks found in review
23ab927a Desert wraps: style-candidate art for the owner's pick (DESERT_WRAPS_ART_COMMISSION_1)
0c9c0cff ManyWaters: river-steam puff angle silently dropped the top of its range
5838bf37 Evictions: skip races installed on disk but not in the live mod set
6c8ea862 Instrument findings recorded: fig6 gate near-zero; shrubland ban-9 flammability violation (10/10) and 46 dead-temp flora rows queued as the fix wave; titan tier census into the ticket
65befe8a Flora portfolio (figs F1-F3) + climate/flammability sources; portfolio notes rewritten to the post-assignment state
dad4e548 Sheets click-test PASSED (controls fire, writes land, file restored); log the chrome.exe kill incident + lesson
9a69acce RimProperty: JobDriver_RM_AnimalSteal under-reserved stacked targets
da71770d Scald dark tower: Rakatan high command, KCSG structure + Rust Cathedral tie
8367eec5 figs 9-11: commonality mass, size ladder, biome matrix — the assignment's own three pictures
9f8bc41f Sand swimmers: RM_DeepSand fishable terrain + Star Wars fish family
90940c68 MECHANOID_BIOME_PRESENCE_REVIEW_1: draft table + planet-wide no-mech-raids doctrine proposal ready for the owner
339aba05 Pyrelands: correct the BiomeWorker calibration comments' wrong arithmetic
8514782a FISH_BY_BIOME_1: census + rulings landed as data; reconcile flag for the concurrent sand-fishing work in the shared tree
d927f4b7 DRAFT: mechanoid/ancient-danger presence table per painted biome (MECHANOID_BIOME_PRESENCE_REVIEW_1)
f18fb5de Fish candidates data pass: 87 fish ThingDefs MEASURED, biome-side fishTypes binding confirmed, per-water donor candidates for the four fish=YES biomes
b56daf72 Verdict sitting item: record the positional row-id trap and the move/purge note requirements from the applier build
e76f0ae0 Residency reads from the rosters, not the register: rosters_residency.py + repoint fig6/fig7, explorer, deck, fiftyone
a5b68a38 TITANIC_CREATURES_MOD_1: ride-with-config verdict from the Large Pawns decompile — OccupiedRect integration, one-ladder rule, its wall-break off, 4x4 ceiling, pen/caravan/perf watch items
8f1e5c49 Assignment review loop: the CONSUMER (apply_assignment_verdicts.py)
ea334c83 Close the enforcement gap: strip race.wildBiomes for non-rostered creatures
2e89ebf4 biome_commonality_zeroed --ours was reading a path that does not exist
017af47c Research: decompile Large Pawns (neku.largepawns) for TITANIC_CREATURES_MOD_1 — verdict ride-with-config
15118a6c Design: widen RM Graffiti to a real functionality engine (punk register + ideoligion sigils)
32f9d25d Flora: FAMILIES rewritten from the rosters; the doc regenerated
d35711b0 ASSIGNMENT_SHEETS_VERDICT_SITTING_1: spec + verify (serve, touchedBySheet gate, applier flow, freeze)
2946edf4 Ledger: close WEEPING_STONES_ROSTER_1 (landed in the roster wave at 5851917a); file ASSIGNMENT_SHEETS_VERDICT_SITTING_1 (needs owner)
b9ac45cb RM Graffiti: 3 generic vanilla-register example marks (R7)
5ab12982 De-dup union: 43 -> 193 pairs, and it now reads OUR OWN cast
1d0f0a31 Stat adjustments the rosters ruled, as one generated patch
793a5bc5 RUT_ biome defs: wildAnimals landed from the rosters
90727e48 Fauna cast now derives from the biome rosters, not the scoring model
ebde00db Fungal soil trade: mineable Rot resource, dig-distress fauna response, trade quest
ea13dfc3 File TITANIC_CREATURES_MOD_1: owner-ruled design — Large Pawns (ACTIVE, found) + destruction wake, thin/thick roof law, auto tiers + curated crush-table, T3 corpse-as-site
1bae4258 Owner review sheets for the landed fauna/flora assignment (BIOME_FAUNA_ASSIGNMENT_SITTING_1)
a56f6203 Geothermal density field: gate geyser count by world position (R12)
77a61de0 DesertVehicleReskin: correct a stale comment on the Seed regression guard
9445450d DroidRepairJobs: split the Destroyed-outcome HistoryEventDef from Kept's
a4b734f3 Assignment pass: _global.json derived (767 live wild MEASURED = prep calibration; 242 rostered, 486 reserve, 88 cuts) + consolidator and validator gates
5851917a Assignment pass: all 28 biome rosters landed (29 painted defs + injections), cross-validated
5b34a08c Moisture farm templates: 5 rimplace plans for the Badlands (homestead, vaporator field, cistern head, walled compound, ruin)
c3e1dcb9 Blue Desert world switch: repaint BiomeGRimond's 1,029 tiles live, sync canon CSV
beffcc4e File BIOME_OWNERSHIP_WAVE_1 (owner, 2026-09-09): own all ~22 donor-painted biome defs for parameter+assignment control; donors stay installed; ledger sync
23e56195 Assignment pass rosters, batches B+F (8 biome defs): nightside/poison/crags/cathedral + the four waters — validated (_validate.py gate added)
24366098 Prefix correction: Grindterra is GRim*, not GR_ (GR_ = VGE chimeras, judged per sheet law) — ruling text fixed, batch-B rosters being re-adjudicated
6b41346e World river colors: gradient mock + WorldDrawLayer_Rivers Harmony patch
fc173df3 RimProperty: droid-loader theft-hauler patches, trainable pet theft, wild-animal theft
757b3dd9 Egg proximity-hatch trigger: mandrake.rm.proximityhatch, wired to RSW_ProtovermesEggFertilized
bffb5432 BIOME_FAUNA_ASSIGNMENT_SITTING_1: record the wildBiomes enforcement gap — cast replacement alone cannot evict; animal-side strip required
e4fd2529 Def↔sheet binding table for the assignment pass: 29 painted defs bound and verified, cast ownership mapped (gen_cast_patch.py owns 23, RUT_ defs own 5, BiomeGRimond donor-only)
be58cb0c Delete the three dead fauna/flora docs instead of superseding (owner ruling 2026-09-09); fix all inbound refs; doctrine updated in CLAUDE.md
ba88416d BIOME_FAUNA_ASSIGNMENT_SITTING_1: owner rulings 2026-09-09 — BENCH executes solo, land-then-review; homeless pool = reserve; SW staples adjust-and-keep; Earth flora purged
5ed3e2a1 Own BiomeDef for the Blue Desert; supersede the wrong solo divvy pass
95e2c5e1 Move hardening + ultra-review-prep audits into the repo (design/Jawa/reviews); write up COMPANION_SILENT_FAILURE_HARDENING_1 (13 done / ~26 deferred)
02d0bb2a Companion hardening batch 3: battery_set setPct clamps 0-1 like its sibling modes (avoided Mathf — no UnityEngine using in this file)
a31cb23d Design: programmatic gravship-launch companion tool (deep-source research) — render-free primitives, the one unverified call, scratch-only test plan
6aecd542 Companion hardening batch 2: pawn_gear honours explicit stuff (was silently discarded); bill_add gets configure_bill's quality enum+range guard
ff4a77d1 Companion hardening batch 1 (10 fixes from the silent-failure audit): success derived from real outcome, not hardcoded
333d5794 World FROZEN canonical (owner, 2026-09-09): CANONICAL_ASHKARR_2026-09-09.rws is the sole save; 20 prior saves archived; world edits closed without explicit unfreeze
4d739565 First-pass biome fauna/flora divvy across all 29 canonical biomes (baseline)
fce77fa0 Gaping Doom: green-throat art + RUT_GapingDoom LandmarkDef (deployed); enrichment plans landed in design/ out of Transient
201a39b0 PLAYER_START_SITE_1: flight-attempt finding — bridge cannot drive the gravship launch (running time destroys staged state); crewed checkpoint is the durable handoff to a hands-on launch
91c06863 File MANYWATERS_COLOR_SUPPORT_1's design proposal (Fable, backgrounded)
c9af67d3 Oasis mutator: whitelist ZBiome_DesertOasis, strip donor snow weathers
bc990fe9 ManyWaters river-steam: split ZBiome_Grasslands hardcode into RUT data hook
67ed9f07 New companion tool: jawa/set_bed_owner_type (deploys next game-down window)
d502e2e3 New companion tool: jawa/world_landmark_rename (deploys next window) — Landmark.name verified plain scribed field
0fdb4990 LANDMARK_NAMING_PASS_1: 18 hand-names in country voice (fork product) — awaits the rename tool
c711e181 Five bridge lessons from the overnight ship work
71bd2f54 ordered_job sets playerForced (vanilla JobDriver_Refuel.cs:34 killed every unforced auto-gated job); build.py takes ORACLE_MOD_DIR to build against the repo Oracle when the deployed copy lags
97d0d123 Regenerate codebase-health treemap and maturity dashboard (owner request)
452cefe8 w9_run.py: halt on the six unchecked stage failures instead of pressing on
f0ecefd5 Crew spec into the repo (Transient citation rule) — PLAYER_START_SITE_1.crew.json
afeeef6c PLAYER_START_SITE_1 run-sheet: flight sequence + crew spec staged; game down, FOUNDRY owns relaunch
af0f1280 Dedicate all our own mods to the public domain (CC0-1.0)
671ff569 Fix DW plain-tier armor modules (Hvy/Lte/Mid) tripping smeltable ConfigError
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-09T16:36:03Z

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M Transient/codebase_health_hook.log
 M Transient/ring_debris_candidate.png
 M infrastructure/state/CODE_REVIEW_STATUS.json
 M infrastructure/state/MODE
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
?? "D:\\Luke\\dev\\Rimworld\\Transient\\bench_tools_dump.json"
?? infrastructure/state/CODE_REVIEW_STATUS.json.lock
?? infrastructure/state/codebase_health_last.json.lock
```

