// Verse-free kernel of the seam between giant plants and titans, plus the Mod Settings gate tree. Both halves of Huge Things meet
// here: which titans smash giant plants (owner ruling 2026-10-07 ~21:20, decision taken by question card: the biggest titans smash
// through giant plants and damage them; smaller titans path around giant trunks as walls) and which feature is live under the
// two master toggles (owner, 2026-10-07: "Many configurations. Do you want giant plants? Giant animals? Detailed behaviors.").
// SelfTest/HugeTitanFuzz.cs compiles this file alone. Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib.
// Tiers are ints (None 0, T1 1, T2 2, T3 3), the same encoding RM_TitanicKernel uses.
using System;
using System.Collections.Generic;

namespace RimMandrake.HugeThings
{
    /// <summary>
    /// The settings tree as pure functions. A detailed behaviour is live only when its master is on AND its own toggle is on,
    /// so either master off is vanilla for that half (the all-off contract). RM_HugeThingsSettings' *Active properties call these.
    /// </summary>
    public static class HugeGates
    {
        public static bool Plant(bool giantPlants, bool feature) => giantPlants && feature;

        public static bool Animal(bool giantAnimals, bool feature) => giantAnimals && feature;

        /// <summary>A sub-behaviour of the wake (roof holing, giant-plant smashing) needs the wake itself on.</summary>
        public static bool Wake(bool giantAnimals, bool wake, bool feature) => giantAnimals && wake && feature;

        /// <summary>Smashing giant plants is the seam: it needs the wake (an animal behaviour) AND giant plants to be giants at
        /// all. With giant plants off a giant is an ordinary plant, and the wake's crush table treats it like one.</summary>
        public static bool Smash(bool giantPlants, bool giantAnimals, bool wake, bool smash) => giantPlants && giantAnimals && wake && smash;

        /// <summary>Is this thing a giant (or its trunk) for the wake: only while giant plants are on.</summary>
        public static bool IsGiantForWake(bool giantPlants, bool isGiantPlantOrTrunk) => giantPlants && isGiantPlantOrTrunk;
    }

    public static class GiantSmash
    {
        /// <summary>Default smash tier: only T3 titans smash giant plants; T1 and T2 path around their trunks.</summary>
        public const int DefaultMinTier = 3;

        /// <summary>Cells beyond the titan's own footprint it smashes into: its footprint plus the adjacent ring, because a
        /// trunk is impassable and so is never inside a footprint, only beside it.</summary>
        public const int Reach = 1;

        /// <summary>Does a titan of this tier smash giant plants at all.</summary>
        public static bool Smashes(int tier, int minTier, bool enabled)
        {
            return enabled && tier > 0 && minTier >= 1 && minTier <= 3 && tier >= minTier;
        }

        /// <summary>
        /// The wake's ordinary crush table must never touch a giant plant: a smasher hits it through Smash below (once per step,
        /// through the plant's own damage path), and a smaller titan leaves it standing (it walks under the cap, around the trunk).
        /// </summary>
        public static bool WakeMayCrush(bool isGiantPlantOrTrunk) => !isGiantPlantOrTrunk;

        /// <summary>
        /// The giant plants one step smashes: every owner with at least one solid cell (a trunk blocker, or the root of a giant
        /// whose own cell is solid) inside the titan's footprint [x0..x1] x [z0..z1] grown by Reach. Each owner once, ascending
        /// by id, so the damage order never depends on the map's thing order. Empty when the tier does not smash.
        /// </summary>
        public static List<int> Owners(int tier, int minTier, bool enabled, int x0, int z0, int x1, int z1,
                                       IList<SolidCell> solid)
        {
            List<int> owners = new List<int>();
            if (!Smashes(tier, minTier, enabled) || solid == null || x1 < x0 || z1 < z0) return owners;
            int ax = x0 - Reach, az = z0 - Reach, bx = x1 + Reach, bz = z1 + Reach;
            HashSet<int> seen = new HashSet<int>();
            for (int i = 0; i < solid.Count; i++)
            {
                SolidCell s = solid[i];
                if (s.X < ax || s.X > bx || s.Z < az || s.Z > bz) continue;
                if (seen.Add(s.Owner)) owners.Add(s.Owner);
            }
            owners.Sort();
            return owners;
        }

        /// <summary>Crush damage one smash deals to a giant plant: the wake's own heavy blow (the titan is at least T2 to get here
        /// by default), scaled by the player's crush multiplier.</summary>
        public static float Damage(float heavyBlow, float multiplier) => Math.Max(0f, heavyBlow * multiplier);
    }

    /// <summary>One solid cell of a giant plant: a trunk blocker cell, or a solid root.</summary>
    public struct SolidCell
    {
        public int X, Z, Owner;

        public SolidCell(int x, int z, int owner)
        {
            X = x;
            Z = z;
            Owner = owner;
        }
    }
}
