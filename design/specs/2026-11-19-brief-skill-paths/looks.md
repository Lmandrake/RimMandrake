# Two looks at the skill-path launch warning (commit f5c94f632a), 2026-11-19

Item: `RIMMANDRAKE_LOOK_TWICE_AT_SKILL_PATH_WARNING_BUILDER_CANNOT`, taken by the helper of
`RIMMANDRAKE_FIX_FOUR_SMALL_DEFECTS_FOUND_AT_TODAYS_WAKE`, which did not build the warning. Page: `boundary.md` beside this.

## Look 1: the code read against each promise

- **a-brief-naming-no-skill-gets-one-warning: kept.** `launch` computes `skill_path_warning(brief)` from the brief as
  given (the footer is added later, inside `_launch`) and appends it after the preflight tail, so it is the last line.
  `_launch` has one `return 0` (the started unit), so "a launch that starts" and `code == 0` are the same set.
  `SKILL_PATH` needs `skills`, a separator, a name and a second separator: `skills/BY_WORK.md` alone has no second
  separator and is warned; `\` paths match.
- **a-brief-naming-a-skill-gets-no-warning: kept.** A match returns None and nothing else in `launch` prints a skill
  warning.
- **the-warning-refuses-nothing: kept.** The exit code is computed before the warning and returned unchanged; on a
  non-zero code neither the tail nor the warning is added, so a refusal's text stays the gate's own.

## Look 2: the real command line, no model run

`python3 src/RimMandrake/rimflow/detached_helper.py launch --seat BENCH --item <this item> --brief-file <brief>
--model sonnet --budget-usd 0 --clone <tmp dir> --skip-launch-checks "..."`, with `RM_DISPATCHER_STATE`,
`RM_CONTROL_DB` and `RM_RUN_TMP_ROOT` in a temp dir and a stub `systemd-run` first on PATH (it records its arguments
and exits 0: no unit, no claude). Measured 2026-11-19 ~2:00 PM PST:

- brief "Look 2 probe brief. Build nothing. Names no skill path.": exit 0, last line `WARNING: the brief names no skill
  path (skills/<name>/SKILL.md); the helper sees no unregistered skill. Name the paths for its kind of work from
  skills/BY_WORK.md`, one WARNING line.
- brief "Read skills/rimbridge/SKILL.md first. Build nothing.": exit 0, no WARNING line.
- the first brief against an uninitialised control store: exit 2, `REFUSED ... by control: not initialised`, no
  WARNING line.

Not run: a launch that starts a real unit (it would start a model run).
