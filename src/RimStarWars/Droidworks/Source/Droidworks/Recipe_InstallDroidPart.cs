using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_FINE_PARTS_1 (packet B4a). One RecipeDef per effectful part
    /// type (Leg/Manipulator/Sensor/Motivator/Servo) carries this extension
    /// naming its own Inferior/Standard/Superior HediffDef trio
    /// (Effects_Droidworks.xml) - one C# class serves all five, same
    /// "parametrize by DefModExtension" shape DroidworksExtension already
    /// uses for the race side.
    /// </summary>
    public class DroidPartEffectExtension : DefModExtension
    {
        public HediffDef inferior;
        public HediffDef standard;
        public HediffDef superior;
    }

    /// <summary>
    /// Reads the consumed RSW_DW_Part_* item's CompQuality and grants the
    /// matching tier's hediff ("superior/inferior parts change stats",
    /// section 1.3) - Awful/Poor -> inferior, Normal/Good -> standard,
    /// Excellent/Masterwork/Legendary -> superior. Replaces, never stacks:
    /// installing a new part of the same kind removes whichever of the
    /// three tier hediffs is already present first.
    /// </summary>
    public class Recipe_InstallDroidPart : Recipe_Surgery
    {
        public override void ApplyOnPawn(Pawn pawn, BodyPartRecord part, Pawn billDoer,
                                         List<Thing> ingredients, Bill bill)
        {
            DroidPartEffectExtension ext = recipe.GetModExtension<DroidPartEffectExtension>();
            if (ext == null) return;

            QualityCategory quality = QualityCategory.Normal;
            foreach (Thing t in ingredients)
            {
                CompQuality cq = t.TryGetComp<CompQuality>();
                if (cq != null) { quality = cq.Quality; break; }
            }

            HediffDef toAdd;
            switch (quality)
            {
                case QualityCategory.Awful:
                case QualityCategory.Poor:
                    toAdd = ext.inferior;
                    break;
                case QualityCategory.Excellent:
                case QualityCategory.Masterwork:
                case QualityCategory.Legendary:
                    toAdd = ext.superior;
                    break;
                default:
                    toAdd = ext.standard;
                    break;
            }
            if (toAdd == null) return;

            Hediff existing = pawn.health.hediffSet.hediffs.FirstOrDefault(h =>
                h.def == ext.inferior || h.def == ext.standard || h.def == ext.superior);
            if (existing != null) pawn.health.RemoveHediff(existing);

            pawn.health.AddHediff(toAdd);
        }
    }
}
