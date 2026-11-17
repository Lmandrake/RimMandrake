using System;
using System.Collections.Generic;

namespace RimMandrake.ExplosiveKnockback
{
    // The whole throw decision of Explosive Knockback, Verse-free (RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX).
    // Until 2026-11-17 these rules lived in RM_MapComponent_Knockback.Execute / ThrowContainer and the two flyers, in Verse
    // code no offline test could run: five blind cycles each found the next real miss there (a pawn on a cover, a throw over
    // a covered pit, a stack on a cover) and ten planted caller faults survived every offline suite. Now the game side only
    // READS facts (KbFacts, IKbWorld) and APPLIES the plan (KbPlan); every rule is here, compiled by Source/SelfTest as
    // shipped and walked by the situation map (SelfTest/KnockbackMap.cs). A `using Verse;` here breaks the selftest build,
    // and that break is the guard rail working.

    /// <summary>What the plan tells the game side to do with one request.</summary>
    public enum KbAct : byte
    {
        None = 0,            // not ours, nothing journalled (a container with the shove off, an open building)
        Skip = 1,            // stays; journal "skip" with `reason`
        Absorb = 2,          // a shield belt absorbed the blast: it pays, the wearer stays
        Blocked = 3,         // a throw was planned but not one cell of it is free; a pawn still takes its impact
        LaunchPawn = 4,      // fly the pawn to res.dest
        ThrowGoods = 5,      // fly the stack or corpse along `legs` (the last leg's dest is where it comes down)
        ContainerThrown = 6, // fly the closed container to (toX, toZ)
        ContainerJolt = 7,   // the closed container shakes in place
    }

    /// <summary>One thing a request names, as the game reads it when the queue is flushed. Plain values only.</summary>
    public sealed class KbFacts
    {
        public KbKind kind;
        public bool container;        // a closed-container building (RM_KnockbackCompat.IsClosedContainer); kind is then ignored
        public bool spawned = true;   // spawned on this map and not destroyed
        public int thingId;
        public int x, z;
        /// <summary>kg. Pawn: the Mass stat less carried inventory, never under 1. Corpse: its inner pawn's Mass. Item: unit
        /// mass x stack count. Container: its own mass plus the goods on its cell (guard on) plus what it holds inside.</summary>
        public float mass;
        // ── a living pawn's states ──
        public bool dead, flying, inBed, carryingPawn, downed, animal, mechanoid;
        public bool shieldAbsorbed;   // a shield absorbed this blast's damage on this pawn
        public bool recovering;       // inside its landing stun plus the recovery window (KbImmunity.CanLaunch said no)
        public int gasShovedAgo = int.MaxValue; // ticks since a burning-gas clump last shoved it
        // ── where it is ──
        public bool onSuperdeep;      // its cell is dug to superdeep, covered or not
        public bool onStorage;        // the edifice under a good is storage of any kind
        public bool onClosed;         // the edifice under a good is a closed container
        // ── a container ──
        public bool oneByOne;
    }

    /// <summary>One blast as a request carries it.</summary>
    public sealed class KbBlast
    {
        public int id;                // the explosion's id; negative = a burning-gas clump burst
        public int cx, cz;
        public float radius, force;
        public bool gas;
    }

    /// <summary>The Mod Settings the decision reads beyond the kernel's KbSettings.</summary>
    public sealed class KbRules
    {
        public bool throwDowned = true, throwAnimals = true, throwMechanoids = true, throwItems = true, throwCorpses = true;
        public bool flyingGoods = true;
        public bool closedContainerGuard = true, openStorageProtects = false, shoveClosedContainers = true;
        public bool shieldsAbsorbThrow = true;
        public float wild = 1.6f;
        public float containerMassLimit = 250f;
        public int gasPawnCooldownTicks = 120;
        public bool goodsRebound = true;
        public float goodsReboundKeepPercent = 70f;
        public int maxBounces = 6;
    }

    /// <summary>The map as the decision reads it. `Grid(forPawn)` is the path grid (pawns block only a thrown pawn); the
    /// rest is what a closed container's rest cell needs.</summary>
    public interface IKbWorld
    {
        IKbGrid Grid(bool forPawn);
        bool PawnAt(int x, int z);
        /// <summary>Anything standing on the cell but filth, grass and the like (an item, a building, a pawn, a blueprint).</summary>
        bool Occupied(int x, int z);
        bool Superdeep(int x, int z);
    }

