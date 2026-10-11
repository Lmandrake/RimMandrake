using System.Collections.Generic;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    /// <summary>Design §5 "Per-def toggles" (built 2026-10-10): which power-conduit defs become messy cords. Every eligible
    /// conduit (isPowerConduit, transmitter-linked graphic, not vanilla HiddenConduit) is a candidate; a defName the player
    /// unticked keeps its vanilla graphic and is carried as an undrawn conduit, exactly like HiddenConduit. Verse-free so the
    /// selftest checks the production rule.</summary>
    public static class ConduitTargets
    {
        public static List<string> Select(IEnumerable<string> candidates, ICollection<string> excluded)
        {
            var res = new List<string>();
            if (candidates == null) return res;
            foreach (string c in candidates)
                if (c != null && (excluded == null || !excluded.Contains(c))) res.Add(c);
            return res;
        }

        /// <summary>Toggle one defName in the exclusion list; returns whether it is now a target.</summary>
        public static bool Toggle(List<string> excluded, string defName, bool target)
        {
            excluded.RemoveAll(x => x == defName);
            if (!target) excluded.Add(defName);
            return target;
        }
    }
}
