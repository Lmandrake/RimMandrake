using RimWorld;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // GELATINOUSSLIME_GLURRO_SALVE_1: the glurro salve SLOWS slimification, never stops it (the
    // antidote stays the only cure). Applying either item gives the patient RM_GlurroSalved at the
    // item's strength; HediffComp_Slimification multiplies its GROWTH rate by (1 - strength) while
    // the hediff lasts. Strength decays on its own (the hediff's severityPerDay), so the slowing
    // fades. All numbers // INVENTED.
    public class GlurroSalveExtension : DefModExtension
    {
        public float strength = 0.5f;   // initial slowing fraction: 0.5 = growth at half speed
    }

    public static class GlurroSalveUtility
    {
        public const float MaxStrength = 0.8f;   // never reaches 1: the clock is slowed, not stopped

        // Growth-rate multiplier for a pawn. 1 = unaffected. Honours the glurroSalve setting.
        public static float GrowthFactor(Pawn pawn)
        {
            if (!SlimeSettings.glurroSalve || pawn == null || pawn.health == null) return 1f;
            HediffDef def = DefDatabase<HediffDef>.GetNamedSilentFail("RM_GlurroSalved");
            if (def == null) return 1f;
            Hediff h = pawn.health.hediffSet.GetFirstHediffOfDef(def);
            if (h == null) return 1f;
            return 1f - UnityEngine.Mathf.Clamp(h.Severity, 0f, MaxStrength);
        }
    }

    // Administered like the antidote (CompTargetable_SinglePawn + target effect), so a doctor can
    // salve a downed patient. Consumes one item.
    public class CompTargetEffect_GlurroSalve : CompTargetEffect
    {
        public override void DoEffectOn(Pawn user, Thing target)
        {
            Pawn patient = target as Pawn;
            if (patient == null || patient.Dead || patient.health == null) return;
            GlurroSalveExtension ext = parent.def.GetModExtension<GlurroSalveExtension>();
            HediffDef def = DefDatabase<HediffDef>.GetNamedSilentFail("RM_GlurroSalved");
            if (ext == null || def == null) return;

            Hediff h = patient.health.hediffSet.GetFirstHediffOfDef(def);
            if (h == null)
            {
                h = HediffMaker.MakeHediff(def, patient);
                h.Severity = ext.strength;
                patient.health.AddHediff(h);
            }
            else if (h.Severity < ext.strength)
            {
                h.Severity = ext.strength;   // a stronger dose refreshes; a weaker one never downgrades
            }
            Messages.Message(patient.LabelShortCap + " is salved. The film will read more slowly for a while.",
                             patient, MessageTypeDefOf.PositiveEvent, false);
            if (!parent.Destroyed) parent.SplitOff(1).Destroy();
        }
    }
}
