# RIMMANDRAKE_SHOW_CODEX_DESIGNER_LANE_TO_THE_MATURATION_READER

## spec

`maturation_dispatch.py status` at 5:14 PM PST 2026-11-15 read LeaningScrub "waiting on nothing running (designer_wait)"
while its Codex Designer run rm-role-designercodex-1794791300 was live. `maturation_autonomy.designer_unit` matched only
journal lines with `"Designer"` (the Claude lane) and `designer_chain` read only the Designer role's chain counts, so the
new DesignerCodex lane was invisible to the pipeline's reader.

Fix: `DESIGNER_ROLES = ("Designer", "DesignerCodex")`; `designer_unit` takes a launch of either lane (by the journal's
`blind.role`, not a substring), and `designer_chain` sums both lanes' chain counts.

Acceptance test: `python3 src/RimMandrake/Utils/selftest_codex_runner.py`, test `test_maturation_sees_the_codex_lane`.
Failed on the base (FAIL), passes after; `selftest_maturation_autonomy.py` ALL PASS.
