## spec
Two assemblies are built, proven to compile, and CANNOT be deployed while
RimWorld runs because the OS holds them memory-mapped. Both land in the next
shutdown window and neither needs a decision:
  1. `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Inhabited --apply`
     `CharacterDef.ConfigErrors` now names any pair of conflicting traits at load,
     and `CharacterApplier` refuses the second rather than building a pawn no
     vanilla generation could produce. **14 of the 269 need this** — see
     `CAST_TRAIT_CONFLICTS_1` in `queue/DECIDE.md`.
  2. `python.exe src/RimMandrake/bridgetools/build.py --gm --apply`
     adds `jawa/faction_name_get`, `jawa/faction_name_set` and
     `jawa/faction_create`, 112 -> **115**.
🔴 **`--gm` on the second one, or the deploy strips every player-acting tool.**

## verify
after the next launch, `Player.log` carries `[Inhabited] ready:` with 269
characters, and the bridge reports 115 `jawa/` tools.

## criteria
both deploys report in sync, and nothing regressed against
`EXPECTED_FAILURES_next_load.md` §4.

## notes
**from:** BUILD, 2026-08-20.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready — waiting on a game-down window only
