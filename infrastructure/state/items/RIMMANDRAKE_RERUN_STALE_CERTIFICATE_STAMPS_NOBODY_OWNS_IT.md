## spec
ExplosiveKnockback 0.1.0 (Offline build, Stage 3, since its visit-3 road back at 2026-11-16 12:28 PM PST) reads
`wait certificate` in maturation_dispatch.py status: judge_certificate refuses 11 of 44 bars only because their offline
deciders' recorded runs are stamped on an older build (ran_on_this_build), with no red decider. cert_red_decide returns
None for that case ("stale stamps alone are `certificate --run`"), and nothing in the pipeline runs
`python3 src/RimMandrake/rimflow/maturation.py certificate <Mod> --run` (zero tokens): the mod waits for a hand.

Build: the Dispatch step gives a stale-stamps-only certificate wait one zero-token run of `certificate <Mod> --run`
(a detached unit, not inside the 60 s tick), lands the table, and re-reads; a run that leaves reds goes to
cert_red_decide's builder as today. Once per build hash, never a loop.

Acceptance test: none written yet, the launch form (tick-run vs detached unit) is the builder's call; the oracle is
a selftest_maturation_dispatch case where a stale-only certificate row gets exactly one certificate run and a second
tick on the same build gets none. Filed by RIMMANDRAKE_UNSTICK_FIVE_STILL_MODS_TWO_OF_TWELVE_MOVING.
