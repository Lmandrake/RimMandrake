# LIVE.md — facts you would otherwise need a running game to learn

Published by CHECK. One line per fact. Superseded lines are replaced, not appended to.
Everything here was read out of a running game or off an artifact a running game wrote.

## The def dump

- **Current dump: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump`,
  captured `2026-08-15T15:10:11Z` (08:10 local), `mode: all`, game `1.6.4871 rev591`.**
  576 mods, 529 files under `defs/`, `animals.json` alongside. Taken during the C37
  load, so it carries `mandrake.starwarsraces` and does NOT carry the three donors
  (`btd.xenotyperemix.starwars`, `guy762.starwarsxenotypes`,
  `neronix17.outerrim.galacticdiversity`).
- 🔴 **FRESHNESS HAS TWO AXES AND THEY DISAGREE RIGHT NOW: fresh in TIME, stale in SET.**
  The dump holds **576** mods; `ModsConfig.xml` `activeMods` holds **575**. The single
  difference is `regrowth.botr.boilingforest`, deprecated at 11:58 — *after* the 08:10
  dump. Direction matters: the dump is a **superset**. Nothing that loads is missing from
  it, so a patch onto a live def is checked correctly; but the dump still describes defs
  from a mod that **no longer loads**, so an xpath onto one of those **validates clean and
  silently no-ops in game**. `refresh.py`'s STALE verdict is right and should be believed.
  Live instance: `D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Patches\JawaWorld_BiomeMix.xml:140`
  carries `<RG_BoilingForest>` — the only BOTR reference left in `Jawa_Patches`.
  ⇒ **"The dump is from today" is not the same claim as "the dump matches what loads."**
  I asserted the second from the first on 2026-08-15 and it was wrong; REP caught it.
- 🔴 **Read freshness from `manifest.json` → `capturedUtc`, NEVER from a folder mtime.**
  The `defs/` folder still reads 2026-08-14 01:20 because the dump overwrites files in
  place and never adds or removes one, so the directory mtime has not moved in a day.
  A stale-looking folder date sent NEXT_RELOAD §1.0 step 0 to the wrong conclusion on
  2026-08-15; the dump was fresh the whole time.
- The dump is armed by `echo all > .../DefDump/dump_request.txt` and the request is read
  **at startup only** — arming it while the game runs does nothing until the next launch.
  It costs 18.7 s of load time (`timingsMs.allDefs` 18579).

## Facial Animation

- **FA's per-xenotype opt-out is keyed by defName**, in
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_1635901197_FacialAnimationMod.xml`,
  and **FA reads it at startup only**. Currently 156 entries, 69 of them
  `Human-RimMandrake*` — verified 2026-08-15 against the 69 XenotypeDefs the races mod
  ships; the two lists match exactly, in both directions. Nothing is unprotected.
- ⚠️ **The races mod ships 69 xenotypes, not 70.** The 70 written through C37 and its
  result block is off by one. 69 is the measured count, from the deployed defs.

## The def dump's blind spots

- 🔴 **79 of the 529 def-type files in the dump are EMPTY** (`"count":0`), so for those
  types **"absent from the dump" says nothing about the game.** `AbilityDef` is one of
  them — zero rows — which is why all 16 ideo-role ability references in
  `The Salvation.rid` come back UNMEASURABLE rather than missing. Others in the list:
  `AbilityAIDef`, `CharacterDef`, `FactionEnlistOptionsDef`, `FaceTypeDef`, `PatchDef`,
  `PawnBioDef`, and 72 more. Full list: rerun the counter in
  `src/RimMandrake/Utils/validate_save_artifact.py --rebuild-index`.
- ⇒ **A `--defs` check against an empty def type is UNMEASURED, not passed.** Give it
  its own word and its own exit code, or it silently reads as a green tick.
