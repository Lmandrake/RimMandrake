using System.Collections;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    // jawa/heat_events -- the rows the Beskar Armorer mod scribes to its RM_HeatEvents game component, for the GM blackboard.
    // Reflection: a mod this assembly must load without (design/RimMandrake/beskar_armorer_quest_design_2026-10-09.md section 6).
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/heat_events",
            Description = "Read the heat events recorded in game by RM_HeatEvents (mandrake.rut.beskararmorer), oldest first. Read-only.",
            ResultDescription = "success, modLoaded, events[{tick,faction,amount,source}]; modLoaded false means no such component, not zero heat.")]
        public static async Task<object> HeatEvents(IRimBridgeContext ctx, CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (Current.Game == null) return new { success = false, message = "No game is loaded." };
                System.Type t = AccessTools.TypeByName("RimMandrake.Utinni.BeskarArmorer.RM_HeatEvents");
                GameComponent comp = t == null ? null : Current.Game.components.Find(c => t.IsInstanceOfType(c));
                var rows = new List<object>();
                if (comp != null)
                    foreach (object e in (IEnumerable)AccessTools.Field(t, "events").GetValue(comp))
                    {
                        Traverse r = Traverse.Create(e);
                        rows.Add(new { tick = r.Field<int>("tick").Value, faction = r.Field<string>("faction").Value, amount = r.Field<int>("amount").Value, source = r.Field<string>("source").Value });
                    }
                return new { success = true, modLoaded = comp != null, events = rows };
            }, cancellationToken);
        }
    }
}
