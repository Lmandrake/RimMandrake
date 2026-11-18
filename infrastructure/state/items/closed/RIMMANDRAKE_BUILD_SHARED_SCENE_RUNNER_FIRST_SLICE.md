## spec
PRIORITIZED by the owner (pick 14, 2026-11-12: "14 (prioritize this)", OWNER.jsonl tsn 1794524114165680240).

### What it is
One shared in-game C# scene runner: "fast-testing step 8", from `design/RimMandrake/fast_testing_2026-11-05/scored.md` §Sequenced
plan item 8 and step 5 of `design/RimMandrake/live_test_speed_assessment_2026-11-12.md` §4. Each scene stages, ticks in
process (no frame wait) and judges, and every scene returns the same PASS / FAIL / UNMEASURED row table. A whole suite is one
bridge call. It lives behind a build switch so it does not ship in the player's mod. Precedent in our tree: the
`static_call` proof pattern, `RM_FirefoamAimProof` and `RM_WebworkProof.cs`. About 110 proof C# files exist with no common shape.

### What it would speed up (measured numbers, live_test_speed_assessment §2)
- Ticks are 81.8% of in-call bridge time (193 of 236 min on 2026-11-11/12; `step_game_ticks` 603 calls, 19 s each).
  A 2,500-tick step takes 41.67 s, which is 60 ticks a second (one per frame). The game's own cost is 0.6 to 1.8 ms a tick,
  so its ceiling is 900 ticks a second on a small list, 555 to 613 on the full list and 1,673 with the cap off.
- FlowWorks `pit_exposure_live.py`: 465 to 529 s a run, about 407 s of it in 10 tick calls.
- Explosive Knockback `storeroom_pit_proof.py`: 31 s, 15 s of it in 36 calls of 25 ticks. Staging and the verdict
  through in-game C# cost 0.5 s, which is the shape this runner generalises.
- The assessment's estimate (50% confidence) is 2 to 4 times beyond the tick-burst step for long scenes. Several scenes
  per load also removes about 140 s of fixed cost per job (testq: median 89 s copy plus 51 s fingerprint).

### First buildable slice
Lift the `RM_FirefoamAimProof` / Webwork pattern into one `[RMTest]` attribute plus a runner. The runner takes a scene
list, runs each scene on its own plot in one call and returns a row table (scene, check, status, measured, expected).
Port ONE suite: Explosive Knockback `storeroom_pit_proof.py`, already C#-judged, or the FlowWorks pit exposure, the
tick-bound one. Prove it by recording that suite's wall time and bridge-call count before and after, with every
verdict row identical.

### Guard
This item is about the shape, not the arithmetic. A scene that reads the same state the mod writes shares the mod's
blind spots (§3 (c)), so each ported suite keeps at least one row read from outside the mod.
