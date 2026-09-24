using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_TAR_NASTINESS_1 (item spec §2). The giver half of the tarred-pawn
    // mechanic: RM_HediffComp_CarriedFilthExposure only tunes a hediff a
    // pawn already carries, so this MapComponent is what actually hands it
    // out the moment a pawn's own Pawn_FilthTracker starts carrying the
    // configured filth def. Auto-instantiated per map by the engine
    // (Verse/Map.cs, no XML wiring needed) — same shape
    // RM_MapComponent_WarmGround/RM_MapComponent_LivingRegrowth already use
    // in this assembly. Fully re-derivable from what pawns are currently
    // carrying (unlike LivingRegrowth's own Scribed bole state), so nothing
    // here needs ExposeData: a save/reload just re-notices on its next
    // scan.
    public class RM_MapComponent_CarriedFilthHediffLink : MapComponent
    {
        public RM_MapComponent_CarriedFilthHediffLink(Map map)
            : base(map)
        {
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (!RM_EnvironmentalHazardsSettings.tarredHediffEnabled)
            {
                return; // mod option: nobody newly tarred gets the hediff; carriers already afflicted keep whatever the comp above is still doing
            }

            RM_CarriedFilthHediffExtension ext = map.Biome?.GetModExtension<RM_CarriedFilthHediffExtension>();
            if (ext == null || ext.filthDef == null || ext.hediffDef == null)
            {
                return;
            }

            int interval = ext.scanIntervalTicks > 0 ? ext.scanIntervalTicks : 250;
            if (Find.TickManager.TicksGame % interval != 0)
            {
                return;
            }

            var pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn pawn = pawns[i];
                if (pawn?.filth == null || pawn.health?.hediffSet == null || pawn.Dead)
                {
                    continue;
                }

                if (pawn.health.hediffSet.HasHediff(ext.hediffDef))
                {
                    continue; // already carries it — RM_HediffComp_CarriedFilthExposure drives severity from here
                }

                if (!IsCarrying(pawn, ext.filthDef))
                {
                    continue;
                }

                Hediff hediff = pawn.health.AddHediff(ext.hediffDef);
                if (hediff != null)
                {
                    hediff.Severity = ext.initialSeverity;
                }
            }
        }

        private static bool IsCarrying(Pawn pawn, ThingDef filthDef)
        {
            var carried = pawn.filth.CarriedFilthListForReading;
            for (int i = 0; i < carried.Count; i++)
            {
                if (carried[i]?.def == filthDef)
                {
                    return true;
                }
            }
            return false;
        }
    }
}
