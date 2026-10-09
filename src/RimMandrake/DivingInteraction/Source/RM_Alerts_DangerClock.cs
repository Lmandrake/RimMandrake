using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // DANGER_CLOCK_ALERTS_1 (design pass DI-4). The player can see the danger clock: an alert while a heated
    // suit is low/empty outside on the Chill seabed, and an alert while a colonist is encased in brine with
    // the hours left before smothering. Both read state that already exists; both obey
    // RM_DivingSettings.dangerClockAlertsEnabled. The "low" threshold is PROVISIONAL.
    public static class RM_DangerClock
    {
        public const float LowSuitFraction = 0.2f;

        public static List<Pawn> LowSuitPawns(Map map)
        {
            var res = new List<Pawn>();
            if (map == null || !RM_ChillFireGate.IsChillSeabedMap(map)) return res;
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned)
            {
                if (p.apparel == null || p.Position.Roofed(map)) continue;
                foreach (Apparel a in p.apparel.WornApparel)
                {
                    RM_CompHeatedSuitBattery c = a.GetComp<RM_CompHeatedSuitBattery>();
                    if (c != null && c.ChargeFraction <= LowSuitFraction) { res.Add(p); break; }
                }
            }
            return res;
        }

        private static ThingDef jacketDef;
        private static bool jacketLooked;

        public static List<RM_Building_BrineEncasement> EncasedColonists(Map map)
        {
            var res = new List<RM_Building_BrineEncasement>();
            if (map == null) return res;
            if (!jacketLooked)
            {
                jacketLooked = true;
                foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
                    if (d.thingClass == typeof(RM_Building_BrineEncasement)) { jacketDef = d; break; }
            }
            if (jacketDef == null) return res;
            foreach (Thing t in map.listerThings.ThingsOfDef(jacketDef))
                if (t is RM_Building_BrineEncasement j && j.ContainedThing is Pawn p && !p.Dead && p.Faction == Faction.OfPlayer)
                    res.Add(j);
            return res;
        }
    }

    public class Alert_HeatedSuitLow : Alert
    {
        private readonly List<Thing> culprits = new List<Thing>();

        public Alert_HeatedSuitLow()
        {
            defaultLabel = "Heated suit low";
            defaultPriority = AlertPriority.High;
        }

        private List<Thing> Culprits()
        {
            culprits.Clear();
            foreach (Map m in Find.Maps)
                if (m.IsPlayerHome)
                    foreach (Pawn p in RM_DangerClock.LowSuitPawns(m)) culprits.Add(p);
            return culprits;
        }

        public override string GetLabel() => culprits.Count > 1 ? "Heated suits low (" + culprits.Count + ")" : "Heated suit low";

        public override TaggedString GetExplanation()
        {
            var sb = new StringBuilder("These colonists are outside with a heated suit low or empty. An empty suit gives no cold protection:\n");
            foreach (Thing t in culprits) sb.Append("\n  - ").Append(t.LabelShortCap);
            return sb.ToString();
        }

        public override AlertReport GetReport()
        {
            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.chillHeatedSuitEnabled || !RM_DivingSettings.dangerClockAlertsEnabled)
                return AlertReport.Inactive;
            return AlertReport.CulpritsAre(Culprits());
        }
    }

    public class Alert_ColonistEncased : Alert
    {
        private readonly List<Thing> culprits = new List<Thing>();

        public Alert_ColonistEncased()
        {
            defaultLabel = "Colonist encased in brine";
            defaultPriority = AlertPriority.Critical;
        }

        private List<Thing> Culprits()
        {
            culprits.Clear();
            foreach (Map m in Find.Maps)
                foreach (RM_Building_BrineEncasement j in RM_DangerClock.EncasedColonists(m)) culprits.Add(j);
            return culprits;
        }

        public override TaggedString GetExplanation()
        {
            var sb = new StringBuilder("Mine the jacket out before they smother:\n");
            foreach (Thing t in culprits)
            {
                var j = (RM_Building_BrineEncasement)t;
                sb.Append("\n  - ").Append(j.ContainedThing.LabelShortCap).Append(": about ").Append(Mathf.CeilToInt(j.SmotherHoursLeft)).Append(" hours");
            }
            return sb.ToString();
        }

        public override AlertReport GetReport()
        {
            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.dangerClockAlertsEnabled) return AlertReport.Inactive;
            return AlertReport.CulpritsAre(Culprits());
        }
    }
}
