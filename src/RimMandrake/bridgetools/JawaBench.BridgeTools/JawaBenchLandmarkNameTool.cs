using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace JawaBench.BridgeTools
{
    // jawa/world_landmark_rename — the one write world_landmarks_set cannot do.
    // Written for LANDMARK_NAMING_PASS_1 (2026-09-09): 32 generated names are
    // reused planet-wide and the fix is hand names, which need a setter.
    // Landmark.name is a plain public string (Source/RimWorld/Landmark.cs:9),
    // scribed by IExposable — a write survives the save with no regeneration.
    //
    // Must extend the shared JawaBenchTerrainTools partial class like every
    // other [Tool]-bearing file in this assembly — a standalone type here
    // never enters RimBridgeServer's discovered Type space (root-caused
    // 2026-09-10, LANDMARK_NAMING_PASS_1).
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/world_landmark_rename",
            Description =
                "Rename the landmark on a world tile. Landmark.name is a plain scribed " +
                "field; nothing regenerates it, so the write is durable in the save. " +
                "Refuses a tile with no landmark rather than silently doing nothing. " +
                "Does not need world_commit (labels redraw per frame).",
            ResultDescription = "success, tile, def, oldName, newName.")]
        public static async Task<object> WorldLandmarkRename(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "World tile id carrying the landmark.")] int tile = -1,
            [ToolParameter(Description = "The new name, verbatim.")] string name = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (Find.World == null) return new { success = false, message = "No world is loaded." };
                if (tile < 0 || string.IsNullOrWhiteSpace(name))
                    return new { success = false, message = "Give 'tile' and 'name'." };
                var wl = Find.World.landmarks;
                if (wl == null || wl.landmarks == null)
                    return new { success = false, message = "No landmark manager on this world." };
                var hit = wl.landmarks.FirstOrDefault(kv => kv.Key.tileId == tile);
                if (hit.Value == null)
                    return new { success = false, message = "Tile " + tile + " carries no landmark." };
                var old = hit.Value.name;
                hit.Value.name = name.Trim();
                return new { success = true, tile, def = hit.Value.def != null ? hit.Value.def.defName : null, oldName = old, newName = hit.Value.name };
            }, cancellationToken).ConfigureAwait(false);
        }
    }
}
