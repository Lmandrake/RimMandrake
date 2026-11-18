## spec

The RimMandrake half of the 2026-11-17 silent-failure audit (Dispatch's nine were fixed that day; this repo was
never audited). Found by reading `verdict_for` and the runner's `record_run` call, and probed by hand
2026-11-17 PST — not inferred.

`status.verdict_for(all_green, walk, refused, reviewed)` (`src/RimMandrake/Utils/modcheck/status.py:415`) answers
`"RED"` whenever `all_green` is false, and `runner.py` hands it a false `all_green` for **three different
situations**:

1. a component genuinely verdicted FAIL — a real defect in the mod (`runner.py:1233`);
2. the suite recorded **no component at all**, so nothing was measured — the code even says so in its own comment,
   *"a suite that recorded NO component at all measured nothing: never green (all() of nothing is True)"*;
3. the known-good **gate SKIPPED** a chain, so that chain was not measured this run (`runner.py:1566`:
   `summary["all_green"] and not (summary.get("gate") or {}).get("skipped")`).

Probed: `verdict_for(False, None)` returns `RED` for all three. Only the visual-floor refusal gets its own answer
(`REFUSED`), and `GREEN` needs five things. So `infrastructure/state/modcheck_status.json` — 71 mods — records a
mod that was never measured identically to one that failed. `AcousticScanner` sits at `"status": "RED"` with no
field anywhere in the entry saying which of the three it was.

This is variant 1 of the four-variant checklist
(`infrastructure/state/lessons/20261117T225720Z-UNSEATED-all-nine-silent-failure-instances-found.md`): the code
COMPUTES the "could not look" case — `all_comps` being empty, `gate.skipped` being non-empty — and then drops that
distinction from the value it stores.

**It is not the whole story, and the ticket must not overstate it.** The machinery around it is better than the
registry field: `spoil_gate.grade()` already produces a four-level `overall` (`RED > UNMEASURED > INDETERMINATE >
GREEN`), components carry a real `UNMEASURED` verdict, and `cli._verdict_line` names WHICH half failed for the
human reader (added precisely because *"'RED' alone sent the pit's real defect unnamed for a month"*). The defect is
that the **stored status**, which other programs read, throws that away. `a2_live_proof.py:144` compares
`entry["status"]` against an expected value; `relentless_envcause.py:44` already has to pattern-match prose to
recover "no modcheck_status entry" as UNMEASURED, which is the workaround this fix removes.

**The fix.** `verdict_for` gains the distinction it already has the inputs for — an UNMEASURED answer (or a
cause field beside the status; the shape is the builder's call, stated in the commit message) — and the runner
passes WHY rather than a collapsed boolean. Keep the four answers apart: GREEN is a measured pass, RED is a measured
failure, UNMEASURED is "could not look" with its cause named (no components / gate skipped / which chain), REFUSED
stays the visual floor. 🔴 A GREEN must not become reachable in any case where it is not today: this change may only
make a non-GREEN more specific, never more permissive. Fix every reader in the same change (`a2_live_proof.py`'s
expected-status comparison is the one that will break first) and say which readers you checked.

**The other two files the audit was pointed at came back CLEAN, measured, not skipped.** This is `[]`, not
`unknown`: both were read, and both already keep the distinction.
- `src/RimMandrake/Utils/deadman_check.py` — `excused()` and `just_restarted()` each catch broadly and return
  False with the comment *"could not ask: an outage stays an outage, and the sweep lives"*: ignorance never
  pardons an alarm, which is the safe direction for something that rings his phone. `judge()` answers
  *"has no readable last-run stamp"* as its own distinct reason, separate from a stale stamp and from a
  future-dated one.
- `src/RimMandrake/Utils/testq/fault_monitor.py` — `steve_read()` returns None only for unreachable, and `tick()`
  stores that as its own field (`reachable=bool(fx)`) rather than folding it into a verdict, plus a separate
  `blind` reason when no canary cycle has been seen. `ps()` returns `rc None` for ssh down, distinct from a
  non-zero rc.
Nothing else in this repo was audited for the four variants; that remains open work, not a clean bill.

## refs

file: src/RimMandrake/Utils/modcheck/status.py
file: src/RimMandrake/Utils/modcheck/runner.py
file: src/RimStarWars/GizkaStowaway/a2_live_proof.py

## verify

python3 src/RimMandrake/Utils/modcheck/selftest_northstar.py

## criteria

- A1: a run with zero measured components records a status distinguishable from a run with a FAIL, with its cause.
- A2: a run whose gate skipped a chain records a status distinguishable from both, naming the skipped chain(s).
- A3: a real FAIL still records RED; the visual floor still records REFUSED.
- A4: no input that reads non-GREEN today reads GREEN after the change (checked over every combination, not by eye).
- A5: every reader of the stored status is updated in the same commit, `a2_live_proof.py` included.

## acceptance

Acceptance test: new cases in `selftest_northstar.py` (or a selftest beside `status.py`) calling `verdict_for` /
`record_run` with the three distinct causes and asserting three distinct recorded answers, plus a sweep over every
combination of its inputs asserting A4. Watched FAILING on the base commit, where all three read `RED` — the
one-liner that produced this item's reading is the base evidence:
`python3 -c "import sys; sys.path.insert(0,'src/RimMandrake/Utils/modcheck'); import status; print(status.verdict_for(False, None))"`
→ `RED` for a FAIL, for nothing-measured and for a gate skip alike.
