using System.Collections.Generic;
using Verse;

namespace RimMandrake.DeepDrill
{
    /// <summary>One row: a deep-lump ThingDef (by defName, so a missing donor mod is harmless) and the biome defNames where a drill may find it.
    /// Empty homes = never found by a drill.</summary>
    public class RM_DeepHomeRow
    {
        public string thing;
        public List<string> homes = new List<string>();
    }

    public class RM_DeepHomeDef : Def
    {
        public List<RM_DeepHomeRow> rows = new List<RM_DeepHomeRow>();

        /// <summary>thing defName -> home biome defNames, merged over every RM_DeepHomeDef.</summary>
        public static Dictionary<string, HashSet<string>> Merge(IEnumerable<RM_DeepHomeDef> defs)
        {
            var d = new Dictionary<string, HashSet<string>>();
            foreach (RM_DeepHomeDef def in defs)
                foreach (RM_DeepHomeRow r in def.rows)
                {
                    if (r == null || string.IsNullOrEmpty(r.thing)) continue;
                    if (!d.TryGetValue(r.thing, out HashSet<string> s)) d[r.thing] = s = new HashSet<string>();
                    if (r.homes != null) foreach (string h in r.homes) s.Add(h);
                }
            return d;
        }
    }
}
