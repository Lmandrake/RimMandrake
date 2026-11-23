# RIMMANDRAKE_REWRITE_SKILL_GRAVSHIP_LAYOUT

Caused by RIMMANDRAKE_LAUNCH_REMAINING_PLAIN_ENGLISH_BATCHES_ELEVEN_LEFT (2026-11-23). The rewrite's parent item is `RIMMANDRAKE_REWRITE_RULE_DOCS_PLAIN_ENGLISH_LOSE_NOTHING`. His words are on it: "let's make sure we're not being oracular or obtuse, without losing information ... This is very important."

## spec

This item is one unit of the plain-English rewrite. Its batch is the row `RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH` of
`design/specs/2026-11-19-plain-english-rule-docs/batch_plan.md`. Obey that row's "special rule" column too.

Files:

- `skills/gravship-layout/SKILL.md`

Special rule: This is a curation session for ONE skill: `CLAUDE.md` allows a skill edit only in a fresh-context curation session, and this run is one. Never change the skill's `description` in its front matter: the description decides when the skill loads (change one only with the trigger evals of `skill-creator`). A skill keeps its lessons. Evidence that leaves the active file moves to `references/history.md` beside the skill (`skills/README.md` §Lessons stay); name that file on the result file's `Also:` line. Rewrite only `SKILL.md`; the skill's other files are not in scope. This skill is read by path.

Read first, in full: `batch_plan.md` (the writing rules, the two no-loss checks, the STE target, the worked example).
Read `~/dev/MandrakeWorkflows/skills/clear-findings/SKILL.md` before you write. Read one earlier result file for its form,
for example `design/specs/2026-11-19-plain-english-rule-docs/results/RIMMANDRAKE_REWRITE_OPERATIONS_ROLE_ONE_OF_TWO_SWITCHED_ON.md`.

Do the work as the plan says:

1. Before your first edit, record the base commit (`git rev-parse HEAD`). The result file holds it as the line
   `Base: <commit>`. Each no-loss check reads the old text as `git:<commit>:<path>`.
2. Rewrite each file in Simplified Technical English. Lose no rule, number, path, name, date or owner quote. Never
   rewrite his quoted words. Do not change what any rule means. Where two files disagree, list the conflict; do not pick.
3. A line that a cold reader cannot act on gets a plain sentence. If you cannot find its meaning in the code or the
   rulings, leave the line and list it under "Could not determine", with who would know.
4. Run both no-loss checks. Watch each check fail on a planted loss first. Run the STE lint and the tests that read
   your files (`git grep -l <file name> -- '*selftest*' '*accept*'`).
5. The meaning read is required before you publish. Start exactly ONE kind of helper: a fresh Opus subagent per file
   (Agent tool, model opus). The subagent gets the old text and the new text, and lists each line whose meaning
   changed, was weakened, or was lost. The subagent does not get your reasoning. Fix what it finds. The slot rule of
   RIMMANDRAKE_ALLOW_REWRITE_BATCH_ITS_ONE_MEANING_READER allows one reader at a time. Start no other helper.
6. Write the result file `design/specs/2026-11-19-plain-english-rule-docs/results/RIMMANDRAKE_REWRITE_SKILL_GRAVSHIP_LAYOUT.md`. It holds the `Base:`
   line, the scores before and after, the hand count, a heading `## What the meaning read found` with its findings
   and your repairs, the conflicts, the lines that you could not determine, and what you did not test. When a rule
   moved to a home file, name the home files on one line `Also: <path>, <path>`.
7. Land with one `./publish` with explicit paths. If another run changed one of your files meanwhile, re-apply your
   rewrite on the new text; never drop the other run's lines.
8. Close the item when the check in ## verify holds. Otherwise leave a note that starts `LEFT OPEN:` and names the
   files or sections that are left.

Final report, in Simplified Technical English: the scores before and after per file, what the meaning reader found
and what you fixed, the lines that you could not determine, the conflicts, and what you did not test.

## verify

Acceptance test: `python3 design/specs/2026-11-19-plain-english-rule-docs/batch_done.py check RIMMANDRAKE_REWRITE_SKILL_GRAVSHIP_LAYOUT skills/gravship-layout/SKILL.md` prints `HOLDS RIMMANDRAKE_REWRITE_SKILL_GRAVSHIP_LAYOUT` and exits 0. On base `835d2d3398` it printed `FAILS RIMMANDRAKE_REWRITE_SKILL_GRAVSHIP_LAYOUT` (no result
file), exit 1. The checker's own planted cases: `python3 design/specs/2026-11-19-plain-english-rule-docs/batch_done.py
selftest` prints `GREEN: 0 failed (12 planted cases)`.

## criteria

- Each file of the item is rewritten, and `rule_doc_lint.py keep` loses nothing against the base commit.
- A fresh Opus reader compared the old and new text of each file. Each finding is repaired or listed.
- The result file holds the scores, the hand count, the conflicts and the lines that could not be determined.
