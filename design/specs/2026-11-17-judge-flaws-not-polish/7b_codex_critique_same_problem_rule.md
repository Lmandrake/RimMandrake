The design needs changes. Row identity still permits both false closure and false refusal, and “changed entry” is weaker than the owner’s “changed passage.”

This is a static review of every line of the supplied files; I did not run tests.

### 1. Concrete wrong outcomes

**A repaired gap blocks because a different problem names the same row.**

Input:

- First look: `g1`, ids `["wall"]`, refuses the missing test that steel arrows stop at stone walls.
- Repair: that test is added and correctly exercises the promise.
- Second look: the judge writes `wall` with nonempty, all-ok parts. It also reports an independent error in an **unchanged tooltip**, naming `["wall"]`: the tooltip incorrectly says steel arrows pass through stone walls.

Rule 2 prevents closure because a finding names `wall`. Rule 3 refuses using the original missing-test record, although that test now exists. Rule 4’s protection for new findings never applies.

Calling the tooltip finding a note does not fix the outcome: judging stops on an obligation already satisfied. This reproduces the substance of the earlier “new finding reusing an old row” review failure.

**Changing the reported row can also sign an unrepaired gap.**

Input:

- Inventory row `wind` and leaf row `spread` describe the same directional-spread capability.
- First look: `g1`, ids `["wind"]`, says the scenes never distinguish directional spread from “always spreads east.”
- The Designer files a claim, triggering another look, but supplies no effective repair.
- Second look: `wind` has nonempty, all-ok parts; a finding naming only `["spread"]` explicitly reports that same missing control. Its quoted material is unchanged.

Under the numbered rules, `g1` closes because its own row is all ok and no finding names it. The `spread` finding is new and advisory. Rule 5 yields `covered`, and the remaining signature checks can pass.

The table assumes that when a finding moves to another row, the original row will be failing or absent. That assumption is not enforced. This is a specific contradictory answer the proposed fail-safe does not survive.

**An unchanged passage qualifies when an unrelated passage in its entry changes.**

For example, the rendered `sheet:Combat` entry initially contains:

```text
## Combat
The tooltip says steel arrows pass through stone walls.
Fire-test note: pending.
```

The repair changes only `pending` to `complete`, alongside a genuine repair of an earlier fire-test gap.

The second judge reports a new `wall` problem, names `sheet:Combat`, and quotes:

```text
The tooltip says steel arrows pass through stone walls.
```

It assigns `severity: problem`; the reader confirms seriousness.

Rule 4 accepts this: the **entry** changed and the quote occurs verbatim in its current text. But the quoted passage and its defect are unchanged. The new problem blocks in violation of the owner’s rule. Verify the quote against the changed passage, rather than merely against an entry containing some change.

**A failed attempt erases the baseline that activates the rule.**

This follows from the existing full-file control flow:

1. A well-formed first refusal containing `g1` is saved.
2. The attempted repair check times out or ends malformed.
3. `run()` overwrites `coverage_verdict.json` with that attempt. `prior_verdict()` subsequently returns `None`.
4. The retry receives a full review without the prior refusal record or its usable hash baseline.

The design expressly applies its new rules only when the prior verdict **on file** is `not_covered`. This retry escapes that scope.

A concrete retry finding on unchanged row `B`, tagged `changed`, survives the existing `tag_gaps()` handling; no prior hashes are available to `retag_against_prior()`. With a valid experience refusal and a sound reader grade, it can block unchanged material. The earlier refusal’s round summary survives, but that summary cannot supply the lost original record.

Keep the last usable verdict independently of failed attempts.

For counting: the pasted code still has `NOT_COVERED_LIMIT = 3`; the design explicitly promises to change it. With that value changed to two and release boundaries corrected, I find no additional ordinary path past **two recorded refusals**. An authorized release is the stated exception.

### 2. Missing or contradictory table regions

The table needs these cases:

- Original rows all ok, but the same unresolved defect is reported under different rows.
- A finding mixing prior-gap rows with genuinely new rows.
- A changed entry containing an unchanged quoted passage.
- A failed or malformed attempt followed by a retry after the prior verdict was overwritten.
- Advisory-only findings accompanied by failing checklist parts.

The last case also exposes a contradiction already in the page. Rule 5 says advisory-only findings produce `covered`; the table says `covered` with a failing row **or gaps** produces `not_covered`. A repaired prior gap plus a new unchanged-material advisory finding satisfies both descriptions. The table must preserve advisory status.

### 3. Phantom reader rounds and releases

**The phantom finding is real.**

`llm_reader()` charges reference `unit + "-reader"`. That reference starts with `UNIT_PREFIX`, while `rounds()` excludes only references exactly matching recorded judges. It consequently invents a legacy round for the reader charge.

For one recorded judge `J` and charges for `J` and `J-reader`, `rounds()` returns the phantom reader round followed by the recorded judge. Folding reader spend into its parent judge removes the phantom while retaining its cost.

**Resolving legacy releases against the old list is the right approach.**

For example:

```text
old list before release: [J1-reader, J1, J2, J3]
stored rounds_at:        4
correct judge boundary:  {J1, J2, J3}
```

After `J4` refuses, slicing the filtered list at index four incorrectly grants another look. Resolving the old prefix to actual judge identities correctly leaves `J4` after the boundary.

During that conversion, retain actual judge records from the prefix; discard phantom records. Do not promote a phantom reader reference into its parent’s presence before the boundary.

New-format releases should identify their boundary unambiguously. “Earlier wins” is conservative, but raw counts from different formats must first be converted into comparable boundaries. The supplied code establishes the mechanism; it does not independently establish the named concepts’ measured histories.

### 4. A simpler rule

Use the program’s existing first-look gap numbers as fixed repair questions:

1. Present each original refusal in a program-selected slot: “Is **this recorded hole** repaired? Give evidence.”
2. Preserve unresolved refusals as their original records.
3. Assess additional findings separately, regardless of overlapping checklist rows. Require an actual changed-passage quote, `problem` severity, and reader confirmation.
4. Derive the verdict from those results, preserve the baseline through failed attempts, and stop after the second refusal.

This removes identity matching without equating every defect within one checklist row. It still trusts the judge’s repair assessment, as the proposed rule does. No syntactic identity scheme can reconcile every contradictory semantic judgment automatically.

Advice: keep row ids for checklist completeness, and add these concrete counterexamples to the acceptance cases.

**VERDICT: FIX_FIRST**

- Row identity can retain a repaired refusal or close an unrepaired one.
- Entry-level change verification permits blocking unchanged problems.
- Failed attempts can erase the baseline and bypass the proposed protection.
- The table contradicts rule 5 for advisory findings with failing rows.