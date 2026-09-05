## Spec
Successor to COLD_LOAD_RUN_SHEET_2 (closed 2026-09-03 after the big-dump load —
its own record stays there). Filed thin (no spec/verify/criteria); written down
by FOUNDRY, 2026-09-04. Same shape as its predecessors: the next batched
full-list window scores everything below, then this closes and a fresh sheet is
filed. Detail for any named item lives in `items/<ID>.md`.

## 0 — deploy, before the next launch ✅ DONE 2026-09-04 (FOUNDRY)
```
python.exe src/RimMandrake/Utils/deploy_custom_mods.py --apply
```
- ✅ Applied: 8 files across 4 mods that were drifted ahead of the deployed
  copy — Droidworks (`About.xml`, `Patches/OnlyOurFactions.xml`), HelixTellurox
  (`About.xml`, new `Patches/ThirdPartySignConfigErrors_Fix.xml`), Livestock
  (`Karrask.png` + 2 def XMLs), ShipMemory (`RimMandrake.Utinni.ShipMemory.dll`
  — the source this repo marked CLEAN 2026-09-04 needed a rebuild+redeploy to
  actually reach the game copy). Re-run confirms "Everything in sync."
- ✅ RESOLVED same day: the companion "would lose 35 tools" warning above was
  just the missing `--gm` build flag, not real drift — rebuilding with
  `build.py --gm --apply` carried every tool forward correctly (verified live,
  `INHABITED_SETTLEMENT_PRODUCER_GAP_1`'s quicktest). No action needed here
  beyond remembering `--gm` is never optional on this companion.
- ⚠️ **NEW, owed before the next launch**: `RimMandrake.Utinni.Antiquities.dll`
  (the new `mandrake.rut.antiquities` mod, see item 2 below) is drifted ahead
  of its deployed copy — a bugfix build made while the game was UP tonight,
  correctly not force-deployed since the OS locks a loaded assembly.
  `deploy_custom_mods.py --mod Antiquities --apply` at the next shutdown
  window.
- Most `not enabled in ModsConfig` lines in the dry-run output are expected
  noise from the minimal-list regime currently active for cheap testing
  (`rimworld-minimal-modlist-regime`) — restore the owner's full list before
  trusting a load against this sheet.

## 1 — decision strings at launch, in the order they were written
### 1. Rites + ResearchRetag first load (BENCH, 2026-09-04)
Superseded from `EXPECTED_FAILURES_next_load.md` (that file now points here).
Two NEW XML-only mods activated at the ModsConfig tail (591 active at the
time this was written; backup `ModsConfig.xml.pre_rites_retag_20260904`):

| cargo | expected-PRESENT | failure looks like |
|---|---|---|
| `mandrake.rut.rites` (5 ResearchProjectDefs + 1 ResearchTabDef, defs only) | "the rites" tab visible in the research window; `measure`/dump shows 527 ResearchProjectDef (was 522) | red XML error naming RUT_Rites_*; tab absent |
| `mandrake.rut.researchretag` (269 defs patched: 185 techLevel, 103 baseCost, 113 prereq lists, all match/nomatch-guarded) | patch-failure count stays at baseline 6 (the 6th is the pre-existing lightsaber FindMod); spot-check via bridge: `guy762_ResearchKotOR_blasters` prereq = hvyblasters, baseCost matches manifest | "[Research Retag] Patch operation ... failed" lines; a red-error storm at def resolution naming research defs; `Could not resolve cross-reference` naming a research defName |

⚠️ The retag's effect is INVISIBLE on the minimal list (conditionals no-op
without the content mods) — proof requires the FULL-list load. A fresh dump
after that load also folds the 5 Rites rows into the manifest (coverage
becomes 527) — rerun `research_manifest_validate.py` then.

### 2. Antiquities + Rites reveal mechanism (FOUNDRY, 2026-09-04, same day)
`ANTIQUITIES_TREE_BUILD_1` slice 1 (`mandrake.rut.antiquities`) and
`RITES_REVEAL_MECHANISM_1` both landed tonight — `mandrake.rut.antiquities`
added to the live list (595 active) alongside Rites/ResearchRetag. Decision
strings:
- PASS: `RUT_Antiquities` tab visible with 5 nodes, all initially
  un-selectable (`CanStartNow` false — proves the never-buildable
  `requiredResearchBuilding` gate). `RUT_Rites_ConduitChoir` (and the 3
  tiers after it) render in the `RUT_Rites` tab GREYED/locked even once
  their own `<prerequisites>` chain is satisfied — that greyed state IS the
  pass condition (owner-ruled visible-locked, not truly hidden).
- FAIL: `Could not resolve cross-reference` naming any `RUT_Antiq_*` or
  `RUT_AntiquityReadingStation`/`RUT_AntiquityCipherBench`; `Config error in
  RUT_` (should be zero — both known config/texture errors were fixed and
  live-verified before tonight's commits).
- Live-verified already, does NOT need re-proving this load: the reading
  loop itself (quicktest, `ANTIQUITIES_TREE_BUILD_1`'s own item file has the
  full trace) and the hiddenPrerequisites defName mapping (source-read
  against `RimWorld/MainTabWindow_Research.cs`). What's genuinely new here
  is only the FULL-list, real-campaign-mods context — the quicktest used a
  19-mod list and can't see cross-mod load-order effects.

## 3 — other items waiting on a game-up/deploy signal, pointer only
Full detail lives in each item's own file — not duplicated here so there is
one place to keep it current. Check each is still live before scoring it.
- `WEAPONS_DONOR_RETIREMENT_1` — retire the 6 weapon donor packs; 1 of 6
  broke the owner's live game before, reverted. `needs: game-up`.
- `INHABITED_STOCK_ONTO_MAP_AND_FATE_1` — spawn a place's stock onto its map,
  collect it back, wire InhabitedFate. `needs: game-up`.
- `MASS_VALIDATION_LADDER_1` — batched validation ladder (get_defs
  deep-serialize, manifest runner, hot-reload trial, first review
  environment). `needs: deploy`.
- `DEV_LOG_AUTOOPEN_SUPPRESS_1` — suppress dev-mode auto-open of the error
  log (Harmony prefix in JawaBench). `needs: deploy`.

Explicitly NOT on this sheet: `INHABITED_SETTLEMENT_PRODUCER_GAP_1`'s live
verify (world_settlements_import's new world_object_def column) — its own
item note says it is provable on the 22s minimal list via a quicktest/bridge
session, not the full list, so it does not belong on a FULL-LIST run sheet.
