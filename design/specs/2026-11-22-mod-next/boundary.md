# BOUNDARY: `mod_next.py`, the one home of what a mod does next and whether it may run now, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/mod_next.py`. Item `RIMMANDRAKE_MERGE_NEXT_STEP_AND_MAY_RUN_THREE_ANSWERS_ONE_MOD`,
candidate 1 of `design/specs/2026-11-22-pipeline-single-source-sweep/report.md`. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_mod_next.py`. The replay of the old paths on recorded inputs is
`src/RimMandrake/rimflow/selftest_mod_next_equivalence.py`.

Before this page, three answers to "what does this mod do next" disagreed: `maturation.next_step` read the stage record
alone and said "automatic" for a mod that the owner held; `maturation.py next` laid the Dispatch tick's reading over it
(`dispatch_overlay`, one caller of three); `./pipe why` read the control store and the tick but not the stage record;
the status page read the steward journal's prose `Next:` line. Each reader of the tick's reading had its own reader
(`control.tick_reading`, `maturation.dispatch_reading`).

## The contract

`next_for(root, mod, now=None, gate=True, src=None)` -> one dict:

- `may_run`: `{"result", "why"}`. `result` is one of `yes`, `held`, `off`, `paused`, `ceiling`, `waiting`, `hand`,
  `UNMEASURED`. `why` is a plain sentence that names its source (the hold, the act, the pause, the gate, the tick).
- `by`: who does the next act (the text in `NEXT (...)`). `next_act`: the act.
- `next`: always `"NEXT (%s): %s" % (by, next_act)`.
- `tick`: what the tick's last reading says of the mod (`line`, `decision`, `klass`, `at_pac`), or why it says nothing.
- With `gate=True`: `gate_next`, the stage record's own NEXT line before any hold, switch, pause or tick (the Conductor
  hand steps that `owed.py` files are read from it), and every key of `maturation.gate_step` (the stage record's exit tests: `stage`, `refusals`,
  `hand_steps`, `spend`, `launch`, `blind`, `ingame`, ...). `maturation.next_step` is `next_for` with `gate=True`.
- With `gate=False`: no exit test runs (a mod at the owner's walk costs about a minute of exit tests, measured
  2026-11-22: FlowWorks 64 s). `stage` comes from the stage record file alone.

`src` replaces a live reader by a fixture: `holds()`, `blocked(spec)`, `pause(now)`, `reading()` and `gate(root, mod)`.
A reader that cannot read raises (`mod_owner_hold.Unreadable`, `control.Unreadable`) or returns an error.

The order of the answer, first match wins: an unreadable hold, switch or pause store; an owner hold; a `pipe off`
switch (on the mod, `all`, the detached family or the mod's stage); a pipeline pause; the gate's own tag when it is not
"automatic"; the tick's reading of the mod.

## ACCEPTS

- **a-reading-in-either-shape.** A tick reading whose `mods` is a dict by mod, or an older list of rows.
- **a-row-without-klass.** A tick row written before the tick classed its rows: the class comes from its decision.
- **any-spelling-of-the-mod.** A path, `design/concepts/<Mod>`, or the bare name.

## DOES NOT SURVIVE (not handled)

- **a-hold-written-during-the-read.** The readers run one after another. A hold written between two reads shows on the
  next call.
- **a-wrong-tick-row.** The tick's row is taken as true for its age. Nothing here checks the tick's own decision.

## PROMISES (each one is owed a test of the same name)

- **held-mod-is-never-automatic.** An owner hold gives `held`, with his words and date and the lift command, whatever
  the gate or the tick says.
- **off-switch-reads-off.** A live `pipe off` switch on the mod, on `all` or on the mod's stage gives `off`, with its
  act id.
- **pause-reads-paused.** A pipeline pause on the mod or on all gives `paused`, with its why.
- **unreadable-store-is-unmeasured.** An unreadable hold file, control store or pause store gives `UNMEASURED` with the
  cause, never `yes`.
- **stale-or-missing-tick-is-unmeasured.** When the gate says "automatic", a tick reading that is missing, has no time,
  or is older than `READING_MAX_AGE_S` gives `UNMEASURED`.
- **ceiling-reads-ceiling.** A tick decision `ceiling` gives `ceiling`, with the tick's why (its release command).
- **tick-class-decides-an-automatic-claim.** When the gate says "automatic": a tick class `launch` gives `yes`; `wait`
  and `owner` give `waiting`; `paused` and `planned` give `paused`; `held` gives `held` or `off` by its decision.
- **a-lift-binds-before-the-tick.** A tick row that says `owner_hold` or `control_off` while the live stores hold
  nothing gives `waiting` (the next tick reads the lift), never `held`.
- **not-on-the-tick-list-is-hand.** A mod that the tick's reading does not list gives `hand`: nothing launches it.
- **gate-tag-decides-a-non-automatic-step.** A gate tag that is not "automatic" decides alone: `OWNER` gives `waiting`
  on him, `PAUSED` gives `paused`, a wait on a live run gives `waiting`, "read again" gives `UNMEASURED`.
- **no-gate-runs-no-exit-test.** With `gate=False`, `gate_step` is never called. The next act is the block's lift, or the
  tick's last decision of the mod, or `maturation.py next <Mod>`.
- **next-line-is-by-and-act.** `next` is always `NEXT (<by>): <next_act>`.
- **one-reader-of-the-tick.** `control` and `maturation` read the tick's reading only through `mod_next.tick_reading`.
