# WB-item-RIMMANDRAKE-READ-FIX-6F18007021-WITH-FRESH-EYES-20261127-091425

One member, `RIMMANDRAKE_READ_FIX_6F18007021_WITH_FRESH_EYES` (fresh read of `src/RimMandrake/rimflow/game_lock.py` at 6f180070217b). Done.

- Problem (the-flight-guard-refuses-creature-flyers-only, not kept): "drake" inside RIMMANDRAKE kept every RIMMANDRAKE_ flight-word item ID refused; "preflight" (a documented take) read as flight; "a drake takes off" admitted. Red 5 FAIL on the parent; fixed f9c76aae2023.
- Polish: run renews its heartbeat (e9ed23a32af4, polish.md line removed); gravship admission cuts showing/following/combat (3d3916311eee).
- Check repairs, both readings: selftest_testpilot_route phrase (3b1efdbb50aa); selftest_owner_hold pinned RM_HOST=archmagi (58dff35dbfd3; 21 FAIL on SteveDesktop before, 0 after, 5 with a planted OWNER-gate bypass).
- game_lock.py flagged (7c5ce4e1e4fe). `fresh_reader.py holds` exit 0.
