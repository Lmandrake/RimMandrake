# RIMMANDRAKE_DESIGN_JUDGE_SAME_PROBLEM_MATCH_FOUR_ROUNDS_LOST

## spec

FINDING: RIMMANDRAKE_WRITE_JUDGE_FOUR_RULES_TWO_LOOK_LIMIT was meant to be judge prompt text plus a two-look limit. Four Codex lane rounds (2026-11-17, last ended 8:08 PM PST) each passed the acceptance case (`design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_four_rules_two_looks.py`, wrong 27 on base, 0 on the draft) and the six selftests, and each fresh review still returned FIX_FIRST with new reproduced defects, all in one place: how `coverage_judge.py` decides that a second-look finding is the SAME problem as a first-look one (a reworded still-open gap signed off as repaired; a new finding reusing an old id counted as the second refusal; an old release record granting an extra look; contradictory repair reports; evidence order). Round 4 ended with no commit: the publisher also selects `selftest_coverage_refusal_record.py`, whose repair fixtures fail three assertions under the draft, and that file was outside the builder's allowlist.

THIS ITEM: design first, no code. One page under `design/specs/2026-11-17-judge-flaws-not-polish/` that states what makes two findings the same problem (what identity is carried, who assigns it, what happens when the match is unsure: the repair stays open), enumerates the input regions (reworded, reused id, split, merged, moved passage, stale release record, contradictory reports), and names every test file the change must touch, `selftest_coverage_refusal_record.py` included. The four rounds' patches and reviews are the evidence: `D:\ClaudeWork\rimmandrake\conductor\codex_lane\RIMMANDRAKE_WRITE_JUDGE_FOUR_RULES_TWO_LOOK_LIMIT*`. The build is filed from that page as its own ticket, with its acceptance test.

Owner trial (2026-11-17, accepted): a reader-confirmed new problem quoting a repaired passage still blocks.

Acceptance test: none, this item produces a design page; the build ticket filed from it carries the test.
