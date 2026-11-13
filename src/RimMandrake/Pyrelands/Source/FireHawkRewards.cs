using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// The fire-hawk's first-sighting letter (RIMMANDRAKE_ANNOUNCE_FIREHAWK_EMBER_LETTER_ON_FIRST_SIGHTING). Owner, 2026-11-13:
    /// "letter describing the embers it is currently carrying the first time it's seen is excellent. It is ok that they are
    /// common. That is the threat." The first time in a game a hawk is on a player home map, unfogged, with the ember in its
    /// beak (CompFireHawkSpread.CarryingEmber), one ThreatSmall letter names it, says what it carries and where it is going,
    /// and says the cure is to bring it down. Once per game: the flag is saved here. Toggle: Mod Settings, "Fire-hawk ember
    /// carrying", fireHawkSightingLetterEnabled (ships on). The gate is RM_FireHawkRewardsKernel.TryClaimSighting, which the
    /// offline fuzz (family rewards) drives.
    /// </summary>
    public class GameComponent_RM_FireHawkSighting : GameComponent
    {
        private bool announced;

        /// <summary>Probe (jawa/static_call, firehawk_rewards_live.py): whether this game's letter has been sent.</summary>
        public static string ProbeState()
        {
            GameComponent_RM_FireHawkSighting c = Current.Game?.GetComponent<GameComponent_RM_FireHawkSighting>();
            return c == null ? "component=absent" : "announced=" + c.announced + " letterEnabled=" + RM_PyrelandsSettings.fireHawkSightingLetterEnabled;
        }

        /// <summary>Live-test hook (firehawk_rewards_live.py only): clears this game's once-only flag so a staged sighting can be
        /// replayed on a reused quicktest game. Returns the flag it cleared. Nothing in play calls it.</summary>
        public static string ProbeRearmForLiveTest()
        {
            GameComponent_RM_FireHawkSighting c = Current.Game?.GetComponent<GameComponent_RM_FireHawkSighting>();
            if (c == null) return "component=absent";
            bool was = c.announced;
            c.announced = false;
            return "rearmed wasAnnounced=" + was;
        }

        public GameComponent_RM_FireHawkSighting(Game game)
        {
        }

        public override void GameComponentTick()
        {
            if (announced || !RM_FireHawkRewardsKernel.LookThisTick(Find.TickManager.TicksGame))
            {
                return;
            }
            List<Map> maps = Find.Maps;
            for (int m = 0; m < maps.Count; m++)
            {
                Map map = maps[m];
                if (!map.IsPlayerHome)
                {
                    continue;
                }
                IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
                for (int i = 0; i < pawns.Count; i++)
                {
                    Pawn hawk = pawns[i];
                    CompFireHawkSpread comp = hawk.TryGetComp<CompFireHawkSpread>();
                    if (comp == null)
                    {
                        continue;
                    }
                    if (RM_FireHawkRewardsKernel.TryClaimSighting(ref announced, RM_PyrelandsSettings.fireHawkSightingLetterEnabled,
                            PyrelandsMechanicsGate.On, comp.CarryingEmber, map.IsPlayerHome, hawk.Position.Fogged(map)))
                    {
                        SendLetter(hawk, map);
                        return;
                    }
                }
            }
        }

        /// <summary>The letter, built from the ember the hawk carries now: the fuel it was snatched from (TargetC, the source
        /// cell) and the fuel it is flying to (TargetB, the drop cell), each with its distance and compass bearing from the hawk.</summary>
        private static void SendLetter(Pawn hawk, Map map)
        {
            Job job = hawk.CurJob;
            IntVec3 source = job?.targetC.Cell ?? IntVec3.Invalid;
            IntVec3 target = job?.targetB.Cell ?? IntVec3.Invalid;
            Plant sourcePlant = source.IsValid && source.InBounds(map) ? source.GetPlant(map) : null;
            Plant targetPlant = target.IsValid && target.InBounds(map) ? target.GetPlant(map) : null;
            string ember = sourcePlant != null
                ? "RM_FireHawkEmberFromPlant".Translate(sourcePlant.def.label).ToString()
                : "RM_FireHawkEmberFromBurn".Translate().ToString();
            string toward = targetPlant != null
                ? "RM_FireHawkTargetPlant".Translate(targetPlant.def.label).ToString()
                : "RM_FireHawkTargetGround".Translate().ToString();
            TaggedString text = "RM_FireHawkSightedText".Translate(
                hawk.LabelShortCap.Named("HAWK"), ember.Named("EMBER"),
                Distance(hawk.Position, source).Named("SOURCE_DIST"), Bearing(hawk.Position, source).Named("SOURCE_DIR"),
                toward.Named("TARGET"),
                Distance(hawk.Position, target).Named("TARGET_DIST"), Bearing(hawk.Position, target).Named("TARGET_DIR"));
            Find.LetterStack.ReceiveLetter("RM_FireHawkSightedLabel".Translate(), text, LetterDefOf.ThreatSmall, new LookTargets(hawk));
        }

        private static string Distance(IntVec3 from, IntVec3 to)
        {
            return to.IsValid ? UnityEngine.Mathf.RoundToInt(from.DistanceTo(to)).ToString() : "?";
        }

        private static readonly string[] CompassKeys =
            { "RM_Compass_N", "RM_Compass_NE", "RM_Compass_E", "RM_Compass_SE", "RM_Compass_S", "RM_Compass_SW", "RM_Compass_W", "RM_Compass_NW" };

        private static string Bearing(IntVec3 from, IntVec3 to)
        {
            int k = to.IsValid ? RM_FireHawkRewardsKernel.Compass8(to.x - from.x, to.z - from.z) : -1;
            return k < 0 ? "RM_Compass_Here".Translate().ToString() : CompassKeys[k].Translate().ToString();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref announced, "announced", false);
        }
    }

    /// <summary>
    /// A butcher product dropped only some of the time, which vanilla's butcherProducts cannot say (Thing.ButcherProducts rounds
    /// count x efficiency; there is no chance). On a race ThingDef: one roll per butchered corpse, flat, the butcher's skill
    /// and the difficulty's yield factor ignored (a trophy is found whole or not at all). First user: RM_FireHawk drops the
    /// pristine firehawk crestfeather at 0.35 (owner accepted 35 %, 2026-11-13).
    /// </summary>
    public class RM_ButcherTrophyExtension : DefModExtension
    {
        public ThingDef thingDef;
        public float chance;
        public int count = 1;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (thingDef == null) yield return "RM_ButcherTrophyExtension has no thingDef";
            if (chance <= 0f || chance > 1f) yield return "RM_ButcherTrophyExtension chance " + chance + " is outside (0, 1]";
            if (count < 1) yield return "RM_ButcherTrophyExtension count " + count + " is below 1";
        }
    }

    /// <summary>The postfix that rolls RM_ButcherTrophyExtension: Pawn.ButcherProducts is what Corpse.ButcherProducts (the butcher
    /// recipe's call, GenRecipe) yields from. Applied manually here, the same pattern as FurnaceWarmthField.</summary>
    [StaticConstructorOnStartup]
    public static class ButcherTrophyPatch
    {
        static ButcherTrophyPatch()
        {
            try
            {
                new Harmony("mandrake.rm.pyrelands.butchertrophy").Patch(
                    AccessTools.Method(typeof(Pawn), nameof(Pawn.ButcherProducts)),
                    postfix: new HarmonyMethod(typeof(ButcherTrophyPatch), nameof(Postfix_ButcherProducts)));
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] butcher trophy: ButcherProducts patch FAILED, no hawk drops a crestfeather: " + e.Message);
            }
        }

        /// <summary>Probe (jawa/static_call, firehawk_rewards_live.py): butchers n freshly generated, never-spawned fire-hawks
        /// through the PATCHED Pawn.ButcherProducts under a fixed seed and counts the crestfeathers, then reads the trophy's
        /// Beauty and MarketValue as the running game computes them. Proves the patch is live and the def as loaded.</summary>
        public static string ProbeButcherYield(int n, int seed)
        {
            ThingDef race = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FireHawk");
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_FireHawk");
            RM_ButcherTrophyExtension ext = race?.GetModExtension<RM_ButcherTrophyExtension>();
            if (race == null || kind == null || ext?.thingDef == null) return "MISSING race=" + (race != null) + " kind=" + (kind != null) + " ext=" + (ext?.thingDef != null);
            int trophies = 0, products = 0;
            Rand.PushState(seed);
            try
            {
                for (int i = 0; i < n; i++)
                {
                    Pawn p = PawnGenerator.GeneratePawn(kind, null);
                    foreach (Thing t in p.ButcherProducts(null, 1f))
                    {
                        products++;
                        if (t.def == ext.thingDef) trophies += t.stackCount;
                    }
                    if (!p.Discarded) p.Discard(true);
                }
            }
            finally
            {
                Rand.PopState();
            }
            Thing one = ThingMaker.MakeThing(ext.thingDef);
            return "YIELD n=" + n + " seed=" + seed + " trophies=" + trophies + " products=" + products + " chance=" + ext.chance
                + " beauty=" + one.GetStatValue(StatDefOf.Beauty) + " marketValue=" + one.GetStatValue(StatDefOf.MarketValue)
                + " stackLimit=" + ext.thingDef.stackLimit + " label=" + ext.thingDef.label;
        }

        public static void Postfix_ButcherProducts(Pawn __instance, ref IEnumerable<Thing> __result)
        {
            RM_ButcherTrophyExtension ext = __instance?.def?.GetModExtension<RM_ButcherTrophyExtension>();
            if (ext?.thingDef != null)
            {
                __result = WithTrophy(__result, ext);
            }
        }

        private static IEnumerable<Thing> WithTrophy(IEnumerable<Thing> products, RM_ButcherTrophyExtension ext)
        {
            foreach (Thing t in products)
            {
                yield return t;
            }
            if (RM_FireHawkRewardsKernel.TrophyDrops(Rand.Value, ext.chance))
            {
                Thing trophy = ThingMaker.MakeThing(ext.thingDef);
                trophy.stackCount = Math.Min(ext.count, ext.thingDef.stackLimit);
                yield return trophy;
            }
        }
    }
}
