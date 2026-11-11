using System.Linq;
using System.Text;
using RimWorld;
using Verse;
using Verse.AI.Group;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// TITAN_CAMPS_SCAVENGERS_EVENTS_1 live criteria A2-A5: PUBLIC STATIC wrappers so `jawa/static_call` (which refuses instance
    /// methods) can drive the corpse site's daily step and the passage's arrival, and read back one text line each. Current map
    /// only. Validation surface: nothing in play calls these.
    /// </summary>
    public static class TitanValidationHooks
    {
        /// <summary>Generates an adult of `kindDefName` at `cell` and kills it there, so the real Corpse.SpawnSetup -> corpse-site
        /// conversion path runs. Returns the corpse's tier and id.</summary>
        public static string KillTitanAt(string kindDefName, IntVec3 cell)
        {
            Map map = Find.CurrentMap;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(kindDefName);
            if (map == null || kind == null) return "FAIL no map or kind " + kindDefName;
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer, map.Tile,
                allowDowned: true, fixedBiologicalAge: kind.RaceProps.lifeStageAges.Last().minAge + 1f));
            GenSpawn.Spawn(p, cell, map);
            string tier = TitanicTierUtility.GetTier(p).ToString();
            p.Kill(null);
            return "killed " + p.ThingID + " tier=" + tier + " bodySize=" + p.BodySize.ToString("0.0") + " corpse=" + (p.Corpse?.ThingID ?? "none");
        }

        public static string SiteReport()
        {
            Map map = Find.CurrentMap;
            if (map == null) return "FAIL no map";
            var sites = map.listerThings.AllThings.OfType<Building_TitanicCorpseSite>().ToList();
            var sb = new StringBuilder("sites=" + sites.Count);
            foreach (var s in sites)
            {
                sb.Append(" | ").Append(s.ThingID).Append(" at ").Append(s.Position.x).Append(',').Append(s.Position.z)
                  .Append(" meat=").Append(s.MeatRemaining).Append(" eaten=").Append(s.VisitorsEatenTotal)
                  .Append(" scav=").Append(s.ScavengerCount).Append(" camp=").Append(s.CamperCount);
                foreach (Pawn p in s.Scavengers.Where(x => x != null))
                    sb.Append(" S[").Append(p.kindDef.defName).Append(" tier=").Append(TitanicTierUtility.AdultTier(p.def))
                      .Append(" homedHere=").Append(map.Biomes.Any(b => b.CommonalityOfAnimal(p.kindDef) > 0f))
                      .Append(" pred=").Append(p.RaceProps.predator).Append(" spawned=").Append(p.Spawned)
                      .Append(" atSite=").Append(CorpseSiteVisitors.AtSite(p, s)).Append(']');
                foreach (Pawn p in s.Campers.Where(x => x != null))
                {
                    Lord lord = p.GetLord();
                    sb.Append(" C[").Append(p.kindDef.defName).Append(" fac=").Append(p.Faction?.Name ?? "none")
                      .Append(" hostile=").Append(p.Faction != null && p.Faction.HostileTo(Faction.OfPlayer))
                      .Append(" lord=").Append(lord?.LordJob?.GetType().Name ?? "none")
                      .Append(" toil=").Append(lord?.CurLordToil?.GetType().Name ?? "none")
                      .Append(" spawned=").Append(p.Spawned).Append(']');
                }
            }
            return sb.ToString();
        }

        /// <summary>One forced daily step on every site of the current map (visitor meal, then the draw and camp rolls, then
        /// spoilage), then SiteReport.</summary>
        public static string SiteDailyStep()
        {
            Map map = Find.CurrentMap;
            if (map == null) return "FAIL no map";
            foreach (var s in map.listerThings.AllThings.OfType<Building_TitanicCorpseSite>().ToList()) s.DebugDailyStep();
            return SiteReport();
        }

        public static string PassageCanFire()
        {
            Map map = Find.CurrentMap;
            IncidentDef def = DefDatabase<IncidentDef>.GetNamedSilentFail("RM_TitanPassage");
            if (map == null || def == null) return "FAIL no map or RM_TitanPassage";
            bool can = def.Worker.CanFireNow(new IncidentParms { target = map });
            bool t3 = TitanPassageUtility.T3OnMap(map);
            var kinds = DefDatabase<PawnKindDef>.AllDefsListForReading.Where(k => TitanPassageUtility.Eligible(k, map, t3)).ToList();
            var ext = map.Biome?.GetModExtension<RM_TitanPassageExtension>();
            string hints = ext == null ? "roster" : ext.none ? "none" : "list" + (ext.passers?.Count ?? 0);
            return "canFire=" + can + " active=" + RM_HugeThingsSettings.TitanEventsActive + " t3OnMap=" + t3
                   + " biome=" + map.Biome?.defName + " seaMap=" + TitanPassageUtility.IsSeaMap(map) + " hints=" + hints
                   + " eligible=" + kinds.Count + " [" + string.Join(",", kinds.Select(k => k.defName + ":"
                   + TitanicTierUtility.AdultTier(k.race) + (TitanPassageUtility.IsSeaCreature(k) ? ":sea" : ":land"))) + "]";
        }

        public static string PassageReport()
        {
            Map map = Find.CurrentMap;
            var comp = map?.GetComponent<MapComponent_TitanPassages>();
            if (comp == null) return "FAIL no MapComponent_TitanPassages";
            var sb = new StringBuilder("pending=" + comp.HasPending + " kind=" + (comp.PendingKind?.defName ?? "none")
                                       + " arrivalIn=" + (comp.HasPending ? comp.ArrivalTick - Find.TickManager.TicksGame : -1));
            Pawn a = comp.LastArrived;
            if (a != null)
            {
                Lord lord = a.GetLord();
                sb.Append(" arrived=").Append(a.ThingID).Append(" kind=").Append(a.kindDef.defName)
                  .Append(" tier=").Append(TitanicTierUtility.AdultTier(a.def)).Append(" spawned=").Append(a.Spawned)
                  .Append(" homedHere=").Append(map.Biomes.Any(b => b.CommonalityOfAnimal(a.kindDef) > 0f))
                  .Append(" seaMatch=").Append(TitanPassageUtility.IsSeaCreature(a.kindDef) == TitanPassageUtility.IsSeaMap(map))
                  .Append(" lord=").Append(lord?.LordJob?.GetType().Name ?? "none")
                  .Append(" pos=").Append(a.Position.x).Append(',').Append(a.Position.z);
            }
            return sb.ToString();
        }

        public static string PassageArriveNow()
        {
            var comp = Find.CurrentMap?.GetComponent<MapComponent_TitanPassages>();
            if (comp == null) return "FAIL no MapComponent_TitanPassages";
            comp.DebugArriveNow();
            return PassageReport();
        }
            // ---- TITANIC_BODYSIZE_TEST_RACE_1: probes for the T2/T3 rows, driven with the harness-only test races
        // (src/RimMandrake/HugeThingsTestRaces: RM_TestTitanT2 bodySize 8, RM_TestTitanT3 20, RM_TestTitanT2Control 8 forced out).

        private static Pawn MakeAdult(PawnKindDef kind, Map map)
        {
            return PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer, map?.Tile ?? -1,
                allowDowned: true, fixedBiologicalAge: kind.RaceProps.lifeStageAges.Last().minAge + 1f));
        }

        /// <summary>Generates (never spawns) an adult of each comma-separated kind and reads the tier the running mod gives it.</summary>
        public static string TierReport(string kindDefNames)
        {
            var sb = new StringBuilder();
            foreach (string name in (kindDefNames ?? "").Split(','))
            {
                PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(name.Trim());
                if (sb.Length > 0) sb.Append(" | ");
                if (kind == null) { sb.Append(name.Trim()).Append(" FAIL no kind"); continue; }
                Pawn p = MakeAdult(kind, Find.CurrentMap);
                sb.Append(kind.defName).Append(" tier=").Append(TitanicTierUtility.GetTier(p)).Append(" adultTier=")
                  .Append(TitanicTierUtility.AdultTier(p.def)).Append(" bodySize=").Append(p.BodySize.ToString("0.0"))
                  .Append(" wakeComp=").Append(p.TryGetComp<CompTitanicWake>() != null);
                p.Destroy();
            }
            return sb.ToString();
        }

        /// <summary>Butchers `n` generated adults of `kindDefName` at efficiency 1 under a fixed Rand seed (so two kinds of equal
        /// mass round alike) through the real Pawn.ButcherProducts, so the yield-curve prefix runs. Returns summed meat/leather and
        /// the kernel factor the curve should apply (1 when the tier is not T1/T2 or the curve is off).</summary>
        public static string ButcherYieldReport(string kindDefName)
        {
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(kindDefName);
            if (kind == null) return "FAIL no kind " + kindDefName;
            const int n = 6;
            int meat = 0, leather = 0;
            float factor = 1f;
            TitanicTier tier = TitanicTier.None;
            for (int i = 0; i < n; i++)
            {
                Pawn p = MakeAdult(kind, Find.CurrentMap);
                tier = TitanicTierUtility.GetTier(p);
                if (RM_HugeThingsSettings.YieldCurveActive && (tier == TitanicTier.T1 || tier == TitanicTier.T2))
                    factor = YieldCurveUtility.SubLinearFactor(p, tier);
                Rand.PushState(424242 + i);
                try
                {
                    foreach (Thing t in p.ButcherProducts(null, 1f))
                    {
                        if (t.def == p.RaceProps.meatDef) meat += t.stackCount;
                        else if (t.def == p.RaceProps.leatherDef) leather += t.stackCount;
                    }
                }
                catch (System.Exception ex)
                {
                    return "FAIL ButcherProducts threw " + ex.GetType().Name + ": " + ex.Message;
                }
                finally
                {
                    Rand.PopState();
                }
                p.Destroy();
            }
            return kind.defName + " tier=" + tier + " n=" + n + " meat=" + meat + " leather=" + leather + " factor=" + factor.ToString("0.0000");
        }

        /// <summary>T2 wake on a thin roof and a wall: puts RoofConstructed and a wood wall on the cell east of `cell`, spawns an adult
        /// of `kindDefName` at `cell` and moves it east through the real Thing.Position setter (the wake's trigger), then reads the
        /// roof and the wall back. Cleans up the pawn, the wall and the roof.</summary>
        public static string RoofWallProbe(string kindDefName, IntVec3 cell)
        {
            Map map = Find.CurrentMap;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(kindDefName);
            if (map == null || kind == null) return "FAIL no map or kind " + kindDefName;
            IntVec3 east = cell + IntVec3.East;
            if (!cell.InBounds(map) || !east.InBounds(map) || !cell.Walkable(map)) return "FAIL cell not usable " + cell;
            map.roofGrid.SetRoof(east, RoofDefOf.RoofConstructed);
            Thing wall = GenSpawn.Spawn(ThingMaker.MakeThing(ThingDefOf.Wall, ThingDefOf.WoodLog), east, map);
            int hpBefore = wall.HitPoints;
            Pawn p = MakeAdult(kind, map);
            GenSpawn.Spawn(p, cell, map);
            string tier = TitanicTierUtility.GetTier(p).ToString();
            p.Position = east;
            RoofDef after = east.GetRoof(map);
            bool wallGone = wall.Destroyed;
            int hpAfter = wallGone ? 0 : wall.HitPoints;
            if (!p.Destroyed) p.Destroy();
            if (!wall.Destroyed) wall.Destroy();
            map.roofGrid.SetRoof(east, null);
            return kind.defName + " tier=" + tier + " roofAfter=" + (after?.defName ?? "none") + " wallHpBefore=" + hpBefore
                   + " wallHpAfter=" + hpAfter + " wallDestroyed=" + wallGone;
        }

        // Pawn_PathFollower.CostToMoveIntoCell(Pawn, IntVec3) is private static: the exact overload Patch_ThickRoofAvoidance targets.
        private static readonly System.Reflection.MethodInfo CostMethod = HarmonyLib.AccessTools.Method(typeof(Verse.AI.Pawn_PathFollower),
            "CostToMoveIntoCell", new[] { typeof(Pawn), typeof(IntVec3) });

        private static float StepCost(Pawn p, IntVec3 c)
        {
            return System.Convert.ToSingle(CostMethod.Invoke(null, new object[] { p, c }));
        }

        /// <summary>Thick-roof slow-down: the step cost (Verse.AI.Pawn_PathFollower.CostToMoveIntoCell, which Patch_ThickRoofAvoidance
        /// postfixes) into the cell east of `cell`, open and then under RoofRockThick, for a spawned adult of `kindDefName`. The
        /// cell's original roof is put back.</summary>
        public static string ThickRoofCostProbe(string kindDefName, IntVec3 cell)
        {
            Map map = Find.CurrentMap;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(kindDefName);
            if (map == null || kind == null) return "FAIL no map or kind " + kindDefName;
            if (CostMethod == null) return "FAIL Pawn_PathFollower.CostToMoveIntoCell(Pawn, IntVec3) not found";
            IntVec3 east = cell + IntVec3.East;
            if (!cell.InBounds(map) || !east.InBounds(map) || !east.Walkable(map)) return "FAIL cell not usable " + cell;
            RoofDef orig = east.GetRoof(map);
            Pawn p = MakeAdult(kind, map);
            GenSpawn.Spawn(p, cell, map);
            string tier = TitanicTierUtility.GetTier(p).ToString();
            map.roofGrid.SetRoof(east, null);
            float open = StepCost(p, east);
            map.roofGrid.SetRoof(east, RoofDefOf.RoofRockThick);
            float thick = StepCost(p, east);
            map.roofGrid.SetRoof(east, orig);
            p.Destroy();
            return kind.defName + " tier=" + tier + " costOpen=" + open.ToString("0.0") + " costThick=" + thick.ToString("0.0");
        }
    }
}
