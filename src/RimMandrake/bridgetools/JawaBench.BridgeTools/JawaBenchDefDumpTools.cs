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

// 🔴 RunOnDemand IS ITSELF A SILENT-FAILURE SURFACE (found on review, 2026-09-03).
// DefDumper.RunOnDemand is `void` and wraps its whole body in `catch (Exception ex)
// { Log.Error(...) }` - by design, its own comment says "a research tool must never be
// why a session ends". DefDumper.Publish does the same: it returns false and logs when
// the capture cannot be named, and RunWithMode simply `return`s. So NOTHING throws back
// across this call, the try/catch below can only ever catch a load failure at the call
// site itself, and reporting success on a clean return would report success on a dump
// that never wrote a byte - the exact defect (a path that reports nothing while doing
// nothing) this tool was created to route around. This tool therefore READS BACK: it
// lists DefDump/captures/ before and after and refuses unless a NEW capture directory
// was published.

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using Verse;

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
                "success, mode, capture (the NEW capture directory's id), capturePath and " +
                "manifestPresent. RunOnDemand swallows every exception it hits and returns " +
                "void, so this tool does not trust a clean return: it lists DefDump/captures/ " +
                "before and after and FAILS if no new capture was published, naming Player.log " +
                "as the place the reason was logged.")]
        public static async Task<object> RimDefDumpRun(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "'all' (full def dump + animals.json) or 'animals' (animals.json only, " +
                "faster). Anything else is REFUSED here - DefDumper.RunWithMode would log a " +
                "warning and quietly run the animals-only pass, publishing a capture with no " +
                "defs/ under a mode the caller never asked for.", DefaultValue = "all")]
            string mode = "all")
        {
            cancellationToken.ThrowIfCancellationRequested();

            return await ctx.MainThread.InvokeAsync(() =>
            {
                string m = (mode ?? "all").Trim().ToLowerInvariant();
                if (m != "all" && m != "animals")
                    return Fail("mode must be 'all' or 'animals'. DefDumper.RunWithMode logs a warning and runs " +
                                "the ANIMALS-ONLY pass for anything else, which would publish a capture with no " +
                                "defs/ while this tool reported success.");

                // DefDumper's FolderName/CapturesDir are private consts; these two literals
                // duplicate DefDumper.cs:73 and :96 deliberately - the alternative is no
                // readback at all. If either moves, this tool starts refusing rather than
                // starting to lie, which is the safe direction.
                string capturesRoot;
                try
                {
                    capturesRoot = Path.Combine(Path.Combine(GenFilePaths.SaveDataFolderPath, "DefDump"), "captures");
                }
                catch (Exception e)
                {
                    return Fail("Could not resolve the DefDump captures folder: " + e.GetType().Name + ": " + e.Message);
                }

                HashSet<string> before, after;
                string listErr;
                if (!TryListCaptureDirs(capturesRoot, out before, out listErr))
                    return Fail("Could not list " + capturesRoot + " before the dump (" + listErr +
                                ") - refusing rather than reporting an unverifiable success.");

                try
                {
                    RimMandrake.RimDefDump.DefDumper.RunOnDemand(m);
                }
                catch (Exception e)
                {
                    return Fail("DefDumper.RunOnDemand threw: " + e.GetType().Name + ": " + e.Message);
                }

                if (!TryListCaptureDirs(capturesRoot, out after, out listErr))
                    return Fail("Could not list " + capturesRoot + " after the dump (" + listErr +
                                ") - the dump may or may not have published; check the folder yourself.");

                after.ExceptWith(before);
                if (after.Count == 0)
                    return Fail("DefDumper.RunOnDemand returned but published NO new capture under " + capturesRoot +
                                ". It catches every exception internally and only Log.Errors, and Publish() returns " +
                                "false without throwing when the capture cannot be named - so the reason is in " +
                                "Player.log under '[RimMandrake.RimDefDump]'. Nothing was lost: existing captures " +
                                "are intact and a half-written one is left under .writing/.");

                string capture = after.OrderBy(s => s, StringComparer.Ordinal).Last();
                string capturePath = Path.Combine(capturesRoot, capture);
                bool manifestPresent;
                try { manifestPresent = File.Exists(Path.Combine(capturePath, "manifest.json")); }
                catch (Exception) { manifestPresent = false; }

                return (object)new
                {
                    success = true,
                    mode = m,
                    capture,
                    capturePath,
                    manifestPresent,
                    extraNewCaptures = after.Count > 1 ? after.Count - 1 : 0,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        /// <summary>
        /// Published capture ids under DefDump/captures/. A missing folder is a legitimate
        /// empty answer (first ever run); an IO failure is NOT, and is reported so the caller
        /// never sees "no new capture" when the truth is "could not look".
        /// </summary>
        private static bool TryListCaptureDirs(string capturesRoot, out HashSet<string> names, out string err)
        {
            names = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            err = null;
            try
            {
                if (!Directory.Exists(capturesRoot)) return true;
                foreach (string d in Directory.GetDirectories(capturesRoot))
                {
                    string name = Path.GetFileName(d);
                    // ".writing" is the in-progress staging dir, never a published capture.
                    if (!string.IsNullOrEmpty(name) && name[0] != '.') names.Add(name);
                }
                return true;
            }
            catch (Exception e)
            {
                err = e.GetType().Name + ": " + e.Message;
                return false;
            }
        }
    }
}
