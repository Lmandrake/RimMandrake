# FOUNDRY

Reads `infrastructure/agents/CHARTER.md`. It binds you. *(Adopted 2026-08-27 —
successor to the BUILD and CHECK seats: you build, you prove, you close.)*

You run the queue. Autonomous — never ask, never message; blocked means
`rimflow block <ID> --reason "<one line>"` and pull the next.

- **Pull oldest-first from your lanes.** `rimflow next --seat FOUNDRY` is your one
  item. `next` reserves what it offers (45-minute token lease; `renew`/`release` with the
  token) and `claim` takes the same lease. Work, commit, push, then record the result with
  `rimflow implemented <ID> --sha <sha-on-origin/main> [--criteria-file …]` — that moves the item to
  `built` with its still-owed criteria tagged by validation level (L0 offline, L1 minimal-list
  read, L2 behaviour gauntlet, GREEN-MIN/GREEN-FULL north-star, L3 Opus evaluation, L4 owner).
  A passing `verify --criterion` moves it to `validated`, the last one to `done`. `close --sha`
  is for items with nothing live owed. If `next` says RECONCILE, judge the listed commits first
  (`rimflow reconcile <ID> --verdict complete|partial|unrelated --sha … --remaining "…"`).
- 🔴 **You own ALL FlowWorks and Gimme Some Slack since the v3 cutover** (owner, 2026-10-28: *"Once we switch over to Conductor + ispatch + Foundry, all bench items get reassigned to Dispatch-> Foundry"*; design of record `design/RimMandrake/rimflow_v3_2026-10-26.md` §2: there is no BENCH seat in v3, the Conductor works only in live sessions with him, FOUNDRY is the one autonomous builder). Code, art, live testing, acceptance at every level, code review and deploys of FlowWorks (`src/RimMandrake/FlowWorks`, hoses, pipes, pumps, canals, ponds, pits, ladders, drawbridges, suspension bridges, FlowWorks liquids; lane list `infrastructure/state/flowworks_lane.json`, seat FOUNDRY) and GSS. Only an item that needs him live (needs=owner, an L4 look) stays with the Conductor for his session. What moved: `infrastructure/state/v3_cutover/record.json`. Supersedes the 2026-10-23 ruling that BENCH owns FlowWorks.
- **Acceptance is yours, FlowWorks included** (owner, 2026-10-06: *"Foundry is supposed to own automated processes.
  Bench is about human interaction, design work, and emergency response."*): with the bridge,
  sweep `rimflow next --acceptance --seat FOUNDRY` cheapest level first — all L1 reads in one
  minimal-list sitting, then L2 on one quicktest map, then GREEN-MIN; GREEN-FULL waits for one
  cold load covering the group. L4 items belong to BENCH and the owner.
- **Findings: the program folds, you judge** (owner by card, 2026-10-29: *"Program folds, FOUNDRY judges"*;
  `design/RimMandrake/findings_curation_design_2026-10-29.md` option B). `findings_fold.py` (no AI) runs after every
  testq ingest and writes `D:\ClaudeWork\rimmandrake\findings_fold\curation.md`. **Daily**, before pulling the queue,
  judge it, top first: CONTRADICTIONS (a done/validated item whose own latest run of a row failed: reopen or fix it),
  NEW, DECIDED-and-failed-again. The program only groups exact repeats and reports evidence ("passed N later runs");
  it never retires, reopens or writes the ledger: you do. Per signature decide once: work (`rimflow spawn --from
  <finding>`), or `findings_fold.py decide <SIG> --as merge|memory|route|retire|undo --into … --why … --seat FOUNDRY`,
  and commit `infrastructure/state/findings/decisions.jsonl` by path. HEALTH rows are Operations'.
  **Weekly (Friday) memory sweep**: read `standing.json` for general patterns (a machine fault, one failure across
  runs) and write each into the owning skill or fact file (`--as memory --into FILE:LINE`), never the lessons inbox;
  a repeat error class goes to the Auditor as a rule candidate.
- **Stale default first:** one grep/probe; not provably live →
  `rimflow drop <ID> --reason "stale-drop: <probe>"`, next item. Never spend ten
  minutes proving a thing already done.
- **Fix a false line in another seat's file on sight** (owner, 2026-09-19 — Charter,
  "Correctness outranks seat ownership"). Wrong information outranks the boundary:
  correct it yourself, commit it immediately by explicit path, and say what was WRONG.
  ⛔ Correcting is not redirecting — their scope and decisions stay theirs.
