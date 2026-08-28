// JawaBenchExportTools.cs - IDENTITY-GRADE reads for the structure exporter.
//
// The owner's ruling, 2026-08-28: an exported structure round-trips at identity
// grade - not just def+stuff+rot, but quality, paint, container CONTENTS, bills
// and storage settings. jawa/list_things stops at quality; this tool returns the
// whole identity row, so the exporter (rimplace BuildPlan JSON) can capture
// everything even before the placer can replay all of it. Capture-first: what is
// recorded is never lost; replay fidelity can grow later.
//
// READ FROM 1.6 SOURCE:
//   Building.PaintColorDef                    - the vanilla paint (may be null)
//   CompQuality.Quality                       - QualityCategory
//   IThingHolder.GetDirectlyHeldThings()      - container contents (ThingOwner)
//   Building_WorkTable.BillStack              - bills: recipe, repeat mode, counts
//   IStoreSettingsParent.GetStoreSettings()   - priority + ThingFilter
//   ThingFilter.AllowedThingDefs              - the filter, as defNames
//   Zone_Growing/Building_PlantGrower GetPlantDefToGrow() - plantToGrow

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
            "jawa/export_things",
            Description =
                "IDENTITY-GRADE read of every thing in a rect, for the structure exporter. " +
                "Per thing: def, stuff, position, rotation, stackCount, hitPoints/max, " +
                "faction, quality, PAINT (the vanilla PaintColorDef, null if unpainted), " +
                "plantToGrow, container CONTENTS one level deep (def/stuff/count/quality " +
                "per held thing), BILLS (recipe, repeatMode, repeatCount, targetCount, " +
                "suspended, pauseWhenSatisfied) and STORAGE settings (priority plus the " +
                "filter as allowed defNames - capped, with allowedCount so a cap is " +
                "visible, never silent). Read-only; pawns and filth excluded by default. " +
                "Terrain layers and floor colour are a separate read - the five-layer " +
                "terrain tool covers those.",
            ResultDescription =
                "success, count, truncated flag, things[] rows as described.")]
        public static async Task<object> ExportThings(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Rect 'x,z,w,h'.")] string rect = null,
            [ToolParameter(Description = "Include pawns. Default false.")] bool includePawns = false,
            [ToolParameter(Description = "Include items lying on the ground (category Item). Default true - they are the ship's cargo.")] bool includeItems = true,
            [ToolParameter(Description = "Max things returned. Default 2000.")] int limit = 2000,
            [ToolParameter(Description = "Max defNames listed per storage filter. Default 400.")] int filterCap = 400)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                CellRect r;
                if (!TryRect(rect, map, out r, out err)) return Fail(err);

                var seen = new HashSet<int>();
                var rows = new List<object>();
                bool truncated = false;

                foreach (var c in r)
                {
                    var things = map.thingGrid.ThingsListAtFast(c);
                    for (int i = 0; i < things.Count; i++)
                    {
                        var t = things[i];
                        if (!seen.Add(t.thingIDNumber)) continue;
                        if (t is Pawn && !includePawns) continue;
                        if (t.def.category == ThingCategory.Filth) continue;
                        if (t.def.category == ThingCategory.Item && !includeItems) continue;
                        if (t.def.category == ThingCategory.Mote) continue;
                        if (rows.Count >= limit) { truncated = true; break; }
                        rows.Add(Row(t, filterCap));
                    }
                    if (truncated) break;
                }

                return (object)new
                {
                    success = true,
                    rect = new { r.minX, minZ = r.minZ, width = r.Width, height = r.Height },
                    count = rows.Count,
                    truncated,
                    things = rows,
                    ticksGame = TicksGameSafe()
                };
            });
        }

        private static object Row(Thing t, int filterCap)
        {
            var b = t as Building;
            string quality = null;
            var cq = t.TryGetComp<CompQuality>();
            if (cq != null) quality = cq.Quality.ToString();

            // contents, one level deep - a shelf of weapons, a rack of apparel
            List<object> contents = null;
            var holder = t as IThingHolder;
            if (holder != null && !(t is Pawn))
            {
                var held = holder.GetDirectlyHeldThings();
                if (held != null && held.Count > 0)
                {
                    contents = new List<object>();
                    foreach (var h in held)
                    {
                        var hq = h.TryGetComp<CompQuality>();
                        contents.Add(new
                        {
                            def = h.def.defName,
                            stuff = h.Stuff == null ? null : h.Stuff.defName,
                            count = h.stackCount,
                            quality = hq == null ? null : hq.Quality.ToString(),
                            hitPoints = h.def.useHitPoints ? (int?)h.HitPoints : null,
                        });
                    }
                }
            }

            // bills - a worktable's production queue
            List<object> bills = null;
            var giver = t as IBillGiver;
            if (giver != null && giver.BillStack != null && giver.BillStack.Count > 0)
            {
                bills = new List<object>();
                foreach (var bill in giver.BillStack)
                {
                    var bp = bill as Bill_Production;
                    bills.Add(new
                    {
                        recipe = bill.recipe == null ? null : bill.recipe.defName,
                        suspended = bill.suspended,
                        repeatMode = bp == null || bp.repeatMode == null ? null : bp.repeatMode.defName,
                        repeatCount = bp == null ? (int?)null : bp.repeatCount,
                        targetCount = bp == null ? (int?)null : bp.targetCount,
                        pauseWhenSatisfied = bp == null ? (bool?)null : bp.pauseWhenSatisfied,
                    });
                }
            }

            // storage settings - priority + the filter as defNames, cap made visible
            object storage = null;
            var store = t as IStoreSettingsParent;
            if (store != null && store.StorageTabVisible)
            {
                var s = store.GetStoreSettings();
                if (s != null)
                {
                    var allowed = s.filter == null ? new List<string>()
                        : s.filter.AllowedThingDefs.Select(d => d.defName).ToList();
                    storage = new
                    {
                        priority = s.Priority.ToString(),
                        allowedCount = allowed.Count,
                        allowed = allowed.Take(filterCap).ToList(),
                    };
                }
            }

            string plantToGrow = null;
            var grower = t as IPlantToGrowSettable;
            if (grower != null)
            {
                var pd = grower.GetPlantDefToGrow();
                plantToGrow = pd == null ? null : pd.defName;
            }

            return new
            {
                id = t.thingIDNumber,
                def = t.def.defName,
                stuff = t.Stuff == null ? null : t.Stuff.defName,
                x = t.Position.x,
                z = t.Position.z,
                rot = t.Rotation.AsInt,
                stackCount = t.stackCount,
                hitPoints = t.def.useHitPoints ? (int?)t.HitPoints : null,
                maxHitPoints = t.def.useHitPoints ? (int?)t.MaxHitPoints : null,
                faction = t.Faction == null ? null : t.Faction.def.defName,
                quality,
                paint = b == null || b.PaintColorDef == null ? null : b.PaintColorDef.defName,
                plantToGrow,
                contents,
                bills,
                storage,
            };
        }
    }
}
