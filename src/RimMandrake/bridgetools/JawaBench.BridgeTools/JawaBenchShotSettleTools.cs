// JawaBenchShotSettleTools.cs - jawa/settle_tweens: snap every spawned pawn's drawn position to its
// real cell while PAUSED, so a screenshot taken after bulk stepping shows where pawns ARE.
// SHOTSETTLE_BUILD_PAUSED_BARRIER (design/RimMandrake/tickburst_2026-11-06/final.md L-e; GPT review 12).
//
// WHY: PawnTweener eases DrawPos toward the pawn's root a little per real frame, scaled by
// TickRateMultiplier, which reads 0 while paused. After a burst of ticks in one frame the pawn's
// sim position has moved and its drawn position has not, so the picture lies. The old cure was
// "a few real frames at Normal", which ADVANCES THE SIMULATION (GPT 12): a picture that costs ticks.
//
// ENGINE, read with ilprobe from the 1.6 Assembly-CSharp (2026-11-06), not recalled:
//   PawnTweener.ResetTweenedPosToRoot(): tweenedPos = TweenedPosRoot(); lastTickSpringPos = tweenedPos;
//   lastDrawFrame = RealTime.frameCount; lastDrawTick = GenTicks.TicksGame.  Field writes only:
//   it READS TicksGame and never advances it. get_TweenedPos returns the tweenedPos field.
//
// GATING: refuses unless the game is paused (or pauseFirst=true pauses it, which is a speed change,
// not a tick). Calls nothing that ticks: no DoSingleTick, no step, no time-speed above Paused.
// THREAD AFFINITY: all game access inside ctx.MainThread.InvokeAsync.
//
// SINCE RIMMANDRAKE_FIX_BRIDGE_STEPPED_PAWNS_DRAWN_ON_OLD_SQUARE the snap is automatic: JawaBenchDrawSettle
// (below) resets a pawn's tweener on the first draw after a tick was stepped under pause, so every capture
// tool shows it on its own square. settle_tweens stays for a caller that wants the proof of the settle.

using System;
using System.Collections.Generic;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using UnityEngine;
using Verse;

