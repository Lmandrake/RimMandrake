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
                            id = h.ThingID,
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
                id = t.ThingID,
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

        // ================================================================
        //  jawa/set_quality, jawa/container_fill - the REPLAY half of the
        //  identity-grade export above. PLACER_IDENTITY_REPLAY_1, 2026-08-29:
        //  bills and storage settings already had setter tools when this was
        //  filed (jawa/bill_add, jawa/configure_bill, jawa/storage_settings,
        //  all added 2026-08-26, two days before the item) - only quality on
        //  an ALREADY-PLACED thing (build_batch's quality param is batch-wide,
        //  not per-thing) and container CONTENTS had no writer at all.
        // ================================================================

        [Tool(
            "jawa/set_quality",
            Description =
                "Set CompQuality on ANY already-existing thing by id - the per-thing replay " +
                "counterpart to jawa/build_batch's quality parameter, which only applies uniformly " +
                "to a whole batch at spawn time. Use this to give an individual placed thing (or a " +
                "container's held item, addressed the same way jawa/export_things reports it) the " +
                "quality an exported identity row recorded. A thing with no CompQuality (most " +
                "non-crafted things) is refused by name, not silently ignored.",
            ResultDescription =
                "success, thing{id, defName}, quality{was, asked, now} read back off CompQuality " +
                "after the write.")]
        public static async Task<object> SetQuality(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID of the target - jawa/list_things / jawa/export_things address things this way.")]
            string thing = null,
            [ToolParameter(Description = "Awful|Poor|Normal|Good|Excellent|Masterwork|Legendary.")]
            string quality = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string terr;
                var t = FindLiveThingById(thing, out terr);
                if (t == null) return Fail(terr);

                var cq = t.TryGetComp<CompQuality>();
                if (cq == null)
                    return Fail(t.def.defName + " (" + t.ThingID + ") has no CompQuality - it cannot carry a quality.");

                if (string.IsNullOrWhiteSpace(quality)) return Fail("Give 'quality'.");
                QualityCategory q;
                try { q = (QualityCategory)Enum.Parse(typeof(QualityCategory), quality.Trim(), true); }
                catch { return Fail("Bad quality '" + quality + "'. Awful|Poor|Normal|Good|Excellent|Masterwork|Legendary."); }

                var was = cq.Quality;
                cq.SetQuality(q, ArtGenerationContext.Outsider);

                return new
                {
                    success = true,
                    thing = new { id = t.ThingID, defName = t.def.defName },
                    quality = new { was = was.ToString(), asked = q.ToString(), now = cq.Quality.ToString() },
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/container_fill",
            Description =
                "Insert freshly-made items into ANY thing that implements IThingHolder (a crate, a " +
                "fuel tank, a hopper - any container jawa/export_things's `contents` field can read) " +
                "- the setter half of that export field, which had no writer until now. Each item is " +
                "made fresh via ThingMaker.MakeThing(def, stuff) (never taken from elsewhere on the " +
                "map) then added straight into the holder's ThingOwner via TryAdd - it does NOT spawn " +
                "on the map first, so this is not jawa/build_batch. " +
                "items grammar: 'ThingDef[:stuff[:quality[:count]]];...' - trailing fields may be " +
                "left empty ('Steel::Excellent:20') to skip one and still set a later one. count " +
                "above the def's stackLimit is CLAMPED and reported, never silently dropped.",
            ResultDescription =
                "success, target{id, defName}, cleared (count of things destroyed if clear=true), " +
                "added[] per entry (def, stuff, quality, requestedCount, addedCount, " +
                "clampedToStackLimit), failed[] naming any entry that did not parse or was refused, " +
                "contentsAfter read back off the holder the same shape as jawa/export_things.")]
        public static async Task<object> ContainerFill(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID of the holder (a spawned container-like thing).")]
            string thing = null,
            [ToolParameter(Description = "'ThingDef[:stuff[:quality[:count]]];...' entries.")]
            string items = null,
            [ToolParameter(Description = "ClearAndDestroyContents() first. Default false.")]
            bool clear = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string terr;
                var t = FindLiveThingById(thing, out terr);
                if (t == null) return Fail(terr);

                var holder = t as IThingHolder;
                if (holder == null || t is Pawn)
                    return Fail(t.def.defName + " (" + t.ThingID + ") does not implement IThingHolder - it cannot hold contained things.");

                var owned = holder.GetDirectlyHeldThings();
                if (owned == null)
                    return Fail(t.def.defName + " (" + t.ThingID + ") returned no ThingOwner from GetDirectlyHeldThings().");

                int clearedCount = 0;
                if (clear)
                {
                    clearedCount = owned.Count;
                    owned.ClearAndDestroyContents();
                }

                var added = new List<object>();
                var failed = new List<object>();

                if (!string.IsNullOrWhiteSpace(items))
                {
                    foreach (var raw in items.Split(new[] { ';', '\n' }, StringSplitOptions.RemoveEmptyEntries))
                    {
                        var entry = raw.Trim(); if (entry.Length == 0) continue;
                        var parts = entry.Split(':');
                        var dn = parts[0].Trim();
                        var td = DefDatabase<ThingDef>.GetNamedSilentFail(dn);
                        if (td == null) { failed.Add(new { entry, why = "no ThingDef '" + dn + "'", suggestions = DefSuggestions<ThingDef>(dn) }); continue; }

                        ThingDef stuffDef = null;
                        if (parts.Length > 1 && !string.IsNullOrWhiteSpace(parts[1]))
                        {
                            stuffDef = DefDatabase<ThingDef>.GetNamedSilentFail(parts[1].Trim());
                            if (stuffDef == null) { failed.Add(new { entry, why = "no stuff ThingDef '" + parts[1].Trim() + "'" }); continue; }
                        }
                        else if (td.MadeFromStuff) stuffDef = GenStuff.DefaultStuffFor(td);
                        if (!td.MadeFromStuff) stuffDef = null;

                        QualityCategory q = QualityCategory.Normal; bool setQ = false;
                        if (parts.Length > 2 && !string.IsNullOrWhiteSpace(parts[2]))
                        {
                            try { q = (QualityCategory)Enum.Parse(typeof(QualityCategory), parts[2].Trim(), true); setQ = true; }
                            catch { failed.Add(new { entry, why = "bad quality '" + parts[2].Trim() + "'" }); continue; }
                        }

                        int count = 1;
                        if (parts.Length > 3 && !string.IsNullOrWhiteSpace(parts[3]))
                        {
                            if (!int.TryParse(parts[3].Trim(), out count) || count <= 0)
                            { failed.Add(new { entry, why = "bad count '" + parts[3].Trim() + "'" }); continue; }
                        }

                        Thing made;
                        try { made = ThingMaker.MakeThing(td, stuffDef); }
                        catch (Exception e) { failed.Add(new { entry, why = "MakeThing threw: " + e.Message }); continue; }

                        if (setQ)
                        {
                            var cq = made.TryGetComp<CompQuality>();
                            if (cq != null) cq.SetQuality(q, ArtGenerationContext.Outsider);
                        }

                        int cap = Math.Max(1, td.stackLimit);
                        int requested = count;
                        int intended = Math.Min(count, cap);
                        made.stackCount = intended;
                        var mq = made.TryGetComp<CompQuality>();
                        string madeQuality = mq == null ? null : mq.Quality.ToString();

                        bool ok = owned.TryAdd(made, true);
                        if (!ok)
                        {
                            failed.Add(new { entry, why = "ThingOwner.TryAdd refused it (not acceptable, or over capacity)." });
                            continue;
                        }

                        // TryAdd(canMergeWithExistingStacks: true) can fully or partially merge
                        // `made` into an existing stack, driving made.stackCount toward 0 (and
                        // destroying `made`) even on success -- report the intended count, not
                        // whatever is left of the (possibly now-destroyed) source Thing.
                        added.Add(new
                        {
                            def = td.defName,
                            stuff = stuffDef == null ? null : stuffDef.defName,
                            quality = madeQuality,
                            requestedCount = requested,
                            addedCount = intended,
                            clampedToStackLimit = requested > cap
                        });
                    }
                }

                var contentsAfter = new List<object>();
                foreach (var h in owned)
                {
                    var hq = h.TryGetComp<CompQuality>();
                    contentsAfter.Add(new
                    {
                        def = h.def.defName,
                        stuff = h.Stuff == null ? null : h.Stuff.defName,
                        count = h.stackCount,
                        quality = hq == null ? null : hq.Quality.ToString(),
                    });
                }

                return new
                {
                    success = true,
                    target = new { id = t.ThingID, defName = t.def.defName },
                    cleared = clearedCount,
                    added,
                    failed,
                    contentsAfter,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
