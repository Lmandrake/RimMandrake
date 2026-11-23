# Result: RIMMANDRAKE_REWRITE_CONDUCTOR_FILES_LONGEST_ROLE_FILE

Batch 2 of `design/specs/2026-11-19-plain-english-rule-docs/batch_plan.md`. Run 1, 2026-11-19, a detached helper (seat
BENCH key, Opus writer). Base commit: `25c18fb733`.

Files:

- `src/RimMandrake/rimflow/roles/conductor.md`
- `src/RimMandrake/rimflow/roles/conductor_restart.md`
- `infrastructure/agents/CONDUCTOR.md`

Special rule of the row: `owed_view_accept.py` reads the "## Start of turn" heading. Each heading is kept word for word.

## Scores

"STE" is violations per 100 words. "long" is the count of sentences over 20 words. "flagged" is the mechanical flag
count of `rule_doc_lint.py lint`.

| file | bytes before | bytes after | words before | words after | STE before | STE after | long before | long after | flagged before | flagged after |
|---|---|---|---|---|---|---|---|---|---|---|
| `conductor.md` | 40,626 | 45,783 | 5,704 | 6,523 | 4.14 | 2.28 | 109 | 55 | 8 | 6 |
| `conductor_restart.md` | 10,708 | 12,035 | 1,673 | 1,868 | 3.89 | 2.19 | 29 | 12 | 1 | 0 |
| `CONDUCTOR.md` | 1,218 | 1,263 | 151 | 160 | 3.97 | 2.50 | 3 | 2 | 0 | 0 |

Each file meets the target: STE at or below 2.5, and a flagged count at or below the count before. The 6 flags left in
`conductor.md` are 5 `shout` (the 🔴 headings and bold slogans that other files cite, kept word for word) and 1
`bare-id` (`D1(b)`, which was there before; the line now names the file that cites the ruling).

### The long sentences that stay (69)

A script sorted each long sentence by its kind. Then the writer read the 6 sentences that the script could not sort.

| kind | count | where |
|---|---|---|
| an owner quote | 22 | `conductor.md` 17, 21, 154, 181, 342, 351, 368, 410, 429, 459, 505, 547, 553, 567, 572; `conductor_restart.md` 11, 27, 35, 96, 103; `CONDUCTOR.md` 9 (one more at `conductor.md` 17 is the second sentence of the same quote) |
| two short sentences that the lint joined at a bold lead | 20 | `conductor.md` 92, 170, 185, 195, 198, 284, 376, 386, 470, 473, 486, 494, 550, 568, 619; `conductor_restart.md` 22, 145, 160; `CONDUCTOR.md` 5 |
| a sentence that holds a code span (a command, a path or a named id) | 26 | `conductor.md` 55, 128, 137, 139, 165, 173, 251, 273, 287, 294, 311, 315, 331, 357, 384, 397, 412, 420, 490, 499, 599, 622; `conductor_restart.md` 44, 62, 155 |
| a list after a colon | 2 | `conductor.md` 222 (the kinds of a major system event); `conductor_restart.md` 164 (what still holds the restart) |

Not every sentence in the code-span row holds a command. Some hold only a path or an id. The plan allows "a sentence that
holds a command". So some sentences in that row are outside the three allowed kinds. Each one keeps a path or id that
the no-loss checks guard. The writer did not split them further.

`conductor_restart.md` line 22 is the bold slogan "Every wake prints the old window's last reply …", kept word for word.

## The hand count: lines that a cold reader could not act on

