# RESTORE_SUPERSEDED_MODLIST_SHA_1 — verify, BUILD, 2026-08-22

## applied by
8c16d94a Restore the fingerprint 9078a15 overwrote, by ADDING a field not changing one

## the entry, field by field (verify: clause)
  modlist_sha           = 5ef6eec3daf6c325
  supersededModlistSha  = e0f11692cf69e516
  seal present          = False
  capturedUtc           = 2026-08-21T08:20:20Z (untouched)

## other two entries byte-unchanged in that commit
 infrastructure/state/dumps/REGISTRY.jsonl | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
4

## selftest_frozen_dumps.py
32/32 passed
