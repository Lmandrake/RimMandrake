# The Test Pilot and the Fable Rescue: one role, or two? (2026-11-25)

Item: `RIMMANDRAKE_COMPARE_TEST_PILOT_WITH_FABLE_RESCUER_ONE_MAY_HOLD_BOTH`. The owner, 2026-11-17: *"That same ticket
should also include comparing a Test Drive agent with the Fable Rescuer... I'm thinking they might actually be the same
thing, or one is a subset of the other, and if so we can simplify and retire what we don't need."*

Files read: `.claude/agents/rm-testpilot.md`, `src/RimMandrake/rimflow/roles/fable_rescue.md`,
`src/RimMandrake/rimflow/testpilot_route.py`, `src/RimMandrake/rimflow/maturation_rescue.py`,
`src/RimMandrake/rimflow/maturation_autonomy.py` (`_pilot_step`, `pilot_brief`).

## RECOMMENDATION: keep both roles; retire criterion C5 of the rescue proposer

1. **Keep the Test Pilot and the Fable Rescue as two roles.** They share one stance. They differ in the unit of work,
   the instrument, the trigger and the end state (table below). Neither role is a subset of the other: each role does
   work that the other role's brief forbids or does not name. The shared part is already one source: the positive steps
   are pinned in both briefs by `selftest_positive_steps_one_source.py`. A merge removes no duplicated machinery.
2. **Retire C5 ("bar with no test running the real mechanic") from `maturation_rescue.py`.** Send C5's evidence to the
   Stage 6 scene repair instead (CLAUDE.md §Touching code has a cost: "the staged scene is wrong" is repaired in the
   sitting), with a Test Pilot sitting as the escalation when the repaired scene still fails. Reason: a C5 finding is a
   scene whose site switches the mechanic off. That is the Test Pilot's own rule ("Never judge a mechanic on a site
   that switches the mechanic off", `rm-testpilot.md`), not a whole-mod design problem. A whole-mod offline rescue is the
   wrong tool for it. Example [measured]: proposal `rp-pyrelands-1795554723` names bar `no_ordinary_rain`, whose only
   decider `sc_no_rain` ran with "weather: Clear locked at the site's start".

## The two roles side by side

| | Test Pilot (`rm-testpilot`) | Fable Rescue (`fable_rescue.md`) |
|---|---|---|
| unit of work | one ledger item or one road-back item | the whole mod: every open ticket for its current version, and every failure of its last in-game visit |
| instrument | the live game: bridge state reads, screen looks, the surprise book | an offline generator over the situations the mod can be in, read by the bars' own checks, proved to agree with the game; the live game comes last (step 11) |
| question | what actually happens here, and why | which regions of the situation space fail every bar at once, and what change dissolves the conflict |
| trigger | `testpilot_route.py`: 3 non-pass runs in a row, a `TESTPILOT_WANTED` note, or a DIAGNOSE item that needs the game; `_pilot_step`: a live road-back item at Stage 6 with N `LEFT OPEN` endings | `maturation_rescue.py` C1–C5 (a mod that circles), as a proposal only |
| launch | automatic: `rimflow pilot` and the Maturation tick book the sitting | the Conductor launches by hand; the proposer launches nothing |
| end state | a cause, a check that goes red for the reported reason, the walk script updated, a `TESTPILOT_SAT` note | the mod's bars hold over the declared range, the instrument landed as a check, an `inventions.md` sheet, questions to the owner |
| model | Fable 5.2 | Fable 5.2 |

What each one does that the other one does not:
- Only the Test Pilot measures surprise on screen, keeps the surprise book, runs an exploration pass and files what a
  player would feel. A rescue has none of this.
- Only the Rescue takes the whole mod, builds the enumerated offline map, and redesigns (unify, invent, propose a
  relaxation) across every bar at once. A pilot ends on one item and files each other defect as its own item.

What they share, and where it already lives:
- The owner's positive steps (2026-11-16), "hunt regimes, not examples", "tag each limit bar or our own rule", "no open
  cases at the end", and "prove an offline copy agrees with the live game". `selftest_positive_steps_one_source.py`
  holds the positive steps as one source. The other shared lines are short and fit each role's instrument.

## The record of use [measured 2026-11-25 00:50 PST, this clone at origin/main]

- Test Pilot: 28 `TESTPILOT_SAT` notes on 18 items, 2026-10-31 to 2026-11-23, from the ledger shards.
- Fable Rescue: 2 hand rescues (Gimme Some Slack, Pyrelands, both 2026-11-17) and 2 launched proposals, from
  `maturation_rescue.py status` and `list`.
- Rescue proposals: 58 made, 54 still open, 2 launched, 4 declined, 0 recorded solved. By criterion: C1 21 (19 open),
  C2 2 (2), C3 13 (11), C4 3 (3), C5 19 (19 open, 0 launched).
- So C5 is a third of all proposals and none was ever acted on. Each open proposal is a Needs Conductor line.

## Alternatives that lost

- **Merge into one Fable role with two modes (live, offline).** Gain: one file. Cost: two tuned briefs (278 and 336
  lines) become one brief that every run reads in full, and the selftests that pin each brief's markers
  (`selftest_testpilot_route.py`, `selftest_offline_model_rule.py`) must be rewritten. The shared stance is already one
  source, so the merge saves little [guess ~75%].
- **Make the Test Pilot a step of the Rescue.** The pilot runs automatically and often (18 items); the rescue runs by
  hand and rarely (4 runs). Folding the frequent automatic role into the rare hand role would stop the automatic route.
- **Retire the rescue proposer entirely and keep only hand rescues.** The record above (2 of 58 proposals launched) is
  evidence for this, but C1 and C3 proposals did lead to the Explosive Knockback rescue. Retire C5 first, and read the
  record of C1 to C4 again after a week [guess ~60% that C2 and C4 also turn out to be noise].

## What the ruling changes

- If the Conductor accepts: remove `"C5"` from `CRITERIA` and its reader from `maturation_rescue.py`, update
  `selftest_maturation_rescue.py`, decline the 19 open C5 proposals with `outcome PID declined --why "C5 retired: a
  locked-site scene is a Stage 6 scene repair"`, and give the Stage 6 visit a line that names a decider on a held site
  as a wrong scene. Check: `cmd:python3 -c "import sys; sys.path.insert(0,'src/RimMandrake/rimflow'); import
  maturation_rescue as R; sys.exit(0 if 'C5' not in R.CRITERIA else 1)"`.
- If the Conductor declines: nothing changes; both roles stay as they are.