| old line (short) | what a cold reader lacks | state after |
|---|---|---|
| "the tile's held step-3 name `AGENT BENCH`" | what "held step 3" is | rewritten: step 3 of the rename is on hold (meaning from `selftest_bench_word_prose.py`) |
| "Part 3 (Orphan homes 1, 2, 4, 6)" | what an orphan home is | meaning added from `role_responsibilities_2026-10-26.md` §Orphan homes |
| "you gate, batch and bring them (quick-mode step 3c)" | where step 3c is | names the section and step |
| "hands you every loosening, in plan words" | what a loosening and plan words are | meaning added from `roles/operations.md` (no account, figure, runway or budget word) |
| "its figures off the blind page" | which page | kept; the sentence now names the owner-only proposal as the subject |
| "a note on the parent item headed `QUESTION FOR OPERATIONS`" | which item is the parent | names `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE` (from `roles/operations.md` lines 244-255) |
| "Only a live helper, the bridge or PAUSE holds it" | what PAUSE is | meaning added: the Dispatcher's stop-everything file `state/PAUSE` (`seat_restart.py` `paused_now`) |
| "Draining with long helpers: checkpoint them (…, then each one's checkpoint order, then `--wait`)" | what a drain is; who sends the order | rewritten; meaning from `conductor_restart.md` steps 1-4 |
| "reopens every promise on that timer" | what a promise is | meaning added from `CLAUDE.md` §An operational item is done only when it is running |
| "(a)-(g)" one-paragraph scheduled check | seven steps in one paragraph | one list item for each step; the letters stay, so `canon_sweep.py`'s "step 3b" still points right |
| "pending enact items from his rulings" | what an enact item is | meaning added from Orphan home 1 |
| "the page itself is token-blind" | what token-blind means | meaning added: the page shows no token or spend figure |
| "(a cut list goes to him as a trade-off, below)" | the section is above, not below | names "What you do raise", above |
| "FlowWorks + GSS" | what GSS is | expanded to Gimme Some Slack (the same file names it in Workshop rules) |
| "126 did not run" | that 126 is an exit code | "Exit 126 means that the gate did not run" |
| "Charter-tier-1 acts complete before you reply" | what tier 1 is; CHARTER has no tiers today | meaning added from commit 0983ac9003 ("Charter-tier-1 work needs no ceremony"; ceremony is the CHARTER's expensive list) |
| "never card … a ruling's twins" | what a twin is | meaning added from `delegation_policy.md` §1 |
| "(a checker's FAIL blocks the close, D1(b))" | what D1(b) is | names the file that cites ruling D1(b) |
| "exempt its own builds" | whose builds | "your own builds" |
| "each unstickable item" | kept | a cold reader can act on it with the DO/DON'T form that follows |
| `conductor_restart.md` "the file wakes `rm-restart-now.path`" | which file | "the request file" |
| `conductor_restart.md` the 800-character paragraph on the goodbye, the backstop and the handoff | one paragraph with five mechanisms | split into the goodbye, the backstop, the close-out and the handoff, each with its own list |

## The checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | `conductor.md` with `OPS_TIMERS_REVIVE_343F` and "up to three rounds" removed, and "3-5 lines" changed to "a few lines" | 2 lost (the id, "5 lines"), exit 1 |
| check 2 (`rule_doc_lint.py keep`) | the same copy | the id, one copy of "5" and the artifacts below, exit 1 |
| check 1 | each real rewrite | `conductor.md` 119 items, `conductor_restart.md` 41, `CONDUCTOR.md` 8; 0 lost, exit 0 each |
| check 2 | `conductor_restart.md`, `CONDUCTOR.md` | 88 and 15 spans, 0 lost, exit 0 |
| check 2 | `conductor.md` | 277 spans, 4 "lost", exit 1. The 4 are artifacts, see below. |
| `rule_doc_lint.py selftest`, `checkable.py selftest` | | PASS, 19 of 19 |

**The 4 artifacts of check 2 in `conductor.md`.** The old text had four code spans broken across a line end (old lines
107-108, 166-168 and 311-312). Check 2 pairs backticks line by line, so it read the prose between two spans as a code
span. The 4 "lost spans" are that prose: ", then each one's checkpoint order, then", "note gives it, revision
included),", "; it reaches his digest. The Producer applies it from that note and records", "). Closing its parent
discharges nothing. Spec:". Each real span on both sides of them is in the new text on one line. The writer read each
of the 4 against the old file.

One real loss that check 2 found was fixed: the token "28," of "2026-10-28, e35afe1dcc".

**People's names.** Neither check reads names. The writer read the diff. The only name is "Lukas", inside an owner quote,
unchanged.

## The tests that read the files

All passed on the base and on the final text: `selftest_skills_by_work.py`, `acceptance/owed_view_accept.py` (17/17),
`selftest_bench_word_prose.py`, `selftest_conductor_authority.py`, `selftest_conductor_identity.py`,
`selftest_restart_now.py` (`--now` exactly twice in `conductor.md`), `selftest_self_fix_rule.py`,
`selftest_dispatcher.py`, `selftest_seat_restart.py`, `selftest_retired_era_gone.py`.

