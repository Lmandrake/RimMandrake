# RIMMANDRAKE_REPIN_WHEN_GRANT_ITEMS_CLOSE

## spec
A coverage grant on a LOCKED concept waits on two things (`coverage_judge.grant_waits`): every `--after` item terminal,
and a `locked_change` (the re-pin, `designer_stage.py repin`) written after the stop the grant lifts. The Maturation
tick routes the first: `maturation_autonomy.stop_tickets` gives each after-item one fixer run while the mod stays
paused. Nothing routes the second. No stage, ticket or brief owes the re-pin, so once the fixers close their items the
grant never comes due, `chain_owed` never fires and the mod stays paused with the pause line reading "every open fix
ticket ... has had its one fixer run" or nothing at all. It does not say that the grant waits on a re-pin that nobody
owes.

Found 2026-11-17 by a Conductor helper while enacting Pyrelands option A (round-9 gaps, delegated Evidence-for-Ask call
on RIMMANDRAKE_RETAKE_PYRELANDS_EXAM_AFTER_LOCKED_CHANGE_RUN_TWO). Each earlier Pyrelands grant (2026-11-15 x3,
2026-11-17) worked only because a hand-filed item carried "then one re-pin" in its spec. For this round the stand-in
is RIMMANDRAKE_REPIN_PYRE_AFTER_ROUND_NINE_GAPS, the last item in the grant's after-list.

Not a defect (checked): `repin` refuses a `CONDUCTOR:<tsn>` source. The Evidence-for-Ask spec keeps `locked_change`
his ("the other owner-only kinds ... stay his"). A delegated call decides that the gaps are fixed; the re-pin cites
the card of his that each fix carries out.

Smallest fix (Relentless freeze: no new rule or key; this repairs a real wait with no owner):
- `_stop_tickets`: when the grant's after-items are all terminal and `grant_waits` still names the re-pin, say so in
  the row (`why`/`need`: "the grant waits on the re-pin: designer_stage.py repin <dir> --source OWNER:<tsn>@<commit>
  ..."). Then give the re-pin one fixer run like a ticket, briefed from the commits since the stop and the OWNER
  events they cite. Or refuse a `release --after` on a locked concept unless one after-item's spec names the re-pin.
  The choice belongs to the builder, who picks whichever adds no new rule.

## verify
A selftest (selftest_maturation_autonomy or selftest_coverage_judge): a fixture locked concept with a coverage_stop, a
grant `--after X`, and X closed. With no locked_change after the stop, the tick row names the re-pin wait (and, under
the fixer variant, routes one fixer run to it). After a locked_change is written, the grant is due and `chain_owed`
fires. An unlocked concept with the same fixture shows no re-pin wait. Watch it fail first on the current base.

## criteria
- a locked concept's grant whose items are all closed never sits paused without naming the re-pin it waits on
