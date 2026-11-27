using System;

namespace RimMandrake.Pyrelands
{
    // Verse-free rule of Pyrelands grass withering under a roof (CompWithersUnderRoof.cs) and of its dead grass crumbling
    // (RM_DeadGrass in the same file). Bar roofed_grass_declines_visibly, owner 2026-11-26: "the grass just suddenly all dies at
    // the same time ... it doesn't turn into dead grass, just... barren nothing". 0.1.0 took the same damage from every plant on
    // every long tick, so a patch roofed together died on one long tick. Here each plant has its own death time, read from its
    // id and cell, spread over a window around witherTicks; it loses hit points evenly up to that time, and its look steps
    // through wilting, then withered. The offline test T_ROOF_WITHER_OFFLINE (selftest_pyrelands_roof_wither.py) drives these
    // same functions through SelfTest/RoofWither.

    public static class RM_RoofWitherKernel
    {
        /// <summary>Ticks between two long ticks of a plant: GenTicks.TickLongInterval (vanilla 1.6, read in the decompile).</summary>
        public const int LongTickTicks = 2000;

        /// <summary>A plant's death time is witherTicks x (SpreadLo + (SpreadHi - SpreadLo) x u), u in [0,1) from its id and
        /// cell. Our own rule, read from the bar ("not all at the same time"): 0.6..1.4 of witherTicks spreads the deaths of a
        /// patch roofed at once over 0.8 x witherTicks (0.8 day at the shipped 60000), about 24 long ticks.</summary>
        public const double SpreadLo = 0.6;
        public const double SpreadHi = 1.4;

        /// <summary>The look turns from wilting to withered at this share of the plant's death time. Our own rule: half way.</summary>
        public const double WitheredFrom = 0.5;

        public const int StageFresh = 0;
        public const int StageWilting = 1;
        public const int StageWithered = 2;
        public const int StageDead = 3;

        /// <summary>A uniform value in [0,1) from a plant's id and cell (an integer hash: neighbours and consecutive ids
        /// decorrelate).</summary>
        public static double SpreadU(int id, int x, int z)
        {
            unchecked
            {
                uint h = (uint)id * 0x9E3779B1u;
                h ^= (uint)x * 0x85EBCA77u + 0x27D4EB2Fu;
                h = (h << 13) | (h >> 19);
                h ^= (uint)z * 0xC2B2AE3Du + 0x165667B1u;
                h ^= h >> 16;
                h *= 0x7FEB352Du;
                h ^= h >> 15;
                h *= 0x846CA68Bu;
                h ^= h >> 16;
                return h / 4294967296.0;
            }
        }

        /// <summary>Roofed ticks after which this plant is dead. Never below one long tick.</summary>
        public static int DeathTicks(int id, int x, int z, int witherTicks)
        {
            if (witherTicks < LongTickTicks)
            {
                witherTicks = LongTickTicks;
            }
            double u = SpreadU(id, x, z);
            int d = (int)Math.Round(witherTicks * (SpreadLo + (SpreadHi - SpreadLo) * u));
            return Math.Max(LongTickTicks, d);
        }

        /// <summary>The hit points the roof has taken from a plant after roofedTicks: rises evenly to maxHp at deathTicks, and
        /// stays below maxHp before it. Rounded up, so the first roofed long tick always takes at least 1 (a plant left at 1 HP
        /// dies on its next roofed long tick).</summary>
        public static int DamageDue(int maxHp, int roofedTicks, int deathTicks)
        {
            if (roofedTicks <= 0 || maxHp <= 0)
            {
                return 0;
            }
            if (roofedTicks >= deathTicks)
            {
                return maxHp;
            }
            long due = ((long)maxHp * roofedTicks + deathTicks - 1) / deathTicks;
            return (int)Math.Min(maxHp - 1, Math.Max(1, due));
        }

        /// <summary>The look of a living plant: fresh, wilting, withered. Fresh when the gate is off.</summary>
        public static int Stage(int roofedTicks, int deathTicks, bool gateOn)
        {
            if (!gateOn || roofedTicks <= 0)
            {
                return StageFresh;
            }
            if (roofedTicks >= deathTicks)
            {
                return StageDead;
            }
            return roofedTicks < WitheredFrom * deathTicks ? StageWilting : StageWithered;
        }

        public struct Step
        {
            /// <summary>Hit points to take now, below the plant's hit points unless Lethal.</summary>
            public int Damage;
            /// <summary>The plant dies now. The caller kills it outside its own tick and leaves its remains.</summary>
            public bool Lethal;
            /// <summary>The look after this step.</summary>
            public int Stage;
        }

        /// <summary>One long tick of one plant. roofedTicks and damageDealt are the plant's saved state. Gate off: nothing
        /// changes. Unroofed: no damage, and roofedTicks falls back one long tick (the look recovers; hit points do not).
        /// Roofed: roofedTicks rises one long tick and the plant takes what the roof owes it since the last step.</summary>
        public static Step Advance(ref int roofedTicks, ref int damageDealt, int id, int x, int z, int maxHp, int hitPoints,
            int witherTicks, bool gateOn, bool roofed)
        {
            int d = DeathTicks(id, x, z, witherTicks);
            Step s = new Step();
            if (!gateOn)
            {
                s.Stage = StageFresh;
                return s;
            }
            if (!roofed)
            {
                roofedTicks = Math.Max(0, roofedTicks - LongTickTicks);
                s.Stage = Stage(roofedTicks, d, true);
                return s;
            }
            roofedTicks += LongTickTicks;
            int due = DamageDue(maxHp, roofedTicks, d);
            int owed = Math.Max(0, due - damageDealt);
            damageDealt = Math.Max(damageDealt, due);
            if (due >= maxHp || (owed > 0 && owed >= hitPoints))
            {
                s.Lethal = true;
                s.Damage = Math.Max(0, hitPoints);
                s.Stage = StageDead;
                return s;
            }
            s.Damage = owed;
            s.Stage = Stage(roofedTicks, d, true);
            return s;
        }

        /// <summary>Dead grass crumbles on its own clock, spread the same way (a patch's dead grass does not vanish on one long
        /// tick either). ageTicks is the remains' saved age. Returns the hit points to take now; Lethal when it is gone.</summary>
        public static Step Crumble(ref int ageTicks, ref int damageDealt, int id, int x, int z, int maxHp, int hitPoints,
            int crumbleTicks)
        {
            ageTicks += LongTickTicks;
            int d = DeathTicks(id, x, z, crumbleTicks);
            int due = DamageDue(maxHp, ageTicks, d);
            int owed = Math.Max(0, due - damageDealt);
            damageDealt = Math.Max(damageDealt, due);
            Step s = new Step();
            if (due >= maxHp || (owed > 0 && owed >= hitPoints))
            {
                s.Lethal = true;
                s.Damage = Math.Max(0, hitPoints);
                s.Stage = StageDead;
                return s;
            }
            s.Damage = owed;
            return s;
        }

        /// <summary>Remaining ticks before dead grass is gone, for its inspect line.</summary>
        public static int CrumbleTicksLeft(int ageTicks, int id, int x, int z, int crumbleTicks)
        {
            return Math.Max(0, DeathTicks(id, x, z, crumbleTicks) - ageTicks);
        }
    }
}
