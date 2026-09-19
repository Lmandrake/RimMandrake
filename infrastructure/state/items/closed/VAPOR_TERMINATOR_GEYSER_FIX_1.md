# VAPOR_TERMINATOR_GEYSER_FIX_1 — zero `SteamGeysers_Increased` at/past the terminator

Filed against the finding in `design/Jawa/worldbuilding/vapor_emitter_review_2026-09-12.md`
Part 3: 21/54 `SteamGeysers_Increased` world-tile mutators sat at or past arc 90 (the
terminator), violating the owner's ruled "radial decay from mountains, zero before the
terminator" steam rule (ruled 2026-09-06).

## done 2026-09-12, FOUNDRY

Backed up the live save first (CHARTER expensive-list #4):
`...\Saves\CANONICAL_ASHKARR_2026-09-09.rws.bak-pre-vapor-terminator-geyser-fix-2026-09-12`.

Loaded the canonical save live (`rimworld/load_game_ready` with
`ignoreModCompatibility: true` — 9 fauna-donor mods recorded on the save are not in
the current active set; unrelated to worldgen/mutators, doesn't affect this fix).

**Re-measured against the LIVE world (not the frozen doc's numbers):**
`jawa/world_mutators_get` (range 0-21871) found **54** tiles carrying
`SteamGeysers_Increased`, matching the doc's count exactly. Cross-referenced against
`jawa/world_tile_export`'s lat/long (arc = `degrees(acos(cos(lon)*cos(lat)))`, the
tidally-locked-world formula) found **21** at arc >= 90 — the identical 21 tiles the
doc named, confirming the doc's claim rather than trusting it blind.

**Fix**: `jawa/world_mutators_set` (`action: remove`, `mutators: SteamGeysers_Increased`)
on those 21 tile IDs, then `jawa/world_commit`. Read-back on the same 21 tiles
confirmed 0 still carry it.

**Independent re-verification**: re-ran the full 21,872-tile scan from scratch
(fresh `world_mutators_get` + `world_tile_export`, not just the 21 touched tiles) —
33 `SteamGeysers_Increased` tiles remain planet-wide (54 - 21 removed), **0 at
arc >= 90**. The rule now holds everywhere on the frozen map, not just on the tiles
touched.

**Persisted**: `rimworld/save_game` back onto `CANONICAL_ASHKARR_2026-09-09` (same
slot — verified by mtime AND size change, `.rws` count unchanged at 12, no new file
created, matching the intended slot per the silent-overwrite trap in
`skills/rimbridge/references/traps.md`).

**Not touched, out of scope for this item**: `AB_MagmaVents`' 5 orphaned tiles and
the `GeothermalVent` (Odyssey, per-colony-map, ungated) finding from the same
review — those are separate cleanup/design items, not part of the terminator rule.

## criteria — met
No `SteamGeysers_Increased` tile remains at or past the terminator (arc >= 90) on
the frozen Ash'karr world.
