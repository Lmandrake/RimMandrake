# First drive of the 45 tools deployed 2026-08-26 — seat CHECK

None of them had ever been called. Full 582-mod list, `[JawaBench] ready: 166 tools`, scratch
quicktest map. Harness: `world/_lf/shakedown.py`, results `world/_lf/shakedown.json`.

## Verdict: **32 WORKS · 7 REFUSES (all clean) · 0 LIES · 0 ERRORS**

Every refusal named the missing parameter and what to pass instead:

```
research_availability  "Give a ResearchProjectDef defName."
research_progress      "Give a ResearchProjectDef defName."
paint_area             "ops is required, e.g. '10,20,5,5;30,30,2,2'."
sky_glow_set           "Give skyGlow and/or targetBrightness."
incident_schedule      "incidentDef is required."
signal_send            "tag is required."
```

⇒ **This is the best-behaved family of tools measured on this bridge.** For comparison, the same
session found `set_time_speed` silently doing nothing, `list_pawns.job` permanently null, and
`build_batch` reporting `placed` for things it then destroyed.

Read-only pass: `time_clock` · `time_perf` · `time_date_at` · `cell_temperature` ·
`incident_parms_preview` · `pawn_thoughts` · `pawn_break_thresholds` · `pawn_stats` · `room_get` ·
`map_zones listZones` — all returned real payloads.

Write pass: `pawn_refresh_needs` · `pawn_dirty_situational` · `pawn_memory` · `set_draft` (both
ways) · `stop_job` · `set_player_settings` · `timetable` · `new_allowed_area` ·
`time_pin_normal_speed` · `weather_roll_next` · `rain_suppress` · `difficulty_tune` — all worked and
all reported before/after state rather than a bare success.

## 🔴 The finding that outweighs the rest: THE BRIDGE SILENTLY DROPS UNKNOWN PARAMETERS

Two of my own shakedown calls were mis-named and **nothing complained.** Proven deliberately:

```
jawa/new_allowed_area {label: "CHECK_correct"}          -> success, label "CHECK_correct"    ✅
jawa/new_allowed_area {name:  "CHECK_wrong", banana:42}  -> success, label "Area 3"           🔴
jawa/time_clock       {zzz:"nonsense", ticks:"not-a-number"} -> success, full correct payload 🔴
```

**`success: true` in every case.** A parameter the schema does not declare is discarded before the
tool runs, with no warning, and the tool proceeds on its defaults.

⇒ **A typo in a parameter name is invisible.** It is caught only when the tool then misses a
*required* field and refuses. Where the tool has a sensible default — `new_allowed_area`'s label,
`stop_job`'s `mode` — you get a successful call that did something other than what you asked.

🔑 **The house rule that follows: read the schema, not the sibling tool.** This session lost calls to
`rect` vs `rects` vs `ops`, `faction: "player"` vs `PlayerColony`, `name` vs `label`, and
`action` vs `mode` — four different grammars across tools that look alike.
⇒ `b.list_tools()` gives the accepted keys; diff your arguments against them before a batch.
`jawa/damage`'s own error text already warns about this; it is now measured on two more tools and it
is a property of the **bridge**, not of any one tool.

## Smaller things worth keeping

* **`jawa/time_clock` reports `paused` and `curTimeSpeed` directly** — a cleaner answer to "is the
  game running" than `get_cell_info.state`, and `get_game_info` still has neither.
* **`jawa/stop_job` mode `endcurrent` on an `Ingest` job reported `beforeJob: Ingest,
  afterJob: Ingest`** — the pawn immediately re-picked the same job. The tool is right; the
  before/after pair is what makes that legible instead of looking like a failure.
* **`jawa/weather_roll_next` rolled `Clear` → `Clear`.** A legitimate outcome, reported honestly with
  both sides.
* **`jawa/rain_suppress`** reads its result back **out of the private field** and says so in a note.
* **`jawa/incident_parms_preview`** returns `defaultParms` with `incidentDef: null` for a category
  query — worth a second look, but it answered.
