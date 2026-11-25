## spec
Design: `design/RimMandrake/tickburst_2026-11-06/final.md`. It was reframed after a skeptical GPT review
(`gpt_review.md` beside it) of `expansion.md`.

### summary
The premise "bridge stepping is one tick per frame" holds only for `rimworld/step_game_ticks`. `jawa/safe_advance`
already runs many ticks per frame: chunks of at most 60 ticks, repeated inside a 40 ms frame budget
(`JawaBenchVitals.cs:719-730`). This item does not build a new stepper. It **measures** safe_advance's ticks/s against
`step_game_ticks` and vanilla's loop. It then **proves**, on three existing proofs, that safe_advance gives the same
verdicts as unpaused normal-speed play. Finally it **moves** those proofs' direct `step_game_ticks` calls onto
safe_advance, only where the verdicts stay equal. Per-tick stop checks belong to `ADVANCEUNTIL_WIRE_PER_TICK_STOP`.
Flyers are excluded.

### acceptance (each is an observation)
1. `src/RimMandrake/Utils/tickburst_bench.py --mock` passes its selftest. Live, a 60-tick sanity probe moves ticksGame
   by exactly 60 in arms A (`step_game_ticks`), B (safe_advance at 40 ms) and C (at 200 ms). Arm R (unpaused Normal)
   is seen to reach its target tick.
2. A throughput JSON for the minimal list exists under `D:\ClaudeWork\rimmandrake\tickburst\minimal\`. It gives
   ticks/s for arms A, B at 40 and 100 ms, C, U and U+ (3 repeats each), a per-frame tick histogram, p99 and worst
   frame ms, round trips, and `UltraSpeedBoost` as read back for each arm.
3. The same JSON exists for the owner's full list under `...\tickburst\full\`, taken on an already-scheduled load. If
   no such load happens, the row is marked OWED with the reason.
4. A guard audit table covers G1-G11, each with a file:line and a sim or visual class. Its `*Update` override census
   lists `CompDissolutionEffect_Goodwill` and `CompDissolutionEffect_Pollution`; this is the sanity probe that the
   census can see.
5. A bounds file for continuous checkpoints is committed at an earlier sha than any equivalence result.
6. Equivalence runs for FlowWorks v2 `P_pits`, `lines_proof.py` and `lp_glowtank_seed_sow.py` (midday and dusk). Each
   proof runs under R, A, B and C: 5 fixture reloads plus 1 fresh process per arm. The results list per-row verdicts,
   discrete checkpoints (exact), continuous checkpoints (within bounds), NaN count and ticking-exception count.
   `P_forced` / `FLYER_LAND_TICKS` are absent.
7. An N-per-frame sweep {1, 30, 60, 61, max} on LINES and glowtank-at-dusk is recorded, using the new
   `perFrameTickCap`.
8. `safe_advance` reports `perFrameTickCap` and `stepMs`. Both have a selftest and are read back live.
9. Every proof whose B arm matched R in all trials now steps through `_BridgeBase.ticks` / `clockgate.advance_chunk`,
   and its own selftest passes. Every proof that did not match keeps `step_game_ticks` and has a filed rimflow item or
   lesson. That record holds the first divergent checkpoint, both digests and the guard (G#) it implicates.
10. Every result row carries provenance: mod-list hash, fixture hash, DLL hashes, arm, N per frame, camera and
    autosave state.

### separate items proposed (namecheck OK 2026-11-06, not filed)
`BATCHREADS_BUILD_ROUND_TRIP_CUT`, `SHOTSETTLE_BUILD_PAUSED_BARRIER`, `SCENERUN_MIGRATE_OFF_UNPAUSED_PLAY`,
`STEPCALLS_MIGRATE_WHERE_VERDICTS_HOLD`. See final.md §5.