    /// <summary>One leg of a thrown good's flight: from (fromX, fromZ) along (dx, dz) as `res` walked it.</summary>
    public struct KbLeg
    {
        public int fromX, fromZ;
        public float dx, dz;
        public KbResult res;
    }

    public sealed class KbPlan
    {
        public KbAct act;
        public string reason;         // Skip: the journal reason
        public KbKind kind;
        public float mass;
        public KbSettings s;          // this request's kernel settings, as the decision left them (a gas shove caps at 1)
        public float dist;
        public int kernelCells, cells;
        public float dx, dz;
        public KbResult res;          // the first leg's walk (a pawn's whole throw)
        /// <summary>ThrowGoods: the leg the stack flies first. Normally the walk from its own cell; `wallFirst` = the wall,
        /// door or map edge stood right behind it, so it takes the hit where it lies and this is already the bounce.</summary>
        public KbLeg first;
        public bool wallFirst;
        public bool hopped;           // its short throw ended on sandbags and it cleared them instead of staying put
        // container
        public int planned, travelled, toX, toZ;
        public bool overLimit;

        public bool Throws => act == KbAct.LaunchPawn || act == KbAct.ThrowGoods || act == KbAct.ContainerThrown;
    }

    public static class KbPlanner
    {
        /// <summary>Why a living pawn is never thrown (leaf the_spared), or null. Order is the journal's.</summary>
        public static string PawnSkipReason(KbFacts f, KbRules q)
        {
            if (f.dead) return "dead";
            if (f.flying) return "flying";
            if (f.inBed) return "in_bed";
            if (f.carryingPawn) return "carrying_pawn";
            if (f.downed && !q.throwDowned) return "downed_off";
            if (f.animal && !q.throwAnimals) return "animals_off";
            if (f.mechanoid && !q.throwMechanoids) return "mechanoids_off";
            if (f.onSuperdeep) return "in_pit"; // GPT #1 + "you can't climb out. Period."
            return null;
        }

        /// <summary>Owner ruling 2026-11-10/11: why the storage under a loose good keeps it, or null. Only a closed container
        /// does (with the closed guard on); open storage only when the player turned the old rule back on.</summary>
        public static string HeldReason(KbFacts f, KbRules q)
        {
            bool closed = q.closedContainerGuard && f.onClosed;
            bool storage = closed || f.onStorage;
            if (!RM_KnockbackMath.GoodsHeld(storage, closed, q.openStorageProtects))
            {
                return null;
            }
            return closed ? "closed_container" : "in_storage";
        }

        private static KbPlan Skip(KbPlan p, string reason)
        {
            p.act = KbAct.Skip;
            p.reason = reason;
            return p;
        }

        private static void Direction(KbFacts f, KbBlast b, out float dx, out float dz)
        {
            if (f.x == b.cx && f.z == b.cz)
            {
                RM_KnockbackMath.EpicentreDir(b.id, f.thingId, out dx, out dz);
            }
            else
            {
                dx = f.x - b.cx;
                dz = f.z - b.cz;
            }
        }

        private static float Dist(KbFacts f, KbBlast b)
        {
            float ex = f.x - b.cx, ez = f.z - b.cz;
            return (float)Math.Sqrt(ex * ex + ez * ez);
        }

