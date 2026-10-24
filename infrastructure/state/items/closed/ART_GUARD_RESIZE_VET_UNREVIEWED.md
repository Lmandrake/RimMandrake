## What to vet
The resized/recompressed half of the codex_image.py foreign-copy guard (CODEX_FOREIGN_COPY_GUARD_FIX_RESIZED) is unreviewed:
`_cache_entries`, `_preexisting_twin(entries)`, `_thumb`, `_thumb_dist`, `_ThumbIndex`, `_peer_outputs`, `_near_copy`,
`foreign_source`, the `_do_image` call site and `stage_and_run`'s `inner.layout_out`, plus `test_resized_foreign_copy` in
selftest_codex_image.py. Both files are DIRTY (code_review_status) on purpose; a second agent reviews and marks clean.

## Evidence
- Calibration: /mnt/d/ClaudeWork/rimmandrake/guard_resize/calib.json — bad Zisska r3 south is 1.12
  from its cache source; nearest legitimate pair (two facings of one creature) 7.05; threshold 4.0.
- Old guard on the new test: 7 failed checks (/mnt/d/ClaudeWork/rimmandrake/guard_resize/st_old.txt); new: all pass (/mnt/d/ClaudeWork/rimmandrake/guard_resize/st5.txt).
- Real replay finds the Zisska source in 47 s cold; warm index 45 s total, of which ~42 s is the pre-existing cache file walk.

## Known caveats (author's own review, no defects found)
- Peer-output thumbnails are not indexed: up to 400 decodes (~20 s on /mnt/d) per placed file.
- A centre-crop of a non-square source is not undone; caught only if the thumbnail stays near.
- Concurrent workers' index saves are last-writer-wins; a lost entry only costs a re-decode.
- A legitimate regen of the same subject without --image could in principle sit < 4.0 from a peer output; not observed.
