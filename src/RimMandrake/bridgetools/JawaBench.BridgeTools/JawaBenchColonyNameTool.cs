using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace JawaBench.BridgeTools
{
    // jawa/name_colony -- name the player faction and every player settlement WITHOUT the dialogs.
    // Why: Faction.FactionTick raises Dialog_NamePlayerFactionAndSettlement every 1000 ticks (TicksGame % 1000 == 200)
    // while !Faction.OfPlayer.HasName / !Settlement.namedByPlayer (read from 1.6 source, Faction.cs +
    // NamePlayerFactionAndSettlementUtility.cs). Setting Faction.Name (public setter) and Settlement.Name +
    // namedByPlayer (public fields, both scribed) is exactly what the dialog's OK does, so the dialog never
    // returns. Ungated like jawa/world_landmark_rename: a name write, not world permission.
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/name_colony",
            Description =
                "Name the player faction and all player settlements directly (what the naming dialogs' OK does), " +
                "so Dialog_NamePlayerFactionAndSettlement / Dialog_NamePlayerSettlement are never raised again. " +
                "Idempotent. Any naming dialog already open is closed with jawa/window_list_close.",
            ResultDescription = "success, factionName, settlements[{tile,name,namedByPlayer}].")]
        public static async Task<object> NameColony(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Faction name. Default 'Northstar Test Colony'.")] string factionName = null,
            [ToolParameter(Description = "Settlement name. Default 'Northstar Base'.")] string settlementName = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (Find.World == null || Find.FactionManager == null)
                    return new { success = false, message = "No game is loaded." };
                var f = Faction.OfPlayer;
                f.Name = string.IsNullOrWhiteSpace(factionName) ? "Northstar Test Colony" : factionName.Trim();
                var sName = string.IsNullOrWhiteSpace(settlementName) ? "Northstar Base" : settlementName.Trim();
                var rows = Find.WorldObjects.Settlements.Where(s => s.Faction == f).ToList();
                foreach (var s in rows) { s.Name = sName; s.namedByPlayer = true; }
                return new
                {
                    success = true,
                    factionName = f.Name,
                    settlements = rows.Select(s => new { tile = (int)s.Tile, name = s.Name, namedByPlayer = s.namedByPlayer }).ToList(),
                };
            }, cancellationToken).ConfigureAwait(false);
        }
    }
}
