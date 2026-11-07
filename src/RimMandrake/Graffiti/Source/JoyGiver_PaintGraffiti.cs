using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Graffiti
{
    // Absorbed from Mlie.GraffitiMod's JoyGiver_PaintGraffiti (compiled-only,
    // no source shipped) - a fresh implementation. Modeled on the verified
    // vanilla shape (JoyGiver_Skygaze, Source/RimWorld/JoyGiver_Skygaze.cs):
    // TryGiveJob finds a target cell, hands it to JobMaker.MakeJob.
    public class JoyGiver_PaintGraffiti : JoyGiver
    {
        /// <summary>The temperament table's paint column times the hand's feel for art: an abrasive or passionate artist reaches for the
        /// brush more, a lazy or clumsy one less, a psychopath or a pawn incapable of art not at all.</summary>
        public override float GetChance(Pawn pawn)
        {
            return base.GetChance(pawn) * GraffitiTemperament.Urge(pawn);
        }

        public override Job TryGiveJob(Pawn pawn)
        {
            if (!RM_GraffitiSettings.paintingEnabled) return null;
            if (pawn.Map == null) return null;
            if (GraffitiTemperament.Urge(pawn) <= 0f) return null;
            if (!GraffitiJobUtility.TryFindWallMarkCell(pawn, out IntVec3 cell, roomCap: true)) return null;
            return JobMaker.MakeJob(def.jobDef, cell);
        }
    }
}