        /// <summary>One request's whole decision. `s` is this request's own kernel settings (a fresh copy: it is changed
        /// here for a gas shove and a container). The gates run in the journal's order; geometry comes last.</summary>
        public static KbPlan Decide(KbFacts f, KbBlast b, KbRules q, KbSettings s, IKbWorld w)
        {
            var p = new KbPlan { act = KbAct.None, kind = f.kind, mass = f.mass, s = s };
            if (!f.spawned)
            {
                return Skip(p, "not_spawned");
            }
            if (f.container)
            {
                return Container(p, f, b, q, s, w);
            }
            bool pawn = f.kind == KbKind.Pawn;
            if (pawn)
            {
                string why = PawnSkipReason(f, q);
                if (why != null)
                {
                    return Skip(p, why);
                }
            }
            else if (f.kind == KbKind.Corpse)
            {
                if (!q.throwCorpses)
                {
                    return Skip(p, "corpses_off");
                }
            }
            else
            {
                if (!q.throwItems)
                {
                    return Skip(p, "items_off");
                }
                string held = HeldReason(f, q);
                if (held != null)
                {
                    return Skip(p, held);
                }
            }
            if (!pawn && f.onSuperdeep)
            {
                return Skip(p, "in_pit");
            }
            // goods in the air off (sheet, settings_scale_and_switch: "goods unthrown, never the old hop")
            if (!pawn && !q.flyingGoods)
            {
                return Skip(p, "flying_off");
            }
            if (pawn && b.gas)
            {
                // burning gas shoves a person one cell, at most once per gasPawnCooldownTicks (plan step 4)
                if (f.gasShovedAgo < q.gasPawnCooldownTicks)
                {
                    return Skip(p, "gas_cooldown");
                }
                s.maxCells = Math.Min(s.maxCells, 1);
            }
            if (pawn && f.shieldAbsorbed && q.shieldsAbsorbThrow)
            {
                p.act = KbAct.Absorb;
                return p;
            }
            if (pawn && f.recovering)
            {
                return Skip(p, "immune");
            }
            if (!RM_KnockbackMath.Eligible(f.kind, f.mass, s))
            {
                return Skip(p, pawn ? "too_heavy_creature" : "too_heavy");
            }
            p.dist = Dist(f, b);
            p.kernelCells = RM_KnockbackMath.ThrowCells(p.dist, b.radius, b.force, f.mass, s);
            // goods and corpses fly wild; people keep the kernel
            p.cells = pawn ? p.kernelCells : RM_KnockbackMath.WildCells(p.dist, b.radius, b.force, f.mass, s, q.wild);
            // the rim (inv_too_weak_skip; every_good_moves' "reached"): a throw is decided by the KERNEL; the wild factor only
            // lengthens a good's throw of a cell or more, it never lifts a rim good the kernel leaves in place
            if (p.kernelCells <= 0 || p.cells <= 0)
            {
                return Skip(p, "too_weak");
            }
            Direction(f, b, out p.dx, out p.dz);
            p.res = RM_KnockbackMath.Resolve(w.Grid(pawn), f.x, f.z, p.dx, p.dz, p.cells, f.kind, f.mass, s);
            if (!p.res.Moved && !pawn)
            {
                GoodsWithNoFirstCell(p, f, s, q, w.Grid(false));
            }
            if (!p.res.Moved && !p.wallFirst)
            {
                p.act = KbAct.Blocked;
                return p;
            }
            if (!pawn && !p.wallFirst)
            {
                p.first = new KbLeg { fromX = f.x, fromZ = f.z, dx = p.dx, dz = p.dz, res = p.res };
            }
            p.act = pawn ? KbAct.LaunchPawn : KbAct.ThrowGoods;
            return p;
        }

        /// <summary>Leaf every_good_moves ("the player never sees one stack sit still in the blast while its neighbours fly")
        /// where the walk gave a good no first cell. The situation map (SelfTest/KnockbackMap.cs, reading M04) found 14,070 of
        /// 47,952 reached goods in walled storerooms sitting still, every one of them for one of two reasons:
        /// a wall, closed door or the map edge right behind it: it is slammed into that face where it lies and bounces off it
        /// like any flying good (leaf goods_arc_spin_rebound), all its cells still to lose;
        /// sandbags (or a shelf) under its whole short throw: backing off them would undo the throw, so it clears them and
        /// comes down on the first cell past them ("they pass over sandbags"), at most HopExtraCells farther.
        /// Deep water right behind it still holds it ("stop short of deep water, never lost in it").</summary>
        private static void GoodsWithNoFirstCell(KbPlan p, KbFacts f, KbSettings s, KbRules q, IKbGrid grid)
        {
            if (p.res.stop == KbStop.None)
            {
                for (int n = p.cells + 1; n <= p.cells + HopExtraCells; n++)
                {
                    KbResult r = RM_KnockbackMath.Resolve(grid, f.x, f.z, p.dx, p.dz, n, f.kind, f.mass, s);
                    if (r.Moved)
                    {
                        p.res = r;
                        p.hopped = true;
                        return;
                    }
                }
                return;
            }
            if (Rebound(grid, p.res.stop, p.cells, 0, p.res, f.x, f.z, p.dx, p.dz, f.kind, f.mass, s, q, out KbLeg bounce))
            {
                p.first = bounce;
                p.wallFirst = true;
            }
        }

        /// <summary>How many cells past its planned throw a good may go to clear sandbags it would otherwise end on. 2 = the
        /// deepest line a throw can end on and still be undone: vanilla sandbags and barricades are one cell deep and a shelf
        /// two (Shelf is 2x1), so a throw of N cells that ends on such a line clears it within N + 2. A counterexample would be
        /// a three-deep sandbag field: there the good stays, as it did before.</summary>
        public const int HopExtraCells = 2;

