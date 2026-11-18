# FLYER_GATE_FIX_NEGATION_READS_AS_FLIGHT

Found by the Conductor's owner-tagged triage (2026-11-03, D:\ClaudeWork\rimmandrake\conductor\owner_triage_2026-11-03.md).

## spec
`src/RimMandrake/rimflow/relentless_live.py` line 68 `flyer_re` is a bare word match
(`fly|flies|flying|flyers?|flight|wings?|airborne|takes? off|take-off`), used by
`relentless_game.gate()` (line 163) and the live lane (line 168). It matches negations:
`infrastructure/state/live_proofs/COLD_STORAGE_PROOF_VERIFY_ROT_RATES_LIVE.criteria` A6 reads
"carried by GravshipUtility.GenerateGravship and set down 12 cells east on the same map (no flight)",
and the item was held with "a flyer's flight is never live-tested without the owner present" — a hold
that then wrote needs=owner. The standing ruling is about a FLYER's flight (a flying creature), not the word.

Fix: hold only when a clause asks a flying creature/def to fly (e.g. a flyer def or flight verb that is not
negated: "no flight", "without flying", "never flies"). Keep every true positive in the current selftest.

## verify
- A1 L0: the relentless_live/relentless_game selftest holds a case built from the COLD_STORAGE A6 text and
  reads gate() == None for it, and still reads a hold for an existing true flyer clause (WEEPINGSTONES_NET_FLEEING_FLIER_1).
