# CONDUCTOR_RESTART_EXPLAIN_ZSH_TOOK_THE_BLAME

Written by an outside session (EMERGENCY window, cwd `/mnt/d/Luke/dev`) at the owner's request,
2026-10-28 ~19:10 PDT: *"Please write up all your findings for Conductor to know."*
Close this once each NEXT below is done or re-filed.

## Why you were restarted

From the phone, the owner saw the first v3 Conductor session (`3b6a848e`, 18:36 PDT) as a run of
failed jobs appearing and disappearing, with no chat reply to him. He asked whether the cause was the
working directory or the clone.

- **It wasn't the cwd.** Every seat ran in its right directory (BENCH `/home/mandrake/rm/bench`,
  FOUNDRY `/home/mandrake/rm/foundry`). No subagents or `claude -p` workers had run either: the
  Dispatcher logged "nothing to do" on every tick.
- **The "failures" were the Conductor's own Bash calls exiting non-zero:**
  - **zsh `NOMATCH`**: the login shell was zsh, which errors on an unmatched unquoted glob, so
    `grep --include=*.md`, `ls ~/.claude-accounts/*.sh` and similar bash idioms failed with
    `(eval):1: no matches found`. 3+ times.
  - **A `find /` sweep** crawled drvfs, hit the 120 s timeout and was killed. That breaks the global
    rule: scope searches to `~/dev`, `~/GDrive` and `~/checkout`, never all of `/` or `$HOME`.
  - Unscoped `git commit`, refused by the house hook. The retry with a pathspec worked (`c530010fd0`).
  - Opening artifact `H82d4dLjyqGtudGG33D48i`, which no longer exists.
  - A foreground `sleep 100` plus an `until … sleep 5` wait loop on the Dispatcher journal. Global
    rule: no wait loops. Use `run_in_background` or Monitor with `waitfor.py`.
  - The owner reads RC on the web/phone, so each of these shows to him as a failed job, and the
    session looked like it was flailing. **Keep Bash calls clean and quiet, and answer him in chat.**

## What was changed

- **`ee9f9acf50`**: `.claude/settings.json` sets `CLAUDE_CODE_SHELL=/bin/bash` (checked against the
  claude binary: it is honoured if the path names bash or zsh and runs). The setting is read at
  window start only.
- The BENCH window was killed (TERM to its claude pid) and reopened at ~19:05 with
  `launch_fleet.ps1 -Seats BENCH`. The new session's shell snapshot is `snapshot-bash-*`, and its
  first commands ran without error.

## Loose ends — each needs an owner

- `434cf3a30d` (dispatcher: account_pick holds nothing until the owner is back, by his card at ~19:00
  "stay on the current account") — committed and pushed by your predecessor, but **cut off while
  confirming `/home/mandrake/rm/dispatch` has pulled it**. NEXT: `git -C /home/mandrake/rm/dispatch merge-base --is-ancestor 434cf3a30d HEAD`, and check the Dispatcher journal stops asking for an account switch.
- **FOUNDRY is still on zsh.** Its window predates `ee9f9acf50`, and its clone was at `e0ec2e6051`.
  NEXT: once FOUNDRY is between items, pull and restart its window (`launch_fleet.ps1 -Seats FOUNDRY`).
- `TIMERS_PAUSE_DIAGNOSE_WHO_HIT_THE_BRAKES` — filed by your predecessor: a `timers_guard pause
  --hours 4 --all` at 18:36:50 stopped every rm-* timer 40 s after the steven switch. Timers were
  restarted at ~18:52, and the Dispatcher has been ticking since. NEXT: make sure FOUNDRY picks it up.
- **`rm-scratch-reap.service` is failed**: at 17:30 it ran the full 30 min, peaked at 3.9 G memory
  and was killed. Not v3-related. NEXT: file an item if none exists.
- **The global SessionStart hook errors in every session**: `~/.claude/settings.json:113` runs
  `$HOME/dev/Placard/contrib/placard_sessionstart_hook.sh`, but Placard is not cloned on Archmagi
  (`D:\Luke\dev\Placard` does not exist). Harmless noise. Not RimMandrake's to fix: raise it with the
  owner (clone Placard, or drop the hook on this machine).
- **Leftover tab**: the old AGENT BENCH tab dropped to a bare `zsh -l` prompt (pid 1129869) when its
  claude exited. Harmless. The owner can close it.
- `/home/mandrake/rm/bench` has uncommitted ledger and conversation files, and a `git pull
  --ff-only` there aborted (~19:08). NEXT: reconcile through the normal `./publish` path; don't merge
  by hand.
