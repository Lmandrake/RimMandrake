## ✅ BUILT 2026-08-26 at `c81814a4` — 35 built, 5 skipped, 1 half-refused with its reason

`198 → 233` declared `[Tool]` names. Builds clean **with and without** `--gm` (0 warnings,
0 errors, no tool removal), so nothing is trapped inside a GM guard.

| group | file | tools |
|---|---|---|
| H | `JawaBenchZoneTools.cs` | `storage_settings` `bill_add` `prioritized_work` `anomaly_knowledge` `royal_title` `set_stuff` |
| I | `JawaBenchIncidentTools.cs` | `storyteller_fire` `storyteller_swap` `quest_lifecycle` `wealth_recount` `lord_defend_spawn` `lord_assault_spawn` `manhunter_preview` `animal_resource_force` |
| J | `JawaBenchSocietyTools.cs` | `ideo_create` `ideo_precept_edit` `ideo_ritual_obligation` `ideo_style` `world_tile_map_generate` `settlement_remove` `caravan_form_exit` `gene_reimplant` `gene_random_set` `pawn_severity_adjust` |
| K | `JawaBenchRenderTools.cs` | `blueprint_place` `frame_finish` `power_net` `anomaly_monolith_set` `anomaly_containment` `map_drop` `artifact_transfer` `pawn_portrait` `pawn_atlas` `room_heat` `stat_explain` |

**Skipped because a tool already covered the row** — the check the roster's stale flags made
necessary, and it caught five:

| row | already covered by |
|---|---|
| create-stockpile / growing zone | `jawa/map_zones` action=createZone |
| add/remove zone cells | `jawa/map_zones` action=paintZone |
| force-job | `jawa/ordered_job` |
| install-bionic | `jawa/pawn_health` action=bionic |
| set master | `jawa/set_player_settings` |
| lock-weather | `jawa/weather_set` lockWeather=true |

⚠️ **One row is deliberately HALF-built and says so in its own Description.**
`jawa/anomaly_containment` reads and writes `containmentMode` and forces `CompStudiable.Study`,
but it does **not** move an entity onto a holding platform: that is a job-driven capture
interaction (WorkGiver + JobDriver), and faking it would mean simulating the game's AI. The
refusal is in the tool, not only here.

🔑 **Two rows looked like duplicates and were not.** `jawa/storyteller_fire` goes through
`Storyteller.TryFire`, which is a different call path from `jawa/fire_incident`'s direct
`Worker.TryExecute`; `jawa/quest_lifecycle` accepts and ends an EXISTING quest, which
`jawa/fire_quest` does not. Both were checked against the source before being built rather than
assumed either way.

⛔ **Built, not deployed** — the game holds the DLL. `NEXT_RELOAD.md` §25. None of the 35 has
ever been called.

---

# BRIDGE_TOOLS_MEDIUM_BLOCK_1 — the 40 MEDIUM capabilities, block 2 of 3

## spec

Derived 2026-08-26 from `design/Jawa/bridge/capability_roster_data.py` and its decision file
`dll_capability_roster.decisions.json`: **41 rows** are MEDIUM, not marked built, and not struck.
(The item's title says 40; the derivation says 41, and the derivation is the number to trust —
the title was written before the roster was re-walked.)

⚠️ **The roster's own `built` flags are STALE, and `ROSTER_VS_BUILT_2026-08-26.md` says so.**
That file's census read 163; the EASY block closed the same day and the companion now declares
**198**. So several of these 41 may already exist. The workload doc tells each builder to check
the live list first and SKIP a covered row, naming the tool that covers it. ⛔ A second tool for
a job that already has one is worse than not building it — it splits the surface and the next
seat picks the wrong one.

| rows | domain |
|---|---|
| 4 | Zones, stockpiles, bills & areas |
| 4 | Storyteller, incidents & quests |
| 4 | Ideology, precepts & rituals |
| 3 | Settlements, caravans & gravship |
| 3 | Map things & buildings |
| 3 | Animals & training |
| 2 | Save/load & scribe |
| 2 | Rendering, camera & screenshots |
| 2 | Pawn state & health |
| 2 | Lords, raids & AI groups |
| 2 | Jobs, work & schedules |
| 2 | Genes & xenotypes |
| 2 | Anomaly & entities (DLC) |
| 1 | Weather, temperature & conditions |
| 1 | Terrain, roof & grids |
| 1 | Skills, traits, relations & backstory |
| 1 | Research & technology |
| 1 | Diagnostics, logging & defs |
| 1 | Apparel, equipment & inventory |

The split into four non-colliding files, with every row's API anchor, is
`infrastructure/state/work/BRIDGE_TOOLS_MEDIUM_REMAINING.md`:

| group | file |
|---|---|
| H | `JawaBenchZoneTools.cs` — zones, bills, areas, jobs, research, skills, apparel |
| I | `JawaBenchIncidentTools.cs` — storyteller, incidents, quests, lords, animals |
| J | `JawaBenchSocietyTools.cs` — ideology, settlements, caravans, genes, pawn health |
| K | `JawaBenchRenderTools.cs` — map things, anomaly, save/load, rendering, terrain, weather |

🔑 **Why four files and not one.** The companion is one `sealed partial class` spread across
many files, so four agents can write four new files at once with no merge. That is how the EASY
block's last 32 shipped in a single pass.

## What makes MEDIUM different from EASY

EASY rows are one engine call with a guard. MEDIUM rows usually have a **required second step
that decides whether the change is visible at all** — a zone is not a zone until `ZoneManager`
registers it and `CheckContiguous` runs; a bill needs its recipe's ingredient filter; an
incident's worker rewrites the parms you gave it. **The failure mode is a call that returns
success and changes nothing**, which is this project's most expensive shape.

⇒ Every tool in this block reads its result back off the game and reports THAT, never the
request. `jawa/fire_raid` had to be fixed on 2026-08-26 for exactly this: it echoed the faction
asked for while a different one raided.

## verify
- `python.exe src/RimMandrake/bridgetools/build.py --gm` succeeds, 0 errors, 0 warnings.
- The new names appear in the built assembly, and the declared `[Tool]` count rises by the number
  actually added — counted by attribute, not by scanning the DLL for strings. ⚠️ `build.py`'s
  `tool_surface` is an UPPER BOUND: it reads 200 against 198 real tools because two names appear
  inside other tools' description prose.
- No existing `[Tool]` name changes or disappears (`build.py` refuses without `--allow-tool-removal`).

## criteria
- [ ] Every Group H/I/J/K row either built, or skipped with the existing tool that covers it named.
- [ ] Build clean with `--gm`, no tool removal.
- [ ] Each new tool reports the outcome read back off the game, not the request.
- [ ] ⛔ Offline only. A tool that compiles is not a tool that works; the live census is a
      separate claim and belongs to the load after the next down-window deploy.
