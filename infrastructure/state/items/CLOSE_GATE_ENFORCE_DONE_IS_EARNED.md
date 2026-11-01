## Why
Requirement RO3 in `design/RimMandrake/operating_requirements_2026-11-01.md`. Read that entry first; it names the signal, threshold file and owner.

## Done when
Each of the four missing is refused. A fail after a pass demotes. A seeded behavioural regression caught later reopens the item. AU4 re-read and in range.

Proved by the planted fault on the real path, not by a statement.

## Ruled 2026-11-01 (owner: "Do items 1,2,3 owner items now.", decisions D1(b))
This item also carries T1 and T3 of the v3 audit (`CLOSE_ENFORCE_NO_OWED_NO_IMPLICIT_HEAD`, `VALIDATED_FIX_DEMOTE_ON_CURRENT_FAIL`, not filed separately) and D1(b), which OVERTURNS the standing ruling "Arbiter verdicts are advisory":
- An Arbiter FAIL on the item's sha blocks `rimflow close` until a new build (new sha) passes the Arbiter, or the owner overrides (`--owner-said`/`--by-card`/`--per-ruling` on the close). No verdict at all blocks nothing (not option c).
- `close` refuses owed criteria (no longer "a WARNING, not a refusal") and an implicit HEAD: `--sha` or `--no-code "<what>"` required; a sha touching none of the cited paths needs `--why`.
- A fail `verify` against the current `built_sha` demotes `validated` to `built` and re-owes the criterion; a pass on a stale `built_sha` does not count. The gate sits in the verify-to-done transition too (`model.py _criterion_passed`), not only in `close`, since the last passing verify makes an item done with no close.
- Calibration is on false ACCEPTS (the Auditor's random slice), not on verdict count; the "1 week / 30 verdicts" binding rule is replaced.
- Standing text to change when this lands (all of it, deciding-and-superseding): `roles/arbiter.md` (header, "Advisory first" section, binding criteria), `roles/auditor.md` l.85 and l.106, `dispatcher_schedule.json` `verdicts` and its `_why`, `arbiter_tiers.py` docstring and `bounces.json` advisory flag, `role_launch.py` verdict note text, `selftest_arbiter_tiers.py` F9, `selftest_role_run_now.py` advisory assertion. A grep for 'advisory' under src/RimMandrake/rimflow must find none that describe the Arbiter's close verdict.
Priority: P0, raised.
