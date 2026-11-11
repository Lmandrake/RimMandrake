// Complete production DrawAll/DropMeshes/DestroyMeshes/DestroyOver/DrawCrossShadow/RebuildCrossShadow
// and BuildCrossMesh are extracted at each build. The real HoseCrossShadows, geometry, carry clipping, key memo and draw
// rotation compile directly. Boundaries below substitute lay discovery, ranks, rendering, materials,
// settings and clock. RibbonInto records mesh submissions, not pixels. No engine/live look claim.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.Shared.Slack;
using RimMandrake.FlowWorks.Hose;

namespace RimMandrake.FlowWorks.Machinery
{
    internal static class RM_UnderCouplers { public static void ResetFrame() { } }
}
namespace RimMandrake.FlowWorks.SelfTest.HoseShadowHarness
{
    namespace UnityEngine
    {
        internal static class Object { public static void Destroy(Mesh m) { m.Destroyed = true; } }
    }
    internal sealed class Mesh {
        public bool Destroyed; public string name;
        public void SetVertices(List<Vector3> v) { }
        public void SetUVs(int i, List<Vector2> v) { }
        public void SetTriangles(List<int> v, int i) { }
        public void RecalculateBounds() { }
    }
    internal struct Vector3 { }
    internal struct Vector2 { }
    internal struct Color { }
    internal struct Matrix4x4 { public static Matrix4x4 identity => new(); }
    internal static class Graphics
    {
        public static void DrawMesh(Mesh m, Matrix4x4 matrix, object material, int layer)
        { if (m.Destroyed) throw new Exception("drawing destroyed mesh"); }
    }
    internal enum CameraZoomRange { Near, Far }
    internal static class Find
    {
        internal sealed class Camera { public CameraZoomRange CurrentZoom; }
        internal sealed class Clock { public int TicksGame = 1000; }
        public static Camera CameraDriver = new();
        public static Clock TickManager = new();
    }
    internal static class Time { public static int frameCount; }
    internal static class RM_HoseSettings
    {
        public static double plumpAmount = 0.5;
        public static HoseTuning Tuning() => new();
    }
    internal sealed class HoseLookMats
    {
        public object Flat(float e) => null;
        public object Plump(float e, Color tint) => null;
    }
    internal static class HoseMaterials
    {
        public static HoseLookMats For(CompHoseReel r) => new();
        public static object Shadow(float alpha) => null;
    }
    internal sealed class CompHoseReel
    {
        internal sealed class Parent { public int thingIDNumber; }
        public Parent parent = new();
        public HoseCarryState carry = HoseCarryState.Laid;
        public List<Cell> trail = new();
        public bool laid = true;
        public string layKey = "fixture";
        public HoseDrawKeyMemo drawKeyMemo;
        public double wound;
        public HoseLay Lay;
        public int Rank;
    }
    internal partial class Component
    {
        private sealed class Cached
        {
            public string key;
            public Mesh flat, plump, shadow, crossShadow;
            public List<Mesh> overMeshes = new();
            public List<V2> pts, rp;
            public int serial;
            public ulong crossKey;
            public bool crossKeyed;
            public List<double[]> crossSpans;
        }
        private sealed class StubCache { public Mesh mesh; }
        private sealed class DrawnFitting { }
        private sealed class MateInfo { public string key; }
        private readonly List<CompHoseReel> reels = new();
        private readonly Dictionary<CompHoseReel, Cached> meshes = new();
        private readonly Dictionary<CompHoseReel, StubCache> stubMeshes = new();
        private readonly Dictionary<CompHoseReel, Dictionary<string, DrawnFitting>> drawnFittings = new();
        private readonly Dictionary<CompHoseReel, int> carryCache = new(), mateKept = new();
        private readonly Dictionary<CompHoseReel, string> lastDraw = new();
        private readonly Dictionary<CompHoseReel, double> lastDrawnLen = new();
        private readonly List<Mesh> frameMeshes = new(), oldFrame = new();
        private readonly List<int> jointScratch = new();
        private readonly HoseCrossShadows crossIndex = new();
        private readonly HoseDrawRotation drawOrder = new();
        private readonly HoseMateEndQueue mateEnds = new();
        private Func<int, int> rankOfId;
        private int cachedSerial;
        private static bool LegacyFrame;
        private bool lastFar;
        private int lastWrapDraws, lastFeedDraws, lastFeedPipeDraws, lastReelEndHidden, lastRelayCouplings,
            lastCarryDraws, lastClipDraws, lastGhostDraws, lastPortCouplings, lastDepthDraws, lastPortStubs,
            lastMateJoins, lastOverDraws, lastCrossShadowDraws, lastDeferredRebuilds, lastDeferredCross, lastDeferredMates;
        private static int DeferredRebuildsTotal, DeferredCrossTotal;
        private long rebuildSpent, crossSpent;
        private const double RebuildBudgetMs = 8, CrossBudgetMs = 4, CrossShadowMargin = 0.25;
        private static readonly double TicksPerMs = System.Diagnostics.Stopwatch.Frequency / 1000.0;
        private static ulong CrossMix(ulong h, long v) => (h ^ unchecked((ulong)v)) * 1099511628211UL;
        private int RankOf(CompHoseReel r) => r.Rank;
        private int RankOfId(int id) => reels.Single(r => r.parent.thingIDNumber == id).Rank;
        // Boundary: pose input is independently fixed; no stand-in implements any cache/drop/shadow decisions.
        private HoseLay EnsureLay(CompHoseReel r, bool draw) => r.Lay;
        private struct PoseInfo { public double Blend, Eased, Visible; public bool Wobbling; public int SinceChange; }
        private static PoseInfo Info(CompHoseReel r) => new() { Blend = 1, Eased = 1, Visible = 0.5 };
        private static bool PortEnd(CompHoseReel r, out V2 at, out V2 axis) { at = axis = default; return false; }
        private MateInfo MateFor(CompHoseReel r) => null;
        private static bool MateEndIsCopy(CompHoseReel r, MateInfo mi) => false;
        private static List<V2> Mated(CompHoseReel r, MateInfo mi, List<V2> pts) => pts;
        private void MatedLater(CompHoseReel r, MateInfo mi, HoseLay lay, Cached c, int i, ref string key, ref List<V2> pts) { }
        private HoseMath.Layering Layered() => new();
        private static List<int> JointsBefore(List<int> joints, int cut) => joints.FindAll(j => j < cut);
        private static double TotalOf(CompHoseReel r) => 10;
        private static double OutletTrim(CompHoseReel r, float vis) => 0;
        private static List<V2> Offset(List<V2> pts, V2 off) => pts.Select(p => new V2(p.X + off.X, p.Z + off.Z)).ToList();
        private static Mesh Ribbon(List<V2> pts, float width, float y, double phase) => pts.Count > 1 ? new() : null;
        private static Color Tint(CompHoseReel r) => new();
        private static void DepthPass(Mesh m, Matrix4x4 matrix, object material) { }
        private void DrawFeed(CompHoseReel r, float y) { }
        private void DrawCarrying(CompHoseReel r, float y, bool far) { lastCarryDraws++; }
        private void DropCarryCache(CompHoseReel r) => carryCache.Remove(r);
        private void DrawOverBuildings(Cached c, HoseLookMats hm, Color tint, float vis, float e, int rank) { }
        private void DrawEnds(CompHoseReel r, HoseLookMats hm, List<int> joints, List<V2> pts, float vis, float y, bool drawn) { }
        private void DrawGhosts(float y) { }
        private const double CrossShadowOffset = 0.10;
        private const float CrossShadowWiden = 1.15f;
        private static int CrossBuilds;
        private static readonly List<Vector3> RibbonV = new();
        private static readonly List<Vector2> RibbonUv = new();
        private static readonly List<int> RibbonTr = new();
        private static void RibbonInto(List<V2> pts, float width, float y, double phase, List<Vector3> v, List<Vector2> uv, List<int> tr)
        { if (pts.Count >= 2) { v.Add(new()); uv.Add(new()); tr.Add(0); } }

