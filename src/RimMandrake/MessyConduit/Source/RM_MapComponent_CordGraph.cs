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
    /// Runtime-only owner of a map's cord graph (design §8.1): nothing here is saved -- not even the
    /// component's own entry (Patch_Map_ExposeComponents_SkipCordGraph, below), so a save loads clean
    /// without the mod; the whole graph and every polyline is rebuilt from the conduit grid on load and
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
            // Publish BEFORE dirtying: a throw below must never leave the map with no cords.
            Dictionary<IntVec2, List<LaidPiece>> prevBy = bySection;
            pieces = next;
            bySection = nextBy;
            // dirty every section whose owned set changed (not just the regenerating one)
            if (Current.ProgramState == ProgramState.Playing)
            {
                var keys = new HashSet<IntVec2>(nextBy.Keys);
                keys.UnionWith(prevBy.Keys);
                foreach (IntVec2 s in keys)
                    if (Sig(prevBy, s) != Sig(nextBy, s)) DirtySection(s);
            }
        }

        /// <summary>
        /// MapDrawer.RegenerateEverythingNow (map load / FinalizeInit) creates its Section objects one by one
        /// INSIDE the regenerate loop, so while the first sections regenerate the later array slots are still
        /// null and MapMeshDirty -> SectionAt(..).dirtyFlags throws (live 2026-10-02: every loaded save drew no
        /// cords). A section not created yet regenerates in that same loop anyway, so skipping it is correct.
        /// </summary>
        private void DirtySection(IntVec2 s)
        {
            var loc = new IntVec3(s.x * Section.Size, 0, s.z * Section.Size);
            if (!loc.InBounds(map)) return;
            Section sec;
            try { sec = map.mapDrawer.SectionAt(loc); }
            catch (NullReferenceException) { return; }       // the drawer's section array itself not built yet
            if (sec == null) return;
            map.mapDrawer.MapMeshDirty(loc, MessyConduitDefOf.RM_MessyCords);
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
        public static int LastGlowDraws;

        /// <summary>The live half of the break readout, every frame and while paused: a flickering
        /// glow at each live tip (the sparks are thrown flecks and only fly while time runs).</summary>
        private void DrawLiveGlow()
        {
            LastGlowDraws = 0;
            if (!MessyConduitSettings.enabled || !MessyConduitSettings.breakReadout || MessyConduitSettings.sparkIntensity <= 0.01f) return;
            if (Find.CurrentMap != map || CordMaterials.LiveGlow == null || RimWorld.Planet.WorldRendererUtility.WorldSelected) return;
            float t = Time.realtimeSinceStartup;
            float y = AltitudeLayer.MoteLow.AltitudeFor();
            int n = 0;
            foreach (LaidPiece p in pieces)
                foreach (CordEnd e in p.Ends)
                {
                    if (!liveEnds.TryGetValue(e.NetCell, out bool live) || !live) continue;
                    if (++n > MaxSparkingEnds) return;
                    int h = (e.NetCell.X * 73856093) ^ (e.NetCell.Z * 19349663);
                    float f = Mathf.PerlinNoise(t * 9f, (h & 0xff) * 0.37f);
                    float size = (0.38f + 0.42f * f * f) * Mathf.Min(1.5f, MessyConduitSettings.sparkIntensity);
                    var pos = new Vector3((float)e.Tip.X, y, (float)e.Tip.Z);
                    Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(pos, Quaternion.identity, new Vector3(size, 1f, size)), CordMaterials.LiveGlow, 0);
                    LastGlowDraws++;
                }
        }

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
            DrawLiveGlow();
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

    /// <summary>
    /// Keeps the cord graph out of the save (walk M9). Map.ExposeComponents writes every MapComponent as
    /// &lt;li Class="..."/&gt; even with no ExposeData, and loading that save without the mod logs two red errors
    /// ("Could not find class RimMandrake.MessyConduit.RM_MapComponent_CordGraph" + "Can't load abstract class
    /// Verse.MapComponent"; measured live 2026-10-02). While SAVING, the component is taken out of the list and
    /// put back afterwards at its old index; FillComponents (end of ExposeComponents) re-adds a fresh instance,
    /// which the finalizer drops again. On load it is simply absent and FillComponents creates it.
    /// </summary>
    [HarmonyLib.HarmonyPatch(typeof(Map), "ExposeComponents")]
    internal static class Patch_Map_ExposeComponents_SkipCordGraph
    {
        internal sealed class Held { public int Index; public MapComponent Comp; }

        private static void Prefix(Map __instance, out Held __state)
        {
            __state = null;
            if (Scribe.mode != LoadSaveMode.Saving) return;
            List<MapComponent> list = __instance.components;
            int i = list.FindIndex(c => c is RM_MapComponent_CordGraph);
            if (i < 0) return;
            __state = new Held { Index = i, Comp = list[i] };
            list.RemoveAt(i);
        }

        private static Exception Finalizer(Map __instance, Exception __exception, Held __state)
        {
            if (__state != null)
            {
                List<MapComponent> list = __instance.components;
                list.RemoveAll(c => c is RM_MapComponent_CordGraph);
                list.Insert(Math.Min(__state.Index, list.Count), __state.Comp);
            }
            return __exception;
        }
    }
}
