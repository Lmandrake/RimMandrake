// KCSG authored-ruin grids adapter (MINESITES_GRIDS_BUILD_STEEL_FOR_BANNED_ORE). Decision:
// design/RimMandrake/minesites_plasteel_ruin_grids_decision_2026-10-31.md. Ancient mining industry ships ten StructureLayoutDefs
// whose walls hold MineablePlasteel / MineableComponentsIndustrial cells: ore mined from rock, which the 2026-09-25 ruling forbids.
// While the registry disables one of those mineables, its cells become MineableSteel (geometry kept, so no wall opens); with the
// policy or master toggle off the grids are restored as the mod ships them.
// KCSG is not referenced (reflection). KCSG parses each def's `layouts` strings into `_layouts` (List<SymbolDef[,]>) once, in
// KCSG.StartupActions' [StaticConstructorOnStartup] (StructureLayoutDef.ResolveLayouts; not in ResolveReferences), and generation
// reads only `_layouts`. Static-constructor order between mods is not fixed, so every refresh writes BOTH: the strings (read if
// KCSG resolves later) and the resolved grid when it is already filled (KCSG 1.6, decompiled 2026-10-31).
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Verse;

namespace RimMandrake.Minerals
{
    public static class RM_MineralLayoutGrids
    {
        private sealed class Target
        {
            public Def Def;
            public List<List<string>> Live;              // the def's own `layouts` object, written in place
            public List<IList<string>> Original;         // deep copy of the rows as first seen
            public List<GridCell> Cells;                 // scope cells of Original
            public FieldInfo Resolved;                   // `_layouts`
        }

        private const BindingFlags Fields = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
        private static List<Target> targets;
        private static Type symbolType;
        private static string scanNote = "";
        private static string lastKey;                  // swap set + resolved-grid count of the last write: log only when it changes

        public static string LastReason { get; private set; } = "never applied";
        public static int TargetCount => targets?.Count ?? 0;

        public static void Refresh(IEnumerable<PolicyDecision> decisions, string why)
        {
            if (targets == null) targets = Scan();
            HashSet<string> disabled = RM_MineralsSettings.enabled
                ? RM_ExplicitListKernel.Disabled(decisions, n => RM_MineralExplicitLists.IsMineable(DefDatabase<ThingDef>.GetNamedSilentFail(n))) : new HashSet<string>();
            HashSet<string> swap = RM_LayoutGridKernel.SwapOut(disabled);
            ThingDef steel = DefDatabase<ThingDef>.GetNamedSilentFail(RM_LayoutGridKernel.Replacement);
            if (swap.Count > 0 && (!RM_MineralExplicitLists.IsMineable(steel) || disabled.Contains(RM_LayoutGridKernel.Replacement)))
            {
                Log.Warning("[RM Minerals] ruin layout grids (" + why + "): " + RM_LayoutGridKernel.Replacement
                          + " is missing or disabled, so no cell is swapped (grids kept as shipped)");
                swap.Clear();
            }
            object steelSymbol = symbolType != null ? GenDefDatabase.GetDefSilentFail(symbolType, RM_LayoutGridKernel.Replacement, false) : null;
            int cells = 0, layouts = 0, grids = 0, unresolved = 0;
            var perToken = new Dictionary<string, int>();
            foreach (Target t in targets)
            {
                List<List<string>> rows = RM_LayoutGridKernel.Rewrite(t.Original, swap, RM_LayoutGridKernel.Replacement);
                for (int i = 0; i < rows.Count && i < t.Live.Count; i++)
                    for (int j = 0; j < rows[i].Count && j < t.Live[i].Count; j++) t.Live[i][j] = rows[i][j];
                int n = t.Cells.Count(c => swap.Contains(c.Token));
                if (n > 0) { layouts++; cells += n; }
                foreach (GridCell c in t.Cells) if (swap.Contains(c.Token)) perToken[c.Token] = (perToken.TryGetValue(c.Token, out int k) ? k : 0) + 1;

                // the resolved grid, when KCSG has already built it
                if (!(t.Resolved?.GetValue(t.Def) is IList grid) || grid.Count < t.Original.Count) continue;
                grids++;
                foreach (GridCell c in t.Cells)
                {
                    if (!(grid[c.Layer] is Array a) || a.Rank != 2 || c.Row >= a.GetLength(0) || c.Col >= a.GetLength(1)) continue;
                    bool toSteel = swap.Contains(c.Token);
                    object sym = toSteel ? steelSymbol : GenDefDatabase.GetDefSilentFail(symbolType, c.Token, false);
                    if (toSteel && sym == null) { unresolved++; continue; }
                    a.SetValue(sym, c.Row, c.Col);
                }
            }
            LastReason = why;
            string key = string.Join(",", swap.OrderBy(x => x)) + "|" + grids;
            bool changed = key != lastKey;
            lastKey = key;
            if (unresolved > 0)
                Log.Warning("[RM Minerals] ruin layout grids (" + why + "): no KCSG symbol " + RM_LayoutGridKernel.Replacement + ", "
                          + unresolved + " resolved cells kept as shipped");
            if (changed)
                Log.Message("[RM Minerals] ruin layout grids (" + why + "): " + targets.Count + " layouts hold " + string.Join("/", RM_LayoutGridKernel.Scope)
                          + scanNote + "; " + (cells > 0 ? cells + " cells -> " + RM_LayoutGridKernel.Replacement + " in " + layouts + " ("
                                                + string.Join(", ", perToken.OrderBy(kv => kv.Key).Select(kv => kv.Key + " " + kv.Value)) + ")"
                                              : "none swapped (policy off or not disabling them)")
                          + "; " + grids + " already resolved by KCSG");
        }

