# Conductor restarts lose nothing — measurement and design

Item: `RIMMANDRAKE_STOP_CONDUCTOR_RESTARTS_LOSING_ITEMS_ASK_GPT` (BENCH, detached helper, 2026-11-15). Design only; nothing
here is built.

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

**Instrument limits.** Being seen is not being done: the regex count gives 70 of 76 seen, and the hand checks found 5 of
those 70 never done. I hand-checked the acted state only where noted. The remaining "carried" rows are seen-and-not-
contradicted, not proven done `[guess ~85% of them were acted on]`. Promises made earlier than a window's last two
replies were not sampled, except where one surfaced (row 19).

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
the sentence that creates the debt is written.** A short view lists only those items, oldest first, and every wake and
every start of turn reads that view first. No new store, verb or schema: `rimflow file --kind` is free-form today
(4,271 `task`, 1,265 `bug`, …), and `caused_by` already links an owed act to the item it acts on.

Each element names the loss it stops:

- **E1 — the owed view** (stops M1: the clone writer and the bundle deploy). `rimflow queue CONDUCTOR --owed` prints
  each open `kind: owed` item `--for BENCH` on one line: id, age, the act (title) and `caused_by`. Oldest first, at most
  40 lines, with a count line if there are more. `seat_restart.py wake` and `handoff.py --wake` print it right after the
  old window's last reply. The role file's Start of turn reads it in place of `queue CONDUCTOR`. Every prompt he sends
  carries one line, `OWED: n, oldest <age> <id>`, through the restart-notice path `conductor_goodbye.py` already has.
  An owed item over 2 h old is marked `LATE` there.
- **E2 — a promise check at every turn end** (stops the launch, decision, question, page and resume losses: rows 1,
  9, 16, 19, 20, 22). A Stop hook on the Conductor seat only reads the reply just ended. It finds promise sentences: an
  `I will` / `I'll` / `next window` / `when … I will` / `this one is mine` / `not launched` / `still owed` / `never
  written` sentence in the future or unfinished tense, or a question to him that ends the reply. The hook blocks the
  stop once if a promise names neither an open owed item nor an item id in the same sentence, and if no `kind owed`
  file event was made in this turn. The block reason lists the sentences and the command that files them. It blocks at
  most once a turn (`stop_hook_active`), so it can never loop. The detector is one module. `seat_restart.py` runs the
  same module at a backstop kill in **file mode, not refuse**: each unmatched promise in the last reply is filed as
  `owed` titled `UNTRIAGED promise: <sentence>`. A backstop is never refused.
- **E3 — results for the Conductor become owed items at their source** (stops M3: row 26). When the code that writes
  "for the Conductor's call" (the maturation park), a detached run ending with `LEFT OPEN:`, or a detached run ending
  in failure writes its log line, it also files one `owed` item with `caused_by` set to the run's item: "read <run> and
  decide". It is idempotent per run id. It is written at the source, so no window has to be alive when the result
  lands.
- **E4 — handoff pointers are owed items, not prose** (stops M2 and rows 7, 12). `handoff.py --check` (the existing
  gate in front of HANDOFF READY) files every pointer whose NEXT is an act as an `owed` item, unless an open owed item
  with that `caused_by` and NEXT already exists. The wake then lists the owed view: a pointer whose item has since
  closed still shows, because the debt is its own item.

Not changed: the goodbye close-out (no goodbye fired in 7 days, so it gets E1's view and nothing else), the held and
refused restart fixes (built), the context limits, and the handoff format.

**What it costs per turn:** E2 is a regex pass over one reply, ≈ 10 ms, and blocks only a reply that promises
something untracked. E1 adds one ledger render the wake already pays for. The blocked turn costs the window one
`rimflow file` call.

## 4. GPT's adversarial read

PENDING

## 5. Build tickets (in build order)

PENDING
