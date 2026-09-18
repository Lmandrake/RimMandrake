using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1. The one species/immunity gate every hazard in
    // this kit shares, so "who does this hurt" is answered identically by the
    // gas, the area-attack hediff comp and the weather condition rather than
    // three subtly different re-implementations (which is exactly the
    // duplication the source review flagged in the donor family).
    public static class HazardTargeting
    {
        public static bool Affects(Pawn pawn, PawnTargetKind kind,
                                   List<ThingDef> immuneThingDefs,
                                   List<PawnKindDef> immunePawnKinds)
        {
            if (pawn == null || !pawn.Spawned || pawn.Dead)
            {
                return false;
            }

            // Vanilla's own opt-out for pawns that game conditions must not
            // touch (quest-critical and scripted kinds set it). Honoured here
            // so a hazard can never softlock a quest.
            if (pawn.kindDef != null && pawn.kindDef.immuneToGameConditionEffects)
            {
                return false;
            }

            if (immuneThingDefs != null && immuneThingDefs.Contains(pawn.def))
            {
                return false;
            }

            if (immunePawnKinds != null && pawn.kindDef != null && immunePawnKinds.Contains(pawn.kindDef))
            {
                return false;
            }

            RaceProperties race = pawn.RaceProps;
            if (race == null)
            {
                return false;
            }

            switch (kind)
            {
                case PawnTargetKind.Flesh:
                    return race.IsFlesh;
                case PawnTargetKind.Mechanical:
                    return race.IsMechanoid;
                default:
                    return true;
            }
        }

        public static bool PlantAffected(Thing plant, List<ThingDef> immuneThingDefs)
        {
            if (plant == null || plant.Destroyed)
            {
                return false;
            }

            if (immuneThingDefs != null && immuneThingDefs.Contains(plant.def))
            {
                return false;
            }

            return true;
        }

        // ROT_SHEEN_WEATHER_1. Shared with RM_GameCondition_WetBulb's own
        // SumApparelProtection (that class predates this shared home and
        // keeps its private copy rather than being touched by this pass) —
        // an "Apparel"-category StatDef has no vanilla auto-aggregation onto
        // a pawn stat (ArmorUtility is the only vanilla reader, and it reads
        // per-apparel-item, not per-pawn), so any consumer summing one across
        // a worn outfit must do it itself. Not clamped here — callers decide
        // their own clamp/floor (e.g. a "gear never fully immunizes" floor).
        public static float SumApparelStat(Pawn pawn, StatDef stat)
        {
            if (stat == null || pawn?.apparel == null)
            {
                return 0f;
            }

            List<Apparel> worn = pawn.apparel.WornApparel;
            float total = 0f;
            for (int i = 0; i < worn.Count; i++)
            {
                total += worn[i].GetStatValue(stat);
            }

            return total;
        }
    }
}
