# 06 — World remake runbook: gates, rehearsal, start save, rollback (2026-10-19)

FOUNDRY, offline. No game, no bridge, no ModsConfig edit was made writing this. **Owner's choice (card, 2026-10-19,
relayed by the FOUNDRY session): Option D** — the remake makes a **DEVELOPMENT world** that may be repainted later,
and it runs **once, when this written checklist passes**. Inputs: `PLAN.md` §5a, `02_world_pipeline.md`,
`03_ticket_impact.md`, the item files via `rimflow show`, and the tools named below (each one was opened, not
recalled). Labels: **MEASURED** (read today, instrument named), **RECORDED** (another doc says it, cited),
**UNMEASURED** (nobody has measured it). A gate whose instrument does not exist says **NO TOOL**.

An agent executes this **with the owner present**. Steps marked 👤 are his hands or his eyes; nothing marked 👤 is
done for him. Steps marked 🔴 cannot be undone inside one run.

---

## 0. Corrections found while writing this (they change what is owed)

1. **Ideoligion tooling exists.** 02 §2/§7 and PLAN.md §4A say no tool sets the twelve fixed ideos after creation.
   The JawaBench bridge has `jawa/faction_ideo_set` (reads `ideoName`/`ideoDescription`/`deityPresets` off the
   FactionDef, calls `FactionIdeosTracker.ChooseOrGenerateIdeo` with `fixedIdeo=true`), plus `jawa/ideo_create`,
   `jawa/ideo_set_primary`, `jawa/faction_ideo_get` (`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchIdeoTools.cs`,
   `JawaBenchSocietyTools.cs`). **Never run on a fresh world on the candidate list: UNMEASURED.**
2. **A faction absent at creation is not absent forever on a dev world.** `jawa/faction_create` exists
   (`JawaBenchFactionTools.cs`): "the only route for a faction that is ABSENT from an existing world". Never run for
   one of our factions: UNMEASURED. On a development world this demotes `HORRORS_RAIDING_FACTION_1` from a hard
   prerequisite to a "create later" (§5, row 31).
3. **The scenario does NOT arrive by gravship.** `Scenario_Utinni.xml` has `ScenPart_PlayerPawnsArriveMethod`
   `<method>Standing</method>`, so GravshipExport's `Page_ChooseGravship` (shown only for gravship arrival,
   `skills/gravship-layout` §Loading a layout) never appears. The ship goes in by **`print_gravship.py`** on the
   landed map (§1, step S10).
4. **The scenario already spawns a bonded `RSW_Ikee`** (`ScenPart_StartingAnimal`, `bondToRandomPlayerPawnChance
   1.0`) — bonded to a *random* starting pawn, not Yeku. The re-bond is therefore a **move**, not a creation (S12).
5. **`w9_run.py` has no input-path flag.** It hard-codes `world/ASHKARR_WORLDMAP_{tiles,links,settlements,mutators,landmarks}.csv`
   (lines 64–68). The remapped CSVs (02 §7 items a–c) can only be stamped by overwriting the tiles RECORD
   (`ASHKARR_WORLDMAP_tiles.csv.frozen.json` guards it) or by adding a flag. **Owed: an `--inputs DIR` flag** (G7).
6. **`WORLDGEN_FACTION_CHECKLIST.md` is stale for this list.** Section 4b names `Jawa_*` defNames; the 536 dump has
   them as `RUT_Jawa_*` (02 §3, MEASURED). Its Section 4 keeps name third-party mods (`JDSCIS_CIS_Faction`,
   `guy762_KotORFaction_RogueDroids`) whose presence on the candidate profile is UNMEASURED. Rewrite it from the
   frozen profile before S5.
7. 🔴 **`measure` cannot count plants or animals on a map.** Its artifact registry classes `*.rws` as "Ludeon's format;
   no format work is possible or planned … Asking a COUNT of anything grid-borne is not [legitimate]", and names
   `rimbench/savemap.py` or the live bridge as the instrument (`measuring-large-artifacts/scripts/measure/artifacts.py`
   lines 78–96). The per-biome spawn gate (G13) therefore uses the bridge mapgen row, with its own sanity probe.

