## spec
Gimme Some Slack's `T_PROOF_LEAVES` is red (MEASURED 2026-11-16 evening Pacific, on origin/main 6508babf91 plus live-end work that does not touch the proof rows): four proof rows cite no leaf (`B7_sway_cpu_two_frame`, `B7b_sway_shader_path`, `B7c_floor_ripple`, `B12_shader_sway_far_zoom_drawn_once`) and two map rows are in no proof line (`B7_ground_cords_never_sway`, `R3b_sway_looks_each_draw`). All six are wind-sway rows, left behind by the sway cleanup (`RIMMANDRAKE_CLEAN_SLACK_SWAY_POLE_WIRES_ONLY_NOT_CONDUIT`: wind sway is for power-pole wires only). Give each row its leaf, or retire the row with the sway it proved.

## refs
file: src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_proof_leaves.py

## verify
`python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_proof_leaves.py` exits 0 with `RED: 0`. Watched failing at filing: `RED: 6` (the six rows above). Expected pass count: every row of the script's own listing, 0 red.

## criteria
- The six rows either cite a leaf that exists or are removed with the sway code they proved.
- No proof row for a behaviour still in the mod is removed.
