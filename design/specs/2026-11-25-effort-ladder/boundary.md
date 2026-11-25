# BOUNDARY: every launch states its effort, and a stuck worker tries harder before anyone files, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/effort.py` (the one table and the ladder's steps); the effort reader in
`src/RimMandrake/Utils/launch_permissions.py` (`effort_scan`); `--effort` on `detached_helper.py launch`; the ladder in
`src/RimMandrake/rimflow/left_open_continue.py` (`ladder_step`, `stuck_why`, `refused_why`).
Item: `RIMMANDRAKE_PASS_EFFORT_ON_EVERY_LAUNCH_STEVEDESKTOP_RAN_MEDIUM`.
Each promise has a check of the same name in `src/RimMandrake/rimflow/selftest_effort_ladder.py`.

The owner, by card 2026-11-25: "No medium anywhere"; a stuck worker: "Effort up, then model up"; a Fable run on stuck
work: "High".

What happened (measured by the Conductor 2026-11-25). No launcher passed `--effort`, so each run took the effort of its
machine's settings file. In three days SteveDesktop ran all 32 Opus runs at medium, and Archmagi ran 134 Sonnet and 44
Fable runs at medium. A launch with `--setting-sources ""` reads no settings file, so a settings line alone does not
cover it.

## ACCEPTS (the only inputs this is built for)

- **a-tracked-launch.** Each launch that the launch reader of `launch_permissions.py` finds: an argv, a command line or a
  command in a brief, in a file that git tracks.
- **a-finished-detached-run.** A record of `detached_helper.py` whose run ended success with its item open and a
  `LEFT OPEN:` note written since the run began.

## DOES NOT SURVIVE (not promised)

- **the-remote-control-server.** `claude remote-control` takes no `--effort`. Its sessions take the effort of the
  machine's settings file (`effortLevel`, high on Archmagi and SteveDesktop since 2026-11-25).
- **the-shipped-game.** The game's own call on a player's machine (`OracleKernel.cs`) is the player's CLI. We do not set
  its effort.
- **a-note-in-other-words.** Whether a `LEFT OPEN:` note names a cause outside the work is read from its words
  (`OUTSIDE_RX`). A cause in words that the pattern does not know reads as stuck, and the run climbs one step.
- **a-blind-role-or-no-tier.** A blind role (a judge, reader, examiner, challenger) and a run whose model names no tier
  do not climb. A blind verdict is calibrated for its model and effort. No step is guessed for an unknown model.
- **a-work-bundle-or-a-list-run.** A run with `RM_WORK_BUNDLE`, or one whose next act belongs to another program
  (`next_act_owner`), follows that program's own rule. The ladder does not climb it.

## PROMISES (each one is owed a check)

- **one-table-floor-high.** `effort.py` holds the one table. Each model reads high. A level under high (`low`, `medium`)
  is refused by name, in the table and at a call.
- **a-launch-without-effort-is-red.** A launch that is not sure to carry `--effort` reads NO EFFORT, exit 1. The planted
  launches of 2026-11-25 (no `--effort`) read NO EFFORT; the same launches with it read EFFORT.
- **every-launch-in-this-tree-states-effort.** The selftest reads this tree at `./publish`. It is red on a NO EFFORT or a
  COULD NOT LOOK. With `--effort` taken out of a file whose launches state it, that file reads red.
- **the-detached-record-keeps-effort.** `detached_helper.py launch --effort L` puts `--effort L` on the run's command
  and `effort: L` on its record. With no `--effort`, the level comes from the table. A level under the floor is refused.
- **the-one-launcher-adds-a-forgotten-effort.** `claude_bounded.sh` adds `--effort` from the table when its caller gave
  none. It adds nothing to `auth`, `update`, `/usage` or `remote-control`.
- **a-refused-set-down-is-stuck.** A run that ends with a filing refusal that it did not resolve
  (`filing_gate.read_refusals` on its unit) is stuck, whatever its note says. A refusal that the run resolved (filed,
  did, dropped) makes nothing stuck. A refusal record that cannot be read decides nothing here; the run-end text names
  it.
- **a-stuck-worker-climbs-effort-first.** A run at high that ended stuck is continued in the same session at xhigh,
  when the resume rule allows a resume. A note that names a cause outside the work, a lane hand-on and a spend stop are
  not stuck: those continue as before, at the same effort.
- **then-a-higher-model-fresh-from-the-note.** A run at xhigh that ended stuck is continued FRESH on the next model at
  high: Sonnet to Opus, Opus to Fable 5.2 by its full name. The brief carries the run's progress record. The resume
  header of the xhigh step asks the worker to write that record.
- **then-the-conductor-raise-first.** A Fable run that ended stuck launches nothing. One line that starts `RAISE FIRST`
  goes to the Conductor log, with the note. Nothing files a ticket before this step.
- **a-ladder-step-spends-no-counted-run.** A ladder step is a continuation (`continued_from`, read by
  `maturation_hands.continued_from` as a program's launch). It writes no failed verify on the item, and it does not count
  against `MAX_PER_DAY`.

## LIMITS

- The ladder's end is its own guard. Danger: a run that climbs without end on a fault that needs the owner. The ladder
  has at most four steps (Sonnet high, Sonnet xhigh, Opus high, Opus xhigh, then Fable high), and the step after Fable
  is the Conductor, never a launch.
- The ladder stops at xhigh, never max. The fleet rule says that max effort rarely pays. This is a rule of the owner's
  fleet ladder, not a speed bar.
