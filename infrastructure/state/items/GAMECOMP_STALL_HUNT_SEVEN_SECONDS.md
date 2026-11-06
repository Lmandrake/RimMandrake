## spec
Name the GameComponent behind one-off stalls on the 550 list (Rot save): gameComp 6.76 s at tg 7501 and 2.88 s at tg 5821 (18 ticks after load) in the TPS record worst[]. Build a `jawa/game_comp_timing` twin of `jawa/map_comp_timing`, catch the next one, rank by owner mod.

## built
- Tool: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchGameCompTiming.cs` (modes run|arm|read|disarm; patches every GameComponent subclass so it survives a reload), pure core `JawaBenchCompTimingCore.cs`, C# units `T_CompTiming*` in `selftest_tps_record.py`.
- Driver and verdict: `src/RimMandrake/Utils/perf/game_comp_stall_hunt.py` (refuses an unnamed stall and an unmapped owner mod), selftest `selftest_game_comp_stall_hunt.py`.
- Live proofs: `infrastructure/state/live_proofs/GAMECOMP_STALL_HUNT_SEVEN_SECONDS.txt`. A1 passed live 2026-11-04 at a16039c753; A2 (Rot save, 550 list) still owed.

## state
2026-11-05: the build pin a16039c753 went stale when other items edited the two tool files (0a3afbe712 BRIDGE_HOOKS_HARDEN_REENTRANT_AND_FAULTY, 52203cfa0a BRIDGE_FLOATMENU_FIX_DEBUG_PICKER_UNREADABLE). The proof was rerun green at a62834e844 (both selftests PASS, 59 C# units with 0 failed, BridgeTools builds with 0 errors) and the item was re-pinned there so the A2 live round can run.
