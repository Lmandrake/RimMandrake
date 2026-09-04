# IMAGE_SKILL_SCRIPT_NITS_1 — two small skill-script findings from the DIRTY_CODE_REVIEW_LOOP sweep

## spec

1. **`skills/editing-images/scripts/compare_images.py`**: docstring promises a
   key-colour fallback when there's no alpha channel, but `subject_stats()` (~45-51)
   has none — when `has_alpha` is False every pixel counts as visible, so
   bbox/coverage/centroid become the full canvas and the resize/move drift checks
   (~125-139) never fire for non-alpha image pairs, silently passing real silhouette
   drift.
2. **`skills/generating-rimworld-sprites/scripts/selftest.py`**: `squash()` (~100-102)
   is dead code — `CASES` (~137) calls `_squash()` directly, so `squash()` and its
   wrapper are never invoked.

## verify

#1: run `compare_images.py` on a non-alpha pair with a deliberately shifted/resized
subject and confirm it currently passes when it should fail.
#2: `grep -n "squash\b" skills/generating-rimworld-sprites/scripts/selftest.py` shows
only the dead definition and `_squash()` calls.

## criteria

Both are skill scripts — fixed in a dedicated fresh-context curation session per
CLAUDE.md, not ad hoc. #1 is the one worth prioritizing (false-pass on real drift);
#2 is a one-line deletion whenever anyone is next in that file.
