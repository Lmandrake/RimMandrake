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
    public class RM_MapComponent_MirrorLight : MapComponent, IRM_LightLayer, IRM_BeamWorld
    {
        private const float MinUseful = 0.02f;
        private const int MinTicksBetweenGridRebuilds = 60; // PROVISIONAL throttle (design §2.8 risk 2)

        private readonly HashSet<RM_CompMirror> mirrors = new HashSet<RM_CompMirror>();
        private readonly List<RM_CompMirror> mirrorList = new List<RM_CompMirror>();
        private readonly HashSet<RM_CompLightReceiver> receivers = new HashSet<RM_CompLightReceiver>();

        // The light pass itself is Kernel/RM_MirrorKernel.cs (Verse-free, fuzzed offline); this component builds its
        // inputs from the comps and writes its results back.
        private readonly RM_MirrorKernel.Pass pass = new RM_MirrorKernel.Pass();
        private float[] light => pass.Light;
        private List<int> litCells => pass.LitCells;
        private RM_MirrorSpec[] specs = new RM_MirrorSpec[0];
        private RM_MirrorResult[] results = new RM_MirrorResult[0];
        private readonly Dictionary<RM_CompMirror, int> indexOf = new Dictionary<RM_CompMirror, int>();
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
        /// <summary>Every registered mirror, in pass order (read by jawa/shade_probe and the work givers).</summary>
        public IReadOnlyList<RM_CompMirror> Mirrors => mirrorList;
        private readonly List<RM_CompLightReceiver> receiverList = new List<RM_CompLightReceiver>();
        public IReadOnlyList<RM_CompLightReceiver> Receivers => receiverList;
        /// <summary>Light passes run since the map loaded (diagnostic, not saved).</summary>
        public int PassCount { get; private set; }
        public int LastChangeHash => lastHash;

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
            if (receivers.Add(r))
            {
                receiverList.Add(r);
            }
        }

        public void Unregister(RM_CompLightReceiver r)
        {
            if (receivers.Remove(r))
            {
                receiverList.Remove(r);
            }
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
            int interval = RM_MirrorKernel.PassInterval(RM_SolarMirrorsSettings.passIntervalTicks);
            if (passRequested || now % interval == 0)
            {
                passRequested = false;
                if (now % interval == 0)
                {
                    TickDust(interval);
                    TickHeliostatPower();
                }
                Pass();
                TickReceivers();
                if (now % interval == 0)
                {
                    TickBlinding(interval);
                    TickRoomHeat(interval);
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
        /// in a sunless sky, or below the horizon. ignoreWeather (mapgen): the weather's sun factor is left out, so the
        /// initial weather never decides whether a field can be laid or solved (validation D5).</summary>
        public bool TrySun(out Vector3 sun, out float daylight)
        {
            return TrySun(out sun, out daylight, false);
        }

        public bool TrySun(out Vector3 sun, out float daylight, bool ignoreWeather)
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
                daylight = RM_MirrorKernel.Daylight(g);
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
            if (!ignoreWeather)
            {
                daylight *= RM_WeatherSenseExtension.SunFactor(map);
            }
            return daylight > 0f && sun.y > 0f;
        }

        // ── geometry ────────────────────────────────────────────────────

        /// <summary>The spot a mirror throws when centred on a cell: the mirror's own size.</summary>
        public void SpotCells(RM_CompMirror m, IntVec3 center, List<IntVec3> into)
        {
            int size, lo;
            RM_MirrorKernel.SpotRange(m.Props.spotSize, out size, out lo);
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
            int idx = mirrorList.IndexOf(m);
            if (idx < 0)
            {
                return cell.InBounds(map) ? null : BlockerEdge;
            }
            return RM_MirrorKernel.FirstBlocker(this, SpecFor(m, 0f), idx, cell.x, cell.z);
        }

        // IRM_BeamWorld: the kernel's view of this map.
        int IRM_BeamWorld.Width => map.Size.x;
        int IRM_BeamWorld.Height => map.Size.z;
        string IRM_BeamWorld.BlockerEdge => BlockerEdge;
        string IRM_BeamWorld.BlockerSky => BlockerSky;
        string IRM_BeamWorld.BlockerRoof => blockerRoof ??= "RM_SolarMirrors_Blocker_Roof".Translate();

        bool IRM_BeamWorld.Roofed(int x, int z)
        {
            return map.roofGrid.Roofed(new IntVec3(x, 0, z));
        }

        bool IRM_BeamWorld.IsAperture(int x, int z)
        {
            Building e = new IntVec3(x, 0, z).GetEdifice(map);
            return e != null && e.def.HasModExtension<RM_MirrorApertureExtension>();
        }

        string IRM_BeamWorld.CellBlocks(int x, int z, int mirrorIndex)
        {
            return CellBlocks(new IntVec3(x, 0, z), mirrorList[mirrorIndex].parent);
        }

        int IRM_BeamWorld.MirrorAt(int x, int z)
        {
            RM_CompMirror other = new IntVec3(x, 0, z).GetEdifice(map)?.TryGetComp<RM_CompMirror>();
            return other != null && indexOf.TryGetValue(other, out int i) ? i : -1;
        }

        private RM_MirrorSpec SpecFor(RM_CompMirror m, float source)
        {
            CellRect own = m.parent.OccupiedRect();
            Vector3 face = m.FacePoint;
            IntVec3 pos = m.parent.Position;
            return new RM_MirrorSpec
            {
                faceX = face.x,
                faceZ = face.z,
                posX = pos.x,
                posZ = pos.z,
                minX = own.minX,
                minZ = own.minZ,
                maxX = own.maxX,
                maxZ = own.maxZ,
                footprintCells = m.parent.def.size.x * m.parent.def.size.z,
                reflectivity = m.Reflectivity,
                spotSize = m.Props.spotSize,
                maxRange = m.Props.maxRange,
                spawned = m.parent.Spawned,
                hasAim = m.HasAim,
                holdsTarget = m.HoldsTarget,
                targetValid = m.Target.IsValid,
                tracking = m.TrackingNow,
                targetX = m.Target.x,
                targetZ = m.Target.z,
                savedNormal = RM_MirrorMath.To(m.CommittedNormal),
                source = source
            };
        }

        // Translated once: a blocked beam is re-tested every pass, and Translate allocates.
        private static string blockerRoof, blockerDoor, blockerEdge, blockerSky;

        internal static string BlockerEdge => blockerEdge ??= "RM_SolarMirrors_Blocker_Edge".Translate();
        internal static string BlockerSky => blockerSky ??= "RM_SolarMirrors_Blocker_Sky".Translate();

        /// <summary>Design §2.2 v1 blocker rule, roofs aside (the kernel asks Roofed/IsAperture itself, so a
        /// glazed aperture lets a beam under a roof, §5 E2): a closed door; a wall-like or impassable edifice
        /// (natural rock included). Mirrors, receivers and apertures never block. Pawns and open doors never block.</summary>
        private string CellBlocks(IntVec3 c, Thing self)
        {
            Building e = c.GetEdifice(map);
            if (e == null || e == self)
            {
                return null;
            }
            if (e is Building_Door door)
            {
                return door.Open ? null : (blockerDoor ??= "RM_SolarMirrors_Blocker_Door".Translate());
            }
            if (e.TryGetComp<RM_CompMirror>() != null || e.TryGetComp<RM_CompLightReceiver>() != null
                || e.def.HasModExtension<RM_MirrorApertureExtension>())
            {
                return null;
            }
            if (e.def.fillPercent >= 0.8f || e.def.passability == Traversability.Impassable)
            {
                return e.LabelShortCap;
            }
            return null;
        }

        /// <summary>The mirror-free sun fraction at a mirror's footprint right now (0..1).</summary>
        public float SourceAt(RM_CompMirror m)
        {
            return CollectorSource(m);
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

        public void Pass()
        {
            PassCount++;
            int count = mirrorList.Count;
            if (specs.Length < count)
            {
                specs = new RM_MirrorSpec[count];
                results = new RM_MirrorResult[count];
            }
            indexOf.Clear();
            for (int k = 0; k < count; k++)
            {
                indexOf[mirrorList[k]] = k;
            }

            bool anyEffect = RM_SolarMirrorsSettings.shadeEffect || RM_SolarMirrorsSettings.glowEffect
                             || RM_SolarMirrorsSettings.blindingDefence || RM_SolarMirrorsSettings.solarFurnace
                             || RM_SolarMirrorsSettings.beamRender > 0;
            bool sunUp = TrySun(out Vector3 sun, out float daylight);
            for (int k = 0; k < count; k++)
            {
                RM_CompMirror m = mirrorList[k];
                // An aim made in the dark: a collector standing in sun takes the sun now; a shaded relay waits for the
                // beam that actually reaches it (resolved after the pass, below; validation pass 3).
                if (sunUp && m.AimDeferred && m.parent.Spawned && CollectorSource(m) > MinUseful)
                {
                    m.ResolveDeferredAim(sun);
                }
                bool eligible = anyEffect && sunUp && m.parent.Spawned && (m.HasAim || m.HoldsTarget && m.Target.IsValid);
                specs[k] = SpecFor(m, eligible ? CollectorSource(m) : 0f);
            }

            pass.Run(this, specs, count, results, anyEffect, sunUp, RM_MirrorMath.To(sun), daylight, RM_SolarMirrorsSettings.maxChain);

            for (int k = 0; k < count; k++)
            {
                RM_CompMirror m = mirrorList[k];
                RM_MirrorResult r = results[k];
                m.lastFired = r.fired;
                m.lastRelayed = r.relayed;
                m.lastDelivered = r.delivered;
                m.lastEfficiency = r.efficiency;
                m.lastBlocker = r.blocker;
                m.lastSpotCenter = r.hasSpot ? new IntVec3(r.spotX, 0, r.spotZ) : IntVec3.Invalid;
                m.lastSource = r.source;
                m.lastInDir = RM_MirrorMath.From(r.inDir);
                if (m.AimDeferred && r.ranFire && !r.inDir.IsZero)
                {
                    m.ResolveDeferredAim(m.lastInDir);
                    passRequested = true;
                }
                if (r.commitNormal)
                {
                    m.CommitNormal(RM_MirrorMath.From(r.normal));
                }
            }
            beams.Clear();
            for (int k = 0; k < pass.Beams.Count; k++)
            {
                RM_BeamOut b = pass.Beams[k];
                beams.Add(new Beam { from = new Vector3(b.fromX, 0f, b.fromZ), to = new Vector3(b.toX, 0f, b.toZ), intensity = b.intensity });
            }

            Publish();
        }

        /// <summary>Change detection on quantised light; a changed layer dirties glow on the
        /// changed cells and schedules one shade-grid rebuild (removals included).</summary>
        private void Publish()
        {
            int hash = pass.ChangeHash();
            if (hash == lastHash)
            {
                return;
            }
            lastHash = hash;
            DirtyGlow(pass.PrevLitCells);
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

        // ── simulation for the field solver (mapgen) ────────────────────

        private readonly RM_MirrorKernel.Pass simPass = new RM_MirrorKernel.Pass();
        private RM_MirrorResult[] simResults = new RM_MirrorResult[0];

        /// <summary>The light every registered mirror would throw in its current state, under the sun with full
        /// daylight (weather ignored), WITHOUT touching the live layer, the comps or the shade grid. The ancient
        /// field's solver calls it once per configuration (design §3.4). maxDepth = the deepest relay that fired.</summary>
        public float[] SimulateLight(out int maxDepth)
        {
            maxDepth = 0;
            int count = mirrorList.Count;
            if (simResults.Length < count)
            {
                simResults = new RM_MirrorResult[count];
            }
            RM_MirrorSpec[] sims = new RM_MirrorSpec[count];
            indexOf.Clear();
            for (int k = 0; k < count; k++)
            {
                indexOf[mirrorList[k]] = k;
            }
            bool sunUp = TrySun(out Vector3 sun, out float _, true);
            for (int k = 0; k < count; k++)
            {
                RM_CompMirror m = mirrorList[k];
                bool eligible = sunUp && m.parent.Spawned && (m.HasAim || m.HoldsTarget && m.Target.IsValid);
                sims[k] = SpecFor(m, eligible ? CollectorSource(m) : 0f);
            }
            simPass.Run(this, sims, count, simResults, true, sunUp, RM_MirrorMath.To(sun), 1f, RM_SolarMirrorsSettings.maxChain);
            for (int k = 0; k < count; k++)
            {
                if (simResults[k].fired && simResults[k].depth > maxDepth)
                {
                    maxDepth = simResults[k].depth;
                }
            }
            return simPass.Light;
        }

        // ── dust (design §3.2), heliostat power, room heat (§2.6, §5 E1/E2) ──

        private void TickDust(int interval)
        {
            if (!RM_SolarMirrorsSettings.dustEnabled)
            {
                return;
            }
            bool storm = RM_MirrorDustWeathersDef.IsDusty(map.weatherManager?.curWeather);
            if (!storm)
            {
                return;
            }
            for (int k = 0; k < mirrorList.Count; k++)
            {
                RM_CompMirror m = mirrorList[k];
                if (m.parent.Spawned && !m.parent.Position.Roofed(map))
                {
                    m.AddDust(RM_MirrorKernel.DustAfter(m.Dust, true, RM_SolarMirrorsSettings.dustPerDay, interval) - m.Dust);
                }
            }
        }

        /// <summary>The settings dial for heliostat draw (design §3.5) applied to every powered tracker that is on.</summary>
        private void TickHeliostatPower()
        {
            for (int k = 0; k < mirrorList.Count; k++)
            {
                RM_CompMirror m = mirrorList[k];
                if (!m.Props.tracks)
                {
                    continue;
                }
                CompPowerTrader p = m.parent.GetComp<CompPowerTrader>();
                if (p != null && p.PowerOn)
                {
                    p.PowerOutput = -RM_SolarMirrorsSettings.heliostatPower;
                }
            }
        }

        /// <summary>Mirror light falling inside an enclosed room warms it (a beam through a glazed aperture, or a lit
        /// solar furnace indoors). Vanilla heat: GenTemperature.PushHeat, which does nothing outdoors.</summary>
        private void TickRoomHeat(int interval)
        {
            if (!RM_SolarMirrorsSettings.roomHeat || litCells.Count == 0)
            {
                return;
            }
            for (int k = 0; k < litCells.Count; k++)
            {
                IntVec3 c = map.cellIndices.IndexToCell(litCells[k]);
                if (!map.roofGrid.Roofed(c) || c.UsesOutdoorTemperature(map))
                {
                    continue;
                }
                float e = RM_MirrorKernel.RoomHeat(light[litCells[k]], RM_SolarMirrorsSettings.roomHeatPerLight, interval);
                if (e > 0f)
                {
                    GenTemperature.PushHeat(c, map, e);
                }
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
                if (l < 0.5f || RM_GlareBlind.EyesProtected(p)) // PROVISIONAL threshold (BlindGain repeats it)
                {
                    continue;
                }
                float gain = RM_MirrorKernel.BlindGain(l, RM_SolarMirrorsSettings.blindSeverityPerDay, interval);
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
