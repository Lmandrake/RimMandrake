## spec
Ticket 1 of `design/specs/2026-11-12-ticket-preflight-before-any-token.md` (section 7). Build the spine of the ticket
preflight: `src/RimMandrake/rimflow/ticket_preflight.py` with the library call `run_text(...)` and the hand-run verb
`rimflow preflight <ID> [--json]`. Report-only: it refuses nothing and no door calls it yet.

It reads only declared facts: the `## refs` lines `file:`, `new:`, `def:`, `tier:` and the proof file's `live-mods:` /
`live-tier:` lines (prose is not read). Checks B1, B4, B5, C1, C2, C10 (spec section 2) with the indexes that exist
today: `git ls-files` and `src/RimMandrake/Utils/defindex.py` (`Index`, `ModSetDefs.provided`, `src_defs`). A door never
builds an index: no cached def index reads UNMEASURED with the build command. Index loading and checks run in one
child process with one deadline (spec 5.2); a cut-off reads UNMEASURED and `cut_off: true`. Every run appends one
timing line (spec 5.4) to `$RIMFLOW_PREFLIGHT_RUNS`, else `~/.local/state/rimmandrake/preflight/runs.jsonl`.

The exact call signature and result shape are fixed by the acceptance test's docstring; follow it.
Owner decisions that bind this build (by card 2026-11-13, spec section 9): filing will only warn, pickup will refuse
(later tickets); the preflight stays out of Relentless; an instrument that cannot look reads UNMEASURED and lets work go.

## refs
new: src/RimMandrake/rimflow/ticket_preflight.py
new: src/RimMandrake/rimflow/selftest_ticket_preflight.py
file: src/RimMandrake/Utils/defindex.py
file: src/RimMandrake/rimflow/cli.py
file: src/RimMandrake/rimflow/acceptance/preflight_spine_accept.py
file: design/specs/2026-11-12-ticket-preflight-before-any-token.md

## verify
python3 src/RimMandrake/rimflow/acceptance/preflight_spine_accept.py

## criteria
- A1: the acceptance test prints `PASS 30/30` and exits 0.
- A2: `rimflow preflight <a real open item> --json` is timed cold and warm; both numbers are in the close note.
- A3: `cmd_claim`, `cmd_file`, `relentless.py` and `detached_helper.py` are unchanged (no door touched).

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/preflight_spine_accept.py` exits 0 with `PASS 30/30`.
Watched failing at e88865a499: `PASS 0/30`, exit 1 (no module `ticket_preflight`). Passability checked against a
throwaway reference `run_text` (not committed): 27/30, the three misses being the CLI verb it did not have.
The builder does not edit the test; a clause believed wrong goes to the Conductor.