`selftest_retired_era_gone.py` failed once on a draft. The draft put the design pointer of the retired era on its
own line, away from the quote that named the retired pipeline. The line in `conductor.md` now says that the era is retired.

## What the meaning read found

One fresh Opus reader for each file (`rm-judge`; `general-purpose` is refused by a hook). Each reader got the old and
the new text only.

**`conductor.md`: 20 items.** Repaired:

| first draft | why it was wrong | repair |
|---|---|---|
| "The Conductor is the window that the owner talks to." | leaves out the headless quick-check runs | names both |
| "set it for him with `seat_restart.py mode hold` (or `ready`, `auto`)" | widened the old line | back to `mode hold` only |
| "You may file an exam … item by hand." | turned a condition into a permission | "An … item that you file by hand carries …" |
| "the tick raises `OPS_MATURATION_HAND_ACT_UNFOLDED`" | the old line does not name the tick | "An act left a day with neither raises …" |
| "(for example taste, through a judge agent)" | made the class open-ended | "(taste, through a judge agent)" |
| "Log each one as your act" | moved the scope of "as your logged act" to all three acts | the old sentence shape is back, so the scope stays as it was |
| "Never drop or build a proposal silently, without his answer." | weakened: only silent drops banned | "Never handle a proposal silently. Do not drop or build any proposal without his answer." |
| "The Conductor lane is the items filed `--for CONDUCTOR`." | an invented definition with no source | deleted; listed below |
| "A promise is the check of a live operational item" | misstated the home file | the meaning from `CLAUDE.md` |
| "Always finish a reply to a message that he sent" | turned a guarantee into an order | "A reply … is always finished." |

The other 10 items are definitions or pointers that have a source. Each was kept and the source is named in the hand
count above: "six" orphan homes, plan words, the parent item, PAUSE, the drain, the enact item, token-blind, the
twin, D1(b), Charter-tier-1. The retired-era mark on the design pointer was kept for `selftest_retired_era_gone.py`.
`CLAUDE.md` says that each module of that retired era is gone.

