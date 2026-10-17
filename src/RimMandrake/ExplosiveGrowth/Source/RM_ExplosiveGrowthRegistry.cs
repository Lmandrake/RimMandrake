using System.Collections.Generic;
using System.Linq;
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
        /// <summary>The ruled archetype (spec §4.3), seeded from the biomes' plant lists unless a row decides.</summary>
        public RM_Archetype archetype = RM_Archetype.Vanilla;
        /// <summary>EC1's old tree rule, kept ONLY for a tree-rules-exempt plant that yields wood (RM_Greatbole, §0: "the build
        /// leaves its ExplosiveGrowth handling as it is"): the tree ratio (0.625) of its archetype's rate. The tree rules
        /// replaced it for every other plant (T1, T2: "treeRatio retired"); fungi take their archetype's rate (Q9).</summary>
        public bool woody;
        /// <summary>tree_burst_design_2026-10-17.md §2 (Q2, Q9, §0): a native whose visual max is 3.0+, not a fungus, not
        /// tree-exempt. No x10, never cycles; water buys it days of life; its end of life is a burst (§3, §4, §6a).</summary>
        public bool isTree;
        /// <summary>Q9: marked a fungus by a roster (never a tree).</summary>
        public bool fungus;
        /// <summary>The tree burst's logs (WoodLog) for a tree whose harvest is not wood; -1 = the Mod Setting default (Q12).</summary>
        public int burstLogs = -1;
        /// <summary>A log tree's own fruit at its burst (Q16), or null.</summary>
        public ThingDef burstFruit;
        public int burstFruitCount;
        /// <summary>-1 = the archetype default (kernel ResolveOutcome).</summary>
        public float ruptureChance = -1f;
        public IntRange sproutCount = IntRange.Zero;
        /// <summary>The liquids that water this plant: clean water plus its adapted liquids (T2). Interned: plants with the
        /// same set share one object, so the channel read caches one grid per distinct set.</summary>
        public HashSet<string> liquids;

        /// <summary>The top is not None (a None plant grows at its archetype's rate but never cycles).</summary>
        public bool Soaks => top != RM_GrowthTop.None;
        /// <summary>One of our natives (dry, wet or fire-adapted): setting B and crop self-fruit (OQ-15) read this.</summary>
        public bool Native => archetype == RM_Archetype.DryNative || archetype == RM_Archetype.WetNative || archetype == RM_Archetype.FireAdapted;
        public bool Accepts(string liquid) => liquid != null && liquids != null && liquids.Contains(liquid);
    }

    /// <summary>
    /// Every plant def classified ONCE at startup into an array indexed by ThingDef.index, so every hot path (the GrowthRate
    /// postfix, Print, the Graphic getter, the TickLong prefix) is one array read. Rebuilt when Mod Settings change.
    /// </summary>
    public static class RM_ExplosiveGrowthRegistry
    {
        // Spec §2.5 exempt row: vanilla/DLC defNames only.
        private static readonly string[] BuiltinExempt =
        {
            "Plant_TreeAnima", "Plant_TreeGauranlen", "Plant_Ambrosia",
        };
        public const string CleanWater = "RM_Fluid_Water";

        private static RM_PlantProfile[] byIndex = new RM_PlantProfile[0];
        private static HashSet<BiomeDef> noSoakBiomes = new HashSet<BiomeDef>();
        private static HashSet<BiomeDef> terminatorBiomes = new HashSet<BiomeDef>();
        private static HashSet<BiomeDef> snowmeltBiomes = new HashSet<BiomeDef>();
        private static bool[] naturalWater = new bool[0];

        public static List<PawnKindDef> RupturePawnKinds = new List<PawnKindDef>();
        public static List<HediffDef> RuptureMutationHediffs = new List<HediffDef>();
        /// <summary>The clean-water set (every plant accepts it; vanilla plants accept only it).</summary>
        public static HashSet<string> CleanWaterSet = new HashSet<string> { CleanWater };
        public static HashSet<WeatherDef> SoakWeathers = new HashSet<WeatherDef>();
        /// <summary>D6: filth def -> the liquid it is.</summary>
        public static Dictionary<ThingDef, string> FilthLiquids = new Dictionary<ThingDef, string>();
        /// <summary>Every distinct accepted-liquid set in use (the channel read caches one grid per set).</summary>
        public static List<HashSet<string>> LiquidSets = new List<HashSet<string>>();
        public static bool TidallyLocked { get; private set; }

        public static bool Ready { get; private set; }

        public static int CountSoaking, CountNone, RosterResolved, RosterMissing, CountTrees, CountFungi;
        public static readonly int[] CountByTop = new int[7];
        public static readonly int[] CountByArchetype = new int[5];
        public static int TerminatorBiomeCount, WetBiomeCount, FireBiomeCount, NaturalWaterTerrainCount, FilthLiquidCount;

        // THE SCOPE IS A BIOME (owner, 2026-10-16): the engine runs on maps whose biome Baroque Biomes ships, or every biome
        // while a campaign roster sets scopeAllBiomes. Setting B (unsupported, off) extends OUR plants' rule elsewhere.
        public static HashSet<BiomeDef> HomeBiomes = new HashSet<BiomeDef>();
        public static string ScopeForcedBy;
        /// <summary>TEST-ONLY scope override for the north-star suite (never Scribed; off at every game start).</summary>
        public static bool TestScopeAll;

        /// <summary>Our biome (or every biome by roster or the test override): vanilla plants obey setting A here and our
        /// natives run their archetype.</summary>
        public static bool BiomeInScope(BiomeDef biome) =>
            ScopeForcedBy != null || TestScopeAll || (biome != null && HomeBiomes.Contains(biome));

        /// <summary>This plant's rule applies on this biome's maps: in scope, or (setting B "same rule", unsupported) a native
        /// anywhere. OQ-10: B defaults to vanilla.</summary>
        public static bool PlantInScope(RM_PlantProfile p, BiomeDef biome) =>
            BiomeInScope(biome) || (p != null && p.Native && ExplosiveGrowthSettings.nativesSameRuleInOtherBiomes);

        /// <summary>Any plant on this map can run the rule (the map pass gate).</summary>
        public static bool MapMayRun(BiomeDef biome) => BiomeInScope(biome) || ExplosiveGrowthSettings.nativesSameRuleInOtherBiomes;

        public static RM_PlantProfile For(ThingDef def)
        {
            int i = def.index;
            return i < byIndex.Length ? byIndex[i] : null;
        }

        public static bool IsNaturalWater(TerrainDef t) => t != null && t.index < naturalWater.Length && naturalWater[t.index];

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

        /// <summary>No water counts on this biome's maps: a carve-out (deep desert), or out of scope.</summary>
        public static bool BiomeRefusesSoak(BiomeDef biome) =>
            (biome != null && noSoakBiomes.Contains(biome)) || !MapMayRun(biome);

        public static bool IsNoSoakBiome(BiomeDef biome) => biome != null && noSoakBiomes.Contains(biome);
        public static bool IsTerminatorBiome(BiomeDef biome) => biome != null && terminatorBiomes.Contains(biome);
        public static bool IsSnowmeltBiome(BiomeDef biome) => biome != null && snowmeltBiomes.Contains(biome);

        private static void AddBiomes(List<string> names, HashSet<BiomeDef> into)
        {
            // Silent when absent: rosters list every plausible name (campaign twin, RM_ biome, donor).
            foreach (string s in names)
            {
                BiomeDef b = DefDatabase<BiomeDef>.GetNamedSilentFail(s);
                if (b != null) into.Add(b);
            }
        }

        private static void PlantsOf(IEnumerable<BiomeDef> biomes, HashSet<ThingDef> into)
        {
            foreach (BiomeDef b in biomes)
            {
                if (b.wildPlants == null) continue;
                foreach (BiomePlantRecord r in b.wildPlants)
                    if (r?.plant != null) into.Add(r.plant);
            }
        }

        private static bool OurBiome(BiomeDef b, HashSet<BiomeDef> home) =>
            home.Contains(b) || b.defName.StartsWith("RM_") || b.defName.StartsWith("RUT_") || b.defName.StartsWith("RSW_");

        private static bool ShippedByUs(ThingDef def)
        {
            string pid = def.modContentPack?.PackageId;
            return pid != null && pid.StartsWith("mandrake.");
        }

        private static bool IsLudeon(ThingDef def)
        {
            ModContentPack m = def.modContentPack;
            return m != null && (m.IsOfficialMod || (m.PackageId != null && m.PackageId.StartsWith("ludeon.")));
        }

        /// <summary>Rebuilds into locals and swaps them in only at the end, so a throw part-way leaves the previous table
        /// (and Ready) in force.</summary>
        public static void Rebuild()
        {
            var rows = new Dictionary<string, RM_ExplosiveGrowthRosterEntry>();
            string forcedBy = null;
            bool locked = false;
            var exempt = new HashSet<string>(BuiltinExempt);
            var biomes = new HashSet<BiomeDef>();
            var kinds = new List<PawnKindDef>();
            var hediffs = new List<HediffDef>();
            var clean = new HashSet<string>();
            var weathers = new HashSet<WeatherDef>();
            var termBiomes = new HashSet<BiomeDef>();
            var wetBiomes = new HashSet<BiomeDef>();
            var fireBiomes = new HashSet<BiomeDef>();
            var snowBiomes = new HashSet<BiomeDef>();
            var waterTerrains = new HashSet<string>();
            var filth = new Dictionary<ThingDef, string>();
            var fungi = new HashSet<string>();
            var treeExempt = new HashSet<string>();
            var treeBursts = new Dictionary<string, RM_TreeBurstEntry>();
            int missing = 0, resolved = 0;

            foreach (RM_ExplosiveGrowthRosterDef roster in DefDatabase<RM_ExplosiveGrowthRosterDef>.AllDefsListForReading)
            {
                foreach (RM_ExplosiveGrowthRosterEntry e in roster.plants)
                {
                    if (string.IsNullOrEmpty(e?.plant)) continue;
                    rows[e.plant] = e;
                }
                if (roster.scopeAllBiomes && forcedBy == null) forcedBy = roster.defName;
                if (roster.tidallyLockedWorld) locked = true;
                foreach (string s in roster.exemptPlants) exempt.Add(s);
                foreach (string s in roster.bandExemptPlants) exempt.Add(s);
                AddBiomes(roster.noSoakBiomes, biomes);
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
                foreach (string s in roster.cleanWaterFluids) clean.Add(s);
                foreach (string s in roster.soakWeathers)
                {
                    WeatherDef w = DefDatabase<WeatherDef>.GetNamedSilentFail(s);
                    if (w != null) weathers.Add(w);
                }
                AddBiomes(roster.terminatorBiomes, termBiomes);
                AddBiomes(roster.wetNativeBiomes, wetBiomes);
                AddBiomes(roster.fireAdaptedBiomes, fireBiomes);
                AddBiomes(roster.snowmeltBiomes, snowBiomes);
                foreach (string s in roster.naturalWaterTerrains) waterTerrains.Add(s);
                foreach (RM_FilthLiquidEntry f in roster.filthLiquids)
                {
                    ThingDef fd = string.IsNullOrEmpty(f?.filth) ? null : DefDatabase<ThingDef>.GetNamedSilentFail(f.filth);
                    if (fd != null && !string.IsNullOrEmpty(f.liquid)) filth[fd] = f.liquid;
                }
                foreach (string s in roster.fungi) if (!string.IsNullOrEmpty(s)) fungi.Add(s);
                foreach (string s in roster.treeRulesExempt) if (!string.IsNullOrEmpty(s)) treeExempt.Add(s);
                foreach (RM_TreeBurstEntry b in roster.treeBursts)
                    if (!string.IsNullOrEmpty(b?.plant)) treeBursts[b.plant] = b;
            }
            if (clean.Count == 0) clean.Add(CleanWater);

            ModContentPack home = ExplosiveGrowthMod.Home;
            var homeBiomes = new HashSet<BiomeDef>();
            if (home != null)
                foreach (BiomeDef b in DefDatabase<BiomeDef>.AllDefsListForReading)
                    if (b.modContentPack == home) homeBiomes.Add(b);

            // §4.3 seeds, from the plant lists (OQ-1).
            var wetPlants = new HashSet<ThingDef>();
            var firePlants = new HashSet<ThingDef>();
            var ourBiomePlants = new HashSet<ThingDef>();
            PlantsOf(wetBiomes, wetPlants);
            PlantsOf(fireBiomes, firePlants);
            PlantsOf(DefDatabase<BiomeDef>.AllDefsListForReading.Where(b => OurBiome(b, homeBiomes)), ourBiomePlants);

            var water = new bool[DefDatabase<TerrainDef>.DefCount];
            int waterCount = 0;
            foreach (TerrainDef t in DefDatabase<TerrainDef>.AllDefsListForReading)
                if (t.index < water.Length && waterTerrains.Contains(t.defName)) { water[t.index] = true; waterCount++; }

            var sets = new Dictionary<string, HashSet<string>>();
            HashSet<string> Intern(IEnumerable<string> extra)
            {
                var all = new SortedSet<string>(clean);
                if (extra != null) foreach (string x in extra) if (!string.IsNullOrEmpty(x)) all.Add(x);
                string key = string.Join("|", all);
                if (!sets.TryGetValue(key, out HashSet<string> set)) sets[key] = set = new HashSet<string>(all);
                return set;
            }
            HashSet<string> cleanSet = Intern(null);

            var table = new RM_PlantProfile[DefDatabase<ThingDef>.DefCount];
            var byTop = new int[CountByTop.Length];
            var byArch = new int[CountByArchetype.Length];
            int soaking = 0, none = 0, trees = 0, fungusCount = 0;

            foreach (ThingDef def in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (def.plant == null || def.index >= table.Length) continue;

                var p = new RM_PlantProfile { top = RM_GrowthTop.Churn };
                RM_ArchetypeChoice choice = RM_ArchetypeChoice.Auto;
                bool fireFlag = false, enrolled = false;
                List<string> adapted = null;

                RM_ExplosiveGrowthExtension ext = def.GetModExtension<RM_ExplosiveGrowthExtension>();
                if (ext != null)
                {
                    enrolled = true;
                    p.top = ext.top;
                    p.produceFactor = ext.produceFactor;
                    p.ringPlant = ext.ringPlant;
                    p.slimeTerrain = ext.slimeTerrain;
                    p.ruptureChance = ext.ruptureChance;
                    p.sproutCount = ext.sproutCount;
                    choice = ext.archetype;
                    fireFlag = ext.fireAdapted;
                    adapted = ext.adaptedLiquids;
                }
                else if (rows.TryGetValue(def.defName, out RM_ExplosiveGrowthRosterEntry row))
                {
                    enrolled = true;
                    p.top = row.top;
                    p.produceFactor = row.produceFactor;
                    if (!string.IsNullOrEmpty(row.ringPlant))
                        p.ringPlant = DefDatabase<ThingDef>.GetNamedSilentFail(row.ringPlant);
                    if (!string.IsNullOrEmpty(row.slimeTerrain))
                        p.slimeTerrain = DefDatabase<TerrainDef>.GetNamedSilentFail(row.slimeTerrain);
                    p.ruptureChance = row.ruptureChance;
                    p.sproutCount = row.sproutCount;
                    choice = row.archetype;
                    fireFlag = row.fireAdapted;
                    adapted = row.adaptedLiquids;
                }
                // A Burst-top row is "1 in 1" unless it says otherwise (C3: "Some plants are 1 in 1").
                if (p.ruptureChance < 0f && p.top == RM_GrowthTop.Burst) p.ruptureChance = 1f;

                // A row that DECIDES the plant's kind (an archetype, or fireAdapted) outranks the under-a-day clause: the
                // owner's Pyrelands-grass ruling (C3, "grow violently quickly and spread itself super-fast") names
                // RM_FE_Plant_EmberGrass (growDays 0.8), which the clause alone would leave at vanilla speed.
                bool decided = choice != RM_ArchetypeChoice.Auto || fireFlag;
                bool isExempt = exempt.Contains(def.defName)
                    || (!decided && def.plant.growDays < ExplosiveGrowthSettings.minGrowDaysToSoak)
                    || (ExplosiveGrowthSettings.cavePlantsNeverSoak && def.plant.cavePlant && !enrolled);

                RM_Archetype a;
                if (isExempt || choice == RM_ArchetypeChoice.Exempt) a = RM_Archetype.Exempt;
                else if (choice == RM_ArchetypeChoice.DryNative) a = RM_Archetype.DryNative;
                else if (choice == RM_ArchetypeChoice.WetNative) a = RM_Archetype.WetNative;
                else if (choice == RM_ArchetypeChoice.FireAdapted || fireFlag || firePlants.Contains(def)) a = RM_Archetype.FireAdapted;
                // §4.3: a plant in a wet biome's list is wet native, even if a dry biome lists it too (the conservative
                // rate until its sheet row decides).
                else if (wetPlants.Contains(def)) a = RM_Archetype.WetNative;
                else if (enrolled || ShippedByUs(def) || (ourBiomePlants.Contains(def) && !IsLudeon(def))) a = RM_Archetype.DryNative;
                else a = RM_Archetype.Vanilla;

                if (a == RM_Archetype.Exempt || a == RM_Archetype.Vanilla) p.top = RM_GrowthTop.None;
                p.archetype = a;
                p.fungus = fungi.Contains(def.defName);
                bool native = a == RM_Archetype.DryNative || a == RM_Archetype.WetNative || a == RM_Archetype.FireAdapted;
                p.isTree = native && !p.fungus && !treeExempt.Contains(def.defName)
                    && def.plant.visualSizeRange.max >= RM_ExplosiveGrowthKernel.TreeMinVisualSize;
                p.woody = treeExempt.Contains(def.defName) && (def.plant.IsTree || def.plant.harvestedThingDef == ThingDefOf.WoodLog);
                if (p.isTree && treeBursts.TryGetValue(def.defName, out RM_TreeBurstEntry tb))
                {
                    p.burstLogs = tb.logs;
                    if (!string.IsNullOrEmpty(tb.fruit) && tb.fruitCount > 0)
                    {
                        p.burstFruit = DefDatabase<ThingDef>.GetNamedSilentFail(tb.fruit);
                        p.burstFruitCount = p.burstFruit != null ? tb.fruitCount : 0;
                    }
                }
                if (p.isTree) trees++;
                if (p.fungus) fungusCount++;
                p.liquids = a == RM_Archetype.Vanilla ? cleanSet : Intern(adapted);

                table[def.index] = p;
                byTop[(int)p.top]++;
                byArch[(int)a]++;
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
            snowmeltBiomes = snowBiomes;
            naturalWater = water;
            TerminatorBiomeCount = termBiomes.Count;
            WetBiomeCount = wetBiomes.Count;
            FireBiomeCount = fireBiomes.Count;
            NaturalWaterTerrainCount = waterCount;
            FilthLiquidCount = filth.Count;
            RupturePawnKinds = kinds;
            RuptureMutationHediffs = hediffs;
            CleanWaterSet = cleanSet;
            SoakWeathers = weathers;
            FilthLiquids = filth;
            LiquidSets = sets.Values.ToList();
            TidallyLocked = locked;
            System.Array.Copy(byTop, CountByTop, byTop.Length);
            System.Array.Copy(byArch, CountByArchetype, byArch.Length);
            CountSoaking = soaking;
            CountNone = none;
            CountTrees = trees;
            CountFungi = fungusCount;
            RosterResolved = resolved;
            RosterMissing = missing;
            HomeBiomes = homeBiomes;
            ScopeForcedBy = forcedBy;
            Ready = true;
        }
    }
}
