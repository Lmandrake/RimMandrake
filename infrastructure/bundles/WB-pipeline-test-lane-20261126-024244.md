# WB-pipeline-test-lane-20261126-024244 (pipeline:test-lane)

Worker: detached BENCH run in clone HARNESS_REPAIR_CAUSE_4D2C5B87_3.det. Started 2026-11-25 6:52 PM PST.

## Members and class (step 1)

- `HARNESS_REPAIR_CAUSE_4D2C5B87_3`: REAL, fix already published (9f434a10d1, class SITE recorded). Open part: the
  re-run. Doors: SteveDesktop refuses mod jobs (host_work_switch), the Archmagi testq lane is off and full-list only.
  Route: a direct re-run on a free Archmagi game, judged by `retest.py passed <record>` (precedent
  RIMMANDRAKE_RERUN_TWO_HARNESS_REPAIRS_ON_FREE_ARCHMAGI_GAME, 99c476351c).
- `HARNESS_REPAIR_CAUSE_3A38C661_3`: HARNESS (class note published). The restart repaired the stale load; run 2 died
  of the companion CAMPAIGN refusal fixed at 4fd408d81b (HARNESS_REPAIR_CAUSE_4AFBF8A2_3); retest kept naming it
  stale_load. Fixed 00725c7501 (+ polish bc78e4eee8).
- `HARNESS_REPAIR_CAUSE_CEF341B8_2`: HARNESS (class note published). colonists_zero read only the current map; the
  chain makes the empty seabed map current. Fixed 9be89583ef; fresh reader's significant case fixed c829ee057e;
  validity.py FLAGGED (6e231c3487).

## Done

- Code fixes for all three are published; both negative controls exit 1. Fresh reader done (one significant finding,
  fixed test first; retest none significant).
- Live re-runs: design/specs/2026-11-26-test-lane-bundle-reruns/take.sh (f218e2ff59), waitalive job wb_tl_all, log
  D:\ClaudeWork\scratch\test_lane_bundle_reruns_20261126\sitting.log. Both Archmagi games held by other BENCH runs
  from 7:16 PM PST to at least 8:51 PM PST.

## Next

1. `waitalive.py attach wb_tl_all` (or re-run take.sh for each record still missing); 2. per item: reshape its check onto
   `<name>_record.json` via retest.py passed, verify, close.
