## Spec row (verbatim, deepfire_luminous_pigment_spec.md §10 step 6)

| # | build | proof |
|---|---|---|
| 6 | Floors: floor grid, `SetTerrainColor` / `DoTerrainChangedEffects` postfixes, clustering, the `CellBeauty` and `RoomStatWorker_Beauty` hooks (§3.5) | quicktest: paint a 6×6 floor, Deepfire it → glow, one proxy per 3×3 block (dev overlay lists 4 proxies); vanilla-paint the floor red → red glow; remove the floor → grid zero, no light; a room's Beauty readout rises by 36 × 0.5 per-cell plus the +6 room line (3 × 10 coated cells) and drops back on removal |

## What already exists to build on

- `CompDeepfire`, `MapComponent_DeepfireLights` (the spawned-invisible-proxy
  light system, category/altitudeLayer `Item` — NOT `Building`, see the
  MEASURED note in `RM_DeepfireLightProxy.xml`'s own header, a
  Building-layer proxy gets WIPED along with whatever it was spawned on by
  `GenSpawn.Spawn`'s default `WipeMode.Vanish`), `RM_Designator_Deepfire`/
  `RemoveDeepfire`, the WorkGiver/JobDriver pair, all ship
  (`DEEPFIRE_PAINT_LIVE_VERIFY_1`, step 5, closed prose in `items/closed/`).
- The proxy registry (`MapComponent_DeepfireLights.RegisterThingLight`/
  `DeregisterThingLight`) is keyed by an arbitrary `object` — a floor CELL
  key (e.g. boxed `IntVec3`, or a small struct) plumbs into the exact same
  machinery with no new light-spawning code owed.
- Spec §3.6's clustering ("contiguous same-colour same-coat building cells
  into one proxy per 3×3 block") is NOT yet built anywhere — step 5 registers
  one proxy per Thing, never per cluster. This item owns clustering for BOTH
  the floor grid AND (if not already sufficient) the wall/furniture case.

## Build

Spec §3.6: a per-cell byte grid `floorCoats[]` on `MapComponent_DeepfireLights`
(or a sibling MapComponent), Scribed; postfix `TerrainGrid.SetTerrainColor`
(recolour → relight; null → keep coats, colour falls back to the floor def's
colour) and `TerrainGrid.DoTerrainChangedEffects` (floor removed/replaced →
coats zeroed, no refund); the `RM_StatPart_Deepfire`-sibling beauty hooks from
spec §3.5's floor bullets: `BeautyUtility.CellBeauty` postfix (`UNMEASURED
signature` per spec — check via RimSage first; if inlined/unpatchable, postfix
`BeautyUtility.AverageBeautyPerceptible` instead, spec's own documented
fallback) and `RM_RoomStatPart_DeepfireFloor` on `RoomStatWorker_Beauty.GetScore`.

## Needs

`bridge` — the quicktest proof above.
