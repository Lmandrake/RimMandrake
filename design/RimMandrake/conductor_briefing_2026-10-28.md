# Conductor Briefing and the goodbye lifecycle

**Date:** 2026-10-28 · **Seat:** BENCH (design helper) · **Status:** design. The owner reviews it; nothing in it is built yet.
**Items:** `CONDUCTOR_BRIEFING_DESIGN_ONE_PAGE_NOT_SIX`, `CONDUCTOR_GOODBYE_DESIGN_FRESH_EACH_TIME`
**Mockups (today's real data):**
- `D:\ClaudeWork\rimmandrake\conductor_briefing\briefing_phone.html`
- `D:\ClaudeWork\rimmandrake\conductor_briefing\briefing_desk.html`

## What he said (verbatim, from the ledger)

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
   - The digest's "Plan usage" lines are token data, which the token-blind Conductor may not read. The Conductor therefore cannot talk him through the page he is reading.
3. **There is nothing to be "on track" against, and the hub answers a different question.**
   - `infrastructure/state/CONDUCTOR_GOALS.md` does not exist.
   - The Producer is not running, so neither page can say on or off track.
   - The hub ("Utinni Control Room") is an 11 MB inventory of codebase health, maturity and registers. Its `publish_ready.json` is from 2026-10-02 (25 days stale).
   - Only a Claude Artifact call can publish the hub. It answers "what exists", never "what changed" or "what needs me".

**Consequence for the design:** one page, built from one data set. It leads with what needs him, counts the backlog as well as the new, carries a short code on every question so he can answer in chat, and keeps token data in a band the Conductor never reads.

---

## Part A — the Briefing

### A1. Shape: one data set, two renderings

- **Program:** `src/RimMandrake/rimflow/briefing.py` (proposed).
  - It writes `D:\ClaudeWork\rimmandrake\conductor\briefing.json`. This is the **blind** data set.
  - It renders `briefing_phone.html` and `briefing_desk.html` from that one JSON file.
  - The Conductor reads **only the JSON**, never the HTML, because the HTML carries the owner-only band. It writes only the `narrative` fields (at most 3 short lines per section, marked `by: Conductor`) and the `ask` text of a question whose item title is not phrased as a question.
- **Owner-only band:**
  - `D:\ClaudeWork\rimmandrake\ops_watch\owner\briefing_owner.json` holds token and runway lines from Operations.
  - Only the HTML renderer reads it. The renderer folds it into a collapsed band that he sees and the Conductor does not.
  - This keeps the Conductor token-blind (`roles/conductor.md`, closed list) while he still gets one page.
- **When it is built:**
  - on every Conductor wake;
  - after every Dispatcher run of Operations;
  - when he opens the page and it is more than 10 min old.

  It is not built on a fixed 05:45/17:15 clock.
- **Where it is served:** by the existing pulse daemon (127.0.0.1:8765, tailnet :8791), as `/briefing` (the phone picks it by user agent or `?v=phone`) and `/briefing?v=desk`. No new server is needed.

### A2. "Since you last read"

- **Keyed on his last read**, recorded in `brief_opens.json`. The brief already does this (`brief.since_basis`), so the code is reused.
  - A read counts only while the page is visible (the existing rule).
  - Opening it on the phone moves the mark for both renderings, because he is one reader.
  - **The mark advances to the snapshot's data cutoff, not to the moment he looked.** Each `briefing.json` records `data_through` (the newest ledger tsn and source times it saw). A read moves the mark to that cutoff, and only forward. Anything that landed after the snapshot was built stays "new" for the next page.
  - "Nothing new" is said only when every source's `data_through` is past the mark. If a source has not refreshed since, the line says "no fresh data from <source> since <time>" instead.
- **Every count is shown twice:** `new since you read` / `total open`.
  - The digest showed only the first number, and that is what made it say "0" while 49 waited.
- **Top line:** "since you read at 17:15 Tue (2 h 40 m ago)".
  - If there is no read on record, it says "no read on record; showing the last 24 h". That is one line, not a silent default.

### A3. Sections, in his order

**Order rule:** must-know first (short), then questions. Everything after the questions is reading, not deciding.

| # | Section | Shows | Data source (field ← source) | Phone | Desk |
|---|---|---|---|---|---|
| 0 | **Header** | since-read mark, generated time, each source's data-through time and age in minutes | `brief_opens.json`; `data_through` of every input below | 1 line + missing sources | 1 line + every source with its age |
| 1 | **Must know** (≤3 lines) | only things that change what he does today: an alarm open, the game or Steve down, a ruling broken, a close-out gap, a source missing | `ops_watch/digest_blind.md` alarms (`TIMER_FAILED`…); `pulse_now.json` (game, bridge, lost windows); `conductor/GOODBYE` gaps; a source missing from this list | ≤3 lines with their state, red only if alarm | same + item ids and source names |
| 2 | **Questions for you** | the non-walk items with `needs=owner` (decide, then look), each with code `Q…`, age, one-line ask, item id; then **probably answered — please confirm** as one batch question; then "promised to you: n" | ledger replay (`model.replay`): `needs=="owner" or owner=="OWNER"`, non-terminal; probably answered = his last `OWNER`/`ownerSaid`/`byCard` event is at or after the `needs→owner` event (ESTIMATE) | first 5 of the sequence, then "+ n more on the desk page · 28 probably answered: confirm" | all, grouped decide / look, plus the full probably-answered list |
| 3 | **Live-walk requests** | the walk items from the same population, each asking him to pick a time; proposed slots | items whose title or kind marks a walk (`WALK`, `SITTING`, `in game`, needs game-up) among the owner items; Ops W1 count shown with its scope; `slot_allocator` free windows | first 3 of the sequence + count | all + proposed slot per walk |
| 4 | **Review artifacts** | sheets and looks ready for him; held ones with the reason they are held | pulse hands (`hands.jsonl`), `review_sheets` registry, `art_sheet.py` gate state; held = gate refused (`no prereview`) | count + summary of holds | full list with hold reasons and ages; stale holds (>7 d) become a filed "retire?" question |
| 5 | **Plan: progress, on/off track, changes to ratify** | the week's goals and the call on each; proposed changes waiting for "ratify" | `CONDUCTOR_GOALS.md` (absent today → one line "no goals file: on/off track UNMEASURED"); go-live wave dates from `rimflow_v3_golive_wave1.md` §5; Producer proposals (when enabled) | 1 line per goal | goals + evidence + proposal diff |
| 6 | **What worked / went wrong / fixed?** | closes since he read, by subject; failures with fixed: yes / no / unknown | ledger `close` events in the window (`rimflow_metrics.py` flow); pulse `failed` and `recovered`; Ops flags | 3 lines: counts + 1 notable each | grouped table, each failure with its item and fixed state |
| 7 | **Running now** | seats busy or idle, game, Steve lane, delegated work | `pulse_now.json`; `ops_watch/digest_blind.md` (Steve jobs); `Transient/delegated_digest_<date>.md`; `slot_allocator` | 2 lines | per-seat table |
| 8 | **Health numbers** | flow, owner waits, verify backlog, blocked, Ops flags | `rimflow_metrics.py --json` (MEASURED); Ops flags (each keeps its own MEASURED/ESTIMATE) | 4 numbers | full KPI table incl. v3 KPIs (UNMEASURED until taken) |
| 9 | **Innovator ideas** | ideas filed since he read | `design/RimMandrake/innovations.md` | 1 line | list |
| 10 | **Owner-only band** (collapsed) | token runway, plan usage, Operations OP- proposals | `ops_watch/owner/briefing_owner.json`, `ops_watch/owner/OP-*.md` | collapsed | collapsed |

Sections 2 and 3 together hold every truly-waiting item, and the line under section 2 says so ("21 truly waiting (15 here + 6 walks)").

**Rules on every section:**
- **Number provenance.** Every number carries MEASURED, ESTIMATE or UNMEASURED, plus its source. The renderer refuses a number that has no tag. A derived number (a subtraction, an age) inherits the weakest tag of its inputs. When every number in a section comes from one source, a single tag and source in the section header covers them (this is how the phone shows provenance without the desk's per-row source names); a number from a different source is tagged on its own line. Label words match the source's definition (for example "net +92 = 160 filed − 62 done − 3 superseded − 3 dropped").
- **Empty sections.** An empty section is one line that says why, for example "Innovator not enabled until Sun (v3.4) — no ideas". An empty section is never hidden.
- **Missing sources.** A missing or stale source is named in the header and the section says "source missing". Today `delegated_digest_2026-10-27.md` is missing. A missing source never reads as "0".
- **Common items.** Phone and desk share sections, codes, wording and data, and both use ONE canonical sequence: questions are sorted by kind (decide, look, walk), then newest first, and codes follow that sequence. The phone shows the first N plus a count line. The desk shows everything and adds ids and paths. **Every phone line also appears on the desk.** The desk lays sections 0-2 down the left column (with walks and review below them) and the reading sections down the right, without changing the order within either column.
- **Status travels with the alarm.** A must-know line carries its own state ("not fixed yet", "no work lost") on both renderings. Only ids and source names are desk-only.
- **Scopes are named.** When a Briefing count and an Ops count describe different populations (6 walks asked of him vs Ops W1's 10 walks owed by all seats), both are shown with their scope in one line.
- **When nothing is new,** a section says so in one line ("Nothing closed or broke since 19:33"). The last 24 h sit behind a collapsed "Last 24 h" line. The page does not quietly swap in a different window.
- **"Probably answered" is never auto-routed.** The 28 items whose last owner event is newer than the hand-off are an ESTIMATE. The Conductor confirms each with him (one batch question) before it moves any of them. The 21 "truly waiting" count inherits that ESTIMATE tag.
- **Asks are answerable.** Every row states its ask in one line, with options when the item has them. A title that is not a question gets an `ask` from the Conductor. Before asking him anything, the Conductor runs `blind_view.py show <ID>` to check for an earlier ruling, which catches "already ruled" (C1) at the source.

### A4. Answers land on the ledger

The page has no buttons (card 2026-10-24 stands). The route is:

1. Each question carries a code, `Q1`…`Qn`. **The code belongs to the item, not to a page.** `D:\ClaudeWork\rimmandrake\conductor\qcodes.json` assigns a code from a counter that only goes up, the first time an item appears, and **never reuses a code**. An answer typed against an old page therefore still reaches the right item. Display order (the canonical sequence) is independent of the code numbers, so a new item can appear at the top carrying a high code. A question the Briefing itself proposes (for example "retire the 13 old hands") is filed as an item before it gets a code.
2. He answers in the Conductor's RC chat in any form, for example "Q2 mask CPU 18" or "Q1 ntfy". A code that resolves to a closed item gets "Q7 closed at <sha> — still want it?" in reply, never a silent re-route.
3. The Conductor resolves the code through `qcodes.json` and records his words verbatim:
   `rimflow note <ID> --owner-said "<his words>"` and, where it is a decision, `rimflow needs <ID> <seat>`. The note carries the RC message timestamp, so a retry can see the answer is already recorded.
4. The next build shows his recorded answer (the first 80 characters) on the row, until the item moves. Moving the item is a separate step from recording the answer.
5. The goodbye close-out (B2 step 1) re-checks that every Q-code he used reached the ledger.

### A5. What retires

- **Pulse digest** (`rm-pulse-digest`, 06:00/17:30) and **pulse brief page** (`rm-pulse-brief`, 05:45/17:15). Their collectors become `briefing.py` inputs, and their pages stop being sent.
  - Retire them only after the Briefing has run for a week and he has said the Briefing replaces them. Until then both stay up.
  - `brief_opens.json` and the brief's judge are kept.
- **Hub** (`infrastructure/dashboards/hub/`): frozen as an inventory, linked from the desk footer, no longer published. It does not answer "what needs me".
- **Delegated digest:** becomes Briefing section 7 (and section 2 when it has "Needs you" rows). The file stays as a source.
- **The 13 hands from 10-07 to 10-16 held for "no pre-read":** retire them or get them pre-read. A hold more than 7 days old shows in section 3 as "retire?".

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

  It then sends him the Briefing link and the top 3 questions. Nothing else is in its context, which is the "fresh each time" he chose. "Already ruled" messages (C1) were MEASURED at 7 in 14 days, and each one is a stale-context error.
- **Session mode** (at the keyboard) is the BENCH seat window, as today. The full handoff ritual runs there when a keyboard session ends.

### B2. The light close-out (about 30 s), triggered by his goodbye

**Trigger:** a message from him whose whole text is one of `goodbye`, `bye`, `gn`, `good night`, `done for now`, `that's all` (case-insensitive, punctuation ignored). A goodbye inside a longer message is not a trigger. The Conductor asks "close out?" instead.

Steps, in order:

1. **Rulings on the ledger.**
   - For every message he sent in this window that answered or ruled on something, the Conductor checks that a `--owner-said` event carries his words. A moved item does not count; the words must be recorded.
   - It records any that are missing, verbatim.
   - This is a self-check, so it is backed by a program: `conductor_closeout.py check` diffs his RC messages against the ledger and lists the gaps.
2. **Promises to items.** Anything the Conductor said it would do and has not done is filed `--for OWNER` with `--why`, one item each, tagged `promise` in the title's twist (for example `..._PROMISED_AT_GOODBYE`). Nothing stays only in chat. Briefing section 2 lists promises on their own line ("promised to you: n"), not as questions, so filing them never adds to his question count.
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
| Older rulings fall out of a fresh window's context | That is the point of freshness, but a question must never re-ask a ruled matter. The Conductor runs `blind_view.py show <ID>` before asking (A3 rules), and the ledger, not the log, is the memory. |
| The phone shows a new `CONDUCTOR` entry, and the old one lingers as offline | Expected (RC skill: a relaunch is a new session entry). The fresh window's first message says "fresh Conductor; the old one is closed" so he knows which entry to use. |
| A whole-fleet kill takes the Conductor down with everything else (`fleet_stop` kills ALL claude pids) | The Conductor restart never calls `fleet_stop`. Conversely, an account failover kills the Conductor too, so `CONDUCTOR` is added to the failover `-Seats` list. |
| The 08:00/20:00 headless quick checks (`dispatcher_schedule.json`) run beside the standing window | While a live `CONDUCTOR` pid exists, the quick check writes its findings into `briefing.json` / `log.md` instead of launching a second Conductor. |
| The close-out misses a ruling (the agent checks itself) | `conductor_closeout.py check` is a program. A gap it finds blocks `closeout: ok`. The gap's text is stored in `GOODBYE`, retried by the next window, and shown in Must know until it is recorded (`GOODBYE` is a Briefing input). |
| `/clear` or `/login` typed in the window | `/clear` keeps RC (seen 2026-10-27; upstream reports differ). `/login` drops RC fleet-wide, so it is never part of this path (RC skill, procedure B). |
| The relaunch fails (wt.exe or interop down) | B3.5 files an item and pushes one line. He still has the Server tile and `rc rescue` (RC skill layer 2-3). |

### B5. Contradictions to propagate (filed as items, not edited here)

- `src/RimMandrake/rimflow/roles/conductor.md`:
  - "His message is not a Dispatcher trigger" → his **goodbye** now is.
  - The quick-mode description → a standing RC window plus the light close-out.
- `design/RimMandrake/rimflow_v3_2026-10-26.md`: quick mode "fresh per message" → fresh per goodbye.
- `src/RimMandrake/rimflow/dispatcher_schedule.json`: the Conductor `quick_checks_local` must not launch beside a live `CONDUCTOR` pid (B4 row 5).
- `src/RimMandrake/Utils/account_failover.py` `-Seats` list: add `CONDUCTOR`.

### B6. Build order (for whoever takes it)

1. `briefing.py` JSON and the two renderers (Part A). This is useful even before the window exists.
2. The `CONDUCTOR` wt profile and `launch_fleet.ps1` seat.
3. `conductor_closeout.py check` and the `GOODBYE` file.
4. Dispatcher handling of `GOODBYE` (grace, busy, kill by PID, relaunch, verify), with selftests for: cancel on a new message, never `fleet_stop`, and a refusal when the pid is not `CONDUCTOR`.
5. Propagate B5.

## Review trail

- **Naive judge, round 1** (gpt_consult, 2026-10-27): 25 findings, recorded in `D:\ClaudeWork\rimmandrake\conductor_briefing\judge1.md`. All were taken except the net-flow arithmetic: +92 is correct (filed − done − superseded − dropped), and only the label changed. What changed as a result:
  - Q-codes are per item (`qcodes.json`).
  - The Conductor reads the JSON only.
  - `GOODBYE` is a state machine, with a quiet check and a re-check before the kill.
  - The read mark is the snapshot's data cutoff.
  - Close-out gaps are kept as text.
  - Promises are listed apart from questions.
  - "Probably answered" items are never auto-routed.
  - The order is one canonical sequence.
  - The wording on the mockups was fixed.
- **Naive judge, round 2** (`judge2.md`): 12 findings, all taken. The changes:
  - Codes are never reused.
  - "Nothing new" is said only when the sources cover the interval.
  - Briefing-proposed questions (Q22, Q23) are filed as items first.
  - The phone asks him to confirm the probably-answered batch.
  - The push options are spelled out, and walk rows ask him to pick a time.
  - Section order is questions → walks → review on both pages.
  - Hand ages are computed from one source.
  - Provenance is given per section.
  - `GOODBYE.lock` uses exclusive create.
