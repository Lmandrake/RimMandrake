# Agent work that Python can do: one page

For Mandrake. 2026-11-23. Full table: `analysis.md` beside this page. Nothing is built or filed. This is a proposal.

**How to read the numbers.** Spend is in weighted tokens. M means million. `[measured]` is read from records.
`[guess ~N%]` is my guess with my confidence. The week is the 7 days to 2026-11-23, 7:56 PM PST.

**The answer.** The week cost 1,719M weighted tokens on this machine `[measured]`. About 23% of that (399M) is
paperwork turns `[measured by fixed rules]`. Paperwork means landing work, ledger notes, waits, game setup and state
reads. Plain Python can take part of the paperwork. The ten changes below would save about 120M a week, or 7%
`[guess ~50%]`. The ten overlap, so their numbers do not add up.

**What we missed before.** An agent copies last time's scripts and changes the names. Each in-game visit copies its
scripts from the visit before. All 17 blind-test rounds that have these scripts hold their own copies `[measured]`. No
earlier study named this.

| rank | what moves to code | saved in a week | build | risk in one line |
|---|---|---|---|---|
| 1 | **Landing.** One command commits, publishes, retries, notes and closes. | 35M `[guess ~60%]` | medium | It makes closing easy. Keep the outcome check in its path. |
| 2 | **Live visits and blind rounds.** One kit opens the game, runs scenes, writes rows. The agent still classes failures and looks. | 22M `[guess ~55%]` | large | A kit can hide a dead scene. It must write "could not look". |
| 3 | **Commands.** The brief carries each command filled in. Agents ask for help text 2,807 times a week `[measured]`. | 20M `[guess ~50%]` | small | The text goes stale. A program makes it from the tool itself. |
| 4 | **Tests.** One call runs a test on the old code, the new code and a planted fault. | 20M `[guess ~50%]` | medium | It can read the wrong build. It must print which build it read. |
| 5 | **Conductor wake.** The wake carries the run's result and the state. Today 408 turns a week open result files `[measured]`. | 18M `[guess ~55%]` | small | A long result fills the window. Nothing decisive may be cut. |
| 6 | **Item history.** The launcher puts the item's history in the brief. | 15M `[guess ~50%]` | small | The packet can omit the one decisive note. It must say what it left out. |
| 7 | **Waits.** One wait of two hours replaces many waits of ten minutes. | 12M `[guess ~60%]` | small | A hung job looks like a long job. The wait must check that it lives. |
| 8 | **Stage moves.** A program advances a mod when every row counts. It files a skeleton ticket for each failed row. | 10M `[guess ~50%]` | medium | It can advance on checks that are wrong together. A steward still reads any look. |
| 9 | **Alarms.** A program gathers the facts of an alarm and answers the steady ones. | 10M `[guess ~50%]` | medium | A slow rise inside the normal band is seen late. |
| 10 | **Sign of life.** The lease and the 20-minute note come from the running process. | 8M `[guess ~55%]` | small | A hung run keeps its lease. Tie the lease to the process. |

Rank 8 reverses a written decision in the pipeline code: "the program never advances". It needs a ruling. Rank 7 uses a
setting that I did not test in a detached run. Ranks 3, 5, 6 and 7 are small. Try those four first.

**What stays with agents.** Agents keep the work that has no test. They find causes, design fixes and choose
words. They judge pictures and choose planted faults. They name holes and class failures. A wrong class moves a mod. A program
may list the facts beside the class. Talk with you and your five acts also stay.

**What I could not see.** I could not see Codex and GPT tokens, or runs on SteveDesktop and the Macs. The real saving
of each change is unmeasured until it is built. The census scripts can count the same acts again after a change.

**The level that is enough.** Every agent role has its jobs classed. For a few small roles I read the role file only. The top ten have a measured pool and a tagged
saving. I stop here.
