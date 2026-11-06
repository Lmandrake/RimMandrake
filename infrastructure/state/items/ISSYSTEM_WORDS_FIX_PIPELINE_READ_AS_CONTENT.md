# ISSYSTEM_WORDS_FIX_PIPELINE_READ_AS_CONTENT

Found 2026-11-05 during the owner's pipeline-only pause (relentless_owner_pause.json, sha 8cf9344f57). While the pause
is on, only `ops_health.is_system` items (plus `LIGHTSPEED_*`) may start, so an `is_system` misfile now refuses
real pipeline work.

`ops_health.is_system` reads every one of these as content. None hits a mod word or a content word; each falls
through because its subject word is missing from `system_words` / `system_words_lead` in
`src/RimMandrake/Utils/ops_watch_rules.json`:

- CLOSE_GATE_ENFORCE_DONE_IS_EARNED (close, gate)
- CLOSE_SHA_FIX_HEAD_FALLBACK_CLAIM_COMMITS (close, sha)
- BENCHSHARD_DIAGNOSE_SAME_EVENTS_NEW_ORDER (benchshard)
- EXPEDITE_GATE_FIX_SPAWNED_ITEMS_LOOK_UNFILED (expedite, gate)
- BREAKER_SELFTEST_FIX_ONE_RED_IN_THIRTEEN (breaker, selftest)
- BOOKS_REGISTRY_UNSTICK_MOVED_FILE (books, registry)
- CONCEPT_TREE_ROUTE_FIX_WORDS_GATE_RED (concept)
- ARTLEDGER_SELFTEST_FIX_WRONG_SHARD_NAMETAG (artledger)
- BLOCK_DELEGATED_CARDS_HOOK_FIX_RECALL_GATE (block, hook)
- ADVANCEUNTIL_WIRE_PER_TICK_STOP (a bridge tool)

Likely the same: CLOSE_AUDIT_MEASURE_FALSE_CLOSES_HONESTLY, CLOSE_RETIER_*, CLOSE_SHA_REPAIR_*,
DEPTH_PROOFS_FIX_EXIT_ZERO_ON_FAIL, FLOWWORKS_SELFTEST_FIX_TWO_STRAY_REDS. About 118 content-read open ids carry
pipeline-ish words. The census and the per-id reasons were in the builder's scratch:
`census.py` / `census.txt` / `classes.json`. Re-run `is_system` over the open ids; do not trust that list.

The reverse direction (system read for content) showed no clear misfile in 13 mod-word hits.

Done when: the subject words are added where they are unambiguous (`selftest`, `hook` and `gate` probably go to
`system_words_lead`), each id above reads `is_system` true, and no content item flips. Add one selftest row per word
added. ops_watch_rules.json is an Operations rules file, so the close needs `--live`.
