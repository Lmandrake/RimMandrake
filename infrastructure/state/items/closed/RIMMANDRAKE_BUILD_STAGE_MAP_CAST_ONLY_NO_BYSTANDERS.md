# RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** the green room and the stage for a test game; the three map kinds of `needs.map` (`settlement` the
  default, `pocket`, `colony`); the stage kept as a fixture save per mod list; the station allocator with margins and
  retirement; the spawners held for the stage map; the per-pawn holds for a `colony` map.
- **Needs:** the staging ops ticket.

Depends on: `RIMMANDRAKE_BUILD_STAGE_OPS_READ_BACK_NEVER_ECHO`.

## verify

Acceptance test (offline), 8 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_stage_stations.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_stage_stations.py`, 8 checks (pure allocator): no two
  stations overlap, margins included; a request that cannot fit says why; a retired station is never given again; a
  station near the edge is refused when the plan asks for distance from it; a `pocket` request by a scene that fires
  an incident is refused; a `colony` request is marked "shared map"; two more on the allocator's edge cases.

- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_stage_map.py`, 6 rows: the stage holds zero
  pawns after make; the green room's colonists are alive and fed after 60,000 ticks of an idle stage; a raid fired at a
  `settlement` stage with cast defenders spawns raiders at an edge with an assault duty; the same raid at a stage with
  no free colonist is reported "called, not fired"; the make time of each map kind is printed; a wild animal that
  appears on the stage is a breach.

Live state at filing: UNRUN: its script `prove_stage_map.py` does not exist yet.

## criteria

- The acceptance test prints 8 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red:** margins left out of the overlap test; a `pocket` stage given to a raid scene.
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
