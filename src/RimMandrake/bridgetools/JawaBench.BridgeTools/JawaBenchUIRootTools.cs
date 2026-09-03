// JawaBenchUIRootTools.cs - two capabilities under Find.UIRoot, the roster's own
// "HARD, no named mechanism" row turned into two concrete, well-anchored tools once
// actually read. Owner, 2026-08-29: "Those are high priority, do now."
//
// EVERY SIGNATURE BELOW WAS READ OUT OF 1.6 SOURCE VIA rimsage, NOT GUESSED:
//   Verse/WindowStack.cs   Windows (IList<Window>, read-only view), IsOpen(Type)
//   Verse/Window.cs        layer, optionalTitle, ID, IsDebug, forcePause,
//                          Close(bool doCloseSound = true) - public virtual, calls
//                          Find.WindowStack.TryRemove(this, doCloseSound) internally
//   Verse/UIRoot.cs        screenshotMode (ScreenshotModeHandler)
//   Verse/ScreenshotModeHandler.cs   Active - a plain settable bool property, the
//                          SAME flag the player's own screenshot-mode hotkey toggles
//
// 🔴 WHY jawa/window_list_close EXISTS: this project's own memory record
// (`stale-modal-blocks-every-later-call`) names a real incident - five runs, five
// wrong counts, because a stuck window was never checked. Nothing on the bridge
// before this could see or clear an open dialog; every prior workaround was
// restarting the game.
//
// GATING: neither is gated. Closing a dialog or toggling a rendering flag changes no
// simulation state - the same tier as jawa/set_fog or jawa/av_effect, not an incident.
//
// THREAD AFFINITY: everything that touches game state is inside
// ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
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
            "jawa/window_list_close",
            Description =
                "List every open Window on the stack, or close one - Find.WindowStack.Windows " +
                "for the list; Window.Close(doCloseSound) to close (the same virtual method " +
                "the window's own close button calls). 'list' is read-only. 'close' targets " +
                "EITHER 'index' (from a prior 'list' call - precise, use this when you already " +
                "know which one) OR 'typeName' (a substring match against the window's own " +
                "type name, case-insensitive - REFUSES rather than guessing if it matches more " +
                "than one window unless closeAll=true). This is the answer to a stuck modal " +
                "silently blocking every later call - a failure this project has hit before.",
            ResultDescription =
                "list: success, count, windows[] (index, type, optionalTitle, layer, ID, " +
                "isDebug, forcePause). close: success (false if ANY target survived), " +
                "closedCount, closed[] (type, optionalTitle), refusedCount, refused[] - a " +
                "window whose own OnCloseRequest() vetoed the close, verified against the " +
                "stack AFTER the call rather than assumed from Close() returning - plus " +
                "refusedNote and stillOpenCount.")]
        public static async Task<object> WindowListClose(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'list' (default) or 'close'.")]
            string action = "list",
            [ToolParameter(Description = "close: index from a prior 'list' call.", DefaultValue = -1)]
            int index = -1,
            [ToolParameter(Description = "close: substring of the window's type name, case-insensitive.")]
            string typeName = null,
            [ToolParameter(Description = "close: if typeName matches more than one window, close all of them rather than refusing. Default false.")]
            bool closeAll = false,
            [ToolParameter(Description = "close: play the window's own close sound. Default true.")]
            bool doCloseSound = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var stack = Find.WindowStack;
                if (stack == null) return Fail("No active WindowStack - is a game loaded?");

                var windows = stack.Windows;

                string a = (action ?? "list").Trim().ToLowerInvariant();
                if (a == "list")
                {
                    var rows = new List<object>();
                    for (int i = 0; i < windows.Count; i++)
                    {
                        var w = windows[i];
                        rows.Add(new
                        {
                            index = i,
                            type = w.GetType().FullName,
                            optionalTitle = w.optionalTitle,
                            layer = w.layer.ToString(),
                            id = w.ID,
                            isDebug = w.IsDebug,
                            forcePause = w.forcePause
                        });
                    }
                    return new { success = true, action = "list", count = rows.Count, windows = rows, ticksGame = TicksGameSafe() };
                }

                if (a == "close")
                {
                    List<Window> targets = new List<Window>();
                    if (index >= 0)
                    {
                        if (index >= windows.Count) return Fail("index " + index + " is out of range (0.." + (windows.Count - 1) + "). Call action=list first.");
                        targets.Add(windows[index]);
                    }
                    else if (!string.IsNullOrWhiteSpace(typeName))
                    {
                        var matches = windows.Where(w => w.GetType().FullName != null &&
                            w.GetType().FullName.IndexOf(typeName.Trim(), StringComparison.OrdinalIgnoreCase) >= 0).ToList();
                        if (matches.Count == 0)
                            return Fail("No open window's type name contains '" + typeName + "'.",
                                new { openTypes = windows.Select(w => w.GetType().FullName).ToList() });
                        if (matches.Count > 1 && !closeAll)
                            return Fail("'" + typeName + "' matches " + matches.Count + " open windows. Pass closeAll=true, or use 'index' for one specific window.",
                                new { matchedTypes = matches.Select(w => w.GetType().FullName).ToList() });
                        targets.AddRange(matches);
                    }
                    else
                    {
                        return Fail("Give 'index' or 'typeName' for action=close.");
                    }

                    var closed = new List<object>();
                    var refused = new List<object>();
                    foreach (var w in targets)
                    {
                        string t = w.GetType().FullName;
                        string title = w.optionalTitle;
                        try { w.Close(doCloseSound); }
                        catch (Exception e) { return Fail("Close() threw " + e.GetType().Name + ": " + e.Message + " on " + t, new { closedSoFar = closed }); }
                        // 🔴 Window.Close(bool) is a one-liner over WindowStack.TryRemove(this, sound)
                        // and THROWS AWAY its bool. TryRemove changes nothing and returns false when
                        // the window's own OnCloseRequest() vetoes (Page_ModsConfig overrides it in
                        // vanilla; mod windows commonly do) or when the window already left the stack.
                        // A stuck modal is precisely what this tool exists for and precisely what
                        // vetoes, so verify against the stack instead of trusting the call.
                        if (stack.Windows.Contains(w)) refused.Add(new { type = t, optionalTitle = title });
                        else closed.Add(new { type = t, optionalTitle = title });
                    }

                    return new
                    {
                        success = refused.Count == 0,
                        action = "close",
                        closedCount = closed.Count,
                        closed,
                        refusedCount = refused.Count,
                        refused,
                        refusedNote = refused.Count > 0
                            ? "Still on the stack after Close(): the window's own OnCloseRequest() " +
                              "refused, or it was already gone. Window.Close() cannot force these."
                            : null,
                        stillOpenCount = stack.Windows.Count,
                        ticksGame = TicksGameSafe()
                    };
                }

                return Fail("action must be 'list' or 'close'.");
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/screenshot_mode",
            Description =
                "Get or set Find.UIRoot.screenshotMode.Active - the same flag the player's own " +
                "screenshot-mode hotkey (KeyBindingDefOf.ToggleScreenshotMode) toggles: hides " +
                "the mouse cursor and most transient UI while active, so jawa/take_screenshot " +
                "captures a clean frame instead of whatever dialog/cursor happened to be on " +
                "screen. Windows with drawInScreenshotMode=false (most utility dialogs) stop " +
                "drawing entirely while this is on.",
            ResultDescription = "success, activeBefore, activeAfter.")]
        public static async Task<object> ScreenshotMode(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "true to enable, false to disable. Omit to just read the current state.")]
            bool? enabled = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Find.UIRoot == null) return Fail("No active UIRoot - is the game running?");
                var handler = Find.UIRoot.screenshotMode;
                if (handler == null) return Fail("UIRoot.screenshotMode is null.");

                bool before = handler.Active;
                if (enabled.HasValue) handler.Active = enabled.Value;

                return new
                {
                    success = true,
                    activeBefore = before,
                    activeAfter = handler.Active,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
