using System;
using System.Collections.Generic;
using RimMandrake.MessyConduit.Core;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit.Hose
{
    /// <summary>
    /// Runtime side of the flexible hoses (design 3.4-3.5): ticks every reel's state machine from the flow providers,
    /// lays hoses lazily (planner + rope settle in HoseMath), and draws them every frame (a handful of meshes; a
    /// settled hose reuses its cached mesh, only a transitioning one is rebuilt per frame). Kept OUT of the save
    /// (Patch_Map_ExposeComponents_SkipHoses): the reels hold everything that must persist.
    /// </summary>
    [StaticConstructorOnStartup]
    public class RM_MapComponent_Hoses : MapComponent
    {
        private readonly List<CompHoseReel> reels = new List<CompHoseReel>();
        private readonly Dictionary<CompHoseReel, Cached> meshes = new Dictionary<CompHoseReel, Cached>();
        private CordWorld world;
        private int worldTick = -1;
        private bool drawErrorLogged;
        public static int Relays, LastLayMs, Retracts;

        private sealed class Cached
        {
            public string key;
            public Mesh flat, plump, shadow;
        }

        public RM_MapComponent_Hoses(Map map) : base(map) { }

        public IReadOnlyList<CompHoseReel> Reels => reels;

        public void Register(CompHoseReel r) { if (!reels.Contains(r)) reels.Add(r); }

        public void Deregister(CompHoseReel r)
        {
            reels.Remove(r);
            DropMeshes(r);
        }

        // ------------------------------------------------------------------ world snapshot for hoses
        /// <summary>A hose's CordWorld: walls, rock, impassable buildings and fog block it; WATER does not (a hose
        /// floats, design 3.5: walkable at extra cost 3); trees cost a little. Cached for the tick it was taken.</summary>
        public CordWorld World()
        {
            int now = Find.TickManager.TicksGame;
            if (world != null && worldTick == now) return world;
            int w = map.Size.x, h = map.Size.z;
            var cw = new CordWorld(w, h);
            CellIndices ci = map.cellIndices;
            for (int idx = 0; idx < w * h; idx++)
            {
                IntVec3 c = ci.IndexToCell(idx);
                var cell = new Cell(c.x, c.z);
                if (map.fogGrid.IsFogged(idx)) { cw.SetBlocked(cell, BlockKind.Rock); continue; }
                Building ed = map.edificeGrid[idx];
                if (ed is Building_Door) cw.SetDoor(cell);
                TerrainDef t = map.terrainGrid.TerrainAt(idx);
                if (map.pathing.Normal.pathGrid.WalkableFast(idx)) continue;
                if (ed == null && t != null && t.IsWater && !HasImpassableThing(c)) { cw.SetExtraCost(cell, 3f); continue; }
                if (ed != null && CompHoseReelOf(ed) != null) continue;
                cw.SetBlocked(cell, ed != null && ed.def.building != null && ed.def.building.isNaturalRock ? BlockKind.Rock : BlockKind.Wall);
            }
            foreach (Plant p in map.listerThings.ThingsInGroup(ThingRequestGroup.Plant))
                if (p.def.plant != null && p.def.plant.IsTree) cw.SetExtraCost(new Cell(p.Position.x, p.Position.z), 1.5f);
            world = cw;
            worldTick = now;
            return cw;
        }

        private bool HasImpassableThing(IntVec3 c)
        {
            List<Thing> l = c.GetThingList(map);
            for (int i = 0; i < l.Count; i++) if (l[i].def.passability == Traversability.Impassable) return true;
            return false;
        }

        private static CompHoseReel CompHoseReelOf(Thing t) => (t as ThingWithComps)?.GetComp<CompHoseReel>();

        public string CheckInstall(CompHoseReel r, IntVec3 target)
        {
            if (!HoseSettings.enabled) return "hoses are switched off in Mod Settings";
            return HoseMath.CheckInstall(World(), r.Rect, new Cell(target.x, target.z), r.MaxLength);
        }

        // ------------------------------------------------------------------ relays (round 6, HoseRelay)
        /// <summary>The reels in thing-id order (the relay tie-break) with their footprints.</summary>
        private List<CompHoseReel> Ordered(out List<HoseReelRect> rects)
        {
            var o = new List<CompHoseReel>(reels);
            o.Sort((a, b) => a.parent.thingIDNumber.CompareTo(b.parent.thingIDNumber));
            rects = new List<HoseReelRect>(o.Count);
            foreach (CompHoseReel r in o) rects.Add(r.Rect);
            return o;
        }

        /// <summary>The reel whose intake this reel's laid hose ends on (null = a free end).</summary>
        public CompHoseReel RelayOf(CompHoseReel r)
        {
            if (r == null || !r.laid || !r.far.IsValid) return null;
            return RelayAt(r, new Cell(r.far.x, r.far.z));
        }

        /// <summary>The reel (other than r) that has <paramref name="c"/> as an intake cell, or null.</summary>
        public CompHoseReel RelayAt(CompHoseReel r, Cell c)
        {
            List<CompHoseReel> o = Ordered(out List<HoseReelRect> rects);
            int i = HoseRelay.RelayOf(c, rects, o.IndexOf(r));
            return i < 0 ? null : o[i];
        }

        /// <summary>The reel whose FOOTPRINT holds the cell (other than r), or null: the player clicked onto a relay.</summary>
        public CompHoseReel ReelCovering(CompHoseReel r, IntVec3 c)
        {
            foreach (CompHoseReel o in reels) if (o != r && o.Rect.Contains(new Cell(c.x, c.z))) return o;
            return null;
        }

        /// <summary>Reels feeding r (their hose ends on r's intake), in thing-id order, loops excluded.</summary>
        public List<CompHoseReel> FeedersOf(CompHoseReel r)
        {
            var o = new List<CompHoseReel>();
            foreach (CompHoseReel f in Ordered(out _))
                if (f != r && RelayOf(f) == r && !Loops(f, r)) o.Add(f);
            return o;
        }

        /// <summary>Would a hose from <paramref name="from"/> into <paramref name="to"/> close a loop?</summary>
        public bool Loops(CompHoseReel from, CompHoseReel to)
        {
            List<CompHoseReel> o = Ordered(out _);
            return HoseRelay.WouldLoop(o.IndexOf(from), o.IndexOf(to), i => { CompHoseReel n = RelayOf(o[i]); return n == null ? -1 : o.IndexOf(n); });
        }

        /// <summary>Where r's hose ends: on a relay, the drawn reel's inlet / outline at its intake side (HoseRelay.DrawnEnd,
        /// round 7), else its free-end cell's centre.</summary>
        public V2 EndPoint(CompHoseReel r, out CompHoseReel relay) => EndPoint(r, out relay, out _);

        /// <summary>As EndPoint; <paramref name="inward"/> = the direction the hose's last stretch and coupling point
        /// into the relay (null at a free end).</summary>
        public V2 EndPoint(CompHoseReel r, out CompHoseReel relay, out V2? inward)
        {
            relay = RelayOf(r);
            inward = null;
            IntVec3 ec = r.EndCell;   // S2: far while laid/dropped, the trail's last cell while carried or wound
            var far = new Cell(ec.x, ec.z);
            if (relay == null) return far.Centre;
            V2 e = HoseRelay.DrawnEnd(relay.Rect, far, HoseMaterials.LookOf(relay), relay.laid, out V2 d);
            inward = d;
            return e;
        }

        // ------------------------------------------------------------------ lay
        /// <summary>The hose leaves the reel at its drum's axis (HoseReelRect.Mouth, round 5), hidden by the sprite, so it shows
        /// coming off the drum; the deployed art paints no hose of its own.</summary>
        public static V2 Start(CompHoseReel r) => r.Rect.Mouth;

        public HoseLay EnsureLay(CompHoseReel r)
        {
            if (!r.HoseOut) return null;
            V2 end = EndPoint(r, out CompHoseReel relay, out V2? inward);
            // the relay's look and art (stored / laid) move the drawn inlet, so they are part of the key; S2: so does the
            // walked trail (empty = the planned route, the key as before)
            string key = r.parent.Position + ">" + r.EndCell + (relay != null ? "R" + relay.parent.thingIDNumber + HoseMaterials.LookOf(relay) + (relay.laid ? "L" : "S") : "") + r.TrailKey() + "|" + HoseSettings.ShapeFingerprint();
            if (r.layKey == key) return r.lay; // a failed lay is cached too (lay null); the 250-tick check clears layKey to retry
            var sw = System.Diagnostics.Stopwatch.StartNew();
            CordWorld w = World();
            HoseShapeParams sp = HoseSettings.Shape();
            sp.MaxLength = r.MaxLength;
            HoseLay lay = HoseMath.LayAlong(w, Start(r), r.TrailCells(), end, sp, r.Seed, inward);
            LastLayMs = (int)sw.ElapsedMilliseconds;
            Relays++;
            r.lay = lay.Ok ? lay : null;
            r.lastLayReason = lay.Ok ? null : (lay.Reason ?? "could not be laid");
            r.layKey = key;
            r.corridorHash = lay.Ok ? CorridorHash(w, lay) : 0;
            DropMeshes(r);
            return r.lay;
        }

        public static ulong CorridorHash(CordWorld w, HoseLay lay)
        {
            int x0 = int.MaxValue, z0 = int.MaxValue, x1 = int.MinValue, z1 = int.MinValue;
            foreach (V2 p in lay.Flat) { Cell c = p.Floor; x0 = Math.Min(x0, c.X); z0 = Math.Min(z0, c.Z); x1 = Math.Max(x1, c.X); z1 = Math.Max(z1, c.Z); }
            ulong h = 1469598103934665603UL;
            for (int z = z0 - 2; z <= z1 + 2; z++)
                for (int x = x0 - 2; x <= x1 + 2; x++)
                {
                    var c = new Cell(x, z);
                    h = (h ^ (ulong)(w.IsWalkable(c) ? 1 : 2) ^ (w.IsDoor(c) ? 4UL : 0UL)) * 1099511628211UL;
                }
            return h;
        }

        public static ulong GeometryHash(HoseLay lay)
        {
            ulong h = 1469598103934665603UL;
            if (lay == null) return 0;
            foreach (V2 p in lay.Flat)
            {
                h = (h ^ unchecked((ulong)(long)Math.Round(p.X * 1000))) * 1099511628211UL;
                h = (h ^ unchecked((ulong)(long)Math.Round(p.Z * 1000))) * 1099511628211UL;
            }
            return h;
        }

        // ------------------------------------------------------------------ tick: the state machines
        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            HoseTuning t = HoseSettings.Tuning();
            for (int i = 0; i < reels.Count; i++)
            {
                CompHoseReel r = reels[i];
                // S2, design section 5 b: a carried / wound hose's holder is re-checked every 30 ticks (the RopingTick
                // pattern) so an end is never held by a pawn that stopped holding it
                if ((r.carry == HoseCarryState.Carrying || r.carry == HoseCarryState.Retracting) && (now + r.parent.thingIDNumber) % 30 == 0)
                    r.HolderCheck();
                if (!r.laid) continue;
                bool sig = HoseFlow.Signal(r, now, out r.lastProvider);
                r.lastSignal = sig;
                HoseVis before = r.sm.State;
                r.sm.Update(now, sig, t);
                if (r.sm.State != before)
                {
                    r.history.Add(new KeyValuePair<int, HoseVis>(now, r.sm.State));
                    if (r.history.Count > 64) r.history.RemoveAt(0);
                }
                // an obstacle built or removed across the hose (checked every 250 ticks): HOSE_BLOCKED_REROUTE_RETRACT_1 --
                // re-route if a route within the hose's length remains, else wind it back onto the reel with an alert.
                // A failed lay is never left laid-but-invisible (no ghost hose).
                if ((now + r.parent.thingIDNumber) % 250 == 0 && r.layKey != null && (r.lay == null || CorridorHash(World(), r.lay) != r.corridorHash))
                {
                    // S2, design section 8: a walked hose that an obstacle cut (or that will not lay) falls back to the
                    // planned route from the reel; the walked shape is lost, which is right: the obstacle moved it
                    if (r.trail.Count > 0 && (r.lay == null || !r.TrailWalkable(World())))
                    {
                        r.trail.Clear();
                        r.layKey = null;
                        continue;
                    }
                    string why = HoseMath.CheckReplan(World(), r.Rect, new Cell(r.far.x, r.far.z), r.MaxLength, r.lay == null, r.lastLayReason);
                    if (why != null) { r.Retract(why); Retracts++; continue; }
                    r.layKey = null;
                }
            }
        }

        // ------------------------------------------------------------------ draw
        public override void MapComponentUpdate()
        {
            HoseProbe.Service(map, this);
            if (!HoseSettings.enabled || Find.CurrentMap != map || reels.Count == 0) { FlushFrameMeshes(); return; }
            try { DrawAll(); }
            catch (Exception ex)
            {
                if (!drawErrorLogged) { drawErrorLogged = true; Log.Error("[MessyConduit] hose drawing failed, skipping it: " + ex); }
                FlushFrameMeshes();
            }
        }

        public struct PoseInfo
        {
            public double Blend, Eased, Visible;
            public int SinceChange;
            public bool Wobbling;
        }

        public static PoseInfo Info(CompHoseReel r)
        {
            int now = Find.TickManager.TicksGame;
            HoseTuning t = HoseSettings.Tuning();
            double b = r.sm.Blend(now, t), e = HoseMath.Ease(b);
            int since = now - r.sm.Since;
            bool wob = HoseSettings.fillWobble && r.sm.Transitions > 0 && HoseMath.WobbleActive(since, t.TransitionTicks);
            return new PoseInfo { Blend = b, Eased = e, Visible = HoseMath.VisibleWidth(e, HoseSettings.plumpAmount), SinceChange = since, Wobbling = wob };
        }

        private void DrawAll()
        {
            float y0 = AltitudeLayer.Conduits.AltitudeFor() + Core.DrawOrder.HoseBaseLift;
            lastWrapDraws = lastFeedDraws = lastReelEndHidden = lastRelayCouplings = 0;
            for (int i = 0; i < reels.Count; i++)
            {
                CompHoseReel r = reels[i];
                // B18: where hoses cross, one passes cleanly over the other, the same way every frame: each hose (and its
                // fittings) sits in its own altitude band, ordered by when the reel was built
                float y = y0 + HoseMath.CrossLift(RankOf(r));
                DrawFeed(r, y0);
                HoseLay lay = EnsureLay(r);
                if (lay == null) continue;
                PoseInfo pi = Info(r);
                double amt = HoseSettings.plumpAmount;
                int T = HoseSettings.Tuning().TransitionTicks;
                List<V2> pts = HoseMath.Pose(lay, pi.Eased, pi.Wobbling ? pi.SinceChange : int.MaxValue / 2, T, amt);
                bool settled = !pi.Wobbling && (pi.Blend <= 0 || pi.Blend >= 1);
                string key = settled ? (pi.Blend >= 1 ? "P" : "F") + r.layKey + "@" + RankOf(r) : null;
                meshes.TryGetValue(r, out Cached c);
                float vis = (float)pi.Visible;
                float e = (float)pi.Eased;
                Mesh fm, pm, sm;
                if (c != null && key != null && c.key == key) { fm = c.flat; pm = c.plump; sm = c.shadow; }
                else
                {
                    fm = e < 0.999f ? Ribbon(pts, (float)HoseMath.MeshWidthFlat(vis), y, 0.37) : null;
                    pm = e > 0.001f ? Ribbon(pts, (float)HoseMath.MeshWidthPlump(vis), y + 0.0004f, 0.37) : null;
                    var off = new V2(0.03 + 0.05 * e, -(0.03 + 0.06 * e));
                    var sp = new List<V2>(pts.Count);
                    foreach (V2 p in pts) sp.Add(p + off);
                    sm = Ribbon(sp, vis * (1.15f + 0.35f * e), y - 0.0004f, 0.11);
                    if (key != null)
                    {
                        if (c != null) { DestroyMeshes(c); }
                        meshes[r] = new Cached { key = key, flat = fm, plump = pm, shadow = sm };
                    }
                    else { frameMeshes.Add(fm); frameMeshes.Add(pm); frameMeshes.Add(sm); }
                }
                Color tint = Tint(r);
                HoseLookMats hm = HoseMaterials.For(r);      // stage 3: the hose draws in its REEL's look
                if (sm != null) Graphics.DrawMesh(sm, Matrix4x4.identity, HoseMaterials.Shadow(0.55f + 0.3f * e), 0);
                if (fm != null) Graphics.DrawMesh(fm, Matrix4x4.identity, hm.Flat(1f - e), 0);
                if (pm != null) Graphics.DrawMesh(pm, Matrix4x4.identity, hm.Plump(e, tint), 0);
                DrawEnds(r, hm, lay, pts, vis, y + 0.001f);
            }
            // a transitioning hose's meshes live one frame
            for (int k = 0; k < oldFrame.Count; k++) if (oldFrame[k] != null) UnityEngine.Object.Destroy(oldFrame[k]);
            oldFrame.Clear();
            oldFrame.AddRange(frameMeshes);
            frameMeshes.Clear();
        }

        // early exits and exceptions skip DrawAll's tail: destroy whatever transitioning meshes are pending
        private void FlushFrameMeshes()
        {
            if (frameMeshes.Count == 0 && oldFrame.Count == 0) return;
            for (int k = 0; k < oldFrame.Count; k++) if (oldFrame[k] != null) UnityEngine.Object.Destroy(oldFrame[k]);
            for (int k = 0; k < frameMeshes.Count; k++) if (frameMeshes[k] != null) UnityEngine.Object.Destroy(frameMeshes[k]);
            oldFrame.Clear(); frameMeshes.Clear();
        }

        private readonly List<Mesh> frameMeshes = new List<Mesh>(), oldFrame = new List<Mesh>();

        private void DropMeshes(CompHoseReel r)
        {
            if (meshes.TryGetValue(r, out Cached c)) { DestroyMeshes(c); meshes.Remove(r); }
        }

        private static void DestroyMeshes(Cached c)
        {
            if (c.flat != null) UnityEngine.Object.Destroy(c.flat);
            if (c.plump != null) UnityEngine.Object.Destroy(c.plump);
            if (c.shadow != null) UnityEngine.Object.Destroy(c.shadow);
        }

        public static Color Tint(CompHoseReel r)
        {
            if (!HoseSettings.tintByContents) return Color.white;
            int[] rgb = HoseTint.Rgb(HoseSettings.defaultFluid);
            var fluid = new Color(rgb[0] / 255f, rgb[1] / 255f, rgb[2] / 255f);
            // wet darkening by 15%, faintly coloured by what it carries (design 3.4)
            return Color.Lerp(Color.white, fluid, 0.25f) * 0.85f + new Color(0, 0, 0, 0.15f);
        }

        // Art geometry (128 px canvases, measured 2026-10-02): the hose band in the coupling/nozzle/cap art is ~40
        // px tall (0.31 canvas); the coupling's brass face is at +0.46 canvas along +X, the nozzle tip at +0.47,
        // the cap face at +0.29; the hose enters every piece from the canvas's -X edge.
        /// <summary>RE-MEASURED 2026-10-04 (owner review B8, "mismatched hose width"): the opaque hose band where the hose
        /// enters Coupling_Brass/EndCap is 32 px of 128 (0.25), not the 0.31 first assumed, so every fitting was drawn ~20%
        /// narrower than the hose. validation.py O6 re-measures these from the PNGs.</summary>
        public const float PieceBand = (float)HoseMath.PieceBand;
        /// <summary>The coupling's brass face, canvas units along +X (measured 2026-10-02: 0.46).</summary>
        public const double JoinerFace = HoseMath.JoinerFace;
        /// <summary>Widest opaque band of each fitting (canvas fraction of 128 px; measured 2026-10-04, validation.py O6
        /// re-measures): Coupling_Brass 65, Nozzle 48, EndCap 44.</summary>
        public const float CouplingMax = (float)HoseMath.CouplingMax, NozzleMax = 0.375f, EndCapMax = 0.344f;
        /// <summary>Binding.png (make_hose_binding.py, 82x40, wrap along +X): the wrap's widest band, 38 px of 40.</summary>
        public const float BindBand = 0.95f;

        private int RankOf(CompHoseReel r)
        {
            int k = 0;
            foreach (CompHoseReel o in reels) if (o.parent.thingIDNumber < r.parent.thingIDNumber) k++;
            return k;
        }

        /// <summary>Both ends of every hose and both halves of every joiner (B22): a cloth binding wrap ~1.4 x the hose
        /// wide and 0.6 cell long covers the hose-to-fitting transition, then the fitting (sized never to read wider than
        /// the wrap) or, at an open free end, a plain dark mouth. The wrap is drawn over the fitting's hose stub.</summary>
        private void DrawEnds(CompHoseReel r, HoseLookMats hm, HoseLay lay, List<V2> pts, float vis, float y)
        {
            int n = pts.Count;
            Color wrapTint = Color.Lerp(Color.white, Tint(r), 0.5f);
            if (HoseStyles.AgedClothWrap(hm.look)) wrapTint *= new Color(0.86f, 0.80f, 0.70f, 1f);   // aged cloth, not white (Scrapper only)
            // reel end: a 1x1 reel's hose ends in a brass coupling whose face meets the reel, pointing into it. Round 5: the
            // 2x2 reel's hose runs on to the drum's axis under the opaque drum (HoseReelRect.Mouth), so nothing is drawn
            // there -- a coupling's body would reach back out past the drum into the gap above the base rail
            V2 d0 = (pts[0] - pts[Math.Min(3, n - 1)]).Norm();
            if (!r.Rect.HidesHoseEnd) Fitting(hm, hm.CouplingBare, CouplingMax, -JoinerFace, -0.03, pts[0], d0, vis, y, wrapTint);
            else lastReelEndHidden++;
            // joiners: only at real bends (B17), each two couplings face to face, screwed together (B9). Pose samples share
            // the lay's sample indices (equal-arc resamples of the same count).
            // round 4: the lay drew the hose dead straight over each joiner's run (HoseMath.StraightenAt), so the joiner's
            // axis is that run's chord, not the tangent at one sample
            double step = n > 1 ? Geo.Length(pts) / (n - 1) : 1;
            int m = Math.Max(1, (int)Math.Round(0.8 * HoseMath.JoinerHalf(vis) / Math.Max(1e-6, step)));
            foreach (int j0 in lay.Joints)
            {
                int j = Math.Min(n - 2, Math.Max(1, j0));
                V2 d = (pts[Math.Min(n - 1, j + m)] - pts[Math.Max(0, j - m)]).Norm();
                Fitting(hm, hm.CouplingBare, CouplingMax, -JoinerFace, -0.03, pts[j], d, vis, y, wrapTint);
                Fitting(hm, hm.CouplingBare, CouplingMax, -JoinerFace, -0.03, pts[j], -d, vis, y, wrapTint);
            }
            // free end: open (default), nozzle or cap, pointing out along the hose
            V2 d1 = (pts[n - 1] - pts[Math.Max(0, n - 4)]).Norm();
            if (RelayOf(r) != null)
            {
                // round 6: a hose feeding a relay reel ends in a brass coupling pointing into the relay. Round 7 (owner,
                // station 42: "pipe does NOT hook up properly to the next reel station"): its face sits ON the drawn reel
                // (the west brass inlet face to face, or the outline on the other sides; HoseRelay.DrawnEnd) and its axis
                // is the intake's, not the hose's last bend. Drawn in the hose band, under the reel sprite, so the reel's
                // own inlet overlaps the joint, never the other way round.
                EndPoint(r, out _, out V2? inward);
                V2 dIn = inward ?? d1;
                Fitting(hm, hm.CouplingBare, CouplingMax, -JoinerFace, -0.03, pts[n - 1], dIn, vis, y, wrapTint);
                lastRelayCouplings++;
            }
            else if (r.end == HoseEnd.Nozzle) Fitting(hm, hm.NozzleBare, NozzleMax, 0.05, -0.16, pts[n - 1], d1, vis, y, wrapTint);
            else if (r.end == HoseEnd.EndCap) Fitting(hm, hm.EndCapBare, EndCapMax, -0.10, -0.15, pts[n - 1], d1, vis, y, wrapTint);
            else
            {
                V2 e = pts[n - 1];
                // the wrap runs right to the cut (it hides the hose's square end), the dark bore sits on its outer face
                Wrap(hm, e - d1 * (HoseMath.WrapLength / 2 - 0.02), d1, vis, y + 0.0002f, wrapTint);
                PieceXZ(hm.Mouth, e - d1 * (0.10 * vis), d1, 0.30f * vis, 0.86f * vis, y + 0.0003f, Color.white);
            }
        }

        public int lastWrapDraws, lastFeedDraws, lastReelEndHidden, lastRelayCouplings;

        /// <summary>Owner review round 2 (2026-10-04, station 16: "the crappy hose reel disconnected from the pipe"): a reel
        /// beside a pipe or tank (HosePorts / HosePortRule) shows a short flat feed hose from under the reel to the port,
        /// with a brass coupling on the shared edge. Drawn in the hose band, below buildings, so under a tank it vanishes
        /// beneath the sprite instead of stopping at its outline; on a pipe it ends on the pipe's centreline.</summary>
        private void DrawFeed(CompHoseReel r, float y)
        {
            if (r.Port() == null) return;
            // the reel cell touching the port (2x2 reel: one of its edge cells), so the feed crosses the shared edge
            var touch = new Cell(r.portContact.X - r.portSide.X, r.portContact.Z - r.portSide.Z);
            HosePortRule.Feed(touch, r.portSide, out V2 from, out V2 to, out V2 coupling);
            float vis = (float)HoseMath.VisibleWidth(0, HoseSettings.plumpAmount);
            HoseLookMats hm = HoseMaterials.For(r);
            Material m = hm.Flat(1f);
            if (m == null) return;
            V2 d = (to - from).Norm();
            Mesh feed = Ribbon(new List<V2> { from, (from + to) * 0.5, to }, (float)HoseMath.MeshWidthFlat(vis), y - 0.0008f, 0.37);
            frameMeshes.Add(feed);
            Graphics.DrawMesh(feed, Matrix4x4.identity, m, 0);
            if (hm.CouplingBare != null)
                Piece(hm.CouplingBare, coupling, d, (float)HoseMath.FittingSize(vis, PieceBand, CouplingMax), y - 0.0006f);
            lastFeedDraws++;
        }

        /// <summary>Which reel art prints (B26, round 2): Graphic_HoseReel swaps stored/deployed on the map mesh (state read).</summary>
        public static string ReelGraphic(CompHoseReel r)
        {
            Graphic g = r.parent.Graphic;
            if (!(g is Graphic_HoseReel gr)) return "stored (graphic class is " + (g?.GetType().Name ?? "null") + ", not Graphic_HoseReel)";
            if (!r.laid) return "stored";
            return gr.HasDeployed && gr.MatAt(Rot4.North, r.parent) != gr.MatSingle ? "deployed" : "stored (stand-in: Reel_Deployed art missing)";
        }

        /// <summary>A fitting whose working end is at <paramref name="end"/> pointing along <paramref name="d"/>: its centre
        /// sits <paramref name="centreOff"/> sizes from the end, its brass starts <paramref name="brassFrom"/> sizes from the
        /// centre; the wrap ends 0.05 cell over the brass start and runs back along the hose.</summary>
        private void Fitting(HoseLookMats hm, Material m, float maxBand, double centreOff, double brassFrom, V2 end, V2 d, float vis, float y, Color wrapTint)
        {
            float size = (float)HoseMath.FittingSize(vis, PieceBand, maxBand);
            V2 c = end + d * (centreOff * size);
            Piece(m, c, d, size, y);
            V2 brass = c + d * (brassFrom * size);
            Wrap(hm, brass + d * (0.05 - HoseMath.WrapLength / 2), d, vis, y + 0.0002f, wrapTint);
        }

        private void Wrap(HoseLookMats hm, V2 centre, V2 d, float vis, float y, Color tint)
        {
            PieceXZ(hm.Binding, centre, d, (float)HoseMath.WrapLength, (float)HoseMath.WrapWidth(vis) / BindBand, y, tint);
            lastWrapDraws++;
        }

        private static void PieceXZ(Material m, V2 c, V2 dir, float sx, float sz, float y, Color tint)
        {
            if (m == null) return;
            float ang = Mathf.Atan2((float)dir.Z, (float)dir.X);
            if (tint != Color.white) m = HoseMaterials.Tinted(m, tint);
            Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(new Vector3((float)c.X, y, (float)c.Z), Quaternion.Euler(0f, -ang * Mathf.Rad2Deg, 0f),
                new Vector3(sx, 1f, sz)), m, 0);
        }

        private static void Piece(Material m, V2 c, V2 dir, float size, float y)
        {
            if (m == null) return;
            float ang = Mathf.Atan2((float)dir.Z, (float)dir.X);
            Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(new Vector3((float)c.X, y, (float)c.Z), Quaternion.Euler(0f, -ang * Mathf.Rad2Deg, 0f),
                new Vector3(size, 1f, size)), m, 0);
        }

        /// <summary>A strip along pts: u runs along it (tile = width x 4, the strips are 256x64), v across.</summary>
        public static Mesh Ribbon(List<V2> pts, float width, float y, double s0)
        {
            if (pts.Count < 2 || width <= 0) return null;
            var v = new List<Vector3>(pts.Count * 2);
            var uv = new List<Vector2>(pts.Count * 2);
            var tr = new List<int>(pts.Count * 6);
            float hw = width / 2f;
            double tile = width * 4.0, u = s0 * 4.0;
            for (int i = 0; i < pts.Count; i++)
            {
                Geo.TanNorm(pts, i, out V2 t, out V2 n);
                if (i > 0) u += V2.Dist(pts[i - 1], pts[i]) / tile;
                V2 l = pts[i] + n * hw, r = pts[i] - n * hw;
                v.Add(new Vector3((float)l.X, y, (float)l.Z));
                v.Add(new Vector3((float)r.X, y, (float)r.Z));
                uv.Add(new Vector2((float)u, 1f));
                uv.Add(new Vector2((float)u, 0f));
                if (i == 0) continue;
                int a = 2 * (i - 1);
                tr.Add(a); tr.Add(a + 2); tr.Add(a + 3);
                tr.Add(a); tr.Add(a + 3); tr.Add(a + 1);
            }
            var m = new Mesh { name = "RM_Hose" };
            m.SetVertices(v);
            m.SetUVs(0, uv);
            m.SetTriangles(tr, 0);
            m.RecalculateBounds();
            return m;
        }
    }

    /// <summary>One look's hose materials (per-build style stage 3): strands, binding wrap, coupling, nozzle, end cap and open
    /// mouth from that look's folder (HoseStyles.PathFor); the strand shadow is shared. A piece missing from a look's
    /// folder falls back to Scrapper's and is listed in <see cref="HoseMaterials.Missing"/> (a config error, logged once).</summary>
    public sealed class HoseLookMats
    {
        public string look;
        public Texture2D flatTex, plumpTex;
        public Material Binding, Mouth, CouplingBare, NozzleBare, EndCapBare;
        /// <summary>State read: piece name -> the texture path actually loaded (a fallback reads as Scrapper's path).</summary>
        public readonly Dictionary<string, string> paths = new Dictionary<string, string>();
        internal readonly Dictionary<long, Material> pool = new Dictionary<long, Material>();

        public Material Flat(float alpha) => HoseMaterials.Get(this, flatTex, 1, alpha, Color.white);
        public Material Plump(float alpha, Color tint) => HoseMaterials.Get(this, plumpTex, 2, alpha, tint);
    }

    [StaticConstructorOnStartup]
    public static class HoseMaterials
    {
        private static readonly Texture2D shadowTex;
        private static readonly Dictionary<long, Material> shadowPool = new Dictionary<long, Material>();
        private static readonly Dictionary<string, HoseLookMats> byLook = new Dictionary<string, HoseLookMats>();
        /// <summary>State read: look/piece pairs whose art was missing (drawn with Scrapper's piece instead).</summary>
        public static readonly List<string> Missing = new List<string>();
        public static readonly int Queue;
        /// <summary>Scrapper's set: the fallback for any look that cannot be resolved.</summary>
        public static readonly HoseLookMats Scrapper;

        static HoseMaterials()
        {
            Queue = Core.DrawOrder.HoseQueue(CordMaterials.StrandQueue);
            shadowTex = Tiled(HoseStyles.PathFor(HoseStyles.Scrapper, HoseStyles.SharedShadow), true);
            Scrapper = Build(HoseStyles.Scrapper, null);
            foreach (string l in Aerial.AerialStyles.Looks)
                if (l != HoseStyles.Scrapper) Build(l, Scrapper);
            foreach (string m in Missing) Log.Error("[MessyConduit] hose style art missing (Scrapper piece drawn instead): " + m);
        }

        private static HoseLookMats Build(string look, HoseLookMats fallback)
        {
            var s = new HoseLookMats { look = look };
            bool report = fallback == null;
            s.flatTex = TexOr(s, "Strand_Flat", true, report, fallback?.flatTex);
            s.plumpTex = TexOr(s, "Strand_Plump", true, report, fallback?.plumpTex);
            s.Binding = PieceOr(s, "Binding", report, fallback?.Binding);
            s.CouplingBare = PieceOr(s, "Coupling_Bare", report, fallback?.CouplingBare);
            s.NozzleBare = PieceOr(s, "Nozzle_Bare", report, fallback?.NozzleBare);
            s.EndCapBare = PieceOr(s, "EndCap_Bare", report, fallback?.EndCapBare);
            s.Mouth = PieceOr(s, "Mouth", report, fallback?.Mouth);
            byLook[look] = s;
            return s;
        }

        private static Texture2D TexOr(HoseLookMats s, string piece, bool tiled, bool report, Texture2D fb)
        {
            string p = HoseStyles.PathFor(s.look, piece);
            Texture2D t = tiled ? Tiled(p, report) : ContentFinder<Texture2D>.Get(p, reportFailure: report);
            if (t != null) { s.paths[piece] = p; return t; }
            if (fb != null) { Missing.Add(s.look + "/" + piece); s.paths[piece] = HoseStyles.PathFor(HoseStyles.Scrapper, piece); }
            return fb;
        }

        private static Material PieceOr(HoseLookMats s, string piece, bool report, Material fb)
        {
            string p = HoseStyles.PathFor(s.look, piece);
            Texture2D t = ContentFinder<Texture2D>.Get(p, reportFailure: report);
            if (t != null) { s.paths[piece] = p; return MaterialPool.MatFrom(new MaterialRequest(t, ShaderDatabase.Transparent) { renderQueue = Queue }); }
            if (fb != null) { Missing.Add(s.look + "/" + piece); s.paths[piece] = HoseStyles.PathFor(HoseStyles.Scrapper, piece); }
            return fb;
        }

        /// <summary>The materials of one look (an unknown look draws Scrapper's).</summary>
        public static HoseLookMats For(string look) => look != null && byLook.TryGetValue(look, out HoseLookMats s) ? s : Scrapper;

        /// <summary>The look a reel's hose draws in: the reel's own (stored style, or the default look for a legacy reel).</summary>
        public static string LookOf(CompHoseReel r) =>
            HoseStyles.HoseLook(r?.parent == null ? null : Aerial.StylePicker.LookOfThing(r.parent), Aerial.StylePicker.DefaultLook);

        public static HoseLookMats For(CompHoseReel r) => For(LookOf(r));

        public static bool Installed => Scrapper?.flatTex != null && Scrapper.plumpTex != null;

        private static Texture2D Tiled(string p, bool report)
        {
            Texture2D t = ContentFinder<Texture2D>.Get(p, reportFailure: report);
            if (t != null) t.wrapMode = TextureWrapMode.Repeat;
            return t;
        }

        private static readonly Dictionary<Material, Dictionary<int, Material>> tinted = new Dictionary<Material, Dictionary<int, Material>>();

        /// <summary>A piece material tinted (the binding takes half the hose's wet tint so it sits on any hose); pooled.</summary>
        public static Material Tinted(Material m, Color c)
        {
            int k = ((int)(c.r * 63) << 12) | ((int)(c.g * 63) << 6) | (int)(c.b * 63);
            if (!tinted.TryGetValue(m, out var byTint)) tinted[m] = byTint = new Dictionary<int, Material>();
            if (byTint.TryGetValue(k, out Material t)) return t;
            t = MaterialPool.MatFrom(new MaterialRequest((Texture2D)m.mainTexture, ShaderDatabase.Transparent, new Color(c.r, c.g, c.b, 1f)) { renderQueue = Queue });
            byTint[k] = t;
            return t;
        }

        /// <summary>Alpha quantised to 1/20 so the cross-fade reuses a handful of pooled materials (one pool per look).</summary>
        internal static Material Get(HoseLookMats s, Texture2D tex, int slot, float alpha, Color tint) =>
            Get(s?.pool ?? shadowPool, tex, slot, alpha, tint);

        private static Material Get(Dictionary<long, Material> pool, Texture2D tex, int slot, float alpha, Color tint)
        {
            if (tex == null) return null;
            int a = Mathf.Clamp(Mathf.RoundToInt(alpha * 20f), 0, 20);
            long key = ((long)slot << 40) ^ ((long)a << 32) ^ (long)(tint.r * 255) << 16 ^ (long)(tint.g * 255) << 8 ^ (long)(tint.b * 255);
            if (pool.TryGetValue(key, out Material m)) return m;
            m = MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent, new Color(tint.r, tint.g, tint.b, a / 20f)) { renderQueue = Queue });
            pool[key] = m;
            return m;
        }

        // B18: every hose material shares ONE render queue, so altitude alone orders them: a crossing hose (its own
        // altitude band, HoseMath.CrossLift) and all its fittings draw over the hose beneath, never interleaved. Within a
        // hose the shadow / flat / plump / fittings order is kept by their small altitude steps.
        public static Material Shadow(float alpha) => Get(shadowPool, shadowTex, 3, alpha, Color.white);
    }

    /// <summary>Keeps RM_MapComponent_Hoses out of the save (as the cord graph and aerial components): every
    /// MapComponent is written by class name, and a mod-less load of a save naming it logs "Could not find class".</summary>
    [HarmonyLib.HarmonyPatch(typeof(Map), "ExposeComponents")]
    internal static class Patch_Map_ExposeComponents_SkipHoses
    {
        internal sealed class Held { public int Index; public MapComponent Comp; }

        private static void Prefix(Map __instance, out Held __state)
        {
            __state = null;
            if (Scribe.mode != LoadSaveMode.Saving) return;
            List<MapComponent> list = __instance.components;
            int i = list.FindIndex(c => c is RM_MapComponent_Hoses);
            if (i < 0) return;
            __state = new Held { Index = i, Comp = list[i] };
            list.RemoveAt(i);
        }

        private static Exception Finalizer(Map __instance, Exception __exception, Held __state)
        {
            if (__state != null)
            {
                List<MapComponent> list = __instance.components;
                list.RemoveAll(c => c is RM_MapComponent_Hoses);
                list.Insert(Math.Min(__state.Index, list.Count), __state.Comp);
            }
            return __exception;
        }
    }
}