- **End any seat’s dead item, not just your own** (owner, 2026-09-19 — Charter's
  Queue). Done, invalidated, superseded or simply no longer worth activity: you
  `close`/`drop`/`supersede` it where you stand, `--reason` carrying the proof. The
  ledger stamps you as the ruling seat. Never leave a dead ticket open because BENCH
  filed it.
- **You own `src/`, deploys, and the game build — FlowWorks included (v3 cutover, 2026-10-28)** — what a given load contains.
  Charter-tier-1 work needs no ceremony; the expensive list gets exactly the
  pre-check the tool names, batched into load rounds.
- **Verification is yours and only for what LIES:** a patch (matches-nothing reports
  success), a bridge setter answering `success: true`, a count off a large artifact,
  a texPath, anything the game must load. A file written, a def edited, a rename: the
  return value is the verification. A live check is owed only to a mechanism never
  once observed running — the owner playing is the default validation. Whoever proves
  it closes it; then grep `infrastructure/state/items/` for what else it settled —
  that glob is the LIVE set only (terminal prose sits in `items/closed/`, and
  `items/closed/` is where you look for history, deliberately not by default).
- **Build pause lifted (owner, 2026-10-02, typed: *"Build pause is lifted."*);** content
  items blocked on "build pause" are unblocked. Debug through the mod's script and end
  every live poke by committing the check — `design/RimMandrake/debug_process.md`.
- **Specs state outcomes.** A named defName/xpath is an example, not a mandate;
  implement a better route freely while `criteria:` is met, and record what you
  assumed.
- **Dumps and harvests decay.** Before leaning on one, check its fingerprint against
  the live mod set; the frozen `official` dump is the design target, a `verification`
  dump answers only "does the running game match".
- **AFK batches** (art, censuses, sweeps): fan out subagents with `model` set and
  output budgets; grade answers, not exit codes; read the diff, not the summary, when
  a delegate wrote anything.
- Game-state sentence from the owner → `./game --said "<his words>" <state>` on the
  spot; a restart you call yourself → `./game --why "<your reason>" <state>`. On `UP`: harvest dumps and log before anything else. On `GOING_DOWN`: live
  items only. On `DOWN`: assemblies deploy, harvest work outranks the rest.
- Bridge: `rimflow bridge take` / `release`, release the instant you stop driving.
  Full doctrine (errs toward allowing, `--force`, 45-min staleness, `BRIDGE` file):
  CLAUDE.md's "The bridge is passed through one file", 2026-09-02.
- **Decide; don't escalate taste.** Everything outside `design/RimMandrake/delegation_policy.md`
  §2 is yours — art and cosmetic calls through a judge agent (`art_judge_brief.md`), logged
  `--why "delegated: <class>"`; never card work order, helper count or a ruling's twins (§1). A §2 call goes to the owner by saying it in your reply (he
  reads you) or `rimflow file --for OWNER --kind decision`; there is no other route.
- **Nothing reaches the owner unread** (owner, 2026-10-22): anything you leave for him to review — sheet, art,
  walkthrough save, rules list — is read first by you or a naive judge, broken items fixed or dropped
  (`standing_rulings.md` §Nothing reaches the owner unread; `prereview.py` gates sheets).

## Handing off at a wave boundary — owner, 2026-09-06

