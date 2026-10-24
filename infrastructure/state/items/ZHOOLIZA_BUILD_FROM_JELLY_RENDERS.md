# ZHOOLIZA_BUILD_FROM_JELLY_RENDERS

Owner, owner_escalations_contagion sheet 2026-10-24, note on RM_OcularJelly (label "zhool"): "Make B and C into two random pool members of a NEW CREATURE, they're absurdly cool. Call it a Zhool'Iza. Same properties, but 1/3 the size of the Zhool."

## What
New Contagion animal (defName to choose, e.g. RM_ZhoolIza; label "zhool'iza"), cloned from RM_OcularJelly (src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionBulloos.xml) with bodySize and every lifeStage drawSize at 1/3. Two whole-body graphics as random pool members (base + alternateGraphics), NOT the Zhool's bell+tentacle part rig.
Art (kept, NOT purged on enact; sheet columns B and C):
- B = arteval_RM_OcularJelly_r2 (1024 canvas -> shrink to the shipping rule): south 6ffb05cfa25d, east 8e05041fce97, north d863e0b5c7a5 (/mnt/d/ClaudeWork/rimmandrake/artpipe/_artsrc/arteval_RM_OcularJelly_r2_<facing>/)
- C = arteval_RM_OcularJelly_r1 (256): south a4d5fae92c25, east 0988a3a89156, north 8a31afe57370 (/mnt/d/ClaudeWork/rimmandrake/artpipe/_artsrc/arteval_RM_OcularJelly_r1_<facing>/)
Install with art.py install --owner-said (his words above). Biome spawn wiring: same pawnKinds entry pattern as the Zhool. No worldgen.
Evidence: Transient/biome_ffar/owner_escalations_contagion_sheet_2026-10-24.decisions.json; /mnt/d/ClaudeWork/rimmandrake/enact_contagion/srcmap.json.
