using RimWorld;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.EnvironmentalHazards
{
    // DONOR_CODE_BURST_REBUILD_1. Our own replacement for the donor's compiled
    // DeathActionWorker_SummonFlashstorm: on death, register vanilla's
    // GameCondition_Flashstorm centred on the corpse. PROVISIONAL numbers (the donor DLL is not
    // decompiled here): radius 8-14 cells, 2500-4500 ticks, first strike within ~1 s.
    public class DeathActionProperties_SummonFlashstorm : DeathActionProperties
    {
        public IntRange areaRadius = new IntRange(8, 14);
        public IntRange durationTicks = new IntRange(2500, 4500);
        public IntRange initialStrikeDelay = new IntRange(30, 90);

        public DeathActionProperties_SummonFlashstorm()
        {
            workerClass = typeof(DeathActionWorker_SummonFlashstorm);
        }
    }

    public class DeathActionWorker_SummonFlashstorm : DeathActionWorker
    {
        public DeathActionProperties_SummonFlashstorm Props => props as DeathActionProperties_SummonFlashstorm;

        public override RulePackDef DeathRules => RulePackDefOf.Transition_DiedExplosive;

        public override bool DangerousInMelee => true;

        public override void PawnDied(Corpse corpse, Lord prevLord)
        {
            if (!RM_EnvironmentalHazardsSettings.deathFlashstormEnabled || corpse == null || corpse.Map == null)
            {
                return;
            }
            Map map = corpse.Map;
            if (map.Size.x <= 16 || map.Size.z <= 16)
            {
                return;
            }
            DeathActionProperties_SummonFlashstorm p = Props ?? new DeathActionProperties_SummonFlashstorm();
            var cond = (GameCondition_Flashstorm)GameConditionMaker.MakeCondition(GameConditionDefOf.Flashstorm, p.durationTicks.RandomInRange);
            cond.centerLocation = new IntVec2(corpse.Position.x, corpse.Position.z);
            cond.areaRadiusOverride = p.areaRadius;
            cond.initialStrikeDelay = p.initialStrikeDelay;
            map.gameConditionManager.RegisterCondition(cond);
        }
    }
}
