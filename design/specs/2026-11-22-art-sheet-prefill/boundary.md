# BOUNDARY: a review sheet's prefill from the owner's keeps, Design Version 0.1.0

Code: `src/RimMandrake/Utils/art/art_sheet.py`, `prefill_for` and `graphic_rulings` (the agent's prefill on each
picture slot of a sheet that `art_sheet.py` builds). Item: `RIMMANDRAKE_GENERATE_FLOWWORKS_TANK_DESIGNS_FIRST_RUN_ONLY_REPAINTED`.
Written 2026-11-22. Each promise has a test of its name in `src/RimMandrake/Utils/art/selftest_prefill_keep_ts.py`. The
prefill keeps no state between builds, so the page has no LIFE CYCLES. The rest of `art_sheet.py` is not on this page.

## ACCEPTS (the only inputs the prefill is built for)

- **the-art-ledger-rulings.** Ruling events of `artledger.Index`: a sheet ruling (`at`, `ts`, `subject_key`,
  `target.shas`) and an install ruling (`ts` only, an empty `subject_key`, `target.sha`).
- **the-graphic-columns.** One graphic's columns, each with its letter, kind and the picture shas of its faces.

## DOES NOT SURVIVE (not promised)

- **a-ruling-with-no-time.** A keep with neither a readable `at` nor `ts` sorts as the oldest. A stamp with no offset is
  read as this machine's local time.
- **two-keeps-at-the-same-second.** Their order is the ledger's order.

## PROMISES (each one is owed a test of the same name)

- **newest-keep-wins-whatever-stamp.** Of the owner's ruled keeps that name a picture on the row, the newest one
  prefills, timed by `at`, else `ts`. A newer sheet keep still beats an older install keep.
- **install-keep-reaches-the-prefill.** An owner keep that names one of the graphic's column pictures reaches the
  prefill even when its `subject_key` is empty, and is listed once when found both ways.
- **newest-keep-wins-across-time-zones.** Stamps are compared as moments, not strings: a UTC `at` (`Z`) and a local
  `ts` (`-0700`) order by the instant they name.
- **released-keep-never-prefills.** A keep that a later ruling releases (`releases: <id>`) does not prefill.
- **live-modern-tank-prefills-what-ships.** On the live art ledger, the Modern liquid tank slot prefills to the shipped
  white tank he picked by card on 2026-10-22, never to the red render he kept on 2026-10-21. Without those rulings in the
  ledger the test fails as UNMEASURED.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
