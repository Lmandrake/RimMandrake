using Verse;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_SAP_SUCKER_GUILD_1. Data side of RM_CompSapSuckerRefusal —
    // see that class for the trigger and the full rationale. One shared
    // comp for the guild's two hediff-based refusals (vaulm's seal, drommath's
    // swell); the third (ollareth's scream) reuses the already-shipped,
    // content-blind RimMandrake.CreatureBehaviors.RM_CompProperties_PlantAlarm
    // instead of a new class here — see RM_SapSuckerGuild.xml's own header
    // for why that reuse is a better fit than tripling this pattern.
    public class RM_CompProperties_SapSuckerRefusal : CompProperties
    {
        // The refusal's visible expression — a sealed shell, a swollen sac.
        // Always non-null for this comp (ollareth, the no-hediff member,
        // uses RM_CompProperties_PlantAlarm instead, never this class).
        public HediffDef refusalHediff;

        // INVENTED placeholder — how "sealed"/"swollen" the animal reads
        // once bothered. FEVERWOOD_SAP_SUCKER_TUNING_1 owns the real number.
        public float refusalSeverity = 1f;

        // INVENTED placeholder — ticks between one refusal trigger actually
        // refreshing the hediff and the next. Design doc's own requirement
        // (fever_wood_fauna_roster_2026-09-23.md §2): "Do not ship a random
        // chance of refusal" — this is a cooldown, never a roll.
        public int cooldownTicks = 2500;

        public RM_CompProperties_SapSuckerRefusal()
        {
            compClass = typeof(RM_CompSapSuckerRefusal);
        }
    }
}
