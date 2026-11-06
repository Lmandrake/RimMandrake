# The full list's managed heap ratchets across game loads

Item: `HEAP_DIAGNOSE_RELOAD_RATCHET_NOT_MAP_SCALE`. Measured 2026-11-06, offline, from TPS record ee0fbaa8 (317 mods, 19:21Z to
22:09Z). Reader: `python3 src/RimMandrake/Utils/heap_ratchet.py --session ee0fbaa8`. **Verdict `reload_ratchet`.**

## The answer to the item's question

The item asked whether Mono keeps its high-water mark (expected) or game reloads retain memory (a leak). **Reloads retain
memory.** The high-water explanation does not fit, because the companion reads both numbers and the alarm is on the other one:

- `heapMB`, the field behind `mem.managed_peak_mb`, is Mono's USED size. It equals `monoUsedMB` on the context rows. RESERVED is
  `monoHeapMB`.
- Reserved does hold its high-water mark: 4020 MB to 6589 MB, and it never fell. That is the expected behaviour, and it stays
  about 1 to 1.5 GB above the used floor.
- Used does not hold a high-water mark. It falls about 440 MB at each GC (game 15), and its floor sometimes drops between games.
  Its post-GC floor still climbed from 3024 MB to 5523 MB. Reserved rose because the floor pushed it.

## Evidence

**Not map scale.** Across the 15 games with a GC, game order explains the floor (r² 0.87) and things on the map do not (r² 0.21).
Game 15 has 3117 things and a floor of 4848 MB. Game 2 has 13358 things and a floor of 3024 MB.

| game | save | post-GC floor MB | GCs | reserved MB | things |
|---|---|---:|---:|---:|---:|
| 2 | RM_TestSite_calm_v2 | 3024 | 1 | 4020 | 13358 |
| 7 | RM_TestSite_calm_v2 | 3321 | 2 | 4052 | 13405 |
| 8 | BENCH_r17_midrain | 3971 | 37 | 5337 | 15164 |
| 10 | BENCH_r17_midrain | 4278 | 21 | 5801 | 14471 |
| 13 | RM_live_session_reload | 4457 | 158 | 5986 | 50750 |
| 15 | BENCH_leaf_scenes_20261026 | 4848 | 30 | 6388 | 3117 |
| 17 | (new game) | 5523 | 9 | 6589 | 43959 |

**Not garbage waiting for a GC.** Within a quiet game the floor stays level: game 13 goes 4624 to 4612 MB over 158 GCs, and game
15 goes 4953 to 4857 MB over 30. Most of the climb therefore happens around loads and added maps, not during ticking.

**Same save, same map.** RM_TestSite_calm_v2 loaded repeatedly gives floors of 3024, 3022, 3130, 3258, 3321 MB, or **74 MB per
load**. BENCH_r17_midrain loaded twice gives 3971 then 4278 MB.

**It goes with the list.** The same save on 14 mods (session 871ad37b, 10 loads) gives floors of 681, 663, 697, 694, 744, 765, 790,
801, 786, 753 MB: 8 MB per load, falling back over the last two loads, and that session's verdict is `high_water_only`. So the
game alone, with the companion, shows no comparable ratchet. A rougher scan of other sessions (lowest reading of any kind, not
this reader) gives 14 to 28 MB per load on 14 to 34 mods.

## What this does not settle

- **What is retained.** Used counts what Mono holds as in use, so this record cannot separate objects still reachable (a static
  cache holding an old game) from memory kept alive some other way, such as heap fragmentation or conservative false pointers.
  Filed: `HEAP_BISECT_WHICH_MODS_RETAIN_PER_RELOAD`.
- **That the whole climb is per-load.** The later games differ in save and map count, and one load can add far more than 74 MB
  (game 8 added 650 MB on the first 2-map load). 74 MB per load is the only figure with the map held fixed.
- **The size of the list effect.** Relative to its starting floor the 14-mod control still rises about 1.2% per load against about
  2.4% on the full list, and that is one pair of sessions. Absolute growth is about 9 times larger; the proportional gap is smaller.
- **A real `map_scale` reading from this reader.** e50b27df has only 2 games, which reads UNMEASURED. That verdict is proved on
  synthetic records only.

## Corrections to what was filed

- The item and the `game_health_debugged.json` acknowledgement said 8 game loads. The record holds 17 `game` rows: 11 loaded a
  save and 6 started a new game.
- The item's 2838 MB and 4852 MB are one-minute context readings of a sawtooth about 440 MB deep, so they alias its phase. The
  4852 reading at 21:31Z happens to sit at the bottom of a tooth; the same game read 5298 MB at 21:32Z.

## Reading the alarm

On this list a long bench session of repeated loads can cross the 6144 MB managed line on small maps. Read the floor table with
`heap_ratchet.py` before calling a crossing map scale.
