# `scene.contract`: state what the scene claims, before the game is touched

**For:** it turns the scene's claim into data that the library can check, record and judge.

## Accepts

| argument | meaning | example |
|---|---|---|
| `claim` | one sentence about what the player sees or can do | `"raiders held in the drained moat do not stab the rim wardens"` |
| `kind` | `"A"` deterministic, `"B"` stochastic, `"C"` hunt | `"A"` |
| `exposure` | conditions that show the opportunity really happened | a raider stood in the moat while it was drained |
| `success` | conditions that must hold | no warden took a hit from a raider |
| `forbidden` | conditions that make a MOD FAILURE in any run | a raider left the moat while it read held |
| `end` | the condition that ends the scene | 2,500 ticks after the sluice opened |
| `limit` | the most ticks the scene may play | `6000` |
| `budget` | kind B only: the number of runs, or X successes in Y opportunities | `None` |

Conditions are built with the helpers of `scene.cond` (`help cond` lists them).

## Returns

A `Contract`: the arguments as given, `hash`, and `needs_record` (every value and event that the conditions read, so
that `scene.open` can arm the recorders for them).

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
| `UNKNOWN_DEF` | a def name that is not in the frozen dump | read the name from the def; the message lists near names |
| `UNRECORDED_VALUE` | a condition on a value that no track or tap can record | name a recordable path (`help cond`), or file a hands ticket |
| `NO_END` | no end condition or no limit | add both |

## Example (FlowWorks `sc_moat_raid`, row `MOAT_rim_wardens_not_stabbed`)

```python
from scene import cond as c
moat = scene.contract(
    claim="raiders held in the drained moat do not stab the rim wardens", kind="A",
    exposure=[c.count("in_cells", who="raiders", cells="moat", after="sluice_open") >= 1],
    success=[c.count("damage", victim="wardens", instigator="raiders") == 0],
    forbidden=[c.any("raiders", c.outside("moat"), after="sluice_open")],
    end=c.ticks_after("sluice_open", 2500), limit=6000)
```

## The red check

`test_contract_refuses_*` (one test for each row above) and `test_contract_makes_no_bridge_call` in
`selftest_scene_library.py`. Planted fault: a contract that is checked after the load.

## Limits

It cannot check what a script does between two library calls. It does not prove that a condition is the right one.