- 450 non-empty types, **79,575 defs**, 62,555 distinct defNames indexed.
- 🔴 **A NON-EMPTY type can still be missing a FIELD.** `PawnKindDef.json` holds all
  1706 kinds, but `weaponTags` is populated on **ZERO** of them — the field is simply
  not exported. So "which pawnkind spawns carrying weapon X" is **not answerable from
  the dump** and must be probed live (spawn the kind, read its equipment back with
  `jawa/list_pawns` / `jawa/inspect_string`). Counting rows in a def type does NOT tell
  you the fields inside those rows are complete; check the field, not the type.
  Found 2026-08-15 CHECK while staging C43.
- 🔴 **`weaponTags` is invisible on BOTH channels — dump AND live bridge.** Confirmed
  2026-08-15: `jawa/get_def defType=PawnKindDef` returns no `weaponTags` key either, on
  `Jawa_Tribal_Scavenger`, `Jawa_Tribal_Slinger` or `Jawa_Colonist`. So "does this kind
  arm its pawns" is answerable **only by spawning one and reading `<equipment>` out of a
  saved `.rws`** — which is how C40(a)'s unarmed-Jawa failure was actually caught.
  ⇒ Two independent read paths hiding the same field is not evidence the field is empty.

## ModsConfig.xml

- **The active-mod count is 576** (`activeMods`), read 2026-08-15 13:43. It was 575 at
  11:58 — a seat added one during this shutdown window. ⚠️ **This number moves; read the
  file, never this line.** It is here to show the counting method, not to be quoted.
- ⚠️ **Counting `<li>` across the whole file gives 580 and is WRONG.** The file has a
  second list, `knownExpansions`, holding the 5 DLC ids, and they are duplicates of ids
  already in `activeMods`. Scope the count to inside `<activeMods>…</activeMods>`, or
  take the size of the *set*. A bare `grep -c '<li>'` overcounts by exactly the DLC count.

## Saved ideo / xenotype artifacts

- **`src/Jawa/ideoligion/The Salvation.rid` is CLEAN as of 2026-08-15**: 267 def
  references, **251 resolve, 0 dangling**, 16 UNMEASURABLE (all `AbilityDef`, the dump
  blind spot above). It carries **101 precepts** — not the 82 written in earlier notes.
- 🔴 **`MandrakeJawa.xtp` is NOT clean — the live game says so, 2026-08-15 CHECK.**
  The earlier "36/36 references resolve" was an OFFLINE verdict and it is WRONG on the
  running stack. At startup RimWorld logged **17 `Could not load reference to`** lines
  (Scribe, not the def loader — different system, and the def-loader crossref count was
  clean at baseline 25). Of them, **7 distinct GeneDefs die out of the saved xenotypes**:
  · **4 are OURS and the cause is a RENAME that the .xtp never followed** —
    `Jawa_Eyes_HugeAmber` → `RimMandrake_Jawa_Eyes_HugeAmber`,
    `Jawa_Eyes_HugeOrange` → `RimMandrake_Jawa_Eyes_HugeOrange`,
    `Jawa_Head_Plain` → `RimMandrake_Jawa_Head_Plain`, and
    `Jawa_Gene_Skittish` → **`RimMandrake_Jawa_Skittish`** (NOT a straight prefix; `Gene_`
    was dropped too). All four new names ARE present in today's 4,306-GeneDef dump, so
    nothing is missing from the game — the SAVED FILE holds pre-rename names.
  · **3 are `guy762_*`** (`_Furskin_shortfur`, `_BodySizeGene_smaller`, `_Eyes_HugeYellow`)
    and are expected: `guy762.starwarsxenotypes` is deliberately OFF for the C36 run.
  The other 5 dead refs are `RG_*` ThingDefs (Owlbeast, boilberries) inside **LWM Deep
  Storage's own settings**, benign collateral of the B-BOIL cut — not our artifact.
  ⚠️ `softshadow.xtp` and `pokean.xtp` carry some of the same dead names.
  ⇒ **An offline validator run against the def dump did NOT catch this, and cannot.**
  Scribe resolves saved names at load; a dump check answers a different question.
