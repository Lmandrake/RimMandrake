# MAPGEN_GL_SHEET_1 round 3 — Sinkhole root-caused and fixed

Round 2 (`Transient/mapgen_gl2/README.md`) left Sinkhole at 1/8 attempts
successful across two rounds ("narrowed but NOT root-caused"), naming its own
suggested next step: compare `gl_emit.py`'s Sinkhole base-graph mapping
against the shipped Sinkhole landform's own WorldTileReq.

## Root cause

Read the shipped `LandformSinkhole.xml` and `LandformCanyon.xml` WorldTileReq
nodes directly (`/mnt/c/.../workshop/content/294100/2773943594/1.6/Landforms-v1/`):

| field | Canyon (works) | Sinkhole (failed) |
|---|---|---|
| `Topology` | `CliffValley` | **`CliffAllSides`** |
| `HillinessRequirement` | `{1, 5}` | **`{6, 6}`** — exact match, the rarest tier |

`gl_emit.py --from <source> --id ... --out ...` (the documented CLI path,
`build_desertplateau`'s `tile_req_overrides`) already loosens `hilliness` to
`(0.0, 6.0)` unconditionally — that part was never the problem. But
**`topology` only gets overridden if the caller explicitly passes
`--topology`**; left unset, it falls straight through to the SOURCE's own
value (`gl_emit.py:566`, `tro.get("topology", kwargs.get("Topology", ...))`).
Whatever ad-hoc script generated round 1/2's eight recipes evidently never
passed `--topology` for Sinkhole, so its recipe kept `CliffAllSides` — a
topology so rare that 6 tile re-rolls across two rounds never once hit it,
while Canyon's `CliffValley` (also unloosened) apparently WAS satisfied by the
tiles it landed on. (Canyon's own recipe generation is likewise lost — no
batch script survives in the repo from round 1/2, so this is read from the
observed behaviour, not a second source file.)

## The fix, live-verified

`gl_emit.py --from <SinkholeSource> --id RUT_Gen_0Nfix --out ... --topology Any --rotate <plan's orientation_deg>`

Tested both Sinkhole plans (`Transient/mapgen_v0/seed05.plan.json`,
`seed06.plan.json`) on the `ModsConfig.VANILLA_BRIDGE_GL.xml` minimal list,
one full process restart per recipe (confirmed the custom-landform folder is
NOT re-scanned by `go_to_main_menu` + `start_debug_game_ready` alone — a
process restart is required to pick up a swapped recipe file, unlike a
same-recipe tile re-roll which needs no restart):

- **`RUT_Gen_05fix`**: applied on the FIRST tile rolled (`TileId 33281`,
  Player.log `Landforms: RUT_Gen_05fix`). Screenshot `RUT_Gen_05fix.png` — an
  unmistakable sinkhole: a bright circular pit with a lake at the floor,
  ringed by cave-tunnel branches.
- **`RUT_Gen_06fix`**: applied on the FIRST tile rolled after a restart
  (`TileId 93069`, Player.log `Landforms: RUT_Gen_06fix`). Screenshot
  `RUT_Gen_06fix.png` — same readable pit shape, different orientation/relief
  per its plan.

**2 of 2 on the first try**, matching every other category's typical success
rate (Canyon/LoneMountain/Crater all applied first or second try in round 2)
— confirms the Topology override was the actual blocker, not tile rarity or
bad luck.

## What this completes

Combined with round 2's already-proven 6 (Canyon x4, LoneMountain, Crater),
**all 8 of the item's 8 landform categories now have a live-proven GL
application** — the mechanism gap round 2 flagged as its biggest open item is
closed.

**`comparator_gl_vs_painter_v3.png`** — the full 8/8 sheet this item's own
`PROVE` line asks for, built by re-rendering all 8 painter grids fresh from
`Transient/mapgen_v3/seed0N.grid.txt` (the current painter output, into
`renders/`) and running `compose_gl_vs_painter.py` against round 2's 6
existing GL screenshots plus this round's 2 new Sinkhole ones. All 8 rows
report `APPLIED`. **The generalised convergence signal round 2 first named
on Canyon holds across every category, not just Canyon**: GL's real terrain
(top row) is organic, branching, cave-riddled and irregular everywhere;
the painter's v3 output (bottom row) is still bold-outlined and comparatively
geometric (near-perfect rings for Sinkhole/Crater/LoneMountain, a fairly
straight diagonal band for Canyon) even after two painter rounds. This is
exactly the kind of side-by-side evidence `MAPGEN_PAINTER_V1_1`'s next round
and `MAPGEN_CONVERGENCE_LOOP_1` need — not a re-litigation of round 3's own
"hold painter round 4" call, just the data that call was waiting on.

`renders/seed0N.png` (fresh v3 painter renders) and
`comparator_gl_vs_painter_v3.png` are committed. `shots/` (the working
directory `compose_gl_vs_painter.py` reads) is NOT committed — it is exactly
round 2's 6 `Transient/mapgen_gl2/RUT_Gen_0N.{png,log.txt}` files plus this
round's `RUT_Gen_05fix.png`/`RUT_Gen_06fix.png` (already committed above)
copied to the `RUT_Gen_0N.png`/`.log.txt` names `compose_gl_vs_painter.py`
expects; reconstructible in one `cp` pass rather than duplicating six
already-committed screenshots a second time.

**Ready for the owner's keep/cut** on `comparator_gl_vs_painter_v3.png` —
this item's own `PROVE` line is now fully met.

## Housekeeping

Custom landform file removed from `Config\CustomLandforms-v1\` after each
test; `ModsConfig.xml` restored to the full list and the game relaunched via
Steam at the end of this session (not the bare `.exe`, per
`rimworld-load-round`'s own measured Harmony-corruption trap).
