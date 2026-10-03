using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Text;
using HarmonyLib;
using RimMandrake.MessyConduit.Core;
using RimWorld;
using Verse;

namespace RimMandrake.MessyConduit
{
    /// <summary>
    /// The functional script's state-read channel (validation.py live tier). No companion tool is
    /// needed: the script writes <see cref="request"/> with the existing jawa/mod_settings_field
    /// tool (it reads/writes any public static field by type name), the current map's
    /// RM_MapComponent_CordGraph services it on its next MapComponentUpdate (every frame, paused or
    /// not), and the answer lands in <see cref="result"/> as JSON with <see cref="serial"/> bumped.
    ///
    /// Commands: census | fresh | poll | rebuild | set:&lt;settingsField&gt;=&lt;value&gt; | defaults
    /// Read-only except set/defaults (which also Apply) and poll/rebuild (cache refresh only).
    /// </summary>
    public static class MessyConduitProbe
    {
        public static string request = "";
        public static string result = "";
        public static int serial;

        public static void Service(Map map, RM_MapComponent_CordGraph comp)
        {
            if (string.IsNullOrEmpty(request) || Find.CurrentMap != map) return;
            string cmd = request.Trim();
            request = "";
            string res;
            try { res = Run(map, comp, cmd); }
            catch (Exception ex) { res = "{\"success\":false,\"cmd\":" + J.S(cmd) + ",\"error\":" + J.S(ex.ToString()) + "}"; }
            result = res;
            serial++;
        }

        private static string Run(Map map, RM_MapComponent_CordGraph comp, string cmd)
        {
            if (cmd == "census") return Census(map, comp);
            if (cmd == "rebuild") { comp.Rebuild(); return "{\"success\":true,\"cmd\":\"rebuild\",\"planned\":" + comp.LastPlanned + ",\"reused\":" + comp.LastReused + "}"; }
            if (cmd == "poll") { int f = comp.PollLive(); return "{\"success\":true,\"cmd\":\"poll\",\"flips\":" + f + "}"; }
            if (cmd == "fresh") return Fresh(map, comp);
            if (cmd == "artfit") return ArtFit(map, comp);
            if (cmd == "motion") return Motion(map, comp);
            if (cmd == "motionreset")
            {
                for (int i = 0; i < RM_MapComponent_CordGraph.DownedHist.Length; i++) RM_MapComponent_CordGraph.DownedHist[i] = 0;
                RM_MapComponent_CordGraph.SparksThrown = 0;
                RM_MapComponent_CordGraph.DripEvents = 0;
                return "{\"success\":true,\"cmd\":\"motionreset\"}";
            }
            if (cmd.StartsWith("select:"))
            {
                // select the first powered thing at x,z (validation's selection-highlight row, B5)
                string[] xz = cmd.Substring(7).Split(',');
                var c = new IntVec3(int.Parse(xz[0], CultureInfo.InvariantCulture), 0, int.Parse(xz[1], CultureInfo.InvariantCulture));
                Thing t = c.InBounds(map) ? c.GetThingList(map).FirstOrDefault(x => x.TryGetComp<CompPower>() != null) : null;
                Find.Selector.ClearSelection();
                if (t != null) Find.Selector.Select(t, playSound: false, forceDesignatorDeselect: false);
                return "{\"success\":" + J.B(t != null) + ",\"cmd\":" + J.S(cmd) + ",\"thing\":" + J.S(t?.def.defName) + "}";
            }
            if (cmd == "deselect") { Find.Selector.ClearSelection(); return "{\"success\":true,\"cmd\":\"deselect\"}"; }
            if (cmd == "defaults")
            {
                MessyConduitSettings.ResetToDefaults();
                MessyConduitSettings.Apply();
                return "{\"success\":true,\"cmd\":\"defaults\"}";
            }
            if (cmd.StartsWith("set:"))
            {
                string[] kv = cmd.Substring(4).Split(new[] { '=' }, 2);
                FieldInfo fi = typeof(MessyConduitSettings).GetField(kv[0], BindingFlags.Public | BindingFlags.Static);
                if (fi == null) return "{\"success\":false,\"error\":\"no settings field " + kv[0] + "\"}";
                object v = fi.FieldType.IsEnum ? Enum.Parse(fi.FieldType, kv[1]) : Convert.ChangeType(kv[1], fi.FieldType, CultureInfo.InvariantCulture);
                fi.SetValue(null, v);
                MessyConduitSettings.Apply();
                return "{\"success\":true,\"cmd\":" + J.S(cmd) + ",\"value\":" + J.S(Convert.ToString(fi.GetValue(null), CultureInfo.InvariantCulture)) + "}";
            }
            if (cmd.StartsWith("rect:")) return RectCensus(map, comp, cmd.Substring(5));   // lane E matrix runner
            if (cmd == "styles") return StyleProbe.Report(map, comp);                       // lane C art styles
            if (cmd == "settingsroundtrip") return StyleProbe.SettingsRoundTrip();         // lane C
            return "{\"success\":false,\"error\":\"unknown command " + J.S(cmd).Trim('"') + "\"}";
        }

