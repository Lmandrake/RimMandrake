// JawaBenchLoreStageTools.cs - STAGED_LORE_PROOF_SPIKE_1.
//
// mandrake.rm.lorestages' own dev-mode debug action ("Lore stages\Set ladder
// stage...") opens a hand-built LudeonTK.Dialog_DebugOptionListLister two
// levels deep - a genuine runtime UI dialog, not a node in the enumerable
// debug-action tree, so execute_debug_action cannot reach into it and OS-level
// mouse clicking is the only route a human has. That is fine for a person at
// the keyboard and unusable for an unattended bridge proof, and doubly so on
// a shared desktop where another window can steal the click mid-flight
// (measured live, 2026-09-11: a File Explorer search popped up over RimWorld
// between two clicks and ate them both).
//
// This tool calls the SAME public API the debug action calls
// (GameComponent_LoreStage.SetStage/GetStage) directly, via reflection so this
// assembly does not need a project reference to RimMandrake.LoreStages.dll
// (which may not even be deployed on every mod list this companion runs
// against). Loads and does nothing but report absence when that mod is not
// active - never throws for a missing optional dependency.
//
// THREAD AFFINITY: touches Current.Game and a GameComponent's mutable state -
// main thread only.

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
        private static Type LoreStageComponentType() =>
            AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(a => { try { return a.GetTypes(); } catch { return Array.Empty<Type>(); } })
                .FirstOrDefault(t => t.FullName == "RimMandrake.LoreStages.GameComponent_LoreStage");

        [Tool(
            "jawa/lore_stage_get",
            Description = "Reads a mandrake.rm.lorestages ladder's current rung via " +
                "GameComponent_LoreStage.GetStage, by reflection (no hard dependency on " +
                "that assembly). Returns present=false, not an error, when the mod is not " +
                "loaded or no Game exists yet.",
            ResultDescription = "success, present, ladderId, stage.")]
        public static async Task<object> LoreStageGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "The ladderId, e.g. \"Scarlands\".")] string ladderId)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Type compType = LoreStageComponentType();
                if (compType == null)
                {
                    return (object)new { success = true, present = false, ladderId, ticksGame = TicksGameSafe() };
                }

                object current = compType.GetProperty("Current", BindingFlags.Public | BindingFlags.Static)
                    ?.GetValue(null);
                if (current == null)
                {
                    return (object)new { success = true, present = false, ladderId, reason = "no Game loaded", ticksGame = TicksGameSafe() };
                }

                int stage = (int)compType.GetMethod("GetStage").Invoke(current, new object[] { ladderId });
                return (object)new { success = true, present = true, ladderId, stage, ticksGame = TicksGameSafe() };
            });
        }

        [Tool(
            "jawa/lore_stage_set",
            Description = "Sets a mandrake.rm.lorestages ladder's rung via " +
                "GameComponent_LoreStage.SetStage, by reflection - the same call the " +
                "mod's own 'Set ladder stage...' debug action makes, without needing to " +
                "click through its two-level runtime dialog. Clamps to the table's " +
                "maxStage and re-applies every staged field immediately. Fails loudly " +
                "(present=false) rather than silently when the mod or Game is absent.",
            ResultDescription = "success, present, ladderId, stage (post-clamp, read back), changed.")]
        public static async Task<object> LoreStageSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "The ladderId, e.g. \"Scarlands\".")] string ladderId,
            [ToolParameter(Description = "The rung to set. Clamped to [0, table.maxStage].")] int stage)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Type compType = LoreStageComponentType();
                if (compType == null)
                {
                    return Fail("mandrake.rm.lorestages is not loaded (GameComponent_LoreStage type not found).");
                }

                object current = compType.GetProperty("Current", BindingFlags.Public | BindingFlags.Static)
                    ?.GetValue(null);
                if (current == null)
                {
                    return Fail("No current Game - start or load one first.");
                }

                bool changed = (bool)compType.GetMethod("SetStage").Invoke(current, new object[] { ladderId, stage });
                int readBack = (int)compType.GetMethod("GetStage").Invoke(current, new object[] { ladderId });
                return (object)new { success = true, present = true, ladderId, stage = readBack, changed, ticksGame = TicksGameSafe() };
            });
        }
    }
}
