// JawaBenchDebugGems1.cs - the first batch from a full [DebugAction] sweep. Owner,
// 2026-08-29: "This should have shown up in the very first bridge building" (about
// GenDebug.ClearArea) - correct, and the reason is structural: every prior roster
// pass, including this session's own Find.X sweep, searched TOP-DOWN from a named
// subsystem accessor. A [DebugAction]-tagged method needs neither - the game's own
// debug-tool menu finds it by attribute reflection, with no Find.* linkage at all.
// grepped: 367 [DebugAction( attributes across 17 vanilla files. This file is the
// first, highest-confidence harvest; more may follow.
//
// EVERY SIGNATURE BELOW WAS READ OUT OF 1.6 SOURCE VIA rimsage, NOT GUESSED:
//   Verse/GenDebug.cs           ClearArea(CellRect, Map) - strips roof, destroys
//                               every destroyable Thing in the rect. Does NOT touch
//                               terrain. SpawnArea(CellRect, Map, ThingDef) - one
//                               GenSpawn.Spawn per cell in the rect.
//   Verse/DebugToolsGeneral.cs  MakeEmptyRoom() (private, reimplemented here with
//                               configurable stuff/floor/roof rather than the
//                               debug tool's hardcoded wood/RoofConstructed/
//                               WoodPlankFloor): ClearArea the rect, wall the edge
//                               (one cell becomes a door), roof + floor the interior.
//   Verse/GenExplosion.cs       DoExplosion(center, map, radius, damType, ...) - the
//                               full public signature is 30+ params with defaults;
//                               this tool exposes the load-bearing subset (damAmount
//                               defaults to damType.defaultDamage when omitted, same
//                               as the engine's own default path).
//   RimWorld/Precept_Ritual.cs  activeObligations (public List<RitualObligation>),
//                               RemoveObligation(RitualObligation, completed=false) -
//                               the removal half jawa/ideo_ritual_obligation's own
//                               ADD never got a sibling for.
//   Verse/PlayDataLoader.cs     HotReloadDefs() - see the tool's own Description for
//                               what this does and does not cover. Read in full.
//
// 🔴 BULK-DESTROY FILTERS (jawa/destroy_bulk) ARE THIS FILE'S OWN LOGIC, not lifted
// from the private debug methods (DebugToolsPawns.cs's own filters were not read -
// the labels "factionless animals"/"player animals"/"non-colonists" are
// self-describing and implemented directly against Pawn.Faction/RaceProps/
// IsColonist, the same predicates used throughout this bridge already).
//
// GATING follows the rule stated across every other file here: #if JAWA_GM_TOOLS is
// for tools that make THE WORLD ACT on the player.
//   GATED:   jawa/explosion_at (damages/can kill anything in a live colony, same
//            tier as jawa/fire_raid).
//   UNGATED: jawa/clear_area, jawa/spawn_fill_area, jawa/make_empty_room (map
//            authoring, same tier as jawa/build_batch/prefab_place),
//            jawa/destroy_bulk (destructive but scoped to non-colonist/animal
//            pawns, dryRun defaults true), jawa/ideo_ritual_obligation_remove
//            (matches its own ADD sibling, already ungated),
//            jawa/hot_reload_defs (a maintenance/dev operation, not an incident -
//            same reasoning as jawa/map_commit).
//
// THREAD AFFINITY: everything that touches game state is inside
// ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ================================================================
        //  Clear / fill a rect
        // ================================================================

        [Tool(
            "jawa/clear_area",
            Description =
                "GenDebug.ClearArea(rect, map) - the exact method behind the dev-tool menu's " +
                "own 'Clear area (rect)' action. Strips roof over the rect, then destroys " +
                "every Thing in it whose def.destroyable is true (buildings, plants, items - " +
                "and, per source, ANYTHING ELSE destroyable standing there, pawns included if " +
                "their def allows it). Does NOT touch terrain - floor/under layers survive; " +
                "use jawa/set_terrain_layer for that. Destructive default is OFF: dryRun " +
                "defaults true and only reports what would be destroyed.",
            ResultDescription =
                "success, dryRun, rect, roofedCellsBefore, destroyedCount, destroyed[] " +
                "(thingId, def, label, category) - populated in both modes.")]
        public static async Task<object> ClearArea(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Rect 'x,z,w,h'. Required.")]
            string rect = null,
            [ToolParameter(Description = "true = report only, destroy nothing. Default true.")]
            bool dryRun = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                CellRect r;
                if (!TryRect(rect, map, out r, out err)) return Fail(err);

                int roofedBefore = 0;
                var toDestroy = new List<object>();
                var seenThingIds = new HashSet<int>();
                foreach (var c in r)
                {
                    if (c.Roofed(map)) roofedBefore++;
                    foreach (var t in c.GetThingList(map).ToList())
                        if (t.def.destroyable && seenThingIds.Add(t.thingIDNumber))
                            toDestroy.Add(new { thingId = t.ThingID, def = t.def.defName, label = t.LabelCap, category = t.def.category.ToString() });
                }

                if (dryRun)
                    return new { success = true, dryRun = true, rect = new { x = r.minX, z = r.minZ, w = r.Width, h = r.Height }, roofedCellsBefore = roofedBefore, destroyedCount = toDestroy.Count, destroyed = toDestroy, ticksGame = TicksGameSafe() };

                try { GenDebug.ClearArea(r, map); }
                catch (Exception e) { return Fail("GenDebug.ClearArea threw " + e.GetType().Name + ": " + e.Message, new { destroyed = toDestroy }); }

                return new
                {
                    success = true,
                    dryRun = false,
                    rect = new { x = r.minX, z = r.minZ, w = r.Width, h = r.Height },
                    roofedCellsBefore = roofedBefore,
                    destroyedCount = toDestroy.Count,
                    destroyed = toDestroy,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/spawn_fill_area",
            Description =
                "GenDebug.SpawnArea(rect, map, def) - one GenSpawn.Spawn(def, cell, map) PER " +
                "CELL in the rect, unconditionally. No collision check, no wipe - a cell " +
                "already occupied gets an overlapping spawn (matches the engine's own debug " +
                "tool exactly, which does the same thing). Use jawa/wipe_cell or " +
                "jawa/clear_area first if the rect is not already empty. " +
                "🔴 GenDebug.SpawnArea discards each per-cell GenSpawn.Spawn() return value, " +
                "and Spawn() returns null WITHOUT THROWING on out-of-bounds or a failed " +
                "def.CanSpawnAt(cell, rot, map) check (Verse/GenSpawn.cs) - so this tool spawns " +
                "cell-by-cell itself instead of delegating to GenDebug.SpawnArea, and " +
                "cellsFilled counts only cells whose Spawn() actually returned a spawned Thing.",
            ResultDescription = "success, rect, thingDef, cellsRequested, cellsFilled, failed[] (x, z, reason).")]
        public static async Task<object> SpawnFillArea(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Rect 'x,z,w,h'. Required.")]
            string rect = null,
            [ToolParameter(Description = "ThingDef defName to spawn at every cell. Required.")]
            string thingDef = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                CellRect r;
                if (!TryRect(rect, map, out r, out err)) return Fail(err);
                if (string.IsNullOrWhiteSpace(thingDef)) return Fail("Give 'thingDef'.");
                var def = DefDatabase<ThingDef>.GetNamedSilentFail(thingDef.Trim());
                if (def == null) return Fail("No ThingDef '" + thingDef + "'.", DefSuggestions<ThingDef>(thingDef));

                int filled = 0;
                var failed = new List<object>();
                foreach (var c in r)
                {
                    Thing spawned;
                    try { spawned = GenSpawn.Spawn(def, c, map); }
                    catch (Exception e) { failed.Add(new { x = c.x, z = c.z, reason = e.GetType().Name + ": " + e.Message }); continue; }
                    if (spawned != null && spawned.Spawned) filled++;
                    else failed.Add(new { x = c.x, z = c.z, reason = "GenSpawn.Spawn returned null (CanSpawnAt refused or out of bounds)" });
                }

                return new
                {
                    success = true,
                    rect = new { x = r.minX, z = r.minZ, w = r.Width, h = r.Height },
                    thingDef = def.defName,
                    cellsRequested = r.Area,
                    cellsFilled = filled,
                    failed,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/make_empty_room",
            Description =
                "Instant scratch room - reimplements the dev-tool menu's 'Make empty room " +
                "(rect)' with configurable materials instead of its hardcoded wood/" +
                "RoofConstructed/WoodPlankFloor: GenDebug.ClearArea the rect first, then wall " +
                "every edge cell (one random non-corner edge cell becomes a door instead), " +
                "then roof + floor every interior cell. Player-faction walls and door.",
            ResultDescription = "success, rect, wallDef, floorDef, doorAt, cellsWalled, cellsFloored.")]
        public static async Task<object> MakeEmptyRoom(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Rect 'x,z,w,h'. Required.")]
            string rect = null,
            [ToolParameter(Description = "Wall ThingDef defName. Default 'Wall'.")]
            string wallDef = "Wall",
            [ToolParameter(Description = "Wall/door stuff ThingDef defName. Default 'WoodLog'.")]
            string stuffDef = "WoodLog",
            [ToolParameter(Description = "Door ThingDef defName. Default 'Door'.")]
            string doorDef = "Door",
            [ToolParameter(Description = "Floor TerrainDef defName. Default 'WoodPlankFloor'.")]
            string floorDef = "WoodPlankFloor",
            [ToolParameter(Description = "Roof RoofDef defName. Default 'RoofConstructed'.")]
            string roofDef = "RoofConstructed")
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                CellRect r;
                if (!TryRect(rect, map, out r, out err)) return Fail(err);
                if (r.Width < 3 || r.Height < 3) return Fail("Rect must be at least 3x3 to have an interior.");

                var wDef = DefDatabase<ThingDef>.GetNamedSilentFail(wallDef.Trim());
                if (wDef == null) return Fail("No ThingDef '" + wallDef + "'.", DefSuggestions<ThingDef>(wallDef));
                var sDef = DefDatabase<ThingDef>.GetNamedSilentFail(stuffDef.Trim());
                if (sDef == null) return Fail("No ThingDef '" + stuffDef + "'.", DefSuggestions<ThingDef>(stuffDef));
                var dDef = DefDatabase<ThingDef>.GetNamedSilentFail(doorDef.Trim());
                if (dDef == null) return Fail("No ThingDef '" + doorDef + "'.", DefSuggestions<ThingDef>(doorDef));
                var fDef = DefDatabase<TerrainDef>.GetNamedSilentFail(floorDef.Trim());
                if (fDef == null) return Fail("No TerrainDef '" + floorDef + "'.", DefSuggestions<TerrainDef>(floorDef));
                var rDef = DefDatabase<RoofDef>.GetNamedSilentFail(roofDef.Trim());
                if (rDef == null) return Fail("No RoofDef '" + roofDef + "'.", DefSuggestions<RoofDef>(roofDef));

                try { GenDebug.ClearArea(r, map); }
                catch (Exception e) { return Fail("ClearArea threw " + e.GetType().Name + ": " + e.Message); }

                var edge = r.EdgeCells.ToList();
                IntVec3 doorCell;
                if (!edge.Where(c => !r.IsCorner(c)).TryRandomElement(out doorCell))
                    return Fail("Could not pick a non-corner edge cell for the door.");

                int walled = 0;
                foreach (var c in edge)
                {
                    var thing = ThingMaker.MakeThing(c == doorCell ? dDef : wDef, sDef);
                    thing.SetFaction(Faction.OfPlayer);
                    if (GenPlace.TryPlaceThing(thing, c, map, ThingPlaceMode.Direct)) walled++;
                }

                int floored = 0;
                foreach (var c in r)
                {
                    map.roofGrid.SetRoof(c, rDef);
                    map.terrainGrid.SetTerrain(c, fDef);
                    floored++;
                }

                return new
                {
                    success = true,
                    rect = new { x = r.minX, z = r.minZ, w = r.Width, h = r.Height },
                    wallDef = wDef.defName,
                    floorDef = fDef.defName,
                    doorAt = new { x = doorCell.x, z = doorCell.z },
                    cellsWalled = walled,
                    cellsFloored = floored,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Bulk pawn cleanup
        // ================================================================

        [Tool(
            "jawa/destroy_bulk",
            Description =
                "Destroy every pawn on the current map matching one filter: " +
                "'factionlessAnimals' (RaceProps.Animal, Faction == null), 'playerAnimals' " +
                "(RaceProps.Animal, Faction == Faction.OfPlayer), 'nonColonists' (!IsColonist). " +
                "Mirrors the dev-tool menu's own bulk-cleanup actions - useful for resetting a " +
                "scratch/quicktest map between runs. Destructive default is OFF: dryRun " +
                "defaults true and only lists what would be destroyed.",
            ResultDescription = "success, dryRun, filter, matchedCount, destroyed[] (thingId, def, label).")]
        public static async Task<object> DestroyBulk(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'factionlessAnimals', 'playerAnimals' or 'nonColonists'. Required.")]
            string filter = null,
            [ToolParameter(Description = "true = report only, destroy nothing. Default true.")]
            bool dryRun = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                string f = (filter ?? "").Trim();
                Func<Pawn, bool> pred;
                if (string.Equals(f, "factionlessAnimals", StringComparison.OrdinalIgnoreCase))
                    pred = p => p.RaceProps != null && p.RaceProps.Animal && p.Faction == null;
                else if (string.Equals(f, "playerAnimals", StringComparison.OrdinalIgnoreCase))
                    pred = p => p.RaceProps != null && p.RaceProps.Animal && p.Faction == Faction.OfPlayer;
                else if (string.Equals(f, "nonColonists", StringComparison.OrdinalIgnoreCase))
                    pred = p => !p.IsColonist;
                else
                    return Fail("filter must be factionlessAnimals, playerAnimals or nonColonists.");

                var matched = map.mapPawns.AllPawnsSpawned.Where(pred).ToList();
                var rows = matched.Select(p => new { thingId = p.ThingID, def = p.def.defName, label = p.LabelShortCap }).ToList();

                if (dryRun)
                    return new { success = true, dryRun = true, filter = f, matchedCount = matched.Count, destroyed = rows, ticksGame = TicksGameSafe() };

                int destroyed = 0;
                foreach (var p in matched)
                {
                    try { p.Destroy(); destroyed++; }
                    catch (Exception e) { return Fail("Destroy threw " + e.GetType().Name + ": " + e.Message + " on " + p.LabelShortCap, new { destroyedSoFar = destroyed }); }
                }

                return new { success = true, dryRun = false, filter = f, matchedCount = matched.Count, destroyed = rows, ticksGame = TicksGameSafe() };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Explosion
        // ================================================================

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/explosion_at",
            Description =
                "*** ACTS ON THE LIVE COLONY *** GenExplosion.DoExplosion at a cell - the same " +
                "utility every bomb/grenade/shell in the game calls. damAmount defaults to " +
                "damType.defaultDamage (the engine's own default) when omitted.",
            ResultDescription = "success, at, radius, damType, damAmount, chanceToStartFire.")]
        public static async Task<object> ExplosionAt(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Cell 'x,z'. Required.")]
            string at = null,
            [ToolParameter(Description = "Explosion radius in cells. Required.")]
            float radius = 0f,
            [ToolParameter(Description = "DamageDef defName, e.g. Bomb, Flame, EMP. Required.")]
            string damType = null,
            [ToolParameter(Description = "Damage amount. <=0 uses damType.defaultDamage.")]
            int damAmount = -1,
            [ToolParameter(Description = "Armor penetration. <0 uses the engine's default (damAmount * 0.015).")]
            float armorPenetration = -1f,
            [ToolParameter(Description = "Chance per cell to start a fire. Default 0.")]
            float chanceToStartFire = 0f,
            [ToolParameter(Description = "Also damage things adjacent to the explosion cells. Default false.")]
            bool applyDamageToNeighbors = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (!TryParseCellLocal(at, out var cell, out err)) return Fail(err);
                if (!cell.InBounds(map)) return Fail("Cell " + cell + " is outside the map (" + map.Size.x + "x" + map.Size.z + ").");
                if (radius <= 0f) return Fail("Give 'radius', greater than 0.");
                if (string.IsNullOrWhiteSpace(damType)) return Fail("Give 'damType', a DamageDef defName.");
                var dDef = DefDatabase<DamageDef>.GetNamedSilentFail(damType.Trim());
                if (dDef == null) return Fail("No DamageDef '" + damType + "'.", DefSuggestions<DamageDef>(damType));

                try
                {
                    GenExplosion.DoExplosion(cell, map, radius, dDef, null, damAmount,
                        armorPenetration, null, null, null, null, null, 0f, 1, null, null, 255,
                        applyDamageToNeighbors, null, 0f, 1, chanceToStartFire);
                }
                catch (Exception e) { return Fail("DoExplosion threw " + e.GetType().Name + ": " + e.Message); }

                return new
                {
                    success = true,
                    at = new { x = cell.x, z = cell.z },
                    radius,
                    damType = dDef.defName,
                    damAmount = damAmount > 0 ? damAmount : dDef.defaultDamage,
                    chanceToStartFire,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
#endif

        // ================================================================
        //  Ritual obligation removal (the sibling jawa/ideo_ritual_obligation never got)
        // ================================================================

        [Tool(
            "jawa/ideo_ritual_obligation_remove",
            Description =
                "The removal half of jawa/ideo_ritual_obligation - Precept_Ritual." +
                "RemoveObligation(obligation). action='list' (default) reads " +
                "activeObligations for a named ritual on a named ideo, resolved the same way " +
                "jawa/ideo_of does; action='remove' takes the obligationId from that list.",
            ResultDescription =
                "list: success, ideo, ritual, obligations[] (obligationId, firstTarget, " +
                "ticksUntilExpiration, stillValid). remove: success, removed{obligationId}, " +
                "obligationCountBefore, obligationCountAfter.")]
        public static async Task<object> IdeoRitualObligationRemove(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Ideo id (numeric) or a substring of its name, per jawa/ideo_of.")]
            string ideo = null,
            [ToolParameter(Description = "PreceptDef defName or label substring matching a Precept_Ritual on this ideo.")]
            string ritual = null,
            [ToolParameter(Description = "'list' (default) or 'remove'.")]
            string action = "list",
            [ToolParameter(Description = "remove: RitualObligation.ID from a prior 'list' call.", DefaultValue = -1)]
            int obligationId = -1)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (!ModsConfig.IdeologyActive) return Fail("Ideology is NOT active. There are no ritual obligations.");
                if (string.IsNullOrWhiteSpace(ideo)) return Fail("Give 'ideo'.");
                if (string.IsNullOrWhiteSpace(ritual)) return Fail("Give 'ritual'.");

                Ideo target;
                var resolveFail = ResolveIdeoArg(ideo, out target);
                if (resolveFail != null) return resolveFail;

                var wanted = ritual.Trim();
                var matches = (target.PreceptsListForReading ?? new List<Precept>()).OfType<Precept_Ritual>().Where(r => r != null && (
                    string.Equals(r.def != null ? r.def.defName : null, wanted, StringComparison.OrdinalIgnoreCase)
                    || (r.def != null && r.def.defName != null && r.def.defName.IndexOf(wanted, StringComparison.OrdinalIgnoreCase) >= 0)
                    || (r.Label ?? "").IndexOf(wanted, StringComparison.OrdinalIgnoreCase) >= 0)).ToList();
                if (matches.Count == 0) return Fail("'" + wanted + "' matches no ritual precept on ideo '" + target.name + "'.");
                if (matches.Count > 1) return Fail("'" + wanted + "' matches " + matches.Count + " ritual precepts ambiguously.");
                var targetRitual = matches[0];
                var obligations = targetRitual.activeObligations ?? new List<RitualObligation>();

                string a = (action ?? "list").Trim().ToLowerInvariant();
                if (a == "list")
                {
                    var rows = obligations.Select(o => new
                    {
                        obligationId = o.ID,
                        firstTarget = o.FirstValidTarget.IsValid ? o.FirstValidTarget.ToString() : null,
                        ticksUntilExpiration = o.TicksUntilExpiration,
                        stillValid = o.StillValid
                    }).ToList();
                    return new { success = true, action = "list", ideo = new { target.id, target.name }, ritual = new { def = targetRitual.def.defName, label = targetRitual.Label }, obligations = rows, ticksGame = TicksGameSafe() };
                }

                if (a == "remove")
                {
                    if (obligationId < 0) return Fail("Give 'obligationId' from a prior action=list call.");
                    var victim = obligations.FirstOrDefault(o => o.ID == obligationId);
                    if (victim == null) return Fail("No active obligation with id " + obligationId + " on this ritual.",
                        new { obligations = obligations.Select(o => o.ID).ToList() });

                    int before = obligations.Count;
                    try { targetRitual.RemoveObligation(victim); }
                    catch (Exception e) { return Fail("RemoveObligation threw " + e.GetType().Name + ": " + e.Message); }
                    int after = targetRitual.activeObligations != null ? targetRitual.activeObligations.Count : 0;

                    return new
                    {
                        success = after < before,
                        removed = new { obligationId },
                        obligationCountBefore = before,
                        obligationCountAfter = after,
                        ticksGame = TicksGameSafe()
                    };
                }

                return Fail("action must be 'list' or 'remove'.");
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Hot reload defs - the headline finding
        // ================================================================

        [Tool(
            "jawa/hot_reload_defs",
            Description =
                "⭐ PlayDataLoader.HotReloadDefs() - the engine's OWN mechanism for reloading " +
                "every active mod's Defs from XML on a LIVE running game, no restart. Read in " +
                "full from source: it re-loads all active mods (LoadedModManager." +
                "LoadAllActiveMods(hotReload:true)), re-resolves cross-references, regenerates " +
                "implied defs, re-matches each already-spawned Thing's ThingComps to the new " +
                "CompProperties (preserving comp state where the class still matches), remaps " +
                "Hediff body parts by index, calls Notify_DefsHotReloaded() on every spawned " +
                "Thing, and rebuilds every map's render mesh. " +
                "🔴 SCOPE: XML/Def changes ONLY - it does NOT reload C# assemblies (the " +
                "companion DLL itself, Harmony patches, or any mod's compiled code). Editing a " +
                "FactionDef, ThingDef, patch XML etc. and calling this is the intended use; a " +
                "code change still needs the DLL rebuilt and the game restarted. " +
                "⚠️ RUNS AS A QUEUED LONG EVENT (LongEventHandler.QueueLongEvent, " +
                "doAsynchronously:false) - this call may return BEFORE the reload has actually " +
                "finished executing; do not trust an immediate follow-up read as proof of " +
                "completion. It also closes every open window as part of its own cleanup. " +
                "NEVER OBSERVED RUNNING through this bridge - the single highest-value thing " +
                "to prove on the next live pass.",
            ResultDescription = "success, threw (if HotReloadDefs itself threw synchronously), ticksGame.")]
        public static async Task<object> HotReloadDefs(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                try { PlayDataLoader.HotReloadDefs(); }
                catch (Exception e) { return Fail("HotReloadDefs threw " + e.GetType().Name + ": " + e.Message); }

                return new
                {
                    success = true,
                    note = "Queued as a long event - completion is not guaranteed by the time this call returns. " +
                           "Verify with a read of something you just changed in XML, not this result alone.",
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  DebugSettings - the whole "Settings" debug-menu column in one tool
        // ================================================================

        [Tool(
            "jawa/debug_settings",
            Description =
                "Read or write any field on Verse.DebugSettings by name - the ~45 public " +
                "static bool flags behind the debug menu's whole 'Settings' column " +
                "(noAnimals, unlimitedPower, instantRecruit, pathThroughWalls, godMode, " +
                "fastResearch, fastLearning, fastEcology, fastCrafting, fastCaravans, " +
                "fastMapUnpollution, alwaysDoLovin, alwaysSocialFight, enableDamage, " +
                "enablePlayerDamage, enableRandomMentalStates, enableStoryteller, " +
                "enableRandomDiseases, and more - action='list' reports every field and its " +
                "current value). One generic reflective tool rather than 45 individual ones, " +
                "since every field is the same shape (public static bool) and self-documenting " +
                "by name. ⚠️ godMode overlaps core RimBridge's own rimworld/set_god_mode - " +
                "either works, they write the same field.",
            ResultDescription =
                "list: success, fields[] (name, value). set: success, field, valueBefore, valueAfter.")]
        public static async Task<object> DebugSettingsTool(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'list' (default) or 'set'.")]
            string action = "list",
            [ToolParameter(Description = "set: field name, e.g. 'noAnimals', 'fastCrafting'.")]
            string field = null,
            [ToolParameter(Description = "set: true or false.")]
            bool value = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var t = typeof(DebugSettings);
                var flags = BindingFlags.Public | BindingFlags.Static;

                string a = (action ?? "list").Trim().ToLowerInvariant();
                if (a == "list")
                {
                    var rows = t.GetFields(flags)
                        .Where(f => f.FieldType == typeof(bool))
                        .Select(f => new { name = f.Name, value = (bool)f.GetValue(null) })
                        .OrderBy(r => r.name)
                        .ToList();
                    return new { success = true, action = "list", count = rows.Count, fields = rows, ticksGame = TicksGameSafe() };
                }

                if (a == "set")
                {
                    if (string.IsNullOrWhiteSpace(field)) return Fail("Give 'field', e.g. 'noAnimals'.");
                    var fi = t.GetField(field.Trim(), flags);
                    if (fi == null || fi.FieldType != typeof(bool))
                        return Fail("No public static bool field '" + field + "' on DebugSettings.",
                            new { fields = t.GetFields(flags).Where(f => f.FieldType == typeof(bool)).Select(f => f.Name).OrderBy(n => n).ToList() });

                    bool before = (bool)fi.GetValue(null);
                    try { fi.SetValue(null, value); }
                    catch (Exception e) { return Fail("SetValue threw " + e.GetType().Name + ": " + e.Message); }

                    return new { success = true, field = fi.Name, valueBefore = before, valueAfter = (bool)fi.GetValue(null), ticksGame = TicksGameSafe() };
                }

                return Fail("action must be 'list' or 'set'.");
            }).ConfigureAwait(false);
        }
    }
}
