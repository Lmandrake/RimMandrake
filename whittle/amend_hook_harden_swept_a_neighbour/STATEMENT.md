# AMEND_HOOK_HARDEN_SWEPT_A_NEIGHBOUR — done statement

Item (filed 2026-10-23, kind bug): the commit-pathspec PreToolUse hook let a bare `git commit --amend` through; in a
shared seat clone it swept the whole index (67633f878 took another helper's 8 staged FeverWood deletions). Refuse
`--amend` without a pathspec too (amend WITH paths is safe).

The fix landed at 9fd7d703c3 (blind PASS, 50/50). The deadman reopened the item 2026-11-08T20:33Z: "hook
block_blanket_git_stage.py is not wired". The Pyrelands landing 8fb9f7f2b6 clobbered `.claude/settings.json` and
dropped every safety hook; 943a7a66da restored it. Now it closes only with a class guard (`rimflow guard`).

- [ ] Bare `git commit --amend` (and the `--amend --no-edit`, `-m` and `-F` heredoc forms) is refused by the hook.
      Evidence: `.claude/hooks/selftest_block_blanket_git_stage.py` run at the closing sha, DENY rows.
- [ ] `git commit --amend <path>` and `--amend -- <path>` are allowed. Evidence: the same selftest, ALLOW rows.
- [ ] The hook is wired as registered (the command in `.claude/settings.json`, not just the script), and the
      registered command refuses a bare amend. Evidence: a run of the registered command line on a bare-amend payload.
- [ ] Class guard: a selftest that fails when `.claude/settings.json` stops wiring a hook that a running promise names
      (`hook=<name>` on the ledger or in `live_baseline.txt`). It is shown FAILING on the instance (the 8fb9f7f2b6
      settings) and passing on main, and recorded with
      `rimflow guard AMEND_HOOK_HARDEN_SWEPT_A_NEIGHBOUR --test <selftest> --instance ...`.
- [ ] Closed with the promise `hook=block_blanket_git_stage.py` holding at close (rimflow close's running-promise flag).
