using System;
using System.Collections.Generic;

namespace RimMandrake.ExplosiveKnockback
{
    // The pure kernel of Explosive Knockback (design/RimMandrake/explosive_knockback_design_2026-10-06.md §3.3-3.4,
    // §4.4, §8.1). Verse-free on purpose: Source/SelfTest compiles THIS file, so every rule below is tested as
    // shipped. A `using Verse;` here breaks the selftest build, and that break is the guard rail working.

    public enum KbCell : byte
    {
        Open = 0,        // walkable, nothing in the way
        Wall = 1,        // impassable edifice / rock / Fillage.Full
        Door = 2,        // a closed door (incl. a FlowWorks sluice door)
        Partial = 3,     // sandbags, barricade: Fillage.Partial and passable
        Pawn = 4,        // another pawn stands here
        Pit = 5,         // an OPEN FlowWorks pit cell (D = 4, uncovered)
        CoveredPit = 6,  // a pit under an intact cover: ground for the path
        Water = 7,       // terrain this thing cannot stand on (deep water, lava)
        OutOfBounds = 8,
    }

    public enum KbKind : byte { Pawn = 0, Item = 1, Corpse = 2 }

    public enum KbStop : byte
    {
        None = 0,        // no move at all
        Distance = 1,    // flew its whole distance
        Wall = 2,
        Door = 3,
        Pawn = 4,
        Pit = 5,
        Water = 6,
        OutOfBounds = 7,
        PartialCover = 8, // only with "sandbags stop a throw" on
    }

    public interface IKbGrid
    {
        KbCell At(int x, int z);
    }

    public sealed class KbSettings
    {
        public float globalMultiplier = 1f;
        public float baseCells = 4f;
        public int maxCells = 6;
        // 70 kg = a clothed, armed human (body 60 kg + worn gear, which counts). The design's 60 kg calibrated a
        // NAKED human: with gear at ~8 kg a mortar beside a colonist threw 2, not the owner's 3 (Q7).
        public float refMass = 70f;
        public float immuneBodySize = 2.5f;
        public float lightMassLimit = 75f;
        public bool impactEnabled = true;
        public float impactPerCell = 4f;
        public bool sandbagsStop = false;
        public bool intoPits = true;
        // per-blast (design §2.1): scales wall / pawn / door impact for this blast (palm thumper 0 = an arrest tool)
        public float impactFactor = 1f;
    }

    /// <summary>One blast's knockback configuration (design §2.1). Supplied WHOLE by the first source that has one, in
    /// order projectile ThingDef -> weapon ThingDef -> DamageDef -> the "unpatched explosions" setting; no field-by-field
    /// merge, so an explicit force 0 on the projectile wins over a DamageDef that throws.</summary>
    public sealed class KbConfig
    {
        public float force = 1f;
        public int ownCap = 0;               // 0 = the global maximum
        public float impactFactor = 1f;
        public float immuneOverride = 0f;    // 0 = unset: the global immune body size holds
        public string source = "none";       // projectile | weapon | damageDef | unpatched | none (journal)
    }

    public static class KbLookup
    {
        /// <summary>First non-null wins whole. With none: a harmful blast throws at the unpatched fraction (default 0),
        /// a harmless one not at all.</summary>
        public static KbConfig Resolve(KbConfig projectile, KbConfig weapon, KbConfig damageDef, bool harmsHealth, float unpatchedFraction)
        {
            if (projectile != null)
            {
                projectile.source = "projectile";
                return projectile;
            }
            if (weapon != null)
            {
                weapon.source = "weapon";
                return weapon;
            }
            if (damageDef != null)
            {
                damageDef.source = "damageDef";
                return damageDef;
            }
            return new KbConfig { force = harmsHealth ? unpatchedFraction : 0f, source = harmsHealth ? "unpatched" : "none" };
        }

        /// <summary>A per-request copy of the global settings with this blast's cap, impact factor and body-size override
        /// applied. Never mutates the shared settings.</summary>
        public static KbSettings Apply(KbSettings global, KbConfig c, int globalCap, float ownCapScale)
        {
            return new KbSettings
            {
                globalMultiplier = global.globalMultiplier,
                baseCells = global.baseCells,
                maxCells = RM_KnockbackMath.CapFor(c?.ownCap ?? 0, globalCap, ownCapScale),
                refMass = global.refMass,
                immuneBodySize = c != null && c.immuneOverride > 0f ? c.immuneOverride : global.immuneBodySize,
                lightMassLimit = global.lightMassLimit,
                impactEnabled = global.impactEnabled,
                impactPerCell = global.impactPerCell,
                sandbagsStop = global.sandbagsStop,
                intoPits = global.intoPits,
                impactFactor = c != null ? Math.Max(0f, c.impactFactor) : 1f,
            };
        }
    }

