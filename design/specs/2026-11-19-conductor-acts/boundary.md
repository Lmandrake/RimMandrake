# BOUNDARY: who may do an act that once needed the owner, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/conductor_acts.py`, and the gates that call it (`rimflow/cli.py`, `maturation.py`,
`designer_stage.py`, `concept_tree.py`, `first_touch.py`, `coverage_judge.py`, `Utils/refresh.py`). Ruling: owner
2026-11-19 ~7:40 AM PST, `design/RimMandrake/standing_rulings.md` §Only five acts stay his; item
`RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`. Written 2026-11-19 by that item's helper. Each promise has a
test of its own name in `src/RimMandrake/rimflow/selftest_conductor_acts.py`. Owed: one fresh reader that did not
write this page (the helper that wrote it could start none).

## ACCEPTS

- **a-conductor-act.** An act named by the caller (a short label, such as `first-touch certify` or `owner bridge
  hold`) and a `--why` in the caller's words, under `--per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS`.
- **the-window-mark.** The process environment: `AGENT_SEAT` (else `RIMFLOW_SEAT`) and `RM_ROLE_UNIT`. The Conductor
  window is seat BENCH with no `RM_ROLE_UNIT` (`mod_owner_hold.conductor_window`, the one definition). The seat is a
  mark, not authentication.
- **a-recorded-event.** A ledger event dict, as `concept_tree.owner_events` returns it, cited as `OWNER:<tsn>`.

## DOES NOT SURVIVE

- A process that sets `AGENT_SEAT=BENCH` and unsets `RM_ROLE_UNIT` by hand reads as the Conductor window. The mark is
  honest by convention; every launcher in this estate sets `RM_ROLE_UNIT`.
- A `--why` that hides a mindful act under words the self-declared pattern does not know is checked as a plain act at
  the cli; the act's own gate (the bridge, a bar removal) still asks for `lost:` and `undo:`.
- A kept act done with no gate at all (a purchase, a public post: text only, no tool) is refused by text alone.

## PROMISES

- **five-acts-refused.** `check` refuses each of the five kept acts (flyer flight, kept art, walk pass, spending money,
  public publishing) for every caller, the Conductor window included.
- **only-the-window.** `check` and `cli_gate` refuse every act outside the Conductor window: a launched run
  (`RM_ROLE_UNIT` set) or any other seat.
- **why-states-act-and-reason.** An empty `--why`, or one under four words, is refused.
- **mindful-names-loss-and-undo.** The four mindful acts (owner bridge hold, account order, work not ours, loosen a
  bar) are refused unless the why carries `lost:` and `undo:`, each followed by at least three words; `cli_gate` also
  asks it of a why that names one of them.
- **recorded-as-conductor-not-his-words.** `tagged` writes the why as `delegated: conductor act: …`; the event carries
  `perRuling` and `why`, never `ownerSaid` or `byCard`, and the digest classes it `conductor act`.
- **event-check.** `is_conductor_event` accepts an OWNER-shard event only when it carries this ruling, a tagged why,
  hands BENCH or CONDUCTOR and no `role_unit`, and never for a kept act.
- **bridge-cut-only-mindful.** His OWNER bridge hold, inside 45 minutes of his last interaction, is cut by a
  ruling-only OWNER take or release only when it is the Conductor window's act under this ruling with `lost:` and
  `undo:`, and never for a flyer's flight; any other `--per-ruling` refuses (before 2026-11-19 any ruling cut it). The
  cut take is marked, so it does not restart his 45 minutes.
- **digest-note-written-first.** `digest_note` writes the note through `rimflow note`, and raises when it is not
  written, so a gate that acts after it acts only on a recorded act.
