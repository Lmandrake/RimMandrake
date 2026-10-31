# Conductor Briefing and the goodbye lifecycle

**Date:** 2026-10-28 · **Seat:** BENCH (design helper) · **Status:** design. The owner reviews it; nothing in it is built yet.
**Items:** `CONDUCTOR_BRIEFING_DESIGN_ONE_PAGE_NOT_SIX`, `CONDUCTOR_GOODBYE_DESIGN_FRESH_EACH_TIME`
**Mockups (v2, the night of 2026-10-27, real data):**
- `D:\ClaudeWork\rimmandrake\conductor_briefing\briefing_phone_v2.html`
- `D:\ClaudeWork\rimmandrake\conductor_briefing\briefing_desk_v2.html`

## What he said (verbatim, from the ledger)

- **On the first mockups:** "Ugh! You need to work much harder on those briefs reports. They are cryptic and obtuse. Do a blind design pass on them asking what it thinks they sound like and are talking about and what a creative human would actually want to know after a 10 hour run unsupervised."
- **Briefing:** "So there need to be two versions. One for the phone, one for a full Keyboard sitting at Archmagi. Very similar, and hopefully as many items are common between them as possible, but I want to acknowledge that. I really enjoy answering quetions during the day, so often that should be what it leads with, as long as it's shown me any information I need to know first."
- **Goodbye:** "Yes option 2 for conductor. Goodbye should be the trigger. Please design and advise whether it should actually handoff or not. It seems potentially wise but I'm not sure."
- **Ruling on the lifecycle** (tsn 1793154577764524326): "Yes I like your design. Go with it." This makes three things his ruling:
  - quick mode gets a light close-out and no full handoff;
  - a full handoff happens only when a keyboard session ends;
  - a message within about 2 minutes cancels the goodbye.

  Part B is designed to that ruling. Where the ruling has a weak spot, it is listed as a risk with a mitigation, not reopened.

---

## 0. Why RimPulse and the hub feel "not quite there"

This section comes from reading the artifacts, not from guessing. Evidence paths:
- `D:\ClaudeWork\rimmandrake\dashboard\digests\digest_2026-10-27_1730_scheduled.md`
- `D:\ClaudeWork\rimmandrake\dashboard\digests\brief_2026-10-27_1715.json`
- `~/.local/state/rm-dashboard/hands.jsonl`
- `infrastructure/dashboards/hub/`

1. **The machine speaks first, and the page says "nothing" when there is plenty.**
   - The 17:30 digest opens with "What broke". That section is infrastructure noise: memory flapping ×3, commit charge ×10, "985 artpipe failed, not blocking", and two stale session files.
   - Next come "Needs your verdict: 0 new" and "To look at: 0 new".
   - On the same evening the ledger holds 49 items waiting on him, 39 of them older than 3 days (MEASURED, `rimflow_metrics.py`).
   - Of those 49, 28 already had his answer and were never moved on (ESTIMATE: his last event is later than the hand-over to him).
   - 15 looks are "held back" and never retire. 13 of them are hands from 10-07 to 10-16 that have no pre-read.
   - About half the page is "Done: 44", one line per close.
   - "New since last time" is computed honestly, and it hides the backlog. That is why it reads as both empty and noisy.
2. **Two vocabularies on two clocks, and no way to answer.**
   - The brief (11 sections, 05:45/17:15) and the digest (6 sections, 06:00/17:30) name the same things differently.
   - Both run on a fixed clock, not when he reads. The brief does record opens (`since_basis`), but the digest does not.
   - The brief is reachable only on localhost or the tailnet. It has no buttons (card 2026-10-24), so answering means switching to chat and retyping the context.
3. **There is nothing to be "on track" against, and the hub answers a different question.**
   - `infrastructure/state/CONDUCTOR_GOALS.md` does not exist.
   - The Producer is not running, so neither page can say on or off track.
   - The hub ("Utinni Control Room") is an 11 MB inventory of codebase health, maturity and registers. Its `publish_ready.json` is from 2026-10-02 (25 days stale).
   - Only a Claude Artifact call can publish the hub. It answers "what exists", never "what changed" or "what needs me".

**Consequence for the design:** one page, built from one data set. It covers the time he was away, leads with the one decision that matters most and says what each decision changes, lets him answer in his own words in chat, and keeps token data in a band the Conductor never reads.

---

