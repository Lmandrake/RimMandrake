#!/usr/bin/env python3
"""Mutation proof for the HugeThings fuzz: plants each defect in the production kernel, runs the fuzz wrapper, demands a FAIL,
restores the file byte-identical (engine: mutate_explosivegrowth_fuzz.run_mutations).

    python3 src/RimMandrake/Utils/mutate_hugethings_fuzz.py [name-substring]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

# Dropped as equivalent: GrowthScale clamps growth > 1 only to be clamped again by the final share (same value), and MaxRect's
# ExpandedBy(1) is slack over an already monotone cover (NorthRect edges are monotone in the width).
MUTATIONS = [
    ("rounding to nearest even", "return (int)Math.Floor(v + 0.5f); }", "return (int)Math.Round(v); }"),
    ("rounding down", "return (int)Math.Floor(v + 0.5f); }", "return (int)Math.Floor(v); }"),
    ("scaled may reach zero", "return Math.Max(1, RoundHalfUp(full * scale));", "return RoundHalfUp(full * scale);"),
    ("growth scale ignores the minimum", "float now = visualMin + (visualMax - visualMin) * g;", "float now = visualMax * g;"),
    ("north rect centred on the wrong column", "return new RM_KRect(rootX - (w - 1) / 2, rootZ, w, d);", "return new RM_KRect(rootX - w / 2, rootZ, w, d);"),
    ("north rect starts south of the root", "return new RM_KRect(rootX - (w - 1) / 2, rootZ, w, d);", "return new RM_KRect(rootX - (w - 1) / 2, rootZ - 1, w, d);"),
    ("young plants block", "if (growth < minGrowthToBlock) return RM_KRect.Empty;", ""),
    ("one-cell trunk allowed", "if (w * d < 2) return RM_KRect.Empty;\n            return NorthRect(rootX, rootZ, w, d);\n        }\n\n        /// <summary>The click area", "if (w * d < 1) return RM_KRect.Empty;\n            return NorthRect(rootX, rootZ, w, d);\n        }\n\n        /// <summary>The click area"),
    ("trunk depth ignores trunkDepth", "int w = Scaled(trunkWidth, s), d = Scaled(DepthOf(trunkWidth, trunkDepth), s);", "int w = Scaled(trunkWidth, s), d = Scaled(trunkWidth, s);"),
    ("click area ignores the stem", "int h = Math.Max(Scaled(DepthOf(trunkWidth, trunkDepth), s), Scaled(StemOf(trunkWidth, trunkDepth, stemHeight), s));", "int h = Scaled(DepthOf(trunkWidth, trunkDepth), s);"),
    ("click area shorter than the trunk", "int h = Math.Max(Scaled(DepthOf(trunkWidth, trunkDepth), s), Scaled(StemOf(trunkWidth, trunkDepth, stemHeight), s));", "int h = Math.Min(Scaled(DepthOf(trunkWidth, trunkDepth), s), Scaled(StemOf(trunkWidth, trunkDepth, stemHeight), s));"),
    ("settings scale unclamped", "public static float ClampScale(float m) { return m < 0f ? 0f : (m > MaxTrunkScale ? MaxTrunkScale : m); }", "public static float ClampScale(float m) { return m; }"),
    ("max rect uses scale 1", "int w = Scaled(trunkWidth, MaxTrunkScale);", "int w = Scaled(trunkWidth, 1f);"),
    ("hitbox side may be zero", "return Math.Max(1, RoundHalfUp(drawn * fraction * ClampScale(multiplier)));", "return RoundHalfUp(drawn * fraction * ClampScale(multiplier));"),
    ("hitbox drops the footprint", "return Union(CentredRect(drawCellX, drawCellZ, w, h), foot);", "return CentredRect(drawCellX, drawCellZ, w, h);"),
    ("single-cell footprint returns itself", "return foot.Area > 1 ? foot : RM_KRect.Empty;", "return foot;"),
    ("union uses min of the max edge", "int maxX = Math.Max(a.MaxX, b.MaxX), maxZ", "int maxX = Math.Min(a.MaxX, b.MaxX), maxZ"),
    ("plan keeps blockers outside the trunk", "if (want.IsEmpty || !want.Contains(PackedX(k), PackedZ(k))) plan.destroyIndexes.Add(i);", "if (want.IsEmpty) plan.destroyIndexes.Add(i);"),
    ("plan keeps blockers for an empty trunk", "if (want.IsEmpty || !want.Contains(PackedX(k), PackedZ(k))) plan.destroyIndexes.Add(i);", "if (!want.IsEmpty && !want.Contains(PackedX(k), PackedZ(k))) plan.destroyIndexes.Add(i);"),
    ("plan spawns on the plant", "if ((x == rootX && z == rootZ) || !inBounds(x, z) || have.Contains(Pack(x, z))) continue;", "if (!inBounds(x, z) || have.Contains(Pack(x, z))) continue;"),
    ("plan ignores the map edge", "if ((x == rootX && z == rootZ) || !inBounds(x, z) || have.Contains(Pack(x, z))) continue;", "if ((x == rootX && z == rootZ) || have.Contains(Pack(x, z))) continue;"),
    ("plan doubles existing blockers", "if ((x == rootX && z == rootZ) || !inBounds(x, z) || have.Contains(Pack(x, z))) continue;", "if ((x == rootX && z == rootZ) || !inBounds(x, z)) continue;"),
    ("plan ignores refused cells", "if (!cellTakesTrunk(x, z)) continue;", ""),
    ("plan skips the last row", "for (int z = want.minZ; z <= want.MaxZ; z++)", "for (int z = want.minZ; z < want.MaxZ; z++)"),
    ("eligibility allows pawns", "return walkable && !hasPawn && !hasBuilding", "return walkable && !hasBuilding"),
    ("eligibility allows unwalkable", "return walkable && !hasPawn", "return !hasPawn"),
    ("eligibility allows trees", "&& !hasIndestructible && !hasTreeOrHugePlant;", "&& !hasIndestructible;"),
    ("pack drops the sign of z", "return (int)(uint)(k & 0xFFFFFFFFL); }", "return (int)(k & 0x7FFFFFFFL); }"),
]

if __name__ == "__main__":
    sys.exit(run_mutations("src/RimMandrake/HugeThings/Source/Kernel/RM_FootprintKernel.cs",
                           "selftest_hugethings_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
