# WARSCAR_CHOTRIX_BUILD_1 work log 2026-10-03 (FOUNDRY)
Scope: Scarlands folder only; CreatureBehaviors untouched (another agent builds FOOTPRINT_TRACK_GRID_1 there).
## Searched first
- src/design: no chotrix def; spec lives in design/Jawa/worldbuilding/biomes/warscar_bedazzle_cast_2026-09-30.md section 5 + the item.
- artpipe: RM_Chotrix_{south,east,north} DONE (done/, _artsrc/), palette kept by owner card -> copy into Scarlands Textures (wired). No art exists for lacquer item or lacquered cloak.
- RM_Tetchik/RM_Chatrak: no defs in src (grep 0) -> prey list is DATA (defName list on a DefModExtension), not hard-wired.
- Geiger choir (WARSCAR_GEIGER_CHOIR_1) has no code -> chotrix exposes a static registry + silence radius for it to read.
## Choices
- Invisibility: own hediff RM_ChotrixCloak with stock HediffCompProperties_Invisibility (same as RM_AquaticAmbushInvisibility); not referencing CreatureBehaviors defs (separate mod).
- Strike reveal: Harmony postfix on Verb_MeleeAttack.TryCastShot -> comp reveals for revealTicks (240) then re-cloaks.
- predator=false on the race so vanilla hunting (which ignores the lone-prey gate) is off; own JobGiver_ChotrixHunt does the hunting, JobGiver_ChotrixFlee flees when hurt after biting.
- Lone gate: pawn prey rejected if any other humanlike/same-faction pawn within 12 cells; animal prey rejected if another of its def within 8 cells. Pawns only at night (hour <6 or >=20). Hunts when food < 70%.
- Cloak lacquer: item RM_CloakLacquer (butcher product, leatherDef-like via butcherProducts on race). Lacquered cloak = distinct apparel RM_Apparel_LacquerCloak crafted at tailor benches from fabric + lacquer (costList) -> "permanent" because it is its own def with a stateless comp; the hediff is saved with the pawn so it persists through save/load. Not timed (owner ruling).
- Cloak condition: still (not Moving) and unseen (no hostile awake pawn with line of sight within lacquerSeenRadius, default 15). Re-evaluated every 20 ticks.
- Settings: chotrixEnabled, chotrixPerMap (genstep 1-2), chotrixRevealSeconds, lacquerCloakEnabled, lacquerSeenRadius.
- Spawn: genstep RM_ChotrixOnMap (1-2 per map).
## NOT built / blocked
- Track prints, dragged-kill marks: wait FOOTPRINT_TRACK_GRID_1 (grid records invisible pawns itself per its spec); tetchik silence ring: waits WARSCAR_GEIGER_CHOIR_1. Both blocked via rimflow block.
- Art for lacquer item and lacquered cloak: vanilla stand-in textures; owed.
- Filed+blocked child WARSCAR_CHOTRIX_SIGNS_1 (prints, drag marks, silence ring). Built OK via winbuild; validation.py STATIC PASS; live criteria UNMEASURED (not deployed). Parent left in doing pending live round.
- Filed+blocked child WARSCAR_CHOTRIX_SIGNS_1 (prints, drag marks, silence ring). Built OK via winbuild; validation.py STATIC PASS; live criteria UNMEASURED (not deployed). Parent left in doing pending live round.