## Part A — the Briefing

### A1. Shape: one data set, two renderings

- **Program:** `src/RimMandrake/rimflow/briefing.py` (proposed).
  - It writes `D:\ClaudeWork\rimmandrake\conductor\briefing.json`.
  - It renders `briefing_phone.html` and `briefing_desk.html` from that one JSON file.
  - The Conductor reads the JSON, the HTML and the owner band (owner, 2026-10-31: no closed sources). It writes only the `narrative` fields (marked `by: Conductor`): the night's sentences, the plain-word gloss and ask for each decision, its options and default, and the caption of the picture. Every number in them comes from a source it read.
- **Token band:**
  - `D:\ClaudeWork\rimmandrake\ops_watch\owner\briefing_owner.json` holds token and runway lines from Operations.
  - The renderer folds it into a collapsed band, so he still gets one page.
- **When it is built:**
  - on every Conductor wake;
  - after every Dispatcher run of Operations;
  - when he opens the page and it is more than 10 min old.

  It is not built on a fixed 05:45/17:15 clock.
- **Where it is served:** by the existing pulse daemon (127.0.0.1:8765, tailnet :8791), as `/briefing` (the phone picks it by user agent or `?v=phone`) and `/briefing?v=desk`. No new server is needed.

### A2. The window: from when he left until he came back

- **It starts when he left:** his last message before going quiet, or his goodbye (B2) if that is later. **It ends when he comes back:** his next message or his first look at the page. Both come from his messages in the chat transcripts and from `GOODBYE.ts`.
- It is not keyed on his last read or on the last scheduled send. Counting "new since last time" is what let the old digest say "0 new" while 49 items waited (section 0). What he wants to know is what happened while he was away.
- `briefing.json` records `window_from`, `window_to` and each source's `data_through`. While he is away the page is rebuilt with the same start. The copy he meets is the one built when he comes back.
- **The header says it in words:** "Mon 23:32 → Tue 04:51 (5 h 19 m), from your last message until you came back". Exact UTC times are in "For the record" only.
- **A source that went quiet is named in words** in the section it feeds, for example "no new test results after 01:12". It never shows as 0 and is never left out.

### A3. Sections, in his order

**Order rule:** he reads only what he must know (the night in four sentences), then the questions for him. Everything after the questions is reading, not deciding.

| # | Section | What it says | Data source | Phone | Desk |
|---|---|---|---|---|---|
| 0 | **Header** | "While you were asleep" (or "away"); the window in words | `window_from`/`window_to` (A2) | 1 line | 1 line |
| 1 | **The night** | A verdict first ("an unproductive night"), then: what changed in the game, what was made, and the biggest loss of time | game-content closes in the window; in-game test results; artpipe output; pulse failures. The Conductor writes the sentences from the JSON | 3-4 sentences | the same, plus one line on what follows |
| 2 | **Answer this first** | One decision: the one with the most work waiting behind it. It says what the pieces are in plain words, why this comes first, the options with one recommended, what to look for, and what happens if he doesn't answer | ledger items needing the owner, ranked by the items blocked behind each; the Conductor writes the plain words | the full question, options and default | the same, plus "what to look for" |
| 3 | **Other decisions that change the game** | Each one: what changes, where it stands now, the default if he doesn't answer, and how to stop it. Then "About the agent team", labelled "no change to the game", with its own defaults | the same population, the rest of the sequence | every decision and default, shorter | the same, with more context |
| 4 | **What got made in the game** | One row per thing: built / tried in your game / approved by you. New art or "none" with the reason. One in-game picture, captioned with what to look at and when it was taken. One "Load Game → <save>, look at <place>" line. New bugs, each with its owner | closes and in-game test results in the window; artpipe; screenshot index; save names from the test runs | a list, the picture and the save line | a table, the picture and the save line |
| 5 | **What went wrong, and what we're doing about it** | Problem / what it cost you / fixed? / next, and who | pulse failures and recoveries; failed test jobs; the items filed for each | a list, with "fixed?" and the owner on each | a table |
| 6 | **Your creative direction** | Whether tonight's work followed his direction, and anything promising. Instructions of his not yet carried out. Art owed to him, and where it stands in our checks | his ruled items in the window; the art pipeline and judging records | 2-3 sentences, keeping his brief's words | a paragraph |
| 7 | **Are we keeping up?** | One trend sentence that starts with a verdict (Yes / No / Mixed), then what the number measures, then tonight's counts | ledger file and close events over 7 days | 2 sentences | 3 sentences |
| 8 | **Agent machinery** | One line on machinery work, said to have no effect on the game unless it does | machinery closes in the window | 1 line | 1 line |
| 9 | **What the night cost** (collapsed, his eyes only) | Token spend, how long the allowance lasts, alarms | `ops_watch/owner/briefing_owner.json` | collapsed | collapsed |
| 10 | **For the record** (collapsed) | Item ids, exact times, sources, how each number was counted, file paths | everything above | ids for each section | ids, sources and paths |

