namespace RimMandrake.StarWars.SithLine
{
    /// <summary>
    /// SANGUOPHAGE_KEPT_UNREACHABLE_1 — the Sith line's decisions, with no Verse or UnityEngine type in it, so the offline
    /// selftest (Source/SelfTest, `python3 src/RimStarWars/SithLine/selftest_sithline.py`) compiles THIS file and drives
    /// the code the game runs. The Harmony patches measure the game and play what this returns. A `using Verse;` landing
    /// here breaks the selftest build.
    /// </summary>
    public static class RSW_SithLineKernel
    {
        public enum GroupKind { Combat, Settlement, Trader, Other }

        // design §4, all PROVISIONAL first guesses (owner 2026-10-03: first guesses ship, tuned live)
        public const float DefaultRaidChance = 0.04f;
        public const float DefaultRaidMinPoints = 1500f;
        public const float DefaultDefenderChance = 0.25f;

        /// <summary>
        /// Whether ONE inquisitor joins this Galactic Empire group. Owner card 2026-10-09: raids and base defenders
        /// only, never a trader or visitor group. <paramref name="roll"/> is a uniform draw in [0, 1).
        /// </summary>
        public static bool AddInquisitor(GroupKind kind, bool isEmpire, float points, float roll,
                                         bool raidsOn, float raidChance, float raidMinPoints,
                                         bool defendersOn, float defenderChance)
        {
            if (!isEmpire || float.IsNaN(roll))
            {
                return false;
            }
            switch (kind)
            {
                case GroupKind.Combat:
                    return raidsOn && !float.IsNaN(points) && points >= raidMinPoints && roll < ClampChance(raidChance);
                case GroupKind.Settlement:
                    return defendersOn && roll < ClampChance(defenderChance);
                default:
                    return false;
            }
        }

        /// <summary>A chance setting held to [0, 1]; NaN is 0 (never), so a corrupt setting fails closed.</summary>
        public static float ClampChance(float c)
        {
            if (float.IsNaN(c) || c <= 0f)
            {
                return 0f;
            }
            return c >= 1f ? 1f : c;
        }

        /// <summary>
        /// Never recruitable (owner typed 2026-10-09, card the same night): a move of a Sith adept into the player's
        /// faction is refused. Every other faction change (capture, release, a hostile faction) is left alone.
        /// </summary>
        public static bool RefuseJoin(bool guardOn, bool isSith, bool targetIsPlayer)
        {
            return guardOn && isSith && targetIsPlayer;
        }

        // design §3, PROVISIONAL
        public const float DefaultRumourWeight = 0.15f;
        public const float DefaultRefireDays = 120f;
        public const int DefaultSearchRadius = 12;
        public const int TicksPerHour = 2500;
        public const float WakeMinHours = 6f;
        public const float WakeMaxHours = 10f;

        /// <summary>The tick a lair Sith rises on its own: 6-10 in-game hours after the lair map is made.</summary>
        public static int WakeTick(int genTick, float roll01)
        {
            if (float.IsNaN(roll01) || roll01 < 0f) roll01 = 0f;
            if (roll01 > 1f) roll01 = 1f;
            return genTick + (int)((WakeMinHours + (WakeMaxHours - WakeMinHours) * roll01) * TicksPerHour);
        }

        /// <summary>The trance breaks on damage, on an intruder inside the sanctum, or at the wake tick.</summary>
        public static bool ShouldWake(bool deathresting, bool tookDamage, bool intruderInside, int now, int wakeTick)
        {
            return deathresting && (tookDamage || intruderInside || now >= wakeTick);
        }

        /// <summary>Silver on the loot shelf, scaled by site points and held to [200, 4000].</summary>
        public static int LootSilver(float points)
        {
            if (float.IsNaN(points) || points < 0f) points = 0f;
            float v = points * 0.6f;
            return (int)(v < 200f ? 200f : (v > 4000f ? 4000f : v));
        }

        /// <summary>The Recruitable getter's answer: a Sith adept is unwaveringly loyal while the guard is on.</summary>
        public static bool Recruitable(bool vanillaAnswer, bool guardOn, bool isSith)
        {
            return vanillaAnswer && !(guardOn && isSith);
        }
    }
}
