# RimWorld 1.6 — Jawa scavenger clan on a desert world

Read `infrastructure/agents/POLICY.md` and your own `infrastructure/agents/<SEAT>.md`.
They are short. This file is only what neither of them covers.

## Facts you cannot guess

- **The game reads `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`,
  never this repo.** Writing a file is not deploying it.
- **A cold load is ~25 minutes.** A quicktest map is ~90 s and answers most things.
  Never say "restart and see".
- **`ModsConfig.xml` is the live mod list**, at
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`.
  Read it for the active count; never a number written in a doc.
- **Never guess a defName, field, or namespace.** Read the def, the `About.xml`, or
  `strings -a -el` the assembly. Plain `strings` misses UTF-16 method bodies.
- **A patch that matches nothing logs nothing.** `PatchOperationConditional` and
  `PatchOperationFindMod` both return true on no match.

## Git

- **Commit explicit paths. Never `git add -A`, `git add .`, or `git commit -a`.**
  Enforced by `.claude/hooks/block_blanket_git_stage.py`.
- **`git commit <path>` commits the working tree at that path, not your index** —
  including a peer's uncommitted edits. Read `git status --porcelain <paths>` first.
- **Push immediately after committing.** Rejected push → `git pull --rebase`, never
  `--force`.
- **Never commit a file over ~50 MB.** GitHub hard-rejects at 100.

## What is where

```
src/                    mods, defs, C#, art          BUILD owns
design/                 campaign specs (Utinni)      DECIDE owns
skills/                 tooling + how-to           the seat that USES it owns it
                                                   broadly shared -> REP
infrastructure/state/   queues, V1.md, facts/        see POLICY.md
```

## Tools

```
python3 src/RimMandrake/Utils/status_server.py     the board -> http://localhost:8787
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod <name> --plan
python3 src/RimMandrake/Utils/refresh.py           rebuild the offline def dump
python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs ...
./src/RimMandrake/Utils/show.sh <path>             open it in Explorer
```

Paths in prose are always full and native, in backticks:
`D:\Luke\dev\Rimworld\infrastructure\state\V1.md`.

## Skills

Load themselves off their description when the task matches. The roster is
`skills/README.md`. The ones you will actually reach for:
`rimworld-modding` · `rimworld-deploy` · `rimworld-load-round` · `rimbridge` ·
`efficient-subagents` · `generating-rimworld-sprites`.
