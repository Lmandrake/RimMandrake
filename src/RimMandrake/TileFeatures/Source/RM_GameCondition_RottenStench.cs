using RimWorld;
using Verse;

namespace RimMandrake.TileFeatures
{
    /// <summary>RM_RottenStench (permanent, from the RM_RottenStench tile feature): every breathing flesh pawn on an affected
    /// map carries the RM_RottenStench hediff, refreshed while it stays. The weather switch in Mod Settings stops it at once.</summary>
    public class RM_GameCondition_RottenStench : GameCondition
    {
        private const int Interval = 2500;

        public override void GameConditionTick()
        {
            base.GameConditionTick();
            if (Find.TickManager.TicksGame % Interval != 0) return;
            HediffDef hd = RM_TileFeatureDefOf.RM_RottenStench;
            if (hd == null) return;
            bool on = RM_TileFeaturesSettings.weatherEnabled;
            foreach (Map map in AffectedMaps)
            {
                foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
                {
                    if (!on)
                    {
                        // Switched off: the stench stops at once, so the hediff (which lasts two days) goes too.
                        Hediff old = p?.health?.hediffSet?.GetFirstHediffOfDef(hd);
                        if (old != null) p.health.RemoveHediff(old);
                        continue;
                    }
                    if (p?.RaceProps == null || !p.RaceProps.IsFlesh || p.Dead) continue;
                    if (!p.health.capacities.CapableOf(PawnCapacityDefOf.Breathing)) continue;
                    Hediff h = p.health.hediffSet.GetFirstHediffOfDef(hd) ?? p.health.AddHediff(hd);
                    HediffComp_Disappears d = h?.TryGetComp<HediffComp_Disappears>();
                    if (d != null) d.ticksToDisappear = d.Props.disappearsAfterTicks.max;
                }
            }
        }
    }
}
