## spec
🔴 **`AUTHORED_KINDS_MUST_FIELD_1`'s XML is ALREADY SHIPPED, and the item does not know it.**
Measured at HEAD by REP, 2026-08-26. `DeepDesertTribes.xml` and `BlackstarCompany.xml` both
carry that item's ID in their own section headers; `Jawa_Empire_Leader` is fielded through
`fixedLeaderKinds` in `GalacticEmpire.xml`. Only the in-game `verify` remains — spawn raids
from `TribeCivil`, `Pirate`, `Empire` — so the item is **awaiting bridge verification, not
ready work.**

⚠️ **REP may not edit BUILD's item file, which is why this exists.** Three corrections belong
at the TOP of `infrastructure/state/items/AUTHORED_KINDS_MUST_FIELD_1.md`:

1. **IMPLEMENTED — do not re-implement.** Name the two files and `fixedLeaderKinds`.
2. **Its ⛔ against `Inherit="False"` WAS OVERRULED, on evidence, and was never told.**
   `TribeCivil` inherits all twelve groups from the abstract `TribeBase`, PatchOperations run
   BEFORE inheritance resolves, and a Replace on the child matches **zero nodes** (verified
   with lxml against Core, 2026-08-22). The route taken declares the whole list on the child
   **and re-declares the eight non-combat groups byte-for-byte from Core**, which answers the
   objection the ⛔ was actually making. Read `DeepDesertTribes.xml` near line 132 first.
3. **The combat weights are TUNED PER GROUP and are not `GalacticEmpire.xml`'s numbers.**

## why it matters — measured, not hypothetical
A cheap-model BUILD trial (`KIMI_GATEWAY_FOR_BUILD_1`, 2026-08-26) was handed
`AUTHORED_KINDS_MUST_FIELD_1` cold, with Write enabled, in a throwaway worktree. It did not
notice the work was done. Told to copy the pattern `GalacticEmpire.xml` ships, it copied the
**numbers**, flattening Deep Desert's `10 / 5 / 6` and Blackstar's `10 / 5 / 3` to Empire's
`5 / 2 / 1.5`, and reported it as completed work.

🔴 **A 14-check structural grader passed that regression 14/14.** XML parsed, no
`Inherit="False"` regression, no vanilla kinds in a combat group, non-combat groups untouched,
both rosters still fielded. **Only `git diff` found the loss.** Grader:
`src/RimMandrake/Utils/grade_authored_kinds_trial.py`. Diff:
`research/nemotron_build_trial_2026-08-26.diff`.

## criteria
The three corrections are at the top of `items/AUTHORED_KINDS_MUST_FIELD_1.md`, and that item
reads as awaiting-verification rather than ready. ⚠️ **This is a doc fix and nothing else — do
not touch the three XML files. They are correct.**
