# TILE_STRUCTURE_DESIGNS_1

Thin item — FOUNDRY decision on spec/verify/criteria, 2026-08-31.

## spec

`design/Jawa/worldbuilding/structure_injection_roster.md` (the content
list) and `design/Jawa/bridge/STRUCTURE_TEMPLATE_ENGINE_SPEC.md` §8-9 (the
engine: rimplace Lua templates, format axis decided, generation axis
staged 🅐→🅑, `GenStep_RimplacePlan` named as the one missing C# piece).

**Scope for this pass, decided by FOUNDRY:**
1. Build `GenStep_RimplacePlan` (`mandrake.rm.injections`, engine tier per
   the naming scheme's engine/content split) — replays a compiled
   rimplace plan at mapgen time. Verify terrain/roof ordering live, per
   the roster's own flag.
2. Author a first batch (3-5 rows) of the 44-row roster as rimplace `.lua`
   templates, per the roster's own §5 "FOUNDRY iteration protocol"
   (batch of 3-5, render sheet, not all 44 blind).

**Collision note:** `src/RimMandrake/Utils/rimplace/plan.py` and
`cli.py` had live uncommitted edits from another window when this item
was picked up (a `compile_flat()` flat-text plan compiler, docstring:
"the flat runtime format GenStep_RimplacePlan reads at mapgen time").
FOUNDRY did not edit either file — built `GenStep_RimplacePlan` to read
that documented flat format from a new, non-colliding location
(`src/RimMandrake/StructureInjections/`) instead of duplicating a JSON
compiler.

## verify

- Offline: the C# compiles clean, and a plan exported by
  `rimplace ... export` round-trips through `RimplacePlan.Parse` with
  every defName present.
- Live: build a test structure on a quicktest map via the new GenStepDef
  wired to a scratch `TileMutatorDef`/debug action, confirm
  terrain→foundation→things(transmitters-first)→roof land in the right
  order and the plan's defnames all resolve — the roster's own flagged
  risk.

## criteria

- `GenStep_RimplacePlan` deployed and proven on at least one existing
  template (`dwelling.lua` or `nursery.lua`) via a live quicktest.
- At least one new roster row shipped as a rimplace template, wired to a
  promise (LandmarkDef + TileMutatorDef + GenStepDef) or whisper
  (territory table row), following the roster's coverage lint (no
  promise without a registered responder).
- The remaining ~40 rows are explicitly left open for further batches,
  not silently declared done.

## 2026-08-31 batch 2 (FOUNDRY) — three more roster rows authored

Per the roster's own §5 protocol (batch of 3-5, offline verify, no live
placement). All lint/verify results independently re-confirmed by
FOUNDRY, not taken on a subagent's word alone (one fork's own summary
was internally confused about which items were done; the actual
`.lua` files and `lint`/`verify` output are the evidence, checked
directly):

- **The Krayt Graveyard** (row 3, RSW) —
  `design/Jawa/templates/krayt_graveyard.lua`. `lint`: 0 findings.
  `verify`: 3/3 defNames found.
- **The Podracer Wreck** (row 4, RSW) —
  `design/Jawa/templates/podracer_wreck.lua`. No "podracer engine"
  ThingDef exists in the stack (verified against the live dump, not
  guessed) — uses `AncientPodCar` (this project's own existing
  `PodCarIsLandspeeder.xml` reskin) as the one intact centerpiece plus
  vanilla `ChunkSlagSteel`/`Steel` scatter. `lint`: 0 findings. `verify`:
  3/3 defNames found.
- **The Hunting Lodge** (row 12, RSW) —
  `design/Jawa/templates/hunting_lodge.lua`. **Caught and fixed a real
  defect**: the template's own footprint requirement (3 bays ≥5 wide
  each + the cold room's power apron) needs 28×18, not the 20×16 first
  tried — `lint` correctly refused with `empty-plan`/`generator-refusal`
  rather than silently under-building. Re-verified clean at 28×18:
  `lint` 0 findings, `verify` 14/14 defNames found.