        /// <summary>Lane E (Northstar matrix runner, 2026-10-02): the census restricted to one scene's rect
        /// "x,z,w,h[,maxPts]" -- every graph node inside it (type, cell, live, wall terminal), the cord edges with an
        /// end inside it, its laid pieces (strands, decals, unwalkable vertices, per-edge hashes, a scene geometry
        /// hash), the strand bounding box (sprawl), the distinct power nets of the transmitters inside it, and the
        /// laid vertices themselves (decimated to maxPts) for the screenshot wire mask. Read-only.</summary>
        private static string RectCensus(Map map, RM_MapComponent_CordGraph comp, string args)
        {
            int[] a = args.Split(',').Select(s => int.Parse(s.Trim(), CultureInfo.InvariantCulture)).ToArray();
            int x0 = a[0], z0 = a[1], x1 = a[0] + a[2] - 1, z1 = a[1] + a[3] - 1, maxPts = a.Length > 4 ? a[4] : 4000;
            bool In(int x, int z) => x >= x0 && x <= x1 && z >= z0 && z <= z1;
            var sb = new StringBuilder("{\"success\":true,\"cmd\":\"rect\"");
            void F(string k, string v) => sb.Append(",\"").Append(k).Append("\":").Append(v);
            F("ticksGame", Find.TickManager.TicksGame.ToString());
            F("enabled", J.B(MessyConduitSettings.enabled));
            F("rect", "[" + x0 + "," + z0 + "," + a[2] + "," + a[3] + "]");
            var nets = new HashSet<PowerNet>();
            foreach (PowerNet n in map.powerNetManager.AllNetsListForReading)
                if (n.transmitters.Any(t => t?.parent != null && In(t.parent.Position.x, t.parent.Position.z))) nets.Add(n);
            F("nets", nets.Count.ToString());
            F("netsLive", nets.Count(n => n.HasActivePowerSource).ToString());
            CordGraph gr = comp.Graph;
            if (gr == null || !MessyConduitSettings.enabled) { sb.Append(",\"graph\":false}"); return sb.ToString(); }
            F("graph", "true");
            F("conduitCells", gr.Cells.Count(c => In(c.X, c.Z)).ToString());
            var nodes = new List<string>();
            foreach (CordNode nd in gr.Nodes.Values.Where(n => In(n.Cell.X, n.Cell.Z)))
            {
                PowerNet net = map.powerNetGrid.TransmittedPowerNetAt(CordWorldAdapter.I(nd.Cell));
                bool? reg = comp.EndLive(nd.Cell);
                nodes.Add("{\"t\":" + J.S(nd.OracleName) + ",\"c\":[" + nd.Cell.X + "," + nd.Cell.Z + "],\"netLive\":" +
                          J.B(net != null && net.HasActivePowerSource) + ",\"reg\":" + (reg.HasValue ? J.B(reg.Value) : "null") +
                          ",\"wt\":" + J.B(nd.WallTerminal) + "}");
            }
            F("nodes", J.Arr(nodes));
            int edges = 0, across = 0, unnetted = 0;
            foreach (CordEdge e in gr.CordEdges())
            {
                Cell ca = gr.CellOf(e.A), cb = gr.CellOf(e.B);
                if (!In(ca.X, ca.Z) && !In(cb.X, cb.Z)) continue;
                edges++;
                PowerNet na = map.powerNetGrid.TransmittedPowerNetAt(CordWorldAdapter.I(ca));
                PowerNet nb = map.powerNetGrid.TransmittedPowerNetAt(CordWorldAdapter.I(cb));
                if (na == null || nb == null) unnetted++; else if (na != nb) across++;
            }
            F("cordEdges", edges.ToString());
            F("cordsAcrossNets", across.ToString());
            F("cordEndsWithoutNet", unnetted.ToString());
            CordWorld w = comp.LastWorld;
            var mine = comp.Pieces.Where(p => In(p.Owner.X, p.Owner.Z)).OrderBy(p => p.Key, StringComparer.Ordinal).ToList();
            int strands = 0, bad = 0, fell = 0, unroutable = 0, total = 0;
            double bx0 = double.MaxValue, bz0 = double.MaxValue, bx1 = double.MinValue, bz1 = double.MinValue;
            foreach (LaidPiece p in mine)
            {
                if (p.Unroutable) unroutable++;
                foreach (CordStrand s in p.Strands)
                {
                    strands++;
                    if (s.FellBack) fell++;
                    total += s.Pts.Count;
                    foreach (V2 q in s.Pts) { bx0 = Math.Min(bx0, q.X); bz0 = Math.Min(bz0, q.Z); bx1 = Math.Max(bx1, q.X); bz1 = Math.Max(bz1, q.Z); }
                    if (s.OverFace || w == null) continue;
                    for (int i = 1; i < s.Pts.Count - 1; i++) if (!w.IsWalkable(s.Pts[i].Floor)) bad++;
                }
            }
            F("pieces", mine.Count.ToString());
            F("strands", strands.ToString());
            F("verticesInUnwalkable", bad.ToString());
            F("fellBack", fell.ToString());
            F("unroutable", unroutable.ToString());
            F("laidPoints", total.ToString());
            F("strandBBox", strands == 0 ? "null" : "[" + J.D(bx0) + "," + J.D(bz0) + "," + J.D(bx1) + "," + J.D(bz1) + "]");
            F("decals", "{" + string.Join(",", mine.SelectMany(p => p.Decals).GroupBy(d => d.Kind.ToString()).OrderBy(x => x.Key)
                .Select(x => J.S(x.Key) + ":" + x.Count())) + "}");
            var ends = new List<string>();
            foreach (LaidPiece p in mine)
                foreach (CordEnd e in p.Ends)
                {
                    PowerNet net = map.powerNetGrid.TransmittedPowerNetAt(CordWorldAdapter.I(e.NetCell));
                    bool? reg = comp.EndLive(e.NetCell);
                    ends.Add("{\"cell\":[" + e.NetCell.X + "," + e.NetCell.Z + "],\"wall\":" + J.B(e.Wall) + ",\"registryLive\":" +
                             (reg.HasValue ? J.B(reg.Value) : "null") + ",\"netLive\":" + J.B(net != null && net.HasActivePowerSource) + "}");
                }
            F("ends", J.Arr(ends));
            ulong hsh = 1469598103934665603UL;
            var per = new List<string>();
            foreach (LaidPiece p in mine.Where(x => x.EndA != null))
            {
                ulong h = p.GeometryHash();
                hsh = (hsh ^ h) * 1099511628211UL;
                per.Add(J.S(EdgeName(p)) + ":" + J.S(h.ToString("x16")));
            }
            F("edgeHashes", "{" + string.Join(",", per) + "}");
            F("geometryHash", J.S(hsh.ToString("x16")));
            int stride = Math.Max(1, (total + maxPts - 1) / Math.Max(1, maxPts));
            var lines = new List<string>();
            foreach (LaidPiece p in mine)
                foreach (CordStrand s in p.Strands)
                {
                    var pts = new List<string>();
                    for (int i = 0; i < s.Pts.Count; i += stride) pts.Add("[" + J.D(s.Pts[i].X) + "," + J.D(s.Pts[i].Z) + "]");
                    V2 last = s.Pts[s.Pts.Count - 1];
                    if ((s.Pts.Count - 1) % stride != 0) pts.Add("[" + J.D(last.X) + "," + J.D(last.Z) + "]");
                    if (pts.Count >= 2) lines.Add("[" + string.Join(",", pts) + "]");
                }
            F("polyStride", stride.ToString());
            F("polylines", J.Arr(lines));
            sb.Append("}");
            return sb.ToString();
        }

