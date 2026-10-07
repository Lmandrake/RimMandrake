# Gimme Some Slack offline fuzz - Approach B (2026-10-06)

Seeded random action-sequence fuzzing over the Verse-free GSS core, no game. Template: `design/RimMandrake/flowworks_offline_kernel_B.md`.

`src/RimMandrake/GimmeSomeSlack/Source/SelfTest/GssFuzz.cs`, called from `Program.cs` after the oracle and lane checks, so
`python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py` (and `run_selftests.py`) run it on every commit. Everything is a pure function
of the seed (`CordRng`); a failing case is shrunk by delta debugging and printed as `family seed N: message | actions`.

Knobs (forwarded by the wrapper): `--fuzz-scale F` (multiplies every case count, `0` skips), `--fuzz-only cords|hose|trail|aerial`
(runs the fuzz first and alone, so a planted bug that breaks the oracle checks cannot hide it), `--fuzz-seed N` (replay one seed).

## Families and invariants

| family | a case is | invariants (asserted) |
|---|---|---|
| cords | random 14-24 x 10-18 map (walls/rock/water, doors, trees, 2-5 machines, per-scene options) then 3-24 actions: build, remove, break, reconnect, wall, rock, water, clear, door, charge, run | **incremental == fresh**: one `CordBuilder` carried through every step equals a fresh builder on the same world (full digest of keys, strands, decals, ends), every 3rd case every step; **no edge between different power nets** (nets = 4-connected conduit; machines may sit on several); **no NaN/inf** strand, decal, end, length; **strand length within the declared limit** (below); **same seed -> same bytes** (two fresh builds); **machine-list order is not a design input** (reversed list, same cords); **an unrelated edit never reshuffles a cord** (a 3-cell run 5+ cells from everything leaves every existing piece identical, design 8.2.5) |
| hose | random 18-40 x 14-30 map with wall/water blobs, 2x2 (nozzled) or 1x1 reel, random target, hose length 10-60, min bend 0.6-2.0; each case laid with the reel's outlet and, for 2x2, without | install verdict (`CheckInstall`) agrees with an independent unbounded route read (fits <=> installs); `Lay` deterministic; ends attached to mouth and target; finite; flat and plump never through a wall; free-mode never gross over the hose, plump never much longer than flat, bend radius beyond the outlet blend never under a tenth of min bend |
| trail | `HoseCarryMachine` on a 36 x 24 walled map, 20-160 events: grab, step (legal 8-way), set down, interrupt, pick up, wind, wind by x, wind interrupt, replan, reel gone, dev lay, dev reel in | the machine's own `Invariant()` after every step; pulled hose starts at the mouth, ends at the last cell, is clear of walls; no cell twice on the trail; stepping never exceeds the hose; winding never lengthens, `Clip` leaves exactly `length - wound`; an interrupted wind keeps at most `length - wound` |
| aerial | 3-14 anchors, 3-14 range, 5-60 actions: link, unlink, remove, kill, auto-link, auto-link selected | links symmetric, no self, no duplicates, `<= MaxLinks`, within range, same faction; `PlanRemoval` reseeds exactly the partners and drops a cord only for a killed anchor's UP spans; `AutoLinkPick` is the nearest (lowest id on a tie); `MinimumSpanningLinks` is in range, in degree, acyclic; span curve finite, exact ends, never shorter than its chord; sway zero at both insulators and bounded by `amp x min(wind, 1.5)`; shadow finite |

**Declared cord length limit.** `CordLayer.AddLoops` splices a loop or heap only while the cord stays within 1.25 x the slack target
(at most `PathLen + MaxExtra`); the broad lateral excursions are **not** charged to that budget (each is a Gaussian bump of amplitude
<= `Cap` x 1.1, extra arc <= its total variation, `round(L / 2.6)` of them). Limit asserted:
`1.25 (PathLen + MaxExtra) + nb x 2 x Cap x 1.1 + 3` (+4 over `LongRun`). Closest a strand came: 3 cells under.

**Negative controls** (always on, in the same run): a two-net graph reads clean; an edge across two nets, a NaN point, a strand far over
its limit are each flagged; the digest tells a 0.01-cell nudge apart; the shrinker reduces 8 actions to the 2 that matter.

## Known gaps (design invariants the shipped code does not hold; tallied with a shrunk reproducer, not failing the run)

Measured at the default case counts, 2026-10-06. Reproduce with `--fuzz-only hose --fuzz-seed N` (add `--fuzz-scale` to sweep).

| id | what | rate | first reproducer |
|---|---|---|---|
| G3 | bend beyond the lead-out under 95% of min bend (marginal, walled corridors) | 1/1249 free | seed 1164 (9 walls) 0.65 < 1.2 |
| G4 | plump hose longer than flat by more than 1% | 11/1153 outlet, 1/1249 free | seed 146: 9.79 vs 8.18 (outlet); seed 253 (free) |
| C1 | **incremental != fresh beyond the corridor margin**: the per-edge cache re-plans a cord only when a cell inside its strands' bounding box + 3 changes walkability, but the sprawl probes up to `Cap` (2.6) cells either side of the *planned* path. A wall or rock 4-6 cells from a cord leaves the cached cord standing where a fresh build lays it differently | 2/1200 cases | seed 790: `Build(6,6) Wall(5,10)` (junction:5,6 - terminal:6,6); seed 967: `Rock(10,3)` |


