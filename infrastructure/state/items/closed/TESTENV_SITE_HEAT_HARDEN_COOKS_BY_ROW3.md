# TESTENV_SITE_HEAT_HARDEN_COOKS_BY_ROW3

Filed by BENCH 2026-10-15 (live round 5, `Transient/bench_live_20261015_r5/SITTING.md`). Evidence:
`Transient/bench_live_20261015_r5/live/pyre/pyre_p3.log`, `pyre_p3b.log`, `pawnget_95731.json` (Heatstroke 0.651),
`hs_at_reload.json` (0.0096 at reload). The fresh Pyrelands site r6 (tile 5) runs 56.7 C outdoors and r7 58.3 C. Vanilla
`HediffGiver_Heat` builds Heatstroke until the colonists are downed inside `scorchfruit_spoils_fast` (a fruit-rot row that waits
4.5 days in half-day steps). The row was restarted twice and never scored, which blocks pilot criterion 3.

## spec

Keep the support colonists on their feet without touching the subject. The site and the sealed spoil room stay at the
site's own heat: nothing is cooled.

## built (2026-10-15, offline)

- `src/RimMandrake/Utils/modcheck/testenv_guards.py` has three helpers:
  - `heatstroke_gain()` is vanilla's formula (curve, 6.45e-5, 0.000375 floor, 60-tick interval).
  - `heat_steps()` splits a wait so no colonist carries more than `HEAT_CHUNK_TICKS` (6000) of exposure.
  - `clear_heatstroke()` removes only the vanilla `Heatstroke` hediff from living humanlike player pawns. It records the
    severity it removed, before removing it.
- `src/RimMandrake/Pyrelands/validation.py`:
  - `_comp` runs one guard pass at the start of each row.
  - `_wait` splits any wait inside a guarded row into 6000-tick steps, with a guard pass between steps.
  - `HEAT_GUARD_EXEMPT = NEEDS_ROWS + ("furnacebeast_warmth",)`: these rows read a colonist's Food or felt temperature, and the
    owner's 2026-10-13 card allows protection only in rows that are not about health, needs, damage or death.
  - Every guard pass is a `[pyre-note] heat guard` line, and `_GEN["heat_guard"]` keeps the list.
- Offline checks, all green:
  - `selftest_testenv_guards.py`: one chunk at 65 C stays below moderate (0.20). The can-fail check: an unguarded half day
    at 56.7 C reaches 0.62 or more.
  - `selftest_pyrelands_site.py` `test_heat_guard_2026_10_15`: the guarded row runs 15 x 6000 ticks with 16 passes and a
    peak below 0.20. The exempt row is never split or guarded, and the same wait there downs the colonist.

## proof (next live round, bridge held, game up on the pyrelands / ratchet_pilot tier)

```
cd /mnt/d/Luke/dev/_rmscratch/<round clone>   # a clone byte-identical to HEAD
timeout 240 python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --fingerprint 417df172fdb5 --tag r6 --reload-only --tile 5 --work "D:\Luke\dev\_rmscratch\<round>\sites" 2>&1 | tr -d '\r' | tail -1
timeout 1800 python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --chains scorchfruit_fire_born,scorchfruit_produces,scorchfruit_spoils,firehawk --no-record --out "D:\Luke\dev\_rmscratch\<round>\Transient\pyre_heat_guard.json" 2>&1 | tr -d '\r' | grep -E "^\[pyre\]|heat guard|GOVERNOR_STOP"
```

Bar:
- `scorchfruit_spoils_fast` is scored: PASS, or FAIL on rot. It is not `RESTART (damage to the test)`.
- No `GOVERNOR_STOP ... downed`.
- Every `heat guard` note shows a cleared severity below 0.20.
- `firehawk_carries_ember` is not restarted.
- `scorchfruit_produces` (exempt) shows no heat-guard note.

If the r6 fixture no longer loads, build a fresh site with `northstar_site.py --site 1` and use the same chains.
