// Fires from the quest via QuestNode_CreateIncidents once the Groundcaller's
// resonant call completes. Spawns RUT_LongHunger, which handles its own eruption
// and tremor pulses (see LongHungerThing.cs). API citations: RCellFinder /
// GenSpawn precedent (RimSage, decompiled 1.6) - same pattern GenStep_Monolith,
// GenStep_Turrets and QuestNode_Root_AncientSignalActivation already use to find
// a standable, unfogged cell near a map's center.
using RimWorld;
using Verse;

namespace LongHunger
{
    public class IncidentWorker_LongHungerSurfaces : IncidentWorker
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            return map != null
                && RCellFinder.TryFindRandomCellNearTheCenterOfTheMapWith(
                    (IntVec3 x) => x.Standable(map) && !x.Fogged(map),
                    map,
                    out _);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            if (map == null)
            {
                return false;
            }
            if (!RCellFinder.TryFindRandomCellNearTheCenterOfTheMapWith(
                    (IntVec3 x) => x.Standable(map) && !x.Fogged(map),
                    map,
                    out IntVec3 cell))
            {
                return false;
            }

            GenSpawn.Spawn(ThingDef.Named("RUT_LongHunger"), cell, map);

            // Plain literals, not .Translate() - no Keyed translation file
            // exists for this mod yet and guessing that shape wrong is a
            // worse failure than skipping localization for a v1 (see the
            // rimworld-quests skill's TKey-in-RulePack precedent used
            // instead, in the QuestScriptDef, where the letter text
            // actually needs it).
            Find.LetterStack.ReceiveLetter(
                "The Long Hunger surfaces",
                "The ground breaks open where you struck the drum. Something vast is moving under the sand.",
                LetterDefOf.ThreatBig,
                new LookTargets(cell, map));

            return true;
        }
    }
}
