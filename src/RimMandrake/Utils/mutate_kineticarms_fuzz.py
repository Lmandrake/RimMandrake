#!/usr/bin/env python3
"""Mutation proof for the KineticArms fuzz: plants each defect in the kernel (RM_KineticMath.cs), demands the fuzz FAILS, restores the
file byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_kineticarms_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/KineticArms/Source/RM_KineticMath.cs"
MUTATIONS = [
    ("dir zero threshold huge", "if (len < 1e-4f)", "if (len < 2f)"),
    ("dir not normalised", "dx = vx / len;\n            dz = vz / len;", "dx = vx;\n            dz = vz;"),
    ("dir swaps axes", "dx = vx / len;\n            dz = vz / len;", "dx = vz / len;\n            dz = vx / len;"),
    ("dir reversed", "dx = vx / len;\n            dz = vz / len;", "dx = -vx / len;\n            dz = -vz / len;"),
    ("backstep steps forward", "bx = ix - sx;\n            bz = iz - sz;", "bx = ix + sx;\n            bz = iz + sz;"),
    ("backstep ignores z", "bz = iz - sz;", "bz = iz;"),
    ("backstep rounds to even", "(int)Math.Round(dx, MidpointRounding.AwayFromZero)", "(int)Math.Round(dx)"),
    ("backstep truncates", "int sx = (int)Math.Round(dx, MidpointRounding.AwayFromZero);", "int sx = (int)dx;"),
    ("cone accepts the centre", "if (vx == 0 && vz == 0)\n            {\n                return false;\n            }", "if (vx == 0 && vz == 0)\n            {\n                return true;\n            }"),
    ("cone 360 refuses", "if (coneDegrees >= 360f)\n            {\n                return true;\n            }", "if (coneDegrees >= 360f)\n            {\n                return false;\n            }"),
    ("cone threshold 450", "if (coneDegrees >= 360f)", "if (coneDegrees >= 450f)"),
    ("cone uses the full angle", "float half = coneDegrees * 0.5f * (float)Math.PI / 180f;", "float half = coneDegrees * (float)Math.PI / 180f;"),
    ("cone inverted", "return cos >= (float)Math.Cos(half) - 1e-4f;", "return cos <= (float)Math.Cos(half) - 1e-4f;"),
    ("cone strict", "return cos >= (float)Math.Cos(half) - 1e-4f;", "return cos > (float)Math.Cos(half) + 1e-4f;"),
    ("cone dot ignores z", "float cos = (vx * dx + vz * dz) / len;", "float cos = (vx * dx) / len;"),
    ("cone dot not normalised", "float cos = (vx * dx + vz * dz) / len;", "float cos = (vx * dx + vz * dz);"),
    ("cone cells radius exclusive", "if (ox * ox + oz * oz > r2)", "if (ox * ox + oz * oz >= r2)"),
    ("cone cells radius square", "float r2 = radius * radius;", "float r2 = radius;"),
    ("cone cells scan too small", "int r = (int)Math.Ceiling(radius);", "int r = (int)Math.Ceiling(radius) - 1;"),
    ("cone cells drop the impact", "if (!cells.Contains((ix, iz)))\n            {\n                cells.Add((ix, iz));\n            }", ""),
    ("cone cells duplicate the impact", "if (!cells.Contains((ix, iz)))", "if (true)"),
    ("cone cells offset by the impact", "int x = cx + ox, z = cz + oz;", "int x = ix + ox, z = iz + oz;"),
    ("facing north is south", "case 0: dx = 0f; dz = 1f; break;", "case 0: dx = 0f; dz = -1f; break;"),
    ("facing east is west", "case 1: dx = 1f; dz = 0f; break;", "case 1: dx = -1f; dz = 0f; break;"),
    ("facing negatives do not wrap", "switch (((rot % 4) + 4) % 4)", "switch (rot % 4)"),
    ("recharge ignores power", "if (!powered || rechargeTicks <= 0)", "if (rechargeTicks <= 0)"),
    ("recharge uncapped", "return Math.Min(capacity, charge + (float)ticks / rechargeTicks);", "return charge + (float)ticks / rechargeTicks;"),
    ("recharge integer division", "charge + (float)ticks / rechargeTicks", "charge + ticks / rechargeTicks"),
    ("recharge double speed", "charge + (float)ticks / rechargeTicks", "charge + 2f * ticks / rechargeTicks"),
    ("unpowered keeps over-capacity", "return Math.Min(charge, capacity);\n            }", "return charge;\n            }"),
    ("recharge divides by zero", "if (!powered || rechargeTicks <= 0)", "if (!powered)"),
    ("canfire needs 2", "public static bool CanFire(float charge) => charge >= 1f - 1e-4f;", "public static bool CanFire(float charge) => charge >= 2f;"),
    ("canfire strict", "charge >= 1f - 1e-4f", "charge > 1f"),
    ("spend takes two", "Math.Max(0f, charge - 1f)", "Math.Max(0f, charge - 2f)"),
    ("spend goes negative", "Math.Max(0f, charge - 1f)", "charge - 1f"),
    ("force can go negative", "Math.Max(0f, baseForce * strength)", "baseForce * strength"),
    ("force ignores strength", "Math.Max(0f, baseForce * strength)", "Math.Max(0f, baseForce)"),
    ("loot ceiling gone", "return m > RaiderPriceCeiling ? RaiderPriceCeiling : m;", "return m;"),
    ("loot ceiling raised", "public const float RaiderPriceCeiling = 1000f;", "public const float RaiderPriceCeiling = 3000f;"),
    ("loot floor ignored", "float m = kindMoneyMax > factionFloor ? kindMoneyMax : factionFloor;", "float m = kindMoneyMax;"),
    ("loot money takes the lower", "float m = kindMoneyMax > factionFloor ? kindMoneyMax : factionFloor;", "float m = kindMoneyMax < factionFloor ? kindMoneyMax : factionFloor;"),
    ("ruins weights: grav-ram common", "{ 30f, 20f, 15f, 10f, 12f, 15f, 5f, 3f }", "{ 30f, 20f, 15f, 10f, 12f, 15f, 5f, 30f }"),
    ("ruins weights: thudder rarer", "{ 30f, 20f, 15f, 10f, 12f, 15f, 5f, 3f }", "{ 3f, 20f, 15f, 10f, 12f, 15f, 5f, 3f }"),
    ("ruins gate inclusive", "if (enabled == null || chance <= 0f || roll1 >= chance)", "if (enabled == null || chance <= 0f || roll1 > chance)"),
    ("ruins picks disabled", "if (enabled[i])\n                {\n                    fit.Add(i);\n                    total += Weight(weights, i);\n                }", "{\n                    fit.Add(i);\n                    total += Weight(weights, i);\n                }"),
    ("ruins uniform fallback gone", "if (total <= 0f)\n            {\n                int k", "if (false)\n            {\n                int k"),
    ("ruins weighted inclusive", "if (target < acc)\n                {\n                    return i;", "if (target <= acc)\n                {\n                    return i;"),
    ("ruins weights ignored", "acc += Weight(weights, i);\n                if (target < acc)", "acc += 1f;\n                if (target < acc)"),
    ("ruins negative weight counts", "return w > 0f ? w : 0f;", "return w;"),
    ("ruins missing weight is 1", "float w = i < weights.Count ? weights[i] : 0f;", "float w = i < weights.Count ? weights[i] : 1f;"),
    ("rollfor ignores disabled before", "if (!enabled[i])\n                {\n                    continue;\n                }\n                if (i == index)", "if (i == index)"),
    ("rollfor lands on the band edge", "return (before + Weight(weights, index) * 0.5f) / total;", "return before / total;"),
    ("rollfor offers a zero-weight roll", "if (Weight(weights, index) <= 0f)\n            {\n                return -1f;\n            }", ""),
    ("rollfor uniform off by one", "return (myRank + 0.5f) / fitCount;", "return (myRank + 1.5f) / fitCount;"),
    ("stack uncapped", "return n > 12 ? 12 : (n < 5 ? 5 : n);", "return n;"),
    ("stack floor 4", "int n = 5 + (int)(roll * 8f);", "int n = 4 + (int)(roll * 8f);"),
    ("stack single weapons stack", "if (!stackable)\n            {\n                return 1;\n            }", ""),
    ("looted gate inclusive", "if (chance <= 0f || roll1 >= chance || options == null)", "if (chance <= 0f || roll1 > chance || options == null)"),
    ("looted ignores the grenade split", "o.enabled && o.grenade == grenadier && o.price <= moneyMax", "o.enabled && o.price <= moneyMax"),
    ("looted ignores the money", "o.enabled && o.grenade == grenadier && o.price <= moneyMax", "o.enabled && o.grenade == grenadier"),
    ("looted money exclusive", "o.price <= moneyMax", "o.price < moneyMax"),
    ("looted ignores the toggle", "o.enabled && o.grenade == grenadier", "o.grenade == grenadier"),
    ("looted pick always first", "int k = (int)(roll2 * fit.Count);\n            return fit[k < 0 ? 0 : (k >= fit.Count ? fit.Count - 1 : k)];\n        }\n    }", "int k = 0;\n            return fit[k < 0 ? 0 : (k >= fit.Count ? fit.Count - 1 : k)];\n        }\n    }"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_kineticarms_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
