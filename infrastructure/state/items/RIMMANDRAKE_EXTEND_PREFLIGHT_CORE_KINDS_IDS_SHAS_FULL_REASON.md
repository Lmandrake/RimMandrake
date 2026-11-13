## spec
Ticket 2 of `design/specs/2026-11-12-ticket-preflight-before-any-token.md` (section 7). After ticket 1
(`RIMMANDRAKE_BUILD_PREFLIGHT_SPINE_TIMED_FROM_BIRTH`), extend `ticket_preflight.run_text` and `rimflow preflight` with
the rest of the CORE shelf (spec 2.3), still report-only:

- the reference record of spec 4.2 with its strict parse, E11 (unknown key names the nearest valid key; two tiers, and a
  def both `def:` and `new-def:`, name both lines); a line ending `(auto)` carries origin `auto`, others `declared`;
- B6 def kinds (`race:`, `pawnkind:`, `biome:`), B10 item ids (a superseded id names its successor), B11 shas (resolves;
  an ancestor of HEAD, else "not landed");
- C4 the Full Mod reason of spec 2.1: asked by `tier: full` or a GREEN-FULL criterion; one of interaction, load-order,
  performance, owner-save, explicit (which must name a real id); no reason prints a candidate `live-mods:` list;
- E12 the declared block: a build, fix or live ticket (kind build/fix/bug/defect/code/feature; needs
  deploy/game-up/bridge/harvest; or a live-proof file) has a confirmed `## refs` line or a `none: <why>` line.
  Owner, by card 2026-11-13: "declared block REQUIRED for build, fix and live tickets; a ticket with none is stopped at
  pickup" (the stop itself is ticket 4; here it is an observation).
- `rimflow preflight --sweep [--json]` over every open ticket, inside the 30 s hard stop, one timing line each, with
  `task_with_verify`: open `task` tickets with a `## verify` command (the gap E12 cannot see).

The test's docstring fixes the new arguments (`kind`, `needs`, `items`, `repo`).

## refs
item: RIMMANDRAKE_BUILD_PREFLIGHT_SPINE_TIMED_FROM_BIRTH
file: src/RimMandrake/rimflow/acceptance/preflight_core_accept.py
file: src/RimMandrake/rimflow/relentless_live_round.py
file: design/specs/2026-11-12-ticket-preflight-before-any-token.md

## verify
python3 src/RimMandrake/rimflow/acceptance/preflight_core_accept.py

## criteria
- A1: the acceptance test prints `PASS 37/37` and exits 0 (it re-runs ticket 1's test as its last clause).
- A2: the sweep's worst-first list and its E12 and C4 counts are in the close note, for the Conductor to read.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/preflight_core_accept.py` exits 0 with `PASS 37/37`.
Watched failing at e88865a499: `PASS 0/37`, exit 1 (no module `ticket_preflight`). Not yet run against any
implementation, so a clause no correct build can meet is possible; report it to the Conductor rather than edit it.
