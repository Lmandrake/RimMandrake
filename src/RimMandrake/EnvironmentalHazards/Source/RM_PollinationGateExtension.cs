using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_KARRATHIL_POLLINATION_GATE_1 — "the disease vector and the
    // mangals' only pollinator, one and the same swarm. You cannot have the
    // trees without the fever" (design/Jawa/worldbuilding/biomes/
    // the_miasma.md §4; miasma_fauna_roster_2026-09-23.md §3/§7).
    //
    // Desktop engine check (this item, this pass, against the real
    // decompiled 1.6/Odyssey source, RimSage confirmed connected this
    // session): wild-plant REPRODUCTION (new individuals appearing, both at
    // initial map-gen seeding and every later regrowth roll) is entirely
    // decided by the per-map `RimWorld.WildPlantSpawner` singleton, never by
    // anything on the `Plant` instance itself — `Plant` exposes no
    // reproduction-time hook a comp could veto (its own virtual surface is
    // Growth/GrowthRate/LifeStage, which governs an ALREADY-SPAWNED
    // individual's maturing, not whether a new one is chosen). So the
    // roster's own "UNMEASURABLE" flag was right: there is no comp for
    // this. There IS a real, already-used choke point:
    // `WildPlantSpawner.CalculatePlantsWhichCanGrowAt` builds the candidate
    // list for a cell before any weight is rolled — the same private method
    // `RM_LeachmossWildSpawnGatePatch` (DESERT_LEACHMOSS_BUILD_1, this same
    // file's sibling) already patches to drop a single hardcoded defName.
    // This extension generalizes that choke point into a data-driven
    // gate: a plant carrying it is dropped from the candidate list outright
    // (never merely taxed) whenever no live individual of `pollinatorRace`
    // is anywhere on the map — a real, binary "cannot reproduce," matching
    // the roster's own "must be able to FAIL flowering, not just tax it."
    //
    // Deliberately MAP-WIDE presence, not per-cell proximity: the sheet's
    // own bargain is "you cannot have the trees without the fever [swarm on
    // this map at all]," not "without a swarm within N tiles of this
    // exact seedling," and `map.listerThings.ThingsOfDef(race)` is an
    // already-indexed O(1) count (the same idiom `WildPlantSpawner.
    // PlantChoiceWeight` itself uses for `plantDef`) — a per-cell radius
    // scan would be new, uncached, per-candidate-cell cost added to a loop
    // that already runs many times per tick. An EXISTING, already-mature
    // stand of the gated plant is never touched by this — only whether a
    // NEW individual can be chosen to spawn; a swarm's death does not kill
    // the canopy, it only stops the canopy replacing itself, exactly the
    // "measurably worse, not zero" shape the item's own verify step asks
    // for on a short live test.
    //
    //   <li MayRequire="mandrake.rm.environmentalhazards" Class="RimMandrake.EnvironmentalHazards.RM_PollinationGateExtension">
    //     <pollinatorRace>RUT_Karrathil</pollinatorRace>
    //   </li>
    //
    // Content decision (the item's own words: "not pre-judged here"): wired
    // originally onto the two donor mangal ThingDefs the biome's flora
    // roster (miasma_flora_roster_2026-09-23.md §3) calls "the mangals (the
    // canopy)" — `AB_MangroveTree`/`AB_ParasiticMangrove`, not
    // `AB_MangrovePalm` (roster's own RM_Ilbareen row recasts that species
    // around dying-in-place as a salt-line gauge, a different mechanism from
    // the flowering bargain). 🔴 MIASMA_FAUNA_FLOOR_ROSTER_1 has since added
    // the same modExtension onto RM_Thessamor/RM_Quennath (MIASMA_FLORA_ROSTER_1's
    // real replacements for those two donor rows in mandrake.rm.miasma) —
    // both pairs of operations now live in RUT_Miasma_PollinationGate.xml,
    // the AB_ pair for the frozen campaign twin's still-live wildPlants and
    // the RM_ pair for the franchise-free mod's own flora.
    public class RM_PollinationGateExtension : DefModExtension
    {
        public ThingDef pollinatorRace;

        public override System.Collections.Generic.IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (pollinatorRace == null)
            {
                yield return "RM_PollinationGateExtension has no pollinatorRace set — "
                    + "this plant would silently never gate.";
            }
        }
    }
}
