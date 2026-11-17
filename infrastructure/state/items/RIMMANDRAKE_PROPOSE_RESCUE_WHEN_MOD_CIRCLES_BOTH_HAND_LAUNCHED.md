# RIMMANDRAKE_PROPOSE_RESCUE_WHEN_MOD_CIRCLES_BOTH_HAND_LAUNCHED

Owner, 2026-11-16 about 10:10 PM PST, asked "Shall I file that as the next step of the work order, with its tests?"
on the Conductor's criteria for when the Maturation Pipeline should propose a Fable Rescue: *"yup. Then we'll watch
stats to see if we need to tune that."*

## spec

Both Fable Rescues of 2026-11-16 (Gimme Some Slack, Pyrelands) were launched by hand: nothing in code saw a mod going
round the same ground. This item gives the Dispatch tick a detector that PROPOSES a rescue and never launches one
(`src/RimMandrake/rimflow/maturation_rescue.py`). It supersedes the line "No stall detector" of
`RIMMANDRAKE_ENACT_INVENTION_WHEN_BARS_CONFLICT_GRADIENT_TOO_EASY`: Pyrelands was the second mod.

The five criteria, each read from records, never guessed (the brief's "Why you were called"):
1. The same check flips between pass and fail across builds of the mod (blind cycles' `lane2/reruns.jsonl` then
   `reruns_after_fix.jsonl`, in-game visits' `rows.jsonl` by `mod_sha`).
2. The same tuning number changed twice in opposite directions (the mod's source history in git since its version
   was seeded: a line whose only change is a numeric literal, up then down or down then up).
3. The same bar refused by a judge in two cycles running (a blind cycle's Problem faults and red offline bars; an
   in-game visit's last-row FAIL through the test table's `decides`).
4. The mod at its stage spend ceiling (the tick's `ceiling` decision) without a green certificate for its next move.
5. A bar with no test that runs the real mechanic: every in-game decider of the bar ran on a site that switched a
   mechanic off or locked a condition. No record held that until this item: an in-game row now carries `held` (the
   list the site switched off or locked; `[]` when the whole mod ran), named in the in-game driver's brief. A row
   without it reads UNMEASURED for this criterion, never a pass or a fire.

A proposal writes one line to the Conductor log, `RESCUE PROPOSED: <mod> ...` with the criteria, the evidence path
and RAISE FIRST, and a Needs Conductor line in the reading. A mod held by the owner (mod_owner_hold.json) is never
proposed; evidence older than a live or ended rescue's end is never proposed; the same evidence is proposed once.
Thresholds are one settings block, first guesses to be tuned from the stats. The stats are an append-only jsonl in the
Dispatch state dir (`rescue_proposals.jsonl`), with `outcome` rows (launched, declined with reason, ended solved or
not, spend) and `status` printing per criterion: proposals, launched, solved, false alarms.

## verify

- `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_rescue` red on the base (no module), green
  after; `selftest_maturation_dispatch,selftest_maturation_hands,selftest_maturation` stay green.
- `python3 src/RimMandrake/rimflow/maturation_rescue.py scan` over the real mods, read and reported on this item.
- Live: the Dispatch tick unit runs the detector; `python3 src/RimMandrake/rimflow/maturation_rescue.py status` reads
  its last pass from `reading.json` (`rescue` block).

## criteria

- It proposes, never launches.
- Every criterion is measured from a record or reported UNMEASURED with what is missing.
- A healthy mod, a held mod, a mod under or just out of a rescue, and the same evidence twice propose nothing.
- One line per proposal in the Conductor log; one stats row per proposal; status fits one screen.

## refs

file: src/RimMandrake/rimflow/maturation_rescue.py
file: src/RimMandrake/rimflow/selftest_maturation_rescue.py
file: src/RimMandrake/rimflow/maturation_dispatch.py
file: src/RimMandrake/rimflow/roles/fable_rescue.md
file: design/specs/2026-11-13-maturation-pipeline.md