        private static List<Target> Scan()
        {
            var found = new List<Target>();
            Type layoutType = GenTypes.GetTypeInAnyAssembly("KCSG.StructureLayoutDef");
            symbolType = GenTypes.GetTypeInAnyAssembly("KCSG.SymbolDef");
            if (layoutType == null || symbolType == null || !typeof(Def).IsAssignableFrom(layoutType)) { scanNote = " (KCSG not loaded)"; return found; }
            FieldInfo rowsField = layoutType.GetField("layouts", Fields);
            FieldInfo resolved = layoutType.GetField("_layouts", Fields);
            if (rowsField == null || resolved == null) { scanNote = " (KCSG StructureLayoutDef has no layouts/_layouts field: unsupported version)"; return found; }
            var scope = new HashSet<string>(RM_LayoutGridKernel.Scope);
            foreach (Def d in GenDefDatabase.GetAllDefsInDatabaseForDef(layoutType))
            {
                if (d == null || !(rowsField.GetValue(d) is List<List<string>> live)) continue;
                var original = live.Select(l => (IList<string>)(l == null ? new List<string>() : new List<string>(l))).ToList();
                List<GridCell> cells = RM_LayoutGridKernel.Find(original, scope);
                if (cells.Count > 0) found.Add(new Target { Def = d, Live = live, Original = original, Cells = cells, Resolved = resolved });
            }
            return found;
        }

        /// <summary>"layouts=N;reason=..;&lt;defName&gt;=rows:P/C/S,grid:P/C/S" (Plasteel/Components/Steel cell counts in the strings
        /// and in KCSG's resolved grid; grid:- when KCSG has not resolved it) for every target whose defName contains a ';'-separated
        /// filter term (empty = all). Bridge proof hook for Minerals/validation.py (jawa/static_call); reads, never writes.</summary>
        public static string ProofState(string filter)
        {
            var terms = (filter ?? "").Split(';').Select(x => x.Trim()).Where(x => x.Length > 0).ToList();
            var sb = new System.Text.StringBuilder();
            sb.Append("layouts=").Append(TargetCount).Append(";reason=").Append(LastReason).Append(scanNote);
            if (targets == null) return sb.ToString();
            string[] tokens = { RM_LayoutGridKernel.Scope[0], RM_LayoutGridKernel.Scope[1], RM_LayoutGridKernel.Replacement };
            foreach (Target t in targets)
            {
                if (terms.Count > 0 && !terms.Any(x => t.Def.defName.Contains(x))) continue;
                Dictionary<string, int> r = RM_LayoutGridKernel.Count(t.Live.Cast<IList<string>>().ToList(), tokens);
                sb.Append(';').Append(t.Def.defName).Append("=rows:").Append(string.Join("/", tokens.Select(x => r[x]))).Append(",grid:");
                if (!(t.Resolved.GetValue(t.Def) is IList grid) || grid.Count == 0) { sb.Append('-'); continue; }
                var g = tokens.ToDictionary(x => x, x => 0);
                foreach (object o in grid)
                    if (o is Array a)
                        foreach (object s in a)
                            if (s is Def sd && g.ContainsKey(sd.defName)) g[sd.defName]++;
                sb.Append(string.Join("/", tokens.Select(x => g[x])));
            }
            return sb.ToString();
        }
    }
}
