# The census scripts

They read the transcripts in `~/.claude/projects` and the run records in `D:\ClaudeWork\rimmandrake\dispatcher`.
They write to the scratch folder `D:\ClaudeWork\rimmandrake\scratch\a2c` (their paths are fixed). Window: 7 days to
2026-11-23 7:56 PM PST. Run order: `runs.py`, `scan.py`, `det.py`, `scan3.py`, then any report. To repeat the census
for another week, change `CUT` in `scan.py` and `scan3.py` and `cut` in `runs.py`.

| script | prints |
|---|---|
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
