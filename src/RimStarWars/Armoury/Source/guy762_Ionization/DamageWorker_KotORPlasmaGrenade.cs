using System.Collections.Generic;
using RimWorld;
using Verse;

namespace guy762_Ionization;

public class DamageWorker_KotORPlasmaGrenade : DamageWorker_Flame
{
    public override void ExplosionAffectCell(Explosion explosion, IntVec3 c, List<Thing> damagedThings, List<Thing> ignoredThings, bool canThrowMotes)
    {
        base.ExplosionAffectCell(explosion, c, damagedThings, ignoredThings, canThrowMotes);
        if (def == DamageDefOf_guy762.guy762_GrenadeDamage_plasma && Rand.Chance(FireUtility.ChanceToStartFireIn(c, explosion.Map)))
        {
            FireUtility.TryStartFireIn(c, explosion.Map, Rand.Range(0.2f, 0.6f), explosion.instigator);
        }
    }
}
