# Narrative dictionary pilot — batch 1

Item `NARRATIVE_DICTIONARY_PILOT_1`. Spec: `design/RimMandrake/narrative_dictionary_design.md`.
Plan: `design/RimMandrake/narrative_dictionary_pilot_plan.md`.

## Pre-registered bar — written and committed BEFORE any dressing exists

Quoted from the spec §7 and the plan's Task 1 `bar.py`, unchanged:

- **claim_recovery_ratio = 2.0** — the dictionary dressings must recover at least 2x the
  intended claims that the control dressings recover,
- **false_claim_rule: dictionary_false <= control_false** — with no more invented history,
- **min_intended_claims = 4** — below this the sample is too thin and the verdict is
  `PROXY_UNTRUSTWORTHY`.
- If the control recovers 0, the dictionary passes iff it recovers >= 1.
- Verdict is one of `PASS` · `FAIL` · `PROXY_UNTRUSTWORTHY`. A FAIL is recorded as FAIL;
  the bar is never moved to accommodate a result.

Scoring is per dressing: a claim counts as recovered only when the reviewer states its
substance (who / what happened / are they still here), not a keyword. A false claim is any
assertion about the room's history that contradicts the intended claim set.

(Method and results sections are filled in below after the dressings are built.)
