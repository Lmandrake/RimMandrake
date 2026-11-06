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

using System;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using UnityEngine;
using Verse;

namespace JawaBench.BridgeTools
{
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
    }
}