    /// <summary>Stun-lock guard (design §4, GPT #4): no new launch until the landing stun has ended AND a recovery window
    /// has passed. window 0 = chain throws allowed.</summary>
    public static class KbImmunity
    {
        public static bool CanLaunch(int now, int landedAt, int stunEnd, int window)
        {
            if (window <= 0)
            {
                return true;
            }
            return now >= Math.Max(landedAt, stunEnd) + window;
        }
    }

    /// <summary>Shield counter (owner Q4): a shield that absorbed the blast absorbs the throw and pays
    /// force x perForce damage-equivalents (x the shield's energy loss per damage) on top. Returns the energy left; below
    /// zero the shield breaks.</summary>
    public static class KbShield
    {
        public static float EnergyAfter(float energy, float force, float perForce, float energyLossPerDamage)
        {
            return energy - Math.Max(0f, force) * Math.Max(0f, perForce) * Math.Max(0f, energyLossPerDamage);
        }
    }

    public struct KbResult
    {
        public int destX, destZ;
        public int cellsPlanned;
        public int cellsTravelled;
        public float impact;          // on the thrown pawn (already split when a pawn was hit)
        public float otherImpact;     // on the pawn it hit
        public bool hitOther;
        public int otherX, otherZ;
        public bool hitDoor;
        public int doorX, doorZ;
        public KbStop stop;

        public bool Moved => cellsTravelled > 0;
    }

    public struct KbCandidate
    {
        public int index;
        public KbKind kind;
        public float distance;
    }

    public static class RM_KnockbackMath
    {
        public static float Clamp01(float v) => v < 0f ? 0f : (v > 1f ? 1f : v);

        public static float Falloff(float dist, float radius)
        {
            if (radius <= 0f)
            {
                return 0f;
            }
            return 1f - Clamp01(dist / radius);
        }

        public static float MassScale(float mass, KbSettings s)
        {
            float m = Math.Max(mass, 1f);
            float v = (float)Math.Sqrt(s.refMass / m);
            return v < 0.25f ? 0.25f : (v > 2f ? 2f : v);
        }

        /// <summary>Cells to throw. 0 = no move. Calibration (owner Q7): mortar r 2.9, distance 1, 60 kg -> 3.</summary>
        public static int ThrowCells(float dist, float radius, float force, float mass, KbSettings s)
        {
            if (force <= 0f || s.globalMultiplier <= 0f)
            {
                return 0;
            }
            double raw = s.baseCells * force * Falloff(dist, radius) * MassScale(mass, s) * s.globalMultiplier;
            int cells = (int)Math.Round(raw, MidpointRounding.AwayFromZero);
            if (cells > s.maxCells)
            {
                cells = s.maxCells;
            }
            return cells < 1 ? 0 : cells;
        }

        /// <summary>The throw cap for one blast (owner, 2026-10-06, by question card: each weapon sets its own).
        /// ownCap > 0 = the blast's own maximum (its DamageDef's RM_KnockbackExtension.maxThrowCells) times the
        /// "weapons with their own maximum" scale, never below 1; ownCap <= 0 = the global maximum, as before.</summary>
        public static int CapFor(int ownCap, int globalCap, float ownCapScale)
        {
            if (ownCap <= 0)
            {
                return globalCap;
            }
            int c = (int)Math.Round(ownCap * ownCapScale, MidpointRounding.AwayFromZero);
            return c < 1 ? 1 : c;
        }

        /// <summary>Does this thing move at all, before geometry? bodySize only matters for pawns and corpses.</summary>
        public static bool Eligible(KbKind kind, float mass, float bodySize, KbSettings s)
        {
            if ((kind == KbKind.Pawn || kind == KbKind.Corpse) && bodySize >= s.immuneBodySize)
            {
                return false;
            }
            if ((kind == KbKind.Item || kind == KbKind.Corpse) && mass > s.lightMassLimit)
            {
                return false;
            }
            return true;
        }

        /// <summary>A deterministic direction for a thing on the blast's own cell, keyed on (explosion, thing).</summary>
        public static void EpicentreDir(int explosionId, int thingId, out float dx, out float dz)
        {
            unchecked
            {
                uint h = 2166136261u;
                h = (h ^ (uint)explosionId) * 16777619u;
                h = (h ^ (uint)thingId) * 16777619u;
                h ^= h >> 13;
                h *= 0x5bd1e995u;
                h ^= h >> 15;
                double a = (h % 360u) * Math.PI / 180.0;
                dx = (float)Math.Cos(a);
                dz = (float)Math.Sin(a);
            }
        }

