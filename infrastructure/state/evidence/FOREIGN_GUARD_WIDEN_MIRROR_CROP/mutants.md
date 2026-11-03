# Mutants that the proof must turn red (FOREIGN_GUARD_WIDEN_MIRROR_CROP)

Run from the repo root with `RM_DATA_ROOT=$(mktemp -d)`:
`python3 src/RimMandrake/Utils/run_selftests.py --only skills/generating-images/scripts/selftest_codex_image.py`.
Each mutant is one edit to `skills/generating-images/scripts/codex_image.py` `_near_copy`. Restore the file after each.

| mutant | check that goes red |
|---|---|
| `if c is not None and c < FOREIGN_DETAIL_CORR:` -> `if False:` (no detail rejection) | "the guard itself keeps an independently drawn sibling west beside a peer's east": foreign_source returns (sibE, mirrored, 1.97) |
| `refs += [_mirror_thumb(r) for r in refs]` -> `pass` (no mirrored input thumbnails) | "a west from its own east reference is kept beside a prior mirror of that reference": prior_west.png, distance 0.23 |
| drop the mirrored entry from `mines` | mirrored cache/peer copies are no longer set aside |
| drop the `centre_t` variant | the centre-square crop is no longer set aside |
| skip `_mirror_grid` on our detail grid | the mirrored copy fails detail and is kept |
