// JawaBenchMiscTools2.cs - the last two genuine gaps found by cross-checking the
// OWNER-CULLED roster (`design/Jawa/bridge/capability_roster_data.py`, 185 rows,
// posture DEFAULT INCLUDE per `dll_capability_roster.decisions.json`) against the
// live 275-tool surface. Everything else in that 185-row roster already matched
// a shipped tool by name-token cross-reference; these two did not, and a manual
// grep of the source confirmed zero hits for either mechanism. (A third
// candidate, "anything touching Find.UIRoot", was skipped as too vague and HARD
// per the roster's own difficulty column - not a named mechanism, a whole
// subsystem.)
//
// EVERY SIGNATURE BELOW WAS READ OUT OF 1.6 SOURCE VIA rimsage, NOT GUESSED:
//   Verse/ScreenshotTaker.cs         TakeNonSteamShot(string fileName = null),
//                                    QueueSilentScreenshot() - the latter is what
//                                    Update() checks for on the NEXT frame, so it
//                                    is NOT synchronous; this tool calls
//                                    TakeNonSteamShot directly instead, which IS
//                                    synchronous from the caller's point of view
//                                    (ScreenCapture.CaptureScreenshot still
//                                    resolves over the next Unity frame or two,
//                                    same as any engine screenshot call).
//   Verse/RegionAndRoomUpdater.cs    TryRebuildDirtyRegionsAndRooms() - rebuilds
//                                    only what is marked dirty; jawa/map_commit
//                                    always calls the full RebuildAllRegionsAndRooms
//                                    instead, which is correct after a bulk paint
//                                    but wasteful after a small, targeted edit.
//
// 🔴 ONE TRAP FROM MEMORY, NOT SOURCE, WORTH REPEATING IN THE TOOL'S OWN
// DESCRIPTION: TakeNonSteamShot writes into GenFilePaths.ScreenshotFolderPath -
// RimWorld's OWN Screenshots folder - which is NOT where the owner's F10 Steam
// screenshots land (Steam userdata). A caller expecting to find this file where
// they look for their own screenshots will not find it there.
//
// GATING: neither is gated. A screenshot changes nothing in the simulation; a
// dirty-region rebuild is a read-consistency operation, the same tier as
// jawa/map_commit itself (ungated).
//
// THREAD AFFINITY: everything that touches game state is inside
// ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/take_screenshot",
            Description =
                "Save a screenshot of the current render via ScreenshotTaker.TakeNonSteamShot" +
                "(fileName). 🔴 Writes into RimWorld's OWN Screenshots folder " +
                "(GenFilePaths.ScreenshotFolderPath) - this is NOT the same folder the owner's " +
                "F10/Steam screenshots land in (Steam userdata). Report the full path back so " +
                "the caller does not have to guess where it went. ⚠️ success=true means the call " +
                "was MADE, not that a file exists: TakeNonSteamShot swallows its own IO exceptions " +
                "(Log.Error only) and ScreenCapture.CaptureScreenshot resolves a frame or two later, " +
                "so nothing here can confirm the write. Stat the path to be sure.",
            ResultDescription =
                "success, folder, filePath (reconstructed exactly as ScreenshotTaker builds it - " +
                "null when fileName is omitted, because the engine's auto-numbering counter is " +
                "private and unreadable), fileName, verified=false always (see the description).")]
        public static async Task<object> TakeScreenshot(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "File name, no extension (a '.png' is appended). Omit for an auto-numbered 'screenshotN.png'.")]
            string fileName = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string folder;
                try { folder = GenFilePaths.ScreenshotFolderPath; }
                catch (Exception e) { return Fail("GenFilePaths.ScreenshotFolderPath threw " + e.GetType().Name + ": " + e.Message); }

                string requested = string.IsNullOrWhiteSpace(fileName) ? null : fileName.Trim();

                try { ScreenshotTaker.TakeNonSteamShot(requested); }
                catch (Exception e) { return Fail("TakeNonSteamShot threw " + e.GetType().Name + ": " + e.Message); }

                // ScreenshotTaker builds "{folder}{DirectorySeparatorChar}{fileName}.png" when a
                // name is given (Verse/ScreenshotTaker.cs). With no name it loops a PRIVATE
                // counter, so the file name is genuinely unknowable from here - say null rather
                // than hand back a folder dressed up as a path.
                string resolvedPath = requested == null
                    ? null
                    : folder + System.IO.Path.DirectorySeparatorChar + requested + ".png";

                return new
                {
                    success = true,
                    folder,
                    filePath = resolvedPath,
                    fileName = requested == null ? null : requested + ".png",
                    verified = false,
                    note = "This is RimWorld's own Screenshots folder, not the owner's F10/Steam " +
                           "screenshot location. success=true means the call was made: the engine " +
                           "catches its own IO failures (Log.Error only) and the capture resolves a " +
                           "frame or two later, so stat the path before trusting the file exists. " +
                           "With no fileName the engine auto-numbers with a private counter and " +
                           "filePath cannot be reconstructed.",
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/rebuild_dirty_regions",
            Description =
                "Rebuild only DIRTY regions/rooms - map.regionAndRoomUpdater." +
                "TryRebuildDirtyRegionsAndRooms(). A lighter alternative to jawa/map_commit, " +
                "which always calls the full RebuildAllRegionsAndRooms(); use this after a " +
                "small, targeted edit where a full-map rebuild would be wasteful, and " +
                "map_commit after a bulk paint or spawn loop. ⛔ REFUSES when " +
                "regionAndRoomUpdater.Enabled is false - the engine method returns immediately in " +
                "that state and rebuilds nothing, so a success there would be a lie.",
            ResultDescription =
                "success, dirtyRegionsRebuilt (bool - AnythingToRebuild read BEFORE the call, i.e. " +
                "whether the updater had anything to do; false means the call was a legitimate " +
                "no-op), anythingToRebuildAfter (read back, should be false), updaterEnabled.")]
        public static async Task<object> RebuildDirtyRegions(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                var updater = map.regionAndRoomUpdater;

                // Both are pure reads - Enabled returns a bool field, AnythingToRebuild is
                // `regionDirtyer.AnyDirty || !initialized` (Verse/RegionAndRoomUpdater.cs) and
                // mutates nothing. Measuring here does NOT perform the thing being measured.
                bool enabled = updater.Enabled;
                bool hadWork = updater.AnythingToRebuild;

                // TryRebuildDirtyRegionsAndRooms() opens with `if (working || !Enabled) return;`
                // - a total silent no-op. Refuse rather than report success over it.
                if (!enabled)
                    return Fail("map.regionAndRoomUpdater.Enabled is false - " +
                                "TryRebuildDirtyRegionsAndRooms() returns immediately and rebuilds " +
                                "nothing. This is a refusal, not a silent no-op.",
                        new { updaterEnabled = false, dirtyRegionsRebuilt = false, anythingToRebuild = hadWork });

                try { updater.TryRebuildDirtyRegionsAndRooms(); }
                catch (Exception e) { return Fail("TryRebuildDirtyRegionsAndRooms threw " + e.GetType().Name + ": " + e.Message); }

                return new
                {
                    success = true,
                    updaterEnabled = true,
                    dirtyRegionsRebuilt = hadWork,
                    anythingToRebuildAfter = updater.AnythingToRebuild,
                    note = hadWork
                        ? null
                        : "Nothing was dirty - the call was a legitimate no-op, not a failure.",
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
