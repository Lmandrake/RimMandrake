# The census scripts

They read the transcripts in `~/.claude/projects` and the run records in `D:\ClaudeWork\rimmandrake\dispatcher`.
They write to the scratch folder `D:\ClaudeWork\rimmandrake\scratch\a2c` (their paths are fixed). Window: 7 days to
2026-11-23 7:56 PM PST. Run order: `runs.py`, `scan.py`, `det.py`, `scan3.py`, then any report. Do not run `scan.py`, `det.py` or
`scan3.py` again: they write over the baseline's data, and `scan.py`, `scan3.py` and `outc.py` import from a clone that is
gone.

For any other week, run `window.py --end <ISO time with zone> --days 7 --out <new folder>`. It reads the transcripts
itself, writes `rates.json`, and refuses a folder that holds another reading. Its rules are those of `p3.py`, `p5.py`, `p6.py`,
`cond.py`, `pure.py` and `pure2.py`; over the baseline's `scan3.pkl` it gives the same 18 counts.
Test: `../acceptance/census_window_accept.py`.

| script | prints |
|---|---|
| `window.py` | the 18 counts of any window, in turns, weighted tokens and per 100 runs |
| `runs.py` | the detached run records of the week |
| `scan.py`, `det.py`, `scan3.py` | one row for each model turn: weighted cost, tool calls, head of each result; duplicate turns removed |
| `kinds.py`, `kinds2.py` | cost by role and by kind of act |
| `launch.py` | detached runs by what launched them |
| `drv.py` | phases of the in-game driver runs (the phase rule fails on FlowWorks: use `p5.py`) |
| `pure2.py` | turns that only land work or write the ledger |
| `pure.py` | refused publishes, red/green turns, table reads (its ledger-grep line is too high: use `p6.py`) |
| `p3.py` | waits and `--help` turns |
| `p4.py` | copied scripts, records, pictures, Operations reads |
| `p5.py` | driver union, refused publishes by cause, test turns |
| `p6.py` | item lookups, progress notes, lease renewals |
| `cond.py` | the Conductor window's turns |
| `outc.py` | what Operations, Conductor and Designer role runs ended with |
