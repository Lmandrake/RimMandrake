# BOUNDARY: outcome checks on list items, and the tick that closes what passes, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/list_effect.py` (all of it), `src/RimMandrake/rimflow/model.py` (the `effect` field of
`file`, the `effect` verb, `Item.effect` and `Item.effect_seen`), `src/RimMandrake/rimflow/cli.py` (`file --effect`,
`effect`, the shared live gate on a List Pipeline check-close), `src/RimMandrake/Utils/systemd/rm-list-effect.{service,timer}`.
Item: `RIMMANDRAKE_BUILD_LIST_OUTCOME_CHECKS_SEVEN_DONE_NEVER_CLOSED`, step 1 of
`design/specs/2026-11-22-coordination-every-agent-must-use/plan.md`. Why: 7 of the 48 Conductor debts in the census of
2026-11-22 were done and never closed. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_list_effect.py`. This page covers only these parts of the files named.

## ACCEPTS (the only inputs this is built for)

- **an-outcome-check-text.** One string in one of three forms: `path-has:<repo path>::<text>` (the file holds the text),
  `path-lacks:<repo path>::<text>` (the file exists and does not hold the text) and `cmd:<shell command>` (run by
  `bash -c` from the clone's root; exit 0 holds, exit 1 fails, any other exit, a timeout or a command that cannot start
  is unmeasured). A repo path is relative and has no `..`; a file outside the repo is checked with `cmd:`.
- **a-ledger-item-outside-a-mod.** Any ledger item. A mod's own state is not in the ledger and is not touched.
- **the-clone-the-tick-runs-in.** The tick reads files and runs commands in the clone it runs from (the dispatch clone,
  kept level with origin/main by its own sync). A check reads that clone's bytes.

## DOES NOT SURVIVE (not promised)

- **a-check-that-reads-a-stale-clone.** A check on a clone behind origin/main reads old bytes; a `path-has` that holds on
  origin may read fails for a beat. The next beat after the sync reads it again.
- **a-cmd-check-that-changes-the-world.** A `cmd:` check is run as written on every beat. A command with side effects
  repeats them. The filer writes a read-only command.
- **a-check-that-passes-for-the-wrong-reason.** A `path-has` text that also appears for another reason closes the item.
  The attach gate refuses a check that held already when the item was filed, and nothing more.

## PROMISES (each one is owed a test of the same name)

- **parse-reads-three-forms-and-never-raises.** `parse` returns the kind and its parts for each of the three forms, and
  `{"kind": "unreadable", "why": ...}` for anything else (empty, an unknown prefix, a path check with no `::text`, an
  absolute path or `..`), with no exception.
- **holds-keeps-could-not-look-apart-from-fails.** `holds` returns `holds`, `fails` or `unmeasured`. A missing page is
  `fails` for `path-has` (the text is not there) and `unmeasured` for `path-lacks`. A command that cannot start, exits
  other than 0 or 1, or outlives its deadline is `unmeasured`. An unreadable check is `unmeasured`. Unmeasured is never
  `holds` and never `fails`.
- **decide-closes-only-on-holds-and-leaves-an-item-with-no-check-alone.** `decide` is `close` on holds, `work` on fails,
  `blind` on unmeasured, `no_effect` for an item with no check (whatever the verdict) and `closed` for an item that is
  done, dropped or superseded.
- **a-check-that-already-holds-is-refused-at-attach-unless-seen-failing-at-filing.** `attach_gate` accepts a check that
  fails now; a path check that holds now and failed at the item's filing commit; or a check that holds, with the filer's
  stated reason why it cannot be seen failing. It refuses a check that holds with no reason, and a vacuous command
  (`true`, `:`, `exit 0`, `echo …`) even with one. Each refusal names its path to pass. An unreadable or unmeasured
  check is refused with its cause.
- **file-and-effect-record-the-check-and-its-red-reading.** `rimflow file --effect` and `rimflow effect <ID> --check`
  write the check and the attach reading on the ledger; `Item.effect` and `Item.effect_seen` replay them;
  `rimflow effect <ID> --clear` removes the check. A refused attach writes nothing.
- **the-tick-closes-a-passing-item-as-the-pipelines-act-with-the-output.** A beat with `--apply` closes an open item whose
  check holds and whose live gate allows the close: a `close` with `noCode` naming the check, the head sha and the check's output, a `role_unit` (the timer's
  unit), seat BENCH, and no `ownerSaid`, `byCard` or `perRuling`. The output is also kept whole in the evidence folder.
- **both-ticks-keep-an-operational-item-open-until-its-live-promise-holds.** A check-close by either tick reads
  `origin/main` for commits naming the item in their subject. If `live_line.needs_line` wants a promise for a changed
  path, the close needs a live line that holds now and is current for the change. It can come from the item (an existing
  promise or `## live`) or a `# Live:` declaration on a changed systemd unit. The close records the line. An item that
  still owes a live line stays open with a single note naming the repair command. An unreadable git read leaves the item
  open as `blind`. The next tick can close an item after the live line starts holding. Ordinary non-operational items
  with no live line close as before.
- **the-tick-closes-nothing-on-fails-unmeasured-or-no-check.** An item whose check fails or is unmeasured is not closed,
  and an item with no check is not looked at. A note on an item closes nothing.
- **the-tick-obeys-pause-and-pipe-off.** Under the pipeline's pause (`pipeline_pause.blocks`), under `pipe off all`,
  `pipe off family:list_effect` or `pipe off item:<ID>`, and when the control store cannot be read, the beat closes
  nothing (the item reads `pipeline_paused`, `off` or `blind`).
- **the-tick-launches-nothing-and-files-nothing.** A beat writes no `file`, `spawn` or `start` and starts no unit. It
  writes `close` or the one note for an operational item that still owes a live promise. (A `close` itself files the remainder that the item's last note names as not built:
  `design/specs/2026-11-24-close-files-its-remainder/boundary.md`.)
- **a-refused-close-is-not-sent-again-unchanged.** When `rimflow close` refuses, the beat records the refusal with the
  item's event count, says it once on the Needs Conductor line, and sends no close for that item until the item or its
  check changes. A pending live line or an unreadable git read is checked again because either can recover between beats.
- **a-close-of-an-item-already-done-is-not-a-refusal.** `close_item` returns 0 when `rimflow close` refuses because that
  item is already done. An item already dropped, another item's name in the text, and every other refusal stay refusals.
  Why: on 2026-11-23 a run closed its item while the beat was at work, and the beat raised a Needs Conductor line.
- **a-dry-beat-writes-nothing.** A beat without `--apply` runs the checks and prints what it would do, and writes no
  ledger event and no state.
- **closed-reads-item-states-for-a-check.** `list_effect.py closed ID...` exits 0 when every item is done, dropped or
  superseded (with `--started`, also doing, built or validated), 1 when one is not or was never filed (each named), and 2 when it is given no item or cannot read the
  ledger: a check built on it never holds on a ledger it could not read.

Later lists beside this page: `polish.md` (none yet).
