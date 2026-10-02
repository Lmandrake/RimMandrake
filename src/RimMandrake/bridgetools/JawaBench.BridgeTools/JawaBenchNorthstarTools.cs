// JawaBenchNorthstarTools.cs - the reads the Graffiti north-star trial cannot fake.
//
// WHY THIS FILE EXISTS
// ====================
// GRAFFITI_NORTHSTAR_BRIDGE_TOOLS_1. The north-star driver
// (src/RimMandrake/Utils/northstar_driver/site.py, NEEDED_TOOLS) and the trial plan
// (design/RimMandrake/northstar_trials/Graffiti_trial_plan.md §3.5, §3.14, §6.7,
// §6.12, §6.14) need five instruments no existing tool answers:
//
//   thing_graphic   which texture a spawned thing ACTUALLY resolved to (BadTex
//                   detection) and which Graphic_Random variant it shows.
//   spawn_variant   spawn a Graphic_Random thing pinned to variant k, so a gallery
//                   photographs every variant instead of hoping RNG covers them.
//   running_mods    the RUNNING mod list (not ModsConfig, which names the next load)
//                   plus where a named assembly was loaded from, its MVID and sha256.
//   glow_at         GlowGrid.GroundGlowAt per cell (1.6's name for GameGlowAt).
//   site_state      one call: auto-home, storyteller, incident queue, map conditions,
//                   weather transition, snow over a rect, every pawn's job targets and
//                   every reservation landing in the rect.
//
// ENGINE FACTS THESE REST ON (RimSage, decompiled 1.6, 2026-10-01)
// ================================================================
//  * Graphic_Random.SubGraphicFor(thing) = subGraphics[(thing.OverrideGraphicIndex
//    ?? thing.thingIDNumber) % count]. Thing.overrideGraphicIndex is a public int?
//    field and is Scribed, so pinning a variant is a field write before spawn - no
//    reroll loop needed, and it survives save/load.
//  * GlowGrid has no GameGlowAt in 1.6; GroundGlowAt(c, ignoreCavePlants, ignoreSky)
//    is the replacement. PsychGlowAt is the bucketed (Dark/Lit/Overlit) form.
//  * ModAssemblyHandler.ReloadAll uses Assembly.LoadFrom, so Location is populated.
//    LoadFrom of a second file with the same identity returns the FIRST - so a
//    duplicate copy is visible only as two mods claiming the same assembly.
//  * DebugSettings.enableStoryteller gates the storyteller; the incident queue is
//    Find.Storyteller.incidentQueue (Clear() exists). PlaySettings.autoHomeArea.
//
// THREAD AFFINITY: everything touching game state is inside ctx.MainThread.InvokeAsync.

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ---- shared helpers for this file ------------------------------------

        // Resolve the map: explicit uniqueID wins and is CHECKED (plan §3.14 "every
        // call carries an explicit map ID"); omitted means Find.CurrentMap.
        private static Map NorthstarMap(int mapId, out string err)
        {
            err = null;
            if (Current.Game == null || Find.Maps == null) { err = "No game loaded."; return null; }
            if (mapId < 0)
            {
                var cur = Find.CurrentMap;
                if (cur == null) err = "No current map.";
                return cur;
            }
            foreach (var m in Find.Maps)
                if (m != null && m.uniqueID == mapId) return m;
            err = "No map with uniqueID " + mapId + ". Live maps: " +
                  string.Join(",", Find.Maps.Select(m => m.uniqueID.ToString()).ToArray());
            return null;
        }

        // Unclipped rect parse, so a rect hanging off the map is REPORTED, not
        // silently shrunk (TryRect clips without saying so).
        private static bool NorthstarRect(string rect, Map map, out CellRect clipped, out int requestedCells, out string err)
        {
            clipped = default(CellRect); requestedCells = 0; err = null;
            if (string.IsNullOrWhiteSpace(rect)) { err = "Give a rect as 'x,z,w,h'."; return false; }
            var b = rect.Split(',');
            int x, z, w, h;
            if (b.Length != 4 || !int.TryParse(b[0].Trim(), out x) || !int.TryParse(b[1].Trim(), out z)
                || !int.TryParse(b[2].Trim(), out w) || !int.TryParse(b[3].Trim(), out h) || w < 1 || h < 1)
            { err = "Bad rect '" + rect + "', expected 'x,z,w,h' with w,h >= 1."; return false; }
            requestedCells = w * h;
            clipped = new CellRect(x, z, w, h).ClipInsideMap(map);
            return true;
        }

        // Walk wrapper graphics (Graphic_Linked, Graphic_RandomRotated, ...) down to
        // the graphic that actually picks a texture. Returns the chain of type names.
        private static Graphic UnwrapGraphic(Graphic g, List<string> chain)
        {
            for (int depth = 0; g != null && depth < 6; depth++)
            {
                chain.Add(g.GetType().Name);
                if (g is Graphic_Random || g is Graphic_Indexed || g is Graphic_Cluster) return g;
                var f = g.GetType().GetField("subGraphic", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
                var inner = f != null ? f.GetValue(g) as Graphic : null;
                if (inner == null || ReferenceEquals(inner, g)) return g;
                g = inner;
            }
            return g;
        }

        private static object DescribeThingGraphic(Thing t)
        {
            var chain = new List<string>();
            Graphic top = null;
            string topErr = null;
            try { top = t.Graphic; } catch (Exception e) { topErr = e.GetType().Name + ": " + e.Message; }
            if (top == null)
                return new { id = t.ThingID, defName = t.def?.defName, graphic = (string)null, error = topErr ?? "Thing.Graphic is null." };

            var g = UnwrapGraphic(top, chain);
            int? variantIndex = null; int? variantCount = null; string variantPath = null;
            List<string> variantPaths = null;
            Graphic resolved = g;
            var rnd = g as Graphic_Random;
            if (rnd != null)
            {
                variantCount = rnd.SubGraphicsCount;
                if (variantCount > 0)
                {
                    int raw = t.OverrideGraphicIndex ?? t.thingIDNumber;
                    // C# % keeps the sign; the engine indexes with the same expression,
                    // so mirror it exactly rather than "fixing" it.
                    variantIndex = raw % variantCount.Value;
                    resolved = rnd.SubGraphicFor(t);
                    variantPath = resolved?.path;
                    variantPaths = new List<string>();
                    for (int i = 0; i < variantCount.Value; i++)
                        variantPaths.Add(rnd.SubGraphicAtIndex(i)?.path);
                }
            }

            Material mat = null; string matErr = null;
            try { mat = resolved != null ? resolved.MatAt(t.Rotation, t) : null; }
            catch (Exception e) { matErr = e.GetType().Name + ": " + e.Message; }
            Texture tex = mat != null ? mat.mainTexture : null;
            bool badMat = mat != null && ReferenceEquals(mat, BaseContent.BadMat);
            bool badTex = tex != null && ReferenceEquals(tex, BaseContent.BadTex);
            bool printOverridden = false;
            try
            {
                var pm = t.GetType().GetMethod("Print", BindingFlags.Instance | BindingFlags.Public, null, new[] { typeof(SectionLayer) }, null);
                printOverridden = pm != null && pm.DeclaringType != typeof(Thing) && pm.DeclaringType != typeof(ThingWithComps) && pm.DeclaringType != typeof(Filth);
            }
            catch { printOverridden = false; }

            return new
            {
                id = t.ThingID,
                defName = t.def?.defName,
                thingClass = t.GetType().FullName,
                cell = t.Spawned ? new { x = t.Position.x, z = t.Position.z } : null,
                graphicClass = top.GetType().Name,
                graphicChain = chain,
                graphicPath = top.path,
                resolvedPath = resolved?.path,
                isGraphicRandom = rnd != null,
                variantCount,
                variantIndex,
                variantPath,
                overrideGraphicIndex = t.overrideGraphicIndex,
                thingIDNumber = t.thingIDNumber,
                variantPaths,
                materialName = mat != null ? mat.name : null,
                textureName = tex != null ? tex.name : null,
                textureSize = tex != null ? new { w = tex.width, h = tex.height } : null,
                shader = mat != null && mat.shader != null ? mat.shader.name : null,
                badTex = badTex || badMat,
                printOverridden,
                error = matErr,
            };
        }

        // ================================================================
        //  thing_graphic
        // ================================================================
        [Tool(
            "jawa/thing_graphic",
            Description =
                "For live things, the texture the engine ACTUALLY resolved - so magenta/BadTex is detectable " +
                "from a read instead of a screenshot - and, for a Graphic_Random def, WHICH variant this " +
                "instance shows (index = (overrideGraphicIndex ?? thingIDNumber) % count, the engine's own " +
                "expression) plus every variant path, so a gallery can prove it photographed all of them. " +
                "Address by 'thing' ids (comma-separated) OR by 'rect' with an optional 'defs' filter. " +
                "Wrapper graphics (Linked, RandomRotated) are unwrapped via their subGraphic field and the " +
                "chain is reported. " +
                "⚠ badTex compares the resolved material/texture BY REFERENCE to BaseContent.BadMat/BadTex; " +
                "a texture that loaded but is the wrong art is NOT detectable here. " +
                "⚠ printOverridden=true means the thing class overrides Print and may draw its OWN materials " +
                "(the Graffiti tier-A sigil marks do) - the def graphic reported is then only the fallback. " +
                "⚠ A rect read is capped by 'limit'; isCompleteList=false means truncated - treat as UNMEASURED.",
            ResultDescription =
                "success, mapId, count, isCompleteList, things[]: id, defName, thingClass, cell, graphicClass, " +
                "graphicChain[], graphicPath, resolvedPath, isGraphicRandom, variantCount, variantIndex, " +
                "variantPath, overrideGraphicIndex, thingIDNumber, variantPaths[], materialName, textureName, " +
                "textureSize, shader, badTex, printOverridden, error. refused[] names unresolved ids.")]
        public static async Task<object> ThingGraphic(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Thing id(s), comma-separated. Bare 'Filth123' or 'Thing_Filth123'.")]
            string thing = null,
            [ToolParameter(Description = "Instead of ids: a rect 'x,z,w,h' on the map; every thing in it is read.")]
            string rect = null,
            [ToolParameter(Description = "With rect: keep only these defNames (comma-separated). Empty keeps all.")]
            string defs = null,
            [ToolParameter(Description = "Map uniqueID to assert/use. -1 = current map (rect mode only; ids search every map).")]
            int mapId = -1,
            [ToolParameter(Description = "Max things returned in rect mode (default 500).")]
            int limit = 500)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                var rows = new List<object>();
                var refused = new List<object>();

                if (!string.IsNullOrWhiteSpace(thing))
                {
                    foreach (var tok in thing.Split(',').Select(s => s.Trim()).Where(s => s.Length > 0))
                    {
                        string err;
                        var t = SystemToolsFindThing(tok, out err);
                        if (t == null) { refused.Add(new { thing = tok, reason = err ?? "not found" }); continue; }
                        if (mapId >= 0 && (t.MapHeld == null || t.MapHeld.uniqueID != mapId))
                        { refused.Add(new { thing = tok, reason = "thing is not on map " + mapId }); continue; }
                        rows.Add(DescribeThingGraphic(t));
                    }
                    return (object)new { success = refused.Count == 0, mapId, count = rows.Count, isCompleteList = true, things = rows, refused, ticksGame = TicksGameSafe() };
                }

                string merr;
                var map = NorthstarMap(mapId, out merr);
                if (map == null) return Fail(merr);
                CellRect r; int requested;
                if (!NorthstarRect(rect, map, out r, out requested, out merr))
                    return Fail("Give 'thing' ids or a 'rect'. " + merr);
                var want = string.IsNullOrWhiteSpace(defs) ? null
                    : new HashSet<string>(defs.Split(',').Select(s => s.Trim()).Where(s => s.Length > 0), StringComparer.Ordinal);
                if (want != null)
                    foreach (var d in want)
                        if (DefDatabase<ThingDef>.GetNamedSilentFail(d) == null)
                            refused.Add(new { def = d, reason = "no such ThingDef", suggestions = DefSuggestions<ThingDef>(d) });
                if (limit < 1) limit = 500;
                bool complete = true;
                var seen = new HashSet<int>();
                foreach (var c in r)
                {
                    foreach (var t in c.GetThingList(map))
                    {
                        if (t == null || t.def == null || !seen.Add(t.thingIDNumber)) continue;
                        if (want != null && !want.Contains(t.def.defName)) continue;
                        if (rows.Count >= limit) { complete = false; break; }
                        rows.Add(DescribeThingGraphic(t));
                    }
                    if (!complete) break;
                }
                return (object)new
                {
                    success = refused.Count == 0,
                    mapId = map.uniqueID,
                    cellsRequested = requested,
                    cellsInMap = r.Area,
                    count = rows.Count,
                    isCompleteList = complete,
                    things = rows,
                    refused,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        // ================================================================
        //  spawn_variant
        // ================================================================
        [Tool(
            "jawa/spawn_variant",
            Description =
                "Spawn ONE thing pinned to a Graphic_Random variant: sets Thing.overrideGraphicIndex = variant " +
                "before GenSpawn.Spawn (the field Graphic_Random.SubGraphicFor reads first; it is Scribed, so " +
                "the pin survives save/load). Then reads the resolved texture back the same way " +
                "thing_graphic does and FAILS if the resolved variant index differs from the one asked for. " +
                "REFUSES: a def whose graphic is not Graphic_Random (after unwrapping), a variant outside " +
                "0..count-1, an out-of-bounds cell, a pawn/blueprint/frame def. " +
                "⚠ Uses plain GenSpawn.Spawn, NOT FilthMaker - a filth def lands as a fresh thickness-1 " +
                "filth, merging with nothing, and a Filth_Mark gets no maker/provenance (tier-A sigil " +
                "marks therefore fall back to the def graphic, which is exactly what a variant gallery wants). " +
                "⚠ Does not clear the cell: an existing thing of the same def stays alongside.",
            ResultDescription =
                "success, mapId, id, defName, cell, variantRequested, variantIndex, variantCount, variantPath, " +
                "resolvedPath, textureName, badTex, variantPaths[].")]
        public static async Task<object> SpawnVariant(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingDef defName (must use Graphic_Random).")]
            string def = null,
            [ToolParameter(Description = "Cell 'x,z'.")]
            string cell = null,
            [ToolParameter(Description = "Variant index k, 0-based.")]
            int variant = 0,
            [ToolParameter(Description = "Stuff defName for a stuffed def. Empty = GenStuff.DefaultStuffFor.")]
            string stuff = null,
            [ToolParameter(Description = "Map uniqueID to assert/use. -1 = current map.")]
            int mapId = -1)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err;
                var map = NorthstarMap(mapId, out err);
                if (map == null) return Fail(err);
                if (string.IsNullOrWhiteSpace(def)) return Fail("Give a def.");
                var td = DefDatabase<ThingDef>.GetNamedSilentFail(def.Trim());
                if (td == null) return Fail("No ThingDef '" + def + "'.", new { suggestions = DefSuggestions<ThingDef>(def) });
                if (td.race != null || td.IsBlueprint || td.IsFrame)
                    return Fail("Refused: '" + td.defName + "' is a pawn/blueprint/frame def.");
                IntVec3 c;
                if (!TryParseCell(cell, out c, out err)) return Fail(err);
                if (!c.InBounds(map)) return Fail("Cell " + c + " is out of bounds for map " + map.uniqueID + ".");
                if (td.graphicData == null) return Fail("'" + td.defName + "' has no graphicData.");

                var chain = new List<string>();
                var g = UnwrapGraphic(td.graphicData.Graphic, chain);
                var rnd = g as Graphic_Random;
                if (rnd == null)
                    return Fail("'" + td.defName + "' does not resolve to Graphic_Random (chain: " + string.Join(">", chain.ToArray()) + ").");
                int count = rnd.SubGraphicsCount;
                if (variant < 0 || variant >= count)
                    return Fail("variant " + variant + " out of range 0.." + (count - 1) + " for '" + td.defName + "'.");

                ThingDef stuffDef = null;
                if (td.MadeFromStuff)
                {
                    if (!string.IsNullOrWhiteSpace(stuff))
                    {
                        stuffDef = DefDatabase<ThingDef>.GetNamedSilentFail(stuff.Trim());
                        if (stuffDef == null) return Fail("No stuff ThingDef '" + stuff + "'.");
                    }
                    else stuffDef = GenStuff.DefaultStuffFor(td);
                }

                Thing t;
                try
                {
                    t = ThingMaker.MakeThing(td, stuffDef);
                    t.overrideGraphicIndex = variant;
                    t = GenSpawn.Spawn(t, c, map);
                }
                catch (Exception e) { return Fail("Spawn threw: " + e.GetType().Name + ": " + e.Message); }
                if (t == null || !t.Spawned) return Fail("GenSpawn.Spawn returned no spawned thing.");

                int idx = (t.OverrideGraphicIndex ?? t.thingIDNumber) % count;
                var sub = rnd.SubGraphicFor(t);
                Material mat = null;
                try { mat = sub?.MatAt(t.Rotation, t); } catch { mat = null; }
                var tex = mat != null ? mat.mainTexture : null;
                bool bad = (mat != null && ReferenceEquals(mat, BaseContent.BadMat)) || (tex != null && ReferenceEquals(tex, BaseContent.BadTex));
                var paths = new List<string>();
                for (int i = 0; i < count; i++) paths.Add(rnd.SubGraphicAtIndex(i)?.path);
                return (object)new
                {
                    success = idx == variant && !bad,
                    message = idx != variant ? "resolved variant " + idx + " != requested " + variant
                            : bad ? "variant resolved to BadTex" : null,
                    mapId = map.uniqueID,
                    id = t.ThingID,
                    defName = td.defName,
                    cell = new { x = t.Position.x, z = t.Position.z },
                    variantRequested = variant,
                    variantIndex = idx,
                    variantCount = count,
                    variantPath = sub?.path,
                    resolvedPath = sub?.path,
                    textureName = tex != null ? tex.name : null,
                    badTex = bad,
                    variantPaths = paths,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        // ================================================================
        //  running_mods
        // ================================================================
        [Tool(
            "jawa/running_mods",
            Description =
                "The RUNNING mod list from LoadedModManager.RunningModsListForReading (packageId + load order) - " +
                "what this process actually loaded, unlike ModsConfig.xml, which names the NEXT load. Plus, for " +
                "a named assembly (default RimMandrakeGraffiti): every AppDomain assembly with that simple name " +
                "with Location, MVID, file sha256 and file size, and every mod whose loadedAssemblies holds it. " +
                "⚠ More than one match, or more than one claiming mod, means a duplicate copy - the caller " +
                "must refuse; Assembly.LoadFrom of a same-identity second file silently returns the first. " +
                "⚠ sha256 is of the file AT Location NOW; a redeploy after launch changes the file but not " +
                "the loaded code, so compare MVID to the built DLL too.",
            ResultDescription =
                "success, count, packageIds[] (load order), mods[]: loadOrder, packageId, name, folder, " +
                "assembly: {name, matchCount, matches[]: location, mvid, version, sha256, fileBytes, " +
                "fileExists, claimedBy[] (packageIds)}.")]
        public static async Task<object> RunningMods(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Simple assembly name to locate (default RimMandrakeGraffiti). Empty skips.")]
            string assembly = "RimMandrakeGraffiti",
            [ToolParameter(Description = "Include the full mods[] rows (default true); false returns packageIds only.")]
            bool details = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var all = LoadedModManager.RunningModsListForReading;
                if (all == null) return Fail("LoadedModManager.RunningModsListForReading is null.");
                var ids = all.Select(m => m.PackageId).ToList();
                var rows = details
                    ? all.Select(m => (object)new { loadOrder = m.loadOrder, packageId = m.PackageId, name = m.Name, folder = m.RootDir }).ToList()
                    : null;

                object asmInfo = null;
                if (!string.IsNullOrWhiteSpace(assembly))
                {
                    var name = assembly.Trim();
                    var matches = new List<object>();
                    foreach (var a in AppDomain.CurrentDomain.GetAssemblies())
                    {
                        string simple;
                        try { simple = a.GetName().Name; } catch { continue; }
                        if (!string.Equals(simple, name, StringComparison.OrdinalIgnoreCase)) continue;
                        string loc = null; try { loc = a.Location; } catch { loc = null; }
                        string sha = null; long bytes = -1; bool exists = false; string hashErr = null;
                        if (!string.IsNullOrEmpty(loc) && File.Exists(loc))
                        {
                            exists = true;
                            try
                            {
                                using (var fs = File.OpenRead(loc))
                                using (var h = SHA256.Create())
                                {
                                    bytes = fs.Length;
                                    sha = BitConverter.ToString(h.ComputeHash(fs)).Replace("-", "").ToLowerInvariant();
                                }
                            }
                            catch (Exception e) { hashErr = e.GetType().Name + ": " + e.Message; }
                        }
                        var claimed = new List<string>();
                        foreach (var m in all)
                        {
                            try
                            {
                                if (m.assemblies != null && m.assemblies.loadedAssemblies.Any(x => ReferenceEquals(x, a)))
                                    claimed.Add(m.PackageId);
                            }
                            catch { }
                        }
                        string mvid = null; try { mvid = a.ManifestModule.ModuleVersionId.ToString(); } catch { mvid = null; }
                        string ver = null; try { ver = a.GetName().Version?.ToString(); } catch { ver = null; }
                        matches.Add(new { location = loc, mvid, version = ver, sha256 = sha, fileBytes = bytes, fileExists = exists, hashError = hashErr, claimedBy = claimed });
                    }
                    asmInfo = new { name, matchCount = matches.Count, matches };
                }

                return (object)new
                {
                    success = true,
                    count = ids.Count,
                    packageIds = ids,
                    mods = rows,
                    assembly = asmInfo,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        // ================================================================
        //  glow_at
        // ================================================================
        [Tool(
            "jawa/glow_at",
            Description =
                "Light level per cell: GlowGrid.GroundGlowAt(c) (1.6's replacement for GameGlowAt; 0..1, " +
                "sky glow on unroofed cells, else accumulated light capped at 0.5 unless a source saturates) " +
                "and PsychGlowAt (Dark/Lit/Overlit). Also returns the map's CurSkyGlow, roofed flag per cell " +
                "and the hour, so a light-band check can tell night from roof from a missing lamp. " +
                "Cells as 'x,z;x,z;...' or a rect. ⚠ Out-of-bounds cells are refused by name, never read as 0.",
            ResultDescription =
                "success, mapId, hour, skyGlow, count, cells[]: x, z, groundGlow, psychGlow, roofed. refused[].")]
        public static async Task<object> GlowAt(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Cells 'x,z;x,z'.")]
            string cells = null,
            [ToolParameter(Description = "Or a rect 'x,z,w,h' (max 4096 cells).")]
            string rect = null,
            [ToolParameter(Description = "Map uniqueID to assert/use. -1 = current map.")]
            int mapId = -1)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err;
                var map = NorthstarMap(mapId, out err);
                if (map == null) return Fail(err);
                var list = new List<IntVec3>();
                var refused = new List<object>();
                if (!string.IsNullOrWhiteSpace(cells))
                {
                    foreach (var tok in cells.Split(';').Select(s => s.Trim()).Where(s => s.Length > 0))
                    {
                        IntVec3 c;
                        if (!TryParseCell(tok, out c, out err)) { refused.Add(new { cell = tok, reason = err }); continue; }
                        if (!c.InBounds(map)) { refused.Add(new { cell = tok, reason = "out of bounds" }); continue; }
                        list.Add(c);
                    }
                }
                else
                {
                    CellRect r; int requested;
                    if (!NorthstarRect(rect, map, out r, out requested, out err)) return Fail("Give 'cells' or 'rect'. " + err);
                    if (r.Area != requested) refused.Add(new { rect, reason = (requested - r.Area) + " cell(s) outside the map" });
                    if (r.Area > 4096) return Fail("rect has " + r.Area + " cells; max 4096.");
                    foreach (var c in r) list.Add(c);
                }
                var rows = new List<object>();
                foreach (var c in list)
                {
                    rows.Add(new
                    {
                        x = c.x,
                        z = c.z,
                        groundGlow = map.glowGrid.GroundGlowAt(c),
                        psychGlow = map.glowGrid.PsychGlowAt(c).ToString(),
                        roofed = map.roofGrid.Roofed(c),
                    });
                }
                return (object)new
                {
                    success = refused.Count == 0,
                    mapId = map.uniqueID,
                    hour = GenLocalDate.HourFloat(map),
                    skyGlow = map.skyManager.CurSkyGlow,
                    count = rows.Count,
                    cells = rows,
                    refused,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        // ================================================================
        //  site_state
        // ================================================================
        private static object TargetRow(LocalTargetInfo ti, Map map)
        {
            if (!ti.IsValid) return null;
            IntVec3 c = ti.HasThing ? (ti.Thing.SpawnedOrAnyParentSpawned ? ti.Thing.PositionHeld : IntVec3.Invalid) : ti.Cell;
            return new { thing = ti.HasThing ? ti.Thing.ThingID : null, x = c.IsValid ? c.x : (int?)null, z = c.IsValid ? c.z : (int?)null };
        }

        private static bool TargetIn(LocalTargetInfo ti, CellRect? r)
        {
            if (r == null || !ti.IsValid) return false;
            IntVec3 c = ti.HasThing ? (ti.Thing.SpawnedOrAnyParentSpawned ? ti.Thing.PositionHeld : IntVec3.Invalid) : ti.Cell;
            return c.IsValid && r.Value.Contains(c);
        }

        [Tool(
            "jawa/site_state",
            Description =
                "One read of everything that can silently spoil a test site, with optional writes for the " +
                "three switches a trial must turn off. READS: auto-home (PlaySettings.autoHomeArea), " +
                "storyteller (DebugSettings.enableStoryteller + def), queued incidents, active map AND world " +
                "game conditions, weather (current, last, transition factor, rain rate), season/hour, snow " +
                "depth over 'rect' (max/sum/nonzero cells), every spawned pawn's current job + targets + " +
                "queued jobs, and every reservation. With 'rect', 'jobTargetsInRect'/'reservationsInRect' " +
                "count those landing inside it - the plan's 'no pawn has a job target in the site' check. " +
                "WRITES (all optional, before-and-after reported): autoHome on|off, storyteller on|off, " +
                "clearIncidentQueue=true. " +
                "⚠ storyteller off is DebugSettings.enableStoryteller - a static, NOT saved with the game; " +
                "a reload or restart turns it back on. ⚠ Map conditions are read, never ended here.",
            ResultDescription =
                "success, mapId, autoHome{before,after}, storyteller{def,enabledBefore,enabledAfter}, " +
                "incidentQueue{countBefore,countAfter,readout}, conditions{map[],world[]}, weather{cur,last," +
                "transition,rainRate,age}, season, hour, snow{cells,nonzero,max,sum}, pawns[]: id, label, " +
                "faction, x, z, job, targetA/B/C, queued, inRect; jobTargetsInRect, reservations, " +
                "reservationsInRect[].")]
        public static async Task<object> SiteState(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Site rect 'x,z,w,h' for snow and in-site job/reservation counts. Empty skips those.")]
            string rect = null,
            [ToolParameter(Description = "Set auto-home: 'on' | 'off'. Empty leaves it.")]
            string autoHome = null,
            [ToolParameter(Description = "Set storyteller: 'on' | 'off'. Empty leaves it.")]
            string storyteller = null,
            [ToolParameter(Description = "true clears Find.Storyteller.incidentQueue.")]
            bool clearIncidentQueue = false,
            [ToolParameter(Description = "Map uniqueID to assert/use. -1 = current map.")]
            int mapId = -1)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err;
                var map = NorthstarMap(mapId, out err);
                if (map == null) return Fail(err);

                bool? OnOff(string s, out string e)
                {
                    e = null;
                    if (string.IsNullOrWhiteSpace(s)) return null;
                    var v = s.Trim().ToLowerInvariant();
                    if (v == "on" || v == "true") return true;
                    if (v == "off" || v == "false") return false;
                    e = "expected on|off, got '" + s + "'";
                    return null;
                }
                var wantHome = OnOff(autoHome, out err);
                if (err != null) return Fail("autoHome: " + err);
                var wantStory = OnOff(storyteller, out err);
                if (err != null) return Fail("storyteller: " + err);

                CellRect? site = null; int requested = 0; CellRect clipped = default(CellRect);
                if (!string.IsNullOrWhiteSpace(rect))
                {
                    if (!NorthstarRect(rect, map, out clipped, out requested, out err)) return Fail(err);
                    site = clipped;
                }

                var ps = Find.PlaySettings;
                bool homeBefore = ps.autoHomeArea;
                if (wantHome.HasValue) ps.autoHomeArea = wantHome.Value;

                bool storyBefore = DebugSettings.enableStoryteller;
                if (wantStory.HasValue) DebugSettings.enableStoryteller = wantStory.Value;
                var st = Find.Storyteller;
                int qBefore = st?.incidentQueue != null ? st.incidentQueue.Count : -1;
                string readout = null;
                try { readout = st?.incidentQueue?.DebugQueueReadout; } catch { readout = null; }
                if (clearIncidentQueue && st?.incidentQueue != null) st.incidentQueue.Clear();
                int qAfter = st?.incidentQueue != null ? st.incidentQueue.Count : -1;

                var mapConds = map.gameConditionManager?.ActiveConditions?.Select(gc => (object)new { def = gc.def?.defName, ticksLeft = gc.Permanent ? -1 : gc.TicksLeft }).ToList() ?? new List<object>();
                var worldConds = Find.World?.gameConditionManager?.ActiveConditions?.Select(gc => (object)new { def = gc.def?.defName, ticksLeft = gc.Permanent ? -1 : gc.TicksLeft }).ToList() ?? new List<object>();

                var wm = map.weatherManager;
                object weather = wm == null ? null : new
                {
                    cur = wm.curWeather?.defName,
                    last = wm.lastWeather?.defName,
                    transition = wm.TransitionLerpFactor,
                    rainRate = wm.RainRate,
                    age = wm.curWeatherAge,
                };

                object snow = null;
                if (site.HasValue)
                {
                    int nonzero = 0; float max = 0f, sum = 0f;
                    foreach (var c in site.Value)
                    {
                        float d = map.snowGrid.GetDepth(c);
                        if (d > 0f) nonzero++;
                        if (d > max) max = d;
                        sum += d;
                    }
                    snow = new { cellsRequested = requested, cells = site.Value.Area, nonzero, max, sum };
                }

                var pawns = new List<object>();
                int jobTargetsInRect = 0;
                foreach (var p in map.mapPawns.AllPawnsSpawned.ToList())
                {
                    var job = p.CurJob;
                    var queued = new List<object>();
                    bool inRect = false;
                    if (job != null)
                        inRect = TargetIn(job.targetA, site) || TargetIn(job.targetB, site) || TargetIn(job.targetC, site)
                                 || (job.targetQueueA != null && job.targetQueueA.Any(x => TargetIn(x, site)))
                                 || (job.targetQueueB != null && job.targetQueueB.Any(x => TargetIn(x, site)));
                    if (p.jobs?.jobQueue != null)
                    {
                        foreach (var qj in p.jobs.jobQueue)
                        {
                            var j = qj.job;
                            if (j == null) continue;
                            bool qIn = TargetIn(j.targetA, site) || TargetIn(j.targetB, site) || TargetIn(j.targetC, site);
                            inRect |= qIn;
                            queued.Add(new { job = j.def?.defName, targetA = TargetRow(j.targetA, map), inRect = qIn });
                        }
                    }
                    if (inRect) jobTargetsInRect++;
                    pawns.Add(new
                    {
                        id = p.ThingID,
                        label = p.LabelShortCap,
                        faction = p.Faction?.def?.defName,
                        x = p.Position.x,
                        z = p.Position.z,
                        job = job?.def?.defName,
                        targetA = job != null ? TargetRow(job.targetA, map) : null,
                        targetB = job != null ? TargetRow(job.targetB, map) : null,
                        targetC = job != null ? TargetRow(job.targetC, map) : null,
                        queued,
                        inRect,
                    });
                }

                var resInRect = new List<object>();
                int resCount = 0;
                var rm = map.reservationManager;
                if (rm != null && rm.ReservationsReadOnly != null)
                {
                    foreach (var res in rm.ReservationsReadOnly)
                    {
                        resCount++;
                        if (TargetIn(res.Target, site))
                            resInRect.Add(new { claimant = res.Claimant?.ThingID, job = res.Job?.def?.defName, target = TargetRow(res.Target, map) });
                    }
                }

                return (object)new
                {
                    success = true,
                    mapId = map.uniqueID,
                    autoHome = new { before = homeBefore, after = ps.autoHomeArea },
                    storyteller = new { def = st?.def?.defName, enabledBefore = storyBefore, enabledAfter = DebugSettings.enableStoryteller },
                    incidentQueue = new { countBefore = qBefore, countAfter = qAfter, readout },
                    conditions = new { map = mapConds, world = worldConds },
                    weather,
                    season = GenLocalDate.Season(map).ToString(),
                    hour = GenLocalDate.HourFloat(map),
                    snow,
                    pawnCount = pawns.Count,
                    pawns,
                    jobTargetsInRect = site.HasValue ? jobTargetsInRect : (int?)null,
                    reservations = resCount,
                    reservationsInRect = site.HasValue ? resInRect : null,
                    ticksGame = TicksGameSafe(),
                };
            });
        }
    }
}
