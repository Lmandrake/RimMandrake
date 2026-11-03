using System;
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

        /// <summary>Body size at and above which the trough is two cells wide on each flank.</summary>
        public const float WideTroughBodySize = 2.5f;

        /// <summary>
        /// The wake trough beside a submerged swimmer's path (STILLSAND_SAND_SWIM_REMAINDER_1 §1):
        /// cell offsets from the cell it just entered, lateral to the step (dx, dz) it took. The
        /// path cell itself is not included (the track grid's cell-entry postfix records it).
        /// Under 0.5 body size there is no trough; 0.5 up to WideTroughBodySize gives one cell on
        /// each flank; at and above it, two. A zero step gives none. Diagonal steps use the
        /// perpendicular diagonal, so the trough stays a straight band either side of the path.
        /// Returns the number of (x, z) pairs written into <paramref name="xs"/>/<paramref name="zs"/>.
        /// </summary>
        public static int WakeTroughOffsets(int dx, int dz, float bodySize, int[] xs, int[] zs)
        {
            int sx = Math.Sign(dx), sz = Math.Sign(dz);
            if ((sx == 0 && sz == 0) || bodySize < 0.5f) return 0;
            int reach = bodySize >= WideTroughBodySize ? 2 : 1;
            int lx = -sz, lz = sx;   // perpendicular to the step
            int n = 0;
            for (int k = 1; k <= reach && n + 1 < xs.Length && n + 1 < zs.Length; k++)
            {
                xs[n] = lx * k; zs[n] = lz * k; n++;
                xs[n] = -lx * k; zs[n] = -lz * k; n++;
            }
            return n;
        }
    }
}
