# WB-item-HARNESS-REPAIR-CAUSE-4AFBF8A2-3-20261125-100229

System: modcheck live runner (src/RimMandrake/Utils/modcheck/runner.py), the site hold after live drivers.

## Members

| member | class | commits | state |
|---|---|---|---|
| HARNESS_REPAIR_CAUSE_4AFBF8A2_3 | REAL, class SITE (note 4) | 04278d644f, 4fd408d81b (both on origin/main) | live re-run PASSES; close owed |

## Learned

- The re-run J20261125T082455Z-f27001 ran at 04278d644f only: INVALID HARNESS, "companion profile is 'campaign', not
  'test'". 4fd408d81b targets that refusal.
- The Archmagi testq lane never admits a targeted job (J20261125T100829Z-9199e0 was cancelled for it); SteveDesktop's lane
  is paused (owner, 2026-11-25 12:38 AM PST). Per the CONDUCTOR RULING of 2:15 AM PST the re-run ran directly on ArchBig.
- A direct modcheck run does not restart the game onto its composed list (it refuses mod_not_installed / stale_load).
  The working sequence, as the lane worker does it: game down, deploy the mod, `rimflow bridge take --host <game>`,
  `modset_builder.py --tier flowworks_list --apply`, `game_instance.py launch <game> --wait`, then modcheck with
  `MODCHECK_KEEP_MODLIST=1 MODCHECK_SKIP_DEPLOY=1`. Scripts: `D:\ClaudeWork\rimmandrake\evidence\HARNESS_REPAIR_CAUSE_4AFBF8A2_3\`.
- modset_builder refused on a 9-hour-old BENCH swap marker (flowworks_list, Nov 24 6:26 PM PST); it was set aside as
  `ModsConfig.swap-active.json.stale-20261125T0338-harness4afb`, as three earlier stale markers were.
- Live reading (ArchBig, 3:45-4:04 AM PST, sha 796f7cee91): the driver suspension_bridge_proof LEFT 1 COLONIST CORPSE,
  the runner started a fresh map, canary GREEN, suspension_bridges_and_covers PASS 9 UNMEASURED 2 (owed by-eye looks),
  machinery_pipes PASS 2. Record: `*.rerun_record.json` beside this file; `retest.py passed <record>` exits 0.

## Next, in order

1. Re-shape the outcome check to the committed record; verify; close with 4fd408d81b.

## Context size after each group

- after reading and submit: 98548 of 1000000
