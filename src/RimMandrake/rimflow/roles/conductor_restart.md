# Conductor window restarts: goodbye, reset switch, context backstop, handoff, checkpoint

This file holds the mechanics behind `conductor.md` "When you run". This file says how the code carries out each rule, the settings that it reads, and the rulings behind it.

One goodbye ruling replaced another. He first asked for a 30-second countdown (2026-11-01). The countdown is now
`goodbye_quiet_s` 0, instant (owner 2026-11-01).

## The reset switch, the goodbye kill and the backstop

**The reset switch (owner 2026-11-03, *"I wish there were a switch I could click on Conductor that said "hold for user interaction" or "ready to reset as soon as possible" or "auto""*; CONDUCTOR_RESET_FIX_KILLED_MID_READ).**

- If his WHOLE message is `hold`, `ready` or `auto`, that word sets the switch for this window
  (`.claude/hooks/conductor_goodbye.py`; `src/RimMandrake/rimflow/reset_mode.py`). The status line shows the switch.
- **hold:** no context restart while he reads or types, up to a ceiling. The ceiling is `hold_ceiling_tokens`, or
  `hold_max_s` with no message from him. Past the ceiling, the ordinary limits return, and he hears it once.
- **ready:** restart at the next ended turn, at any size. Live helpers still hold the restart. A new message from him
  delays it one round.
- **auto:** the limits below.

**The goodbye kill is ON.** Owner 2026-10-29, after blind review 3 (the third blind code review of this restart; it found that the check
and the kill of a live window cannot be one step): *"Leave the goodbye kill on. If I'm typing at the same time it's an acceptable risk."*
The goodbye restart below is ON (`seat_restart.seats.BENCH._why_enabled`).

**The context backstop for this window is ON** (owner by card 2026-11-01: "Should the Conductor restart itself like Foundry? → Same limits as Foundry"; `seat_restart.seats.BENCH._why_backstop`).

- Over 110k, idle 30 min, no message from him for 4 h, no helper alive: the backstop restarts the window.
- Over 400k: the backstop restarts the window at the next ended turn plus 20 s of quiet, **even mid-conversation**. The
  reason: this limit copies the hard limit of the retired FOUNDRY seat. That hard limit did not wait for him. His typing
  cancels the restart, and the next tick re-arms it.
- A goodbye outranks all of the backstop. A goodbye is instant and uninterruptible, and it joins any pending backstop.

His message is not a Dispatcher trigger, with one exception: his **goodbye** in the standing Remote Control `CONDUCTOR`
window (owner 2026-10-27/28: *"Goodbye should be the trigger."*, *"Yes I like your design. Go with it."*).

- The goodbye runs the LIGHT close-out. The close-out has three parts:
  - a program check of his rulings and answers against the ledger;
  - open promises, filed `--for OWNER`;
  - a 3-5 line note to the Conductor log, which the wake reads.
- The program is `conductor_closeout.py check`. `seat_restart.py request` stores its verdict and its gaps. The next wake
  prints them until they are recorded or dismissed.
- BUILT (2026-10-29, `CONDUCTOR_GOODBYE_DESIGN_FRESH_EACH_TIME`): `.claude/hooks/conductor_goodbye.py` matches his WHOLE
  message and prints the close-out. The close-out ends in `seat_restart.py request --seat CONDUCTOR --fresh --now`.
  That request is the normal end of any Conductor window: the request file wakes `rm-restart-now.path`, and the
  restart lands within seconds.
- The Dispatcher restarts the window at once, as a fresh Remote Control `CONDUCTOR` (`goodbye_quiet_s` 0, owner
  2026-11-01).
- Only a live helper, the bridge or PAUSE holds the restart. PAUSE is the Dispatcher's stop-everything file
  (`state/PAUSE`). On a goodbye, the background commands of the window end with the window.
- A request that printed DEFERRED (live helpers) drains: it waits for the live helpers to end.
- The wake of the fresh window lists, whole, what he sent the old window after the goodbye. The wake lists that text
  again until a window has answered. `--gen` binds the wake to that one restart.

**A full handoff is written only when a keyboard sitting ends.**

- When a handoff is written, the last message of the window says `HANDOFF READY` on a line of its own (or opening a
  line, then a stamp).
- The Stop hook `.claude/hooks/handoff_restart.py` then runs `handoff.py --check` and
  `seat_restart.py request --ticket HANDOFF --fresh --now`. The restart needs no goodbye of his, and his presence is not read.
- So the kill follows the turn end by seconds, not by the Dispatcher's 120 s timer
  (CONDUCTOR_REBOOT_FIX_THREE_WASTED_MINUTES, owner 2026-11-03).
- Live helpers still hold the kill. The end of the last helper re-kicks it.

The restart is the shared one in `src/RimMandrake/rimflow/seat_restart.py` (`seat_restart.seats.BENCH`, kind
`conductor`). The Conductor design: `design/RimMandrake/conductor_briefing_2026-10-28.md` Part B.

The Dispatcher rules: `src/RimMandrake/rimflow/roles/conductor.md` §When you run. The details that it lacks:

- The Dispatcher can refuse to start a quick run, or stop one that has gone on too long. It journals what it refused
  or stopped.
