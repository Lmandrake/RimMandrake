// JawaBenchCathedralAttitudeTools.cs - CATHEDRAL_STAGE_HUM_BRIDGE_1.
//
// The arc's conduct-stage (0 WARY, 1 TOLERATED, 2 VOUCHED --
// design/Jawa/cathedral_concealment_arc_spec.md §1) sets the baseline the
// Rust Cathedral kit's hum-mood composite band recovers toward. The GM
// blackboard (item 1, Python, shadow-mode first per the arc spec's own
// build table) is the eventual stage SOURCE; this tool is the bridge lane
// that lets it (or a human/quicktest proving this item) push a stage onto
// a live map's RM_MapComponent_BiomeAttitude, exactly the "small setter...
// exposed as a JawaBench bridge tool, NOT a second attitude system" the
// item's own spec calls for.
//
// Reflection, not a project reference -- same reasoning as
// JawaBenchLoreStageTools.cs: mandrake.utinni.rustcathedralhum is an
// optional campaign mod that may not be on every list this companion
// builds against, so this file must load and report absence cleanly
// rather than fail the whole assembly when it isn't.
//
// THREAD AFFINITY: touches a Map's MapComponent state - main thread only.

using System;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private static Type CathedralAttitudeComponentType() =>
            AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(a => { try { return a.GetTypes(); } catch { return Array.Empty<Type>(); } })
                .FirstOrDefault(t => t.FullName == "RimMandrake.Utinni.RustCathedralHum.RM_MapComponent_BiomeAttitude");

        [Tool(
            "jawa/cathedral_attitude_set_stage",
            Description = "Sets the current map's Rust Cathedral conduct-stage (0 WARY, " +
                "1 TOLERATED, 2 VOUCHED -- design/Jawa/cathedral_concealment_arc_spec.md " +
                "§1) via RM_MapComponent_BiomeAttitude.SetStage, by reflection (no hard " +
                "dependency on that mod). NOT a second attitude system and not ratcheted " +
                "here -- callable in any direction at any time, including the arc's own " +
                "'dark flip' back to WARY regardless of history. Only affects the " +
                "DISPLAYED hum band (ceiling + decay speed); raw irritation/goodwill/" +
                "hysteresis math is untouched. present=false (not an error) when the mod " +
                "is not loaded, no current map exists, or the map's biome has no matching " +
                "RM_BiomeAttitudeDef (every biome but the Cathedral today).",
            ResultDescription = "success, present, stage (read back), displayBand, " +
                "rawBand (the unclamped internal band, for diagnosing the ceiling's " +
                "effect), ticksGame.")]
        public static async Task<object> CathedralAttitudeSetStage(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "The stage to set: 0 WARY, 1 TOLERATED, 2 VOUCHED (or any int the def's own stageParams key on).")] int stage)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null)
                {
                    return (object)new { success = true, present = false, reason = "no current map", ticksGame = TicksGameSafe() };
                }

                Type compType = CathedralAttitudeComponentType();
                if (compType == null)
                {
                    return (object)new { success = true, present = false, reason = "RustCathedralHum not loaded", ticksGame = TicksGameSafe() };
                }

                MethodInfo setStageMethod = compType.GetMethod("SetStage", BindingFlags.Public | BindingFlags.Static);
                MethodInfo getStageMethod = compType.GetMethod("GetStage", BindingFlags.Public | BindingFlags.Static);
                MethodInfo getBandMethod = compType.GetMethod("GetBand", BindingFlags.Public | BindingFlags.Static);
                if (setStageMethod == null || getStageMethod == null || getBandMethod == null)
                {
                    return Fail("RM_MapComponent_BiomeAttitude.SetStage/GetStage/GetBand not found by reflection (renamed or removed).");
                }

                object componentObj = map.GetComponent(compType);
                if (componentObj == null)
                {
                    // FillComponents instantiates every MapComponent subclass on every
                    // map (see that class's own header comment), so a null here means
                    // the map genuinely has no attitude def match -- report present,
                    // not an error, per GetStage's own -1 "no def" convention.
                    return (object)new { success = true, present = false, reason = "no RM_BiomeAttitudeDef targets this map's biome", ticksGame = TicksGameSafe() };
                }

                setStageMethod.Invoke(null, new object[] { map, stage });
                int readBackStage = (int)getStageMethod.Invoke(null, new object[] { map });
                int displayBand = (int)getBandMethod.Invoke(null, new object[] { map });

                FieldInfo rawBandField = compType.GetField("currentBand", BindingFlags.NonPublic | BindingFlags.Instance);
                int rawBand = rawBandField != null ? (int)rawBandField.GetValue(componentObj) : -1;

                return (object)new
                {
                    success = true,
                    present = true,
                    stage = readBackStage,
                    displayBand,
                    rawBand,
                    ticksGame = TicksGameSafe(),
                };
            });
        }
    }
}
