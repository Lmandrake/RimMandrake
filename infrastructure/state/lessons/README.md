# Lessons inbox — one file per lesson, curated into skills in fresh-context passes

**Prefer writing a new lesson straight into the owning skill**; use this inbox only when no
skill owns it, and say which home you propose. File one with

    python3 src/RimMandrake/Utils/lessons.py add "<the lesson>" [--seat BENCH]

which creates `infrastructure/state/lessons/<utc>-<seat>-<slug>.md`; commit that path. Curation
folds a lesson into its skill and **deletes its file**. `LESSONS_INBOX.md` beside this folder is a
gitignored view — `python3 src/RimMandrake/Utils/lessons.py render` rebuilds it; never edit it.
Last drained 2026-09-23 (308 of 337 entries folded into their owning skills).
