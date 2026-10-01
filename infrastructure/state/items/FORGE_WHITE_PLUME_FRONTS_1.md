# FORGE_WHITE_PLUME_FRONTS_1 — white plume fronts

Split from `FORGE_GPT_ENRICHMENT_1` §4 (owner-picked). Not built: every mechanical choice below is open, and the
spec gives no numbers.

## spec (from the parent)

Quench steam rolls out from newly crusted vents as moving fronts. They briefly obscure shooters, soak the ground,
and heat exposed pawns faster through **vanilla heatstroke** (`SOLAR_HEAT_EXPOSURE_1`, one kind of heat).
Vapour-adapted creatures move normally inside them. Build: a phase-bound cell front, flecks, a ranged-accuracy
modifier, AI avoidance, and an adapted-species exemption.

## what exists to build on

`RM_GameCondition_ForgeCycle` knows every newly crusted cell (`FrozenCells`, filled in batches through the
freeze phase). Vanilla 1.6 has `GasType.BlindSmoke`. If it is used for the "obscure" half, ranged accuracy and AI
avoidance come from vanilla and no Harmony is needed. That is a suggestion, not a ruling.

## open questions (owner)

1. Obscuring: vanilla blind smoke (cheap, and the AI already avoids it) or a custom front with its own accuracy
   number?
2. Heatstroke inside a front: how much faster than the Forge's ambient heat?
3. "Soak the ground": wet terrain or filth, or FlowWorks water?
4. Which species are "vapour-adapted"? Every pawn with `CompProperties_VaporDrifter`, or a named list?
