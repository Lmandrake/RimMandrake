# CODEX_FOREIGN_COPY_GUARD_FIX_RESIZED

Found by the round-3 fauna judge (FOUNDRY judge, 2026-10-24, delegated: art-eval).

## What is wrong

Three round-3 art-eval jobs finished `ok` with one byte-identical PNG: sha256 prefix bde44afbfe6c, 256x256, 91,497 bytes. The image
is an unrelated machine render, a riveted copper port flange beside a clamped pipe stub.

| job | done (local) | mode | worker note |
|---|---|---|---|
| arteval_RM_Zisska_r3_south | 02:00 | edit, derive_from ..._r3_east | "Derived the accepted zisska master ... preserved transparent margins" |
| arteval_RM_Surrik_r3_south | 02:18 | edit, derive_from ..._r3_east | "Derived the accepted surrik master ... resized it to exactly 256x256" |
| arteval_RM_SparkleechGrub_r3_east | 02:22 | generate | "Generated with built-in imagegen ... resized to exactly 256x256" |

All three finished after the CODEX_FOREIGN_IMAGE_COPY guard (8cea1c2d5f, 01:15). The guard refuses a placed file only when
it is byte-identical to a pre-existing cache image. These workers RESIZED the foreign file to 256 before placing it, so the
bytes no longer match the cache and the guard passes them. It is the same defect as the one 8cea1c2d5f fixed, reached by one extra step. The
second fix (afaee7c244, 02:23) landed after all three.

A scan of every artpipe render since 2026-10-23 12:00 (311 files) found only this one duplicate group:
`D:\ClaudeWork\rimmandrake\judge_round3\dup_scan.txt`.

## To do

1. Harden the guard: compare the placed file against cache images after downscaling both, for example an alpha-cropped 32px thumbnail
   distance, as the foreign-copy audit already did. A cheap cross-job check also works: refuse a result byte-identical to another
   job's `_artsrc` output.
2. Re-queue the three jobs (done -> pending, with their manifests moved to `_requeued_manifests`) and judge them as round 3. They were NOT
   judged, so no regen round was spent on a picture that was not theirs. Subjects RM_Zisska, RM_Surrik and RM_SparkleechGrub
   are held at round 3 until this is done.
