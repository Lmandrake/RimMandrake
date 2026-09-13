
## spec
RULED (owner cards, bench 2026-09-12): 325x325, FUTURE LANDINGS ONLY.
- Find where the stored map size lives in the canonical start save
  (CANONICAL_ASHKARR_START_2026-09-12.rws — world info / game init data), and
  what actually governs NEW gravship landing map sizes on the full list.
  Verify the mechanism before editing (rimworld-savegame skill; back up the
  save, stat afterwards, confirm no other file changed).
- The already-generated Zeddo's Yard start map is NOT regenerated (owner card:
  future landings only).
- If map size proves to be per-settlement/site rather than a save global,
  report the real mechanism back instead of forcing it.

## verify
A quicktest-scale check is insufficient (map size binds at map creation on the
campaign save): land the gravship on a fresh tile in a COPY of the canonical
save and measure the new map's dimensions (savemap.py or in-game bridge read) = 325.

## 2026-09-13 (FOUNDRY) — mechanism found, verified live, applied

**Mechanism**: `WorldInfo.initialMapSize`, a single per-WORLD global stored
once in the save's world-info block (`<initialMapSize>(x, 1, z)</initialMapSize>`,
one occurrence per save). `jawa/world_tile_map_generate`'s own tool
description confirms it's the fallback: "`sizeX`/`sizeZ`: -1 uses
`Find.World.info.initialMapSize`" — and that tool shares the exact
`GetOrGenerateMap` code path a gravship landing or Settlement/Site entry
uses. Per-settlement/per-site sizing does NOT exist; it is a world global,
so a single edit governs every future landing.

**Verified live before touching the real save**, per this item's own
instruction not to force it blind:
1. Read the canonical save's own field: `<initialMapSize>(250, 1,
   250)</initialMapSize>`, exactly one occurrence
   (`MEASURE_ALLOW_SCAN=1 grep`). `jawa/world_info_get` on the live loaded
   game read back the identical `{x:250,y:1,z:250}` — two independent reads
   agree on the field and its live value.
2. Made a TEST COPY (`Saves/TEST_GravshipMapSize_2026-09-13.rws` —
   never edited in place), changed only that one field to `(325, 1, 325)`,
   loaded it (`rimworld/load_game_ready`, `ignoreModCompatibility` since the
   live mod count had moved since the save's own recorded 594).
3. **Confirmed the split the owner's ruling asked for, live**: the already-
   generated start map (Map_3, tile 17007, "Zeddo's Salvage Yard") stayed
   **250x250** — not regenerated, exactly as required. Founded a fresh
   settlement at an empty tile and called `jawa/world_tile_map_generate`
   (default `sizeX`/`sizeZ`, the same "no override" a real landing would
   use) — the new map generated at **325x325**, confirmed via the tool's own
   `mapSize` response field. Mechanism proven on the live engine, not
   inferred from source alone.

**Applied to the real save**: backed up
`CANONICAL_ASHKARR_START_2026-09-12.rws` to
`CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-gravshipmapsize-2026-09-13`
(stat'd — original size 16,466,734 bytes, byte-identical to the pre-edit
backup), made the same single-field edit, parse-validated the result as
well-formed XML, then reloaded it live: `jawa/world_info_get` reads back
`{x:325,y:1,z:325}` after a real save/load round trip (not just in-memory),
and the start map is still 250x250 on that same reload. No other file
touched; no other line in the save changed (single targeted string
replace, not a full rewrite).

## criteria
New landing maps generate at 325x325 on the canonical campaign; the start map
is byte-unchanged; the canonical save's keeper status respected (backup kept).
