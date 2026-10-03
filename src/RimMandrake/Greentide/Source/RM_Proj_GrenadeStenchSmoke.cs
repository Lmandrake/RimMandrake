using RimMandrake.CreatureBehaviors;
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
        private const int StenchSuppressionTicks = 5000;

        protected override void Explode()
        {
            if (!RM_GreentideSettings.stenchGrenadeEnabled)
            {
                Destroy();
                return;
            }

            def.projectile.explosionRadius =
                RM_GreentideSettings.StenchGrenadeBaseRadius * RM_GreentideSettings.stenchGrenadeRadiusMultiplier;

            // REACTION_MECHANISM_GENERALISE_1 step 5: the grenade is one CALLER
            // of the general reaction suppression (owner: the stench repels
            // every animal in the biome, wasps included). Inside the cloud no
            // gall boils, no swarm spreads, and swarming pawns give up. Read
            // Map/Position before base.Explode() destroys this projectile.
            // Duration INVENTED: 2 in-game hours, scaled by CreatureBehaviors'
            // own suppression-duration dial.
            if (Map != null)
            {
                RM_ReactionSuppression.Suppress(Map, Position, def.projectile.explosionRadius, StenchSuppressionTicks);
            }

            base.Explode();
        }
    }
}
