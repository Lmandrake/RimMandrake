// JawaBenchPaintTools.cs - the vanilla PAINT system, reachable from the bridge.
//
// WHY THIS EXISTS. Ship hull colouring had exactly two routes before this tool, and
// both were workarounds: the dev "T: Set Color" UI tool (a measured ~380-invocation
// per-game-session budget, then every FloatMenu silently misses - see
// Utils/apply_wall_colors.py), or expressing colour as MATERIAL (the hull became
// MegaBone/DinoChitin to fake a palette - Utils/apply_wall_stuff.py). The engine has
// had the real thing all along: Building.ChangePaint(ColorDef) is the same mechanism
// as the in-game paint designator - persistent (Scribe_Defs paintColorDef), visible
// in the inspect pane as the paint colour, removable in play with the remove-paint
// designator, and it dirties the map mesh itself, so no commit call is needed.
//
// READ FROM 1.6 SOURCE, NOT REMEMBERED:
//   Verse/Building.cs        ChangePaint(ColorDef): sets paintColorDef,
//                            Notify_ColorChanged(), MapMeshDirty at the position.
//   Verse/Building.cs:110    Scribe_Defs.Look(ref paintColorDef) - save-persistent.
//   RimWorld/BuildingProperties.cs:134   bool paintable - the vanilla gate; Core's
//                            Wall carries paintable=true, and GravshipHull inherits
//                            ParentName="Wall" (Odyssey Buildings_Gravship.xml).

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/paint_building",
            Description =
                "Paint, unpaint or census buildings with the VANILLA paint system " +
                "(Building.ChangePaint) - the same persistent, savegame-scribed paint the " +
                "in-game designator applies, NOT the dev Set Color tint and NOT a material " +
                "swap. Scope is a rect 'x,z,w,h' or cells 'x,z;x,z;...'. With colorDef " +
                "set: paints every paintable building in scope (optionally only defName). " +
                "With removePaint=true: clears paint back to material colour. With " +
                "neither: a read-only census of current paint by def and colour. " +
                "REFUSES buildings whose def.building.paintable is false and reports them " +
                "- it never silently skips. Multi-cell buildings are counted once. " +
                "No commit call needed afterwards; ChangePaint dirties the mesh itself.",
            ResultDescription =
                "success; painted / removed / alreadyThatColor counts; verified (paint " +
                "read back from Building.PaintColorDef, not assumed); notPaintable count " +
                "+ first examples; filtered count when defName is set; census[] rows of " +
                "def/color/count in census mode.")]
        public static async Task<object> PaintBuilding(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Rect 'x,z,w,h'. Give this or cells.")] string rect = null,
            [ToolParameter(Description = "Cells 'x,z;x,z;...'. Give this or rect.")] string cells = null,
            [ToolParameter(Description = "ColorDef defName to paint (e.g. Structure_Red). Empty + removePaint=false = census mode.")] string colorDef = null,
            [ToolParameter(Description = "Clear paint instead of applying one.")] bool removePaint = false,
            [ToolParameter(Description = "Only touch buildings of this ThingDef (e.g. GravshipHull). Empty = every paintable building in scope.")] string defName = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                // -- scope ------------------------------------------------------
                var targets = new List<IntVec3>();
                if (!string.IsNullOrEmpty(rect))
                {
                    CellRect r;
                    if (!TryRect(rect, map, out r, out err)) return Fail(err);
                    targets.AddRange(r.Cells);
                }
                else if (!string.IsNullOrEmpty(cells))
                {
                    foreach (var part in cells.Split(';'))
                    {
                        if (string.IsNullOrWhiteSpace(part)) continue;
                        var b = part.Split(',');
                        int x, z;
                        if (b.Length != 2 || !int.TryParse(b[0].Trim(), out x) || !int.TryParse(b[1].Trim(), out z))
                            return Fail("Bad cell '" + part + "', expected 'x,z'.");
                        var c = new IntVec3(x, 0, z);
                        if (c.InBounds(map)) targets.Add(c);
                    }
                }
                else return Fail("Give a rect 'x,z,w,h' or cells 'x,z;x,z;...'.");

                ColorDef cd = null;
                if (!string.IsNullOrEmpty(colorDef))
                {
                    cd = DefDatabase<ColorDef>.GetNamedSilentFail(colorDef);
                    if (cd == null) return Fail("No ColorDef '" + colorDef + "'.", DefSuggestions<ColorDef>(colorDef));
                }
                if (cd != null && removePaint)
                    return Fail("colorDef and removePaint together are ambiguous - pass one.");

                // -- collect buildings, deduped (a wall section is one cell, but be safe) --
                var seen = new HashSet<int>();
                var buildings = new List<Building>();
                foreach (var c in targets)
                {
                    var things = map.thingGrid.ThingsListAtFast(c);
                    for (int i = 0; i < things.Count; i++)
                    {
                        var b = things[i] as Building;
                        if (b == null || !seen.Add(b.thingIDNumber)) continue;
                        buildings.Add(b);
                    }
                }

                int filtered = 0, notPaintable = 0, already = 0, changed = 0, verified = 0;
                var notPaintableExamples = new List<string>();
                var perDef = new Dictionary<string, int>();

                // census mode: report, touch nothing
                if (cd == null && !removePaint)
                {
                    var rows = buildings
                        .GroupBy(b => new { def = b.def.defName, color = b.PaintColorDef == null ? "(unpainted)" : b.PaintColorDef.defName })
                        .Select(g => new { g.Key.def, g.Key.color, count = g.Count() })
                        .OrderByDescending(g => g.count).ToList();
                    return (object)new { success = true, mode = "census", cellsInScope = targets.Count,
                                         buildings = buildings.Count, census = rows, ticksGame = TicksGameSafe() };
                }

                foreach (var b in buildings)
                {
                    if (!string.IsNullOrEmpty(defName) && b.def.defName != defName) { filtered++; continue; }
                    if (b.def.building == null || !b.def.building.paintable)
                    {
                        notPaintable++;
                        if (notPaintableExamples.Count < 12)
                            notPaintableExamples.Add(b.def.defName + "@" + b.Position.x + "," + b.Position.z);
                        continue;
                    }
                    if (b.PaintColorDef == cd) { already++; continue; }
                    b.ChangePaint(cd);                       // null = remove paint
                    if (b.PaintColorDef == cd) verified++;   // read back, never assumed
                    changed++;
                    int n; perDef.TryGetValue(b.def.defName, out n); perDef[b.def.defName] = n + 1;
                }

                return (object)new
                {
                    success = true,
                    mode = removePaint ? "remove" : "paint",
                    color = cd == null ? null : cd.defName,
                    cellsInScope = targets.Count,
                    buildingsInScope = buildings.Count,
                    painted = removePaint ? 0 : changed,
                    removed = removePaint ? changed : 0,
                    verified,
                    alreadyThatColor = already,
                    filteredByDefName = filtered,
                    notPaintable,
                    notPaintableExamples,
                    perDef,
                    ticksGame = TicksGameSafe()
                };
            });
        }
    }
}
