# DIRTY_CODE_REVIEW_LOOP_RESTART_17

Continuity note for the standing dirty-code-review loop (FOUNDRY). Successor
to `DIRTY_CODE_REVIEW_LOOP_RESTART_16` — read that file (and its own chain)
for fuller history. This wave ran in a git worktree
(`agent-a4ba792d14ba36967`), BELT mode, no live-game bridge held.

## Two tracking schemes — re-checked fresh, still both live

`DIRTY_CODE_REVIEW_STANDING_LOOP_1` (filed 2026-09-03) is still `doing`.
Re-read its full history fresh this wave: its last actual review-wave note
is still the FlowWorks wave at 03:33:45 (2026-09-18) that RESTART_16 already
recorded — nothing landed on it since. No work in this wave duplicates it;
picks below were cross-checked against it and against `rimflow show` on
every gating item candidate, fresh, not trusted from either restart note.

## Where things stood at the start of this wave

`code_review_status.py list`, freshly re-run: **2845 clean / 96 dirty / 2
orphaned** (RESTART_16's own closing figure, 2862/79/2, was already stale —
never trust it past its own session).

## What this wave did

Re-verified every RESTART_16 "next candidate" against a FRESH `rimflow show`
on its gate (gates decay in hours here, not days) before touching it:

- `src/RimMandrake/rimflow/model.py` (1456 lines) — no active gate found
  (confirmed via `grep -rl` over `infrastructure/state/items/` — only other
  DIRTY_CODE_REVIEW_LOOP_RESTART_* files mention it). Full read, all 1456
  lines. **1 real bug found+fixed**: `drop` and `supersede` never cleared
  `item.blocked`/`blocked_reason`/`blocked_on` — only `close` did, despite
  the exact same bug having already been found and fixed for `close`
  (documented in the file's own comment, citing a 2026-09-03 measurement of
  23 live items). Verified live via a throwaway `model.replay()`: **6 items
  right now** render `state: dropped (BLOCKED)` / `state: superseded
  (BLOCKED)` with a permanently stale reason (B55,
  REFMATCH_THRESHOLDS_CALIBRATE_1, FINAL_WORLD_PREP_1,
  WORLD_MUTATOR_LANDMARK_IMPORTERS_1, SARLACC_NATIVE_HABITAT_1,
  UTINNI_SHELL_DEFNAME_BUG_1). Fixed to match `close`'s own pattern; 67/67
  `selftest_model.py` checks still pass. Marked CLEAN at `534c14f53`.

