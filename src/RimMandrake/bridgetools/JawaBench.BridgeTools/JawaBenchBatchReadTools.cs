// BATCHREADS_BUILD_ROUND_TRIP_CUT (tickburst final.md L-d): a bridge round trip costs
// about 53 ms, and proofs read many cells, things, pawns and nets one call at a time.
// Each tool here is the batch twin of a single-call read, in the get_terrain_batch
// pattern: many targets in, one main-thread hop, one row per target out. Every row is
// built by the SAME helper the single-call tool uses (ThingListRow, PawnSnapshot,
// PowerNetBlock), so a batch read and a single read of the same
// target cannot disagree about its fields. A target the batch cannot read comes back as
// its own row with ok=false and the single tool's reason; it never drops out silently
// and never reads as zero. Fluid cells already had their batch read before this item
// (flowworks_excavation_rect in JawaBenchFlowWorksPulseTools.cs, rows with dEff/fEff,
// dl and isSink); the FlowWorks northstar extensions now read through it.
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
        private const int MaxBatchIds = 1024;

        private static List<string> SplitIdList(string ids)
        {
            var list = new List<string>();
            if (string.IsNullOrWhiteSpace(ids)) return list;
            foreach (var piece in ids.Split(new[] { ',', ';', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries))
            {
                var t = piece.Trim();
                if (t.Length > 0) list.Add(t);
            }
            return list;
        }

        // ================================================================
        //  things in many rects (batch twin of list_things)
        // ================================================================
        [Tool(
            "jawa/list_things_batch",
            Description =
                "List things in MANY rects in one call: the batch twin of list_things, one " +
                "main-thread hop instead of one round trip per rect (~53 ms each). rects: " +
                "'x,z,w,h' separated by ';' or newlines (w/h default 1). A rect may carry its " +
                "own defName filter as a prefix, 'DefA|DefB:x,z,w,h'; without one the " +
                "defName parameter applies. A thing is in a rect when its root Position is " +
                "(the same test list_things applies), so a multi-cell building belongs only " +
                "to the rect holding its root. Overlapping rects each report the thing. " +
                "Every row is the same row list_things returns for that thing.",
            ResultDescription =
                "success, rectCount, scanned (things examined once for all rects), " +
                "results[] in rect order: {rect, defNames, things[], countMatched, " +
                "countReturned, truncated, perDef}, ticksGame. A zero countMatched with " +
                "scanned>0 is a filter result, not an empty map.")]
        public static async Task<object> ListThingsBatch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Rects 'x,z,w,h' separated by ';'; optional 'DefA|DefB:' prefix per rect.")]
            string rects,
            [ToolParameter(Description = "Default defName filter (comma-separated) for rects with no prefix. " +
                "Omit for none.", DefaultValue = null)]
            string defName = null,
            [ToolParameter(Description = "Optional ThingRequestGroup name, as list_things. Invalid names are refused.",
                DefaultValue = null)]
            string group = null,
            [ToolParameter(Description = "Include pawns, as list_things.", DefaultValue = false)]
            bool includePawns = false,
            [ToolParameter(Description = "Cap on returned things PER RECT.", DefaultValue = 200)]
            int limit = 200)
        {
            if (string.IsNullOrWhiteSpace(rects))
                return Fail("rects is required, e.g. '10,20,5,5;30,20,1,1'.");
            List<ParsedOp> parsed;
            var errors = new List<string>();
            if (!TryParseOps(rects, "_", out parsed, errors) || errors.Count > 0)
                return Fail("Could not parse rects.", new { errors });
            if (parsed.Count > MaxOps)
                return Fail($"Too many rects: {parsed.Count} > {MaxOps}. Split the call.");

            var defaultWanted = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (var piece in SplitIdList(defName)) defaultWanted.Add(piece);
            var wantedPer = new List<HashSet<string>>();
            foreach (var op in parsed)
            {
                if (op.Terrain == "_") { wantedPer.Add(defaultWanted); continue; }
                var set = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                foreach (var piece in op.Terrain.Split('|'))
                    if (!string.IsNullOrWhiteSpace(piece)) set.Add(piece.Trim());
                wantedPer.Add(set);
            }

            ThingRequestGroup grp = ThingRequestGroup.Undefined;
            if (!string.IsNullOrWhiteSpace(group) && !Enum.TryParse(group.Trim(), true, out grp))
                return Fail($"No ThingRequestGroup named '{group}'.",
                    new { valid = Enum.GetNames(typeof(ThingRequestGroup)) });

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");
                var source = grp == ThingRequestGroup.Undefined
                    ? (IEnumerable<Thing>)map.listerThings.AllThings
                    : map.listerThings.ThingsInGroup(grp);

                int n = parsed.Count;
                var rows = new List<object>[n];
                var perDef = new Dictionary<string, int>[n];
                var matched = new int[n];
                var truncated = new int[n];
                for (int i = 0; i < n; i++) { rows[i] = new List<object>(); perDef[i] = new Dictionary<string, int>(); }
                int scanned = 0;

                foreach (var thing in source)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    if (thing?.def == null) continue;
                    scanned++;
                    if (!includePawns && thing is Pawn) continue;
                    var pos = thing.Spawned ? thing.Position : IntVec3.Invalid;
                    if (!pos.IsValid) continue;
                    for (int i = 0; i < n; i++)
                    {
                        var op = parsed[i];
                        if (pos.x < op.X || pos.z < op.Z || pos.x >= op.X + op.W || pos.z >= op.Z + op.H) continue;
                        if (wantedPer[i].Count > 0 && !wantedPer[i].Contains(thing.def.defName)) continue;
                        matched[i]++;
                        int c;
                        perDef[i].TryGetValue(thing.def.defName, out c);
                        perDef[i][thing.def.defName] = c + 1;
                        if (rows[i].Count >= limit) { truncated[i]++; continue; }
                        rows[i].Add(ThingListRow(thing, pos));
                    }
                }

                var results = new List<object>(n);
                for (int i = 0; i < n; i++)
                {
                    var op = parsed[i];
                    results.Add(new
                    {
                        rect = new { x = op.X, z = op.Z, w = op.W, h = op.H },
                        defNames = wantedPer[i].ToList(),
                        things = rows[i],
                        countMatched = matched[i],
                        countReturned = rows[i].Count,
                        truncated = truncated[i],
                        perDef = perDef[i]
                    });
                }
                return new { success = true, rectCount = n, scanned, results, ticksGame = TicksGameSafe() };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ================================================================
        //  many pawns (batch twin of pawn_get)
        // ================================================================
        [Tool(
            "jawa/get_pawns_batch",
            Description =
                "Deep read of MANY named pawns in one call: the batch twin of pawn_get, one " +
                "main-thread hop instead of one round trip per pawn. Each pawn is resolved " +
                "exactly as pawn_get resolves it (id, thingId with or without 'Thing_', or " +
                "name) and snapshotted by the same code, so each row's `pawn` equals " +
                "pawn_get's pawns[0] for that query. A pawn that cannot be found is its own " +
                "row with ok=false and pawn_get's reason, never dropped.",
            ResultDescription =
                "success, requested, found, missing, rows[] in query order: {query, ok, " +
                "pawn (the pawn_get snapshot) | error}, ticksGame.")]
        public static async Task<object> PawnGetBatch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn ids, thingIds or names, separated by ',' or ';'.")]
            string pawns)
        {
            var queries = SplitIdList(pawns);
            if (queries.Count == 0) return Fail("pawns is required, e.g. 'Human101,Human102'.");
            if (queries.Count > MaxBatchIds) return Fail($"Too many pawns: {queries.Count} > {MaxBatchIds}.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (Find.Maps == null || Find.Maps.Count == 0) return Fail("No map loaded.");
                var rows = new List<object>(queries.Count);
                int found = 0;
                foreach (var q in queries)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    string err;
                    var pw = FindPawn(q, out err);
                    if (pw == null) { rows.Add(new { query = q, ok = false, error = err }); continue; }
                    found++;
                    rows.Add(new { query = q, ok = true, pawn = PawnSnapshot(pw) });
                }
                return new
                {
                    success = true,
                    requested = queries.Count,
                    found,
                    missing = queries.Count - found,
                    rows,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ================================================================
        //  many power nets (batch twin of power_net, read only)
        // ================================================================
        [Tool(
            "jawa/get_power_nets_batch",
            Description =
                "READ the PowerNet of MANY buildings in one call: the batch twin of power_net " +
                "(read half only; it never forces PowerOn). Each row's `net` is built by the " +
                "same code as power_net's, and refusals carry power_net's reason: a thing " +
                "with no CompPower is a refused row (ok=false), never a net of zeros; an " +
                "unconnected CompPower is ok with connected=false. Buildings on the same " +
                "PowerNet share a netIndex, so one call also says which buildings are wired " +
                "together.",
            ResultDescription =
                "success, requested, ok, refused, netCount, rows[] in query order: {query, " +
                "ok, thing{id,defName}, connected, netIndex (-1 unconnected), net, " +
                "isPowerTrader, powerOn, energyOutputPerTick | error}, ticksGame.")]
        public static async Task<object> PowerNetBatch(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Thing ids of buildings carrying CompPower, separated by ',' or ';'.")]
            string things)
        {
            var queries = SplitIdList(things);
            if (queries.Count == 0) return Fail("things is required, e.g. 'Battery1234,SolarGenerator88'.");
            if (queries.Count > MaxBatchIds) return Fail($"Too many things: {queries.Count} > {MaxBatchIds}.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (Current.Game == null) return Fail("No game loaded.");
                var nets = new List<PowerNet>();
                var rows = new List<object>(queries.Count);
                int okCount = 0;
                foreach (var q in queries)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    string terr;
                    var t = SystemToolsFindThing(q, out terr);
                    if (t == null) { rows.Add(new { query = q, ok = false, error = terr ?? "No thing." }); continue; }
                    var twc = t as ThingWithComps;
                    if (twc == null)
                    {
                        rows.Add(new { query = q, ok = false, error = t.ThingID + " is not a ThingWithComps - it cannot carry CompPower." });
                        continue;
                    }
                    var cp = twc.GetComp<CompPower>();
                    if (cp == null)
                    {
                        rows.Add(new { query = q, ok = false, error = t.ThingID + " (" + (t.def != null ? t.def.defName : "?") + ") has no CompPower." });
                        continue;
                    }
                    var net = cp.PowerNet;
                    int netIndex = -1;
                    if (net != null)
                    {
                        netIndex = nets.IndexOf(net);
                        if (netIndex < 0) { nets.Add(net); netIndex = nets.Count - 1; }
                    }
                    var trader = cp as CompPowerTrader;
                    okCount++;
                    rows.Add(new
                    {
                        query = q,
                        ok = true,
                        thing = new { id = t.ThingID, defName = t.def != null ? t.def.defName : null },
                        connected = net != null,
                        netIndex,
                        net = PowerNetBlock(net),
                        isPowerTrader = trader != null,
                        powerOn = trader != null ? trader.PowerOn : (bool?)null,
                        energyOutputPerTick = trader != null ? (float?)trader.EnergyOutputPerTick : null
                    });
                }
                return new
                {
                    success = true,
                    requested = queries.Count,
                    ok = okCount,
                    refused = queries.Count - okCount,
                    netCount = nets.Count,
                    rows,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }
    }
}
