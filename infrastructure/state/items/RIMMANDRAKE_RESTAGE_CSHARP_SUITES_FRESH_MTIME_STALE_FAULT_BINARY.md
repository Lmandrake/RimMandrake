## spec
`selftest_explosiveknockback_map.py`, `selftest_explosiveknockback_kernel.py` and `selftest_kineticarms_kernel.py`
stage their C# into a fixed folder under the agent build root (`D:\ClaudeWork\rimmandrake\build\...`) with
`shutil.copy2`, which keeps each source's old mtime, then `dotnet run`, which rebuilds only when a source is newer
than the build output. The map suite plants 30 faults by rewriting the staged `RM_KnockbackPlan.cs` (fresh mtime,
rebuilt) and restores with `copy2` (old mtime): the next run skips the build and runs the binary compiled with the last
planted fault ("downed pawns cannot be switched off"), failing `CASE FAILED settings: throwDowned off changes only
downed changed:` [measured 2026-11-18 ~7:20 PM PST: 8 consecutive FAIL runs on 0117263cc, under PYTHONHASHSEED 0-5
too; the staged file held the shipped line]. The same staleness reaches across clones: a clone with older sources runs
another clone's newer binary. The certificate run at 6:43 PM PST read T_SITUATION_MAP_OFFLINE red for this reason.
Not fixed here: the two Graffiti suites with the same pattern (`selftest_graffiti_weather.py`,
`selftest_graffiti_raid_tag_wall.py`), Graffiti being owner-held.

## verify
Acceptance test: `python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_map.py` run twice in a
row, both exit 0 ("PASS ... 30 of 30 planted faults seen"). Watched FAIL on base 0117263cc (second and later runs
rc 1); green with `shutil.copy` (fresh mtimes) in a throwaway clone.

## criteria
- A staged C# suite always runs a binary built from the bytes it staged.
