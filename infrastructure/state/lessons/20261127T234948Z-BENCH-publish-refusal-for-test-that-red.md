A ./publish refusal for a test that is red on origin/main too often means your clone's base is stale and another run has already fixed it. Run 'git pull --rebase origin main' and publish again before you fix the test yourself. Twice in one run (steve_lane_sweep c90669d5c5, lane_sweep), my own fix then conflicted with the fix on main. A seat clone refuses 'git reset --hard': undo your own commit with 'reset --soft', then 'restore --staged' and 'checkout --' on your paths.
item: RIMMANDRAKE_FINISH_PREPARE_FIRST_LOOK_MATRIX_UNBUILT_PARTS
home: skills/clone-landing-commits
