# Polish beside design/specs/art-install-authority/boundary.md

## (fresh read, WB-pipeline-read-utils-20261128-092119, 2026-11-28)
- `src/RimMandrake/Utils/art/artledger.py` `install()` under a Conductor ruling alone takes the owner-authority branch and skips the `was_purged` and `rejection_refusal` guards; no page promise names this (a next_version candidate).
- `src/RimMandrake/Utils/art/artledger.py` in picture mode `correct_keep` does not check that the keep came from an install; only a provenance_fix could make such a keep, and no call site does.
- `src/RimMandrake/Utils/art/artledger.py` `install()` with the Conductor ruling and a `ruling_id` both writes `ruling_id` and `reason="conductor-ruling"` on the event.
