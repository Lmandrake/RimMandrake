using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.ScavengerEvents
{
    /// <summary>
    /// RUT_SCAVENGEREVENTS_BUILD_1, mechanism 2 of 8 (mechanism reference:
    /// infrastructure/state/items/RUT_SCAVENGEREVENTS_BUILD_1.md). Unconditional:
    /// one drop pod holding a Hyperweave survival outfit, four survival meals
    /// and an autopistol. Ported behavior-not-bugs from
    /// MoreIncidents.MOIncidentWorker_SurvivalPod -- same fixed contents, same
    /// GetNamedSilentFail degrade-quietly pattern for the stuff def (Hyperweave
    /// is Royalty content and may not always be active).
    /// </summary>
    public class IncidentWorker_SurvivalPod : IncidentWorker
    {
        private const int DropRadius = 110;

        private static ThingDef hyperweave;
        private static bool hyperweaveResolved;

        private static ThingDef Hyperweave
        {
            get
            {
                if (!hyperweaveResolved)
                {
                    hyperweave = DefDatabase<ThingDef>.GetNamedSilentFail("Hyperweave");
                    hyperweaveResolved = true;
                }
                return hyperweave;
            }
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            var map = (Map)parms.target;
            ThingDef stuff = Hyperweave;

            var contents = new List<Thing>
            {
                ThingMaker.MakeThing(ThingDef.Named("Apparel_Pants"), stuff),
                ThingMaker.MakeThing(ThingDef.Named("Apparel_BasicShirt"), stuff),
                ThingMaker.MakeThing(ThingDef.Named("Apparel_Jacket"), stuff),
                ThingMaker.MakeThing(ThingDef.Named("Apparel_Tuque"), stuff),
                ThingMaker.MakeThing(ThingDef.Named("MealSurvivalPack")),
                ThingMaker.MakeThing(ThingDef.Named("MealSurvivalPack")),
                ThingMaker.MakeThing(ThingDef.Named("MealSurvivalPack")),
                ThingMaker.MakeThing(ThingDef.Named("MealSurvivalPack")),
                ThingMaker.MakeThing(ThingDef.Named("Gun_Autopistol")),
            };

            IntVec3 dropSpot = DropCellFinder.RandomDropSpot(map);
            // Positional, matching the decompiled call exactly (radius=110,
            // then leaveSlag/canRoofPunch/forbid/allowFogged/? in the donor's
            // own bool order) rather than guessing named-parameter semantics.
            DropPodUtility.DropThingsNear(dropSpot, map, contents, DropRadius, false, false, true, true, true, null);

            Find.LetterStack.ReceiveLetter(
                "RUT_SurvivalPod".Translate(),
                "RUT_SurvivalPodDesc".Translate(),
                LetterDefOf.PositiveEvent,
                new TargetInfo(dropSpot, map));

            return true;
        }
    }
}
