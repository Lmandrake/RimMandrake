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


## Method (as built, 2026-10-03, offline)

`build.py` builds the whole slice deterministically. `python3 build.py` rebuilds every
file below. `python3 build.py --selftest` runs 6 checks, 5 of them negative controls:
same-register, all-LOW, unmet-counted-as-met, unknown ROOM_KIND, and invented provenance
must each be rejected.

| file | contents |
|---|---|
| `objects.jsonl` | 45 rows: 42 placeable props + 3 floors. Each field carries provenance (`MEASURED`/`DEF_TEXT`/`VISION`). Every defName was verified against the live def dump (628 mods, 2026-09-26). |
| `vignettes.md` | 8 vignettes (4 *poor but tended*, 4 *rich but abandoned*). Each is a set of predicates that resolve to defNames, with a traceability grade and a register per ingredient. Unmet ingredients are named. |
| `dressings.md` | One room plan, a 13x9 salvage bay (`service`), dressed 4 ways: A/B x dictionary/control. Each comes as a grid plus a defName table. |
| `reviewer_packet.md` | **The blind test.** Part 1 shows the 4 rooms shuffled to W/X/Y/Z, with in-game labels and visible state only (no defNames, no intent). Part 2 lists the 8 vignettes as bare prop lists. |
| `answer_key.md` | The room-to-condition map, the intended claims, and blank scoring sheets. |
| `GAPS.md` | What the dictionary could not express. Its §4 scopes `EVENT_TRACE_PROPS_LIBRARY_1`. |

**How BENCH runs the blind test:** give a FRESH agent `reviewer_packet.md` and nothing
else. Use a different model from the author's if possible, and never haiku, because the
gateway does not serve it. Score its answers against `answer_key.md` by hand, then apply
the bar above unchanged.

## Results so far

- **Prop table:** 45 rows, 0 provenance problems. The vision pass covered only 7 rows
  (our loose PNGs). The other 38 are vanilla/DLC sprites in `resources.assets`, so their
  legibility is UNMEASURED (GAPS S7).
- **Vignettes:** 8 authored, 7 valid. **`A3_daily_path` was refused by the validator.**
  Every ingredient that could be placed was LOW traceability, so "they walk this path
  daily" cannot be said with what exists. This is the traceability rule working. Under
  premise-then-subtract it is left out of the A dressing, so set A carries 3 intended
  claims and set B carries 4.
- **Gaps:** 6 unfilled ingredients and 7 structural gaps. The top three are wall blaster
  scars, directional traces (drag, footprints, worn path) and drift edges.
- **Correction to spec §6a:** across the live mod set, event traces are scarce but not
  absent. `Filth_BlastMark`, `Filth_BloodSmear` (a crawl trail) and `Filth_DriedBlood`
  already exist (GAPS §3). The spec has been amended to say so.
- **Verdict: PENDING.** It is owed to BENCH's blind run of `reviewer_packet.md`.

## Deviations from the plan (`narrative_dictionary_pilot_plan.md`), smallest faithful version

- Outputs live here, not in `infrastructure/state/narrative/` plus the 9 modules under
  `src/RimMandrake/Utils/narrative/`. One script, `build.py`, replaces sheets, vignettes,
  query, compose and evaluate. The two hard validators and their negative controls are
  kept.
- **There is no PIL composite.** Rooms are given to the reviewer as a grid plus labels.
  That adds a third proxy layer to the two in spec §7a: text is not pixels. Vanilla
  sprites were not extracted, and a composite built only from our 7 PNGs would have
  biased the comparison.
- The control approximates `structure_procedural_spec.md`'s R4/§3.4 clutter pass: a
  uniform draw from the same 40-defName salvage-bay pool, with random-start placement,
  70% preferring a wall, and seeds 1 and 2.
- The plan's Task 1 Step 1 was not done: the 12 retry sources were not read into spec §12.
- No query ranking or mood filter was built. Vignettes were resolved by hand against the
  table. The density ceiling (spec §8) was deferred, as the plan already said.
- The ledger item is not closed. That waits for the blind-run verdict.
