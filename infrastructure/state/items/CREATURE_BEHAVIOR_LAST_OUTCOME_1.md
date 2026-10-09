# CREATURE_BEHAVIOR_LAST_OUTCOME_1 — CB-7: Ambushers, lures and alarms record last outcome

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row CB-7 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:

| CB-7 | *(test support)* Ambushers, lures and alarms record what they last did and why, the way the traction lance already does. A test script can then read the answer directly instead of watching for it. | Copy the `tetherLastOutcome` pattern into DrumLure, AquaticAmbusher, HeatBurstPredator and ReactionSource, and expose it through the inspect string or a bridge read. | S | none | CreatureBehaviors; feeds CREATURE_BEHAVIORS_FIRST_SCRIPT_1 | only `RM_CompTetherPull.cs` / `RM_Building_TractionLance.cs` carry a last-outcome field; the first-script item wants "cheap state checks" |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: CreatureBehaviors builds clean; each of DrumLure, AquaticAmbusher, HeatBurstPredator, ReactionSource carries a last-outcome field shown in the inspect string; toggle in Mod Settings.
