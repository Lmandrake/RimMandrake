# LIQUID_BODY_FLUID_IDENTITY_1 — Fluid identity per liquid body (retire per-map ActiveFluid); the merge rule

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
[F]: each liquid body carries its own FluidDef; `ActiveFluid` per map retires (save migration). Two pits fed by different sluices hold different fluids.
Merge rule when a channel joins two bodies of different fluid: **DEFAULT — they do not mix; the channel stays dry between them until one body is drained** (owner question on mixing may change this).

## verify
Bridge: water body and oil body side by side; a channel dug between them follows the merge rule; save/load keeps each body's fluid.

## criteria
`fill_fluid_distinct` becomes reachable.

## depends
**`FLOWWORKS_CHANNEL_OSCILLATION_1`** (flow must fill in every direction first).

## northstar
State components: fluid per body before/after joining; the old "unconditional BLOCKED (one ActiveFluid per map)" row is promoted to a real check.
