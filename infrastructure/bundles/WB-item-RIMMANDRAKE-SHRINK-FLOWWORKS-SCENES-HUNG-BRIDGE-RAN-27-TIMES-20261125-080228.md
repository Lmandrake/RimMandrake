# Work bundle WB-item-RIMMANDRAKE-SHRINK-FLOWWORKS-SCENES-HUNG-BRIDGE-RAN-27-TIMES-20261125-080228

System: FlowWorks's oversized live scenes (design/specs/2026-11-24-oversized-scenes/table.md section 1). One member.

## Done

| member | class | outcome | commits | live reading |
|---|---|---|---|---|
| RIMMANDRAKE_SHRINK_FLOWWORKS_SCENES_HUNG_BRIDGE_RAN_27_TIMES | REAL | fixed | 0a6c3358d2 (split, deciders moved), f303a90f1f (refill check repaired, split source scenes' offline cases), d679c4e592 (live rows) | 11 of 11 PASS on ArchBig, visit 13 early rows (version/in_game/bundle_shrink_20261125/rows.jsonl) |

- Red run: oversized_scenes_accept.py FlowWorks on 58fda53f61, 16 FAIL lines. Green from 0a6c3358d2.
- Offline: T_STOCK red on a planted endless pond (RM_StockMath.CanSupply true; rc 1), green on the real build (rc 0, 87
  cases), so the empty-pond follow left the live suite. CALLER_SPR_SPRAYS_WITHOUT_PUMP caught by T_SPRINKLER;
  CALLER_CONV_DROPS_CLIPPED caught by T_CONVERT run by hand (plant_faults.py said MISSED: a wrong verdict, lesson filed);
  DEF_STILL_RATE_TENFOLD red in selftest_garden_scene.py's new def check.
- Fresh reader (rm-consult, opus): one significant finding, no offline test of scene_source_draws, scene_source_refills or
  _src_brim. Fixed test first in f303a90f1f.
- Live run 1 (01:21 PST) ran on the 315-mod list (the stop never stopped the game); sc_source_refills FAILED there on a wrong
  check (rain lands in lumps more than 1,000 ticks apart), repaired test first. Run 2 (02:20 PST): 11 of 11 PASS, on the
  24-mod list another run had loaded (holds every fw_gss_sitting mod and FlowWorks; lacks mandrake.rm.patches of the
  flowworks tier), because game_instance.py stop inside game_lock.py run refused its own holder. That tool defect was fixed
  by another run at e446b9b324 while this run fixed it too (this run's copy dropped).

## Left

- An exact-tier rerun (13-mod flowworks; fw_gss_sitting for sc_lake_endless) was not made. live_pass.sh now works with
  e446b9b324: `python3 design/concepts/FlowWorks/version/in_game/bundle_shrink_20261125/wait_and_run.py`.
- The locked version's re-pin: this run's commit is tied to the owner's card (bc1493f318). The re-pin is still refused for
  51e271d211 (sc_moat_raid, 2026-11-23, another run's, no card); the Maturation tick reports it with its repair.

## Context size

After the build: about 290k of 1M. After the live pass: about 380k.
