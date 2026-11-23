# RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** `JawaBenchSceneKernelCore.cs` (pure: the plan parser, the phase order, the closed list of act ops) and
  `JawaBenchSceneKernel.cs` (the tools `jawa/run_plan` and `jawa/run_status`, TEST profile only). The phases admit,
  arm, act and run, settle, leave on the present plot grid, with a small set of stage ops only (spawn a thing, spawn a
  pawn, set a cell's terrain, by the bodies of the present tools) and aliases. The receipt facts. The minimum put-back:
  the debt file written before the first change and repaid at the next start. `src/RimMandrake/Utils/scene.py run
  <plan.json>` drives it and calls the judge. First scene as data: Explosive Knockback's spared carrier (worked
  example 1 of `02_needs_design.md`).
- **Needs:** the slice, the judge, the game watcher and the life-cycle ticket; the sibling's receipt function. Runs in bootstrap mode.

Depends on: `RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED`, `RIMMANDRAKE_BUILD_SCENE_JUDGE_OUTSIDE_GAME_FROM_KEPT_TRACE`, `RIMMANDRAKE_BUILD_GAME_WATCHER_NAMES_THE_BROKEN_STATE`, `RIMMANDRAKE_HARDEN_RUN_LIFE_CYCLE_KILL_CANCEL_THROWN_TICK`, `RIMMANDRAKE_BUILD_BRIDGE_RECEIPT_CALM_AND_TAP_EITHER_WAY`.

## verify

Acceptance test (offline), 17 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_scene_kernel_core.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_scene_kernel_core.py`, 17 checks: each phase's
  refusal by name (5); an act step that cannot be delivered is an apparatus fact, not a verdict (1); a plan whose
  build hash differs from the loaded one is refused in admit, before any change (1); an alias bound twice is refused
  (1); the settle reconciliation flags a cast thing that vanished with no event (1), flags an actor that is still
  there with a health that differs from the trace (1), and passes a clean run (1); a run over the tick threshold
  returns a handle and a later status (2); unknown plan keys are refused (1); the game is left paused in every ending
  (1); the kernel names no type of a PROOF build (1); a receipt made with no certificate reads BOOTSTRAP (1).

- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_run_plan_spared_carrier.py`, 4 rows: the data
  scene gives SUCCESS on the release build; the existing `[RMTest]` pair gives the same result on the same save; the
  whole run is one bridge call and one status read; a red run under a compiled mutant ("the carried pawn is not
  spared") gives MOD FAILURE on the named condition. That red run is on another build, so the scene's "shown both
  ways" record reads PROVISIONAL until the mutant ticket gives a red run on the release DLL.

Live state at filing: UNRUN: its script `prove_run_plan_spared_carrier.py` does not exist yet.

## criteria

- The acceptance test prints 17 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red:** admit that checks the build after staging; a settle that skips the health
  reconciliation; a leave that does not repay the debt file after a thrown tick.
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
