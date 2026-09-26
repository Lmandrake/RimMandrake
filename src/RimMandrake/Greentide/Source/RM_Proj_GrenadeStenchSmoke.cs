using Verse;

namespace RimMandrake.Greentide
{
    // GREENTIDE_GRENADE_WEAPONS_1. A thin override of vanilla
    // Projectile_Explosive (RimSage-verified: Explode() is `protected
    // virtual`, and base.Explode() reads def.projectile.explosionRadius
    // directly with no comp-level override hook — CompExplosive's
    // customExplosiveRadius field does NOT apply to a thrown grenade's own
    // impact, only to the item itself detonating on the ground from damage,
    // a separate code path). This class exists purely so Mod Settings can
    // gate and tune this one grenade without Harmony — this mod ships none
    // (RM_Greentide.csproj header: "every class here is a plain engine
    // extension point").
    //
    //   - stenchGrenadeEnabled=false: the grenade lands and does nothing —
    //     no damage, no gas, no explosion FX, a true dud. Nothing else in
    //     the mod reads this flag, so this is the entire "all-off degrades
    //     gracefully" story for this item.
    //   - stenchGrenadeRadiusMultiplier: mutates the SHARED
    //     ProjectilePropertiesDef instance in place, immediately before
    //     exploding. Safe because ticking is single-threaded and the value
    //     is (re)applied fresh on every throw — there is no load-order
    //     dependency on when Mod Settings finish initializing relative to
    //     def loading.
    public class RM_Proj_GrenadeStenchSmoke : Projectile_Explosive
    {
        protected override void Explode()
        {
            if (!RM_GreentideSettings.stenchGrenadeEnabled)
            {
                Destroy();
                return;
            }

            def.projectile.explosionRadius =
                RM_GreentideSettings.StenchGrenadeBaseRadius * RM_GreentideSettings.stenchGrenadeRadiusMultiplier;
            base.Explode();
        }
    }
}
