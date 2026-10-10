// Reads vector lines on stdin, answers each with the production JawaBenchTpsMath result.
// Driven by src/RimMandrake/Utils/selftest_tps_record.py, which compares every line against
// the Python port in tps_record.py. Line grammar (space-separated, invariant culture):
//   K                                         -> the constants
//   A name                                    -> start a new frame trace (fresh accumulator); echoes "A name"
//   F now paused mult ticksBefore explained multAfter ticksAfter simS
//                                             -> one frame; prints "G <gap fields>" for a gap and
//                                                "W <window fields>" when a window closes
//   M x...                                    -> median
//   S r...                                    -> sustained verdict
//   R currentBytes lineBytes                  -> rotate(0|1)
//   N epochSeconds session pid segment        -> segment file name
//   X bytes:ageDays:session:pinned:active ... cap -> retention plan (indices to delete, in order)
//   U                                         -> the C# unit group (Units*.cs): "U name ok|FAIL why",
//                                                "J name <json>" production-composed lines, "U-count n"
using System;
using System.Globalization;
using System.Linq;
using M = JawaBench.BridgeTools.JawaBenchTpsMath;

namespace JawaBench.BridgeTools
{
    internal static class Program
    {
        static double P(string s) => double.Parse(s, CultureInfo.InvariantCulture);

        static int Main()
        {
            var acc = new M.FrameAccumulator();
            string line;
            while ((line = Console.In.ReadLine()) != null)
            {
                var a = line.Trim().Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
                if (a.Length == 0) continue;
                switch (a[0])
                {
                    case "K":
                        Console.WriteLine(string.Join(" ", new[] {
                            "K", M.F(M.CadenceSeconds, 4), M.F(M.GapSeconds, 4), M.F(M.ExplainedShare, 4),
                            M.F(M.TicksPerSecondAtSpeed1, 4), M.F(M.PausedShare, 4), M.F(M.StallShare, 4),
                            M.F(M.LongEventShare, 4), M.F(M.MixedShare, 4), M.F(M.FrameBudgetSeconds, 4),
                            M.MaxGapsPerWindow.ToString(CultureInfo.InvariantCulture),
                            M.SegmentBytes.ToString(CultureInfo.InvariantCulture), M.F(M.RetentionDays, 4),
                            M.RetentionBytes.ToString(CultureInfo.InvariantCulture),
                            M.LogRetentionBytes.ToString(CultureInfo.InvariantCulture),
                            M.QueueCapacity.ToString(CultureInfo.InvariantCulture),
                            M.F(M.SilenceSeconds, 4), M.F(M.SilenceRepeatSeconds, 4),
                            M.RingCapacity.ToString(CultureInfo.InvariantCulture),
                            M.SustainedSamples.ToString(CultureInfo.InvariantCulture),
                            M.F(M.LowRatio, 4), M.F(M.HighRatio, 4) }));
                        break;
                    case "A":
                        acc = new M.FrameAccumulator();
                        Console.WriteLine("A " + a[1]);
                        break;
                    case "F":
                        var g = acc.Pre(P(a[1]), a[2] == "1", P(a[3]), int.Parse(a[4]), P(a[5]));
                        if (g.HasValue) Console.WriteLine("G \"type\":\"" + g.Value.Kind + "\"," + M.GapFields(g.Value));
                        var w = acc.TakeClosed();
                        if (w != null) Console.WriteLine("W " + M.WindowFields(w));
                        acc.Post(P(a[6]), int.Parse(a[7]), P(a[8]));
                        break;
                    case "M":
                        Console.WriteLine("M " + M.F(M.Median(a.Skip(1).Select(P).ToList()), 3));
                        break;
                    case "S":
                        Console.WriteLine("S " + M.Sustained(a.Skip(1).Select(P).ToList()));
                        break;
                    case "Q":   // the SAMPLER's streak: raw ratios through StreakValue, then Sustained
                        Console.WriteLine("Q " + M.Sustained(a.Skip(1).Select(P).Select(M.StreakValue).ToList()));
                        break;
                    case "R":
                        Console.WriteLine("R " + (M.ShouldRotate(long.Parse(a[1]), long.Parse(a[2])) ? 1 : 0));
                        break;
                    case "N":
                        var t = DateTimeOffset.FromUnixTimeSeconds(long.Parse(a[1])).UtcDateTime;
                        Console.WriteLine("N " + M.SegmentName(t, a[2], int.Parse(a[3]), int.Parse(a[4])));
                        break;
                    case "X":
                        var items = a.Skip(1).Take(a.Length - 2).Select(x => x.Split(':')).ToList();
                        var del = M.PlanRetention(items.Select(x => long.Parse(x[0])).ToList(),
                                                  items.Select(x => P(x[1])).ToList(),
                                                  items.Select(x => x[2]).ToList(),
                                                  items.Select(x => x[3] == "1").ToList(),
                                                  items.Select(x => x[4] == "1").ToList(), long.Parse(a[a.Length - 1]));
                        Console.WriteLine("X " + string.Join(",", del));
                        break;
                    case "U":
                        Units.Run();
                        break;
                    default:
                        Console.WriteLine("? " + line);
                        return 2;
                }
            }
            return 0;
        }
    }
}
