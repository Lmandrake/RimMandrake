# LIQUID_SINK_DRAINAGE_1 — map-edge sinks drain a canal, live-proven

Owner, 2026-09-16: "I suppose we should add Sinks too at the edge of the map that simply
provide drainage from empty canals" — the inverse of a limitless source: liquid leaving is
transferred off-map, not destroyed, and overflow stays the only other conservation
exception. Filed as new work, but three earlier FOUNDRY passes this wave (history above)
found the mechanism was **already built** under `FLOWWORKS_BUILD_PROGRAM_1` Phase 4
(`8bb7c29d2`) the same day as this filing: `RM_MapComponent_Excavation.IsSinkCell()` gates
an excavated cell within `GenGrid.NoBuildEdgeWidth` of the map edge on
`RimMandrakeFlowWorksSettings.edgeSinksEnabled`, and `ResolveComponent()` drains it before
the flow pulse into a dedicated `sinkTransferredTotal` counter, kept separate from
`overflowDestroyedTotal` by design (ruling 9: "very different rules, so they are different
counters"). No ThingDef/Comp was ever needed — a source and a sink are both terrain-only
per ruling 2/24. Offline verification (clean build, 52/52 selftests, code-review CLEAN) was
done three times over; the one gap left standing was a **live proof** that digging into the
edge band actually drains a filled channel, distinctly from the overflow path.

## What blocked the live proof, and how it was closed

`SinkTransferredTotal`/`fillGrid` are private `MapComponent` fields with no prior
`DebugAction` or bridge exposure (checked and confirmed 2026-09-19 06:XX and again
20:19 — no cheap existing observable). Building a filled channel by hand (colonist
labor) or an admin excavation shortcut were the two options on the table; both were
genuine build work, not a quick check.

**2026-09-19 (FOUNDRY, owner asked to prioritize biome-mod deploy work):** built the
admin shortcut as a proper bridge tool rather than a one-off hack, since
`RM_MapComponent_Excavation`'s whole read surface (`DepthAt`/`FillAt`/`IsExcavated`/
`IsSourceCell`/`IsSinkCell`/`SinkTransferredTotal`/`OverflowDestroyedTotal`) and its
driver-API write surface (`Deepen`, `TrySetDriverFill`) were **already public** — built
for the FloodedCanyon flood driver (`CANYON_FLOOD_ERASES_CANALS_1`, ruling 8) — so no
engine code changed, only two new reflection-coupled bridge tools
(`ce7a8b0a6`, `JawaBenchFlowWorksTools.cs`):

- `jawa/flowworks_excavation_report(x,z)` — raw read of D/F plus the two map-wide counters
- `jawa/flowworks_excavation_drive(x,z,deepenLevels,setFill)` — calls the SAME
  `Deepen()`/`TrySetDriverFill()` the flood driver uses, so it obeys the engine's own
  clamps (LAW 1, 0<=F<=D) rather than poking the grid directly

## live proof — 2026-09-19, `pits` tier quicktest (9 mods: Bridge+FlowWorks+DLC), 250x250 map

```
PROVE    dig+fill a cell inside GenGrid.NoBuildEdgeWidth(10) of the map edge, step 300
         game ticks (>= PulseIntervalTicks default floor 60), read FillAt/
         SinkTransferredTotal/OverflowDestroyedTotal before and after; a control cell
         dug+filled the same way but in the map interior (not sink-eligible) rides
         alongside as the negative control.
EXPECT   sink-band cell's fill drops toward 0 and SinkTransferredTotal climbs by the
         same amount; OverflowDestroyedTotal stays 0 (proves it is the SINK counter
         moving, not overflow); the interior control cell's fill is UNCHANGED (proves
         the drain is edge-gated, not "everything leaks").
LIES     if MapComponentTick's pulse had not fired yet (paused, or fewer ticks than
         PulseIntervalTicks), a false negative would read as "sinks don't work" rather
         than "the pulse hasn't run" — mitigated by stepping 300 ticks against a 60-tick
         floor and reading engine-owned counters, not the terrain looks.
```

Result (cell (5,50), sink-band; control (125,125), interior; both dug to depth 1, filled
to 1, on a fresh quicktest map, `ticksGame` 1 -> 301 via `rimworld/step_game_ticks`):

| | before | after |
|---|---|---|
| sink-band cell `fill` | 1 | **0** |
| `sinkTransferredTotal` (map-wide) | 0.0 | **1.0** |
| `overflowDestroyedTotal` (map-wide) | 0.0 | 0.0 (unchanged) |
| control cell `fill` | 1 | 1 (unchanged) |

Every number moved exactly as predicted, nothing moved that shouldn't have. This is a
**quicktest finding** (fresh generated map, not the campaign) — it proves the MECHANISM,
which is what this item asked for; it says nothing about the campaign's own terrain.

## status — CLOSED, 2026-09-19 (FOUNDRY)

Mechanism built (2026-09-16, `8bb7c29d2`), offline-verified three times, now live-proven
on the exact axis that was missing: a filled channel in the edge band drains distinctly
from overflow, and an equivalent non-edge channel does not. Nothing left owed by this
item. The two new bridge tools stay shipped (`jawa/flowworks_excavation_report` /
`_drive`) as the reusable test surface for any future FlowWorks live-proof.
