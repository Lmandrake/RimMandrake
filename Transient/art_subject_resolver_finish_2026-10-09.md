# ART_SUBJECT_RESOLVER_1 finish notes 2026-10-09
Started from 76a1f7c1f. Order: (1) backfill target_def, (2) legacy index, (3) name-logic retirement.
- step1 code: backfill.step_artpipe now reads target_def/install_to/target_original and emits idempotent 'binding' events (Index.bindings); selftest_backfill_bind.py. Live run pending.
