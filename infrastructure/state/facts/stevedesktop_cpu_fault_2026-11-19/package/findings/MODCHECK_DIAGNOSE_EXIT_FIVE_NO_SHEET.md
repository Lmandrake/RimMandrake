# MODCHECK_DIAGNOSE_EXIT_FIVE_NO_SHEET: what "modcheck exit 5, no sheet" is (2026-11-04)

Source: testq records under `D:\ClaudeWork\rimmandrake\testq\done` and `\quarantined`, windows from
`D:\ClaudeWork\rimmandrake\testq\fault_windows.json` (read 2026-11-04 ~08:40Z).

## The stack (MEASURED)

The first exit-5 job since the worker ran `python.exe -X faulthandler` is `J20261103T233438Z-aa0482` (FlowWorks
targeted, ran 23:37:30Z to 23:47:35Z 2026-11-03). Its note:

    modcheck exit 5, no sheet; Windows fatal exception: access violation ... File "C:\Program Files\Python313\Lib\ast.py",
    line 50 in parse  File "...\Utils\modcheck\status.py" ... cli.py", line 533 in <module>

An access violation (0xC0000005, whose low byte is the 5 WSL reports) inside `ast.parse`, which is CPython's own C
parser over source text: no extension module, ctypes or game call in the frame. The job ran inside SteveDesktop SIMD
fault window `F20261103T195921Z` (last clean 22:47:02Z, first bad 22:52:02Z, ended by the 02:45:13Z reboot) and
fault_monitor quarantined it at 02:36:05Z.

## The census (MEASURED; small sample)

Non-zero exits other than 1 among all records: exit 5 x8, exit 9 x1 (`J20261031T083004Z-78564c`, 3 s in, stack in
runner.py:1052 load_validation; 9 may be the low byte of 0xC0000409, a hypothesis).
- Since the 2026-10-31 18:03:15Z reboot: 42 jobs overlapped a fault window, 1 of them crashed (aa0482); 57 ran
  outside any window, 0 crashed.
- The 8 earlier crashes (10-27 to 10-31 14:47Z) predate fault_monitor (first window 11-01), so their window
  membership is UNMEASURED; all ran before the 10-31 18:03Z reboot that cleared the CPU 2 fault measured that day.

## Verdict

Exit 5 with no sheet is python.exe dying of a native access violation in pure CPython code, the signature of the
host's SIMD fault (`infrastructure/state/facts/steve_fault_diagnosis.md`), not a modcheck or harness bug. No exit 5
outside a fault window is on record. If one appears, its faulthandler stack is in the job note (worker.py read_sheet)
and is a new lead.

## What changed

- `ingest.quarantine_one` now also notes every `HARNESS_REPAIR_` item the quarantined attempt filed or was noted on,
  as a host fault (`repairs_of`; selftest `selftest_ingest.quarantine_repair_checks`). Before, aa0482's repair item
  `HARNESS_REPAIR_CAUSE_99231A83` was left chasing the hardware fault.