**Rules on every section:**
- **Voice.** A producer talking to a director. Plain words, and the consequence for him comes before the mechanism ("a freshly dug square can stay dry next to working water", not "the first source checked is disabled").
  - Each project name gets a gloss the first time it appears: "FlowWorks, your water-and-digging mod"; "the bleed well (a tap that draws liquid out of the ground)"; "Bench (the agent that runs FlowWorks and the testing)".
  - Estimates say "about". A claim says only what the evidence shows ("in the test the meal cooked fine", not "nothing breaks").
- **Ids and tags live only in "For the record".** Above it: no item ids, no file paths, no MEASURED / ESTIMATE / UNMEASURED labels, no seat names without a gloss. Every number in the body still has a source and a provenance tag, recorded in the footer. The renderer refuses a body number that has no footer entry.
- **Every problem has an owner.** Before the page is published, the Conductor gives each unowned problem an owner (`rimflow needs <ID> <seat>`). The row then says "assigned to Bench as this page was built". The page never says "nobody owns it".
- **Every decision carries its stakes:** what changes, why now, the options with one recommended, and what happens if he doesn't answer (the default). Exactly one is "Answer this first". An instruction of his that was missed is reported as missed and carried out by default. It is not asked again as a new question.
- **Done has three states:** built / tried in your game / approved by you. A repair says "nothing to approve". "Fixed" is never used for something only built or only bench-tested.
- **Pictures** are real in-game screenshots. Each caption says what to look at and when it was taken, and an old picture says it is old. A thing with no picture says so. Each "Load Game" line names a save that exists, and the place in it to look.
- **The trend sentence** gives a verdict and a qualifier together ("No. The list grows by two for every one finished; that measures the list, not the game slipping").
- **Empty sections** are one line that says why ("No new art: the art queue was empty all night"). They are never hidden.
- **Phone and desk** have the same sections in the same order, with the same decisions, defaults, owners and verdicts. The phone shortens the supporting detail. It never drops a decision, its stakes, an owner, or the limits of the evidence. The desk adds the item list, "what to look for", and tables.
- **Look:** a 70s palette of cream, brown, rust, mustard and olive, with a light and a dark mode (`prefers-color-scheme`). Serif body text. The phone page is one 390 px column. "Answer this first" has the rust frame; decisions are olive and problems are rust.
- **"Probably answered" is never auto-routed.** Items whose last owner event is newer than the hand-over to him are confirmed with him as one batch question in section 3 before any of them moves.
- **Asks are answerable.** Before asking him anything, the Conductor runs `rimflow show <ID>` to check for an earlier ruling, which catches "already ruled" (C1) at the source.

**Still open after the second blind check of v2** (`blind_check_v2_2.md`):
- the mockup has no previews of the twelve pieces or of the Surrik redraw;
- the cost band is empty;
- it doesn't say what was planned for the night;
- it doesn't fully explain how "finished" fits with the open bugs and the unanswered tests;
- the checker decision has no concrete allowance;
- decisions have no deadlines.

The builder of `briefing.py` closes these. The first two need a renderer that has the data.

### A4. Answers land on the ledger

The page has no buttons (card 2026-10-24 stands). The route is:

1. Each decision in `briefing.json` carries its item id and a code, `Q1`…`Qn`. **The code belongs to the item, not to a page.** `D:\ClaudeWork\rimmandrake\conductor\qcodes.json` assigns a code from a counter that only goes up, the first time an item appears, and **never reuses a code**. Codes and ids appear only in "For the record". A question the Briefing itself proposes (for example "retire the 13 old hands") is filed as an item before it gets a code.
2. He answers in the Conductor's RC chat in his own words, for example "walk Thu evening" or "keep the Rot beasts small". The page's examples are shortcuts, not required words. The Conductor matches the reply to a decision on the page he read. If two decisions could match, it asks which one before recording anything. A code he types still works. An answer that matches a closed item gets "that one closed at <sha>; still want it?" in reply, never a silent re-route.
3. The Conductor records his words verbatim against the matched item:
   `rimflow note <ID> --owner-said "<his words>"` and, where it is a decision, `rimflow needs <ID> <seat>`. The note carries the RC message timestamp, so a retry can see the answer is already recorded.
