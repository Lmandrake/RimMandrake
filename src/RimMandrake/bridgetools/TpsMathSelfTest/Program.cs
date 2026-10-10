// Reads vector lines on stdin, answers each with the production JawaBenchTpsMath result.
// Driven by src/RimMandrake/Utils/selftest_tps_record.py, which compares every line against
// the Python port in tps_record.py. Line grammar (space-separated, invariant culture):
//   K                                   -> the constants
//   C dTicks dReal frames paused mult changed(0|1)   -> tps target ratio pausedFrac state
//   W dReal dTicks                      -> usable(0|1)
//   M x...                              -> median
//   S r...                              -> sustained verdict
//   R currentBytes lineBytes            -> rotate(0|1)
using System;
using System.Globalization;
using System.Linq;

namespace JawaBench.BridgeTools
{
    internal static class Program
    {
        static float P(string s) => float.Parse(s, CultureInfo.InvariantCulture);

        static int Main()
        {
            string line;
            while ((line = Console.In.ReadLine()) != null)
            {
                var a = line.Trim().Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
                if (a.Length == 0) continue;
                switch (a[0])
                {
                    case "K":
                        Console.WriteLine(string.Join(" ", new[] {
                            "K", JawaBenchTpsMath.F(JawaBenchTpsMath.CadenceSeconds, 4),
                            JawaBenchTpsMath.F(JawaBenchTpsMath.MaxWindowSeconds, 4),
                            JawaBenchTpsMath.F(JawaBenchTpsMath.TicksPerSecondAtSpeed1, 4),
                            JawaBenchTpsMath.F(JawaBenchTpsMath.PausedShare, 4),
                            JawaBenchTpsMath.RotateBytes.ToString(CultureInfo.InvariantCulture),
                            JawaBenchTpsMath.RingCapacity.ToString(CultureInfo.InvariantCulture),
                            JawaBenchTpsMath.SustainedSamples.ToString(CultureInfo.InvariantCulture),
                            JawaBenchTpsMath.F(JawaBenchTpsMath.LowRatio, 4),
                            JawaBenchTpsMath.F(JawaBenchTpsMath.HighRatio, 4) }));
                        break;
                    case "C":
                        var s = JawaBenchTpsMath.Compute(int.Parse(a[1]), P(a[2]), int.Parse(a[3]), int.Parse(a[4]),
                                                         P(a[5]), a[6] == "1");
                        Console.WriteLine("C " + JawaBenchTpsMath.F(s.Tps, 2) + " " + JawaBenchTpsMath.F(s.Target, 2) + " " +
                                          JawaBenchTpsMath.F(s.Ratio, 3) + " " + JawaBenchTpsMath.F(s.PausedFrac, 3) + " " + s.State);
                        break;
                    case "W":
                        Console.WriteLine("W " + (JawaBenchTpsMath.WindowUsable(P(a[1]), int.Parse(a[2])) ? 1 : 0));
                        break;
                    case "M":
                        Console.WriteLine("M " + JawaBenchTpsMath.F(JawaBenchTpsMath.Median(a.Skip(1).Select(P).ToList()), 3));
                        break;
                    case "S":
                        Console.WriteLine("S " + JawaBenchTpsMath.Sustained(a.Skip(1).Select(P).ToList()));
                        break;
                    case "R":
                        Console.WriteLine("R " + (JawaBenchTpsMath.ShouldRotate(long.Parse(a[1]), long.Parse(a[2])) ? 1 : 0));
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