        private static List<V2> Line(double x0, double z0, double x1, double z1) => new() { new(x0,z0), new(x1,z1) };
        private CompHoseReel Add(int id, int rank, List<V2> pts)
        {
            var r = new CompHoseReel { Rank = rank, Lay = new HoseLay { Ok = true, Flat = pts, Plump = pts, Joints = new() } };
            r.parent.thingIDNumber = id;
            reels.Add(r);
            return r;
        }
        private static void Assert(bool ok, string why) { if (!ok) throw new Exception(why); }
        private void Frame() { Time.frameCount++; DrawAll(); }
        private void Shadow(CompHoseReel r) => DrawCrossShadow(r, meshes[r], 0.5f, 1, 0, r.Rank);
        private bool HasShadow(CompHoseReel r) => meshes[r].crossShadow != null && meshes[r].crossSpans?.Count > 0;
        private static Component Fixture(bool upperFirst, out CompHoseReel gone, out CompHoseReel active, out CompHoseReel upper)
        {
            LegacyFrame = false;
            var c = new Component();
            gone = c.Add(10, 0, Line(3,-5,3,5));
            active = c.Add(11, 1, Line(8,-5,8,5));
            upper = c.Add(12, 2, Line(0,0,12,0));
            if (upperFirst) { c.reels.Remove(upper); c.reels.Insert(0,upper); }
            c.Frame(); c.Frame(); // both enumeration orders have populated the production cache/index
            Assert(c.HasShadow(upper) && c.meshes[upper].crossSpans.Count == 2, "fixture: two distinct real lower crossings");
            Assert(!c.crossIndex.Pending(upper.parent.thingIDNumber, upper.Rank), "fixture: upper is clean/keyed");
            return c;
        }
        private static void Transition(int mode, bool upperFirst)
        {
            var c = Fixture(upperFirst, out var gone, out var active, out var upper);
            Cached old = c.meshes[gone];
            Mesh removedFlat = old.plump, upperBefore = c.meshes[upper].crossShadow;
            var stub = new Mesh(); c.stubMeshes[gone] = new StubCache { mesh = stub };
            if (mode == 0) { gone.carry = HoseCarryState.Carrying; gone.trail.Add(new Cell(3,1)); gone.laid = false; gone.Lay = null; }
            if (mode == 1) { gone.carry = HoseCarryState.Stored; gone.laid = false; gone.Lay = null; }
            if (mode == 2) { gone.carry = HoseCarryState.Retracting; gone.wound = 5; }
            c.Frame();
            Assert(!c.meshes.ContainsKey(gone) && !c.crossIndex.TryGet(10,out _), "transition removes full-route mesh and strand");
            Assert(removedFlat.Destroyed && stub.Destroyed && !c.stubMeshes.ContainsKey(gone), "transition destroys old rendered meshes and stub");
            Assert(c.crossIndex.TryGet(11,out _) && c.meshes.ContainsKey(active), "active lower remains cached/indexed");
            // An upper visited first may draw the old crossing once; the dropped lower marks it pending.
            // A budgeted upper may also keep its prior mesh. Neither case loses dirty state.
            if (upperFirst) Assert(c.meshes[upper].crossSpans.Count == 2 && c.crossIndex.Pending(12,2), "upper-first visit retains one stale frame and pending dirt");
            c.crossSpent = 0; c.Shadow(upper);
            Assert(c.HasShadow(upper) && c.meshes[upper].crossSpans.Count == 1, "former crossing removed; active crossing survives");
            var oracle = HoseOverDraw.CrossSpans(c.meshes[upper].rp, new List<IList<V2>> { c.meshes[active].rp }, 0.5, CrossShadowMargin);
            Assert(HoseCrossShadowChecks.SpanDiff(oracle, c.meshes[upper].crossSpans) == "", "spans equal independent all-pairs oracle");
            Assert(upperBefore.Destroyed && !c.crossIndex.Pending(12, upper.Rank), "dependent old mesh destroyed and pending consumed");
            c.Frame(); Assert(c.HasShadow(upper) && c.meshes[upper].crossSpans.Count == 1, "next frame keeps only active crossing");
            if (mode == 0) Assert(c.lastCarryDraws == 1,"carried draw path reached");
            if (mode == 1) Assert(c.lastDraw[gone] == "none","null-lay path reached");
            if (mode == 2) Assert(c.lastClipDraws == 1,"retraction clipping path reached");
        }
        public static void Run(Action<string,Action> Case)
        {
            foreach (int m in new[] { 0,1,2 }) foreach (bool first in new[] { false,true })
            {
                int mode=m; bool order=first;
                Case($"HS_transition_{mode}_upperFirst_{order}", () => Transition(mode,order));
            }
            Case("HS_drop_budget_dirty_then_drain_and_idempotence", () =>
            {
                var c=Fixture(false,out var gone,out var active,out var upper);
                Mesh previous=c.meshes[upper].crossShadow;
                c.DropMeshes(gone);
                Assert(c.crossIndex.Pending(12,2),"drop invalidates clean dependent upper");
                c.crossSpent=long.MaxValue; c.Shadow(upper);
                Assert(c.crossIndex.Pending(12,2) && ReferenceEquals(previous,c.meshes[upper].crossShadow) && c.lastDeferredCross>0,"budget preserves pending dirt and old mesh");
                c.crossSpent=0; c.Shadow(upper);
                Assert(c.meshes[upper].crossSpans.Count==1 && previous.Destroyed,"later budget removes old crossing and keeps active one");
                c.DropMeshes(gone); c.crossSpent=0; c.Shadow(upper);
                Assert(c.HasShadow(upper) && !c.crossIndex.Pending(12,2),"repeat drop is harmless");
                c.DropMeshes(active); c.crossSpent=0; c.Shadow(upper);
                Assert(!c.HasShadow(upper) && c.meshes[upper].crossSpans.Count==0,"last lower drop removes dependent shadow mesh");
            });
            Case("HS_rank_toggle_and_same_key_relay", () =>
            {
                var c=Fixture(false,out var gone,out var active,out var upper);
                gone.Rank=3; c.crossIndex.RankMoved(10); c.crossSpent=0; c.Shadow(upper);
                Assert(c.meshes[upper].crossSpans.Count==1,"higher ranked crossing contributes no shadow");
                gone.Rank=0; c.crossIndex.RankMoved(10); c.crossSpent=0; c.Shadow(upper);
                Assert(c.meshes[upper].crossSpans.Count==2,"lower rank restored contributes shadow");
                LegacyFrame=true; c.Shadow(upper);
                Assert(c.meshes[upper].crossSpans.Count==2,"legacy positive comparison");
                c.DropMeshes(gone); gone.Lay=null; gone.laid=false; LegacyFrame=false; c.crossSpent=0; c.Shadow(upper);
                Assert(c.meshes[upper].crossSpans.Count==1,"drop while legacy selected still invalidates default index");
                active.Rank=0; upper.Rank=1; c.crossIndex.RankMoved(11); c.crossIndex.RankMoved(12); c.crossSpent=0; c.Shadow(upper);
                Assert(c.HasShadow(upper) && c.meshes[upper].crossSpans.Count==1,"drop plus rank compaction keeps active crossing");
                active.Rank=2; c.crossIndex.RankMoved(11); c.crossSpent=0; c.Shadow(upper);
                Assert(!c.HasShadow(upper),"remaining hose moved above upper contributes no shadow");
                active.Rank=0; c.crossIndex.RankMoved(11); c.crossSpent=0; c.Shadow(upper);
                c.Frame(); string key=c.meshes[active].key;
                c.DropMeshes(active); active.Lay=new HoseLay {Ok=true,Flat=Line(8,8,8,15),Plump=Line(8,8,8,15),Joints=new()};
                c.Frame(); c.crossSpent=0; c.Shadow(upper);
                Assert(c.meshes[active].key==key && !c.HasShadow(upper),"same-key new route invalidates old crossing");
                c.DropMeshes(active); active.Lay=new HoseLay {Ok=true,Flat=Line(8,-5,8,5),Plump=Line(8,-5,8,5),Joints=new()};
                c.Frame(); c.crossSpent=0; c.Shadow(upper);
                Assert(c.HasShadow(upper) && c.meshes[upper].crossSpans.Count==1,"drop and re-lay restores a real crossing");
                LegacyFrame=false;
            });
            Case("HS_legacy_retains_original_carry_comparison", () =>
            {
                var c=Fixture(false,out var gone,out var active,out var upper);
                LegacyFrame=true; gone.carry=HoseCarryState.Carrying; gone.trail.Add(new Cell(3,1)); gone.Lay=null;
                c.Frame();
                Assert(c.meshes.ContainsKey(gone) && c.meshes[upper].crossSpans.Count==2,"legacy deliberately preserves old carry route");
                LegacyFrame=false; c.Frame(); c.crossSpent=0; c.Shadow(upper);
                Assert(!c.meshes.ContainsKey(gone) && c.meshes[upper].crossSpans.Count==1,"shipping default drops route after toggle");
            });
        }
    }
}
