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

## Round 3 (2026-09-13, FOUNDRY) — Sinkhole root-caused and fixed, 8/8 mechanism now proven

Round 2 left Sinkhole at 1/8 attempts across two rounds, root cause not found
(`Transient/mapgen_gl2/README.md`). Read the shipped `LandformSinkhole.xml`
vs `LandformCanyon.xml` WorldTileReq nodes directly: Sinkhole ships
`Topology=CliffAllSides` (Canyon: `CliffValley`) and `HillinessRequirement=
{6,6}` exact-match (Canyon: `{1,5}`). `gl_emit.py --from`'s own
`tile_req_overrides` already loosens hilliness to `(0,6)` unconditionally,
but `topology` only gets overridden when `--topology` is explicitly passed
(`gl_emit.py:566`) — whatever generated round 1/2's recipes evidently never
passed it for Sinkhole, leaving `CliffAllSides` (a topology essentially never
rolled) as the live requirement.

**Fix, live-verified on `ModsConfig.VANILLA_BRIDGE_GL.xml`:**
`gl_emit.py --from <SinkholeSource> --id RUT_Gen_0Nfix --out ... --topology Any
--rotate <plan's orientation_deg>`. Both `RUT_Gen_05fix` and `RUT_Gen_06fix`
applied on the FIRST tile rolled after a restart (Player.log `Landforms:
RUT_Gen_0Nfix`), screenshots confirm an unmistakable readable sinkhole for
both (`Transient/mapgen_gl3/RUT_Gen_05fix.png`, `RUT_Gen_06fix.png`) — full
writeup and evidence table in `Transient/mapgen_gl3/README.md`.

Combined with round 2's already-proven 6 (Canyon x4, LoneMountain, Crater),
**all 8 of 8 landform categories now have a live-proven GL application** —
the mechanism gap is closed. **Not yet done:** compositing the final 8-image
comparator sheet (swap the two grey "no GL shot" tiles in
`comparator_gl_vs_painter_v2.png` for these two real screenshots via
`compose_gl_vs_painter.py`) — that is the one step left before this item is
ready for the owner's keep/cut per its own `PROVE` line. Housekeeping done:
custom landform file removed, `ModsConfig.xml` restored to the full list, game
relaunched via Steam (not the bare `.exe`), bridge to be released once the
full-list reload is confirmed healthy.