        /// <summary>The cells of the throw: grid steps along the line from (sx,sz) in direction (dx,dz), exactly
        /// `cells` steps long (cell count is grid steps, not Euclidean — GPT #15). Excludes the start.</summary>
        public static List<(int x, int z)> Line(int sx, int sz, float dx, float dz, int cells)
        {
            var path = new List<(int, int)>(Math.Max(cells, 0));
            float m = Math.Max(Math.Abs(dx), Math.Abs(dz));
            if (cells <= 0 || m < 1e-6f)
            {
                return path;
            }
            int tx = sx + (int)Math.Round(dx / m * cells, MidpointRounding.AwayFromZero);
            int tz = sz + (int)Math.Round(dz / m * cells, MidpointRounding.AwayFromZero);
            int ddx = Math.Abs(tx - sx), ddz = Math.Abs(tz - sz);
            int stepX = tx > sx ? 1 : -1, stepZ = tz > sz ? 1 : -1;
            int n = Math.Max(ddx, ddz);
            for (int i = 1; i <= n; i++)
            {
                // symmetric DDA: one step per i along the major axis
                int x = sx + (ddx == 0 ? 0 : stepX * (int)Math.Round((double)ddx * i / n, MidpointRounding.AwayFromZero));
                int z = sz + (ddz == 0 ? 0 : stepZ * (int)Math.Round((double)ddz * i / n, MidpointRounding.AwayFromZero));
                path.Add((x, z));
            }
            return path;
        }

        private static bool Solid(KbCell c) => c == KbCell.Wall || c == KbCell.Door || c == KbCell.OutOfBounds;

        public static float ImpactFor(int notTravelled, float mass, KbSettings s)
        {
            if (!s.impactEnabled || notTravelled <= 0)
            {
                return 0f;
            }
            return s.impactPerCell * s.impactFactor * notTravelled / (float)Math.Sqrt(MassScale(mass, s));
        }

        /// <summary>Walk the throw (design §3.4). The start cell is never read.</summary>
        public static KbResult Resolve(IKbGrid grid, int sx, int sz, float dx, float dz, int cells, KbKind kind,
            float mass, KbSettings s)
        {
            var r = new KbResult { destX = sx, destZ = sz, cellsPlanned = cells, stop = KbStop.None };
            if (cells <= 0)
            {
                return r;
            }
            bool pawn = kind == KbKind.Pawn;
            List<(int x, int z)> path = Line(sx, sz, dx, dz, cells);
            int px = sx, pz = sz;
            int travelled = 0;
            KbStop stop = KbStop.Distance;
            int lastNonPartialX = sx, lastNonPartialZ = sz, lastNonPartialN = 0;
            foreach ((int x, int z) in path)
            {
                KbCell c = grid.At(x, z);
                // a diagonal step never cuts a wall corner: both orthogonal neighbours must be open
                if (x != px && z != pz && c != KbCell.OutOfBounds)
                {
                    if (Solid(grid.At(x, pz)) || Solid(grid.At(px, z)))
                    {
                        stop = KbStop.Wall;
                        break;
                    }
                }
                if (c == KbCell.OutOfBounds)
                {
                    stop = KbStop.OutOfBounds;
                    break;
                }
                if (c == KbCell.Wall)
                {
                    stop = KbStop.Wall;
                    break;
                }
                if (c == KbCell.Door)
                {
                    stop = KbStop.Door;
                    r.hitDoor = true;
                    r.doorX = x;
                    r.doorZ = z;
                    break;
                }
                if (c == KbCell.Water)
                {
                    stop = KbStop.Water;
                    break;
                }
                if (c == KbCell.Pit && !s.intoPits)
                {
                    stop = KbStop.Wall; // "throw into pits" off: an open pit is a wall for the path
                    break;
                }
                if (c == KbCell.Partial && pawn && s.sandbagsStop)
                {
                    stop = KbStop.PartialCover;
                    break;
                }
                if (c == KbCell.Pawn && pawn)
                {
                    stop = KbStop.Pawn;
                    r.hitOther = true;
                    r.otherX = x;
                    r.otherZ = z;
                    break;
                }
                // enter the cell
                px = x;
                pz = z;
                travelled++;
                if (c != KbCell.Partial)
                {
                    lastNonPartialX = x;
                    lastNonPartialZ = z;
                    lastNonPartialN = travelled;
                }
                if (c == KbCell.Pit)
                {
                    stop = KbStop.Pit; // stops IN the first open pit cell: nothing is thrown across a pit
                    break;
                }
            }
            // nothing comes to rest on a sandbag cell (vanilla Sandbags are PassThroughOnly: walkable, not standable):
            // back to the last free cell along the line
            if (travelled > 0 && grid.At(px, pz) == KbCell.Partial)
            {
                px = lastNonPartialX;
                pz = lastNonPartialZ;
                travelled = lastNonPartialN;
            }
            r.destX = px;
            r.destZ = pz;
            r.cellsTravelled = travelled;
            r.stop = travelled == 0 && stop == KbStop.Distance ? KbStop.None : stop;
            if (pawn && (stop == KbStop.Wall || stop == KbStop.Door || stop == KbStop.Pawn || stop == KbStop.PartialCover))
            {
                float imp = ImpactFor(cells - travelled, mass, s);
                if (stop == KbStop.Pawn)
                {
                    r.impact = imp * 0.5f;
                    r.otherImpact = imp * 0.5f;
                }
                else
                {
                    r.impact = imp;
                }
            }
            return r;
        }

