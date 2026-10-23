using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
    /// <summary>
    /// The hose UNDER-COUPLER's drawing (geometry and the owner's ruling: <see cref="UnderCouplerGeometry"/>): a collar at the
    /// port point and a pipe running on inward until it is beneath the fixture's opaque body (UnderCouplerReach), in the fixture's look, at the altitude
    /// the caller gives (the hose band, below the building layer, so the fixture's opaque art covers it). Per frame, only
    /// where a hose is coupled (RM_MapComponent_Hoses.DrawEnds). Nothing while the join fittings are switched off.
    /// </summary>
    public static class RM_UnderCouplers
    {
        /// <summary>State read: under-couplers drawn last frame (probe / live look); reset by <see cref="ResetFrame"/>.</summary>
        public static int lastDraws;

        private static readonly System.Collections.Generic.Dictionary<string, Material[]> matCache = new System.Collections.Generic.Dictionary<string, Material[]>();

        /// <summary>Per-def under-coupler look for fixtures that are not style-picked and whose art is not the default (Scrapper, copper) look:
        /// Kludged = weathered dark steel pipework (Industrial set); Repaired = painted white/red steel, clean brushed steel (Modern set).</summary>
        public static readonly System.Collections.Generic.Dictionary<string, string> ArtLookOverride = new System.Collections.Generic.Dictionary<string, string>
        {
            { "RM_PumpingStation_Kludged", "Industrial" },
            { "RM_PumpingStation_Repaired", "Modern" },
        };

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
            // PUMPSTATION_COUPLER_MATCH_FIX_STEEL (delegated art pick 2026-10-23): unstyled fixtures whose art is steel, not copper
            if (!PipeLook.IsStyled(port.def) && ArtLookOverride.TryGetValue(port.def.defName, out string artLook)) look = artLook;
            // per-look cache: RM_LiquidJoins.Mat builds a key string per call, and this runs every frame for every coupled hose end
            if (!matCache.TryGetValue(look ?? "", out Material[] mp))
            {
                mp = new[] { RM_LiquidJoins.Mat("UnderCollar", look), RM_LiquidJoins.Mat("UnderPipe", look) };
                matCache[look ?? ""] = mp;
            }
            Material collar = mp[0], pipe = mp[1];
            if (collar == null || pipe == null) return false;
            CellRect r = port.OccupiedRect();
            double reach = UnderCouplerGeometry.Reach(px, pz, sx, sz, r.minX, r.minZ, r.Width, r.Height);
            // judge FIX 2026-10-23: the pipe ends beneath the first opaque body run of the fixture's art (UnderCouplerReach,
            // measured from the installed art), never across open ground; no body on this axis = no under-coupler
            int side = sz == 1 ? 0 : sz == -1 ? 1 : sx == 1 ? 2 : 3;
            int lane = sx != 0 ? (int)System.Math.Floor(pz - r.minZ) : (int)System.Math.Floor(px - r.minX);
            lane = System.Math.Max(0, System.Math.Min((sx != 0 ? r.Height : r.Width) - 1, lane));
            if (UnderCouplerReach.TryGet(port.def.defName, PipeLook.IsStyled(port.def) ? look : "", side, lane, out double measured))
            {
                if (measured < 0) return false;
                reach = measured;
            }
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
