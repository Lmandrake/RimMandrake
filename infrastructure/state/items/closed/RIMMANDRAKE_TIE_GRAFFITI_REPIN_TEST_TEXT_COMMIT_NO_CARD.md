## spec
`designer_stage.py repin design/concepts/Graffiti` refuses after the ugliness_visible card (OWNER:1794889675303725702@1bee0c2e96):
"stage 3: scenes was changed by 68f199064a, which no source cites". 68f199064a (2026-11-15, the hidden-face fix,
RIMMANDRAKE_REFUSE_HIDDEN_FACE_PAINT_ORDER_OUTLIVED_ITS_WALL) changed sc_wall_closeup's control as test text; the steward
re-pinned it in version/bars.md with a journal line (the bars.md re-pin rule) but stage.json's stage-3 pin was never moved, and
repin accepts only commits tied to an owner event. His lock card (OWNER:1794771556666342734) says that defect "stays open in this
version", but no ledger event on RIMMANDRAKE_ADVANCE_GRAFFITI_LOCKED_VERSION_TO_PREFLIGHT names 68f199064a, so change_tied is False.
Two re-pin rules disagree: bars.md re-pins test text with a journal line; designer_stage.repin needs his card for every commit.
Path to pass (pick one, then rerun the command below): (a) a ledger note on RIMMANDRAKE_ADVANCE_GRAFFITI_LOCKED_VERSION_TO_PREFLIGHT
naming 68f199064a as carrying out the defect his lock card kept open, then add `--source OWNER:1794771556666342734@68f199064a`;
or (b) repin learns the test-text route (a commit re-pinned in bars.md with a journal line is cited by that row).
Rerun: python3 src/RimMandrake/rimflow/designer_stage.py repin design/concepts/Graffiti --source "OWNER:1794889675303725702@1bee0c2e96346a6ed10cfdf2393409321a7bc331" --source OWNER:1794790746864442914 --source OWNER:1794790752285697966 --source OWNER:1794790788426165373 --source OWNER:1794790829027694796 --why "..."
(the four 17947907.. sources are 2026-11-15 card answers re-stamped by the card backfill; repin asked for them first).

## verify
Acceptance test: the rerun above prints the re-pinned stages and exits 0; today it exits non-zero with the stage-3 refusal (seen 2026-11-16 8:59 PM PST).

## criteria
- the Graffiti repin after the ugliness_visible card succeeds by a route that cites every commit truthfully.

## refs
file: src/RimMandrake/rimflow/designer_stage.py
file: design/concepts/Graffiti/stage.json
