// Verse-free: FlowWorks/selftest_hose_fittings.py parses the constants below (never edit their shape without the gate).
using System;

namespace RimMandrake.FlowWorks.Machinery
{
    /// <summary>
    /// HOSE UNDER-COUPLERS (owner ruling 2026-10-23, by card: "Make your couplers as needed, but have their art go UNDER the
    /// tank or pump or other fixture. That way you don't have to worry about how they "end" on the item ... So have them seem
    /// to go beneath, and all is well."). Where a hose end is coupled to a tank, liquid machine or other non-pipe port, a rigid
    /// spigot in the port's look is drawn in the hose band -- below the building layer -- from the port point (where the
    /// hose's brass coupling face sits) inward along the port axis to the footprint's centre line: a COLLAR (the coupler face)
    /// then a straight PIPE. The fixture's opaque art hides it; its transparent margins show a coupler that runs on beneath.
    /// Art: Textures/RimMandrake/FlowWorks/Joins/&lt;Look&gt;/UnderCollar.png and UnderPipe.png (art_source/UnderCouplers/
    /// under_couplers.py), each drawn as a quad of exactly the sizes below, its texture's +u pointing inward.
    /// </summary>
    public static class UnderCouplerGeometry
    {
        /// <summary>Cells: the collar's length along the axis and width across it; the pipe's width (its length is
        /// <see cref="PipeLength"/>). Canvas px at 256 px/cell: collar 36 x 80, pipe 32 (stretched) x 56.</summary>
        public const double CollarLength = 0.140625, CollarWidth = 0.3125, PipeWidth = 0.21875;

        /// <summary>How far the spigot runs inward from the port point (px, pz) along the unit step (sx, sz) (end cell -> fixture)
        /// to the footprint's centre line; never shorter than the collar.</summary>
        public static double Reach(double px, double pz, int sx, int sz, int bx, int bz, int bw, int bh)
        {
            double cx = bx + bw / 2.0, cz = bz + bh / 2.0;
            double d = sx != 0 ? (cx - px) * sx : (cz - pz) * sz;
            return Math.Max(CollarLength, d);
        }

        /// <summary>Centre (along the axis from the port point) and length of the pipe quad: from halfway along the collar
        /// (the collar draws over that half, so no seam shows) to <see cref="Reach"/>.</summary>
        public static void Pipe(double reach, out double centreAlong, out double length)
        {
            length = Math.Max(0.0, reach - CollarLength / 2.0);
            centreAlong = CollarLength / 2.0 + length / 2.0;
        }
    }
}
