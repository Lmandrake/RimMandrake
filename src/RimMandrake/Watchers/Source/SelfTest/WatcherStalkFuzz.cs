// Approach B for the Rust Cathedral Watcher (../Kernel/RM_WatcherStalkKernel.cs), family "stalk":
//   - the phase machine driven tick by tick against random worlds (intruders in and out of the flinch circle, bouts running out, settings
//     with zero-length animations): the hidden hediff goes on ONLY after a retract has run its full length (or with no stalk up at all),
//     a retract once begun always finishes unless the job is force-ended, the stalk is never drawn while hidden, a hidden watcher
//     emerges into a rise, and a bout that runs out retracts before it ends;
//   - angle easing against brute force (never overshoots, always takes the shorter arc, reaches the target in ceil(|d|/step) steps);
//   - the octant and mirrored-picture table against an independent restatement.
// A failing case prints `stalk seed N: message`; --fuzz-seed N replays it. PROVISIONAL numbers (rise 40, retract 10) are tuning only.
using System;
using System.Collections.Generic;
using RimMandrake.Watchers;

namespace RimMandrake.Watchers.SelfTest
{
    internal static class WatcherStalkFuzz
    {
        public static long Hides, Retracts, Rises, EndRetracts, Emerges;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        public static List<string> Run(int cases, int baseSeed)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = baseSeed + c;
                try { Phase(seed); Angles(seed); }
                catch (Exception e) { fails.Add("stalk seed " + seed + ": " + e.Message); }
                WatcherFuzz.Cases++;
            }
            try { Table(); } catch (Exception e) { fails.Add("stalk table: " + e.Message); }
            if (cases >= 100 && (Hides == 0 || Retracts == 0 || Rises == 0 || EndRetracts == 0 || Emerges == 0))
                fails.Add($"stalk fuzz never reached a path (blind): hides {Hides}, retracts {Retracts}, rises {Rises}, end-retracts {EndRetracts}, emerges {Emerges}");
            return fails;
        }

        private static void Phase(int seed)
        {
            var r = new Random(seed);
            int rise = r.Next(4) == 0 ? 0 : r.Next(1, 60);
            int retract = r.Next(4) == 0 ? 0 : r.Next(1, 30);
            int maxWatch = r.Next(100, 3000);
            int interval = 1 + r.Next(30);
            StalkPhase phase = StalkPhase.Down;
            int phaseStart = 0, hiddenUntil = -1, watchStart = 0;
            bool hidden = false, endAfter = false, intruder = false, ended = false;
            int retractStartedAt = -1;
            for (int t = 0; t < 4000 && !ended; t += interval)
            {
                if (r.Next(40) == 0) intruder = !intruder;
                bool forceOff = r.Next(400) == 0;
                StepFlags kit = RM_WatcherKernel.DecideStep(new StepIn
                {
                    watchersEnabled = !forceOff, onMedium = true, hidden = hidden, hideAndFlinch = true, turnToFace = true,
                    hasNearest = intruder, inFlinch = intruder, now = t, hiddenUntil = hiddenUntil, watchStart = watchStart, maxWatchTicks = maxWatch,
                });
                StalkOut o = RM_WatcherStalkKernel.Step(new StalkIn
                {
                    phase = phase, elapsed = t - phaseStart, riseTicks = rise, retractTicks = retract, endAfterRetract = endAfter,
                    hidden = hidden, kit = kit,
                });
                StalkPhase before = phase;
                if ((o.flags & StalkFlags.EndInterrupted) != 0) { ended = true; break; }
                Check(!(hidden && before != StalkPhase.Down), $"t{t}: hidden while phase {before}");
                if ((o.flags & StalkFlags.ApplyHide) != 0)
                {
                    Check(!hidden, $"t{t}: hide applied while already hidden");
                    bool fromRetract = before == StalkPhase.Retracting;
                    bool instant = (before == StalkPhase.Up || before == StalkPhase.Rising) && retract == 0;
                    bool neverUp = before == StalkPhase.Down;
                    Check(fromRetract || instant || neverUp, $"t{t}: hide from phase {before}");
                    if (fromRetract) Check(t - retractStartedAt >= retract, $"t{t}: hide {t - retractStartedAt} ticks into a {retract}-tick retract");
                    Check(o.phase == StalkPhase.Down, $"t{t}: hidden but phase {o.phase}");
                    hidden = true; Hides++;
                    hiddenUntil = t + r.Next(50, 400);
                }
                if ((o.flags & StalkFlags.StartRetract) != 0) { retractStartedAt = t; Retracts++; }
                if (before == StalkPhase.Retracting && o.phase != StalkPhase.Retracting)
                    Check(t - retractStartedAt >= retract, $"t{t}: retract cut short at {t - retractStartedAt} of {retract}");
                if (before == StalkPhase.Retracting && o.phase == StalkPhase.Retracting)
                    Check((o.flags & (StalkFlags.ApplyHide | StalkFlags.EndSucceeded | StalkFlags.StartRise)) == 0, $"t{t}: acted mid-retract");
                if ((o.flags & StalkFlags.ApplyEmerge) != 0)
                {
                    Check(hidden, $"t{t}: emerge while not hidden");
                    hidden = false; Emerges++;
                    Check((o.flags & StalkFlags.StartRise) != 0 && o.phase == StalkPhase.Rising, $"t{t}: emerged without a rise");
                }
                if ((o.flags & StalkFlags.StartRise) != 0) { Rises++; Check(o.phase == StalkPhase.Rising, $"t{t}: rise but phase {o.phase}"); }
                if ((o.flags & StalkFlags.ResetWatchClock) != 0) watchStart = t;
                if ((o.flags & StalkFlags.EndSucceeded) != 0)
                {
                    Check(!hidden, $"t{t}: bout ended while hidden (the kit's hungry path is unused here)");
                    Check(o.phase == StalkPhase.Down, $"t{t}: bout ended with the stalk {o.phase}");
                    if (before == StalkPhase.Retracting) EndRetracts++;
                    else Check(before == StalkPhase.Down || retract == 0, $"t{t}: bout ended from {before} without a retract");
                    ended = true;
                }
                Check(!(hidden && RM_WatcherStalkKernel.StalkDrawn(o.phase, false, false)), $"t{t}: stalk drawn while hidden");
                if (o.phaseChanged || o.phase != phase) { phase = o.phase; phaseStart = t; }
                endAfter = o.endAfterRetract;
                WatcherFuzz.Steps++;
            }
        }

        private static void Angles(int seed)
        {
            var r = new Random(seed ^ 0x5a5a);
            float cur = (float)(r.NextDouble() * 720 - 360), target = (float)(r.NextDouble() * 720 - 360);
            float step = r.Next(5) == 0 ? 0f : (float)(0.5 + r.NextDouble() * 20);
            float d0 = Math.Abs(RM_WatcherStalkKernel.Delta(cur, target));
            Check(d0 <= 180.0001f, $"delta {d0} > 180");
            int need = step <= 0f ? 1 : (int)Math.Ceiling(d0 / step - 1e-4);
            float prevDist = d0;
            for (int i = 0; i < need + 2; i++)
            {
                float next = RM_WatcherStalkKernel.Ease(cur, target, step);
                Check(next >= 0f && next < 360f, $"ease left [0,360): {next}");
                float moved = Math.Abs(RM_WatcherStalkKernel.Delta(cur, next));
                if (step > 0f) Check(moved <= step + 1e-3f, $"moved {moved} > step {step}");
                float dist = Math.Abs(RM_WatcherStalkKernel.Delta(next, target));
                Check(dist <= prevDist + 1e-3f, $"moved away: {prevDist} -> {dist}");
                cur = next; prevDist = dist;
                WatcherFuzz.Steps++;
            }
            Check(prevDist < 1e-2f, $"did not reach target within {need} steps (left {prevDist}, step {step})");
        }

        private static void Table()
        {
            string[] dirs = { "N", "NE", "E", "SE", "S", "SW", "W", "NW" };
            for (int deg = -720; deg <= 720; deg++)
            {
                int o = RM_WatcherStalkKernel.Octant(deg);
                double n = ((deg % 360) + 360) % 360;
                int spec = (int)Math.Floor((n + 22.5) / 45.0) % 8;
                Check(o == spec, $"octant({deg}) = {o}, spec {spec}");
            }
            // Picture table, restated: N NE E SE S drawn; SW = SE mirrored, W = E mirrored, NW = NE mirrored.
            int[] pic = { 0, 1, 2, 3, 4, 3, 2, 1 };
            bool[] mir = { false, false, false, false, false, true, true, true };
            for (int i = 0; i < 8; i++)
            {
                int p = RM_WatcherStalkKernel.PictureFor(i, out bool m);
                Check(p == pic[i] && m == mir[i], $"{dirs[i]}: picture {p} mirrored {m}");
                Check(RM_WatcherStalkKernel.Octant(RM_WatcherStalkKernel.OctantAngle(i)) == i, $"octant centre {i} round trip");
            }
            for (int i = 0; i < 1000; i++)
            {
                float roll = i / 1000f;
                float t = RM_WatcherStalkKernel.IdleTarget(100f, roll);
                float d = Math.Abs(RM_WatcherStalkKernel.Delta(100f, t));
                Check(d >= 45f - 1e-3f && d <= 135f + 1e-3f, $"idle turn {d} outside 45-135");
            }
            WatcherFuzz.Cases++;
        }
    }
}
