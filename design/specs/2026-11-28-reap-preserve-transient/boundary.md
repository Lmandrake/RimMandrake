# BOUNDARY: an archive outlasts a short ENOMEM and a failed one leaves nothing, Design Version 0.1.0

Code: `preserve`, `preserve_retrying` and `PRESERVE_ENOMEM_WAITS_S` in `src/RimMandrake/Utils/scratch_reap.py`, and
the call of `preserve_retrying` in `act`. Item: `OPS_SCRATCH_DIRT_MEASURE_AT_END_YOGQ`, written Sat 2026-11-28. Each
promise has a test of its name in `src/RimMandrake/Utils/selftest_scratch_reap_preserve_enomem.py`.

## Why

- The archive root is on `/mnt/d` (drvfs) on Archmagi. Under load drvfs answers ENOMEM and works a moment later.
- The rm-scratch-reap run of 2026-11-28 04:00Z ended with one failure, `tmp1otmqzap: [Errno 12] Cannot allocate
  memory`. The failure rang SCRATCH_DIRTY_END and reopened the item. The next run archived the same dir at 07:12Z with
  no error. The same refusal is on record on 2026-11-02, for a 1.7 GB session dir.
- That failed attempt also left `.incoming-6_xh5zj6` (a clone.bundle and a status.txt) in the archive. `preserve`
  removed its `.incoming-` dir only when the final rename failed.

## The danger the limits guard

- **`PRESERVE_ENOMEM_WAITS_S` (5 s, then 30 s).** A hang guard against an ENOMEM that does not clear. Then the row is
  refused and the next run tries again, as before. The waits sum to 35 s, in a reap that runs about 3 h.

## ACCEPTS (the only inputs this is built for)

- **an-archive-row.** A row with verdict ARCHIVE that `act` hands to `preserve_retrying`, with the archive root on any
  filesystem.

## DOES NOT SURVIVE (not promised)

- **an-enomem-after-the-final-rename.** An ENOMEM in the fsync of the day dirs, after the rename, lands a second
  archive of the same source on the retry. Both archives are whole; only the space is spent twice.
- **a-killed-reap.** A SIGKILL between the copy and the rename still leaves an `.incoming-` dir.

## PROMISES (each one is owed a test of the same name)

- **a-short-enomem-is-retried.** One ENOMEM during an archive, then the archive lands with its manifest, once.
- **a-lasting-enomem-fails-loud.** An ENOMEM that outlasts the waits raises, and the source stays.
- **another-error-is-not-retried.** An error that is not ENOMEM raises at once.
- **a-failed-attempt-leaves-no-incoming.** No attempt that raises before the final rename leaves an `.incoming-` dir.
