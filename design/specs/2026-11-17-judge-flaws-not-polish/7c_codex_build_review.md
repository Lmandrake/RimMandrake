Full-file review completed against all four inlined files. I ran isolated Python reproductions of the relevant functions; I did not run the repository’s full suite.

1. **Exact JSON quotes can become advisory, allowing signing over a repair defect.** `coverage_judge.py:533`

   `changed_passage()` removes JSON escapes before comparing against stored JSON that retains them. For example, add this scene:

   ```python
   entry = {"id": "sc_wall", "asserts": 'the label reads "wall" after the blast'}
   since = "scene:sc_wall\n" + json.dumps(entry, ensure_ascii=False)
   ```

   This copies exactly what `delta_prompt()` shows. With the scene absent before and present afterward, `changed_passage()` nevertheless returns `None`. Reproduction through `classify_new()` produced `covered`, zero blocking gaps, and `short_list: true`.

   With the old slots repaired, passing rows, calibration, and unchanged inputs, signing proceeds despite this reported repair defect. Preserve the rendered passage’s escapes when comparing it.

2. **A new finding tagged `first` incorrectly reopens an old slot on unchanged material.** `coverage_judge.py:497`

   Concrete input: `g1` owns `leaf_wall`; its repair answer is true; its checklist row passes. Return a different finding with:

   ```json
   {"ids":["leaf_wall"], "new_since":"first", "since":""}
   ```

   The code attaches it to `g1` because `first` is outside `NEW_TAGS`. Reproduction returned zero closed slots and one open slot. Changing only its tag to `late` closed the slot.

   Design rule 2 permits row-based naming for an `unfixed` report; this valid schema value broadens that rule. The resulting second refusal blocks on the original gap instead of making the new, unchanged-material finding advisory. The same broad condition occurs in `reopen_named()`.

3. **A successful released look does not consume the release.** `coverage_judge.py:711`

   Concrete state:

   ```python
   coverage_rounds = [j1_not_covered, j2_not_covered, j3_covered]
   coverage_releases = [{"judges_at": ["j1", "j2"]}]
   ```

   Using one token per round, the actual `stop_reason()` returns `None`. After another covered round, it still returns `None`. The legacy release form behaves likewise.

   After `j3` signs, an artifact edit invalidating that signature can therefore launch another judge under the same release. Only a refusal consumes it; covered looks accumulate until a separate cap intervenes. Record consumption of the first usable released look.

4. **Malformed repair answers silently activate legacy closure.** `coverage_judge.py:1478`

   A response containing `"repairs": null`, `{}`, or a string passes `ask()`’s structural checks and becomes `repairs=None`. With passing checklist rows and no findings, `_slots()` closes `g1` despite receiving no repaired answer.

   All three inputs reproduced that closure. The design reserves legacy behavior for an **absent** `repairs` key. Reject malformed present values, or keep their slots open.

5. **The reader-spend assertion passes when reader spend is discarded.** `case_same_problem_identity.py:352`

   The recorded judge row omits `tokens`, so it already contributes the p90 fallback. Consequently, `CJ.spend(rs) >= 7` passes both with and without the reader’s seven tokens.

   Reproduction: correct spend `684913`; reader tokens discarded: `684906`; both assertions pass. Give the recorded judge five tokens and assert an exact total of twelve.

The supplied fixes address the named delta-scope drop and reasked-record reopening paths. Static tracing also preserves reworded `unfixed` reports, duplicate contradictory repair answers, evidence-order independence, timeout/error baselines, calibration gating, and stopping at two ordinary refusals. Findings 1–3 expose remaining variants of the quote, identity, and release problems.

Advice, nonblocking: `coverage_judge.py:451` still describes carried-gap closure through passing rows alone. Include the required repaired-slot answer in that prompt sentence.

VERDICT: FIX_FIRST