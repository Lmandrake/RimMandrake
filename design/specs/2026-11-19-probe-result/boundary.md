# BOUNDARY: probe results and the could-not-look lint, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/probe_result.py` (the type) and `src/RimMandrake/Utils/could_not_look_lint.py` (the
lint). Design: `design/specs/2026-11-18-review-growth-cycle/01-design.md` §5.5, parts 1 and 2. Item:
`RIMMANDRAKE_SHARE_PROBE_RESULT_TYPE_NINE_FILES_ROLL_OWN`. Written 2026-11-19. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_probe_result.py`, and a deliberately broken stand-in that turns that test red in
`src/RimMandrake/rimflow/acceptance/probe_result_promise_breaks_accept.py`. Neither part keeps state between calls, so
the page has no LIFE CYCLES.

## ACCEPTS (the only inputs the two parts are built for)

- **a-read-of-the-outside-world.** A function that reads systemd, a file, the store or another program returns one of
  four answers: `value(x)`, `empty()`, `could_not_look(cause)`, `failed(cause)`. Any Python value may be a value.
- **pipeline-python-files.** The lint reads the `.py` files matched by `pipeline_files` in
  `src/RimMandrake/Utils/pipeline_tests.json` (selftests skipped), or only the files named after `--files`.

## DOES NOT SURVIVE (not promised)

- **a-caller-that-unwraps-by-hand.** A caller that catches `NotAnswered` and returns empty, or tests `kind` with a
  misspelt name: the type cannot see it.
- **an-empty-built-another-way.** `x if x else []`, `rows = []` inside an `except`, an empty returned through a
  variable: the lint sees only the two shapes it names, and an allowlisted line is read by a person, not by the lint.
- **a-file-that-does-not-parse.** The lint names it UNREADABLE and exits 3; it lints nothing in it.

## PROMISES (each one is owed a test of the same name)

- **probe-never-lies.** `could_not_look(cause)` and `failed(cause)` raise `NotAnswered` at once when used as a truth
  value (`x or []`), a list (iterated, `len`, indexed, `in`) or a number (`int`, `float`, an index), or unwrapped
  with `.value`. Never an ordinary answer.
- **blind-answers-keep-their-cause.** Each keeps its cause, which may not be blank. `str()` of one says which of the
  two it is and the cause, and printing one never raises.
- **looked-answers-read-plainly.** `value(x)` reads as `x` (truth, iteration, `len`, index, `in`, `int`, `.value`);
  `empty()` reads as an empty list and is false. Printed into a log or failure line (`%s`, `%r`), one reads as `x`
  (`[]` for empty) and never raises, as `control_kill_drill.py` and `selftest_control.py` print them.
- **four-answers-never-blur.** `kind` is exactly one of `value`, `empty`, `could_not_look`, `failed`, and `ok` is true
  for the first two only. `value()` of a blind answer raises instead of hiding it.
- **lint-sees-both-shapes.** The lint names `file:line` for `<call> or []` (also `{}`, `()`, `0`, `None`, `""`) and for
  an `except` whose body returns one of those. A `.get(...)` on the left reads a mapping already in hand and is not
  flagged; neither is a name or an attribute on the left.
- **lint-allowlist-is-counted.** A hit beyond its allowlist count (key: file, function, shape) is red, exit 1; a line
  moving inside its function changes nothing. A fixed hit leaves slack, which `--prune` removes.
- **lint-shadow-refuses-nothing.** With `--shadow` the lint prints its count and every hit beyond the allowlist and
  exits 0, an unreadable file included. `./publish` runs it so (a `"shadow": true` check in
  `publish_tree_checks.json`): it prints the lint's last line and refuses nothing.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
