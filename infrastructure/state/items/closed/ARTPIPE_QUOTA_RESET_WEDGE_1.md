# ARTPIPE_QUOTA_RESET_WEDGE_1 — the idle meter refresh can only re-read stale data

Filed by BENCH as a one-line title: "artpiped cannot notice a Codex quota reset:
idle meter refresh reads only stale rollouts, so it stays parked until something
runs codex exec in a leased home." Investigated and (partially) fixed by FOUNDRY
2026-09-25, reading `src/RimMandrake/Utils/artpipe/artpiped.py` and
`skills/generating-images/scripts/codex_grumpiness.py`.

## The actual mechanism (confirmed by reading the code, not guessed)

`artpiped.py`'s codex-channel admission gate is `Detector.admission_blocked()`.
Once a completing job's meter reading trips row 2 (weekly usage — `refuse_new` at
`WEEKLY_REFUSE`=99%, `stop_all` at `WEEKLY_STOP`=99.8%), `admission_blocked()`
refuses **every** new codex claim. `Detector.note_meters()` — the only thing that
can clear `refuse_new`/`stop_all` — is called from exactly two places:

1. `finalize_job()`, after a codex job **completes**. But no new codex job can be
   admitted while blocked, so this path cannot fire again on its own — a real
   catch-22.
2. The "Finding 4" idle refresh in `main()`'s poll loop (now around
   `artpiped.py:2384-2400`, gated by `DEFAULT_METER_REFRESH_INTERVAL_S`), added
   specifically to break that catch-22 by re-reading meters independently of any
   job running.

The bug: `codex_grumpiness.read_meters()` (which that idle refresh calls) is a
**passive file read** — `newest_rollout()` just globs
`$CODEX_HOME/sessions/**/rollout-*.jsonl` and returns the most recently modified
one; it never calls the Codex API or runs `codex exec` itself. A rollout file is
only ever written by an **actual `codex exec` turn running in that CODEX_HOME**.
While the daemon is blocked, no codex job is admitted in the leased home the idle
refresh is reading, so no new rollout is ever written there, so the idle refresh
polls the identical stale file forever and gets back the identical stale
percentages. `refuse_new`/`stop_all` never clear themselves — the daemon stays
parked even long after the real account's weekly quota window has actually reset,
**until some outside process** (a human's manual `codex exec` in that same leased
`CODEX_HOME`, or a daemon restart, which gets a fresh un-latched `Detector`) writes
a fresh rollout for it to find. This is not hypothetical: the existing selftest
`test_daemon_unwedges_codex_channel_without_restart_end_to_end` only unwedges the
mock daemon by explicitly calling `mock_codex_worker.write_rollout(fresh_home,
weekly=1.0, five_h=1.0)` from outside the daemon's own control flow — i.e. it
already encodes "an outside write is required" as the documented, accepted shape
of the fix, which is exactly the gap this item names.

Row 1 (`hard_stop`, an explicit `TooManyRequests`) is **not** part of this bug —
it is deliberately latched for the whole daemon run by design (a real throttle
refusal must never be papered over by a later reading), and stays that way.

Row 3 (5h/`primary`) partially avoids this trap already: `sleep_until` is set from
the reported `primary_resets_at` epoch, and `admission_blocked()` already has a
time-based check (`time.time() < self.sleep_until`) that stops blocking once that
deadline passes — admission resumes on its own, and the next job's own completion
gets a real fresh reading. Row 2 (weekly) had no equivalent: `Detector.note_meters()`
read `primary_resets_at` but never looked at `secondary_resets_at`, even though
`codex_grumpiness.classify()` already returns it (same shape, same rollout, already
selftested in `skills/generating-images/scripts/selftest_codex_grumpiness.py`).

## Related but distinct — not the same bug

`requeue_quota_failures.py` handles jobs that landed in `failed/` because a worker
attempt actually ran and got an explicit "hit your usage limit" refusal text; it
moves them back to `pending/` for a fresh claim. That is orthogonal to this item:
it does nothing about the `Detector`-level admission gate that prevents jobs from
being claimed in the first place, and it doesn't touch meter state at all.

## FIXED 2026-09-25 — the weekly-window half, using data already being read