        /// <summary>Where a landing stack is put, in order, each tried until one takes it (RM_MapComponent_Knockback.PlaceLanding
        /// applies them through GenPlace; the map's model applies the same list).</summary>
        public enum KbPlace : byte
        {
            Direct = 0,       // on the landing cell itself
            NearCell = 1,     // GenPlace's "near" the landing cell
            PitFloor = 2,     // near the landing cell, on an open pit floor only, within PitSpread of it
            NearRim = 3,      // beside the pit on the side it came from, never past it
            NearOrigin = 4,   // GenPlace's "near" where it was thrown from
            Fallback = 5,     // spawned on the landing cell whatever is there
        }

        /// <summary>A pit floor cell this far from the landing cell still takes the stack: 1.5 = the eight cells around it, the
        /// first ring GenPlace's own "near" search reads, so a stack that finds its pit cell taken settles beside it on the
        /// floor and is never seen to jump along a trench.</summary>
        public const float PitSpread = 1.5f;

        /// <summary>With the pit floor beside it full, a stack is set down on open ground this near its landing cell, on the side
        /// its leg came from (no farther from the leg's start than the landing cell is, so never past the pit). 2.9 = the
        /// radius of GenPlace's own second search ring (PlaceNearMiddleRadialCells is the cells within 3): near enough to read
        /// as tumbling back off the heap. The map's reading M15 counts every such landing and how far it was set down.</summary>
        public const float RimSpread = 2.9f;

        /// <summary>Leaf thrown_into_pit_falls ("falls to its floor ... never anything thrown across a pit"; false pass "the
        /// stack lands on the pit rim"). The map (reading M02) found 401 of 2,200 flights that met a pit ending on the rim or
        /// past it: the game holds one stack a cell, and GenPlace's "near" then picked any neighbour, the far rim included. A
        /// landing on a pit cell that cannot take the stack now goes to the pit floor beside it, and only with that floor full
        /// to the rim on the side it came from. `wouldBump` = a Direct placement would move a resident stack (never done).</summary>
        public static KbPlace[] LandingOrder(bool wouldBump, bool destSuperdeep)
        {
            if (destSuperdeep)
            {
                return wouldBump
                    ? new[] { KbPlace.PitFloor, KbPlace.NearRim, KbPlace.NearOrigin, KbPlace.Fallback }
                    : new[] { KbPlace.Direct, KbPlace.PitFloor, KbPlace.NearRim, KbPlace.NearOrigin, KbPlace.Fallback };
            }
            return wouldBump
                ? new[] { KbPlace.NearCell, KbPlace.NearOrigin, KbPlace.Fallback }
                : new[] { KbPlace.Direct, KbPlace.NearCell, KbPlace.NearOrigin, KbPlace.Fallback };
        }

        /// <summary>May the stack that came down on pit cell (dx, dz), on a leg flown from (fromX, fromZ), be put on (x, z)
        /// under `place`? `cell` is the path grid's reading of (x, z) for goods. PitFloor: an open pit floor cell within
        /// PitSpread. NearRim: open ground within RimSpread of the landing cell and no farther from where the leg began than
        /// the landing cell is (the side it came from). Never a wall, a door, water or sandbags: GenPlace's "near" takes even those when nothing
        /// better is offered.</summary>
        public static bool PlaceAllows(KbPlace place, int x, int z, int dx, int dz, int fromX, int fromZ, KbCell cell)
        {
            float ex = x - dx, ez = z - dz;
            float d2 = ex * ex + ez * ez;
            if (place == KbPlace.PitFloor)
            {
                return cell == KbCell.Pit && d2 <= PitSpread * PitSpread;
            }
            if (place == KbPlace.NearRim)
            {
                float a = (x - fromX) * (float)(x - fromX) + (z - fromZ) * (float)(z - fromZ);
                float b = (dx - fromX) * (float)(dx - fromX) + (dz - fromZ) * (float)(dz - fromZ);
                return cell == KbCell.Open && d2 <= RimSpread * RimSpread && a <= b;
            }
            return true;
        }

        /// <summary>The explosion prefix's question, asked BEFORE the blast damages the stack: will Decide throw it (same
        /// gates, same kernel)? Path blocks are not predicted: a stack spared and then blocked is still spared.</summary>
        public static bool GoodWillBeThrown(KbFacts f, KbBlast b, KbRules q, KbSettings s)
        {
            if (!f.spawned || !q.throwItems || !q.flyingGoods || HeldReason(f, q) != null || f.onSuperdeep
                || !RM_KnockbackMath.Eligible(KbKind.Item, f.mass, s))
            {
                return false;
            }
            float dist = Dist(f, b);
            return RM_KnockbackMath.ThrowCells(dist, b.radius, b.force, f.mass, s) > 0
                && RM_KnockbackMath.WildCells(dist, b.radius, b.force, f.mass, s, q.wild) > 0;
        }

