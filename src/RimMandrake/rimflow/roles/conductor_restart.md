# Conductor window restarts: goodbye, reset switch, context backstop, handoff, checkpoint

The mechanics behind `conductor.md` "When you run". The rules are stated there once; how each is built, the settings it reads and
the rulings behind it are here. One goodbye ruling replaced another: the 30-second countdown he first asked for (2026-11-01) is now
`goodbye_quiet_s` 0, instant (owner 2026-11-01).

## The reset switch, the goodbye kill and the backstop

**The reset switch (owner 2026-11-03, *"I wish there were a switch I could click on Conductor that said "hold for user interaction" or "ready to reset as soon as possible" or "auto""*; CONDUCTOR_RESET_FIX_KILLED_MID_READ).** His WHOLE message `hold`, `ready` or `auto` sets it for this window (`.claude/hooks/conductor_goodbye.py`; `src/RimMandrake/rimflow/reset_mode.py`), and the status line shows it. **hold:** no context restart while he reads or types, up to a ceiling (`hold_ceiling_tokens`, or `hold_max_s` with no message from him), past which the ordinary limits return and he hears it once. **ready:** restart at the next ended turn at any size; live helpers still hold it, and a new message from him delays it one round. **auto:** the limits below. A goodbye or HANDOFF READY outranks all three, and a fresh window always starts on auto. To set it for him when he says so in a longer sentence: `seat_restart.py mode hold`. **Every wake prints the old window's last reply: put it word for word at the top of your first reply, because the fresh window's screen is empty and he may have been reading it.**

**Owner 2026-10-29, after blind review 3: *"Leave the goodbye kill on. If I'm typing at the same time it's an acceptable risk."* The goodbye restart below is ON (`seat_restart.seats.BENCH._why_enabled`). The context backstop for this window is ON (owner by card 2026-11-01: "Should the Conductor restart itself like Foundry? → Same limits as Foundry"; `seat_restart.seats.BENCH._why_backstop`): over 110k, idle 30 min, no message from him for 4 h, no helper alive; over 200k it restarts at the next ended turn plus 20 s of quiet **even mid-conversation**, because Foundry's hard limit does not wait for him (his typing cancels and the next tick re-arms). A goodbye outranks all of it: instant, uninterruptible, joining any pending backstop.** His message is not a Dispatcher trigger, with one exception: his **goodbye** in the standing Remote Control `CONDUCTOR`
window (owner 2026-10-27/28: *"Goodbye should be the trigger."*, *"Yes I like your design. Go with it."*). The goodbye
runs the LIGHT close-out (a program check of his rulings and answers against the ledger, open promises filed `--for OWNER`,
a 3-5 line note to the Conductor log read at wake; the program is `conductor_closeout.py check`, and
`seat_restart.py request` stores its verdict and gaps, which the next wake prints until recorded or dismissed). BUILT (2026-10-29, `CONDUCTOR_GOODBYE_DESIGN_FRESH_EACH_TIME`): `.claude/hooks/conductor_goodbye.py` matches
his WHOLE message and prints the close-out, which ends in `seat_restart.py request --seat CONDUCTOR --fresh --now` (the normal end of any Conductor window: the file wakes `rm-restart-now.path` and the restart lands within seconds). The Dispatcher
restarts the window as a fresh Remote Control `CONDUCTOR` at once (`goodbye_quiet_s` 0, owner 2026-11-01), and no text stops
it (owner 2026-11-01), his or a machine's: the window is killed mid-reply if need be, and what he sent after the goodbye
goes to the Conductor log and the wake. Only a live helper, the bridge or PAUSE holds it; the window's own background commands end with it. A
request that printed DEFERRED (live helpers) drains. The fresh window's wake (`--gen` binds it to that one restart) lists, whole
and once, what he sent the old one after the goodbye. The context backstop (above) restarts it too: after 4 h with no message from him at 110k, at any ended turn at 200k. A full handoff is written only when a keyboard sitting ends. When a handoff is written, it ends in the window's last message saying `HANDOFF READY` on a line of its own (or opening a line, then a stamp): the Stop hook `.claude/hooks/handoff_restart.py` then runs `handoff.py --check` and `seat_restart.py request --ticket HANDOFF --fresh --now` (no goodbye of his needed; his presence is not read), so the kill follows the turn end by seconds, not by the Dispatcher's 120 s timer (CONDUCTOR_REBOOT_FIX_THREE_WASTED_MINUTES, owner 2026-11-03). Live helpers still hold the kill; the last one's end re-kicks it. The restart is the shared one in
`src/RimMandrake/rimflow/seat_restart.py` (`seat_restart.seats.BENCH`, kind `conductor`; the Conductor design:
`design/RimMandrake/conductor_briefing_2026-10-28.md` Part B). The Dispatcher launches only the
`quick_checks_local` runs, and none while a live `CONDUCTOR` window exists (that window writes the findings itself).
Session mode is the Conductor window the owner is already talking to; nothing starts it and nothing stops it but him.