`Detector` now remembers `secondary_resets_at` (as `self.weekly_resets_at`) on
every `note_meters()` call that carries a weekly reading, mirroring exactly how
row 3 already uses `primary_resets_at`/`sleep_until`. `admission_blocked()` no
longer treats a stale `stop_all`/`refuse_new` as an unconditional block: once
wall-clock time passes the last known `weekly_resets_at`, admission resumes, one
job runs, and that job's own completion produces a genuinely fresh reading via the
ordinary `finalize_job -> note_meters()` path (confirming the reset, or re-blocking
if reality disagreed). No extra API call, no guessed poll cadence — it only ever
trusts a deadline Codex itself already reported in the last real reading.

This is a small, mechanical change (two fields threaded through, one new
time-gate condition in `admission_blocked()`), reusing an established,
owner-reviewed pattern already in the same file rather than inventing a new
polling/probing design. It does not touch codex_home leasing, concurrency, or spend
concurrency, and does not contradict "the artist tile is the daemon, not a seat —
no-LLM by design": it still never calls out to an LLM itself, it only decides
*when* to let an already-scheduled real job through.

Selftest: `test_detector_weekly_resets_at_self_heals_the_wedge` in
`src/RimMandrake/Utils/artpipe/selftest_artpipe.py` (6 assertions: still blocked
before the deadline; unblocked after it while `stop_all`/`refuse_new` remain
stale-True; the same self-heal covers `refuse_new`, not only `stop_all`; no
regression when `secondary_resets_at` is absent or garbage; row 1's `hard_stop`
is never de-latched by this). Full suite re-run clean:
`python3 src/RimMandrake/Utils/artpipe/selftest_artpipe.py` → all checks pass
(388 `ok` lines, 0 `FAIL`), and
`python3 skills/generating-images/scripts/selftest_codex_grumpiness.py` → 12/12.

## 🔴 What is NOT fixed — the honest residual, left for a human call

This only self-heals when the daemon actually captured a valid `secondary_resets_at`
before going blocked (i.e. the reading that tripped `refuse_new`/`stop_all` in the
first place carried a coercible weekly reset epoch). If that field was missing or
uncoercible, `weekly_resets_at` stays `None` and the daemon is exactly as parked as
before — still dependent on an outside `codex exec` refreshing the rollout, or a
restart.

Closing that residual for good would mean the daemon **forcing** a fresh reading —
i.e. running some kind of probe/no-op `codex exec` in the leased home on its own
idle cycle, even while blocked, purely to refresh the rollout. That is explicitly
the kind of change this item was told NOT to guess at: it burns real Codex quota to
check Codex quota, and picking how often to do that (too eager wastes the exact
budget the detector exists to protect; too rare re-opens most of this same wedge)
is a genuine design/product call, not a mechanical fix. **Recommendation, not
shipped:** if the owner wants this residual closed too, the shape to consider is a
single, rate-limited "probe admission" — let admission_blocked() allow through
**one** codex job even while `refuse_new`/`stop_all` is set, no more often than
some modest interval (longer than `DEFAULT_METER_REFRESH_INTERVAL_S`, since this
one actually spends), so the daemon can self-heal even with no `resets_at` data at
all — but the interval and whether it's worth the guaranteed spend is his call.

## spec

1. Give `Detector` a data-driven way to know when a weekly-window block might have
   expired, without depending on an external rollout write. **DONE** via
   `weekly_resets_at` / `_weekly_window_should_have_reset()`.
2. Do not touch row 1 (`hard_stop`) — it is deliberately latched for the run.
   **DONE** — untouched, covered by a selftest assertion.
3. (Open, not shipped) Decide whether the residual "no `resets_at` at all" case is
   worth a bounded, spend-accepting self-probe, and if so at what cadence.

## verify

- `test_detector_weekly_resets_at_self_heals_the_wedge` passes (see above).
- Full `selftest_artpipe.py` suite still passes after the change (re-run, all
  green, no prior test's behavior changed).
- `test_daemon_unwedges_codex_channel_without_restart_end_to_end` and
  `test_detector_unwedges_via_direct_meter_reread_without_a_new_job` (the existing
  "Finding 4" tests) still pass unmodified — this change is additive, not a
  replacement of that mechanism.

## criteria

- Closed when: the owner rules on §3 (probe or no probe, and at what cost/cadence)
  and, if he wants it, that gets built and selftested the same way.
- Already true regardless of §3: a weekly-window wedge whose last known reading
  carried a valid `secondary_resets_at` now clears itself on the next poll after
  that deadline, with no human and no external `codex exec` required.
