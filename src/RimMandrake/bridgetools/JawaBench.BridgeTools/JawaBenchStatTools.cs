// JawaBenchStatTools.cs - reading a StatDef off a live pawn, and reading a Room.
//
// WHY THIS FILE EXISTS
// ====================
// Two whole classes of question had NO instrument on this bridge, and both were
// found the same way: an item asked for a number, and every one of the 163 tools
// turned out to answer something adjacent to it.
//
//   1. A PAWN'S STAT.  LIVE_HALF_OF_LOAD_1 rows T1/T2/N1/N2 turn entirely on
//      ComfyTemperatureMin/Max on a live pawn. jawa/pawn_get returns identity,
//      apparel, equipment, hediffs, needs, skills, traits and xenotype - and no
//      stats. rimworld/get_map_target_info returns the same shape.
//      jawa/inspect_string is the inspect pane, which does not carry it. The UI
//      route is shut too: rimworld/select_pawn is COLONIST-ONLY and refused a
//      non-player Jawa, and Dialog_InfoCard has no public parameterless
//      constructor so open_window_by_type cannot build one.
//
//   2. A ROOM.  TEMPLATE_ENGINE_ACCEPTANCE_1 criteria 1 and 2 need Room.Role
//      ("the game agrees it is a house") and a room's temperature ("the shell
//      holds"). rimworld/get_cell_info returns terrain, roof, fog, walkability,
//      zone, areas, designations and things - no room object at all. A regex for
//      `room` over every live tool name returns nothing.
//
// Those four rows were recorded UNMEASURED on 2026-08-26 rather than rounded to
// a pass, which is the right answer and a useless one. This file is the fix.
//
// THE ONE RULE THAT SHAPES EVERY LINE HERE
// ========================================
// READ THE INSTANCE, NEVER THE DEF. def.statBases is the pre-generation number;
// genes, hediffs, apparel, traits and the xenotype all move it afterwards, and
// the whole reason those items exist is that the def-level value was already
// known and already doubted. Thing.GetStatValue is the only honest source, and
// it is what the game's own info card calls.
//
// NOT A CACHE TRAP - and this is worth saying out loud, because the sibling file
// JawaBenchCacheTools.cs exists entirely because Tile's caches are never
// invalidated. Room is DIFFERENT. Room.Role and Room.GetStat check
// statsAndRoleDirty and call UpdateRoomStatsAndRole() when it is set, and the
// game SETS that flag whenever the room changes (Verse/Room.cs). So reading
// through the property is the correct, current value - it recomputes rather than
// serving a stale one. Do NOT "improve" this by reaching for the private fields
// with reflection the way the Tile audit has to; here that would read a value
// the engine has already marked dirty.
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

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ================================================================
        //  jawa/pawn_stats
        // ================================================================
        [Tool(
            "jawa/pawn_stats",
            Description =
                "Read StatDef values OFF A LIVE PAWN, which nothing else on this bridge can do. " +
                "jawa/pawn_get returns identity, apparel, equipment, hediffs, needs, skills, traits " +
                "and xenotype and NO STATS; rimworld/select_pawn is colonist-only and Dialog_InfoCard " +
                "cannot be opened by type, so the UI route is shut as well. " +
                "🔑 THIS READS THE INSTANCE, via Thing.GetStatValue - the same call the game's own " +
                "info card makes - and NEVER def.statBases. That distinction is the entire point: genes, " +
                "hediffs, apparel, traits and the xenotype all move a stat AFTER generation, so a " +
                "def-level read confirms exactly the thing that is in doubt. " +
                "Name stats with 'stats'; leave it empty to get the ones the game itself would show for " +
                "this pawn (StatWorker.ShouldShowFor). " +
                "⚠ A stat name that does not resolve is REFUSED with suggestions, not skipped - a " +
                "silently skipped stat reads as 'the pawn does not have it', which is a lie. " +
                "Comfortable temperature is TWO stats and they are spelled ComfyTemperatureMin and " +
                "ComfyTemperatureMax (NOT Comfortable...), both present in the def dump.",
            ResultDescription =
                "success, pawn (id, name, kindDef, xenotype), count, and stats[]: defName, label, " +
                "value (float, post-processed), valueString (the game's own formatting, so a " +
                "temperature reads '-40 °C'), category, and shownByGame. Plus refused[] naming any " +
                "stat that did not resolve, with suggestions.")]
        public static async Task<object> PawnStats(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name, as returned by jawa/list_pawns.")]
            string pawn = null,
            [ToolParameter(Description = "Comma-separated StatDef defNames, e.g. 'ComfyTemperatureMin,ComfyTemperatureMax,MoveSpeed'. Empty returns every stat the game itself would show for this pawn.")]
            string stats = null,
            [ToolParameter(Description = "With an empty 'stats', include stats the game would NOT show (alwaysHide, or ShouldShowFor false). Off by default - the shown set is what a player can see and is what a criterion normally means.")]
            bool includeHidden = false,
            [ToolParameter(Description = "Cap on returned rows when 'stats' is empty. Default 60. Named stats are never capped.")]
            int limit = 60)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string err;
                var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err ?? "No pawn.");

                var rows = new List<object>();
                var refused = new List<object>();
                var req = StatRequest.For(p);

                Func<StatDef, bool> shown = sd =>
                {
                    if (sd.alwaysHide) return false;
                    try { return sd.Worker != null && sd.Worker.ShouldShowFor(req); }
                    catch { return false; }
                };

                Action<StatDef> add = sd =>
                {
                    float v;
                    string vs;
                    try { v = p.GetStatValue(sd); }
                    catch (Exception ex)
                    {
                        refused.Add(new { stat = sd.defName, reason = ex.GetType().Name, message = ex.Message });
                        return;
                    }
                    // ValueToString is what the player sees. It is allowed to throw on an
                    // exotic worker, and a stat we could not FORMAT is still a stat we
                    // measured - so the number survives even when the string does not.
                    try { vs = sd.Worker != null ? sd.Worker.ValueToString(v, true, sd.toStringNumberSense) : v.ToString(); }
                    catch { vs = null; }
                    rows.Add(new
                    {
                        defName = sd.defName,
                        label = sd.label,
                        value = v,
                        valueString = vs,
                        category = sd.category != null ? sd.category.defName : null,
                        shownByGame = shown(sd)
                    });
                };

                if (!string.IsNullOrWhiteSpace(stats))
                {
                    foreach (var raw in stats.Split(new[] { ',', ';', '\n' }, StringSplitOptions.RemoveEmptyEntries))
                    {
                        cancellationToken.ThrowIfCancellationRequested();
                        var nm = raw.Trim();
                        if (nm.Length == 0) continue;
                        var sd = DefDatabase<StatDef>.GetNamedSilentFail(nm);
                        if (sd == null)
                        {
                            refused.Add(new
                            {
                                stat = nm,
                                reason = "NoSuchStatDef",
                                suggestions = DefSuggestions<StatDef>(nm)
                            });
                            continue;
                        }
                        add(sd);
                    }
                    // 🔴 A named stat that did not resolve is a FAILED call, not a footnote.
                    // The caller asked a question about that stat and got no answer; letting
                    // success:true stand is how an unrun check becomes a pass.
                    if (refused.Count > 0 && rows.Count == 0)
                        return Fail("No named stat resolved. Nothing was measured.", new { refused });
                }
                else
                {
                    var all = DefDatabase<StatDef>.AllDefsListForReading;
                    foreach (var sd in all)
                    {
                        cancellationToken.ThrowIfCancellationRequested();
                        if (!includeHidden && !shown(sd)) continue;
                        if (rows.Count >= limit) break;
                        add(sd);
                    }
                }

                return new
                {
                    success = true,
                    message = string.Format("{0} stat(s) read off {1} ({2}){3}.",
                        rows.Count, p.LabelShortCap, p.kindDef != null ? p.kindDef.defName : "?",
                        refused.Count > 0 ? ", " + refused.Count + " REFUSED" : ""),
                    pawn = new
                    {
                        id = p.ThingID,
                        name = p.Name != null ? p.Name.ToStringShort : p.LabelShortCap,
                        kindDef = p.kindDef != null ? p.kindDef.defName : null,
                        xenotype = p.genes != null && p.genes.Xenotype != null ? p.genes.Xenotype.defName : null,
                        faction = p.Faction != null ? p.Faction.def.defName : null
                    },
                    count = rows.Count,
                    stats = rows,
                    refused,
                    readTheInstance = true,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/room_get
        // ================================================================
        [Tool(
            "jawa/room_get",
            Description =
                "Read the ROOM at a cell, or every distinct room touching a rect. Nothing else on " +
                "this bridge can see a Room at all - rimworld/get_cell_info returns terrain, roof, " +
                "fog, walkability, zone, areas, designations and things and no room object. " +
                "Answers the two questions a built structure is judged on: does the GAME agree it is " +
                "a bedroom/dining room/storeroom (Role), and does the shell hold temperature. " +
                "🔑 NOT A CACHE TRAP, unlike the Tile caches jawa/world_cache_audit exists for: " +
                "Room.Role and Room.GetStat check statsAndRoleDirty and RECOMPUTE when the game has " +
                "marked the room changed, so the property is the current value, not a stale one. Do " +
                "not reach for the private fields here. " +
                "⚠ A cell outside a room, or in the great outdoors, returns a row with " +
                "isOutdoors true rather than an error - 'there is no room here' is an answer.",
            ResultDescription =
                "success, roomsFound, and rooms[]: id, role, roleLabel, cellCount, temperature, " +
                "openRoofCount, properRoom, psychologicallyOutdoors, isOutdoors, sampleCell, and " +
                "stats{Impressiveness, Beauty, Space, Cleanliness, Wealth} read through Room.GetStat.")]
        public static async Task<object> RoomGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Cell X. Use with z for a single cell.")]
            int x = -1,
            [ToolParameter(Description = "Cell Z.")]
            int z = -1,
            [ToolParameter(Description = "Rect 'x,z,w,h' instead of a single cell. Every DISTINCT room touching it is reported once, so a whole building is one call.")]
            string rect = null,
            [ToolParameter(Description = "Include rooms that are psychologically outdoors. Off by default - a 250x250 map is mostly one huge outdoor room and it drowns the answer.")]
            bool includeOutdoors = false,
            [ToolParameter(Description = "Cap on distinct rooms returned. Default 40.")]
            int limit = 40)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                var cells = new List<IntVec3>();
                var size = map.Size;

                if (!string.IsNullOrWhiteSpace(rect))
                {
                    var parts = rect.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries);
                    int rx, rz, rw, rh;
                    if (parts.Length != 4
                        || !int.TryParse(parts[0].Trim(), out rx) || !int.TryParse(parts[1].Trim(), out rz)
                        || !int.TryParse(parts[2].Trim(), out rw) || !int.TryParse(parts[3].Trim(), out rh))
                        return Fail("rect must be 'x,z,w,h', e.g. '170,170,18,10'.");
                    if (rw <= 0 || rh <= 0) return Fail("rect width and height must be positive.");
                    if ((long)rw * rh > 4096L)
                        return Fail("rect covers " + ((long)rw * rh) + " cells; the cap is 4096. "
                                    + "Rooms are found by touching cells, so a smaller rect that still "
                                    + "touches every room gives the identical answer.");
                    for (int cx = rx; cx < rx + rw; cx++)
                        for (int cz = rz; cz < rz + rh; cz++)
                        {
                            if (cx < 0 || cz < 0 || cx >= size.x || cz >= size.z) continue;
                            cells.Add(new IntVec3(cx, 0, cz));
                        }
                    if (cells.Count == 0) return Fail("The whole rect is outside the map.");
                }
                else
                {
                    if (x < 0 || z < 0) return Fail("Give x and z, or rect.");
                    if (x >= size.x || z >= size.z) return Fail("Cell is outside the map.");
                    cells.Add(new IntVec3(x, 0, z));
                }

                var seen = new HashSet<int>();
                var rows = new List<object>();
                int outdoorsSkipped = 0;

                foreach (var cell in cells)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    if (rows.Count >= limit) break;
                    Room room = cell.GetRoom(map);
                    if (room == null) continue;
                    if (!seen.Add(room.ID)) continue;

                    bool outdoors;
                    try { outdoors = room.PsychologicallyOutdoors; } catch { outdoors = false; }
                    if (outdoors && !includeOutdoors) { outdoorsSkipped++; continue; }

                    Func<RoomStatDef, float?> stat = sd =>
                    {
                        if (sd == null) return null;
                        try { return room.GetStat(sd); } catch { return null; }
                    };

                    rows.Add(new
                    {
                        id = room.ID,
                        role = room.Role != null ? room.Role.defName : null,
                        roleLabel = room.Role != null ? room.Role.label : null,
                        cellCount = room.CellCount,
                        temperature = room.Temperature,
                        openRoofCount = room.OpenRoofCount,
                        properRoom = room.ProperRoom,
                        psychologicallyOutdoors = outdoors,
                        isOutdoors = outdoors,
                        usesOutdoorTemperature = room.UsesOutdoorTemperature,
                        sampleCell = new { x = cell.x, z = cell.z },
                        stats = new
                        {
                            Impressiveness = stat(RoomStatDefOf.Impressiveness),
                            Beauty = stat(RoomStatDefOf.Beauty),
                            Space = stat(RoomStatDefOf.Space),
                            Cleanliness = stat(RoomStatDefOf.Cleanliness),
                            Wealth = stat(RoomStatDefOf.Wealth)
                        }
                    });
                }

                return new
                {
                    success = true,
                    message = string.Format(
                        "{0} distinct room(s) over {1} cell(s){2}.",
                        rows.Count, cells.Count,
                        outdoorsSkipped > 0
                            ? ", " + outdoorsSkipped + " outdoor room(s) skipped - pass includeOutdoors to see them"
                            : ""),
                    cellsProbed = cells.Count,
                    roomsFound = rows.Count,
                    outdoorsSkipped,
                    rooms = rows,
                    recomputedNotCached = true,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
