# RIMPLACE_GENSTEP_LIVE_PROOF_1 — the GenStep works; the thing that proved it did not

Live, 2026-09-02, BENCH, owner AFK. Full mod list (~400 active, NOT a minimal
tier), Ash'karr, fresh 250×250 desert map, `ticksGame 1`, paused.

⇒ **This discharges `TILE_STRUCTURE_DESIGNS_1`'s live-verify criterion** — *"build
a test structure on a quicktest map via the new GenStepDef, confirm
terrain→foundation→things(transmitters-first)→roof land in the right order and the
plan's defnames all resolve"* — the roster's own flagged risk. That item stays
FOUNDRY's; only its live gate is answered here.

## spec — what was run

`Actions\T: Run plan: dwelling_test.txt` (a `ToolMap` DebugAction in
`mandrake.rm.injections`) driven through `rimworld/execute_debug_action` with
explicit `x`/`z`. No mapgen, no world edit, no reload — the debug action calls
`GenStep_RimplacePlan.ApplyPlan` directly, which is the same implementation the
production `Generate()` path uses.

⭐ **Verified capability, worth keeping:** a `ToolMap` debug action that reads
`UI.MouseCell()` internally DOES honour the `x`/`z` the bridge passes. The action
ran at the exact cell named. That was an open question and it is now closed.

## verify — every planned cell checked against the live map

`dwelling_test.txt` (footprint 16×12), read back cell by cell via
`rimworld/get_cell_info`:

| layer | planned | present |
|---|---|---|
| terrain | 130 | **130** |
| things | 69 | **69** |
| roof | 192 | **192** |

⚠️ The log's `thingsSpawned=64` against 69 planned is NOT five failures — it is a
NET count (`AllThings` before vs after), and spawning into a cell destroys the
plant under it. All 69 are on the map. Do not chase it again.

**Foundation ordering was NOT exercised by either shipped plan** — neither
`dwelling_test.txt` nor `moisture_farm_test.txt` contains a single `FOUNDATION`
line, so `SetFoundation` had never run in this path. Covered it with a synthetic
6×6 plan (36 `FOUNDATION Substructure`, 16 `TERRAIN Gravel` on top, 20 `Wall`
ring, 16 `ROOF`), written over the hardcoded plan path, run, then the original
restored:

```
foundation → terrain → things → roof, read back with jawa/get_terrain_layers:
  16/16 cells   top: Gravel   foundation: Substructure   isSubstructure: true
  walls 20/20, roof 16/16
```

⇒ **The ordering guarantee holds, foundation included.** A floor laid over
substructure survives; the two layers coexist as intended.

## 🔴 the defect this found, and it is FIXED IN SOURCE

`ApplyPlan(map, plan, dx, dz, …)`'s `dx`/`dz` are an **offset added to every plan
cell** (`SetTerrainCell`: `new IntVec3(c.X + dx, …)`). `StructureInjectionsDebugActions.RunAt`
passed the clicked cell straight in — so a plan whose `FOOTPRINT` starts at
`100,100` (all of them do) built itself **100 cells away from the click**, while
the log printed `origin=(60, 0, 60)`, the cell you clicked.

Measured: clicked `(60,60)`, built at `(160,160)`. Verified against the click
cell it read as **0/130 terrain, 0/69 things, 3/192 roof** — a total failure of a
GenStep that had in fact worked perfectly. A silent-wrong-place bug that
publishes a confident wrong number is worse than a crash.

**Fixed** in `src/RimMandrake/StructureInjections/Source/StructureInjectionsDebugActions.cs`:
`dx = c.x - plan.FootprintX` (same for z), and the log now prints `clicked=` and
`offset=` rather than a fictional origin. `Build succeeded`, 0 warnings.

⚠️ **Built, NOT deployed.** `dotnet build` wrote
`src/RimMandrake/StructureInjections/Assemblies/RimMandrakeStructureInjections.dll`;
the game holds the deployed copy open. Deploy with
`python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod StructureInjections --apply`
at the next shutdown window. Until then the repo DLL is NEWER than the game's, so
an mtime comparison will read as "deployed" and be wrong.

## criteria
- [x] GenStep_RimplacePlan proven on a shipped template, live, full mod list
- [x] terrain / foundation / things / roof ordering confirmed by read-back, not by log
- [x] every defName in `dwelling_test.txt` resolved (69/69 spawned)
- [ ] deploy the debug-action fix (next shutdown window)
- [ ] the production path — a `TileMutatorDef` on a real Ash'karr tile + a generated
      map — is still unproven. No tile carries `RSW_MoistureFarm` or any sibling;
      every such def is commented "NOT YET PLACED". That is content wiring, and it
      is the remaining half of `TILE_STRUCTURE_DESIGNS_1`.
