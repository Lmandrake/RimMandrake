## Status: left `doing` — game went unreachable before any write, nothing applied

## Plan found, not invented
An already-vetted, gate-checked placement plan for exactly this item exists at
`design/Jawa/worldbuilding/enrichment/grey_sea.csv` (279 rows) and
`.../twilight_sea.csv` (310 rows), documented in
`design/Jawa/worldbuilding/enrichment/REVIEW.md`. It reads
`design/Jawa/worldbuilding/biomes/the_grey_deep.md` and `the_twilight_deep.md`
(both FROZEN, `BIOME_FREEZE_FABLE_REVIEW_1`) plus `terminator_sea.md`'s
surface/shore law, and picks only defs already gate-safe for these tiles
(`coastSides=0..0` / `maxHilliness=Flat` / ungated): `IceDunes`, `Crevasse`,
`VEE_GravelBeach`, `Harbor`, `AncientSmokeVent`. No `CoastalIsland`/`Archipelago`
-class def was used. This is execution of an already-ruled B1 enrichment wave,
not new design — consistent with this item's brief.

Diving-arc check (per the brief): both sheets explicitly **defer implementation
"for when the diving mods need it"** (owner ruling, 2026-09-07) — no live diving
mechanic exists in this repo yet to feed. The landmarks placed here are
forward-looking set-dressing per the sheets' own "Owed" sections, not wired to
any mechanic.

## Verified against the live defs (this pass, via mcp__rimsage)
`IceDunes`, `Crevasse`, `Harbor`, `AncientSmokeVent` are real `LandmarkDef`s
(checked XML). Their `TileMutatorDef` twins' `biomeWhitelist`s do not include
`RUT_GreySea`/`RUT_TwilightSea` — per `rimworld-world-editing`'s
`mutators-and-objects.md` §7/§8, this gates the WORLDGEN ROLL only and does not
block hand placement (`AddLandmark`/`AddMutator` never re-check biome); `IceDunes`
is already live-proven on 5 Grey Sea tiles per REVIEW.md, so this is a followed
convention, not a new risk.

**One thing flagged, not silently shipped**: `Harbor`'s `LandmarkDef` is
`category=coastal` and its `mutatorChances` carries `Bay Required="True"` — so
placing it also force-adds the `Bay` mutator (`coastSidesRange 1~5`, a real
coastal gate) onto a tile the census says has zero coast sides. The prior
plan's stated rule ("no CoastalIsland/Archipelago/Bay-class def added") reads as
though it should have excluded `Harbor` for the same reason but didn't. Per
`mutators-and-objects.md` §8 this is mechanically inert (the gate binds only the
generator, not a hand write) and IceDunes/Crevasse already set the "override a
whitelist by hand" precedent on these exact tiles — so it is left in the plan,
flagged here for whoever next reviews it rather than re-litigated solo.

## Measured fresh this pass — the plan's tile-count denominator has drifted
`WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1` (commit `ec8e4670`, 2026-09-09 12:26,
12h AFTER the enrichment CSVs were written at 00:09) repainted 171
previously-mislabeled-biome sea-bottom tiles onto these two seas (128 into
`RUT_TwilightSea`, 43 into `RUT_GreySea`). Live re-measure this pass
(`jawa/world_mutators_get` over every tile the current
`world/ASHKARR_WORLDMAP_tiles.csv` lists as either biome — see
`Transient/seal_measure_before.json`):

| sea | tiles when CSV was planned | tiles now (live) | landmarked now |
|---|---|---|---|
| RUT_GreySea | 429 | **472** | 0 |
| RUT_TwilightSea | 479 (1 landmarked) | **607** | 0 |

The Twilight Sea's one pre-existing landmark (tile 5307, `VEE_GravelBeach`) no
longer counts: tile 5307's biome is now `AridShrubland` in the live game — it
drifted off this biome entirely, unrelated to this item, confirmed via a direct
`jawa/world_mutators_get` read.

