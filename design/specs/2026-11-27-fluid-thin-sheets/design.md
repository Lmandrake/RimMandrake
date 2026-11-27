# FlowWorks 0.2.0: fluids as thin sheets on the ground

Item: RIMMANDRAKE_DESIGN_FLUID_THIN_SHEETS_TAR_SHOWED_MISTY_GREY (his words "NEXT VERSION").
Folded in: RIMMANDRAKE_ANIMATE_POUR_SPILL_SHEET_ARRIVES_ALL_AT_ONCE ("I wanted to watch the water bulge
and move", 2026-11-12) and his row 10f ruling of 2026-11-14 ("ALL game wetness should now migrate to a thin film").
Status: design for his look. Nothing here moves a 0.1.0 bar. All work is on the 0.2.0 line.

## 1. What is wrong now (measured)

- Station 75 (walk 3, 2026-11-25, picture 8.png): poured tar shows as translucent grey-purple squares on brown soil.
  The cause is in `SectionLayer_RMSheetWater.MatFor(FluidDef, Tier)`. A non-water sheet draws with the colour of
  the brim terrain def (`fillTerrainBrim ?? floodTerrain`). RM_Fill_Tar_Brim is (86,82,88), a mid grey. Alpha is
  0.30 for Film, so the soil shows through and the tar reads as mist.
- The pit draws tar from a different source: the RM_Liquid_Tar surface look (tint (0.07,0.065,0.06), near black,
  owner 2026-10-05: tar "should look like black liquid"). Pit and ground disagree for the same liquid.
- Oil, Blood and Astrofuel have no look row at all. They fall back to brim colours.
- Each wet square is one hard quad of plain WhiteTex. The edge is a staircase. Opacity has three steps (tier).
- `RM_SheetMath.ResolveSpills` fills up to 16 lips to the 50 cm cap in one call. A big pour appears complete in
  one frame. `Level` (D8, "sheets lie level", card 2026-10-22) then flattens each puddle exactly every pulse.
  No bulge can exist. This is why he could not "watch the water bulge and move".
- `Sweep` ignores viscosity. Tar spreads at the speed of water. Viscosity only slows soak and evaporation
  (`RM_SheetFluidMath.RuleFor`).
- The mesh redraws only on a tier change or a spill (`EnginePulse`, `rep.TierChanged`). Between pulses
  (250 ticks) nothing on screen moves.
- Station 22: "stacks of 'layered' blue". Two translucent surfaces lie over one square.

## 2. What the player sees: each liquid as a thin sheet

General rules for every liquid:
- One look source. The ground sheet uses the same `RM_LiquidLooks.LookOfFluid` row as the pit: tint, shader,
  sheen, seeThrough. The brim terrain colour is no longer a look source.
- Opacity follows depth smoothly, not in three steps. A film (under 3 cm) shows the ground through it. A sheet
  shows the ground faintly. A pool (15 cm and more) hides the ground. Each liquid has its own floor: tar and
  slime are opaque even as a film; water stays the most see-through.
- The edge is a smooth, irregular line. It is not a square outline. A thick liquid has a rounded, raised-looking
  edge (a darker rim and a highlight line). A thin liquid has a soft, feathered edge.
- Far zoom: the liquid reads by hue and value only. Tar is a black shape; water is a blue-grey shape; blood is a
  dark red shape. Close zoom: the sheen, the moving front, ripples and flecks show.
- One surface per square. No liquid layer draws over another liquid layer on the same square.

| Liquid | Colour | Sheen | Edge | Thin film (close) | Pool (far) |
|---|---|---|---|---|---|
| Water | blue-grey, see-through | ripples, small glints | soft, feathered | ground clearly visible, darkened | blue, ground hidden |
| Tar | near black (pit tint) | broad soft gloss | thick, rounded, dark rim | black, opaque, glossy | black mass |
| Oil (new row) | brown-black | strong gloss, faint rainbow | thick, rounded | dark brown gloss | brown-black |
| Chemfuel | amber | rainbow film sheen | thin, runs | amber tint, iridescent | amber |
| Blood (new row) | dark red | low gloss | medium | dark red, dries to brown | dark red |
| Slimes (4) | red, green, white, yellow | Flow shader gel | thick, rounded | opaque gel colour | gel colour |
| Propane | clear, frosted | vapour puffs (AirPuff) | thin | faint frost, puffs | pale grey |
| Acid | yellow-green | bubbles | thin | yellow-green tint | yellow-green |
| Poison | green | ToxicWater ramp | thin | green tint | green |
| Boiling water | pale blue | steam puffs, bubbles | soft | wet look plus steam | pale blue |
| Icy water, Ice | white-blue | matt | crisp | frosty | white |
| Reaction liquor | pale violet | overlay sheen | thin | violet sheen | pale violet |
| Astrofuel (new row) | pale cyan | cold sheen | thin | pale cyan | cyan |

## 3. How a sheet moves over time

The "bulge and move" (his 2026-11-12 words):
- A pour arrives over time, not at once. A pour point shows a raised mound (a darker, more opaque spot) and
  a front that moves out ring by ring. The mound sinks as the front grows. When the pour ends, the sheet
  comes level at the pace of its liquid.
- Between pulses the front moves smoothly on screen. Each touched square fades from its old depth to its new
  depth over the pulse.

Viscosity per liquid (from each FluidDef's own ticksPerTile, the same ratio the channels use):
- Water, chemfuel, propane, acid, poison, boiling water, icy water, reaction liquor, astrofuel: run. The front
  moves fast. The sheet comes level in a few pulses.
- Blood: a little slower than water.
- Oil: slow.
- Tar: creeps. The mound stays visible for a long time. The front advances slowly with a thick edge.
- Slimes: slowest. A gel that holds its shape longest.

Slope:
- RimWorld ground is flat. The only downhill is dug ground (pits, trenches, canals) and the kernel's
  micro-relief. This design adds no height map (Principle 5; no worldgen ruling).
- Liquid beside an open hole with room runs into that hole. This exists now as Receivers; it stays.

Soaking and drying:
- Soak stays per ground (sand 4, soil 2, gravel 1 cm/day; 0 on rock, floors, ice, mud, water). It is scaled
  by viscosity as now. Tar soaks very slowly.
- Drying stays per temperature and roof. Chemfuel evaporates fast. Propane boils off.
- As a sheet dries below the flow limit (retention, 1 cm), it stops being liquid and becomes damp ground
  (section 4). A non-water liquid leaves a stain (section 4).

## 4. How a sheet joins the thin-film wetness (row 10f)

One state, from the kernel's own numbers:
- Damp is depth above 0 and at or under retention. The kernel already holds this water: it does not flow.
- Damp draws as darkened ground, not as liquid. It draws only on ground that soaks (`SoakCmPerDay > 0`).
  Tile, cement and other floors do not change (his words). Rock does not change.
- Damp has no path cost, gives no SoakingWet, and does not drown crops. This keeps `wetting_is_not_flood`
  ("wetted ground is never drawn or behaving as standing water").
- Damp dries at the same drying rate. Evaporation leaves wet ground for a while (his row 10d).
- Canal wetting (`canal_wets_two_squares`): the canal tops up undug neighbours to retention. The canal pays
  for it in dL, so the ledger still closes.
- Plants drink the damp film (the 0.2.0 irrigation bar, `inv_irrigation`). `wetness_probe` reads damp dL.
- Drained natural water reveals mud with a wet film that dries (row 10f). The all-game owner of that is
  RIMMANDRAKE_DESIGN_SPILLED_WATER_WET_GROUND_ONE_STATE. This design gives it the interface: a cell's
  damp dL and the damp draw.
- Rain: one map-wide dampness value on unroofed, soaking ground, with no per-square state (Q2).
- Non-water liquids: when the last film dries, the square keeps a stain that fades over days. Tar and oil
  stains are dark; blood is brown; slime is pale. A stain is a look only (Q3).

## 5. Code changes

`Source/Sheet/SectionLayer_RMSheetWater.cs`
- `MatFor(FluidDef, Tier)`: get the material from `RM_LiquidLooks.LookOfFluid(f)` (tint, shader, seeThrough).
  Remove the brim-colour path. Keep the brim colour only as the last fallback, with a WarningOnce.
- `Regenerate()`: draw per-vertex colour and alpha with `RM_WaterLooks.Quad(...)`. Each corner takes the mean
  depth of its four squares. Split each edge square into 2x2 sub-quads (marching squares) so the edge is a
  curve. Add a small edge offset from the kernel's `Relief` value so the line is irregular and stable.
- Alpha from depth: a new `RM_LiquidLooks.SheetAlpha(look, dL)`, a smooth curve from a per-look floor to 1.
- Damp: a second, opaque-free pass that draws darkened ground (multiply tint) on soaking terrain only.
- One surface per square: if a pit liquid surface already draws on a square, the sheet does not draw there.

`Source/RM_LiquidLooks.cs`, `Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml`
- Add look rows for RM_Fluid_Oil, RM_Fluid_Blood and RM_Fluid_Astrofuel (as `surfaceLook` on the FluidDef).
- Add `sheetAlphaFloor` and `edgeThickness` fields to `RM_LiquidSurfaceLook`, and `stainColor`.

`Source/RM_SheetMath.cs` (Verse-free, compiled into SelfTest)
- `FluidRule`: add `SpreadPermille` (Sweep pace) and `SettlePermille` (Level pace). Both come from
  ticksPerTile in `RM_SheetFluidMath.RuleFor`, by the same ratio as `RM_StockMath.ViscosityStride`.
  The World defaults are 1000, so every 0.1.0 offline test keeps its result.
- `Sweep`: scale the per-pair flux by the slower `SpreadPermille` of the two cells.
- `LevelPuddle`: move each cell `SettlePermille/1000` of the way to the level, not all the way. A puddle at
  rest still lies exactly level (D8 holds at rest). A puddle being fed holds a mound (Q1).
- New `PourQueue` (in `State`, saved): each entry is origin, fluid, dL left, dL per pulse. `Pulse` offers
  one share per pulse through the existing `ResolveSpills`. The ledger gains a `Pouring` term:
  `In == Standing + Returned + JoinedLake + Soaked + Evaporated + Burned + Purged + Pouring`.
- `State.KernelVersion` goes 2 to 3. Load of a version-2 save gives an empty queue.
- `Tiers`: report the cells whose draw step (a quantised depth, 8 steps) changed, not only tier changes.
- Stains: a small per-cell byte array (stain fluid index and age), saved, outside the dL ledger.

`Source/Sheet/RM_MapComponent_Sheet.cs`
- `SyncParams`: pass `SpreadPermille`, `SettlePermille` and the per-fluid pour rate.
- `SpillHomeless`, `SpillRelease`, and the dev pour `RM_GodLiquid.PourOverflow` (`Source/Debug/RM_GodLiquid.cs`):
  enqueue the pour instead of one `Offer`. `PumpSpillOutlet` is already metered; it stays.
- `EnginePulse`: mark the mesh dirty on a draw-step change. Keep the previous dL of each touched cell.
- New `MapComponentUpdate()`: per frame, draw the touched cells only, fading from the previous to the current
  dL over the pulse. Only cells on screen. Capped at a fixed cell count per frame; beyond the cap the
  cells draw at their current depth (no fade).
- `ExposeData`: save the pour queue and stains.
- `PathCostAt`: unchanged for Film/Sheet/Pool. Damp costs 0.

`Source/Sheet/RM_SheetSettings.cs`
- Add `pourCmPerPulse` (pour rate) and `sheetMotionFade` (on/off for the per-frame fade).

## 6. Proposed 0.2.0 bars (experience sentences) and their cheapest test

| # | Bar | Cheapest test |
|---|---|---|
| B1 | Tar on the ground reads as tar: black, glossy and thick, never grey. | Offline: `MatFor` colour for every fluid equals its `LookOfFluid` tint; a planted brim colour goes red. One live picture for his look. |
| B2 | Each liquid can be told apart from the others by its look alone. | Offline: pairwise colour distance of every look row at film and pool depth over a soil and a sand ground; worst pair printed. His look on a lineup picture. |
| B3 | A pour grows over time: it bulges at the pour point and its front moves out. It never arrives all at once. | Offline kernel: a 2000 dL pour; wet cell count rises over several pulses; depth at origin is the maximum while pouring. |
| B4 | Thick liquids creep and thin ones run. | Offline kernel: front radius after N pulses, water > oil > tar > slime. |
| B5 | A sheet's edge is a smooth, irregular line, not squares. | Offline render of the mesh to PNG (PY_FW_OFFLINE_ART pattern); count of axis-aligned edge runs longer than one square. His look. |
| B6 | Depth reads by look: a thin film shows the ground, a deep pool hides it. | Offline: `SheetAlpha` rises with dL for each look; film alpha below pool alpha. |
| B7 | Liquid beside an open hole with room runs into it. | Existing kernel Receiver tests (T_SHEET_KERNEL_OFFLINE) stay green. |
| B8 | Wet ground is darkened soil or sand that dries. It is never standing water. Tile and cement stay as they are. | Offline: damp cells have path cost 0, no SoakingWet, no draw on floors. Live picture of a canal edge. |
| B9 | One surface shows on each square. Liquid layers never stack. | Offline: no square has both a sheet quad and a pit surface; planted double draw goes red. |
| B10 | A dried oil, tar, blood or slime spill leaves a stain that fades away. | Offline kernel: stain present after last dL, gone after its age. |
| B11 | A map with a large moving spill plays as smoothly as one without. | Existing `RM_SheetProofs.ProofSheetPerf`, run with a pour in progress and the fade on. |
| B12 | A save made during a pour loads and the pour continues the same way. | Offline: kernel Save/Load mid-pour gives identical states after K pulses. Live: SAVE_LOAD_CONTINUES_IDENTICAL. |

## 7. Offline simulation: yes or no, and why

Yes, for most of the work. The kernel (`RM_SheetMath`) is Verse-free, integer and deterministic, and it is
already compiled into SelfTest. These can be proved offline: the pour over time, the mound, the levelling
pace, the front speed per liquid, the ledger closure with `Pouring`, damp state, stains, save/load mid-pour,
the colour identity of `MatFor` against `LookOfFluid`, the alpha curve, and the edge mesh (render it to PNG
offline, as PY_FW_OFFLINE_ART does).

No, for the final look. The sheen comes from the game's shaders (vanilla water, Odyssey
`Map/TerrainLavaShallow`) over real terrain at real zoom. Only the game shows that. He judges it from one live
lineup scene: each liquid poured on soil and on sand, far and close zoom, plus one pour filmed as frames.

## 8. Risks

- Save/load continuity: the saved pour queue and stains bump `KernelVersion`. SAVE_LOAD_CONTINUES_IDENTICAL
  is already open (FLOWWORKS_SHEETS_DIAGNOSE_LOAD_DIVERGES). Build after that item closes, or the two will mix.
- Bars that read levelling: paced levelling must not change any 0.1.0 check. The defaults (1000 permille)
  keep the 0.1.0 behaviour; checks to run after each change: T_SHEET, T_SHEET_KERNEL_OFFLINE,
  T_REVIEW1022_SHEET_OFFLINE, LOOK_STAGE8, PY_FLOWWORKS_SHEET_DROWN_MESSAGE, PY_LIQUID_LOOKS, PY_FW_OFFLINE_ART.
- Per-frame cost: the fade redraws touched cells each frame. The on-screen limit and the cell cap bound it.
  B11 measures it.
- MaxWetCells (4000): canal wetting and damp cells use slots. A long canal can fill them. Damp may need a
  separate, cheaper store if the count is near the cap; measure on a long canal first.
- The Flow shader needs Odyssey. Every DLC is assumed; the existing WarningOnce fallback stays.
- A pit rim: the sheet and the pit surface meet. B9 guards the double draw.
- Drowning and path cost read tiers. A slower Level changes where Sheet and Pool are while a pour runs.
  That is the intended truth (Principle 4), but PY_FLOWWORKS_SHEET_DROWN_MESSAGE must stay green.
- Out of scope, other items: tar fire speed (`RM_SheetFire`, already creeps), tar smoke
  (RIMMANDRAKE_DESIGN_TAR_SMOKE_AND_GAS_ON_THE_WIND), the wider all-game wet state
  (RIMMANDRAKE_DESIGN_SPILLED_WATER_WET_GROUND_ONE_STATE), and the helper that scoops spills into pits (row 10).
- Load (Principle 5): per map, one extra int per touched cell (previous dL), a small pour queue, one stain
  byte pair per stained cell, and a capped per-frame draw. No new tick work outside the pulse.

## 9. Open questions for him

Q1. D8 says sheets lie level (card 2026-10-22). May a sheet that is still being fed hold a mound and come
level at its own pace (fast for water, slow for tar)? At rest it is still exactly level.
Recommendation: yes. Without it there is no bulge to watch.

Q2. Rain wetness: one map-wide dampness value on open soil and sand, or wetness per square?
Recommendation: map-wide. Per square costs a wet-cell slot on every open square of the map.

Q3. A dried oil, tar, blood or slime spill: a stain that fades by itself, or vanilla filth that a colonist
must clean?
Recommendation: a stain that fades. It adds no chore, and the look still tells the story.

Q4. A pour rate: should a big dev pour or a burst tank take seconds or minutes of game time to finish?
Recommendation: a burst tank empties within about one in-game hour, so the front is easy to watch at speed 1.
