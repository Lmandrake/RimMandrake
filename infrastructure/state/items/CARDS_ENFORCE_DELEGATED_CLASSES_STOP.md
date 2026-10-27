# CARDS_ENFORCE_DELEGATED_CLASSES_STOP

Enforcement gap, not a new ruling. delegation_policy.md §1 already delegates work order and helper count (`scope`)
and §2.4 delegates applying a ruling to a case it does not name (twins: campaign copy, sister biome, all ages and
sexes). Agents still card him about both: 29 ordering/helper-count cards (81% agreement) and 9 twin cards (8 yes)
in 3 weeks (design/RimMandrake/delegation_candidates_2026-10-26.md §1 rows 1 and 5).

## Build
A check on the question-card path (the AskUserQuestion hook or the question-card skill's pre-send step; the
skill lives at ~/.claude/skills/question-card, outside the repo) that classifies a card's question and WARNS, then
REFUSES, when its only question is ordering / which next / helper count / rule now or later, or whether a ruling
applies to a twin. The refusal tells the agent to decide, log `--why "delegated: scope"` (or `delegated: twin`),
and list it in the digest. Text added to delegation_policy.md §1, BENCH.md and FOUNDRY.md on 2026-10-26.
## Verify
Replay the 29+9 historical cards: >= 90% flagged; a sample of 20 genuine §2 cards: 0 refused.
