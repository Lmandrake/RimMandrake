# The Codex lane: test-proven list tickets go to Codex while the Claude room is short

Item `RIMMANDRAKE_BUILD_CODEX_LANE_WHEN_CLAUDE_ROOM_IS_SHORT` (promised to the owner on the account-room card of
2026-11-26; launched by `RIMMANDRAKE_ROUTE_REVIEWS_PROVEN_TICKETS_TO_CODEX_ROOM_SHORT`).

Code: `src/RimMandrake/rimflow/codex_lane.py`, a step of `src/RimMandrake/rimflow/list_dispatch.py` (its tick).

Settings: the `codex_lane` block of `src/RimMandrake/rimflow/list_dispatch.json`. Tests:
`src/RimMandrake/rimflow/selftest_codex_lane.py`.

## What it does

While the Claude room is short, each tick of the ticket lane takes the test-proven tickets of
`list_home.py offer` out of the Claude lane and sends each one to Codex, in its own scratch clone. When Codex ends,
the Codex work unit runs the ticket's own check in that clone. Only a result whose check holds goes on: one Sonnet
run (a test proves the code) applies the diff in its own clone, runs the check again, judges each Problem in the diff
by the significance rule of `src/RimMandrake/rimflow/roles/code_review.md`, and lands with `./publish`. A result whose
check fails is not landed; the ticket goes back to the Claude lane. The same door sends a code review by
`roles/code_review.md` (`codex_lane.py review <path>...`): Codex returns the findings, one Sonnet run judges and fixes.

The Codex door is Dispatch's (`src/RimMandrake/Utils/agent_runner.py` for a build in a clone, which edits files;
`src/RimMandrake/Utils/gpt_consult.py` for a review, which reads inlined files). Both pass the account plan's gate
first (`src/RimMandrake/Utils/codex_advice.py`).

Offline simulation: yes. The selftest drives the real `plan`, `execute` and `work` functions with a fake notice, a
fake Codex meter, a fake Codex runner, a fake check and a fake launcher.

## ACCEPTS

- A tick of `list_dispatch.py` with its facts (`gather`): the open list items with their outcome check, its verdict,
  their mod reading, their block, wait and lease.
- The account plan's notice (`account_plan.notice_dir()/notice.json`), on the deciding machine or on a following one.
- The Codex advice of `codex_advice.advice()`.
- `codex_lane.py work <ID>`, started by the lane as a systemd unit of family `codex_lane`.
- `codex_lane.py review <path>...` from a seat or the Conductor.

## DOES NOT SURVIVE

- A Codex work unit killed between its check and its state write: the next tick reads the unit gone and the state
  `sent`, and voids the try (no try spent); the scratch clone stays for the pool reaper (a clone that holds staged files and sits idle an hour reads as stranded work to the pool alarm: land it or bundle it).
- Two ticks in the same instant: `list_dispatch.py tick` holds its own lock, so this does not happen in ordinary use.
- A Sonnet lander that dies: its own detached-helper record and the left-open route carry it.

## PROMISES

- **room short sends a proven ticket to codex**: when the notice is fresh and reads the room short (no account can
  take over, the fleet is stopped, or the live account is at its line), a ticket that the lane offers, whose check
  fails now and runs a selftest or an `_accept.py`, is sent to Codex, and the Claude lane does not launch it.
- **a member of a live bundle or run is never sent**: a ticket that is a member of a live work bundle, or that a live
  run works, is not sent to Codex; nor is any ticket while the run records could not be read. The Claude lane's own row
  for it says which (`in_bundle`, `live`, `blind`).
- **a fresh reader ticket stays with the claude lane**: a ticket that reads a fix (`fresh_reader.is_reader`) is never
  sent to Codex, whatever file names its check reads; its check reads review records, and the Claude lane supplies the
  reader's brief.
- **room ample sends none**: when the room is not short, or the notice is missing or stale (could not look), no
  ticket goes to Codex, and every ticket stays with the Claude lane.