namespace RimMandrake.MessyConduit.Hose
{
    /// <summary>HOSE_BLOCKED_REROUTE_RETRACT_1's visible alert: reels whose hose was wound back in automatically in the last
    /// in-game day because no route within its length remained. Clears when the player lays the hose again.</summary>
    public class Alert_HoseRetracted : Alert
    {
        private readonly List<Thing> culprits = new List<Thing>();

        public Alert_HoseRetracted()
        {
            defaultLabel = "Hose reeled in";
            defaultPriority = AlertPriority.Medium;
        }

        private List<Thing> Culprits()
        {
            culprits.Clear();
            int now = Find.TickManager.TicksGame;
            foreach (Map m in Find.Maps)
            {
                RM_MapComponent_Hoses c = m.GetComponent<RM_MapComponent_Hoses>();
                if (c == null) continue;
                foreach (CompHoseReel r in c.Reels)
                    if (!r.laid && r.lastRetractReason != null && r.lastRetractTick >= 0 && now - r.lastRetractTick < GenDate.TicksPerDay)
                        culprits.Add(r.parent);
            }
            return culprits;
        }

        public override TaggedString GetExplanation()
        {
            var sb = new System.Text.StringBuilder("An obstacle cut these hoses' routes and no other route fits within the hose's length, so they were wound back onto the reel:\n");
            foreach (Thing t in culprits)
            {
                CompHoseReel rc = t.TryGetComp<CompHoseReel>();
                sb.Append("\n  - ").Append(t.LabelShort).Append(": ").Append(rc?.Explain(rc.lastRetractReason, rc.lastRetractNeed));
            }
            sb.Append("\n\nClear the way or lay the hose to a nearer cell.");
            return sb.ToString();
        }

        public override AlertReport GetReport() => HoseSettings.enabled ? AlertReport.CulpritsAre(Culprits()) : AlertReport.Inactive;
    }
}
