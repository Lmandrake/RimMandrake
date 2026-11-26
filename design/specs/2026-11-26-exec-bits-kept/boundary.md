# Boundary: the exec bit of a script that is run directly

Code: `src/RimMandrake/Utils/selftest_exec_bits.py`, run by `./publish` (`src/RimMandrake/Utils/publish_tree_checks.json`).

## Why

A systemd unit or a desktop shortcut that runs a repo script by its path needs mode 100755 in git. When an edit
rewrites the file and drops the bit, the unit fails at once with `status=203/EXEC ... Permission denied`, and nothing
else turns red. Measured: commit 66512f784d (2026-11-25) dropped the bit of `src/RimMandrake/Utils/findings_judge.sh`
and `infrastructure/stevedesktop/claude_session.sh`. The 2026-11-26 07:20 PST daily findings judge did not start, and
the UNTRIAGED alarm rang on OPS_FINDINGS_DIAGNOSE_XZLM.

## ACCEPTS

- Every tracked unit file (`*.service`, and `*.service.d/*.conf`). It reads each `Exec*=` line.
- The first word of an `Exec*=` line, after the prefixes `-@:+!`. A path under `/home/mandrake/rm/<clone>/` or
  `%h/rm/<clone>/` names a repo file.
- The list `DIRECT` in the selftest: scripts that something outside a unit runs by path, each with its caller.

## PROMISES

- **units-name-their-scripts.** The parser reads the repo path out of a unit's `Exec*=` line, for `/home/...`, `%h/...`
  and a `-` prefix. An interpreter (`/usr/bin/python3`) is not a repo file.
- **tree-finds-the-judge.** On the real tree, the scripts that the units run include `findings_judge.sh`. So the
  derived list is never silently empty.
- **run-scripts-keep-exec-bit.** Each script that a unit runs, and each script in `DIRECT`, is mode 100755 in the git
  index.

## DOES NOT SURVIVE

- A script that a unit runs through an interpreter word (`/bin/bash x.sh`). That path needs no bit, and it is not
  checked.
- A caller outside a unit that is not in `DIRECT`. Add it to `DIRECT` with its caller.