- **a mod ticket is never sent**: a ticket that is one mod's work (`mod_work`, a `mod:` home or a mod folder in its
  title), or whose mod reading could not be made, is never sent to Codex.
- **a result that fails its check is not landed**: a Codex result whose check does not hold in its scratch clone
  launches no lander and lands nothing; the item gets a note and goes back to the Claude lane.
- **his codex share is left**: when Codex is at or under its leave line in the account plan (his share of the Codex
  week), or the advice could not look, no job goes to Codex, for a build and for a review.
- **a passing result gets one sonnet lander**: a result whose check holds launches one Sonnet lander, whose brief
  names the patch, the check and `roles/code_review.md`.
- **one try per ticket**: a ticket gets at most one Codex try; a try that a system failure ended (its unit gone
  before it wrote a result) is voided and does not count; at most `max_live` Codex units live at once, and a ticket
  past them waits for a Codex slot.
- **two failed launches return the ticket to claude**: a ticket whose Codex launch is refused twice in a row (the
  state `void_seen` included) is `stopped` at `max_voids_per_item` and goes to the Claude lane; no tick sends it again.
- **the codex child reads no real state**: the Codex child runs with the Maturation and Dispatcher state paths
  pinned to a sandbox folder of its job (lesson of 2026-11-17: a Codex builder reached the real Dispatcher state).
- **the scratch clone is freed when the patch is saved**: when a work unit ends (built, failed or void), it deletes
  its `cx-` scratch clone; the patch and the answer stay in the job folder. A path that is no `cx-` clone with a
  `.git` is never deleted.
- **review goes by code review brief**: a review job inlines `roles/code_review.md`, each named file and its boundary
  page, and launches one Sonnet judge on the answer.

## LIFE CYCLES

One record per ticket in `<list_dispatch state dir>/codex_lane/state.json`:

- (none) -> `sent`: the tick launched its Codex work unit.
- `sent` -> `built`: Codex ended and the check holds in the clone.
- `sent` -> `failed`: Codex ended with no answer, an empty diff, or a check that does not hold. Final: the ticket
  goes back to the Claude lane.
- `sent` -> `void`: the unit is gone with no result, or Codex gave no answer, or the gate refused. The next tick may
  send it again (`void_seen`); after `max_voids_per_item` system failures in a row it is `stopped`, and the Claude lane
  takes it.
- `built` -> `landing`: the Sonnet lander was launched. A refused launch leaves it `built` for the next tick whose
  account gate goes.
- `built` -> `gone`: the ticket is no longer open with a failing check (closed or fixed by another route), so no
  lander starts. Final: the lane never sends it again.
- `landing` is final for this lane: the lander's own record, its note and its close carry the ticket.

## LIMITS

- `max_live` (2): Codex work units live at once. Danger: each unit holds a scratch clone of the shared pool of 16
  (root `CLAUDE.md` §Git) and a check run on the machine; evidence: the pool and the load gate refused launches on
  2026-11-23 and 2026-11-24 (`list_dispatch.json` `_machine_load_per_core_doc`). Ends no work: the rest wait for a
  later tick.
- One Codex try per ticket, by the life cycle (`failed` is final). Danger: a chain that feeds itself, the retired loop
  of 2026-11-05 (`list_dispatch.json` `_max_runs_per_item_doc`). Ends no work: the Claude lane takes the ticket.
- `max_voids_per_item` (2): system failures in a row before the lane stops trying a ticket (`stopped`). Danger: a launch
  sent again every tick into the same failure (root `CLAUDE.md` §A fault of form: a program never sends the same
  refused input again unchanged; as `max_never_started`). Ends no work: the Claude lane takes the ticket. A refusal at
  his leave line is no strike.
- The Codex call deadline is the door's own hang guard (`agent_runner.run`, 7200 s); a review uses `gpt_consult.py`'s.