4. The next build shows his recorded answer (the first 80 characters) on the row, until the item moves. Moving the item is a separate step from recording the answer.
5. The goodbye close-out (B2 step 1) re-checks that every answer he gave reached the ledger.

### A5. What retires

- **Pulse digest** (`rm-pulse-digest`, 06:00/17:30) and **pulse brief page** (`rm-pulse-brief`, 05:45/17:15). Their collectors become `briefing.py` inputs, and their pages stop being sent.
  - Retire them only after the Briefing has run for a week and he has said the Briefing replaces them. Until then both stay up.
  - `brief_opens.json` (his first look at the page ends the window, A2) and the brief's judge are kept.
- **Hub** (`infrastructure/dashboards/hub/`): frozen as an inventory, linked from the desk footer, no longer published. It does not answer "what needs me".
- **Delegated digest:** feeds Briefing sections 4 and 5 (and section 3 when it has "Needs you" rows). The file stays as a source.
- **The 13 hands from 10-07 to 10-16 held for "no pre-read":** retire them or get them pre-read. A hold more than 7 days old is filed as a "retire?" decision and shows in section 3.

---

## Part B — the goodbye lifecycle (owner-ruled)

### B1. The standing Conductor window

- **One interactive Remote Control window** titled `CONDUCTOR` (wt profile `CONDUCTOR`), in the BENCH clone.
  - It launches like the other seats: `claude_bounded.sh --dangerously-skip-permissions --name 'CONDUCTOR' --model opus --remote-control 'CONDUCTOR'`.
  - The profile is written by `install_wt_seat_profiles.py --apply` and placed by `launch_fleet.ps1` like any seat.
- **At wake it reads:**
  - `role conductor.md`;
  - `D:\ClaudeWork\rimmandrake\conductor\log.md` (last 40 lines);
  - `GOODBYE` (the previous `session_id`, `ts` and any close-out gaps);
  - every owner message in the previous session's jsonl newer than `GOODBYE.ts` (all of them, not a fixed tail; there are normally none);
  - `briefing.json`.

  It then sends him the Briefing link and its "Answer this first" question. Nothing else is in its context, which is the "fresh each time" he chose. "Already ruled" messages (C1) were MEASURED at 7 in 14 days, and each one is a stale-context error.
- **Session mode** (at the keyboard) is the BENCH seat window, as today. The full handoff ritual runs there when a keyboard session ends.

### B2. The light close-out (about 30 s), triggered by his goodbye

**Trigger:** a message from him whose whole text is one of `goodbye`, `bye`, `gn`, `good night`, `done for now`, `that's all` (case-insensitive, punctuation ignored). A goodbye inside a longer message is not a trigger. The Conductor asks "close out?" instead.

Steps, in order:

1. **Rulings on the ledger.**
   - For every message he sent in this window that answered or ruled on something, the Conductor checks that a `--owner-said` event carries his words. A moved item does not count; the words must be recorded.
   - It records any that are missing, verbatim.
   - This is a self-check, so it is backed by a program: `conductor_closeout.py check` diffs his RC messages against the ledger and lists the gaps.
2. **Promises to items.** Anything the Conductor said it would do and has not done is filed `--for OWNER` with `--why`, one item each, tagged `promise` in the title's twist (for example `..._PROMISED_AT_GOODBYE`). Nothing stays only in chat. Briefing section 5 lists an open promise like a problem, with its owner and next step ("we said we would re-run the four tests; not done yet, Bench"), never as a question. Filing promises therefore never adds to his decisions.
3. **Log note.** It appends 3-5 lines to `D:\ClaudeWork\rimmandrake\conductor\log.md`: time, what he decided (item ids), what is pending, and what the next window should raise first.
4. **Signal.** It writes `D:\ClaudeWork\rimmandrake\conductor\GOODBYE` with `{pid, ts, session_id, closeout: ok|partial, gaps: [<his message text + ts + intended item>...], state: "pending"}`. A partial close-out keeps the gaps themselves, not just a count. The next window retries them first, and section 1 (Must know) shows them until they are recorded.
5. **Reply:** "Closed out: N rulings on the ledger, M promises filed. Fresh Conductor in 2-6 min; write any time, and nothing you send is lost." Then it stops.

