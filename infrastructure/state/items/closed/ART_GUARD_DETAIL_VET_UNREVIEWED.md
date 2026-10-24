## spec
ART_GUARD_RESIZE_VET_UNREVIEWED's review found a false-positive defect in the codex_image.py foreign-copy picture check and
fixed it; the fix is unreviewed. Both files are DIRTY on purpose (code_review_status): a different agent reviews and marks clean.
- skills/generating-images/scripts/codex_image.py: `FOREIGN_DETAIL_N`, `FOREIGN_DETAIL_CORR` (0.5), `_detail`, `_detail_corr`,
  and `_near_copy.match(p, t)` (a coarse 16x16 match must be confirmed by fine-detail correlation; flat fills keep the coarse verdict).
- selftest_codex_image.py: `noise_texture_png`, `test_lookalike_texture_not_foreign` (fails on the pre-fix code).

## Defect found
Independent codex terrain renders sit inside the 16x16 distance 4.0: dregen BankSilt_Rich vs FE_Ground SoilRich 1.81,
BasaltShingle vs BlackPebbles 2.73, PackedIce vs PackedSnow 3.59 (11 such pairs among 5,205 artpipe outputs). The guard would
set aside a terrain render as a "foreign copy" of a look-alike in the cache or a peer job.

## Evidence (/mnt/d/ClaudeWork/rimmandrake/guard_vet/)
- pairs_le6.txt / pairs_classified.tsv: all pairs <= 6 over 5,205 outputs; corr_all.tsv: detail correlation of every pair <= 4.
- fine.out / corr.out: copies 0.96-1.00, independent terrain -0.03..0.05; wing frames of one flyer 0.66/0.83 (unknown provenance).
- replay_fix.out: with the fix all 11 independent terrain pairs clear; the 38 still flagged are the known copy clusters.
- st_before_fix.txt (1 FAIL), st_after_fix.txt (all pass). Montage m1.png.

## verify
The 0.5 bar: a 2x downscale of pure per-pixel noise copies at 0.90 (selftest), real copies >= 0.96. A heavy JPEG/blur of a copy
is untested. The detail check also drops the accidental catch of mirrored/cropped terrain copies (FOREIGN_GUARD_WIDEN_MIRROR_CROP).
