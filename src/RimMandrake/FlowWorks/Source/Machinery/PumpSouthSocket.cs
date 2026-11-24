// Verse-free (the SelfTest compiles this file): how a pipe on the liquid pump's south side is drawn into the pump.
using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.Machinery
{
    /// <summary>
    /// Owner 2026-11-23 (LIQUID_PUMP_REDRAW_PLAN_VIEW_HUB): "I should not be able to see the capped end when a pipe is connected,
    /// right? It should cover the cap but leave the bolted rim visible just like the other directions show." The pump's art
    /// draws its south arm end-on: a round cap inside a bolted rim. The pipes draw below the pump, so a pipe from the south
    /// passed behind that cap. This is the piece of that pipe drawn over the pump: from the shared cell edge up onto the cap,
    /// its width going from the pipe's own to the cap's, its end the top half of the cap's outline. Only while a pipe or a hose is
    /// there (a pipe: SectionLayer_RM_PipeCentreStubs; a hose: RM_UnderCouplers.DrawSouthSocket, per frame, in the pump's look).
    /// Cell units, from the pump cell's south-west corner.
    /// </summary>
    public static class PumpSouthSocket
    {
        public const int Columns = 24;
        /// <summary>Where the universal pipe's north-south tile is drawn across its 0..1 width (every look;
        /// selftest_pump_south_socket.py re-measures it).</summary>
        public const double PipeLo = 0.4318, PipeHi = 0.5682;

        public struct Cap
        {
            public readonly double X, Z, HalfW, HalfH;
            public Cap(double x, double z, double hw, double hh) { X = x; Z = z; HalfW = hw; HalfH = hh; }
        }

        /// <summary>The cap's outline, measured from the installed art: art_source/PumpOblique/v2/south_socket.py --write.</summary>
        private static readonly Dictionary<string, Cap> Caps = new Dictionary<string, Cap>
        {
            // table:
            { "Scrapper", new Cap(0.4997, 0.1251, 0.0650, 0.0561) },
            { "Industrial", new Cap(0.4994, 0.1328, 0.0656, 0.0564) },
            { "Modern", new Cap(0.4997, 0.1300, 0.0698, 0.0605) },
            { "Futuristic", new Cap(0.4999, 0.1201, 0.0648, 0.0544) },
            // :table
        };

        public static bool TryCap(string look, out Cap cap) => Caps.TryGetValue(look ?? "", out cap) || Caps.TryGetValue("Scrapper", out cap);

        /// <summary>Does a hose coupled with the unit step (sx, sz) from its end into the thing cover the cap: the liquid pump,
        /// from its south.</summary>
        public static bool HoseCovers(bool isLiquidPump, int sx, int sz) => isLiquidPump && sx == 0 && sz == 1;

        /// <summary>One corner of a quad: position in the cell and position on the pipe's straight tile.</summary>
        public struct Vert
        {
            public double X, Z, U, V;
        }

        /// <summary>The piece as quads of four corners in clockwise order seen from above (south-west, north-west, north-east,
        /// south-east): per column, one quad from the cell edge to the cap's middle and one on up to the cap's outline.</summary>
        public static List<Vert> Quads(Cap cap)
        {
            var o = new List<Vert>(Columns * 8);
            for (int i = 0; i < Columns; i++)
            {
                double a = (double)i / Columns, b = (double)(i + 1) / Columns;
                Add(o, cap, a, b, 0);
                Add(o, cap, a, b, 1);
            }
            return o;
        }

        private static void Add(List<Vert> o, Cap cap, double a, double b, int upper)
        {
            o.Add(Point(cap, a, upper));
            o.Add(Point(cap, a, upper + 1));
            o.Add(Point(cap, b, upper + 1));
            o.Add(Point(cap, b, upper));
        }

        /// <summary>Row 0 = the cell edge (the pipe's own width), 1 = the cap's middle line, 2 = the top of the cap's outline.</summary>
        private static Vert Point(Cap cap, double f, int row)
        {
            double u = PipeLo + f * (PipeHi - PipeLo);
            double across = 2 * f - 1;
            double x = row == 0 ? u : cap.X + across * cap.HalfW;
            double z = row == 0 ? 0 : row == 1 ? cap.Z : cap.Z + cap.HalfH * Math.Sqrt(Math.Max(0, 1 - across * across));
            return new Vert { X = x, Z = z, U = u, V = z };
        }
    }
}
