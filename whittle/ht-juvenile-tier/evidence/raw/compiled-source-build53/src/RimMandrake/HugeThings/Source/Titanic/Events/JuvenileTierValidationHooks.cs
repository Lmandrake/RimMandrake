using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>Entry-state loaded-method probes. Never register, spawn, generate or destroy pawns/defs; no map or game writes.
    /// Fixtures own their race/stage/extension objects. Selecting a stage writes only the local pawn's age-tracker cache,
    /// so actual Pawn.BodySize and GetTier execute without a Game, generation RNG, age progression or flight.</summary>
    public static class JuvenileTierValidationHooks
    {
        private static string F(float value) => value.ToString("R", CultureInfo.InvariantCulture);

        private static string ObserveRace(ThingDef race, int stageIndex)
        {
            int adult = (int)TitanicTierUtility.AdultTier(race), spacing = (int)TitanicTierUtility.SpacingTier(race);
            RM_TitanicTierDef t = TitanicTierUtility.Thresholds;
            string runtime = "unsupported", size = "unsupported", factor = "unsupported";
            if (race?.race?.lifeStageAges != null && stageIndex >= 0 && stageIndex < race.race.lifeStageAges.Count
                && race.race.lifeStageAges[stageIndex]?.def != null)
            {
                var pawn = new Pawn { def = race };
                pawn.ageTracker = new Pawn_AgeTracker(pawn);
                AccessTools.Field(typeof(Pawn_AgeTracker), "cachedLifeStageIndex").SetValue(pawn.ageTracker, stageIndex);
                factor = F(pawn.ageTracker.CurLifeStage.bodySizeFactor);
                size = F(pawn.BodySize);
                runtime = ((int)TitanicTierUtility.GetTier(pawn)).ToString();
            }
            Func<bool, bool> eligible = present => RM_TitanicKernel.TitanEventEligible(adult, spacing,
                false, false, false, false, false, true, true, present);
            RM_TitanicExtension ext = race?.GetModExtension<RM_TitanicExtension>();
            return "race=" + (race?.defName ?? "null") + ";base=" + (race?.race == null ? "null" : F(race.race.baseBodySize))
                + ";stages=" + (race?.race?.lifeStageAges == null ? "null" : string.Join(",", race.race.lifeStageAges.Select(
                    a => a == null ? "null-entry" : a.def == null ? "null-def" : a.def.defName + ":" + F(a.def.bodySizeFactor))))
                + ";force=" + TitanicTierUtility.ForceOf(ext) + ";harness=" + (ext?.harnessOnly == true)
                + ";stageIndex=" + stageIndex + ";factor=" + factor + ";body=" + size + ";GetTier=" + runtime
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
