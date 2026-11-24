# RIMMANDRAKE_FIX_STEVE_TWO_LANE_READING_STEVE_ONE_INSTALL

## spec

`infrastructure/stevedesktop/worker.py` `Attempt.mods_dir` answers Steve1's Steam install for both games. `companion_dir` is
its sibling. So a job on Steve2 checked and installed the companion in Steve1's folder, said FRESH, and the game loaded the
old one: J20261124T001426Z-9581b9 (worker.log: FRESH 9117e7c4efd5 under `/mnt/d/SteamLibrary`; Steve2's Player.log: `[JawaBench]
ready: 435 tools, build d5e3400df232`; the proof read "Tool 'jawa/scene_slice' not found"). The attested mod hashes of each
Steve2 result were Steve1's too.

## verify

Seen red on base `c6f60081f3`: `t_steve2_reads_its_own_install`. Expected: exit 0.

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/testq/selftest_testq_steve2.py
```

## criteria

- The acceptance test exits 0.
- A job on Steve2 loads the companion built from its sha (the Player.log line names it).
