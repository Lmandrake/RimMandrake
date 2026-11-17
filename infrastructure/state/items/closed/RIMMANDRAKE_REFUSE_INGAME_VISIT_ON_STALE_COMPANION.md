# RIMMANDRAKE_REFUSE_INGAME_VISIT_ON_STALE_COMPANION

## spec
Measured 2026-11-17 ~9:50 AM PST on Archmagi. The Maturation Pipeline's in-game launch
(`maturation.launch_mod`, in_game branch) checked the model, the visit owed and the bridge, and nothing else.
`build_match.py identity` hashes the mod's deployed folder, never `BridgeTools/JawaBench`, and the visit brief
deploys the mod but not the companion. Before this fix, the game folder's companion DLL read STALE
(`companion_identity.py`: embedded e7ace96c, wanted 9a021edc) after the GSS walk fixes landed (48a0c87a42,
1e99d7c0da). Nothing would have refused GSS visit 2, so its walk would have run the old checks.

Fix: at in_game, `launch_mod` reads `companion_identity.verdict` of the game folder's
`BridgeTools/JawaBench/JawaBench.BridgeTools.dll` against the launch tree's HEAD (cover on). Anything other than
FRESH refuses (rc 2). The refusal names the companion, its state, and the command that fixes it
(`python3 src/RimMandrake/bridgetools/build.py --gm --apply`, with the game down).

## verify
- `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation`: a STALE fixture DLL refuses with
  "companion" and "build.py" in the text and launches nothing. A MISSING DLL refuses. A FRESH fixture launches.

## refs
file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/selftest_maturation.py
