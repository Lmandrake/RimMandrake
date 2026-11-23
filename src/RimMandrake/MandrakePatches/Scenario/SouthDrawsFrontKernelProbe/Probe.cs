using System;
using System.Globalization;
using System.IO;
using System.Text;
using RimMandrake.Patches;

// One query per stdin line, one answer per stdout line (float "R", invariant culture):
//   B <layer> <footMinZ> <mapSizeZ>   SouthDrawsFrontKernel.BuildingAltitude
//   L <layer> <footMinZ> <mapSizeZ>   SouthDrawsFrontKernel.BuildingLift
//   P <foot> <mapSizeZ>               SouthDrawsFrontKernel.PlantAltitude
//   O <isPlant 0|1> <layer>           SouthDrawsFrontKernel.Orders (1 or 0)
//   A <layer>                         SouthDrawsFrontKernel.LayerAltitude
// An unknown query answers "ERR <line>" so the caller can never read a stale number for it.
public static class Probe
{
    public static int Main()
    {
        CultureInfo inv = CultureInfo.InvariantCulture;
        var sb = new StringBuilder();
        string line;
        TextReader input = Console.In;
        while ((line = input.ReadLine()) != null)
        {
            string[] p = line.Trim().Split(' ');
            if (p.Length == 0 || p[0].Length == 0)
                continue;
            string a;
            try
            {
                switch (p[0])
                {
                    case "B": a = SouthDrawsFrontKernel.BuildingAltitude(int.Parse(p[1], inv), int.Parse(p[2], inv), int.Parse(p[3], inv)).ToString("R", inv); break;
                    case "L": a = SouthDrawsFrontKernel.BuildingLift(int.Parse(p[1], inv), int.Parse(p[2], inv), int.Parse(p[3], inv)).ToString("R", inv); break;
                    case "P": a = SouthDrawsFrontKernel.PlantAltitude(float.Parse(p[1], inv), int.Parse(p[2], inv)).ToString("R", inv); break;
                    case "O": a = SouthDrawsFrontKernel.Orders(p[1] == "1", int.Parse(p[2], inv)) ? "1" : "0"; break;
                    case "A": a = SouthDrawsFrontKernel.LayerAltitude(int.Parse(p[1], inv)).ToString("R", inv); break;
                    default: a = "ERR " + line; break;
                }
            }
            catch (Exception e)
            {
                a = "ERR " + line + " " + e.GetType().Name;
            }
            sb.Append(a).Append('\n');
        }
        Console.Out.Write(sb.ToString());
        return 0;
    }
}
