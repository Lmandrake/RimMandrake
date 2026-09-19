# BENCH_REBOOT_HANDOFF_202609091702 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609082018`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

`design/Jawa/worldbuilding/biomes/rosters/*.json` is now the SINGLE source of truth
for what lives and grows where. Every downstream artifact derives from it: the cast
(`rosters_to_cast.py` → `gen_cast_patch.py`), the RUT_ def wildAnimals, the de-dup
union, the wildBiomes eviction strip, the stat/tolerance/flammability patches, the
flora FAMILIES, the three review sheets, and the analyses portfolio
(`rosters_residency.py`). Never hand-edit downstream; edit the roster, regenerate the
chain, and REBUILD THE SHEETS (their `c:`/`nd:` row-ids are positional — an array
shift lands verdicts on the wrong entry). The owner's overrides flow back through
`review/apply_assignment_verdicts.py`, which refuses an untouched prefill.

## What the owner should see

- **The verdict sitting is ready** (`ASSIGNMENT_SHEETS_VERDICT_SITTING_1`): three
  click-tested sheets — `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\fauna_assignment_register.html`,
  `...\flora_assignment_register.html`, `...\creature_art_register.html`. Contested
  groups first; my invented calls are declared in each page (Mynock two-home,
  Aerofleet-as-Fumerider, Dunealisk/Skalder imports, all commonality values).
- ⚠️ **His Chrome windows were force-killed ~17:00 by a test agent** chasing a dead
  CDP route (incident + lesson logged). Nothing else touched.
- **Deploy is HELD** — the game still runs the OLD fauna; the assignment patches ride
  the next load round, entangled with the other window's ownership-wave files.
- **Muffalo has no wild home** (in-joke keep, unplaced) — one card.
- **Interim numbers he can veto**: animalDensity 0.2/0.1/0.1/0.15 on nightside+seas
  (were 0 — landed fauna could never spawn); shrubland stand-in flora Flammability→0.
- **Three rulings ready as one-liners**: mech raids deny planet-wide (draft table,
  `d927f4b7`) · staged lore descriptions FEASIBLE ~1.5 days (`672051c9`) · Alpha
  top-5 comps to own (`5c4f237d`).

## What is half-done, and where it stops

- **Assignment deploy**: repo complete; next action = batched
  `deploy_custom_mods.py --mod UtinniPatches --apply` at the next load round, AFTER
  reconciling with the other window's uncommitted ownership-wave files in the same
  plan (their RUT_Sump/Forge/Rot/Umbra defs, GeothermalDensityField, SandFishing).
- **FISH_BY_BIOME_1**: greentide gap (RSW fish are wired to the Miasma, not
  BiomeCypreJungle/RUT_Greentide — and which of those two is live is unresolved) +
  cracked-lands is the other window's sand-fishing; reconcile before closing.
- **WORLDMAP_FINAL_REVIEW_1**: deliberately NOT started — the paint is mid-churn
  under the ownership wave; run its Phase-0 fresh exports after the switches settle.
- **TITANIC_CREATURES_MOD_1**: design complete + decompile verdict in; first build
  step is the Large Pawns bridge quicktest (bs 12 spawn, occupancy by getter).
- Uncommitted tree at wrap: everything non-Transient below is another seat's or
  hook-owned (MODE, CODE_REVIEW_STATUS, codebase_health, the .lock files); my only
  uncommitted line is the WORLDMAP defer note + ledger, committed with this handoff.

## Traps learned

- figF2 counted dead-temp flora off the 08-23 `plant_pool.csv` snapshot: 46 claimed,
  6 real against the live dump (LESSONS_INBOX filed).
- `plant_tolerances.py` + `biome_flora.py` + `biome_commonality_zeroed.py` all
  carried dead output paths from JAWA_PATCHES_SPLIT_1 and returned confident cleans;
  a regeneration would have silently reverted 508 tolerance ops. Fixed this pass.
- The shared git index swept my staged files into another window's commit
  (`9411247f`) — content safe, provenance muddled; stage-and-commit atomically.
- GR_ ≠ Grindterra (GRim*): a prefix guessed in a ruling propagated into six agent
  batches before the first report caught it; verify identifiers before recording.
- Sheet-claimed "already assigned" decays: the greentide fish claim didn't survive
  one grep.

## Closed since the last handoff (3)

- `WEEPING_STONES_ROSTER_1` — 5851917a
- `BIOME_FLORA_ROSTER_GAP_1` — 32f9d25d
- `BIOME_FAUNA_ASSIGNMENT_SITTING_1` — d19997bd

## Filed and still open (4) — the next seat's queue

