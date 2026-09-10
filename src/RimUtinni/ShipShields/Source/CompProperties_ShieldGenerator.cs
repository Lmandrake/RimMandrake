using RimWorld;
using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    // Subclasses vanilla's CompProperties_ProjectileInterceptor -- the same
    // XML shape Odyssey's own gravship shield generator uses
    // (RimWorld/CompGravshipShieldGenerator.cs) -- rather than any mod's
    // shield engine (SHIELD_MODS_LEVERAGE_1's source-verification found
    // VEF's CompShieldField is pawn-apparel only, not building-scale).
    public class CompProperties_ShieldGenerator : CompProperties_ProjectileInterceptor
    {
        // shd:shield-collapse-evacuate: "Slow pressing things move through
        // all shields is long-standing canon, including the crew." Any
        // projectile slower than this (tiles/tick) is let through untouched
        // instead of intercepted. See HarmonyPatches.cs -- CheckIntercept is
        // not virtual, so this needs a prefix, not an override.
        public float slowPassThroughSpeed = 0.3f;

        // shd:bubble-not-wall: "prone to overheating or even explosion when
        // forcibly collapsed." Fired once from CompShieldGenerator.CompTick
        // when currentHitPoints reaches 0 from damage.
        public float collapseExplosionRadius = 4.5f;
        public DamageDef collapseExplosionDamage;
        public int collapseExplosionDamageAmount = 80;
        public float collapseExplosionChanceToStartFire;

        public CompProperties_ShieldGenerator()
        {
            compClass = typeof(CompShieldGenerator);
        }
    }
}
