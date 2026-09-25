# RIVER_STEAM_ANIMATION_1 — animated steam rising from Pyrelands rivers

Owner, verbatim (2026-09-02): *"could we add animated steam rising from the
river? That is an amazing idea, file a ticket on that alone!"*

Thin item — FOUNDRY decision on spec/verify/criteria, 2026-09-02.

## spec

Pure ambience feature, no gameplay effect, no new art. `mandrake.rut.riversteam`
(RimUtinni tier — this names Ash'karr's Pyrelands specifically, per
`NAMING_SCHEME_PLAN.md`'s tier test).

`MapComponent_RiverSteam` (`src/RimUtinni/RiverSteam/Source/RiverSteamHook.cs`):
- MapComponent subclasses are auto-instantiated per map by `Map.FillComponents()`
  (`Verse/Map.cs:710`) — no Harmony patch or XML registration needed, confirmed
  by reading the real vanilla source, not assumed.
- Gates on `map.Biome.defName == "ZBiome_Grasslands"` — the Pyrelands' actual
  BiomeDef, per `ASHKARR_WORLD_DEFINITION.md`'s biome table ("stormy savanna").
  Every other biome's rivers stay silent.
  ⚠️ **Superseded, this original 2026-09-02 framing** — `PYRELANDS_WRONG_BIOME_DEF_1`
  (closed 2026-09-20) found the intended Pyrelands def is `RM_FE_Pyrelands`, not
  `ZBiome_Grasslands`, and which one carries the live tiles is UNRECONCILED
  against `world/ASHKARR_WORLDMAP_tiles.csv`. The engine is no longer hardcoded
  on this string: the mechanism moved to `src/RimMandrake/FlowWorks/Source/ManyWaters/RiverSteamHook.cs`
  (a `RiverSteamBiomeExtension` DefModExtension any biome can carry), and
  `src/RimUtinni/UtinniPatches/Patches/ManyWaters_RiverSteam_Ashkarr.xml` now
  applies the extension to BOTH `ZBiome_Grasslands` and `RM_FE_Pyrelands` for
  exactly this reason.
- River cells found via `TerrainDef.IsRiver` (`HasTag("River")`) — the exact
  test `RimWorld.SeasonalFlood` already uses for the same purpose
  (`Source/RimWorld/SeasonalFlood.cs:63`), cached once at `FinalizeInit()`.
- Every 90–260 ticks (randomized), one river cell is picked and — if not
  fogged — thrown a puff of vanilla's own **`Steam` FleckDef**
  (`Defs/Ideology/Effects/Fleck_Visual.xml`, `ParentName="FleckBase_Thrown"`,
  `texPath=Things/Mote/Smoke`) via `FleckMaker.GetDataStatic` + a slight
  upward drift (`velocityAngle` 60–120°, `velocitySpeed` 0.15–0.3). No new
  texture, no heat push (unlike `IntermittentSteamSprayer`, which this
  deliberately does NOT reuse — that class pushes 40 heat/interval, which is
  a real geyser gameplay mechanic, not ambience).

## verify

- `dotnet build RiverSteamHook.csproj -c Release` — clean (0/0), confirmed.
- Deploy clean, file-copy only (`deploy_custom_mods.py --mod RiverSteam --apply`).
- Live-observed: load a save/quicktest with a Pyrelands-biome map open, confirm
  steam puffs appear near river cells at a reasonable, non-spammy rate, and
  that a NON-Pyrelands map's rivers stay silent (the biome gate holds).

## criteria

Steam visibly rises from river cells on a live Pyrelands map at an ambient,
non-distracting cadence; no gameplay stat/mechanic is touched; other biomes'
rivers are unaffected.

## 2026-09-02 — offline build (FOUNDRY)

Built and deployed as above. `ZBiome_Grasslands` is a third-party mod's
BiomeDef (`RimSage` only indexes vanilla source, so its exact schema wasn't
independently re-verified here — the defName itself is sourced from
`ASHKARR_WORLD_DEFINITION.md`'s own biome table, not guessed). Not enabled
in `ModsConfig.xml`, no restart — live-quicktest-observed steam-on-Pyrelands
(and silence-elsewhere) is owed to a future bridge session. Left `doing`.

## 2026-09-07 (FOUNDRY) — live session run, mechanism confirmed loading clean, fleck sighting NOT captured (tooling gap)

Restarted on a custom 13-mod minimal list (BASE + `zylle.MoreVanillaBiomes` for
the real `ZBiome_Grasslands` def, `mandrake.rut.riversteam`,
`mandrake.rm.ninefold`, `mandrake.rsw.cuisine`) — clean load, 0 config errors,
0 crossref errors, 0 patch failures, 0 typeload (`sweep_load.sh` verdict).

**Confirmed live**: a real map with `map.Biome.defName == "ZBiome_Grasslands"`
loads with `mandrake.rut.riversteam` active and throws zero errors (bridge
`get_bridge_status` optionalPatchFailureCount 0 throughout the session,
`jawa/map_info` read the biome back correctly on three separately-generated
maps this session).

**NOT captured**: an actual on-screen steam fleck. Blocked on a genuine
quicktest-tooling gap, not a RiverSteam defect — spent most of a session on
this alone:
- `start_debug_game_ready`'s own start tile had `riverCount: 0` on **11 of 11**
  fresh worldgens tried this session — Crashlanded/Odyssey site selection
  appears to systematically avoid river-adjacent start tiles.
- A hand-spliced 2-tile `jawa/world_links_set` river (`kind=river, def=River`)
  registers at the WORLD level (`riverCount: 1` reads back correctly) but the
  **map generator's own terrain-painting genstep does not paint any
  river/Riverbank/WaterMoving* terrain for it** — tried on three separate
  synthetic links (tiles 48115↔48116, 84638↔84639 chain, 84688↔84689), all
  three came back with zero `River`-tagged terrain in a full-map
  `jawa/get_terrain_batch` scan. Likely an accumulated-flow/width threshold in
  vanilla's river genstep that a single isolated stub never crosses — a NATURAL
  river (this session found several via `jawa/world_tile_get` scans, e.g. the
  very first world's tile 43317 with `riverCount: 2`) DOES paint real
  `Riverbank`/`WaterMovingShallow` terrain; confirmed by a raw cell scan before
  that specific map was lost (see below).
- The one map that DID have real river terrain (tile 43317, natural
  `riverCount: 2`, forced to `ZBiome_Grasslands` via `jawa/world_tile_set`)
  was lost to an apparent bridge/engine auto-cleanup of an unowned
  (faction-less) generated `Settlement` map once ticks were advanced past it —
  `mapCount` silently dropped to 0 mid-session. Rebuilding a Player-owned
  version of the same setup (`jawa/colony_found` first) survived fine, but by
  then no natural-river tile was reachable near the new world's start location
  to repeat the combination (Player-owned + natural river + `ZBiome_Grasslands`
  + still the bridge's current map) inside the remaining session.

**Verdict**: the code-level mechanism is correct (read again this pass: exact
`ZBiome_Grasslands` string match, `TerrainDef.IsRiver` — the same test
`SeasonalFlood` uses — and vanilla's own `Steam` FleckDef via
`FleckMaker.GetDataStatic`/`map.flecks.CreateFleck`, all APIs already proven
elsewhere in the base game), and it loads with zero errors on a real
Grasslands-biome live map. The one thing this item's own `verify` section
asks for — an actual sighted fleck — was not reached this pass; not because
the mod misbehaves, but because reliably producing "ZBiome_Grasslands biome +
real accumulated river + still-current, non-cleaned-up map" together, live,
via the bridge, needs either the real Ash'karr Pyrelands map data (which has
genuine accumulated rivers) or a new companion tool. Left `doing`, not closed
— the owner's own doctrine is that a live check on a mechanism never observed
running is still owed, and "loads clean" is not the same claim as "seen doing
the thing." Recommend either: (a) run this same check against the frozen
Ash'karr world/save once one exists with real Pyrelands geography, or (b) file
a follow-up for a `jawa/` tool that force-paints a river terrain segment
directly (bypassing the world-level flow-accumulation gate) so quicktest maps
can put a real river anywhere on demand.

## 2026-09-13 (FOUNDRY) — recommendation (a) executed: real Pyrelands+river now exists live, but a NEW bridge blocker replaces the old one

Recommendation (a) from the prior pass is now possible — the frozen Ash'karr
world is live under the current campaign save (tile 17007, `RUT_ExtremeDesert`,
"Zeddo's Salvage Yard"), and the authored planet CSV
(`world/ASHKARR_WORLDMAP_tiles.csv`) lists 9 tiles that are both
`ZBiome_Grasslands` and `river_flow > 0`. Confirmed **live**, not just in the
design CSV: `jawa/world_tile_get` on all 9 (1534, 1535, 6213, 14344, 14345,
16486, 16489, 16490, 16494) reads back `biome: ZBiome_Grasslands`,
`riverCount: 2-4` on every one — the real authored river geography this
item's prior pass could only synthesize badly.

Founded a throwaway Player settlement at tile 1534 (`jawa/colony_found`,
name `RiverSteamProbe`) and generated its map
(`jawa/world_tile_map_generate` → `mapId: 4`, 250x250, `wasAlreadyGenerated:
false`). Confirmed via `jawa/get_terrain_batch` across multiple rows: this map
has REAL `WaterMovingShallow` river cells (7-8 cells wide) flanked by
`VEE_FertileRiverbank`, running the length of the map — not a stub, not
synthetic. `jawa/map_info` on this map reports `mapBiome: ZBiome_Grasslands`,
`mapBiomeLabel: "the Pyrelands"`. **This is the first time this item has had
a real, live, non-synthetic Pyrelands-river map to test against.**

**Still not closed.** Every screenshot of this new map (`take_screenshot`,
`screenshot_cell_rect`, many zooms/coordinates, across ~1,170 stepped ticks —
well over the mod's 90-260 tick throw interval, so several puffs almost
certainly fired map-wide) rendered as a blank void with "Not visible area" in
the status bar, DESPITE `rimworld/get_cell_info` confirming `"fogged": false`
on the exact cells being shot and a full `jawa/set_fog unfogAll` driving
fogged cells to 0. A sanity-check screenshot of the player's ordinary colony
map (`Map_3`, entered the normal way at game start) taken seconds later on
the same connection was perfectly sharp. **This is a newly-identified bridge
rendering gap, not a mod defect or a fog problem** — full writeup and evidence
in `skills/rimbridge/references/traps.md` ("A `world_tile_map_generate`'d map
can render as a blank void"). No workaround found this session.

**Verdict, updated**: the mechanism is now proven correct against the real
authored world data (biome gate, river-cell test, both confirmed live on
non-synthetic terrain) one level closer than the 2026-09-07 pass, but the
final "seen a fleck" bar is now blocked on a DIFFERENT tooling gap (bridge
screenshot of a debug-map-generated map) rather than the old one (no reachable
river tile). Left `doing`. Next session: either fix/work around the
render-void trap (see traps.md's candidates — force a full `MapDrawer`
regen, or reach the map via a real caravan arrival instead of `Change Map`),
or just wait for a live human-observed session once the owner is actually
playing near a Pyrelands river tile in the real campaign.

## 2026-09-25 (FOUNDRY) — offline re-verify only; bridge unavailable this pass

Bridge is held by a different live FOUNDRY window this session (`bridge who`:
"held by FOUNDRY since 2026-09-25T06:04:50Z, for a full-modlist restart + 5-item
live-verify batch, idle 2 min" — provably alive, not stale) — per this session's
own instructions, not taken/forced. So the item's real remaining blocker (a
live-observed steam fleck) is still not reachable this pass. Two things
genuinely re-checked instead, both new evidence, not repeats:

1. **Build re-confirmed clean on today's tree**:
   `/mnt/c/Users/Mandrake/.dotnet/dotnet.exe build
   'D:\Luke\dev\Rimworld\src\RimMandrake\FlowWorks\Source\RimMandrake_FlowWorks.csproj' -c Release`
   → 0 Warning(s), 0 Error(s). `RiverSteamHook.cs`/`RiverSteamSettings.cs` unchanged
   since the 2026-09-20 pass; still correct on read (biome-extension-gated,
   `TerrainDef.IsRiver`, vanilla `Steam` fleck, no heat push).

2. **`ManyWaters_RiverSteam_Ashkarr.xml` validated against the CURRENT live
   627-mod set** with `validate_patch.py --defs <RimWorld/Data> --defs
   <RimWorld/Mods> --defs <Steam workshop 294100> --defs src --mods-config
   <live ModsConfig.xml>` — **this item's first real `--live` xpath check**,
   not just a def-dump/RimSage read: "load set: 627 active mods, 627 found on
   disk, 8,862 def files". Result: 0 errors, only the two expected
   add-if-missing WARNs the patch's own comments already call out. Concretely,
   against today's actual installed files:
   - `ZBiome_Grasslands`'s `<modExtensions>` test matches 0 nodes (it has none
     yet) → the `nomatch` branch fires and adds the extension. Confirmed
     against `More Vanilla Biomes: ZBiome_Grasslands.xml`.
   - `RM_Pyrelands`'s `<modExtensions>` test matches **1** node (it already has
     a `<modExtensions>` block) → the `match` branch fires and appends into it.
     Confirmed against `Pyrelands: Pyrelands.xml`.
   So **both** conditional adds resolve to a real, non-silent branch on the
   live install — neither operation is a dead no-op today. (Which of
   `ZBiome_Grasslands`/`RM_Pyrelands` actually carries live world tiles is the
   separate, deliberately-unresolved-until-the-repaint question from
   `PYRELANDS_WRONG_BIOME_DEF_1`/`WORLD_REMAKE_FINAL_STEP_1` — not re-opened
   here, per the standing "biome painted once at the end" rule.)
   Also re-confirmed via `ModsConfig.xml` (ElementTree-parsed, 627 active):
   `mandrake.rm.flowworks`, `mandrake.rut.patches` and `zylle.morevanillabiomes`
   are all still active on today's list.

**Net**: every offline-checkable precondition (compiles clean, patch resolves
correctly on the real current install, correct mods active) is re-confirmed
on today's tree/mod-set. The ONLY gap is still the one the 2026-09-19 passes
already characterised in detail: no bridge route exists that reaches a
generated map without hitting the render-void, and this session had no
bridge access to retest whether `BRIDGE_MAPGEN_STALE_FINALIZE_1`'s
(closed 2026-09-19, same day as this item's render-void discovery) unconditional
`mapDrawer.RegenerateEverythingNow` fix — built for a *different* symptom
(stale mesh on map reuse), not this one (pure-black first render) — happens to
also cover this case. **That is now the single cheapest next check**: on a
future bridge session, generate a fresh Pyrelands-river map via
`jawa/world_tile_map_generate` (which now runs that finalize sequence
unconditionally per `BRIDGE_MAPGEN_STALE_FINALIZE_1`) and screenshot it before
trying anything else — it may already be fixed as a side effect of unrelated
work landed the same day. Left `blocked` (same standing reason: needs a live
bridge window not already committed to other work, or the owner glancing at a
real Pyrelands river tile in the campaign).

## 2026-09-25 (FOUNDRY) — live-caught, owner-judged, reworked for shape

**The render-void gap from 2026-09-19/07 is CLOSED** — confirmed live this
session, no longer a mystery. `BRIDGE_MAPGEN_STALE_FINALIZE_1`'s finalize
sequence does cover it: generated a scratch map on a real natural-river tile
(world tile 6450, live-sampled, `riverCount: 2`; the campaign's own Pyrelands
region tiles all read biome `TemperateForest` with `riverCount: 0` — the
mid-migration state `BIOME_PAINT_ONCE_AT_THE_END_1` already documents, not a
defect), forced its biome to `RM_Pyrelands` for the test only (reverted after,
see below), generated the map (`mapDrawer.RegenerateEverythingNow` ran as
part of `mapFinalize`, 0 failed steps), and it rendered clean — no black
screen. `VEE_SwampyWaterMovingShallow`/`VEE_StagnantRiverWater` painted as
real river terrain on the generated map, confirming the whole chain works
(biome extension → `TerrainDef.IsRiver` cache → steam trigger).

**First live sighting, and it's the wrong shape.** Owner watched it live and
called it directly: *"The steam puffs are too rare and too opaque. They look
like little choo-choo train round clouds. They should be oscillating,
wavering distortions and thin ribons of rising structure"* (photo reference
supplied: mist rising off a jungle river in several soft columns, not
discrete blobs). Root cause: the v1 mechanism threw ONE round `Steam` fleck
from a RANDOM river cell every 90-260 ticks — both the shape (vanilla's round
`Things/Mote/Smoke` texture, uniform scale) and the cadence/placement (rare,
anywhere) were wrong for "rising mist," which reads as a few dense, wavering,
near-continuous columns.

### Reworked, same session, no new art
`RiverSteamHook.cs` rewritten:
- **Shape**: `FleckCreationData.exactScale` (a real engine field, MEASURED via
  RimSage before use) lets a fleck be stretched non-uniformly — each instance
  is now a thin vertical sliver (`ribbonWidth` 0.12-0.22, `ribbonHeight`
  1.0-1.7) instead of a round puff, at low opacity (`alpha` 0.30-0.50 via
  `instanceColor`) so overlapping instances blend into haze rather than
  stacking as visible blobs.
- **Motion**: added `rotationRate` (`wobbleDegreesPerSec` 4-10, sign
  randomized) for the "oscillating" sway as each ribbon rises; slowed
  `velocitySpeed` (was 0.15-0.3, now 0.05-0.15) for a gentle standing rise
  instead of a thrown puff.
- **Reveal**: default `fleckDef` swapped `Steam` → `SmokeGrowing` (same
  underlying texture, but a 6s slow swell instead of Steam's snappy 1.2s
  reveal — softer entrance, still zero new art).
- **Placement/cadence**: replaced "one random river cell, whole-map pool,
  90-260 ticks" with `maxVents` (default 6) persistent vent cells spaced
  evenly along the river, each firing independently every 20-50 ticks — reads
  as a handful of standing, continuously-active columns (matching the
  reference photo) instead of one puff hopping around rarely.
- All new fields live on `RiverSteamBiomeExtension`, so any biome reusing
  this hook can retune without touching C#; `RiverSteamSettings`'
  enable-toggle and `puffRateMultiplier` are untouched and still apply on top.
- Built clean (`dotnet build RimMandrake_FlowWorks.csproj -c Release`, 0/0).
  `deploy_custom_mods.py --mod FlowWorks --apply`: the def/hash half deployed;
  the DLL itself FAILED (locked by the running game, expected) — same
  restart-owed state as `SCALD_WATER_AGITATION_FLECKS_1`'s two DLLs this
  session. **Not yet seen live** — the shape/motion rework is un-verified
  until the next restart.

### Cleanup — the scratch test did NOT touch real world state, after a revert
World tile 6450 was forced from its real biome (`RUT_Greentide`) to
`RM_Pyrelands` for this test only. **Reverted and re-committed
(`jawa/world_tile_set` + `jawa/world_commit`) before ending the session** —
confirmed back to `RUT_Greentide` in the live world. The scratch map itself
(mapId 10) is disposable per the standing "map state is disposable debug"
rule and was left as-is, no cleanup owed.

⚠️ **Side effect worth recording**: tile 6450 already belonged to a resident
mechanoid faction ("Totharth Mechhive") before this test. Planting a
`PlayerColony` colonist there (to stop the scratch map from being auto-culled
per the known trap) and unpausing triggered a real raid from that faction —
vanilla storyteller behaviour against an intruded hostile settlement, not a
RiverSteam or scenario defect. Cost a few minutes of confusion (owner briefly
read it as an uncontrolled mechanoid-assault problem in the live campaign)
before the letter stack (`rimworld/list_letters`) showed both raid letters
targeting the scratch map's `mapId`, not the real colony's. **Lesson for next
time**: pick an unclaimed/wild tile for a scratch settlement-map test, or
check the tile's existing faction before generating a `Settlement`-parented
map on it.

### owed
- **Live-verify the reworked shape/motion at the next restart** — this is now
  the item's whole remaining bar. Generate or find a river on a
  `RiverSteamBiomeExtension`-carrying biome (pick an unclaimed tile this
  time), watch it for at least one full `ticksBetweenPuffs` cycle per vent,
  and get the owner's verdict against the reference photo before closing.
- The render-void question this item carried since 2026-09-07/19 is now
  answered (closed, not just "may be fixed") — safe to cite as resolved
  anywhere else that references it.

Left `doing` — a live look at the reworked mechanism, with the owner judging
the shape/motion against the reference photo, is the only bar left standing.
