using RimWorld;
using Verse;

namespace RimMandrake.Abyss
{
    // ABYSS_DURRGAK_BUILD_1. A wild durrgak slowly sets obsidian-shard rings on the ground it walks.
    // Tamed (Faction != null) it never places one: tamed, it tidies via vanilla Haul training.
    public class CompProperties_Durrgak : CompProperties
    {
        public ThingDef cairnDef;
        public int radius = 7;
        public float chancePerRareTick = 0.08f;
        public int maxCairnsOnMap = 10;

        public CompProperties_Durrgak()
        {
            compClass = typeof(CompDurrgak);
        }
    }

    public class CompDurrgak : ThingComp
    {
        private CompProperties_Durrgak Props => (CompProperties_Durrgak)props;

        public override void CompTickRare()
        {
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed) return;
            if (!RM_AbyssSettings.durrgakRingsEnabled || Props.cairnDef == null) return;
            if (pawn.Faction != null || pawn.Map == null) return;
            if (!Rand.Chance(Props.chancePerRareTick)) return;
            Map map = pawn.Map;
            if (map.listerThings.ThingsOfDef(Props.cairnDef).Count >= Props.maxCairnsOnMap) return;

            for (int i = 0; i < 12; i++)
            {
                IntVec3 c = pawn.Position + GenRadial.RadialPattern[Rand.RangeInclusive(2, GenRadial.NumCellsInRadius(Props.radius) - 1)];
                if (!c.InBounds(map) || !c.Standable(map) || c.GetEdifice(map) != null) continue;
                if (c.GetThingList(map).Count > 0) continue;
                if (map.areaManager.Home[c]) continue;
                if (c.GetTerrain(map).passability != Traversability.Standable) continue;
                Thing cairn = ThingMaker.MakeThing(Props.cairnDef);
                GenSpawn.Spawn(cairn, c, map);
                return;
            }
        }
    }

    // The ring's own comp: a colonist who comes near and sees it gets a small, non-stacking memory.
    public class CompProperties_DurrgakCairn : CompProperties
    {
        public ThoughtDef memory;
        public int radius = 5;

        public CompProperties_DurrgakCairn()
        {
            compClass = typeof(CompDurrgakCairn);
        }
    }

    public class CompDurrgakCairn : ThingComp
    {
        private CompProperties_DurrgakCairn Props => (CompProperties_DurrgakCairn)props;

        public override void CompTickRare()
        {
            if (!parent.Spawned || Props.memory == null) return;
            Map map = parent.Map;
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned)
            {
                if (p.Dead || p.needs?.mood?.thoughts?.memories == null) continue;
                if (!p.Position.InHorDistOf(parent.Position, Props.radius)) continue;
                if (!GenSight.LineOfSight(p.Position, parent.Position, map)) continue;
                p.needs.mood.thoughts.memories.TryGainMemory(Props.memory);
            }
        }
    }
}
