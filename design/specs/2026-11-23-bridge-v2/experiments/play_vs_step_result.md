# PLAY against STEP: the result of `scene.py compare`

Item `RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED`. Written by `scene_compare.py`; every run's trace is in
`<this page's name>_samples.jsonl` beside it. Wall time is never compared; ticks per second are measured from the driver.

- plan: `src/RimMandrake/Utils/scene_compare_plans/colony_drift.py` (sha 508dc3fe38f72d99)
- start: save `rm_fixture_play_vs_step` (sha256 767681e80d68c5f33263b259d7247ad336e5ec9c5a3c2eb66883eafae7c9f0ad), tick 2, random state 1174067367689240 written back before every run
- game: ArchBig; mod list fingerprint sha256:87ce560b1c402c3771e4def40bcd888b3059e747793bc96690dda09f96c5596a

| run | arm | speed | refused | verdict | first difference | ticks | wall s | ticks/s |
|---|---|---|---|---|---|---|---|---|
| 1 | play1 | Normal |  | REFERENCE |  | 1200 | 21.1 | 57 |
| 2 | play1 | Normal |  | DIVERGED | track Human196.Position at tick 101 | 1200 | 21.0 | 57 |
| 3 | play1 | Normal |  | DIVERGED | track Human199.Position at tick 101 | 1200 | 21.4 | 56 |
| 4 | play1 | Normal |  | DIVERGED | track Human199.Position at tick 51 | 1200 | 21.3 | 56 |
| 5 | play1 | Normal |  | DIVERGED | track Human199.Position at tick 101 | 769 | 74.7 | 10 |
| 6 | play3 | Superfast |  | DIVERGED | track Human196.Position at tick 101 | 1200 | 4.6 | 260 |
| 7 | play3 | Superfast |  | DIVERGED | track Human196.Position at tick 101 | 1069 | 64.9 | 16 |
| 8 | play3 | Superfast |  | DIVERGED | track Human199.Position at tick 51 | 1200 | 4.7 | 256 |
| 9 | play3 | Superfast |  | DIVERGED | track Human199.Position at tick 51 | 1200 | 4.7 | 256 |
| 10 | play3 | Superfast |  | DIVERGED | track Human196.Position at tick 101 | 1200 | 4.8 | 251 |
| 11 | ultra | Ultrafast |  | DIVERGED | track Human199.Position at tick 51 | 1200 | 2.3 | 512 |
| 12 | ultra | Ultrafast |  | DIVERGED | track Human196.Position at tick 101 | 1200 | 2.4 | 498 |
| 13 | ultra | Ultrafast |  | DIVERGED | track Human199.Position at tick 51 | 1200 | 2.2 | 535 |
| 14 | ultra | Ultrafast |  | DIVERGED | track Human199.Position at tick 51 | 1200 | 2.6 | 460 |
| 15 | ultra | Ultrafast |  | DIVERGED | track Human196.Position at tick 51 | 1200 | 2.3 | 523 |
| 16 | step | Step |  | DIVERGED | track Human196.Position at tick 101 | 1200 | 2.7 | 448 |
| 17 | step | Step |  | DIVERGED | track Human199.Position at tick 201 | 1200 | 2.7 | 437 |
| 18 | step | Step |  | DIVERGED | track Human196.Position at tick 101 | 1200 | 2.4 | 501 |
| 19 | step | Step |  | DIVERGED | track Human199.Position at tick 51 | 1200 | 2.4 | 506 |
| 20 | step | Step |  | DIVERGED | track Human196.Position at tick 51 | 1200 | 2.4 | 509 |

## Each arm

- **play1**: against the reference: the reference is not repeatable: 4 of its 4 other runs diverge from run 1, first on tick 101 (track Human196.Position): run 1 ('ok', '108,125'), other ('ok', '109,125'). Repeatability: 0 of 10 pairs of its own runs equal; its own runs first differ on ticks [51, 101, 151]. Ticks/s min 10, mean 47, max 57 (26 active mods); key `27b4bcccee37dbe6`
- **play3**: against the reference: first diverging tick 101 (track Human196.Position): reference ('ok', '108,125'), arm ('ok', '110,123'). Repeatability: 0 of 10 pairs of its own runs equal; its own runs first differ on ticks [51, 101]. Ticks/s min 16, mean 208, max 260 (26 active mods); key `9d3841a2076baa0c`
- **ultra**: against the reference: first diverging tick 51 (track Human199.Position): reference ('ok', '117,131'), arm ('ok', '119,131'). Repeatability: 0 of 10 pairs of its own runs equal; its own runs first differ on ticks [51, 301]. Ticks/s min 460, mean 506, max 535 (26 active mods); key `2acf8a1e3c9234aa`
- **step**: against the reference: first diverging tick 101 (track Human196.Position): reference ('ok', '108,125'), arm ('ok', '109,125'). Repeatability: 0 of 10 pairs of its own runs equal; its own runs first differ on ticks [51, 101]. Ticks/s min 437, mean 480, max 509 (26 active mods); key `ab3102218a62b9af`

- full mod list: UNMEASURED: no full-list load was scheduled to ride (full-list testing is retired until integration)

arms that count for a bar: play1 (the reference)
