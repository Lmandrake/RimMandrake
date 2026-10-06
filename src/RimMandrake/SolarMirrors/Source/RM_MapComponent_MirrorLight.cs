using System.Collections.Generic;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.SolarMirrors
{
    // SOLAR_MIRRORS_MOD_DESIGN_1 §2.2-§2.7. The mirror light layer: one float per cell of
    // irradiance (0..N, N > 1 = concentration), rebuilt from zero every pass and never saved
    // (rebuilt on FinalizeInit, like the shade grid). A pass:
    //   1. collectors: each mirror whose own footprint stands in sun (a MIRROR-FREE query: roof
    //      and cast shade from the shade grid, never the composed shade this layer edits);
    //   2. each firing mirror throws reflectivity x cosine x input onto its spot, cell by cell,
    //      stopped by walls, rock, closed doors and roofs (path and target);
    //   3. relays: a mirror whose footprint a spot lands on fires next, from that beam's
    //      direction, consuming its energy; each mirror fires at most once (acyclic), depth <= maxChain.
    // On a change (quantised to 0.05) it asks the shade grid for one full Recompute. This
    // component is the grid's registered light source (IRM_LightLayer, CreatureBehaviors'
    // public hook, design §2.3): the grid pulls the light via AddLight inside every Recompute
    // and folds it into ShadeAt, the cached exposure and the path-cost grid, so pathing and the
    // herd patch graph see it under one GridVersion.
    public class RM_MapComponent_MirrorLight : MapComponent, IRM_LightLayer
    {
        private const float MinUseful = 0.02f;
        private const int MinTicksBetweenGridRebuilds = 60; // PROVISIONAL throttle (design §2.8 risk 2)

        private readonly HashSet<RM_CompMirror> mirrors = new HashSet<RM_CompMirror>();
        private readonly List<RM_CompMirror> mirrorList = new List<RM_CompMirror>();
        private readonly HashSet<RM_CompLightReceiver> receivers = new HashSet<RM_CompLightReceiver>();

        private float[] light;
        private readonly List<int> litCells = new List<int>();
        private readonly List<int> prevLitCells = new List<int>();
        private int lastHash;
        private bool passRequested = true;
        private bool gridRebuildPending;
        private int lastGridRebuildTick = -99999;
        private RM_MapComponent_ShadeGrid registeredGrid;

        public struct Beam
        {
            public Vector3 from;
            public Vector3 to;
            public float intensity;
        }

        private readonly List<Beam> beams = new List<Beam>();
        private readonly List<IntVec3> scratchCells = new List<IntVec3>();

        private static Map cachedMap;
        private static RM_MapComponent_MirrorLight cachedComp;

        public RM_MapComponent_MirrorLight(Map map) : base(map)
        {
        }

        public static RM_MapComponent_MirrorLight For(Map map)
        {
            if (map == null)
            {
                return null;
            }
            if (map == cachedMap && cachedComp != null)
            {
                return cachedComp;
            }
            RM_MapComponent_MirrorLight c = map.GetComponent<RM_MapComponent_MirrorLight>();
            cachedMap = map;
            cachedComp = c;
            return c;
        }

        public IReadOnlyList<Beam> Beams => beams;
        public IReadOnlyList<int> LitCells => litCells;
        public int MirrorCount => mirrors.Count;
        public bool AnyLight => litCells.Count > 0;

        /// <summary>Raw irradiance at a cell index (0 where unlit). Unclamped.</summary>
        public float LightAtIndex(int i)
        {
            return light != null && i >= 0 && i < light.Length ? light[i] : 0f;
        }

        public float LightAt(IntVec3 c)
        {
            if (light == null || !c.InBounds(map))
            {
                return 0f;
            }
            return light[map.cellIndices.CellToIndex(c)];
        }

        public void Register(RM_CompMirror m)
        {
            if (mirrors.Add(m))
            {
                mirrorList.Add(m);
                passRequested = true;
            }
        }

        public void Unregister(RM_CompMirror m)
        {
            if (mirrors.Remove(m))
            {
                mirrorList.Remove(m);
                passRequested = true;
            }
        }

        public void Register(RM_CompLightReceiver r)
        {
            receivers.Add(r);
        }

        public void Unregister(RM_CompLightReceiver r)
        {
            receivers.Remove(r);
        }

        public void RequestPass()
        {
            passRequested = true;
        }

        /// <summary>A setting the grid reads through AddLight changed: rebuild the grid even if
        /// the light itself did not (the change hash would not see it).</summary>
        public void RequestGridRebuild()
        {
            gridRebuildPending = true;
        }

        /// <summary>IRM_LightLayer (CreatureBehaviors, design §2.3): add this map's mirror light
        /// to the shade grid's buffer. Called by the grid inside Recompute, main thread. No
        /// allocation: one pass over the lit cells.</summary>
        public bool AddLight(float[] into)
        {
            if (!RM_SolarMirrorsSettings.shadeEffect || light == null || into == null || into.Length != light.Length)
            {
                return false;
            }
            for (int k = 0; k < litCells.Count; k++)
            {
                int i = litCells[k];
                into[i] += light[i];
            }
            return litCells.Count > 0;
        }

        private void EnsureRegistered()
        {
            if (registeredGrid != null)
            {
                return;
            }
            registeredGrid = RM_MapComponent_ShadeGrid.For(map);
            registeredGrid?.RegisterLightSource(this);
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            passRequested = true;
            EnsureRegistered();
        }

        public override void MapRemoved()
        {
            base.MapRemoved();
            registeredGrid?.UnregisterLightSource(this);
            registeredGrid = null;
            if (cachedMap == map)
            {
                cachedMap = null;
                cachedComp = null;
            }
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            EnsureRegistered();
            int now = Find.TickManager.TicksGame;
            int interval = Mathf.Clamp(RM_SolarMirrorsSettings.passIntervalTicks, 125, 1000);
            if (passRequested || now % interval == 0)
            {
                passRequested = false;
                Pass();
                TickReceivers();
                if (now % interval == 0)
                {
                    TickBlinding(interval);
                }
            }
            if (gridRebuildPending && now - lastGridRebuildTick >= MinTicksBetweenGridRebuilds)
            {
                RebuildShadeGrid(now);
            }
        }

        private void RebuildShadeGrid(int now)
        {
            gridRebuildPending = false;
            lastGridRebuildTick = now;
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(map);
            if (grid != null && RM_CreatureBehaviorsSettings.shadeGridEnabled)
            {
                grid.Recompute();
            }
        }

        // ── the sun ─────────────────────────────────────────────────────

        /// <summary>The unit vector toward the light source and a 0..1 daylight factor. Pinned sun
        /// (Long Shade), else the shade grid's fixed sun, else a simple moving sun. False at night,
        /// in a sunless sky, or below the horizon.</summary>
        public bool TrySun(out Vector3 sun, out float daylight)
        {
            sun = Vector3.up;
            daylight = 0f;
            RM_MapComponent_PinnedSun pin = RM_MapComponent_PinnedSun.For(map);
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(map);
            bool pinned = pin != null && pin.IsActive;
            if (pinned)
            {
                Vector2 d = pin.ShadowDirection;
                sun = RM_MirrorMath.SunVector(d.x, d.y, pin.SunElevationDegrees);
                daylight = 1f;
            }
            else
            {
                // PROVISIONAL: daylight from the clock's celestial glow, 0 at night (<= 0.1),
                // full from 0.6 (vanilla's dusk ceiling) up.
                float g = GenCelestial.CurCelestialSunGlow(map);
                daylight = Mathf.Clamp01((g - 0.1f) / 0.5f);
                if (grid != null && grid.IsDirectional && !float.IsNaN(grid.SunElevationDegrees))
                {
                    Vector2 d = grid.SunShadowDirection;
                    sun = RM_MirrorMath.SunVector(d.x, d.y, grid.SunElevationDegrees);
                }
                else
                {
                    float lat = 0f;
                    if (Find.WorldGrid != null && map.Tile.Valid)
                    {
                        lat = Find.WorldGrid.LongLatOf(map.Tile).y;
                    }
                    if (!RM_MirrorMath.MovingSun(GenLocalDate.DayPercent(map), lat, out sun))
                    {
                        daylight = 0f;
                    }
                }
            }
            daylight *= RM_WeatherSenseExtension.SunFactor(map);
            return daylight > 0f && sun.y > 0f;
        }

        // ── geometry ────────────────────────────────────────────────────

        /// <summary>The spot a mirror throws when centred on a cell: the mirror's own size.</summary>
        public void SpotCells(RM_CompMirror m, IntVec3 center, List<IntVec3> into)
        {
            int size = Mathf.Max(1, m.Props.spotSize);
            int lo = -(size - 1) / 2;
            for (int dx = 0; dx < size; dx++)
            {
                for (int dz = 0; dz < size; dz++)
                {
                    IntVec3 c = new IntVec3(center.x + lo + dx, 0, center.z + lo + dz);
                    if (c.InBounds(map))
                    {
                        into.Add(c);
                    }
                }
            }
        }

        /// <summary>Why a beam from this mirror to this cell is stopped, or null when it is clear.</summary>
        public string FirstBlocker(RM_CompMirror m, IntVec3 cell)
        {
            if (!cell.InBounds(map))
            {
                return BlockerEdge;
            }
            CellRect own = m.parent.OccupiedRect();
            IntVec3 from = m.parent.Position;
            BeamWalk walk = new BeamWalk { comp = this, own = own, self = m.parent };
            if (!RM_MirrorMath.LineClear(from.x, from.z, cell.x, cell.z, ref walk))
            {
                return walk.why;
            }
            if (!own.Contains(cell))
            {
                return CellBlocks(cell, m.parent);
            }
            return null;
        }

        private struct BeamWalk : IRM_LineVisitor
        {
            public RM_MapComponent_MirrorLight comp;
            public CellRect own;
            public Thing self;
            public string why;

            public bool Blocked(int x, int z)
            {
                IntVec3 c = new IntVec3(x, 0, z);
                if (own.Contains(c))
                {
                    return false;
                }
                why = comp.CellBlocks(c, self);
                return why != null;
            }
        }

        // Translated once: a blocked beam is re-tested every pass, and Translate allocates.
        private static string blockerRoof, blockerDoor, blockerEdge, blockerSky;

        internal static string BlockerEdge => blockerEdge ??= "RM_SolarMirrors_Blocker_Edge".Translate();
        internal static string BlockerSky => blockerSky ??= "RM_SolarMirrors_Blocker_Sky".Translate();

        /// <summary>Design §2.2 v1 blocker rule: any roof; a closed door; a wall-like or impassable
        /// edifice (natural rock included). Mirrors and receivers never block (they are the
        /// apertures and the targets). Pawns and open doors never block.</summary>
        private string CellBlocks(IntVec3 c, Thing self)
        {
            if (map.roofGrid.Roofed(c))
            {
                return blockerRoof ??= "RM_SolarMirrors_Blocker_Roof".Translate();
            }
            Building e = c.GetEdifice(map);
            if (e == null || e == self)
            {
                return null;
            }
            if (e is Building_Door door)
            {
                return door.Open ? null : (blockerDoor ??= "RM_SolarMirrors_Blocker_Door".Translate());
            }
            if (e.TryGetComp<RM_CompMirror>() != null || e.TryGetComp<RM_CompLightReceiver>() != null)
            {
                return null;
            }
            if (e.def.fillPercent >= 0.8f || e.def.passability == Traversability.Impassable)
            {
                return e.LabelShortCap;
            }
            return null;
        }

        /// <summary>Mirror-free sun at the mirror's own footprint (design §2.2 collectors): the mean
        /// of (1 - max(roof, cast shade)) from the shade grid's raw layers, which this mod never edits.</summary>
        private float CollectorSource(RM_CompMirror m)
        {
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(map);
            float sum = 0f;
            int count = 0;
            foreach (IntVec3 c in m.parent.OccupiedRect())
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                count++;
                if (map.roofGrid.Roofed(c))
                {
                    continue;
                }
                float shade = grid != null ? Mathf.Max(grid.RoofShadeAt(c), grid.CastShadeAt(c)) : 0f;
                sum += 1f - shade;
            }
            return count > 0 ? sum / count : 0f;
        }

        // ── the pass ────────────────────────────────────────────────────

        private struct Shot
        {
            public RM_CompMirror mirror;
            public Vector3 inDir;
            public float input;
            public bool relayed;
        }

        private readonly List<Shot> queue = new List<Shot>();
        private readonly List<Shot> next = new List<Shot>();
        private readonly HashSet<RM_CompMirror> fired = new HashSet<RM_CompMirror>();
        private readonly Dictionary<RM_CompMirror, float> relayIn = new Dictionary<RM_CompMirror, float>();
        private readonly Dictionary<RM_CompMirror, Vector3> relayDir = new Dictionary<RM_CompMirror, Vector3>();

        public void Pass()
        {
            int n = map.cellIndices.NumGridCells;
            if (light == null || light.Length != n)
            {
                light = new float[n];
                litCells.Clear();
            }
            prevLitCells.Clear();
            prevLitCells.AddRange(litCells);
            for (int k = 0; k < litCells.Count; k++)
            {
                light[litCells[k]] = 0f;
            }
            litCells.Clear();
            beams.Clear();
            fired.Clear();
            queue.Clear();

            bool anyEffect = RM_SolarMirrorsSettings.shadeEffect || RM_SolarMirrorsSettings.glowEffect
                             || RM_SolarMirrorsSettings.blindingDefence || RM_SolarMirrorsSettings.solarFurnace
                             || RM_SolarMirrorsSettings.beamRender > 0;
            bool sunUp = TrySun(out Vector3 sun, out float daylight);
            for (int k = 0; k < mirrorList.Count; k++)
            {
                RM_CompMirror m = mirrorList[k];
                m.lastFired = false;
                m.lastRelayed = false;
                m.lastDelivered = 0f;
                m.lastEfficiency = 0f;
                m.lastBlocker = null;
                m.lastSpotCenter = IntVec3.Invalid;
                m.lastSource = 0f;
                m.lastInDir = Vector3.zero;
                if (!anyEffect || !sunUp || !m.parent.Spawned || !m.HasAim && !(m.HoldsTarget && m.Target.IsValid))
                {
                    continue;
                }
                float src = CollectorSource(m) * daylight;
                m.lastSource = src;
                if (src > MinUseful)
                {
                    queue.Add(new Shot { mirror = m, inDir = sun, input = src });
                }
            }

            int depthCap = Mathf.Clamp(RM_SolarMirrorsSettings.maxChain, 1, 6);
            for (int depth = 0; depth < depthCap && queue.Count > 0; depth++)
            {
                next.Clear();
                relayIn.Clear();
                relayDir.Clear();
                for (int q = 0; q < queue.Count; q++)
                {
                    Fire(queue[q]);
                }
                foreach (KeyValuePair<RM_CompMirror, float> kv in relayIn)
                {
                    if (!fired.Contains(kv.Key) && kv.Value > MinUseful)
                    {
                        next.Add(new Shot { mirror = kv.Key, inDir = relayDir[kv.Key], input = kv.Value, relayed = true });
                    }
                }
                queue.Clear();
                queue.AddRange(next);
            }
            queue.Clear();
            next.Clear();

            Publish();
        }

        private void Fire(Shot shot)
        {
            RM_CompMirror m = shot.mirror;
            if (!fired.Add(m))
            {
                return; // acyclic: a mirror fires once per pass (design §2.2)
            }
            m.lastInDir = shot.inDir;
            Vector3 nrm = m.NormalFor(shot.inDir);
            if (nrm == Vector3.zero)
            {
                return;
            }
            float cos = RM_MirrorMath.Cosine(nrm, shot.inDir);
            float output = shot.input * m.Reflectivity * cos;
            m.lastEfficiency = cos;
            if (output <= MinUseful)
            {
                return;
            }
            IntVec3 center;
            Vector3 face = m.FacePoint;
            if (m.HoldsTarget && m.Target.IsValid)
            {
                center = m.Target;
            }
            else
            {
                Vector3 outDir = RM_MirrorMath.Reflect(shot.inDir, nrm);
                if (!RM_MirrorMath.GroundHit(face.x, face.y, face.z, outDir, m.Props.maxRange, out float hx, out float hz))
                {
                    m.lastBlocker = BlockerSky;
                    return;
                }
                center = new IntVec3(Mathf.FloorToInt(hx), 0, Mathf.FloorToInt(hz));
            }
            if (!center.InBounds(map))
            {
                m.lastBlocker = BlockerEdge;
                return;
            }
            scratchCells.Clear();
            SpotCells(m, center, scratchCells);
            int lit = 0;
            for (int k = 0; k < scratchCells.Count; k++)
            {
                IntVec3 c = scratchCells[k];
                string why = FirstBlocker(m, c);
                if (why != null)
                {
                    m.lastBlocker ??= why;
                    continue;
                }
                AddLight(c, output);
                lit++;
                Building e = c.GetEdifice(map);
                RM_CompMirror other = e?.TryGetComp<RM_CompMirror>();
                if (other != null && other != m && !fired.Contains(other))
                {
                    // Relay input: this beam's share of the other mirror's footprint.
                    float share = output / Mathf.Max(1, other.parent.def.size.x * other.parent.def.size.z);
                    relayIn.TryGetValue(other, out float had);
                    relayIn[other] = had + share;
                    relayDir[other] = (face - other.FacePoint).normalized;
                }
            }
            if (lit == 0)
            {
                return;
            }
            m.lastFired = true;
            m.lastRelayed = shot.relayed;
            m.lastDelivered = output;
            m.lastSpotCenter = center;
            beams.Add(new Beam { from = new Vector3(face.x, 0f, face.z), to = RM_CompMirror.GroundPoint(center), intensity = output });
        }

        private void AddLight(IntVec3 c, float v)
        {
            int i = map.cellIndices.CellToIndex(c);
            if (light[i] <= 0f)
            {
                litCells.Add(i);
            }
            light[i] += v;
        }

        /// <summary>Change detection on quantised light; a changed layer dirties glow on the
        /// changed cells and schedules one shade-grid rebuild (removals included).</summary>
        private void Publish()
        {
            int hash = 17;
            for (int k = 0; k < litCells.Count; k++)
            {
                int i = litCells[k];
                hash = unchecked(hash * 31 + i * 7 + RM_MirrorMath.Quantise(light[i]));
            }
            hash = unchecked(hash * 31 + litCells.Count);
            if (hash == lastHash)
            {
                return;
            }
            lastHash = hash;
            DirtyGlow(prevLitCells);
            DirtyGlow(litCells);
            gridRebuildPending = true;
        }

        private void DirtyGlow(List<int> cells)
        {
            for (int k = 0; k < cells.Count; k++)
            {
                IntVec3 c = map.cellIndices.IndexToCell(cells[k]);
                map.mapDrawer.MapMeshDirty(c, MapMeshFlagDefOf.GroundGlow);
                map.events.Notify_GlowChanged(c);
            }
        }

        // ── receivers and the blinding defence ──────────────────────────

        private readonly List<RM_CompLightReceiver> receiverScratch = new List<RM_CompLightReceiver>();

        private void TickReceivers()
        {
            receiverScratch.Clear();
            receiverScratch.AddRange(receivers);
            for (int k = 0; k < receiverScratch.Count; k++)
            {
                RM_CompLightReceiver r = receiverScratch[k];
                if (r.parent.Spawned)
                {
                    r.UpdateLight(this);
                }
            }
            receiverScratch.Clear();
        }

        private static HediffDef glareBlind;
        private static bool glareLooked;
        private readonly List<Pawn> pawnScratch = new List<Pawn>();

        /// <summary>Design §5 E4: a hostile humanlike standing in a beam slowly goes glare-blind
        /// (CreatureBehaviors' RM_GlareBlind hediff on vanilla Sight), unless a gene or goggles
        /// protect the eyes. Its own -2/day decay is the recovery.</summary>
        private void TickBlinding(int interval)
        {
            if (!RM_SolarMirrorsSettings.blindingDefence || litCells.Count == 0)
            {
                return;
            }
            if (!glareLooked)
            {
                glareLooked = true;
                glareBlind = DefDatabase<HediffDef>.GetNamedSilentFail("RM_GlareBlind");
            }
            if (glareBlind == null)
            {
                return;
            }
            pawnScratch.Clear();
            pawnScratch.AddRange(map.mapPawns.AllPawnsSpawned);
            for (int k = 0; k < pawnScratch.Count; k++)
            {
                Pawn p = pawnScratch[k];
                if (p.Dead || p.RaceProps == null || !p.RaceProps.Humanlike || !p.HostileTo(Faction.OfPlayer))
                {
                    continue;
                }
                float l = LightAt(p.Position);
                if (l < 0.5f || RM_GlareBlind.EyesProtected(p)) // PROVISIONAL threshold
                {
                    continue;
                }
                float gain = RM_SolarMirrorsSettings.blindSeverityPerDay * Mathf.Min(1f, l) * interval / 60000f;
                HealthUtility.AdjustSeverity(p, glareBlind, gain);
            }
            pawnScratch.Clear();
        }

        // ── rendering (design §2.5, central, never PostDraw) ────────────

        private static Material[] spotMats;
        private static Material beamMat;

        public override void MapComponentUpdate()
        {
            base.MapComponentUpdate();
            int mode = RM_SolarMirrorsSettings.beamRender;
            // Map.MapUpdate calls this on every map, world view open or not (it gates its own
            // drawing on WorldRendererUtility.DrawingMap): never draw a spot over the planet.
            if (mode <= 0 || map != Find.CurrentMap || litCells.Count == 0 || !WorldRendererUtility.DrawingMap)
            {
                return;
            }
            if (spotMats == null)
            {
                spotMats = new Material[5];
                for (int k = 0; k < 5; k++)
                {
                    float a = 0.12f + 0.08f * k;
                    spotMats[k] = MaterialPool.MatFrom(BaseContent.WhiteTex, ShaderDatabase.MoteGlow, new Color(1f, 0.85f, 0.55f, a));
                }
                beamMat = MaterialPool.MatFrom(BaseContent.WhiteTex, ShaderDatabase.MoteGlow, new Color(1f, 0.9f, 0.6f, 0.18f));
            }
            float y = AltitudeLayer.MoteLow.AltitudeFor();
            for (int k = 0; k < litCells.Count; k++)
            {
                int i = litCells[k];
                IntVec3 c = map.cellIndices.IndexToCell(i);
                if (c.Fogged(map))
                {
                    continue;
                }
                int level = Mathf.Clamp(Mathf.FloorToInt(light[i] * 4f), 0, 4);
                Matrix4x4 mtx = Matrix4x4.TRS(new Vector3(c.x + 0.5f, y, c.z + 0.5f), Quaternion.identity, Vector3.one);
                Graphics.DrawMesh(MeshPool.plane10, mtx, spotMats[level], 0);
            }
            if (mode >= 2)
            {
                float by = AltitudeLayer.MoteOverhead.AltitudeFor();
                for (int k = 0; k < beams.Count; k++)
                {
                    Beam b = beams[k];
                    GenDraw.DrawLineBetween(new Vector3(b.from.x, by, b.from.z), new Vector3(b.to.x, by, b.to.z), beamMat, 0.35f);
                }
            }
        }
    }
}
