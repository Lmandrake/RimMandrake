using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_TAR_LIVING_SYSTEMS_1 part 1 (SUMP_TAR_HYDROLOGY_1 ruling 8): "slow responders after every rewrite —
    // soffeth rings grow at new seeps, mouse-lines re-route, flora margins migrate to new edges over days. The
    // literacy game stays true after every belch."
    //
    // A rewrite is any change of a cell INTO tar (RM_TarShallow/RM_TarDeep) or tar glass (RM_TarGlass): the belch's
    // Flood_FlowWorks release and its CoolFrontToGlass, or a tar canal release. Detected by an hourly terrain diff, so
    // this needs no hook in FlowWorks or in the belch worker. Three responders follow it:
    //   1. soffeth ring: a rewrite of >= MinRewriteCells cells seeds a ring of RM_Soffeth (radius 2-4) around it,
    //      one stalk at a time, starting a day later — "a soffeth ring means gas below".
    //   2. mouse-lines re-route: each new glass cell is fresh crust. After MouseRerouteDelay the dread field reports it
    //      dreaded (RM_MapComponent_DreadField.IsDreaded), so RM_JobGiver_DreadAvoidWander mice detour around it,
    //      until the crust sets (CrustSetTicks) or mirrelin has grown onto it.
    //   3. flora margins migrate: RM_Mirrelin (the glass-reach graze) sprouts onto new glass after MarginDelay, a few
    //      cells per hour, and each sprout lifts that cell's fresh-crust dread (the gnawed trail is the mouse-line).
    //
    // 🔑 PROVISIONAL numbers (owner ruling 2026-10-03, by question card: first-guess pacing ships, tuned live later).
    // Every constant below marked PROVISIONAL is a first guess. One Mod Setting scales all delays at once
    // (sumpLivingMapPace); its tooltip says PROVISIONAL too.
    //
    // Gate: the map's biome must carry RM_Soffeth or RM_Mirrelin as a wild plant (data-driven, so any biome that adopts
    // the Sump flora gets the responders; RUT_Sump, which carries neither today, gets none). Toggle:
    // sumpLivingMapEnabled. Off: no scan, nothing new is queued, queued responders wait; already-grown plants stay.
    //
    // Save: responders and fresh-crust cells are Scribed. The terrain snapshot is not — the first scan after a load
    // re-baselines, so a rewrite in the last hour before a save is not responded to (bounded, cosmetic loss).
    public class RM_MapComponent_SumpLivingMap : MapComponent
    {
        public const int ScanIntervalTicks = 2500;            // PROVISIONAL: diff once per game hour
        public const int MinRewriteCells = 8;                 // PROVISIONAL: smaller changes seed no soffeth ring
        public const int SoffethDelayTicks = 60000;           // PROVISIONAL: first stalk 1 day after the seep
        public const int SoffethIntervalTicks = 15000;        // PROVISIONAL: one stalk per 6 h after that
        public const int SoffethRingSize = 6;                 // PROVISIONAL: stalks per ring
        public const float SoffethRingInner = 2f;             // PROVISIONAL
        public const float SoffethRingOuter = 4.9f;           // PROVISIONAL
        public const int MouseRerouteDelayTicks = 15000;      // PROVISIONAL: mice learn the new crust in 6 h
        public const int CrustSetTicks = 360000;              // PROVISIONAL: fresh crust sets (dread lifts) in 6 days
        public const int MarginDelayTicks = 120000;           // PROVISIONAL: mirrelin starts reaching new glass after 2 days
        public const float MarginSproutChancePerScan = 0.014f; // PROVISIONAL: ~1/72 per hour, most cells in ~3 days
        public const int MaxMarginSproutsPerScan = 4;         // PROVISIONAL
        public const int MaxFreshCrustCells = 400;            // bound on tracked cells (newest kept)

        private class Ring : IExposable
        {
            public IntVec3 center;
            public int nextTick;
            public int remaining;

            public void ExposeData()
            {
                Scribe_Values.Look(ref center, "center");
                Scribe_Values.Look(ref nextTick, "nextTick");
                Scribe_Values.Look(ref remaining, "remaining");
            }
        }

        private List<Ring> rings = new List<Ring>();
        private List<int> crustCells = new List<int>();
        private List<int> crustBornTick = new List<int>();
        private readonly HashSet<int> crustSet = new HashSet<int>();
        private TerrainDef[] snapshot;
        private bool? gateCache;

        public int PendingRings => rings.Count;
        public int FreshCrustCount => crustCells.Count;

        public RM_MapComponent_SumpLivingMap(Map map) : base(map)
        {
        }

        private static float Pace => Mathf.Max(0.05f, RM_EnvironmentalHazardsSettings.sumpLivingMapPace);

        public static int Scaled(int ticks) => Mathf.Max(1, Mathf.RoundToInt(ticks / Pace));

        public bool BiomeCarriesSumpFlora()
        {
            if (gateCache.HasValue)
            {
                return gateCache.Value;
            }
            BiomeDef b = map.Biome;
            ThingDef soffeth = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Soffeth");
            ThingDef mirrelin = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Mirrelin");
            bool ok = b != null && ((soffeth != null && b.CommonalityOfPlant(soffeth) > 0f)
                                 || (mirrelin != null && b.CommonalityOfPlant(mirrelin) > 0f));
            gateCache = ok;
            return ok;
        }

        // EH-5: the tar terrains come from FlowWorks' RM_Liquid_Tar entry (terrainSuite), falling back to the
        // historical names only when the entry is absent, so a renamed terrain or a second tar liquid cannot
        // silently break the beast, the belch or this component.
        private static TerrainDef tarShallowCache, tarDeepCache;
        private static bool tarResolved;

        private static void ResolveTar()
        {
            if (tarResolved) return;
            tarResolved = true;
            RimMandrake.FlowWorks.LiquidTypes.LiquidDef liq =
                DefDatabase<RimMandrake.FlowWorks.LiquidTypes.LiquidDef>.GetNamedSilentFail("RM_Liquid_Tar");
            tarShallowCache = liq?.terrainSuite?.shallow ?? DefDatabase<TerrainDef>.GetNamedSilentFail("RM_TarShallow");
            tarDeepCache = liq?.terrainSuite?.deep ?? DefDatabase<TerrainDef>.GetNamedSilentFail("RM_TarDeep");
        }

        public static TerrainDef TarShallow { get { ResolveTar(); return tarShallowCache; } }
        public static TerrainDef TarDeep { get { ResolveTar(); return tarDeepCache; } }

        public static bool IsTarLiquid(TerrainDef t) => t != null && (t == TarShallow || t == TarDeep);
        public static bool IsTarGlass(TerrainDef t) => t != null && t.defName == "RM_TarGlass";

        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (now % ScanIntervalTicks != 0)
            {
                return;
            }
            if (!RM_EnvironmentalHazardsSettings.sumpLivingMapEnabled || !BiomeCarriesSumpFlora())
            {
                return;
            }
            Step(now);
        }

        // One scan + one responder pass. Public so the proof (RM_SumpLivingMapProof) can drive it with a synthetic clock.
        public void Step(int now)
        {
            Scan(now);
            Process(now);
        }

        public void Rebaseline()
        {
            int n = map.cellIndices.NumGridCells;
            if (snapshot == null || snapshot.Length != n)
            {
                snapshot = new TerrainDef[n];
            }
            for (int i = 0; i < n; i++)
            {
                snapshot[i] = map.terrainGrid.TerrainAt(map.cellIndices.IndexToCell(i));
            }
        }

        // Returns the number of rewritten cells seen this scan.
        public int Scan(int now)
        {
            if (!RM_EnvironmentalHazardsSettings.sumpLivingMapEnabled)
            {
                return 0;
            }
            if (snapshot == null || snapshot.Length != map.cellIndices.NumGridCells)
            {
                Rebaseline();
                return 0;
            }
            var rewritten = new List<IntVec3>();
            int n = snapshot.Length;
            for (int i = 0; i < n; i++)
            {
                IntVec3 c = map.cellIndices.IndexToCell(i);
                TerrainDef cur = map.terrainGrid.TerrainAt(c);
                TerrainDef old = snapshot[i];
                if (cur == old)
                {
                    continue;
                }
                snapshot[i] = cur;
                if (IsTarLiquid(cur) || IsTarGlass(cur))
                {
                    rewritten.Add(c);
                    if (IsTarGlass(cur) && !crustSet.Contains(i))
                    {
                        crustSet.Add(i);
                        crustCells.Add(i);
                        crustBornTick.Add(now);
                    }
                }
            }
            while (crustCells.Count > MaxFreshCrustCells)
            {
                crustSet.Remove(crustCells[0]);
                crustCells.RemoveAt(0);
                crustBornTick.RemoveAt(0);
            }
            if (rewritten.Count >= MinRewriteCells)
            {
                float sx = 0f, sz = 0f;
                foreach (IntVec3 c in rewritten) { sx += c.x; sz += c.z; }
                var centroid = new IntVec3(Mathf.RoundToInt(sx / rewritten.Count), 0, Mathf.RoundToInt(sz / rewritten.Count));
                IntVec3 best = rewritten[0];
                foreach (IntVec3 c in rewritten)
                {
                    if ((c - centroid).LengthHorizontalSquared < (best - centroid).LengthHorizontalSquared) best = c;
                }
                rings.Add(new Ring { center = best, nextTick = now + Scaled(SoffethDelayTicks), remaining = SoffethRingSize });
            }
            return rewritten.Count;
        }

        // Plants due soffeth stalks and mirrelin sprouts, expires set crust. Returns plants spawned.
        public int Process(int now, List<Thing> spawnedOut = null)
        {
            int spawned = 0;
            ThingDef soffeth = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Soffeth");
            ThingDef mirrelin = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Mirrelin");
            for (int r = rings.Count - 1; r >= 0; r--)
            {
                Ring ring = rings[r];
                while (ring.remaining > 0 && now >= ring.nextTick)
                {
                    ring.remaining--;
                    ring.nextTick += Scaled(SoffethIntervalTicks);
                    if (soffeth != null && TryRingCell(ring.center, out IntVec3 cell) && TrySpawnPlant(soffeth, cell, spawnedOut))
                    {
                        spawned++;
                    }
                }
                if (ring.remaining <= 0)
                {
                    rings.RemoveAt(r);
                }
            }
            int sprouts = 0;
            for (int k = crustCells.Count - 1; k >= 0; k--)
            {
                int idx = crustCells[k];
                IntVec3 c = map.cellIndices.IndexToCell(idx);
                int age = now - crustBornTick[k];
                bool stillGlass = IsTarGlass(map.terrainGrid.TerrainAt(c));
                if (!stillGlass || age >= Scaled(CrustSetTicks))
                {
                    RemoveCrustAt(k);
                    continue;
                }
                if (mirrelin != null && sprouts < MaxMarginSproutsPerScan && age >= Scaled(MarginDelayTicks)
                    && Rand.Chance(Mathf.Clamp01(MarginSproutChancePerScan * Pace)) && TrySpawnPlant(mirrelin, c, spawnedOut))
                {
                    sprouts++;
                    spawned++;
                    RemoveCrustAt(k); // the graze has reached it: the gnawed trail crosses, the dread lifts
                }
            }
            return spawned;
        }

        private void RemoveCrustAt(int k)
        {
            crustSet.Remove(crustCells[k]);
            crustCells.RemoveAt(k);
            crustBornTick.RemoveAt(k);
        }

        // Fresh crust the mice have learned to avoid: born at least MouseRerouteDelay ago, not yet set or grazed.
        public bool IsFreshCrust(IntVec3 cell, int now)
        {
            if (!RM_EnvironmentalHazardsSettings.sumpLivingMapEnabled || crustSet.Count == 0 || !cell.InBounds(map))
            {
                return false;
            }
            int idx = map.cellIndices.CellToIndex(cell);
            if (!crustSet.Contains(idx))
            {
                return false;
            }
            int k = crustCells.IndexOf(idx);
            int age = now - crustBornTick[k];
            return age >= Scaled(MouseRerouteDelayTicks) && age < Scaled(CrustSetTicks);
        }

        private bool TryRingCell(IntVec3 center, out IntVec3 result)
        {
            var cands = new List<IntVec3>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, SoffethRingOuter, useCenter: false))
            {
                if (!c.InBounds(map) || (c - center).LengthHorizontal < SoffethRingInner)
                {
                    continue;
                }
                if (PlantableHere(c) && !IsTarLiquid(map.terrainGrid.TerrainAt(c)))
                {
                    cands.Add(c);
                }
            }
            if (cands.Count == 0)
            {
                result = IntVec3.Invalid;
                return false;
            }
            result = cands.RandomElement();
            return true;
        }

        private bool PlantableHere(IntVec3 c)
        {
            return c.Standable(map) && c.GetPlant(map) == null && c.GetEdifice(map) == null && !c.Roofed(map);
        }

        private bool TrySpawnPlant(ThingDef def, IntVec3 c, List<Thing> spawnedOut)
        {
            if (!PlantableHere(c))
            {
                return false;
            }
            Thing t = GenSpawn.Spawn(ThingMaker.MakeThing(def), c, map);
            if (t is Plant p)
            {
                p.Growth = 0.15f;
            }
            spawnedOut?.Add(t);
            return true;
        }

        public void ClearForProof()
        {
            rings.Clear();
            crustCells.Clear();
            crustBornTick.Clear();
            crustSet.Clear();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref rings, "rmLivingMapRings", LookMode.Deep);
            Scribe_Collections.Look(ref crustCells, "rmLivingMapCrustCells", LookMode.Value);
            Scribe_Collections.Look(ref crustBornTick, "rmLivingMapCrustBorn", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                rings = rings ?? new List<Ring>();
                crustCells = crustCells ?? new List<int>();
                crustBornTick = crustBornTick ?? new List<int>();
                if (crustBornTick.Count != crustCells.Count)
                {
                    crustCells.Clear();
                    crustBornTick.Clear();
                }
                crustSet.Clear();
                foreach (int i in crustCells) crustSet.Add(i);
            }
        }
    }

    // Live proof hook for SUMP_TAR_LIVING_SYSTEMS_1 (jawa/static_call
    // RimMandrake.EnvironmentalHazards.RM_SumpLivingMapProof ProofRewrite on|off). On the CURRENT map: glasses a 4x4
    // block of ordinary ground, drives the real component on a synthetic clock through 10 days, reads every
    // responder, then restores the terrain and destroys every plant it spawned. Settings restored in finally.
    // "on": expects 1 ring queued, 16 fresh-crust cells, dread false before the reroute delay and true after,
    // >=1 soffeth and >=1 mirrelin spawned. "off" (toggle false): expects nothing queued and nothing spawned.
    public static class RM_SumpLivingMapProof
    {
        public static string ProofRewrite(string mode)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "UNMEASURED: no current map";
            TerrainDef glass = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_TarGlass");
            ThingDef soffeth = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Soffeth");
            ThingDef mirrelin = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Mirrelin");
            if (glass == null || soffeth == null || mirrelin == null)
                return "UNMEASURED: RM_TarGlass / RM_Soffeth / RM_Mirrelin not loaded (needs FlowWorks + TheSump)";
            var comp = map.GetComponent<RM_MapComponent_SumpLivingMap>();
            if (comp == null) return "FAIL: RM_MapComponent_SumpLivingMap not on the map";
            bool on = mode != "off";
            bool savedEnabled = RM_EnvironmentalHazardsSettings.sumpLivingMapEnabled;
            float savedPace = RM_EnvironmentalHazardsSettings.sumpLivingMapPace;
            var block = new List<IntVec3>();
            var oldTerrain = new List<TerrainDef>();
            var spawned = new List<Thing>();
            try
            {
                RM_EnvironmentalHazardsSettings.sumpLivingMapEnabled = on;
                RM_EnvironmentalHazardsSettings.sumpLivingMapPace = 1f;
                if (!FindBlock(map, out IntVec3 corner)) return "UNMEASURED: no clear (plant-free, unroofed) 12x12 patch of ordinary ground";
                comp.ClearForProof();
                comp.Rebaseline();
                for (int x = 4; x < 8; x++)
                    for (int z = 4; z < 8; z++)
                    {
                        IntVec3 c = corner + new IntVec3(x, 0, z);
                        block.Add(c);
                        oldTerrain.Add(map.terrainGrid.TerrainAt(c));
                        map.terrainGrid.SetTerrain(c, glass);
                    }
                int t0 = Find.TickManager.TicksGame;
                int seen = comp.Scan(t0);
                int rings = comp.PendingRings, crust = comp.FreshCrustCount;
                bool dreadEarly = comp.IsFreshCrust(block[5], t0 + 1);
                bool dreadLate = comp.IsFreshCrust(block[5], t0 + RM_MapComponent_SumpLivingMap.MouseRerouteDelayTicks + 1);
                for (int h = 1; h <= 240; h++)
                    comp.Process(t0 + h * RM_MapComponent_SumpLivingMap.ScanIntervalTicks, spawned);
                int nSoff = 0, nMirr = 0;
                foreach (Thing t in spawned) { if (t.def == soffeth) nSoff++; else if (t.def == mirrelin) nMirr++; }
                string facts = string.Format("seen={0} rings={1} crust={2} dreadEarly={3} dreadLate={4} soffeth={5} mirrelin={6}",
                    seen, rings, crust, dreadEarly, dreadLate, nSoff, nMirr);
                bool pass = on
                    ? seen == 16 && rings == 1 && crust == 16 && !dreadEarly && dreadLate && nSoff >= 1 && nMirr >= 1
                    : seen == 0 && rings == 0 && crust == 0 && !dreadLate && spawned.Count == 0;
                return (pass ? "PASS " : "FAIL ") + "mode=" + (on ? "on " : "off ") + facts;
            }
            finally
            {
                foreach (Thing t in spawned) if (t != null && !t.Destroyed) t.Destroy();
                for (int i = 0; i < block.Count; i++) map.terrainGrid.SetTerrain(block[i], oldTerrain[i]);
                comp.ClearForProof();
                comp.Rebaseline();
                RM_EnvironmentalHazardsSettings.sumpLivingMapEnabled = savedEnabled;
                RM_EnvironmentalHazardsSettings.sumpLivingMapPace = savedPace;
            }
        }

        private static bool FindBlock(Map map, out IntVec3 corner)
        {
            for (int tries = 0; tries < 2000; tries++)
            {
                IntVec3 c = new IntVec3(Rand.RangeInclusive(0, map.Size.x - 12), 0, Rand.RangeInclusive(0, map.Size.z - 12));
                bool ok = true;
                for (int x = 0; x < 12 && ok; x++)
                    for (int z = 0; z < 12 && ok; z++)
                    {
                        IntVec3 k = c + new IntVec3(x, 0, z);
                        // A clear patch: the proof must be able to plant in it, and it never destroys a plant to make room.
                        ok = k.InBounds(map) && k.Standable(map) && k.GetEdifice(map) == null && !k.Roofed(map)
                             && k.GetPlant(map) == null
                             && !RM_MapComponent_SumpLivingMap.IsTarLiquid(map.terrainGrid.TerrainAt(k))
                             && !RM_MapComponent_SumpLivingMap.IsTarGlass(map.terrainGrid.TerrainAt(k));
                    }
                if (ok) { corner = c; return true; }
            }
            corner = IntVec3.Invalid;
            return false;
        }
    }
}
