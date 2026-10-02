# Shared-tree leftovers triage — 2026-10-02

Owner ruling (card 2026-10-02 01:20): *"Sort and land the safe ones"*.

Source: snapshot tag `archive/shared-tree-dirty-20261002T075419Z` (`0d9d474540a6`), parent B = `b246bc43797b`;
plus `archive/shared-tree/e55ff18da0fa` and `archive/shared-tree/4e2b103f3d44`. Tar-only big files from
`D:\Luke\dev\_rm_shared_tree_leftovers_2026-10\leftovers.manifest.tsv`.

## Method

Blob census (python, `git ls-tree -r` of snapshot S, B and origin/main at `4bfad6d29`) over every path where
S ≠ B: **already-upstream** if origin == S; **generated** by path class; **candidate** if origin == B
(untouched upstream), then read by hand; otherwise **conflict**. Sanity probe:
`src/RimMandrake/Abyss/About/About.xml` (in S, classed already-upstream). Census total 3,479 = 3,184 stored +
295 deletions, matching the snapshot commit.

## Census

| class | paths |
|---|---|
| already-upstream (origin blob == snapshot blob) | 1,028 (462 add, 294 del, 272 mod) |
| generated / junk | 2,434 |
| conflict (origin changed path since B) | 12 |
| doubtful | 1 |
| **landed** | **4** |
| total | 3,479 |

The two `archive/shared-tree/*` commits are **fully upstream in content**: every file is either byte-identical
on origin/main (`e55ff18da` landed as `f0e26f43a`) or a shard/inbox/runner path whose added lines are all
present upstream (0 absent lines). Nothing to land.

## Landed

| sha | paths |
|---|---|
| `dcd68699b` | `design/Jawa/worldbuilding/biomes/rosters/the_propane_lakes.json`, `design/Jawa/worldbuilding/biomes/terminal_seas_cast_proposal_2026-09-25.md`, `design/RimMandrake/sea_shore_mutator_spec.md`, `design/RimUtinni/vanilla_beast_excision_census.md` — `RM_PropaneLake`→`RM_TheChill` rename follow-through; src on origin has 0 `RM_PropaneLake`, 25 files with `RM_TheChill` |

## Conflict (origin changed the path since B)

Not landed. "absent" = lines the snapshot added that origin/main does not contain.

| path | absent | reading |
|---|---|---|
| `CLAUDE.md` | 30 | shared-tree-era `./publish` block; superseded by the seat-clone workflow — obsolete |
| `publish`, `src/RimMandrake/Utils/publish.py`, `src/RimMandrake/Utils/selftest_publish.py` | 1 / 494 / 94 | old shared-tree publish tool; upstream has its own version — obsolete |
| `design/RimMandrake/sea_dive_maps_spec.md` | 3 | same TheChill rename; upstream still has 1 `RM_PropaneLake` line — worth a hand fix |
| `src/RimMandrake/Utils/modcheck/runner.py` | 1 | `ensure_playing_map(dry_run, _client, _starter)` signature variant |
| `src/RimMandrake/Utils/modcheck/selftest.py` | 2 | tests for that `_starter` variant |
| `src/RimMandrake/CreatureBehaviors/Source/SelfTest/Program.cs` | 1 | `Assembly.LoadFrom(dll)` line (no DLL involved) |
| `infrastructure/state/LESSONS_INBOX.md`, `src/RimMandrake/Utils/loadsweep/biome_load_proof.sh`, `src/RimMandrake/Utils/selftest_deployed_biome_refs.py` | 0 | everything added is already upstream |
| `infrastructure/state/items/NORTHSTAR_MOTION_FRAMES_1.md` | deletion | upstream still has the item; its liveness is a rimflow question |

## Doubtful

| path | why |
|---|---|
| `src/RimMandrake/Utils/firehawk_flight_probe.py` | its own docstring says "Throwaway probe … Not committed" |

## Generated / junk (counts only)

| class | paths |
|---|---|
| `infrastructure/artpipe/{done,failed,_withdrawn}` (state now outside git, `D:\Luke\dev\_artpipe`) | 1,680 |
| `Transient/` | 695 |
| `deployed/config/ModsConfig.before-*` backups | 32 |
| `infrastructure/state/modlists/` backups | 9 |
| ledger shards | 3 (BENCH/FOUNDRY events all upstream; OWNER has 6 stale 2026-09-29 game/bridge stamps not upstream) |
| queue views, dashboards, codebase_health, artpipe registry/throughput/logs, cherrypicker preswap, `done.flag` | rest |

## Tar-only files > 5 MB (listed, not landed)

18 files, 431.6 MB, all junk: 17 × 24.9 MB desktop screenshots `Transient/{scald1-3,scald5,rw_state1-3,menu1-7,game_state_check,game_state_check2-3}.bmp`
and `Transient/world_label_sizes/CANONICAL_ASHKARR_START_2026-09-12.biome.equirect.svg` (8.6 MB).

## For the owner

- Nothing of substance was trapped: 4 doc fixes landed; both archived commits were already upstream.
- `modcheck/runner.py` `ensure_playing_map(_starter=…)` variant (+2 selftests) was never landed — keep or drop?
- The tar (`D:\Luke\dev\_rm_shared_tree_leftovers_2026-10\leftovers.tar`) holds nothing worth keeping beyond the git tag; safe to delete on your word.
