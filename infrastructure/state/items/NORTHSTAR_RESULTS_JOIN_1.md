# NORTHSTAR_RESULTS_JOIN_1 — the lead metric cannot see the two finished checkouts

**MEASURED 2026-10-06 00:00.** `required_checks_report.py` printed `TOTAL proven 0 of 1543` and listed neither
FlowWorks nor GimmeSomeSlack. Cause (read from the source, not inferred): the report reads only
`Transient/modcheck/live_queue/*/<Mod>_summary.json`; both mods' real checkouts (`GimmeSomeSlack/proof_all.py`,
`FlowWorks/northstar/validation_v2.py`) write their own JSON beside the mod, and nothing reads it. The manifest
rows exist (FlowWorks 210 required, GSS 76) but are counted from each mod's `validation.py` components, while the
proofs emit different row ids (`P1_fresh_map`…), so even a reader could not join them today.

Since 2026-10-06 the report NAMES this instead of dropping it: "NOT IN THE TOTAL: 108 mods (1783 required checks)
have a manifest row and no record this report reads; 2 of them hold checkout results it cannot join". The 1543
denominator covers 40 of 148 manifest mods.

## Owed
1. One result contract: a checkout (Suite, proof_all, validation_v2) finalizes a record the report reads, with the
   run identity (deploy fingerprint, DLL srchash, mod-list fingerprint, harness hash) bound in it.
2. The manifest enumerates the ids the mod's ACTUAL checkout emits (walk header names the checkout script).
3. Selftest: a fresh valid synthetic proof_all result contributes; a stale one does not; an unread mod is listed.

Review that found it: `design/RimMandrake/northstar_review_2026-10-06.md` (GPT action 1, tested offline).

NEXT: add a `checkout:` header to the GSS walk naming proof_all.py, teach required_checks.py to enumerate its row ids, and add a proof_all-result reader to required_checks_report.py.
