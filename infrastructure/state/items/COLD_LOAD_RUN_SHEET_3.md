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
- ⚠️ Companion DLL (`JawaBench.BridgeTools.dll`) is **NOT** re-deployed by this
  pass — separate tool. `build.py`'s own deploy-plan gate reported the
  currently-deployed copy (commit `f8b647e7ce24`) carries several tools
  (`jawa/pawn_*`, `jawa/lord_*`, `jawa/weather_*`, others) that a fresh build
  from current HEAD does not — pre-existing drift, unrelated to today's
  `INHABITED_SETTLEMENT_PRODUCER_GAP_1` change (verified: every one of those
  tool names still has a live source file; only `JawaBenchWorldTools.cs` was
  touched today). **Owed before the next launch:** `git log` the companion
  source to find where those tools left the build (or the deploy simply never
  ran for whatever removed them), THEN `build.py --gm --apply` —
  `--allow-tool-removal` should not be passed blind.
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

## 2 — other items waiting on a game-up/deploy signal, pointer only
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
