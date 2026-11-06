# LIVEVERDICT_REBUILD_ALLOWLIST_MEETS_OPENLANE

Split from `RELENTLESS_REDESIGN_VERDICT_FAIL_CLOSED` (2026-11-06), which built design Rule 6 only (relentless.py:
check binding, deadlines on arrival, close-retry cap). This item carries Rules 1-5 of
`design/RimMandrake/relentless_verdict_identity_design_2026-11-02.md` for the live tier:

1. Identity binding taken after `bridge take` and before release (build blobs vs game folder via the compose manifest,
   process pid+start, `jawa/running_mods` hash); any move = UNMEASURED.
2. Fail closed: tool verdict = exit code AND last `VERDICT` line; `run()` wrapped so any escape is one UNMEASURED row;
   a malformed `runs.jsonl` row refuses the round.
3. Proof-command allowlist (shlex argv, `shell=False`, `-I`, per-tool `proof_parser` with `allow_abbrev=False`).
4. Proof children reaped (`start_new_session`, `killpg`, one 5 s monotonic budget); a survivor = UNMEASURED.
5. Argument-keyed selftest fakes and mutants M1-M13.

## The conflict to settle first

The design (2026-11-02) allowlists two tools (`live_def_check.py`, `live_log_check.py`). Since then the live lane
(`src/RimMandrake/rimflow/relentless_live_round.py`, `infrastructure/state/live_proofs/<ID>.txt`) runs worker-written
`live-proof <CID>: <command>` lines of any read-only shape, and the Relentless worker brief tells workers to write them
(e.g. `relentless_live_round.py deployed --item <ID>`). A two-tool allowlist would refuse most of today's proofs. Decide
the allowlist's shape (grow `PROOF_TOOLS`, or an argv grammar over a vetted tool set) against the real proof lines in
`infrastructure/state/live_proofs/` before writing code. The design's line "Relentless must not build or edit any file
named here (relentless_rules.json `own_paths`)" was removed 2026-11-06: no `own_paths` key exists.

Also owed from Rule 6.2, not built: `ledger_close` treats the item as closed only when the ledger's close names the
candidate sha (r6a#3); builder admission re-run in full after the clone is prepared (r6a#7).