**Fixed 2026-10-06 and now ASSERTED (fail the run), no longer gaps:**
- **G1 / GPT B3** (laid hose longer than the hose): `HoseMath.LayOn` retries an overlong lay with no slack and otherwise refuses it
  ("route too long (the laid hose, lead-out included, ...)"); the reel retracts with that reason.
- **G2 / GPT B5** (tight bend at the nozzle). **Owner decision by question card 2026-10-06: straight lead-out.** The hose leaves the
  nozzle dead straight for `HoseMath.LeadOutStraight` = 1.6 + 0.5 x min bend radius, then joins the laid hose by the shortest
  curve never under the minimum radius (a Dubins path, every word tried so one that turns away from the reel body is found). A
  target with no room for that is refused ("no room for the straight lead-out from the nozzle"), never laid kinked or without the
  lead-out. The old cause was `StraightenStart` dragging the first 1.6 + 2R cells onto the outlet line by position interpolation
  (951/965 tight bends sat in that blend). Fuzz now: 0 lead-out bends under 95% of the minimum over 1,153 outlet lays; 196/1,445
  outlet cases are refused for no lead-out room (cramped random worlds: walls or the map edge within one turn of the nozzle).
- **G6 / GPT B2** (fitting route refused for a cheaper longer one): `CheckInstall` judges the SHORTEST route (`RouteCells(..., costs:
  false)`); `CostVsLengthProbe` asserts the 37.4-cell water corridor is allowed for a 40-cell hose.

C1 is a trade-off, not an oversight: raising the margin to 7 clears every case but breaks the shipped check "unrelated edit re-plans only
the touched edge" (planned 3, reused 11), so it was not changed. Whether stale-until-next-edit is acceptable is a design call.

**Resolved 2026-10-06 by renaming the setting (owner decision by question card, A12/B15).** The setting now called `loopBudget`
("Loop budget", `LayParams.MaxExtra`, 2-40) caps the cord spent on loops and heaps, not a cord's length: a cord with `MaxExtra` 2 lays
2-5x its path because the excursions are outside the budget (seed 141: 1-cell lead to a lamp, `MaxExtra` 2, lays 10.9 cells). The
assertion above follows the code, not the setting's name.

## Defect found and fixed

**Wall-terminal / stub look was missing from the per-edge cache key** (`Core/CordBuilder.cs`). Removing a conduit cell behind a device stub
(seed 81 `Remove(4,4)`, seed 115 `Remove(8,1)`) turned that stub's buried run into a dead end inside the wall (a *wall terminal*, extra loose
wire and end) but the key had only the node type, so the cached piece kept the old look until something else invalidated it: incremental
!= fresh. The key now carries the node's wall-terminal flag, gap flag, junction class, open side, and stub direction and face. Both seeds pass
after the fix; with the fix reverted they fail again, shrunk to the one action.

## Planted-bug probes (each planted in production source, run, removed; `git diff` shows none left)

| plant | caught by | shrunk reproducer |
|---|---|---|
| (the real bug above) cache key without wall terminal | cords, 2/120 | `seed 81: Remove(4,4)`, `seed 115: Remove(8,1)` |
| `CordGraph` links 8-neighbours instead of 4 | cords, 38/120 | `seed 5: Build(7,10)` |
| `CheckInstall` without the "route too long" test | hose, 4/827 | `seed 204`: route needs 17.59 > 17.01, install allowed |
| `HoseTrail.Step` length limit x1.5 | trail, 8/1500 | `seed 95: DevLay(n10) PickUp Step(1,-1) Step(1,-1)` |
| `AerialMath.CanLink` `>=` -> `>` on max links | aerial, 326/5000 | `seed 9: Auto(105,106) Link(105,100)` (anchor 105 has 2 links, max 1) |

## Timing (Archmagi, Release build, 2026-10-06)

| family | cases | steps | seconds |
|---|---|---|---|
| cords (every build also rebuilt fresh on every 3rd case) | 120 | 3,057 | 7.65 |
| hose (1500 seeds, outlet + free for 2x2 reels) | 2,798 | 8,200 | 4.71 |
| trail | 1,500 | 133,643 | 0.27 |
| aerial | 5,000 | 165,292 | 0.39 |
| **all fuzz** | **9,418** | **310,192** | **13-14** |

Cords dominate: ~2.5 ms per build, ~25 ms per case. `--fuzz-scale 4` runs 1,200 cords cases in 74 s.

## What this does not cover

The adapter that snapshots a real map into `CordWorld` (linkGrid, thingGrid, pathing) and the render path are not in the offline project;
the fuzz's map model is its own. Live check of the adapter is still owed to a bridge session.
