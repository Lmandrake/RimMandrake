using Verse;

namespace MinePocket;

public class Projectile_SpawnMine : Projectile
{
    protected override void Impact(Thing hitThing, bool blockedByShield = false)
    {
        Map map = Map;
        base.Impact(hitThing, blockedByShield);
        IntVec3 spawnAt = Position;
        if (def.projectile.tryAdjacentFreeSpaces && Position.GetFirstBuilding(map) != null)
        {
            foreach (IntVec3 cell in GenAdjFast.AdjacentCells8Way(Position))
            {
                if (cell.GetFirstBuilding(map) == null && cell.Standable(map))
                {
                    spawnAt = cell;
                    break;
                }
            }
        }
        Thing mine = GenSpawn.Spawn(ThingMaker.MakeThing(def.projectile.spawnsThingDef), spawnAt, map);
        if (mine.def.CanHaveFaction)
        {
            mine.SetFaction(launcher.Faction);
        }
    }
}
