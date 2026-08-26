// JawaBenchSystemTools.cs - Group G: map things, terrain/roof/depth grids, Anomaly,
// save/load and diagnostics. See infrastructure/state/work/BRIDGE_TOOLS_EASY_REMAINING.md
// (Group G) for the census this file answers.
//
// EVERY SIGNATURE READ FROM 1.6 SOURCE, NOT REMEMBERED - MinifyUtility.cs,
// RoofCollapserImmediate.cs, SnowGrid.cs, SandGrid.cs, GameComponent_Anomaly.cs,
// EntityCodex.cs, Autosaver.cs, ScribeMetaHeaderUtility.cs, LoadedModManager.cs,
// ModContentPack.cs / ModAssemblyHandler.cs, StatWorker.cs, Prefs.cs, ModsConfig.cs.
//
// TWO DLC GUARDS THAT ARE NOT OPTIONAL, per the work doc:
//   - Every Anomaly-only row checks ModsConfig.AnomalyActive and REFUSES by name if
//     it is off. GameComponent_Anomaly and EntityCodex both degrade silently
//     (EntityCodex.SetDiscovered no-ops via ModLister.CheckAnomaly; Find.Anomaly
//     itself only exists because Current.Game.GetComponent<> would return null) -
//     a silent no-op read back as success:true is exactly the bug this project
//     keeps finding, so it is refused here instead.
//   - The sand grid is Odyssey-only. SandGrid's own constructor only allocates its
//     backing array when ModLister.CheckOdyssey passes; off-Odyssey, SetDepth
//     checks depthGrid.IsCreated and silently does nothing. Refused here too.
//
// THREAD AFFINITY: same rule as every other file here. Everything that touches
// game state is inside ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;
using Verse.Sound;   // SoundStarter.PlayOneShot and SoundInfo both live here, not in Verse

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ---- local helpers (this file only - do not redefine the shared ones) ----

        // A thing-by-id lookup that also reaches into pawns' equipment / apparel /
        // inventory, mirroring jawa/thing_stats. Named distinctively so it cannot
        // collide with a sibling Group file's own helper of a similar purpose.
        private static Thing SystemToolsFindThing(string id, out string err)
        {
            err = null;
            if (string.IsNullOrWhiteSpace(id)) { err = "Give a thing id."; return null; }
            var tok = id.Trim();
            var bare = tok.StartsWith("Thing_", StringComparison.OrdinalIgnoreCase) ? tok.Substring(6) : tok;
            var defCandidates = new List<string>();

            Func<Thing, bool> matches = t => t != null && (t.ThingID == tok || t.ThingID == bare);

            if (Find.Maps != null)
            {
                foreach (var m in Find.Maps)
                {
                    foreach (var t in m.listerThings.AllThings)
                    {
                        if (matches(t)) return t;
                        if (t.def != null && string.Equals(t.def.defName, bare, StringComparison.OrdinalIgnoreCase) && defCandidates.Count < 10)
                            defCandidates.Add(t.ThingID);
                    }
                    foreach (var p in m.mapPawns.AllPawnsSpawned)
                    {
                        if (p.equipment != null)
                            foreach (var t in p.equipment.AllEquipmentListForReading) if (matches(t)) return t;
                        if (p.apparel != null)
                            foreach (var t in p.apparel.WornApparel) if (matches(t)) return t;
                        if (p.inventory != null && p.inventory.innerContainer != null)
                            foreach (var t in p.inventory.innerContainer) if (matches(t)) return t;
                    }
                }
            }

            err = defCandidates.Count > 0
                ? "'" + bare + "' is a defName, not an id. Live ids with that def: " + string.Join(", ", defCandidates)
                : "No live thing with id '" + bare + "' on any loaded map, or in any pawn's equipment/apparel/inventory.";
            return null;
        }

        // Parses "x,z,w,h" or a single "x,z" into the in-bounds cell list. Shared by
        // roof_collapse and depth_grid, both of which act over a rect or one cell.
        private static bool SystemToolsCells(string rect, int x, int z, Map map, out List<IntVec3> cells, out string err)
        {
            cells = new List<IntVec3>();
            err = null;
            var size = map.Size;

            if (!string.IsNullOrWhiteSpace(rect))
            {
                var parts = rect.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries);
                int rx, rz, rw, rh;
                if (parts.Length != 4
                    || !int.TryParse(parts[0].Trim(), out rx) || !int.TryParse(parts[1].Trim(), out rz)
                    || !int.TryParse(parts[2].Trim(), out rw) || !int.TryParse(parts[3].Trim(), out rh))
                { err = "rect must be 'x,z,w,h', e.g. '170,170,18,10'."; return false; }
                if (rw <= 0 || rh <= 0) { err = "rect width and height must be positive."; return false; }
                if ((long)rw * rh > 4096L)
                { err = "rect covers " + ((long)rw * rh) + " cells; the cap is 4096."; return false; }
                for (int cx = rx; cx < rx + rw; cx++)
                    for (int cz = rz; cz < rz + rh; cz++)
                    {
                        if (cx < 0 || cz < 0 || cx >= size.x || cz >= size.z) continue;
                        cells.Add(new IntVec3(cx, 0, cz));
                    }
                if (cells.Count == 0) { err = "The whole rect is outside the map."; return false; }
                return true;
            }

            if (x < 0 || z < 0) { err = "Give x and z, or rect."; return false; }
            if (x >= size.x || z >= size.z) { err = "Cell is outside the map."; return false; }
            cells.Add(new IntVec3(x, 0, z));
            return true;
        }

        // ================================================================
        //  jawa/thing_minify
        // ================================================================
        [Tool(
            "jawa/thing_minify",
            Description =
                "Turn a spawned, minifiable thing (an installed building, mostly) into a carryable " +
                "MinifiedThing placed near its old position - what the deconstruct-to-carry gizmo does. " +
                "Wraps Thing.Uninstall(), reimplemented here (not called directly) only so a caller can " +
                "choose the DestroyMode via MinifyUtility.MakeMinified underneath; the default 'Vanish' " +
                "matches vanilla Uninstall exactly. " +
                "⚠ A thing whose def is not Minifiable is REFUSED BY NAME, not silently ignored - " +
                "MinifyUtility.MakeMinified itself only logs a warning and returns null on that thing, " +
                "which would otherwise look like nothing happened for no reason. " +
                "⚠ The thing must be Spawned on a map; an unspawned thing (already in an inventory, " +
                "already minified) is refused rather than attempted.",
            ResultDescription =
                "success, sourceThing (id, defName, label), minified (id, defName, label, position, " +
                "map), destroyMode.")]
        public static async Task<object> ThingMinify(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Thing id to minify/uninstall, as returned by jawa/list_things.")]
            string thing = null,
            [ToolParameter(Description = "DestroyMode passed to MinifyUtility.MakeMinified: Vanish, KillFinalize, KillFinalizeLeavingsOnly, Deconstruct, FailConstruction, Cancel, Refund. Default Vanish, matching vanilla Uninstall.")]
            string destroyMode = "Vanish")
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string terr;
                var t = SystemToolsFindThing(thing, out terr);
                if (t == null) return Fail(terr ?? "No thing.");

                if (t.def == null || !t.def.Minifiable)
                    return Fail("'" + (t.def != null ? t.def.defName : "?") + "' is not Minifiable. MinifyUtility.MakeMinified would silently warn and return null on this thing.");
                if (!t.Spawned)
                    return Fail(t.ThingID + " is not Spawned. Only a thing standing on a map can be uninstalled.");

                DestroyMode dm;
                if (!Enum.TryParse(destroyMode, true, out dm))
                    return Fail("Unknown destroyMode '" + destroyMode + "'. Valid: " + string.Join(", ", Enum.GetNames(typeof(DestroyMode))));

                var sourceId = t.ThingID;
                var sourceDef = t.def.defName;
                var sourceLabel = t.LabelCap.ToString();
                var map = t.Map;
                var pos = t.Position;
                bool wasSelected = Find.Selector != null && Find.Selector.IsSelected(t);

                MinifiedThing minified;
                try { minified = t.MakeMinified(dm); }
                catch (Exception ex) { return Fail("MakeMinified threw: " + ex.GetType().Name + ": " + ex.Message); }
                if (minified == null) return Fail("MakeMinified returned null for " + sourceId + ".");

                Thing placed;
                bool ok = GenPlace.TryPlaceThing(minified, pos, map, ThingPlaceMode.Near, out placed);
                if (!ok) return Fail("MakeMinified succeeded but GenPlace.TryPlaceThing found no spot near " + pos + " on map " + map.Index + ".");

                // SoundStarter.PlayOneShot is the extension on SoundDef; the TargetInfo
                // overload lives on SoundStarter too, as PlayOneShot(SoundDef, SoundInfo).
                try { SoundDefOf.ThingUninstalled.PlayOneShot(SoundInfo.InMap(new TargetInfo(pos, map))); } catch { }
                if (wasSelected && Find.Selector != null)
                { try { Find.Selector.Select(placed, false, false); } catch { } }

                return new
                {
                    success = true,
                    message = sourceLabel + " minified.",
                    sourceThing = new { id = sourceId, defName = sourceDef, label = sourceLabel },
                    minified = new
                    {
                        id = placed.ThingID,
                        defName = placed.def != null ? placed.def.defName : null,
                        label = placed.LabelCap.ToString(),
                        position = new { x = placed.Position.x, z = placed.Position.z },
                        map = map.Index
                    },
                    destroyMode = dm.ToString(),
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/roof_collapse
        // ================================================================
        [Tool(
            "jawa/roof_collapse",
            Description =
                "Drop the roof over a cell or rect via RoofCollapserImmediate.DropRoofInCells, crushing " +
                "whatever is underneath. Only cells that are ACTUALLY ROOFED are dropped - the engine " +
                "silently skips an unroofed cell, so this tool reports roofedCells separately from " +
                "cellsRequested: a low roofedCells with an empty crushed[] means 'nothing was roofed " +
                "here', while a roofedCells count with an empty crushed[] means 'roofed, but nothing " +
                "worth mentioning was under it' (only Buildings, Pawns, and Items worth >0.01 market " +
                "value are reported - filth and cheap debris are not, matching vanilla's crush letter).",
            ResultDescription =
                "success, cellsRequested, roofedCells (how many actually had a roof), " +
                "crushed[]: id, defName, label, category - each thing WorthMentioningInCrushLetter caught.")]
        public static async Task<object> RoofCollapse(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Cell X. Use with z for a single cell.")]
            int x = -1,
            [ToolParameter(Description = "Cell Z.")]
            int z = -1,
            [ToolParameter(Description = "Rect 'x,z,w,h' instead of a single cell. Cap 4096 cells.")]
            string rect = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string merr;
                var map = MapOrNull(out merr);
                if (map == null) return Fail(merr);

                List<IntVec3> cells;
                string cerr;
                if (!SystemToolsCells(rect, x, z, map, out cells, out cerr)) return Fail(cerr);

                int roofed = 0;
                foreach (var c in cells) if (c.Roofed(map)) roofed++;

                var crushed = new List<Thing>();
                try { RoofCollapserImmediate.DropRoofInCells(cells, map, crushed); }
                catch (Exception ex) { return Fail("DropRoofInCells threw: " + ex.GetType().Name + ": " + ex.Message); }

                return new
                {
                    success = true,
                    message = roofed + " of " + cells.Count + " requested cell(s) were roofed and dropped; " + crushed.Count + " thing(s) crushed.",
                    cellsRequested = cells.Count,
                    roofedCells = roofed,
                    crushed = crushed.Select(t => (object)new
                    {
                        id = t.ThingID,
                        defName = t.def != null ? t.def.defName : null,
                        label = t.LabelCap.ToString(),
                        category = t.def != null ? t.def.category.ToString() : null
                    }).ToList(),
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/depth_grid_set
        // ================================================================
        [Tool(
            "jawa/depth_grid_set",
            Description =
                "Set per-cell depth (0-1) on the SNOW or SAND grid via SnowGrid.SetDepth / " +
                "SandGrid.SetDepth, then read it back with GetDepth so the write is proven, not assumed " +
                "- both grids clamp and can reject a cell (e.g. under a full-fill building, or a floor " +
                "that does not holdSnowOrSand), so the readback can legitimately differ from what you asked for. " +
                "⚠ ⚠ SAND IS ODYSSEY-ONLY. SandGrid only allocates its backing array when " +
                "ModsConfig.OdysseyActive was true when the map's grids were built; without it, " +
                "SetDepth silently does nothing (depthGrid.IsCreated is false) rather than throwing. " +
                "This tool checks ModsConfig.OdysseyActive itself and REFUSES grid=sand when it is off, " +
                "rather than letting that no-op through as success.",
            ResultDescription =
                "success, grid, cellsRequested, cellsWritten[]: x, z, requestedDepth, actualDepth " +
                "(post-clamp readback), and mapTotalDepth (SnowGrid/SandGrid.TotalDepth after the write).")]
        public static async Task<object> DepthGridSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'snow' or 'sand'.")]
            string grid = null,
            [ToolParameter(Description = "Depth to set, 0-1 (clamped by the engine).")]
            float depth = 0f,
            [ToolParameter(Description = "Cell X. Use with z for a single cell.")]
            int x = -1,
            [ToolParameter(Description = "Cell Z.")]
            int z = -1,
            [ToolParameter(Description = "Rect 'x,z,w,h' instead of a single cell. Cap 4096 cells.")]
            string rect = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string merr;
                var map = MapOrNull(out merr);
                if (map == null) return Fail(merr);

                var g = (grid ?? "").Trim().ToLowerInvariant();
                if (g != "snow" && g != "sand")
                    return Fail("grid must be 'snow' or 'sand', got '" + grid + "'.");
                if (g == "sand" && !ModsConfig.OdysseyActive)
                    return Fail("The sand grid is Odyssey-only (ModsConfig.OdysseyActive is false). " +
                                "SandGrid.SetDepth would silently no-op on this map rather than write anything.");

                List<IntVec3> cells;
                string cerr;
                if (!SystemToolsCells(rect, x, z, map, out cells, out cerr)) return Fail(cerr);

                var rows = new List<object>();
                if (g == "snow")
                {
                    if (map.snowGrid == null) return Fail("map.snowGrid is null.");
                    foreach (var c in cells)
                    {
                        map.snowGrid.SetDepth(c, depth);
                        rows.Add(new { x = c.x, z = c.z, requestedDepth = depth, actualDepth = map.snowGrid.GetDepth(c) });
                    }
                }
                else
                {
                    if (map.sandGrid == null) return Fail("map.sandGrid is null.");
                    foreach (var c in cells)
                    {
                        map.sandGrid.SetDepth(c, depth);
                        rows.Add(new { x = c.x, z = c.z, requestedDepth = depth, actualDepth = map.sandGrid.GetDepth(c) });
                    }
                }

                return new
                {
                    success = true,
                    message = rows.Count + " cell(s) written on the " + g + " grid.",
                    grid = g,
                    cellsRequested = cells.Count,
                    cellsWritten = rows,
                    mapTotalDepth = g == "snow" ? map.snowGrid.TotalDepth : map.sandGrid.TotalDepth,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/anomaly_monolith_get
        // ================================================================
        [Tool(
            "jawa/anomaly_monolith_get",
            Description =
                "Read where the Anomaly monolith arc stands: GameComponent_Anomaly's Level/LevelDef, " +
                "NextLevelDef, HighestLevelReached, AmbientHorrorMode and related flags. " +
                "⚠ ⚠ REQUIRES ModsConfig.AnomalyActive - refused by name when the DLC is off, rather " +
                "than reading Find.Anomaly against a GameComponent that was never added to this game.",
            ResultDescription =
                "success, level, levelDef, nextLevelDef, highestLevelReached, ambientHorrorMode, " +
                "monolithSpawned, generateMonolith, questlineEnded, anomalyStudyEnabled, " +
                "anomalyThreatFractionNow, ticksSinceLastLevelChange.")]
        public static async Task<object> AnomalyMonolithGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                if (!ModsConfig.AnomalyActive)
                    return Fail("ModsConfig.AnomalyActive is false. The Anomaly DLC is not active, so there is no monolith arc to read.");

                var a = Find.Anomaly;
                if (a == null) return Fail("Find.Anomaly returned null (GameComponent_Anomaly missing from this game).");

                return new
                {
                    success = true,
                    level = a.Level,
                    levelDef = a.LevelDef != null ? a.LevelDef.defName : null,
                    nextLevelDef = a.NextLevelDef != null ? a.NextLevelDef.defName : null,
                    highestLevelReached = a.HighestLevelReached,
                    ambientHorrorMode = a.AmbientHorrorMode,
                    monolithSpawned = a.MonolithSpawned,
                    generateMonolith = a.GenerateMonolith,
                    questlineEnded = a.QuestlineEnded,
                    anomalyStudyEnabled = a.AnomalyStudyEnabled,
                    anomalyThreatFractionNow = a.AnomalyThreatFractionNow,
                    ticksSinceLastLevelChange = a.TicksSinceLastLevelChange,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/anomaly_codex_discover
        // ================================================================
        [Tool(
            "jawa/anomaly_codex_discover",
            Description =
                "Mark an EntityCodexEntryDef discovered via EntityCodex.SetDiscovered - the way finding " +
                "or studying an entity unlocks its codex page and, if configured, sends the discovery " +
                "letter and unlocks research. " +
                "⚠ ⚠ REQUIRES ModsConfig.AnomalyActive - EntityCodex.SetDiscovered itself checks " +
                "ModLister.CheckAnomaly and no-ops without it (returns having done nothing, no error), " +
                "so this tool refuses by name up front instead of returning success:true for nothing.",
            ResultDescription =
                "success, entry, alreadyDiscoveredBefore, discoveredNow, category, discoveredDef " +
                "(the ThingDef credited, if any).")]
        public static async Task<object> AnomalyCodexDiscover(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "EntityCodexEntryDef defName to mark discovered.")]
            string entry = null,
            [ToolParameter(Description = "Optional ThingDef defName credited as the discovered entity (EntityCodex.SetDiscovered's discoveredDef).")]
            string discoveredDefName = null,
            [ToolParameter(Description = "Optional live thing id credited as the discovering Thing (EntityCodex.SetDiscovered's discoveredThing).")]
            string discoveredThing = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                if (!ModsConfig.AnomalyActive)
                    return Fail("ModsConfig.AnomalyActive is false. EntityCodex.SetDiscovered would silently no-op on every entry.");
                if (string.IsNullOrWhiteSpace(entry)) return Fail("Give an EntityCodexEntryDef defName in 'entry'.");

                var ed = DefDatabase<EntityCodexEntryDef>.GetNamedSilentFail(entry.Trim());
                if (ed == null) return Fail("No EntityCodexEntryDef '" + entry + "'.", new { suggestions = DefSuggestions<EntityCodexEntryDef>(entry) });

                ThingDef discDef = null;
                if (!string.IsNullOrWhiteSpace(discoveredDefName))
                {
                    discDef = DefDatabase<ThingDef>.GetNamedSilentFail(discoveredDefName.Trim());
                    if (discDef == null) return Fail("No ThingDef '" + discoveredDefName + "'.", new { suggestions = DefSuggestions<ThingDef>(discoveredDefName) });
                }

                Thing discThing = null;
                if (!string.IsNullOrWhiteSpace(discoveredThing))
                {
                    string terr;
                    discThing = SystemToolsFindThing(discoveredThing, out terr);
                    if (discThing == null) return Fail(terr ?? "No thing.");
                }

                var codex = Find.EntityCodex;
                if (codex == null) return Fail("Find.EntityCodex is null.");
                bool before = codex.Discovered(ed);

                try { codex.SetDiscovered(ed, discDef, discThing); }
                catch (Exception ex) { return Fail("EntityCodex.SetDiscovered threw: " + ex.GetType().Name + ": " + ex.Message); }

                bool after = codex.Discovered(ed);

                return new
                {
                    success = true,
                    message = ed.defName + (after ? " is discovered." : " did not register as discovered - check the entry's category."),
                    entry = ed.defName,
                    alreadyDiscoveredBefore = before,
                    discoveredNow = after,
                    category = ed.category != null ? ed.category.defName : null,
                    discoveredDef = discDef != null ? discDef.defName : null,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/dlc_status
        // ================================================================
        [Tool(
            "jawa/dlc_status",
            Description =
                "Read ModsConfig's five expansion-active flags in one call - Royalty, Ideology, " +
                "Biotech, Anomaly, Odyssey. THIS IS THE GUARD every Anomaly tool (jawa/anomaly_*) and " +
                "the sand half of jawa/depth_grid_set need before you call them: those refuse by name " +
                "when the matching flag is false rather than silently doing nothing, and this tool is " +
                "how you check first instead of finding out from a refusal.",
            ResultDescription = "success, royaltyActive, ideologyActive, biotechActive, anomalyActive, odysseyActive.")]
        public static async Task<object> DlcStatus(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                return new
                {
                    success = true,
                    royaltyActive = ModsConfig.RoyaltyActive,
                    ideologyActive = ModsConfig.IdeologyActive,
                    biotechActive = ModsConfig.BiotechActive,
                    anomalyActive = ModsConfig.AnomalyActive,
                    odysseyActive = ModsConfig.OdysseyActive,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/autosave_now
        // ================================================================
        [Tool(
            "jawa/autosave_now",
            Description =
                "Trigger Find.Autosaver.DoAutosave() immediately - the same call the storyteller's " +
                "autosave timer makes, choosing an autosave slot (or the permadeath save name) and " +
                "writing it. " +
                "⚠ Unlike the vanilla path, this does NOT go through LongEventHandler.QueueLongEvent - " +
                "it saves SYNCHRONOUSLY on the main thread, which is fine for a bridge call but will " +
                "hitch a frame on a large save. " +
                "⚠ GameDataSaveLoader.SaveGame swallows its own exceptions (logs and returns), so a " +
                "write failure shows up in Player.log, not in this tool's result - this tool can only " +
                "report that the call returned, not that the file is good.",
            ResultDescription = "success, ticksGame at the moment of the call. Check Player.log for write errors.")]
        public static async Task<object> AutosaveNow(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                if (Find.Autosaver == null) return Fail("Find.Autosaver is null.");

                try { Find.Autosaver.DoAutosave(); }
                catch (Exception ex) { return Fail("DoAutosave threw: " + ex.GetType().Name + ": " + ex.Message); }

                return new
                {
                    success = true,
                    message = "DoAutosave() called synchronously. Check Player.log for any write error - SaveGame swallows its own exceptions.",
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/savegame_mod_match
        // ================================================================
        [Tool(
            "jawa/savegame_mod_match",
            Description =
                "Does the LAST LOADED save's mod list match the mods running right now? Wraps " +
                "ScribeMetaHeaderUtility.LoadedModsMatchesActiveMods, which compares the static " +
                "loadedModIdsList (populated by LoadGameDataHeader whenever a save's meta header was " +
                "read) against LoadedModManager.RunningMods. " +
                "⚠ This reads the meta header from the MOST RECENT LOAD this process performed, not " +
                "the currently running game's def-loaded state re-verified live - if nothing has been " +
                "loaded yet this session, loadedModsSummary reads 'None' and matches is false, which is " +
                "a true answer, not a bug.",
            ResultDescription = "success, matches, loadedModsSummary, runningModsSummary.")]
        public static async Task<object> SavegameModMatch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string loadedSummary, runningSummary;
                bool matches;
                try { matches = ScribeMetaHeaderUtility.LoadedModsMatchesActiveMods(out loadedSummary, out runningSummary); }
                catch (Exception ex) { return Fail("LoadedModsMatchesActiveMods threw: " + ex.GetType().Name + ": " + ex.Message); }

                return new
                {
                    success = true,
                    matches,
                    loadedModsSummary = loadedSummary,
                    runningModsSummary = runningSummary,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/mod_inventory
        // ================================================================
        [Tool(
            "jawa/mod_inventory",
            Description =
                "List every running mod via LoadedModManager.RunningModsListForReading, in load order, " +
                "with packageId and the names of the assemblies it actually loaded " +
                "(ModContentPack.assemblies.loadedAssemblies) - not what an About.xml claims, what the " +
                "engine loaded.",
            ResultDescription =
                "success, count, mods[]: loadOrder, name, packageId, folderName, isCoreMod, isOfficial, " +
                "assemblyCount, assemblies[] (short names).")]
        public static async Task<object> ModInventory(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Keep only mods whose name or packageId contains this (case-insensitive). Empty returns all.")]
            string filter = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var all = LoadedModManager.RunningModsListForReading;
                if (all == null) return Fail("LoadedModManager.RunningModsListForReading is null.");

                IEnumerable<ModContentPack> query = all;
                if (!string.IsNullOrWhiteSpace(filter))
                {
                    var f = filter.Trim();
                    query = query.Where(m =>
                        (m.Name != null && m.Name.IndexOf(f, StringComparison.OrdinalIgnoreCase) >= 0)
                        || (m.PackageId != null && m.PackageId.IndexOf(f, StringComparison.OrdinalIgnoreCase) >= 0));
                }

                var rows = query.Select(m =>
                {
                    List<string> asmNames;
                    try { asmNames = m.assemblies != null ? m.assemblies.loadedAssemblies.Select(a => a.GetName().Name).ToList() : new List<string>(); }
                    catch { asmNames = new List<string>(); }
                    return (object)new
                    {
                        loadOrder = m.loadOrder,
                        name = m.Name,
                        packageId = m.PackageId,
                        folderName = m.FolderName,
                        isCoreMod = m.IsCoreMod,
                        isOfficial = m.IsOfficialMod,
                        assemblyCount = asmNames.Count,
                        assemblies = asmNames
                    };
                }).ToList();

                if (rows.Count == 0)
                    return Fail("No running mod matched filter '" + filter + "'. Nothing was measured.");

                return new
                {
                    success = true,
                    count = rows.Count,
                    mods = rows,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/stat_cache_bust
        // ================================================================
        [Tool(
            "jawa/stat_cache_bust",
            Description =
                "Clear a StatWorker's cache - required after editing quality, stuff or hediffs out from " +
                "under a stat the game already cached, or a stale value keeps reading. With 'thing', " +
                "calls StatWorker.ClearCacheForThing(thing) (that one thing's entry only); without it, " +
                "calls StatWorker.DeleteStatCache() (the WHOLE cache for that stat, every thing). Name " +
                "stats with 'stats'; leave it empty to bust every StatDef's cache (heavy, but this is a " +
                "diagnostic tool, not a hot path).",
            ResultDescription = "success, mode ('perThing' or 'wholeCache'), thing (if given), statsCleared[], count.")]
        public static async Task<object> StatCacheBust(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated StatDef defNames. Empty means every StatDef.")]
            string stats = null,
            [ToolParameter(Description = "Thing id (jawa/list_things) to clear ONLY that thing's cache entry. Omit to delete the whole cache for the named stat(s) instead.")]
            string thing = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();

                Thing t = null;
                if (!string.IsNullOrWhiteSpace(thing))
                {
                    string terr;
                    t = SystemToolsFindThing(thing, out terr);
                    if (t == null) return Fail(terr ?? "No thing.");
                }

                var refused = new List<object>();
                var cleared = new List<string>();
                List<StatDef> targets;
                if (!string.IsNullOrWhiteSpace(stats))
                {
                    targets = new List<StatDef>();
                    foreach (var raw in stats.Split(new[] { ',', ';', '\n' }, StringSplitOptions.RemoveEmptyEntries))
                    {
                        var nm = raw.Trim();
                        if (nm.Length == 0) continue;
                        var sd = DefDatabase<StatDef>.GetNamedSilentFail(nm);
                        if (sd == null) { refused.Add(new { stat = nm, reason = "NoSuchStatDef", suggestions = DefSuggestions<StatDef>(nm) }); continue; }
                        targets.Add(sd);
                    }
                    if (targets.Count == 0) return Fail("No named stat resolved. Nothing was cleared.", new { refused });
                }
                else
                {
                    targets = DefDatabase<StatDef>.AllDefsListForReading.ToList();
                }

                foreach (var sd in targets)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    if (sd.Worker == null) continue;
                    try
                    {
                        if (t != null) sd.Worker.ClearCacheForThing(t);
                        else sd.Worker.DeleteStatCache();
                        cleared.Add(sd.defName);
                    }
                    catch (Exception ex) { refused.Add(new { stat = sd.defName, reason = ex.GetType().Name, message = ex.Message }); }
                }

                return new
                {
                    success = true,
                    message = cleared.Count + " StatDef cache(s) cleared" + (t != null ? " for " + t.ThingID + "." : " (whole cache)."),
                    mode = t != null ? "perThing" : "wholeCache",
                    thing = t != null ? t.ThingID : null,
                    statsCleared = cleared,
                    count = cleared.Count,
                    refused,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/prefs
        // ================================================================
        [Tool(
            "jawa/prefs",
            Description =
                "Read and optionally write Prefs (Verse.Prefs) - devMode, logVerbose, " +
                "autosaveIntervalDays, autosavesCount, pauseOnLoad. Omit every setter to just read. " +
                "🔑 ⚠ ⚠ Prefs.xml IS REWRITTEN FROM THE IN-MEMORY VALUES WHEN THE GAME EXITS - a write " +
                "here that is not followed by Prefs.Save() (which this tool always calls after any " +
                "write) can be clobbered by whatever the game itself holds at exit; even with Save() " +
                "called, a later normal exit re-saves the game's own in-memory copy, which is this same " +
                "value unless something else changed it meanwhile. " +
                "⚠ Turning devMode OFF also clears logVerbose, resetModsConfigOnCrash and DebugSettings.godMode - that is Prefs' own setter, not this tool.",
            ResultDescription = "success, before, after, saved (true if Prefs.Save() was called, i.e. any setter was given).")]
        public static async Task<object> PrefsTool(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Prefs.DevMode. Omit to leave unchanged.")]
            bool? devMode = null,
            [ToolParameter(Description = "Prefs.LogVerbose. Omit to leave unchanged.")]
            bool? logVerbose = null,
            [ToolParameter(Description = "Prefs.AutosaveIntervalDays. Omit to leave unchanged.")]
            float? autosaveIntervalDays = null,
            [ToolParameter(Description = "Prefs.AutosavesCount. Omit to leave unchanged.")]
            int? autosavesCount = null,
            [ToolParameter(Description = "Prefs.PauseOnLoad. Omit to leave unchanged.")]
            bool? pauseOnLoad = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();

                Func<object> snapshot = () => new
                {
                    devMode = Prefs.DevMode,
                    logVerbose = Prefs.LogVerbose,
                    autosaveIntervalDays = Prefs.AutosaveIntervalDays,
                    autosavesCount = Prefs.AutosavesCount,
                    pauseOnLoad = Prefs.PauseOnLoad
                };

                var before = snapshot();
                bool wroteAny = devMode.HasValue || logVerbose.HasValue || autosaveIntervalDays.HasValue
                                || autosavesCount.HasValue || pauseOnLoad.HasValue;

                if (devMode.HasValue) Prefs.DevMode = devMode.Value;
                if (logVerbose.HasValue) Prefs.LogVerbose = logVerbose.Value;
                if (autosaveIntervalDays.HasValue) Prefs.AutosaveIntervalDays = autosaveIntervalDays.Value;
                if (autosavesCount.HasValue) Prefs.AutosavesCount = autosavesCount.Value;
                if (pauseOnLoad.HasValue) Prefs.PauseOnLoad = pauseOnLoad.Value;

                if (wroteAny)
                {
                    try { Prefs.Save(); } catch (Exception ex) { return Fail("Prefs.Save() threw: " + ex.GetType().Name + ": " + ex.Message, new { before, after = snapshot() }); }
                }

                return new
                {
                    success = true,
                    before,
                    after = snapshot(),
                    saved = wroteAny,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
