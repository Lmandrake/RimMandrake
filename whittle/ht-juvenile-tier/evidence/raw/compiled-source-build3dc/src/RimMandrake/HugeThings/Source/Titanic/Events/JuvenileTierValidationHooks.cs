using System;
using System.Collections.Generic;
using System.Reflection;
using System.Globalization;
using System.Linq;
using System.Text;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>Entry-state loaded-method probes. Never register, spawn, generate or destroy pawns/defs; no map or game writes.
    /// Fixtures own race/stage/extension objects and fresh pawns with engine age/health trackers. VEF's live postfix takes
    /// its needs-null/living-pawn default-cache branch; its memo references are observed, never cleared or unpatched,
    /// and die when the proof process stops. No generated-pawn gene/hediff modifier or age-progression claim.</summary>
    public static class JuvenileTierValidationHooks
    {
        private static string F(float value) => value.ToString("R", CultureInfo.InvariantCulture);
        private static object Static(string type, string field) => AccessTools.Field(AccessTools.TypeByName(type), field).GetValue(null);
        private static object Member(object owner, string field) => AccessTools.Field(owner.GetType(), field).GetValue(owner);
        private const string VefData = "VEF.AestheticScaling.CachedPawnData";
        private const string VefPostfix = "VEF.Genes.VanillaExpandedFramework_Pawn_BodySize";

        /// <summary>Read-only environment/patch/cache inventory on the same bridge main thread as the probes.</summary>
        public static string Environment()
        {
            var methods = new MethodBase[] {
                AccessTools.PropertyGetter(typeof(Pawn), "BodySize"), AccessTools.PropertyGetter(typeof(Pawn), "Dead"),
                AccessTools.Constructor(typeof(Pawn_HealthTracker), new[] { typeof(Pawn) }),
                AccessTools.PropertyGetter(typeof(Pawn_AgeTracker), "CurLifeStage"),
                AccessTools.Method(typeof(TitanicTierUtility), "GetTier") };
            string patches = string.Join("|", methods.Select(m => {
                var info = Harmony.GetPatchInfo(m);
                IEnumerable<string> owners = info == null ? Enumerable.Empty<string>() : info.Owners;
                return m.DeclaringType.FullName + "." + m.Name + ":" + string.Join(",", owners.OrderBy(x => x));
            }));
            object data = Static(VefData, "defaultCache");
            return "program=" + Current.ProgramState + ";gameNull=" + (Current.Game == null)
                + ";rand=" + AccessTools.Property(typeof(Rand), "StateCompressed").GetValue(null, null)
                + ";thingDefs=" + DefDatabase<ThingDef>.AllDefsListForReading.Count
                + ";stageDefs=" + DefDatabase<LifeStageDef>.AllDefsListForReading.Count
                + ";kindDefs=" + DefDatabase<PawnKindDef>.AllDefsListForReading.Count
                + ";engineMvid=" + typeof(Pawn).Assembly.ManifestModule.ModuleVersionId
                + ";modMvid=" + typeof(TitanicTierUtility).Assembly.ManifestModule.ModuleVersionId
                + ";vefMvid=" + AccessTools.TypeByName(VefData).Assembly.ManifestModule.ModuleVersionId
                + ";vefOffset=" + F((float)Member(data, "bodySizeOffset"))
                + ";vefCacheCount=" + ((System.Collections.IDictionary)Static(VefData, "cache")).Count
                + ";patches=" + patches;
        }


        private static string ObserveRace(ThingDef race, int stageIndex)
        {
            int adult = (int)TitanicTierUtility.AdultTier(race), spacing = (int)TitanicTierUtility.SpacingTier(race);
            RM_TitanicTierDef t = TitanicTierUtility.Thresholds;
            string runtime = "unsupported", size = "unsupported", factor = "unsupported", sizeAgain = "unsupported", bits = "unsupported", vef = "unsupported";
            if (race?.race?.lifeStageAges != null && stageIndex >= 0 && stageIndex < race.race.lifeStageAges.Count
                && race.race.lifeStageAges[stageIndex]?.def != null)
            {
                var pawn = new Pawn { def = race };
                pawn.ageTracker = new Pawn_AgeTracker(pawn);
                AccessTools.Field(typeof(Pawn_AgeTracker), "cachedLifeStageIndex").SetValue(pawn.ageTracker, stageIndex);
                // VEF.GetPawnDataCache asks Pawn.Dead when needs is null. Construct the required engine tracker;
                // never write healthState or add a needs tracker to force a modifier-computation path.
                pawn.health = new Pawn_HealthTracker(pawn);
                if (pawn.needs != null || pawn.genes != null || pawn.story != null || pawn.Dead || pawn.health.hediffSet.hediffs.Count != 0)
                    throw new InvalidOperationException("Non-neutral fixture trackers");
                factor = F(pawn.ageTracker.CurLifeStage.bodySizeFactor);
                float first = pawn.BodySize;
                runtime = ((int)TitanicTierUtility.GetTier(pawn)).ToString();
                float second = pawn.BodySize;
                int firstBits = BitConverter.ToInt32(BitConverter.GetBytes(first), 0);
                int secondBits = BitConverter.ToInt32(BitConverter.GetBytes(second), 0);
                if (firstBits != secondBits) throw new InvalidOperationException("BodySize changed between actual reads");
                size = F(first); sizeAgain = F(second); bits = firstBits.ToString("X8");
                object memo = Static(VefPostfix, "sizeCache"), data = Static(VefData, "defaultCache");
                bool memoPawn = ReferenceEquals(Member(memo, "pawn"), pawn), memoDefault = ReferenceEquals(Member(memo, "cache"), data);
                if (!memoPawn || !memoDefault || pawn.needs != null) throw new InvalidOperationException("Unexpected VEF fixture cache branch");
                vef = "defaultCache,needsNull,alive,emptyHediffs,unspawned:" + (!pawn.Spawned)
                    + ",memoOwnPawn:" + memoPawn + ",memoDefault:" + memoDefault + ",offset:" + F((float)Member(data, "bodySizeOffset"))
                    + ",Tick10:" + Static("VEF.AestheticScaling.CachedPawnDataSlowUpdate", "Tick10");
            }
            Func<bool, bool> eligible = present => RM_TitanicKernel.TitanEventEligible(adult, spacing,
                false, false, false, false, false, true, true, present);
            RM_TitanicExtension ext = race?.GetModExtension<RM_TitanicExtension>();
            return "race=" + (race?.defName ?? "null") + ";base=" + (race?.race == null ? "null" : F(race.race.baseBodySize))
                + ";stages=" + (race?.race?.lifeStageAges == null ? "null" : string.Join(",", race.race.lifeStageAges.Select(
                    a => a == null ? "null-entry" : a.def == null ? "null-def" : a.def.defName + ":" + F(a.def.bodySizeFactor))))
                + ";force=" + TitanicTierUtility.ForceOf(ext) + ";harness=" + (ext?.harnessOnly == true)
                + ";stageIndex=" + stageIndex + ";factor=" + factor + ";body=" + size + ";GetTier=" + runtime
                + ";bodyAgain=" + sizeAgain + ";bodyFloat32Bits=" + bits + ";VEF=" + vef
                + ";AdultTier=" + adult + ";SpacingTier=" + spacing + ";DefQualifies=" + TitanicTierUtility.DefQualifies(race)
                + ";eligibleNoT3=" + eligible(false) + ";eligibleWithT3=" + eligible(true)
                + ";thresholds=" + F(t.t1MinBodySize) + "," + F(t.t2MinBodySize) + "," + F(t.t3MinBodySize);
        }

        public static string Observe(ThingDef race, int stageIndex) => ObserveRace(race, stageIndex);

        public static string Fixture(float baseSize, string factors, int force, int stageIndex)
        {
            var race = new ThingDef { defName = "RM_JuvenileTierLocalFixture", race = new RaceProperties { baseBodySize = baseSize } };
            race.modExtensions = new List<DefModExtension> { new RM_TitanicExtension {
                forceEnabled = force < 0 ? (bool?)false : force > 0 ? (bool?)true : null } };
            if (factors == "null-list") race.race.lifeStageAges = null;
            else
            {
                race.race.lifeStageAges = new List<LifeStageAge>();
                if (factors != "empty") foreach (string token in factors.Split(','))
                {
                    if (token == "null-entry") race.race.lifeStageAges.Add(null);
                    else race.race.lifeStageAges.Add(new LifeStageAge { def = token == "null-def" ? null :
                        new LifeStageDef { defName = "RM_LocalStage", bodySizeFactor = float.Parse(token, CultureInfo.InvariantCulture) } });
                }
            }
            return ObserveRace(race, stageIndex);
        }

        /// <summary>All resolved kinds, no name-based eligibility filter. This is tier census, not map eligibility.</summary>
        public static string Census()
        {
            return string.Join("\n", DefDatabase<PawnKindDef>.AllDefsListForReading.Where(k => k.race?.race != null)
                .OrderBy(k => k.defName).Select(k => "kind=" + k.defName + ";" + ObserveRace(k.race, -1)));
        }

        /// <summary>Exhaustive unchanged habitat/pool/season gates with explicit occupied/unoccupied T3 input.</summary>
        public static string GateMatrix(int adultTier, int spacingTier)
        {
            var sb = new StringBuilder();
            for (int bits = 0; bits < 256; bits++)
            {
                Func<int, bool> b = i => (bits & (1 << i)) != 0;
                bool result = RM_TitanicKernel.TitanEventEligible(adultTier, spacingTier, b(0), b(1), b(2), b(3), b(4), b(5), b(6), b(7));
                sb.Append(result ? '1' : '0');
            }
            return sb.ToString();
        }
    }
}
