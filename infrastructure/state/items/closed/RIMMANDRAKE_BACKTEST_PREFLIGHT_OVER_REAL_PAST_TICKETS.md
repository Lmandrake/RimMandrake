## spec
Ticket 3 of `design/specs/2026-11-12-ticket-preflight-before-any-token.md` (sections 7 and 8). After tickets 1 and 2:

1. **Shadow at the doors outside Relentless.** `rimflow file`, `claim`, `start` and `detached_helper.launch` run the
   preflight, print its lines and record, refusing nothing. Each run writes its timing line with `door`; the claim and
   start events gain `preflight_run` and `preflight_ms`. Thin wrappers record the answer and time of each existing gate
   at those doors (at least A1 at filing, I2 and E1 at claim). A runner that throws prints "preflight did not run" and
   the door carries on; an unwritable timing file is reported and stops nothing. `RIMFLOW_PREFLIGHT_BREAK=1` is the
   test hook that makes the runner raise.
2. **Nothing in Relentless.** Owner, by card 2026-11-13: keep the preflight out of Relentless entirely until the
   2026-11-06 freeze ends. No `relentless*.py` file imports or calls it.
3. **The backtest of section 8** over its four corpora, written to
   `infrastructure/state/evidence/preflight_backtest/<date>.json` (shape in the acceptance test's docstring), with 10
   planted known-bad tickets that must each be caught, the per-check table, the joint false-block rate and timing per
   door. Its answer to "what would this catch that today's gates do not" is one paragraph for the owner.

## refs
item: RIMMANDRAKE_EXTEND_PREFLIGHT_CORE_KINDS_IDS_SHAS_FULL_REASON
file: src/RimMandrake/rimflow/cli.py
file: src/RimMandrake/rimflow/detached_helper.py
file: src/RimMandrake/rimflow/acceptance/preflight_shadow_accept.py
new: infrastructure/state/evidence/preflight_backtest

## verify
python3 src/RimMandrake/rimflow/acceptance/preflight_shadow_accept.py

## criteria
- A1: the acceptance test prints `PASS 21/21` and exits 0.
- A2: each would-be refusal sampled for a check is read by a person as of pickup (section 8 "False refusal"); the
  audited n and false k per check are in the table. This part is judged by the Conductor at close, not by the test.
- A3: the list of checks proposed for enforcement in ticket 4, each with its audited row.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/preflight_shadow_accept.py` exits 0 with `PASS 21/21`.
Watched failing at e88865a499: `PASS 4/21`, exit 1 (the four that pass on base are the never-refuse and
no-Relentless clauses, which a correct build must keep). It runs file/claim/start in a sandbox ledger
(`RIMFLOW_LEDGER`, `RIMFLOW_ITEMS`), never the real one. The human audit of A2 is outside the test by nature.