**`conductor_restart.md`: 6 items.** Items 1-3 (PAUSE, drain) have a source in `seat_restart.py` and stay. Repaired:
"Always finish a reply" (back to the guarantee); "The line names every hold with its fix" (back to the old clause,
"every hold named with its fix"); the config citation `seat_restart.seats.BENCH` (back to a citation, not the name of
the request); "nothing reads his presence" (back to "his presence is not read"); "The causes:" (now "The causes that the
request names:", so the list does not claim to be complete).

**`CONDUCTOR.md`: 0 items.**

**Repair check.** After the repairs, the writer split 12 more long sentences. Each of the two readers then read only
the repairs (the diff against the version that it read). Their answers are in the section "Repair check", below.

## Repair check

- `conductor.md`: the reader checked each of the 20 changed hunks against the old text. TOTAL 0. It also checked the twin
  and the Charter-tier-1 definitions against their sources, and found that both match.
- `conductor_restart.md`: the reader checked each changed line. TOTAL 0. One borderline item stays: "The causes that the
  request names:" can still read as a complete list.

## Lines that this run could not determine

| line | what is unknown | who would know |
|---|---|---|
| "you order the Conductor lane from the goals yourself"; "file it to the Conductor lane" | what the Conductor lane is. Best guess: the items filed for the Conductor seat. No code or doc defines it. | the Conductor |
| "Until the Producer runs (Friday wave)"; "until Sunday" (Auditor); "until Friday" | whether these waves still bind. The batch plan says that the Producer and the Auditor are switched off. | the Conductor |
| "a wider budget inside his weekly partition and night reserve (card 2026-10-25)" | what the partition and the reserve are. `delegation_policy.md` names the partition but does not define it. | Operations or the owner (his card) |
| "a raised N" | N is not defined in these files. The spawn hook prints "the allocator allows N=3", so N is most likely the helper count. Not added. | Operations |
| "how builds are judged, charged, gated or walled"; "a Judge or wall change" | what a wall is | the Conductor |
| "CHURNING (3+ returns or spend over 3M …)" | the unit of 3M | the Conductor |
| "read its NEEDS YOU line on RUNNING NOW"; "an item reading READY TO SHOW" | No file in `src` prints READY TO SHOW (git grep: only `conductor.md`). RUNNING NOW occurs only in a comment in `designer_stage.py`, which points at `owner_queue.needs_you`; `src/RimMandrake/Utils/owner_queue.py` prints neither. The showings rule can point at a surface that no longer exists. The line is kept. | the Conductor |
| "On arrival, the headless FlowWorks builder … is fenced first" | who fences it (a person or a program). The passive voice is kept for that reason. | the Conductor |
| `conductor_restart.md` "Owner 2026-10-29, after blind review 3" | what blind review 3 was | the Conductor (git history of the Conductor design) |

## Conflicts found (not resolved; the Conductor decides)

1. **The daily digest.** `conductor.md` "What you read" and Quick mode step 3(d): a program builds the digest; "Never
   assemble the digest by hand." Workshop rules: "Build his daily digest of delegated calls."
2. **The seat name in the owed-item command.** "Type CONDUCTOR wherever a seat is asked for." The owed-item command in
   Start of turn says `rimflow file <ID> --for BENCH …`.
3. **The Start of turn list.** `CONDUCTOR.md` lists 4 commands and omits `queue CONDUCTOR --owed`. The role file lists 5,
   with `--owed` second. The role file says that it is the one source.
4. **Background commands.** `conductor_restart.md` says "The background commands of the window end with the window" in
   the list of what holds the restart. The section "Held or refused" says that background commands still hold the
   restart.
5. **How often the wake lists his late text.** `conductor_restart.md` says "lists, whole and once". The section on the
   wake says the command "lists that text again until a window has answered".
6. **The helper limit of a session.** The Off switch says that a session "has no helper limit". Session mode says that
   there is no limit only for work started within 20 min of his last typed message, and two helpers after that.
7. **A cut list.** Quick mode step 3(c) says that a cut list goes to him as a trade-off. "What you do raise" says that
   the Conductor decides the cut and never waits on him.

## Other findings

- The slot hook took a slot reservation (90 s) for each spawn that a later hook refused. Three refused
  `general-purpose` spawns blocked the next `rm-judge` spawn for about a minute. Not filed: the hold is 90 s and expires
  by itself.

## What this run did not test

- No Conductor window has woken on the new text. No measurement shows that the Conductor behaves better.
- The sorting of the long sentences by kind is a heuristic script, read by the writer for the 6 that it could not sort.
- The canon sweep (`canon_sweep.py`) was not run on the new text. Its pointer "roles/conductor.md step 3b" still names a
  step with that letter.

## Second read of the repairs

Run 2026-11-23, item `RIMMANDRAKE_REREAD_REWRITE_REPAIRS_NO_READER_SAW_THEM`. One fresh Opus reader that made none of
these edits read each repair, restored line and late edit against the base text and the lines that travel with it. SAME
means that a reader of the new line acts as a reader of the old line. A gloss reads SAME when its source says the same.
His quotes: a script compared each quote of three words or more in the base with today's text, whitespace ignored. Quotes of the base that are not in today's two files were moved by a later crystallize run. Each stands word for word in `roles.history.md`, `standing_rulings.md` or the ledger.

| file | line read | verdict | what was done |
|---|---|---|---|
| conductor.md | the window and the headless quick checks | SAME | none |
| conductor.md | `seat_restart.py mode hold` only | SAME | none |
| conductor.md | "An … item that you file by hand carries …" | SAME | none |
| conductor.md | "An act left a day with neither raises …" | SAME | none |
| conductor.md | "(taste, through a judge agent)" | SAME | none |
| conductor.md | "Log each one as your act", old sentence shape | SAME | none |
| conductor.md | "Never handle a proposal silently. Do not drop or build any …" | SAME | none |
| conductor.md | the Conductor lane definition deleted | SAME | none |
| conductor.md | the gloss of a promise | SAME | none |
| conductor.md | "A reply … is always finished." | SAME | none |
| conductor_restart.md | "A reply … is always finished." (the line was removed later; `conductor.md` holds it) | SAME | none |
| conductor_restart.md | "every hold named with its fix" | SAME | none |
| conductor_restart.md | the `seat_restart.seats.BENCH` citation | SAME | none |
| conductor_restart.md | "his presence is not read" | SAME | none |
| conductor_restart.md | "The causes that the request names:" | SAME | none |
