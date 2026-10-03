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
- **Verdict: PASS** (see "Blind test result" below).

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

## Blind test result

Blind reviewer: a fresh sonnet agent that read only `reviewer_packet.md`. Answers verbatim in
`blind_answers_2026-10-03.md`. Scored against `answer_key.md` with the bar above, unchanged.

| room | condition | claim | result | reason |
|---|---|---|---|---|
| W | B-dictionary | B1 looted | HIT | scavengers/raiders forced the lockers and stripped them |
| W | B-dictionary | B2 nobody for years | PARTIAL | "probably nobody remains", sand at the door; no "years" |
| W | B-dictionary | B3 fight at door, wounded crawled | HIT | blast at the door, fight, blood trailing inward; crawl direction not stated |
| W | B-dictionary | B4 smashed on purpose | HIT | consoles smashed, crossed-out crown read as a repudiated regime |
| X | B-control | B1 looted | HIT | "forced-open lockers... looted long ago" |
| X | B-control | B2 nobody for years | PARTIAL | nobody present, long dormancy; desert coming in not read |
| X | B-control | B3 fight at door | MISS | blood smear read as "a small injury" |
| X | B-control | B4 smashed on purpose | MISS | consoles smashed, no motive read |
| Z | A-dictionary | A1 sorted salvage | HIT | "materials are sorted" |
| Z | A-dictionary | A2 one worker sleeps at bench | HIT | a salvager/mechanic lives and works here |
| Z | A-dictionary | A3 family, child | PARTIAL | floordrawing: "perhaps a child"; "possibly a family or partners" |
| Y | A-control | A1 sorted salvage | MISS | not read |
| Y | A-control | A2 one worker sleeps at bench | PARTIAL | camp, lived-in, bedrolls; no workshop or bench worker |
| Y | A-control | A3 family, child | MISS | not read |


- Totals over 14 scored claims: 6 hits, 4 partials, 4 misses. Dictionary (W+Z, 7 claims): 5 hits, 2 partials, 0 misses. Control (X+Y, 7 claims): 1 hit, 2 partials, 4 misses.
- Strict count (partial = not recovered): dictionary 5 vs control 1 = 5x. Lenient (partial = half): 6 vs 2 = 3x. Both clear 2.0.
- False claims: dictionary 0. Control 1 (Room Y: "they may have left in a hurry or died... I lean toward left" for a tended, lived-in room; also tally marks read as a prisoner count). 0 <= 1.
- intended_total = 7 >= 4.
- Confidently wrong: none. Z was "high" and correct. The control's errors (Y, X) were all low to medium confidence.
- Part 2 (diagnostic): S1, S2, S4, S6, S8 HIT; S5 and S7 PARTIAL (S5 lost "wounded defender crawled away", S7 lost "family"); S3 refused. Part 1 dictionary misses are placement-free: the props carry nearly every claim.

**Verdict: PASS.** Result holds under the strict and the lenient count. Caveats: one reviewer, one room plan, one control seed pair; text grids, not pixels (third proxy layer); the control happened to include many of the same wall and floor props, so its hits come from the shared pool. New gaps from the partials: GAPS.md section 5.
