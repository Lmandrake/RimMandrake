# Result: `RIMMANDRAKE_REWRITE_GIT_GAME_PURPOSE_DOCS_THREE_FILES`

Batch 10 of `batch_plan.md`. Files: `design/RimMandrake/GIT_WORKFLOW.md`, `infrastructure/GAME_STATE_WORKFLOW.md`,
`PURPOSE.md`. Run 2026-11-23.

Base: 9be9c8fb34ec221150d8a834d27ecb8a0585c838

Special rule of the batch: keep each owner quote. Each owner quote stays word for word. The declaration in `PURPOSE.md`
is byte-identical to the base (checked with `cmp`).

This run also changed one comment line in `game` (line 86). That comment said that `rimflow` refuses a bare assent.
The code records the assent (`_check_owner_said` in `src/RimMandrake/rimflow/cli.py`). The comment is now true.

## Scores

| file | measure | before | after |
|---|---|---|---|
| `GIT_WORKFLOW.md` | bytes | 31,831 | 36,480 |
| | words in linted prose | 1,989 | 4,703 |
| | STE violations per 100 words | 3.72 | 1.36 |
| | sentences over 20 words | 37 | 7 |
| | flagged lines (mechanical) | 2 (1 shout, 1 bare-id) | 2 (1 shout, 1 bare-id) |
| | hand count (lines a cold reader cannot act on) | 11 | 0 that this run could resolve; 2 under "Could not determine" |
| `GAME_STATE_WORKFLOW.md` | bytes | 7,295 | 8,184 |
| | words in linted prose | 760 | 882 |
| | STE violations per 100 words | 4.87 | 2.15 |
| | sentences over 20 words | 14 | 1 |
| | flagged lines (mechanical) | 8 (8 shout, 1 pronoun) | 8 (8 shout) |
| | hand count | 9 | 0 that this run could resolve; 1 under "Could not determine" |
| `PURPOSE.md` | bytes | 9,457 | 10,062 |
| | words in linted prose | 1,369 | 1,463 |
| | STE violations per 100 words | 4.75 | 1.64 |
| | sentences over 20 words | 29 | 5 |
| | flagged lines (mechanical) | 9 (9 pronoun) | 4 (4 pronoun) |
| | hand count | 4 | 0 |

The word count of `GIT_WORKFLOW.md` grew because the lint does not read table rows. Before this run, most of the file
(the traps table) was in table rows. This run made each trap a short entry of bullets. So the "before" figures of
`GIT_WORKFLOW.md` measure only about 40% of its text. The "after" figures measure nearly all of it.

The file sizes grew by 15%, 12% and 6%.

### The long sentences that stay

- `GIT_WORKFLOW.md`, 7: each holds a command (lines 97, 343, 418 twice, 427, 429), or is a bold lead that the lint
  joined with a sentence that holds a command (line 186).
- `GAME_STATE_WORKFLOW.md`, 1: line 101 holds an owner quote.
- `PURPOSE.md`, 5: each is a bold lead that the lint joined with the next sentence (lines 4, 89, 99, 109, 127).

### The flags that stay

- `GIT_WORKFLOW.md`: the 🔴 on "Worktrees are OFF" (an owner ruling), and `OP2` (now named: the
  `disk.scratch_outside_cap` alarm).
- `GAME_STATE_WORKFLOW.md`: 8 shout flags. Each is a heading or a ruling mark that other agents look for. This run
  removed one ⭐ mark.
- `PURPOSE.md`: 4 pronoun flags, all inside the owner's quoted declaration.

## The hand count

