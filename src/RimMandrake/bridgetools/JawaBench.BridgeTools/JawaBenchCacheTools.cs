// JawaBenchCacheTools.cs - reading the caches that lie.
//
// WHY THIS FILE EXISTS
// ====================
// Tile carries four private caches that NOTHING in RimWorld ever invalidates:
//
//     private Hilliness? hillinessLabelCached;
//     private float?     cachedMaxTemp;
//     private float?     cachedMinTemp;
//     private bool?      tmpHasSecondaryBiome;   // + tmpSecondaryBiome
//
// (Read out of RimWorld/Planet/Tile.cs, 1.6, not remembered.)
//
// Every other validator in this companion reads the RAW field on purpose, because
// the cached getters report the pre-write value for the rest of the session. That
// is the right call for validating a write - but it left a whole class of damage
// invisible: after a repaint, the raw field is correct, every automated check
// passes, and the UI still uses the stale cache. The owner found it by CLICKING
// TILES and reporting that mountains stayed unclickable. That is the opposite of
// what an instrument is for.
//
// So this file does the one thing the rest of the companion refuses to do: it
// reads the CACHE, deliberately, and puts it beside a freshly recomputed value so
// a divergence is a NUMBER instead of an anecdote.
//
// HOW IT AVOIDS BECOMING THE BUG IT MEASURES
// ==========================================
// The obvious implementation - call t.HillinessLabel and compare it to
// t.hilliness - is WRONG TWICE:
//
//  1. HillinessLabel is NOT just hilliness. The getter seeds itself from the raw
//     field and then lets any mutator with hillinessLabel != Undefined override
//     it. Comparing the label to the raw field therefore reports a false stale on
//     every tile carrying such a mutator, forever.
//  2. Touching the getter POPULATES the cache when it is empty. An audit that
//     reads through the property would quietly fill in every unpopulated tile as
//     it went, changing the very state it claims to measure.
//
// This reads the private fields by REFLECTION - no side effect, and it can tell
// "cached and wrong" apart from "never cached" - and recomputes the expected
// value by replaying the getter's own logic. Two independent sources, which is
// what the criterion "must not silently return the raw value twice" demands.
//
// THREAD AFFINITY: same rule as every other file here. Everything that touches
// game state is inside ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ================================================================
        //  Reflection handles onto Tile's private caches.
        //  Resolved once, and every one of them is checked for null at the
        //  call site: a RimWorld update that renames a field must make this
        //  tool REFUSE, not silently report zero divergences.
        // ================================================================
        private static readonly FieldInfo FiHillinessLabelCached =
            typeof(Tile).GetField("hillinessLabelCached", BindingFlags.NonPublic | BindingFlags.Instance);
        private static readonly FieldInfo FiCachedMinTemp =
            typeof(Tile).GetField("cachedMinTemp", BindingFlags.NonPublic | BindingFlags.Instance);
        private static readonly FieldInfo FiCachedMaxTemp =
            typeof(Tile).GetField("cachedMaxTemp", BindingFlags.NonPublic | BindingFlags.Instance);
        private static readonly FieldInfo FiTmpHasSecondaryBiome =
            typeof(Tile).GetField("tmpHasSecondaryBiome", BindingFlags.NonPublic | BindingFlags.Instance);

        /// <summary>
        /// Replays Tile.HillinessLabel's own logic WITHOUT touching the property,
        /// so the cache is neither read nor populated: seed from the raw field,
        /// then let any mutator with an explicit hillinessLabel override it.
        /// </summary>
        private static Hilliness ExpectedHillinessLabel(Tile t)
        {
            Hilliness result = t.hilliness;
            foreach (TileMutatorDef m in t.Mutators)
            {
                if (m.hillinessLabel != Hilliness.Undefined) result = m.hillinessLabel;
            }
            return result;
        }

        /// <summary>True when this tile really does carry a mixed-biome mutator.</summary>
        private static bool ExpectedHasSecondaryBiome(Tile t)
        {
            foreach (TileMutatorDef m in t.Mutators)
            {
                if (m.Worker is TileMutatorWorker_MixedBiome) return true;
            }
            return false;
        }

        [Tool(
            "jawa/world_cache_audit",
            Description =
                "Count the tiles whose PRIVATE CACHES disagree with a freshly recomputed value. " +
                "Tile caches hillinessLabelCached, cachedMinTemp, cachedMaxTemp and " +
                "tmpHasSecondaryBiome lazily and NOTHING IN RIMWORLD EVER INVALIDATES THEM, so " +
                "after any repaint the raw fields are right, every raw-field validator passes, " +
                "and the UI still uses the old value - which is what makes repainted mountains " +
                "stay unclickable. THIS IS THE ONLY TOOL HERE THAT READS THE CACHE ON PURPOSE. " +
                "It reads the private fields by reflection, so it has NO side effect and can " +
                "tell 'cached and wrong' from 'never cached'; reading the public getters would " +
                "populate the empty ones and destroy the measurement. EXPECTED USE: audit after " +
                "a repaint and expect a non-zero staleHilliness; save, reload, audit again and " +
                "expect ZERO. There is no cache-clearing tool because RimWorld has no reset " +
                "method for these - a RELOAD is the only fix, and that is the finding, not a " +
                "limitation of this tool. Temperature checking is OFF by default because " +
                "recomputing min/max per tile samples the year and is slow over a whole planet.",
            ResultDescription =
                "success, tilesScanned, and per cache: cachedCount (populated), staleCount " +
                "(populated AND disagreeing), plus up to 'limit' example rows showing cached vs " +
                "expected. staleTotal is the one number that answers 'did the repaint stick'.")]
        public static async Task<object> WorldCacheAudit(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated tile ids. Omit both this and 'range' to scan every surface tile.")]
            string tiles = null,
            [ToolParameter(Description = "Inclusive range 'from-to', e.g. '0-4999'. Combines with 'tiles'.")]
            string range = null,
            [ToolParameter(Description = "Max example rows returned. Counts always cover the whole scan. Default 50.")]
            int limit = 50,
            [ToolParameter(Description = "Also check cachedMinTemp/cachedMaxTemp. SLOW over a whole planet - recomputes the yearly curve per tile. Default false.")]
            bool includeTemps = false,
            [ToolParameter(Description = "Tolerance in Celsius before a temperature cache counts as stale. Default 0.01.")]
            float tempEpsilon = 0.01f,
            [ToolParameter(Description = "AFTER measuring, touch the public getters so empty caches become populated. CHANGES STATE - off by default. A tile with no cache cannot go stale, so this is how you arm a before/after test: populate, repaint, audit again. Never combine with a measurement you intend to trust as 'before'.")]
            bool populate = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (FiHillinessLabelCached == null || FiTmpHasSecondaryBiome == null
                    || FiCachedMinTemp == null || FiCachedMaxTemp == null)
                {
                    return Fail(
                        "Tile's private cache fields could not be resolved by reflection - RimWorld may have renamed them. " +
                        "REFUSING rather than reporting zero divergences, which would look exactly like a pass.",
                        new
                        {
                            hillinessLabelCached = FiHillinessLabelCached != null,
                            cachedMinTemp = FiCachedMinTemp != null,
                            cachedMaxTemp = FiCachedMaxTemp != null,
                            tmpHasSecondaryBiome = FiTmpHasSecondaryBiome != null,
                        });
                }

                WorldGrid grid = Find.WorldGrid;
                if (grid == null) return Fail("No world grid - is a world loaded?");

                // ---- resolve the tile set -------------------------------------
                var ids = new List<int>();
                var refused = new List<object>();
                if (string.IsNullOrEmpty(tiles) && string.IsNullOrEmpty(range))
                {
                    for (int i = 0; i < grid.TilesCount; i++) ids.Add(i);
                }
                else
                {
                    if (!string.IsNullOrEmpty(tiles))
                    {
                        foreach (string part in tiles.Split(','))
                        {
                            int n;
                            if (int.TryParse(part.Trim(), out n)) ids.Add(n);
                            else refused.Add(new { value = part.Trim(), reason = "not an integer" });
                        }
                    }
                    if (!string.IsNullOrEmpty(range))
                    {
                        string[] fromTo = range.Split('-');
                        int a, b;
                        if (fromTo.Length == 2 && int.TryParse(fromTo[0].Trim(), out a) && int.TryParse(fromTo[1].Trim(), out b))
                        {
                            if (b < a) { int t = a; a = b; b = t; }
                            for (int i = a; i <= b; i++) ids.Add(i);
                        }
                        else refused.Add(new { value = range, reason = "not a 'from-to' range" });
                    }
                }

                int scanned = 0;
                int hillCached = 0, hillStale = 0;
                int biomeCached = 0, biomeStale = 0;
                int minCached = 0, minStale = 0, maxCached = 0, maxStale = 0;
                int newlyPopulated = 0;
                int staleTileCount = 0;
                var rows = new List<object>();

                bool completed = true;
                foreach (int id in ids)
                {
                    if (cancellationToken.IsCancellationRequested) { completed = false; break; }
                    if (id < 0 || id >= grid.TilesCount)
                    {
                        if (refused.Count < 50) refused.Add(new { value = id, reason = "out of range" });
                        continue;
                    }
                    Tile t = grid[id];
                    if (t == null)
                    {
                        if (refused.Count < 50) refused.Add(new { value = id, reason = "null tile" });
                        continue;
                    }
                    scanned++;

                    bool anyStale = false;
                    string why = null;

                    // ---- hilliness label -------------------------------------
                    var hCached = (Hilliness?)FiHillinessLabelCached.GetValue(t);
                    Hilliness hExpected = ExpectedHillinessLabel(t);
                    if (hCached.HasValue)
                    {
                        hillCached++;
                        if (hCached.Value != hExpected)
                        {
                            hillStale++; anyStale = true;
                            why = "hilliness";
                        }
                    }

                    // ---- secondary biome presence ----------------------------
                    var bCached = (bool?)FiTmpHasSecondaryBiome.GetValue(t);
                    bool bExpected = ExpectedHasSecondaryBiome(t);
                    if (bCached.HasValue)
                    {
                        biomeCached++;
                        if (bCached.Value != bExpected)
                        {
                            biomeStale++; anyStale = true;
                            why = why == null ? "secondaryBiome" : why + "+secondaryBiome";
                        }
                    }

                    // ---- temperatures, opt-in --------------------------------
                    float? minC = null, maxC = null, minE = null, maxE = null;
                    if (includeTemps)
                    {
                        minC = (float?)FiCachedMinTemp.GetValue(t);
                        maxC = (float?)FiCachedMaxTemp.GetValue(t);
                        if (minC.HasValue)
                        {
                            minCached++;
                            minE = GenTemperature.MinTemperatureAtTile(t.tile);
                            if (Math.Abs(minC.Value - minE.Value) > tempEpsilon)
                            {
                                minStale++; anyStale = true;
                                why = why == null ? "minTemp" : why + "+minTemp";
                            }
                        }
                        if (maxC.HasValue)
                        {
                            maxCached++;
                            maxE = GenTemperature.MaxTemperatureAtTile(t.tile);
                            if (Math.Abs(maxC.Value - maxE.Value) > tempEpsilon)
                            {
                                maxStale++; anyStale = true;
                                why = why == null ? "maxTemp" : why + "+maxTemp";
                            }
                        }
                    }

                    // ---- optional ARM step, strictly AFTER the measurement ----
                    // Touching the getters fills an empty cache. Done first it would
                    // guarantee agreement and make every audit a pass, so it happens
                    // here, once this tile's comparison is already recorded.
                    if (populate)
                    {
                        if (!hCached.HasValue) { var _ = t.HillinessLabel; newlyPopulated++; }
                        // ⚠️ tmpHasSecondaryBiome is filled ONLY by Tile.Biomes, and Biomes is an
                        // ITERATOR - touching the property runs none of its body. It must be
                        // enumerated. Without this the secondary-biome cache is never armed, so
                        // the arm/repaint/re-audit cycle reports secondaryBiome.stale = 0 forever,
                        // which is indistinguishable from a pass.
                        if (!bCached.HasValue) { foreach (BiomeDef unused in t.Biomes) { } newlyPopulated++; }
                        if (includeTemps)
                        {
                            if (!minC.HasValue) { var _ = t.MinTemperature; newlyPopulated++; }
                            if (!maxC.HasValue) { var _ = t.MaxTemperature; newlyPopulated++; }
                        }
                    }

                    if (anyStale)
                    {
                        staleTileCount++;
                    }
                    if (anyStale && rows.Count < Math.Max(0, limit))
                    {
                        rows.Add(new
                        {
                            tile = id,
                            stale = why,
                            hillinessRaw = t.hilliness.ToString(),
                            hillinessLabelCached = hCached.HasValue ? hCached.Value.ToString() : null,
                            hillinessLabelExpected = hExpected.ToString(),
                            secondaryBiomeCached = bCached,
                            secondaryBiomeExpected = bExpected,
                            minTempCached = minC,
                            minTempExpected = minE,
                            maxTempCached = maxC,
                            maxTempExpected = maxE,
                        });
                    }
                }

                int staleTotal = hillStale + biomeStale + minStale + maxStale;

                return (object)new
                {
                    success = true,
                    completed,
                    tilesScanned = scanned,
                    staleTotal,
                    hilliness = new { cached = hillCached, stale = hillStale },
                    secondaryBiome = new { cached = biomeCached, stale = biomeStale },
                    minTemp = new { cached = minCached, stale = minStale, checked_ = includeTemps },
                    maxTemp = new { cached = maxCached, stale = maxStale, checked_ = includeTemps },
                    newlyPopulated,
                    examples = rows,
                    exampleCap = limit,
                    examplesTruncated = staleTileCount > rows.Count,
                    refusedCount = refused.Count,
                    refused,
                    populateRequested = populate,
                    note = !completed
                        ? "SCAN CANCELLED before every tile in `tiles`/the full sweep was checked - staleTotal/tilesScanned cover only the tiles reached, NOT the whole requested set. Treat this as inconclusive, not a pass."
                        : includeTemps
                            ? "A non-zero staleTotal means a RELOAD is required; RimWorld has no reset for these caches."
                            : "Temperature caches were NOT checked - pass includeTemps=true. A non-zero staleTotal means a RELOAD is required.",
                    ticksGame = TicksGameSafe(),
                };
            });
        }
    }
}
