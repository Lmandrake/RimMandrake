## Context discipline (why: every call re-sends your whole conversation — cost grows with every line you let in)
- Your context auto-compacts at 150k tokens. Compaction keeps a summary, not the details. So your PROGRESS FILE is your memory.
  - Write the progress file as a skeleton first.
  - After each step, record in the progress file your decisions, your pending operations, your evidence paths and your next action.
  - After any compaction, read the progress file again.
- Never let bulk output into your context.
  - Send long command output to a file (`cmd > out.txt 2>&1; rc=$?; tail -n 30 out.txt`, then report `$rc`). Then grep that file.
  - When you pipe, use `set -o pipefail`.
  - When you know the region of a file, read the file with offset and limit.
  - Do not cat or print logs, diffs, JSON dumps, or whole files that you will not edit.
- Images: view only the images that you must judge, at most 1500 px on a side. Crop to the subject. Do not view whole screenshots again and again.
- Load a skill only when the step needs it, once.
- Stop at the end of your assigned item or batch. Do not go looking for more work. Report, and the parent briefs a fresh helper. A defect that you meet on the way follows "Touching code has a cost" below.
- Before you stop, leave the tree clean: commit, or write a clear handoff note that lists your uncommitted paths.
- Return ≤10 lines: verdict, ids, shas, evidence paths, and what is owed. Put a big result in a file, and return its path.

## Project rules you would otherwise get from CLAUDE.md (it is NOT loaded — it cost ~23k tokens per call)
Before you act in an area, run `grep -n -i '<topic>' /home/mandrake/rm/bench/CLAUDE.md`. Read only the matching lines and the file that they point at. The essentials:
- Clones: work in the clone that your parent names (the seat clone /home/mandrake/rm/bench, or a pool clone).
  - FOUNDRY and its clone are retired.
  - `D:\Luke\dev\RimMandrake` is a read-only mirror. Never write to the mirror.
  - Each path that you report to the owner is absolute and Windows-native (`D:\Luke\dev\RimMandrake\...`).
- Agent scratch, builds, backups and logs go under `D:\ClaudeWork` (`/mnt/d/ClaudeWork/rimmandrake/...`), never in `~/dev` or the repo.
  - If a human reads the output once, put it in `Transient/`. If a program reads the output, put it in scratch.
- The game reads `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`, never the repo. So writing a file is not deploying it.
  - `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod <name>` makes a plan. Add `--apply` to write.
  - For C# builds, use `python3 src/RimMandrake/Utils/winbuild.py`.
  - Parse `ModsConfig.xml`; never grep it. `ModsConfig.xml` describes the NEXT load.
- Never guess a defName, field or namespace. Read it from the def, the About.xml, or `measure`.
  - A count about a large artifact comes from `measure`.
  - Treat a count that is round, zero or alarming as a query bug. That count stays a query bug until a sanity probe proves that the instrument can see (`infrastructure/state/facts/instrument_traps.md`).
- Engine traps:
  - `Plant` ticks only `TickLong()`.
  - The game ignores `MayRequire` on a top-level `<Operation>`. Use PatchOperationFindMod instead.
  - A patch that matches nothing logs nothing.
- Names:
  - The packageId is `mandrake.<tier>.<mod>`. The prefixes are `RM_`/`RSW_`/`RUT_`.
  - Name each new queue item `RIMMANDRAKE_VERB_INTENTION_TWIST`. Older names stay valid. Check a name with `rimflow namecheck`.
- Use the ledger only through `python3 src/RimMandrake/rimflow/cli.py` (skill `using-rimflow`). The provenance flags are:
  - `--owner-said`: his words;
  - `--by-card`: a decision that he took by question card;
  - `--per-ruling`: a standing ruling, cited by reference;
  - `--why`: your own words.
- Code is CLEAN when its boundary page has a passing test for each promise: `python3 src/RimMandrake/Utils/code_review_status.py check <path>`
  reads CLEAN, DIRTY, UNREADABLE or NO PAGE. A reviewer fixes each significant finding, test first. One blind reread
  checks the fix. If the reread also fixes a significant finding, flag the file (`code_review_status.py flag`).
- Before a commit, run only the tests for what you changed: `python3 src/RimMandrake/Utils/run_selftests.py --only <tests>`.
- Standing rulings that you must not contradict:
  - no worldgen of any kind;
  - a biome of ours on 0 tiles is expected, not a defect;
  - every DLC is assumed;
  - never live-test a flyer's flight;
  - the Conductor launches every FlowWorks and GSS build directly, as a helper in the Maturation Pipeline (owner, 2026-11-13 and 2026-11-18). GSS is Gimme Some Slack;
  - every pipeline before the Maturation Pipeline is retired (owner, 2026-11-13 and 2026-11-18);
  - FOUNDRY is retired (its items are the Conductor's, ledger key BENCH);
  - nothing reaches the owner unread;
  - wrong material is deleted, not superseded. Fix every inbound reference.

  A reset or clean-up of a test scene is harness housekeeping (save before, reload after; owner 2026-11-17). A reset or clean-up is never a mod deliverable, a coverage gap, or a Problem or Polish finding.
- Never name a GenAI account, host or key in code. Read the environment.

## Repo hygiene
