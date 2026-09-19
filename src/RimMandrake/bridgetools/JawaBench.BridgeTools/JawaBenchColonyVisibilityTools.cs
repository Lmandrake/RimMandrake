// JawaBenchColonyVisibilityTools.cs - read RimMandrake.Visibility's GameComponent, for
// COLONY_VISIBILITY_BUILD_1's tile-memory round trip live-proof.
//
// COUPLING: strictly by reflection, same pattern as jawa/canal_cell_report and
// jawa/flowworks_excavation_report - the companion must load and register on a mod
// list WITHOUT mandrake.rm.visibility, so no hard assembly reference.
//
// Every field/property name below is READ off GameComponent_ColonyVisibility.cs
// (src/RimMandrake/Visibility/Source/), not guessed: shipVisibility (public field),
// Band (public property), ShkaarEscalationMultiplier (public field), tileMemory
// (public field, Dictionary<PlanetTile, TileVisibilityMemory>). TileVisibilityMemory
// is a public class with public fields visibilityAtDeparture/departedTick.
// PlanetTile itself is a real engine type this assembly already references
// (JawaBenchGravshipTools.cs uses it directly), so only the two RimMandrake.Visibility
// types need reflection - the dictionary key comes back as a real PlanetTile with no
// cast-through-object games needed for ITS fields.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld.Planet;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private const string ColonyVisibilityTypeName = "RimMandrake.Visibility.GameComponent_ColonyVisibility";

        private static object ResolveColonyVisibilityComponent(out Type type, out string error)
        {
            error = null;
            type = GenTypes.GetTypeInAnyAssembly(ColonyVisibilityTypeName);
            if (type == null)
            {
                error = "GameComponent_ColonyVisibility type not resolvable - mandrake.rm.visibility is not loaded.";
                return null;
            }
            if (Current.Game == null)
            {
                error = "No current game.";
                return null;
            }
            foreach (GameComponent c in Current.Game.components)
            {
                if (type.IsInstanceOfType(c)) return c;
            }
            error = "GameComponent_ColonyVisibility type resolved but no instance is registered on Current.Game.";
            return null;
        }

        [Tool(
            "jawa/visibility_report",
            Description =
                "RAW read of RimMandrake.Visibility's GameComponent_ColonyVisibility - the " +
                "0-100 dial, its band, the Sh'kaar escalation multiplier, and every recorded " +
                "tile-memory entry (COLONY_VISIBILITY_BUILD_1's tile-memory round trip: " +
                "recorded on gravship launch via GravshipUtility.GenerateGravship, applied on " +
                "arrival via ArriveNewMap/ArriveExistingMap - both real Harmony postfixes, not " +
                "reflected here, only READ here). Reflection-coupled like " +
                "jawa/flowworks_excavation_report, so this works with or without the mod " +
                "loaded (fails loudly naming why).",
            ResultDescription =
                "success, shipVisibility, band, shkaarEscalationMultiplier, tileMemory[] of " +
                "{tileId, layerId, visibilityAtDeparture, departedTick, ticksAgo, " +
                "predictedDecayedNow (DecayedTileVisibility applied to ticksAgo, so a caller " +
                "can predict a restore BEFORE looking)}, ticksGame.")]
        public static async Task<object> VisibilityReport(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                object comp = ResolveColonyVisibilityComponent(out Type type, out string err);
                if (comp == null) return Fail(err);

                float shipVisibility = (float)type.GetField("shipVisibility").GetValue(comp);
                object bandVal = type.GetProperty("Band").GetValue(comp);
                float shkaar = (float)type.GetField("ShkaarEscalationMultiplier").GetValue(comp);

                IDictionary tileMemory = (IDictionary)type.GetField("tileMemory").GetValue(comp);
                Type memoryType = null;
                var entries = new List<object>();
                int nowTicks = TicksGameSafe();
                foreach (DictionaryEntry de in tileMemory)
                {
                    PlanetTile tile = (PlanetTile)de.Key;
                    object mem = de.Value;
                    if (memoryType == null) memoryType = mem.GetType();
                    float visibilityAtDeparture = (float)memoryType.GetField("visibilityAtDeparture").GetValue(mem);
                    int departedTick = (int)memoryType.GetField("departedTick").GetValue(mem);
                    int ticksAgo = nowTicks - departedTick;
                    float predictedDecayedNow = (float)type.GetMethod("DecayedTileVisibility")
                        .Invoke(null, new object[] { visibilityAtDeparture, ticksAgo });
                    entries.Add(new
                    {
                        tileId = tile.tileId,
                        layerId = tile.Layer.LayerID,
                        tileString = tile.ToString(),
                        visibilityAtDeparture,
                        departedTick,
                        ticksAgo,
                        predictedDecayedNow,
                    });
                }

                return (object)new
                {
                    success = true,
                    shipVisibility,
                    band = bandVal?.ToString(),
                    shkaarEscalationMultiplier = shkaar,
                    tileMemoryCount = entries.Count,
                    tileMemory = entries,
                    ticksGame = nowTicks,
                };
            });
        }
    }
}
