# RIMMANDRAKE_CRYSTALLIZE_KNOWLEDGE_EVIDENCE_MOVES_NEVER_VANISHES

## spec
Crystallize lane 1: merge CLAUDE.md against the rulings files, and the auto-memory folder, under the merge-do-not-concatenate gate. Brief: `D:\ClaudeWork\rimmandrake\conductor\briefs_20261119\crystallize_knowledge.md` (the whole work order; skill `crystallize`). Owner, 2026-11-19 10:45 AM PST: "Let's crystallize now."

## criteria
Nothing checkable is lost: every quote, date, number, path and id of a rewritten file is findable in the rewritten file or a file its evidence moved to.

## verify
`python3 ~/.claude/skills/crystallize/scripts/checkable.py compare git:HEAD:<file> <file> --also <history files>` exits 0 for every rewritten file; the selftests that read CLAUDE.md stay green.
