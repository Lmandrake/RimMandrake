using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_BOLT_PAYOFF_1 (packet B5): "aura thought" - "depressing to
    /// be around" (design/Jawa/droid_system_spec.md section 7). Backs
    /// RSW_DW_NearBoltedDroid (HediffDefs_Droidworks.xml is the wrong file
    /// for a ThoughtDef; wired in ThoughtDefs_Droidworks.xml). Active for any
    /// pawn within radius of a spawned pawn wearing RSW_DW_RestrainingBolt -
    /// scanned live every time the mood UI asks, same as vanilla's own
    /// situational thoughts (e.g. ThoughtWorker_Cannibalism), never a
    /// persisted memory.
    /// </summary>
    public class ThoughtWorker_NearBoltedDroid : ThoughtWorker
    {
        private const float Radius = 12f;

        protected override ThoughtState CurrentStateInternal(Pawn p)
        {
            if (p?.Map == null || !p.Spawned) return ThoughtState.Inactive;
            bool nearBolted = p.Map.mapPawns.AllPawnsSpawned.Any(other =>
                other != p
                && other.Position.DistanceTo(p.Position) <= Radius
                && other.health?.hediffSet != null
                && other.health.hediffSet.HasHediff(DroidworksDefOf.RSW_DW_RestrainingBolt));
            return nearBolted ? ThoughtState.ActiveAtStage(0) : ThoughtState.Inactive;
        }
    }
}