The Dispatcher may refuse to start a quick run or stop one that has gone on too long, and it journals what it refused
or stopped; in a scheduled or Dispatcher-launched run the helper allocator may give you fewer helpers than you ask for. Those are
theirs, never yours. A reply to a message he sent in the window is always finished. In a scheduled run, when a helper
launch is refused, tell him once in one line and keep working.

## Goodbye: what he said, the drain and the checkpoint

Owner, 2026-11-01:
*"I want a goodbye that cannot be interrupted by text. Period. Additional text is just written to a handoff but does not
stop the countdown. And the countdown should be thirty seconds."* No input cancels or delays it, his or any machine's, and
the window is killed mid-reply if need be; what he sent after the goodbye lands in the Conductor log and the wake. A message
whose last sentence is "goodbye" counts. Live helpers never refuse a goodbye, the window takes no ticket and spawns nothing.
When the last one is done, publish your shard and end the turn; the kill holds for both.
**Checkpoint, so a drain never freezes him** (owner 2026-11-02: *"a context-draining agent be able to redirect
long-running subagents to just write out their results to their tickets"*; CONDUCTOR_RESTART_REDESIGN_NEVER_FREEZE_HIM).
A helper cannot outlive this window, so a drain with long helpers: (1) `seat_restart.py checkpoint --seat CONDUCTOR` lists
each live helper's agentId and item and records a 10-min deadline; (2) SendMessage each (`to` = the agentId) the order
*"Checkpoint now: write your state, evidence paths and one imperative NEXT as a note on your item, commit and publish
what is done, then stop."*; (3) `seat_restart.py checkpoint --seat CONDUCTOR --wait` (re-run until DONE or LOST): at the
deadline a helper still alive is LOST, its item gets a note, the kill stops waiting on it and the wake lists it;
(4) publish the shard and request. Work expected to run over ~20 min never goes in-process: `python3 src/RimMandrake/rimflow/detached_helper.py launch --seat CONDUCTOR --item <ID> --brief-file <F> --model sonnet|opus --max-s <s>` runs it in its own unit (pool clone, bounded time and spend), survives your restart, and ends with a note on the item and a line in this log; `detached_helper.py status` lists runs. The Agent tool stays for short work.
(`seat_restart.seats.BENCH`, kind `conductor`; the request binds his goodbye's time, a transcript byte cursor and the
transcript's path, and the Dispatcher reads everything after the cursor in full, ignoring timestamps, and again right
before the kill). The fresh window runs `seat_restart.py wake --seat CONDUCTOR --gen <restart id>` first. That lists, whole,
everything he sent the old window after the goodbye, and lists it again until a window has answered, so a fresh
window that dies on it costs nothing; a window opened without a token runs the same command with no `--gen`. If the request prints
REFUSED (shard unpublished or unmeasured with no helper alive, or his last message is no longer the goodbye: answer him), fix
what it names and request again; if it still refuses, tell him in one line that this window
stays open.
