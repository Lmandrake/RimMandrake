# Boundary for waiting on one testq lane job

Code: `src/RimMandrake/Utils/testq/testq.py`

`RIMMANDRAKE_WAIT_AND_WAKE_ON_ONE_LANE_JOB` covers `wait_for` and `cmd_wait` in
`src/RimMandrake/Utils/testq/testq.py`, tested in `selftest_testq.py` beside it.

## ACCEPTS

A testq job ID and an optional finite, non-negative timeout in seconds. Zero reads the current state once.
The queue on Archmagi is the record. Tests may supply a temporary `TESTQ_QUEUE` and a clock.

## DOES NOT SURVIVE

A missing queue, unreadable result, or quarantined result reads `could not look`. A running
record with a stale heartbeat shows that the queue lost contact with the job. It does not diagnose why.

## PROMISES

- **Wait returns recorded rows.** Pending and fresh running jobs keep waiting within the caller's time.
  A finished job returns `done`, the recorded outcome and all rows. The CLI exits 0 for a read done record.
- **Wait detects a stale heartbeat.** The running file's modification time is its heartbeat. A fresh job at
  the deadline reads `timeout` (6). A stale one (no heartbeat for `STALE_S`) reads `hung` (5) at the deadline,
  even when the caller gives it zero seconds.
- **Wait keeps waiting through a late first heartbeat.** Before the caller's deadline, a stale heartbeat alone
  does not end the wait: the tick that admits a SteveDesktop job is busy about 5 minutes starting it, and a
  healthy job read `hung` twice on 2026-11-27. With no deadline, a silence of `HUNG_S` reads `hung`.
- **Wait stops on unknown or cancelled.** An unknown ID returns immediately (4). A cancellation gives its
  recorded reason when available (3), including a cancelled attempt stored in `done/`.
- **Wait distinguishes unreadable, empty and zero.** An unreadable result gives no rows and `could not look`
  (2). An actually empty result returns `[]`. Measured rows keep their verdicts, including `FAIL`.
- **Wait prints a short result.** The command reads local files and prints the outcome and non-passing rows
  in fewer than 40 lines, with an omitted-row count when needed.

## LIMITS

- `STALE_S` is 300 seconds across a 60-second dispatch tick. It ends no work: at the caller's deadline it
  chooses `hung` over `timeout`. `OPS_TESTQ_UNSTICK_ECPK` established that a running record goes stale without
  worker confirmation.
- `HUNG_S` is 9000 seconds: 10 times the longest tick silence on record (ticks stalled for 7 to 15 minutes on
  Nov 21 and 23, `done_once`). It guards a waiter with no deadline against an endless wait on an orphaned job.
- A caller deadline bounds the wait when the lane remains pending, as in the 142.7 paused hours recorded
  in the SteveDesktop study. The waiter checks at most once per second to avoid busy-reading the queue
  files over waits such as those 111 measured in one week. It wakes sooner at the caller's deadline.
- The output budget keeps a large sweep from turning a one-job reading into a full record dump.
  The SteveDesktop study counted 275 job or lane reads in one week and calls for a short result here.
