# History: evidence and old lines that left `SKILL.md`

The lessons are in `../SKILL.md`. This file holds old lines that are no longer true, and examples. Git holds the rest.
Each line below is a record, not a rule. Every correction below is of 2026-11-23, unless the line gives another date.

## The bland world (§1)

- §1 once said that the runner uses `bland_world.py` "today". `modcheck run` does not pass `bland_world=True`. Only
  `live_queue/situational_rerun.py --bland-world` does.
- §1 once said that the design of record overrides §§3–6 at its §10. The heading of §10 there says §§3–8.
- §1 once said that `save_base` proves that no other save changed size. `save_guard` now compares hashes.

## The envelope (§2)

- §2 once gave `t.expect(kind, matcher, until_tick=, phase=, max_count=)`. `TestContext.expect` in `suite.py` has no
  `phase`; `Watch.expect` has it.
- §2 once said that a 95 000-tick wait that is not chunked is UNMEASURED by budget. Chunks alone do not help: the budget
  is per chain. Antiquities also declares `tick_cap` (2026-10-01).
- The rollout gate once asked for a pass "on the current envelope, covering every on-disk suite". Since 2026-11-06
  (commits f96ff254c1 and 44d904c1cc), the gate asks for a pass at or after its own newest commit, and for the suites
  that compose onto the minimal list. Reason: the envelope files took 3-7 commits a day, and the pass takes about a day.
- §2 once said that the game is always left paused with its settings restored. `Watch.__exit__` does not raise when a
  step fails. It writes the failure to `close_problems`.

## The queue (§3)

- §3 once said that every hazard of `abort_proof` must abort. Since the owner's card of 2026-10-10, the `hostile_raid`
  case proves the visitor rule: the hostiles are recorded and removed, and the run goes on.

## The playbook (§5)

- The focus row once named the Alt-tap + AppActivate fallback as the fix. `focus_game` now refuses without
  `RM_FOCUS_OPT_IN` (owner ruling 2026-10-04, item `FOCUS_HEAL_TAME_HANDS_OFF_HIS_WINDOWS`, 2026-10-10).

## The scoreboard and DRAFT

- `required_checks_report.py` once read only `Transient/modcheck/live_queue/*_summary.json`. It now also reads the results
  of a `checkout:` script (`NORTHSTAR_RESULTS_JOIN_1`, 2026-10-06).
- Example of a hash that returned a north star to DRAFT: a later commit trimmed stale status prose off the WreckedMachines
  `never_two_identical_smelters` cannot-show line. The trim loosened nothing. `NORTH_STAR_WALK_AUTHORING_1` still listed
  the mod as VALIDATED.
- The last section once said that a new bar needs the owner to hear the lines. The delegated route for new bars is of
  2026-10-26 (`delegation_policy.md` §1). The section also said that "the loop" needs `shows=` claims. The loop is
  retired. The refusal is in `runner.refusal`.
