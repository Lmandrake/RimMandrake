using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.BrainWorms
{
    /// <summary>
    /// BRAINWORM_MOD_BUILD_1 - the "hostile hive faction lens" the spec asks for.
    ///
    /// Vanilla has no faction-swap for a puppeted pawn and does not need one: the
    /// engine already asks the mental state itself who the pawn is hostile to
    /// (MentalState.ForceHostileTo, Verse/AI/MentalState.cs), which is how
    /// MentalState_Berserk turns one colonist against the room without touching
    /// Faction at all. This is that, minus the hive's own: worms and other infected
    /// hosts are not targets.
    ///
    /// 🔴 The host is ALIVE. This state is entered and maintained only by
    /// HediffComp_BrainWormPuppeteer, which refuses a dead pawn; nothing in this mod
    /// animates a corpse (owner's permanent ruling, 2026-09-11).
    /// </summary>
    public class MentalState_BrainWormPuppet : MentalState
    {
        public override bool ForceHostileTo(Thing t)
        {
            if (t is Pawn p && BrainWormUtility.IsHiveFlesh(p))
            {
                return false;
            }
            return true;
        }

        public override bool ForceHostileTo(Faction f)
        {
            return true;
        }

        public override RandomSocialMode SocialModeMax()
        {
            return RandomSocialMode.Off;
        }
    }
}
