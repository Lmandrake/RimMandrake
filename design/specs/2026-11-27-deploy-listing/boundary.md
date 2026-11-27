# Deploy listing: boundary page

Code: `src/RimMandrake/Utils/deploy_listing.py`, used by `deploy_custom_mods.py` (`inventory`) and `deploy_def_guard.py`
(`xml_files`). Tests: `src/RimMandrake/Utils/selftest_deploy_listing.py` (offline). Item:
`RIMMANDRAKE_SPEED_DEPLOY_PLAN_RELATIVE_STAT_ENOMEM_SILENT`. Index page: `design/specs/2026-11-26-deploy-index/boundary.md`.

Why: a stat of a game-copy file by absolute path cost 8 to 10 ms on the Windows drive, 1.5 ms relative to the open
folder. A folder listing that failed with ENOMEM under load was skipped without a word, so its files were unseen.

## DOES NOT SURVIVE (not handled)

- **a-vanished-subfolder.** A subfolder deleted between its parent's listing and its own listing stops the plan with
  its path. Only a missing mod root is an empty inventory.

## PROMISES (each one is owed a test of the same name)

- **enomem-listing-is-retried.** The walk restarts the folder listing after ENOMEM, including when iteration fails
  partway through. It uses the entries from the successful attempt.
- **a-listing-that-still-fails-is-named-not-skipped.** A folder that still cannot be listed after ENOMEM retries
  stops the plan with its path and the error. Other listing errors stop it immediately. An absent mod root is
  an empty inventory.
- **relative-stat-gives-the-same-index-as-absolute.** Where directory descriptors are supported, the walk lists the
  open folder and stats entries relative to it. The file paths, sizes, nanosecond times, hashes and cached defs
  agree with the absolute-path results.
