# ARENA_SANDBOX_HARDEN_HARNESS_RUNS_ARM_CODE

## spec
arm_sandbox.wrap now sandboxes every arm MODEL launch (RA.CmdModel.spawn), but the loop harness itself still executes
code the arm can rewrite in its clone, unsandboxed, as the same uid (blind GPT review of the arm_sandbox commit, r1
finding 1, 2026-10-30):
- ralph_a_loop.default_precheck: `python3 src/RimMandrake/Utils/run_selftests.py --quick` with cwd = the arm clone
  (clone-controlled run_selftests.py and every selftest it runs);
- ralph_a_loop.default_release: the clone's `src/RimMandrake/rimflow/cli.py bridge release --mine`;
- ralph_a_loop.Loop._final: `./publish` (publish_cmd) with cwd = the clone;
- whatever arena_gate steps execute from the clone (selftests, builds).
A builder can edit any of these to read an answer holder (retired trees, bench/foundry, the D:\ mirror, ClaudeWork) and
write it into its clone; the next build pass reads it. Same for ralph_c / trio / v3 (they reuse these paths).

## criteria
Done when every execution of clone-controlled code by a loop harness goes through arm_sandbox.wrap (or runs trusted
harness code on validated input instead), and a selftest plants a payload in each hook (precheck, release, publish,
each gate step that runs clone code) that tries to read a retired tree, and proves it sees nothing.
