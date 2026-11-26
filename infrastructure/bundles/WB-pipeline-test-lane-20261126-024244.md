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

## Done (2026-11-25 11:05 PM PST): every member closed

| ticket | class | fix | live reading | outcome |
|---|---|---|---|---|
| HARNESS_REPAIR_CAUSE_4D2C5B87_3 | SITE | 9f434a10d1 | 4D2C5B87_record.json (47 judged rows) + 4D2C5B87_swept_record.json (stay wait ran, PASS) | closed d24b4492b6 |
| HARNESS_REPAIR_CAUSE_3A38C661_3 | HARNESS | 00725c7501, polish bc78e4eee8 | 3A38C661_record.json (10 PASS) | closed by the list_effect tick |
| HARNESS_REPAIR_CAUSE_CEF341B8_2 | HARNESS | 9be89583ef, c829ee057e (fresh reader) | CEF341B8_record.json (FAIL now valid) | closed by the list_effect tick |

Records: design/specs/2026-11-26-test-lane-bundle-reruns/. Re-runs were direct on ArchSmall (SteveDesktop refuses mod
jobs; the Archmagi testq lane takes no targeted job). Found on the way and filed: kutte.stairs (in ModsConfig.MINIMAL.xml,
on no Archmagi folder) on RIMMANDRAKE_MAKE_MODCHECK_RESTART_GAME_ONTO_ITS_LIST_THREE_HAND_WORKAROUNDS; Grey floor 0 of 17
plants on GREYSEA_FLOOR_FLORA_ZERO_1; thirst T9/T17 FAIL and astrofuel muffalo death on
RIMMANDRAKE_CLASS_SEVEN_THIRST_FAILS_SITE_FULL_OF_PATIENTS; publish-under-live-run lesson merged (fb3062b6da).
Context after the code groups: 252k of 1M (GO ON); no restart.
