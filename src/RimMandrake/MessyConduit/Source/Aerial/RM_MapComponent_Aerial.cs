using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.MessyConduit.Aerial
{
    /// <summary>
    /// Runtime side of the aerial lines on one map (design 2.2-2.6). Saves NOTHING (links live on the anchors);
    /// kept out of the save by Patch_Map_ExposeComponents_SkipAerial, like the cord component.
    ///  * auto-link queue (a new anchor links on the tick after it spawns, once its faction is set)
    ///  * the 250-tick watchdog: every UP span's two ends must share one non-null PowerNet, else both are re-seeded and
    ///    netRepairs counts it (a non-zero netRepairs in a clean test is a defect signal, not a success)
    ///  * roof sweep: a roof over an anchor cuts its spans (coiled, no sparks)
    ///  * fallen cords: live/dead poll, sparks and the per-frame glow at live tips (look only: no shock)
    ///  * per-frame span drawing from cached meshes; CPU sway deforms only spans in view
    /// </summary>
    public class RM_MapComponent_Aerial : MapComponent
    {
        private readonly HashSet<CompAerialAnchor> anchors = new HashSet<CompAerialAnchor>();
        private readonly HashSet<CompPowerTap> taps = new HashSet<CompPowerTap>();
        private readonly List<CompAerialAnchor> pendingAuto = new List<CompAerialAnchor>();
        private readonly Dictionary<long, SpanMesh> meshes = new Dictionary<long, SpanMesh>();
        private readonly Dictionary<int, bool> anchorLive = new Dictionary<int, bool>();
        private readonly Dictionary<FallenCord, FallenLay> lays = new Dictionary<FallenCord, FallenLay>();

        public int netRepairs, roofCuts, explosionCuts, autoLinks, watchdogRuns;
        public int lastSwayDraws, lastSpanDraws, lastTopDraws, lastGlowDraws, lastDropDraws;
        public string lastSwayReason = "";

        public RM_MapComponent_Aerial(Map map) : base(map) { }

        public IEnumerable<CompAerialAnchor> Anchors => anchors.Where(a => a.Spawned);
        public IEnumerable<CompPowerTap> Taps => taps.Where(t => t.parent.Spawned);

        public void Register(CompAerialAnchor a) { anchors.Add(a); DirtyGround(a); }
        public void Deregister(CompAerialAnchor a, Map onMap = null)
        {
            anchors.Remove(a);
            pendingAuto.Remove(a);
            anchorLive.Remove(a.thingIDNumber);
            DirtyCell(a.Position);
        }
        public void Register(CompPowerTap t) => taps.Add(t);
        public void Deregister(CompPowerTap t) => taps.Remove(t);
        public void QueueAutoLink(CompAerialAnchor a) { if (!pendingAuto.Contains(a)) pendingAuto.Add(a); }

        public void Notify_SpansChanged() => meshes.Clear();

        public void Notify_SettingsChanged()
        {
            meshes.Clear();
            foreach (CompAerialAnchor a in Anchors) DirtyGround(a);
        }

        /// <summary>Re-print the ground layer (span shadows, fallen cords) of the section holding this anchor.</summary>
        public void DirtyGround(CompAerialAnchor a)
        {
            if (a != null) DirtyCell(a.Position);
        }

        private void DirtyCell(IntVec3 c)
        {
            if (Current.ProgramState != ProgramState.Playing) return;
            if (!c.InBounds(map)) return;
            lays.Clear();
            foreach (var kv in drops.Values) if (kv.Value != null) UnityEngine.Object.Destroy(kv.Value);
            drops.Clear();
            try { if (map.mapDrawer.SectionAt(c) == null) return; }
            catch (NullReferenceException) { return; }              // section array not built yet (map load)
            map.mapDrawer.MapMeshDirty(c, AerialDefOf.RM_AerialLines);
        }

        // ------------------------------------------------------------------ ticks
        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (pendingAuto.Count > 0) ProcessAutoLinks();
            if (now % 250 == (map.uniqueID * 7 + 31) % 250)
            {
                Watchdog();
                RoofSweep();
                PollFallen();
            }
            Sparks(now);
        }

        private void ProcessAutoLinks()
        {
            foreach (CompAerialAnchor a in pendingAuto.ToList())
            {
                if (!a.Spawned) { pendingAuto.Remove(a); continue; }
                if (a.Faction == null) continue;                       // build_batch may set the faction a moment later
                pendingAuto.Remove(a);
                if (!AerialSettings.enabled || !AerialSettings.autoLink) continue;
                var others = Anchors.Where(o => o != a).ToList();
                int pick = AerialMath.AutoLinkPick(a.Info(), others.Select(o => o.Info()).ToList(), AerialSettings.Range);
                if (pick < 0) continue;
                if (CompAerialAnchor.TryLink(a, others.First(o => o.thingIDNumber == pick).parent) == LinkVerdict.Ok) autoLinks++;
            }
        }

        public static int NetId(PowerNet n) => n == null ? -1 : System.Runtime.CompilerServices.RuntimeHelpers.GetHashCode(n) & 0x7fffffff;

        /// <summary>
        /// The net a transmitter REALLY belongs to, or null. LEARNED live 2026-10-02 (M14 control): PowerNetManager.
        /// DeletePowerNet drops a net from the manager and the grid but never clears CompPower.transNet, so after the
        /// despawn gap both stranded sides still point at the SAME deleted net -- "same non-null net" reads healthy
        /// while no power flows (the net is no longer ticked). Only a net still registered with the manager counts.
        /// </summary>
        public static PowerNet Registered(Map map, PowerNet n) =>
            n != null && map != null && map.powerNetManager.AllNetsListForReading.Contains(n) ? n : null;

        public static PowerNet NetOf(CompAerialAnchor a) => a?.PowerComp == null || !a.Spawned ? null : Registered(a.Map, a.PowerComp.PowerNet);

        /// <summary>Design 2.2.4. Spans changed within the last 2 ticks are skipped: their nets are rebuilt on the next
        /// MapPreTick and reading them now would count a repair that is not one.</summary>
        public int Watchdog()
        {
            watchdogRuns++;
            int now = Find.TickManager.TicksGame;
            var reads = new List<SpanNetRead>();
            var pairs = new List<(CompAerialAnchor, CompAerialAnchor)>();
            foreach (CompAerialAnchor a in Anchors)
                foreach (SpanLink l in a.links)
                {
                    if (l.other == null || !l.other.Spawned || !AerialMath.Owns(a.thingIDNumber, l.other.thingIDNumber)) continue;
                    if (l.changedTick >= now - 2) continue;
                    reads.Add(new SpanNetRead { Span = pairs.Count, State = l.state, NetA = NetId(NetOf(a)), NetB = NetId(NetOf(l.other)) });
                    pairs.Add((a, l.other));
                }
            List<int> rep = AerialMath.WatchdogRepairs(reads);
            foreach (int i in rep)
            {
                netRepairs++;
                CompAerialAnchor.Reseed(pairs[i].Item1);
                CompAerialAnchor.Reseed(pairs[i].Item2);
            }
            return rep.Count;
        }

        private void RoofSweep()
        {
            foreach (CompAerialAnchor a in Anchors.ToList())
            {
                if (!map.roofGrid.Roofed(a.Position)) continue;
                var up = a.links.Where(l => l.state == SpanState.Up && l.other != null).Select(l => l.other).ToList();
                if (up.Count == 0) continue;
                foreach (CompAerialAnchor o in up)
                    if (CompAerialAnchor.Cut(a, o, 0.5f, false)) roofCuts++;
                if (a.Faction == Faction.OfPlayer)
                    Messages.Message(a.LabelCap + ": a roof was built over it, so its overhead wires were taken down.", a.parent, MessageTypeDefOf.NegativeEvent, false);
            }
        }

        public bool AnchorLive(CompAerialAnchor a) => NetOf(a) is PowerNet n && n.HasActivePowerSource;

        public int PollFallen()
        {
            int flips = 0;
            foreach (CompAerialAnchor a in Anchors)
            {
                if (a.fallen.Count == 0) continue;
                bool live = AnchorLive(a);
                if (anchorLive.TryGetValue(a.thingIDNumber, out bool was) && was == live) continue;
                anchorLive[a.thingIDNumber] = live;
                flips++;
                DirtyGround(a);
            }
            return flips;
        }

        public bool? FallenLiveCached(CompAerialAnchor a) => anchorLive.TryGetValue(a.thingIDNumber, out bool v) ? v : (bool?)null;

        /// <summary>The fallen / cut wire of <paramref name="f"/>: ONE cable from the anchor's middle insulator down to the
        /// break point on the ground (B21); Tip is the break. Cached until the ground or the look changes.</summary>
        public FallenLay Lay(CompAerialAnchor a, FallenCord f)
        {
            if (lays.TryGetValue(f, out FallenLay l)) return l;
            Vector3 b = a.BasePoint, t = a.AttachPoint;
            double[] ins = AerialMaterials.InsulatorsFor(a);
            PathGrid pg = map.pathing.Normal.pathGrid;
            IntVec3 home = a.Position;
            Func<int, int, bool> walk = (x, z) =>
            {
                var c = new IntVec3(x, 0, z);
                if (!c.InBounds(map)) return false;
                return c == home || pg.WalkableFast(c);
            };
            l = AerialMath.LayFallen(new P2(t.x + ins[ins.Length / 2], t.z), new P2(b.x, b.z), new P2(f.toward.x + 0.5, f.toward.z + 0.5), f.length, f.seed, walk);
            lays[f] = l;
            return l;
        }

        private const int MaxSparkingEnds = 24;

        private void Sparks(int tick)
        {
            if (!AerialSettings.enabled || !MessyConduitSettings.breakReadout || MessyConduitSettings.sparkIntensity <= 0.01f) return;
            int n = 0;
            foreach (CompAerialAnchor a in Anchors)
            {
                if (a.fallen.Count == 0 || !(FallenLiveCached(a) ?? false)) continue;
                foreach (FallenCord f in a.fallen)
                {
                    if (++n > MaxSparkingEnds) return;
                    int period = Mathf.Max(12, Mathf.RoundToInt(60 / MessyConduitSettings.sparkIntensity));
                    if ((tick + (f.seed & 0x7fff)) % period != 0) continue;
                    FallenLay l = Lay(a, f);
                    var at = new Vector3((float)l.Tip.X, AltitudeLayer.MoteOverhead.AltitudeFor(), (float)l.Tip.Z);
                    FleckMaker.ThrowMicroSparks(at, map);
                    if (((tick / period + f.seed) & 3) == 0) FleckMaker.ThrowLightningGlow(at, map, 0.5f);
                }
            }
        }

        // ------------------------------------------------------------------ explosions (design 2.6)
        public int Notify_Explosion(IntVec3 center, float radius, float damage)
        {
            if (!AerialSettings.explosionsCut || damage <= 0f) return 0;
            int cuts = 0;
            var c = new P2(center.x + 0.5, center.z + 0.5);
            foreach (CompAerialAnchor a in Anchors.ToList())
                foreach (SpanLink l in a.links.ToList())
                {
                    if (l.state != SpanState.Up || l.other == null || !AerialMath.Owns(a.thingIDNumber, l.other.thingIDNumber)) continue;
                    var pa = new P2(a.BasePoint.x, a.BasePoint.z);
                    var pb = new P2(l.other.BasePoint.x, l.other.BasePoint.z);
                    if (!AerialMath.SpanHit(pa, pb, c, radius)) continue;
                    SpanLink back = l.other.LinkTo(a);
                    l.hp -= damage;
                    if (back != null) back.hp = l.hp;
                    if (l.hp > 0f) continue;
                    if (CompAerialAnchor.Cut(a, l.other, (float)AerialMath.ClosestT(pa, pb, c), true)) { cuts++; explosionCuts++; }
                }
            return cuts;
        }

        // ------------------------------------------------------------------ drawing
        public override void MapComponentUpdate()
        {
            AerialProbe.Service(map, this);
            lastSpanDraws = lastSwayDraws = lastTopDraws = lastGlowDraws = lastDropDraws = 0;
            if (!AerialSettings.enabled || Find.CurrentMap != map || RimWorld.Planet.WorldRendererUtility.WorldSelected) return;
            CellRect view = Find.CameraDriver.CurrentViewRect.ExpandedBy(3);
            float wind = map.windManager.WindSpeed;
            bool sway = WireSway.Active(map, out lastSwayReason);
            float time = Find.TickManager.TicksGame / 60f;
            float spanY = SpanAltitude;
            foreach (CompAerialAnchor a in Anchors)
            {
                Material top = AerialMaterials.Top(AerialMaterials.TopPathFor(a.def) ?? a.Ext.topTexPath);
                if (top != null && view.Contains(a.Position))
                {
                    var pos = new Vector3(a.Position.x + 0.5f, TopAltitude, a.Position.z + 0.5f + a.Ext.topOffsetZ);
                    Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(pos, Quaternion.identity, new Vector3(top.mainTexture != null ? top.mainTexture.width / 128f : 1f, 1f, 1f)), top, 0);
                    lastTopDraws++;
                }
                foreach (SpanLink l in a.links)
                {
                    if (l.state != SpanState.Up || l.other == null || !l.other.Spawned || !AerialMath.Owns(a.thingIDNumber, l.other.thingIDNumber)) continue;
                    SpanMesh m = MeshFor(a, l.other, spanY);
                    if (m == null || !m.rect.Overlaps(view)) continue;
                    if (sway) { m.Sway(time, wind, 0.12f * AerialSettings.swayStrength); lastSwayDraws++; }
                    else m.Rest();
                    Graphics.DrawMesh(m.mesh, Matrix4x4.identity, AerialMaterials.Span, 0);
                    lastSpanDraws++;
                }
                // B11/B21: a cut / orphaned wire is ONE cable from the insulator down to the break on the ground, in the
                // span's own material and width (the ground layer prints only the frayed end at its tip)
                if (a.fallen.Count > 0 && AerialMaterials.Span != null)
                    foreach (FallenCord f in a.fallen)
                    {
                        Mesh dm = WireMesh(a, f, spanY);
                        if (dm == null || !dm.bounds.Intersects(new Bounds(view.CenterVector3, new Vector3(view.Width, 100f, view.Height)))) continue;
                        Graphics.DrawMesh(dm, Matrix4x4.identity, AerialMaterials.Span, 0);
                        lastDropDraws++;
                    }
            }
            DrawFallenGlow();
        }

        public static float SpanAltitude => AltitudeLayer.PawnState.AltitudeFor(5f);
        public static float TopAltitude => AltitudeLayer.PawnState.AltitudeFor(4f);

        private void DrawFallenGlow()
        {
            if (!MessyConduitSettings.breakReadout || MessyConduitSettings.sparkIntensity <= 0.01f || AerialMaterials.Glow == null) return;
            float t = Time.realtimeSinceStartup;
            float y = AltitudeLayer.MoteLow.AltitudeFor();
            int n = 0;
            foreach (CompAerialAnchor a in Anchors)
            {
                if (a.fallen.Count == 0 || !(FallenLiveCached(a) ?? false)) continue;
                foreach (FallenCord f in a.fallen)
                {
                    if (++n > MaxSparkingEnds) return;
                    FallenLay l = Lay(a, f);
                    float k = Mathf.PerlinNoise(t * 9f, (f.seed & 0xff) * 0.37f);
                    float size = (0.38f + 0.42f * k * k) * Mathf.Min(1.5f, MessyConduitSettings.sparkIntensity);
                    Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(new Vector3((float)l.Tip.X, y, (float)l.Tip.Z), Quaternion.identity, new Vector3(size, 1f, size)), AerialMaterials.Glow, 0);
                    lastGlowDraws++;
                }
            }
        }

        public int SpanMeshCount => meshes.Count;

        private readonly Dictionary<FallenCord, KeyValuePair<int, Mesh>> drops = new Dictionary<FallenCord, KeyValuePair<int, Mesh>>();

        /// <summary>The fallen wire's ribbon mesh: exactly <see cref="Lay"/>'s polyline at the span width (cached; rebuilt
        /// when the anchor moves or the look's width changes).</summary>
        public Mesh WireMesh(CompAerialAnchor a, FallenCord f, float y)
        {
            int sig = Gen.HashCombineInt(a.Position.GetHashCode(), Mathf.RoundToInt(AerialMaterials.SpanWidth * 1000f));
            sig = Gen.HashCombineInt(sig, Mathf.RoundToInt(a.Ext.attachZ * 1000f));
            if (drops.TryGetValue(f, out var kv) && kv.Key == sig) return kv.Value;
            List<P2> pts = Lay(a, f).Pts;
            if (pts.Count < 2) return null;
            var verts = new List<Vector3>(); var uvs = new List<Vector2>(); var tris = new List<int>();
            float w = AerialMaterials.SpanWidth;
            double u = 0;
            for (int i = 0; i < pts.Count; i++)
            {
                P2 prev = i > 0 ? pts[i - 1] : pts[i], next = i < pts.Count - 1 ? pts[i + 1] : pts[i];
                double tx = next.X - prev.X, tz = next.Z - prev.Z, tl = Math.Sqrt(tx * tx + tz * tz);
                if (tl < 1e-9) { tx = 0; tz = -1; tl = 1; }
                double nx = -tz / tl * w / 2, nz = tx / tl * w / 2;
                if (i > 0) u += P2.Dist(pts[i - 1], pts[i]) / (w * 4);
                verts.Add(new Vector3((float)(pts[i].X + nx), y, (float)(pts[i].Z + nz)));
                verts.Add(new Vector3((float)(pts[i].X - nx), y, (float)(pts[i].Z - nz)));
                uvs.Add(new Vector2((float)u, 1f)); uvs.Add(new Vector2((float)u, 0f));
                if (i == 0) continue;
                int q = 2 * (i - 1);
                tris.Add(q); tris.Add(q + 2); tris.Add(q + 3);
                tris.Add(q); tris.Add(q + 3); tris.Add(q + 1);
            }
            var m = new Mesh { name = "RM_AerialFallenWire" };
            m.SetVertices(verts); m.SetUVs(0, uvs); m.SetTriangles(tris, 0); m.RecalculateBounds();
            if (drops.TryGetValue(f, out var old) && old.Value != null) UnityEngine.Object.Destroy(old.Value);
            drops[f] = new KeyValuePair<int, Mesh>(sig, m);
            return m;
        }

        private SpanMesh MeshFor(CompAerialAnchor a, CompAerialAnchor b, float y)
        {
            long key = ((long)a.thingIDNumber << 32) ^ (uint)b.thingIDNumber;
            int sig = Gen.HashCombineInt(a.Position.GetHashCode(), b.Position.GetHashCode());
            sig = Gen.HashCombineInt(sig, Mathf.RoundToInt(AerialSettings.sag * 1000f) * 7 + AerialSettings.maxStrands);
            sig = Gen.HashCombineInt(sig, Mathf.RoundToInt(AerialMaterials.SpanWidth * 1000f));
            sig = Gen.HashCombineInt(sig, Mathf.RoundToInt((a.Ext.attachZ + 7f * b.Ext.attachZ) * 1000f));
            sig = Gen.HashCombineInt(sig, AerialMaterials.Look.GetHashCode());
            if (meshes.TryGetValue(key, out SpanMesh m) && m.sig == sig) return m;
            m = SpanMesh.Build(a, b, y, sig);
            meshes[key] = m;
            return m;
        }

        public static int SpanSeed(CompAerialAnchor a, CompAerialAnchor b) =>
            (int)(AerialMath.Hash(Math.Min(a.thingIDNumber, b.thingIDNumber), Math.Max(a.thingIDNumber, b.thingIDNumber), 3) & 0x7fffffff);
    }

    /// <summary>One span's cached ribbon mesh (all its strands). Static unless swaying; sway rewrites the vertices of
    /// spans in view only, so a paused game holds the pose (game-tick clock).</summary>
    public class SpanMesh
    {
        public Mesh mesh;
        public int sig, seed;
        public CellRect rect;
        private readonly List<List<P2>> strands = new List<List<P2>>();
        private readonly List<double> ts = new List<double>();
        private Vector3[] verts;
        private P2 dir;
        private float y;
        private bool atRest = true;
        /// <summary>The look's cable width (AerialMaterials.SpanWidth: thick black Star Wars cable, thin modern/Cybertek lines).</summary>
        public static float Width => AerialMaterials.SpanWidth;
        public int Verts => verts?.Length ?? 0;

        public static SpanMesh Build(CompAerialAnchor a, CompAerialAnchor b, float y, int sig)
        {
            var m = new SpanMesh { sig = sig, y = y, seed = RM_MapComponent_Aerial.SpanSeed(a, b) };
            Vector3 pa = a.AttachPoint, pb = b.AttachPoint;
            double len = Math.Max(0.01, Vector3.Distance(pa, pb));
            m.dir = new P2((pb.x - pa.x) / len, (pb.z - pa.z) / len);
            var n = new P2(-m.dir.Z, m.dir.X);
            double[] ia = AerialMaterials.InsulatorsFor(a), ib = AerialMaterials.InsulatorsFor(b);
            List<StrandSpec> specs = AerialMath.StrandsFor(m.seed, AerialSettings.maxStrands);
            for (int si = 0; si < specs.Count; si++)
            {
                // each strand leaves its OWN insulator on the crossarm (fanned along the arm), plus its small lateral
                StrandSpec s = specs[si];
                double xa = ia[AerialMath.InsulatorIndex(si, specs.Count, ia.Length)], xb = ib[AerialMath.InsulatorIndex(si, specs.Count, ib.Length)];
                var A = new P2(pa.x + xa + n.X * s.Lateral, pa.z + n.Z * s.Lateral);
                var B = new P2(pb.x + xb + n.X * s.Lateral, pb.z + n.Z * s.Lateral);
                m.strands.Add(AerialMath.SpanCurve(A, B, AerialSettings.sag * s.SagMul));
            }
            int total = m.strands.Sum(s => s.Count) * 2;
            m.verts = new Vector3[total];
            var uvs = new Vector2[total];
            var tris = new List<int>();
            int v = 0;
            int minX = int.MaxValue, minZ = int.MaxValue, maxX = int.MinValue, maxZ = int.MinValue;
            foreach (List<P2> s in m.strands)
            {
                double u = 0;
                for (int i = 0; i < s.Count; i++)
                {
                    if (i > 0) u += P2.Dist(s[i - 1], s[i]) / (Width * 4);
                    uvs[v] = new Vector2((float)u, 1f);
                    uvs[v + 1] = new Vector2((float)u, 0f);
                    if (i > 0)
                    {
                        int q = v - 2;
                        tris.Add(q); tris.Add(q + 2); tris.Add(q + 3);
                        tris.Add(q); tris.Add(q + 3); tris.Add(q + 1);
                    }
                    minX = Math.Min(minX, (int)Math.Floor(s[i].X)); maxX = Math.Max(maxX, (int)Math.Floor(s[i].X));
                    minZ = Math.Min(minZ, (int)Math.Floor(s[i].Z)); maxZ = Math.Max(maxZ, (int)Math.Floor(s[i].Z));
                    v += 2;
                }
            }
            m.rect = CellRect.FromLimits(minX - 1, minZ - 1, maxX + 1, maxZ + 1);
            m.mesh = new Mesh { name = "RM_AerialSpan" };
            m.WriteVerts(0, 0, 0);
            m.mesh.vertices = m.verts;
            m.mesh.uv = uvs;
            m.mesh.SetTriangles(tris, 0);
            m.mesh.RecalculateBounds();
            return m;
        }

        public void Rest()
        {
            if (atRest) return;
            WriteVerts(0, 0, 0);
            mesh.vertices = verts;
            atRest = true;
        }

        public void Sway(float time, float wind, float amp)
        {
            WriteVerts(time, wind, amp);
            mesh.vertices = verts;
            atRest = false;
        }

        /// <summary>Ribbon vertices; each sample displaced perpendicular to the span in the ground plane by AerialMath.Sway.</summary>
        private void WriteVerts(float time, float wind, float amp)
        {
            var n = new P2(-dir.Z, dir.X);
            int v = 0;
            for (int si = 0; si < strands.Count; si++)
            {
                List<P2> s = strands[si];
                for (int i = 0; i < s.Count; i++)
                {
                    double t = i / (double)(s.Count - 1);
                    double off = amp > 0 ? AerialMath.Sway(t, time, wind, amp, seed + si * 977) : 0;
                    P2 p = new P2(s[i].X + n.X * off, s[i].Z + n.Z * off);
                    P2 prev = i > 0 ? s[i - 1] : s[i], next = i < s.Count - 1 ? s[i + 1] : s[i];
                    double tx = next.X - prev.X, tz = next.Z - prev.Z, tl = Math.Sqrt(tx * tx + tz * tz);
                    if (tl < 1e-9) { tx = dir.X; tz = dir.Z; tl = 1; }
                    double nx = -tz / tl * Width / 2, nz = tx / tl * Width / 2;
                    verts[v] = new Vector3((float)(p.X + nx), y, (float)(p.Z + nz));
                    verts[v + 1] = new Vector3((float)(p.X - nx), y, (float)(p.Z - nz));
                    v += 2;
                }
            }
        }
    }

    /// <summary>
    /// The wind-sway hook shared with the floor-cord lifted pieces (L4, design 1.5 / 2.5): ONE switch and one answer
    /// for "should wires move now", so the two lanes never disagree. Shader path not built (its displacement axis is
    /// unverified), so Auto means CPU.
    /// </summary>
    public static class WireSway
    {
        public static bool Active(Map map, out string reason)
        {
            if (AerialSettings.sway == WireSwayMode.Off) { reason = "setting off"; return false; }
            if (!Prefs.PlantWindSway) { reason = "game plant-sway preference off"; return false; }
            if (map == null || map.windManager.WindSpeed < 0.01f) { reason = "no wind"; return false; }
            if (AerialSettings.swayStrength <= 0.001f) { reason = "strength 0"; return false; }
            reason = "cpu";
            return true;
        }

        /// <summary>Perpendicular offset (cells) of a point at fraction t along a piece pinned at both ends.</summary>
        public static float Offset(Map map, float t, int seed, float amp = 0.12f)
        {
            if (!Active(map, out _)) return 0f;
            return (float)AerialMath.Sway(t, Find.TickManager.TicksGame / 60.0, map.windManager.WindSpeed, amp * AerialSettings.swayStrength, seed);
        }
    }

    /// <summary>Keeps RM_MapComponent_Aerial out of the save (as the cord component is kept out): a save loads clean
    /// without the mod's component class. Links are on the anchors.</summary>
    [HarmonyPatch(typeof(Map), "ExposeComponents")]
    internal static class Patch_Map_ExposeComponents_SkipAerial
    {
        internal sealed class Held { public int Index; public MapComponent Comp; }

        private static void Prefix(Map __instance, out Held __state)
        {
            __state = null;
            if (Scribe.mode != LoadSaveMode.Saving) return;
            List<MapComponent> list = __instance.components;
            int i = list.FindIndex(c => c is RM_MapComponent_Aerial);
            if (i < 0) return;
            __state = new Held { Index = i, Comp = list[i] };
            list.RemoveAt(i);
        }

        private static Exception Finalizer(Map __instance, Exception __exception, Held __state)
        {
            if (__state != null)
            {
                List<MapComponent> list = __instance.components;
                list.RemoveAll(c => c is RM_MapComponent_Aerial);
                list.Insert(Math.Min(__state.Index, list.Count), __state.Comp);
            }
            return __exception;
        }
    }

    /// <summary>Explosions cut spans whose ground line they reach (design 2.6). GenExplosion.DoExplosion signature read in
    /// decompiled 1.6 (center, map, radius, damType, instigator, damAmount = -1, ...).</summary>
    [HarmonyPatch(typeof(GenExplosion), nameof(GenExplosion.DoExplosion))]
    internal static class Patch_GenExplosion_CutSpans
    {
        private static void Postfix(IntVec3 center, Map map, float radius, DamageDef damType, int damAmount)
        {
            try
            {
                if (map == null || damType == null || !damType.harmsHealth) return;
                float dmg = damAmount >= 0 ? damAmount : damType.defaultDamage;
                map.GetComponent<RM_MapComponent_Aerial>()?.Notify_Explosion(center, radius, dmg);
            }
            catch (Exception ex) { Log.ErrorOnce("[MessyConduit] aerial explosion hook: " + ex, 0x7A9E12); }
        }
    }
}
