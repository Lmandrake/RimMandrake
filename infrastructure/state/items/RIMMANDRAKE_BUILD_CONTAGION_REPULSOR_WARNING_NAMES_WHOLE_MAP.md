## spec
The Repulsor's whole-map warning is approved (record.json `d_efa_q04`) but not built: `CompCloudRepulsor.cs` has no
warning or confirm text (grep, 2026-11-16). Build it: when a Repulsor is powered on the Contagion, one warning that names
the whole map is shown before warmup begins. Owed by Contagion coverage gap g5 (`rm-coverage-judge-1794821839`); the
record's inventory row is `repulsor_warning`, and `sc_repulsor_warns_and_clears` asserts this build in its start.

## verify
The acceptance test below passes on the deployed DLL, and the scene's live arm is recorded (UNRUN until Stage 6).

## criteria
Acceptance test: a fake-game selftest powering CompCloudRepulsor on a Contagion map reads exactly one warning naming the
whole map before warmup ticks start, and none on an off-biome map: 2 passes. Drafted at filing and not yet runnable; the
building run writes it first and watches it fail on the base (no warning exists).
Live: scene `sc_repulsor_warns_and_clears` (design/concepts/Contagion/scenes.json).
