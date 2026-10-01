# lint_calls baseline, 2026-10-01

Command: `python3 src/RimMandrake/Utils/northstar_driver/lint_calls.py src`
Snapshot: `src/RimMandrake/Utils/northstar_driver/tool_schemas.json` = 482 tools: 438 from the live
`--list-tools` census `Transient/bench_tools_dump.json` + 44 tools that exist only in C# `[Tool]`
attributes (the census predates the current DLL; all 30 first-pass UNKNOWN_TOOL hits were these, e.g.
`jawa/mod_settings_field`, `jawa/flowworks_*`, `jawa/set_current_map`, `jawa/site_state`).
Scanned: every `validation.py`, `northstar_plan.py`, `northstar_site.py`, `preflight_*.py` under src/;
477 literal-named bridge calls checked.

Totals: 7 problems — UNKNOWN_TOOL 0, UNDECLARED_PARAM 1, MISSING_REQUIRED 0, UNCHECKED 6.

| file:line | tool | kind | detail | owner action |
|---|---|---|---|---|
| `src/RimStarWars/Cuisine/validation.py:274` | jawa/list_things | UNDECLARED_PARAM | `fields="label"`; tool declares defName, group, includePawns, limit, rect. Silently dropped by the bridge. Not a typo, so not fixed here. | Cuisine owner: drop `fields=` |
| `src/RimMandrake/Pyrelands/preflight_pyrelands.py:153` | ? | UNCHECKED | `s.call(tool, **p)` inside a generic wrapper | none (wrapper); its callers are linted |
| `src/RimMandrake/Pyrelands/validation.py:249` | jawa/list_things | UNCHECKED | `**kwargs` | confirm kwargs keys against declared params |
| `src/RimMandrake/Pyrelands/validation.py:262` | jawa/list_things | UNCHECKED | `**kwargs` | same |
| `src/RimMandrake/Pyrelands/validation.py:394` | jawa/list_pawns | UNCHECKED | `**kwargs` | same |
| `src/RimStarWars/Droidworks/validation.py:169` | jawa/pawn_health | UNCHECKED | `**kwargs` | same |
| `src/RimStarWars/JawaIonWeapons/validation.py:322` | jawa/pawn_gear | UNCHECKED | `**kwargs` | same |

Notes
- The three defects measured today (`set_draft draft=`, `set_plants defName/rect`, weather_get/dlc_status result
  shapes) are not in any current file in scope; the first two are proven flagged by the selftest against the
  committed snapshot. Result-shape defects are not detectable by a parameter lint.
- The census flags `required` false for our own `[Tool]`s whose C# parameter has no default, so the snapshot
  merges C#-required into the census. If the binder tolerates a missing no-default param, MISSING_REQUIRED could
  over-report; baseline has 0 so none observed yet.
- Refresh the snapshot with a fresh census when the bridge holder can: `python.exe src/RimMandrake/Utils/northstar_driver/tool_schemas.py --live`.
- Not covered: `call_many([...])`, calls through aliases other than `.call/.bridge_call/_call`, tool names built from variables.
