# PROOF_ALL_DURABLE_RESULTS_1 — proof_all.py can lose or overstate evidence

Found by the 2026-10-06 northstar review (`design/RimMandrake/northstar_review_2026-10-06.md` finding 6), each
CONFIRMED by reading `src/RimMandrake/GimmeSomeSlack/proof_all.py`:
1. The result JSON is written only after `P.run()` returns (l. ~701-711, `try/finally` restores, then writes): an
   exception in any later block (determinism, log budget) loses every row already taken.
2. `p3_probes_and_site()` (l. 299): `w.get("success") is not False` reads a response with no `success` field as a
   success, so a failed pawn-list call can look like an empty region.
3. `Proof.want()`: `--only core,aerial` also skips the `preflight` block unless it is named.

⚠️ `proof_all.py` sits in the mod root, so editing it makes the GSS proof STALE (mod_hash excludes only
validation.py / human_review.py / northstar/). Move it under `northstar/` in the same change.

NEXT: move proof_all.py under GimmeSomeSlack/northstar/, write the result JSON after every block (partial, marked not certifiable), require an explicit `success: true`, and always run preflight; add a fake-bridge selftest that injects a final-block exception.
