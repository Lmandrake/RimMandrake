# Test-environment hardening, round 2 (BENCH builder, 2026-10-15)

This follows `testenv_hardening.md` (commit 867c1da25e, `testenv_guards.py`). The evidence is in
`Transient/bench_live_20261015_r6/`. Each item's full write-up, offline checks and exact live proof command are in
`infrastructure/state/items/<ID>.md`. No row's measurement was changed. Nothing was deployed and the bridge was not used.

## 1. TESTENV_FOGGED_MECH_HARDEN_WOKE_ON_REVEAL (residual on r6 map 3)

**Cause.** The reveal came from a later fog-blocker removal. It was not a pawn's sight, and not a trigger type the guard
missed: P3 had read back zero triggers and zero hostiles.
- In 1.6 the ThreatBig "Area revealed" letter has one sender, `FogGrid.NotifyAreaRevealed`, reached only through
  `FloodUnfogAdjacent(sendLetters)`.
- Mid-run, that path is `Building.DeSpawn` -> `Notify_FogBlockerRemoved`. A site clear (the matrix board's
  `destroy_batch All`) removed rock beside a fogged pocket, the flood woke what was in it, and it lettered on the mechs.
- The 3 mechs had map-gen ids, but they were in neither P3's spawned sweep nor the 15808 vitals census. So they were held
  unspawned. Where they were held is presumed, unproven.

**Guard.** `testenv_guards.clear_map_fog()` is the last step of the new `proof_all.calm_map()`.
- It runs `set_fog unfogAll` and reads back `foggedCellsNow` == 0.
- It is refused while any hostile is listed, because an unfog wakes what it uncovers.
- P3 FAILs SITE unless it is verified.

**Offline checks.** `selftest_testenv_guards` `test_map_fog` (a fog-pocket model that goes red without the guard) and
`selftest_proof_all` 5c.

## 2. TESTENV_STORM_FIRES_HARDEN_DECOY_BURN

**Cause.** The fulgurite chain's teardown only UNLOCKED DryThunderstorm. Unlocking leaves it the current weather, and even a
transition to Clear keeps `lastWeather` lightning ticking for 4000 ticks. Its 177 fires became the burn line's newest sample
instead of burn B.

**Guard.**
- `testenv_guards.calm_sky()` locks Clear, transitions to Clear a second time (so lastWeather is Clear), extinguishes the
  map, runs one 60-tick settle and reads back zero Fire.
- `herd_follows_drive` calls it before burn A. A sky that will not calm is UNMEASURED SITE. The lock is released in a
  `finally`.
- Every weather teardown is now unlock + Clear x2.

**Offline checks.** `selftest_testenv_guards` `test_calm_sky` (a WeatherManager model: the old teardown and a single
transition still light fires) and `test_pyrelands_storm_wiring`. The wiring check lives in Utils because
`Pyrelands/selftest_pyrelands_site.py` is inside the Pyrelands mod_hash.

## 3. TESTENV_CONTROL_NOISE_HARDEN_SPIDER_AT_ARM

**Cause.** `p2c_control_noise` advances 600 governed ticks before P3's sweep, so a map-gen Megaspider or a dormant hive
stopped the first advance.

**Guard.** `proof_all.calm_map()` (triggers, hostile buildings, non-colonists, map unfog) now runs in p2c before the control
save, and again in P3.
- A map that will not calm FAILs P2c SITE without ticking.
- The control still measures the list's own save/load and tick noise on the session's map. That map is swept from P3 on
  anyway.

**Offline check.** `selftest_proof_all` 5d.

## 4. TESTENV_SWEPT_BRUISE_HARDEN_OWN_HAZARD

**Cause.** FlowWorks' own designed river hazard bruises the swept pawn (owner card 2, `bruiseChancePerStep` 0.15), and the
vitals governor stopped the wait as damage.

**Guard, and why.** The hazard is the mod under test, so switching it off (bruise chance 0) or protecting the pawns would
change what the row runs, and would hide a real hazard defect. Instead the row DECLARES the expected disturbance:
- `clockgate.expected_disturbance()` plus `testenv_guards.expected_hurt(staged, "Bruise")`.
- Only a 'hurt' trigger on the row's own staged throwaways whose newest hediff is Bruise is resumed past, and it is noted.
- Another pawn, another hediff, downed, dead or a hostile still stops the clock.
- The setting is never touched.
- `governor.RowGovernor` is untouched. It keeps its own `RowContract(expected=...)`.

**Offline checks.**
- `selftest_clockgate` `test_expected_disturbance` (five can-fail cases).
- `selftest_testenv_guards` `test_expected_hurt`.
- `FlowWorks/northstar/selftest_extensions` runs the real swept chain. It was mutation-checked red.

## Selftests, CLEAN status, commits

- `run_selftests --only` on 11 tests is GREEN 11/11: testenv_guards, clockgate, governor, quiet_site, watch,
  suite_corrections, proof_all, pyrelands_site, extensions, proof_hose and flowworks_northstar.
- All 9 changed files had a full-file review and are marked CLEAN at the code commit. The commit shas are in the commit log
  and the ledger notes.
- The other builder's files were not touched: RM_CliffMask.cs, the northstar_driver lint snapshot, art/selftest_subject and
  rimflow reader_invariant.