| file | old line | what a cold reader lacks | state after |
|---|---|---|---|
| GIT | "The default is a cone-sparse tree" | what a cone-sparse tree is | defined from the same text (a sparse checkout of the listed dirs) |
| GIT | "(git cherry `-`, or the same bytes per path)" | what `-` means | "git cherry marks it `-`" |
| GIT | the "Pre-push guards" paragraph inside the state table | the paragraph broke the table: the last 7 rows did not render as a table | paragraph moved after the table |
| GIT | "`/home/mandrake/.seat-tmp/land.sh` is a one-line wrapper" | the file is absent | corrected, measured 2026-11-23 |
| GIT | "`rm-scratch-reap.timer` runs it hourly, dry run until `--apply` is added" | the unit runs `--apply` | corrected, measured 2026-11-23 (`systemctl --user cat rm-scratch-reap.service`) |
| GIT | "`ops_watch` OP2 reads `rm_scratch_clones`" | what OP2 is | names the alarm, from `ops_watch.py` |
| GIT | "read YOUNG to `scratch_reap` until the TTL" | how long the TTL is | 24 h, from `scratch_reap.py` |
| GIT | heading "The loop (seat)" | "loop" is a retired term; the section is about landing | "Landing work (seat)". No file cites the old heading (`git grep`). |
| GIT | traps table cells with 4 to 8 instructions each | where each instruction starts | one entry per trap, with numbered steps |
| GIT | "after the work-history excise" | which event | could not determine |
| GIT | "a board's `done` must mean LANDED" | which board | could not determine |
| GAME | "finish mining the last load's corpse" | what to mine | "the harvest of the last load: drain its dumps and its log" |
| GAME | "(only window a DLL can be replaced)" | what "window" is | "`DOWN` is the only state in which a DLL can be replaced" |
| GAME | "game a", "game b" | root `CLAUDE.md` bans those names | ArchBig, ArchSmall, Steve1, Steve2; lock keys unchanged |
| GAME | "that idleness is the owner's go-signal" | whose idleness | "Going idle is the owner's go-signal" (after `rimflow seat ready`) |
| GAME | "This is still the ONLY thing a window may reach `broadcast.py` for" | what "This" is | "Game state is still the ONLY subject …" |
| GAME | "`--owner-said` refuses bare assent" | false since 2026-11-20 | corrected from `cli.py` |
| GAME | "that is the one case worth a one-line question" | the scope of "one case" | "Only this case of a game kill is worth a question" |
| GAME | the FOUNDRY note inside a column header | a header that holds history | moved to a lead sentence |
| GAME | "announce "Close the Game" when clear" | clear of what | could not determine; the line stays |
| PURPOSE | "That is the actual research question." | what "That" is | "Whether a pipeline can work this way …" |
| PURPOSE | "`infrastructure/agents/` holds the role files" | false: the role files are in `src/RimMandrake/rimflow/roles/` | corrected; `infrastructure/agents/` is named as the home of the charter, the model policy and the Conductor's file |
| PURPOSE | "It has two intentions" and 5 more lines that open with "It" or "This" | the subject | names the subject |
| PURPOSE | "Several of these were built, measured …" | several of what | "several of these experiments" |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy of the new `GIT_WORKFLOW.md` with `RM_CODEX_SIDE` removed, "up to 8 times" changed to "a few times", and `CRACKEDLANDS_FULL_RENAME_1` removed | 2 lost (the two ids), exit 1. Check 1 did not see the lost "8". |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 4 lost (the code span, one copy of 8, the two ids), exit 1 |
| check 2 | the first draft of `GIT_WORKFLOW.md` | 4 lost: the whole "served review-sheet output" trap. The writer restored the trap. |
| check 1 | final, each file | 97, 21 and 15 items; 0 unfindable; exit 0 |
| check 2 | final, each file | 397, 69 and 28 spans; 0 lost; exit 0 |
| `batch_done.py selftest` | — | GREEN: 0 failed (12 planted cases) |
| `src/RimMandrake/Utils/selftest_scratch_clone.py` (reads `GIT_WORKFLOW.md` for `--sparse`) | new | OK |
| `src/RimMandrake/rimflow/selftest_model.py` (cites `GAME_STATE_WORKFLOW.md`) | new | 72/72 passed |
| `src/RimMandrake/rimflow/selftest_retired_era_gone.py` (reads all three files) | first draft | FAIL: one line named `/home/mandrake/rm/foundry` with no "retired" on it |
| `selftest_retired_era_gone.py` | final | PASS |
| `src/RimMandrake/rimflow/selftest_game_names_prose.py` | final | PASS |
| `src/RimMandrake/Utils/selftest_game_provenance.py` (the `game` comment) | final | all passed |

Names of people: this run read the diff for names. "Lukas Mandrake" stays in `PURPOSE.md` as in the old text. "Steve1"
and "Steve2" are game names from root `CLAUDE.md`. "the owner" replaces "him" or "his" where the subject was not
named.

## What the meaning read found

One fresh Opus reader per file (rm-judge, model opus), one at a time. Each reader got the old text and the new text,
and not the writer's reasoning.

### `GIT_WORKFLOW.md`: 5 findings, 0 changed or weakened rules

| finding | repair |
|---|---|
| the land.sh wrapper correction (measured) | kept; the reader confirmed the file is absent |
| the reaper `--apply` correction (measured) | kept; the reader confirmed the unit's ExecStart |
| the OP2 alarm name was added with no source | now says "`ops_watch.py` names it so, read 2026-11-23" |
| "24 h" was added to the TTL with no source | now cites `scratch_reap.py` |
| "Those services are outside `ops_clocks.json`" picked one reading of the old "they" | restored the old "(they are outside `ops_clocks.json`)" |
| polish: "Nobody has run `git gc` there" read as today's fact | "At that measurement, nobody had run `git gc` there." |
| polish: "holds only the root files" added "only" | "only" removed |

### `GAME_STATE_WORKFLOW.md`: 8 findings

