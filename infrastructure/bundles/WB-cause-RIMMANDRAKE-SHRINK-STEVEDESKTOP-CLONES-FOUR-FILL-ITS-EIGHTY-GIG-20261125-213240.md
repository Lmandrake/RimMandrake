# Work bundle WB-cause-RIMMANDRAKE-SHRINK-STEVEDESKTOP-CLONES-FOUR-FILL-ITS-EIGHTY-GIG-20261125-213240

System: SteveDesktop disk room (cause RIMMANDRAKE_SHRINK_STEVEDESKTOP_CLONES_FOUR_FILL_ITS_EIGHTY_GIG). One member.

## Done

| member | class | outcome | commit |
|---|---|---|---|
| RIMMANDRAKE_PRUNE_STEVE_LANE_SCREENSHOTS_HALF_GIG_A_DAY_ONTO_FULL_C | REAL | done (closed by the list_effect tick); live: unit run 3:16 PM PST, check HOLDS; deadman watches it via live_baseline.txt | cd98dd40b0, a544fa39db, c7a1379969, 0cb98773f1 |

Context after the group: 217k of 1M.

## What the next context needs

- `family_clean.py` has a host-only `screenshots` family. It runs only where `FAMILY_CLEAN_FAMILIES=screenshots`.
  Archmagi's daily run is unchanged.
- SteveDesktop kit: `infrastructure/stevedesktop/family_clean/` (unit, timer every 6 h, `install.sh`). The unit runs
  from `~/rm/runner`. Its `ExecStartPre` refuses runner code older than the family, because that code ignores the
  family set and would run every Archmagi family on SteveDesktop.
- `~/rm/runner` moves only when no lane job runs (`/mnt/d/RimTest/testq/current` empty): `git pull --ff-only`, as
  `/opt/stevedesktop/selfupgrade.sh` does.

## Next, in order

Nothing. The bundle is finished.
