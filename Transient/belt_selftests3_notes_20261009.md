# belt selftests 3 notes 2026-10-09

Fresh clone of origin/main (SSH), `run_selftests.py`: PASS 343/347, FAIL 1, UNMEASURED 1, CRASH 0, SKIPPED 2 (wall 297 s).
Raw output: `Transient/belt_selftests3_20261009.txt`.

## Reds
- FAIL `src/RimMandrake/rimflow/selftest_items_glob_live.py`: `LIQUID_UNIT_CONTRACT_ROUNDTRIP_1.md` was in both `items/` and `items/closed/` (byte-identical) though ledger state is done. Cause: a pushed commit (MovingDunes 47353706b / belt hygiene) put the closed copy in place while the live copy stayed. FIXED by deleting the live duplicate; selftest 3/3.
- UNMEASURED `src/RimMandrake/bridgetools/selftest_tool_metadata.py`: needs the Windows-built `JawaBench.BridgeTools.dll` (`python.exe bridgetools/build.py --gm`). Not caused by pushed work; not run (no bridge/build tonight).
- SKIPPED by tier (deployed): `modcheck/selftest_deployed_floor.py`, `selftest_deployed_biome_refs.py`.

## Not red on fresh origin
`selftest_ledger_lint.py` and `selftest_memwatch.py` PASS on origin/main; their reds in the shared clone were lag/pollution only.