| finding | repair |
|---|---|
| bare assent: "refuses" became "records" | kept: the code records it. "is his instruction" restored to "passes". The stale comment in `game` is fixed. |
| game names renamed | kept: root `CLAUDE.md` gives the names and bans "game a" / "game b" |
| "The ledger clears them" named an actor that the old text did not name | restored the passive: "Those items are cleared automatically" |
| "the ledger records it" (`take --force`) | restored: "always works and is recorded" |
| "The ledger refuses an inferred state" | restored: "An inferred state is refused" |
| "No other case is worth a question" widened to all questions | "Only this case of a game kill is worth a question" |
| "When the live items are done" narrowed "when clear" | restored "when clear"; listed under "Could not determine" |
| "This file is the owner's specification" changed the authority line | "Authority: the owner's specification of the game-state cycle, 2026-08-20" |
| polish: "That idle seat" lost the act of going idle | "Going idle is the owner's go-signal" |
| polish: "Ask hard" weaker than "aggressively question" | "Aggressively question" |

### `PURPOSE.md`: 9 findings, none severe

| finding | repair |
|---|---|
| "know instantly what is wrong" stated four flat defects | restored "whether": four "whether …" bullets, with "threw the right things" |
| "hard to buy" lost "at once": each property, not the set | "That combination is extraordinarily hard to buy anywhere else." |
| "does not file the defect" lost its condition | "In that case the pipeline does not file the defect for someone else." |
| "cannot quietly redefine success" overstated a purpose | "the versions keep a pipeline from quietly redefining success" |
| "is the primary hazard" stated a stance as fact | "We treat … as the primary hazard" |
| role files correction | kept; the reader confirmed it in the repo |
| "The ledger logs every delegated call" added the ledger as actor | restored "Every delegated call is logged as a delegation" |
| "The game is the one environment" made a world claim | "The attempt runs in the one environment where …" |
| "one question: is the player's experience right?" made the criterion exclusive | "We judge the remake on whether a player's experience is right." |
| polish: "If we draw an autonomy boundary wrong" lost "discovering" | "To discover a wrongly drawn autonomy boundary costs a bad afternoon, not an incident." |

No reader read the repairs again. The repairs are listed above so that a reader can check them.

## Conflicts (listed, not decided)

1. **A stale bridge hold.** `GAME_STATE_WORKFLOW.md` says "A stale hold (45 minutes idle) is simply taken". Root
   `CLAUDE.md` §The bridge is passed through one file says that a holder is a process, and the game is free at once
   when the process ends. In root `CLAUDE.md`, 45 minutes applies only to the owner's OWNER hold, after his last
   deliberate interaction.
2. **`take --force`.** `GAME_STATE_WORKFLOW.md` says "`take --force` always works". Root `CLAUDE.md` says that nobody
   may take his OWNER hold until 45 min after his last deliberate interaction, "`--force` included".
3. **Who reaches `broadcast.py`.** `GAME_STATE_WORKFLOW.md` says that game state is "the ONLY subject for which a window
   may reach `broadcast.py`". The line before it says that only the owner, when he runs `broadcast.py` himself, reaches
   the windows. The `broadcast` skill says "OWNER ONLY". The file keeps both lines.
4. **A bare assent at closeout.** `src/RimMandrake/rimflow/conductor_closeout.py:182` says that the ledger refuses to
   quote a bare assent. `_check_owner_said` in `cli.py` records it with a note. This run did not decide which is
   current for the closeout path.
5. **One writer per clone.** `GIT_WORKFLOW.md` says that the seat clone has "one writer (the seat's own window)". The
   traps section says "Two windows of one seat share a clone and its index". Both lines stay.

## Could not determine

| file | line | question | who would know |
|---|---|---|---|
| GIT | "after the work-history excise" | which rewrite of origin/main this was, and when | the agent that ran the excise; `git log` of the SteveDesktop runner notes (`infrastructure/stevedesktop/RUNBOOK.md`) |
| GIT | "a board's `done` must mean LANDED" | which board: Lodestar's BOARD.md was retired on 2026-11-10 | the author of the parallel-integration rehearsal |
| GAME | "announce "Close the Game" when clear" | clear of live items, of the bridge, or of all work | the owner (his 2026-08-20 specification) |

`/home/mandrake/rm/roles/artpiped` (the artpipe daemon's home) and SteveDesktop's `~/rm/runner` were not checked. Both
lines stay as in the old text.

## What this run did not test

- No agent run read the new files and acted on them.
- No measurement shows that an agent acts better on the new text.
- No reader read the repairs of the meaning read a second time.
- The changed comment in `game` is a comment only. `bash -n game` passes. No behaviour changed.
- The two path claims in "Could not determine" were not checked.
