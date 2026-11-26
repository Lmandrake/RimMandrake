## spec
`publish.py pipeline_checks` honours `RM_PUBLISH_SKIP_PIPELINE_CHECKS="<why>"` by printing one line and returning. The
skip and its reason are written nowhere durable: no commit trailer, no ledger event, no file [measured 2026-11-18:
grep of publish.py; `git log` of the five pipeline-touching 2026-11-17 landings carries no marker]. The builder's
handoff (CONDUCTOR_HANDOFF_202611180743, culled 2026-11-25; in git at `eeb532cee4`) says four commits used it; which four cannot be read from the record, so
RIMMANDRAKE_VERIFY_REMOTE_LANDINGS_FOUR_SKIPPED_THE_DOOR had to re-run the door at all five. A skipped door is the
loud path only if it stays loud afterwards. Same gap for RM_PUBLISH_SKIP_TREE_CHECKS.

## verify
Acceptance test: none yet. The builder first writes a selftest_publish.py case: a fixture publish with
RM_PUBLISH_SKIP_PIPELINE_CHECKS set leaves its reason readable afterwards (a trailer on the landed commit, or a ledger
event naming the sha), watched failing on 5b2094cc9d.

## criteria
- Every landing that skipped the pipeline or tree checks can be found later, with its reason, from git or the ledger.
