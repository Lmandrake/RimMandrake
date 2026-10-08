#!/usr/bin/env python3
"""Mutation proof for the CreatureBehaviors fuzz: plants each defect in the pure production files the fuzz compiles (sand swim kernel, moving
shade math and layer, shade patch graph + dash math, wild-leave math), runs the fuzz wrapper, demands a FAIL, restores the file byte-identical
(engine: mutate_explosivegrowth_fuzz.run_mutations). Mutants of RM_SunHeatMath are left to selftest_sun_heat.py (the fuzz reaches it only
through the shade families).

    python3 src/RimMandrake/Utils/mutate_creaturebehaviors_fuzz.py [name-substring]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

B = "src/RimMandrake/CreatureBehaviors/Source/"
W = "selftest_creaturebehaviors_fuzz.py"

# Dropped as equivalent: CastBody's `depth <= 0` early-out (Clamp01 of a non-positive depth is 0 and every write is max(cell, 0)); ShadowBounds' extra slack cell past the exact tip is a safety margin CastInto never needs (its rounding stays inside the
# exact tip); a minPatchCells <= 0 is already satisfied by every non-empty group; a patch cell is at distance 0 so the field can never be
# improved across it; relaxing a stale Dial bucket entry offers only costs the better entry already beat.
SWIM = [
    ("swim: hard ground does not breach", "env.Surface(submerged); // reached hard ground: breaches out onto it", "env.Surface(false);"),
    ("swim: hard ground keeps swimming", "if (!onSwim)\n            {\n                env.Surface(submerged); // reached hard ground: breaches out onto it\n                return;\n            }", "if (!onSwim)\n            {\n                env.Surface(submerged);\n            }"),
    ("swim: droid immunity ignored", "if (submerged && hasTarget && isPawn && env.DroidImmunity && !hasWater)", "if (submerged && hasTarget && isPawn && !hasWater)"),
    ("swim: immunity drops watered pawns", "if (submerged && hasTarget && isPawn && env.DroidImmunity && !hasWater)", "if (submerged && hasTarget && isPawn && env.DroidImmunity)"),
    ("swim: immunity job not ended", "env.EndJob();\n                hasTarget = false;\n            }\n\n            if (submerged && hasTarget && env.StormBlindsStrike())", "hasTarget = false;\n            }\n\n            if (submerged && hasTarget && env.StormBlindsStrike())"),
    ("swim: storm roll even when surfaced", "if (submerged && hasTarget && env.StormBlindsStrike())", "if (hasTarget && env.StormBlindsStrike())"),
    ("swim: storm ignored", "if (submerged && hasTarget && env.StormBlindsStrike())", "if (false)"),
    ("swim: strike range squared wrongly", "if (distSq <= range * range)", "if (distSq <= range)"),
    ("swim: strike range exclusive", "if (distSq <= range * range)", "if (distSq < range * range)"),
    ("swim: melee does not surface", "if (env.MeleeThreat())\n            {\n                env.Surface(submerged); // in melee: never fights from under the sand\n                return;\n            }", ""),
    ("swim: dives at once after a breach", "if (env.Now < env.SurfacedUntil)\n            {\n                return; // just breached - stays up\n            }", ""),
    ("swim: stays up one tick too long", "if (env.Now < env.SurfacedUntil)", "if (env.Now <= env.SurfacedUntil)"),
    ("swim: never submerges", "env.Submerge();\n        }", "}"),
    ("swim: breach until wrong", "return now + surfacedTicks;", "return now;"),
]

SHADE = [
    ("shade bounds: no radius", "int r = Math.Max(0, radius);\n            minX = cx - r;", "int r = 0;\n            minX = cx - r;"),
    ("shade bounds: negative radius", "int r = Math.Max(0, radius);\n            minX = cx - r;", "int r = radius;\n            minX = cx - r;"),
    ("shade bounds: z slack", "int ez = (int)Math.Ceiling(Math.Abs(dirZ / norm) * length) + 1;", "int ez = (int)Math.Floor(Math.Abs(dirZ / norm) * length);"),
    ("shade bounds: wrong x side", "if (dirX > 0f) { maxX += ex; } else if (dirX < 0f) { minX -= ex; }", "if (dirX > 0f) { minX -= ex; } else if (dirX < 0f) { maxX += ex; }"),
    ("shade bounds: no z growth", "if (dirZ > 0f) { maxZ += ez; } else if (dirZ < 0f) { minZ -= ez; }", ""),
    ("shade bounds: ring dropped", "minX--; minZ--; maxX++; maxZ++;", ""),
    ("shade bounds: not clipped", "maxX = Math.Min(width - 1, maxX);", ""),
    ("shade bounds: off-map reported on", "return minX <= maxX && minZ <= maxZ;", "return true;"),
    ("shade cast: depth unclamped", "float d = RM_SunHeatMath.Clamp01(depth);", "float d = depth;"),
    ("shade cast: ring too small", "cx - r - 1, cz - r - 1, cx + r + 1, cz + r + 1, d);", "cx - r, cz - r, cx + r, cz + r, d);"),
    ("shade cast: no tail", "RM_SunHeatMath.CastInto(grid, width, height, x, z, dirX, dirZ, length, tipShade, d);", ""),
    ("shade clear: skips the last row", "for (int z = Math.Max(0, minZ); z <= Math.Min(height - 1, maxZ); z++)", "for (int z = Math.Max(0, minZ); z < Math.Min(height - 1, maxZ); z++)"),
    ("shade clear: skips the last column", "for (int x = Math.Max(0, minX); x <= Math.Min(width - 1, maxX); x++)", "for (int x = Math.Max(0, minX); x < Math.Min(width - 1, maxX); x++)"),
    ("layer: unregister keeps the shade", "RM_MovingShadeMath.ClearRect(grid, width, height, st.minX, st.minZ, st.maxX, st.maxZ);\n                }\n                casters.Remove(key);", "}\n                casters.Remove(key);"),
    ("layer: moved casters not noticed", "if (info.x != kv.Value.lastX || info.z != kv.Value.lastZ)", "if (false)"),
    ("layer: old shade not cleared", "RM_MovingShadeMath.ClearRect(grid, w, h, st.minX, st.minZ, st.maxX, st.maxZ);\n                    st.hasRect = false;", "st.hasRect = false;"),
    ("layer: off switch still casts", "if (!on)\n            {\n                return;\n            }", ""),
    ("layer: no force reset", "Array.Clear(grid, 0, n);", ""),
    ("layer: dead casters kept", "if (!src.TryGetCaster(kv.Key, out RM_MovingCasterInfo info) || !info.alive)", "if (!src.TryGetCaster(kv.Key, out RM_MovingCasterInfo info))"),
    ("layer: height-less casters cast", "if (!info.hasProps || info.height <= 0f)", "if (!info.hasProps)"),
]

PATCH = [
    ("patch: orthogonal neighbours only", "if (dx == 0 && dz == 0) continue;\n                            int vx = ux + dx, vz = uz + dz;\n                            if (vx < 0 || vz < 0 || vx >= width || vz >= height) continue;\n                            int v = vz * width + vx;\n                            if (seen[v]", "if (dx == 0 && dz == 0) continue;\n                            if (dx != 0 && dz != 0) continue;\n                            int vx = ux + dx, vz = uz + dz;\n                            if (vx < 0 || vz < 0 || vx >= width || vz >= height) continue;\n                            int v = vz * width + vx;\n                            if (seen[v]"),
    ("patch: flecks become patches", "if (members.Count < minPatchCells)", "if (members.Count < 1)"),
    ("patch: size rule off by one", "if (members.Count < minPatchCells)", "if (members.Count <= minPatchCells)"),
    ("patch: unwalkable shade labelled", "if (seen[start] || !shade[start] || !walkable[start])", "if (seen[start] || !shade[start])"),
    ("patch: cell counts wrong", "Patch p = new Patch { id = patches.Count, cellCount = members.Count };", "Patch p = new Patch { id = patches.Count, cellCount = members.Count + 1 };"),
    ("patch: patch cells not zero", "distToShade[i] = 0;\n                nearestShade[i] = i;", "nearestShade[i] = i;"),
    ("patch: rim needs a cardinal neighbour", "if (walkable[v] && patchOf[v] == NoPatch)\n                        {\n                            rim = true;", "if (walkable[v] && patchOf[v] == NoPatch && (dx == 0 || dz == 0))\n                        {\n                            rim = true;"),
    ("patch: rim ignores walkability", "if (walkable[v] && patchOf[v] == NoPatch)\n                        {\n                            rim = true;", "if (patchOf[v] == NoPatch)\n                        {\n                            rim = true;"),
    ("patch: diagonal costs a cardinal step", "public const int DiagonalCost = 14;", "public const int DiagonalCost = 10;"),
    ("patch: cardinal cost", "public const int CardinalCost = 10;", "public const int CardinalCost = 11;"),
    ("patch: cap exclusive", "if (nd > capCost || nd >= distToShade[v]) continue;", "if (nd >= capCost || nd >= distToShade[v]) continue;"),
    ("patch: cap ignored", "if (nd > capCost || nd >= distToShade[v]) continue;", "if (nd >= distToShade[v]) continue;"),
    ("patch: field crosses walls", "if (!walkable[v] || patchOf[v] != NoPatch) continue;\n                            int nd", "if (patchOf[v] != NoPatch) continue;\n                            int nd"),
    ("patch: nearest shade not propagated", "nearestShade[v] = nearestShade[u];", ""),
    ("patch: negative cap not floored", "g.Spread(walkable, Math.Max(0, capCost));", "g.Spread(walkable, capCost);"),
    ("patch: edge cost drops a leg", "int total = distToShade[u] + distToShade[v] + (dx != 0 && dz != 0 ? DiagonalCost : CardinalCost);", "int total = distToShade[u] + distToShade[v];"),
    ("patch: edge over the cap kept", "if (total > capCost) continue;", ""),
    ("patch: edge keeps the dearer hop", "if (!best.TryGetValue(key, out Edge e) || total < e.cost)", "if (!best.TryGetValue(key, out Edge e) || total > e.cost)"),
    ("patch: edge not mirrored", "patches[e.to].edges.Add(new Edge { to = pa, cost = e.cost, fromCell = e.toCell, toCell = e.fromCell });", "patches[e.to].edges.Add(new Edge { to = pa, cost = e.cost, fromCell = e.fromCell, toCell = e.toCell });"),
    ("patch: edge to the same patch", "if (pb == NoPatch || pb <= pa || distToShade[v] == Unreached || !walkable[v]) continue;", "if (pb == NoPatch || pb < pa || distToShade[v] == Unreached || !walkable[v]) continue;"),
    ("patch: edge count not halved", "return e / 2;", "return e;"),
    ("patch: PatchAt unguarded", "return index >= 0 && index < patchOf.Length ? patchOf[index] : NoPatch;", "return patchOf[index];"),
    ("patch: octile uses the long leg twice", "return lo * DiagonalCost + (hi - lo) * CardinalCost;", "return lo * DiagonalCost + hi * CardinalCost;"),
    ("patch: ring range zero allowed", "if (rangeCost <= 0 || origin < 0 || origin >= patchOf.Length)", "if (rangeCost < 0 || origin < 0 || origin >= patchOf.Length)"),
    ("patch: ring ignores the return trip", "if (outCost + back <= rangeCost)", "if (outCost <= rangeCost)"),
    ("patch: ring includes unreached", "if (back == Unreached) continue;", ""),
    ("patch: ring strict", "if (outCost + back <= rangeCost)", "if (outCost + back < rangeCost)"),
    ("patch: ring square too small", "int r = rangeCost / CardinalCost;", "int r = rangeCost / CardinalCost - 1;"),
    ("dash: severity floor", "return Math.Max(curvedOverage * 6.45E-05f, 0.000375f);", "return curvedOverage * 6.45E-05f;"),
    ("dash: severity slope", "curvedOverage * 6.45E-05f", "curvedOverage * 6.0E-05f"),
    ("dash: no budget tolerates", "if (budget <= 0f)\n            {\n                return 0;\n            }", ""),
    ("dash: safe sun has a limit", "if (feltInSunC <= safeMaxC)\n            {\n                return int.MaxValue;\n            }", ""),
    ("dash: tolerance interval", "double ticks = budget / per * HeatIntervalTicks;", "double ticks = budget / per;"),
    ("dash: tolerance not saturated", "return ticks >= int.MaxValue ? int.MaxValue : (int)ticks;", "return (int)ticks;"),
    ("dash: ticks per cell floor", "return t < 1f ? 1f : t;", "return t;"),
    ("dash: no strictness zero guard", "if (toleratedTicks <= 0 || strictnessRange <= 0f)", "if (toleratedTicks <= 0)"),
    ("dash: unlimited tolerance not max", "double cells = toleratedTicks == int.MaxValue ? maxCells : toleratedTicks / (double)ticksPerCell;", "double cells = toleratedTicks / (double)ticksPerCell;"),
    ("dash: max clamp", "if (cells > maxCells) cells = maxCells;", ""),
    ("dash: min clamp", "if (cells < minCells) cells = minCells;", ""),
    ("dash: strictness after the clamp", "cells *= strictnessRange;\n            if (cells > maxCells) cells = maxCells;\n            if (cells < minCells) cells = minCells;", "if (cells > maxCells) cells = maxCells;\n            if (cells < minCells) cells = minCells;\n            cells *= strictnessRange;"),
]

LEAVE = [
    ("leave: season warm edge", "if (seasonalTemp >= comfyMax) return RM_WildLeaveReason.TooWarm;", "if (seasonalTemp > comfyMax) return RM_WildLeaveReason.TooWarm;"),
    ("leave: season cold edge", "if (seasonalTemp <= comfyMin) return RM_WildLeaveReason.TooCold;", "if (seasonalTemp < comfyMin) return RM_WildLeaveReason.TooCold;"),
    ("leave: ambient warm edge", "if (ambientTemp > safeMax) return RM_WildLeaveReason.TooWarm;", "if (ambientTemp >= safeMax) return RM_WildLeaveReason.TooWarm;"),
    ("leave: ambient cold edge", "if (ambientTemp < safeMin) return RM_WildLeaveReason.TooCold;", "if (ambientTemp <= safeMin) return RM_WildLeaveReason.TooCold;"),
    ("leave: starving before temperature", "if (seasonalTemp >= comfyMax) return RM_WildLeaveReason.TooWarm;", "if (starving) return RM_WildLeaveReason.Starving;\n            if (seasonalTemp >= comfyMax) return RM_WildLeaveReason.TooWarm;"),
    ("leave: starving ignored", "if (starving) return RM_WildLeaveReason.Starving;", ""),
    ("leave: notice window edge", "return lastNotifiedTick < 0 || nowTick - lastNotifiedTick >= windowTicks;", "return lastNotifiedTick < 0 || nowTick - lastNotifiedTick > windowTicks;"),
    ("leave: first notice withheld", "return lastNotifiedTick < 0 || nowTick - lastNotifiedTick >= windowTicks;", "return nowTick - lastNotifiedTick >= windowTicks;"),
]

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rc = 0
    for f, muts in (("RM_SandSwimKernel.cs", SWIM), ("RM_MovingShadeMath.cs", [m for m in SHADE if m[0].startswith(("shade bounds", "shade cast", "shade clear"))]),
                    ("RM_MovingShadeLayer.cs", [m for m in SHADE if m[0].startswith("layer")]), ("RM_ShadePatchGraph.cs", PATCH), ("RM_WildLeaveMath.cs", LEAVE)):
        rc |= run_mutations(B + f, W, muts, only)
    sys.exit(rc)
