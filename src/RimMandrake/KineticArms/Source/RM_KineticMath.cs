using System;
using System.Collections.Generic;

namespace RimMandrake.KineticArms
{
    /// <summary>
    /// Verse-free geometry and charge rules for Kinetic Arms (design §10), compiled both into the mod and into the
    /// offline selftest (Source/SelfTest). The push-along-shot trick: a bolt explodes one cell BEHIND its impact, so
    /// Explosive Knockback's radial throw (away from the explosion centre) points along the shot; only cells inside a
    /// cone ahead of that centre are affected, and the impact cell is always kept.
    /// </summary>
    public static class RM_KineticMath
    {
        /// <summary>Unit direction from (ox,oz) to (tx,tz). False (and 0,0) for a zero-length vector.</summary>
        public static bool Dir(float ox, float oz, float tx, float tz, out float dx, out float dz)
        {
            float vx = tx - ox, vz = tz - oz;
            float len = (float)Math.Sqrt(vx * vx + vz * vz);
            if (len < 1e-4f)
            {
                dx = dz = 0f;
                return false;
            }
            dx = vx / len;
            dz = vz / len;
            return true;
        }

        /// <summary>The cell one step back from the impact cell against the unit direction (dx,dz). Rounds each axis,
        /// so a diagonal shot steps back diagonally and a shallow one steps back along its major axis. A zero direction
        /// returns the impact cell itself.</summary>
        public static void BackStep(int ix, int iz, float dx, float dz, out int bx, out int bz)
        {
            int sx = (int)Math.Round(dx, MidpointRounding.AwayFromZero);
            int sz = (int)Math.Round(dz, MidpointRounding.AwayFromZero);
            bx = ix - sx;
            bz = iz - sz;
        }

        /// <summary>Is cell (x,z) inside the cone of total angle <paramref name="coneDegrees"/> opening from (cx,cz)
        /// along unit (dx,dz)? Uses a dot product, so there is no angle wrap-around at ±180. The centre cell itself is
        /// never in the cone (it lies behind the target). coneDegrees ≥ 360 accepts every other cell.</summary>
        public static bool InCone(int cx, int cz, int x, int z, float dx, float dz, float coneDegrees)
        {
            int vx = x - cx, vz = z - cz;
            if (vx == 0 && vz == 0)
            {
                return false;
            }
            if (coneDegrees >= 360f)
            {
                return true;
            }
            float len = (float)Math.Sqrt(vx * vx + vz * vz);
            float cos = (vx * dx + vz * dz) / len;
            float half = coneDegrees * 0.5f * (float)Math.PI / 180f;
            return cos >= (float)Math.Cos(half) - 1e-4f;
        }

        /// <summary>Every cell within <paramref name="radius"/> of the centre that lies in the cone, plus the impact cell
        /// (always kept). Bounds, line of sight and walls are the caller's (Verse) business.</summary>
        public static List<(int x, int z)> ConeCells(int cx, int cz, int ix, int iz, float dx, float dz, float radius, float coneDegrees)
        {
            var cells = new List<(int x, int z)>();
            int r = (int)Math.Ceiling(radius);
            float r2 = radius * radius;
            for (int ox = -r; ox <= r; ox++)
            {
                for (int oz = -r; oz <= r; oz++)
                {
                    if (ox * ox + oz * oz > r2)
                    {
                        continue;
                    }
                    int x = cx + ox, z = cz + oz;
                    if (InCone(cx, cz, x, z, dx, dz, coneDegrees))
                    {
                        cells.Add((x, z));
                    }
                }
            }
            if (!cells.Contains((ix, iz)))
            {
                cells.Add((ix, iz));
            }
            return cells;
        }

        /// <summary>Unit facing for a Rot4 index (0 north, 1 east, 2 south, 3 west) in RimWorld's x/z grid.</summary>
        public static void Facing(int rot, out float dx, out float dz)
        {
            switch (((rot % 4) + 4) % 4)
            {
                case 0: dx = 0f; dz = 1f; break;
                case 1: dx = 1f; dz = 0f; break;
                case 2: dx = 0f; dz = -1f; break;
                default: dx = -1f; dz = 0f; break;
            }
        }

