# Lessons inbox — one file per lesson, curated into skills in fresh-context passes

**Prefer writing a new lesson straight into the owning skill**; use this inbox only when no
skill owns it, and say which home you propose. File one with

    python3 src/RimMandrake/Utils/lessons.py add "<the lesson>" [--seat BENCH] --home <skill-or-doc|NONE> [--item <ID|NONE>]

which creates `infrastructure/state/lessons/<utc>-<seat>-<slug>.md`; commit that path. `--item` names the item you
learned it on (default: the session's `$RIMFLOW_ITEM`, else the Whittle loop's `$WC_ITEM`). The daily agent-improvement
pass reads the lesson's task kind from it, and a change built on lessons with no item cannot have its generalization
checked (design `daily_agent_improvement_2026-11-02.md` 4.3). Curation
folds a lesson into its skill and **deletes its file**; the Auditor does it every week with a
budget (`roles/auditor.md`, owner 2026-10-29: "The Auditor once a week."). `LESSONS_INBOX.md` beside this folder is a
gitignored view — `python3 src/RimMandrake/Utils/lessons.py render` rebuilds it; never edit it.
Last drained 2026-11-07 (spring clean, two runs: every lesson folded into its owning skill or fact file, or spent, except one a companion `.cs` comment cites). How it was done, reusably: checked digests that classify each lesson covered, rule, merge or spent, then a script that applies them and deletes what landed. Folded detail goes to a skill's `references/traps.md`, not its SKILL.md.
