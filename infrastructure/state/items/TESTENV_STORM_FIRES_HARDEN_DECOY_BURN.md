# TESTENV_STORM_FIRES_HARDEN_DECOY_BURN

Filed by BENCH 2026-10-15 (r6). Evidence: `Transient/bench_live_20261015_r6/live/pyre/pyre_p4.log` and `pyre_p4b.log`. The
r6 p4 piece ran `burrowers, fulgurite, ullai_and_giant, sand_shovel, lightning_breaker` on one fixture reload.

What happened:
- `herd_follows_two_day_old_burn` read UNMEASURED because the burn line's newest sample was (184,135), with 177 cells burning
  centred on (176,141). Burn B was at (220,100).
- The same row alone on a fresh reload (p4b) PASSed.

## cause (rimsage 1.6 source)

- The `fulgurite` chain locks DryThunderstorm. Its teardown only UNLOCKED the weather and put the fires out.
- `jawa/weather_set unlock` ends the forcing condition but leaves DryThunderstorm as the CURRENT weather.
- Even a transition to Clear keeps `WeatherManager.lastWeather` ticking for `TransitionTicks` 4000 at a falling weight. Its
  lightning is included (`WeatherManagerTick`: `lastWeather.Worker.WeatherTick(map, 1 - TransitionLerpFactor)`).
- So the storm went on lighting grass through `ullai_and_giant`. Its fires were what the burn line sampled.
- Class: SITE/HARNESS. The burn line read the fires that were really burning; the row was handed a decoy.

## guard (2026-10-15, offline)

- `testenv_guards.calm_sky()` locks Clear, then transitions to Clear a SECOND time, so `lastWeather` is Clear and no storm
  tail ticks. It then extinguishes the whole map, runs one short settle (60 ticks, governed) and reads back the stray Fire
  count.
- `Pyrelands/validation.py` `_calm_sky` runs it at the start of `herd_follows_drive`, before burn A. A sky that will not calm
  is UNMEASURED/SITE, never a decoy read as burn A or B.
- The calm's Clear lock is released in a `finally` at the end of the row, so it never outlives it.
- Every `@_teardown(weather=True)` (fulgurite, fresh_burn_bonus, ashfall chains, cinderfall, blackrain, ambient_ash_drift)
  now unlocks and then transitions to Clear twice, so no chain leaks its weather into the next.
- What the row measures is unchanged. It lights its own burns A and B and reads the burn line. Weather is not its subject,
  and the burn-line setting and the herd giver are untouched.

## offline checks (can go red)

`src/RimMandrake/Utils/modcheck/selftest_testenv_guards.py`:
- `test_calm_sky` is a WeatherManager model. The old teardown (unlock + extinguish) and a single Clear transition both still
  light fires. `calm_sky` lights none. A refused weather call or a fire read back is not verified.
- `test_pyrelands_storm_wiring` loads Pyrelands' `validation.py`. It checks that the herd drive calms before burn A, that 177
  stray fires make the row UNMEASURED SITE, that the lock is released in a finally, and that a weather teardown is
  unlock + Clear x2.
- This check lives in Utils, not in `Pyrelands/selftest_pyrelands_site.py`, because that file is inside the Pyrelands
  mod_hash. Editing it would turn the r6 proofs STALE.

## proof (next live round, bridge held, ratchet_pilot tier, r6 fixture)

Reload the fixture, then run the r6 p4 piece in the same order that failed:
```
timeout 240 python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --fingerprint 417df172fdb5 --tag r6 --reload-only --tile 5 --work "D:\Luke\dev\_rmscratch\bench_live_20261015_r5\sites"
timeout 1200 python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --chains burrowers,fulgurite,ullai_and_giant,sand_shovel,lightning_breaker --no-record --out "D:\Luke\dev\_rmscratch\<round>\pyre_p4.json" 2>&1 | tr -d '\r' | grep -E "^\[pyre\]|sky calmed|GOVERNOR_STOP"
```
Expect:
- `herd_follows_two_day_old_burn` PASS in the same run as fulgurite.
- The "sky calmed" note shows `strayFires` 0.
- No `teardown` FAIL component.
