# Selftest triage 2026-10-06

| test | verdict |
|---|---|
| FlowWorks/Tools/selftest_liquid_looks.py | stale expectation: tar moved to the Solid terrain shader in 13e7f8c82; test now asserts Solid + tint (0.24,0.24,0.24) + wake 0 |
| FlowWorks/northstar/selftest_flowworks_northstar.py | stale: (a) flowworks tier gained GSS in 169e004f6; (b) site_spec.SETTINGS lacked 5 new C# fields (ladderRaiseLowerEnabled, liquidBubblesEnabled, liquidBubbleDensity, liquidSeeThroughEnabled, pitWalkNormalEnabled) - added with the C# defaults, toggle count 83 -> 87 |
| Utils/selftest_gimmesomeslack.py | passes alone (738/738, exit 0) and in the full sweep; earlier failure was load-dependent flake |
| bridgetools/selftest_tool_metadata.py | environmental: deployed JawaBench DLL lacks 10 tools declared in source (JAWABENCH_DLL_STALE_REBUILD_1); not touched |
| rimflow/selftest_built.py | stale: real ledger now legitimately holds "implemented" events, so the guard's blanket event clause false-positived; now checks only the test's own IID |
| UtinniPatches/selftest_utinnipatches_dump.py | environmental: load-14 dump predates MINDSTONE_MATRIX (721e81866) - RUT_MindstoneMatrix + 2 recipes absent from the dump; needs a dump refresh from a live game, not a test edit |

Also seen once under parallel load, passes alone: Utils/art/selftest_placeholder_detect.py (flake).
