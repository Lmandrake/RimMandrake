using RimWorld;
using Verse;

namespace RimMandrake.Abyss
{
    // ABYSS_GHARREK_BUILD_1. Dormant in the still, open and feeding at every gust.
    // Dormant = the RM_GharrekDormant hediff (Moving capped to 0). Open = hediff removed and one
    // meal of nutritionPerGust added at the gust's rising edge, so a gharrek only ever fattens in
    // gusts. Gill-ash is plain CompProperties_Shearable on the def; no extra gating is invented here.
    public class CompProperties_Gharrek : CompProperties
    {
        public HediffDef dormantHediff;
        public float nutritionPerGust = 0.12f;

        public CompProperties_Gharrek()
        {
            compClass = typeof(CompGharrek);
        }
    }

    public class CompGharrek : ThingComp
    {
        private const int CheckInterval = 15;
        private bool open;
        private int lastFedGust = -1;

        private CompProperties_Gharrek Props => (CompProperties_Gharrek)props;

        public bool IsOpen => open;

        public override void CompTick()
        {
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || !pawn.IsHashIntervalTick(CheckInterval)) return;
            // the rule (open and awake in a gust, fed once per gust, dormant out of one, always open with the option off) is
            // RM_GustKernel.GharrekStep; this reads the engine in and applies the result
            var gusts = pawn.Map.GetComponent<RM_MapComponent_GustController>();
            if (RM_AbyssSettings.gustFeedersEnabled && gusts == null) return;

            float fed = RM_GustKernel.GharrekStep(RM_AbyssSettings.gustFeedersEnabled, gusts != null && gusts.IsGust,
                gusts != null ? gusts.GustCount : 0, Props.nutritionPerGust, ref lastFedGust, out bool dormant, out open);
            SetDormant(pawn, dormant);
            if (fed > 0f)
            {
                Need_Food food = pawn.needs?.food;
                if (food != null) food.CurLevel += fed;
            }
        }

        private void SetDormant(Pawn pawn, bool dormant)
        {
            if (Props.dormantHediff == null) return;
            Hediff h = pawn.health.hediffSet.GetFirstHediffOfDef(Props.dormantHediff);
            if (dormant && h == null)
            {
                pawn.health.AddHediff(Props.dormantHediff);
            }
            else if (!dormant && h != null)
            {
                pawn.health.RemoveHediff(h);
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref open, "open", false);
            Scribe_Values.Look(ref lastFedGust, "lastFedGust", -1);
        }
    }
}
