# RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** `scene.py compare`: one plan, from one fixture save loaded fresh for every run, with the random state
  recorded at arm and written back before each run (two loads of one save do not start with equal random state; read
  in this pass: the state is not in the save). Arms, in order of trust: PLAY speed 1 (the reference), PLAY speed 3,
  PLAY Ultrafast, STEP. Five runs each; traces compared tick by tick; ticks per second of each arm on the 13-mod list
  and, riding a load that is already scheduled, on the full list. The receipt field `mode`, and the rule "an arm that
  was not compared with the reference counts for no bar". A comparison holds for one key (plan hash, loaded hashes of
  the mods the scene touches, companion hash, mod list, arm) and is owed again when the key changes. Replaces the stuck measuring tool of
  `TICKBURST_PROVE_MANY_TICKS_ONE_FRAME`.
- **Needs:** the instruments ticket (`jawa/run_until`, session), done. The run-plan ticket is held; "plan" here means what the scene script asks for in a call (`06_build_order.md` §Pass three).
- This is the first of pass one's six first-week measurements. Its result decides which arms may be used for
  acceptance, and whether a faster driver is ever built.

Depends on: `RIMMANDRAKE_WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH` (done).

## verify

Acceptance test (offline), 8 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_scene_compare.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_scene_compare.py`, 8 checks: two equal traces compare equal;
  a difference in a track names the tick and the value; a difference only in wall time is no difference; a missing
  tick range is "could not compare", not "equal"; a replay is never counted as a sample; two runs that did not start
  from one save are refused; a run whose random state was not written back is refused; a comparison under another key
  is not used.

- **Live test (UNRUN):** `python.exe src\RimMandrake\Utils\scene.py compare --plan <spared carrier> --arms play1,play3,ultra,step --n 5`:
  a table of 20 runs and, for each arm, "no divergence observed in 5 runs" or the first diverging tick and value.

Live state at filing: UNRUN.

## criteria

- The acceptance test prints 8 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red:** a comparison that ignores taps; "could not compare" reported as equal.
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
