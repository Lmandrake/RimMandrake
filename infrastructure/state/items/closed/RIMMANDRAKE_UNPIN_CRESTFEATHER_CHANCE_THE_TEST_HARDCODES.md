## spec
`src/RimMandrake/Pyrelands/selftest_pyrelands_firehawk_crestfeather.py` (T_FH_CRESTFEATHER, a decider of bar
`inv_firehawk_hunt_rewards`) pins the butcher-trophy chance: `CHANCE = 0.35`, and line ~99 fails unless the race XML says
exactly 0.35. A tuning change would turn a bar's decider red with nothing broken. Under the owner's 2026-11-16 ruling (bars
never pin tuning numbers, yields or asset counts) and the Conductor's rule that a test pinning a tuning value is the wrong
side, the test should read the chance from the mod and check only its shape (present, 0 < chance < 1). The live half
(`firehawk_rewards_live.py` firehawk_crestfeather_yield) should likewise compare the measured yield to the chance read from
the def, not to 0.35; the coverage leaf `firehawk_hunt_rewards`' oracle text says "the built 35%", which is the same pin in prose.
Found by RIMMANDRAKE_LOCK_PYRELANDS_TWO_LEAVES_THE_TABLE_MAKER_REFUSES (2026-11-16); not fixed there (out of its brief).

## Acceptance test
`! grep -qE '^CHANCE = 0\.35' src/RimMandrake/Pyrelands/selftest_pyrelands_firehawk_crestfeather.py && python3 src/RimMandrake/Pyrelands/selftest_pyrelands_firehawk_crestfeather.py`
exits 0; and with the race XML's trophy `<chance>` edited in a scratch copy to 0.2 the test still passes, to 0 or 1.5 it
fails. Watched fail 2026-11-16: the grep finds the pin.

## refs
file: src/RimMandrake/Pyrelands/selftest_pyrelands_firehawk_crestfeather.py
file: src/RimMandrake/Pyrelands/firehawk_rewards_live.py
