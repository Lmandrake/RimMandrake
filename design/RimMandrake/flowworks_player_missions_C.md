# FlowWorks player missions — Approach C ("AI plays the mod"), built 2026-10-06

Approach C from `design/RimMandrake/flowworks_playtest_automation_2026-10-06.md` (GPT runs A/B/C, "bounded agent
plays missions"). The owner asked for all three approaches to be built so he can try them and **time** them; no plan
is adopted. This is the thin driver the runs asked for, not a game-playing platform.

## What it is

A player agent (a Claude subagent) plays one fixed mission through `player_missions.py`, one command per move:
`observe` (compact state, optional screenshot), `act <tool> <json>` (whitelisted, logged, timed) and `note <kind>`
(agent-reported friction). The driver owns the fixture, the storyteller events, the deadline and the goal check.
`report` produces the verdict (PASS / FAIL / TIMEOUT / UNMEASURED) from game state, plus a timing table, a friction
log and the action trace.

## Files

| file | role |
|---|---|
| `src/RimMandrake/FlowWorks/northstar/player_missions.py` | the driver: `start`, `observe`, `act`, `note`, `report`, `verify`; `--dry-run` |
| `src/RimMandrake/FlowWorks/northstar/player_missions_spec.json` | missions, whitelist with per-tool verification claims, refused tools/patterns/labels, fixture tools |
| `src/RimMandrake/FlowWorks/northstar/player_missions_BRIEF.md` | the operator brief handed to the playing subagent |
| `src/RimMandrake/FlowWorks/northstar/selftest_player_missions.py` | offline selftest (620 checks, paired negatives) |
| `Transient/player_missions/<mission>_<stamp>/` | per run: `run.json`, `actions.jsonl`, `report.json`; `CURRENT` names the active run |

## Missions

| id | fixture (setup only, before the clock) | goal check (game state) | deadline |
|---|---|---|---|
| `canal` | calm weather, incident queue cleared, site 32×16 cleared to Soil, 4×4 `WaterShallow` pond at its west end | ≥10 cells in the 3×16 GOAL band with `isExcavated` and `fEff ≥ 1` (`jawa/flowworks_excavation_rect`) | 1800 s, 60k ticks, 150 actions |
| `pit` | calm, 150 wood + 75 steel at the site; event at +30k ticks: `jawa/fire_raid` 60 pts `TribeRough`, `ImmediateAttack`, `EdgeWalkIn` | a non-player pawn `isPrisonerOfColony` (`jawa/pawn_roles`), first seen ≥15k ticks before the check | 2400 s, 90k ticks, 200 actions |
| `chain` | calm, site to Soil, pond, 4-wide `WaterMovingChestDeep` channel, `MoisturePump` research finished, steel/wood/components | a colonist inside `far_bank`, no injury/drowning hediffs, an `RM_LiquidTank` whose inspect line reads ≥10 units | 2400 s, 90k ticks, 200 actions |

Sites are anchored at the map centre (or `--anchor x,z`). `start` pauses the game, runs the fixture, writes a
checkpoint save `PM_<mission>_start_<stamp>` and prints the goal and the places. **Stat the Saves folder yourself;**
`save_game` has written the current slot instead of the named one before (CLAUDE.md, rimbridge skill §2).

## Whitelist: what is verified and what is not

`python3 src/RimMandrake/FlowWorks/northstar/player_missions.py verify` re-derives every claim in the spec:
`dump` = tool name and every listed parameter found in `Transient/bench_tools_dump.json` (438 tools, written
2026-10-02); `source` = found as `[Tool]` + parameter in `src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs`.
Result on 2026-10-06: **80 tools, 0 problems**.

- **Verified by name and parameters (dump):** every `rimworld/*` read, selection, camera, tab, letter, alert,
  designator, gizmo, draft, time and screenshot tool, plus `jawa/list_things`, `jawa/list_pawns`, `jawa/bill_*`,
  `jawa/configure_bill` and `jawa/set_work_priority`.
- **Verified from source only** (built after the dump): `jawa/pawn_roles`, `jawa/flowworks_excavation_rect`,
  `jawa/flowworks_pit_report`, `jawa/flowworks_body_report` (driver forces `classify=false`, because `true` forms a
  body permanently), `jawa/canal_cell_report`.
- **UNVERIFIED behaviour:** choosing a float-menu option. `right_click_cell` opens the menu, and a `Verse.FloatMenu`
  is visible only through `get_ui_layout` (silent-failures.md). Whether `click_ui_target`, `open_context_menu` or
  `execute_context_menu_option` can pick an option has not been proven live, and **the pit mission's "capture down"
  is a float-menu order** (`Source/Superdeep/RM_PitRooms.cs`). The first live pit run decides it.
- **Name/param verification is not behaviour verification.** Every response field the driver reads is read
  defensively and reports UNMEASURED when absent. Fields still unproven live: `list_colonists[].position`, letter
  and message labels, `list_selected_gizmos[].gizmoId/label`, the `designators[].id` the canal mission needs, and the
  tank's `Holding: X (a / b units)` inspect line (keyed `RM_LiquidTankHolding`, read by clicking the tank).
- **Fixture defs, MEASURED in the 2026-10-04 def dump (`measure get`):** `WaterShallow`, `WaterMovingChestDeep`,
  `Soil`, `WoodLog`, `Steel`, `ComponentIndustrial`, `MoisturePump` (ResearchProjectDef), `RM_LiquidTank`,
  `TribeRough`, `ImmediateAttack`, `EdgeWalkIn`, `Clear`. Absent from that dump: `RM_LiquidPump`, `RM_LiquidHose`,
  `RM_FordStones`, `RM_UniversalCargoTank`. All four are in FlowWorks XML. The fixture does not name them, and the
  player must find them in the Architect; if they are missing in game, that is a finding.
- **Fixture caveats:** the painted channel is plain moving-water terrain, not a generated river, so FlowWorks river
  behaviour may not apply. The `fire_raid` `faction` value is a FactionDef defName by the tool's description, but
  this use is unproven, and a quicktest world may hold no `TribeRough` faction (`fire_raid` then reports
  `actual.substituted`).

Refused outright (spec `refused`, plus name patterns `teleport|resurrect|heal|proof|deepen|instant|debug|godmode|spawn`
and UI labels matching dev/debug/Deepen/proof/instant/god mode): `flowworks_excavation_drive`, `canal_dig`,
`flowworks_pulse`, `flowworks_spawn_flood`, `flowworks_set_active_fluid`, `flowworks_job_probe`, `ordered_job`,
`prioritized_work`, `order_pawn`, `stop_job`, `designate_batch`, `map_zones`, the debug menu, god mode, every
spawn/destroy/terrain/research/time-jump/health/guest/faction write, `fire_raid` (driver-only), save/load, settings,
and `run_script`/`run_lua*`. Unknown parameter names are refused, not dropped: the bridge drops them silently.

## Timing model (first-class output)

Each `actions.jsonl` row carries:

| field | meaning |
|---|---|
| `think_s` | wall gap from the previous row's end to this row's start, i.e. the agent's deliberation, including its LLM turn and process start |
| `bridge_ms` | the tool call itself |
| `overhead_ms` | the two `get_game_info` tick reads around it (driver cost, kept apart) |
| `ticks_advanced` | game ticks during the call |
| `ticks_during_think` | ticks that passed between actions, when the agent left the game running |
| `shot`, `shot_ms` | screenshot path and capture time (`observe --shot`; `act` screenshots count too) |
| `flags` | friction |

`report` totals: mission wall time, fixture time (kept outside the mission clock), think, bridge, overhead, ticks by
actions, ticks during think, screenshot count and time, action/observe/refused counts, internal reads, and a
per-class table (read / ui / designate / gizmo / order / time / shot).

**Friction log.** Automatic flags: `failed_placement`, `partial_placement` (trace only), `failed_action`,
`unclear_refusal` (a failure with no reason text), `repeated_attempt` (same non-read, non-time call with the same
arguments), `refused_by_driver`, `transport_limitation` (dry-run fake cannot model the call). Agent notes add
`abandoned_job`, `unclear_feedback`, `unexpected_consequence`, `cannot_find`, `agent_error` and
`transport_limitation`. Per the GPT runs, a friction finding becomes a mod defect only after a short deterministic
reproduction.

## Running mission 1 (canal) live

1. Bridge: `python3 src/RimMandrake/rimflow/cli.py bridge take --for "player mission canal"`.
2. Game on the flowworks tier with a fresh quicktest map loaded, paused, and **Options → Run in background ON**.
3. From the repo root: `python.exe src/RimMandrake/FlowWorks/northstar/player_missions.py start canal`. Check
   `FIXTURE: … 0 failed`, then stat the Saves folder for `PM_canal_start_*.rws`.
4. Spawn the player subagent (model per `infrastructure/agents/Agent_Policy.md`). Give it
   `player_missions_BRIEF.md` and the `start` output. Tell it to run every command in the foreground and to stop at
   PASS or DEADLINE.
5. `python.exe src/RimMandrake/FlowWorks/northstar/player_missions.py report` prints the timing table and friction
   log; `report.json` is in the run dir.
6. `python3 src/RimMandrake/rimflow/cli.py bridge release`.

## Dry run and selftest

- `python3 …/player_missions.py start canal --dry-run`, then the same `observe`/`act`/`report` with `python3`.
  `fakegame.FakeFlowWorksGame` serves the base reads. A toy extension in the driver adds the rest: a fake dig
  designator, one cell dug per 300 ticks, and dug cells 4-connected to the pond drawing one unit each from a
  40-unit stock. Fake state is pickled in the run dir between commands. **The toy physics proves the loop, never
  FlowWorks.** `pit` and `chain` dry-runs hit unmodelled tools; those land as `transport_limitation`.
- `python3 src/RimMandrake/FlowWorks/northstar/selftest_player_missions.py` → `PASS 620/620`. It covers the
  whitelist (each refused tool, patterns, unknown params, forced args, caps, dev labels), friction flags, timing
  arithmetic (think gaps, ticks during think, screenshots), event firing once, action- and wall-deadlines (FAIL →
  TIMEOUT), a dry-run that reaches PASS by digging against one that never digs and FAILs, and `verify` catching an
  invented tool and a wrong parameter.

## Open

- Float-menu option choice (above). It decides whether `pit` can be played at all through the player surface.
- The tank-units read selects the tank via `click_cell`. If the UI is jammed by an armed designator, `chain` reads
  UNMEASURED.
- No live run yet, so no timing numbers exist. The GPT estimate was 15–40 live minutes per episode, and the first
  `report` replaces it.
