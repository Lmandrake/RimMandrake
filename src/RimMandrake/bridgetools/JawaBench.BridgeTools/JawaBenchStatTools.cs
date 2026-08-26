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

        // ================================================================
        //  jawa/thing_stats
        // ================================================================
        //
        // The sibling of jawa/pawn_stats, for the OTHER half of the same gap:
        // pawn_stats reads a stat off a live PAWN, and nothing at all could read
        // one off a live ITEM. jawa/get_defs returns def.statBases (the number
        // before any StatPart runs), jawa/pawn_get names the equipped weapon
        // without saying what it does, and jawa/inspect_string returns sentences.
        //
        // WHY THE DEF-LEVEL NUMBER IS NOT THE ANSWER, in one concrete case:
        // Lightsaber.dll (workshop 3466124712) carries AdjustedArmorPenetration
        // and StatPart_EquippedStatOffsetIncrease, so ArmorPenetration is adjusted
        // at runtime and the adjustment is tied to EQUIPPED context. Every AP
        // number in this project's record was read off a ground-spawned weapon and
        // is therefore unproven for a held one. With ~578 mods, any modded stat
        // with a StatPart reads differently on an instance than on its def.
        //
        // 🔑 THIS IS WHY defBase IS RETURNED BESIDE value, ALWAYS. A single number
        // cannot show that a StatPart moved it, and showing that is the whole
        // point of the tool: value == defBase is itself the finding "nothing
        // adjusted this", and it must be readable without a second call.
        [Tool(
            "jawa/thing_stats",
            Description =
                "Read StatDef values OFF A LIVE ITEM - a weapon on the ground, the same weapon in a " +
                "pawn's hands, a piece of apparel being worn - which nothing else on this bridge can do. " +
                "jawa/get_defs returns def.statBases, the value BEFORE any StatPart runs; jawa/pawn_get " +
                "names the equipped weapon but not what it does; jawa/pawn_stats reads the PAWN, not the " +
                "thing it is holding. " +
                "🔑 Every row returns 'value' (Thing.GetStatValue - the instance, the same call the " +
                "game's own info card makes) BESIDE 'defBase' (ThingDef.GetStatValueAbstract with this " +
                "thing's stuff - what a def-only reader would have told you). 'movedFromDef' says " +
                "whether anything adjusted it. That comparison is the entire reason this tool exists: " +
                "a modded stat with a StatPart reads differently held than lying in the dirt. " +
                "Address the thing by id ('thing', comma-separated for several - so the ground copy and " +
                "the equipped copy come back in ONE answer, already side by side), or by 'pawn' plus " +
                "'slot' (equipment | apparel | inventory) to reach what a pawn is carrying. " +
                "⚠ An unknown StatDef is REFUSED BY NAME with suggestions, never reported as 0 - a stat " +
                "that does not exist and a stat that evaluates to zero must not look alike. " +
                "⚠ An unresolved thing id is likewise refused by name, and if the id was really a " +
                "defName the refusal lists the live ids of things with that def.",
            ResultDescription =
                "success, count, things[]: id, defName, label, stuff, quality, holder {pawn, id, slot} " +
                "or location {x,z,map} for a ground item, and stats[]: defName, label, value, " +
                "valueString, defBase, delta, movedFromDef, statParts[] (the StatPart types that can " +
                "move it), category, shownByGame. Plus refused[] for any stat or thing that did not " +
                "resolve, each naming what was asked for.")]
        public static async Task<object> ThingStats(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Thing id, or several comma-separated. Accepts the bare form 'Bow12345' and the prefixed 'Thing_Bow12345' alike. Searches every map, plus every pawn's equipment, apparel and inventory - so an equipped weapon is reachable by id.")]
            string thing = null,
            [ToolParameter(Description = "Instead of ids: a pawn, as accepted by jawa/pawn_stats. Returns the things in that pawn's slots.")]
            string pawn = null,
            [ToolParameter(Description = "With 'pawn': equipment | apparel | inventory, comma-separated. Default 'equipment,apparel'.")]
            string slot = null,
            [ToolParameter(Description = "With 'pawn': keep only items whose defName or label contains this (case-insensitive).")]
            string defFilter = null,
            [ToolParameter(Description = "Comma-separated StatDef defNames, e.g. 'ArmorPenetrationSharp,MeleeWeapon_AverageDPS'. Empty returns every stat the game itself would show for the item.")]
            string stats = null,
            [ToolParameter(Description = "With an empty 'stats', include stats the game would NOT show (alwaysHide, or ShouldShowFor false).")]
            bool includeHidden = false,
            [ToolParameter(Description = "Cap on stat rows per thing when 'stats' is empty. Default 40. Named stats are never capped.")]
            int limit = 40)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                var targets = new List<Thing>();
                var refused = new List<object>();

                // ---- resolve the things -------------------------------------
                if (!string.IsNullOrWhiteSpace(pawn))
                {
                    string perr;
                    var p = FindPawn(pawn, out perr);
                    if (p == null) return Fail(perr ?? "No pawn.");

                    var want = string.IsNullOrWhiteSpace(slot) ? "equipment,apparel" : slot.ToLowerInvariant();
                    Func<Thing, bool> keep = t =>
                        string.IsNullOrWhiteSpace(defFilter)
                        || (t.def != null && t.def.defName.IndexOf(defFilter, StringComparison.OrdinalIgnoreCase) >= 0)
                        || (t.Label != null && t.Label.IndexOf(defFilter, StringComparison.OrdinalIgnoreCase) >= 0);

                    if (want.Contains("equipment") && p.equipment != null)
                        foreach (var t in p.equipment.AllEquipmentListForReading) if (keep(t)) targets.Add(t);
                    if (want.Contains("apparel") && p.apparel != null)
                        foreach (var t in p.apparel.WornApparel) if (keep(t)) targets.Add(t);
                    if (want.Contains("inventory") && p.inventory != null && p.inventory.innerContainer != null)
                        foreach (var t in p.inventory.innerContainer) if (keep(t)) targets.Add(t);

                    if (targets.Count == 0)
                        return Fail(string.Format(
                            "{0} carries nothing matching slot '{1}'{2}. That is an answer, not an error - "
                            + "but it is reported as a failure because a caller asking what a pawn's gear does "
                            + "must not read an empty list as 'it does nothing'.",
                            p.LabelShortCap, want,
                            string.IsNullOrWhiteSpace(defFilter) ? "" : " and defFilter '" + defFilter + "'"));
                }
                else if (!string.IsNullOrWhiteSpace(thing))
                {
                    // One pass over the live things, building both an id index and a
                    // defName index - the second one exists so an id that was really a
                    // defName gets a refusal that NAMES the candidates instead of a null.
                    var byId = new Dictionary<string, Thing>();
                    var byDef = new Dictionary<string, List<string>>(StringComparer.OrdinalIgnoreCase);
                    Action<Thing> index = t =>
                    {
                        if (t == null || t.def == null) return;
                        if (!byId.ContainsKey(t.ThingID)) byId[t.ThingID] = t;
                        List<string> ids;
                        if (!byDef.TryGetValue(t.def.defName, out ids)) { ids = new List<string>(); byDef[t.def.defName] = ids; }
                        if (ids.Count < 10) ids.Add(t.ThingID);
                    };
                    foreach (var m in Find.Maps)
                    {
                        cancellationToken.ThrowIfCancellationRequested();
                        foreach (var t in m.listerThings.AllThings) index(t);
                        foreach (var p in m.mapPawns.AllPawnsSpawned)
                        {
                            if (p.equipment != null) foreach (var t in p.equipment.AllEquipmentListForReading) index(t);
                            if (p.apparel != null) foreach (var t in p.apparel.WornApparel) index(t);
                            if (p.inventory != null && p.inventory.innerContainer != null)
                                foreach (var t in p.inventory.innerContainer) index(t);
                        }
                    }

                    foreach (var raw in thing.Split(new[] { ',', ';', '\n' }, StringSplitOptions.RemoveEmptyEntries))
                    {
                        var tok = raw.Trim();
                        if (tok.Length == 0) continue;
                        var bare = tok.StartsWith("Thing_", StringComparison.OrdinalIgnoreCase) ? tok.Substring(6) : tok;
                        Thing found;
                        if (byId.TryGetValue(tok, out found) || byId.TryGetValue(bare, out found)) { targets.Add(found); continue; }
                        List<string> cands;
                        if (byDef.TryGetValue(bare, out cands))
                            refused.Add(new
                            {
                                thing = tok,
                                reason = "ThatIsADefNameNotAnId",
                                message = "'" + bare + "' is a defName. Ask for one of these live ids.",
                                liveIds = cands
                            });
                        else
                            refused.Add(new { thing = tok, reason = "NoSuchThingId", message = "No live thing with id '" + bare + "' on any loaded map, in any pawn's equipment, apparel or inventory." });
                    }

                    if (targets.Count == 0)
                        return Fail("No thing id resolved. Nothing was measured.", new { refused });
                }
                else
                {
                    return Fail("Give 'thing' (one or more ids) or 'pawn' (with an optional 'slot').");
                }

                // ---- read the stats -----------------------------------------
                var rows = new List<object>();
                int statTotal = 0;
                foreach (var t in targets)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    var req = StatRequest.For(t);
                    var statRows = new List<object>();

                    Func<StatDef, bool> shown = sd =>
                    {
                        if (sd.alwaysHide) return false;
                        try { return sd.Worker != null && sd.Worker.ShouldShowFor(req); }
                        catch { return false; }
                    };

                    Action<StatDef> add = sd =>
                    {
                        float v;
                        try { v = t.GetStatValue(sd); }
                        catch (Exception ex)
                        {
                            refused.Add(new { thing = t.ThingID, stat = sd.defName, reason = ex.GetType().Name, message = ex.Message });
                            return;
                        }
                        // The def-level number, WITH this thing's stuff - i.e. exactly what a
                        // def-only reader would have reported for this item. Allowed to fail
                        // independently; a base we could not compute must read null, never 0,
                        // or 'nothing moved it' becomes indistinguishable from 'we did not look'.
                        float? baseVal = null;
                        try { baseVal = t.def.GetStatValueAbstract(sd, t.Stuff); }
                        catch { baseVal = null; }
                        string vs;
                        try { vs = sd.Worker != null ? sd.Worker.ValueToString(v, true, sd.toStringNumberSense) : v.ToString(); }
                        catch { vs = null; }
                        List<string> parts = null;
                        try
                        {
                            if (sd.parts != null && sd.parts.Count > 0)
                                parts = sd.parts.Select(pt => pt.GetType().Name).ToList();
                        }
                        catch { parts = null; }

                        statRows.Add(new
                        {
                            defName = sd.defName,
                            label = sd.label,
                            value = v,
                            valueString = vs,
                            defBase = baseVal,
                            delta = baseVal.HasValue ? (float?)(v - baseVal.Value) : null,
                            movedFromDef = baseVal.HasValue ? (bool?)(Math.Abs(v - baseVal.Value) > 0.0001f) : null,
                            statParts = parts,
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
                                refused.Add(new { thing = t.ThingID, stat = nm, reason = "NoSuchStatDef", suggestions = DefSuggestions<StatDef>(nm) });
                                continue;
                            }
                            add(sd);
                        }
                    }
                    else
                    {
                        foreach (var sd in DefDatabase<StatDef>.AllDefsListForReading)
                        {
                            cancellationToken.ThrowIfCancellationRequested();
                            if (!includeHidden && !shown(sd)) continue;
                            if (statRows.Count >= limit) break;
                            add(sd);
                        }
                    }

                    // where is it, and who is holding it
                    Pawn holderPawn = null; string holderSlot = null;
                    try
                    {
                        var ph = t.ParentHolder;
                        var eq = ph as Pawn_EquipmentTracker;
                        if (eq != null) { holderPawn = eq.pawn; holderSlot = "equipment"; }
                        else
                        {
                            var ap = ph as Pawn_ApparelTracker;
                            if (ap != null) { holderPawn = ap.pawn; holderSlot = "apparel"; }
                            else
                            {
                                var inv = ph as Pawn_InventoryTracker;
                                if (inv != null) { holderPawn = inv.pawn; holderSlot = "inventory"; }
                            }
                        }
                    }
                    catch { }

                    statTotal += statRows.Count;

                    QualityCategory q;
                    string quality = t.TryGetQuality(out q) ? q.ToString() : null;

                    rows.Add(new
                    {
                        id = t.ThingID,
                        defName = t.def != null ? t.def.defName : null,
                        label = t.LabelCap.ToString(),
                        stuff = t.Stuff != null ? t.Stuff.defName : null,
                        quality,
                        stackCount = t.stackCount,
                        holder = holderPawn != null
                            ? (object)new
                            {
                                pawn = holderPawn.LabelShortCap.ToString(),
                                id = holderPawn.ThingID,
                                kindDef = holderPawn.kindDef != null ? holderPawn.kindDef.defName : null,
                                slot = holderSlot
                            }
                            : null,
                        location = t.Spawned ? (object)new { x = t.Position.x, z = t.Position.z, map = t.Map != null ? t.Map.Index : -1 } : null,
                        onGround = t.Spawned && holderPawn == null,
                        count = statRows.Count,
                        stats = statRows
                    });
                }

                // 🔴 A named stat that resolved nowhere is a FAILED call, not a footnote -
                // the same rule jawa/pawn_stats enforces, and the one
                // BRIDGE_ARG_SHAPES_INCONSISTENT_1 exists because four bridge tools break:
                // an empty collection returned with success:true is indistinguishable from
                // a true empty result, and that is how an unrun check becomes a pass.
                if (!string.IsNullOrWhiteSpace(stats) && statTotal == 0)
                    return Fail("No named stat resolved on any thing. Nothing was measured.", new { refused });

                return new
                {
                    success = true,
                    message = string.Format("{0} stat(s) read off {1} thing(s){2}. value is the INSTANCE; defBase is what the def alone would have said.",
                        statTotal, rows.Count, refused.Count > 0 ? ", " + refused.Count + " REFUSED" : ""),
                    count = rows.Count,
                    things = rows,
                    refused,
                    readTheInstance = true,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
