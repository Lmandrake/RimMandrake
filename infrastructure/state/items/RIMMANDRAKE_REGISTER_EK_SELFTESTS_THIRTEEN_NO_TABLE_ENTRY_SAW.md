## spec
13 of 22 on-disk `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback*.py` suites are named by no command in `design/concepts/ExplosiveKnockback/version/test_table.json` (measured 2026-11-18): barrage_p99, blind_cycle1, gas_into_pit, goods_obstacles, journal_jolt, landing_job_search, map, pit_fetch, runner_advance, stage6_visit1, stage6_visit2, storeroom_bomb_pit, walk_raid. The certificate, the blind brief and any table-driven harness never see them; walk_raid already kills PF_V_FRAME_OVER_LOOSE and PF_V_FRAME_ROW_ALWAYS_PASS (RIMMANDRAKE_LIST_WALK_SUITE_IN_HARNESS_MUTANTS_SURVIVED). For each: register it (kind offline, file, reads, command, the bar it supports or decides) or, if it tests pipeline machinery rather than the mod (blind_cycle1, stage6_visit*, runner_advance look like that), list it under a top-level `unlisted_suites` map with a one-line why. Then `maturation.py certificate ExplosiveKnockback --run`. Placing a test as a DECIDER of a bar is the Designer's call; `supports` is enough here. The sibling (validation.py --selftest) was registered by the sync run as T_WALK_FRAME_JUDGE_OFFLINE.

## verify
```
python3 -c "import json,glob,os,sys; t=json.load(open('design/concepts/ExplosiveKnockback/version/test_table.json')); c=' '.join(json.dumps(v.get('command')) for v in t['tests'].values()); x=t.get('unlisted_suites') or {}; m=[os.path.basename(p) for p in sorted(glob.glob('src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback*.py')) if os.path.basename(p) not in c and not (isinstance(x.get(os.path.basename(p)),str) and x[os.path.basename(p)].strip())]; print(len(m),'unlisted:',m); sys.exit(1 if m else 0)"
```
Pass: rc 0, prints `0 unlisted: []`. Watched failing 2026-11-18 on fdd6893e09 + the sync run's EK table: rc 1, 13 unlisted.

## criteria
Every on-disk EK selftest is either a test-table entry or in unlisted_suites with a why; certificate --run OK.
