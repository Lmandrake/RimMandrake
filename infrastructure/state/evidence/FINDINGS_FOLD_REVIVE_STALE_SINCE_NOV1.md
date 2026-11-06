# FINDINGS_FOLD_REVIVE_STALE_SINCE_NOV1: was the testq fold tick running? Yes.

Measured 2026-11-06 ~10:10Z on Archmagi from `journalctl --user -u testq-tick.service --since 2026-11-01`
(5444 `findings_fold` lines; 5243 of them `unchanged since`).

- **The fold ran every tick (~1/min) through the whole "stale" window.** Its last write was 2026-11-01 16:40:55 PST
  (generated `2026-11-02T00:40`). From then until 2026-11-03 07:22 PST it printed
  `findings_fold: unchanged since 2026-11-02T00:40...: nothing written` 1319 times. That is the designed behaviour
  (docstring: "a rerun that would render the same table writes nothing"; selftest_findings_fold G8).
- **Nothing new arrived because the lane was paused.** In the same window the tick logged `lane paused; no fill` 1597 times and
  `steward: PAUSED ... Steve NVMe swap: owner fitting the Kingston now` 183 times. Exactly one job finished
  (`J20261102T000218Z-381f76 DONE-> INTERRUPTED CRASH`, 00:40:35Z), which was the last change the fold folded.
- **Real failures in the window, all transient, none of them keeping the file stale:** 2026-11-02 03:28–03:33 PST, five runs
  were `UNMEASURED: ledger unreadable` (a torn line in the dispatch clone's DISPATCHER.jsonl/RUNNER.jsonl, healed by
  the next pull). Since 2026-11-01 there were also three `[Errno 12] Cannot allocate memory` reads (11-01 13:37, 11-04 17:18,
  11-05 22:29) on D:. Every one fails closed and the next tick succeeded.
- **The fold writes again when content changes:** first write after the window 2026-11-03 07:22 PST; on 2026-11-06 there
  were 21 writes by 02:01 PST, the latest generated `2026-11-06T09:49:43Z` (records 771).

Nothing was revived because nothing was dead. The trap, filed in `infrastructure/state/facts/instrument_traps.md`:
the report's `generated` stamp moves only when the table changes, so it measures the lane's output, not the fold's
liveness. Liveness is the journal line, which every run prints.
