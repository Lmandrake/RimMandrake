# JawaBench companion tool surface — silent-failure audit

Read-only offline audit, 2026-09-09. Scope: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs`,
concentrated on JawaBenchTerrainTools, JawaBenchWorldTools/WorldEdit2, JawaBenchMapTools/MapInfoTools/StatTools,
JawaBenchPawnTools/PawnKitTools, JawaBenchJobTools/ZoneTools/EventTools (five parallel Sonnet sub-audits,
full-file reads). No game, no bridge, no builds, no commits — findings only.

**General note from every sub-audit**: this file set is unusually self-hardened already — most files carry
inline `🔴`/"Fixed 2026-0X-0X (opus/sonnet code review)" comments from prior passes that closed the obvious
"success:true on a no-op" holes with read-back verification and `refused[]`/`changed[]` counters. The findings
below are what survived that hardening: places the pattern was applied to one tool but not its sibling, places
where a read-back was added for the write-count but not for the specific fact a caller actually needs, and
naming drift between tools that do the same thing.

## Ranked findings (highest cost to a caller first)

1. **`JawaBenchTerrainTools.cs:5373` (tool) / `:5496` (field)** — `jawa/list_things` — **CONFIRMED live incident.**
   Row exposes only `faction` (a defName), no `factionName` companion like `jawa/list_pawns` has; a caller
   reading `factionName` gets nothing and a player-owned thing reads as factionless.
   Guard: add `factionName = thing.Faction?.Name` alongside `faction`, matching `list_pawns`' shape.

2. **`JawaBenchZoneTools.cs:369` (tool) / `:465-468` (risk)** — `jawa/prioritized_work` — builds its job
   identically to `jawa/ordered_job` but never sets `job.playerForced = true` — reproduces the exact
   CONFIRMED "accepted then curJob=Wait after 60 ticks" bug that `JawaBenchJobTools.cs:1043` just fixed on
   the sibling tool. The fix landed on one tool and not the other.
   Guard: add `job.playerForced = true` before `TryTakeOrderedJobPrioritizedWork`.

3. **`JawaBenchPawnTools.cs:722-725,771-773`** (tool reg `:664-681`) — `jawa/pawn_gear` action=wear — the
   caller's `stuff` parameter is resolved into `sd` but never passed to `PawnApparelGenerator.GenerateApparelOfDefFor`,
   so a requested stuff is silently discarded whenever generation succeeds — the exact "accepted the request,
   silently substituted a different value" shape as the ChemfuelTank fuel-filter incident.
   Guard: pass `sd` into the generator call, or fall back to `ThingMaker.MakeThing(td, sd)` when `stuff` was explicit.

4. **`JawaBenchWorldEdit2.cs:274` (tool) / `:385-406` (risk)** — `jawa/wipe_cell` — `refunded:true` reflects
   the wiped thing's CATEGORY, not a confirmed landing; `GenPlace.TryPlaceThing` can fail silently in a crowded
   area and the tool never re-checks, so real material/item loss reports as success (the tool's own doc admits
   this and adds no verification).
   Guard: re-query the map for the expected refunded thing/minified crate and report `refundConfirmed`.

5. **`JawaBenchEventTools.cs:1210` (tool) / `:1261-1294` (risk)** — `jawa/social_marry` — destroys existing
   Lover/Spouse relations and sets Fiance **before** checking `TryStartMarriageCeremony`'s own result, then
   returns `success:true` even when `ceremonyStarted:false` — relation edits are stranded with no rollback.
   Guard: require `started`/`married` for `success`, and auto-revert the relation edits when it's false.

6. **`JawaBenchWorldTools.cs`** — a systemic pattern across at least seven world-write tools: `success:true`
   is hardcoded regardless of the actual per-item outcome —
   `:256`/`:372-382` `jawa/world_tile_set` (written may be 0),
   `:678`/`:825-846` `jawa/world_tile_import` (applied==0, all skipped),
   `:1103`/`:1201-1210` `jawa/world_links_set` (laid==0, all refused),
   `:1343`/`:1501-1514` `jawa/world_links_import` (rivers/roads==0, all unknown/refused),
   `:1792`/`:1927-1945` `jawa/world_mutators_set` (non-empty errors[], added==removed==0),
   `:2744`/`:2812-2819` `jawa/world_info_set` (every field in refused[]),
   `:496`/`:565-578` `jawa/world_view` (success regardless of `acted`, camera jump can no-op).
   Guard: derive `success` from the actual outcome count/errors in each case (e.g. `written>0 || errors.Count==0`),
   never hardcode `true`.

7. **`JawaBenchZoneTools.cs:97` (tool) / `:212-228` (risk)** — `jawa/storage_settings` — `success:true` even
   when every entry in `allow`/`disallow` lands in `refused[]` and `changed[]` is empty.
   Guard: `success = refused.Count == 0` (or require `changed.Count>0 || refused.Count==0`).

8. **`JawaBenchEventTools.cs:1131` (tool `jawa/social_gathering_start`) `:1199-1206`, and `:1298` (tool
   `jawa/ritual_start`) `:1395-1409`** — both hardcode `success:true` regardless of `started`, even though
   `ritual_start`'s own note admits `TryExecuteOn` "fails SILENTLY."
   Guard: `success = started` in both.

9. **`JawaBenchPawnTools.cs:53-68`** (helper `FindPawn`, def at `:38`, used by ~all 19 `jawa/pawn_*` write
   tools) — name lookup does `FirstOrDefault` with no ambiguity check; two same-named pawns silently resolve
   to the wrong one and the write reports success against the wrong target.
   Guard: if >1 pawn matches a name, refuse and list candidates (mirror `jawa/lock_apparel`'s substring-match guard).

10. **`JawaBenchMapTools.cs:51-64`** (shared `TryRect` helper, used by ~10 tools incl. `jawa/get_terrain_layers`,
    `jawa/set_substructure_batch`, `jawa/set_terrain_layer`, `jawa/set_deep_resource`, `jawa/designate_batch`,
    `jawa/map_zones`, `jawa/build_check`) — silently clamps w/h<1 to 1 and clips an out-of-bounds rect to
    whatever fits, with no flag distinguishing "you asked for this" from "I shrank your request."
    Guard: return the originally-requested w/h/area alongside the clipped `r.Area`.

11. **`JawaBenchStatTools.cs:111-116`** (tool `jawa/pawn_stats` `:64`) **and `:513-518`** (tool `jawa/thing_stats`
    `:368`) — the `shown` lambda swallows any `StatWorker.ShouldShowFor` exception into `false`, silently
    dropping that stat from the default listing — the exact failure the tool's own docs say named-stat lookups
    must never do.
    Guard: log/report the swallowed exception per-stat instead of folding it into "not shown."

12. **`JawaBenchZoneTools.cs:235` (tool `jawa/bill_add`) `:333-342`** — `qualityMin`/`qualityMax` use bare
    `Enum.TryParse` with no `Enum.IsDefined` and no `min<=max` check — the exact bug `jawa/configure_bill` was
    hardened against (comment at `JawaBenchJobTools.cs:536-558`) reappears unpatched on this sibling tool.
    Guard: copy `configure_bill`'s `IsDefined` + inverted-range guard into `bill_add`.

13. **`JawaBenchMapTools.cs:2186-2187`** (tool `jawa/connect_cells` `:2101`) — `isBridgeable` swallows any
    `GetAffordances` exception into `false`, so a cell that is genuinely bridgeable but throws is reported as
    "IMPOSSIBLE ... cannot be bridged" — a confidently WRONG answer, not merely an absent one.
    Guard: surface the exception text in the refusal instead of collapsing it into a negative result.

14. **`JawaBenchJobTools.cs:859` (tool `jawa/ordered_job`) `:1099-1118`** — when accepted but the requested
    job never became `curJob`, the note enumerates several *possible* causes without naming which one occurred;
    a non-playerForced FailOn kill is still indistinguishable from normal completion.
    Guard: surface the JobDriver's last `JobCondition` rather than only inferring from curJob identity.

15. **Field-name inconsistency, cross-cutting** (category 2, listed once — affects many callers):
    - `faction`/`factionName`/`defName`/`name` named three different ways across `jawa/list_pawns`,
      `jawa/list_things` (`JawaBenchTerrainTools.cs:1173-1174,5496`), `jawa/list_factions` (`:5199-5200`),
      `jawa/set_faction_relation` (`:6381-6382`).
    - "what went wrong per cell/op" named `failed`/`refused`/`problems`/`blocked` across `jawa/build_batch`
      (`JawaBenchMapTools.cs:1125`), `jawa/set_gas` (`:1772`), `jawa/designate_batch` (`:1366`),
      `jawa/connect_cells` (`:2434`/`:2228`).
    - `count` means "stats returned" in `jawa/pawn_stats` (`JawaBenchStatTools.cs:196`) but "things counted"
      (not stats — that's `statTotal`) in `jawa/thing_stats` (`:651-652`).
    - "why didn't this fully apply" named `refused[]`/`notes[]` in `JawaBenchPawnTools.cs:453-459` vs a single
      `message` string in `JawaBenchPawnKitTools.cs:251-262`.
    - "count actually changed" named `written`/`applied`/`added`/`changed`/`tilesAssigned`/`laid` across
      `JawaBenchWorldTools.cs:375,832,1929,2385,2677,1203` — only `laid` is read-back-verified, the rest are
      attempt-counted.
    Guard: pick one canonical name per concept (`factionDefName`/`factionName`, `problems[]`+`problemCount`,
    a `verified:bool` flag beside the changed-count) and apply it project-wide; this is the class the owner's
    confirmed `faction` vs `factionName` incident belongs to.

## Additional findings (lower rank, still real)

16. `JawaBenchPawnTools.cs:775-777` (`jawa/pawn_gear` wear) — `apparel.Wear()` drops conflicting worn garments
    via `CanWearTogether`, but only `equip`'s primary-slot displacement is reported in `displaced[]`; wear's
    own drops are invisible. Guard: diff `WornApparel` before/after and populate `displaced[]` for wear too.
17. `JawaBenchPawnTools.cs:855-859` (`jawa/pawn_health` add) — `AddHediff` return not checked against
    `hediffSet` afterward, unlike this file's own `equip`/`restore` verification pattern. Guard: confirm
    presence in `hediffSet.hediffs` before reporting success.
18. `JawaBenchPawnTools.cs:1104-1109` (`jawa/set_pawn_ideo` action=role) — `Precept_Role.Assign` not verified
    via `IsAssigned`, unlike the sibling `action=set` path in the same tool. Guard: check `r.IsAssigned(p)` after `Assign`.
19. `JawaBenchPawnTools.cs:1520-1533` (`jawa/pawn_psychic` psyfocus) — both sub-ops can fail into `notes[]`
    while `success:true` still returns. Guard: flip `success` false when every requested sub-action failed.
20. `JawaBenchPawnTools.cs:207-222` (`jawa/pawn_get`, no `pawn` given) — row list capped by `limit` with no
    `totalSpawned` field; a caller can't tell "exactly N pawns" from "truncated." Guard: add `totalSpawned`.
21. `JawaBenchEventTools.cs:834` (`jawa/map_fire`) `:909-920` — `success:true` hardcoded even when
    `cellsFailed == cellsTried` from real exceptions. Guard: `success = failed == 0`.
22. `JawaBenchEventTools.cs:924` (`jawa/map_skyfaller`) `:1018-1029` — `success = spawned` ignores whether
    `innerThingCarried` actually landed. Guard: fold `carried` into `success` when `innerThing` was requested.
23. `JawaBenchZoneTools.cs:620` (`jawa/royal_title`) `:713-726` — `success:true` unconditional, no read-back
    of `titleAfter`/`favorAfter` against the request. Guard: require read-back equality for `success`.
24. `JawaBenchZoneTools.cs:539` (`jawa/anomaly_knowledge`) `:592-611` — overflow receipt into
    `overflowCategory` is never independently read back. Guard: `GetKnowledge` on the overflow project too.
25. `JawaBenchMapTools.cs:419,438` (`jawa/set_terrain_layer` under/color, tool `:352`) — `changed++`
    unconditional, no before/after diff, unlike every sibling grid-writer in the file. Guard: diff
    `UnderTerrainAt`/terrain-colour before/after.
26. `JawaBenchMapTools.cs:1339,1349` (`jawa/designate_batch` action=remove, tool `:1221`) — removing a
    non-existent designation is a silent no-op with no counter (add has `alreadyPresent`). Guard: add
    `alreadyAbsent`.
27. `JawaBenchMapTools.cs:1910` (`jawa/map_zones`, tool `:1781`) — `z.CheckContiguous()` wrapped in bare
    `catch {}` after bulk `AddCell`. Guard: capture and report the exception message.
28. `JawaBenchTerrainTools.cs:514`/`:686-701` (`jawa/spawn_batch`) — `FilthMaker.TryMakeFilth` ORs multiple
    thickening passes into one bool; a pass hitting maxThickness is invisible, `spawned++`/`placedThings=count`
    still trusts the requested count. Guard: read filth thickness delta on the cell instead of trusting count.
29. `JawaBenchTerrainTools.cs:2349`/`:2538-2547` (`jawa/set_pawn_style` hairColor) — per-field `ok` hardcoded
    `true` regardless of read-back mismatch (only a `note` attached). Guard: set `ok` from actual `now == requested`.
30. `JawaBenchTerrainTools.cs:1012`/`:1125-1133` (`jawa/list_pawns` capacities) — bare `try/catch{skip}` around
    `capacities.GetLevel(cap)`, indistinguishable from a capacity the pawn genuinely lacks. Guard: collect a
    `capacityErrors` list of `{cap, exceptionType}`.
31. `JawaBenchTerrainTools.cs:3934`/`:4974,5052` (`jawa/get_defs`) — `catch { continue; }` on `f.GetValue(o)`
    reports the field identically to "no such field." Guard: emit `"(threw: <ExceptionType>)"` on catch.
32. `JawaBenchMapInfoTools.cs:213-222` (`jawa/map_info` `:105-134`) — `playerSettlementsOnThisTile` returns
    sentinel `-1` on exception, undocumented in ResultDescription as anything but "a COUNT." Same pattern at
    `JawaBenchMapTools.cs:1392-1397` (`jawa/prefab_list`, `CountPrefabThings`). Guard: document -1 explicitly
    or return null.
33. `JawaBenchMapInfoTools.cs:196-201` (`jawa/map_info`) — each tile field read without its own try/catch
    inside the outer try, so one throwing accessor blanks the whole `tileInfo` block. Guard: wrap each field
    read individually.
34. `JawaBenchStatTools.cs:293-295` (`jawa/room_get`, tool `:208`) — `room.PsychologicallyOutdoors` exception
    defaults to `false`, letting a genuinely-outdoor room leak past the `includeOutdoors=false` filter. Guard:
    on exception, exclude the room (fail-safe toward the documented default), don't include it.
35. `JawaBenchZoneTools.cs:733` (`jawa/set_stuff`, tool `:733`) `:792-793` — bare `catch (Exception) {}`/`catch {}`
    around `Notify_ColorChanged()`/`DirtyMapMesh()` with zero note or log. Guard: collect into `notes[]`.
36. `JawaBenchWorldEdit2.cs:195` (`jawa/battery_set` mode=setPct) `:229-231` — no range clamp/check on `value`
    unlike sibling modes `add`/`draw`. Guard: clamp 0-1 and report if clamped.
37. `JawaBenchWorldTools.cs:3075`/`:3123-3125` (`jawa/world_objects_add`) — collision check tests `o.def == wd`
    only, so a second map-capable object can stack on a tile already holding one — the exact collision its own
    sibling `world_settlements_import` guards via `canHaveMap`. Guard: reuse the `canHaveMap` check.
38. `JawaBenchWorldTools.cs:850`/`:940,949` (`jawa/world_tile_validate`) — documented `tolerance` parameter is
    silently ignored for `swampiness`/`pollution` (hardcoded `0.02f`). Guard: apply `tolerance` uniformly or
    document the two fields as fixed-tolerance separately.
39. `JawaBenchPawnTools.cs:772` and `:427-432` and `:362` — three separate empty `catch {}` blocks
    (`GenerateApparelOfDefFor`, `BackstoryDef.DisallowsTrait`, disabled-work-types readback) that silently
    fall back to a default rather than surfacing the exception. Guard: log/note the exception in each case
    instead of discarding it.

## Category 4 — disambiguator scorecard (spot check)

**Already good** (have a `scanned`/`refused`/`verified`-style disambiguator): `jawa/list_pawns` capacities
(partially — see #30), `jawa/set_terrain_batch`, `jawa/set_roof_batch`, `jawa/destroy_batch`,
`jawa/order_pawn`, `jawa/set_faction_relation`, `jawa/fire_quest`, `jawa/world_links_set` (`laid`, read-back
verified), `jawa/designate_batch` add path (`alreadyPresent`).

**Missing** (empty/zero is ambiguous, no disambiguator): `rimworld/get_cell_info` (things[] can be empty on a
populated cell — confirmed incident, cited in comments at `JawaBenchTerrainTools.cs:1016`,
`JawaBenchStatTools.cs:212`, `JawaBenchMapInfoTools.cs:6`, `JawaBenchTerrainTools.cs:5381,6054,6084` — no
fix present in this file set, likely lives outside JawaBench.BridgeTools), `jawa/map_info`
(`playerSettlementsOnThisTile` -1 sentinel undocumented), `jawa/prefab_list` (`CountPrefabThings` -1 sentinel
undocumented), `jawa/designate_batch` remove path (no `alreadyAbsent`), `TryRect`-based batch tools (no
"requested vs. clipped" size field).