---

## 1. (a) The start-save procedure, end to end

Nothing here has ever run end to end on any list (02 §7, RECORDED). Every duration is UNMEASURED unless cited.

| # | step | tool / route | who | notes |
|---|---|---|---|---|
| S0 | **All gates in §2 read PASS**, written into this file's §2 table with date and evidence path | — | agent; 👤 signs | Any FAIL or NO-TOOL gate without his waiver stops here |
| S1 | Checkpoints C1–C3 (§4) | `cp` | agent | before the game starts |
| S2 | Cold load on the **frozen candidate profile**; arm a def dump (`dump_request.txt` = `all`, delete after) | Steam launch; `./game --why "remake cold load" loading` | agent (bridge holder) | Record wall-clock launch→main menu. 536 list: UNMEASURED (02 §2) |
| S3 | Worldbuilder preset 7 subdivisions / coverage 1.0 → 21,872 tiles; re-load the preset in the UI | `python3 src/RimMandrake/Utils/set_planet_subcount.py 7` **after** launch (AlienWorlds rewrites the preset folder each launch, 02 §1b) | agent; 👤 re-load click | Tile count is geometry-only (02 §2, MEASURED 2026-08-17) |
| S4 | Pick the scenario **Scenario_Utinni** | UI | 👤 | ScenarioDef in `src/RimUtinni/UtinniPatches/Defs/ScenarioDefs/Scenario_Utinni.xml`; six `ScenPart_ConfigPage_ConfigureStartingPawns_Xenotypes`, Standing arrival, bonded Ikee, 40 Anomaly `DisableIncident`s. Anomaly playstyle is a difficulty setting the scenario cannot force — 👤 sets it (bucket B, `rimworld-scenario-building`) |
| S5 | 🔴 **Ideology mode.** Ash'karr was made in **classic** mode and held 1 ideo (`closed/ASHKARR_IDEOLOGY_MODE_CALL_1.md`, RECORDED 2026-08-26). Two routes: **(i)** non-classic at creation, so worldgen gives every `fixedIdeo=true` FactionDef its own ideo; **(ii)** classic again, then `jawa/faction_ideo_set` per faction after S8 | UI; bridge | 👤 decides | Player ideo: load **`src/Jawa/ideoligion/The Salvation.rid`** at the ideo page. Validate it first: `python3 src/RimMandrake/Utils/validate_save_artifact.py "src/Jawa/ideoligion/The Salvation.rid"` → exit 0 (2 = UNMEASURED, not pass). The founders' `Ideo_20` is remapped onto the player's primary ideo (S11), so this must be right before S11 |
| S6 | 🔴 **Configure Factions** — the irreversible hand pass | UI, against the rewritten checklist (§0.6) | 👤 | Screenshot the page before leaving it (`system_screenshot.py`). Roster: Section 4 keeps that survive the profile + Section 4b ours (13 rows, `RUT_Jawa_*` names). Duration UNMEASURED |
| S7 | Generate; at `Page_SelectStartingSite` audit the roster | `jawa/list_factions` (`rimworld-world-editing` §5) | agent | Every wanted defName present, no fiction-breakers. Presence only — settlements read `None` at this screen. Wrong roster ⇒ stop and decide with 👤 (regenerate or `jawa/faction_create`) |
| S8 | Stamp the paint | `python.exe src/RimMandrake/Utils/w9_run.py` (dry), then `--apply` | agent | Inputs = the **remapped** CSVs (G7), via the owed `--inputs` flag. Stages 1 → 2 → 3 → 3b → 4 → 4b → 5 → 6, order is engine fact. Never `--despite-map` / `--despite-abort` |
| S8b | Rescale feature labels (not persisted) | `jawa/world_features_set` loop | agent | `FEATURE_LABELS_SIZED_UNUSABLY_1` |
| S8c | Rename dice-named third-party factions; if route S5(ii), `jawa/faction_ideo_set` for each of ours | bridge | agent | |
| S9 | `jawa/world_commit`, lint, render, **LOOK** against `world/view/ASHKARR_WORLDMAP.biome.equirect.png` | `python3 src/RimMandrake/Utils/worldview.py <save>` | 👤 looks | Then save world-only (~5 MB; ~20 MB means a map is in it — wrong file). Checkpoint C4 |
| S10 | **Land** at the start tile: Zeddo's Yard **17007** (alternates 1621, 17011 — `PLAYER_START_SITE_1`, still `proposed`; 👤 confirms the tile) | UI landing; `jawa/colony_found` exists but builds no map | 👤 picks; agent drives | Save immediately after the map exists (landing chain can wedge, `gravship-layout`). Checkpoint C5 |
| S10b | **Ship.** Copy `ship_build/exported/Gravship_v2_ring_2026-09-12.xml` to a remap copy: `AG_RustedTile` (892 cells, MEASURED 02 §3) → an owned floor 👤 picks (cosmetic ⇒ his permission); drop or replace `RG_BoulderRockMediumSandstone` ×1 and `RG_BoulderRockMediumMarble` ×1 (👤). Then print it | `python.exe src/RimMandrake/Utils/print_gravship.py design/Jawa/worldbuilding/ship_build/exported/Gravship_v2_ring_2026-09-12.paint.xml --center x,z --apply` | agent | Order strip → foundation → terrain → things; `SetFoundation` refuses cells with an under-layer (paint `MetalTile`, then `jawa/set_terrain_layer removeTop`). No GravEngine in the export; the script places it. The four flight gates stay closed until powered/fuelled. Read-back count must equal the layout's thing count. **Remap tool exists (2026-10-20):** table `ship_remap_S10b.json` (this folder), `python3 src/RimMandrake/Utils/ship_remap.py <in> <out>`; committed result `Gravship_v2_ring_2026-09-12.paint.xml` (print THAT file; floors are proposals until 👤 agrees; guarded by `selftest_ship_paint_closure.py`). Checkpoint C6 |
| S11 | **Founders.** Copy the fragments folder **without** `animal_Marquee_AA_Eyeling669122.xml` (the retired Alpha Animals Eyeling). Save the game, quit to menu, splice offline into a **copy** | `python3 design/Jawa/worldbuilding/founders/import_founders.py <copy.rws> --fragments <dir> --dry-run`, then without `--dry-run` | agent | Remaps faction/ideo/map/position/genes/hediffs/jobs/abilities by parsing the destination. ⚠️ Yeku's fragment carries a Bond to the dropped Eyeling: how the importer handles a relation to an absent pawn is **UNMEASURED** — check the dry-run output. 🔴 Owner ruling 2026-08-18/19: *"Please don't write to the savegame file anymore"* — this is an offline save write. It writes a copy and refuses keeper names, but **it needs his word at the sitting** (02 §5.5 already flags the strain). Founder refs last resolved on the 618 list (169, 0 unresolved); **536/candidate list UNMEASURED**. Checkpoint C7 |
| S11b | Decide the scenario's own starting pawns (the chooser made some) — keep, remove, or make world pawns | bridge | 👤 | Not written anywhere; UNMEASURED |
| S12 | **Ikee re-bond.** The scenario Ikee is bonded to a random pawn. Remove that bond, then bond Yeku (`Human470530` in the fragment; new id after S11) | `jawa/animal_bond` | agent | `animal_bond` **refuses when the animal already carries a Bond**. No bridge tool to remove a relation was found: **NO TOOL** for the un-bond half (alternative: destroy and re-spawn the Ikee, then bond — trainability is Advanced via `Ikee_Tuning.xml`, so Obedience can be assigned; untested). World pawn `AA_Eyeling657692`, if it exists in a fresh world (it should not — it came from the old save): 👤 call (`donor_save_residue` step 5) |
| S13 | Save under a new name `ASHKARR_DEV_START_<date>.rws`; censuses | §2 G11 | agent | Checkpoint C8 |
| S14 | 🔴 **Cold reload** of S13 and exercise landing state, founders, ship, a bond read, and one representative map per §2 G13 | §2 G12 | agent | Read the FIRST exception in `Player.log` |
| S15 | 👤 promotes it (or not). Then `git add -f` the world-only save and the start save (both < 50 MB: 5 MB, ~20 MB RECORDED) and `./publish` | git | agent on his word | |

