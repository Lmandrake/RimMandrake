# 15 — Unattended conductor for the development-world remake (runbook S0–S15), 2026-10-20

FOUNDRY helper, offline. No game, bridge or live ModsConfig was touched writing this. **Order** (owner, 2026-10-19
11:2x PM, going AFK): *"Keep going until we are finally free and the world is repainted. I'd like to start tomorrow
able to continue developing mods rather than retiring them."* **Option D** (card, 2026-10-19): a DEVELOPMENT world that
may be repainted later. The canonical start save `CANONICAL_ASHKARR_START_*` is never written; nothing here promotes.

This file turns `06_remake_runbook.md` §1 into steps a live conductor (the bridge holder) can run **without the owner**,
and for every 👤 step says whether a bridge or UI-automation route exists and which **provisional, reversible default**
to take. Labels as in 06: **MEASURED** (read today, instrument named), **RECORDED** (another doc says it), **INFERRED**
(read from engine source, not run), **UNMEASURED**.

Why defaults are acceptable: the dev world is disposable (Option D), and every step from S10 on has a checkpoint (C5–C8) to
return to; there is no C4 (no save is possible at the landing page in 1.6 — the world lives in `Current.CreatingWorld` and `Current.Game` is null until landing (`rimworld/save_game` → 'No game is currently loaded'; `GameDataSaveLoader.SaveGame` NREs; MEASURED 2026-10-20)), so a failure between S6 and C5 costs a regeneration. What cannot be undone *inside one world* (ideology mode, the faction pass) costs only a regeneration.

---

## 0. Tools this plan relies on (new ones are in `src/RimMandrake/Utils/remake/`)

