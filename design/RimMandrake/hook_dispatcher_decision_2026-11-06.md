# One dispatcher per tool: measured, not built

Item `HOOKS_MERGE_ONE_DISPATCHER_PER_TOOL` (deferred WP-13, `redesign_final.md` G19: merge only if a hook-latency
measurement shows material cost). **Verdict: not material. The hook entries stay as they are.**

Rerun with `python3 src/RimMandrake/Utils/hook_latency.py --gate`. It measures again, replays the corpus, and fails if
`.claude/settings.json` disagrees with the verdict, including when a future measurement says the merge is owed. Raw
numbers: `src/RimMandrake/Utils/hook_latency_transcripts.json` (real calls) and `hook_latency_corpus.json` (replay set).

## What "material" means

Fixed in `hook_latency.py`; any one makes the cost material. The saving, per typical Bash call, is at least 500 ms; or
at least 5% of a typical agent step; or the CPU saved across a day's calls is at least 5% of the machine.

## What was measured

Claude Code runs a tool's matching hooks in parallel, so a call waits for the slowest hook, not the sum. Transcripts
agree: the fastest 1% of real Bash calls took 142 ms, under the 620 ms a serial run of the 17 hooks takes.

The prototype is one process running every matching hook in turn from cached bytecode. It is never registered. These
are medians from 2026-11-06 at load 12-19 on 14 cores; the wall figures move with load, so rerun rather than quote.

| Call | Hooks | Wall now | Wall merged | CPU now | CPU merged |
|---|---|---|---|---|---|
| Common Bash (`ls -la src`) | 17 | 121 ms | 101 ms | 441 ms | 59 ms |
| `git commit` | 17 | 133 ms | 128 ms | 468 ms | 77 ms |
| `git push` | 17 | 1313 ms | 2258 ms | 2735 ms | 2199 ms |
| Edit | 4 | 26 ms | 50 ms | 86 ms | 48 ms |
| Agent | 5 | 86 ms | 108 ms | 158 ms | 97 ms |

Three days of transcripts (2418 files) give 20,205 Bash calls a day, 8.1% of them commit, push or publish, and a median
agent step of 6.07 s. Against the bars:

- **Time per call:** the typical call gets about 19 ms *slower*. A common call gains 20 ms, but heavy calls lose about
  470 ms because hooks that now overlap would queue.
- **Share of a step:** that is -0.3%. Even removing the whole 121 ms hook phase would be 2% of a step.
- **CPU:** the one real gain, 382 ms a call, which is 2.1 core-hours a day or 0.64% of the machine.

Entry count is not an outcome, as G19 says: 17 entries cost 121 ms of wall time.

## What would actually help

`block_blind_scan.py` is most of the wall time on its own: 121 ms when the next slowest hook takes 31 ms. It imports the
`measure` package at startup, from a skill folder on the D: mount, on every Bash call, although few commands name a
scanner. With the skill folder absent the same hook reads 23 ms against 116 ms, so the import is the cost. Importing it
only when the command names a scanner is a small change, and removes most of what a merge would not.
That work is filed separately as `HOOKS_BLINDSCAN_TUNE_DRIVE_D_IMPORT_TOLL`.

## Same refusals, same allowed operations

The corpus holds 166 real calls from transcripts: up to six per kind of refusal, plus 60 sampled allowed calls. They
are only ever fed to hooks, never executed. Each goes through the registered commands and through the prototype, and
each hook's decision and reason are compared with digits blanked, because hooks quote live clocks and counts. An entry
that differs is asked again up to twice, since live state can move between the two runs. The 2026-11-06 result was 80
refused by 11 hooks, 86 allowed, and no differences. Hooks that refuse on live state can move those counts.

Replay needs one guard: an allowed Agent call makes `block_agent_over_slots.py` reserve a real helper slot for 90 s.
The tool sets `RM_SPAWN_RESERVE_S=0` for every hook it runs, so a replay cannot take a working seat's slots.

## Dispatcher failure behaviour

This binds any dispatcher built later. Today's behaviour is the baseline, and it was measured.

- **A hook that raises:** that hook fails open and the others still decide. The dispatcher catches everything but a
  refusal per hook, as `selftest_hook_registrations_refuse.py` requires of registered hooks.
- **Exit codes:** the entries muted with `2>/dev/null || true` can refuse only by JSON on stdout. An unmuted exit 2
  refuses. The dispatcher keeps this per hook, or a muted hook's stray exit 2 becomes a new refusal.
- **Several refusals:** any refusal refuses the call, and every refusing hook's reason is shown.
- **A slow hook:** each hook keeps its own budget (today 10 to 60 s). When one overruns it fails open with a line on
  stderr, and the rest still run. One shared timeout is not acceptable: transcripts show 11 PreToolUse hooks cancelled
  in 3 days, and today each loses one guard, where a merged entry would lose all 17.
- **The dispatcher itself dies:** an unhandled crash or a missing file must not read as "allowed" silently. It may fail
  open only if it also raises an alarm, because it is now a single point of failure for every guard on that tool.
- **Heavy hooks stay concurrent:** the ledger lint, DLL and canon checks run in parallel, or `git push` pays the 70%
  shown above.
- **`os._exit` and global state:** hooks run isolated. `sys.path` is restored between hooks, since `block_blind_scan.py`
  prepends a folder on D:, and a hook that calls `os._exit` runs in its own process.

Hooks registered in `~/.claude/settings.json` (such as Machinist's `bash_guard.py`) sit outside any project dispatcher
and keep their own entries.