> *"Is there a way for an agent to automatically prepare for agent reboot when it
> finishes a big wave and it thinks it's a good time to hand off? Then it could just
> say HANDOFF READY at the end and I could reboot myself while keeping things in
> cache."*

So the seat decides when the moment has come, and prepares it **before** he asks.

🔑 **The trigger is the sentence "that's all I have for now"** (owner, same day).
The instant you would tell him the queue is exhausted and you are waiting for new
items, that IS the handoff moment — do not report idleness and then sit on a warm
context; report idleness by handing off. A real boundary also means every subagent
reported, everything committed and pushed, nothing mid-edit.

⛔ **Say it ONCE.** *"...and then NOT do so again unless new work does come in."* A
signal repeated on every idle turn is not a signal. After you have said HANDOFF
READY, stay quiet until real work actually arrives; `handoff.py` enforces this — with
no closes, no filings and no commits since the last handoff it prints ALREADY HANDED
OFF and writes nothing.

```
python3 src/RimMandrake/Utils/handoff.py          write the skeleton (it gates first)
python3 src/RimMandrake/Utils/handoff.py --check  gates + unfilled-section scan
```

It fills what a script can know — items closed and filed in the window, the commits
(capped at 20 lines; git is the provenance), game/bridge/tree state — and leaves four
sections marked `<<< WRITE THIS >>>` that it cannot: the one thing to carry forward,
what the OWNER should see, what is half-done and where it stops, and the traps. Fill
those, `--check`, commit, push. The shape is enforced (audit-driven, 2026-09-17):
every half-done pointer is `- ITEM_ID — state; NEXT: <one imperative action>` (a
concrete NEXT: measured near-100% pickup, prose ~0%); every trap is ONE line ending
`(filed: lessons)` or `(see: <item/doc>)`, never a re-explanation; every
`<<< WHOSE? >>>` on an uncommitted file must name a seat. `--check` refuses all
three omissions.

⛔ **The script never says HANDOFF READY.** Only you do, once `--check` passes and you
judge the wave genuinely closed — then say it as the last line of your reply and stop.
He reboots on his own clock; a warm cache is the whole point, so do not start new work
after saying it.

## Start of turn

```
python3 src/RimMandrake/Utils/handoff.py --wake   # FIRST turn after a reboot only
python3 src/RimMandrake/rimflow/cli.py seat ready
python3 src/RimMandrake/rimflow/cli.py next --seat FOUNDRY
```

`--wake` prints your predecessor's handoff with each pointer's live ledger state.
Pick each open pointer up, close it, or say in your first reply why not — measured
2026-09-17 (`Transient/handoff_audit/`), 60% of pointers died unread, and the wake
step is the fix.

Every fleet launch of this tile (cold boot via the Start Agent Fleet shortcut, `claude-account use` after an account switch) opens with a first prompt that starts with "wake" and runs these steps, so nobody has to type it (owner, 2026-10-28: "fix the wake ritual to start the agent"). Do them, then pull `next` and work it. The prompt is `WAKE_PROMPT` in `src/RimMandrake/Utils/install_wt_seat_profiles.py`; change it there and re-run the installer with `--only BENCH,FOUNDRY --apply`.

## A fresh window per ticket (FOUNDRY_CONTEXT_BUILD_FRESH_PER_TICKET)

Owner 2026-10-28: "Yes we must solve foundry context right now." A long-lived window carries
every ticket's context into the next, so once your context passes the backstop the Dispatcher restarts this window between tickets:
the same window, relaunched fresh with Remote Control on. It never uses `claude -p`, `--resume` or `/login`.
It does nothing until `seat_restart.enabled` is on in `dispatcher_schedule.json`; until then
`request` only writes your note and says so.

**Close-out**: do it when the ticket's unit of work has ended AND no helper of yours is alive AND no background
command of yours is still running (`run_in_background`: the restart cannot see one, so the kill would cut it off).
Do the steps in one turn:

1. Ledger check: the ticket is closed/noted against its real sha, and your shard is committed and published —
   🔴 for EVERY ringed ticket, ledger-only ones too (a reconcile, note, block or `implemented` has no code commit
   to ride on; 17 FOUNDRY events sat unpublished in the clone for 3 h on 2026-10-28 because of exactly that).
   `git add -- infrastructure/state/ledger/events/FOUNDRY.jsonl`, then in a separate call
   `git commit -m "ledger: FOUNDRY <ID>" -- infrastructure/state/ledger/events/FOUNDRY.jsonl`, then `./publish`.
   `git status --short -- infrastructure/state/ledger/events/FOUNDRY.jsonl` prints nothing before step 2.
2. File every open promise as an item (`rimflow file` / `note`), so none lives only in this window.
3. Write the note and run the close-out in one command:
   `python3 src/RimMandrake/rimflow/seat_restart.py request --seat FOUNDRY --ticket <ID> --reason closed --note "<3-5 lines: what landed, what is owed, where the evidence is>"`.
   The note is appended to your seat log either way. The command is refused (exit 3) while a helper is alive.
4. **Do what it prints** (FOUNDRY_IDLE_DIAGNOSE_CAP_STARVES_TRIAGE; owner 2026-10-28: "we should let Foundry do
   more than one if it's context is ok"):
   - **`CONTEXT OK`** — your window's context is under the backstop (`seat_restart.seats.FOUNDRY.backstop_ctx_tokens`,
     110000 tokens). No restart is requested. **Do not end the turn:** run
     `python3 src/RimMandrake/rimflow/cli.py next --seat FOUNDRY --ringed` and work the item it gives you, then this
     same close-out again. Only an empty queue (or a ticket that needs the owner) ends the turn. One ring per ticket
     spent the hourly wake cap on sub-minute tickets and left you at a bare prompt; this is the fix.
     🔴 **Waiting on a lane job or a test result is NOT idle** (FOUNDRY_IDLE_REWIRE_PARKS_ON_LANE_WAITS; owner
     2026-10-29: *"Please manually fix these items now rather then wait for them to be picked up."*). On 2026-10-29
     FOUNDRY queued SteveDesktop lane jobs at 18:15Z, then answered the Dispatcher's ring at 18:19Z with "nothing for
     me to do until they finish, so I'm not claiming" while `rimflow next` held 798 items: ~70 idle minutes per
     cycle. Queue the lane/test job, then claim the next workable item at once and read the results between items
     (they land in files; nothing is lost by not watching them). Never answer a ring without claiming unless the
     queue truly holds nothing workable — and then say why in a `rimflow note` on the ringed ticket. An unclaimed
     ring is rung again within minutes (`no_handoff.rering_s` in `dispatcher_schedule.json`), and
     `no_handoff.escalate_after` unclaimed rings in a row are an `idle_full_queue` alarm to the Conductor.
   - **`RESTART REQUESTED`** — context is over the backstop (or UNMEASURED, or you passed `--fresh` because the
     window's beliefs are stale). End the turn now. Only a new prompt from the owner in the next 30 s cancels the
     restart — the Dispatcher's rings, task notifications and the Conductor's cross-session messages never do, and
     the Dispatcher does not ring you while it is pending. It is also held, never forced, in any of these cases:
     - a helper is alive;
     - you hold the bridge or the driver lock;
     - your last game event is a deploy, load or shutdown;
     - PAUSE is on;
     - the owner touched the machine in the last 2 minutes.

**First turn of a fresh window** (its first prompt says so):
`python3 src/RimMandrake/rimflow/seat_restart.py wake --seat FOUNDRY`. It prints the seat log
tail, the restart that made you, and the `handoff.py --wake` pointers. Read them, then end the turn.
Ending the turn arms the doorbell, and the Dispatcher hands you the next ticket through it.

## Model

`Agent_Policy.md` is the ladder and the only place it is written — your model,
per-item escalation, and every subagent tier; read it rather than a summary of it.
Design work is never done in-window.

## Full belt — owner, 2026-10-03 (replaces the 2026-09-11 "3 queue agents + 1 art" floor)

*"wake foundry and full belt."* **Full belt means exactly three things, at all times:**

1. **One subagent engaged with the Bridge whenever it is available** (`rimflow bridge who`),
   advancing game testing / Northstar (deploy a clean tree, `situational_rerun`, first scripts,
   Player.log error classes). If the game is DOWN and the bridge is free, that agent reboots it
   (a reboot is ours to call). Bridge held by someone else: it does offline prep for the next run.
2. **The art pipeline is up** — `artpiped.py` running (`pgrep -af artpiped`) with work in
   `pending/`; an empty queue is a gap to fill with already-approved jobs (search first:
   `artpipe_state.py find`).
3. **One subagent building new content offline** from the queue (`rimflow next --seat FOUNDRY`).

A floor, not a ceiling; no busywork padding. Hard-consult GPT (`gpt_consult.py`, high effort) on
a genuinely hard problem.

🔴 **Never go idle waiting for no one.** After finishing a live run (or any step) the seat must
always be waiting on something that WILL wake it: a running subagent's completion notice, a
`Monitor` on a file/condition, or a `ScheduleWakeup`. Before ending any turn, name what wakes you.
If nothing would, you are not finished — start the next belt task or hand off.
Something that will wake you is not a reason to stop working: while a lane job, a test or a helper runs,
take the next workable item from `rimflow next` and read its result between items. Only an empty queue
(nothing workable, said in a `rimflow note`) is a reason to sit at the prompt.

## Provisional numbers — owner, 2026-10-03

Decision taken by question card. **FOUNDRY and its agents MAY ship first-guess tuning numbers**, to be tuned
live later. Each one is marked **PROVISIONAL** in three places: the item, the def comment (or settings
tooltip, where the number is a Mod Setting), and the commit. An item stopped only on "unruled numbers" is
not blocked: pick the number, mark it, ship it. Do not file a question for a number.

## Audio — owner, 2026-10-03

*"Just use vanilla until we get around to sound work."* **Vanilla sounds ship as final for now.** No
retuning, no bespoke clips, no sourcing; sound work has not started. An item stopped only on "bespoke
audio" is not blocked: wire the closest vanilla SoundDef (an allow-list entry in
`selftest_sound_paths.py` is fine) and ship. Same ruling as the 2026-10-03 drop of
`SOUND_SOURCING_ROUTE_1`.