        private static string EdgeName(LaidPiece p) => p.EndA + "|" + p.EndB;

        private static string Fresh(Map map, RM_MapComponent_CordGraph comp)
        {
            CordWorld w = CordWorldAdapter.Snapshot(map);
            var b = new CordBuilder();
            List<LaidPiece> fresh = b.Build(w, MessyConduitSettings.BuildOptions(), c => CordWorldAdapter.IsLive(map, c));
            var cur = comp.Pieces.Where(p => p.EndA != null).ToDictionary(p => p.Key, p => p.GeometryHash());
            int same = 0, diff = 0, missing = 0;
            foreach (LaidPiece p in fresh.Where(p => p.EndA != null))
            {
                if (!cur.TryGetValue(p.Key, out ulong h)) missing++;
                else if (h == p.GeometryHash()) same++;
                else diff++;
            }
            return "{\"success\":true,\"cmd\":\"fresh\",\"edges\":" + fresh.Count(p => p.EndA != null) + ",\"same\":" + same +
                   ",\"different\":" + diff + ",\"missing\":" + missing + "}";
        }

        /// <summary>Polish pass 2026-10-02: the art-fit audit on the LIVE laid pieces (the same
        /// Core.CordAudit the SelfTest runs), every decal's pose, the render queues our materials hold,
        /// and the queue/shader/altitude of whatever wall and rock edifices our stubs sit on.</summary>
        private static string ArtFit(Map map, RM_MapComponent_CordGraph comp)
        {
            if (comp.Graph == null) return "{\"success\":false,\"error\":\"no graph\"}";
            ArtFitResult r = CordAudit.ArtFit(comp.Graph, comp.Pieces.ToList(), c => comp.EndLive(c) ?? CordWorldAdapter.IsLive(map, c));
            var sb = new StringBuilder("{\"success\":true,\"cmd\":\"artfit\"");
            void F(string k, string v) => sb.Append(",\"").Append(k).Append("\":").Append(v);
            F("faults", r.Faults.ToString());
            F("junctions", r.Junctions.ToString()); F("junctionFaults", r.JunctionFaults.ToString());
            F("plugEnds", r.PlugEnds.ToString()); F("plugFaults", r.PlugFaults.ToString());
            F("stubs", r.Stubs.ToString()); F("stubFaults", r.StubFaults.ToString());
            F("deadEnds", r.DeadEnds.ToString()); F("deadFaults", r.DeadFaults.ToString());
            F("deadOffLine", J.Arr(r.DeadOffLine.Select(J.D)));
            F("liveEnds", r.LiveEnds.ToString()); F("liveFaults", r.LiveFaults.ToString());
            F("liveArrivalDeg", J.Arr(r.LiveArrivalDeg.Select(J.D)));
            F("messages", J.Arr(r.Messages.Take(12).Select(J.S)));
            F("decalList", J.Arr(comp.Pieces.SelectMany(p => p.Decals).Select(d =>
                "{\"k\":" + J.S(d.Kind.ToString()) + ",\"x\":" + J.D(d.Pos.X) + ",\"z\":" + J.D(d.Pos.Z) + ",\"deg\":" + J.D(d.Angle * 180 / Math.PI) + ",\"s\":" + J.D(d.Scale) + "}")));
            F("queues", "{\"strand\":" + CordMaterials.StrandQueue + ",\"shadow\":" + (CordMaterials.Shadow?.renderQueue ?? -1) +
                        ",\"piece\":" + (CordMaterials.Decal(DecalKind.JunctionTin)?.renderQueue ?? -1) +
                        ",\"face\":" + (CordMaterials.Decal(DecalKind.StubWall)?.renderQueue ?? -1) +
                        ",\"strandFace\":" + (CordMaterials.StrandFace?.renderQueue ?? -1) + "}");
            F("altitudes", "{\"conduits\":" + J.D(AltitudeLayer.Conduits.AltitudeFor()) + ",\"building\":" + J.D(AltitudeLayer.Building.AltitudeFor()) +
                           ",\"face\":" + J.D(AltitudeLayer.BuildingOnTop.AltitudeFor() + SectionLayer_RM_MessyCords.FaceLift) + "}");
            var seen = new List<string>();
            foreach (CordNode nd in comp.Graph.Nodes.Values.Where(n => n.Type == NodeType.StubWall || n.Type == NodeType.StubRock))
            {
                Building ed = map.edificeGrid[CordWorldAdapter.I(nd.Buried)];
                if (ed == null) continue;
                UnityEngine.Material m = ed.Graphic?.MatSingle;
                if (ed.Graphic is Graphic_Linked gl) m = gl.SubGraphic?.MatSingle ?? m;
                seen.Add("{\"node\":" + J.S(nd.Type.ToString()) + ",\"def\":" + J.S(ed.def.defName) + ",\"shader\":" + J.S(m?.shader?.name) +
                         ",\"queue\":" + (m?.renderQueue ?? -1) + ",\"altitude\":" + J.D(ed.def.Altitude) + "}");
            }
            F("faceEdifices", J.Arr(seen));
            F("glowDraws", RM_MapComponent_CordGraph.LastGlowDraws.ToString());
            sb.Append("}");
            return sb.ToString();
        }

