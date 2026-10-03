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
            if (!RM_AbyssSettings.gustFeedersEnabled)
            {
                SetDormant(pawn, false);
                open = true;
                return;
            }
            var gusts = pawn.Map.GetComponent<RM_MapComponent_GustController>();
            if (gusts == null) return;

            bool gust = gusts.IsGust;
            if (gust)
            {
                SetDormant(pawn, false);
                if (gusts.GustCount != lastFedGust)
                {
                    lastFedGust = gusts.GustCount;
                    Need_Food food = pawn.needs?.food;
                    if (food != null) food.CurLevel += Props.nutritionPerGust;
                }
            }
            else
            {
                SetDormant(pawn, true);
            }
            open = gust;
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
