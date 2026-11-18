# RIMMANDRAKE_KEEP_SHA256_REFLOG_TIPS_FORTY_CHAR_FILTER

## spec
`scratch_reap.py` `reflog_tips()` (line ~1025) keeps a reflog entry only when `len(w[1]) == 40`. A SHA-256 repository's
object ids are 64 characters, so every reflog tip of such a clone is dropped: a clean SHA-256 clone that was reset away
from its only unique commit can be judged DELETE although its reflog still holds that commit. Found by Codex's full-file
review of scratch_reap.py 2026-11-18 (lane I, RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH); read and
confirmed in the source, not run. selftest_scratch_reap_objformat.py exists and is the natural home for the case.

## verify
Acceptance test: a case in `src/RimMandrake/Utils/selftest_scratch_reap_objformat.py`: a `git init --object-format=sha256`
clone, commit A, commit B, `git reset --hard A` (B only in the reflog), aged past the TTL; the reaper must not judge it
DELETE (ARCHIVE or REFUSE). Expected: red on the base (B's 64-char id is filtered), green after accepting ids of the
repository's object format. Not yet written or watched failing: the filing run ended its lane first.

## criteria
- A SHA-256 clone whose only unique commit lives in its reflog is never deleted unbundled.
