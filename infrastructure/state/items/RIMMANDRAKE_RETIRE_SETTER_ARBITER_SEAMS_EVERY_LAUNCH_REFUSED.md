# RIMMANDRAKE_RETIRE_SETTER_ARBITER_SEAMS_EVERY_LAUNCH_REFUSED

Filed 2026-11-18 by BENCH (item `RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES`, move 3).

## spec

`role_launch.py` still routes a stage's check/bar rejection into two Relentless-era seams: the Setter seam
(`to_setter`/`setter_resit` -> `item_exam.status/set_status/kick`) and the arbiter seam (`to_arbiter` ->
`stage_dispute.role_stage_dispute`). Both act only on an item that holds a Relentless exam in
`/home/mandrake/rm/relentless/store/exams/` (102 exist, the newest touched 2026-11-06; nothing live creates one), and
every unit they start launches as family `relentless`, which the control store refuses (`./pipe show`:
`family:relentless OFF`, measured 2026-11-18 3:58 PM PST). So the Setter seam can only write `owed.json` and report
"unit did not start", and the arbiter's box is made and then refused. Move 3 of the split moved this code verbatim to
`item_exam.py`, `stage_dispute.py` and `checker_box.py` (a move, not a redesign); this item removes the seams from
`role_launch.py` so a rejection takes the route it takes for an item with no exam, then deletes what only the seams
reach (`item_exam.py`, `stage_dispute.py`, the parts of `checker_box.py` that `evidence.py`'s `box_config` does not use).

## verify

Acceptance test (red on `7a910cdd97`+move 3, watched: rc=1):
`bash -c '! grep -q -E "item_exam|stage_dispute" src/RimMandrake/rimflow/role_launch.py && python3 src/RimMandrake/rimflow/selftest_role_launch_reject_routes.py'`
passes (exit 0), with the reject-routes selftest's Setter/arbiter cases rewritten to the no-exam route.

## criteria

- A1 (offline): the acceptance test above exits 0.