        /// <summary>Pulse cannon charge after <paramref name="ticks"/> powered ticks: one charge per
        /// <paramref name="rechargeTicks"/>, capped at <paramref name="capacity"/>. Unpowered = unchanged.</summary>
        public static float Recharge(float charge, int capacity, int rechargeTicks, int ticks, bool powered)
        {
            if (!powered || rechargeTicks <= 0)
            {
                return Math.Min(charge, capacity);
            }
            return Math.Min(capacity, charge + (float)ticks / rechargeTicks);
        }

        /// <summary>A shot spends exactly one whole charge; a cannon below one charge does not pick targets.</summary>
        public static bool CanFire(float charge) => charge >= 1f - 1e-4f;

        public static float Spend(float charge) => Math.Max(0f, charge - 1f);

        /// <summary>Scaled DamageDef force for the "Kinetic throw strength" setting.</summary>
        public static float ScaledForce(float baseForce, float strength) => Math.Max(0f, baseForce * strength);

        /// <summary>One looted kinetic weapon a raider might carry instead of the gun he generated with.</summary>
        public struct LootOption
        {
            public bool grenade;
            public float price;
            public bool enabled;
        }

        /// <summary>Raiders never carry the grav-ram, however rich their kind is (Blackstar specialists and leaders, Hutt leaders).</summary>
        public const float RaiderPriceCeiling = 1000f;

        /// <summary>The money a looter pawn "could afford" for a looted weapon: his kind's weapon money, lifted to the faction's
        /// floor (a poor faction's salvage still holds a cheap thumper), never above RaiderPriceCeiling.</summary>
        public static float LootMoney(float kindMoneyMax, float factionFloor)
        {
            float m = kindMoneyMax > factionFloor ? kindMoneyMax : factionFloor;
            return m > RaiderPriceCeiling ? RaiderPriceCeiling : m;
        }

        /// <summary>Ruins loot (owner, card 22:37: found in Ancient Danger ruins). Index of the kinetic weapon one ancient
        /// temple holds, or -1. roll1 &lt; chance gates it; roll2 picks uniformly among the enabled weapons.</summary>
        public static int PickRuins(IList<bool> enabled, float chance, float roll1, float roll2)
        {
            if (enabled == null || chance <= 0f || roll1 >= chance)
            {
                return -1;
            }
            var fit = new List<int>();
            for (int i = 0; i < enabled.Count; i++)
            {
                if (enabled[i])
                {
                    fit.Add(i);
                }
            }
            if (fit.Count == 0)
            {
                return -1;
            }
            int k = (int)(roll2 * fit.Count);
            return fit[k < 0 ? 0 : (k >= fit.Count ? fit.Count - 1 : k)];
        }

        /// <summary>How many of the picked thing a temple holds: thump shells come as a stack of 5-12 (PROVISIONAL),
        /// everything else singly.</summary>
        public static int RuinsStack(bool stackable, float roll)
        {
            if (!stackable)
            {
                return 1;
            }
            int n = 5 + (int)(roll * 8f);
            return n > 12 ? 12 : (n < 5 ? 5 : n);
        }

        /// <summary>Owner 2026-10-06 (typed): "Mostly ruins only, but rare on raids that stole it from said ruins
        /// (pirates/outlaws)". Index of the looted weapon a looter-faction raider carries, or -1 (keeps his own).
        /// roll1 &lt; chance gates it; a grenadier gets only grenades, anyone else only non-grenades he could afford
        /// (price &lt;= his kind's weapon money); roll2 picks uniformly among those. Rolls are in [0,1).</summary>
        public static int PickLooted(IList<LootOption> options, bool grenadier, float moneyMax, float chance, float roll1, float roll2)
        {
            if (chance <= 0f || roll1 >= chance || options == null)
            {
                return -1;
            }
            var fit = new List<int>();
            for (int i = 0; i < options.Count; i++)
            {
                LootOption o = options[i];
                if (o.enabled && o.grenade == grenadier && o.price <= moneyMax)
                {
                    fit.Add(i);
                }
            }
            if (fit.Count == 0)
            {
                return -1;
            }
            int k = (int)(roll2 * fit.Count);
            return fit[k < 0 ? 0 : (k >= fit.Count ? fit.Count - 1 : k)];
        }
    }
}
