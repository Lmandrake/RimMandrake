# SCORCH_FRUIT_FIX_ROLLS_BEFORE_THE_ASHES (MOD, Pyrelands / FireEcologyHook.cs)

Bars `scorch_fruit_seed` (toggle floor) and `pyre_scorchfruit_fire_born` FAIL on every run since 2026-10-01: 0 ScorchFruit in a
burned, fully grassed 24x24 cohort after 11,600 ticks (2026-10-12: rect 0 / map 9; `Transient/bench_live_20261012/pyre_ns.log`;
history in `Transient/pyrelands_live_iteration_2026-10-01.md` runs 4-7).

Mechanism (read in `src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs`, `Patch_FireTick_AshAndScorchFruit.Postfix`):
each Fire takes its ONE roll (`MarkFireRolled`) on its FIRST tick-interval, and the fruit may only spawn on a 3x3 neighbour
that is standable AND has no plant. At that moment the grass the fire is about to burn still stands in its own cell and
its neighbours, so the roll is spent with no legal spot. Fruit only appears where a neighbour is already bare: a re-burned
pad (the 12 fruit on the LADDER pad after its 3-cycle burn, 2026-10-01) or the plant-stripped firebreak ring.

The suite ignites every cell of the cohort at once (`map_fire` over the rect), which is the worst case; a natural spreading
front sometimes has a burned parent cell beside the new fire. Discriminator before the fix: ignite a 2x2 seed in the
grassed cohort and let it spread; if fruit still ~0, the MOD defect is confirmed for natural fires too.

Fix direction (FOUNDRY): roll when the fire's cell is burned out (e.g. on the fire's despawn / when its plant is gone),
or let the burning cell itself qualify once its plant is destroyed, keeping "one roll per burned cell" (owner 2026-09-16,
"perhaps one in twenty squares").

Triage: `Transient/pyre_site_2026-10-12.md`.
