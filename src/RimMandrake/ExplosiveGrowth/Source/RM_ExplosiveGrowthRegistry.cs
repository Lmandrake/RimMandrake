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

        public static List<PawnKindDef> RupturePawnKinds = new List<PawnKindDef>();
        public static List<HediffDef> RuptureMutationHediffs = new List<HediffDef>();
        public static HashSet<string> IrrigationFluids = new HashSet<string>();
        public static HashSet<WeatherDef> SoakWeathers = new HashSet<WeatherDef>();

        public static bool Ready { get; private set; }

        public static int CountSoaking, CountNone, RosterResolved, RosterMissing;
        public static readonly int[] CountByTop = new int[7];

        public static RM_PlantProfile For(ThingDef def)
        {
            int i = def.index;
            return i < byIndex.Length ? byIndex[i] : null;
        }

        public static bool BiomeRefusesSoak(BiomeDef biome) =>
            biome != null && noSoakBiomes.Contains(biome);

        public static void Rebuild()
        {
            Ready = false;

            var rows = new Dictionary<string, RM_ExplosiveGrowthRosterEntry>();
            var exempt = new HashSet<string>(BuiltinExempt);
            var biomes = new HashSet<BiomeDef>();
            var kinds = new List<PawnKindDef>();
            var hediffs = new List<HediffDef>();
            var fluids = new HashSet<string>();
            var weathers = new HashSet<WeatherDef>();
            int missing = 0, resolved = 0;

            foreach (RM_ExplosiveGrowthRosterDef roster in DefDatabase<RM_ExplosiveGrowthRosterDef>.AllDefsListForReading)
            {
                foreach (RM_ExplosiveGrowthRosterEntry e in roster.plants)
                {
                    if (!string.IsNullOrEmpty(e?.plant)) rows[e.plant] = e;
                }
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
            }

            var table = new RM_PlantProfile[DefDatabase<ThingDef>.DefCount];
            for (int t = 0; t < CountByTop.Length; t++) CountByTop[t] = 0;
            int soaking = 0, none = 0;

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

                table[def.index] = p;
                CountByTop[(int)p.top]++;
                if (p.Soaks) soaking++; else none++;
            }

            foreach (string name in rows.Keys)
            {
                if (DefDatabase<ThingDef>.GetNamedSilentFail(name) != null) resolved++;
                else missing++;
            }

            byIndex = table;
            noSoakBiomes = biomes;
            RupturePawnKinds = kinds;
            RuptureMutationHediffs = hediffs;
            IrrigationFluids = fluids;
            SoakWeathers = weathers;
            CountSoaking = soaking;
            CountNone = none;
            RosterResolved = resolved;
            RosterMissing = missing;
            Ready = true;
        }
    }
}
