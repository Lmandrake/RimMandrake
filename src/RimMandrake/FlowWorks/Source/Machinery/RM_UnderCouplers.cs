using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
    /// <summary>
    /// The hose UNDER-COUPLER's drawing (geometry and the owner's ruling: <see cref="UnderCouplerGeometry"/>): a collar at the
    /// port point and a pipe running on inward to the fixture's footprint centre line, in the fixture's look, at the altitude
    /// the caller gives (the hose band, below the building layer, so the fixture's opaque art covers it). Per frame, only
    /// where a hose is coupled (RM_MapComponent_Hoses.DrawEnds). Nothing while the join fittings are switched off.
    /// </summary>
    public static class RM_UnderCouplers
    {
        /// <summary>State read: under-couplers drawn last frame (probe / live look); reset by <see cref="ResetFrame"/>.</summary>
        public static int lastDraws;

        public static void ResetFrame() => lastDraws = 0;

        /// <summary>True when a hose coupled to <paramref name="port"/> gets an under-coupler (any spawned non-pipe port).</summary>
        public static bool Wanted(Thing port) =>
            RM_MachinerySettings.joinFittings && port != null && port.Spawned && !RM_LiquidNet.IsPipe(port);

        /// <summary>Draw the under-coupler of a hose coupled at port point (px, pz), (sx, sz) = unit step from the hose's end cell
        /// into <paramref name="port"/>. False = nothing drawn (the caller keeps its own stub).</summary>
        public static bool Draw(Thing port, double px, double pz, int sx, int sz, float y)
        {
            if (!Wanted(port) || System.Math.Abs(sx) + System.Math.Abs(sz) != 1) return false;
            string look = RM_LiquidJoins.LookOf(port);
            Material collar = RM_LiquidJoins.Mat("UnderCollar", look), pipe = RM_LiquidJoins.Mat("UnderPipe", look);
            if (collar == null || pipe == null) return false;
            CellRect r = port.OccupiedRect();
            double reach = UnderCouplerGeometry.Reach(px, pz, sx, sz, r.minX, r.minZ, r.Width, r.Height);
            UnderCouplerGeometry.Pipe(reach, out double pc, out double pl);
            // +u of each sprite points inward (along (sx, sz)): the plane's +x rotated onto that axis
            Quaternion q = Quaternion.Euler(0f, -Mathf.Atan2(sz, sx) * Mathf.Rad2Deg, 0f);
            if (pl > 0)
                Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(new Vector3((float)(px + sx * pc), y, (float)(pz + sz * pc)), q,
                    new Vector3((float)pl, 1f, (float)UnderCouplerGeometry.PipeWidth)), pipe, 0);
            double cc = UnderCouplerGeometry.CollarLength / 2.0;
            Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(new Vector3((float)(px + sx * cc), y + 0.0002f, (float)(pz + sz * cc)), q,
                new Vector3((float)UnderCouplerGeometry.CollarLength, 1f, (float)UnderCouplerGeometry.CollarWidth)), collar, 0);
            lastDraws++;
            return true;
        }
    }
}
