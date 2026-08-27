> 🧹 **PRUNED 2026-08-24 01:4x on the owner's order — "clean out all stale NEXT_RELOAD files
> immediately".** Every block whose only item IDs had already closed, dropped or been superseded
> was removed; blocks naming still-live work were kept verbatim. **Nothing is lost — the full
> previous text is the parent of commit `ec0b5a61` in git.** ⚠️ A block here is a DUPLICATE of a ledger
> item; when the two disagree, the ledger is right.

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

⚠️ **Painting under a map destroys THAT COLONY — not the game.** Make a new colony and carry on.

## Housekeeping done before this launch

- The def-dump marker is **disarmed** — today's dump is current for this mod set and the
  marker is not consumed, so every load would otherwise pay ~27 s for a duplicate.
- `Player.log` from the previous session is preserved at
  `observed/2026-08-21_Player.log.worldpaint-menu`; the launch overwrites the live one.
- Both assemblies are deployed and byte-verified. Nothing is waiting on a shutdown window.