        /// <summary>Phase 1b lane A state reads: whip/sway/highlight counters of the last drawn frame, the
        /// downed-wire state histogram since motionreset, LOD and cutscene state, and per-net cord counts.</summary>
        private static string Motion(Map map, RM_MapComponent_CordGraph comp)
        {
            var sb = new StringBuilder("{\"success\":true,\"cmd\":\"motion\"");
            void F(string k, string v) => sb.Append(",\"").Append(k).Append("\":").Append(v);
            F("ticksGame", Find.TickManager.TicksGame.ToString());
            F("paused", J.B(Find.TickManager.Paused));
            F("frame", UnityEngine.Time.frameCount.ToString());
            F("whipDraws", RM_MapComponent_CordGraph.WhipDraws.ToString());
            int whipTails = comp.Pieces.Sum(p => p.Strands.Sum(x => (x.WhipA > 0 ? 1 : 0) + (x.WhipB > 0 ? 1 : 0)));
            F("whipTails", whipTails.ToString());
            int liveFloorEnds = comp.Pieces.Sum(p => p.Ends.Count(e => !e.Wall && (comp.EndLive(e.NetCell) ?? false)));
            int deadFloorEnds = comp.Pieces.Sum(p => p.Ends.Count(e => !e.Wall && !(comp.EndLive(e.NetCell) ?? false)));
            F("liveFloorEnds", liveFloorEnds.ToString());
            F("deadFloorEnds", deadFloorEnds.ToString());
            F("swayMode", J.S("CPU"));
            F("plantWindSway", J.B(Prefs.PlantWindSway));
            F("windSpeed", J.D(map.windManager.WindSpeed));
            F("swayAmplitude", J.D(MessyConduitSettings.swayAmplitude));
            F("liftedStrands", comp.Pieces.Sum(p => p.Strands.Count(x => x.Lifted)).ToString());
            F("liftedSwaying", comp.Pieces.Sum(p => p.Strands.Count(x => x.Lifted && RM_MapComponent_CordGraph.SwaysNow(map, x))).ToString());
            F("swayDraws", RM_MapComponent_CordGraph.SwayDraws.ToString());
            F("swayVerts", RM_MapComponent_CordGraph.SwayVerts.ToString());
            F("swayHash", J.S(RM_MapComponent_CordGraph.SwayHash.ToString("x16")));
            F("downedHist", "{\"Drip\":" + RM_MapComponent_CordGraph.DownedHist[0] + ",\"Flash\":" + RM_MapComponent_CordGraph.DownedHist[1] +
                            ",\"Quiet\":" + RM_MapComponent_CordGraph.DownedHist[2] + ",\"Crackle\":" + RM_MapComponent_CordGraph.DownedHist[3] + "}");
            F("dripEvents", RM_MapComponent_CordGraph.DripEvents.ToString());
            F("sparksThrown", RM_MapComponent_CordGraph.SparksThrown.ToString());
            F("liveWallEnds", comp.Pieces.Sum(p => p.Ends.Count(e => e.Wall && (comp.EndLive(e.NetCell) ?? false))).ToString());
            F("glowDraws", RM_MapComponent_CordGraph.LastGlowDraws.ToString());
            F("highlightCords", RM_MapComponent_CordGraph.HighlightCords.ToString());
            F("highlightStubs", RM_MapComponent_CordGraph.HighlightStubs.ToString());
            F("highlightNet", J.S(RM_MapComponent_CordGraph.HighlightNetId));
            PowerNet sel = comp.SelectedNet();
            F("selectedNet", J.S(sel?.GetHashCode().ToString()));
            var perNet = comp.Pieces.GroupBy(p => comp.NetOf(p.Owner)?.GetHashCode().ToString() ?? "none")
                .Select(gp => J.S(gp.Key) + ":" + gp.Sum(p => p.Strands.Count));
            F("cordsPerNet", "{" + string.Join(",", perNet) + "}");
            F("lodSetting", J.B(MessyConduitSettings.lod));
            F("zoom", J.S(Find.CameraDriver.CurrentZoom.ToString()));
            F("lodFarNow", J.B(SectionLayer_RM_MessyCords.FarNow));
            F("lastDrawFar", J.B(SectionLayer_RM_MessyCords.LastDrawFar));
            int lodSm = 0, lodOn = 0, fullSm = 0, fullOn = 0;
            var sections = Traverse.Create(map.mapDrawer).Field("sections").GetValue<Section[,]>();
            if (sections != null)
                foreach (Section sec in sections)
                    foreach (SectionLayer l in Traverse.Create(sec).Field("layers").GetValue<List<SectionLayer>>())
                    {
                        if (!(l is SectionLayer_RM_MessyCords)) continue;
                        foreach (LayerSubMesh m in l.subMeshes.Where(m => m.finalized && m.verts.Count > 0))
                        {
                            if (CordMaterials.IsLod(m.material)) { lodSm++; if (!m.disabled) lodOn++; }
                            else { fullSm++; if (!m.disabled) fullOn++; }
                        }
                    }
            F("lodSubMeshes", lodSm.ToString()); F("lodEnabled", lodOn.ToString());
            F("fullSubMeshes", fullSm.ToString()); F("fullEnabled", fullOn.ToString());
            F("cutsceneInProgress", J.B(WorldComponent_GravshipController.CutsceneInProgress));
            F("cutsceneHides", J.B(SectionLayer_RM_MessyCords.CutsceneHides));
            F("cutsceneSkips", SectionLayer_RM_MessyCords.CutsceneSkips.ToString());
            CordGraph g = comp.Graph;
            if (g != null)
            {
                F("tangles", g.Nodes.Values.Count(n => n.Type == NodeType.Tangle).ToString());
                F("tangleMinUsed", g.tangleMin.ToString());
                F("mergedStubs", g.MergedStubs.ToString());
                F("stubs", g.Nodes.Values.Count(n => n.IsStub).ToString());
            }
            var settled = comp.Pieces.SelectMany(p => p.Strands).Where(x => x.Settle != null).ToList();
            F("settledStrands", settled.Count.ToString());
            F("settleMaxStretch", J.D(settled.Count == 0 ? 0 : settled.Max(x => x.Settle.MaxStretch)));
            F("settleMaxLenDev", J.D(settled.Count == 0 ? 0 : settled.Max(x => Math.Abs(x.Settle.SettledLen / Math.Max(1e-9, x.Settle.RestLen) - 1))));
            F("endHeaps", settled.Sum(x => x.Settle.EndHeaps).ToString());
            F("litStrips", comp.Pieces.Sum(p => p.Decals.Count(d => d.Kind == DecalKind.PowerStrip)).ToString());
            F("darkStrips", comp.Pieces.Sum(p => p.Decals.Count(d => d.Kind == DecalKind.PowerStripDark)).ToString());
            F("lastRebuildMs", J.D(comp.LastRebuildMs));
            F("laidPoints", comp.Pieces.Sum(p => p.Strands.Sum(x => x.Pts.Count)).ToString());
            sb.Append("}");
            return sb.ToString();
        }

