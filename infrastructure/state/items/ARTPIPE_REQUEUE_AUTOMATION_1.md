# ARTPIPE_REQUEUE_AUTOMATION_1

The art daemon files every codex `response-schema channel mismatch` run as worker_error after 2 attempts, and a failed east master permanently fails its north/south `derive_from` siblings as master_failed. Over 24h (2026-10-04/05) that was 54 worker_error and 59 master_failed of 171 failures; all worker_error jobs requeued fine by hand (`Transient/biome_ffar/failure_triage_2026-10-05.md`).

Owed: a requeue pass (like `requeue_quota_failures.py`) for worker_error with that signature, which also requeues master_failed siblings once their master is pending or done. Never touches failed_canon; the canon gate stays as is. Also owed: a facing-word lint at job-filing time, since 'all three facings' in a prompt wasted a whole job set.
