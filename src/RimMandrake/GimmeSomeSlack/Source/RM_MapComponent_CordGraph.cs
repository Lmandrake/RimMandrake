using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.GimmeSomeSlack
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
        public double LastRebuildMs;
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

        /// <summary>Lane F 2026-10-02: a change dirtied a section that is OFF SCREEN. Vanilla only regenerates
        /// sections overlapping the view (Section.TryUpdate), so the rebuild that our layer's regenerate triggers
        /// never ran and the pieces lagged the map until the camera looked (live: the 18-scene aerial board's
        /// fresh probe found one edge the component had not laid). MapComponentUpdate rebuilds once instead.</summary>
        public bool StaleOffscreen;
        public int OffscreenRebuilds;

        // ---- lane C (2026-10-02): per-net strand variant (extension-cord colour, Star Wars cable kind)
        private Dictionary<LaidPiece, int> netSeeds = new Dictionary<LaidPiece, int>();

        /// <summary>The strand variant of a piece: its cord net's seed through CordMaterials.VariantFor, so every
        /// cord of one connected net shares a colour and the pick is the same on every rebuild and after a load.</summary>
        public int VariantOf(LaidPiece p) => CordMaterials.VariantFor(netSeeds.TryGetValue(p, out int s) ? s : 0);

        public int NetSeedOf(LaidPiece p) => netSeeds.TryGetValue(p, out int s) ? s : 0;

        // ---- stage 2 (per-build style, conduit runs): each piece's material by (style, colour / kind) of its run
        private Dictionary<LaidPiece, int> matIdx = new Dictionary<LaidPiece, int>();
        private HashSet<LaidPiece> legacyPieces = new HashSet<LaidPiece>();
        private HashSet<LaidPiece> mixPieces = new HashSet<LaidPiece>();

        /// <summary>A piece of a Modern "random mix" run. Round 5: it is ONE colour from node to node (ConduitStyles.MixPieceColours,
        /// already in its material index), the colours varying piece to piece; the static and moving layers both draw that.</summary>
        public bool IsMix(LaidPiece p) => mixPieces.Contains(p);

        /// <summary>The flat material index (CordMaterials.StrandG / DecalG) a piece prints with: from the stored style of the
        /// conduit cell it is coloured by (Aerial.ConduitStyles.PieceVariant); a piece with no styled cell is LEGACY and draws
        /// the default look's pre-stage-2 per-net pick (CordMaterials.LegacyGlobal), exactly as before.</summary>
        public int MatIndexOf(LaidPiece p) => matIdx.TryGetValue(p, out int g) ? g : CordMaterials.LegacyGlobal(NetSeedOf(p));

        public bool IsLegacy(LaidPiece p) => !matIdx.ContainsKey(p) || legacyPieces.Contains(p);

        /// <summary>The cell a piece takes its style from, and that cell's stored (look, colour): conduit cells first (they
        /// carry the Modern colour), then a switch or anchor of the run. Null look = legacy.</summary>
        public static string StyleCellOf(LaidPiece p, Dictionary<Cell, Aerial.CellStyle> cells, out Cell at, out string colour)
        {
            at = p.Owner; colour = null;
            Aerial.CellStyle best = null;
            foreach (Cell c in CandidateCells(p))
            {
                if (!cells.TryGetValue(c, out Aerial.CellStyle cs)) continue;
                if (best == null || (cs.Conduit && !best.Conduit)) { best = cs; at = c; }
                if (best.Conduit) break;
            }
            if (best == null) return null;
            colour = best.Colour;
            return best.Look;
        }

        private static IEnumerable<Cell> CandidateCells(LaidPiece p)
        {
            yield return p.Owner;
            if (p.EndA != null && TryCell(p.EndA, out Cell a)) yield return a;
            if (p.EndB != null && TryCell(p.EndB, out Cell b)) yield return b;
        }

        public static bool TryCell(string end, out Cell c)
        {
            c = default(Cell);
            int i = end.LastIndexOf(':');
            string t = i >= 0 ? end.Substring(i + 1) : end;
            int k = t.IndexOf(',');
            if (k <= 0) return false;
            if (!int.TryParse(t.Substring(0, k), out int x) || !int.TryParse(t.Substring(k + 1), out int z)) return false;
            c = new Cell(x, z);
            return true;
        }

        private void ComputeMaterials(List<LaidPiece> ps, Dictionary<Cell, Aerial.CellStyle> cells)
        {
            var next = new Dictionary<LaidPiece, int>();
            var leg = new HashSet<LaidPiece>();
            var mix = new HashSet<LaidPiece>();
            bool single = GimmeSomeSlackSettings.extCordColorMode == ExtCordColorMode.Single;
            foreach (LaidPiece p in ps)
            {
                int seed = NetSeedOf(p);
                string look = StyleCellOf(p, cells, out Cell at, out string colour);
                if (look == null) { next[p] = CordMaterials.LegacyGlobal(seed); leg.Add(p); continue; }
                int v = Aerial.ConduitStyles.PieceVariant(look, colour, at.X, at.Z, seed, single, GimmeSomeSlackSettings.extCordColor);
                if (look == "Modern" && colour == Aerial.ConduitStyles.Mix) mix.Add(p);
                next[p] = Aerial.ConduitStyles.Global(look, v);
            }
            // round 5: a mix piece's colour is its own, one per piece node to node, neighbours differing (MixPieceColours)
            if (mix.Count > 0)
            {
                string Tok(string end) { int i = end.LastIndexOf(':'); return i >= 0 ? end.Substring(i + 1) : end; }
                // the colour key is the piece's endpoint key (before the first '#'): a live/dead flip or a re-lay keeps the colour
                string CKey(LaidPiece p) { string k = p.Key ?? (p.Owner.X + "," + p.Owner.Z); int h = k.IndexOf('#'); return h > 0 ? k.Substring(0, h) : k; }
                var input = mix.Select(p => new KeyValuePair<string, string[]>(CKey(p),
                    p.EndA != null || p.EndB != null ? new[] { p.EndA != null ? Tok(p.EndA) : null, p.EndB != null ? Tok(p.EndB) : null }
                                                     : new[] { p.Owner.X + "," + p.Owner.Z })).ToList();
                Dictionary<string, int> col = Aerial.ConduitStyles.MixPieceColours(input);
                foreach (LaidPiece p in mix)
                    if (col.TryGetValue(CKey(p), out int c)) next[p] = Aerial.ConduitStyles.Global("Modern", c);
            }
            matIdx = next;
            legacyPieces = leg;
            mixPieces = mix;
        }

        /// <summary>Union the pieces by the cells they touch (edge ends, node/coil/tangle owner cells); a component's
        /// seed is a stable FNV hash of its smallest cell token -- pure geometry, no vanilla PowerNet (which is not
        /// built yet while a loaded map's sections first regenerate).</summary>
        private static Dictionary<LaidPiece, int> ComputeNetSeeds(List<LaidPiece> ps)
        {
            var parent = new Dictionary<string, string>();
            string Find(string x)
            {
                if (!parent.TryGetValue(x, out string px)) { parent[x] = x; return x; }
                while (px != x) { string g = parent[px]; parent[x] = g; x = px; px = g; }
                return x;
            }
            void Union(string a, string b)
            {
                string ra = Find(a), rb = Find(b);
                if (ra == rb) return;
                if (string.CompareOrdinal(ra, rb) < 0) parent[rb] = ra; else parent[ra] = rb;
            }
            string Tok(string end) { int i = end.LastIndexOf(':'); return i >= 0 ? end.Substring(i + 1) : end; }
            var first = new Dictionary<LaidPiece, string>();
            foreach (LaidPiece p in ps)
            {
                string own = p.Owner.X + "," + p.Owner.Z;
                string a = p.EndA != null ? Tok(p.EndA) : own;
                Find(a);
                if (p.EndB != null) Union(a, Tok(p.EndB));
                first[p] = a;
            }
            var res = new Dictionary<LaidPiece, int>();
            foreach (KeyValuePair<LaidPiece, string> kv in first)
            {
                string root = Find(kv.Value);          // roots are the ordinal-smallest token (Union keeps the smaller)
                uint h = 2166136261u;
                foreach (char c in root) h = unchecked((h ^ c) * 16777619u);
                res[kv.Key] = unchecked((int)h);
            }
            return res;
        }

        public void Rebuild()
        {
            builtFrame = Time.frameCount;
            if (!GimmeSomeSlackSettings.enabled)
            {
                pieces = new List<LaidPiece>();
                bySection = new Dictionary<IntVec2, List<LaidPiece>>();
                return;
            }
            var sw = System.Diagnostics.Stopwatch.StartNew();
            CordWorld world = CordWorldAdapter.Snapshot(map);
            LastWorld = world;
            CordBuilder b = builder;
            List<LaidPiece> next;
            BuildOptions opt = GimmeSomeSlackSettings.BuildOptions();
            Dictionary<Cell, Aerial.CellStyle> styled = Aerial.ConduitStylePicker.CellStyles(map);
            // stage 2: each run's pile art follows ITS look (strips in Modern, junction boxes otherwise); unstyled = default
            opt.PileAt = c => styled.TryGetValue(c, out Aerial.CellStyle cs) ? (cs.Look == "Modern" ? PileArt.Strips : PileArt.Junctions) : (PileArt?)null;
            try { next = b.Build(world, opt, c => LiveNow(c)); }
            catch (Exception ex)
            {
                if (!buildErrorLogged) { buildErrorLogged = true; Log.Error("[GimmeSomeSlack] cord build failed, drawing no cords: " + ex); }
                next = new List<LaidPiece>();
            }
            Builds++;
            LastRebuildMs = sw.Elapsed.TotalMilliseconds;
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
            Dictionary<LaidPiece, int> prevSeeds = netSeeds;
            try { netSeeds = ComputeNetSeeds(next); }
            catch (Exception ex) { netSeeds = new Dictionary<LaidPiece, int>(); Log.ErrorOnce("[GimmeSomeSlack] net seeds: " + ex, 0x4d43_5345); }
            Dictionary<LaidPiece, int> prevMat = matIdx;
            try { ComputeMaterials(next, styled); }
            catch (Exception ex) { matIdx = new Dictionary<LaidPiece, int>(); legacyPieces = new HashSet<LaidPiece>(); mixPieces = new HashSet<LaidPiece>(); Log.ErrorOnce("[GimmeSomeSlack] run styles: " + ex, 0x4d43_5346); }
            // dirty every section whose owned set changed (not just the regenerating one)
            if (Current.ProgramState == ProgramState.Playing)
            {
                var keys = new HashSet<IntVec2>(nextBy.Keys);
                keys.UnionWith(prevBy.Keys);
                foreach (IntVec2 s in keys)
                    if (Sig(prevBy, s, prevSeeds, prevMat) != Sig(nextBy, s, netSeeds, matIdx)) DirtySection(s);
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
            map.mapDrawer.MapMeshDirty(loc, GimmeSomeSlackDefOf.RM_MessyCords);
        }

        /// <summary>A section's owned-set signature: piece keys, geometry, and (lane C) the net seed, so a net that
        /// merges or splits reprints the sections whose cords change colour even when their geometry did not.</summary>
        private static string Sig(Dictionary<IntVec2, List<LaidPiece>> d, IntVec2 s, Dictionary<LaidPiece, int> seeds, Dictionary<LaidPiece, int> mats) =>
            d.TryGetValue(s, out List<LaidPiece> l)
                ? string.Join("\n", l.Select(p => p.Key + "@" + p.GeometryHash() + "#" + (seeds.TryGetValue(p, out int v) ? v : 0) +
                                                  "%" + (mats.TryGetValue(p, out int g) ? g : -1)))
                : "";

        private bool LiveNow(Cell c)
        {
            bool v = CordWorldAdapter.IsLive(map, c);
            liveEnds[c] = v;
            return v;
        }

        public override void MapComponentTick()
        {
            if (!GimmeSomeSlackSettings.enabled) return;
            int t = Find.TickManager.TicksGame;
            if (t % 250 == map.uniqueID % 250) PollLive();
            if (SparksAllowed) Sparks(t);
        }

        /// <summary>Re-read live/dead for every conduit end and every LED key (tangle / device strips,
        /// phase 1b B6); a flip dirties its owner section only.</summary>
        public int PollLive()
        {
            int flips = 0;
            foreach (LaidPiece p in pieces)
            {
                foreach (CordEnd e in p.Ends) flips += Flip(p, e.NetCell);
                foreach (Cell c in p.LiveKeys) flips += Flip(p, c);
            }
            return flips;
        }

        private int Flip(LaidPiece p, Cell c)
        {
            bool now = CordWorldAdapter.IsLive(map, c);
            if (liveEnds.TryGetValue(c, out bool was) && was == now) return 0;
            liveEnds[c] = now;
            map.mapDrawer.MapMeshDirty(CordWorldAdapter.I(p.Owner), GimmeSomeSlackDefOf.RM_MessyCords);
            return 1;
        }

        public bool? EndLive(Cell c) => liveEnds.TryGetValue(c, out bool v) ? v : (bool?)null;

        private static int MaxSparkingEnds => Mathf.Clamp(GimmeSomeSlackSettings.maxSparkingEnds, 1, 200);
        public static int LastGlowDraws;

        /// <summary>Sparks/glow allowed right now (break readout on, intensity, the overlay-only option).</summary>
        private static bool SparksAllowed =>
            GimmeSomeSlackSettings.breakReadout && GimmeSomeSlackSettings.sparkIntensity > 0.01f &&
            (!GimmeSomeSlackSettings.sparksOnlyOverlay || OverlayDrawHandler.ShouldDrawPowerGrid);

        /// <summary>The live half of the break readout, every frame and while paused: a flickering
        /// glow at each live tip (the sparks are thrown flecks and only fly while time runs).</summary>
        private void DrawLiveGlow()
        {
            LastGlowDraws = 0;
            if (!GimmeSomeSlackSettings.enabled || !SparksAllowed) return;
            if (Find.CurrentMap != map || CordMaterials.LiveGlow == null || RimWorld.Planet.WorldRendererUtility.WorldSelected) return;
            if (SectionLayer_RM_MessyCords.CutsceneHides) return;
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
                    float size = (0.38f + 0.42f * f * f) * Mathf.Min(1.5f, GimmeSomeSlackSettings.sparkIntensity);
                    // a downed wire's glow follows its burst schedule: a 2x flash, brief pops, an ember between
                    if (e.Wall && GimmeSomeSlackSettings.downedWire && downed.TryGetValue(e.NetCell, out DownedWireSchedule dw))
                        size = (float)(0.45 * dw.Glow(t)) * Mathf.Min(1.5f, GimmeSomeSlackSettings.sparkIntensity);
                    var pos = new Vector3((float)e.Tip.X, y, (float)e.Tip.Z);
                    Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(pos, Quaternion.identity, new Vector3(size, 1f, size)), CordMaterials.LiveGlow, 0);
                    LastGlowDraws++;
                }
        }

        private void Sparks(int tick)
        {
            int n = 0;
            float k = GimmeSomeSlackSettings.sparkIntensity;
            foreach (LaidPiece p in pieces)
                foreach (CordEnd e in p.Ends)
                {
                    if (!liveEnds.TryGetValue(e.NetCell, out bool live) || !live) continue;
                    if (++n > MaxSparkingEnds) return;
                    if (e.Wall && GimmeSomeSlackSettings.downedWire) continue;   // the drip schedule owns wall ends
                    int h = (e.NetCell.X * 73856093) ^ (e.NetCell.Z * 19349663);
                    int period = Mathf.Max(12, Mathf.RoundToInt((e.Wall ? 50 : 80) / k));
                    if ((tick + (h & 0x7fff)) % period != 0) continue;
                    var at = new Vector3((float)e.Tip.X, AltitudeLayer.MoteOverhead.AltitudeFor(), (float)e.Tip.Z);
                    FleckMaker.ThrowMicroSparks(at, map);
                    SparksThrown++;
                    if (((tick / period + h) & 3) == 0) FleckMaker.ThrowLightningGlow(at, map, e.Wall ? 0.6f : 0.4f);
                }
        }

        // ================================================================ phase 1b lane A: motion
        // Whip (B3), downed-wire bursts (B4), selection highlight (B5), wind sway of lifted pieces (B7,
        // CPU path). All runtime-only, drawn from MapComponentUpdate with two dynamic meshes rebuilt per
        // frame for what is on screen; nothing here touches the static section meshes.
        private bool motionErrorLogged;
        private readonly Dictionary<Cell, DownedWireSchedule> downed = new Dictionary<Cell, DownedWireSchedule>();
        private Mesh hiMesh;
        /// <summary>Per strand variant (lane C): one whip mesh and one sway mesh each, drawn with that variant's material.</summary>
        private readonly Mesh[] floorMeshes = new Mesh[16], faceMeshes = new Mesh[16], rippleMeshes = new Mesh[16];
        private readonly List<Vector3> mv = new List<Vector3>();
        private readonly List<Vector2> mu = new List<Vector2>();
        private readonly List<int> mt = new List<int>();
        private PowerNet hiNet;
        private int hiBuilds = -1;
        public static int WhipDraws, WhipStillDraws, SwayDraws, SwayVerts, HighlightCords, HighlightStubs, SparksThrown, DripEvents;
        public static ulong SwayHash, RippleHash;
        public static int RippleDraws, RippleVerts;
        public static float LastWind;
        public static readonly int[] DownedHist = new int[4];
        public static string HighlightNetId;

        /// <summary>Does this lifted strand sway right now (so the static layer leaves it out)? Setting on,
        /// strength > 0, vanilla's plant-sway preference on, and not under a roof (design §8.4: 0 under a roof).</summary>
        public static bool SwaysNow(Map map, CordStrand s)
        {
            if (!SwayOn || EffectiveSwayMode(out _) != SwayMode.CPU) return false;
            if (s.Pts == null || s.Pts.Count < 2 || s.SwayW == null) return false;
            return !PinRoofed(map, s);
        }

        /// <summary>Sway is wanted at all: setting on, strength > 0, vanilla's plant-sway preference on.</summary>
        public static bool SwayOn => GimmeSomeSlackSettings.sway && GimmeSomeSlackSettings.swayAmplitude > 0.01f && Prefs.PlantWindSway;

        /// <summary>A lifted strand's pin cell (where it leaves the wall) is roofed, or off the map.</summary>
        public static bool PinRoofed(Map map, CordStrand s)
        {
            IntVec3 c = CordWorldAdapter.I(s.Pts[0].Floor);
            return !c.InBounds(map) || map.roofGrid.Roofed(c);
        }

        private static System.Reflection.FieldInfo plantMatsField;
        /// <summary>WindManager's private static plant material list (reflection): the shader route only moves a
        /// material that is in it, because WindManagerTick writes _SwayHead to exactly that list.</summary>
        public static bool RegisteredWithWind(Material m)
        {
            if (m == null) return false;
            if (plantMatsField == null)
                plantMatsField = typeof(WindManager).GetField("plantMaterials", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static);
            return plantMatsField?.GetValue(null) is List<Material> l && l.Contains(m);
        }

        /// <summary>The sway route actually used: Shader only when chosen AND the CutoutPlant strand material exists, uses
        /// that shader and is registered with WindManager; otherwise CPU (the safe fallback). reason says why.</summary>
        public static SwayMode EffectiveSwayMode(out string reason)
        {
            if (GimmeSomeSlackSettings.swayMode != SwayMode.Shader) { reason = "cpu (setting)"; return SwayMode.CPU; }
            Material m = CordMaterials.StrandPlant;
            if (ShaderDatabase.CutoutPlant == null || m == null) { reason = "fallback: no CutoutPlant strand material"; return SwayMode.CPU; }
            if (m.shader != ShaderDatabase.CutoutPlant) { reason = "fallback: strand material shader is " + m.shader?.name; return SwayMode.CPU; }
            if (!RegisteredWithWind(m)) { reason = "fallback: material not registered with WindManager"; return SwayMode.CPU; }
            reason = "shader";
            return SwayMode.Shader;
        }

        /// <summary>The section layer prints this lifted strand with the plant shader (vertex alpha = sway weight).</summary>
        public static bool ShaderSwayPrints(CordStrand s) =>
            s.Lifted && s.SwayW != null && s.Pts != null && s.Pts.Count >= 2 && SwayOn && EffectiveSwayMode(out _) == SwayMode.Shader;

        /// <summary>Optional floor ripple: a plain floor strand (not lifted, not over a face, no whip tail) whose middle
        /// cell is unroofed ripples per frame while the setting (default OFF) and the game's plant sway are on.</summary>
        public static bool RipplesNow(Map map, CordStrand s)
        {
            if (!GimmeSomeSlackSettings.floorRipple || GimmeSomeSlackSettings.swayAmplitude <= 0.01f || !Prefs.PlantWindSway) return false;
            if (s.Lifted || s.OverFace || s.WhipA > 0 || s.WhipB > 0 || s.Pts == null || s.Pts.Count < 3) return false;
            IntVec3 c = CordWorldAdapter.I(s.Pts[s.Pts.Count / 2].Floor);
            return c.InBounds(map) && !map.roofGrid.Roofed(c);
        }

        private static Mesh Fresh(ref Mesh m)
        {
            if (m == null) { m = new Mesh { name = "RM_MessyCords_Motion" }; m.indexFormat = UnityEngine.Rendering.IndexFormat.UInt32; m.MarkDynamic(); }
            return m;
        }

        private void Flush(ref Mesh m, Material mat)
        {
            Mesh mesh = Fresh(ref m);
            mesh.Clear();
            if (mv.Count == 0 || mat == null) return;
            mesh.SetVertices(mv);
            mesh.SetUVs(0, mu);
            mesh.SetTriangles(mt, 0);
            mesh.RecalculateBounds();
            Graphics.DrawMesh(mesh, Matrix4x4.identity, mat, 0);
        }

        private void DrawMotion()
        {
            WhipDraws = 0; WhipStillDraws = 0; SwayDraws = 0; SwayVerts = 0; HighlightCords = 0; HighlightStubs = 0; RippleDraws = 0; RippleVerts = 0;
            if (!GimmeSomeSlackSettings.enabled || Find.CurrentMap != map || RimWorld.Planet.WorldRendererUtility.WorldSelected) return;
            if (SectionLayer_RM_MessyCords.CutsceneHides) return;
            if (SectionLayer_RM_MessyCords.FarNow) return;            // far zoom: LOD only, no motion
            CellRect view = Find.CameraDriver.CurrentViewRect.ExpandedBy(3);
            float now = Time.realtimeSinceStartup;
            float baseY = AltitudeLayer.Conduits.AltitudeFor() + 0.002f;
            float faceY = AltitudeLayer.BuildingOnTop.AltitudeFor() + SectionLayer_RM_MessyCords.FaceLift;
            bool whip = GimmeSomeSlackSettings.whip && GimmeSomeSlackSettings.breakReadout;
            // ---- B3 whipping live tails (floor)
            // stage 2: one mesh per flat material index (every look's strands), each piece in its own run's material
            int nv = Mathf.Clamp(CordMaterials.GlobalCount, 1, floorMeshes.Length);
            int cap = MaxSparkingEnds * 3;
            for (int v = 0; v < nv; v++)
            {
            mv.Clear(); mu.Clear(); mt.Clear();
            if (whip)
                foreach (LaidPiece p in pieces)
                {
                    if (nv > 1 && MatIndexOf(p) != v) continue;
                    foreach (CordStrand s in p.Strands)
                    {
                        if (s.WhipA <= 0 && s.WhipB <= 0) continue;
                        for (int side = 0; side < 2; side++)
                        {
                            bool atStart = side == 0;
                            int cnt = atStart ? s.WhipA : s.WhipB;
                            if (cnt <= 0) continue;
                            V2 tip = atStart ? s.Pts[cnt - 1] : s.Pts[s.Pts.Count - cnt];   // outer end of the tail; test it before allocating
                            if (!view.Contains(CordWorldAdapter.I(tip.Floor))) continue;
                            List<V2> tail = atStart ? s.Pts.GetRange(0, cnt) : s.Pts.GetRange(s.Pts.Count - cnt, cnt);
                            if (atStart) tail.Reverse();                       // tail[0] = the joint
                            ulong seed = CordRng.Hash("whip", p.Key, s.S0, atStart);
                            // GPT source read 2026-10-06 A10: tails past the motion cap used to be drawn by NEITHER path (the section
                            // layer leaves every whip tail to this one); past the cap they are drawn still, at their laid pose
                            bool animate = WhipDraws < cap;
                            List<V2> bent = animate ? CordMotion.Whip(tail, now, seed, 0.12) : tail;
                            SectionLayer_RM_MessyCords.RibbonInto(mv, mu, mt, bent, SectionLayer_RM_MessyCords.StrandWidth, baseY, s.S0);
                            if (animate) WhipDraws++; else WhipStillDraws++;
                            Material fray = CordMaterials.DecalG(DecalKind.FrayLive, v);
                            if (fray != null)
                            {
                                V2 d = bent[bent.Count - 1] - bent[Math.Max(0, bent.Count - 3)];
                                float ang = (float)Math.Atan2(d.Z, d.X);
                                var pos = new Vector3((float)bent[bent.Count - 1].X, baseY + 0.009f, (float)bent[bent.Count - 1].Z);
                                // decal +X along the cord: rotate the plane so its +X maps to the angle
                                Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(pos, Quaternion.Euler(0f, -ang * Mathf.Rad2Deg, 0f), new Vector3(0.5f, 1f, 0.5f)), fray, 0);
                            }
                        }
                    }
                }
            Flush(ref floorMeshes[v], CordMaterials.StrandG(v));
            }
            // ---- B7 sway of lifted pieces (wall-hanging tails), CPU path, game-time clock
            float wind = map.windManager.WindSpeed;
            LastWind = wind;
            double gt = Find.TickManager.TicksGame / 60.0;
            ulong h = 1469598103934665603UL;
            for (int v = 0; v < nv; v++)
            {
            mv.Clear(); mu.Clear(); mt.Clear();
            foreach (LaidPiece p in pieces)
                foreach (CordStrand s in p.Strands)
                {
                    if (nv > 1 && MatIndexOf(p) != v) continue;
                    if (!s.Lifted || !SwaysNow(map, s)) continue;
                    if (!view.Contains(CordWorldAdapter.I(s.Pts[0].Floor))) continue;
                    List<V2> sw = CordMotion.Sway(s.Pts, s.SwayW, gt, CordRng.Hash("sway", p.Key), 0.12 * GimmeSomeSlackSettings.swayAmplitude, wind);
                    SectionLayer_RM_MessyCords.RibbonInto(mv, mu, mt, sw, SectionLayer_RM_MessyCords.StrandWidth, faceY, s.S0);
                    foreach (V2 q in sw)
                    {
                        h = (h ^ unchecked((ulong)(long)Math.Round(q.X * 10000))) * 1099511628211UL;
                        h = (h ^ unchecked((ulong)(long)Math.Round(q.Z * 10000))) * 1099511628211UL;
                    }
                    SwayDraws++;
                }
            SwayVerts += mv.Count;
            Flush(ref faceMeshes[v], CordMaterials.StrandFaceG(v) ?? CordMaterials.StrandG(v));
            }
            SwayHash = h;
            // ---- optional floor ripple (default off): unroofed plain floor strands on screen, game-time clock
            ulong rh = 1469598103934665603UL;
            if (GimmeSomeSlackSettings.floorRipple)
                for (int v = 0; v < nv; v++)
                {
                    mv.Clear(); mu.Clear(); mt.Clear();
                    foreach (LaidPiece p in pieces)
                    {
                        if (nv > 1 && MatIndexOf(p) != v) continue;
                        int si = 0;
                        foreach (CordStrand s in p.Strands)
                        {
                            si++;
                            if (!RipplesNow(map, s)) continue;
                            if (!view.Contains(CordWorldAdapter.I(s.Pts[s.Pts.Count / 2].Floor))) continue;
                            List<V2> rp = CordMotion.Ripple(s.Pts, gt, CordRng.Hash("ripple", p.Key, si), CordMotion.RippleAmp * GimmeSomeSlackSettings.swayAmplitude, wind);
                            SectionLayer_RM_MessyCords.RibbonInto(mv, mu, mt, rp, SectionLayer_RM_MessyCords.StrandWidth, baseY, s.S0);
                            foreach (V2 q in rp)
                            {
                                rh = (rh ^ unchecked((ulong)(long)Math.Round(q.X * 10000))) * 1099511628211UL;
                                rh = (rh ^ unchecked((ulong)(long)Math.Round(q.Z * 10000))) * 1099511628211UL;
                            }
                            RippleDraws++;
                        }
                    }
                    RippleVerts += mv.Count;
                    Flush(ref rippleMeshes[v], CordMaterials.StrandG(v));
                }
            RippleHash = rh;
            // ---- B4 downed-wire bursts at live wall terminals (real-time schedule; flecks only while time runs)
            if (GimmeSomeSlackSettings.downedWire && SparksAllowed) DownedWires(now);
            // ---- B5 selection highlight
            if (GimmeSomeSlackSettings.highlight) DrawHighlight(baseY);
        }

        private void DownedWires(float now)
        {
            bool paused = Find.TickManager.Paused;
            int n = 0;
            foreach (LaidPiece p in pieces)
                foreach (CordEnd e in p.Ends)
                {
                    if (!e.Wall) continue;
                    if (!liveEnds.TryGetValue(e.NetCell, out bool live) || !live) { downed.Remove(e.NetCell); continue; }
                    if (++n > MaxSparkingEnds) return;
                    if (!downed.TryGetValue(e.NetCell, out DownedWireSchedule dw))
                        downed[e.NetCell] = dw = new DownedWireSchedule(CordRng.Hash("downed", e.NetCell.X, e.NetCell.Z, map.uniqueID), now);
                    if (dw.Due(now))
                    {
                        dw.Advance(now);
                        DownedHist[(int)dw.State]++;
                        DripEvents++;
                        thrownOf[e.NetCell] = 0;
                        if (!paused && dw.State == DripState.Flash)
                            FleckMaker.ThrowLightningGlow(new Vector3((float)e.Tip.X, AltitudeLayer.MoteOverhead.AltitudeFor(), (float)e.Tip.Z), map, 0.8f * Mathf.Min(1.5f, GimmeSomeSlackSettings.sparkIntensity));
                    }
                    if (paused) continue;
                    thrownOf.TryGetValue(e.NetCell, out int done);
                    int due = dw.SparksDue(now);
                    for (; done < due; done++)
                    {
                        var loc = new Vector3((float)e.Tip.X + Rand.Range(-0.06f, 0.06f), AltitudeLayer.MoteOverhead.AltitudeFor(), (float)e.Tip.Z);
                        if (!loc.ShouldSpawnMotesAt(map)) continue;
                        FleckCreationData d = FleckMaker.GetDataStatic(loc, map, FleckDefOf.MicroSparks, Rand.Range(0.7f, 1.1f));
                        d.rotationRate = Rand.Range(-12f, 12f);
                        d.velocityAngle = Rand.Range(160f, 200f);           // screen-down: the sparks fall down the face
                        d.velocitySpeed = Rand.Range(0.5f, 1.3f);
                        map.flecks.CreateFleck(d);
                        SparksThrown++;
                    }
                    thrownOf[e.NetCell] = done;
                }
        }
        private readonly Dictionary<Cell, int> thrownOf = new Dictionary<Cell, int>();

        /// <summary>The net of whatever powered thing is selected (a conduit, a battery, a lamp), or null.</summary>
        public PowerNet SelectedNet()
        {
            if (Find.Selector == null) return null;
            foreach (object o in Find.Selector.SelectedObjectsListForReading)
            {
                if (!(o is ThingWithComps t) || t.Map != map) continue;
                CompPower cp = t.TryGetComp<CompPower>();
                if (cp?.PowerNet != null) return cp.PowerNet;
            }
            return null;
        }

        public PowerNet NetOf(Cell c) => map.powerNetGrid.TransmittedPowerNetAt(CordWorldAdapter.I(c));

        private void DrawHighlight(float baseY)
        {
            PowerNet net = SelectedNet();
            HighlightNetId = net == null ? null : net.GetHashCode().ToString();
            if (net == null || CordMaterials.Highlight == null) { hiNet = null; return; }
            if (net != hiNet || hiBuilds != Builds || hiMesh == null)
            {
                hiNet = net;
                hiBuilds = Builds;
                mv.Clear(); mu.Clear(); mt.Clear();
                hiCount = 0;
                float y = AltitudeLayer.BuildingOnTop.AltitudeFor() + SectionLayer_RM_MessyCords.FaceLift + 0.004f;
                foreach (LaidPiece p in pieces)
                {
                    if (NetOf(p.Owner) != net) continue;
                    foreach (CordStrand s in p.Strands)
                    {
                        SectionLayer_RM_MessyCords.RibbonInto(mv, mu, mt, s.Pts, SectionLayer_RM_MessyCords.StrandWidth + 0.02f, y, s.S0);
                        hiCount++;
                    }
                }
                Mesh m = Fresh(ref hiMesh);
                m.Clear();
                if (mv.Count > 0) { m.SetVertices(mv); m.SetUVs(0, mu); m.SetTriangles(mt, 0); m.RecalculateBounds(); }
            }
            HighlightCords = hiCount;
            if (hiMesh.vertexCount > 0) Graphics.DrawMesh(hiMesh, Matrix4x4.identity, CordMaterials.Highlight, 0);
            // a buried run's openings read as one: a ring at every stub on the net
            CordGraph g = builder.Graph;
            if (g == null) return;
            float ry = AltitudeLayer.MetaOverlays.AltitudeFor();
            foreach (CordNode nd in g.Nodes.Values)
            {
                if (!nd.IsStub || NetOf(nd.Cell) != net) continue;
                GenDraw.DrawCircleOutline(new Vector3((float)nd.Face.X, ry, (float)nd.Face.Z), 0.3f, SimpleColor.Yellow);
                HighlightStubs++;
            }
        }
        private int hiCount;

        public override void MapComponentUpdate()
        {
            if (StaleOffscreen)
            {
                StaleOffscreen = false;
                if (builtFrame != Time.frameCount && GimmeSomeSlackSettings.enabled) { Rebuild(); OffscreenRebuilds++; }
            }
            GimmeSomeSlackProbe.Service(map, this);
            DrawLiveGlow();
            try { DrawMotion(); }
            catch (Exception ex)
            {
                if (!motionErrorLogged) { motionErrorLogged = true; Log.Error("[GimmeSomeSlack] per-frame cord motion failed, skipping it: " + ex); }
            }
            if (!GimmeSomeSlackSettings.enabled || !GimmeSomeSlackSettings.debugDraw || Find.CurrentMap != map) return;
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

    /// <summary>Marks the map's cord graph stale on every mesh-dirty event for our layer's flags that lands outside the
    /// view (TryUpdate regenerates only sections overlapping the view; see StaleOffscreen). Hooking the dirty event
    /// itself, not Section.dirtyFlags, catches the 2nd+ change to a section whose bits are already set, keeps one
    /// rebuild per dirty event, and holds no per-section state (nothing to leak after a map is discarded).</summary>
    [HarmonyLib.HarmonyPatch(typeof(MapDrawer), nameof(MapDrawer.MapMeshDirty), new[] { typeof(IntVec3), typeof(ulong), typeof(bool), typeof(bool) })]
    internal static class Patch_MapDrawer_MapMeshDirty_MarkStale
    {
        private static ulong mask;

        private static void Prefix(MapDrawer __instance, IntVec3 loc, ulong dirtyFlags)
        {
            if (!GimmeSomeSlackSettings.enabled) return;
            if (mask == 0UL)
                mask = (ulong)MapMeshFlagDefOf.Buildings | (ulong)MapMeshFlagDefOf.PowerGrid | (ulong)MapMeshFlagDefOf.Terrain |
                       (ulong)MapMeshFlagDefOf.FogOfWar | (ulong)MapMeshFlagDefOf.Roofs;
            if ((dirtyFlags & mask) == 0UL) return;
            Map map = HarmonyLib.Traverse.Create(__instance).Field("map").GetValue<Map>();
            if (map == null) return;
            if (map == Find.CurrentMap && Find.CameraDriver != null && Find.CameraDriver.CurrentViewRect.ExpandedBy(3).Contains(loc)) return; // on screen: the layer regenerates itself
            RM_MapComponent_CordGraph comp = map.GetComponent<RM_MapComponent_CordGraph>();
            if (comp != null) comp.StaleOffscreen = true;
        }
    }

    /// <summary>
    /// Keeps the cord graph out of the save (walk M9). Map.ExposeComponents writes every MapComponent as
    /// &lt;li Class="..."/&gt; even with no ExposeData, and loading that save without the mod logs two red errors
    /// ("Could not find class RimMandrake.GimmeSomeSlack.RM_MapComponent_CordGraph" + "Can't load abstract class
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
