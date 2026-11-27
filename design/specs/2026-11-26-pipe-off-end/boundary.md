# Boundary: a `pipe off` carries its end condition (`src/RimMandrake/rimflow/pipe_off_end.py`)

Item RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX, part 5. His answer by card, 2026-11-26: "Program lifts it
(Recommended)": each off states an end condition that a program can check; the timed pipeline pass lifts the off when
the condition is true; his page shows each off with its age. Why: a `pipe off` on Gimme Some Slack stayed 43.5 h after
its reason ended, and five readiness offs were lifted by hand at up to 106 h (the stuck-items study, Table E).

## ACCEPTS

- **an-end-text.** `pipe off <target> --why "..." --end "<condition>"`. A condition is one of:
  `closed:<ITEM>` (the ledger item is done, dropped or superseded), `ready:<Mod>` (the newest
  `design/concepts/<Mod>/version/in_game/readiness_*.md` has a line that starts `READY`), or `cmd:<command>` (exit 0
  true, exit 1 false, any other exit or a hang: could not look).
- **the-switch-rows.** `control.switches()`: the live rows; a row's `extra` JSON holds `{"end": <parsed condition>}`.

## DOES NOT SURVIVE

- **a-condition-that-lies.** A condition that reads true too early lifts the off too early. The Conductor writes the
  condition; the program only reads it.

## PROMISES

- **an-end-is-parsed-or-refused.** `parse` returns the condition, or raises `Refused` naming the three forms. `pipe off`
  with a bad `--end` writes nothing.
- **a-true-end-lifts-the-off.** `sweep(apply=True)` lifts a control-layer off whose condition reads true, as a program
  act (`--per-ruling` the card), with the reading in its why and the undo line in its result.
- **an-unread-end-lifts-nothing.** A condition that cannot be read (no file, an exit 2, a hang, an unreadable ledger)
  lifts nothing; the row reads `could not look: <cause>`.
- **his-holds-are-never-touched.** An owner-layer row (his hold) and a control row that carries his words
  (`said`, from `--owner-said`) are never lifted, whatever their condition.
- **every-off-shows-its-reason-age-and-end.** `rows` gives each live switch its scope, reason, age, end condition
  (`none set`) and last reading; `page_lines` prints them for his page.
- **the-tick-and-the-page-read-it.** `maturation_dispatch._tick` sweeps before it reads the holds (an applied tick, or a
  caller that stands in `pipe_off_end`); `maturation_now.offs_md` prints `## Switched off (n)` with each row.
- **each-limit-names-its-danger.** `CMD_DEADLINE_S` names its danger.

## LIFE CYCLES

- **a Maturation tick (rm-maturation-dispatch.timer):** `maturation_dispatch._tick` → `pipe_off_end.sweep(apply)` →
  `control.switch(scope, False, ...)` for each true condition.
- **a Maturation Now build:** `pipe_off_end.page_lines` → the "Switched off" block.

Later lists beside this page: `polish.md` (none yet).
