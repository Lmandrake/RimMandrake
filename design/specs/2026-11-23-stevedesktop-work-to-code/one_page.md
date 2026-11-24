# SteveDesktop: do we set its work up wrongly and lose track of it?

For Mandrake. 2026-11-23, 8:35 PM PST. Full table: `analysis.md` beside this page. Nothing is built. This is a proposal.

**How to read the numbers.** A job is one test run that we queue for SteveDesktop. An asked job is one that an agent or
the visit feed queued. The visit feed is the program that sends checks of an open in-game visit. A filler job is one that
the queue makes for itself when it is empty. M means million weighted tokens. `[measured]` is read from records.
`[guess ~N%]` is my guess. The window is 21 days, to 8:30 PM today.

**The answer: yes, both halves of your claim hold.**

| | 21 days | last 7 days |
|---|---|---|
| Asked jobs | 248 | 61 |
| Killed by our own setup | 94 (38%) | 16 (26%) |
| Ran to the end and measured nothing | 43 | 14 |
| Gave at least one pass or fail | 79 (32%) | 29 (48%) |
| Filler jobs that gave a pass or fail | 70% | 75% |

`[measured]`. Work that the program asks for does far better than work that we ask for.

**The setup faults, 150 jobs in all** `[measured]`. The bridge helper DLL was stale: 50. Steve2 refused its own running
game: 47, all on 11-23. The mod list could not be written: 26. The loaded list was wrong: 11. The map was wrong: 10. The
runner clone could not update: 5. One result had a wrong shape. Most causes are fixed, after many repeats. Steve2
gave the same refusal 47 times in 11 hours. Its ticket is still open, though the fix landed at 2:50 PM.

**The tracking faults** `[measured]`.
- The visit feed sent 32 jobs. 12 gave 163 passes and 3 fails. No visit counted one of them. The visits ran the checks again elsewhere.
- Of 1,819 visit result rows, 1 came from SteveDesktop.
- The reader of proof-job results was deleted on 11-18. The queue still says that this reader handles them. 3 of 12 later results have no ledger line.
- 62 of 165 kept asked jobs have no ledger line after they ended. 157 ledger verdicts come from machine-fault windows, and none says so. Your order of 11-12 covers 132 of them.

**Idle time** `[measured]`. Steve1 ran jobs for 155 of 504 hours. Asked jobs waited 150 hours while nothing ran, 143 of
them under a pause. The soak took 66 paused hours. One pause had no end date and lasted 49 hours. Since the audio
driver went off on 11-21, Steve1 is busy 71% of the time.

**Load** `[measured]`. Setup, submission, waiting and reading cost 15.1M in 7 days. That is 0.9% of the week's 1,716M.
Fixing the queue's code cost 23.7M. Runs on SteveDesktop itself cost 0.5M. Codex is UNMEASURED.
So the loss is game time, not tokens.

| rank | change | failures prevented | saved in a week | build | risk in one line |
|---|---|---|---|---|---|
| 1 | **Count the results.** A program writes each visit result into the visit's rows, and each proof result onto its item. | 22 finished visit jobs and 3 proof jobs uncounted `[measured]` | 1.5M `[guess ~40%]` | medium | It could count a result from another build. Keep the build check. |
| 2 | **Stop on a repeat.** Two equal refusals on one game stop that game and file one ticket. | 81 repeat jobs in 21 days `[measured]` | 1M `[guess ~40%]` | small | A passing glitch stops a game. A program retries in 30 minutes. |
| 3 | **One-line ask.** `testq.py ask ITEM` fills all 24 settings. It first checks the host's mods, save, DLL and Python. | about 8 setup deaths and 26 empty runs in a week `[guess ~50%]` | 3M `[guess ~45%]` | large | It can run a needless check. The agent still gives the purpose. |
| 4 | **Pause with an end.** A pause must name its end. Work moves to another free game while it lasts. | up to 143 waiting hours; half of them `[guess ~40%]` | 0.3M `[guess ~40%]` | small | It could resume during a soak. The end names the job that must be over. |
| 5 | **Stop a spoiled game.** A dead colonist on a kept map stops the game before the next job. | about 15 of 33 spoiled jobs `[guess ~40%]` | 0.5M `[guess ~35%]` | small | One more load of about 8 minutes. |
| 6 | **Mark the fault window** on the ledger line. | 157 verdicts would carry their mark `[measured]` | 0 | small | None. |
| 7 | **Wait and wake.** One command waits for the job and returns its rows. | none counted | 1.5M `[guess ~45%]` | small | It must see a hung job. |

The ranks overlap. Together they save about 6M a week `[guess ~40%]`. Try 1 and 2 first. They match the two halves of your claim.

**What stays with agents.** They choose what to test, class failures, write new checks and find causes. 43 of 443
in-game checks of six mods have a route to SteveDesktop today `[measured]`. Open tickets cover the rest.

**What I could not see.** I could not see Codex tokens, hand use of Steve1 and Steve2, or results that agents read without
writing the job id. No saving is measured until it is built.
