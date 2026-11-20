# BOUNDARY: the logon shortcut for `./pages`, Design Version 0.1.0

Code: `src/RimMandrake/Utils/pages_logon_shortcut.py`. Tests: `src/RimMandrake/Utils/selftest_logon_shortcut.py`, one `t_<promise>` each.
Why: the owner's card answer, Thu 2026-11-19 10:17 PM PST, *"At every logon (Recommended)"* (question: *"When should the three status tabs open?"*).

## ACCEPTS
- **a-windows-user-with-startup-folder.** `powershell.exe` reaches Windows from WSL2; the Startup folder is asked of Windows, never written as a path.
- **a-repo-checkout-with-pages.** `--repo` (default `/home/mandrake/rm/bench`) holds an executable `pages`.

## DOES NOT SURVIVE
- **no-wsl-at-logon.** If WSL cannot start at logon, nothing opens and nothing says so.
- **reboot-while-away.** A reboot opens the Chrome window too (the cost the owner accepted).

## PROMISES
- **shortcut-runs-pages-minimized.** The `.lnk` target is `wsl.exe`, its arguments run `<repo>/pages` (no `--show`), its window style is 7 (minimized, no activation). Tested by `t_shortcut_runs_pages_minimized`.
- **no-fullscreen-no-focus.** The command carries no `--show`, kiosk, app or fullscreen flag. Tested by `t_no_fullscreen_no_focus`.
- **uninstall-removes-only-ours.** `--uninstall` deletes `RimMandrake pages.lnk` and nothing else; a missing shortcut is reported as absent, exit 0. Tested by `t_uninstall_removes_only_ours`.
- **dry-run-writes-nothing.** `--dry-run` prints the plan and writes nothing. Tested by `t_dry_run_writes_nothing`.
- **missing-pages-refused.** A repo with no `pages` exits 3 and writes no shortcut. Tested by `t_missing_pages_refused`.
