using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    /// <summary>ENVHAZARDS_HAZARD_CLOCK_READOUTS_1. A small alert while a colonist stands in a contact-venom stand: who,
    /// and when the next scratch lands. The numbers are MapComponent_ContactVenom's own clocks; this only reads them.
    /// Gated by RM_EnvironmentalHazardsSettings.hazardClockReadoutsEnabled (and the contact-venom switch).</summary>
    public class Alert_VenomContactClock : Alert
    {
        private readonly List<Pawn> inContact = new List<Pawn>();

        public Alert_VenomContactClock()
        {
            defaultPriority = AlertPriority.Medium;
        }

        private void Refresh()
        {
            inContact.Clear();
            if (!RM_EnvironmentalHazardsSettings.hazardClockReadoutsEnabled || !RM_EnvironmentalHazardsSettings.contactVenomEnabled)
            {
                return;
            }
            List<Map> maps = Find.Maps;
            for (int i = 0; i < maps.Count; i++)
            {
                if (!maps[i].IsPlayerHome && maps[i].mapPawns.FreeColonistsSpawnedCount == 0)
                {
                    continue;
                }
                maps[i].GetComponent<MapComponent_ContactVenom>()?.ColonistsInContact(inContact);
            }
        }

        public override AlertReport GetReport()
        {
            Refresh();
            return inContact.Count > 0 ? AlertReport.CulpritIs(inContact[0]) : AlertReport.Inactive;
        }

        public override string GetLabel()
        {
            return "RM_VenomContactAlert".Translate(inContact.Count);
        }

        public override TaggedString GetExplanation()
        {
            System.Text.StringBuilder sb = new System.Text.StringBuilder();
            for (int i = 0; i < inContact.Count; i++)
            {
                Pawn p = inContact[i];
                MapComponent_ContactVenom tracker = p.Map?.GetComponent<MapComponent_ContactVenom>();
                int ticks = tracker != null ? tracker.TicksToNextScratch(p) : -1;
                if (ticks >= 0)
                {
                    sb.AppendLine("RM_VenomContactClock".Translate(p.LabelShortCap, ticks.ToStringTicksToPeriod()));
                }
            }
            return sb.ToString().TrimEndNewlines();
        }
    }
}
