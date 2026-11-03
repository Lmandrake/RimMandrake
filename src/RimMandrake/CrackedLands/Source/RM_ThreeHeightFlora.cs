using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.CrackedLands
{
    // ════════════════════════════════════════════════════════════════════
    // CRACKEDLANDS_THREE_HEIGHT_FLORA_1 — the canyon's three heights of flora.
    //
    //   floor  RM_QirraMat    red-brown mats that open only on open ground a recede wetted, and live only while it
    //                         stays wet (the soak decay window). Woken by RM_MapComponent_RecedeAftermath.OnRecede.
    //                         Harvest: dye (ruled 2026-10-09 by card).
    //   shade  RM_Veqma       (existing) the shade-line law is a glow limit on its def (ruled 2026-10-09 by card), so
    //                         it holds anywhere, player-sown included: RM_GlowLimitExtension.
    //   wall   RM_TalusClasp  pale clasps that root only touching natural wall rock (RM_WallRootedExtension), seeded
    //                         beside fossil seams at map generation. Ruled 2026-10-09 by card: prying opens fossil
    //                         seams (natural walls only) with a letter each time, mining beside a clasp yields more,
    //                         and cutting one sometimes turns up a fossil from the seam it was prying.
    //
    // Every law is enforced in TWO places: PlantUtility.CanEverPlantAt (wild spawning, sowing, any GenSpawn route that
    // asks) and RM_Plant_FloraLaw.CurrentDyingDamagePerTick (a plant whose cell stops obeying dies back, like any
    // vanilla plant in the wrong light). The arithmetic is RM_FloraLawKernel (fuzzed offline).
    // ════════════════════════════════════════════════════════════════════

    /// <summary>The plant lives only where the cell's DAYLIGHT glow (RM_FloraLawKernel.DaylightGlow) is at most maxGlow.</summary>
    public class RM_GlowLimitExtension : DefModExtension
    {
        public float maxGlow = 0.625f;
    }

    /// <summary>The plant lives only on open dry ground a recede wetted within the soak window.</summary>
    public class RM_FloodWokenExtension : DefModExtension
    {
    }

    /// <summary>The plant lives only where a cardinal neighbour is natural wall rock.</summary>
    public class RM_WallRootedExtension : DefModExtension
    {
        /// <summary>Chance a harvest also turns up a fossil from the seam the clasp was prying.</summary>
        public float fossilFindChance = 0.15f;
    }

    public static class RM_FloraLaws
    {
        public const int LawGlow = 1, LawFlood = 2, LawWall = 4;

        private static readonly Dictionary<ThingDef, int> lawsByDef = new Dictionary<ThingDef, int>();

        public static int LawsOf(ThingDef def)
        {
            if (def == null)
            {
                return 0;
            }
            if (!lawsByDef.TryGetValue(def, out int laws))
            {
                laws = (def.HasModExtension<RM_GlowLimitExtension>() ? LawGlow : 0)
                    | (def.HasModExtension<RM_FloodWokenExtension>() ? LawFlood : 0)
                    | (def.HasModExtension<RM_WallRootedExtension>() ? LawWall : 0);
                lawsByDef[def] = laws;
            }
            return laws;
        }

        public static int LightBlockers(IntVec3 c, Map map)
        {
            int n = 0;
            for (int i = 0; i < 8; i++)
            {
                IntVec3 a = c + GenAdj.AdjacentCells[i];
                if (!a.InBounds(map))
                {
                    continue;
                }
                Building ed = a.GetEdifice(map);
                if (ed != null && ed.def.blockLight)
                {
                    n++;
                }
            }
            return n;
        }

        public static float DaylightGlow(IntVec3 c, Map map)
        {
            float artificial = map.glowGrid.GroundGlowAt(c, false, true);
            return RM_FloraLawKernel.DaylightGlow(c.Roofed(map), artificial, LightBlockers(c, map));
        }

        public static bool IsNaturalRock(IntVec3 c, Map map)
        {
            if (!c.InBounds(map))
            {
                return false;
            }
            Building ed = c.GetEdifice(map);
            return ed != null && ed.def.building != null && ed.def.building.isNaturalRock;
        }

        public static int NaturalWallCardinals(IntVec3 c, Map map)
        {
            int n = 0;
            for (int i = 0; i < 4; i++)
            {
                if (IsNaturalRock(c + GenAdj.CardinalDirections[i], map))
                {
                    n++;
                }
            }
            return n;
        }

        public static bool RecentlyWet(IntVec3 c, Map map)
        {
            RM_MapComponent_ThreeHeightFlora comp = map.GetComponent<RM_MapComponent_ThreeHeightFlora>();
            return comp != null && RM_FloraLawKernel.RecentlyWet(comp.WetUntil(c), Find.TickManager.TicksGame);
        }

        public static bool QirraGround(IntVec3 c, Map map)
        {
            TerrainDef t = c.GetTerrain(map);
            return RM_FloraLawKernel.QirraCellOk(RecentlyWet(c, map), c.Roofed(map), t == null || t.IsWater);
        }

        /// <summary>Null when every law of DEF holds at C; otherwise the reason the first broken law gives.</summary>
        public static string Broken(ThingDef def, IntVec3 c, Map map)
        {
            int laws = LawsOf(def);
            if (laws == 0 || map == null || !c.InBounds(map))
            {
                return null;
            }
            if ((laws & LawGlow) != 0 && RM_CrackedLandsSettings.veqmaShadeLawEnabled)
            {
                float max = def.GetModExtension<RM_GlowLimitExtension>().maxGlow;
                if (!RM_FloraLawKernel.GlowAllowed(DaylightGlow(c, map), max))
                {
                    return "Too much daylight: grows only in shade (the lee of a wall, a roof or a cave).";
                }
            }
            if ((laws & LawFlood) != 0 && !QirraGround(c, map))
            {
                return "Opens only on open ground a flood has just wetted.";
            }
            if ((laws & LawWall) != 0 && !RM_FloraLawKernel.ClaspCellOk(NaturalWallCardinals(c, map)))
            {
                return "Roots only against natural rock wall.";
            }
            return null;
        }
    }

    [HarmonyPatch(typeof(PlantUtility), nameof(PlantUtility.CanEverPlantAt),
        new[] { typeof(ThingDef), typeof(IntVec3), typeof(Map), typeof(Thing), typeof(bool), typeof(bool), typeof(bool) },
        new[] { ArgumentType.Normal, ArgumentType.Normal, ArgumentType.Normal, ArgumentType.Out, ArgumentType.Normal, ArgumentType.Normal, ArgumentType.Normal })]
    [RimMandrake.Shared.PatchFeature("Qirra / veqma / talus clasp placement laws")]
    public static class RM_FloraLawPlacementPatch
    {
        public static void Postfix(ThingDef plantDef, IntVec3 c, Map map, ref AcceptanceReport __result)
        {
            if (!__result.Accepted || RM_FloraLaws.LawsOf(plantDef) == 0)
            {
                return;
            }
            string why = RM_FloraLaws.Broken(plantDef, c, map);
            if (why != null)
            {
                __result = new AcceptanceReport(why);
            }
        }
    }

    /// <summary>The thingClass of every law-bound plant: a plant whose cell stops obeying its law dies back.</summary>
    public class RM_Plant_FloraLaw : Plant
    {
        // TUNED: the vanilla "dying" rate (Plant.CurrentDyingDamagePerTick's 0.005): ten hit points a long tick.
        private const float LawDyingPerTick = 0.005f;

        public bool LawBroken => Spawned && RM_FloraLaws.Broken(def, Position, Map) != null;

        public override float CurrentDyingDamagePerTick
        {
            get
            {
                float d = base.CurrentDyingDamagePerTick;
                return LawBroken ? Mathf.Max(d, LawDyingPerTick) : d;
            }
        }
    }

    /// <summary>The talus clasp: pries its wall into a fresh fossil seam now and then; a cut one may turn up a fossil.</summary>
    public class RM_Plant_TalusClasp : RM_Plant_FloraLaw
    {
        public override void TickLong()
        {
            base.TickLong();
            if (!Spawned || Destroyed || !RM_CrackedLandsSettings.claspPryEnabled || Growth < 0.999f)
            {
                return;
            }
            if (!Rand.Chance(RM_FloraLawKernel.ChancePerLongTick(RM_CrackedLandsSettings.claspPryMtbDays)))
            {
                return;
            }
            Map.GetComponent<RM_MapComponent_ThreeHeightFlora>()?.TryPry(this, false);
        }

#pragma warning disable CS0672, CS0618 // JobDriver_PlantWork still calls PlantCollected in 1.6 (decompiled line 112).
        public override void PlantCollected(Pawn by, PlantDestructionMode plantDestructionMode)
        {
            Map map = Map;
            IntVec3 at = Position;
            bool grown = HarvestableNow;
            float chance = def.GetModExtension<RM_WallRootedExtension>()?.fossilFindChance ?? 0f;
            base.PlantCollected(by, plantDestructionMode);
            if (map != null && grown && Rand.Chance(chance))
            {
                Thing fossil = ThingMaker.MakeThing(RM_ThreeHeightFloraDefOf.RM_FossilImpression);
                if (fossil != null && GenPlace.TryPlaceThing(fossil, at, map, ThingPlaceMode.Near))
                {
                    Messages.Message("Cutting the talus clasp loosened a fossil from the crack it was prying.",
                        new LookTargets(fossil), MessageTypeDefOf.PositiveEvent);
                }
            }
        }
#pragma warning restore CS0672, CS0618
    }

    [DefOf]
    public static class RM_ThreeHeightFloraDefOf
    {
        public static ThingDef RM_QirraMat;
        public static ThingDef RM_TalusClasp;
        public static ThingDef RM_Veqma;
        public static ThingDef RM_FossilImpression;

        static RM_ThreeHeightFloraDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_ThreeHeightFloraDefOf));
        }
    }

    /// <summary>Per map: which cells a recede wetted and until when; the qirra wake; the talus pry and its letter.</summary>
    public class RM_MapComponent_ThreeHeightFlora : MapComponent
    {
        private Dictionary<int, int> wetUntil = new Dictionary<int, int>();
        private int lastPryTick = -1;
        public int pries;
        public int wokenLast;
        public int wakeCandidatesLast;
        public int wokenOffWetLast;

        public RM_MapComponent_ThreeHeightFlora(Map map) : base(map)
        {
        }

        public int WetUntil(IntVec3 c)
        {
            return wetUntil.TryGetValue(map.cellIndices.CellToIndex(c), out int t) ? t : 0;
        }

        public int WetCount()
        {
            int now = Find.TickManager.TicksGame;
            return wetUntil.Count(kv => RM_FloraLawKernel.RecentlyWet(kv.Value, now));
        }

        /// <summary>Called at every recede with its wetted cells: they are wet until the soak decays; qirra mats open.</summary>
        public int OnRecede(List<IntVec3> wetted, int untilTick)
        {
            int now = Find.TickManager.TicksGame;
            foreach (int k in wetUntil.Keys.ToList())
            {
                if (!RM_FloraLawKernel.RecentlyWet(wetUntil[k], now))
                {
                    wetUntil.Remove(k);
                }
            }
            foreach (IntVec3 c in wetted)
            {
                if (c.InBounds(map))
                {
                    int i = map.cellIndices.CellToIndex(c);
                    wetUntil[i] = Math.Max(untilTick, wetUntil.TryGetValue(i, out int old) ? old : 0);
                }
            }
            wokenLast = RM_CrackedLandsSettings.qirraWakeEnabled ? WakeQirra(wetted) : 0;
            return wokenLast;
        }

        private int WakeQirra(List<IntVec3> wetted)
        {
            ThingDef qirra = RM_ThreeHeightFloraDefOf.RM_QirraMat;
            List<IntVec3> good = wetted.FindAll(c => c.InBounds(map) && !c.Fogged(map) && c.GetPlant(map) == null
                && qirra.CanEverPlantAt(c, map));
            int want = RM_FloraLawKernel.QirraWant(good.Count, RM_CrackedLandsSettings.qirraWakeShare, RM_CrackedLandsSettings.qirraWakeMax);
            wakeCandidatesLast = good.Count;
            wokenOffWetLast = 0;
            good.Shuffle();
            int n = 0;
            for (int i = 0; i < want; i++)
            {
                Plant p = (Plant)ThingMaker.MakeThing(qirra);
                p.Growth = Rand.Range(0.3f, 0.6f);
                GenSpawn.Spawn(p, good[i], map);
                if (!RM_FloraLaws.QirraGround(good[i], map)) wokenOffWetLast++;
                n++;
            }
            if (n > 0)
            {
                Messages.Message("The drained clay is blooming rust-red: qirra mats have opened on the wetted ground. They close again as it dries.",
                    new LookTargets(good[0], map), MessageTypeDefOf.NeutralEvent);
            }
            return n;
        }

        /// <summary>A clasp pries one natural wall cell it grips into a fresh fossil seam; a letter says so. FORCE skips
        /// the map-wide gap (the debug action). Returns the cell cut, or Invalid.</summary>
        public IntVec3 TryPry(Plant clasp, bool force)
        {
            int now = Find.TickManager.TicksGame;
            if (!force && !RM_FloraLawKernel.PryAllowedNow(lastPryTick, now, (int)(RM_CrackedLandsSettings.claspPryGapDays * GenDate.TicksPerDay)))
            {
                return IntVec3.Invalid;
            }
            List<IntVec3> walls = new List<IntVec3>();
            for (int i = 0; i < 4; i++)
            {
                IntVec3 n = clasp.Position + GenAdj.CardinalDirections[i];
                if (RM_FossilStrata.IsNaturalWallRock(n, map))
                {
                    walls.Add(n);
                }
            }
            if (walls.Count == 0)
            {
                return IntVec3.Invalid;
            }
            IntVec3 cell = walls.RandomElement();
            ThingDef seam = Rand.Chance(0.15f) ? RM_CrackedLandsDefOf.RM_FossilSeam_Skeleton : RM_CrackedLandsDefOf.RM_FossilSeam_Impression;
            if (!RM_FossilStrata.ReplaceRock(map, cell, seam))
            {
                return IntVec3.Invalid;
            }
            lastPryTick = now;
            pries++;
            Find.LetterStack.ReceiveLetter("Crack pried open",
                "A talus clasp's roots have pried a crack in the canyon wall wide open. The split face shows fossil-bearing "
                + "strata: mine it for the fossils inside. Rock mined beside a clasp yields more, the cracks already started for you.",
                LetterDefOf.NeutralEvent, new LookTargets(cell, map));
            return cell;
        }

        /// <summary>Seeds clasps on open cells touching natural wall, beside the fossil seams (map generation).</summary>
        public static int SeedClasps(Map map)
        {
            ThingDef clasp = RM_ThreeHeightFloraDefOf.RM_TalusClasp;
            HashSet<IntVec3> spots = new HashSet<IntVec3>();
            IEnumerable<Thing> seams = map.listerThings.ThingsOfDef(RM_CrackedLandsDefOf.RM_FossilSeam_Impression)
                .Concat(map.listerThings.ThingsOfDef(RM_CrackedLandsDefOf.RM_FossilSeam_Skeleton))
                .Concat(map.listerThings.ThingsOfDef(RM_CrackedLandsDefOf.RM_FossilSeam_Unique));
            foreach (Thing b in seams)
            {
                for (int i = 0; i < 4; i++)
                {
                    IntVec3 c = b.Position + GenAdj.CardinalDirections[i];
                    if (c.InBounds(map) && c.GetEdifice(map) == null && c.GetPlant(map) == null && clasp.CanEverPlantAt(c, map))
                    {
                        spots.Add(c);
                    }
                }
            }
            int n = 0;
            foreach (IntVec3 c in spots)
            {
                // TUNED: about one open cell in three beside a seam holds a clasp — a scatter, never a hedge.
                if (!Rand.Chance(0.35f))
                {
                    continue;
                }
                Plant p = (Plant)ThingMaker.MakeThing(clasp);
                p.Growth = Rand.Range(0.15f, 1f);
                p.Age = Rand.Range(0, Mathf.Max(1, (int)(clasp.plant.LifespanTicks * 0.5f)));
                GenSpawn.Spawn(p, c, map);
                n++;
            }
            return n;
        }

        public string DebugReport()
        {
            int qirra = 0, qirraOff = 0, clasp = 0, claspOff = 0, veqma = 0, veqmaOver = 0;
            foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.Plant))
            {
                if (t.def == RM_ThreeHeightFloraDefOf.RM_QirraMat)
                {
                    qirra++;
                    if (!RM_FloraLaws.QirraGround(t.Position, map)) qirraOff++;
                }
                else if (t.def == RM_ThreeHeightFloraDefOf.RM_TalusClasp)
                {
                    clasp++;
                    if (!RM_FloraLawKernel.ClaspCellOk(RM_FloraLaws.NaturalWallCardinals(t.Position, map))) claspOff++;
                }
                else if (t.def == RM_ThreeHeightFloraDefOf.RM_Veqma)
                {
                    veqma++;
                    float max = t.def.GetModExtension<RM_GlowLimitExtension>()?.maxGlow ?? 1f;
                    if (!RM_FloraLawKernel.GlowAllowed(RM_FloraLaws.DaylightGlow(t.Position, map), max)) veqmaOver++;
                }
            }
            return "qirra=" + qirra + " qirraOffWet=" + qirraOff + " clasp=" + clasp + " claspOffWall=" + claspOff
                + " veqma=" + veqma + " veqmaOverGlow=" + veqmaOver + " wetCells=" + WetCount() + " wokenLast=" + wokenLast
                + " wakeCandidatesLast=" + wakeCandidatesLast + " wokenOffWetLast=" + wokenOffWetLast
                + " pries=" + pries + " lastPryTick=" + lastPryTick;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref wetUntil, "wetUntil", LookMode.Value, LookMode.Value);
            Scribe_Values.Look(ref lastPryTick, "lastPryTick", -1);
            Scribe_Values.Look(ref pries, "pries");
            if (Scribe.mode == LoadSaveMode.PostLoadInit && wetUntil == null)
            {
                wetUntil = new Dictionary<int, int>();
            }
        }
    }

    /// <summary>Mining a rock cell beside a grown talus clasp yields more: the clasp's roots had already cracked it.</summary>
    [HarmonyPatch(typeof(Mineable), nameof(Mineable.DestroyMined))]
    [RimMandrake.Shared.PatchFeature("Talus clasp mining bonus")]
    public static class RM_TalusClaspMiningPatch
    {
        public struct Site
        {
            public Map map;
            public IntVec3 cell;
            public ThingDef yield;
            public int baseYield;
        }

        public static void Prefix(Mineable __instance, out Site __state)
        {
            __state = default;
            ThingDef y = __instance.def.building?.mineableThing;
            if (y == null || !__instance.Spawned || RM_CrackedLandsSettings.claspMiningBonus <= 0f)
            {
                return;
            }
            __state = new Site { map = __instance.Map, cell = __instance.Position, yield = y, baseYield = __instance.def.building.EffectiveMineableYield };
        }

        public static void Postfix(Pawn pawn, Site __state)
        {
            if (__state.map == null || pawn == null || !BesideGrownClasp(__state.cell, __state.map))
            {
                return;
            }
            int extra = RM_FloraLawKernel.MiningBonus(__state.baseYield, RM_CrackedLandsSettings.claspMiningBonus);
            while (extra > 0)
            {
                Thing t = ThingMaker.MakeThing(__state.yield);
                t.stackCount = Mathf.Min(extra, __state.yield.stackLimit);
                extra -= t.stackCount;
                GenPlace.TryPlaceThing(t, __state.cell, __state.map, ThingPlaceMode.Near);
            }
        }

        public static bool BesideGrownClasp(IntVec3 cell, Map map)
        {
            for (int i = 0; i < 8; i++)
            {
                IntVec3 a = cell + GenAdj.AdjacentCells[i];
                if (a.InBounds(map) && a.GetPlant(map) is Plant p && p.def == RM_ThreeHeightFloraDefOf.RM_TalusClasp && p.Growth >= 0.999f)
                {
                    return true;
                }
            }
            return false;
        }
    }
}