### B3. The Dispatcher restart (grounded in how relaunches work today)

**Today:**
- `account_failover.py` → `claude-account use`.
- `fleet_stop()` SIGTERMs **every** claude process on the machine, then `fleet_start()` runs `launch_fleet.ps1 -Seats SERVER,HESTIA,EMERGENCY,FOUNDRY,BENCH`.
- `verify_relaunch()` polls for 90 s.

**There is no per-window restart today.** The Conductor restart is a new, narrower path, built from the same parts:

`GOODBYE` is a small state machine: `pending → claimed → killed → relaunched → verified | failed | cancelled`. Each step rewrites the file atomically (write a temp file, then rename) and adds the Dispatcher run id. Exclusive ownership comes from a separate lock, not from the state field: a handler first creates `GOODBYE.lock` with exclusive create (`O_CREAT|O_EXCL`) holding its run id and pid, and a handler that cannot create it does nothing. A lock whose pid is gone and which is older than 10 min is abandoned: the next tick removes it and resumes from the recorded state, without starting over. The Dispatcher already runs one instance at a time; the lock covers a manual run beside it.

1. **Signal and grace.** The Dispatcher tick (every 2 min) sees `GOODBYE` in state `pending`.
   - The grace is measured from `GOODBYE.ts`: if less than **120 s** have passed, it waits for the next tick. In practice the restart therefore begins 2-4 min after his goodbye.
   - It cancels if his most recent RC message in the Conductor session is newer than `GOODBYE.ts`. It reads the session's jsonl under `~/.claude/projects/-home-mandrake-rm-bench/<session_id>.jsonl`.
   - On cancel it sets `state: cancelled` and appends "goodbye cancelled (new message)" to `log.md`.
2. **Quiet check.** The window must be idle: its last jsonl record is an assistant turn that ended with no tool call still open, and that record is at least 30 s old. Otherwise the Dispatcher waits a tick. After 3 ticks still busy, it sets `failed: busy` and leaves the window alone; the window stays usable and he is told once.
3. **Re-check, then kill one PID.** Immediately before signalling, the Dispatcher repeats the new-message and quiet checks (they take milliseconds). Then:
   - set `state: claimed`;
   - SIGTERM the pid recorded in `GOODBYE`, after confirming that `~/.claude/sessions/<pid>.json` names that `session_id` and the name `CONDUCTOR`;
   - wait 10 s, then SIGKILL, and set `state: killed`.
   - **Never** `fleet_stop()`, never `pkill -f`, never `/login`.
4. **Relaunch.** Run `powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& '<launch_fleet.ps1>' -Seats CONDUCTOR"`. That is the same command `fleet_start()` uses, narrowed to one seat.
5. **Verify.**
   - Within 90 s a new claude pid appears whose `sessions/<pid>.json` has the name `CONDUCTOR`, a `session_id` different from the old one, and a start time after `state: killed`. It sets `state: verified` and records `new_session_id`.
   - It writes `conductor/restart.jsonl {old_pid, new_pid, s}`.
   - On failure, it files `CONDUCTOR_RESTART_FAILED_<date>` for Operations and pushes one line to his phone through the existing notify path.
6. **Off switch.** `conductor\CONDUCTOR_OFF` (the existing switch) suppresses both the restart and the scheduled quick checks.

### B4. Races and risks (each with a mitigation)

