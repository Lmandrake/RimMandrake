using Verse;

namespace guy762_Ionization;

public class DamageWorker_OrganicStun : DamageWorker
{
    public override DamageResult Apply(DamageInfo dinfo, Thing victim)
    {
        DamageResult result = base.Apply(dinfo, victim);
        if (victim is Pawn pawn && pawn.RaceProps.IsFlesh)
        {
            result.stunned = true;
        }
        return result;
    }
}