---

## 2. (b) Readiness gates — the checklist

Every gate gets **PASS / FAIL / UNMEASURED**, a date and an evidence path written into the `result` column at the
sitting. UNMEASURED never counts as PASS.

| # | gate | exact command or measurement | bar | tool? | result |
|---|---|---|---|---|---|
| G1 | **Deployed builds frozen** | `python3 src/RimMandrake/Utils/deploy_custom_mods.py` (plan only, every mod) and `python3 src/RimMandrake/Utils/dll_source_stamp.py` per C# mod; record `git rev-parse origin/main` | plan shows no pending writes; every DLL's `.srchash` matches src | yes | |
| G2 | **Ordered creation profile frozen** | parse ModsConfig: `python3 -c "import xml.etree.ElementTree as E,hashlib;p=r'/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml';a=[l.text.strip().lower() for l in E.parse(p).find('activeMods')];print(len(a),hashlib.sha256('\n'.join(sorted(a)).encode()).hexdigest()[:16])"`, compare with the candidate profile file; the ORDER is the file itself (save a copy, sha256sum it) | count and sha equal the candidate's; never compare counts alone (`WORLD_REDRAFT.md` 578≠578) | yes (one-liner; the sha rule is `dumps/REGISTRY.jsonl` `modlist_sha`) | |
| G3 | **Mod settings frozen** | copy `…/Config/Mod_*.xml` to the checkpoint and `sha256sum` them | hashes recorded; no setting changed after | **NO TOOL** (manual copy) | |
| G4 | **Cherry Picker profile frozen** | `python3 src/RimMandrake/Utils/cherrypicker_swap.py --status`; `CHERRY_PICKER_RESTORE_FROM_SHIP_PROFILE` done | live = `infrastructure/state/cherrypicker/CherryPicker.SHIP.WAVE1_CANDIDATE.xml`, live key count 2,177 (the item's own bar) | yes | |
| G5 | **Removed-dependency audit** | About.xml closure: `modset_builder.py` walks `<modDependencies>` forward for a tier; the **reverse** closure of the removal set (which retained mod needs a removed one, PLAN §5b) has no tool; C# string defName refs and `text()=` XPath refs are UNMEASURED (01 line 77) | 0 retained mods depend on a removed one; 0 C#/XPath refs to removed defs | **PARTIAL** (forward closure only; reverse closure, C# strings, XPath: NO TOOL) | |
| G6 | **Names frozen** | `rimflow show` on `BIOME_DEFNAME_MIGRATION_WAVE_1`, `CRACKEDLANDS_FULL_RENAME_1`, `BIOME_TIER_CLEANUP_1`, `PLANT_TIERS_RECONCILE_MOST_ARE_BAROQUE` | all done (or 👤 waives) | yes | |
| G7 | **Stamp inputs valid** | (a) remap tiles CSV biome names to `RM_` targets per `infrastructure/state/facts/biome_paint_list.md` + 👤 call on `RUT_Umbra` ×2,531; (b) mutators/landmarks through `design/RimMandrake/retired_mutators_port_map.json`; (c) settlements `Jawa_X`→`RUT_Jawa_X`; then resolve every def name in all five CSVs against the frozen dump; then `w9_run.py` dry run | 0 unresolved names; dry run clean | **NO TOOL** for (a)–(c) and the resolver (02 measured with a one-off subagent script); `--inputs` flag owed (§0.5) | |
| G8 | **Worldgen workers safe** | every BiomeDef on the profile: `workerClass` resolves, or `generatesNaturally=false` (a worker-less natural biome crashes ALL worldgen, `rimworld-world-editing` §5a); `RM_LanternDeeps` and `RM_Seabed*` are UNMEASURED (02 §6) | 0 worker-less natural biomes | **NO TOOL** (one-off script) | |
| G9 | **Authoritative layers exported and compared** | name the authoritative save (👤): `CANONICAL_ASHKARR_START_2026-09-12.rws` was edited in place after 09-12 (its `.bak-pre-*` trail runs to 2026-10-19). Export roads, rivers, mutators (27,856), landmarks (3,008), settlements (96 NPC), factions, names, features, worldTags; compare tile IDs, edge topology, assignments and settlement identities against the stamp CSVs — not counts | 👤 accepts every listed loss | **NO TOOL** — offline readers exist (`worldmap.py`: biome/scalars, settlements, landmarks, features; `ashkarr_rebase_from_save.py`: tiles, live), no exporter for links/mutators/landmarks and no comparer | |
| G10 | **`AB_PropaneLakes` contradiction settled** | `python3 src/RimMandrake/Utils/save_adoption_check.py --save <authoritative> --json /tmp/adopt.json`, then read the AB_PropaneLakes rows | one answer, written into `donor_save_residue_2026-10-19.md` | yes | |
| G11 | **Start-save censuses** (after S13) | `python3 src/RimMandrake/Utils/save_class_census.py <save>` · `python3 src/RimMandrake/Utils/save_def_census.py <save> --modsconfig <frozen ModsConfig>` · `python3 src/RimMandrake/Utils/save_adoption_check.py --save <save> --modlist <frozen ModsConfig>` | 0 FATAL · 0 THING rows · 0 unresolved. Sanity probes are built in: def census refuses if it cannot see `ThingDef Human`; adoption check requires `<def>Human</def>` > 0 | yes | |
| G12 | **Cold reload** (S14) | restart the game, load the S13 save, wall-clock launch→map, first exception in `Player.log` | map loads; 0 exceptions attributable to our content | **NO TOOL** for the timing (wall clock by hand); `./game` stamps state | |
| G13 | **Representative biome generation**, one map per paint target (28 `RM_` targets, 02 §6) | `python3 src/RimMandrake/Utils/modcheck/l1_donor_off_round.py derive --out <m.json>`, then on Windows `python.exe src/RimMandrake/Utils/modcheck/l1_donor_off_round.py run --manifest <m.json> --phase mapgen` (`jawa/world_tile_map_generate` on a scratch tile → count → `jawa/map_drop`). `derive` lists only donor-touched biomes, so the 28 need a manifest of their own (`--only-biomes` filters, it does not add) | per biome: map biome == B, wild animals > 0 **or** plants > 0 (the harness's bar, gate 0.5.5 #5), no mapgen exception. **Sanity probe**: the same run includes one vanilla control biome known to populate (e.g. `AridShrubland`) and must read plants > 0 and animals > 0, or every zero in the run is UNMEASURED (`instrument_traps.md`: "Any count that is round, zero or alarming is a query bug until a sanity probe proves the instrument can see"). Temperature matters: Cauldron read 0 animals at −2.9 °C and 4 at 30 °C (`Transient/live_testing_2026-10-19d/RESULTS.md`) — record the tile temperature beside each zero | yes (bridge); **`measure` cannot do it** (§0.7); a 28-biome manifest is owed | |
| G14 | **Globe LOOK** (S9) | `worldview.py` render beside `world/view/ASHKARR_WORLDMAP.biome.equirect.png` | 👤 says it reads right | yes | |
| G15 | **Roster at creation** (S7) | `jawa/list_factions` | every wanted faction present | yes | |
| G16 | **Contaminated fixtures** | list `Saves/RM_TestSite_*`; run G11's three censuses on each | each rebuilt or moved to a quarantine folder | censuses yes; **NO TOOL** to rebuild | |
| G17 | **Checkpoints exist** | §4 C1–C3 present before S2, with sha256 | all present | yes (`cp`, `sha256sum`) | |
| G18 | **Load proof of the list** | `DONOR_OFF_LOAD_PROVE_AFTER_BENCH` / `DONOR_FOUR_RETIRE_JUST_GET_IT_DONE` A3, and re-checks of `QUICKTEST_POLICY_NRE_FULLLIST_1`, `MATERIAL_MERGE_LOAD_CRASH_1` (both UNMEASURED since filing) | a quicktest map starts on the frozen profile; first exception not ours | yes (`l1_donor_off_round.py`, quicktest) | |

**Gates with no tool today:** G3 (settings snapshot), G5 (reverse closure, C# strings, XPath), G7 (the three remaps,
the CSV resolver, `w9_run --inputs`), G8 (worker check), G9 (layer exporter and comparer), G12 (load timer),
G16 (fixture rebuild), plus the ship remap (S10b) and the Ikee un-bond (S12). G13 needs a 28-biome manifest.

---

## 3. (c) The throwaway rehearsal

### The ruling it must sit inside — `design/Jawa/worldbuilding/WORLD_REDRAFT.md`, owner 2026-08-21

> 🔴 **WHEN THIS RUNS — owner's ruling, 2026-08-21 12:4x, to DECIDE: CONTENT FIRST, REMAKE LATER.** Offered
> content-first / remake-next / throwaway-probe; he took content-first.
> ⇒ **This procedure does NOT run next.** It runs ONCE, after the creation-gated content is finished, because every
> remake spends a Configure Factions hand-pass and bakes the ideoligions permanently […]
> ⛔ **Nobody schedules a remake to "test" something.** If a check is only possible before a world exists, file it
> against this procedure's pre-flight, do not burn a generation on it.

PLAN.md Option D adds: the remake *"may not be, or authorise, a test redraft or an alternate planet"*, and the
2026-08-18 ruling forbids anything that produces an alternative planet.

### What the rehearsal measures, and whether each part stays inside

| # | measurement | how | inside the ruling? |
|---|---|---|---|
| R1 | Cold-load time on the candidate profile | launch to main menu, wall clock, `Player.log` first exception. No world, no save | ✅ a load is not a generation |
| R2 | Load time of an existing world on the candidate profile | load a **copy** of `CANONICAL_ASHKARR_START_2026-09-12.DONORFREE_CANDIDATE_2026-10-18_AREAFIX2.rws`; wall clock | ✅ no generation, no faction pass; the Option-D fixture route |
| R3 | Per-biome spawn (G13 dry run) | `l1_donor_off_round.py --phase mapgen` on scratch tiles of the quicktest world or of the R2 copy, maps dropped after counting | ✅ the existing ~90 s quicktest workflow (CLAUDE.md, RECORDED), which PLAN D item 1 names; it rolls a small dev world, not Ash'karr, and no Configure Factions pass |
| R4 | Stamp-stage timings | `w9_run.py` **dry run** against the R2 copy's world — reads and plans, writes nothing | ✅ no write, no generation |
| R5 | **Generation time of a 21,872-tile world** | generate at 7 / 1.0 with default factions, time it, discard without saving | ⚠️ **needs the owner's word.** It burns a full-size generation to test something — exactly the "throwaway-probe" he declined on 2026-08-21, and a planet that is not Ash'karr. Without his word it stays **UNMEASURED** and is simply recorded during the real run (S7), which costs nothing: on a development world a slow generation changes no decision |

R1–R4 never open the Create World page, so they spend no Configure Factions pass, write no world save and cannot
become a redraft. Results go to `Transient/remake_rehearsal_<date>.md` (a human reads it once) and the numbers are
copied into §2's result column. Running R1–R4 needs the bridge (`rimflow bridge take --for "remake rehearsal"`)
and a game-up window; it is not offline work.

---

## 4. (d) Checkpoints and rollback

Saves folder: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves`. Nothing below
writes to `CANONICAL_ASHKARR_START_*` or `ASHKARR_FALLLINE_*` (keepers; `import_founders.py` refuses them by name).
Each checkpoint: copy + `sha256sum` into `D:\Luke\dev\_rmscratch\remake_<date>\` (outside the repo; the saves are
large and gitignored).

| id | when | what is copied | rollback from it |
|---|---|---|---|
| C1 | before S2 | the whole `Saves` folder | restore the folder; nothing in the game changed yet |
| C2 | before S2 | live `ModsConfig.xml` + `ModsConfig.FULL.LATEST.xml` | copy back with the game DOWN (`modset_builder.py --restore` writes the pre-swap list md5-verified). ⚠️ never `--restore-full` blind: FULL.LATEST still lists the 7 donors retired 10-18 (PLAN §2) |
| C3 | before S2 | live Cherry Picker file, `Config/Mod_*.xml`, `Config/GravshipExport/` | copy back with the game down; `cherrypicker_swap.py --status` to confirm |
| C4 | after S9 | world-only save `ASHKARR_DEV_WORLD_<date>.rws` | reload it; S10 onward repeats without spending the faction pass again |
| C5 | after S10 | landed save, before the ship | reload; repeat S10b |
| C6 | after S10b | save with the ship | reload; repeat S11 |
| C7 | before S11 | the copy the splice writes into (the importer also backs up unless `--no-backup`) | discard the spliced copy |
| C8 | after S13 | the candidate start save | it is the promotion candidate |

**Abort rules.** An error storm or failed map ⇒ stop, close the game, `./game --why "<reason>" down`, root-cause the
first exception (standing rule: never leave a broken game running). A failure before S6 costs only a load; a failure
after S6 returns to C4 if C4 exists, else the faction pass is spent again and 👤 decides whether to repeat.
**Promotion** is his word only; until then the old canonical save stays the reference and nothing is deleted.

---

## 5. (e) The 31 "must come first" items, in order

Source: 03 class C, states from `rimflow show` today (2026-10-19). "→" = must follow. Dev-world note: on a
development world (Option D) a faction or ideo can be added later by tool (§0.1–0.2), so row 31 is no longer hard.

**Stage 1 — rosters off donor defs** (G7/G13 depend on these)

| # | item | state / needs | depends on |
|---|---|---|---|
| 1 | `ALPHA_BIOMES_MIGRATE_PLANTS_TO_RM_TWINS` | ready · offline | — |
| 2 | `ALPHA_BIOMES_MIGRATE_DISEASES_AND_CODE` | ready · offline | — |
| 3 | `ALPHA_BIOMES_CENSUS_THE_REST_OF_IT` | proposed · **owner** (~130 AB_ names) | — |
| 4 | `ALPHA_BIOMES_RETIRE_THE_LAST_PLANT_DONOR` | ready · offline (umbrella) | → 1, 2, 3 |
| 5 | `DONOR_DEFS_PORT_TO_OURS_1` | ready, **BLOCKED**: owner-sat plan first | 👤 |
| 6 | `DESERT_FAMILY_PORT_EXECUTION_1` | proposed, **BLOCKED**: review sheet never owner-reviewed | → 5, 👤 sheet |
| 7 | `ALPHA_ANIMAL_PORTS_REHOME_1` | doing · offline | — |
| 8 | `REGEN_GAPS_DECIDE_STRAYS_AND_FLYERS` | proposed · offline (16 donor roster rows) | → 5 |
| 9 | `DONOR_ROSTER_GUARDS_FIX_WRONG_PACKAGE_ID` | proposed · "at his sitting" | 👤 |
| 10 | `ABYSS_SHEET_DONOR_PORT_1` | validated · owes A5 L3 (art on quicktest spawn) | bridge window |
| 11 | `WARSCAR_SHEET_DONOR_PORT_1` | validated · owes A3 L3 | bridge window |
| 12 | `CONTAGION_RULED_CONTENT_1` | built · owes A1 L1 … A5 L4 | bridge window |
| 13 | `CRACKEDLANDS_RULED_CONTENT_1` | doing, **BLOCKED**: live verify + `CRACKEDLANDS_MECHANICS_BUILD_1` | → `CRACKEDLANDS_MECHANICS_BUILD_1` |

**Stage 2 — names frozen** (G6)

| # | item | state / needs | depends on |
|---|---|---|---|
| 14 | `PLANT_TIERS_RECONCILE_MOST_ARE_BAROQUE` | doing · **owner** (BENCH) | 👤 list |
| 15 | `BIOME_TIER_CLEANUP_1` | proposed · game-up | → 14 |
| 16 | `BIOME_DEFNAME_MIGRATION_WAVE_1` | proposed, **BLOCKED** (stale edge; prose reason: live tile counts unreadable) | 👤: the rename breaks the old reference save, which D keeps |
| 17 | `CRACKEDLANDS_FULL_RENAME_1` | built, **BLOCKED** by owner card 2026-10-09 (STOP if the canonical save references it — it does, 44 tiles) | 👤 must lift the card's stop for the remake |

**Stage 3 — the creation list** (G1–G5)

| # | item | state / needs | depends on |
|---|---|---|---|
| 18 | `WAVE1_FIXES_DEPLOY_BEFORE_THE_CUT` | proposed · deploy | — |
| 19 | `MINES_SWAP_RETIRE_SHAFT_ALREADY_DUG` | proposed · deploy | — |
| 20 | `VRE_XENO_MODS_RETIRE_DEFOF_HOLDOUTS` | proposed · offline | — |
| 21 | `WAVE1_MODLIST_RETIRE_37_IN_ONE_LOAD` (list half; the edited-save-copy half is obsolete under a remake) | proposed · bridge | → 18, G5 reverse closure |
| 22 | `CHERRY_PICKER_RESTORE_FROM_SHIP_PROFILE` | proposed · deploy | → 21 |
| 23 | `GENERATOR_MODS_PROVE_INERT_AFTER_CREATION` | proposed · bridge (loads a saved world with/without each; no generation) | → 21 |

**Stage 4 — proof the list makes a game** (G18)

| # | item | state / needs | depends on |
|---|---|---|---|
| 24 | `MATERIAL_MERGE_LOAD_CRASH_1` | proposed · re-check (UNMEASURED since 2026-10-10) | — |
| 25 | `QUICKTEST_POLICY_NRE_FULLLIST_1` | proposed · re-check (UNMEASURED since filing) | — |
| 26 | `DONOR_FOUR_RETIRE_JUST_GET_IT_DONE` | validated · owes A3 L2 (mapgen), A5 L4 (owner unticks) | → 4, 7 |
| 27 | `DONOR_PHASE0_FINISH_AWAITING_HIS_RULINGS` | proposed · bridge (deploy SWBestiary, donor-off L1) | 👤 batch 5/6 rulings |
| 28 | `DONOR_OFF_LOAD_PROVE_AFTER_BENCH` | proposed · bridge (W4 gate) | → 27, 22 |

**Stage 5 — paint inputs** (G7, G13)

| # | item | state / needs | depends on |
|---|---|---|---|
| 29 | `DONOR_MUTATORS_MIGRATE_TWENTY_TWO_CAME_HOME` | built · owes deploy + live tile check (A1 L1, A2 L2) | → 28 load |
| 30 | `BIOME_WORLDTEX_BUILD_EVERY_BIOME_A_FACE` | proposed · offline (BENCH) | — |
| 31 | `HORRORS_RAIDING_FACTION_1` | doing, **BLOCKED**: owner hold 2026-09-09 until `HORRORWASTES_BIOME_DISSOLVE_1`'s render | 👤; on a dev world, may be created later with `jawa/faction_create` (UNMEASURED) |

Owner-gated rows: 3, 5, 6, 9, 14, 16, 17, 27, 31. Everything else can proceed in the order shown.

---

## 6. What this runbook still needs from the owner (not decided here)

`RUT_Umbra`'s 2,531 tiles (G7) · the authoritative save and the accepted layer losses (G9) · Ideology route (S5) ·
the start tile (S10) · the ship floor and boulder substitutes (S10b, cosmetic) · the offline founders splice under the
2026-08-18/19 no-save-writes ruling (S11) · what happens to the scenario's own starting pawns (S11b) · whether R5
may run (§3) · lifting the stops on rows 16 and 17.
