using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
    // KHORRAK_STEEL_DIET_TIER_1: the metal-eat live proof, moved with the mechanic from SWBestiary's RSW_BeastMechanicsProof.
    // Live proof hook for jawa/static_call, args "current": spawns the real creature on the current map, puts its real food
    // beside it, and asks the SHIPPED job giver what it would do (hungry, fed, and with the setting off). Everything it
    // spawns is destroyed before it returns, and the toggle is restored in a finally.
    public static class RM_MetalEaterProof
    {
        private sealed class EatProbe : RM_JobGiver_EatMetal
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

        /// <summary>A hungry metal-eater beside a stack of its food: the giver must hand it RM_EatMetal on that
        /// stack, and nothing with metalEatingEnabled off or when fed.</summary>
        public static string ProofMetalEat(Map map)
        {
            map = map ?? Find.CurrentMap;
            ThingDef race = RaceWith<RM_CompProperties_MetalEater>();
            if (map == null || race == null)
            {
                return "ERROR no map or no race with RM_CompProperties_MetalEater";
            }
            var props = race.GetCompProperties<RM_CompProperties_MetalEater>();
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
            bool was = RM_CreatureBehaviorsSettings.metalEatingEnabled;
            try
            {
                IntVec3 beside = GenAdj.CellsAdjacent8Way(p).First(a => a.InBounds(map) && a.Standable(map) && a.GetFirstItem(map) == null);
                stack = GenSpawn.Spawn(ThingMaker.MakeThing(food), beside, map);
                stack.stackCount = System.Math.Min(food.stackLimit, 50);
                var probe = new EatProbe();
                RM_CreatureBehaviorsSettings.metalEatingEnabled = true;
                p.needs.food.CurLevelPercentage = 0.05f;
                string hungry = JobText(probe.Give(p));
                p.needs.food.CurLevelPercentage = 1f;
                string fed = JobText(probe.Give(p));
                p.needs.food.CurLevelPercentage = 0.05f;
                RM_CreatureBehaviorsSettings.metalEatingEnabled = false;
                string off = JobText(probe.Give(p));
                return "eater=" + race.defName + " food=" + food.defName + " hungry=" + hungry.Replace(' ', '|')
                       + " fed=" + fed.Replace(' ', '|') + " off=" + off.Replace(' ', '|');
            }
            finally
            {
                RM_CreatureBehaviorsSettings.metalEatingEnabled = was;
                if (stack != null && !stack.Destroyed) stack.Destroy();
                if (!p.Destroyed) p.Destroy();
            }
        }
    }
}
