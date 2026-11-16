# Conductor restarts lose nothing — measurement and design

Item: `RIMMANDRAKE_STOP_CONDUCTOR_RESTARTS_LOSING_ITEMS_ASK_GPT` (BENCH, detached helper, 2026-11-15). Design only; nothing
here is built. GPT's verbatim read: `design/specs/2026-11-15-conductor-restart-loses-nothing.gpt.md`.

Owner, 2026-11-15 ~5:30 PM PST: *"I think the Conductor windows' restarting is losing items, so you need to write
things down more as tickets to work somehow in a place they get seen or something. Worth sending an item out to GPT
for it to consider for you."*

**Verdict on his theory: partly true** `[measured]`. Over 7 days, 9 of 76 things a dying window owed were lost or
late (12%). The kind of thing lost matters more than the kind of restart. 8 of the 9 were acts the Conductor owed
itself that no ledger item recorded: a question it asked him, a decision it called "mine", a launch it promised
"when a slot frees", a page it said it would write. And the place the wake "reads" is not read. Every wake ran
`queue CONDUCTOR | tail -40` (or `head -60`) of a **23,872-line, 1.6 MB** view, so it saw the newest four items and
nothing a dying window had filed before them.

## 1. Measurement (2026-11-08 11:30 AM → 2026-11-15 4:55 PM PST)

**Method.** I read 28 Conductor windows (`/home/mandrake/.claude/projects/-home-mandrake-rm-bench/*.jsonl`, entrypoint
`cli`, first prompt a wake) and so 27 restarts. The restart kind comes from the Dispatcher journal
(`/mnt/d/ClaudeWork/rimmandrake/dispatcher/journal.jsonl`: `restart_kill` `why`, `backstop_hard`/`backstop`/`request`
with ticket `HANDOFF`) and, before 11-13 18:00 UTC where the journal has no restart rows, from the window's own last
reply and the successor's first prompt. I took what each dying window owed by hand from its last two replies and the
owner's last two messages: its stated "next I will", promises to him, results it had read but not acted on, and
launches it said it would make. **"Seen"** means the first later window that names the thing in its own words or tool
calls, not counting the wake's reprint of the old reply (`/tmp/crl/owed.py`, regex per thing). **"Acted"** was
hand-checked for every thing marked lost or late, and for a sample of the rest. Lost = never acted. Late = first acted
more than 2 h after the restart.

