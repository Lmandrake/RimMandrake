using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.GimmeSomeSlack.Aerial
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
        private readonly Dictionary<FallenCord, List<FallenLay>> lays = new Dictionary<FallenCord, List<FallenLay>>();

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

        public void Notify_SpansChanged() => meshes.Clear();      // local drops re-sign themselves every frame (DrawLocalDrops)

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
            TapSparks(now);
        }

        // ------------------------------------------------------------------ the power-tap clamp: a NODE both grids cable into (round 3)
        /// <summary>Round 3 (owner 2026-10-04): "the enemy grid ... will look like the same art. So the bite should just be 'on
        /// top of' whatever's being drawn in the middle of their node there ... the power tap should be considered a Node that
        /// both power systems now must connect with their cables." The tap is a node of the cord graph that BOTH nets' cables
        /// run into (CordWorldAdapter: its machine hooks our connectParent conduit AND the conduit it bites), and the clamp
        /// (Aerial/TapClamp: jaws only, no drawn line of its own since round 3) is drawn ON TOP of that node, its jaws on the
        /// tap's centre where the cables meet, its handle turned toward our side. Size and the jaws' place in the art (fraction
        /// of the width from the centre) PROVISIONAL, measured from the 128 px art.</summary>
        public const float TapSize = 1.5f, TapBiteX = -0.40f;
        public int lastTapDraws, tapSparks;
        /// <summary>Clamp material per look (art round 5: Aerial/Styles/&lt;Look&gt;/TapClamp, Scrapper = root), null = art missing.</summary>
        private static readonly Dictionary<string, Material> tapMats = new Dictionary<string, Material>();
        /// <summary>State read: the clamp art path each look resolved to (a look whose own art is missing falls back to root).</summary>
        public static readonly Dictionary<string, string> TapPaths = new Dictionary<string, string>();

        /// <summary>The look a clamp draws in: the look of the run member it bites (legacy / none = the default look).</summary>
        public static string TapLookOf(CompPowerTap t)
        {
            t.VictimNet(out Thing v);
            return ConduitStyles.TapLook(v == null ? null : ConduitStylePicker.RawLook(v), StylePicker.DefaultLook);
        }

        public static Material TapMat(string look)
        {
            if (look == null) look = "Scrapper";
            if (tapMats.TryGetValue(look, out Material m)) return m;
            string path = ConduitStyles.TapClampPath(AerialMaterials.AerialDir, look);
            Texture2D tex = ContentFinder<Texture2D>.Get(path, false);
            if (tex == null && look != "Scrapper")
            {
                Log.WarningOnce("[GimmeSomeSlack] tap clamp art missing for " + look + " (" + path + "): drawing the root clamp", path.GetHashCode());
                path = ConduitStyles.TapClampPath(AerialMaterials.AerialDir, null);
                tex = ContentFinder<Texture2D>.Get(path, false);
            }
            // above every cord material (strands 3000, plugs 3001, wall faces 3002): the clamp sits ON the meeting cables
            m = tex == null ? null : MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent) { renderQueue = Core.DrawOrder.TapClampQueue(CordMaterials.StrandQueue) });
            tapMats[look] = m;
            TapPaths[look] = m == null ? null : path;
            return m;
        }

        public static bool TapBite(CompPowerTap t, out Vector3 bite, out Vector3 centre, out float angle)
        {
            Vector3 home = t.parent.TrueCenter();
            t.VictimNet(out Thing v);
            bite = home;
            Vector3 ours = t.Trader?.connectParent?.parent != null ? t.Trader.connectParent.parent.TrueCenter() : home;
            Vector3 back = ours - home;
            if (back.MagnitudeHorizontalSquared() < 1e-4f && v != null) back = home - v.TrueCenter();
            back.y = 0f;
            if (back.sqrMagnitude < 1e-6f) back = Vector3.right;
            back = back.normalized;
            centre = bite - back * (TapBiteX * TapSize);
            angle = -Mathf.Atan2(back.z, back.x) * Mathf.Rad2Deg;
            return v != null;
        }

        private void DrawTaps(CellRect view)
        {
            lastTapDraws = 0;
            float y = AltitudeLayer.BuildingOnTop.AltitudeFor();
            foreach (CompPowerTap t in Taps)
            {
                if (!view.Contains(t.parent.Position)) continue;
                Material tapMat = TapMat(TapLookOf(t));
                if (tapMat == null) continue;
                TapBite(t, out _, out Vector3 c, out float ang);
                c.y = y;
                Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(c, Quaternion.AngleAxis(ang, Vector3.up), new Vector3(TapSize, 1f, TapSize)), tapMat, 0);
                lastTapDraws++;
            }
        }

        /// <summary>A clamp that is drawing power now spits a few sparks from its jaws now and then (look only).</summary>
        private void TapSparks(int tick)
        {
            if (!AerialSettings.enabled || GimmeSomeSlackSettings.sparkIntensity <= 0.01f || Find.CurrentMap != map) return;
            foreach (CompPowerTap t in Taps)
            {
                if (t.lastStolenW <= 0f) continue;
                int seed = (int)(AerialMath.Hash(t.parent.thingIDNumber, 0x7A9) & 0x7fff);
                int period = Mathf.Max(40, Mathf.RoundToInt((150 + seed % 120) / GimmeSomeSlackSettings.sparkIntensity));
                if ((tick + seed) % period != 0) continue;
                if (!TapBite(t, out Vector3 bite, out _, out _)) continue;
                bite.y = AltitudeLayer.MoteOverhead.AltitudeFor();
                FleckMaker.ThrowMicroSparks(bite, map);
                if (((tick / period + seed) % 3) == 0) FleckMaker.ThrowLightningGlow(bite, map, 0.35f);
                tapSparks++;
            }
        }

        private void ProcessAutoLinks()
        {
            map.GetComponent<RM_MapComponent_ConduitRuns>()?.ProcessPending();      // a new pole adopts its run's look first
            foreach (CompAerialAnchor a in pendingAuto.ToList())
            {
                if (!a.Spawned) { pendingAuto.Remove(a); continue; }
                if (a.Faction == null) continue;                       // build_batch may set the faction a moment later
                pendingAuto.Remove(a);
                if (!AerialSettings.enabled || !AerialSettings.autoLink) continue;
                // stage 2 (design 2.3): auto-link only links to a run of the SAME look; linking two looks by hand is a bridge
                string look = StylePicker.LookOfThing(a.parent);
                var others = Anchors.Where(o => o != a && StylePicker.LookOfThing(o.parent) == look).ToList();
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

        /// <summary>The fallen / cut wires of <paramref name="f"/> (round 3: EVERY wire the span carried falls, f.wires of
        /// them); each is ONE cable from its insulator down to the break on the ground (B21), Tip = its end at the break.
        /// Cached until the ground or the look changes.</summary>
        public List<FallenLay> Lays(CompAerialAnchor a, FallenCord f)
        {
            if (lays.TryGetValue(f, out List<FallenLay> l)) return l;
            Vector3 b = a.BasePoint;
            List<P2> tips = a.InsulatorTips();
            if (tips.Count == 0) tips.Add(new P2(a.AttachPoint.x, a.AttachPoint.z));
            PathGrid pg = map.pathing.Normal.pathGrid;
            IntVec3 home = a.Position;
            Func<int, int, bool> walk = (x, z) =>
            {
                var c = new IntVec3(x, 0, z);
                if (!c.InBounds(map)) return false;
                return c == home || pg.WalkableFast(c);
            };
            int n = f.wires > 0 ? f.wires : AerialMath.StrandCount(tips.Count, tips.Count, AerialSettings.maxStrands);
            l = AerialMath.LayFallenStrands(tips, new P2(b.x, b.z), new P2(f.toward.x + 0.5, f.toward.z + 0.5), f.length, f.seed, n, walk);
            lays[f] = l;
            return l;
        }

        /// <summary>The middle fallen wire of <paramref name="f"/> (sparks, glow, the probe's single-wire fields).</summary>
        public FallenLay Lay(CompAerialAnchor a, FallenCord f)
        {
            List<FallenLay> l = Lays(a, f);
            return l[l.Count / 2];
        }

        private const int MaxSparkingEnds = 24;

        private void Sparks(int tick)
        {
            if (!AerialSettings.enabled || !GimmeSomeSlackSettings.breakReadout || GimmeSomeSlackSettings.sparkIntensity <= 0.01f) return;
            int n = 0;
            foreach (CompAerialAnchor a in Anchors)
            {
                if (a.fallen.Count == 0 || !(FallenLiveCached(a) ?? false)) continue;
                foreach (FallenCord f in a.fallen)
                {
                    if (++n > MaxSparkingEnds) return;
                    int period = Mathf.Max(12, Mathf.RoundToInt(60 / GimmeSomeSlackSettings.sparkIntensity));
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
                Material top = AerialMaterials.Top(AerialMaterials.TopPathFor(a));
                if (top != null && view.Contains(a.Position))
                {
                    var pos = new Vector3(a.Position.x + 0.5f, TopAltitude, a.Position.z + 0.5f + AerialMaterials.TopOffsetZ(a));
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
                    Graphics.DrawMesh(m.mesh, Matrix4x4.identity, m.mat, 0);
                    lastSpanDraws++;
                }
                // B11/B21: a cut / orphaned wire is ONE cable from the insulator down to the break on the ground, in the
                // span's own material and width (the ground layer prints only the frayed end at its tip)
                Material own = a.fallen.Count > 0 ? AerialMaterials.For(AerialMaterials.LookOf(a)).Span : null;
                if (own != null)
                    foreach (FallenCord f in a.fallen)
                    {
                        Mesh dm = WireMesh(a, f, spanY);
                        if (dm == null || !dm.bounds.Intersects(new Bounds(view.CenterVector3, new Vector3(view.Width, 100f, view.Height)))) continue;
                        Graphics.DrawMesh(dm, Matrix4x4.identity, own, 0);
                        lastDropDraws++;
                    }
            }
            DrawLocalDrops(view);
            DrawTaps(view);
            DrawFallenGlow();
        }

        // ------------------------------------------------------------------ local drops (owner round 2, 2026-10-04)
        public int lastLocalDrops;
        /// <summary>State read: per anchor id, device id -> terminal index used on the last frame.</summary>
        public readonly Dictionary<int, Dictionary<int, int>> lastTerminals = new Dictionary<int, Dictionary<int, int>>();
        private readonly Dictionary<long, KeyValuePair<int, Mesh[]>> dropMeshes = new Dictionary<long, KeyValuePair<int, Mesh[]>>();
        private readonly HashSet<long> dropUsed = new HashSet<long>();

        /// <summary>The things that hang off this pole locally: the devices vanilla wired to it (connectChildren) and the
        /// transmitters standing cardinally beside it (a battery: joined by adjacency, drawn by nothing until round 2).
        /// Our invisible conduit is the cord graph's; other anchors are spans.</summary>
        public static List<Thing> LocalConnections(CompAerialAnchor a)
        {
            var r = new List<Thing>();
            CompPower pc = a.PowerComp;
            if (pc?.connectChildren != null)
                foreach (CompPower c in pc.connectChildren)
                    if (c?.parent != null && c.parent.Spawned && !r.Contains(c.parent)) r.Add(c.parent);
            if (!a.Spawned) return r;
            foreach (IntVec3 adj in GenAdj.CellsAdjacentCardinal(a.parent))
            {
                if (!adj.InBounds(a.Map)) continue;
                foreach (Thing t in adj.GetThingList(a.Map))
                {
                    if (!(t is Building b) || r.Contains(t) || CompAerialAnchor.Of(t) != null) continue;
                    if (t.def.building != null && t.def.building.isPowerConduit) continue;
                    CompPower p = b.PowerComp;
                    if (p == null || !p.Props.transmitsPower) continue;
                    r.Add(t);
                }
            }
            return r;
        }

        /// <summary>Each local connection is a drop wire from the device's CENTROID up to the pole terminal
        /// AerialMath.AssignTerminals gave it (spread over the crossarm, shared only when there are more devices than
        /// insulators). The part over the device's own art is drawn BENEATH the building (SmallWire), so it vanishes into the
        /// device whatever its art; the rest hangs at span altitude and ends exactly on the insulator tip.</summary>
        private void DrawLocalDrops(CellRect view)
        {
            lastLocalDrops = 0;
            if (!AerialSettings.enabled || AerialMaterials.Span == null) return;
            dropUsed.Clear();
            float under = AltitudeLayer.SmallWire.AltitudeFor(), over = SpanAltitude;
            foreach (CompAerialAnchor a in Anchors)
            {
                if (!view.ExpandedBy(6).Contains(a.Position)) continue;
                List<Thing> devs = LocalConnections(a);
                if (devs.Count == 0) { lastTerminals.Remove(a.thingIDNumber); continue; }
                List<P2> tips = a.InsulatorTips();
                if (tips.Count == 0) continue;
                AerialMaterials.LookMats lm = AerialMaterials.For(AerialMaterials.LookOf(a));
                if (lm.Span == null) continue;
                Vector3 bp = a.BasePoint;
                Dictionary<int, int> term = AerialMath.AssignTerminals(devs.Select(d => (d.thingIDNumber, (double)(d.TrueCenter().x - bp.x))).ToList(), tips.Count);
                lastTerminals[a.thingIDNumber] = term;
                foreach (Thing d in devs)
                {
                    P2 tip = tips[Mathf.Clamp(term[d.thingIDNumber], 0, tips.Count - 1)];
                    long key = ((long)a.thingIDNumber << 32) ^ (uint)d.thingIDNumber;
                    dropUsed.Add(key);
                    Vector3 c = DeviceHome(d);
                    int sig = Gen.HashCombineInt(Gen.HashCombineInt(c.GetHashCode(), tip.X.GetHashCode() ^ tip.Z.GetHashCode()),
                                                 Gen.HashCombineInt(Mathf.RoundToInt(lm.Width * 1000f), d.Rotation.AsInt));
                    if (!dropMeshes.TryGetValue(key, out var kv) || kv.Key != sig)
                    {
                        if (kv.Value != null) foreach (Mesh old in kv.Value) if (old != null) UnityEngine.Object.Destroy(old);
                        kv = new KeyValuePair<int, Mesh[]>(sig, DropMeshes(d, new P2(c.x, c.z), tip, under, over, lm.Width));
                        dropMeshes[key] = kv;
                    }
                    foreach (Mesh m in kv.Value)
                        if (m != null) Graphics.DrawMesh(m, Matrix4x4.identity, lm.Span, 0);
                    lastLocalDrops++;
                }
            }
            if (dropMeshes.Count > dropUsed.Count * 2 + 32)
                foreach (long k in dropMeshes.Keys.Where(k => !dropUsed.Contains(k)).ToList())
                {
                    foreach (Mesh old in dropMeshes[k].Value) if (old != null) UnityEngine.Object.Destroy(old);
                    dropMeshes.Remove(k);
                }
        }

        /// <summary>Where a device's drop starts: its centroid, or (round 4, owner 2026-10-04 station 19: cords to wall devices
        /// "should just go up to and beneath the wall that contains the device") the centre of the wall a wall-mounted device
        /// hangs on, beneath that wall.</summary>
        public static Vector3 DeviceHome(Thing d)
        {
            if (d.def.building != null && d.def.building.isAttachment && d.Spawned)
            {
                Thing wall = GenConstruct.GetWallAttachedTo(d);
                if (wall != null) return wall.Position.ToVector3Shifted();
            }
            return d.TrueCenter();
        }

        /// <summary>The device's drawn extent (its footprint united with its graphic rect, and the wall a wall-mounted device
        /// hangs on), in which the drop runs under it.</summary>
        public static bool InDeviceArt(Thing d, P2 p)
        {
            CellRect r = d.OccupiedRect();
            if (p.X >= r.minX && p.X <= r.maxX + 1 && p.Z >= r.minZ && p.Z <= r.maxZ + 1) return true;
            if (d.def.building != null && d.def.building.isAttachment && d.Spawned)
            {
                Thing wall = GenConstruct.GetWallAttachedTo(d);
                if (wall != null && p.X >= wall.Position.x && p.X <= wall.Position.x + 1 && p.Z >= wall.Position.z && p.Z <= wall.Position.z + 1) return true;
            }
            if (d.Graphic == null) return false;
            Vector3 g = d.TrueCenter() + d.Graphic.DrawOffset(d.Rotation);
            Vector2 sz = d.Graphic.drawSize;
            if (d.Rotation.IsHorizontal && d.Graphic.ShouldDrawRotated) sz = new Vector2(sz.y, sz.x);
            return Math.Abs(p.X - g.x) <= sz.x / 2f && Math.Abs(p.Z - g.z) <= sz.y / 2f;
        }

        private static Mesh[] DropMeshes(Thing d, P2 from, P2 tip, float under, float over, float width)
        {
            List<P2> pts = AerialMath.SpanCurve(from, tip, 0.04, 0.2);
            int split = 0;
            while (split < pts.Count - 1 && InDeviceArt(d, pts[split])) split++;
            var lo = pts.GetRange(0, Math.Min(pts.Count, split + 1));
            var hi = pts.GetRange(split, pts.Count - split);
            return new[] { Ribbon(lo, under, "RM_AerialDropUnder", width), Ribbon(hi, over, "RM_AerialDrop", width) };
        }

        private static Mesh Ribbon(List<P2> pts, float y, string name, float width)
        {
            if (pts.Count < 2) return null;
            var verts = new List<Vector3>(); var uvs = new List<Vector2>(); var tris = new List<int>();
            float w = width * 0.85f;
            double u = 0;
            for (int i = 0; i < pts.Count; i++)
            {
                P2 prev = i > 0 ? pts[i - 1] : pts[i], next = i < pts.Count - 1 ? pts[i + 1] : pts[i];
                double tx = next.X - prev.X, tz = next.Z - prev.Z, tl = Math.Sqrt(tx * tx + tz * tz);
                if (tl < 1e-9) { tx = 0; tz = 1; tl = 1; }
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
            var m = new Mesh { name = name };
            m.SetVertices(verts); m.SetUVs(0, uvs); m.SetTriangles(tris, 0); m.RecalculateBounds();
            return m;
        }

        public static float SpanAltitude => AltitudeLayer.PawnState.AltitudeFor(Core.DrawOrder.SpanInc);
        public static float TopAltitude => AltitudeLayer.PawnState.AltitudeFor(Core.DrawOrder.TopInc);

        // Round 5 (owner 2026-10-04: "Make the lamps on the lamp masts like ordinary lights, not frozen bright sparkles. Make
        // them the same as the wall lights normally used."): no lit-head sprite. Like vanilla WallLamp / StandingLamp the mast
        // is its look's art plus a CompGlower, and the light is the glow grid's alone.

        private void DrawFallenGlow()
        {
            if (!GimmeSomeSlackSettings.breakReadout || GimmeSomeSlackSettings.sparkIntensity <= 0.01f || AerialMaterials.Glow == null) return;
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
                    float size = (0.38f + 0.42f * k * k) * Mathf.Min(1.5f, GimmeSomeSlackSettings.sparkIntensity);
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
            float w = AerialMaterials.For(AerialMaterials.LookOf(a)).Width;
            int sig = Gen.HashCombineInt(a.Position.GetHashCode(), Mathf.RoundToInt(w * 1000f));
            sig = Gen.HashCombineInt(sig, Mathf.RoundToInt(AerialMaterials.AttachZ(a) * 1000f));
            if (drops.TryGetValue(f, out var kv) && kv.Key == sig) return kv.Value;
            var verts = new List<Vector3>(); var uvs = new List<Vector2>(); var tris = new List<int>();
            foreach (FallenLay lay in Lays(a, f))
            {
            List<P2> pts = lay.Pts;
            if (pts.Count < 2) continue;
            int v0 = verts.Count;
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
                int q = v0 + 2 * (i - 1);
                tris.Add(q); tris.Add(q + 2); tris.Add(q + 3);
                tris.Add(q); tris.Add(q + 3); tris.Add(q + 1);
            }
            }
            if (verts.Count == 0) return null;
            var m = new Mesh { name = "RM_AerialFallenWire" };
            m.SetVertices(verts); m.SetUVs(0, uvs); m.SetTriangles(tris, 0); m.RecalculateBounds();
            if (drops.TryGetValue(f, out var old) && old.Value != null) UnityEngine.Object.Destroy(old.Value);
            drops[f] = new KeyValuePair<int, Mesh>(sig, m);
            return m;
        }

        /// <summary>State read (AerialProbe "styles"): the span mesh as drawn now, built if missing.</summary>
        public SpanMesh SpanMeshFor(CompAerialAnchor a, CompAerialAnchor b) => MeshFor(a, b, SpanAltitude);

        private SpanMesh MeshFor(CompAerialAnchor a, CompAerialAnchor b, float y)
        {
            long key = ((long)a.thingIDNumber << 32) ^ (uint)b.thingIDNumber;
            int sig = Gen.HashCombineInt(a.Position.GetHashCode(), b.Position.GetHashCode());
            sig = Gen.HashCombineInt(sig, Mathf.RoundToInt(AerialSettings.sag * 1000f) * 7 + AerialSettings.maxStrands);
            // per-build style: the span's look (AerialMaterials.SpanLookOf) and BOTH poles' looks (their insulator rows)
            AerialMaterials.LookMats lm = AerialMaterials.SpanMats(a, b);
            sig = Gen.HashCombineInt(sig, Mathf.RoundToInt(lm.Width * 1000f));
            sig = Gen.HashCombineInt(sig, Mathf.RoundToInt((AerialMaterials.AttachZ(a) + 7f * AerialMaterials.AttachZ(b)) * 1000f));
            sig = Gen.HashCombineInt(sig, Gen.HashCombineInt(lm.Look.GetHashCode(), (AerialMaterials.LookOf(a) + "|" + AerialMaterials.LookOf(b)).GetHashCode()));
            if (meshes.TryGetValue(key, out SpanMesh m) && m.sig == sig) return m;
            m = SpanMesh.Build(a, b, y, sig, lm);
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
        /// <summary>The span's cable (its look's, AerialMaterials.SpanLookOf) and the look it was built in (state read).</summary>
        public Material mat;
        public string look;
        public int sig, seed;
        public CellRect rect;
        private readonly List<List<P2>> strands = new List<List<P2>>();
        /// <summary>State read: each strand's end points and insulator indices (B23).</summary>
        public List<AerialMath.SpanStrand> ends = new List<AerialMath.SpanStrand>();
        private readonly List<double> ts = new List<double>();
        private Vector3[] verts;
        private P2 dir;
        private float y;
        private bool atRest = true;
        /// <summary>The span look's cable width (thick black Industrial cable, thin Modern/Futuristic lines).</summary>
        public float Width = 0.17f;
        public int Verts => verts?.Length ?? 0;

        public static SpanMesh Build(CompAerialAnchor a, CompAerialAnchor b, float y, int sig, AerialMaterials.LookMats lm)
        {
            var m = new SpanMesh { sig = sig, y = y, seed = RM_MapComponent_Aerial.SpanSeed(a, b), mat = lm.Span, look = lm.Look, Width = lm.Width };
            Vector3 ba = a.BasePoint, bb = b.BasePoint;
            double len = Math.Max(0.01, Vector3.Distance(ba, bb));
            m.dir = new P2((bb.x - ba.x) / len, (bb.z - ba.z) / len);
            // B23: one wire per insulator, each ending exactly on an insulator tip of each pole
            m.ends = AerialMath.SpanStrands(new P2(ba.x, ba.z), AerialMaterials.InsulatorsFor(a), new P2(bb.x, bb.z), AerialMaterials.InsulatorsFor(b), m.seed, AerialSettings.maxStrands);
            foreach (AerialMath.SpanStrand s in m.ends)
                m.strands.Add(AerialMath.SpanCurve(s.A, s.B, AerialSettings.sag * s.SagMul));
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
                    if (i > 0) u += P2.Dist(s[i - 1], s[i]) / (m.Width * 4);
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
            catch (Exception ex) { Log.ErrorOnce("[GimmeSomeSlack] aerial explosion hook: " + ex, 0x7A9E12); }
        }
    }
}