- ⚠️ `The Salvation.rid`'s provenance was REPOINTED at the live set in `a9b2509` — it now
  carries 576 modIds matching `activeMods` exactly, both directions, with none stale.
  Re-validated after that rewrite: references unchanged, still zero dangling.
  `MandrakeJawa.xtp` still carries the ORIGINAL 585 with 11 no longer active. That is
  **provenance, not a dependency list** — harmless, and it matters only if a reference
  also fails to resolve. Neither file has one.
- ✅ **The 19 empty `<li>` entries are NORMAL and need no live check** — retracted, I
  raised them as suspicious and they are not. Vanilla `Technocracy.rid` has the same
  shape (22 empty in `hairFrequencies`, 11 in `beardFrequencies`): Scribe writes
  `<li />` for a default-valued entry. Compared directly, game down, 2026-08-15.
  ⚠️ Also note `hairFrequencies`/`beardFrequencies` carry `<vals>` with **no `<keys>`**
  in BOTH files — that too is the normal shape, not a lost def reference.
- The tool: `python3 src/RimMandrake/Utils/validate_save_artifact.py <file>`.
  `validate_ideoligion.py` CANNOT read these — it answers `no religions found` and
  checks nothing.
- 🔴 **A clean run is necessary, not sufficient.** It proves no dangling names. It does
  NOT prove the ideo loads. Only the live dialog does that.

## Config files

- **No config file waits for anything** — not RimSort, not game close. Owner ruling
  `0460ee4`, 2026-08-15. **Assemblies are the only exception**, because the OS locks a
  loaded DLL. This retires every "check whether RimSort is open" step.

## The planet, read off the assembly — CHECK, 2026-08-19

