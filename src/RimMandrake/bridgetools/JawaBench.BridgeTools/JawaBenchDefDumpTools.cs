// JawaBenchDefDumpTools.cs - fire RMDefDump's on-demand dump directly, no debug-action tree.
//
// DEFDUMP_ONDEMAND_BRIDGE_UNREACHABLE_1. RimMandrake.RimDefDump.RimDefDumpDebugActions'
// two [DebugAction] methods (plain actionType=Action, category "RMDefDump") are
// unreachable via both the host's own rimworld/list_debug_action_children /
// execute_debug_action AND this project's own jawa/debug_actions catalogue tool - measured
// 2026-09-03: `list_debug_action_children('Actions\RMDefDump')` answers "Could not find",
// and a flat execute of "Actions\Dump defs now (all)" times out without RunOnDemand's own
// first log line ever printing. jawa/debug_actions is explicitly "a catalogue, not a
// trigger" even if it did find the entry (see JawaBenchDebugActionTools.cs) - it could
// never have fired this either way.
//
// FIX: call RimMandrake.RimDefDump.DefDumper.RunOnDemand(mode) directly. This is a
// PLAIN STATIC METHOD CALL against RimDefDump.dll (referenced the same way
// RimMandrakeOracle.dll already is - see the csproj's OracleModDir comment for why
// Private=false against the game's own deployed copy is correct here too), with zero
// dependency on GenTypes.AllTypes, DebugTabMenu_Actions, or either bridge's debug-action
// discovery surface. Whatever is actually keeping those two unreachable (a stale
// GenTypes.AllTypes snapshot is the leading theory from a related investigation,
// FLUID_CANAL_DEBUG_SURFACE_1 - unconfirmed for this mod specifically) simply does not
// matter to this tool, because it never asks either bridge to find or run a debug action
// at all.
//
// THREAD AFFINITY: RunOnDemand walks DefDatabase<T> and writes files - no live Map/Pawn/
// Thing state, but it does touch Verse statics (GenFilePaths, DefDatabase) the same way
// the vanilla [StaticConstructorOnStartup] path already does off the render loop. Routed
// through MainThread.InvokeAsync anyway, matching this project's own default rule (see
// the rimbridge-companion skill's design rule 1) rather than asserting a new exception.

using System;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/rimdefdump_run",
            Description =
                "Fire RimMandrake.RimDefDump.DefDumper.RunOnDemand(mode) directly - a plain " +
                "static call, not a debug-action lookup. Exists because RMDefDump's two " +
                "[DebugAction]s (category 'RMDefDump') are unreachable via both the host's " +
                "rimworld/execute_debug_action and this project's own jawa/debug_actions " +
                "(DEFDUMP_ONDEMAND_BRIDGE_UNREACHABLE_1). No map or game object is touched; " +
                "defs are already fully loaded and cross-resolved the moment any game state " +
                "exists, so the dump this produces matches the one the startup path takes. " +
                "Writes under RimWorld's own DefDump/captures/<timestamp>/ folder, same as " +
                "the automatic startup dump.",
            ResultDescription =
                "success. The dump itself writes its own manifest.json under DefDump/captures/ " +
                "- this tool does not read it back, so confirm the new capture directory " +
                "appeared (and its capturedUtc/modCount) before trusting the result.")]
        public static async Task<object> RimDefDumpRun(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "'all' (full def dump + animals.json) or 'animals' (animals.json only, " +
                "faster). Anything else runs the animals-only pass and logs a warning - " +
                "see DefDumper.Run's own mode handling.", DefaultValue = "all")]
            string mode = "all")
        {
            cancellationToken.ThrowIfCancellationRequested();

            return await ctx.MainThread.InvokeAsync(() =>
            {
                try
                {
                    RimMandrake.RimDefDump.DefDumper.RunOnDemand(mode);
                }
                catch (Exception e)
                {
                    return Fail("DefDumper.RunOnDemand threw: " + e.GetType().Name + ": " + e.Message);
                }

                return (object)new
                {
                    success = true,
                    mode,
                    note = "RunOnDemand does not hand back its own manifest path - check " +
                           "DefDump/captures/ for a new capture directory to confirm.",
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