| Risk | Mitigation |
|---|---|
| He writes again within 2 min of goodbye | The grace check (B3.1) cancels the restart. The old window answers as usual, and his next goodbye starts over. |
| He writes during the about 10-90 s restart | The message lands in a dead session, or in the old session's jsonl if the window was still alive. The new window reads every owner message newer than `GOODBYE.ts` from the old session (B1) and answers those first. Whether the RC server writes a message into a session whose process has died is **UNMEASURED**: until it is measured, the fresh window's first line says "if you wrote in the last few minutes and I do not answer it, send it again". |
| Older rulings fall out of a fresh window's context | That is the point of freshness, but a question must never re-ask a ruled matter. The Conductor runs `rimflow show <ID>` before asking (A3 rules), and the ledger, not the log, is the memory. |
| The phone shows a new `CONDUCTOR` entry, and the old one lingers as offline | Expected (RC skill: a relaunch is a new session entry). The fresh window's first message says "fresh Conductor; the old one is closed" so he knows which entry to use. |
| A whole-fleet kill takes the Conductor down with everything else (`fleet_stop` kills ALL claude pids) | The Conductor restart never calls `fleet_stop`. Conversely, an account failover kills the Conductor too, so `CONDUCTOR` is added to the failover `-Seats` list. |
| The 08:00/20:00 headless quick checks (`dispatcher_schedule.json`) run beside the standing window | While a live `CONDUCTOR` pid exists, the quick check writes its findings into `briefing.json` / `log.md` instead of launching a second Conductor. |
| The close-out misses a ruling (the agent checks itself) | `conductor_closeout.py check` is a program. A gap it finds blocks `closeout: ok`. The gap's text is stored in `GOODBYE`, retried by the next window, and shown in Must know until it is recorded (`GOODBYE` is a Briefing input). |
| `/clear` or `/login` typed in the window | `/clear` keeps RC (seen 2026-10-27; upstream reports differ). `/login` drops RC fleet-wide, so it is never part of this path (RC skill, procedure B). |
| The relaunch fails (wt.exe or interop down) | B3.5 files an item and pushes one line. He still has the Server tile and `rc rescue` (RC skill layer 2-3). |

### B5. Contradictions propagated (2026-10-28)

Done in the text: `src/RimMandrake/rimflow/roles/conductor.md` (his goodbye is the one Dispatcher trigger; quick mode is a
standing window, fresh after each goodbye), `design/RimMandrake/rimflow_v3_2026-10-26.md` ("fresh per message" is now
fresh per goodbye), the `_why` of the Conductor role in `src/RimMandrake/rimflow/dispatcher_schedule.json`.
Owed to the build (B6 step 4): the `quick_checks_local` launch must not fire beside a live `CONDUCTOR` pid (code in
`role_launch.py`), and `CONDUCTOR` goes into the failover `-Seats` list (that list is in the machine's launcher config,
not in the repo).

### B6. Build order (for whoever takes it)

1. `briefing.py` JSON and the two renderers (Part A). This is useful even before the window exists.
2. The `CONDUCTOR` wt profile and `launch_fleet.ps1` seat.
3. `conductor_closeout.py check` and the `GOODBYE` file.
4. Dispatcher handling of `GOODBYE` (grace, busy, kill by PID, relaunch, verify), with selftests for: cancel on a new message, never `fleet_stop`, and a refusal when the pid is not `CONDUCTOR`.
5. Propagate B5.

## Review trail

- **Naive judge, rounds 1 and 2** (gpt_consult, 2026-10-27; `D:\ClaudeWork\rimmandrake\conductor_briefing\judge1.md`, `judge2.md`): 25 and 12 findings on the first mockups. What still stands from them:
  - Q-codes are per item (`qcodes.json`) and never reused.
  - The Conductor reads the JSON only.
  - `GOODBYE` is a state machine, with a quiet check and a re-check before the kill; `GOODBYE.lock` uses exclusive create.
  - Close-out gaps are kept as text.
  - "Probably answered" items are never auto-routed.
  - Briefing-proposed questions are filed as items first.
- **The owner rejected the first mockups** as cryptic (his words are under "What he said"). The layout and voice in A2-A3 were redesigned from scratch for v2.
- **Blind checks of v2** (gpt_consult, 2026-10-27; `blind_check_v2_1.md`, `blind_check_v2_2.md` in the same folder). The reader was given only the pages and asked what they sound like and what a creative human would want to know after a long unsupervised run. The framing prompt of the first owner-rejection pass was not saved, so the prompt was written afresh. Each check's findings were applied to both pages. What it changed:
  - a verdict on the night up front;
  - a missed instruction is reported as missed and carried out by default, not asked again;
  - every problem has an owner;
  - "done" became built / tried in your game / approved;
  - claims that the evidence didn't show were cut;
  - project names got plain glosses;
  - the phone was brought level with the desk on decisions and defaults.

  What check 2 still flags is listed at the end of A3.
