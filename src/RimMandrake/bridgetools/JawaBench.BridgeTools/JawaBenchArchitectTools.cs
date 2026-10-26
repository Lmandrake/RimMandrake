using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;

namespace JawaBench.BridgeTools
{
    // jawa/architect_designator_visible -- what the architect tab would actually DRAW.
    // Why (ARCHITECT_VISIBLE_FIX_READS_ALWAYS_TRUE): the stock list_architect_designators 'visible' field is membership in
    // DesignationCategoryDef.ResolvedAllowedDesignators (game rules) and read true for 880/880 designators, even one whose
    // PlaceWorker.IsBuildDesignatorVisible returns false. The gizmo grid skips a designator whose Visible is false, and a
    // dropdown element shows only if root.Visible && element.Visible (same rule as RM_SuspensionProofs.ProofButtons).
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/architect_designator_visible",
            Description =
                "Census of Designator.Visible over every DesignationCategoryDef.ResolvedAllowedDesignators entry, dropdowns " +
                "expanded (an element is drawn only when the dropdown root AND the element are Visible). Designator_Build.Visible " +
                "consults research, DLC and every PlaceWorker IsBuildDesignatorVisible, so this is the build-menu visibility the " +
                "stock list tool does NOT measure (its 'visible' is list membership only). Read only. Needs a loaded game. " +
                "Visible can depend on the current map and on god mode; both are reported.",
            ResultDescription =
                "success, godMode, total, visibleCount, hiddenCount, errors, rows[{category, label, buildDef, designatorClass, " +
                "inDropdown, rootVisible, visible, drawn, error}] (rows filtered by defName/category/onlyHidden; counts are " +
                "over ALL designators before filtering).")]
        public static async Task<object> ArchitectDesignatorVisible(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Only rows whose placed def's defName contains this (case-insensitive). Optional.")] string defName = null,
            [ToolParameter(Description = "Only rows in this DesignationCategoryDef defName. Optional.")] string category = null,
            [ToolParameter(Description = "Only return rows that are NOT drawn. Default false.")] bool onlyHidden = false,
            [ToolParameter(Description = "Max rows returned (counts are never truncated). Default 400.")] int limit = 400)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (Current.Game == null) return Fail("No game is loaded.");
                if (limit <= 0) limit = 400;
                var rows = new List<object>();
                int total = 0, drawnCount = 0, hiddenCount = 0, errors = 0, matched = 0;
                foreach (DesignationCategoryDef cat in DefDatabase<DesignationCategoryDef>.AllDefsListForReading)
                {
                    IEnumerable<Designator> roots;
                    try { roots = cat.ResolvedAllowedDesignators.ToList(); }
                    catch (System.Exception e)
                    {
                        errors++;
                        if (rows.Count < limit) rows.Add(new { category = cat.defName, error = "ResolvedAllowedDesignators threw " + e.GetType().Name + ": " + e.Message });
                        continue;
                    }
                    foreach (Designator root in roots)
                    {
                        bool rootVisible; string rootErr = null;
                        try { rootVisible = root.Visible; }
                        catch (System.Exception e) { rootVisible = false; rootErr = e.GetType().Name + ": " + e.Message; }
                        var dd = root as Designator_Dropdown;
                        IEnumerable<Designator> each = dd != null ? (IEnumerable<Designator>)dd.Elements : new[] { root };
                        foreach (Designator d in each)
                        {
                            total++;
                            bool vis; string err = rootErr;
                            if (ReferenceEquals(d, root)) vis = rootVisible;
                            else
                            {
                                try { vis = d.Visible; }
                                catch (System.Exception e) { vis = false; err = (err == null ? "" : err + "; ") + e.GetType().Name + ": " + e.Message; }
                            }
                            if (err != null) errors++;
                            bool drawn = rootVisible && vis && err == null;
                            if (drawn) drawnCount++; else hiddenCount++;
                            string placed = (d as Designator_Place)?.PlacingDef?.defName;
                            if (!string.IsNullOrEmpty(defName) && (placed == null || placed.IndexOf(defName, System.StringComparison.OrdinalIgnoreCase) < 0)) continue;
                            if (!string.IsNullOrEmpty(category) && cat.defName != category) continue;
                            if (onlyHidden && drawn) continue;
                            matched++;
                            if (rows.Count >= limit) continue;
                            string label = null;
                            try { label = d.Label; } catch (System.Exception e) { label = "<Label threw " + e.GetType().Name + ">"; }
                            rows.Add(new
                            {
                                category = cat.defName,
                                label,
                                buildDef = placed,
                                designatorClass = d.GetType().FullName,
                                inDropdown = dd != null,
                                rootVisible,
                                visible = vis,
                                drawn,
                                error = err,
                            });
                        }
                    }
                }
                return (object)new
                {
                    success = true,
                    godMode = DebugSettings.godMode,
                    currentMap = Find.CurrentMap?.uniqueID,
                    total,
                    visibleCount = drawnCount,
                    hiddenCount,
                    errors,
                    matched,
                    returned = rows.Count,
                    truncated = matched > rows.Count,
                    rows,
                    ticksGame = TicksGameSafe(),
                };
            }, cancellationToken).ConfigureAwait(false);
        }
    }
}
