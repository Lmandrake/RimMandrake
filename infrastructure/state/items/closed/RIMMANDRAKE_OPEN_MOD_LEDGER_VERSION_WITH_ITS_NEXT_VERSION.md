# RIMMANDRAKE_OPEN_MOD_LEDGER_VERSION_WITH_ITS_NEXT_VERSION

## spec
A failure happened. GimmeSomeSlack opened Design Version 0.1.1 by `maturation.py next-version` at 2026-11-20 4:09 PM
PST. Its mod ledger (`design/concepts/GimmeSomeSlack/ledger/`) still reduced to version 0.1.0. So the
preflight-to-offline_build `stage.accepted` of 0.1.1 (DISPATCH:d2ef0eafff878f00, 2026-11-21T00:59:23Z) was written with
`"version": "0.1.0"`, and the views showed 0.1.0.

Cause: `maturation.next_version` opens the new stage record but writes no `version.open` to the mod ledger. Only
`modledger_backfill` wrote `version.open`, and `modledger.append` takes the version from the ledger's own reduction.

Fix: `maturation.ledger_version_open` appends one DISPATCH `version.open` (body `version`, `text`) after the new record
is committed, for a mod that has a ledger. GimmeSomeSlack's ledger was repaired in the same run with a `version.open
0.1.1` (DISPATCH:1769d7817c8f1dfd). The earlier event stays as written (append-only).

## criteria
- After next-version to a newer version, `modledger.reduce(modledger.read(root, mod))["version"]` reads the new version.

## verify
`python3 src/RimMandrake/rimflow/selftest_maturation.py` row "next-version opens the new version in the mod ledger
too". Seen red before the fix ("ledger reads 0.1.0, want 9.9.9"). ALL PASS after the fix. Also green:
selftest_modledger, selftest_maturation_dispatch, selftest_maturation_autonomy.

## refs
file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/selftest_maturation.py
