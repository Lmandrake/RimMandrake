# RIMMANDRAKE_WIRE_PAWN_KIT_TOOLS_REPLY_FROM_READ_BACK

The remainder of `RIMMANDRAKE_BUILD_STAGE_OPS_READ_BACK_NEVER_ECHO`. Its Builds line names "the pawn kit tools". The core
(`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchStageReadBack.cs`) and the four batch tools were done at
`c1383c825f`; the live proof `src/RimMandrake/bridgetools/prove_stage_ops.py` held 5 of 5 rows on Steve2.

## spec

- Each pawn kit tool that `s.stage` calls replies from a `StageReadBack` that it opens and replies inside its one
  main-thread hop, as `jawa/spawn_pawn` does: `jawa/pawn_gear`, `jawa/pawn_traits`, `jawa/set_pawn_skill`,
  `jawa/pawn_need`, `jawa/pawn_health` (`JawaBenchPawnTools.cs`) and `jawa/set_work_priority` (`JawaBenchJobTools.cs`).
- Each `Got` reads the pawn after the write (the skill level, the trait list, the worn and equipped defs, the need
  level, each hediff and its part, the priority); never the request value.
- The tool's `success` is false when the block's `ok` is false.
- Promises: a row per tool on `design/specs/2026-11-23-bridge-v2/boundary.md` §THE STAGE READ-BACK.

## verify

- Offline: `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_stage_ops.py`, with each kit tool
  added to `WIRING` and one call-site plant per tool that echoes the request (each turns the wiring red).
- Live (UNRUN): a kit row in `prove_stage_ops.py`: a pawn given a skill, a trait, gear and an injury reads each back,
  and two builds give equal digests. Also stage a reservation in row R4 (not staged at `4da3d6a7e6`).

## criteria

- The offline selftest is green and each new plant was seen red.
- The live row ran on a game with this build deployed (its srcHash on the output), or it is recorded UNRUN with its command.
