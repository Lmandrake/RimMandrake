# sc_barrage_perf criterion repair, step 1: the mod-off spikes land inside the event window

Item `RIMMANDRAKE_REPAIR_BARRAGE_FRAME_CRITERION_BASELINE_FAILS_TOO`, neutral fixer, 2026-11-15. Offline, from visit 2's own
per-frame probe rows (no bridge, no game). Refusal record: `refusal.json` (same folder).

**Result: STOP condition met.** With Explosive Knockback OFF, the worst frame inside the barrage-and-chain window is over
50 ms in 3 of 3 runs. Restricting the statistic to the event window does not separate the mod from the scene, so no build
can be shown to meet the bar's words; the bar is the owner's card (text drafted in the steward's note on
`RIMMANDRAKE_ROUTE_EXPLOSIVEKNOCKBACK_VISIT_TWO_FAILURES`). The bar and scenes.json are unchanged.

## How it was measured

- `probe_csv/`: the nine `RM_FrameProbe_*.csv` the three visit-2 runs wrote (selfcheck, off, on per run), copied from the
  game's data folder. One row per rendered frame; probe time = running sum of `ms`.
- Event window 0.9-8.25 s of probe time: the scene's schedule (`RM_KnockbackProof_StageThree.cs` `BarragePerf`: shells at
  stagedTick+60+30i, ignite at +300) and the run journal (last `gas_burst` at stagedTick+476..496, i.e. <= 8.1 s). The mod-on
  runs' `in_air` column (first 0.94-0.96 s, last 7.57-8.02 s) confirms tick time tracks probe time to ~0.06 s.
- `python3 window_analysis.py` reproduces every number below; its output is `window_analysis.out.txt`.

## Numbers (ms)

| run | off: worst all | off: worst in window | on: worst all | on: worst in window |
|---|---|---|---|---|
| first | 151.3 | **151.3** (7.29 s) | 153.9 | 28.9 |
| settled | 144.4 | **54.4** (5.89 s) | 65.3 | 25.8 |
| third | 104.6 | **100.8** (6.87 s; also 88 and 93 during the shells) | 155.2 | **75.3** (1.21 s) |

- The visit's three "barrage worst" figures (153.9 / 65.3 / 155.2) all fall OUTSIDE the window (11.8 / 14.3 / 10.4 s).
- Background: after the window, off and on runs together show 13 frames over 50 ms in 100.6 s = **0.13 per second** (list
  noise: autosave, other mods' rare ticks). A 7.35 s window then holds ~0.95 noise spikes on average, so a single-worst-frame
  bar in that window fails ~60% of runs from noise alone [guess ~70%: Poisson assumption, 13 events]. Whether the in-window
  off spikes are the vanilla barrage's own cost or noise that landed in the window is not separable at this sample size.

## What this means for the drafted card's options

- (a) "the mod adds at most 50 ms to the mod-off worst frame in the same window": on today's rows it passes 3 of 3 (on
  minus off in window: -122, -29, -26 ms), but it compares two noise-dominated single frames.
- (b) minimal list: the tree's tier reason says frame time is meaningful only on the real list and machine.
- (c) shrink the scene: the off in-window spikes include 5.9-7.3 s, the chain's phase, and noise at 0.13/s stays.
- Not on the card, offered for the asker: a statistic robust to one noise frame (e.g. the in-window p99, or the worst frame
  over N repeated runs' medians) keeps "the barrage stays smooth" without the list's own spikes deciding it.

## Step 2: the bar reworded to his answer (2026-11-15, after 7:28 PM PST)

He agreed (OWNER:1794799770273329641, *"1 agree."*) to the 99th-percentile frame inside the 0.9-8.25 s window at most
50 ms. Nearest rank over the unpaused frames whose probe time lies in the window; a probe that stops before 8.25 s fails;
the worst frame is still reported. Decider: `KbFrameStats.WithinBudget` (`Source/RM_KnockbackMath.cs`), fed the window by
`RM_FrameProbe.Stop(BarrageWindowLoS, BarrageWindowHiS)`. Test: `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_barrage_p99.py`
runs the production decider on these nine files and four planted ones and checks it against a Python reading of the same rows.

| run | off: p99 in window | on: p99 in window | on: verdict |
|---|---|---|---|
| first | 15.0 | 21.6 | PASS |
| settled | 11.4 | 20.8 | PASS |
| third | 24.7 | 17.8 | PASS |

Planted, from the settled mod-on run: 1.5 s of 75 ms frames in the window FAIL (p99 75.0); 2 s of 55 ms frames FAIL (p99
55.0); one 200 ms frame PASS (p99 21.5, worst 200.0); the probe cut at 6 s FAIL ("before the window closed").

- **What p99 gives up:** it counts frames, not time. The top 1% of the window's frames (4 at ~60 fps, 9 at ~120 fps) never
  decide it, so up to that many separate long hitches pass. A stretch of slow frames longer than 1% of the window fails.
- **Applied:** `tree_sheet_rewording.patch` (this folder) carries the leaf's and the sheet's words; it was applied and the tree
  re-certified on his "1 agree." at `3aa7e5c15d`/`fab7999d8f` (`RECERTIFY.md`).
- **Live acceptance: UNRUN.** `python.exe src\RimMandrake\ExplosiveKnockback\knockback_runner.py --scenes frame_probe_selfcheck,barrage_perf_off,barrage_perf --ticks 0 --real-seconds 25`
  on the proof build and the owner's full list on Archmagi.