The 279+310 planned rows all target tiles that were already Grey/Twilight Sea
before the boundary fix and are unaffected by it — the plan itself is still
correct execution material, just under-covers the 171 newly-added boundary tiles
(no gate/coastSides data was ever computed for those, so extending onto them here
would be inventing new placement judgement, not executing the ruled plan — left
as a natural follow-up, not attempted).

## What stopped the pass: the live game went unreachable, mid-measurement
This item is one of a large concurrent BELT wave — the ledger shows a dozen+
other `SEA_ENRICHMENT_LANDMARKS_1`-adjacent FOUNDRY items claiming/starting/
taking the bridge within the same few minutes tonight
(`DROIDWORKS_PERSONALITY_VERIFY_1`, `BIOMESKIT_RENDER_LAYER_MISSING_1`,
`BIOME_ENRICHMENT_POISON_FOREST_1`, etc.), all against the one live RimWorld
process. Sequence this pass:

1. Bridge confirmed FREE (`rimflow bridge who`), taken for this item at
   19:41:41Z.
2. `rimworld/get_ui_state` confirmed `programState: Playing`,
   `hasCurrentGame: true` — game reachable and healthy.
3. Ran the offline-safe **measure** step only (`Transient/seal_apply.py --step
   measure`): confirmed the tile-count drift above via `jawa/world_mutators_get`,
   zero writes issued.
4. A `jawa/world_stats` read-only call (checking total tile count for the
   verification harness) returned normally (`tilesTotal: 119904` — a different
   figure from the frozen 21,872-row hand-authored CSV; not chased further, see
   below).
5. The *next* bridge call (`jawa/world_info_get`, still read-only, still before
   any write) got `ConnectionResetError`, then every retry got `WinError 10061
   connection refused`. `tasklist.exe` shows no RimWorld process at all.
   Player.log's tail (mtime concurrent with the crash) shows ordinary map-gen
   and Ninefold-faction research/satiation log lines, not an obvious crash
   trace — consistent with the process having gone down from something another
   concurrent agent's live session was doing on the shared game, not from any
   call this item made (**no `world_landmarks_set` or other write call was ever
   issued** — `apply` step was never run).
6. Bridge released cleanly (`rimflow bridge release`) so the next window isn't
   blocked on a stale hold.

**Zero writes were made to the live game or the frozen CSV/world files.**
`world/ASHKARR_WORLDMAP_tiles.csv` and its `.frozen.json` are untouched (this
item never needed to touch them anyway — landmarks are not a column in that
CSV; see `world_mutators_get`'s field list vs. the tiles.csv header).

## Not chased this pass, flagged for whoever restarts the game
- The `tilesTotal: 119904` reading from `jawa/world_stats` doesn't match the
  frozen world's documented 21,872-tile hand-authored size. Given the same tile
  IDs cleanly resolved to the expected `RUT_GreySea`/`RUT_TwilightSea` biome
  counts (with exactly the expected +43/+128 drift from a same-session commit),
  this is very likely `world_stats`' own scope/field being something other than
  "this world's authored tile count" rather than evidence of a wrong world —
  but it was not run to ground before the connection dropped. Whoever resumes
  this item should sanity-check that field before trusting `world_stats` again.
- The game was not restarted by this item. Restarting is expensive-list-tier
  and, with a dozen other FOUNDRY items concurrently claiming the bridge this
  same session, unilaterally cold-loading here would step on whichever other
  agent's work is mid-flight. Leaving that call to whoever next holds a clean
  bridge/game-up window.

## To resume
1. Confirm a live game + free bridge (`rimflow bridge who`, then a
   `rimbridge/get_bridge_status` read).
2. Re-run `python.exe Transient/seal_apply.py --step measure` — if tile-count
   drift matches the table above, the plan is still valid as-is.
3. `--step apply`, then `jawa/world_commit`, then `--step verify` (this also
   does the required whole-planet mutator-loss diff — needs a `--step
   full-before` harvest captured BEFORE `apply`, not included in this pass's
   partial run; add one before applying).
4. Close with `rimflow close SEA_ENRICHMENT_LANDMARKS_1 --seat FOUNDRY --sha
   <commit>`.
