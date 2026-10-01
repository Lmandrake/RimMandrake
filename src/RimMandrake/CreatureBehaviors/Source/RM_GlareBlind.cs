using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_GLARE_BLIND_GOGGLES_1 — glare-blind, race-gated by GENE.
    //
    // Owner, typed: "the sun protection for the eyes is great for races that
    // need it, but the Jawa won't need it, but the slaves might". On a biome
    // whose RM_SunHeatExtension names a glareBlindHediff, every spawned
    // humanlike standing in full glare (exposure, as sun heat reads it, at
    // or above glareBlindExposureMin) slowly gains that hediff, which sits on
    // vanilla Sight. Recovery is the hediff's own SeverityPerDay decay.
    //
    // Immunity is never a race or defName list:
    //   - an active gene carrying RM_GlareProtectionExtension (RM_GlareAdapted,
    //     which an RSW patch puts on the Jawa xenotype);
    //   - worn apparel carrying RM_GlareProtectionExtension, or tagged
    //     RM_GlareProtection in apparel.tags (RM_SunGoggles, and the
    //     Armoury's existing goggle headgear by patch-added tag).
    // Animals are out of scope. Mod Settings: glareBlindEnabled (off: nobody
    // gains it, an existing hediff just decays) and glareBlindRateMultiplier.
    // ════════════════════════════════════════════════════════════════════
    public class RM_GlareProtectionExtension : DefModExtension
    {
    }

    public static class RM_GlareBlind
    {
        public const int CheckIntervalTicks = 250;

        /// <summary>The apparel tag that marks eye protection, for gear whose
        /// def cannot carry a CreatureBehaviors type (a patch from a mod that
        /// does not depend on this one).</summary>
        public const string ProtectionApparelTag = "RM_GlareProtection";

        private static readonly List<Pawn> scratch = new List<Pawn>();

        public static void Tick(Map map, RM_MapComponent_ShadeGrid grid)
        {
            if (!RM_CreatureBehaviorsSettings.glareBlindEnabled || grid == null || !grid.SunHeatActive)
            {
                return;
            }
            RM_SunHeatExtension ext = grid.HeatExtension;
            if (ext?.glareBlindHediff == null)
            {
                return;
            }
            scratch.Clear();
            scratch.AddRange(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < scratch.Count; i++)
            {
                Pawn p = scratch[i];
                if (p.Dead || p.RaceProps == null || !p.RaceProps.Humanlike)
                {
                    continue;
                }
                float gain = RM_SunHeatMath.GlareBlindGain(grid.ExposureFor(p), ext.glareBlindExposureMin,
                    ext.glareBlindSeverityPerDay, RM_CreatureBehaviorsSettings.glareBlindRateMultiplier,
                    CheckIntervalTicks, EyesProtected(p));
                if (gain > 0f)
                {
                    HealthUtility.AdjustSeverity(p, ext.glareBlindHediff, gain);
                }
            }
            scratch.Clear();
        }

        /// <summary>True when a gene or worn apparel protects this pawn's eyes.</summary>
        public static bool EyesProtected(Pawn p)
        {
            if (p.genes != null)
            {
                List<Gene> genes = p.genes.GenesListForReading;
                for (int i = 0; i < genes.Count; i++)
                {
                    if (genes[i].Active && genes[i].def.HasModExtension<RM_GlareProtectionExtension>())
                    {
                        return true;
                    }
                }
            }
            if (p.apparel != null)
            {
                List<Apparel> worn = p.apparel.WornApparel;
                for (int i = 0; i < worn.Count; i++)
                {
                    ThingDef d = worn[i].def;
                    if (d.HasModExtension<RM_GlareProtectionExtension>()
                        || (d.apparel?.tags != null && d.apparel.tags.Contains(ProtectionApparelTag)))
                    {
                        return true;
                    }
                }
            }
            return false;
        }
    }
}
