# RELOAD_CHECK.md — load the painted world, and settle three things at once

**The next launch does not generate anything.** It loads `WORLDMAP_gen`, which already holds
the painted planet. Written before the launch, because a prediction written afterwards is a
story that fits.

## What is on disk right now

`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\WORLDMAP_gen.rws`
— 5,160,699 bytes, saved 2026-08-21 02:32, md5 `9b572575ec23a8d5f00a98ed3c7e85d8`, backed up
into the repo at `world/WORLDMAP_gen.rws` by `388646f`.

    <maps />                     ⭐ EMPTY — the destroyed colony is NOT in it
    <subdivisions>7              correct geometry
    <planetCoverage>1
    WB_MapLabelFeature ×23       our region labels, at the corrected small size
    tileMutatorDefsDeflate       the mutator layer is scribed
    tileMutatorTilesDeflate
    AncientHeatVent, sw_Sarlacc  our landmarks
    Jawa_HuttCartel …            our factions

⭐ **A painted planet with no map is exactly the target state**, and it survived the session
that broke around it. Nothing needs generating.

⚠️ **Two fixes landed AFTER the save and are therefore NOT in it:**

| fix | pushed live | in the save? |
|---|---|---|
| label resize (23 features) | 02:17 | ✅ yes |
| rainfall clamp (231 tiles off the ceiling) | ~02:47 | ❌ **no** — lava still reads 1668 mm |
| river re-grade (113 HugeRiver → 29) | ~02:53 | ❌ **no** — still the inverted hierarchy |

Both are one bridge call each to re-push after loading.

## The three questions this one load answers

> 🔴 **ANSWERED 2026-08-21 04:00, and the answer changed the plan.** `WORLDMAP_gen` aborted
> with the identical `FactionControl.CrossRefHandler_ResolveAllCrossReferences.Postfix`
> signature — **third save, third abort, one stack frame.** It is the mod set, not the saves.
> `thereallemon.factioncontrol` is now DISABLED and the load is being retried.
> ⚠️ And `ErrorWhileLoadingGame` read **0** on that abort, because it fires on MAP init and
> this save has no map — so string 1 below was NOT sufficient and `w9_run.py`'s canary has
> been taught `Exception in FinalizeLoading` as well.
> `LOAD_ABORT_IS_FACTIONCONTROL_1`.

**1. 🔴 Does the load abort?** This is `LOADS_ARE_BLOCKED_NEEDS_YOU_1`, open since 2026-08-20.
`rt_probe` and `WORLDMAP_gen_sub7b` both died on
`FactionControl.CrossRefHandler_ResolveAllCrossReferences.Postfix()` inside
`ScribeLoader.FinalizeLoading`. Those were older saves. **This one was written by this mod
set, tonight.** Either result is worth the load: clean means the abort was save-specific;
abort means it is the mod set, and FactionControl is the suspect.

**2. Do the mountain-acting tiles clarify?** The owner's observation: tiles that used to be
mountainous or impassable stayed unclickable after the repaint. Cause is documented in
`jawa/world_commit`'s own contract — `hillinessLabelCached`, `cachedMaxTemp`, `cachedMinTemp`
and `tmpSecondaryBiome` have **no reset method anywhere in RimWorld** and clear only on
reload. This load is the only way to test it.

⚠️ **The bridge could not answer this at 03:00 and now can.** `jawa/world_tile_get` builds
both `hilliness` and `hillinessInt` from the RAW field, so it reports a tile as correct
whether the cache is stale or not. `jawa/tile_cache_audit`, built and deployed 2026-08-21,
reads `hillinessLabelCached` **by reflection** — calling the property would populate the very
cache it is observing — and separates a real stale entry from a `TileMutatorDef` legitimately
supplying the label. String 12. `HILLINESS_CACHE_NOT_READABLE_1`.

**3. Does the paint survive a round trip?** Read back after loading and compare to the CSV.