**Wiring added same pass**: `GenStepDefs_Batch2.xml` +
`TileMutatorDefs_Batch2.xml` in `mandrake.rsw.injections` give all
three (`RSW_KraytGraveyard`, `RSW_PodracerWreck`, `RSW_HuntingLodge`)
the same `extraGenSteps` responder wiring Moisture Farm has —
`validate_patch.py`: 0 errors on the whole content pack (5 files).
Still not "shipped" by the roster's own §5 bar: no letter text in the
gods' register, not placed on any tile (deliberately — a live world-tile
edit, out of scope here, same as Moisture Farm). 40 of 44 rows remain
untouched. Left `doing`.

## STATE 2026-08-31, session end (owner went AFK mid-item)

**Done, offline-verified:**
- `mandrake.rm.injections` (`src/RimMandrake/StructureInjections/`) —
  `GenStep_RimplacePlan` + `RimplacePlan.cs` parser for the flat runtime
  format `rimplace.plan.compile_flat()` emits (added to `plan.py`/`cli.py`
  as an `export` command — see collision note above, now resolved: the
  format landed clean, `selftest` 28/28 still passes). Ordering mirrors
  `compile_calls()`'s live-proven order exactly: foundation → terrain →
  things (transmitters via `ThingDef.EverTransmitsPower` before
  connectors) → roof. Builds clean (0 warnings, 0 errors). API calls are
  cited against decompiled 1.6 source, not guessed (`TerrainGrid.SetTerrain`/
  `SetFoundation`, `RoofGrid.SetRoof`, `GenSpawn.Spawn`, `TileMutatorDef.
  extraGenSteps` → `MapGenerator.cs:158-165`).
- A debug-action proof surface (`StructureInjectionsDebugActions.cs`,
  category `RMInject`) that replays an exported `.txt` plan at the mouse
  cell on the current map — bridge-reachable, same pattern as
  `PitDebugActions`.
- `mandrake.rsw.injections` (`src/RimStarWars/StructureInjectionsSW/`) —
  roster row 1, "The Moisture Farm": `design/Jawa/templates/moisture_farm.lua`
  (lint 0 findings, verify 9/9 defNames found), exported plan, a
  `GenStepDef` + `TileMutatorDef` (`RSW_MoistureFarm`) wiring it in via
  `extraGenSteps` — the actual responder mechanism, not a stub.
  `validate_patch.py`: 0 errors on both mods.
- 🔴 **Self-caught bug**: both mods were first authored as folders named
  `StructureInjections` under two different tiers
  (`src/RimMandrake/...` and `src/RimStarWars/...`) — `deploy_custom_mods.py`
  keys mods by folder BASENAME across all tiers, so the second deploy
  silently overlaid the first mod's `About.xml` in the live `Mods/`
  folder while orphaning its `Assemblies/`. Caught by reading the deploy
  plan output, not assumed clean. Fixed: content pack renamed to
  `StructureInjectionsSW`, the corrupted live folder deleted and both
  redeployed clean, `ModsConfig.xml` updated to the new packageId.
  **Lesson for future mods: folder basenames must be unique across the
  WHOLE `src/` tree, not just within a tier** — worth a line in
  `rimworld-deploy` or `deploy_custom_mods.py`'s own help text.

**Not done — owed to the next restart / a future session:**
- Live proof of `GenStep_RimplacePlan`'s ordering (the roster's own
  flagged risk) — needs a cold load with both mods active; restarts are
  the owner's call. Two ready-made debug actions
  (`Run plan: dwelling_test.txt`, `Run plan: moisture_farm_test.txt`)
  are wired for whoever drives the next load.
- The Moisture Farm is NOT yet a "shipped" roster row by the roster's own
  bar (§5): no letter text in Oomo's register, and not placed on any
  actual Ash'karr tile (deliberately deferred — that is a live world-tile
  edit on the frozen map, bridge + `world_commit`, out of scope here).
- 43 of 44 roster rows are untouched. The roster's own §5 protocol (batch
  of 3-5, render sheet, owner review) still stands for whoever picks this
  up next — this session did not try to force all 44 through solo.

