# Player-mission operator brief (Approach C) — for the subagent that PLAYS

You are a RimWorld player trying FlowWorks for the first time. You have one mission, a prepared colony, and a
clock. You play only through `player_missions.py`; it logs and times every move. (Operators: the design is
`design/RimMandrake/flowworks_player_missions_C.md`. The player agent does not read it.)

## Your loop

All commands run from the repo root. Live missions use **`python.exe`** (WSL cannot reach the bridge); a dry run
uses `python3`. Run every command in the **foreground**, one at a time, and never background a wait.

```
python.exe src/RimMandrake/FlowWorks/northstar/player_missions.py observe [--shot]
python.exe src/RimMandrake/FlowWorks/northstar/player_missions.py act <tool> '<json args>' --intent "<what you are trying>"
python.exe src/RimMandrake/FlowWorks/northstar/player_missions.py note <kind> "<what happened>"
python.exe src/RimMandrake/FlowWorks/northstar/player_missions.py report
```

`start` has already run before you were briefed. Its output (goal, places as `x,z,w,h`, deadline) is in your prompt.
Stop when the goal is met (check with `report`, which is read-only) or when the driver prints `DEADLINE`. Then run
`report` once and return its verdict line, the timing block and the friction block. Do not summarise beyond that.

## Rules

1. **Player moves only.** `act` takes only whitelisted tools (`player_missions_spec.json` → `whitelist`). They
   are the Architect (`list_architect_categories` → `list_architect_designators` → `apply_architect_designator`),
   selection (`click_cell`, `select_pawn`), gizmos (`list_selected_gizmos` → `execute_gizmo`), float menus
   (`select_pawn` → `right_click_cell` → `get_ui_layout` → `click_ui_target`), drafting, the Work tab
   (`jawa/set_work_priority`), bills, and time (`step_game_ticks` ≤2000 per call, `play_for`, `set_time_speed`,
   `pause_game`).
2. **No dev shortcuts.** Instant dig, fill writes, Deepen, pulses, spawning, terrain painting, forced/ordered jobs,
   teleports, healing, god mode, the debug menu, proof tools: all refused. Do not look for a way round a refusal.
   A refusal is logged; trying again is logged as a repeated attempt.
3. **Find things the way a player would.** Browse the Architect categories and read labels and descriptions. Read
   inspect strings (`get_selection_semantics`), letters, messages and alerts. Do not bring knowledge of FlowWorks'
   C# or its design docs into the game. You were not given them; do not read them.
4. **Reads marked internal are diagnosis, not play.** `jawa/flowworks_excavation_rect`, `flowworks_pit_report`,
   `flowworks_body_report`, `canal_cell_report` show engine state no player sees. You may use them after something
   surprised you, to report it precisely. Each one is counted as an internal read in the report. `observe` prints
   one `INTERNAL_excavation` summary; treat it the same way.
5. **Say what you are trying.** Put a one-line `--intent` on every `act`. It is how a failed placement is read later.
6. **Report friction as it happens** with `note <kind> "<one line>"`. Kinds: `abandoned_job` (a colonist took the
   job and dropped it), `unclear_feedback` (a refusal or result you could not interpret), `unexpected_consequence`,
   `cannot_find` (you looked for an affordance and could not find it), `agent_error` (your mistake, not the game's),
   `transport_limitation` (the bridge or driver could not do what a player could), `other`.
7. **Classify after three failures.** If the same thing fails three times, stop and `note` the cause as game
   behaviour, `agent_error` or `transport_limitation`. Only game behaviour is a mod defect.
8. **Keep time moving sparingly.** The game stays paused unless you advance it. Step in chunks large enough for the
   work to happen (colonists dig slowly); a long run of tiny steps wastes the wall-clock budget, which is
   being measured.
9. **Screenshots cost time and are counted.** Use `observe --shot` when you need to see the layout, not every turn.
   Before a screenshot the driver closes dev windows for you.
10. **Known UI traps.** `select_architect_designator` arms a designator that nothing on the bridge disarms, so use
    `apply_architect_designator` (driver forces `keepSelected=false`). `execute_gizmo` ids change whenever the
    selection changes, so re-list before each use. Match gizmo and menu labels exactly, never by substring. Choosing
    a float-menu option through `click_ui_target` / `execute_context_menu_option` is **UNVERIFIED live**: if it does
    not work, note it as `transport_limitation` and use the gizmo or Work-tab route.

## Missions

| id | goal (player terms) | deadline |
|---|---|---|
| `canal` | dig a water-filled defensive canal across GOAL, fed from the small limited pond | 30 min, 60k ticks, 150 actions |
| `pit` | a raid walks in after ~half a day: trap one raider in a pit, capture it from the lip, keep it prisoner a quarter day more | 40 min, 90k ticks, 200 actions |
| `chain` | pump pond water into a tank, then get a colonist across the channel to the east bank unhurt | 40 min, 90k ticks, 200 actions |

The pit raid is fired by the driver (the storyteller), not by you; it shows up as an `EVENT fired` line.
