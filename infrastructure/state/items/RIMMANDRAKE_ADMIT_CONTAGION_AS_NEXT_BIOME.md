# RIMMANDRAKE_ADMIT_CONTAGION_AS_NEXT_BIOME

## spec

The owner, 2026-11-15 ~05:40 PST (typed on his phone; "modest" corrected to "mod set"):
"If the current mod set isn't enough to keep the pipeline busy then pick the next most mature biome mod to add."

BENCH measured the pipeline at 05:43 PST.
- The two maturation dispatch slots were full: the EK in-game driver and the GSS blind judge.
- FlowWorks and Pyrelands were waiting, and Graffiti was parked.
- The Designer lane was idle, so there was room for offline Designer work.

The ranking is in `D:\ClaudeWork\rimmandrake\conductor\next_biome_mod_20261115.md`. It puts Contagion first, a clear lead over Cauldron, LeaningScrub, GelatinousSlime and Stillsand:
- review clean 87%
- the only mechanics item at L1
- 16 testq jobs done, 0 FAIL rows
- selftests green

This item is Contagion's entry into the Maturation Pipeline and its first-touch Designer item:
- the stage record goes from intake to designer, by the owner's words (`maturation.py advance --owner-said`)
- `designer_stage.py init design/concepts/Contagion --mod Contagion --item RIMMANDRAKE_ADMIT_CONTAGION_AS_NEXT_BIOME`
- `role_launch.py run-now --role Designer --concept design/concepts/Contagion`

What the Designer works from:
- the mod at `src/RimMandrake/Contagion` (RM_Contagion biome; Burn/Bloom weather, the Coalescence)
- its built items (CONTAGION_RULED_CONTENT_1, CONTAGION_MECHANICS_BUILD_1 and the CONTAGION_* fixes)

## the route

`maturation.py` clause `intake_closed` now passes when the request carries the owner's words. Before, the only way through was a walk.
The selftest `selftest_maturation.py` was watched failing first.
