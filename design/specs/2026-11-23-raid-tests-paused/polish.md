# Polish: raid tests paused
- The harness's own proofs that fire a raid (`modcheck/live_queue/abort_proof.py`, `map_awareness_proof.py`,
  `bridgetools/prove_three_tools.py`, `prove_vitals_governor.py`) are refused at that row. Their item goes in `allow` when one
  of them must run.
- `scenes.json` of Explosive Knockback still words the acts of `sc_walk_raid` as a raid (locked text; the test table's
  `sc_walk_blasts` is what runs). Reword it when that file next opens.
- `Webwork` (a siege proof in C#) and `UtinniPatches/prove_night_horrors_live.py` stage raids from scripts no pipeline run starts.