## The decision strings, written before the launch

| # | what settles it | expected |
|---|---|---|
| 1 | `grep -c ErrorWhileLoadingGame Player.log`, read **20 s after** `status: game_loaded` | **0**. The abort is written after the status flips, so an immediate read passes a broken load |
| 2 | `rimworld/get_game_info` → `mapCount` | **0**. If a map appears, something instantiated one and the paint must not be re-pushed |
| 3 | `jawa/world_info_get` → `tilesCount` | **21872** |
| 4 | seven CSV tiles read back — 2476, 11350, 15087, 8147, 19495, 10, 12411 | biome, temperature and rainfall match the CSV **to the digit** (rainfall on the volcanic ones will read the OLD 1668 until the re-push) |
| 5 | `jawa/world_landmarks_get` | **16** |
| 6 | `jawa/world_features_get` | **23**, and `maxDrawSizeInTiles` ≤ 24.3 — proves the label resize scribed |
| 7 | the owner clicks a tile that was mountainous before the repaint and is Flat now | it selects. ⭐ String 12 now answers this as a number, so this is the confirmation rather than the instrument |
| 8 | after the two re-pushes: `jawa/world_tile_get` on 11965 / 19495 / 2540 | rainfall **40**, not 1668 |
| 9 | after the two re-pushes: `world_links_import` reply | `rivers 238`, `roads 837`, `unknownDefs []` |

| 10 | `grep -c "WorldMaterials/BiomesKit" Player.log`, **after the planet has drawn** | **0** ⇒ the magenta belonged to the broken session. **~44** ⇒ normal for this mod stack; ReGrowth 2 ships no `_VerySnowy`/`_FullySnowy` for ANY biome, so it is the framework's gap, not our map's. `BIOMESKIT_SNOWY_DESERT_TEXTURES_1` |
| 11 | `jawa/tile_settleable` with no args | a planet sweep. Expect ~**2,232 refused** (1,780 water · 504 settlement-adjacent · 39 impassable) and the engine's own reason text on each |
| 12 | `jawa/tile_cache_audit` with no args | `unexplainedStale` — **this is the mountain question**, answered as a number instead of by clicking |
| 13 | `jawa/biome_art_audit` | `missingCount` **0**, or the biome that draws magenta named |
| 14 | `jawa/faction_leader_get` | effective title beside def title for Empire/Outlander/Tribe/Pirate — settles the `leaderTitle` half of B40–B43 |

⭐ Strings 11–14 exercise **four new tools built 2026-08-21** and deployed into this launch.
Proving them IS part of this run: a tool that has never returned a number is not a tool yet.

## The sequence

1. Launch. **Do not generate anything.**
2. Load `WORLDMAP_gen`.
3. **Stop.** Do not pick a landing site, do not settle. `mapCount` must stay 0.
4. CHECK reads strings 1–6.
5. Owner tries string 7 — click a formerly-mountainous tile.
6. If 1–6 are clean, CHECK re-pushes the two fixes:
   `jawa/world_tile_import` (rainfall) and `jawa/world_links_import` (river grades),
   then `jawa/world_commit`.
7. Owner **saves over `WORLDMAP_gen`**, and only then lands if he wants to.

⛔ **Do NOT paint under a map, ever again.** `PAINT_UNDER_MAP_DESTROYS_GAME_1` records what
that cost on 2026-08-21: the colony, the ability to make a new one, the UI's button icons,
and the planet-scale preset on a world remade in that session.

## Housekeeping done before this launch

- The def-dump marker is **disarmed** — today's dump is current for this mod set and the
  marker is not consumed, so every load would otherwise pay ~27 s for a duplicate.
- `Player.log` from the previous session is preserved at
  `observed/2026-08-21_Player.log.worldpaint-menu`; the launch overwrites the live one.
- Both assemblies are deployed and byte-verified. Nothing is waiting on a shutdown window.