        /// <summary>Owner, 2026-11-12: "the whole crate/chest would go flying a bit, but their contents would remain inside and
        /// protected". A 1x1 closed container at or under the container mass limit flies the kernel's item throw at its whole
        /// mass; never into a pit (a pit is a wall for its path), never through a person; it comes to rest on the farthest
        /// free open cell of its path. With no such cell it jolts in place.</summary>
        private static KbPlan Container(KbPlan p, KbFacts f, KbBlast b, KbRules q, KbSettings s, IKbWorld w)
        {
            if (!q.shoveClosedContainers)
            {
                return p; // None
            }
            Direction(f, b, out p.dx, out p.dz);
            s.intoPits = false; // an open pit is a wall for a container's path
            p.dist = Dist(f, b);
            p.overLimit = f.mass > q.containerMassLimit;
            p.planned = RM_KnockbackMath.ContainerThrowCells(f.oneByOne, f.mass, q.containerMassLimit, p.dist, b.radius, b.force, s);
            p.toX = f.x;
            p.toZ = f.z;
            p.travelled = 0;
            if (p.planned > 0)
            {
                IKbGrid grid = w.Grid(true);
                p.res = RM_KnockbackMath.Resolve(grid, f.x, f.z, p.dx, p.dz, p.planned, KbKind.Item, f.mass, s);
                // the cells the walk read: the first cellsTravelled of the PLANNED line. A shorter line is not its prefix off
                // the eight compass rays (the map's reading M14: 14 of 874 thrown containers came down on a cell the walk
                // never read)
                List<(int x, int z)> path = RM_KnockbackMath.Line(f.x, f.z, p.dx, p.dz, p.planned);
                for (int i = 0; i < p.res.cellsTravelled; i++)
                {
                    int x = path[i].x, z = path[i].z;
                    if (w.PawnAt(x, z))
                    {
                        break; // it does not fly through a person
                    }
                    if (ContainerCellFree(w, x, z))
                    {
                        p.toX = x;
                        p.toZ = z;
                        p.travelled = i + 1;
                    }
                }
            }
            p.act = p.travelled > 0 ? KbAct.ContainerThrown : KbAct.ContainerJolt;
            return p;
        }

        /// <summary>A cell a thrown container may come to rest on: open ground (no wall, door, sandbag, water, pit or edge),
        /// no pawn, nothing standing there but filth, grass and the like.</summary>
        public static bool ContainerCellFree(IKbWorld w, int x, int z)
        {
            return RM_KnockbackMath.ShoveCellFree(w.Grid(true).At(x, z), w.Occupied(x, z)) && !w.Superdeep(x, z);
        }

        /// <summary>A flying good's leg has ended on a solid hit: does it bounce on (leaf goods_arc_spin_rebound)? True with
        /// the next leg when the rebound is on, bounces remain, the cells left keep at least one after the loss, there is a
        /// face to reflect off and the reflected walk moves at least a cell.</summary>
        public static bool Rebound(IKbGrid grid, KbStop stop, int cellsLeft, int bounces, KbResult hit, int atX, int atZ, float dirX, float dirZ,
            KbKind kind, float mass, KbSettings s, KbRules q, out KbLeg next)
        {
            next = default(KbLeg);
            bool solid = stop == KbStop.Wall || stop == KbStop.Door || stop == KbStop.OutOfBounds;
            if (!solid || cellsLeft <= 0 || !q.goodsRebound || bounces >= q.maxBounces)
            {
                return false;
            }
            int cells = RM_KnockbackMath.ReboundCells(cellsLeft, q.goodsReboundKeepPercent);
            if (cells <= 0 || !RM_KnockbackMath.Reflect(grid, hit, dirX, dirZ, out float rx, out float rz))
            {
                return false;
            }
            KbResult nr = RM_KnockbackMath.Resolve(grid, atX, atZ, rx, rz, cells, kind, mass, s);
            if (!nr.Moved)
            {
                return false;
            }
            next = new KbLeg { fromX = atX, fromZ = atZ, dx = rx, dz = rz, res = nr };
            return true;
        }
    }
}