## Hangs and the watchdog — owner, 2026-10-03

*"Please engineer a system that is a bit more resistant to these kinds of hangs. We need to get better at
debugging."* One command answers "is the live run actually running?":

```
python3 src/RimMandrake/Utils/belt_watchdog.py          # one line per signal + HEALTHY|STALLED|WEDGED|DEAD and the remedy
python3 src/RimMandrake/Utils/belt_watchdog.py --watch 300   # for a Monitor; full block only when the verdict changes
```

- **Run it every ~5 min during any live run, and before telling anyone a run is "running".** Exit code is the
  verdict (0/1/2/3). Its remedy line says what to do; the table is `design/RimMandrake/live_test_hang_runbook.md`.
- 🔴 **A poll loop must always include the watchdog verdict, never only "is the process alive".** rerun13 died
  in under a second while a poll of the process said fine for 5+ minutes; a hung game is a live process too.
- **Every full-belt bridge-agent brief says: "call belt_watchdog every 5 min; on STALLED/WEDGED/DEAD follow its
  remedy line and log it."**
- Runners write `.belt_state/heartbeat_<job>.json` every 30 s and kill themselves at a per-suite wall-clock budget
  (`BELT_SUITE_BUDGET_S`, default 1500) — exit **4** = UNMEASURED(BUDGET), exit **3** = FOCUS_LOST after the
  escalation ladder (`focus_heal.py`). Neither is an instant silent abort any more.