Decompiled, not inferred, from
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`.
Nobody needs a live game to re-derive these; they need `ilspycmd`.

- **How to decompile here.** `ilspycmd` installs via `C:\Program Files\dotnet\dotnet.exe
  tool install -g ilspycmd`, but ships targeting net6 while this machine has net8 only —
  it will not launch until `rollForward: LatestMajor` is added to its
  `ilspycmd.runtimeconfig.json` under `C:\Users\Mandrake\.dotnet\tools\.store\`.
  `ilspycmd -p -o <dir> <dll>` writes the whole assembly as a C# project. There is no
  `dotnet` on the WSL PATH; use the Windows exe.
- 🔴 **Rivers and roads: use `WorldGrid.OverlayRiver(from, to, def)` /
  `OverlayRoad(...)`, never `SurfaceTile.potentialRivers` / `potentialRoads` directly.**
  Both are public and both append to **BOTH** endpoints. The save stores each undirected
  edge once (origin < target, reciprocity 0.000) — that is a serialization fact and it is
  FALSE of the live object graph.
- **There is no neighbour-slot index at runtime.** `SurfaceTile.RiverLink` is
  `{ PlanetTile neighbor; RiverDef river; }`, `RoadLink` is `{ PlanetTile neighbor;
  RoadDef road; }`. The link holds the tile. The 0.197-vs-0.161 offline reconstruction
  result is moot, not a blocker.
- **`riverDist` needs no BFS.** `OverlayRiver` ends
  `to.riverDist = max(to.riverDist, from.riverDist + 1)` and nothing else in the assembly
  writes it — so it is order-dependent: call rivers **mouth first, upstream after**.
- **Settlements:** `WorldObjectMaker.MakeWorldObject(layer.Def.SettlementWorldObjectDef)`
  → `SetFaction` → `.Tile` → `INameableWorldObject.Name` → `Find.WorldObjects.Add`.
  ⚠️ It is `layer.Def.SettlementWorldObjectDef`, **not** `WorldObjectDefOf.Settlement`.
- **Features:** `new WorldFeature(def, layer)` → `.name` → `grid[t].feature = f` per member
  tile → `drawCenter` / `maxDrawSizeInTiles` → append to `Find.WorldFeatures.features`.
  `FeatureWorker.AssignBestDrawPos` is `protected`; supply the centroid yourself.
- **`Tile.feature` is a `WorldFeature` object reference**, not a ushort (the save stores
  the **uniqueID**). **`Tile.pollution` is a `float`** — the `/65535` scale argument is a
  save-format question only.
- ⚠️ **`SurfaceTile.Roads` / `.Rivers` return `null`** when the tile's biome sets
  `allowRoads` / `allowRivers` false. An authored road across such a biome is stored and
  invisible — it is not a missing write.

## Companion DLL and mod list — CHECK, 2026-08-19

- ~~The companion is 32 `jawa/` tools~~ ⇒ **the companion is now 47 `jawa/` tools**, and
  **15 of them WRITE the world**. See "The worldmap bridge" below. Verified live by
  `tools/list`, not by `strings`.
  ⚠️ The companion lives in `<gamedir>\BridgeTools\`, a **sibling of `Mods\`**, not inside it,
  and it is discovered by the RimBridgeServer MOD at startup — so `brrainz.rimbridgeserver`
  must be ACTIVE or there is no bridge at all, however the DLL is deployed.
- ~~All four world tools are READ-ONLY~~ ⛔ **SUPERSEDED 2026-08-19.** The batch tile setter
  and the link setter are BUILT, DEPLOYED AND PROVEN. Also: "read-only" was only ever true
  of *game state* — `world_neighbors` and `world_tile_export` both write a file to disk.
- 🔴 **`ModsConfig.xml` is 578 active mods, NOT 583.** Every earlier figure counted the five
  `<knownExpansions>` entries — `grep -c '<li>'` over that file is wrong by exactly 5. Use
  `activeMods` only. So the `mandrake.jawaseashaper` removal was **579 → 578**.
  Version `1.6.4871 rev590`. Full list backed up at
  `D:\Luke\dev\Rimworld\infrastructure\state\modlists\ModsConfig.FULL.LATEST.xml`.
- **Scale 7 / coverage 100% is a PRESET FILE, not a mod of ours** —
  `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3626210061\Worldbuilder\TidallyLocked\Preset.xml`
  carries `<myLittlePlanetSubcount>7</myLittlePlanetSubcount>` and `<planetCoverage>1</planetCoverage>`.
  Confirmed present 2026-08-19. The four mods behind it — `oblitus.mylittleplanet`,
  `ferny.worldbuilder`, `7f.alienworlds`, `7f.alienworlds.tidallylocked` — are all active.
  🔴 **`AlienWorldsFramework.Refresh()` deletes and rewrites that folder, and an ABSENT
  `myLittlePlanetSubcount` Scribes back as 10, not 7** — it fails silently to the wrong
  planet. Rewrite with `python3 src/RimMandrake/Utils/set_planet_subcount.py 7`.
- **Savegame WRITING is gone** (owner, 2026-08-19): nine scripts deleted and
  `worldmap.py`'s two `write()` methods now raise. Reading, decoding and rendering are
  untouched, and `src/RimMandrake/Utils/rimbench/savemap.py` is kept whole — it refuses
  to overwrite its source and passes `fogGrid` through undecoded.

## The worldmap bridge — CHECK, 2026-08-19. 15 new tools, all proven live

Full element census and every API signature:
`design/Jawa/worldbuilding/WORLDMAP_BRIDGE_SURFACE.md`. **Do not re-derive it.**

**The tools** (all under `jawa/`): `world_layers` · `world_tile_get/set/import/validate` ·
`world_commit` · `world_view` · `world_links_get/set/clear/import/validate` ·
`world_mutators_get/set/audit` · `world_landmarks_get/set` · `world_objects_get/set/validate` ·
`world_features_get/set` · `world_info_get/set` · `world_lint`.

- ⚡ **Writing all 21,872 tiles takes 0.1 seconds.** Bulk world editing is not expensive.
- 🔴 **Nothing you write is visible until `jawa/world_commit` runs.** RimWorld has NO
  per-tile visual invalidation except pollution; everything else needs a whole
  `WorldDrawLayer` mesh regeneration. The recipe is vanilla's own and all 8 steps run green.
- 🔴 **`Tile`'s private caches never invalidate.** `HillinessLabel`, `MinTemperature`,
  `MaxTemperature` and `Biomes` are lazily cached with **no reset method anywhere in
  RimWorld**. Read RAW FIELDS to validate, or you will confirm writes that never landed.
- 🔴 **`SurfaceTile.Roads`/`Rivers` are biome-FILTERED views** of `potentialRoads`/
  `potentialRivers`. A biome with `allowRivers=false` HIDES links without deleting them.
  Measured: an untouched world carries 20+ such tiles.
- 🔴 **`BiomeDef.allowRivers` / `allowRoads` are ABSENT from the offline def dump** — all 80
  biomes report neither — yet live they are `False` on `Ocean`, `IceSheet`, `GlacialPlain`.
  **This question cannot be answered offline.**
- 🔴 **`OverlayRiver`/`OverlayRoad` cannot REMOVE** (null only logs `ErrorOnce`) and silently
  refuse a lower-priority def. `jawa/world_links_clear` is ours and edits both endpoints.
- 🔴 **`AddLandmark` does NOT enforce `LandmarkDef.IsValidTile`.** Measured on a settlement
  tile: verdict False, landmark added anyway. Ordering is ours to enforce, silently.
- 🔴 **A `Settlement` with a null faction is DESTROYED on load.** `jawa/world_objects_validate`
  checks exactly that, scoped to Settlements (AsteroidBasic legitimately has none).
- 🔴 **`WorldInfo.overallPopulation` and `landmarkDensity` are not scribed** — they revert on
  every load. `world_info_set` refuses them unless forced.
- 🔑 **`Find.WorldFeatures.textsCreated = false` is the commit step for region LABELS**,
  separate from draw-layer regeneration. ⭐ `drawAngle` is never set by vanilla (all 68
  generated features read 0.0), so label rotation is control the base game does not use.
- 🔑 **A contiguous tile-ID range is NOT a contiguous region on the globe.** Use the
  neighbour graph, never id arithmetic.

**Vanilla `world_lint` baseline** — judge a hand-made planet against THIS, not against zero:
52 findings; 8 single-tile islands; 2 settlements on water; 2 on impassable; **40 of ~100
settlements with no road** (so "no road" is not by itself a defect); 38 river systems with
**0 reaching no sea**.

## Fast reload regime — CHECK, 2026-08-19

- 🟢 **A cold load on the 13-mod MINIMAL list is 22 SECONDS**, against ~25 min on 578.
  Engine's own clock: `[RimBridge] STARTUP_TIMING phase=bridge-start.total elapsedMs=12364`.
  A quicktest world+map on top is **5 s** (`rimworld/start_debug_game_ready`).
  ⇒ the whole edit→build→deploy→launch→test cycle is about **one minute**.
- `python3 src/RimMandrake/Utils/modlist_swap.py --status | --minimal | --restore` (add
  `--apply`; plan-only by default, archives the live file before every write).
- ⚠️ **The minimal list cannot reproduce the 21,872-tile geometry** — `ferny.Worldbuilder`
  is absent and Worldbuilder is what loads the TidallyLocked preset. It is for building
  tools only. Anything depending on real tile IDs needs the full list.
- ⚠️ **`build.py --apply` without `--gm` silently drops `jawa/fire_incident` and
  `jawa/send_letter`.** It refuses and names them. Always `--gm --apply`.
- ⚠️ **`rimworld/search_debug_actions` timed out at 30 s even on 13 mods.** The documented
  debug-discovery hang is not only a heavy-modlist problem. Do not call it.
- ⚠️ **The debug log has Auto-open ON and reopens on any warning**, obscuring screenshots.
  `src/RimMandrake/bridgetools/shoot_planet.py` closes and re-checks up to 4 times.
- ⚠️ **`CameraJumper.TryShowWorld()` returns false unless `ProgramState == Playing`**, which
  `readiness=mapData` does NOT guarantee. `jawa/world_view` takes `altitude` (125 min /
  550 entry / 1100 whole-globe) and `northUp`; the public `altitude` field alone snaps back
  because `Update` lerps toward the private `desiredAltitude`.
