# PLAY against STEP: the result of `scene.py compare`

Item `RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED`. Written by `scene_compare.py`; every run's trace is in
`<this page's name>_samples.jsonl` beside it. Wall time is never compared; ticks per second are measured from the driver.

- plan: `\\wsl.localhost\Ubuntu\home\mandrake\rm\relentless\clones\RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED.det\src\RimMandrake\Utils\scene_compare_plans\colony_drift_rand.py` (sha 06d31dd1b34131c9)
- start: save `rm_fixture_play_vs_step` (sha256 767681e80d68c5f33263b259d7247ad336e5ec9c5a3c2eb66883eafae7c9f0ad), tick 2, random state 1079694051294232 written back before every run
- game: ArchBig; mod list fingerprint sha256:87ce560b1c402c3771e4def40bcd888b3059e747793bc96690dda09f96c5596a

| run | arm | speed | refused | verdict | first difference | ticks | wall s | ticks/s |
|---|---|---|---|---|---|---|---|---|
| 1 | play1 | Normal |  | REFERENCE |  | 300 | 6.3 | 47 |
| 2 | play1 | Normal |  | DIVERGED | track static:Verse.Rand.iterations at tick 3 | 300 | 6.3 | 48 |
| 3 | play1 | Normal |  | DIVERGED | track static:Verse.Rand.iterations at tick 22 | 300 | 6.5 | 46 |
| 4 | step | Step |  | DIVERGED | track static:Verse.Rand.iterations at tick 1 | 300 | 1.6 | 188 |
| 5 | step | Step |  | DIVERGED | track static:Verse.Rand.iterations at tick 22 | 300 | 1.6 | 185 |
| 6 | step | Step |  | DIVERGED | track static:Verse.Rand.iterations at tick 4 | 300 | 1.5 | 195 |

## Each arm

- **play1**: first diverging tick 3 (track static:Verse.Rand.iterations): reference ('ok', 251745), arm ('ok', 251757); ticks/s min 46, mean 47, max 48 (13-mod list); key `8e1b0efd947eb3f7`
- **step**: first diverging tick 1 (track static:Verse.Rand.iterations): reference ('ok', 251535), arm ('ok', 251541); ticks/s min 185, mean 189, max 195 (13-mod list); key `ec5558140087a8f9`

- full mod list: UNMEASURED: no full-list load was scheduled to ride (full-list testing is retired until integration)

arms that count for a bar: none
