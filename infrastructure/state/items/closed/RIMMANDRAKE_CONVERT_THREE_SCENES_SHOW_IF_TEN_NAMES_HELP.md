# RIMMANDRAKE_CONVERT_THREE_SCENES_SHOW_IF_TEN_NAMES_HELP

One ticket of the Bridge v2.0 build order, under the enacted pick of pass three. Read
`design/specs/2026-11-23-bridge-v2/11_design.md`, then the contract pages it names in
`design/specs/2026-11-23-bridge-v2/contracts/`. The order is the last section of
`design/specs/2026-11-23-bridge-v2/06_build_order.md`. Filed by `RIMMANDRAKE_DESIGN_BRIDGE_TWO_PYTHON_TESTS_FEW_RICH_ENTRY_POINTS`.

## spec

Three real scenes are written again on the scene library, and the result is measured against the scripts of today.
This is the test of the hypothesis that ten names help (`11_design.md`, challenge point 5).

| scene | today | why this one |
|---|---|---|
| FlowWorks `sc_moat_raid` (`FlowWorks/northstar/concept_scenes.py`, `_moat_raid`) | PASS, FAIL, PASS in three valid runs on visit 9; reads each raider every 60 ticks from Python; reads `held=` by a text search of a C# helper's output | the per-tick recorder, the exact stop, the hidden read |
| Explosive Knockback, the storeroom bomb pit (`ExplosiveKnockback/knockback_runner.py`, `proof/storeroom_pit_proof.py`) | staged and judged by C# in a PROOF build | an act on a tick; a verdict that moves out of C# |
| Gimme Some Slack `sc_wall_lamp_looks` (`GimmeSomeSlack/northstar/scene_rows.py`, `wall_lamp_looks`) | builds through `jawa/build_batch` and action strings; a capture for the judge | staging with read-back; a look |

- **Builds:** each of the other names of the library when the first of the three scenes needs it, to its contract
  page, by extraction: `scene.contract` (it carries the lint duties of the dropped scene-file compiler), `s.stage`,
  `s.act` (the verbs these scenes use, and `tune` only if one uses it), `s.read`, `s.shot`. `scene.judge` is
  `RIMMANDRAKE_BUILD_SCENE_JUDGE_OUTSIDE_GAME_FROM_KEPT_TRACE`. A name or verb that none of the three needs is not
  built here.
- Each converted scene is added beside the old one. The old row stays the deciding row of its mod's test table until
  the converted scene was seen to FAIL on a planted fault and PASS on the real build in one sitting.
- **The measurement**, written to `design/specs/2026-11-23-bridge-v2/12_conversion_readings.md`: for each scene, old
  against new: lines; bridge calls in one run; distinct tool or entry-point names; `s.raw` calls left (each is a
  promotion or hands candidate); runs needed to the first valid run; spoiled runs and their class. One of the three is
  written by a fresh agent that is given only `scene.py help` and the old scene's claim, and its questions and wrong
  turns are listed.
- A struggle in Python found on the way (a poll loop, a helper compiled into a mod, a value no path reaches) is filed
  as a hands ticket, with its acceptance test.

## verify

Acceptance test (offline), 17 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_scene_conversion.py
```

Seen red on base `47689bd93d` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** 17 checks against the fake bridge and kept traces: each of the three scenes imports only `scene`
  (3); each plays to its end on recorded replies (3); `scene.contract` refuses a success with no exposure, a kind B
  scene with no budget, a def name that is not in the frozen dump, and a condition on a value that nothing can record,
  with no bridge call made (4); `s.stage` builds its reply from the read-back and reports a replaced pawn kind as a
  staging fault (1); `s.read` gives `gone` for a gone thing, never 0 (1); the moat scene's judge gives MOD FAILURE on
  the hits captured live with the melee rule off, and SUCCESS on the hits captured with it on (the two readings of
  `selftest_flowworks_moat_rim_stabs.py`) (2); a run that used `s.act.tune` or a changing `s.raw` does not count for a
  bar (1); a trace with no closing record is judged COULD NOT LOOK (1); `12_conversion_readings.md` has a measured row
  for each scene, old and new (1).
- **Live test (UNRUN):** for each scene, `python.exe src\RimMandrake\Utils\scene.py accept <the converted script>`
  on a free game with the scene's tier list: the outcome of the converted scene equals the old row's on the same build;
  then the planted fault of that scene (the melee rule off; the compiled mutant "the carried pawn is not spared" or the
  pit's own plant; the master switch off) gives MOD FAILURE.

Live state at filing: UNRUN: the converted scripts do not exist yet.

## criteria

- The acceptance test prints 17 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red:** a `stage` that echoes the request; a `read` that returns 0 for a gone thing; a
  `contract` that is checked after the load; a judge that gives SUCCESS with no exposure.
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on a
  boundary page first (`design/specs/2026-11-23-bridge-v2/boundary.md`, or the contract page of the name it serves).
- `12_conversion_readings.md` states, from its rows, whether the ten names helped, and names what it could not measure.
