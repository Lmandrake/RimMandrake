# RIMMANDRAKE_BUILD_FLIGHT_PROBES_STATE_AND_FRAME_NO_PICTURES

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** the probes `pawn.flight.*` and `pawn.anim.*` (the graphic state's name and `texPath` from
  `PawnRenderNode.TryGetAnimationGraphicState`, the animation's name and start tick), the offline audit that every
  frame's texture exists for every facing, the flapping scene of worked example 3 as a file. Takes over the build
  half of `FLYERFRAMES_PROVE_JOINT_SESSION`.
- **Needs:** the run-plan and compiler tickets.

Depends on: `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`, `RIMMANDRAKE_BUILD_SCENE_FILE_COMPILER_AND_LINT_NO_GAME`.

## verify

Acceptance test (offline), 8 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_flight_frames.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_flight_frames.py`, 8 checks on recorded and hand-made
  series: a full flight passes; a skipped state fails; a flip-book that repeats one frame fails; a frame held for the
  wrong number of ticks fails; a landing that keeps a flying picture fails; a bird still in the air at the limit is not
  judged; "no bird took off" is an allowed miss; the asset audit names a missing texture.

- **Live test:** **the owner's act.** The first live run is with him present (`07_for_the_owner.md`, choice 1).

Live state at filing: UNRUN.

## criteria

- The acceptance test prints 8 checks passed and exits 0.
- At least one planted fault per promise was seen red before the ticket closes (the build order names no plant here).
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- The first live run is with the owner present (`07_for_the_owner.md` choice 1). No helper runs it.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
