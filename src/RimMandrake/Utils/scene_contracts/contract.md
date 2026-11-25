# `scene.contract`: state what the scene claims, before the game is touched

**For:** it turns the scene's claim into data that the library can check, record and judge.

## Accepts

| argument | meaning | example |
|---|---|---|
| `claim` | one sentence about what the player sees or can do | `"raiders held in the drained moat do not stab the rim wardens"` |
| `kind` | `"A"` deterministic, `"B"` stochastic, `"C"` hunt | `"A"` |
| `exposure` | a condition, or a list (all must hold on one tick after the first): the opportunity really happened | a raider stood in the drained moat |
| `success` | a condition, or a list (all must hold on the last tick) | the run played 900 ticks and no warden is downed |
| `forbidden` | a condition, or a list (any one, on any tick, is a MOD FAILURE) | a raider swung at a warden |
| `end` | the `until` of the run that the judge reads: a condition, or a number of ticks | `900` |
| `limit` | the most ticks the scene may play | `6000` |
| `budget` | kind B only: the number of runs, or X successes in Y opportunities | `None` |

Conditions are built with the helpers of `scene.cond` (`help cond` lists them). A condition reads a value path of an alias
(`c.value("wardens[0]", "health.downed")`), its state (`c.state(...) == "gone"`) or the tick. The judge reads a success on the
last sample and refuses a success that is true on the first (an APPARATUS FAULT), so a "nothing bad happened" claim joins
`c.played(n)` to its success: true once n ticks of the judged run have played. Aliases are named before the game is touched,
and `s.stage` binds them; a group has a fixed size (`people[0]` to `people[4]`). A cast tap (`c.count("damage", ...)`) is refused
`UNRECORDED_VALUE` until the taps are built (`RIMMANDRAKE_BUILD_WORLD_EVENT_TAPS_SECOND_FAMILY`).

`scene.open(game, contract=moat, ...)` keeps the contract. Every `s.run` of that session records each value the contract reads,
and writes `contract.json` beside its trace: **the last run of a session is the run that the judge reads.**

## Returns

A `Contract`: the arguments as given, `hash`, `needs_record` (every value that the conditions read, so that each run records
it), and `plan(request, start)`, the judge's `contract.json`. Kind C (a hunt) is judged as kind B with no allowed miss.

Receipt: `game` and `build`: `not applicable`; `did: []`; `hands: []` (no bridge call is made); `could_not_look`: always one line, "whether a
success condition is already true before the first act: the judge decides that on the first sample".

## State changes

None. The game is not touched. No file is written.

## Refuses

| name | when | repair |
|---|---|---|
| `NO_EXPOSURE` | a success with no exposure condition | add the condition that shows the opportunity happened |
| `KIND_B_NO_BUDGET` | kind B with no budget | write the budget before the first run |
| `KIND_A_ALLOWED_MISS` | kind A with an allowed miss or an X of Y | make it kind B, or remove the miss |
| `UNKNOWN_DEF` | a `def:<Type>/<name>` target that is not in the frozen dump | read the name from the def; the message lists near names. Where the dump is not readable (a helper clone), the name is not checked and `could_not_look` says so |
| `UNRECORDED_VALUE` | a condition on a value that no track or tap can record | name a recordable path (`help cond`), or file a hands ticket |
| `NO_END` | no end condition or no limit | add both |

## Example (FlowWorks `sc_moat_raid`, row `MOAT_rim_wardens_not_stabbed`)

```python
from scene import cond as c
W = ["wardens[0]", "wardens[1]"]
moat = scene.contract(
    claim="raiders held in the drained moat do not stab the rim wardens", kind="A",
    exposure=c.any_(*[in_ring(r) for r in ("raiders[0]", "raiders[1]")]),       # in_ring: a helper of the script, on positionInt
    success=[c.played(900)] + [c.value(w, "health.downed") == False for w in W],
    forbidden=[c.value(w, "mindState.lastMeleeThreatHarmTick") >= 0 for w in W],  # the game sets it on every melee swing at the pawn
    end=900, limit=1000)
```

The whole scene: `src/RimMandrake/FlowWorks/northstar/scene_moat_rim_wardens.py`.

## The red check

`test_contract_refuses_*` (one test for each row above) and `test_contract_makes_no_bridge_call` in
`selftest_scene_library.py`. Planted fault: a contract that is checked after the load.

## Limits

It cannot check what a script does between two library calls. It does not prove that a condition is the right one.
