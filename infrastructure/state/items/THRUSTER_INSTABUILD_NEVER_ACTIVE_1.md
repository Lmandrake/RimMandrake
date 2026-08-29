# THRUSTER_INSTABUILD_NEVER_ACTIVE_1 — tool-built thrusters link but never contribute range

Measured 2026-08-28, 582-mod list, scratch quicktest. Three thrusters (SmallThruster x2,
LargeThruster x1; build_batch AND god-mode designator; both pad edges; exclusion zones
verified empty of foundations/things/roof; rot verified 0 via jawa/export_things): all end
LINKED (engine missingComponents clears) and NEVER ACTIVE — engine GravshipRange stays 0.
The campaign ship's hand-built thrusters on the same list give range 40. No log errors.
Suspect a mod patch (VGE re-categorizes thrusters into Platform and may patch activity/stat).

## verify
Same build sequence on the 13-mod minimal list (modlist_swap): if range appears, bisect the
mod; if not, the vanilla condition analysis in GRAVSHIP_LAUNCH_TRAVEL_1's session missed
something — instrument CompGravshipThruster.CanBeActive with a companion read tool.

## Note 2026-08-28 (BENCH): VEF patches this exact machinery
`vendor/mod_sources/VanillaExpandedFramework-main/Source/VEF/Buildings/Harmony/` transpiles
`CompAffectedByFacilities.PotentialThingsToLinkTo` / `CanPotentiallyLinkTo` (facility
"equivalence") and patches `GravshipUtility.PreLaunchConfirmation`. Start the bisect there.

## 2026-08-29 (FOUNDRY): mechanism fully mapped from 1.6 source; live repro contaminated by
## map-side accidents before a clean confirmation — writing up what's proven, not closing

**The full chain, read from source, not guessed:**
`Building_GravEngine.MaxLaunchDistance` reads `StatDefOf.GravshipRange`, computed by
`CompAffectedByFacilities.GetStatOffset` (`Source/RimWorld/CompAffectedByFacilities.cs:466`):
sums each linked facility's `StatOffsets[GravshipRange]` **only when
`IsFacilityActive(facility)`** — which is just `facility.TryGetComp<CompFacility>().CanBeActive`.
For a thruster that resolves to `CompGravshipThruster.CanBeActive`
(`Source/RimWorld/CompGravshipThruster.cs:39`): `base.CanBeActive` (engine in range AND
`OnValidSubstructure`/`LooselyConnectedToGravEngine`) `&& !Blocked && !BrokenDown &&
LinkedBuildings.NonEmpty() && outdoors == true`. `Blocked` checks a 1×5 exclusion zone
(`exclusionAreaSize`/`Offset` on `CompProperties_GravshipThruster`, read from the live dump:
size `{x:1,y:0,z:5}`, offset `{x:0,y:0,z:-5}`) for any `blockWind` thing or substructure
foundation; `outdoors` checks the cells along the thruster's facing edge are
`!Room.UsesOutdoorTemperature`.

**`missingComponents` clearing is NOT the same check as thruster activity** — it comes from
`Building_GravEngine.GravshipComponents`, which is `AffectedByFacilities.LinkedFacilitiesListForReading`
filtered to things with a `CompGravshipFacility` — i.e. it only proves the LINK exists, not
that `CanBeActive` is true. The item's own "engine missingComponents clears" observation is
consistent with the thruster being linked but still inactive; these were never the same fact.

**No new instrumentation was needed** — `jawa/inspect_string` already surfaces
`CompGravshipThruster.CompInspectStringExtra()` verbatim ("Not functional: Blocked by X" /
"...must be outside" / "Not connected to grav engine"), which names the exact failing gate.
This satisfies the item's own `verify` ask; do not build a new companion tool for this.

**Live repro, on a fresh quicktest map (Alpha Biomes mountain/desert), bridge-driven:**
- First attempts: `SmallThruster` built adjacent to leftover `AB_Obsidianstone` mineable rock
  (its own `blockWind=true`) inside the 1×5 exclusion zone → correctly reported "Blocked by
  onyxglass". This is a REAL vanilla mechanic (mineable ore blocks the exhaust the same as any
  wall), not a bug — but it means **build_batch-placed thrusters on natural/unmined terrain are
  very easy to place with an unnoticed blocker in the 5-cell exclusion zone**, which the
  item's own "exclusion zones verified empty" claim may not have checked exhaustively (5 cells
  deep, not 1).
- After clearing the zone and rebuilding: thruster read **"Not connected to grav engine"**
  while the ENGINE's `missingComponents` had already dropped `Thruster` from its list — the
  asymmetry named above, reproduced live, matching the item's exact complaint shape.
- Stepping game ticks (`rimworld/step_game_ticks`, needed since `RecalculateBlocked`/
  `RecalculateOutdoors` only refresh on `CompTickRare`, a periodic tick — a build_batch/
  god-mode INSTABUILD skips whatever a normal timed construction would let settle) to let the
  state resolve further **destroyed both buildings** — a mountain roof collapse from an
  overly broad `jawa/destroy_batch` clearing supporting rock nearby, not a reproduction of the
  target bug. Confirmed via `jawa/drain_log`: a genuinely separate, real, currently-firing bug
  — `VanillaGravshipExpanded.SectionLayer_SubstructureProps_Regenerate_Patch`'s transpiler
  throws `IndexOutOfRangeException` in `SectionLayer_GravshipHull.ShouldDrawCornerPiece` via
  `EdificeGrid.get_Item` when a substructure cell sits near the map edge — a RENDER-layer crash
  (`vendor/mod_sources/VanillaGravshipExpanded-main/Source/HarmonyPatches/
  SectionLayer_SubstructureProps_Regenerate_Patch.cs`), unrelated to thruster activity logic,
  worth its own item if it recurs on the real campaign ship.

## What is NOT yet proven
Whether the "linked but inactive" state I reproduced would have resolved itself given a clean
tick or two (facility auto-link and `CanBeActive` are two different, only loosely-coupled
recalculations — plausible it's just a timing gap that closes within seconds of real play) or
is a persistent state VEF's facility-equivalence patch causes to never resolve. The buildings
were destroyed before this could be checked cleanly.

## Recommended next repro (not done here — bridge session ended on this line of investigation)
Build on FLAT, non-mountain terrain (avoid mineable-rock false "Blocked" reads and roof-collapse
risk entirely), well inside the map bounds (avoid the VGE edge-crash), and after confirming
"Not connected to grav engine" with `jawa/inspect_string`, step a SMALL number of ticks (60,
not 500) and re-read — narrow whether the asymmetry is transient or persistent before touching
anything else nearby.

## criteria
- [ ] Confirm whether the engine/thruster link asymmetry is transient (resolves on its own
      within a handful of ticks) or persistent (needs VEF's facility-equivalence patch fixed
      or worked around).
- [ ] If persistent: read `VanillaExpandedFramework`'s `CanPotentiallyLinkTo`/
      `PotentialThingsToLinkTo` transpiler against this exact call chain and name the line.
