# TESTENV_CONTROL_NOISE_HARDEN_SPIDER_AT_ARM

Filed by BENCH 2026-10-15 (r6). Evidence: `Transient/bench_live_20261015_r6/live/gss/gss_fogguard_1b_spider_preflight.log`,
`gss_fogguard_1c_structure_preflight.log` and `gss_fogguard_3a_structure_preflight.log`.

Three of six GSS `proof_all` attempts aborted in preflight:
- Attempt 1b: a hostile Megaspider stopped the advance (GovernorStop hostile_arrival after 60 of 600 ticks).
- Attempts 1c and 3a: a dormant Hive threat_structure was present at arm.

## cause

- `proof_all.run` runs preflight as P1, P2, then p2c_control_noise, then P3.
- p2c saves, loads and advances 600 governed ticks (`B.ticks(600)`, safe_advance) to measure the list's own error noise.
- The non-colonist and hostile-structure sweep only ran in P3, after that advance.
- So any map-gen hostile stopped the very first governed advance. Class: SITE/HARNESS.

## guard (2026-10-15, offline)

- The sweep moved into `proof_all.calm_map()`: disarm the fog triggers, destroy hostile buildings, `destroy_bulk
  nonColonists`, then unfog the whole map (see TESTENV_FOGGED_MECH_HARDEN_WOKE_ON_REVEAL).
- p2c calls it BEFORE the control save and its 600 ticks, and records `res.control_noise_calm`. P3 calls it again.
- A map that will not calm FAILs `P2c_control_save_load` SITE and never advances the clock. The preflight then aborts with
  the reason instead of a GovernorStop.
- What the control measures is unchanged: the list's own save/load and tick noise, on the map the session will run on.
- That map has no hives or wild hostiles from P3 on anyway, so a control taken on the swept map is the faithful one. The
  only difference is that hive tick errors it no longer sees cannot recur later in the session either.

## offline check (can go red)

`selftest_proof_all.py` 5d:
- p2c's order is `destroy_bulk` < unfog < `save_game` < `ticks:600`.
- A calm map leaves no P2c row.
- A map with a hostile left FAILs P2c and never ticks.

## proof (next live round, same runs as TESTENV_FOGGED_MECH_HARDEN_WOKE_ON_REVEAL)

```
timeout 1200 python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --no-shots 2>&1 | tr -d '\r' | tee "D:\Luke\dev\_rmscratch\<round>\gss_fogguard2_<n>.log" | grep -E "P2c_|P3_|ABORTED|NOT PASS|GOVERNOR_STOP"
```
Run it on 3 or more fresh quicktest maps. Expect:
- No preflight abort on a GovernorStop.
- `res.control_noise_calm.calm` true, with `nonColonistsDestroyed` and `hostileBuildingsDestroyed` recorded.
- Over 3 maps, more than one map-gen hostile swept before p2c, with the run going on.

## live proof r8 (BENCH 2026-10-15, HEAD 22b596181b): PASS

Same runs as TESTENV_FLESHBEAST_HARDEN_FREED_BY_UNFOG (`Transient/bench_live_20261015_r8/SITTING.md` §2). 3 of 3 attempts, no
preflight abort (r7: 5 of 8 aborted). `control_noise_calm.calm` true on all; nonColonistsDestroyed 16 / 15 / 22,
hostileBuildingsDestroyed GlowPod + Hive (map 1), plus 10 unfog-freed hostiles swept before the control save. 110/110 each.
