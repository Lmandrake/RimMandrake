# modset restore bug (TESTENV_MODSET_RESTORE_WRONG_FILE)

## Cause
modset_builder.py --restore never looked at the before-copy: it did shutil.copy2(FULL_BACKUP) i.e.
infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml (md5 1ab545a0). The newest
ModsConfig.before-tier-*.xml was only compared by mod COUNT inside try/except: pass.

## Fix
- --tier --apply now records deployed/config/ModsConfig.swap-active.json (tier, before-copy, md5); a second
  swap keeps the original before-copy (does not snapshot the previous tier's tiny list).
- --restore copies the marker's before-copy, verifies md5 before and after, removes marker; refuses loudly
  with no marker / missing / tampered copy. FULL.LATEST only via explicit --restore-full.
- selftest_modset_restore.py (temp dirs) 6/6. Skill rimworld-load-round line fixed (--minimal --restore are exclusive).

## Proof
run_selftests: 416/419 pass; only FAIL selftest_flowworks_stock.py (unrelated, PondReturnChecks.cs edited uncommitted by another window).
