#!/usr/bin/env python3
"""Mutation proof for the ExplosiveKnockback fuzz: plants each defect in the production kernel, runs the fuzz wrapper, demands a FAIL,
restores the file byte-identical (engine: mutate_explosivegrowth_fuzz.run_mutations). The older K-01..K-16 checks are not run here.

    python3 src/RimMandrake/Utils/mutate_explosiveknockback_fuzz.py [name-substring]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

# Dropped as equivalent: the early-out `force <= 0 || globalMultiplier <= 0` is redundant with the rounding below it (a zero or negative
# product rounds to < 1 and returns 0), so removing either half of it cannot change a result.
MUTATIONS = [
    ("falloff not clamped above", "return 1f - Clamp01(dist / radius);", "return 1f - dist / radius;"),
    ("falloff ignores radius 0", "if (radius <= 0f)\n            {\n                return 0f;\n            }\n            return 1f - Clamp01", "return 1f - Clamp01"),
    ("mass scale floor", "float v = (float)Math.Sqrt(s.refMass / m);\n            return v < 0.25f ? 0.25f : (v > 2f ? 2f : v);", "float v = (float)Math.Sqrt(s.refMass / m);\n            return v > 2f ? 2f : v;"),
    ("mass scale ceiling", "return v < 0.25f ? 0.25f : (v > 2f ? 2f : v);", "return v < 0.25f ? 0.25f : v;"),
    ("mass below 1 not floored", "float m = Math.Max(mass, 1f);", "float m = mass;"),
    ("rounding to even", "int cells = (int)Math.Round(raw, MidpointRounding.AwayFromZero);", "int cells = (int)Math.Round(raw);"),
    ("rounding down", "int cells = (int)Math.Round(raw, MidpointRounding.AwayFromZero);", "int cells = (int)raw;"),
    ("cap ignored", "if (cells > s.maxCells)\n            {\n                cells = s.maxCells;\n            }\n            return cells < 1 ? 0 : cells;", "return cells < 1 ? 0 : cells;"),
    ("sub-cell throw rounds up to 1", "return cells < 1 ? 0 : cells;", "return cells < 1 ? 1 : cells;"),
    ("own cap ignores the scale", "int c = (int)Math.Round(ownCap * ownCapScale, MidpointRounding.AwayFromZero);", "int c = ownCap;"),
    ("own cap may be zero", "return c < 1 ? 1 : c;", "return c;"),
    ("own cap 0 means no throw", "if (ownCap <= 0)\n            {\n                return globalCap;\n            }", "if (ownCap < 0)\n            {\n                return globalCap;\n            }"),
    ("pawn body size gate off by one", "bodySize >= s.immuneBodySize", "bodySize > s.immuneBodySize"),
    ("items ignore the mass limit", "(kind == KbKind.Item || kind == KbKind.Corpse) && mass > s.lightMassLimit", "kind == KbKind.Corpse && mass > s.lightMassLimit"),
    ("corpses ignore body size", "(kind == KbKind.Pawn || kind == KbKind.Corpse) && bodySize >= s.immuneBodySize", "kind == KbKind.Pawn && bodySize >= s.immuneBodySize"),
    ("line length one short", "int tx = sx + (int)Math.Round(dx / m * cells, MidpointRounding.AwayFromZero);", "int tx = sx + (int)Math.Round(dx / m * (cells - 1), MidpointRounding.AwayFromZero);"),
    ("line rounds to even", "int x = sx + (ddx == 0 ? 0 : stepX * (int)Math.Round((double)ddx * i / n, MidpointRounding.AwayFromZero));", "int x = sx + (ddx == 0 ? 0 : stepX * (int)Math.Round((double)ddx * i / n));"),
    ("line truncates z", "int z = sz + (ddz == 0 ? 0 : stepZ * (int)Math.Round((double)ddz * i / n, MidpointRounding.AwayFromZero));", "int z = sz + (ddz == 0 ? 0 : stepZ * (int)((double)ddz * i / n));"),
    ("line includes the start", "for (int i = 1; i <= n; i++)", "for (int i = 0; i <= n; i++)"),
    ("negative capacity not guarded", "new List<(int, int)>(Math.Max(cells, 0))", "new List<(int, int)>(cells)"),
    ("corner cut allowed", "if (Solid(grid.At(x, pz)) || Solid(grid.At(px, z)))", "if (Solid(grid.At(x, pz)) && Solid(grid.At(px, z)))"),
    ("doors do not stop", "if (c == KbCell.Door)\n                {\n                    stop = KbStop.Door;", "if (c == KbCell.Door && false)\n                {\n                    stop = KbStop.Door;"),
    ("water does not stop", "if (c == KbCell.Water)\n                {", "if (c == KbCell.Water && false)\n                {"),
    ("pits ignore the setting", "if (c == KbCell.Pit && !s.intoPits)", "if (c == KbCell.Pit && false)"),
    ("sandbags stop items too", "if (c == KbCell.Partial && pawn && s.sandbagsStop)", "if (c == KbCell.Partial && s.sandbagsStop)"),
    ("sandbag setting ignored", "if (c == KbCell.Partial && pawn && s.sandbagsStop)", "if (c == KbCell.Partial && pawn)"),
    ("items stop on pawns", "if (c == KbCell.Pawn && pawn)", "if (c == KbCell.Pawn)"),
    ("pit does not stop the throw", "if (c == KbCell.Pit)\n                {\n                    stop = KbStop.Pit;", "if (c == KbCell.Pit && false)\n                {\n                    stop = KbStop.Pit;"),
    ("no back-off from sandbags", "if (travelled > 0 && grid.At(px, pz) == KbCell.Partial)", "if (false)"),
    ("back-off keeps the sandbag count", "travelled = lastNonPartialN;", "travelled = travelled;"),
    ("impact split not halved", "r.impact = imp * 0.5f;\n                    r.otherImpact = imp * 0.5f;", "r.impact = imp;\n                    r.otherImpact = imp;"),
    ("items take impact", "if (pawn && (stop == KbStop.Wall", "if ((stop == KbStop.Wall"),
    ("impact switch ignored", "if (!s.impactEnabled || notTravelled <= 0)", "if (notTravelled <= 0)"),
    ("impact ignores the factor", "return s.impactPerCell * s.impactFactor * notTravelled", "return s.impactPerCell * notTravelled"),
    ("impact on a plain distance stop", "if (pawn && (stop == KbStop.Wall || stop == KbStop.Door || stop == KbStop.Pawn || stop == KbStop.PartialCover))", "if (pawn)"),
    ("stun window off by one", "return now >= Math.Max(landedAt, stunEnd) + window;", "return now > Math.Max(landedAt, stunEnd) + window;"),
    ("stun uses only the landing stamp", "return now >= Math.Max(landedAt, stunEnd) + window;", "return now >= landedAt + window;"),
    ("shield gains from negative force", "return energy - Math.Max(0f, force) * Math.Max(0f, perForce) * Math.Max(0f, energyLossPerDamage);", "return energy - force * perForce * energyLossPerDamage;"),
    ("lookup prefers the weapon", "if (projectile != null)\n            {\n                projectile.source = \"projectile\";\n                return projectile;\n            }\n            if (weapon != null)", "if (projectile != null && weapon == null)\n            {\n                projectile.source = \"projectile\";\n                return projectile;\n            }\n            if (weapon != null)"),
    ("unpatched harmless blast throws", "force = harmsHealth ? unpatchedFraction : 0f", "force = unpatchedFraction"),
    ("apply mutates the shared settings", "return new KbSettings\n            {\n                globalMultiplier = global.globalMultiplier,", "global.impactFactor = 2f;\n            return new KbSettings\n            {\n                globalMultiplier = global.globalMultiplier,"),
    ("immune override of 0 applied", "c != null && c.immuneOverride > 0f ? c.immuneOverride : global.immuneBodySize", "c != null ? c.immuneOverride : global.immuneBodySize"),
    ("negative impact factor kept", "impactFactor = c != null ? Math.Max(0f, c.impactFactor) : 1f,", "impactFactor = c != null ? c.impactFactor : 1f,"),
    ("prioritise ignores kind", "int ka = KindRank(a.kind), kb = KindRank(b.kind);", "int ka = 0, kb = 0;"),
    ("prioritise nearest last", "int d = a.distance.CompareTo(b.distance);", "int d = b.distance.CompareTo(a.distance);"),
    ("prioritise tie-break dropped", "return d != 0 ? d : a.index.CompareTo(b.index);", "return d;"),
    ("prioritise cap off by one", "sorted.RemoveRange(cap, sorted.Count - cap);", "sorted.RemoveRange(cap + 1, sorted.Count - cap - 1);"),
    ("ledger key drops the explosion", "long key = ((long)explosionId << 32) ^ (uint)thingId;", "long key = (uint)thingId;"),
    ("ledger forgets everything at a rotation (the original wholesale clear)", "seenPrev = seenCur; seenCur = new HashSet<long>();\n                launchedPrev = launchedCur; launchedCur = new Dictionary<int, int>();", "seenPrev = new HashSet<long>(); seenCur = new HashSet<long>();\n                launchedPrev = new Dictionary<int, int>(); launchedCur = new Dictionary<int, int>();"),
    ("ledger never rotates", "if (gen == curGen + 1)", "if (false)"),
    ("ledger ignores the previous generation for pairs", "if (seenPrev.Contains(key)) return false;", ""),
    ("ledger forgets the previous generation's launches", "return cur + prev;", "return cur;"),
    ("ledger keeps stale entries after a long idle", "else    // two or more generations on, or the clock went backwards: nothing remembered is live\n            {\n                seenCur.Clear(); seenPrev.Clear(); launchedCur.Clear(); launchedPrev.Clear();\n            }", "else\n            {\n                seenPrev = seenCur; seenCur = new HashSet<long>();\n            }"),
    ("ledger launch count not added", "launchedCur[explosionId] = n + 1;", "launchedCur[explosionId] = 1;"),
    ("ledger window zero", "this.window = Math.Max(1, window);", "this.window = window;"),
    ("budget never resets", "if (now != tick)", "if (now < tick)"),
    ("budget allows cap + 1", "if (used >= cap)", "if (used > cap)"),
    ("epicentre direction not unit", "dz = (float)Math.Sin(a);", "dz = (float)Math.Sin(a) * 2;"),
    ("epicentre ignores the explosion", "h = (h ^ (uint)explosionId) * 16777619u;", "h = h * 16777619u;"),
]

if __name__ == "__main__":
    sys.exit(run_mutations("src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackMath.cs",
                           "selftest_explosiveknockback_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
