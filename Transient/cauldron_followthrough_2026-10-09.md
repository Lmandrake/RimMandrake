# Cauldron sheet follow-through — 2026-10-09

One line per TODO/conflict from `art.py enact` (8eaa2b252): what was done, evidence.

## TODOs

## Conflicts

## Enact bug
- ROOT CAUSE: on --apply, step 1 ingest wrote owner KEEP rulings for the row's own pick column (GR_Beetlefleet: pick B incl. B-north 1353dead) and for a DEFAULT variant column on a redo row (AA_InfectedAerofleet: variants [B], variantsDefault, all three B pictures ✕'d) — ruling ids 0bc5d894264bbaa0b3c6, f23447ec2a9ccf1a612b. Step 4 then read those fresh keeps as protection. The dry run never writes ingest, so it planned the purges: dry ≠ apply.
- FIX: ingest.py drops ✕'d shas of the same row from pick/picks/variant keeps (a wholly ✕'d column gets no keep); enact.py never installs or protects a same-row ✕'d picture, and a keep minted by the same row of the same decisions file no longer blocks that row's ✕ (purge releases it). Selftest `src/RimMandrake/Utils/art/selftest_enact_selfpurge.py` (fails 8/10 on the pre-fix code, passes 10/10 after).

## Legacy unqueued
