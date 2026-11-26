# BOUNDARY: `ops_watch.py whea-quiet`, the outcome check of the D: NVMe reseat, Design Version 0.1.0

Code: `whea_quiet` and the `whea-quiet` verb in `src/RimMandrake/Utils/ops_watch.py`. It reads the same collector as
the `disk.whea_*` points (`whea_lines`, `whea_parse`). Item: `DDRIVE_NVME_REPAIR_RESEAT_NEXT_SITTING`, written Thu
2026-11-26, 12:10 AM PST. Each promise has a test of its name in `src/RimMandrake/Utils/selftest_ops_whea_quiet.py`.

## The danger the limits guard

- **`WHEA_QUIET_HOURS` (72 h).** It guards a pass on a lull. From 2026-10-26 to 2026-11-25 the drive logged 3 to 17
  corrected errors on every day, and 25 in the 72 h before this page. So 3 days with none are a change in the drive, not
  chance.

## ACCEPTS (the only inputs this is built for)

- **a-wsl-host-with-windows.** Archmagi's WSL, where `POWERSHELL` exists and the System event log is readable.
- **the-list-effect-argv.** `python3 src/RimMandrake/Utils/ops_watch.py whea-quiet` from the clone root.

## DOES NOT SURVIVE (not promised)

- **a-cleared-event-log.** A System log that somebody cleared reads quiet. The drive is then not judged.

## PROMISES (each one is owed a test of the same name)

- **whea-quiet-exits-0-only-on-a-quiet-window.** Exit 0 when Windows lists no WHEA event in the last `--hours` but a CPU
  machine check (id 19, which is not the drive). Events older than the window do not count.
- **whea-quiet-exits-1-on-any-drive-event.** Exit 1 when one corrected or fatal event is in the window.
- **whea-quiet-exits-2-when-it-could-not-look.** Exit 2, with a line that starts `UNMEASURED`, when the collector is
  blind (no file or no Windows, no END line, a row ahead of the clock) or the window is past the query's days. A blind
  reading is never quiet.
