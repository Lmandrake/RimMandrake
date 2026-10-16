using RimWorld;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.Contagion
{
    // CONTAGION_MECHANICS_BUILD_1 — Contagion mulch (owner Q4, 2026-10-15: plain fertilizer only). The Unfinished already
    // dissolve on death through vanilla DeathActionProperties_Vanish (slime, no corpse); this keeps that exactly and adds a
    // small heap of RM_ContagionMulch where the body was. Item and floor: Defs/ThingDefs/RM_ContagionMulch.xml.
    public class DeathActionProperties_RM_VanishToMulch : DeathActionProperties_Vanish
    {
        public ThingDef mulchDef;
        public IntRange mulchCountRange = new IntRange(2, 4);

        public DeathActionProperties_RM_VanishToMulch()
        {
            workerClass = typeof(DeathActionWorker_RM_VanishToMulch);
        }
    }

    public class DeathActionWorker_RM_VanishToMulch : DeathActionWorker_Vanish
    {
        public override void PawnDied(Corpse corpse, Lord prevLord)
        {
            // Read where the body lies BEFORE the vanilla vanish destroys the corpse.
            Map map = corpse?.MapHeld;
            IntVec3 cell = corpse != null ? corpse.PositionHeld : IntVec3.Invalid;
            base.PawnDied(corpse, prevLord);
            DeathActionProperties_RM_VanishToMulch p = props as DeathActionProperties_RM_VanishToMulch;
            if (p != null) RM_ContagionMulchUtility.Drop(p.mulchDef, p.mulchCountRange.RandomInRange, cell, map);
        }
    }

    public static class RM_ContagionMulchUtility
    {
        // Places count mulch near cell. Nothing when the setting is off, the def or map is missing, or count <= 0.
        public static void Drop(ThingDef def, int count, IntVec3 cell, Map map)
        {
            if (!RM_ContagionSettings.mulchDropsEnabled || def == null || map == null || count <= 0 || !cell.IsValid) return;
            while (count > 0)
            {
                Thing t = ThingMaker.MakeThing(def);
                t.stackCount = count > def.stackLimit ? def.stackLimit : count;
                count -= t.stackCount;
                GenPlace.TryPlaceThing(t, cell, map, ThingPlaceMode.Near);
            }
        }
    }
}
