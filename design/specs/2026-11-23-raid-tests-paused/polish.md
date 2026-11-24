# Polish: raid tests paused
- The harness's own proofs that fire a raid (`modcheck/live_queue/abort_proof.py`, `map_awareness_proof.py`,
  `bridgetools/prove_three_tools.py`, `prove_vitals_governor.py`) are refused at that row. Their item goes in `allow` when one
  of them must run.
- `scenes.json` of Explosive Knockback still words the acts of `sc_walk_raid` as a raid (locked text; the test table's
  `sc_walk_blasts` is what runs). Reword it when that file next opens.
- `Webwork` (a siege proof in C#) and `UtinniPatches/prove_night_horrors_live.py` stage raids from scripts no pipeline run starts.
- Codex review 2026-11-24, not significant in ordinary operation (only_paused_scene_blocks_stage_six, `maturation.py:5229`): Put a version whose sole valid Stage 6 check is a tagged raid scene into in-game acceptance while the pause is on. The next-step reader pauses the whole mod, and even a visit with a valid save and all other evidence complete reads `not_met` because the filtered check list is empty.
- Codex review 2026-11-24, not significant in ordinary operation (full_sweep_admits_only_paused_chains, `pipeline_admit.py:139`): Submit a fresh `Visibility --full --purpose sweep` job on a published SHA with the pause on and no owner hold. Every chain in the suite is paused, yet the job can enter the queue because the selector names the suite as a whole.
- Codex review 2026-11-24, not significant in ordinary operation (census_misses_live_raid_script, `raid_pause.py:207`): Run the read-only census. It omits `map_awareness_proof.py`, whose documented A9 proof fires `RaidEnemy` by passing a dictionary to `jawa/fire_incident`.
- Codex review 2026-11-24, not significant in ordinary operation (driver_brief_pause_listing_untested, `selftest_raid_pause.py:114`): Remove the block that appends paused scenes to the generated driver brief. A visit with a tagged `c1` then loses the brief's named pause notice, and the same-name test still passes because it checks the helper and a different renderer.
- Codex review 2026-11-24, not significant in ordinary operation (walk_diagnostic_says_paused_after_lift, `maturation.py:3988`): Lift the pause before an outstanding raid scene gains a standing pass, then read a walk brief that omits its bar. The refusal correctly names the bar but still describes the scene as PAUSED.
