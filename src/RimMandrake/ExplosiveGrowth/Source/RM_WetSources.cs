using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.ExplosiveGrowth
{
    // ════════════════════════════════════════════════════════════════════
    // "IS THIS CELL WET?" — THE ONE SOURCE REGISTRY (spec §2, §3).
    //
    // A cell is WET while at least one live source is present on it whose liquid the plant standing there accepts (T2:
    // clean water waters everything; any other liquid only a plant that lists it). There is no settle state, no fresh
    // event, no re-arm (W3: "It always counts as fresh as long as it's there. It's continuous."). Every reader — the
    // GrowthRate postfix, the dormancy prefix, the arming pass, setting A's "water nearby" — asks THIS registry.
    //
    // Built-in sources, in read order (cheapest first):
    //   natural   river / fresh water / marsh / mud terrain: its own cell only, permanent, never used up (W2)
    //   timed     a flood or surge pushed through ExplosiveGrowthAPI (Cracked Lands, the salt line): while it runs (OQ-13)
    //   spill     standing-water filth: a hose spill of water, a poured can, a rain puddle (D6; consumed = destroyed)
    //   channel   a FlowWorks dug cell holding an accepted liquid waters itself and its 8 neighbours (D5)
    //   rain      unroofed ground while a water rain (or snowmelt, OQ-3) falls, and a few hours after (OQ-9)
    //
    // THE SEAM for sprinklers and ponds (SPRINKLERS_DESIGN_PIPES_THEN_PANACHE, deferred by SP1): implement IRM_WetSource and
    // call RM_WetSources.Register once at startup. Nothing else in the engine needs to change.
    // ════════════════════════════════════════════════════════════════════
    public interface IRM_WetSource
    {
        /// <summary>Short name for reports ("natural", "spill", ...).</summary>
        string Key { get; }
        /// <summary>Its Mod Settings switch (all-off degrades to vanilla).</summary>
        bool Enabled { get; }
        /// <summary>A liquid this source holds on cell c is one of <paramref name="accepts"/>. Must not allocate.</summary>
        bool WetFor(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now);
        /// <summary>A fruiting plant used this water (OQ-8, EC3). Return true if anything was used up. A natural source
        /// returns false and keeps its water.</summary>
        bool Consume(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now);
    }

    public static class RM_WetSources
    {
        private static readonly List<IRM_WetSource> sources = new List<IRM_WetSource>
        {
            new NaturalWaterSource(), new TimedSource(), new SpillFilthSource(), new ChannelSource(), new RainSource(),
        };

        public static IReadOnlyList<IRM_WetSource> All => sources;

        /// <summary>Add a source (sprinklers, ponds, another mod's water). Idempotent by Key.</summary>
        public static void Register(IRM_WetSource s)
        {
            if (s == null) return;
            for (int i = 0; i < sources.Count; i++) if (sources[i].Key == s.Key) { sources[i] = s; return; }
            sources.Add(s);
        }

        /// <summary>The cell is wet for a plant accepting <paramref name="accepts"/>. Suppressed ground and a no-soak biome
        /// are never wet.</summary>
        public static bool IsWet(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now)
        {
            return WetBy(comp, c, accepts, now) != null;
        }

        /// <summary>The first source wetting the cell, or null.</summary>
        public static IRM_WetSource WetBy(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now)
        {
            if (comp == null || accepts == null || comp.NoWaterHere || comp.IsSuppressed(c, now)) return null;
            for (int i = 0; i < sources.Count; i++)
            {
                IRM_WetSource s = sources[i];
                if (s.Enabled && s.WetFor(comp, c, accepts, now)) return s;
            }
            return null;
        }

        /// <summary>Setting A: an accepted source within <paramref name="radius"/> cells (Chebyshev, OQ-17: 2).</summary>
        public static bool WaterNearby(RM_MapComponent_ExplosiveGrowth comp, IntVec3 center, HashSet<string> accepts, int radius, int now)
        {
            Map map = comp.map;
            for (int dz = -radius; dz <= radius; dz++)
                for (int dx = -radius; dx <= radius; dx++)
                {
                    IntVec3 c = new IntVec3(center.x + dx, 0, center.z + dz);
                    if (c.InBounds(map) && IsWet(comp, c, accepts, now)) return true;
                }
            return false;
        }

        /// <summary>Use up every consumable source wetting the cell for this plant; -> how many gave water.</summary>
        public static int Consume(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now)
        {
            if (comp == null || accepts == null) return 0;
            int n = 0;
            for (int i = 0; i < sources.Count; i++)
            {
                IRM_WetSource s = sources[i];
                try
                {
                    if (s.Enabled && s.WetFor(comp, c, accepts, now) && s.Consume(comp, c, accepts, now)) n++;
                }
                catch (Exception e)
                {
                    Log.WarningOnce("[RM ExplosiveGrowth] water source " + s.Key + " failed to consume: " + e.Message, 0x5E0B ^ s.Key.GetHashCode());
                }
            }
            return n;
        }

        // ── the built-in sources ─────────────────────────────────────────

        private sealed class NaturalWaterSource : IRM_WetSource
        {
            public string Key => "natural";
            public bool Enabled => ExplosiveGrowthSettings.naturalWaterEnabled;
            public bool WetFor(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now)
                => accepts.Contains(RM_ExplosiveGrowthRegistry.CleanWater) && RM_ExplosiveGrowthRegistry.IsNaturalWater(c.GetTerrain(comp.map));
            public bool Consume(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now) => false;
        }

        /// <summary>Floods and surges carry clean water; a running one is never used up (spec §2.2).</summary>
        private sealed class TimedSource : IRM_WetSource
        {
            public string Key => "timed";
            public bool Enabled => true;   // each pusher has its own switch (Cracked Lands's coupling, the surge toggle)
            public bool WetFor(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now)
                => accepts.Contains(RM_ExplosiveGrowthRegistry.CleanWater) && comp.IsTimedSoaked(c, now);
            public bool Consume(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now) => false;
        }

        private sealed class SpillFilthSource : IRM_WetSource
        {
            public string Key => "spill";
            public bool Enabled => ExplosiveGrowthSettings.spillWaterEnabled && RM_ExplosiveGrowthRegistry.FilthLiquids.Count > 0;

            private static Thing Find(Map map, IntVec3 c, HashSet<string> accepts)
            {
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    Thing t = things[i];
                    if (t is Filth && RM_ExplosiveGrowthRegistry.FilthLiquids.TryGetValue(t.def, out string liquid) && accepts.Contains(liquid))
                        return t;
                }
                return null;
            }

            public bool WetFor(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now) => Find(comp.map, c, accepts) != null;

            public bool Consume(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now)
            {
                Thing t = Find(comp.map, c, accepts);
                if (t == null) return false;
                t.Destroy();
                return true;
            }
        }

        private sealed class ChannelSource : IRM_WetSource
        {
            public string Key => "channel";
            public bool Enabled => ExplosiveGrowthSettings.irrigationSoakEnabled && RimMandrake.Shared.FlowWorksIrrigationRead.Available;

            public bool WetFor(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now)
            {
                RimMandrake.Shared.FlowWorksIrrigationRead.Grids g = comp.ChannelGrids(accepts);
                if (g == null) return false;
                Map map = comp.map;
                CellIndices idx = map.cellIndices;
                if (g.IsSource(idx.CellToIndex(c))) return true;
                for (int d = 0; d < 8; d++)
                {
                    IntVec3 nb = c + GenAdj.AdjacentCells[d];
                    if (nb.InBounds(map) && g.IsSource(idx.CellToIndex(nb))) return true;
                }
                return false;
            }

            // OWED (EG_CHANNEL_DRAW_NEEDS_A_FLOWWORKS_EXIT): the crop draw-down (cropDrawLitres) needs FlowWorks to disclose a
            // "drunk by plants" exit in its L0 ledger; taking a level through TryTakeLevel would be an undisclosed exit. Until
            // FlowWorks ships one, ChannelDraw stays null and a channel's water is not used up. The seam is this delegate.
            public bool Consume(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now)
                => ChannelDraw != null && ChannelDraw(comp.map, c, ExplosiveGrowthSettings.cropDrawLevels);
        }

        /// <summary>The channel draw-down hook (map, plant cell, levels) -> drew anything. Set by FlowWorks when it ships a
        /// disclosed plant-use exit; null today.</summary>
        public static Func<Map, IntVec3, int, bool> ChannelDraw;

        private sealed class RainSource : IRM_WetSource
        {
            public string Key => "rain";
            public bool Enabled => ExplosiveGrowthSettings.rainWaterEnabled;
            public bool WetFor(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now)
                => accepts.Contains(RM_ExplosiveGrowthRegistry.CleanWater) && comp.RainWetAt(c, now);
            public bool Consume(RM_MapComponent_ExplosiveGrowth comp, IntVec3 c, HashSet<string> accepts, int now)
                => comp.ConsumeRain(c, now);
        }
    }
}
