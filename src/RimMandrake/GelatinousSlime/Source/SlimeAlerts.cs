using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // ════════════════════════════════════════════════════════════════════
    // THE ALERT CASCADE, standing half (spec §3 law 1).
    //
    // The letters at each stage transition are in HediffComp_Slimification;
    // this is the persistent bar that does not go away until the colonist
    // does — the "spend the antidote or leave" alert at stage 2 and the red
    // one with the clock at stage 3.
    //
    // 🔑 ONE ALERT, NOT THREE. Vanilla shows one alert per condition and
    // escalates its priority; three separate alert classes would stack three
    // bars on one colonist walking up the ladder.
    // ════════════════════════════════════════════════════════════════════
    public class Alert_Slimification : Alert
    {
        private readonly List<Pawn> slicked = new List<Pawn>();
        private readonly List<Pawn> critical = new List<Pawn>();

        public Alert_Slimification()
        {
            defaultLabel = "Slimification";
        }

        private void RecalculateLists()
        {
            slicked.Clear();
            critical.Clear();
            if (SlimeDefs.Slimification == null)
            {
                return;
            }
            foreach (Pawn p in PawnsFinder.AllMaps_FreeColonistsAndPrisoners)
            {
                if (p == null || p.health == null)
                {
                    continue;
                }
                Hediff h = p.health.hediffSet.GetFirstHediffOfDef(SlimeDefs.Slimification);
                if (h == null)
                {
                    continue;
                }
                int stage = HediffComp_Slimification.StageIndex(h.Severity);
                if (stage >= 2)
                {
                    critical.Add(p);
                }
                else if (stage == 1)
                {
                    slicked.Add(p);
                }
            }
        }

        public override AlertPriority Priority
        {
            get { return critical.Count > 0 ? AlertPriority.High : AlertPriority.Medium; }
        }

        public override string GetLabel()
        {
            int n = slicked.Count + critical.Count;
            if (critical.Count > 0)
            {
                return "Being absorbed: " + n;
            }
            return "Slicked with slime: " + n;
        }

        public override TaggedString GetExplanation()
        {
            System.Text.StringBuilder sb = new System.Text.StringBuilder();
            if (critical.Count > 0)
            {
                sb.AppendLine("Past the point of walking it off, and running out of time:");
                for (int i = 0; i < critical.Count; i++)
                {
                    sb.AppendLine("  " + critical[i].LabelShortCap);
                }
                sb.AppendLine();
            }
            if (slicked.Count > 0)
            {
                sb.AppendLine("No longer wiping off on their own:");
                for (int i = 0; i < slicked.Count; i++)
                {
                    sb.AppendLine("  " + slicked[i].LabelShortCap);
                }
                sb.AppendLine();
            }
            sb.AppendLine("Administer a slime antidote, or take them to dry country — desert, "
                          + "arid shrubland, or out to sea — and let it leach off on the road. "
                          + "Wet country only holds it where it is.");
            return sb.ToString().TrimEndNewlines();
        }

        public override AlertReport GetReport()
        {
            RecalculateLists();
            if (critical.Count > 0)
            {
                return AlertReport.CulpritsAre(critical);
            }
            if (slicked.Count > 0)
            {
                return AlertReport.CulpritsAre(slicked);
            }
            return false;
        }
    }
}
