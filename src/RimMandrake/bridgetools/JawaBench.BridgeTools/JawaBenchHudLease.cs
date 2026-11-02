// JawaBenchHudLease.cs - the screenshot-mode lease behind clear_ui's hideHud
// (CELL_RECT_SHOT_FIX_COLONIST_BAR_PHOTOBOMBS).
//
// 🔴 WHY: clear_ui closed the dev windows and the selection, but the COLONIST BAR is
// neither. It is drawn by MapInterface.MapInterfaceOnGUI_BeforeMainTabs, which calls
// ColonistBar.ColonistBarOnGUI unless Find.UIRoot.screenshotMode.FiltersCurrentEvent
// (read from the 1.6 IL with ilprobe, not recalled). ColonistBar.Visible itself has no
// preference: it is only screen size and the tile picker. So every tall rect shot
// carried the bar across its top (live art look 2026-10-22: r4_south.png,
// probe_site.png). Vanilla's own screenshot mode - the player's hotkey flag - is the
// one switch that removes it, along with the main tabs, messages and tooltips.
//
// ⚠️ A FLAG LEFT ON IS THE OWNER'S HUD GONE. Screenshot mode is persistent UI state;
// a harness that sets it and crashes, or simply never resets it, hands him a game with
// no interface. So clear_ui does not just set it: it takes a short REALTIME LEASE.
// Each clear_ui call extends the lease; a Harmony postfix on
// ScreenshotModeHandler.ScreenshotModesOnGUI (called by UIRoot.UIRootOnGUI on every
// OnGUI event, unconditionally - also read from the IL) turns the flag back off when
// the lease runs out. Only a flag WE turned on is turned off: if screenshot mode was
// already on when the lease began (his own hotkey), the lease never touches it.
//
// Harmony contact point, isolated on the same discipline as JawaBenchArgGuard: no
// Harmony type touched outside Install()/Postfix, both try/catch-guarded.
//
// ⛔ NO jawa/ PREFIXES IN PROSE IN THIS FILE: build.py scans the assembly for them.

using System;
using System.Reflection;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchHudLease
    {
        internal const string TargetType = "Verse.ScreenshotModeHandler";
        internal const string TargetMethod = "ScreenshotModesOnGUI";

        internal static bool Installed;
        internal static string InstallError;      // null when Installed

        /// <summary>Realtime (Time.realtimeSinceStartup) at which the lease ends; 0 = no lease.</summary>
        internal static float LeaseUntil;
        /// <summary>True only when the lease itself switched screenshot mode on.</summary>
        internal static bool Owned;
        internal static int Expiries;

        private static readonly object Gate = new object();
        private static bool _attempted;

        internal static void Install()
        {
            lock (Gate)
            {
                if (_attempted) return;
                _attempted = true;
                try
                {
                    var t = AccessTools.TypeByName(TargetType);
                    var m = t == null ? null : AccessTools.Method(t, TargetMethod);
                    if (m == null)
                    {
                        InstallError = TargetType + "." + TargetMethod + " not found";
                        Log.Warning("[JawaBench] HUD lease NOT installed: " + InstallError +
                                    " - clear_ui will not hide the HUD (it refuses to set a flag nothing would reset).");
                        return;
                    }
                    var harmony = new Harmony("mandrake.jawabench.hudlease");
                    harmony.Patch(m, postfix: new HarmonyMethod(
                        typeof(JawaBenchHudLease).GetMethod(nameof(Postfix),
                            BindingFlags.Static | BindingFlags.NonPublic)));
                    Installed = true;
                }
                catch (Exception e)
                {
                    InstallError = e.GetType().Name + ": " + e.Message;
                    Log.Warning("[JawaBench] HUD lease NOT installed: " + InstallError);
                }
            }
        }

        /// <summary>Main thread only. Hide the HUD for `seconds` of realtime from now.
        /// Returns whether the HUD is hidden after the call; `error` says why not.</summary>
        internal static bool Take(float seconds, out bool wasActive, out string error)
        {
            wasActive = false;
            error = null;
            Install();
            if (!Installed) { error = "HUD lease not installed: " + InstallError; return false; }
            var handler = Find.UIRoot?.screenshotMode;
            if (handler == null) { error = "No UIRoot.screenshotMode - not at a UI-bearing state."; return false; }
            wasActive = handler.Active;
            if (!wasActive)
            {
                handler.Active = true;
                Owned = true;
            }
            // A flag already on and not ours (his hotkey) is left alone at expiry.
            if (Owned)
                LeaseUntil = Mathf.Max(LeaseUntil, Time.realtimeSinceStartup + seconds);
            return handler.Active;
        }

        private static void Postfix(ScreenshotModeHandler __instance)
        {
            try
            {
                if (!Owned || Time.realtimeSinceStartup < LeaseUntil) return;
                Owned = false;
                LeaseUntil = 0f;
                __instance.Active = false;
                Expiries++;
            }
            catch
            {
                // Never break the UI root's OnGUI over a convenience flag.
            }
        }
    }
}
