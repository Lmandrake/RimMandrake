# BUILD — handoff

## Owed, and it is one command

🔴 **A companion DLL deploy waits on a game-down window.** XML deploys with the game up;
assemblies do not, because the OS locks them. Do it FIRST in the window.

```
taskkill.exe /F /IM RimWorldWin64.exe
python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py --gm --apply
```

🔑 **`--gm` is required.** Without it three tools compile out and `build.py` refuses with
*"THIS DEPLOY WOULD REMOVE TOOLS"*. That refusal is correct — do not reach for
`--allow-tool-removal`. Check the output for the word `deployed`; a piped `grep` hides the
running-game refusal and you then test stale code.

⚠️ **The game copy is far behind:** 166 tool names deployed against 238 built, 670 KB of IL.
The window pays for much more than the four items below.

| tool | item |
|---|---|
| `jawa/lord_set_job` | LORD_JOB_SWAP_TOOL_1 |
| `jawa/bridge_arg_report` | BRIDGE_DROPS_UNKNOWN_PARAMS_1 |
| `jawa/debug_actions` | DEBUG_ACTION_SEARCH_WEDGES_BRIDGE_1 |
| `jawa/build_batch` (survived/displaced) | BUILD_BATCH_OVERWRITES_SILENTLY_1 |

Each item carries a three-line `## Prove it`. ⚠️ New this build: the companion now
references `0Harmony` and patches one RimBridgeServer private method. If the bridge
misbehaves in a way unrelated to the new tools, suspect that first — grep `Player.log` for
`[JawaBench] argument guard`, and read `installed` from `jawa/bridge_arg_report`.

## Deployed with the game up, awaiting only a capture

- `BiomeCast_Ashkarr.xml` — 28 biomes, 801 entries, md5 identical.
- `JawaFactionRoster.xml` — `PrestigeCombatGear` removed from all four Helix kinds.
- `AncientArsenal_Ashkarr.xml` — the scatterbow sever was already deployed.

## Open, offline, ready to pick up

**Four Outer Rim kinds carry an apparel tag with zero surviving carriers**, so they draw
from the generic pool. Replacements are measured and unambiguous — every carrier is
`OuterRim_*` and includes the items each kind already requires by name:

```
OuterRim_ImperialTrader      ORImperialLight(0) -> ImperialApparel(21) + ImperialOfficer(6)
OuterRim_RebelJumpTrooper    RebelApparel(0)    -> RebelForestCamo(4) + RebelJetpack(1)
OuterRim_RebelOfficer        RebelApparel(0)    -> RebelOfficer(3) + RebelFleetTrooper(2)
OuterRim_RebelTrader         RebelApparel(0)    -> RebelOfficer(3) + RebelFleetTrooper(2)
```

Supply index: `observed/apparel/supply_index.json`. Audit: `Utils/apparel_tag_audit.py`.
⚠️ Do NOT do the four `Ancient*` kinds in the same sweep — their pools were emptied by the
owner's own Cherry Picker cuts (`AM_CataphractHelmetFashion`, `AM_CataphractHelmetSlaughter`
are in his config). Restoring them reverses his decision. That is his call.

## Do not re-do these — done in source, waiting only on a load

`BRIDGE_READ_VEHICLE_COMPONENTS_1` · `STAT_ON_INSTANCE_TOOL_1` · `EMPIRE_GRUNT_SPAWNS_BARE_1`
· `JAWA_SCENARIO_PARTS_1` · `BLACKSTAR_NAME_MUST_NOT_LEAK_1` ·
`EMPIRE_BLACKSTAR_ALWAYS_WILLING_1`. Evidence with file:line:
`infrastructure/state/evidence/ITEM_SOURCE_SWEEP_2026-08-27.txt`.

⛔ **`ROLE_KINDS_ARMED_5_OF_5_1`: do not extend `REQUIRE_VIOLENT` past Empire and Blackstar.**
That reverses DECIDE's ruling that a pacifist pawn is acceptable from ten of twelve factions.
The `weaponMoney` shortfall is the half that is fair game.

## Rules that changed today — read these before working

- A live check must be **proven needed**; the default is source. Whoever proves a thing
  **closes** it — no hand-back — then greps `items/` for what it also settled.
- **BUILD designs its own verification.** DECIDE states the outcome only. ⛔ Do not re-raise
  the self-grading objection; the owner accepted that trade for speed.
- **Files must shrink.** Write the instruction, delete what it supersedes. No quotes, no
  dates, no "used to say". Git is provenance.
