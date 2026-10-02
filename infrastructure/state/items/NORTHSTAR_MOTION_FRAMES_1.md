
## Built as a provisional seed — 2026-10-01, `8463a2734`

The 2026-09-17 deferral was lifted by the owner on 2026-10-01 (relayed by the
coordinator): *"There will be many such mods that require a human nearby to build proper
northstar scripts. You are mostly seeding the field right now with reasonable initial
guesses for refinement later through debugging needs or live feedback."*

What landed (spec `design/RimMandrake/north_star_validation_spec.md` §4b.1): `(change)`
tag parsed by `northstar` (`kinds_for`), `suite.capture_frames(n, every_ticks)`, a
sequence prompt in `judge` with `MIN_CHANGE_FRAMES = 2` (fewer is UNJUDGEABLE), kinds
wired through `runner.apply_judgement`, and `modcheck/selftest_motion_frames.py`, where a
fake judge that compares frames makes a static sequence FAIL a "moves" bar.

Still open, deliberately: the frame count per line is a guess, and
`never_interpolated_colour` still needs a material-cache count, not an eye. The
AtmosphericBase checklist itself was not touched (`NORTH_STAR_ATMOSPHERIC_TBD_1`).
FOUNDRY could not close this BENCH item; BENCH closes it on `8463a2734`.
