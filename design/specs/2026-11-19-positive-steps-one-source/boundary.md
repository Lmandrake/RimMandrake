# BOUNDARY: the owner's "positive steps" text has one source, Design Version 0.1.0

Source: `.claude/rm_positive_steps.md` (two lines, his words). Check: `src/RimMandrake/Utils/selftest_positive_steps_one_source.py`.
Item: `RIMMANDRAKE_SHARE_POSITIVE_STEPS_TEXT_FOUR_COPIES_DRIFTED`, written 2026-11-19. On 2026-11-17 the owner caught a copy that
had lost the text: *"Those were in the prompt that worked! Why are we dropping that?"* Before this page the text lived in
four files and two Python briefs, and the agent files and the two briefs had each lost two of his sentences ("Provide bars
where they are missing... Create instruments to prove your diagnoses."). Same mechanism as `.claude/rm_agent_shared_block.md`.
Each promise has a test of its name in the selftest.

## ACCEPTS (the only inputs this is built for)

- **a-carrier-file-or-brief.** The three files (`src/RimMandrake/rimflow/roles/builder.md`, `.claude/agents/rm-builder.md`,
  `rm-fixer.md`) and the two texts built in Python (`maturation.HOW_A_BAR_HOLDS`,
  `testpilot_route.HOLDS_LINES`), compared after collapsing runs of whitespace (a markdown line wrap is not an edit).

## DOES NOT SURVIVE (not promised)

- **a-fifth-carrier-nobody-listed.** A new file that copies his text is not found unless it is added to the check's list.
  A sweep of `src/`, `.claude/` and `skills/` on 2026-11-19 found only the six above (and selftests that quote the text).

## PROMISES

- **an-edited-copy-is-refused.** A carrier whose copy of either source line differs by one word fails, naming the carrier.
- **a-missing-copy-is-refused.** A carrier that lacks either line, or an absent carrier file, fails, naming it.
- **an-edited-source-refuses-every-carrier.** A source edited without its copies fails every carrier.
- **a-missing-or-empty-source-is-refused.** An absent source, or one with fewer than two lines, fails; it never passes.
- **the-real-tree-is-clean.** All six carriers hold both lines word for word.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