| gate | tool | state 2026-10-20 |
|---|---|---|
| G3 / C3 | `python3 src/RimMandrake/Utils/remake/checkpoint.py make --ids C3`; `verify <dir>/C3 --against-live` | built, selftest; probe run 109 files 12.3 MB, live-verify PASS |
| G17 / C1–C2 | `checkpoint.py make --ids C1,C2`; `checkpoint.py status --date <d>`; `restore <dir> --apply --game-is-down` | built, selftest. Root `D:\ClaudeWork\remake\<date>\` (06 §4 says `D:\Luke\dev\_rmscratch`; nothing new goes under `D:\Luke\dev`) |
| G5 | `python3 src/RimMandrake/Utils/remake/g5_reverse_closure.py --json <out>` | **FAIL**: 0 HARD, 112 unguarded refs on PAINT.RULED (76 in our mods). These are load-time error lines, not crashes: a top-level patch that matches nothing, or a cross-reference Scribe drops |
| G8 | `python3 src/RimMandrake/Utils/remake/g8_worker_safety.py` | **PASS** (MEASURED, dump 2026-10-20T06-17-12Z) |
| G10 | `save_adoption_check.py` | **SETTLED**: `AB_PropaneLakes` is 2 world-creation slider keys, not a landmark |
| G16 | `python3 src/RimMandrake/Utils/remake/g16_fixture_census.py run` · `table` · `quarantine --apply --game-is-down` | **FAIL**: 14/14 `RM_TestSite_*` CONTAMINATED vs DEV.RULED, 6 of them FATAL Class= (map never loads) |

Evidence: `D:\ClaudeWork\remake\` (`g5_2026-10-19.txt/.json`, `g8_2026-10-19.json`, `g10_adopt_canonical.md/.json`,
`g16_fixtures\TABLE.md`, `gates_progress.md`).

---

## 1. Pre-flight the conductor runs before S0 (all offline, game down)

1. `git -C /home/mandrake/rm/foundry pull`; record `git rev-parse origin/main`.
2. Re-run G8 and G5 on the **frozen** profile (`--profile infrastructure/state/modlists/ModsConfig.PAINT.RULED_2026-10-20.xml`
   unless a newer PAINT file is frozen). G8 must read PASS. G5 FAIL does **not** stop a dev world (§5 waiver logic);
   copy its unguarded rows into the S2 run-sheet as *expected* error lines, so the S2 log triage can tell them apart.
3. G16: `g16_fixture_census.py quarantine --apply --game-is-down` moves the 14 fixtures to `Saves\_quarantine_<date>\`
   (a move, never a delete). Reversible by moving them back. Needs no owner: fixtures are test data.
4. G1, G2, G4, G6, G7, G18 per 06 §2 with their own tools. G7 (`w9_run.py --inputs world/paint_inputs_2026-10-20
   --check-inputs`) is another unit's work; S8 does not start without it.

## 2. The run, step by step

Columns: **route** = how the conductor does it alone; **default** = the provisional pick; **undo** = how it is reversed.

| # | step | route (unattended) | default | undo |
|---|---|---|---|---|
| S0 | gates table | write each result + evidence path into 06 §2 | proceed when G1, G2, G4, G7, G8 PASS; G5/G16 FAIL waived for a dev world per §5 | — |
| S1 | checkpoints C1–C3 | `checkpoint.py make --ids C1,C2,C3 --date <d>` then `checkpoint.py status --date <d>` → `G17 PASS` | C1 is 6.3 GB (MEASURED du 2026-10-19): budget the copy, run it in slices under the 600 s watchdog by retrying `make --ids C1 --suffix` only if it was killed (a killed make leaves a dir without MANIFEST.json → `status` says FAIL, never PASS) | `restore` |
| — | install the profile | game down: atomic copy of the frozen PAINT file over live `ModsConfig.xml` (`modset_builder.py`/`modlist_swap.py` have no "apply this file" mode, MEASURED by their argparse); then 06 G2 one-liner, count + sha equal | PAINT.RULED (83, MEASURED parse) | `checkpoint.py restore <d>/C2 --apply --game-is-down` |
| S2 | cold load + dump | Steam launch; `./game --why "remake cold load" loading`; arm `dump_request.txt`=`all` | — | close game |
| S3 | 7 subdivisions + planet type | `python3 src/RimMandrake/Utils/remake/set_planet_type.py --check` (exit 0 = TidallyLocked saved) BEFORE launch. 🔴 **Alien Worlds default-planet trap:** without Worldbuilder (PAINT) Alien Worlds runs its Standalone backend and sets the planet type at startup from its own settings file; no file = `Default` = a VANILLA, not tidally locked, planet (MEASURED 2026-10-20: `selectedPlanetType` read "Default"). Persisted by `python3 src/RimMandrake/Utils/remake/set_planet_type.py --apply` (writes `Config/Mod_3626210061_AlienWorldsFramework.xml`; applied 2026-10-20); check with `--check` before generating, and verify `alienWorldsFrameworkPlanetType` = TidallyLocked in the saved world. On PAINT Worldbuilder is absent, so `set_planet_subcount.py` is moot: `mandrake.rm.planetpresetprime` primes coverage 1.0 / subdivisions 7 (2026-10-20 run: 21,872 tiles). | — | — |
| S4 👤 | scenario **`RUT_Jawa_UtinniStart`** (file `Scenario_Utinni.xml`; no def is named Scenario_Utinni) | **`jawa/scenario_select {scenario:"RUT_Jawa_UtinniStart", advance:true}`** from the main menu (opens the page itself) — built 2026-10-20, **live only after the §8 deploy**. Fallback if not deployed: at `Page_SelectScenario`, `get_ui_layout`, find the row labelled with the scenario's label, `click_ui_target`; if the row is not `actionable`, `system_click.py` at the row rect's centre. Then `Next` | RUT_Jawa_UtinniStart. Anomaly playstyle: leave the default (difficulty, changeable later in Storyteller settings) | regenerate |
| S5 👤 | ideology mode | ⚠️ the page comes **after S10**, not here (`Scenario.GetFirstConfigPage`, 1.6: Storyteller → CreateWorldParams → SelectStartingSite → ChooseIdeoPreset → pawns; §8). At `Page_ChooseIdeoPreset`: **`jawa/ideo_load_rid {path:"D:\\Luke\\dev\\RimMandrake\\src\\Jawa\\ideoligion\\The Salvation.rid"}`** (after the §8 deploy). See §3 for the pick | **non-classic, load `src/Jawa/ideoligion/The Salvation.rid`** (validate first: `validate_save_artifact.py` exit 0). On PAINT the original names off-PAINT rituals (PostLoadInit NREs, 2026-10-20); the stripped dev variant `src/Jawa/ideoligion/The Salvation (PAINT-clean).rid` validates 172/172 — 👤 picks. Fallback if the load dialog cannot be driven: pick any preset, then fix after landing (§3) | regenerate (dev world) |
| S6 👤 | Configure Factions | **no clicks needed for the roster we want** — see §4. Click `Next`/`Generate` via `click_ui_target`; `system_screenshot.py` the page first | accept the default list | `jawa/faction_create` adds a missing faction after S7 |
| S7 | roster audit | `jawa/list_factions` at `Page_SelectStartingSite` | the 8 `RUT_Jawa_*` present + vanilla required set; anything else noted, not removed | `faction_create` for gaps |
| S8 | stamp | `python.exe src/RimMandrake/Utils/w9_run.py --inputs <G7 bundle>` dry, then `--apply` | stage 6 labels: Core `Desert` featureDef, no Worldbuilder needed (71 regions, 2026-10-20) | regenerate |
| S8b/c | labels, renames, ideos | `jawa/world_features_set` loop; `jawa/faction_name_set`; ideos only if §3 fallback | — | — |
| S9 👤 | LOOK | `jawa/world_commit`, `world_lint`, `worldview.py <save>` render beside `world/view/ASHKARR_WORLDMAP.biome.equirect.png` | **conductor proceeds** on a lint-clean commit and writes the render path into the morning list; the owner's look is deferred, not skipped (§6). No save is possible here (1.6), so no C4 | regenerate |
| S10 👤 | start tile | **`jawa/start_site_select {tiles:"17011", advance:true}`** (17007/1621 sit next to Zeddo's Toll on the current paint inputs and are refused) (after the §8 deploy): takes the first tile the game accepts, returns each skipped tile's reason; a proximity confirmation returns `success:false` + `pendingConfirmation` (confirm by `click_ui_target`). Fallback if not deployed: `jawa/world_view` centres the globe on the tile, `system_click.py` at the screen centre, read the selection back from `get_ui_state`/`get_ui_layout` before `Next` | **17011** (Zeddo's Yard cluster, `PLAYER_START_SITE_1`; 👤 confirms the tile). 17007 and 1621 are directly ADJACENT to the stamped Hutt settlement Zeddo's Toll (tile 17006, `RUT_Jawa_HuttCartel`, paint-inputs settlements CSV), and the engine refuses any start tile adjacent to a settlement (`TileFinder.IsValidTileForNewSettlement` → FactionBaseAdjacent); both were refused in the 2026-10-20 run. 17011 is 2 tiles off, inside the ruled cluster (Hutt distance 1–2). A paint-inputs tweak CAN free 17007 — move Zeddo's Toll ≥2 tiles from it in `world/paint_inputs_<date>/ASHKARR_WORLDMAP_settlements.csv` — but that moves the owner's settlement: his call, not a conductor default | regenerate |
| S11b 👤 | scenario's own starting pawns (chooser page) | `click_ui_target` on `Start` (accept the rolled six) | **keep them** (nothing destroyed; 12 colonists harm nothing on a dev world). Morning call | `jawa/destroy_batch` later, or reload C5 |
| — | save at once | `rimworld/save_game` → **C5** | — | — |
| S10b | ship | `print_gravship.py design/Jawa/worldbuilding/ship_build/exported/Gravship_v2_ring_2026-09-12.paint.xml --center x,z --apply` (floors per owner ruling 20, 13 file) → **C6** | — | reload C5 |
| S11 | founders | `import_founders.py <copy.rws> --fragments <dir> --dry-run`, then real, into a **copy** | ⚠️ the 2026-08-18/19 no-save-writes ruling: 06 says it needs his word at the sitting. **Default: stop before the real splice**, leave the dry-run output for the morning (§6). Everything before S11 is unattended | discard copy (C7) |
| S12 | Ikee re-bond | §5 below — a route exists, no new tool | — | `pawn_relations add` back |
| S13 | save `ASHKARR_DEV_START_<date>.rws` + G11 censuses → **C8** | `save_class_census.py`, `save_def_census.py --modsconfig <frozen>`, `save_adoption_check.py --save <s> --modlist <frozen>` | — | — |
| S14 | cold reload | as 06 | — | — |
| S15 👤 | promotion | **never unattended.** Owner's word only | not promoted | — |

**What the conductor does if S11 waits for his word:** finish S12 on the scenario's own pawns? No — S12 bonds Yeku,
who arrives only with S11. So the unattended run ends at **C6 (world + landing + ship)** with S11/S12 prepared
(dry-run output, the exact S12 calls written out). That already gives him a dev world to develop mods on in the morning.

---

## 3. S5 ideology route — the pick and why

**Pick: route (i), non-classic, load The Salvation.rid at the ideo page.** Reasons, from 1.6 source (INFERRED, read
via RimSage 2026-10-20):

1. **Classic mode switches ideology off game-wide**, not only for the player: `Find.IdeoManager.classicMode` gates
   rituals (`Dialog_BeginRitual`), conversion (`InteractionWorker_ConvertIdeoAttempt`), precept thoughts (`Thought.cs`),
   certainty, ideo styles, the Ideo tab (`MainButtonWorker`), relic quests and more (~50 call sites). A DEVELOPMENT world
   for `rut.rites`, Doctrine and the twelve fixed ideos would test none of that in classic mode.
2. **Classic does not save us the per-faction ideos anyway.** `FactionGenerator.CreateFactionAndAddToManager` builds
   `fixedIdeo: true` parms from the FactionDef (`ideoName`, `deityPresets`, `forcedMemes`…) for every def with
   `fixedIdeo`, and `FactionIdeosTracker.ChooseOrGenerateIdeo` takes the `fixedIdeo` branch **before** the classic
   branch. All 8 `RUT_Jawa_*` FactionDefs read `fixedIdeo=True` in the dump (MEASURED, capture 2026-10-20T06-38-59Z),
   so worldgen gives each its own fixed ideo **in either mode**. Route (ii)'s `jawa/faction_ideo_set` pass (never run
   on a fresh world, UNMEASURED) becomes a repair tool, not a required step. (The RECORDED 1-ideo Ash'karr was made
   before these defs carried `fixedIdeo`, or by a path this reading does not cover: UNMEASURED which.)
3. **Classic skips the ideo page**, so The Salvation cannot be loaded there; `jawa/ideo_load_rid` (built 2026-10-20,
   §8) loads a `.rid` at that page or into a running game. Non-classic is the only
   native route to the player ideo the founders' `Ideo_20` is remapped onto (S11).
4. Non-classic is the superset: everything classic offers can still be approximated later; classic cannot be left.

Automation: `jawa/ideo_load_rid` at `Page_ChooseIdeoPreset` (§8). Without the deploy: the load button →
`Dialog_IdeoList_Load` row "The Salvation" → `click_ui_target` (UNMEASURED: actionable or not; fallback `system_click.py`
at the layout rect). **Fallback if neither works:** take any non-classic preset, land, then `jawa/ideo_load_rid` in the
running game (`setPlayerPrimary:true`; colonists keep their ideo until converted) — not a regeneration.

## 4. S6 Configure Factions — why the default list is the roster

`Page_CreateWorldParams` passes the configured list to `FactionGenerator.InitializeFactions`; its defaults come from
each configurable def's `startingCountAtWorldCreation` (INFERRED from the 1.6 source of `ConfigurableFactions`:
`maxConfigurableAtWorldCreation > 0`). On the PAINT profile (dump MEASURED):

- **ours, all `req=1 start=1 max=9999 fixedIdeo=True`:** `RUT_Jawa_AscendantHelix`, `_DeepwaterCompact`,
  `_FreeDroidEnclaves`, `_GeonosianFoundryHive`, `_HuttCartel`, `_Junkers`, `_IndigenousTribes`, `_WildsteamClan`
  = **8**, not the "13 rows" 06 S6 cites (the 13 may count rows of the stale checklist that are not FactionDefs;
  UNMEASURED). Also `RM_Faction_CombHolds` (start 1), hidden `RM_Thozziks`, `RSW_PustuleHornets`,
  `RUT_GreentideAntFaction` (req 1, start 0, hidden: owner ruling 7 wants Green Tide present — check it in S7).
- **vanilla start=1:** OutlanderCivil, TribeCivil, Pirate, Empire + the hidden required set (Ancients, Mechanoid,
  Insect, Entities, HoraxCult …).
- **third-party on PAINT with `start>0`:** player-only defs (BS_/VFET_/OuterRim player factions) — they never spawn
  as NPCs. NPC third-party defs on PAINT (`OuterRim_*`, `DV_PirateKeshig`, `VRESaurids_*`) read `start=0`.

So **accepting the default page yields our 8 + the vanilla minimum** without a single roster click: the brief's
"13 RUT_Jawa factions plus the vanilla minimum" in practice. S7's `jawa/list_factions` is the check; a missing one is
added with `jawa/faction_create` (UNMEASURED for ours, so S7 records it rather than retrying). Nothing is removed on
a dev world.

## 5. S12 — the Ikee un-bond has a route (no new tool)

06 S12 said **NO TOOL** for the un-bond half. That was wrong (corrected in 06 the same commit series):

- `jawa/pawn_relations` (`JawaBenchPawnTools.cs`) does `action=remove` → `p.relations.RemoveDirectRelation(rd, other)`.
  Core `Bond` is `implied=false`, `reflexive=true` (`PawnRelations_Misc.xml`), and `TryRemoveDirectRelation` removes
  the mirrored entry on the other pawn too (engine source, INFERRED). So one call clears both sides.
- Re-bond: prefer `jawa/pawn_relations action=add relation=Bond` (a direct `AddDirectRelation`, no gates). `jawa/animal_bond`
  calls `TryDevelopBondRelation`, which multiplies the chance by 0.55 for every other live Bond Yeku holds and by his
  `BondAnimalChanceFactor`, then rolls `Rand` — at chance 1.0 it can fail silently if the Eyeling bond survived S11.
- Master: `jawa/set_player_settings pawnId=<Ikee> masterId=<Yeku>`.

Calls, in order (ids from `rimworld/list_colonists` after S11):
```
jawa/pawn_relations  {pawn:<Ikee>, action:"list"}                                  -> the current bondee
jawa/pawn_relations  {pawn:<Ikee>, action:"remove", relation:"Bond", otherPawn:<bondee>}
jawa/pawn_relations  {pawn:<Yeku>, action:"list"}                                  -> no Bond to an absent Eyeling? note it
jawa/pawn_relations  {pawn:<Yeku>, action:"add", relation:"Bond", otherPawn:<Ikee>}
jawa/set_player_settings {pawnId:<Ikee>, masterId:<Yeku>}
jawa/pawn_relations  {pawn:<Ikee>, action:"list"}                                  -> read-back: Bond -> Yeku only
```

## 6. What truly needs his eyes in the morning

1. **S9 look** — the globe render beside the reference equirect (`worldview.py` output path written to
   `D:\ClaudeWork\remake\gates_progress.md`). The conductor proceeded on lint; sending it back means a regeneration (there is no C4).
2. **S11 founders splice** — the offline save write under the 2026-08-18/19 ruling; dry-run output waits for his word.
3. **S15 promotion** — never unattended.
4. Lighter calls, each with the default already applied: start tile (17011; 17007 refused — adjacent to Zeddo's Toll), scenario starters kept, ideology route
   (non-classic + Salvation, or the fallback if the load dialog could not be driven), G5's 112 unguarded refs and the
   14 quarantined fixtures (waived for a dev world; fixing them is ordinary mod work, `RM_TestSite_*` rebuild has no tool).

## 7. Waivers a dev world can take, and why

- **G5 FAIL**: unguarded refs are log noise on load (a failed patch or a dropped cross-reference), not a worldgen
  crash; G8 (the crash class) is PASS. Record them as expected lines; fix as mod work.
- **G16 FAIL**: fixtures are test maps, not the world; quarantine (a move) makes them unloadable by accident and is
  reversible.
- Not waivable: G8, G2 (the profile the world is made under), G7 (stamp inputs), G17 (checkpoints).

## 8. New start-flow tools (S4, S5, S10): deploy and verify

Built 2026-10-20 in `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchStartFlowTools.cs` (logic in
`JawaBenchStartFlowCore.cs`, offline units `python3 src/RimMandrake/Utils/selftest_start_flow_core.py`, 37/37). Built with
`build.py --gm` (409 tools in the DLL == source; `selftest_tool_metadata.py` PASS). **NOT DEPLOYED**: the game was up
under another helper. Each tool does what its page's own button does (1.6 source, RimSage), and reads back the state the
page reads:

| tool | does | read-back |
|---|---|---|
| `jawa/scenario_select {scenario, advance, openIfAbsent}` | at the main menu opens `Page_SelectScenario` (as New colony does), sets its private `curScen`; `advance` = the page's own `CanDoNext`/`DoNext` (creates the new `Game`) | `curScen` is the object; `Current.Game.Scenario` after Next; next page open |
| `jawa/start_site_select {tiles, advance, jumpCamera}` | at `Page_SelectStartingSite`: first candidate `TileFinder.IsValidTileForNewSettlement` accepts → `WorldInterface.SelectedTile` + `GameInitData.startingTile` | both fields, biome, hilliness, landmark; every skipped tile's reason; a proximity confirmation → `success:false` + `pendingConfirmation` |
| `jawa/ideo_load_rid {path, setPlayerPrimary, allowDuplicateName, dryRun}` | at `Page_ChooseIdeoPreset`: `Page_ChooseIdeoPreset.DoLoad`'s steps (load, new id, player primary + initial ideo, drop unused starting ideos, `PostIdeoChosen`, `classicMode=false`) then advances; in a running game: adds it (+ primary) | `PrimaryIdeo` is it, in `IdeoManager`, `classicMode`, page closed, next page open |

**Page order (1.6, `Scenario.GetFirstConfigPage`):** Storyteller → CreateWorldParams (S3/S6) → SelectStartingSite (S7/S10)
→ ChooseIdeoPreset (S5) → starting pawns (S11b). S5 therefore runs AFTER S10. Note S8/S9 (stamp, look) run at the
landing-site page, before S10, as the table has them; nothing can be saved there.

**Deploy (the first game-down window; nothing else needed, no ModsConfig change):**
1. Game down (`./game` reads `down`; companion DLL is memory-mapped while it runs).
2. From the seat clone at a commit containing these files: `python3 src/RimMandrake/bridgetools/build.py --gm --apply`
   → must print `deployed` (no `THIS DEPLOY WOULD REMOVE TOOLS`; if it does, read it, never `--allow-tool-removal`).
3. Launch as the run already does (S2's cold load). The new tools ride that load: no extra load is spent.

**Verify (at the main menu, before S3; all read-only or refusal paths):**
1. `python.exe D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\rimbridge_client.py --list-tools` lists all three.
2. `jawa/start_site_select {tiles:"17007"}` → `success:false`, "landing-site page ... is not open" (refusal path live).
3. `jawa/ideo_load_rid {path:"D:\\Luke\\dev\\RimMandrake\\src\\Jawa\\ideoligion\\The Salvation.rid", dryRun:true}` →
   `success:false`, "Neither the ideoligion page ... nor a game running" — proves path resolution + file found (a bad path
   fails earlier with "No file at"). ⚠️ the mirror must hold the file: `./mirror sync` if unsure.
4. `jawa/scenario_select {scenario:"Utinni_typo", openIfAbsent:false}` → `success:false`, "No scenario page is open".
   Then the real S4 call: `{scenario:"RUT_Jawa_UtinniStart", advance:true}` → check `pickReadBack:true`,
   `gameScenario` = the Utinni scenario name, `nextPage:"Page_SelectStoryteller"`.
5. S10 / S5 are proven by their own read-backs in the run (`startingTileReadBack` == the chosen tile — 17011 in the 2026-10-20 run — and `selectionWrites` 1, or a listed refusal;
   `isPlayerPrimary:true`, `classicMode:false`, `ideo.name` "The Salvation", `nextPage` the pawn page).
   Any `success:false` → fall back to the UI route in that row and record the response JSON in
   `D:\ClaudeWork\remake\gates_progress.md`.
