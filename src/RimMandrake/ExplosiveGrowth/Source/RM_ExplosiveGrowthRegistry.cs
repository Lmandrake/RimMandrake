using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.ExplosiveGrowth
{
    /// <summary>What the engine needs to know about one plant def, resolved once.</summary>
    public sealed class RM_PlantProfile
    {
        public RM_GrowthTop top;
        public float produceFactor = 1f;
        public ThingDef ringPlant;
        public TerrainDef slimeTerrain;
        /// <summary>The ambient bands apply (in the shared scope and not band-exempt).</summary>
        public bool banded;
        public bool tree;

        public bool Soaks => top != RM_GrowthTop.None;
    }

    /// <summary>
    /// Every plant def classified ONCE at startup into an array indexed by
    /// ThingDef.index, so every hot path (the GrowthRate postfix, Print, the
    /// Graphic getter) is one array read. Rebuilt when Mod Settings change.
    /// </summary>
    public static class RM_ExplosiveGrowthRegistry
    {
        // R-G5 defaults in the RM tier: vanilla/DLC defNames only.
        private static readonly string[] BuiltinExempt =
        {
            "Plant_TreeAnima", "Plant_TreeGauranlen", "Plant_Ambrosia",
        };

        private static RM_PlantProfile[] byIndex = new RM_PlantProfile[0];
        private static HashSet<BiomeDef> noSoakBiomes = new HashSet<BiomeDef>();
        private static HashSet<BiomeDef> terminatorBiomes = new HashSet<BiomeDef>();
        private static HashSet<BiomeDef> wetAmbientBiomes = new HashSet<BiomeDef>();

        public static List<PawnKindDef> RupturePawnKinds = new List<PawnKindDef>();
        public static List<HediffDef> RuptureMutationHediffs = new List<HediffDef>();
        public static HashSet<string> IrrigationFluids = new HashSet<string>();
        public static HashSet<WeatherDef> SoakWeathers = new HashSet<WeatherDef>();

        public static bool Ready { get; private set; }

        public static int CountSoaking, CountNone, RosterResolved, RosterMissing;
        // THE SCOPE IS A BIOME (owner, 2026-10-16, PLANT_GROWTH_MERGE_NEVER_MEANT_APART: "there should just be an option
        // in Baroque Biomes to allow the accelerated plant growth and explosive growth to apply to other biomes, but we
        // won't test or support that"). Everyday bands and the soak run on maps whose biome Baroque Biomes ships; the
        // option (off, unsupported) or a campaign roster's scopeAllBiomes extends both to every biome.
        /// <summary>BiomeDefs shipped by this engine's own mod (read at the last Rebuild).</summary>
        public static HashSet<BiomeDef> HomeBiomes = new HashSet<BiomeDef>();
        /// <summary>defName of a roster that sets scopeAllBiomes (every biome in scope, the option moot), else null.</summary>
        public static string ScopeForcedBy;
        /// <summary>TEST-ONLY scope override for the north-star suite (RM_ExplosiveGrowthProof.ProofTestScopeAll*): every
        /// biome in scope, but never Scribed, so a run that dies part-way cannot persist it to the player's settings
        /// file. Off at every game start. The suites stage on quicktest maps, whose biome is rarely ours.</summary>
        public static bool TestScopeAll;

        /// <summary>Both tiers run on this biome's maps. Null (an unspawned or held plant) is out of scope unless
        /// every biome is.</summary>
        public static bool BiomeInScope(BiomeDef biome) =>
            ExplosiveGrowthSettings.applyInOtherBiomes || ScopeForcedBy != null || TestScopeAll
            || (biome != null && HomeBiomes.Contains(biome));
        public static readonly int[] CountByTop = new int[7];
        /// <summary>Ambient bands (PLANT_GROWTH_MERGE_NEVER_MEANT_APART): plant defs the bands scale, plant defs left
        /// alone (exempt or under the grow-days floor, in scope), and the resolved biome rosters.</summary>
        public static int BandedCount, BandExemptCount, TerminatorBiomeCount, WetAmbientBiomeCount;

        public static RM_PlantProfile For(ThingDef def)
        {
            int i = def.index;
            return i < byIndex.Length ? byIndex[i] : null;
        }

        /// <summary>Rebuild, logging (not throwing) a failure; the previous table stays in force. -> success.</summary>
        public static bool TryRebuild(string why)
        {
            try
            {
                Rebuild();
                return true;
            }
            catch (System.Exception e)
            {
                Log.Error("[RM ExplosiveGrowth] plant table rebuild (" + why + ") failed; the previous table stays in force: " + e);
                return false;
            }
        }

        /// <summary>No soak forms on this biome's maps: a carve-out (terminator, deep desert), or out of scope.</summary>
        public static bool BiomeRefusesSoak(BiomeDef biome) =>
            (biome != null && noSoakBiomes.Contains(biome)) || !BiomeInScope(biome);

        public static bool IsTerminatorBiome(BiomeDef biome) => biome != null && terminatorBiomes.Contains(biome);
        public static bool IsWetAmbientBiome(BiomeDef biome) => biome != null && wetAmbientBiomes.Contains(biome);

        /// <summary>Rebuilds into locals and swaps them in only at the end, so a throw part-way leaves the previous table
        /// (and Ready) in force. Callers after startup use TryRebuild.</summary>
        public static void Rebuild()
        {
            var rows = new Dictionary<string, RM_ExplosiveGrowthRosterEntry>();
            string forcedBy = null;
            var exempt = new HashSet<string>(BuiltinExempt);
            var biomes = new HashSet<BiomeDef>();
            var kinds = new List<PawnKindDef>();
            var hediffs = new List<HediffDef>();
            var fluids = new HashSet<string>();
            var weathers = new HashSet<WeatherDef>();
            var bandExempt = new HashSet<string>(BuiltinExempt);
            var termBiomes = new HashSet<BiomeDef>();
            var wetBiomes = new HashSet<BiomeDef>();
            int missing = 0, resolved = 0;

            foreach (RM_ExplosiveGrowthRosterDef roster in DefDatabase<RM_ExplosiveGrowthRosterDef>.AllDefsListForReading)
            {
                foreach (RM_ExplosiveGrowthRosterEntry e in roster.plants)
                {
                    if (string.IsNullOrEmpty(e?.plant)) continue;
                    rows[e.plant] = e;
                }
                if (roster.scopeAllBiomes && forcedBy == null) forcedBy = roster.defName;
                foreach (string s in roster.exemptPlants) exempt.Add(s);
                foreach (string s in roster.noSoakBiomes)
                {
                    BiomeDef b = DefDatabase<BiomeDef>.GetNamedSilentFail(s);
                    if (b != null) biomes.Add(b);
                }
                foreach (string s in roster.rupturePawnKinds)
                {
                    PawnKindDef k = DefDatabase<PawnKindDef>.GetNamedSilentFail(s);
                    if (k != null && !kinds.Contains(k)) kinds.Add(k);
                }
                foreach (string s in roster.ruptureMutationHediffs)
                {
                    HediffDef h = DefDatabase<HediffDef>.GetNamedSilentFail(s);
                    if (h != null && !hediffs.Contains(h)) hediffs.Add(h);
                }
                foreach (string s in roster.irrigationFluids) fluids.Add(s);
                foreach (string s in roster.soakWeathers)
                {
                    WeatherDef w = DefDatabase<WeatherDef>.GetNamedSilentFail(s);
                    if (w != null) weathers.Add(w);
                }
                foreach (string s in roster.bandExemptPlants) bandExempt.Add(s);
                // Silent when absent: the rosters list every plausible name (campaign twin, RM_ biome, donor), and a
                // player running only one of them should not see a warning per load. The startup line counts them.
                foreach (string s in roster.terminatorBiomes)
                {
                    BiomeDef b = DefDatabase<BiomeDef>.GetNamedSilentFail(s);
                    if (b != null) termBiomes.Add(b);
                }
                foreach (string s in roster.wetAmbientBiomes)
                {
                    BiomeDef b = DefDatabase<BiomeDef>.GetNamedSilentFail(s);
                    if (b != null) wetBiomes.Add(b);
                }
            }

            // The native scope: the BiomeDefs this engine's own mod (Baroque Biomes) ships.
            ModContentPack home = ExplosiveGrowthMod.Home;
            var homeBiomes = new HashSet<BiomeDef>();
            if (home != null)
                foreach (BiomeDef b in DefDatabase<BiomeDef>.AllDefsListForReading)
                    if (b.modContentPack == home) homeBiomes.Add(b);

            var table = new RM_PlantProfile[DefDatabase<ThingDef>.DefCount];
            var byTop = new int[CountByTop.Length];
            int soaking = 0, none = 0, banded = 0, bandLeft = 0;

            foreach (ThingDef def in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (def.plant == null || def.index >= table.Length) continue;

                var p = new RM_PlantProfile { top = RM_GrowthTop.Churn };

                RM_ExplosiveGrowthExtension ext = def.GetModExtension<RM_ExplosiveGrowthExtension>();
                if (ext != null)
                {
                    p.top = ext.top;
                    p.produceFactor = ext.produceFactor;
                    p.ringPlant = ext.ringPlant;
                    p.slimeTerrain = ext.slimeTerrain;
                }
                else if (rows.TryGetValue(def.defName, out RM_ExplosiveGrowthRosterEntry row))
                {
                    p.top = row.top;
                    p.produceFactor = row.produceFactor;
                    if (!string.IsNullOrEmpty(row.ringPlant))
                        p.ringPlant = DefDatabase<ThingDef>.GetNamedSilentFail(row.ringPlant);
                    if (!string.IsNullOrEmpty(row.slimeTerrain))
                        p.slimeTerrain = DefDatabase<TerrainDef>.GetNamedSilentFail(row.slimeTerrain);
                }

                // R-G5 exemptions and the under-a-day clause: an exempt plant
                // never soaks (design doc §0). Cave plants (fungus) are the
                // design's "the Sheen is not water / fungal biomes" carve-out
                // generalised to the RM tier — INVENTED, a Mod Settings toggle.
                if (exempt.Contains(def.defName)
                    || def.plant.growDays < ExplosiveGrowthSettings.minGrowDaysToSoak
                    || (ExplosiveGrowthSettings.cavePlantsNeverSoak && def.plant.cavePlant && ext == null && !rows.ContainsKey(def.defName)))
                {
                    p.top = RM_GrowthTop.None;
                }

                // The ambient bands' plant-side filter (scope is the map's biome, checked at runtime).
                p.tree = def.plant.IsTree;
                p.banded = !bandExempt.Contains(def.defName) && def.plant.growDays >= ExplosiveGrowthSettings.minGrowDaysToBoost;
                if (p.banded) banded++; else bandLeft++;

                table[def.index] = p;
                byTop[(int)p.top]++;
                if (p.Soaks) soaking++; else none++;
            }

            foreach (string name in rows.Keys)
            {
                if (DefDatabase<ThingDef>.GetNamedSilentFail(name) != null) resolved++;
                else missing++;
            }

            byIndex = table;
            noSoakBiomes = biomes;
            terminatorBiomes = termBiomes;
            wetAmbientBiomes = wetBiomes;
            BandedCount = banded;
            BandExemptCount = bandLeft;
            TerminatorBiomeCount = termBiomes.Count;
            WetAmbientBiomeCount = wetBiomes.Count;
            RupturePawnKinds = kinds;
            RuptureMutationHediffs = hediffs;
            IrrigationFluids = fluids;
            SoakWeathers = weathers;
            System.Array.Copy(byTop, CountByTop, byTop.Length);
            CountSoaking = soaking;
            CountNone = none;
            RosterResolved = resolved;
            RosterMissing = missing;
            HomeBiomes = homeBiomes;
            ScopeForcedBy = forcedBy;
            Ready = true;
        }
    }
}
