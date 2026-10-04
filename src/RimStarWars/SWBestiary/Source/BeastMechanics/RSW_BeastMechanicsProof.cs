using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.SWBestiary
{
    // SWBESTIARY_COVERAGE_GAPS_1 follow-up (r28 left metal eating and hoarding proven only by a settings round-trip).
    // Live proof hooks for jawa/static_call, args "current": each spawns the real creature on the current map, puts
    // the real food (or scrap and nest) beside it, and asks the SHIPPED job giver what it would do, then asks again
    // with the setting off. Everything it spawns is destroyed before it returns. Read-only on settings: the toggle is
    // restored in a finally.
    public static class RSW_BeastMechanicsProof
    {
        private sealed class EatProbe : JobGiver_EatMetal
        {
            public Job Give(Pawn p) => TryGiveJob(p);
        }

        private sealed class HoardProbe : JobGiver_HoardScrap
        {
            public Job Give(Pawn p) => TryGiveJob(p);
        }

        private static ThingDef RaceWith<T>() where T : CompProperties =>
            DefDatabase<ThingDef>.AllDefsListForReading.FirstOrDefault(d => d.race != null && d.GetCompProperties<T>() != null);

        private static Pawn SpawnWild(ThingDef race, Map map, out IntVec3 cell, out string error)
        {
            cell = IntVec3.Invalid;
            error = null;
            PawnKindDef kind = DefDatabase<PawnKindDef>.AllDefsListForReading.FirstOrDefault(k => k.race == race);
            if (kind == null)
            {
                error = "no PawnKindDef for " + race.defName;
                return null;
            }
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 40, c => c.Standable(map) && !c.Roofed(map)
                    && !map.areaManager.Home[c] && c.GetFirstItem(map) == null && c.GetEdifice(map) == null
                    && GenAdj.CellsAdjacent8Way(new TargetInfo(c, map)).Count(a => a.InBounds(map) && a.Standable(map)
                        && !map.areaManager.Home[a] && a.GetFirstItem(map) == null && a.GetEdifice(map) == null) >= 6,
                    out cell))
            {
                error = "no open non-home cell";
                return null;
            }
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, fixedBiologicalAge: 5f,
                fixedChronologicalAge: 5f));
            GenSpawn.Spawn(p, cell, map);
            return p;
        }

        private static string JobText(Job j) =>
            j == null ? "none" : j.def.defName + " target=" + (j.targetA.Thing?.def.defName ?? "-")
                                 + " targetB=" + (j.targetB.Thing?.def.defName ?? "-");

        /// <summary>A hungry metal-eater beside a stack of its food: the giver must hand it RSW_EatMetal on that
        /// stack, and nothing with metalEatingEnabled off or when fed.</summary>
        public static string ProofMetalEat(Map map)
        {
            map = map ?? Find.CurrentMap;
            ThingDef race = RaceWith<CompProperties_MetalEater>();
            if (map == null || race == null)
            {
                return "ERROR no map or no race with CompProperties_MetalEater";
            }
            var props = race.GetCompProperties<CompProperties_MetalEater>();
            ThingDef food = props.customThingToEat?.Select(n => DefDatabase<ThingDef>.GetNamedSilentFail(n)).FirstOrDefault(d => d != null);
            if (food == null)
            {
                return "ERROR " + race.defName + " names no loaded food";
            }
            Pawn p = SpawnWild(race, map, out IntVec3 cell, out string err);
            if (p == null)
            {
                return "ERROR " + err;
            }
            Thing stack = null;
            bool was = RSW_BeastMechanicsSettings.metalEatingEnabled;
            try
            {
                IntVec3 beside = GenAdj.CellsAdjacent8Way(p).First(a => a.InBounds(map) && a.Standable(map) && a.GetFirstItem(map) == null);
                stack = GenSpawn.Spawn(ThingMaker.MakeThing(food), beside, map);
                stack.stackCount = System.Math.Min(food.stackLimit, 50);
                var probe = new EatProbe();
                RSW_BeastMechanicsSettings.metalEatingEnabled = true;
                p.needs.food.CurLevelPercentage = 0.05f;
                string hungry = JobText(probe.Give(p));
                p.needs.food.CurLevelPercentage = 1f;
                string fed = JobText(probe.Give(p));
                p.needs.food.CurLevelPercentage = 0.05f;
                RSW_BeastMechanicsSettings.metalEatingEnabled = false;
                string off = JobText(probe.Give(p));
                return "eater=" + race.defName + " food=" + food.defName + " hungry=" + hungry.Replace(' ', '|')
                       + " fed=" + fed.Replace(' ', '|') + " off=" + off.Replace(' ', '|');
            }
            finally
            {
                RSW_BeastMechanicsSettings.metalEatingEnabled = was;
                if (stack != null && !stack.Destroyed) stack.Destroy();
                if (!p.Destroyed) p.Destroy();
            }
        }

        /// <summary>A rested, fed scrap-hoarder with its nest nearby and a hoardable item a few cells off: the giver
        /// must hand it RSW_HoardScrap (scrap, nest), and nothing with scrapHoardingEnabled off.</summary>
        public static string ProofHoard(Map map)
        {
            map = map ?? Find.CurrentMap;
            ThingDef race = RaceWith<CompProperties_ScrapHoarder>();
            if (map == null || race == null)
            {
                return "ERROR no map or no race with CompProperties_ScrapHoarder";
            }
            var props = race.GetCompProperties<CompProperties_ScrapHoarder>();
            ThingDef nestDef = DefDatabase<ThingDef>.GetNamedSilentFail(props.nestDef);
            ThingDef scrapDef = props.hoardableDefs?.Select(n => DefDatabase<ThingDef>.GetNamedSilentFail(n)).FirstOrDefault(d => d != null);
            if (nestDef == null || scrapDef == null)
            {
                return "ERROR nest " + props.nestDef + " or hoardable not loaded";
            }
            Pawn p = SpawnWild(race, map, out IntVec3 cell, out string err);
            if (p == null)
            {
                return "ERROR " + err;
            }
            Thing nest = null, scrap = null;
            bool was = RSW_BeastMechanicsSettings.scrapHoardingEnabled;
            try
            {
                if (!CellFinder.TryFindRandomCellNear(cell, map, 6, c => c.Standable(map) && c.GetFirstItem(map) == null
                        && c.GetEdifice(map) == null && !map.areaManager.Home[c] && c.DistanceTo(cell) >= 3f
                        && GenSpawn.CanSpawnAt(nestDef, c, map), out IntVec3 nestCell))
                {
                    return "ERROR no nest cell";
                }
                nest = GenSpawn.Spawn(nestDef, nestCell, map, WipeMode.Vanish);
                if (!CellFinder.TryFindRandomCellNear(cell, map, 6, c => c.Standable(map) && c.GetFirstItem(map) == null
                        && c.GetEdifice(map) == null && !map.areaManager.Home[c] && c.DistanceTo(nestCell) > 3f, out IntVec3 scrapCell))
                {
                    return "ERROR no scrap cell";
                }
                scrap = GenSpawn.Spawn(ThingMaker.MakeThing(scrapDef), scrapCell, map);
                if (p.needs?.food != null) p.needs.food.CurLevelPercentage = 1f;
                if (p.needs?.rest != null) p.needs.rest.CurLevel = 1f;
                var probe = new HoardProbe();
                RSW_BeastMechanicsSettings.scrapHoardingEnabled = true;
                string on = JobText(probe.Give(p));
                RSW_BeastMechanicsSettings.scrapHoardingEnabled = false;
                string off = JobText(probe.Give(p));
                return "hoarder=" + race.defName + " nest=" + nestDef.defName + " scrap=" + scrapDef.defName
                       + " on=" + on.Replace(' ', '|') + " off=" + off.Replace(' ', '|');
            }
            finally
            {
                RSW_BeastMechanicsSettings.scrapHoardingEnabled = was;
                if (scrap != null && !scrap.Destroyed) scrap.Destroy();
                if (nest != null && !nest.Destroyed) nest.Destroy();
                if (!p.Destroyed) p.Destroy();
            }
        }
    }
}
