# BOUNDARY: the ticket preflight stops a launched run at pickup on a wrong declared fact, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/ticket_preflight.py` (`Shadow.enforce`, `Shadow.stops`, `timing`, `render_timing`), and
the doors that call it: `rimflow/cli.py` (`_pickup_gates` at `claim` and `start`; `preflight --timing`). Spec:
`design/specs/2026-11-12-ticket-preflight-before-any-token.md` section 7 ticket 4 and section 9 (the owner's card
answers of 2026-11-13: Q1 filing warns, pickup stops; Q3 a build, fix or live ticket with no declared refs is stopped
at pickup; Q4 a Full Mod ask with no reason is stopped at pickup; Q5 only the Conductor may bypass; Q6 a check that
cannot look lets the work through). Rules: root `CLAUDE.md` §A fault of form is repaired where it is found (the stop
goes back to the same agent with its repair) and its case "His word and the Conductor's act are not refused"
(`principal.form`). Item `RIMMANDRAKE_PREFLIGHT_TICKETS_BEFORE_ANY_TOKEN_IS_SPENT`. Each promise has a test of its own
name (`t_` + the name, dashes as underscores) in `src/RimMandrake/rimflow/selftest_preflight_enforce.py`.

## ACCEPTS

- **a-ticket.** The item's live prose `infrastructure/state/items/<ID>.md` (its `## refs` section only) and its proof
  file `infrastructure/state/live_proofs/<ID>.txt` (`live-tier:` and `live-mods:` lines), and the item's kind and needs
  from the ledger.
- **the-caller-mark.** The seat and `RM_ROLE_UNIT`, read through `principal.who`: the Conductor window is seat BENCH
  with no `RM_ROLE_UNIT`, the owner is seat OWNER with no `RM_ROLE_UNIT`; any launched run is neither.
- **the-timing-file.** `RIMFLOW_PREFLIGHT_RUNS`, else beside a redirected ledger, else
  `~/.local/state/rimmandrake/preflight/runs.jsonl`: one JSON line per door attempt.

## DOES NOT SURVIVE

- A lane that gives a helper a ticket and lets it work without `claim` or `start` meets no stop. Every helper brief
  today opens with one of the two; nothing enforces that.
- The helper-launch door does not stop: no agent is present there to repair the ticket, so the stop waits for the
  run's own `claim` or `start`, after its brief is read. That costs the tokens of reading the brief.
- A stale def index can make B4 or C2 FAIL on a def that exists. The agent then repairs the line (or the index), as
  the FIX says; the stop cannot tell a stale index from a wrong def.
- The launch door replays the ledger to learn kind and needs (about 2 to 4 s measured, 2026-11-26, 58 runs). It is
  recorded on each line and shown as `added p95` by `--timing`; it is not cut.

## PROMISES

- **claim-and-start-stop-a-launched-run-on-a-failed-declared-fact.** At `claim` and `start`, a FAIL of a new check on a
  line the ticket declared (a missing `file:` path B1, a def nowhere B4 or off the list C2, an unknown tier C1, a bad
  kind B6, item id B10 or sha B11, a malformed refs line P0/E11, a Full ask with no reason C4, a build, fix or live
  ticket with no confirmed refs line E12) exits 2 for a launched run before the door writes any event. A task ticket
  owes no refs.
- **the-refusal-carries-each-repair-and-the-repaired-ticket-passes.** The stop names each failed check, its evidence,
  its FIX and `rimflow preflight <ID>`; once the ticket carries the repair, the same caller's `claim` or `start` goes
  through.
- **the-conductor-and-the-owner-pass-with-a-note.** For the Conductor window or the owner the door goes on with one
  NOTE line naming the checks, and the timing line records `override` and a verdict `passed by <who>: <ids>`.
- **filing-and-the-launch-door-never-stop.** `file` and `detached_helper.launch` run the same checks and print and
  record them; they stop nothing.
- **a-check-that-cannot-look-stops-nothing.** A preflight that did not run, an UNMEASURED or cut-off check, and a tool's
  own `(auto)` guess stop nothing. A prose file that exists but cannot be read is "did not run", never "no refs" (only a
  missing file means nothing is declared). An existing gate's FAIL keeps its own authority: the preflight adds no stop
  to it.
- **every-attempt-is-a-timing-line-and-timing-reads-them.** Every door attempt, a refused one included, writes one
  timing line with `total_ms` and its verdict. `rimflow preflight --timing` prints per door: runs, p50, p95, max, the
  preflight's own added p95 against the spec 5.2 target, refusals, principal passes, cut-offs, runs that did not run,
  and the five slowest checks. A missing timing file is said, never raised.
- **the-real-doors-in-a-sandbox-ledger.** `src/RimMandrake/rimflow/acceptance/preflight_enforce_accept.py` drives the
  real `rimflow file / claim / start / preflight --timing` in a sandbox ledger and passes every clause.
