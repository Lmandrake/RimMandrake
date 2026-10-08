# BELT contagion2 2026-10-08

## Steps
- started
- read mechanism (Building_RM_Coalescence.cs, RM_GameCondition_ContagionBurn.cs, RM_SkyKernel.PressureActive, validation.py, selftest fake)
- burn_off_means_no_harm: HARNESS ordering. Fresh colonist was spawned and walked 200 ticks under the forced Burn with burnEnabled still ON, then the toggle went off. Live dose 0.0117 < one pass (0.02) = one pre-toggle pass, decayed. Mod gates pressure on burnEnabled (PressureActive). Fix: toggle off BEFORE spawning/exposing.
- coalescence_absorbs_and_grows_a_stage: HARNESS timing. Absorb runs per 250-tick hash pass; Unfinished (impaired Moving, Walk urgency) need a pass to get a Goto and a later pass to be eaten. Live: mass 0->5 in 600 ticks (off-arm kid + 4 of 6), both stragglers (and a pre-existing wild one) parked INSIDE the absorb ring (172,123)/(172,127) awaiting the next pass. Fix: poll per pass until the kids are gone (cap 10 passes, < passiveGrowthTicks 6000 so passive growth cannot mask a no-absorb bug).
- fake-bridge: order_pawn now runs the clock for waitTicks; Absorb models ring + approach, new break slow_walkers (expected []). Against the OLD harness the fake now reproduces BOTH live failures (healthy 57/59, slow_walkers reds coalescence_absorbs); new harness 59/59, 45/45 breaks.
- no C# change: mod behaviour is correct for both (PressureActive gates on burnEnabled; Absorb eats anything in the ring next pass) -> no winbuild needed
- run_selftests: 341/341 PASS
