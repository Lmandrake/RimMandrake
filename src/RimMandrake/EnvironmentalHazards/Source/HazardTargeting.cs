using System.Collections.Generic;
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
    }
}
