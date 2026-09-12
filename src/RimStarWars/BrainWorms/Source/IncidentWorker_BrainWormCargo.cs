using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.BrainWorms
{
    /// <summary>
    /// BRAINWORM_MOD_BUILD_1, vector 2 - salvaged cargo, the Ahsoka route and the
    /// scavenger fantasy of dragging home something that hatches.
    ///
    /// Deliberately built on vanilla's own cargo-pod shape
    /// (RimWorld/IncidentWorker_ResourcePodCrash.cs) and its ResourcePod thing set:
    /// what lands is an ordinary, genuinely useful salvage haul with an egg cluster
    /// buried in it. The letter is the normal cargo-pod good news, because that is
    /// the trap - nothing about the arrival says "parasite", and the egg's own
    /// inspect string is the only warning a careful player gets.
    /// </summary>
    public class IncidentWorker_BrainWormCargo : IncidentWorker
    {
        // MOD_OPTIONS_RETROFIT_1: master toggle for this infection vector.
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!RSW_BrainWormsSettings.cargoIncidentEnabled)
            {
                return false;
            }
            return base.CanFireNowSub(parms);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = parms.target as Map;
            if (map == null)
            {
                return false;
            }

            List<Thing> things = ThingSetMakerDefOf.ResourcePod.root.Generate();

            Thing eggs = ThingMaker.MakeThing(BrainWormsDefOf.RSW_BrainWormEggCluster);
            eggs.stackCount = Rand.RangeInclusive(1, 3);
            things.Add(eggs);

            IntVec3 cell = DropCellFinder.RandomDropSpot(map);
            DropPodUtility.DropThingsNear(cell, map, things, 110, canInstaDropDuringInit: false, leaveSlag: true);

            SendStandardLetter(
                "Cargo pod crash",
                "A cargo pod has crashed nearby. Its contents are scattered around the impact site.",
                LetterDefOf.PositiveEvent,
                parms,
                new TargetInfo(cell, map));

            return true;
        }
    }
}
