// T_ROOF_WITHER_OFFLINE driver. One plant per stdin line:
//   W id x z maxHp hp witherTicks gate(0|1) roofFrom roofUntil steps    (a living plant; roofed on long ticks roofFrom <= k < roofUntil)
//   C id x z maxHp hp crumbleTicks steps                                 (dead grass crumbling)
// Prints one line per long tick: "line k stage damage lethal hp" (line = the plant's 0-based input line), and stops a plant at its lethal step.
using System;
using System.Globalization;
using System.Text;

namespace RimMandrake.Pyrelands.RoofWither
{
    internal static class Program
    {
        private static int Main()
        {
            var o = new StringBuilder();
            string line;
            int plants = 0;
            while ((line = Console.In.ReadLine()) != null)
            {
                string[] f = line.Split(' ', StringSplitOptions.RemoveEmptyEntries);
                if (f.Length == 0) continue;
                int[] n = new int[f.Length - 1];
                for (int i = 1; i < f.Length; i++) n[i - 1] = int.Parse(f[i], CultureInfo.InvariantCulture);
                int id = n[0], x = n[1], z = n[2], maxHp = n[3], hp = n[4];
                int state = 0, dealt = 0;
                plants++;
                if (f[0] == "W")
                {
                    int wither = n[5]; bool gate = n[6] != 0; int from = n[7], until = n[8], steps = n[9];
                    for (int k = 0; k < steps; k++)
                    {
                        bool roofed = k >= from && k < until;
                        var s = RM_RoofWitherKernel.Advance(ref state, ref dealt, id, x, z, maxHp, hp, wither, gate, roofed);
                        hp -= s.Damage;
                        o.Append(plants - 1).Append(' ').Append(k).Append(' ').Append(s.Stage).Append(' ').Append(s.Damage).Append(' ')
                            .Append(s.Lethal ? 1 : 0).Append(' ').Append(hp).Append('\n');
                        if (s.Lethal) break;
                    }
                }
                else
                {
                    int crumble = n[5], steps = n[6];
                    for (int k = 0; k < steps; k++)
                    {
                        var s = RM_RoofWitherKernel.Crumble(ref state, ref dealt, id, x, z, maxHp, hp, crumble);
                        hp -= s.Damage;
                        o.Append(plants - 1).Append(' ').Append(k).Append(' ').Append(s.Stage).Append(' ').Append(s.Damage).Append(' ')
                            .Append(s.Lethal ? 1 : 0).Append(' ').Append(hp).Append('\n');
                        if (s.Lethal) break;
                    }
                }
            }
            Console.Out.Write(o.ToString());
            Console.Out.WriteLine("END " + plants);
            return 0;
        }
    }
}
