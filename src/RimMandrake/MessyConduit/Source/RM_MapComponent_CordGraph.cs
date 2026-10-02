using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.MessyConduit.Core;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit
{
    /// <summary>
    /// Runtime-only owner of a map's cord graph (design §8.1): nothing here is saved (no
    /// ExposeData), the whole graph and every polyline is rebuilt from the conduit grid on load and
    /// seeded so it comes out identical.
    ///
    /// Rebuild trigger: a SectionLayer_RM_MessyCords regenerating means one of its change flags
    /// fired (Buildings, PowerGrid, Terrain, FogOfWar, or our own RM_MessyCords). The first such
    /// regenerate in a frame rebuilds the map's pieces (CordBuilder re-plans only edges whose key or
    /// corridor changed); any OTHER section whose owned pieces changed is then dirtied with the
    /// RM_MessyCords flag, because vanilla only dirties the changed cell's neighbours while a cord
    /// can run several sections away (§8.1).
    ///
    /// Live/dead (§8.5): every 250 ticks each conduit end's net is re-read; a flip dirties only its
    /// owning section (dead ends lie limp, live ones are straight and spark).
    /// </summary>
    public class RM_MapComponent_CordGraph : MapComponent
    {
        private readonly CordBuilder builder = new CordBuilder();
        private List<LaidPiece> pieces = new List<LaidPiece>();
        private Dictionary<IntVec2, List<LaidPiece>> bySection = new Dictionary<IntVec2, List<LaidPiece>>();
        private Dictionary<Cell, bool> liveEnds = new Dictionary<Cell, bool>();
        private int builtFrame = -1;
        private bool buildErrorLogged;
        public int Builds, LastPlanned, LastReused;
        public CordWorld LastWorld;

        public RM_MapComponent_CordGraph(Map map) : base(map) { }

        public CordGraph Graph => builder.Graph;
        public IReadOnlyList<LaidPiece> Pieces => pieces;

        public static IntVec2 SectionOf(Cell c) => new IntVec2(c.X / Section.Size, c.Z / Section.Size);

        public List<LaidPiece> PiecesForSection(IntVec3 botLeft)
        {
            if (Time.frameCount != builtFrame) Rebuild();
            var key = new IntVec2(botLeft.x / Section.Size, botLeft.z / Section.Size);
            return bySection.TryGetValue(key, out List<LaidPiece> l) ? l : null;
        }

        public void Notify_SettingsChanged() => builtFrame = -1;

        public void Rebuild()
        {
            builtFrame = Time.frameCount;
            if (!MessyConduitSettings.enabled)
            {
                pieces = new List<LaidPiece>();
                bySection = new Dictionary<IntVec2, List<LaidPiece>>();
                return;
            }
            CordWorld world = CordWorldAdapter.Snapshot(map);
            LastWorld = world;
            CordBuilder b = builder;
            List<LaidPiece> next;
            try { next = b.Build(world, MessyConduitSettings.BuildOptions(), c => LiveNow(c)); }
            catch (Exception ex)
            {
                if (!buildErrorLogged) { buildErrorLogged = true; Log.Error("[MessyConduit] cord build failed, drawing no cords: " + ex); }
                next = new List<LaidPiece>();
            }
            Builds++;
            LastPlanned = b.LastPlanned;
            LastReused = b.LastReused;
            var nextBy = new Dictionary<IntVec2, List<LaidPiece>>();
            foreach (LaidPiece p in next)
            {
                IntVec2 s = SectionOf(p.Owner);
                if (!nextBy.TryGetValue(s, out List<LaidPiece> l)) nextBy[s] = l = new List<LaidPiece>();
                l.Add(p);
            }
            // dirty every section whose owned set changed (not just the regenerating one)
            if (Current.ProgramState == ProgramState.Playing)
            {
                var keys = new HashSet<IntVec2>(nextBy.Keys);
                keys.UnionWith(bySection.Keys);
                foreach (IntVec2 s in keys)
                {
                    string a = Sig(bySection, s), z = Sig(nextBy, s);
                    if (a != z)
                        map.mapDrawer.MapMeshDirty(new IntVec3(s.x * Section.Size, 0, s.z * Section.Size), MessyConduitDefOf.RM_MessyCords);
                }
            }
            pieces = next;
            bySection = nextBy;
        }

        private static string Sig(Dictionary<IntVec2, List<LaidPiece>> d, IntVec2 s) =>
            d.TryGetValue(s, out List<LaidPiece> l) ? string.Join("\n", l.Select(p => p.Key + "@" + p.GeometryHash())) : "";

        private bool LiveNow(Cell c)
        {
            bool v = CordWorldAdapter.IsLive(map, c);
            liveEnds[c] = v;
            return v;
        }

        public override void MapComponentTick()
        {
            if (!MessyConduitSettings.enabled) return;
            int t = Find.TickManager.TicksGame;
            if (t % 250 == map.uniqueID % 250) PollLive();
            if (MessyConduitSettings.breakReadout && MessyConduitSettings.sparkIntensity > 0.01f) Sparks(t);
        }

        /// <summary>Re-read live/dead for every conduit end; a flip dirties its owner section only.</summary>
        public int PollLive()
        {
            int flips = 0;
            foreach (LaidPiece p in pieces)
                foreach (CordEnd e in p.Ends)
                {
                    bool now = CordWorldAdapter.IsLive(map, e.NetCell);
                    if (liveEnds.TryGetValue(e.NetCell, out bool was) && was == now) continue;
                    liveEnds[e.NetCell] = now;
                    flips++;
                    map.mapDrawer.MapMeshDirty(CordWorldAdapter.I(p.Owner), MessyConduitDefOf.RM_MessyCords);
                }
            return flips;
        }

        public bool? EndLive(Cell c) => liveEnds.TryGetValue(c, out bool v) ? v : (bool?)null;

        private const int MaxSparkingEnds = 24;

        private void Sparks(int tick)
        {
            int n = 0;
            float k = MessyConduitSettings.sparkIntensity;
            foreach (LaidPiece p in pieces)
                foreach (CordEnd e in p.Ends)
                {
                    if (!liveEnds.TryGetValue(e.NetCell, out bool live) || !live) continue;
                    if (++n > MaxSparkingEnds) return;
                    int h = (e.NetCell.X * 73856093) ^ (e.NetCell.Z * 19349663);
                    int period = Mathf.Max(12, Mathf.RoundToInt((e.Wall ? 50 : 80) / k));
                    if ((tick + (h & 0x7fff)) % period != 0) continue;
                    var at = new Vector3((float)e.Tip.X, AltitudeLayer.MoteOverhead.AltitudeFor(), (float)e.Tip.Z);
                    FleckMaker.ThrowMicroSparks(at, map);
                    if (((tick / period + h) & 3) == 0) FleckMaker.ThrowLightningGlow(at, map, e.Wall ? 0.6f : 0.4f);
                }
        }

        public override void MapComponentUpdate()
        {
            MessyConduitProbe.Service(map, this);
            if (!MessyConduitSettings.enabled || !MessyConduitSettings.debugDraw || Find.CurrentMap != map) return;
            CordGraph g = builder.Graph;
            if (g == null) return;
            float y = AltitudeLayer.MetaOverlays.AltitudeFor();
            foreach (CordEdge e in g.Edges)
            {
                var a = new Vector3((float)e.PA.X, y, (float)e.PA.Z);
                var b = new Vector3((float)e.PB.X, y, (float)e.PB.Z);
                GenDraw.DrawLineBetween(a, b, e.Hidden ? SimpleColor.Magenta : SimpleColor.White, 0.08f);
            }
            foreach (CordNode nd in g.Nodes.Values)
            {
                SimpleColor col = nd.Type == NodeType.Terminal ? SimpleColor.Red : nd.IsMachine ? SimpleColor.Yellow :
                                  nd.IsStub ? SimpleColor.Cyan : nd.Type == NodeType.Junction ? SimpleColor.Blue : SimpleColor.Green;
                GenDraw.DrawCircleOutline(new Vector3((float)nd.Pos.X, y, (float)nd.Pos.Z), 0.22f, col);
            }
        }
    }
}
