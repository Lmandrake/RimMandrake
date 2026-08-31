using Verse;

namespace MinePocket;

public class Verb_ShootMine : Verb_LaunchProjectileStatic
{
    public override bool ValidateTarget(LocalTargetInfo target, bool showMessages = true)
    {
        if (!base.ValidateTarget(target, showMessages))
        {
            return false;
        }
        if (target.Cell.GetFirstBuilding(Find.CurrentMap) == null)
        {
            return target.Cell.Standable(Find.CurrentMap);
        }
        return false;
    }
}
