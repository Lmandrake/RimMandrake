# Belt fails fix 2026-10-09

Source: Transient/belt_acc_sitting2_20261009.md. Game down; nothing deployed or live-tested. The ledger fails stand; re-check items filed for sitting 3.

## DUNES_TINT_GATE_PROOF_1.A1 (real mod bug, fixed in source)
- Evidence: ProofTint reported hasColorProp=False; MatBases.Sand = Misc/Sand (Custom/Snow) has no _Color.
- Mechanism read: SectionLayer_DuneSand cloned MatBases.Sand and set Material.color, a silent no-op on that shader. Vertex RGB is the pollution lerp (SectionLayer_Sand writes red = pollution), so the existing VertexColor fallback would also misread a tint as pollution.
- False theory: "just flip the default tintMode to VertexColor". Rejected: red channel means pollution in the vanilla shader.
- Fix: for a non-white tint on a shader lacking _Color, draw a Map/Transparent clone of the sand texture with the tint as colour and white vertex RGB (relief lift kept). White tint unchanged. The check itself was right (the proof worked and resolved MOVING_DUNES_BUILD_1.A3); the criterion predicted hasColorProp=True, which is the false premise the fix removes.
- Recheck: DUNES_TINT_RENDER_RECHECK_1 (needs bridge + a new probe).

## LEANINGSCRUB_WEEPER_VINE_1.A1
- Confirmed on origin/main: cd03da899 removed placementMask from RM_VenomPool and RM_ThornLitter (no placementMask left under LeaningScrub). Sitting 2 saw 8 pools post-redeploy. Recheck: LEANINGSCRUB_WEEPER_RECHECK_1.

## LONGSHADE_JAWATOW_LIVECHECK_1 and GELATINOUSSLIME_JOININGWATER_LIVECHECK_1
- Cause was a wrong check target in content, not mechanism code: MayRequire mandrake.rm.longshade is a folded id; cd03da899 changed them (JawaReturnTow now mandrake.rm.biomes; JoiningWater defs mandrake.rm.biomes,Ideology). Sitting 2 live-proved both defs load after redeploy, but ran neither behaviour. Nothing further to change in source. Rechecks: LONGSHADE_JAWATOW_RECHECK_1, GELATINOUSSLIME_JOININGWATER_RECHECK_1.

## PARTIALS (not touched)
- ILLISK_LIVE_CHECK_1 (no water on the test tile) and LONGSHADE_SCENE_LIVECHECK_1 (force_incapacitate cannot attribute the harrok strike) are measurement gaps, not mod defects; left for sitting 3.
