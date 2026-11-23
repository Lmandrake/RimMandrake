# Result: `RIMMANDRAKE_REWRITE_TOOL_TRAPS_KEEP_EVERY_MEASUREMENT`

Part of batch 9 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_TRAP_FACT_FILES_TWO_FILES`). File:
`infrastructure/state/facts/tool_traps.md`. Run 2026-11-23.

Base: 2c4b78e1441a427baed197a118ac4b19e2f9a928

Special rule of the batch: keep each measurement. The file is a home for evidence, so the STE target binds only its rule
bullets. This run kept every measurement, date, number, path and quote (check 2: 486 of 486 spans).

## Scores

| measure | before | after |
|---|---|---|
| bytes | 35,787 | 38,525 |
| words in linted prose | 5,395 | 5,742 |
| STE violations per 100 words | 4.00 | 2.14 |
| sentences over 20 words | 123 | 60 |
| flagged lines (mechanical) | 15 (12 shout, 1 pronoun, 2 bare-id) | 14 (12 shout, 2 bare-id) |
| lines that a cold reader cannot act on (hand count, by the writer) | 9 | 0 that this run could resolve; 5 listed under "Could not determine" |

The file grew by 8%.

### The 60 long sentences that stay

- 45 are a bold lead that the lint joined with the next sentence. Each bold lead is the name of one trap.
- 7 hold a command: lines 53, 138, 160, 232, 308, 329, 427.
- 3 are two sentences that the lint joined because the second one opens with a lower-case name: lines 37 (`md5`),
  332 (`setsid`), 187 (the quoted term).
- 5 are a measurement that stays whole: lines 155, 193, 339, 431, and line 88 (the family-count line, kept word for
  word).

The 12 shout flags are the 🔴, ⚠️ and ✅ marks at the start of a trap. The run kept them, and removed two ⚠️ marks
inside bullets that the split made into separate lines. The 2 bare-id flags: `Wait F1` (a firmware setting name) and
`preflight O13` (see "Could not determine").

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| Hasleo: "It shrinks the big partition …" | the subject of "It" | names Hasleo |
| RimSage: one bullet held four facts and a second warning | where each instruction starts | split into sub-bullets |
| "What outlives a dead parent": one paragraph held six routes | which route has which result | one bullet per route |
| systemd bare PATH: one sentence held six instructions | the steps in order | one bullet per instruction |
| `/proc/<pid>/environ`: "start time … plus btime older than …" | what the test rules out | names "started too early" and defines it from the same text |
| "(Steve: offline 27+ min)" | which machine | could not determine (see below) |
| "disk Id=7" | what Id=7 is | could not determine (see below) |
| "preflight O13" | which check O13 is | could not determine (see below) |
| "a low Codex runway" | what a runway is | could not determine (see below) |

## Section moves

Three entries moved to the section that their content names. The family counts on the line "By tool family" now match
the entries. Before this run, "Everything else" held 12 entries and the line said 11.

- `refusal_contract.py calibrate --help` moved from "Everything else" to "Ledger, rimflow, handoffs and lessons".
- `codex exec --json` moved from "Ledger, rimflow, handoffs and lessons" to "GPT, Codex and image tools".
- `gpt_call_log tokens_used` moved from "GPT, Codex and image tools" to "Probing filters, sandboxes and meters".

The header line "text unchanged except heading levels" was false after this rewrite. This run deleted that phrase.

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy with `RM_GPT_CALL_LOG` removed and "(1046 of 2167 on one day)" changed to "(about half on one day)" | 2 lost (the numbers, the id), exit 1 |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 4 lost (the code span, 1046, 2167, the id), exit 1 |
| check 1 | the final rewrite | 122 items, 0 unfindable, exit 0 |
| check 2 | the final rewrite | 486 spans, 0 lost, exit 0 |
| `batch_done.py selftest` | — | GREEN: 0 failed (12 planted cases) |
| `selftest_human_input_readers_queued.py` (the one test that names the file) | new | 0 failed |
| `.claude/hooks/selftest_block_unbounded_robocopy.py` (the hook cites the file) | new | 26/26 PASS |
| `selftest_retired_era_gone.py` | new | PASS |

Names of people: this run read the diff for names. "Steve" stays as in the old text. "the owner" replaces "his" in
two places where the subject was not named; the owner's quote dates stay.

## What the meaning read found

A fresh Opus reader (rm-judge, model opus) read the old and the new text side by side. It did not get the writer's
reasoning. It read 76 entries and found 7 lines. The writer repaired all 7.

| first draft | why it was wrong | repair |
|---|---|---|
| "Use that API before Fetcher." | the old text says to prefer the API over Fetcher, not to try it first | "Prefer that API over Fetcher." |
| "(Steve's machine, SteveDesktop: offline 27+ min)" | the old text does not name the machine | restored "(Steve: offline 27+ min)" |
| "Id=7 is the Windows event id of the disk source." | an invented gloss in a file of measurements | sentence removed; listed below |
| "The Codex runway is the Codex quota that is left." | an invented definition | sentence removed; listed below |
| "A root-disk fall is a fast drop of free space on `/`." | "fast" is not in the old text | "a drop of free space on `/` (`disk.root_free_gb`)", from the entry's own field |
| "often returns MISSING" | weaker than the old "constantly" | "returns MISSING for real subjects constantly" |
| "`subprocess.Popen` can lack a readable argv" | lost "yet": the gap is a timing effect | restored "may not have a readable argv yet" |

The same reader then read only the repair diff: 7 of 7 fixed, 0 new findings.

## Conflicts (listed, not decided)

1. **Pointers to traps that this file no longer holds.** Root `CLAUDE.md` §Facts you cannot guess says that this file
   covers "subagent watchdog, mid-session hooks, card gates, `handoff.py`, two Conductor windows".
   `design/RimMandrake/standing_rulings.md` §Facts you cannot guess says the same ("600 s subagent watchdog …"). This
   file has none of those five topics. Commit `b6e61a7630` (2026-11-07, "lessons folded into active files:
   tt_git_rimflow") removed 80 lines from this file. The traps went to skill reference files, for example
   `skills/rimflow-operations/references/traps.md`. This run did not trace each topic to its new home. The Conductor
   decides the pointer text.
2. **`pgrep -f` inside the file.** The `tasklist.exe` entry says "Check with `pgrep -f artpiped.py` from WSL". The
   `pkill -f` / `pgrep -f` entry says that `pgrep -f` matches the agent's own shell, and says to add `-A`. The file
   keeps both lines.
3. **`system_screenshot.py`.** Root `CLAUDE.md` §Tools calls it "always allowed, do not ask". This file says that it
   refuses under WSL. The two can both be true (allowed, but it does not work under WSL). The file keeps its line.
4. **`show.sh`.** `~/.claude/CLAUDE.md` says "Opening a file is a command … on archmagi `./Utils/show.sh <path>`". This
   file says that `show.sh` selects the file and does not open it. The file keeps its line.
5. **The `./pipe why` entry sits under "Simulators".** It is a rimflow display trap, not a simulator trap. This run did
   not move it, because the move would make the family counts false again.

## Could not determine

| line | question | who would know |
|---|---|---|
| "(Steve: offline 27+ min)" | Steve the person, or SteveDesktop | the author of the clone trial (the Steve fault work, `infrastructure/state/facts/steve_fault_diagnosis.md`) |
| "disk Id=7" | the event source and log of Id=7 | the author of the SteveDesktop disk entry |
| "preflight O13" | which preflight check O13 is: no code in the repo names it | the authors of the bridge preflight |
| "a low Codex runway" | what number makes a runway low for `gpt_consult` | the author of the runway gate in `gpt_consult.py` |
| "spurious L1/L2 violation" (`Handoff.tla`) | `Handoff.tla` is not in the repo; L1 and L2 have no gloss | the author of the TLA+ model |

Two counts could be stale. A quick grep found `taskkill /IM RimWorldWin64.exe` in 2 code files (the line says 5) and
`Select -First 1` in 2 files (the line says 7). The grep did not match the original count method, so this run kept the
measurement. The csproj `HarmonyDll` default still names the `Current` path in 72 lines (the winbuild entry still
holds).

## What this run did not test

- No agent run read the new file and acted on it.
- No measurement shows that an agent acts better on the new text.
- The repair check by the reader covers only the 7 repaired lines.
- Five lines over 120 characters stay (55, 117, 242 and two code spans). That is a style point only.

## Second read of the repairs

Run 2026-11-23, item `RIMMANDRAKE_REREAD_REWRITE_REPAIRS_NO_READER_SAW_THEM`. One fresh Opus reader that made none of
these edits read each repair, restored line and late edit against the base text and the lines that travel with it. SAME
means that a reader of the new line acts as a reader of the old line. A gloss reads SAME when its source says the same.
His quotes: a script compared each quote of three words or more in the base with today's text, whitespace ignored. No quote differs.

| file | line read | verdict | what was done |
|---|---|---|---|
| tool_traps | "Prefer that API over Fetcher." | SAME | none |
| tool_traps | "(Steve: offline 27+ min)" | SAME | none |
| tool_traps | the Id=7 sentence removed | SAME | none |
| tool_traps | the Codex runway sentence removed | SAME | none |
| tool_traps | "a drop of free space on `/` (`disk.root_free_gb`)" | SAME | none |
| tool_traps | "returns MISSING for real subjects constantly" | SAME | none |
| tool_traps | "may not have a readable argv yet" | SAME | none |