- In a scheduled or Dispatcher-launched run, the helper allocator may give you fewer helpers than you ask for.
- In a scheduled run, when a helper launch is refused, tell him once, in one line, and keep working.

## Goodbye: what he said, the drain and the checkpoint

Owner, 2026-11-01:
*"I want a goodbye that cannot be interrupted by text. Period. Additional text is just written to a handoff but does not
stop the countdown. And the countdown should be thirty seconds."*

- No input cancels or delays the goodbye, his or any machine's. If need be, the window is killed mid-reply. What he
  sent after the goodbye lands in the Conductor log and the wake.
- Live helpers never refuse a goodbye. The window takes no ticket and spawns nothing.
- When the last helper is done, end the turn. The restart publishes the window's ledger shard
  (`infrastructure/state/ledger/events/BENCH.jsonl`) itself (§Held or refused).

**Checkpoint, so a drain never freezes him** (owner 2026-11-02: *"a context-draining agent be able to redirect
long-running subagents to just write out their results to their tickets"*; CONDUCTOR_RESTART_REDESIGN_NEVER_FREEZE_HIM).
A helper cannot outlive this window. So a drain with long helpers has four steps:

1. Run `seat_restart.py checkpoint --seat CONDUCTOR`. The command lists the agentId and the item of each live helper,
   and records a 10-min deadline.
2. SendMessage each helper (`to` = the agentId) the order *"Checkpoint now: write your state, evidence paths and one
   imperative NEXT as a note on your item, commit and publish what is done, then stop."*
3. Run `seat_restart.py checkpoint --seat CONDUCTOR --wait`. Run it again until it says DONE or LOST. At the deadline,
   a helper that is still alive is LOST. Its item gets a note, the kill stops waiting on it, and the wake lists it.
4. Run `seat_restart.py request --seat CONDUCTOR` with the flags of the goodbye close-out. The command publishes the
   window's ledger shard (`infrastructure/state/ledger/events/BENCH.jsonl`).

Work expected to run over ~20 min goes to a detached helper: `src/RimMandrake/rimflow/roles/conductor.md` §When you run.
- The command runs the work in its own unit (pool clone, bounded time and spend).
- The detached run survives your restart. It ends with a note on the item and a line in this log.
- `detached_helper.py status` lists runs.

Code: `seat_restart.seats.BENCH`, kind `conductor`. The request binds the time of his goodbye, a transcript byte cursor
and the path of the transcript. The Dispatcher reads everything after the cursor in full, and ignores timestamps. The Dispatcher reads
again right before the kill.

The fresh window runs `seat_restart.py wake --seat CONDUCTOR --gen <restart id>` first.

- The command lists, whole, everything that he sent the old window after the goodbye.
- It lists that text again until a window has answered. So a fresh window that dies on it costs nothing.
- A window opened without a token runs the same command with no `--gen`.

The request can print REFUSED. The causes that the request names:

- a shard that it could not publish, or one that git cannot read, with no helper alive;
- his last message is no longer the goodbye: answer him.

Every refusal names the blocker and the smallest fix. What to do then: `conductor.md` "When you run".

## Held or refused: the shard publishes itself, and the hold is seen

The incident behind this section is RIMMANDRAKE_PUBLISH_HELD_RESTART_LEDGER_LINE_SILENT_TWO_HOURS (2026-11-15; its
story: `design/RimMandrake/roles.history.md` §conductor_restart.md).

Built in `seat_restart.py`:

- **The shard is never the window's job at the kill.** Three steps publish the seat's own shard themselves, and then
  proceed: the request, the drain of the Stop hook, and the Dispatcher's re-check right before the kill.
  - Each step uses `publish_owed_shard`: commit by explicit path, `./publish`, re-check, up to three rounds. So a
    peer's append in between is published too.
  - Only the shard: a local commit of anything else refuses before `./publish` runs.
  - A shard line that origin already holds under another commit hash reads as published. So a stranded clone no
    longer reads unpushed for ever.
  - If the publish fails, the hold names the files that block the publish, and the smallest fix. An example is a
    stray uncommitted file that stops `./publish`. The kill tries again after 5 min.
- **A hold is seen.**
  - The first hold of a restart writes one RAISE FIRST line to the Conductor log (`restart:<SEAT>:held_first`), every
    hold named with its fix.
  - A HANDOFF READY or goodbye still held 10 min after its request (`held_tell_s` 600) raises one alarm. For any other
    restart, the alarm comes at `hold_alarm_s`. The alarm has the fixed id `restart:<SEAT>:held`. The alarm goes into the
    Conductor log, once per restart.
- **The window hears it.** While its restart is refused (`restart/<SEAT>.refused.json`) or held, every prompt that he
  sends that window carries the reason (`conductor_goodbye.py`, `seat_restart.restart_notice`). So the window stops
  saying HANDOFF READY into the void. Fix what the reason names, or tell him in one line why the window stays open.

These still hold the restart, as before: a live helper, the bridge or driver lock, PAUSE, and his reset switch.
Background commands hold every restart of this window but a goodbye (`seat_restart.conductor_holds`). A dirty file that is not a ledger file holds the restart only when it stops the shard's publish.
Selftest: `selftest_seat_restart_held.py`.

**Authority:** `CLAUDE.md` §The Conductor speaks with the owner's authority. Record an act on a Conductor
instruction `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`, plus the Conductor's text in `--why`.
