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
