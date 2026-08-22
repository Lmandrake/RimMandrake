# LIVE.md — facts you would otherwise need a running game to learn

Published by CHECK. One line per fact. Superseded lines are replaced, not appended to.
Everything here was read out of a running game or off an artifact a running game wrote.

## The def dump

🔴 **RATIFIED AS DEFINITIVE BY THE OWNER, 2026-08-20:** *"Please keep this thingdef dump
as definitive until I say otherwise. I don't plan on adding new mods for some time now, so
let's go with these dumps and do some real normalization and later v1 freezing."*

- **Current dump: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump`,
  captured `2026-08-20T08:06:19Z`, `mode: all`, game `1.6.4871 rev591`, **577 mods**.
  `ThingDef 24,878 · PawnKindDef 1,735 · FactionDef 86`.
- ✅ **FRESH ON BOTH AXES, which is the first time that has been true.** The dump holds 577
  and `ModsConfig.xml` `activeMods` holds **577** — the same set, not a superset. That is
  what makes it usable as a reference rather than as a hint, and it is the condition the
  owner's ruling above depends on.
- 🔑 **THE FINGERPRINT IS THE MOD SET, NOT THE CLOCK.** The pair to compare is dump
  `modCount` against the count of `<activeMods>` children — never a file or folder mtime,
  and never `grep -c '<li>'`, which also sweeps in the five `<knownExpansions>` entries and
  reads five too high. `src/RimMandrake/Utils/weapon_tag_audit.py` refuses to report at all
  when the two disagree; that refusal is the check working, not an obstacle.
- ⇒ **Until the owner says otherwise, a def question is answered from THIS dump.** If a
  mod is added or removed, the ruling lapses and the dump must be retaken — the set
  changing is precisely what "otherwise" means.
- ⚠️ **What the dump still cannot tell you** is unchanged and matters for the
  normalization work: it is post-inheritance, post-PatchOperation and post-dedup, so it
  describes what LOADED — but a `PatchOperationConditional` that matched nothing left no
  trace in it or in the log, and 79 def types come through empty (see
  `rimworld-def-dump-blind-spots`). Absent from the dump is not the same as absent from
  the game.

### History: the two-axis trap that produced this rule
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

- ~~The companion is 32 `jawa/` tools~~ ~~106~~ ⇒ **the companion SOURCE declares 120 `jawa/`
  tools** (2026-08-22, regex over the `[Tool(` attribute across the `JawaBench*Tools.cs`
  files). ⚠️ **Two are `#if JAWA_GM_TOOLS`** (`fire_incident`, `send_letter`), so a build
  without `--gm` ships **118** — and the LIVE total is larger again, because RimBridgeServer
  contributes its own `rimworld/*` family that no source count of ours can see.
  🔑 **Count it live with `tools/list`, never quote a number from a doc, and NEVER use
  `strings` on the assembly** — it found 16 of 115 names and reported the shortfall as a
  clean answer.
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

## `jawa/world_cache_audit` — CHECK, 2026-08-22. Built and deployed; NOT yet proven live

🔴 **`Tile` caches four values and RimWorld never invalidates any of them:**
`hillinessLabelCached`, `cachedMinTemp`, `cachedMaxTemp`, `tmpHasSecondaryBiome`
(read out of `RimWorld/Planet/Tile.cs` 1.6). ⇒ **After a repaint the raw fields are correct,
every raw-field validator passes, and the UI still draws the OLD value.** That is why
repainted mountains stayed unclickable, and it was only ever findable by a human clicking.

- The audit reads those private fields **by reflection** — no side effect — and recomputes
  the expected value by replaying the getter's own logic. It reports `cached` (populated)
  separately from `stale` (populated AND disagreeing).
- ⛔ **Do not "simplify" it to compare `HillinessLabel` against `hilliness`.** Two ways that
  fails, both of which look exactly like a pass: `HillinessLabel` is seeded from the raw
  field and then **overridden by any mutator with `hillinessLabel != Undefined`**, so the
  comparison reports a false stale on every mutated tile forever; and **touching the public
  getter POPULATES an empty cache**, so the audit silently repairs what it is measuring.
- 🔑 **A tile with an EMPTY cache cannot go stale** — a fresh load reporting zero is correct,
  not a pass. `populate=true` (off by default, and it runs *after* the measurement) arms a
  before/after test: populate → repaint → audit.
- **There is no cache-clearing tool and there will not be one.** RimWorld has no reset method
  for these; **a reload is the only fix**, and that is the finding.
- Proof harness: `src/RimMandrake/bridgetools/prove_world_cache_audit.py`. ⚠️ Its last step —
  save, reload, expect `staleTotal == 0` — costs a second load and is deliberately NOT run by
  the script.

## The worldmap bridge — CHECK, 2026-08-19. 25 new tools, all proven live

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

## The map and pawn tools — CHECK, 2026-08-19. 22 more tools, all proven live

`JawaBenchMapTools.cs` (13) and `JawaBenchPawnTools.cs` (9). Roster and reasoning:
`design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md`.

```
MAP     map_commit · get_terrain_layers · set_substructure_batch · set_terrain_layer
        set_fog · set_weather_buildup · set_deep_resource
        build_batch · build_check · designate_batch
        prefab_capture · prefab_place · prefab_list
PAWN    pawn_get · set_pawn_identity · set_pawn_backstory · pawn_traits · set_pawn_skill
        set_pawn_appearance · pawn_gear · pawn_health · pawn_need
        set_pawn_faction · set_pawn_ideo · pawn_relations · pawn_genes · set_pawn_age
```

### Things the engine does that will cost you a session if you don't know them

* 🔴 **`PrefabUtility.CreatePrefab` NEVER SETS `size`.** It comes back `(0,0)`, and `size`
  drives `GetRoot` and every bounds check — so a prefab captured with vanilla's own API is
  **unusable** until the caller fills it in. Found by it refusing to place.
* 🔴 **`SpawnPrefab` CENTRES on `pos`.** The min corner is `pos - ((size-1)/2)`, measured at
  two positions. It is not a corner placement.
* 🔴 **`ageTracker.DebugSetAge` is FORWARD-ONLY.** 34→54 works; 54→8 leaves the pawn at 54
  **and reports success.** Aging down needs the raw `AgeBiologicalTicks` setter, which
  skips every `BirthdayBiological` — so life-stage hediffs and growth moments never fire.
* 🔴 **`equipment.AddEquipment` `Log.Error`s and does NOTHING if a primary exists.**
  `MakeRoomFor` first or the call reports success having changed nothing.
* 🔴 **`ThingMaker.MakeThing` calls `PostMake`, which RANDOMISES HitPoints** from
  `def.startingHpRange`. Set HP *after* the spawn or it is silently lost.
* 🔴 **Setting a backstory refreshes NOTHING.** Four calls are needed —
  `Notify_DisabledWorkTypesChanged`, `skills.Notify_SkillDisablesChanged`,
  `skills.DirtyAptitudes`, `MeditationFocusTypeAvailabilityCache.ClearFor`. **The game's own
  debug tool runs only the last.** Proven: doing all four moved the pawn's disabled-skill
  set from `['Cooking']` to `['Social']`.
* 🔴 **`GainTrait` checks NO conflicts and `TraitSet` has NO cap.** Our refusal is ours.
* 🔴 **`SkillRecord.Level`'s getter ADDS APTITUDES**, so read-back ≠ what you wrote. Compare
  against `GetLevel(false)`.
* 🔴 **`Sibling` and `Child` are IMPLIED relations** — computed from the family graph, not
  storable. Only 9 of 41 `PawnRelationDef`s can be added directly.
* 🔴 **`SUBSTRUCTURE` is a foundation-layer `TerrainDef`**, not a grid.
  `Map.substructureGrid` is only an overlay drawer. 1.6 has **five** terrain layers.
* 🔴 **Walls create NO roof.** Confirmed by building a room and finding it open to the sky.
* ⚠️ `health.RestorePart` is **recursive**, wipes child hediffs and drops nothing.
* ⚠️ Social `ThoughtDef`s require an `otherPawn` or are dropped **silently**.
* ⚠️ `TryAddOrTransfer` returns the **count** moved, not a bool.
* ⚠️ Appearance writes do not dirty the renderer — call `SetAllGraphicsDirty()`.
* ⭐ `install_bionic` needs **no RecipeDef and no surgeon**: `RestorePart` then `AddHediff`.
* ⭐ `map_commit` is the map twin of `world_commit`. `Thing.SpawnSetup` already handles
  listers, grids, glow, temperature and region dirtying; `map_commit` covers the rest.

### Two workflow traps that cost real time here

* 🔴 **`Player.log` PERSISTS between runs.** Grepping it for the bridge-ready marker matches
  the PREVIOUS session and returns instantly, before the new game has started. Wait for the
  log to **truncate** first — `src/RimMandrake/bridgetools/launch_and_wait.sh` does.
* 🔴 **Kill RimWorld BEFORE building.** `build.py` cannot overwrite a memory-mapped DLL and
  says so, but a piped `grep` can hide the refusal and you then test stale code.
* ⚠️ **A docstring containing `jawa/world_*` made `build.py` report a phantom lost tool.**
  Its scanner reads `jawa/...` literals out of the assembly. Avoid that pattern in prose.
* ⚠️ **Fog defeats screenshots.** A slab written correctly in unvisited territory photographs
  as nothing. `jawa/set_fog action=unfogAll` first.
* 📌 **Never guess a defName** — 1,225 BackstoryDefs, 2,129 ThoughtDefs, 265 TraitDefs, 41
  PawnRelationDefs. Four of my test names were invented and all four failed. Read the dump.

## Routing, effects, pawn systems and social events — CHECK, 2026-08-20

```
ROUTE    connect_cells        strict | mine | bridge, atomic, never half-laid
EFFECTS  map_explosion · map_fire · map_skyfaller
PAWN     pawn_psychic · pawn_pregnancy · pawn_mental · pawn_romance
WORLD    world_objects_add · world_objects_remove
SOCIAL   social_list · social_gathering_start · social_marry · ritual_start · social_cancel
```

* 🔑 **Mountain is EXPENSIVE; deep water is IMPOSSIBLE.** `WaterDeep` has no terrain
  affordances and is not Bridgeable. Wall → `mine` goes straight through (45 cells);
  shallow water → `strict` routes *around* (49), `bridge` goes through (45).
* 🔴 **Vanilla routes conduits with a FLOOD FILL over placeability, not a pathfinder**
  (`GenStep_Power`). `FloodFiller` is **4-connected**, `PathFinder` is **8-connected** — a
  pathfinder route must be densified to cardinal steps or **the net breaks at every diagonal**.
* 🔴 **Maps are NOT square and quicktest sizes vary** — one was 100×400, the next 250×250.
* 🔴 **`ChangePsylinkLevel` never reads its offset on the first call** — one call can only
  reach level 1.
* 🔴 **Gestation IS the pregnancy hediff's Severity.** No separate field; 1.0 starts labour.
* 🔴 **`TryStartMentalState` returns false silently** on ~6 conditions. Surface the bool.
* 🔴 **Opinion is purely COMPUTED** from relations + memories. A memory is the only lever —
  a bare relation change produces no thought at all.
* 🔴 **`TryStartMarriageCeremony` IGNORES its second argument** and re-derives the partner
  from the **Fiance** relation, which is mandatory.
* 🔴 **Funerals are NOT Ideology-only.** `FuneralBase` is `<classic>true</classic>`, so
  Funeral, FuneralNoCorpse and the `Classic_` parties exist with Ideology uninstalled.
  Gate on the precept being present, never on the DLC flag.
* 🔴 **`RitualBehaviorWorker.TryExecuteOn` is void and fails silently.** Call
  `CanStartRitualNow` first; use the lord count as evidence.
* 🔴 **Gathering game-conditions live in `GatheringDef.CanExecute`, not `Worker.TryExecute`** —
  calling the worker bypasses them all, as vanilla's debug action does. But
  **`respectTimetable` is NOT bypassable**: a forced party during a Work block stays empty.
* ⭐ **Gathering attendees are PULL, not push** — the lord starts with zero pawns and
  colonists self-join. Proven: 0 → 3 pawns after 400 ticks.
* ⚠️ **`PsychicShock` is a HediffDef and `Bioferrite` a ThingDef** — neither is a DamageDef.
* 📌 A quicktest map can spawn mid-**fleshbeast assault**, which blocks every social event.
  The tools were telling the truth; the environment was hostile.

## Gas, zones, areas — M4, commit `669be9e` — CHECK, 2026-08-19

```
GRID    set_gas          add | clear, four types only:
                         BlindSmoke · ToxGas · RotStink · DeadlifeDust
ZONE    map_zones        listZones · createZone (stockpile | growing) · paintZone ·
                         deleteZone · listAreas · paintArea
```

* ✅ 64 cells of `ToxGas` added and cleared; stockpile created 36/36 cells, growing zone
  25/25 with `Plant_Potato` set, painted and deleted; `Home` and `NoRoof` painted with
  `trueCount` following.
* 🔴 **A bulk `AddCell` REFUSES cells silently** — the first cut wrapped it in a bare
  `catch {}` and a 6×6 stockpile took **11 of 36 cells while reporting success**. The tool
  now returns `cellsRequested`, `refusedCount` and `refusedCells[]` with each refused
  cell's terrain, and says plainly when nothing changed. Read those, never the bare success.
* ⚠️ `CheckContiguous()` runs after every bulk `AddCell` — a rect that straddles an
  obstacle does not stay one zone.
* 📌 The 1.6 area name really is **`Area_SnowOrSandClear`**, renamed from `Area_SnowClear`.

## Weather, game conditions and raids — E1, commit `a5b0f2d` — CHECK, 2026-08-19

```
READ    weather_get · raid_preview            ungated
GM      weather_set · game_condition · fire_raid    #if JAWA_GM_TOOLS
```

* ⭐ **A REAL RAID FIRED AND ARRIVED.** RaidEnemy, 1,200 pts, `ImmediateAttack`,
  `EdgeWalkIn` → **14 `TribeSavageImpid` raiders**, pawn count 10 → 24. Confirmed by
  counting pawns, not by `executed: true`.
* 🔴 **`CanFireNow` being FALSE does NOT block `TryExecute`.** It reported false throughout
  and the raid fired anyway — it carries storyteller pacing the executor never consults.
  It is not a gate.
* 🔴 **`RaidStrategyDef.Worker.CanUseWith` is MEANINGLESS while `parms.faction` is null** —
  all 11 strategies then report unusable at every point value, which reads as "raids are
  impossible". Resolve an attacker first. With one resolved the point gating is visible:
  35 → none · 250 → ImmediateAttack, ImmediateAttackSmart, StageThenAttack ·
  1000 → + ImmediateAttackBreaching(Smart), ImmediateAttackSappers · 3000 → + Siege.
* 🔴 **Ending a condition LOOKS like it failed while paused.** `Duration = TicksPassed`
  expires on the NEXT tick, so a paused game still lists it; stepping 5 ticks cleared it.
  The tools report `endsNextTick` and `gamePaused`.
* 🔑 **A plain `TransitionTo` is temporary; only `lockWeather=true` is durable** — it
  registers a permanent `GameCondition_ForceWeather` and `WeatherController` appears in the
  active condition list. That is the only durable weather control in the game.
* ⚠️ **`Planetkiller` is hard-blocked** by the tool, and says why: it ends the game.
* 📌 `weather_get` exposes what nothing else does — `threatPoints` (35 on a fresh colony)
  and the wealth split (total / items / buildings).

## Six new companion tools, deployed and UNTESTED — CHECK, 2026-08-20 overnight

Deployed and byte-verified while the game was down; **none has run in a live process.**
The assembly carries **112 distinct `jawa/` tool names** against 106 live in the last
session. Treat every one as a hypothesis until a load exercises it.

| tool | what it answers |
|---|---|
| `jawa/faction_relations_get` | the pairwise faction matrix, BOTH directions, with an `asymmetric` list |
| `jawa/faction_relations_set` | any pair including `Player`; writes both records and fires `Notify_RelationKindChanged` |
| `jawa/pawnkind_audit` | which PawnKindDefs can never arm, split into noWeaponTags / emptyTagPool / cannotAfford |
| `jawa/texture_audit` | every texPath that resolves to nothing, incl. per-lifeStage and FEMALE variants |
| `jawa/world_settlements_import` | W9 stage 5; refuses the whole import if any faction is unresolvable |
| `jawa/world_features_import` | W9 stage 7; the 23 named regions, from the tiles CSV's own `region` column |

🔑 **`weaponMoney` is a CEILING, not a bracket.** `PawnWeaponGenerator.TryGenerateWeaponFor`
keeps every pair whose `Price` is not greater than ONE roll of `weaponMoney.RandomInRange`.
`min` never excludes a weapon; only `max` can empty the pool. And the comparison is
`ThingStuffPair.Price`, which includes stuff — bare `MarketValue` understates it.

🔑 **A texPath question cannot be settled from a shell.** Windows' filesystem is
case-insensitive; RimWorld's content index is not. `GRimPinkBird` resolves from `ls` and
fails in game. Only the running game can answer it — hence `texture_audit`.

⚠️ **`world_lint` no longer counts `Lake` as sea-level water.** It did, and fired 312 times
on the Ash'karr import — exactly once per authored lake. A lake at altitude is ordinary
geography. Ocean and SeaIce still score; lakes are reported separately at zero weight.

📌 **One command for a fresh load:** `python.exe src/RimMandrake/Utils/first_light.py`
— tool census, arming audit, texture sweep, world identity, tile validate, lint. All reads,
about a minute, writes `infrastructure/output/first_light_<date>.md`.

## A game can fail to load and keep answering — CHECK, 2026-08-20

🔴 **`status: game_loaded` is not proof the game loaded.** On 2026-08-20 `rt_probe.rws`
aborted mid-load — `FactionControl`'s postfix on `CrossRefHandler.ResolveAllCrossReferences`
threw with the signature of a collection modified during enumeration — the engine called
`ErrorWhileLoadingGame` → `GoToMainMenu`, and **that bail handler itself NREd** in
`MapDrawer.Dispose`. The process then ran for hours in a half-disposed state, reporting
`game_loaded`, answering every bridge call, and returning plausible numbers.

🔑 **THE CANARY, and it costs one call:** `rimworld/list_debug_action_children("Actions")`.
In a zombie it throws `NullReferenceException` while `Outputs` (233 children) and
`Settings` (184) answer normally. `first_light.py` now runs this automatically. Run it
FIRST on any load, before believing anything else.

📌 Secondary tells, all present that day and all easy to explain away individually:
Vehicle Framework's ColonistBar patch spamming `KeyNotFoundException: key '0'` every
OnGUI; dozens of `Could not find think node with key …`; and a `Could not get load ID …
never added during LoadingVars` above the abort.

⚠️ **What still counts from a zombie session:** results about the TOOLS. A tile import that
reports 21,872/21,872 and validates at 100% really did do that. What does NOT count is any
claim about the game's state, its save, or its behaviour.

---

## An ideoligion's DESCRIPTION is not readable through the bridge — CHECK, 2026-08-21

`jawa/ideo_of` returns name, adjective, memberName, culture, structureMeme, keyDeityName,
memes, precepts, roles, veneratedAnimals, preferredXenotypes, primaryFactions and believer
counts — **and no `description`**. `rimbridge/run_script` only chains existing capability
calls, so there is no reflection route either.

✅ **The route that works: save the game and read the `.rws`.** `rimworld/save_game` then
`ideoManager/ideos/li/{name,description,memes}`. A quicktest save is ~17 MB and parses in
seconds with `ET.iterparse`. This is how B54's twelve `ideoDescription` strings were proved
verbatim.

⚠️ **RimWorld unescapes literal `\n` in XML text at load.** An authored description
containing `\n\n` will differ from the runtime string by 2 bytes per occurrence and is NOT
a content mismatch. Unescape before comparing, or you will report a false DIFF.

## A dev quicktest generates the full faction roster and every ideo — CHECK, 2026-08-21

`rimworld/start_debug_game_ready` on the owner's full 578-mod list produces a world with
the complete faction set and 45 Ideos, in ~1 minute. **All twelve authored faction faiths
were present and correctly attached.** So the eleven-faiths class of question does NOT need
a real worldgen click to answer.

🔴 **`readiness: gameData` returns in ~1.6 s and is a lie about progress** — it comes back
with `hasCurrentGame: true`, `longEventPending: true`, `mapCount: 0`. Poll
`rimworld/get_game_info` until `status: game_loaded`; that took ~45–70 s here.

⚠️ **Two quicktests came back byte-identical** — same ideo ids, memes, deities, factions.
Reproducibility, yes; **evidence of a shared seed, not proof that the owner's real worldgen
will match.** Do not report a quicktest result as a prediction about the frozen world.

## ⚠️ `BiomeDef.wildAnimals` lists EVERY animal, at commonality 0 — CHECK, 2026-08-21

`Ocean` carries **1024** `BiomeAnimalRecord` entries. The animals that cannot live there are
present with **`commonality: 0`**. ⇒ **"appears in `wildAnimals`" means nothing.** Asking
which biomes list `AA_Eyeling` returns **79**, including `Ocean`, `Space`, `Orbit`,
`IceSheet` and `MetalHell`. Filtering `commonality > 0` returns the true answer: **3**
(`ExtremeDesert`, `Wasteland`, `ZBiome_DesertOasis`).

🔑 The same shape almost certainly applies to `wildPlants`. **Filter on commonality before
counting anything biome-borne**, or a desert animal reads as living in orbit.

## A dev quicktest generates the full authored faction roster — CHECK, 2026-08-21

37 visible factions, **105 settlements**, and all twelve authored factions present with
settlements: Hutt Cartel 6 · the Junkers 4 · Ascendant Helix 3 · Jawa Trade Moot 3 ·
Homestead Defense League 3 · Deepwater Compact 2 · Free Droid Enclaves 2 · Deep Desert
Tribes 2 · Geonosian Foundry Hive 1 · Wildsteam Clan 1 · Galactic Empire 1 · Blackstar
Company 1. ⇒ Faction-roster questions do **not** need a real worldgen click.