        private static string Census(Map map, RM_MapComponent_CordGraph comp)
        {
            var sb = new StringBuilder("{\"success\":true,\"cmd\":\"census\"");
            void F(string k, string v) => sb.Append(",\"").Append(k).Append("\":").Append(v);
            F("ticksGame", Find.TickManager.TicksGame.ToString());
            F("enabled", J.B(MessyConduitSettings.enabled));
            F("settings", "{" + string.Join(",", typeof(MessyConduitSettings).GetFields(BindingFlags.Public | BindingFlags.Static)
                .Select(f => J.S(f.Name) + ":" + J.S(Convert.ToString(f.GetValue(null), CultureInfo.InvariantCulture)))) + "}");
            F("invisibleApplied", J.B(ConduitVisuals.Applied));
            F("texPaths", "{" + string.Join(",", ConduitVisuals.CurrentTexPaths().Select(kv => J.S(kv.Key) + ":" + J.S(kv.Value))) + "}");
            // what a spawned PowerConduit actually renders with: the linked graphic's inner texture
            Thing anyConduit = map.listerThings.AllThings.FirstOrDefault(t => ConduitVisuals.IsTarget(t.def));
            string tex = null;
            if (anyConduit != null)
            {
                Graphic g = anyConduit.Graphic;
                Graphic inner = g is Graphic_Linked gl ? gl.SubGraphic : g;
                tex = inner?.MatSingle?.mainTexture?.name;
            }
            F("spawnedConduitTexture", J.S(tex));
            F("hookupWiresSuppressed", ConduitVisuals.HookupWiresSuppressed.ToString());
            F("overlayWiresPrinted", ConduitVisuals.OverlayWiresPrinted.ToString());
            F("builds", comp.Builds.ToString());
            F("lastPlanned", comp.LastPlanned.ToString());
            F("lastReused", comp.LastReused.ToString());
            CordGraph gr = comp.Graph;
            CordWorld w = comp.LastWorld;
            if (gr != null && w != null && MessyConduitSettings.enabled)
            {
                F("conduitCells", gr.Cells.Count.ToString());
                F("buriedCells", gr.BuriedCells.Count.ToString());
                F("nodeTypes", "{" + string.Join(",", gr.Nodes.Values.GroupBy(n => n.OracleName).OrderBy(x => x.Key)
                    .Select(x => J.S(x.Key) + ":" + x.Count())) + "}");
                F("cordEdges", gr.CordEdges().Count().ToString());
                F("hiddenEdges", gr.Edges.Count(e => e.Hidden).ToString());
                // design §8.2.2 / walk line 2: no cord edge joins two different PowerNets
                int across = 0, unnetted = 0;
                var crossing = new List<string>();
                foreach (CordEdge e in gr.CordEdges())
                {
                    PowerNet na = map.powerNetGrid.TransmittedPowerNetAt(CordWorldAdapter.I(gr.CellOf(e.A)));
                    PowerNet nb = map.powerNetGrid.TransmittedPowerNetAt(CordWorldAdapter.I(gr.CellOf(e.B)));
                    if (na == null || nb == null) unnetted++;
                    else if (na != nb) { across++; crossing.Add(gr.Nodes[e.A].Cell + "-" + gr.Nodes[e.B].Cell); }
                }
                F("cordsAcrossNets", across.ToString());
                F("cordsAcrossNetsList", J.Arr(crossing.Select(J.S)));
                F("cordEndsWithoutNet", unnetted.ToString());
                int strands = 0, bad = 0, vtx = 0, fell = 0, unroutable = 0;
                foreach (LaidPiece p in comp.Pieces)
                {
                    if (p.Unroutable) unroutable++;
                    foreach (CordStrand s in p.Strands)
                    {
                        strands++;
                        if (s.FellBack) fell++;
                        if (s.OverFace) continue;
                        for (int i = 1; i < s.Pts.Count - 1; i++)
                        {
                            vtx++;
                            if (!w.IsWalkable(s.Pts[i].Floor)) bad++;
                        }
                    }
                }
                F("pieces", comp.Pieces.Count.ToString());
                F("decals", "{" + string.Join(",", comp.Pieces.SelectMany(p => p.Decals).GroupBy(d => d.Kind.ToString()).OrderBy(x => x.Key)
                    .Select(x => J.S(x.Key) + ":" + x.Count())) + "}");
                F("strands", strands.ToString());
                F("interiorVertices", vtx.ToString());
                F("verticesInUnwalkable", bad.ToString());
                F("fellBack", fell.ToString());
                F("unroutable", unroutable.ToString());
                var ends = new List<string>();
                foreach (LaidPiece p in comp.Pieces)
                    foreach (CordEnd e in p.Ends)
                    {
                        PowerNet net = map.powerNetGrid.TransmittedPowerNetAt(CordWorldAdapter.I(e.NetCell));
                        bool? reg = comp.EndLive(e.NetCell);
                        ends.Add("{\"cell\":[" + e.NetCell.X + "," + e.NetCell.Z + "],\"tip\":[" + J.D(e.Tip.X) + "," + J.D(e.Tip.Z) +
                                 "],\"wall\":" + J.B(e.Wall) + ",\"registryLive\":" + (reg.HasValue ? J.B(reg.Value) : "null") +
                                 ",\"netLive\":" + J.B(net != null && net.HasActivePowerSource) + ",\"net\":" + (net == null ? "null" : J.S(net.GetHashCode().ToString())) + "}");
                    }
                F("ends", J.Arr(ends));
                ulong total = 1469598103934665603UL;
                var per = new List<string>();
                foreach (LaidPiece p in comp.Pieces.Where(x => x.EndA != null).OrderBy(x => x.Key, StringComparer.Ordinal))
                {
                    ulong h = p.GeometryHash();
                    total = (total ^ h) * 1099511628211UL;
                    per.Add(J.S(EdgeName(p)) + ":" + J.S(h.ToString("x16")));
                }
                F("edgeHashes", "{" + string.Join(",", per) + "}");
                F("geometryHash", J.S(total.ToString("x16")));
            }
            // what the drawer and the vanilla overlay actually hold in their section meshes
            int ourVerts = 0, ourSections = 0, connectorVerts = 0;
            bool ourVisible = false;
            var sections = Traverse.Create(map.mapDrawer).Field("sections").GetValue<Section[,]>();
            if (sections != null)
                foreach (Section s in sections)
                {
                    var layers = Traverse.Create(s).Field("layers").GetValue<List<SectionLayer>>();
                    foreach (SectionLayer l in layers)
                    {
                        if (l is SectionLayer_RM_MessyCords)
                        {
                            ourVisible |= l.Visible;
                            int v = l.subMeshes.Where(m => m.finalized).Sum(m => m.verts.Count);
                            ourVerts += v;
                            if (v > 0) ourSections++;
                        }
                        else if (l is SectionLayer_ThingsPowerGrid)
                            connectorVerts += l.subMeshes.Where(m => m.material == PowerOverlayMats.MatConnectorLine).Sum(m => m.verts.Count);
                    }
                }
            F("layerVisible", J.B(ourVisible));
            F("layerVerts", ourVerts.ToString());
            F("layerSectionsWithCords", ourSections.ToString());
            F("overlayConnectorVerts", connectorVerts.ToString());
            sb.Append("}");
            return sb.ToString();
        }

        /// <summary>Tiny JSON helpers (the game ships no JSON library we may rely on).</summary>
        private static class J
        {
            public static string S(string s)
            {
                if (s == null) return "null";
                var b = new StringBuilder("\"");
                foreach (char c in s)
                {
                    if (c == '"' || c == '\\') b.Append('\\').Append(c);
                    else if (c < 32) b.Append("\\u").Append(((int)c).ToString("x4"));
                    else b.Append(c);
                }
                return b.Append('"').ToString();
            }
            public static string B(bool b) => b ? "true" : "false";
            public static string D(double d) => d.ToString("0.###", CultureInfo.InvariantCulture);
            public static string Arr(IEnumerable<string> items) => "[" + string.Join(",", items) + "]";
        }
    }
}
