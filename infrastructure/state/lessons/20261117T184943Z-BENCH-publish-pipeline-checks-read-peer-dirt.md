./publish runs its pipeline checks in the shared working tree, so a peer unit's UNCOMMITTED edit can red your publish (2026-11-17: selftest_mod_owner_hold read 'slots_full' from another unit's half-done maturation_dispatch.py/json max_live 1 work). Prove it is theirs first: copy rimflow+Utils+contracts into scratch with the peer files at HEAD and your files as-is, run the test (was 39 ok); then RM_PUBLISH_SKIP_PIPELINE_CHECKS='<why + evidence path>' ./publish. Never edit their files.
item: RIMMANDRAKE_REPIN_WHEN_GRANT_ITEMS_CLOSE
home: clone-landing-commits