**Instrument limits.** Being seen is not being done. The regex count gives 72 of 76 seen. Of the 4 never seen, 2
were lost, 1 was done before the kill (row 13) and 1 is still pending (row 25). The hand checks found 3 of the 72 seen
things never done (rows 9, 16, 22). The "carried" rows are seen and not contradicted. A random audit of 10 of them
(seed 20261115, after GPT's read) found a concrete action, a launch, brief, note or relay, for 8. One stayed on the
waiting-on-him list, and one is a run still going. Promises made earlier than a window's last two replies were not
sampled, except where one surfaced (row 19). Times for rows 0–12 come from the transcripts. The journal holds no
restart rows before 11-13 10:00 AM PST.

| # | restart (PST) | kind | owed | lost | late | what was lost or late |
|---|---|---|---|---|---|---|
| 0 | 11-08 17:46 | handoff | 4 | 0 | 0 | ($60 relaunch "if it stops on the cap": the condition was not checked, UNMEASURED) |
| 1 | 11-09 03:58 | handoff (he was asleep) | 3 | 1 | 1 | **lost:** "Should I turn [the GPT-usage timer] back on?" was never asked again. **Late 6.4 h:** GSS notes stuck on the GSS branch |
| 2 | 11-10 02:51 | handoff | 4 | 0 | 0 | |
| 3 | 11-10 22:59 | WSL restart (crash) | 1 | 0 | 0 | the FlowWorks drain was recovered from its own files |
| 4 | 11-11 01:20 | boot / fleet | 0 | 0 | 0 | |
| 5 | 11-11 06:21 | account switch | 2 | 0 | 0 | |
| 6 | 11-11 12:28 | boot / fleet | 2 | 0 | 0 | |
| 7 | 11-12 05:52 | handoff (his order) | 5 | 1 | 0 | **lost:** "restarting the Archmagi agent", a handoff pointer with no item (moot later, when Whittle retired) |
| 8 | 11-12 09:43 | handoff (his order) | 1 | 0 | 0 | |
| 9 | 11-12 13:37 | handoff, not signalled | 3 | 1 | 0 | **lost:** "the Lodestar ledger step for the Augur work was skipped" |
| 10 | 11-12 18:20 | handoff | 4 | 0 | 0 | |
| 11 | 11-12 22:32 | handoff | 3 | 0 | 0 | |
| 12 | 11-13 11:24 | handoff | 4 | 0 | 1 | **late 5.7 h:** the bundled exact-water deploy and restart ("the one thing for the next window") |
| 13 | 11-13 14:02 | context backstop | 3 | 0 | 0 | killed mid-task ("Now trim the project copies…"); the trim had landed |
| 14 | 11-13 15:20 | context backstop | 3 | 0 | 0 | |
| 15 | 11-14 00:35 | context backstop | 1 | 0 | 0 | the fresh window's first turn died on `API Error EAI_AGAIN`; it recovered 40 min later |
| 16 | 11-14 10:44 | context backstop | 4 | 1 | 0 | **lost:** "When one of those slots frees I will launch the FlowWorks proof realignment". Its item `RIMMANDRAKE_REALIGN_FLOWWORKS_PROOFS_AFTER_UNDER_LIQUID_LAW` is still `proposed`; the promise lived only in prose |
| 17 | 11-14 12:18 | context backstop | 1 | 0 | 0 | |
| 18 | 11-14 15:13 | context backstop | 2 | 0 | 0 | |
| 19 | 11-14 20:28 | context backstop | 3 | 0 | 0 | lost inside the window, not at the restart: "I said I would start these at 4:15 PM and have not" (four launches, about 2 h late) |
| 20 | 11-14 23:01 | context backstop | 2 | 0 | 1 | **late 12.6 h:** "Pyrelands, six gaps' live halves: undecided. This one is mine; I have not ruled on it yet." No item |
| 21 | 11-15 05:05 | handoff, refused 34 min, then his `/clear` | 3 | 0 | 0 | the restart itself failed silently: the window's own detached run held the driver lock |
| 22 | 11-15 06:50 | handoff | 3 | 1 | 0 | **lost:** "The one-page owner summary of the pipeline review was never written." Not written since |
| 23 | 11-15 10:35 | handoff, about 1 h over 200k, held by its own background log watch | 3 | 0 | 0 | |
| 24 | 11-15 12:05 | account switch | 3 | 0 | 0 | |
| 25 | 11-15 15:41 | handoff, **held 2 h 13 min silently** | 6 | 0 | 1 | **late, still unacted:** "find which run writes into /home/mandrake/rm/bench". It has an item NEXT, and two wakes read it without acting. The two restart fixes "I did not get to write into the handoff" survived only through the wake's reprint of the last reply |
| 26 | 11-15 16:55 | context backstop | 3 | 0 | 0 | ("Gimme Some Slack is paused for the Conductor's call": the wake relayed the pause at 4:56 PM, but no item holds the owed call, UNMEASURED whether it was made) |
| | **total** | | **76** | **5** | **4** | 65 carried, 2 UNMEASURED |

**By restart kind** `[measured on the rows above]`:

| kind | restarts | owed | lost | late | lost + late |
|---|---|---|---|---|---|
| HANDOFF READY (incl. refused or held) | 13 | 46 | 4 | 3 | **15%** |
| context backstop (no handoff, no close-out) | 9 | 22 | 1 | 1 | 9% |
| boot, crash, account switch | 5 | 8 | 0 | 0 | 0% |
| goodbye (light close-out) | **0** in 7 days | — | — | — | — (no window got his goodbye: `\bgood ?bye\b` is in none of his messages) |

The handoff restarts lose the most, against intuition: a handoff writes the owed thing as prose, and prose is read
once, at the wake, then drops out of sight. A backstop window keeps going until the kill, so less is pending at the
kill. The three restarts that did not happen on time (rows 21, 23, 25) cost him most: he had to `/clear` once and
shout twice ("You have still not reset!"). That defect is fixed and built
(`RIMMANDRAKE_PUBLISH_HELD_RESTART_LEDGER_LINE_SILENT_TWO_HOURS`, `conductor_restart.md` §Held or refused), and it is
not redesigned here.

## 2. What exactly is lost

The 9 lost or late things, by kind. In 8 of them, no ledger item recorded that the **Conductor** owed the act:

| kind of owed thing | lost | late | example | had an item? |
|---|---|---|---|---|
| a launch it promised ("when a slot frees I will launch…") | 1 | 1 (+4 in-window) | FlowWorks proof realignment; the exact-water bundle | the target item existed; the promise was in prose only |
| a decision it took for itself ("this one is mine") | 0 | 1 | Pyrelands live halves | no |
| a question it put to him in a last reply | 1 | 0 | the GPT-usage timer | no |
| a page or record it said it would write | 2 | 0 | the one-page pipeline summary; the Augur journal step | no |
| resuming something it stopped | 1 | 0 | the Archmagi agent | no |
| a housekeeping fix it noticed | 0 | 1 | GSS notes stuck on a branch | no |
| an item NEXT nobody acted on | 0 | 1 | the clone writer | **yes**: in the 23,872-line queue |

Three mechanisms lose them:

- **M1 — the wake does not read the queue.** `queue CONDUCTOR` is 23,872 lines in `priority.rank()` order, topped by
  stale ops alarms (`GSS_SWITCHES_PROVE_LAST_FOUR_STANDING`, `JAM_WATCH_…`). All 14 measured wakes piped it through
  `tail -40..60` or `head -40..60`. "File it in the queue" today means "file it where no wake looks". This is why the
  owner's direction needs a **short** owed view, not only more tickets.
- **M2 — the owed act is prose, so closing an item hides it.** A handoff pointer's NEXT is often a relay or a decision
  ("tell him where Gimme Some Slack stands"). When the pointer's item closes, `handoff.py --wake` prints CLOSED and the
  NEXT reads as done. In the 15:28 handoff, 3 of 15 NEXT pointers named items already done when it was written; 5 of the 15 are done now, and whether their relays to him happened is recorded nowhere but chat.
- **M3 — results reach a window that is gone.** A run that parks a mod "for the Conductor's call", or a detached run
  that ends with `LEFT OPEN:`, writes a log line and a note. The window that launched it may be dead. The next one sees
  the line only if it happens to fall in `tail -n 40` of a 3,979-line log.

## 3. Design: one owed list, written when the debt is made

The rule: **anything the Conductor owes is an open ledger item of kind `owed`, filed for the Conductor's seat, when
the sentence that creates the debt is written.** A short view lists only those items, and every wake and every start
of turn reads it first. No new store, verb or schema: `rimflow file --kind` is free-form today (4,271 `task`, 1,265
`bug`, …), `caused_by` already links an owed act to the item it acts on, `wait` already parks an act on a trigger, and
`close --no-code` already takes evidence text. This is the design as amended by GPT's read (§4).

Each element names the loss it stops:

- **E1 — the owed view, with evidence to discharge** (stops M1: the clone writer, the bundle deploy). `rimflow queue
  CONDUCTOR --owed` prints only the open `kind: owed` items of the Conductor's seat. Its first line is `OWED n
  (actionable a, waiting w), oldest <age> <id>`. Then come the actionable items, oldest first, one line each, with
  `LATE` past 2 h and the `caused_by` shown. Then `WAITING (w):` lists each item under a `rimflow wait`, with its
  trigger. The view is at most 40 lines, with an `--all` line past that, and an item never loses its age. `seat_restart.py
  wake` and `handoff.py --wake` print it right after the old window's last reply, and the role file's Start of turn
  reads it before the full queue. Every prompt he sends carries the first line, through the restart-notice path
  `conductor_goodbye.py` already has. Closing an owed item needs evidence: a sha, a run id, a path, or `told him at
  <time>`. Closing its parent discharges nothing. `rimflow next` never offers an owed item to a builder. **Seeded**
  at build with the debts measured open: the FlowWorks proof realignment launch and the clone-writer hunt.
- **E4 — handoff pointers cite owed ids** (stops M2 and rows 7, 12). `handoff.py --check` stays a validator. It
  refuses a `- \`ID\` … NEXT:` pointer that cites no open owed id, or that cites a closed one, naming the line. The
  window files the owed item, then writes the pointer, so a pointer whose item has closed still points at a live debt.
- **E2 — untracked promises are shown, then filed at a kill; advisory first** (stops the launch, decision, question,
  page and resume losses: rows 1, 9, 16, 19, 20, 22). `promise_scan.py` finds promise sentences in a reply. A promise is
  a future or unfinished act of the Conductor's own, or a question to him that ends the reply. A sentence counts as
  tracked only if it names an open owed id. A target item's id alone does not: T16 named its item and was lost. The
  per-prompt notice prints the last reply's untracked promises, `UNTRACKED in your last reply: …`, so the window files
  them on its next turn. Nothing blocks a turn in this version. At a backstop kill, where no next turn exists,
  `seat_restart.py` files each one as `owed` titled `UNTRACKED promise: <sentence>`, before the shard-publish path runs.
  Blocking at the Stop hook is a later decision, taken only after a week's false-positive count.
- **E3 — explicit Conductor hand steps become owed items at their source** (stops M3: row 26). The Dispatcher tick runs
  `owed.py sync-sources`. It files one owed item for each maturation row whose next step says the Conductor decides
  (three blind cycles) or that a card goes to him, and for each detached run record carrying `owed_close` whose item is
  still open. Each item is keyed by its source and serialized through the ledger writer, so a key is never filed twice,
  even by two runs at once. Plain failed runs are not sources (noise, §4).

Not changed: the goodbye close-out (no goodbye fired in 7 days, so it gets E1's view and nothing else), the held and
refused restart fixes (built), the context limits, the handoff prose, and the full queue.

**What it costs:** E2 is a regex pass over one reply per prompt, ≈ 10 ms. E1 is one ledger render the wake already
pays for. E3 is one pass per Dispatcher tick over the maturation status and the detached records. E4 is one replay per
`--check`.

## 4. GPT's adversarial read

Verbatim, with the question: `design/specs/2026-11-15-conductor-restart-loses-nothing.gpt.md`.

**Taken:**
- **Fix the count and audit "carried"** (its A.1, A.2): my draft said 70 of 76 seen while `owed_out.txt` has 72; now
  corrected. Its cheapest check was a random audit of 10 carried things for an action artifact, and I ran it (§1): 8 of
  10 have one, 1 stayed on the waiting-on-him list, and 1 is still running. The "carried" count stands.
- **E1**: actionable apart from waiting, waiting needs a trigger, ages never reset, discharge needs evidence, a closed
  parent never discharges, owed items stay out of builder allocation, and the open debts are seeded (its B.3, C.7).
- **E2 advisory first**: per-sentence matching, a target id alone not counting, no blocking during goodbye, handoff
  or backstop, and capture before the shard publish (its B.4).
- **E3 narrowed** to the explicit Conductor hand steps the code already names, with a stable key and serialized,
  concurrency-proof filing (its B.5). The acceptance test runs two `sync-sources` at once.
- **E4 a validator**: pointers cite owed ids, and `--check` mutates nothing (its B.6).
- **Build order**: E1 first (its D.8).

**Rejected, with why:**
- **"Cut E2's detector"** (its C.7). 6 of the 9 losses were promises written as prose in ordinary replies. A structured
  record is what the window forgets to write, which is the omission GPT itself names. I kept the detector and dropped
  only the blocking.
- **"Retain ordinary queue coverage at scheduled checks"** (its B.3). The full queue was never read: every measured
  wake took `tail -40` of 23,872 lines. It stays where it is, but nothing relies on it.
- **"Reconcile and audit measurement" as ticket 1** (its D.8). Done in this run, so it is no ticket.
- **"On each wake, record the next step or blocker of one actionable debt"** (its B.3): this is a new ritual with no
  incident. E1's `LATE` mark and the per-prompt count put the oldest debt in front of every turn, and that costs nothing.

## 5. Build tickets (in build order)

Each ticket has a runnable acceptance test written at filing. I watched each one fail on the base `0639e8226d`.

| # | ticket | stops | acceptance test | on base | when built |
|---|---|---|---|---|---|
| 1 | `RIMMANDRAKE_LIST_CONDUCTOR_OWES_FIRST_AT_EVERY_WAKE` (E1) | M1; seeds the 2 open debts | `python3 src/RimMandrake/rimflow/acceptance/owed_view_accept.py` | FAIL 2/17 | PASS 17/17 |
| 2 | `RIMMANDRAKE_REFUSE_HANDOFF_POINTER_WITHOUT_OWED_ID` (E4) | M2 | `python3 src/RimMandrake/rimflow/acceptance/owed_pointers_accept.py` | FAIL 0/7 | PASS 7/7 |
| 3 | `RIMMANDRAKE_SHOW_UNTRACKED_PROMISES_NEXT_PROMPT_FILE_AT_KILL` (E2) | the prose promises (6 of 9 losses) | `python3 src/RimMandrake/rimflow/acceptance/owed_promise_scan_accept.py` | FAIL 0/21 | PASS 21/21 |
| 4 | `RIMMANDRAKE_FILE_OWED_WHERE_RUNS_PARK_FOR_THE_CONDUCTOR` (E3) | M3 | `python3 src/RimMandrake/rimflow/acceptance/owed_sources_accept.py` | FAIL 2/10 | PASS 10/10 |

The tickets are ordered by dependency: 2–4 file or read `kind: owed` items, and 1 makes them visible and dischargeable.
Ticket 3's positive cases are the measured sentences themselves.

**UNMEASURED:** whether the Gimme Some Slack three-cycle decision (row 26) has been made; whether the row 0 $60
relaunch condition ever fired; the false-positive rate of `promise_scan` on a real week of replies (ticket 3 measures it
before any blocking); losses from promises made earlier than a window's last two replies, which were not sampled.