- `WORLDMAP_FINAL_REVIEW_1` — Studio-grade final worldmap review: measured audits (rivers/roads/mutators/landmarks/settlements/biomes/landforms) + full-planet screenshot STARE + te
- `PLAYER_START_SITE_1` — The formal player start site: Hutt junkyard of ruined ships + old megastructures — lore fixed by Scenario_Utinni + fall_line.md; candidates measured (
- `COMPANION_SILENT_FAILURE_HARDENING_1` — Harden the JawaBench companion against silent-failure modes (39-finding audit): success:true hardcoded across 7 world tools, playerForced missing on p
- `ASSIGNMENT_SHEETS_VERDICT_SITTING_1` — Owner verdict pass over the two assignment review sheets (fauna 372 rows / flora 313 incl. NEW-ART ledger) — overrides amend rosters/*.json and regene

## Commits

```
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
8028b316 FOUNDRY reboot handoff 202609090517
437b8b81 Port Lumi.doorsexpanded's blast doors into StarWarsPatches (BLASTDOOR_LUMI_PORT_1)
a085bf59 Mynock custom art (south/east/north): hideous wet practical-effects redesign
2ed52d77 Review C-series doc sync: one_map water bodies, world-def roster note, mutator census superseded in place; five B-series items filed for FOUNDRY
9ad92b7c Punch list: text rulings + cap roads patch + island canon + waterline owned (owner rulings, 2026-09-08)
4975090f PLAYER_START_SITE_1 ruled: Zeddo's Yard (Fall Line, tile 17007 cluster) is the formal start anchor — owner's card, 2026-09-08
afa5ac40 File PLAYER_START_SITE_1: the Hutt junkyard start — lore fixed, two candidates measured and staged (owner, 2026-09-08)
ec0694fe WORLDMAP_FINAL_REVIEW_1: the studio review report — verdict THE MAP pending 11-item punch list
6c8cf269 File + claim WORLDMAP_FINAL_REVIEW_1: the studio review plan (owner's charge, 2026-09-08)
6714f03f Ring: band-limited war-debris strip replaces the moire one (owner picked over Saturn revert, 2026-09-08)
c536d804 File GAPING_DOOM_SITE_1: dead-sarlacc waste pit at tile 2403, green-throat art spec (owner, 2026-09-08)
b92adbbd Complex-structures icons: wet-green biomes ruled out (owner, 2026-09-08)
e9c90d7b Ledger: BIOME_FREEZE_FABLE_REVIEW_1 + SETTLEMENT_REJIGGER_ROUND2_1 closed on owner's word — both already performed and adopted
d88d0117 Poison Forest: measured arc envelope recorded, owner accepted — last open distribution question closed; map distributions freeze-ready
87bea559 Sheets: fold today's ruled repaints into the receiving sides (freeze-sweep follow-through)
36952ad4 Ledger: both Propane Lakes conversion items dropped on owner's card ruling — sheet strategy is bend-the-donor; RUT_PropaneLake (lake water def) stays
9656a389 Canon CSV: sync biome column to live V26 — 5,258 tiles of un-synced repaint history (coldside re-partition, fungal merge, poison forest expansion); drift now zero, all other fields already matched
f9f65d2f Worldmap sitting: four distribution rulings landed (owner, 2026-09-08)
f91877bc File BLASTDOOR_LUMI_PORT_1: port Lumi.doorsexpanded's blast doors before retiring it
a5020486 Worldmap sitting: Propane Lakes harmony pass + Rot cold-tail repaint (owner rulings 2026-09-08)
ddad4e68 Armoury: regen Armour_Leather.xml and Armour_Ratings.xml, confirmed real drift
d1c2c008 UTINNI_SHELL_DEFNAME_BUG_1: root cause is upstream (VBE), cosmetic only
e9304377 Ledger sync: Propane Lakes picked as next biome conversion — SELF_CONTAINED_BIOME_1 + WORLD_SWITCH_1 filed for FOUNDRY; bridge taken for worldmap sitting
cdd3b907 LanternDeeps: declare the two host-biome mods GenStep_ScatterCavePortal checks for
618f9486 RaidRedesigner: guard PropertyEngine.Fire, don't hard-declare it
555ef84b StarWarsRaces: guard DefModExt_HeadTypeStuff with MayRequire=neronix17.toolbox
ef628781 Oracle: rewrite transport to shell out to claude -p, per owner's 2026-09-05 ruling
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
 M infrastructure/state/items/WORLDMAP_FINAL_REVIEW_1.md
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
?? "D:\\Luke\\dev\\Rimworld\\Transient\\bench_tools_dump.json"
?? infrastructure/state/CODE_REVIEW_STATUS.json.lock
?? infrastructure/state/codebase_health_last.json.lock
```

