using Verse;

namespace RimMandrake.StarWars.BrainWorms
{
    /// <summary>
    /// BRAINWORM_MOD_BUILD_1, vector 3 - weaponized eggs as war retribution (owner,
    /// 2026-09-11, verbatim: "As punishment if they go to war against the Jawa:
    /// bring a catapult and hurl eggs at their ship, then leave.").
    ///
    /// The spec left the delivery mechanism as this build's design question. Answer:
    /// a mortar shell. It needs no new world-map machinery and it IS the fantasy -
    /// the player caravans a mortar onto a hostile settlement's map, shells them with
    /// egg rounds, and leaves before the worms find anyone. Vanilla artillery does
    /// the rest: ThingDef.projectileWhenLoaded points a shell item at this
    /// projectile, and any mortar can fire it.
    ///
    /// The shell does almost no damage - the payload is the worms.
    /// </summary>
    public class Projectile_BrainWormEgg : Projectile
    {
        protected override void Impact(Thing hitThing, bool blockedByShield = false)
        {
            // base.Impact destroys this thing, which clears Map and Position: snapshot first.
            Map map = Map;
            IntVec3 cell = Position;

            base.Impact(hitThing, blockedByShield);

            if (blockedByShield || map == null)
            {
                return;
            }

            BrainWormUtility.SpawnWormBurst(map, cell, Rand.RangeInclusive(2, 4));
        }
    }
}
