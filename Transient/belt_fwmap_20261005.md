# FlowWorks review MAP — belt notes 2026-10-05

## status
- 20:37 offline done: review_map.py --plan ok (51 gallery stations + 34 visuals + S0/M/F), selftests green.
- coordinator: visuals first (owner: "I need to see it in the game"); save as soon as visuals verified.

## offline
- src/RimMandrake/FlowWorks/review_map.py (+ selftest_review_map.py); shared helper Utils/modcheck/reviewmap.py (+ selftest);
  GSS save_review_map.py now uses reviewmap.save_keeper.
- key sheet at FlowWorks/northstar/review/map/ (under northstar/: outside the mod hash, already DEPLOY_HOLD'd).
- NOTE: review_map.py, review_map_visuals.py, review_map_stations_visuals.json sit at the FlowWorks root, so they ARE in
  the FlowWorks mod hash (modcheck status._EXCLUDED_BASENAMES has only human_review.py). Not changed here (would restale
  any record mid-proof); decide with the northstar agent.

## live
- bridge held by the northstar agent; waiting.

## owed
- 20:44 bridge taken; ModsConfig (50 mods) backed up Transient/ModsConfig_before_fwmap.xml; deployed FlowWorks from origin/main export; tier flowworks
- 20:49 visuals built + verified 34/34 (state reads: D, F, scorch, colonist per plot); keeper saved RM_fw_review_20261005.rws (1 new file, 0 changed). Building the gallery next.
- 21:08 gallery built + verified 51/51 (dug cells and depths, buildings/spawns present, held pawns present); two
  harness fixes on the way (Boar -> WildBoar; RM_FordStones is a TerrainDef, painted). Labels re-laid: title + status above
  each station, the what-to-notice line below in tiny print (the long sub line ran into neighbours). Saved keeper
  RM_fw_review_20261005_b.rws (full map; 1 new file, 0 changed). ModsConfig restored byte-for-byte; bridge released; game
  left running on the review map.
- owed: the bridge take/release ledger lines sit in the shared clone's FOUNDRY.jsonl (diverged clone; the ledger hook blocks
  rebuilding the shard outside rimflow) -- they ride whoever reconciles the clone.
- note: run_selftests 187/188; the 1 FAIL is selftest_ledger_lint 'real ledger clean (worktree vs origin/main)' = the shared
  clone's diverged ledger, not this work.
