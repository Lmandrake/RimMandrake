using Verse;

namespace RimMandrake.StarWars.JawaIonWeapons
{
    /// <summary>
    /// A DamageDef that carries the ion blaster's TARGET-CLASS GRADIENT as XML.
    ///
    /// The owner's LOCKED SPEC D1 (design/Jawa/mods/required_mods.md, 2026-08-08)
    /// requires three tiers, strongest first:
    ///
    ///     machines / mechanoids   near one-shot disable
    ///     droids &amp; vehicles       strong
    ///     flesh people            weakest - no stun at all, only the slow
    ///                             RSW_JawaIon_Stun buildup that ends in a live collapse
    ///
    /// The two numbers below are EMP-equivalent damage amounts, not ticks.
    /// StunHandler turns them into ticks at 30 per point and then subtracts the
    /// target's EMPResistance, so an armoured mech resists exactly as it does
    /// against a vanilla EMP grenade. 60 -> 1800 ticks (30 s) before resistance;
    /// vanilla's own EMP grenade lands 20 for 600. That gap IS the "strongest
    /// vs pure machines" half of D1.
    ///
    /// ⛔ Do not convert these to raw tick counts. Going through EMP's own amount
    /// is what buys stunResistStat, the EMP adaptation timer and the
    /// DisabledByEMP effecter for free; see DamageWorker_IonBuildup.
    /// </summary>
    public class IonDamageDef : DamageDef
    {
        /// <summary>EMP-equivalent amount applied to true mechanoids and drones.</summary>
        public float empAmountMachine = 60f;

        /// <summary>EMP-equivalent amount applied to non-flesh non-mechanoids: droids, vehicles.</summary>
        public float empAmountDroid = 24f;
    }
}
