## spec
Filed 2026-11-18 about midnight PST by the detached run on `RIMMANDRAKE_ENACT_PAGE_BEFORE_CODE_CONTROL_STORE_IS_PILOT`, as step 4 of that item: owed by the owner's
card of 2026-11-18 (`standing_rulings.md` §A boundary page before pipeline code). Not from a review finding.

One shared result type for reads of the outside world, and its lint (design `design/specs/2026-11-18-review-growth-cycle/01-design.md` section 5.5, parts 1 and 2).
`src/RimMandrake/rimflow/probe_result.py`: `value(x)`, `empty()`, `could_not_look(cause)`, `failed(cause)`. The last two
cannot be used as a truth value, a list or a number: doing so raises at once. `src/RimMandrake/Utils/could_not_look_lint.py`,
built like `call_deadline_lint.py` with a counted allowlist, is red at `./publish` on `<call> or []` and on an `except`
that returns an empty value in a pipeline file.

Why: "could not look" was read as "nothing there" at least 5 times in `control.py` on 2026-11-18 [`00-problem.md`, a
reading of claim text, ~80%], and 9 files under `rimflow` and `Utils` each define their own `Unreadable` or `Unmeasured`
class [measured: grep of `^class (Unreadable|Unmeasured)`, selftests excluded]. Scope: the type, the lint, its first
allowlist, and `control.py`'s own reads. Other callers move when they are next extended, not in a sweep.

## refs
file: src/RimMandrake/Utils/call_deadline_lint.py
file: src/RimMandrake/rimflow/control.py

## criteria
- `python3 src/RimMandrake/rimflow/acceptance/probe_result_type_accept.py` exits 0 (6 checks).
- The lint runs at `./publish` and its allowlist is counted.

## verify
python3 src/RimMandrake/rimflow/acceptance/probe_result_type_accept.py   # exit 0
Acceptance test: watched failing on a6aac8a6fc7c: the module and the lint do not exist, 3 fail. Expected: 6 pass.
