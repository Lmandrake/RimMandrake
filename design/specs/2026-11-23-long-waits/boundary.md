# BOUNDARY: one long wait that checks that its job lives (waitalive.py), Design Version 0.1.0

Code: `src/RimMandrake/Utils/waitalive.py` (all of it). In `src/RimMandrake/rimflow/detached_helper.py`: the constant
`BASH_MAX_MS`, the variable that `launch_argv` sets from it, and the line of `FOOTER` that names `waitalive.py`.
Item: `RIMMANDRAKE_LENGTHEN_WAITS_UNDER_ONE_HOUR_CACHE_DIES_AFTER`. Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_waitalive.py`. Acceptance:
`design/specs/2026-11-23-agent-work-to-code/acceptance/rank7_long_waits_accept.py`. Experiment: `experiment.json` beside
this page.

Why: a `claude -p` run ends with its turn, so a wait blocks inside one Bash call. The call limit was 10 minutes. One wait
of 50 minutes was five turns. `waitalive.py` is for such runs. A window that the harness wakes when a background command
ends uses the background command.

## ACCEPTS (the only inputs this is built for)

- **a-command-on-this-linux.** `run [--name N] [--max DUR] [--silence DUR] [--progress FILE] -- CMD ARGS...`. The job
  starts in the caller's folder and environment, with no standard input. Its output goes to a file.
- **a-job-that-run-started.** `attach NAME [--max DUR] [--silence DUR] [--progress FILE]`, from the same detached run.
  Two detached runs that use one name have two jobs: the folder of a job is under the name of its run's unit.
- **a-duration.** `90`, `90s`, `5m` or `2h`. Any other text is a usage error (exit 2).

## DOES NOT SURVIVE (not promised)

- **work-on-another-machine-or-on-windows.** A job that only waits for a Windows process, a game or a server writes
  nothing and burns no CPU here. It reads HUNG after `--silence`. Give `--progress FILE` (the log that the far work writes).
- **a-hung-job-that-still-writes.** A job that prints a line or burns CPU for ever has a sign of life. It reads STILL
  RUNNING at `--max`, never HUNG.
- **a-silence-over-two-waits.** The silence counts from the start of this wait. A job that was silent for 9 minutes
  before an `attach` gets one full `--silence` again.
- **a-daemon.** A process that left the job's session and whose parent ended is not in the process tree: its CPU time is
  no sign of life, and its end is not the job's end.
- **a-run-that-ends.** A detached run's unit ends all of its processes, the job too.
- **a-call-that-names-no-timeout.** The Bash tool's own limit is the `timeout` of the call. A shorter `timeout` cuts the
  wait with no verdict line. The job stays: `attach` takes it.

## LIMITS (each names the danger that it guards and the evidence)

- `MAX_WAIT_S = 3300` (55 minutes), the default and the highest `--max`. Danger: the prompt cache of the run lives one
  hour, and a wait past that rebuilds the whole cache. Evidence, over the main-chain turns of one week of detached runs
  (to 2026-11-23, 7:56 PM PST), by the gap since the turn before; a rebuild is a turn that wrote more cache than it
  read, and over 20k tokens `[measured]`:

  | gap before the turn | turns | turns that rebuilt the cache | average cost of a turn | average cost of a rebuilt turn |
  |---|---|---|---|---|
  | under 1 min | 44,714 | 0 | 21.7k | - |
  | 1 to 5 min | 4,644 | 3 | 27.5k | 519k |
  | 5 to 11 min | 1,056 | 4 | 24.4k | 534k |
  | 11 to 59 min | 48 | 6 | 102.6k | 547k |
  | over 59 min | 18 | 17 | 848.4k | 895k |

  Costs are in weighted tokens (`weighted_v2`). A longer `--max` is cut to 55 minutes with a NOTE.
- `BASH_MAX_MS = 3420000` (57 minutes) in `detached_helper.py`, the value of `BASH_MAX_TIMEOUT_MS` in the unit. Danger:
  a Bash call that outlives the prompt cache (the table), and a call that the harness cuts before the 55 minute verdict.
  Evidence, `experiment.json`, 2026-11-23 on Claude Code 2.1.325: three real units made one Bash call of 1,503 s, 3,004 s
  and 3,303 s (the last with this value). The harness cut none, and the turn after each read the whole prompt cache
  (67k tokens read, under 600 written) `[measured]`. A Claude Code update can end this effect in silence: read the
  experiment again after one.
- `SILENCE_S = 600` (10 minutes), the default of `--silence`. Danger: a hung job that looks like a long job. Evidence:
  10 minutes is when the old call limit gave the agent its next look at a job.
- `CPU_SHARE = 0.01`, and at least `CPU_MIN_S = 0.05`: CPU time is a sign of life only when it grew by 1% of the silence
  bound. Danger: a hung job that polls looks alive. Evidence, 2026-11-23: a python loop that sleeps 0.1 s used 0.05% of
  one CPU, and a shell loop of `grep` and `sleep 1` used 0.4% `[measured]`.
- `START_S = 30`: a hang guard of the start of a job (it took under 0.5 s `[measured]`).
- `KEEP_DAYS = 14`: the folder of an ended job is deleted after 14 days. Danger: job outputs fill the disk
  (`/tmp` filled with 15 GB of agent scratch on 2026-11-03, `src/RimMandrake/rimflow/run_tmp.py`).

## PROMISES (each one is owed a test of the same name)

- **a-hung-job-is-named.** No growth of the output, of the progress file or of the CPU time of the process tree for the
  `--silence` bound: exit 3, HUNG, with the pid.
- **a-live-job-is-never-called-hung.** A job that prints, a job whose progress file grows, and a silent job that burns
  CPU (in a child process too) are alive past the silence bound.
- **a-failure-is-never-finished-well.** Exit 0 is only for the job's own exit code 0. Exit code 7 is exit 1 with `rc=7`.
  A command that cannot start is exit 1 with `rc=127` or `rc=126` and its cause.
- **a-dead-job-is-died.** A job that a signal ended, and a job that is gone with no recorded exit code, are exit 6, DIED.
- **could-not-look-is-its-own-answer.** An unknown name, a state file or a process that cannot be read and a state folder that cannot
  be made are exit 5, COULD NOT LOOK. None of them is finished, died or hung.
- **no-wait-outlives-the-cache.** No wait is longer than `MAX_WAIT_S`, whatever `--max` says. `BASH_MAX_MS` is at most 59
  minutes and over `MAX_WAIT_S`.
- **the-job-outlives-the-wait.** STILL RUNNING (exit 4) and HUNG kill nothing. A wait that is killed kills nothing. The
  next `attach` takes the end of the job, its own exit code included.
- **the-call-returns.** The job holds no pipe of the caller: a caller that reads the output to its end gets it at the
  verdict.
- **one-verdict-line-last.** The last line of the output is the verdict, with one exit for each verdict: 0 FINISHED rc=0,
  1 FINISHED rc=N, 2 usage, 3 HUNG, 4 STILL RUNNING, 5 COULD NOT LOOK, 6 DIED.
- **a-taken-name-is-repaired.** `run` with the name, the command and the folder of a job that still runs attaches to
  it. Any other taken name gets a number, and a NOTE says so. The folder of a job is never reused: an `attach` never reads
  the end of another job. No case refuses, and no output is lost.
- **each-verdict-is-logged.** Each verdict is one line of `verdicts.jsonl` in the state folder, with the silent time. A
  log that cannot be written is a NOTE and changes no verdict.
- **the-setting-stands-on-the-experiment.** `launch_argv` sets `BASH_MAX_TIMEOUT_MS` only to a value that
  `experiment.json` holds as tried, not cut by the harness, with the prompt cache read after the wait.
- **the-brief-names-the-command.** The text of each detached run names `waitalive.py run`, `attach` and the `timeout` of
  the call, and tells no spend.

Later lists beside this page: `polish.md`.
