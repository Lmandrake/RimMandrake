using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>WIRE_DOWN_ALERT_1 (GS-4): lists every player anchor whose overhead wire is cut or lying on the ground, so a
    /// cut line in a corner of the base is noticed before something browns out. Clicking an entry jumps to the anchor,
    /// where "Re-string cut wires" already lives. A fallen cord whose far anchor died cannot be re-strung: the
    /// explanation says to build a new anchor. Obeys AerialSettings.wireDownAlert.</summary>
    public class Alert_WireDown : Alert
    {
        private readonly List<Thing> culprits = new List<Thing>();

        public Alert_WireDown()
        {
            defaultLabel = "Wire down";
            defaultPriority = AlertPriority.Medium;
        }

        /// <summary>Player anchors with a Cut link or a fallen cord on this map. Shared with AerialProbe "alert".</summary>
        public static List<CompAerialAnchor> Down(Map map)
        {
            RM_MapComponent_Aerial c = map?.GetComponent<RM_MapComponent_Aerial>();
            var res = new List<CompAerialAnchor>();
            if (c == null) return res;
            foreach (CompAerialAnchor a in c.Anchors)
                if (a.Faction == Faction.OfPlayer && (a.fallen.Count > 0 || a.links.Any(l => l.state == SpanState.Cut)))
                    res.Add(a);
            return res;
        }

        private List<Thing> Culprits()
        {
            culprits.Clear();
            foreach (Map m in Find.Maps)
                if (m.IsPlayerHome)
                    foreach (CompAerialAnchor a in Down(m)) culprits.Add(a.parent);
            return culprits;
        }

        public override string GetLabel() => culprits.Count > 1 ? "Wires down (" + culprits.Count + ")" : "Wire down";

        public override TaggedString GetExplanation()
        {
            var sb = new StringBuilder("These anchors have a cut wire or a wire lying on the ground, so the line they carried is dead:\n");
            foreach (Thing t in culprits)
            {
                CompAerialAnchor a = CompAerialAnchor.Of(t);
                int cut = a?.links.Count(l => l.state == SpanState.Cut) ?? 0;
                int orphan = a?.fallen.Count(f => f.cutPartner == -1) ?? 0;
                sb.Append("\n  - ").Append(t.LabelShortCap).Append(" (").Append(t.Position.x).Append(", ").Append(t.Position.z).Append(")");
                if (cut > 0) sb.Append(": ").Append(cut).Append(" cut, select it and use Re-string cut wires");
                if (orphan > 0) sb.Append(cut > 0 ? "; " : ": ").Append(orphan).Append(" fell from a lost anchor, link it to a new one");
            }
            return sb.ToString();
        }

        public override AlertReport GetReport() => AerialSettings.enabled && AerialSettings.wireDownAlert ? AlertReport.CulpritsAre(Culprits()) : AlertReport.Inactive;
    }
}
