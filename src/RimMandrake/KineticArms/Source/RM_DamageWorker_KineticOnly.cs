using Verse;

namespace RimMandrake.KineticArms
{
    /// <summary>The Repulse family's worker (design §3): it applies NOTHING to anything it reaches. The explosion still
    /// walks its cells and calls DamageWorker.ExplosionDamageThing, which is where Explosive Knockback hooks, so the
    /// throw (and its wall/pit impact) is the whole effect. Shields still see the incoming DamageInfo first.</summary>
    public class RM_DamageWorker_KineticOnly : DamageWorker
    {
        public override DamageResult Apply(DamageInfo dinfo, Thing victim)
        {
            return new DamageResult();
        }
    }
}
