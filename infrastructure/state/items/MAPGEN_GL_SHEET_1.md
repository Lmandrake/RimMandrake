# MAPGEN_GL_SHEET_1 — the generator's terrain through Geological Landforms, one sheet of real in-game maps

Owner 2026-09-06 (research doc §8 #9): both routes; GL is the real output. Bridge work.

## spec

- Input: the 8 plans `Transient/mapgen_v0/seed0[1-8].plan.json` (or fresh ones from
  `mapgen_v0.py --batch`). For each plan, `gl_emit.py` writes a GL recipe: landform
  Id → the matching shipped GL graph as the base (Canyon, Crater, Sinkhole,
  LoneMountain, DesertPlateau, Badlands, Rift, Gorge, Cirque, SecludedValley), the
  plan's `landform_params` mapped onto that graph's exposed knobs (Perlin
  frequency/octaves, linear function slopes, rotation from `orientation_deg`),
  Id `RUT_Gen_<seed>`, IsCustom, commonness 1, permissive `worldTileReq`. Only ONE
  custom file in `Config\CustomLandforms-v1\` at a time (GL draws by commonness —
  two at 1.0 would compete), so: write file → restart minimal+GL (36 s) → quicktest
  → Player.log `Landforms: RUT_Gen_<seed>` → screenshot with a unique name → remove
  file → next. ~8 × 2 min.
- Sheet: the 8 screenshots (cropped to the map) beside the 8 painter renders of the
  SAME plans (`render_terrain.py --sheet`), captions = premise. That side-by-side IS
  the convergence measure the owner asked for.
- Housekeeping every time (§5.8 d): no custom landform file left in the live config;
  `modlist_swap.py --restore --apply` at the end; bridge released.

## verify

```
PROVE   8 Player.log lines 'Landforms: RUT_Gen_<seed>', 8 screenshots, one sheet; owner keeps/cuts on it
EXPECT  every GL render shows the plan's ONE landform; the owner names the gap between painter and GL per map
LIES    a GL that silently skipped a malformed recipe and drew a stock landform — the log's Landforms field is the proof, never the picture alone
```

## not chasing

Structures, residents, dressing; the painter's fidelity (MAPGEN_PAINTER_V1_1).
