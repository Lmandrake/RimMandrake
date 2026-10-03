using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Abyss
{
    // ABYSS_DONOR_BEASTS_FREED_1. The summ (cast bible 2026-10-01 §4C): "It regenerates. UV-sensitive (it
    // suffers in daylight off the Abyss) and sees in darkness and the Dark unimpaired." Sight needs no code:
    // the Dark's murk (RM_MapComponentDark) touches humanlikes only. This comp does the other two:
    //  - regeneration: every rare tick, heals a little from one injury (never a missing part);
    //  - daylight: unroofed under a bright sky the RM_SummSunburn hediff rises (a readable sign on the
    //    health tab, with pain and slowness); in shade or the dark it falls away.
    public class CompProperties_RM_SummHide : CompProperties
    {
        public float healPerRareTick = 1.5f;
        public float sunGlowAtLeast = 0.5f;
        public float burnPerRareTick = 0.04f;
        public float coolPerRareTick = 0.06f;
        public HediffDef sunburnHediff;

        public CompProperties_RM_SummHide()
        {
            compClass = typeof(CompRM_SummHide);
        }
    }

    public class CompRM_SummHide : ThingComp
    {
        private CompProperties_RM_SummHide Props => (CompProperties_RM_SummHide)props;

        public override void CompTickRare()
        {
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead) return;
            if (RM_AbyssSettings.summRegenerates) Regenerate(pawn);
            Sun(pawn);
        }

        private void Regenerate(Pawn pawn)
        {
            List<Hediff_Injury> injuries = new List<Hediff_Injury>();
            pawn.health.hediffSet.GetHediffs(ref injuries, h => h.CanHealNaturally() || h.CanHealFromTending());
            if (injuries.Count == 0) return;
            injuries.RandomElement().Heal(Props.healPerRareTick * pawn.HealthScale);
        }

        /// <summary>True when the pawn stands unroofed under a sky at or above the daylight threshold.</summary>
        public bool InDaylight(Pawn pawn)
        {
            return !pawn.Position.Roofed(pawn.Map) && pawn.Map.skyManager.CurSkyGlow >= Props.sunGlowAtLeast;
        }

        private void Sun(Pawn pawn)
        {
            if (Props.sunburnHediff == null) return;
            Hediff h = pawn.health.hediffSet.GetFirstHediffOfDef(Props.sunburnHediff);
            if (RM_AbyssSettings.summUVSensitive && InDaylight(pawn))
            {
                if (h == null)
                {
                    h = HediffMaker.MakeHediff(Props.sunburnHediff, pawn);
                    h.Severity = Props.burnPerRareTick;
                    pawn.health.AddHediff(h);
                }
                else
                {
                    h.Severity = Mathf.Min(h.def.maxSeverity, h.Severity + Props.burnPerRareTick);
                }
            }
            else if (h != null)
            {
                h.Severity -= Props.coolPerRareTick;
                if (h.Severity <= 0.001f) pawn.health.RemoveHediff(h);
            }
        }
    }
}
