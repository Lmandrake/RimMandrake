# Lessons inbox — one file per lesson, curated into skills in fresh-context passes

**Prefer writing a new lesson straight into the owning skill**; use this inbox only when no
skill owns it, and say which home you propose. File one with

    python3 src/RimMandrake/Utils/lessons.py add "<the lesson>" [--seat BENCH] --home <skill-or-doc|NONE>

which creates `infrastructure/state/lessons/<utc>-<seat>-<slug>.md`; commit that path. Curation
folds a lesson into its skill and **deletes its file**; the Auditor does it every week with a
budget (`roles/auditor.md`, owner 2026-10-29: "The Auditor once a week."). `LESSONS_INBOX.md` beside this folder is a
gitignored view — `python3 src/RimMandrake/Utils/lessons.py render` rebuilds it; never edit it.
Last drained 2026-11-07 (spring clean: about 1,750 of 2,005 folded into their owning skills and fact files, the rest kept for a second pass). How it was done, reusably: checked digests that classify each lesson covered, rule, merge or spent, then a script that applies them and deletes what landed (`D:\ClaudeWork\rimmandrake\conductor\spring_clean_2026-11-07\inv\`). Folded detail goes to a skill's `references/traps.md`, not its SKILL.md.
