using RimMandrake.StarWars.Armoury;
using Verse;

namespace guy762_Ionization;

public class DamageWorker_OrganicStun : DamageWorker
{
    public override DamageResult Apply(DamageInfo dinfo, Thing victim)
    {
        DamageResult result = base.Apply(dinfo, victim);
        if (RSW_ArmourySettings.ionDamageEnabled && victim is Pawn pawn && pawn.RaceProps.IsFlesh)
        {
            result.stunned = true;
        }
        return result;
    }
}
