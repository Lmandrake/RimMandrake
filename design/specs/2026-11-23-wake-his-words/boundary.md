# BOUNDARY: wake_words.py, the Conductor wake's reading of his words, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/wake_words.py`, called by `cmd_wake`, `cmd_last_reply` and `cmd_words` in
`src/RimMandrake/rimflow/seat_restart.py` (`_wake_words`, `_print_words`, `_stamp_words`) for a seat of kind
`conductor`. Item: `RIMMANDRAKE_SHOW_HIS_WORDS_AT_WAKE_FRESH_WINDOW_DENIED_A_MOD_PASS`.
Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_wake_words.py`. The item's acceptance test,
`src/RimMandrake/rimflow/acceptance/wake_his_words_accept.py`, runs the whole `cmd_wake` on a throwaway clone, ledger
and transcript, and carries the planted faults (`--mutants`).

The failure behind it (2026-11-23): the Conductor window restarted at its 400k limit with no handoff. His words "GSS walk
full pass. Looks great!" were on the OWNER shard. The wake printed none of his words, and the fresh window read a stale
note and told him that the mod was not passed. A window at its context limit is the least reliable author. So no model
writes any line here. Every line comes from records that already exist.

## ACCEPTS (the only inputs the reading is built for)

- **the-seat-clone.** The seat's clone (`cfg.clone`, else this repo) holds `infrastructure/state/ledger/events/*.jsonl`
  (the OWNER shard included) and `design/concepts/<Mod>/version/stage_record.json`.
- **owner-shard-events.** An event carries his words in `ownerSaid` (his typed words) or `byCard` (a card he answered).
  `ts` is ISO UTC. `id` is the item. A `title` on any shard's event names the item's title.
- **claude-code-transcripts.** The window transcripts of the seat under `~/.claude/projects/<clone>/` as Claude Code
  writes them. A window of the seat is one that `is_window_of` reads as `customTitle` = the seat's `session_name`, with
  entrypoint `cli`. His typed messages are the records that `seat_restart._is_human_input` counts (queued prompts
  included).
- **the-wake-stamp.** `restart/<SEAT>.wake_words.json` in the dispatcher state, written whole by `_write_json`.

## The rules the code uses

- **The previous wake.** The time in the stamp that the last wake wrote. When the window that wrote the stamp ended no
  turn after it, that window told him nothing, so its own start carries back. When this window runs the wake again,
  the wake keeps the start of its first run. With no stamp (the first wake after this change), the start is the first
  record of the old window's transcript. When both read, the earlier one is used.
- **A home for a typed message** (the probe's rule, `design/specs/2026-11-22-one-view-of-open-work/probe_his_words.py`,
  with a typo allowance for short messages). Both sides are normalised: system reminders and image tags removed, lower
  case, words of `a-z 0-9 '`. A message has a home when an event with `ownerSaid`, from 1 h before the message onward,
  holds half of the message's 5-word runs, or holds a quote of 5 or more words of which 80% of runs lie inside the
  message. A message under five words has a home when a run of as many words in an `ownerSaid` equals it or is within a
  typo of it (difflib ratio 0.85 or more). A message with no home is printed. When another field (a note, a reason, a
  title) holds a quarter of its runs or 8 words in a row, the line says where it is echoed, not as his words.
- **A mod named by an event.** The event's item id, its text fields and the item's title, normalised, contain the
  mod's folder name, its words (`gimme some slack`), or, for a name of three or more capitals, its initials (`gss`).
- **The mods listed.** Each mod with a stage record that `mod_owner_hold.load()` does not hold.
- **Layout.** More than 30 events in "HIS WORDS" print grouped by item, in the order of each item's first event. Every
  event is still printed. No text is cut and no count is capped.

## DOES NOT SURVIVE (not handled)

- **a-message-typed-elsewhere.** A message that he typed on another machine, in another project's window, or by Remote
  Control into a session that no transcript on this machine holds, is not read.
- **a-paraphrased-record.** A message recorded only in other words (a note that restates it) reads as no home, with the
  echo named when the words overlap enough. The probe of 2026-11-22 found 5 of 51 such.
- **a-mod-named-only-by-a-nickname.** An event that names a mod by a word that is not its folder name, its words or its
  initials (for example "the slack mod") is not tied to that mod in "EACH MOD NOW". "HIS WORDS" still prints it.
- **a-stamp-written-by-a-window-that-was-not-the-conductor.** A wake run by another named session in the dispatcher
  state moves the stamp. The test and the real-wake check of this item ran with a copied state folder for this reason.
- **an-unreadable-stamp.** A wake stamp that is present but does not parse reads as no stamp. The start is then the
  old window's first record, which shows more of his words, not fewer.
- **a-clock-skew-over-an-hour.** A ledger event stamped more than 1 h before the message that it records does not
  count as its home.

## PROMISES (each one is owed a test of the same name)

- **pass-is-the-first-line.** A stage-record move to `passed` since the previous wake is the first line of the whole
  wake output, with the mod, its version, the time and the move's reason. With no such move, the first line says
  `looked: none`. With no previous-wake time, it says UNMEASURED.
- **his-walk-words-on-top.** His words since the previous wake on an item that names a mod at Stage 8 (his walk) are
  printed at the top, word for word, before the seat log.
- **every-word-since-the-wake.** "HIS WORDS SINCE THE PREVIOUS WAKE" prints every OWNER-shard event with `ownerSaid` or
  `byCard` since the previous wake, whole, oldest first, each with its item id and local Pacific time, and no event
  from before. Above 30 events it groups by item and still prints every one. A line of the OWNER shard that does not
  parse is named as UNMEASURED.
- **each-unheld-mod-with-his-newest-words.** "EACH MOD NOW" prints one line per mod that is not held: its version, its
  stage from the stage record, and his newest words on an item that names it, marked NEW when they are since the
  previous wake. A held mod is not listed.
- **homeless-message-printed-whole.** "HIS TYPED MESSAGES WITH NO HOME" prints, whole, each typed message since the
  previous wake that has no owner-said home. A message with a home, a typo fix included, is not printed. A message from
  before the previous wake is not read.
- **four-answers-apart.** Each section keeps its answers apart. An unreadable transcript is UNMEASURED with its path
  and cause, never `looked: none`. A missing OWNER shard is UNMEASURED by name. Nothing found is `looked: none`. A
  section whose code raises prints FAILED with the cause, and the other sections still print.
- **since-is-the-previous-wake.** The next wake reads from the time this wake stamped. A second run in the same window
  keeps the first run's start. A stamp whose window ended no turn carries its start back. With no stamp, the start is
  the old window's first record. A wake with no named session writes no stamp.
- **sections-once-per-window.** The three sections print at the restart wake (`seat_restart.py wake`) and at the
  fleet-launch wake (`handoff.py --wake`, which runs `seat_restart.py last-reply`), so a window that no restart made (a
  boot, a crash, an account switch) gets them too. A second run in the same window prints one line that names
  `seat_restart.py words --seat <SEAT>`, which prints them again and writes no stamp.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
