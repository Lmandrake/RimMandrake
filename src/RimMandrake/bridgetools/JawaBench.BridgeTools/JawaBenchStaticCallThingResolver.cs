using System.Collections.Generic;
using System.Globalization;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
#if JAWA_GM_TOOLS
        // Exact ThingID ("Human123") or bare thingIDNumber ("123"); the current map first, then every map.
        // Compare the full ThingID because its defName can end in a digit.
        private static Thing StaticCallResolveThing(string a, out string foundAt)
        {
            foundAt = null;
            if (Find.Maps == null) return null;
            bool bare = int.TryParse(a, NumberStyles.None, CultureInfo.InvariantCulture, out int num)
                && char.IsDigit(a[a.Length - 1]);
            var maps = new List<Map>();
            if (Find.CurrentMap != null) maps.Add(Find.CurrentMap);
            foreach (Map m in Find.Maps) if (!maps.Contains(m)) maps.Add(m);
            foreach (Map m in maps)
            {
                List<Thing> all = m.listerThings.AllThings;
                for (int k = 0; k < all.Count; k++)
                {
                    Thing t = all[k];
                    if (bare ? t.thingIDNumber != num : t.ThingID != a) continue;
                    foundAt = (m == Find.CurrentMap ? "current map" : "map " + m.Index) + (bare ? ", by thingIDNumber" : ", by ThingID");
                    return t;
                }
            }
            return null;
        }
#endif
    }
}
