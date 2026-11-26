# WB-pipeline-art-pipeline-20261126-103530 (pipeline:art-pipeline)

Worker: detached BENCH run in clone RIMMASTER_TEACH_FLYER_JUDGE_PARTS_SHEET_STILLS_MISSED_IT.det on SteveDesktop. Steps
that need GPT or Archmagi-only pictures ran on Archmagi over Tailscale SSH, in a scratch clone (now removed).

## Step A, the reality sort

- `SHADOW_SHEET_FIX_SHOWS_ONLY_THE_INSTALLED`: done already. Shadow builds on runs recorded after the fix
  (owner_escalations_contagion_20261024, audit_20261026_c1r1, audit_auto_20261107_1651) show the uninstalled candidate
  PNGs as reference panels on their rows. Its built sha 5a439387f2 left main in a history rewrite: re-recorded at the
  main-line copy 6292651282, A1 verified, done.
- `REGEN_RENDERS_INSTALL_AS_THEY_LAND`: done already. A1 live pass 2026-10-21; A2 settled by his card "Judge by a second
  agent, you veto" (B/C/D KEEP 2026-10-23). Built sha 3fd18591bc re-recorded at the main-line copy 110fb20fe4, done.
- `RIMMASTER_TEACH_FLYER_JUDGE_PARTS_SHEET_STILLS_MISSED_IT`: kept. Its check was shaped already; parts 2 and 3 red.

## Step B and C: done (2026-11-26 3:51 AM PST), every member closed

| ticket | outcome | commits | reading |
|---|---|---|---|
| RIMMASTER_TEACH_FLYER_JUDGE_PARTS_SHEET_STILLS_MISSED_IT | closed by the list_effect tick (check holds 3/3) | 7a22bb2856, 24b9e6b8f5, 65b241332b, c61c24ae56 | regress_flyer_c5a_full_20261126: 10/13, the 3 fails named misses; CL-047 fixed |
| SHADOW_SHEET_FIX_SHOWS_ONLY_THE_INSTALLED | done already | 6292651282 | owner_escalations_contagion_20261024/shadow_build.log |
| REGEN_RENDERS_INSTALL_AS_THEY_LAND | done already | 110fb20fe4 | rustpuff_ABCD_live_20261021.png; art_judgments_2026-10-23.md |

Fixed on the way, no ticket left open:
- The art judge brief read UNTESTED after the two flyer rows joined the regression set: their cards had no pins and
  lived in another run. `art_calibration.py` now reads a card from the run that `card_sources` names, and names flight
  frames and the parts sheet to the judge (65b241332b).
- The first 16-case calibration kept Danglemaw r1 on C1 (refused in the 3 runs before; the judge wrote "C1 only bans a
  face or eyes"). C1 now says a mouth or teeth is face and the back of a head is closed (9ad7d729e5, diffguard:
  clarify). Recalibrated: CALIBRATED 16/16 (2d62ca2641).
- Flyer must-pass control: vanilla Chicken flight frames (his bird E) raise no C5a FLYER code in either judge
  (`infrastructure/state/art_eval/runs/chicken_flyer_control_20261126b/`).

Fresh reader (GPT, code_review.md, on Archmagi): no significant finding, no polish line.
