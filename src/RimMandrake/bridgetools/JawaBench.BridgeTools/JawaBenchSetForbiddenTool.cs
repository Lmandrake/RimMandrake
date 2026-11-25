using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;

namespace JawaBench.BridgeTools
{
    // jawa/set_forbidden -- set every forbiddable thing in one rect forbidden or allowed (CompForbiddable.Forbidden), read back.
    // Why (RIMMANDRAKE_BUILD_COLONY_STATION_HOLDS_BYSTANDERS_BY_AREA): on a colony stage the scene's things sit among a real
    // colony's haulers and cleaners; a forbidden thing is not hauled, eaten or reserved by a bystander. Things with no
    // CompForbiddable (a wall, a plant) are counted as skipped, never as set.
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/set_forbidden",
            Description =
                "Set CompForbiddable.Forbidden on every thing in one rect 'x,z,w,h' of the current map, then read each one back. " +
                "Things without the comp are skipped and counted.",
            ResultDescription = "success, changed (things whose read-back equals the wanted value), failedVerify, skipped, rect.")]
        public static async Task<object> SetForbidden(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "One rect 'x,z,w,h' in map cells.")] string rect = null,
            [ToolParameter(Description = "true forbids, false allows.", DefaultValue = true)] bool forbidden = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");
                var errors = new List<string>();
                List<ParsedOp> parsed;
                if (string.IsNullOrWhiteSpace(rect) || !TryParseOps(rect, "_", out parsed, errors) || parsed.Count != 1)
                    return Fail("rect must be a single 'x,z,w,h'.", new { errors });
                var r = parsed[0];
                var things = new HashSet<Thing>();
                for (var x = r.X; x < r.X + r.W; x++)
                    for (var z = r.Z; z < r.Z + r.H; z++)
                    {
                        var c = new IntVec3(x, 0, z);
                        if (!c.InBounds(map)) continue;
                        foreach (var t in map.thingGrid.ThingsListAtFast(c)) things.Add(t);
                    }
                int changed = 0, failed = 0, skipped = 0;
                foreach (var t in things.ToList())
                {
                    var comp = (t as ThingWithComps)?.GetComp<CompForbiddable>();
                    if (comp == null) { skipped++; continue; }
                    comp.Forbidden = forbidden;
                    if (comp.Forbidden == forbidden) changed++; else failed++;
                }
                return new { success = true, changed, failedVerify = failed, skipped, rect };
            }, cancellationToken).ConfigureAwait(false);
        }
    }
}