namespace JawaBench.BridgeTools
{
    /// <summary>The automatic half of the barrier. ENGINE (PawnTweener.PreDrawPosCalculation, read 2026-11-24 with RimSage):
    /// a pawn drawn on every frame eases by 0.09 * deltaTime * 60 * TickRateMultiplier, and the multiplier is 0 under
    /// CurTimeSpeed Paused, which is how the bridge steps ticks. So the drawn position stays where the walk began. The
    /// prefix resets the tweener when the tick moved since the pawn's last draw and the game stands paused. A game that
    /// plays never gets here: it is not paused on the frame that ticks. On the frames of an ordinary pause the pawn was
    /// already drawn on that tick, so an ordinary pause keeps its vanilla smoothing.</summary>
    internal static class JawaBenchDrawSettle
    {
        internal static bool Installed;
        internal static string InstallError;        // null when Installed
        internal static bool On = true;
        internal static int Resets;                 // Interlocked: DrawPos may be read off the main thread
        internal static int Faults;

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
                    var m = AccessTools.Method(typeof(PawnTweener), nameof(PawnTweener.PreDrawPosCalculation));
                    if (m == null) { InstallError = "Verse.PawnTweener.PreDrawPosCalculation not found"; return; }
                    new Harmony("mandrake.jawabench.drawsettle").Patch(m, prefix: new HarmonyMethod(
                        typeof(JawaBenchDrawSettle).GetMethod(nameof(TweenPrefix), BindingFlags.Static | BindingFlags.NonPublic)));
                    Installed = true;
                }
                catch (Exception e) { InstallError = e.GetType().Name + ": " + e.Message; }
                finally
                {
                    if (!Installed) Log.Warning("[JawaBench] draw settle NOT installed: " + InstallError +
                                                " - a capture after stepped ticks can draw a pawn on its old square.");
                }
            }
        }

        private static void TweenPrefix(PawnTweener __instance, int ___lastDrawTick)
        {
            try
            {
                if (!On || ___lastDrawTick < 0 || ___lastDrawTick == GenTicks.TicksGame) return;
                var tm = Find.TickManager;
                if (tm == null || !tm.Paused) return;
                __instance.ResetTweenedPosToRoot();
                Interlocked.Increment(ref Resets);
            }
            catch { Interlocked.Increment(ref Faults); }
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/settle_tweens",
            Description =
                "Snap every spawned pawn on the current map to its real position for drawing " +
                "(PawnTweener.ResetTweenedPosToRoot), so a screenshot right after bulk tick stepping " +
                "does not show pawns lagging behind where they are. Runs only while PAUSED and " +
                "advances no ticks: it reports ticksGame before and after so the caller can prove " +
                "it. Call it immediately before take_screenshot (rimbench/shotsettle.py does).",
            ResultDescription =
                "success, paused, ticksBefore, ticksAfter (equal, or success=false), settled (pawns " +
                "reset), noTweener (spawned pawns without a drawer/tweener), maxShiftCells (largest " +
                "drawn-position jump the reset made, x/z plane), mapIndex.")]
        public static async Task<object> SettleTweens(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Pause the game first if it is running (a speed change, never a tick). Off by " +
                "default: an unpaused game is refused, because a running game moves pawns again " +
                "between this call and the capture.", DefaultValue = false)]
            bool pauseFirst = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (Current.Game == null || Find.TickManager == null)
                    return Fail("No game is running.");
                Map map = Find.CurrentMap;
                if (map == null)
                    return Fail("No current map to settle.");
                var tm = Find.TickManager;
                if (!tm.Paused)
                {
                    if (!pauseFirst)
                        return Fail("Game is not paused: pause first (or pass pauseFirst=true); a " +
                                    "running game re-tweens pawns before the capture.",
                                    new { paused = false, ticksGame = tm.TicksGame });
                    tm.CurTimeSpeed = TimeSpeed.Paused;
                }
                int before = tm.TicksGame;
                int settled = 0, noTweener = 0;
                float maxShift = 0f;
                foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    var tw = p?.Drawer?.tweener;
                    if (tw == null) { noTweener++; continue; }
                    Vector3 was = tw.TweenedPos;
                    tw.ResetTweenedPosToRoot();
                    Vector3 now = tw.TweenedPos;
                    // A pawn never drawn yet holds tweenedPos at zero: its "shift" is its distance
                    // from the map origin, not lag, so it is not counted in maxShiftCells.
                    if (was != Vector3.zero)
                    {
                        float dx = now.x - was.x, dz = now.z - was.z;
                        maxShift = Math.Max(maxShift, (float)Math.Sqrt(dx * dx + dz * dz));
                    }
                    settled++;
                }
                int after = tm.TicksGame;
                bool ok = after == before && tm.Paused;
                return new
                {
                    success = ok,
                    message = ok ? null : "ticksGame moved or the game unpaused during the settle",
                    paused = tm.Paused,
                    ticksBefore = before,
                    ticksAfter = after,
                    settled,
                    noTweener,
                    maxShiftCells = maxShift,
                    mapIndex = map.Index,
                };
            });
        }

        [Tool(
            "jawa/drawn_positions",
            Description =
                "Where each named pawn is DRAWN against the square it stands on. Reads PawnTweener.TweenedPos, the field that " +
                "the last drawn frame used: it calls no DrawPos, so the read itself moves nothing. A pawn that the camera does " +
                "not draw has an old drawn position: read framesSinceDraw (0..2 = drawn now) before you use its offset. " +
                "autoSettle on|off turns the automatic snap of stepped pawns (JawaBenchDrawSettle) on or off; keep (default) " +
                "only reads it. It is on at startup; off is for a red control.",
            ResultDescription =
                "success, ticksGame, paused, autoSettle{installed, installError, on, resets, faults}, pawns[] {thingId, x, z, " +
                "drawnX, drawnZ (cells, a square's centre is +0.5), offsetCells (drawn to the centre of the pawn's own square), " +
                "moving, framesSinceDraw (-1 = never drawn)}, notFound[].")]
        public static async Task<object> DrawnPositions(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "comma list of ThingIDs; empty = every spawned pawn of the current map", DefaultValue = "")] string pawnIds = "",
            [ToolParameter(Description = "keep | on | off", DefaultValue = "keep")] string autoSettle = "keep")
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                Map map = Current.Game == null ? null : Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                string mode = (autoSettle ?? "keep").Trim().ToLowerInvariant();
                if (mode != "keep" && mode != "on" && mode != "off") return Fail("autoSettle must be keep, on or off");
                if (mode != "keep") JawaBenchDrawSettle.On = mode == "on";
                var want = new List<string>();
                foreach (var s in (pawnIds ?? "").Split(',')) if (s.Trim().Length > 0) want.Add(s.Trim());
                var lastFrame = AccessTools.Field(typeof(PawnTweener), "lastDrawFrame");
                if (lastFrame == null) return Fail("Verse.PawnTweener.lastDrawFrame not found: a drawn position cannot be dated");
                var rows = new List<object>();
                var found = new HashSet<string>();
                foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    if (want.Count > 0 && !want.Contains(p.ThingID)) continue;
                    found.Add(p.ThingID);
                    var tw = p.Drawer?.tweener;
                    if (tw == null) { rows.Add(new { thingId = p.ThingID, x = p.Position.x, z = p.Position.z, noTweener = true }); continue; }
                    int f = (int)lastFrame.GetValue(tw);
                    Vector3 d = tw.TweenedPos, c = p.Position.ToVector3Shifted();
                    float dx = d.x - c.x, dz = d.z - c.z;
                    rows.Add(new
                    {
                        thingId = p.ThingID, x = p.Position.x, z = p.Position.z, drawnX = Math.Round(d.x, 3), drawnZ = Math.Round(d.z, 3),
                        offsetCells = Math.Round(Math.Sqrt(dx * dx + dz * dz), 3), moving = p.pather != null && p.pather.MovingNow,
                        framesSinceDraw = f < 0 ? -1 : RealTime.frameCount - f,
                    });
                }
                var missing = new List<string>();
                foreach (var w in want) if (!found.Contains(w)) missing.Add(w);
                return new
                {
                    success = missing.Count == 0, message = missing.Count == 0 ? null : "not spawned on the current map: " + string.Join(", ", missing.ToArray()),
                    ticksGame = Find.TickManager.TicksGame, paused = Find.TickManager.Paused,
                    autoSettle = new { installed = JawaBenchDrawSettle.Installed, installError = JawaBenchDrawSettle.InstallError, on = JawaBenchDrawSettle.On,
                                       resets = JawaBenchDrawSettle.Resets, faults = JawaBenchDrawSettle.Faults },
                    pawns = rows, notFound = missing,
                };
            });
        }
    }
}