        /// <summary>Per-explosion cap (§4.4): pawns first, then corpses, then items nearest the centre.
        /// Returns the candidates kept, in throw order.</summary>
        public static List<KbCandidate> Prioritise(List<KbCandidate> all, int cap)
        {
            var sorted = new List<KbCandidate>(all);
            sorted.Sort((a, b) =>
            {
                int ka = KindRank(a.kind), kb = KindRank(b.kind);
                if (ka != kb)
                {
                    return ka.CompareTo(kb);
                }
                int d = a.distance.CompareTo(b.distance);
                return d != 0 ? d : a.index.CompareTo(b.index);
            });
            if (cap >= 0 && sorted.Count > cap)
            {
                sorted.RemoveRange(cap, sorted.Count - cap);
            }
            return sorted;
        }

        private static int KindRank(KbKind k) => k == KbKind.Pawn ? 0 : (k == KbKind.Corpse ? 1 : 2);
    }

    /// <summary>
    /// What one map remembers about recent explosions: which (explosion, thing) pairs were already queued (a repeat callback enqueues
    /// nothing, GPT #2) and how many throws each explosion has launched (the per-explosion cap spans several ticks). Ids never repeat, so
    /// old entries are dead weight; they are dropped in two generations a `window` apart instead of all at once, so an explosion whose
    /// wave straddles a rotation still has its pairs and its launch count: an entry lives at least `window` and at most 2 x `window` ticks.
    /// (The first version cleared everything every 600 ticks, which wiped a live explosion's cap and dedupe about 1% of the time.)
    /// </summary>
    public sealed class KbExplosionLedger
    {
        public const int DefaultWindow = 600;
        private HashSet<long> seenCur = new HashSet<long>(), seenPrev = new HashSet<long>();
        private Dictionary<int, int> launchedCur = new Dictionary<int, int>(), launchedPrev = new Dictionary<int, int>();
        private long curGen = long.MinValue;
        private readonly int window;

        public KbExplosionLedger(int window = DefaultWindow) { this.window = Math.Max(1, window); }

        // generations sit on a fixed grid of `window` ticks, so an entry made at tick t is certainly live until t + window and certainly
        // gone from t + 2 x window, however sparse the calls are
        private void Advance(int now)
        {
            long gen = now >= 0 ? now / window : -((-(long)now + window - 1) / window);
            if (curGen == long.MinValue) { curGen = gen; return; }
            if (gen == curGen) return;
            if (gen == curGen + 1)
            {
                seenPrev = seenCur; seenCur = new HashSet<long>();
                launchedPrev = launchedCur; launchedCur = new Dictionary<int, int>();
            }
            else    // two or more generations on, or the clock went backwards: nothing remembered is live
            {
                seenCur.Clear(); seenPrev.Clear(); launchedCur.Clear(); launchedPrev.Clear();
            }
            curGen = gen;
        }

        /// <summary>True the first time this (explosion, thing) pair is seen inside the memory window.</summary>
        public bool TryAdd(int explosionId, int thingId, int now)
        {
            Advance(now);
            long key = ((long)explosionId << 32) ^ (uint)thingId;
            if (seenPrev.Contains(key)) return false;
            return seenCur.Add(key);
        }

        /// <summary>Throws launched for this explosion within the memory window (both generations).</summary>
        public int Launched(int explosionId, int now)
        {
            Advance(now);
            int cur, prev;
            launchedCur.TryGetValue(explosionId, out cur);
            launchedPrev.TryGetValue(explosionId, out prev);
            return cur + prev;
        }

        public void AddLaunched(int explosionId, int now)
        {
            Advance(now);
            int n;
            launchedCur.TryGetValue(explosionId, out n);
            launchedCur[explosionId] = n + 1;
        }
    }

    /// <summary>The per-map-tick item cap: overflow is DROPPED, not deferred, so nothing accumulates.</summary>
    public sealed class KbTickBudget
    {
        private int tick = int.MinValue;
        private int used;

        public bool TryTake(int now, int cap)
        {
            if (now != tick)
            {
                tick = now;
                used = 0;
            }
            if (used >= cap)
            {
                return false;
            }
            used++;
            return true;
        }

        public int Used(int now) => now == tick ? used : 0;
    }
}
