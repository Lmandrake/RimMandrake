// KCSG layout grids kernel (MINESITES_GRIDS_BUILD_STEEL_FOR_BANNED_ORE). Verse-free so the offline SelfTest compiles it alone.
// Decision: design/RimMandrake/minesites_plasteel_ruin_grids_decision_2026-10-31.md - every MineablePlasteel and
// MineableComponentsIndustrial cell of an authored ruin grid becomes MineableSteel (swap the symbol, keep the geometry), only while
// the registry disables that mineable. A layout row is one comma-joined string, so the swap is token-exact and always made from
// the rows as first seen: applying twice equals once, and an empty swap set restores the rows the mod shipped.
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.Minerals
{
    /// <summary>One grid cell that holds a symbol in scope, as first seen (Layer = index into StructureLayoutDef.layouts).</summary>
    public sealed class GridCell
    {
        public int Layer, Row, Col;
        public string Token;
    }

    public static class RM_LayoutGridKernel
    {
        /// <summary>The only symbols the decision swaps. A disabled mineable outside this list is never rewritten here.</summary>
        public static readonly string[] Scope = { "MineablePlasteel", "MineableComponentsIndustrial" };
        public const string Replacement = "MineableSteel";

        /// <summary>The scope symbols to swap now: those the registry disables (empty when the master toggle is off).</summary>
        public static HashSet<string> SwapOut(ICollection<string> disabled)
        {
            var s = new HashSet<string>();
            if (disabled == null) return s;
            foreach (string n in Scope) if (disabled.Contains(n)) s.Add(n);
            return s;
        }

        /// <summary>Every cell whose token is in <paramref name="scope"/>, split exactly as KCSG splits a row (',' with no trim).</summary>
        public static List<GridCell> Find(IList<IList<string>> layers, ICollection<string> scope)
        {
            var cells = new List<GridCell>();
            if (layers == null || scope == null || scope.Count == 0) return cells;
            for (int i = 0; i < layers.Count; i++)
            {
                IList<string> rows = layers[i];
                if (rows == null) continue;
                for (int j = 0; j < rows.Count; j++)
                {
                    if (rows[j] == null) continue;
                    string[] tok = rows[j].Split(',');
                    for (int k = 0; k < tok.Length; k++)
                        if (scope.Contains(tok[k])) cells.Add(new GridCell { Layer = i, Row = j, Col = k, Token = tok[k] });
                }
            }
            return cells;
        }

        /// <summary>The rows with every token in <paramref name="swapOut"/> replaced by <paramref name="replacement"/>; every other
        /// character (separators, empty tokens, "." cells) is kept. Pure: the input is never written.</summary>
        public static List<List<string>> Rewrite(IList<IList<string>> layers, ICollection<string> swapOut, string replacement)
        {
            var outLayers = new List<List<string>>();
            if (layers == null) return outLayers;
            bool any = swapOut != null && swapOut.Count > 0 && replacement != null;
            foreach (IList<string> rows in layers)
            {
                var outRows = new List<string>();
                if (rows != null)
                    foreach (string row in rows)
                    {
                        if (!any || row == null) { outRows.Add(row); continue; }
                        string[] tok = row.Split(',');
                        for (int k = 0; k < tok.Length; k++) if (swapOut.Contains(tok[k])) tok[k] = replacement;
                        outRows.Add(string.Join(",", tok));
                    }
                outLayers.Add(outRows);
            }
            return outLayers;
        }

        /// <summary>token -> count over every row of every layer (the before/after instrument).</summary>
        public static Dictionary<string, int> Count(IList<IList<string>> layers, ICollection<string> tokens)
        {
            var c = tokens.ToDictionary(t => t, t => 0);
            if (layers == null) return c;
            foreach (IList<string> rows in layers)
                if (rows != null)
                    foreach (string row in rows)
                        if (row != null)
                            foreach (string t in row.Split(','))
                                if (c.ContainsKey(t)) c[t]++;
            return c;
        }
    }
}
