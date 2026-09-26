# SUMP_TAR_FIRE_NETWORK_1 — network fire with gate firebreaks, and wiring the belch to glass-front cooling

Split out of `SUMP_TAR_HYDROLOGY_1` (FOUNDRY, 2026-09-26) — two of that
item's six sub-mechanisms that need either unbuilt hardware, a live burn
test, or an edit to a contended assembly, none of which fit that pass's
offline-only, uncontended-folders scope.

## what this item owns

1. **Network fire with gate firebreaks** (`SUMP_TAR_HYDROLOGY_1` ruling 5):
   "Lit tar propagates along connected liquid — a lit canal burns to its
   gate, a lit pool to its edges. Gate placement is life-and-death craft; a
   belch during a moat-burn is a genuine catastrophe."
   - `LiquidIgnitionMapComponent` (`Source/LiquidTypes/LiquidIgnition.cs`,
     `mandrake.rm.flowworks`) is a real, compiling PROTOTYPE — off by
     default, and its own header says outright "has never ticked inside a
     running game." It only proves the trigger-gated shape (adjacent real
     `Fire` Thing -> `FireUtility.TryStartFireIn`), not propagation-along-a-
     network or a stop-at-a-gate rule.
   - Tar is NOT flagged flammable in the registry today
     (`RM_Liquid_Tar`/`RM_LiquidProperties` on `RM_TarShallow`/`RM_TarDeep`
     carry no `flammable`/`igniteTemp`). Wiring it needs the SAME careful
     calibration `FLOWWORKS_BUILD_PROGRAM_1` Phase 6 flags for propane:
     terrain `Flammability` must stay near-zero so vanilla's own
     `Fire.TrySpread` cannot spontaneously ignite it (hard ban #4, "no
     ignition without a thermal or electrical trigger"), with the real
     ignition gate living in code, not the stat.
   - **Gates do not exist as hardware at all.** `FLOWWORKS_BUILD_PROGRAM_1`
     Phase 8 ("sluice gates, which retire the leave-the-last-cell-undug
     trick and give the defense spine a real trigger") is unbuilt. A
     firebreak needs a real placeable gate ThingDef + a comp that can be
     open/closed, and fire-propagation logic that treats a closed gate as a
     hard stop along the connected-liquid graph.
   - `FLOWWORKS_BUILD_PROGRAM_1` Phase 6's own line: "a 200-cell detonation
     means many simultaneous blasts — drive them centrally from the
     component; do not spawn a Thing per cell." A tar canal fire is the
     same shape (many cells, one network) and needs the same centrally-
     driven design, not a `Fire` Thing per burning cell.
   - Needs a live burn test before shipping (fire spreading wrong on a tar
     network is the kind of defect that reads as a crash-adjacent
     catastrophe, not a cosmetic miss).

2. **Wire the Sump belch incident to `SUMP_TAR_HYDROLOGY_1`'s new
   glass-cooling mechanism.** That item built the generic FlowWorks engine
   piece (`FluidDef.coolsToGlassEdge`, `Flood_FlowWorks.CoolFrontToGlass()`,
   `RM_TarGlass`) but explicitly did NOT touch
   `RUT_IncidentWorker_TarPitBelch.cs`
   (`src/RimMandrake/EnvironmentalHazards/Source/`, contended that session).
   That class's own header already names the intended swap verbatim: "find
   epicenter -> flood pulse," replacing the current
   `RM_TarCoatingUtility.CoatRadius` filth-splash call with spawning a real
   `Flood_FlowWorks` release seeded at the epicenter using `RM_Fluid_Tar` —
   at which point the new glass-cooling mechanism applies automatically with
   NO further change needed to the `IncidentDef`, the settings toggle, or
   the biome restriction. This is a small, well-scoped edit once
   `EnvironmentalHazards` is not contended.

## what NOT to do

- Do not build gates as a one-off Sump mechanic. `FLOWWORKS_BUILD_PROGRAM_1`
  Phase 8 owns sluice gates as a cross-liquid FlowWorks hardware piece;
  build there and let tar consume it, the same way canal-work itself is
  generic.
- Do not flip `RM_Liquid_Tar.flammable = true` without also working out the
  terrain-side `Flammability` stat carefully (see above) — a naive flip
  risks vanilla's own fire spread igniting tar on its own schedule, which is
  the exact hard-ban-#4 violation `LiquidIgnition.cs`'s header spends most
  of its length avoiding for propane.

## verify

Quicktest/live: a lit canal of tar burns along its own connected network and
stops dead at a closed gate; an open gate lets it through; a belch mid-burn
does not silently no-op the fire; a fresh belch (once wired) leaves a
visible glass rim after its flood recedes.

## criteria

Tar is genuinely dangerous to burn and genuinely controllable with gates —
the "gate placement is life-and-death craft" ruling is playable, not just
described.
