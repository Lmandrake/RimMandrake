# RIMMANDRAKE_BUILD_MOD_TRACE_AND_RESET_HOOKS_BY_REFLECTION

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** `src/RimMandrake/_Shared/TestHooks/RMTestHooks.cs` (`RMTrace`, `RMResetAttribute`, `RMDigestAttribute`;
  pass three builds no `RMProbe` plug-in); the kernel's discovery; the "mod says" record type; first use in Explosive Knockback and
  FlowWorks when each next advances.
- **Needs:** the instruments ticket `RIMMANDRAKE_WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH` (pass three moved the block off the held run-plan ticket).

Depends on: `RIMMANDRAKE_WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH` (pass three; it was the held run-plan ticket).

## verify

Acceptance test (offline), 8 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_test_hooks.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_test_hooks.py`, 8 checks: a mod with no hook is
  listed as such; a hook of the wrong shape is a named problem; `Emit` with a null sink allocates nothing; the sink is
  cleared at leave, also after a thrown tick; two mods' hooks do not collide; a hook from a PROOF build is refused
  for an acceptance run; a mod's release DLL with hooks names no type of the companion; **a digest hook is accepted
  only after it was seen to differ between a clean state and a state dirtied on purpose**.

Live test (UNRUN): `python.exe src\RimMandrake\bridgetools\prove_mod_hooks.py` on a TEST-profile game with the companion of this
build, 3 rows; row 3 reads UNMEASURED until a loaded mod has a trace point (the first use, in each mod's next version).

## criteria

- The acceptance test prints 8 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red:** a `Digest` that returns a constant (GPT's case).
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
