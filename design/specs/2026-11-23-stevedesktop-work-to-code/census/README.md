# The census scripts of the SteveDesktop study

They read the lane's own records (`D:\ClaudeWork\rimmandrake\testq`), the ledger shards and the Claude transcripts. They
write nothing. Window: 21 days to Mon 2026-11-23 8:30 PM PST (`END` and `CENSUS_DAYS` in `common.py`). The output of the
first run is `results_2026-11-23.txt`. Run each from this folder: `python3 <script>`.

| script | prints |
|---|---|
| `jobs.py` | jobs by state, host, requester, mod, outcome, what ingest did |
| `kinds.py` | each not-DONE job in one setup kind; the faults that a DONE outcome hides; asked against filler |
| `notdone.py` | the raw note heads behind `kinds.py`, with an example id |
| `windows.py` | ledger verdicts that rest on a job run inside a machine-fault window |
| `visits.py` | the jobs that the visit feed sent, and whether any visit folder used them |
| `ledger_after.py` | for each asked job: who wrote its id on the ledger after it ended |
| `tracked_mentions.py` | the same, over items, design, git and transcripts (slower; a loose match) |
| `idle.py`, `idle_why.py` | hours busy, down, paused by day and by reason; hours an asked job waited while nothing ran |
| `submits.py` | each `testq.py submit` an agent ran: accepted, refused, help text |
| `items.py` | ledger items about SteveDesktop filed in the window, by family and state |
| `tokens.py` | weighted tokens of the SteveDesktop turns in the last 7 days (`tokens.py PRICES.json`) |

`PRICES.json` is `MODEL_PRICES` of `src/RimMandrake/rimflow/role_launch.py`, written as JSON. To count the runs on
SteveDesktop itself: `PRICES="$(tr -d ' \n' < PRICES.json)"; ssh mandrake@stevedesktop-wsl "PRICES='$PRICES' python3 -" < tokens.py`.
