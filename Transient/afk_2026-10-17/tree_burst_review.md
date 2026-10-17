# Tree burst build review (2026-10-17, BENCH AFK)
Review of c698bbe683's three DIRTY files plus a spot-check of its core C#.

## DIRTY files: each read in full, fixed, marked clean
- `Source/SelfTest/ExplosiveGrowthFuzz.cs`: one latent false-FAIL. The tree-rate ceiling invariant left out `s.dryDry`, and the random sliders allow up to 1.01. Fixed to include it.
- `validation.py`:
  - `probe_tree_life` would false-FAIL "threw no logs" on a Rupture-top (Contagion) tree, whose burst is its Rupture (Q15). It now skips the log check on `rupture:1`.
  - The young-gain message now prints the same `min(0.8, 10/gd)` that the check uses.
  - DEFAULTS match ExplosiveGrowthMod.cs field for field (scripted compare).
- `northstar_site.py`: no defects. DEFAULTS have the same keys and values as validation.py.

## Spot-check of core C# (RM_TreeLife, RM_TopResolver.TreeBurst, TickLong prefix, registry): no defects
- TickLong: the patch is a Plant.TickLong prefix. The only override in src/ (Pyrelands PlantGrowthStages) calls base first and checks Destroyed afterwards.
- Save/load: no new per-plant or per-map state. Drinks write vanilla's `ageInt`/Growth, which vanilla saves. The `Last*` statics are proof read-outs only.
- WoodLog guard: TreeBurst is reached only for `isTree` (OnTickLong goes through TreeRulesHere; the forced-top path checks `prof.isTree`). The non-tree drop path keeps the guard.
- Greatbole: RM_Greatbole is in the roster's `treeRulesExempt`, so `isTree` is false. It keeps only the old treeRatio path.

## Build / selftests
The mod DLL is unchanged; only the selftest project changed, and the fuzz selftest rebuilds it. run_selftests: explosivegrowth fuzz, archetype_seed and gpt_fixes all PASS (3/3, GREEN). validation.py static: PASS.

## Owed
probe_tree_life / probe_tree_burst_off have never run live. They need the BENCH live agent.
