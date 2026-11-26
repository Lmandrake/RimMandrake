# BOUNDARY: a stopped or killed testq attempt leaves no Windows process of its own alive, Design Version 0.1.0

Code: `infrastructure/stevedesktop/worker.py` (`WIN_TAG`, `WIN_KEEP`, `tag_windows_python`, `windows_processes`,
`windows_tree`, `kill_windows_tree`, the tag in `Attempt.sh`, the Windows step of `Attempt.kill_child` and of
`cmd_stop`, `UNIT_KILL_MODE` in `spawn`). Item: `RIMMANDRAKE_KILL_WINDOWS_CHILD_ON_TESTQ_CANCEL_ORPHAN_DROVE_STEVE2`, written 2026-11-26. Each
promise has a test of its name in `infrastructure/stevedesktop/selftest_steve_worker_windows_tree.py`. This page covers
only these parts of worker.py; the rest of the file has its own pages.

The fault: `testq cancel --running` of J20261125T083122Z-dedc8e (2026-11-25) ended the worker, but thirst_live.py
(Windows pid 11336), started by live_session.py's python.exe, drove Steve2 for 20 minutes more. A killpg of the
attempt's bash kills the WSL interop shim, and the shim takes its own Windows python.exe with it, but Windows kills no
child of a dead parent (measured on Archmagi 2026-11-26: the direct child gone after TERM or KILL, its child alive with
a dead ParentProcessId).

## ACCEPTS (the only inputs this is built for)

- **a-worker-on-wsl-with-windows-tools.** The worker runs in WSL2 with `powershell.exe` and `taskkill.exe` on PATH or
  at their fixed paths under `C:\Windows\System32`. Both lanes run this worker: SteveDesktop's Steve1 and Steve2, and
  Archmagi's (`testq.archmagi_worker`).
- **a-python-exe-at-a-command-start.** A command that the worker runs through `Attempt.sh` and that starts a Windows
  python with `python.exe` at a command start (line start, after `&&`, `||`, `;`, `|`, `(`, or after `VAR=x`).

## DOES NOT SURVIVE (not promised)

- **a-python-exe-not-at-a-command-start.** A python.exe started by a Linux python3 through subprocess, or behind a
  prefix such as `timeout 60 python.exe` or a `VAR=$(...)` assignment with spaces in it, carries no tag; its Windows
  children are not found (its own python.exe still dies with its shim). Measured 2026-11-26: 1 of 471 live-proof and
  live-site lines (`BRIDGE_TPS_REVIEW2_FIXES_1.txt` C3, after `RM_DATA_ROOT=$(python3 -c '...')`).
- **a-windows-child-born-after-the-shim-died.** A child spawned between the Windows step and the killpg of the Linux
  side escapes; the window is one powershell read (about 2 s).
- **an-unreadable-windows-table.** When the table cannot be read, the stop goes on with the Linux side and says why
  (`windows_unread` in the stop's JSON line, `windows children: <why>` in worker.log); it ends no Windows process.

## PROMISES (each one is owed a test of the same name)

- **python-exe-carries-the-attempt-tag.** Each command-starting python.exe in a command that `Attempt.sh` runs carries
  `-X testq_attempt=<attempt id>` (CPython keeps an unknown -X option and ignores it); a python.exe inside an argument
  word is left alone; a command with no python.exe is unchanged.
- **windows-tree-is-the-attempts-own.** The tree is every process whose command line carries this attempt's tag, and
  their descendants by ParentProcessId. The tag must end where the attempt id ends (`.a1` is not `.a10`); a child
  created before its parent names a reused pid and is not followed; the game (`RimWorldWin64.exe`) and Steam, and what
  they started, are never in it: a phase decides their stop.
- **stop-ends-the-windows-grandchild.** `worker.py stop --attempt <id>` (what `testq cancel --running` sends) ends the
  attempt's Windows processes, its python.exe's own children included, before it stops the unit or signals the pid.
  A stop runs the runner clone's worker.py, which may be pinned to a job's older sha with no Windows step: so the
  attempt's unit has `KillMode=mixed`, and a `systemctl stop` alone sends SIGTERM to the worker only, whose
  `kill_child` ends the tree (with control-group every shim died at once and the child lived on: the unit scene of
  `--real-windows`, red with control-group planted, green with mixed, Archmagi 2026-11-26).
- **a-killed-command-ends-its-windows-grandchild.** When `Attempt.kill_child` kills a command (its deadline passed, or
  the attempt was stopped), it first ends that attempt's Windows processes, its python.exe's own children included.