- `src/RimUtinni/PawnFlavor/Patches/PawnFlavorPhase2_ThoughtDef.xml`
  (7.3MB, ~143.8k lines — too large for a single read, dispatched to a
  sonnet subagent briefed to cover the WHOLE file via XML-validity parse +
  an exhaustive `stages/li[N]` target-collision sweep, not a sample, plus
  targeted reads on every `LovinAsexual`/`Rakatan`/`archotech` hit). Its
  diff was read and independently re-verified by me before commit (not
  trusted on the subagent's word alone) — re-ran the same collision sweep
  myself pre- and post-fix. **2 real content-loss bugs found+fixed**,
  both RESTART_15/16-named leads finally landed:
  1. The "Archotech is Rakatan" rename (`6bc96eaf7`) missed the deep
     nomatch→nomatch fallback branch of `ABF_Thought_Synstruct_
     ArchotechImplantDissonance`'s 6 stages — all 6 still read the old
     "archotech piece" wording. Fixed, 0 stale occurrences remain.
  2. `LovinAsexualNegative` and `LovinAsexualPositive` each carried TWO
     top-level patch blocks both targeting `stages/li[1]`, so the second
     silently overwrote the first at patch-apply time, permanently
     discarding the mild-severity stage text. Retargeted the second
     block's `li[1]`→`li[2]` (7 xpath occurrences per defName). My own
     re-run of the collision sweep across all 2385 distinct (defName,
     stage) targets in the file confirms zero anomalies remain for either
     defName, and zero elsewhere in the file except 3 pre-existing
     byte-identical harmless duplicate blocks (`HAR_AlienVsXenophobia`,
     `HAR_XenophobiaVsAlien`, `HAR_XenophobeVsXenophile` — verified
     content-identical, no content loss, left as-is — wasted patch cycles,
     not a correctness bug, not worth a restructuring edit in a cleaning
     pass). Marked CLEAN at `21d7a2cec`.

- `src/RimMandrake/Utils/naming_lint.py` — no active gate
  (`STALE_RENAME_GATE_SWEEP_1`, its only recent toucher, is `done`). Full
  read. **1 real bug found+fixed**: the `leak` check read raw file text
  instead of the comment-stripped text its own `defName` check already
  uses (`_stripped()`, which exists specifically "so a ... string that
  only appears inside a `<!-- -->` is not counted as shipping"), so a
  comment merely EXPLAINING why code is exempt from JawaBench (dev
  tooling, exempt per CLAUDE.md) flagged as a live leak. Verified this was
  producing exactly 3 live false positives before the fix
  (`RM_MapComponent_MudSwallow.cs`, `DroidworksHardwareQuirks.cs`,
  `WarLabCraterMutation.cs` — all three hits are `//` comments, none
  shipped code); 0 after. Added a comment stripper covering both XML and
  C# comment syntax. Marked CLEAN.

- `src/RimUtinni/KyberTradePlot/Defs/QuestScriptDefs/
  RUT_KyberDonationSmuggle.xml` — gate (`STALE_RENAME_GATE_SWEEP_1`) is
  `done`. Full read; field names (`settlement`, `storeAs`/`timeout`,
  `duration`, `requestedThingDef`/`Count`) cross-checked against the
  working sibling `RUT_FungalSoilTradeRequest.xml` this file's own header
  says it's modeled on — all match exactly. No bug. Marked CLEAN.

- `src/RimUtinni/RotSporeKit/Defs/ThingDefs_Plants/RUT_PaleTree.xml` —
  its gate, `ROT_PALE_TREE_1`, is `ready` (not `doing`) — nobody actively
  mid-editing. Full read; `requiredSubplantCountPerPsylinkLevel`'s 2-entry
  list, `MayRequire="Ludeon.RimWorld.Royalty"` placement, and the
  `compClass` note on `CompProperties_SpawnSubplant` all match the file's
  own header ruling exactly. No bug. Marked CLEAN.

- `src/RimStarWars/NunaArtOverride/About/About.xml` — gate
  (`NUNA_ART_REGEN_1`) is `done`. Full read; both `loadAfter` packageIds
  (`Mlie.StarWarsAnimalCollection`, `mandrake.rsw.swbestiary`) checked
  against `ModsConfig.FULL.LATEST.xml` — `swbestiary` active,
  `Mlie.StarWarsAnimalCollection` currently inactive in that snapshot
  (harmless: `loadAfter` on an inactive mod is a no-op, not a bug). No
  bug. Marked CLEAN.

- `src/RimMandrake/MovingDunes/Source/RimMandrake_MovingDunes.csproj` —
  its build item, `MOVING_DUNES_BUILD_1`, is `doing BLOCKED` (the engine
  is already built and the item is blocked on a live-load gate, not mid-
  edit) — the one touch on this file (`cade628c1`) was an incidental
  1-line change inside an unrelated FlowWorks commit, not active
  MovingDunes work. Full read; the 11-file `Compile Include` list matches
  the 11 `.cs` files actually on disk exactly (no missing/orphaned
  entries). No bug. Marked CLEAN.

- `src/RimMandrake/EnvironmentalHazards/Source/
  RM_RootCausewayBiomeExtension.cs` — its build item,
  `ENVHAZARDS_DLL_REBUILD_OWED_1`, is `proposed` (not `doing`) — a stale
  deploy-vs-source DLL note, not active code work. Full read plus its
  consumer, `RM_GenStep_RootCauseways.cs`, to cross-check field names
  (`causewayTerrain`, `basinTerrains`, `pathsPerAnchorRange`,
  `laneWidthRange`, `pathLengthRange`, `turnChancePerStep`,
  `fallbackAnchorCountRange`/`fallbackMinAnchorSpacing`/
  `fallbackEdgeMargin`, `additionalPasses`) — all match exactly,
  `ConfigErrors()` correctly implemented. No bug. Marked CLEAN.

8 files marked CLEAN this wave (1 large file done via a verified subagent
pass, 7 read directly), 4 real bugs found and fixed across 3 files. All
selftests re-run: `run_selftests.py` reports 57/60 passed — the 3 failures
(`selftest_art_checks.py`, `selftest_one_path_seam.py`,
`selftest_tool_metadata.py`) are all **pre-existing and unrelated** to this
wave's files (a Nuna sprite art-boundary check, a `LocalLow` path literal in
`build_flora_legibility_sheet.py`, and a missing local JawaBench DLL build
in this worktree) — none touch `model.py`, `naming_lint.py`,
`PawnFlavorPhase2_ThoughtDef.xml`, or any of the other 5 files this wave
reviewed. `selftest_model.py` itself: 67/67.

`code_review_status.py list`, freshly re-run at the end of this wave:
**2853 clean / 88 dirty / 2 orphaned** — re-run `list` fresh, don't trust
this figure past this session, exactly like every prior restart note says.

## Skipped this wave, and why (gates re-verified fresh, not inherited)

- `src/RimMandrake/FlowWorks/**` (~23 dirty) — `FLOWWORKS_BUILD_PROGRAM_1`
  still `doing`.
- `src/RimStarWars/SWBestiary/*` Mlie files, `RustCathedralHum/
  RUT_CoolantEel.xml`, `src/RimMandrake/Utils/modset_builder.py` —
  `FISH_BESTIARY_BUILD_1` and/or `MLIE_FAUNA_ABSORPTION_1` `doing`
  (FISH_BESTIARY_BUILD_1 is NEW since RESTART_16, filed 2026-09-18).
- `src/RimUtinni/ShipShields/*` — `SHIELD_MODS_LEVERAGE_1` `doing`.
- `src/RimMandrake/RimProperty/*` — `SETTLEMENT_VERBS_WAVE_1` `doing`.
- `src/RimMandrake/Ninefold/Source/*` — `NINEFOLD_ENGINE_M0_1`/
  `NINEFOLD_MISSING_EVENT_HOOKS_1` `doing`.
- `src/RimMandrake/Utils/expectations_manifest.py`, `run_expectations.py`,
  `selftest_expectations_manifest.py`,
  `src/RimMandrake/bridgetools/JawaBench.BridgeTools/
  JawaBenchTerrainTools.cs` — `MASS_VALIDATION_LADDER_1` `doing`.
- `src/RimMandrake/Utils/structure_roster_lint.py` —
  `TILE_STRUCTURE_DESIGNS_1` `doing` (its one recent touch was a 2-line
  incidental edit inside an unrelated Kiln-ruling commit, but the item
  itself is still actively `doing`, so left it — the safer read of "gate
  decays fast, re-verify" is to trust the item state over a guess about
  one commit's actual scope).
- `src/RimMandrake/Utils/gm_blackboard_shadow.py` —
  `GM_BLACKBOARD_SHADOW_M4_1` `doing`.
- `src/RimMandrake/Greentide/*` — `GREENTIDE_MECHANICS_2` `doing`.
- `src/RimUtinni/ShokkweaveEconomy/About/About.xml` —
  `SHOKKWEAVE_SOLE_SOURCE_1` `doing`.
- `src/RimStarWars/Droidworks/Defs/PawnKinds_*.xml`,
  `gen_droidworks_defs.py` — `DROIDWORKS_PRIMITIVE_TIER_1` family still
  `doing` (not re-verified line-by-line this wave; carried from RESTART_16
  on the strength of the gate still showing recent commits).
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/*`,
  `design/Jawa/fauna/BiomeCast_Ashkarr.xml`,
  `src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml` and the
  `RUT_*_BiomeWiring.xml`/`RUT_*_Lock_BiomeWiring.xml` files — each ties to
  an actively-`doing` biome-kit build item (Greentide/Scald/Rot/Wasteland/
  WeepingStones/CrackedLands), same as every prior restart's account; the
  generated-file regression on `BiomeCast_Ashkarr.xml` is still open,
  still needs whoever owns `gen_cast_patch.py`.
- `src/RimStarWars/Armoury/Defs/Absorbed_KotorWeapons/.../
  Absorbed_KotorWeapons_WeaponRanged_KotORIonPistol.xml` — still needs an
  owner design call on the dead `KotORElectricBolt` projectile reference
  (unchanged since RESTART_15).
- `src/RimUtinni/RustCathedralHum/*`, `Pyrelands/*`, `Inhabited/*`,
  `StructureInjections/About/About.xml` — not investigated this wave
  (budget), several plausibly tied to the same FISH_BESTIARY_BUILD_1 /
  Pyrelands-item cluster that's newly active since RESTART_16; check gates
  fresh before touching, do not assume from this list.

## Recommended next steps, in order

1. Re-run `code_review_status.py list` fresh — do not trust the 2853/88
   figure above past this session.
2. `rimflow show DIRTY_CODE_REVIEW_STANDING_LOOP_1` and `rimflow show
   FISH_BESTIARY_BUILD_1` before picking anything fish/biome-adjacent —
   FISH_BESTIARY_BUILD_1 is new and actively claiming files across several
   mods this session.
3. `src/RimUtinni/RustCathedralHum/*`, `Pyrelands/*`, `Inhabited/*`,
   `StructureInjections/About/About.xml` — re-check their gates fresh, not
   investigated this wave.
4. The 3 pre-existing selftest failures
   (`selftest_art_checks.py`/`selftest_one_path_seam.py`/
   `selftest_tool_metadata.py`) are real and worth a look by whoever owns
   art-checks/the path-seam/bridgetools, but are unrelated to this loop's
   file-cleaning scope — not filed as a new item this wave, just flagged.
