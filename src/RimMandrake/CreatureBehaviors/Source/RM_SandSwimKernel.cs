namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// STILLSAND_SAND_SWIM_KIT_1, the decision half of RM_CompSandSwim.Evaluate, extracted so the offline fuzz
    /// (Source/SelfTestFuzz, Utils/selftest_creaturebehaviors_fuzz.py) compiles this exact file. System only.
    /// The comp supplies the live facts and effects through IRM_SwimEnv (a private struct, so no allocation);
    /// the order of every read and effect below is the order Evaluate always had, including that the storm
    /// roll and the melee-threat read happen only when reached.
    /// </summary>
    public interface IRM_SwimEnv
    {
        int Now { get; }
        int SurfacedUntil { get; }
        bool Submerged { get; }
        bool DroidImmunity { get; }
        float StrikeRange { get; }
        bool OnSwimTerrain();
        /// <summary>The current melee/hunt target. False when there is none. distSq is the horizontal squared
        /// distance from the swimmer.</summary>
        bool TryGetTarget(out bool isPawn, out bool hasWater, out int distSq);
        /// <summary>True when the weather's sense chance is below 1 and the roll failed (evaluated lazily).</summary>
        bool StormBlindsStrike();
        bool MeleeThreat();
        void EndJob();
        void Surface(bool breach);
        void Submerge();
    }

    public static class RM_SandSwimKernel
    {
        public static void Evaluate<TE>(ref TE env) where TE : struct, IRM_SwimEnv
        {
            bool onSwim = env.OnSwimTerrain();
            bool submerged = env.Submerged;

            if (!onSwim)
            {
                env.Surface(submerged); // reached hard ground: breaches out onto it
                return;
            }

            bool hasTarget = env.TryGetTarget(out bool isPawn, out bool hasWater, out int distSq);
            if (submerged && hasTarget && isPawn && env.DroidImmunity && !hasWater)
            {
                // nothing under the sand senses a pawn with no water in it: drop the attack rather than surface
                env.EndJob();
                hasTarget = false;
            }

            if (submerged && hasTarget && env.StormBlindsStrike())
            {
                env.EndJob();
                hasTarget = false;
            }

            if (hasTarget)
            {
                float range = env.StrikeRange;
                if (distSq <= range * range)
                {
                    env.Surface(submerged); // the strike
                    return;
                }
            }

            if (env.MeleeThreat())
            {
                env.Surface(submerged); // in melee: never fights from under the sand
                return;
            }

            if (env.Now < env.SurfacedUntil)
            {
                return; // just breached - stays up
            }

            env.Submerge();
        }

        /// <summary>The tick until which a swimmer that just breached stays surfaced.</summary>
        public static int BreachUntil(int now, int surfacedTicks)
        {
            return now + surfacedTicks;
        }
    }
}
