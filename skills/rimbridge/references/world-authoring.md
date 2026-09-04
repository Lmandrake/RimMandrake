# World authoring — the 25 planet tools

The planet, at the world screen or from a running colony. Element census and every API
signature: `design/Jawa/worldbuilding/WORLDMAP_BRIDGE_SURFACE.md`. Screen-specific
behaviour: the `rimworld-world-editing` skill.

⚡ **Writing all 21,872 tiles takes 0.1 seconds.** Bulk world editing is not expensive.

```
READ      world_layers · world_neighbors · world_tile_get · world_links_get · world_mutators_get
          world_landmarks_get · world_objects_get · world_features_get · world_info_get
WRITE     world_tile_set · world_tile_import · world_links_set · world_links_clear
          world_links_import · world_mutators_set · world_landmarks_set
          world_objects_set · world_objects_add · world_objects_remove
          world_features_set · world_info_set
VALIDATE  world_tile_validate · world_links_validate · world_objects_validate
          world_mutators_audit · world_lint
COMMIT    world_commit          ⬅ nothing you write is visible without it
CAMERA    world_view            ⬅ the only bridge route to the planet at all
```

## The order the engine forces

1. **biome before links** — `Roads`/`Rivers` are filtered by `PrimaryBiome.allowRoads` /
   `allowRivers`, so painting water over a river hides it
2. **rivers mouth-first** — `OverlayRiver` maintains `riverDist = max(d, other.d + 1)`
3. **landmarks before settlements** — `IsValidTile` rejects a settlement tile
   ⚠️ though nothing enforces it; see `silent-failures.md` §5
4. **roads last** — shortest paths over the graph between real settlements
5. **`world_commit` once at the end**, never per write

## Import and validation

`world_tile_import` and `world_links_import` take a **file path**, not an ops string. The
companion's batch convention caps at `MaxOps = 4096`; 21,872 tiles would be six calls and a
multi-megabyte socket payload. Reading the CSV in-process is symmetric with
`world_tile_export`.

**Always pass `expectTiles`.** A different My Little Planet subcount shifts **every** tile id
and silently paints the wrong planet. The guard is measured working: `expectTiles=21872`
against a 119,904-tile grid returns `success:false` and says why.

`world_tile_validate` compares live against a CSV **on raw fields** and reports `byField`,
so a mismatch names the field rather than a count.

## `world_lint` — judge against vanilla, not against zero

The owner's sanity pass, run in-engine. **Calibrate before trusting a clean sheet.** Vanilla
baseline on an untouched world:

| check | vanilla |
|---|---|
| total findings | **52** |
| single-tile islands | 8 |
| settlements on water / impassable | 2 / 2 |
| **settlements with NO ROAD** | **40 of ~100** — so "unreachable by road" is *not* by itself a defect |
| river systems | 38, **0 reaching no sea** |

🔑 That last row is the useful one: **vanilla rivers all reach the sea**, so an orphaned
trunk on a hand-made planet is anomalous against the engine's own generator.

🔑 The river rule is **conditional** by the owner's ruling — only HIGH-accumulation trunks
must reach a sea; low-accumulation rivers may die in playas and salt pans. `world_lint`
floods river components and judges each by its largest def.

## `jawa/world_map_mode` — a screenshot taken on the call's return photographs the OLD mode

A `MapModeFramework` planet view mode is switched by
`MapModeComponent.Instance.RequestMapModeSwitch(mapMode)`, and `jawa/world_map_mode` now
drives it. The switch only sets `regenerateNow` — the border mesh rebuilds later in the
render loop, so a `take_screenshot` fired right on the call's return still shows the
previous mode. Give the render loop a beat (or step a frame/tick) before capturing.

## Things worth knowing

* **Layers come from the SCENARIO** (`ScenPart_PlanetLayer`), not worldgen params. A
  quicktest gets Surface + Orbit only — 2 layers, not 3.
* **`WorldFeature.Tiles` is a full-grid scan.** Never call it in a loop over 24 regions;
  `world_features_get` builds one map in a single pass.
* ⭐ **`drawAngle` is never set by vanilla** — all 68 generated features read 0.0, so every
  rotated label on the planet is yours.
* **`world_view altitude`**: 125 min · 550 entry default · **1100 = whole globe**. The
  public `altitude` field alone snaps back because `Update` lerps toward the private
  `desiredAltitude` — the tool sets both.
* ⚠️ **`CameraJumper.TryShowWorld()` returns false unless `ProgramState == Playing`**, which
  `readiness=mapData` does not guarantee.
