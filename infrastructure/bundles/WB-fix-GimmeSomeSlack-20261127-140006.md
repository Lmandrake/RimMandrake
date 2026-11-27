# WB-fix-GimmeSomeSlack-20261127-140006 (state)

## Done
- RIMMANDRAKE_RAISE_SLACK_GATE_DEADLINE_SIXTY_SECONDS_FROM_ITS_RUN: closed at 4a1c7179f325. validation.py: OFFLINE_CALL_S 6000
  (was 600 x6), OFFLINE_TIER_S 12000 (WSL hop, was 3600). Offline tier 9/9 PASS in 473 s on Archmagi.

## In hand (one group: the wall lamp scene's two bridge hands)
- RIMMANDRAKE_STAGE_STYLE_KEY_SO_A_LOOK_NEEDS_NO_MOD_PROBE: jawa/build_batch `style=` (ThingStyleDef, set after the spawn as
  vanilla god mode does: Designator_Build.DesignateSingleCell), read back from CompStyleable.styleDef; s.stage things style=,
  s.act.place style=. Fact: the mod's pick (ConduitStylePicker.Pick) sets only des.styleDef + a menu memory, so for a lamp
  the style set is equal to the pick.
- RIMMANDRAKE_READ_WHAT_A_THING_DRAWS_NOT_ONLY_ITS_STYLE: path step `drawn` (host-computed, reviewed): thing.Graphic (mod
  patches run: GSS Patch_Thing_Graphic_LampMasterOff gives DefaultGraphic when the master is off), MatAt(thing.Rotation),
  -> fields path, texture, graphicClass, rot. DRAWN_PATH = "drawn.path" in scene_wall_lamp_looks.py.

## Group 2 state (2026-11-27)
- Published ef32aa59074c (style= + drawn reader + the scene), polish 99cbc9570f4e (slice start-guard check), c6c08113a45c
  (rect read by footprint). Offline green: selftest_scene_conversion 19/19, selftest_run_until 19+2+1 and plants red,
  selftest_stage_ops 6/6 and plants red. Context after group 2: 271k of 1M.
- Next: live pass on ArchBig (ArchSmall held by the Pyrelands run): modset_builder --tier gimmesomeslack_walk --apply,
  bridgetools/build.py --apply, deploy_custom_mods --mod GimmeSomeSlack --apply, launch, then
  `python.exe src/RimMandrake/Utils/scene.py accept src/RimMandrake/GimmeSomeSlack/northstar/scene_wall_lamp_looks.py --game ArchBig`
  clean and `--plant master_switch_off`. Never publish while an accept run is live.
