# Work bundle WB-cause-RIMMANDRAKE-REDRAW-SKINFLAP-FLUTTER-BUTTERFLY-NOT-SAME-PICTURE-20261127-102434

## Members

| ticket | class | outcome | commits |
|---|---|---|---|
| RIMMANDRAKE_RESIZE_FLYERS_ADULTS_FLY_AT_BABY_SIZE_TWENTY_OF_THEM | REAL | fixed for 13 of 20 flyers; 7 on owner-held mods go to RIMMANDRAKE_RESIZE_HELD_FLYERS_FLY_AT_OWN_STAGE_SIZE_WHEN_LIFTED | abbfb368 (defs, census, model), de2c807d (live check), 772c121e (fix tool, remainder spec), 33950733 (flight.md) |

## Evidence

- Red: `flyer_size_census.py` listed 20 OFF on the parent. Green: `--except-held` exits 0 (13 fixed + Skinflap ok, 7 HELD).
- New female check: red on a planted Porg (female colours removed), green on the build.
- Live check `live_flyer_flight_sizes.py`: pass on the real Skinflap live reading (3d27ae3a, ArchSmall), fail on a planted
  baby-size reply. In-game run UNRUN: this run ran on SteveDesktop; ArchBig and ArchSmall are Archmagi's games, and
  Steve1/Steve2 take work only through the test lane. Command (after a deploy of the touched mods):
  `python.exe src/RimMandrake/Utils/art/live_flyer_flight_sizes.py RM_Krizzak RM_Vrisk RM_Skiralim RM_FeverSwarm RM_FireWasp RM_Sivvern RM_Kirruk RSW_Mynock RSW_Dactillion RSW_Porg RSW_Sketto RSW_Strill RSW_Urusai`
- Tests that read the changed files: 10 green; selftest_flyer_gate and selftest_flyer_tier_two fail identically on the
  parent (flier_body_stabilize.py: no cv2 on this machine, UNMEASURED).
- Fresh reader: RIMMANDRAKE_READ_FIX_ABBFB36895_WITH_FRESH_EYES.

## Context

After the one group: 164648 tokens (GO ON). Nothing is next in this bundle.
