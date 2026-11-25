# BOUNDARY: the weekly follow-through audit, Design Version 0.1.0

Code: `src/RimMandrake/Utils/follow_through.py` (all of it), `src/RimMandrake/Utils/follow_through_reader.md` (the
reader's brief), `src/RimMandrake/Utils/systemd/rm-follow-through.{service,timer}`.
Item: `RIMMANDRAKE_BUILD_FOLLOW_THROUGH_AUDIT_LOWER_RATE_IS_HEADLINE`, step 5 of
`design/specs/2026-11-22-coordination-every-agent-must-use/plan.md` (§The measurement, read Sunday 2026-11-29). Why: the
owner wants traceable, reliable production, not helpers that get forgotten (2026-11-23). The audit measures how much of
what was asked in a week reached its result without his hand. Each promise below has a test of its name in
`src/RimMandrake/Utils/selftest_follow_through.py`. The contract of `sample`, `rates` and `hands_off` is also tested by
`src/RimMandrake/rimflow/acceptance/step5_follow_through_accept.py`.

## How a week is audited

1. `rm-follow-through.timer` fires daily at 18:00 local (Pacific). `follow_through.py tick --apply` works the week
   that ends on the latest Sunday, from the week ending 2026-11-29 (`FIRST_WEEK`, the plan's first reading) on. It
   files two items, once each: the reader item for that week, with an outcome check (`follow_through.py judged
   --week-ending <date>`), and the planted need of the NEXT week, so that each audit reads a need that had its whole
   week. The first planted need (week ending 2026-11-29) was filed by hand with `follow_through.py plant`. It then launches one fresh reader (opus) on the reader item
   itself, through `detached_helper.py launch`, once. The audit does not wait for the Workshop Pipeline to launch the
   reader, because the audit watches that pipeline from outside (plan §Where I push back: a pipeline that reports false
   progress is the worse failure). A daily beat retries a launch that a gate held on Sunday. A reader run that ended
   with the item open is left to the Workshop Pipeline, which works the item by its check.
2. The reader (a fresh run that did none of the work) runs `follow_through.py sample --week-ending <date> --write`. The
   program draws the sample and writes the audit page and its record (`audit/<date>.md` and `audit/<date>.json` beside
   this page). The reader judges each drawn need against the real file or run and writes the verdicts into the record.
   Then it runs `follow_through.py rates --week-ending <date> --write`, which puts the two rates and the headline on the
   page. The item's check then holds.

## ACCEPTS (the only inputs this is built for)

- **a-week-ending-date.** A date `YYYY-MM-DD`. The audit's week is the seven days before it, from 00:00 Pacific seven
  days earlier to 00:00 Pacific on the date. So every need in the week has had at least the hours up to the reading.
- **the-talk-stream.** His typed messages in the Conductor window's transcripts, read by `wake_words.window_transcripts`
  and `wake_words.typed_since` (the wake's own reader; there is no second reader). One need per message.
- **the-pipe-stream.** The ledger notes of the week whose text starts `LEFT OPEN:`: a run end that named a next act
  (the detached-run contract, `detached_helper.LEFT_OPEN`). One need per item: its first such note in the week.
- **the-ledger.** Every shard, read once by `wake_words.Ledger`, and the replayed world (`model.replay`).
- **a-verdict.** `outcome` (the need reached its result), `disposed` (dropped or answered no, for a stated reason),
  `moved` (only a new note, a follow-on item or a new date), `nothing` (no act at all) or `not_a_need` (the message or
  note asked for nothing). Each verdict carries one line of evidence: a path, a sha, a run or an event.

## DOES NOT SURVIVE (not promised)

- **a-need-the-reader-misjudges.** A verdict is a judgement. Nothing here tests it. The record keeps the evidence line
  beside each verdict so that a second reader can check it.
- **a-message-typed-in-another-window.** Only the Conductor window's transcripts are read. Words typed in a helper's
  window, on the phone outside the window, or said aloud are not in the talk stream.
- **a-run-end-with-no-left-open-note.** A run that named its next act only in its result text, or in a note with
  another head, is not in the pipe stream.
- **an-actor-recorded-wrongly.** The Conductor window's acts are read from `role_unit`, `seat` and `ranBy`. A helper
  that wrote an event with no `role_unit` reads as the window. An event by `ranBy AGENT` (a subagent inside a window)
  reads as the window.

## PROMISES (each one is owed a test of the same name)

- **sample-draws-n-the-same-for-a-seed-and-keeps-none.** `sample(streams, n, seed)` returns `n` needs from each stream
  (the whole stream when it has fewer), none twice, the same draw for the same seed and stream, another draw for
  another seed. A stream that could not be read (`None`) stays `None`, never `[]`.
- **rates-count-outcome-and-disposed-and-the-headline-is-the-lower.** `rates` counts `outcome` and `disposed` as followed
  through, and `moved` and `nothing` as not. `not_a_need` leaves the count. The headline is the lower of the stream
  rates.
- **rates-keep-no-verdicts-apart-from-zero.** A stream that is `None`, empty, or only `not_a_need` has rate `None`
  and is named in `unmeasured`. The headline is `None` while any stream is unmeasured. A rate of `0.0` means needs were
  judged and none followed through.
- **rates-refuse-an-unknown-verdict.** A verdict outside the five raises `ValueError` that names it and the five. It is
  never counted as one of them.
- **hands-off-reads-closed-items-only-and-none-is-never-a-guess.** `hands_off(items)` counts only closed items. An item
  whose acts could not be read makes the share `None`. No closed item gives share `None` and `closed` 0.
- **window-act-is-an-event-by-the-conductors-hands.** `window_act(ev)` is `True` for an event with no `role_unit` whose
  `ranBy` is BENCH, CONDUCTOR or AGENT, or (with no `ranBy`) whose seat is BENCH or CONDUCTOR. It is `False` for an
  event with a `role_unit`, by another seat, or on the OWNER shard with no `ranBy` (his own hands). It is `None` for an
  event with no seat.
- **the-week-is-seven-days-before-the-date-pacific.** `week(date)` returns the epochs of 00:00 Pacific seven days
  before the date and 00:00 Pacific on the date. A date that is not `YYYY-MM-DD` raises `ValueError`.
- **pipe-stream-is-the-first-left-open-per-item-in-the-week.** `pipe_needs(events, lo, hi)` returns one need per item:
  the first note in `[lo, hi)` whose text starts `LEFT OPEN:` (after spaces and `*`/`_` emphasis, any case). A note
  that only mentions the words inside a sentence is not a need.
- **talk-stream-is-none-when-it-cannot-be-read-and-drops-machine-text.** `talk_needs` returns `(None, cause, notes)` when the
  transcripts folder cannot be listed, when no Conductor window transcript was written in the week, when none could be
  read, or when the machine-text rule cannot be read. It returns `([], None, notes)` when transcripts were read and he
  typed nothing. Machine text (the probe's `MACHINE` rule in `probe_his_words.py`: a wake prompt, a `/command`) is not
  a need, and its count is a note.
- **beside-numbers-read-the-ledger-and-say-unmeasured-when-blind.** `beside(world, events, now, …)` returns the Conductor
  debts ripe over a day and still open, the waits past their date with no event since, and the typed messages of the
  last three days with no home (`wake_words.home_of`, the wake's rule). Each is a count with its rows, or `UNMEASURED`
  with its cause. None is ever 0 for a source it could not read. An event with no readable time is placed in no window: on a waited item it counts as a look
  (`untimed` counts those items), so a blind read never adds a drop.
- **sample-write-never-overwrites-verdicts.** `sample --write` refuses (exit 3) when the week's record already holds a
  verdict. It names the record and the command that passes.
- **judged-holds-only-when-every-need-has-a-verdict-evidence-and-the-page-has-rates.** `judged` exits 0 only when the
  record exists, every drawn need has a verdict of the five and an evidence line, and the page states the rates that
  `rates` computes from the record now. It exits 1 when one of these fails (named; a record that does not exist yet
  is a fail), and 2 when the record exists and cannot be read.
- **the-page-says-unmeasured-for-each-stream-it-could-not-read.** The page names each stream that could not be read as
  `UNMEASURED` with its cause, and each rate not yet judged as `UNMEASURED (not judged yet)`. It never prints a rate of
  0 for a stream with no verdicts.
- **tick-files-once-launches-the-reader-once-and-is-dry-by-default.** `tick` without `--apply` writes nothing to the
  ledger and launches nothing: it says what it would do, and writes its reading. With `--apply` it files the reader
  item and the next week's planted need when they are absent, and launches the reader only when the reader item is open, no run
  was ever launched on it, and no gate holds (the pipeline's pause, `./pipe off family:follow_through` or
  `item:<ID>`, the Dispatcher's account pick; a gate that cannot be read holds). A second beat files nothing again and
  launches nothing again. Before `FIRST_WEEK` it does nothing and says so.
- **the-planted-need-is-read-from-outside.** `planted_reading(world, events, item)` says whether the planted need is
  closed, when and by whom (the closing event's `role_unit` or seat), how many window acts it took, and how many runs
  were launched on it. A planted item that is not on the ledger reads `UNMEASURED: not filed`.

## LIMITS

- **20 needs per stream** (`N`). Danger: a sample too small to show a difference, or too large for one reader to judge
  well. Evidence: the plan's number (plan §The measurement). Changing it changes the draw, not the arithmetic.
- **A debt is ripe over a day** (`RIPE_S`) and **typed messages with no home are read over 3 days** (`HOMELESS_S`).
  Danger: a debt or a message that is only hours old reads as a drop. Evidence: the census of 2026-11-22
  (`design/specs/2026-11-22-one-view-of-open-work/census.md`), whose numbers these repeat.
- **The reader's spend cap is 12 USD** (`READER_CAP_USD`), stopped from outside by `spend_watchdog`. Danger: a runaway
  reader. Evidence: the same cap as `list_dispatch.json` `opus_cap_usd`. The brief does not state it.
- **Hang guards** (`LAUNCH_TIMEOUT_S`, `CLI_TIMEOUT_S`): one `detached_helper.py launch` and one `rimflow` write. They are
  far above a real run and are not speed bars.
