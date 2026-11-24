## Repo hygiene
- Commit explicit paths only. Never use `git add -A/./-a` (`git add -A`, `git add .` or `git commit -a`), `--force`, `reset --hard`, `checkout --`, `stash` or worktrees.
- Keep writes and commits in separate Bash calls. Use `./publish` to push.
- Before you stop, leave the tree clean: commit, or write a clear handoff note that lists your uncommitted paths.
- Deploys and builds:
  - `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod <name>` makes a plan. Add `--apply` to write.
  - For C# builds, use `python3 src/RimMandrake/Utils/winbuild.py`.
- The packageId is `mandrake.<tier>.<mod>`. The prefixes are `RM_`/`RSW_`/`RUT_`.
- Code is CLEAN when its boundary page has a passing test for each promise: `python3 src/RimMandrake/Utils/code_review_status.py check <path>`
  reads CLEAN, DIRTY, UNREADABLE or NO PAGE. A reviewer fixes each significant finding, test first. One blind reread
  checks the fix. If the reread also fixes a significant finding, flag the file (`code_review_status.py flag`).
- Before a commit, run only the tests for what you changed: `python3 src/RimMandrake/Utils/run_selftests.py --only <tests>`.
