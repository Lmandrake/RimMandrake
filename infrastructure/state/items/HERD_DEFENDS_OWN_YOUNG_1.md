# HERD_DEFENDS_OWN_YOUNG_1 — CB-2: herds defend own young only; one defender per nursery

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` (remaining rows, helper pass 2026-10-09; owner 'Queue all' card 2026-10-08). Row CB-2 there is the spec; its 'Checked' column says what was read to confirm it is unbuilt. Re-check src before building.

| CB-2 | A herd defends its own young only. Tame adults defend tame calves, wild adults defend wild ones, and a tame adult never turns on its own colonists. One intrusion rouses one defender per nursery, not one per calf. | Faction match in FindGuardian; shared per-intruder cooldown. | S | low | CreatureBehaviors (consumers: RSW_ShrublandGiant and other ParentalEnrage users) | `RM_CompParentalEnrage.cs:350-398` FindGuardian matches def/adult/distance/true-parent only, no faction test; exemptSameFaction (l.183, 309) filters the intruder, not the guardian |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.
