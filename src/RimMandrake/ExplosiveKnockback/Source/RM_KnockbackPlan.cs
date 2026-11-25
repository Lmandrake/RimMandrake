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
        public bool onCover;          // that superdeep cell is under an intact cover (bar gas_shoves_pawn_on_pit_cover)
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
        public bool tumbled;          // no line of its throw, hop or bounce took it: it tumbled along the freest of the eight directions
        // container
        public int planned, travelled, toX, toZ;
        public bool overLimit;

        public bool Throws => act == KbAct.LaunchPawn || act == KbAct.ThrowGoods || act == KbAct.ContainerThrown;
    }

    public static class KbPlanner
    {
        /// <summary>Why a living pawn is never thrown (leaf the_spared), or null. Order is the journal's.</summary>
        public static string PawnSkipReason(KbFacts f, KbRules q, bool gas = false)
        {
            if (f.dead) return "dead";
            if (f.flying) return "flying";
            if (f.inBed) return "in_bed";
            if (f.carryingPawn) return "carrying_pawn";
            if (f.downed && !q.throwDowned) return "downed_off";
            if (f.animal && !q.throwAnimals) return "animals_off";
            if (f.mechanoid && !q.throwMechanoids) return "mechanoids_off";
            // GPT #1 + "you can't climb out. Period." A person on an intact cover stands on ground to the player: burning gas
            // shoves them as on any floor (bar gas_shoves_pawn_on_pit_cover); a blast breaks that cover, so it still skips them
            if (f.onSuperdeep && !(gas && f.onCover)) return "in_pit";
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
                string why = PawnSkipReason(f, q, b.gas);
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
            IKbGrid grid = w.Grid(pawn);
            p.res = RM_KnockbackMath.Resolve(grid, f.x, f.z, p.dx, p.dz, p.cells, f.kind, f.mass, s);
            if (!p.res.Moved && !pawn)
            {
                GoodsWithNoFirstCell(p, f, s, q, grid, b.gas);
            }
            if (!p.res.Moved && !p.wallFirst)
            {
                p.act = KbAct.Blocked;
                return p;
            }
            if (!pawn && !p.wallFirst)
            {
                if (s.intoPits)
                {
                    p.res = StopAtCrossedPit(grid, f.x, f.z, p.res);
                }
                p.first = new KbLeg { fromX = f.x, fromZ = f.z, dx = p.dx, dz = p.dz, res = p.res };
            }
            p.act = pawn ? KbAct.LaunchPawn : KbAct.ThrowGoods;
            return p;
        }

        /// <summary>Bar carried_thing_own_arc (owner 2026-11-14: "Next version it should go flying independently of the person
        /// holding it. Different trajectories."): the plan of what a thrown pawn carries, decided as a loose good of its own
        /// kind and mass lying on the carrier's cell when the blast goes off. It leaves the carrier's hands at the blast either
        /// way: a plan that Throws flies on its own flight; any other plan (too heavy, items or goods in the air switched off,
        /// a pit) leaves it on the carrier's start cell (CarriedRest). The carrier's own plan does not read it.</summary>
        public static KbPlan Carried(KbFacts carrier, int thingId, KbKind kind, float mass, KbBlast b, KbRules q, KbSettings s, IKbWorld w)
        {
            var f = new KbFacts { kind = kind == KbKind.Corpse ? KbKind.Corpse : KbKind.Item, spawned = carrier.spawned, thingId = thingId,
                x = carrier.x, z = carrier.z, mass = mass, onSuperdeep = carrier.onSuperdeep, onCover = carrier.onCover };
            return Decide(f, b, q, s, w);
        }

        /// <summary>Where a carried thing comes to rest by its plan (Carried): the end of its own first leg when it flies (a
        /// rebound or a pit may still change that in flight, as for any flying good), else the carrier's start cell.</summary>
        public static void CarriedRest(KbPlan p, KbFacts carrier, out int x, out int z)
        {
            if (p != null && p.act == KbAct.ThrowGoods)
            {
                x = p.first.res.destX;
                z = p.first.res.destZ;
                return;
            }
            x = carrier.x;
            z = carrier.z;
        }

        /// <summary>Bar collision_bruise_by_size: one rule for both ways two pawns meet. A throw the walk stopped at a pawn
        /// (res.hitOther) bruises both by size, the thrown one by the other's mass and the other by the thrown one's,
        /// in place of the walk's even split; a throw that met no pawn is left as it is.</summary>
        public static void Collide(ref KbResult res, float ownMass, float otherMass, KbSettings s)
        {
            if (!res.hitOther)
            {
                res.otherImpact = 0f;
                return;
            }
            res.impact = RM_KnockbackMath.CollisionBruise(ownMass, otherMass, s);
            res.otherImpact = RM_KnockbackMath.CollisionBruise(otherMass, ownMass, s);
        }

        /// <summary>Leaf every_good_moves ("the player never sees one stack sit still in the blast while its neighbours fly")
        /// where the walk gave a good no first cell. The situation map (SelfTest/KnockbackMap.cs, reading M04) found 14,070 of
        /// 47,952 reached goods in walled storerooms sitting still, every one of them for one of two reasons:
        /// a wall, closed door or the map edge right behind it: it is slammed into that face where it lies and bounces off it
        /// like any flying good (leaf goods_arc_spin_rebound), all its cells still to lose;
        /// sandbags (or a shelf) under its whole short throw: backing off them would undo the throw, so it clears them and
        /// comes down on the first cell past them ("they pass over sandbags"), at most HopExtraCells farther.
        /// Deep water right behind it still holds it ("stop short of deep water, never lost in it").</summary>
        private static void GoodsWithNoFirstCell(KbPlan p, KbFacts f, KbSettings s, KbRules q, IKbGrid grid, bool gas)
        {
            int maxCells = p.cells + HopExtraCells;
            if (gas)
            {
                maxCells = Math.Min(maxCells, s.maxCells);
            }
            if (p.res.stop == KbStop.None)
            {
                for (int n = p.cells + 1; n <= maxCells; n++)
                {
                    KbResult r = RM_KnockbackMath.Resolve(grid, f.x, f.z, p.dx, p.dz, n, f.kind, f.mass, s);
                    if (r.Moved)
                    {
                        p.res = r;
                        p.hopped = true;
                        return;
                    }
                }
            }
            else if (p.res.stop == KbStop.Water)
            {
                return; // deep water right behind it holds it ("never into deep water")
            }
            else if (Rebound(grid, p.res.stop, p.cells, 0, p.res, f.x, f.z, p.dx, p.dz, f.kind, f.mass, s, q, out KbLeg bounce))
            {
                p.first = bounce;
                p.wallFirst = true;
                return;
            }
            Tumble(p, f, s, grid, maxCells);
        }

        /// <summary>Leaf every_good_moves, the cases its throw, hop and bounce all leave in place (blind cycle 6,
        /// RIMMANDRAKE_MOVE_KNOCKBACK_GOODS_PINNED_AGAINST_WALLS_SHELVES; seed 7741: 593 of 12,474 reached goods in walled rooms, and
        /// 764 of 10,699 in shelf storerooms, sat still): a one-cell throw into a wall (a bounce keeps floor(0.7 x 1) = 0 cells), a
        /// bounce whose reflected line is blocked at a corner, a throw along a shelf row deeper than HopExtraCells. The good tumbles
        /// along the first of the eight directions, most in line with its throw first, whose walk of its throw (up to
        /// HopExtraCells more, to clear a shelf) moves it. Only a good with no such line anywhere stays.</summary>
        private static void Tumble(KbPlan p, KbFacts f, KbSettings s, IKbGrid grid, int maxCells)
        {
            float m = (float)Math.Sqrt(p.dx * p.dx + p.dz * p.dz);
            float ux = m > 1e-6f ? p.dx / m : 1f, uz = m > 1e-6f ? p.dz / m : 0f;
            var dirs = new List<(int x, int z, float dot)>(8);
            for (int ddx = -1; ddx <= 1; ddx++)
            {
                for (int ddz = -1; ddz <= 1; ddz++)
                {
                    if (ddx == 0 && ddz == 0) continue;
                    float n2 = (float)Math.Sqrt(ddx * ddx + ddz * ddz);
                    dirs.Add((ddx, ddz, (ddx * ux + ddz * uz) / n2));
                }
            }
            // most in line first; ties keep the fixed order above, so the choice is deterministic
            var order = new List<int> { 0, 1, 2, 3, 4, 5, 6, 7 };
            order.Sort((a, b) => { int c = dirs[b].dot.CompareTo(dirs[a].dot); return c != 0 ? c : a.CompareTo(b); });
            foreach (int i in order)
            {
                for (int n = Math.Max(1, p.cells); n <= maxCells; n++)
                {
                    KbResult r = RM_KnockbackMath.Resolve(grid, f.x, f.z, dirs[i].x, dirs[i].z, n, f.kind, f.mass, s);
                    if (r.Moved)
                    {
                        p.res = r;
                        p.dx = dirs[i].x;
                        p.dz = dirs[i].z;
                        p.tumbled = true;
                        return;
                    }
                }
            }
        }

        /// <summary>How many cells past its planned throw a good may go to clear sandbags it would otherwise end on. 2 = the
        /// deepest line a throw can end on and still be undone: vanilla sandbags and barricades are one cell deep and a shelf
        /// two (Shelf is 2x1), so a throw of N cells that ends on such a line clears it within N + 2. A counterexample would be
        /// a three-deep sandbag field: there the good stays, as it did before.</summary>
        public const int HopExtraCells = 2;

        /// <summary>Goods fly from cell centre to cell centre. Between the kernel's rounded steps the straight leg can
        /// enter an open pit. End the flight on that ray at the pit lip and use the pit cell for landing.</summary>
        private static KbResult StopAtCrossedPit(IKbGrid grid, int fromX, int fromZ, KbResult res)
        {
            int dx = res.destX - fromX, dz = res.destZ - fromZ;
            if (dx == 0 || dz == 0)
            {
                return res;
            }
            int nx = Math.Abs(dx), nz = Math.Abs(dz);
            int stepX = Math.Sign(dx), stepZ = Math.Sign(dz);
            int x = 0, z = 0;
            while (x != nx || z != nz)
            {
                // Compare the next boundary times (x + 0.5) / nx and (z + 0.5) / nz. A corner enters only the diagonal cell.
                int crossX = (2 * x + 1) * nz, crossZ = (2 * z + 1) * nx;
                if (crossX <= crossZ) x++;
                if (crossZ <= crossX) z++;
                if (x == nx && z == nz) return res;
                int atX = fromX + x * stepX, atZ = fromZ + z * stepZ;
                if (grid.At(atX, atZ) == KbCell.Pit)
                {
                    float entry = Math.Min(crossX, crossZ) / (2f * nx * nz);
                    return new KbResult { destX = atX, destZ = atZ, cellsPlanned = res.cellsPlanned,
                        cellsTravelled = Math.Max(x, z), stop = KbStop.Pit,
                        pitEntryOffsetX = dx * entry - x * stepX, pitEntryOffsetZ = dz * entry - z * stepZ };
                }
            }
            return res;
        }

        /// <summary>Where a landing stack is put, in order, each tried until one takes it (RM_MapComponent_Knockback.PlaceLanding
        /// applies them through GenPlace; the map's model applies the same list).</summary>
        public enum KbPlace : byte
        {
            Direct = 0,       // on the landing cell itself
            NearCell = 1,     // GenPlace's "near" the landing cell
            PitFloor = 2,     // the nearest free floor cell of the pit it came down in (PitAround)
            NearRim = 3,      // beside the pit on the side it came from, never past it
            NearOrigin = 4,   // GenPlace's "near" where it was thrown from
            Fallback = 5,     // spawned on the landing cell whatever is there
        }

        public static bool LandingWithinCap(int x, int z, int originX, int originZ, int cap)
        {
            return cap <= 0 || Math.Max(Math.Abs(x - originX), Math.Abs(z - originZ)) <= cap;
        }

        /// <summary>The floor of the pit at (x, z): every open pit cell joined to it, corners included, within PitReach. Owner, by card
        /// 2026-11-22: "Always into the pit somewhere, THEN bounced out of the pit if totally full." A stack whose landing cell is
        /// taken settles on the nearest free cell of this floor, and is bounced out only when the floor holds no place for it.</summary>
        public static HashSet<long> PitAround(IKbGrid grid, int x, int z)
        {
            var seen = new HashSet<long> { Key(x, z) };
            var open = new Queue<(int x, int z)>();
            open.Enqueue((x, z));
            while (open.Count > 0)
            {
                (int cx, int cz) = open.Dequeue();
                for (int ox = -1; ox <= 1; ox++)
                {
                    for (int oz = -1; oz <= 1; oz++)
                    {
                        int nx = cx + ox, nz = cz + oz;
                        if ((nx - x) * (nx - x) + (nz - z) * (nz - z) <= PitReach * PitReach && !seen.Contains(Key(nx, nz))
                            && grid.At(nx, nz) == KbCell.Pit)
                        {
                            seen.Add(Key(nx, nz));
                            open.Enqueue((nx, nz));
                        }
                    }
                }
            }
            return seen;
        }

        /// <summary>The farthest floor cell asked for: 12.9 = the radius of GenPlace's own last "near" search ring, which never
        /// looks farther.</summary>
        public const float PitReach = 12.9f;

        private static long Key(int x, int z) => ((long)x << 32) | (uint)z;

        /// <summary>With the pit floor beside it full, a stack is set down on open ground this near its landing cell, on the side
        /// its leg came from (no farther from the leg's start than the landing cell is, so never past the pit). 2.9 = the
        /// radius of GenPlace's own second search ring (PlaceNearMiddleRadialCells is the cells within 3): near enough to read
        /// as tumbling back off the heap. The map's reading M15 counts every such landing and how far it was set down.</summary>
        public const float RimSpread = 2.9f;

        /// <summary>Leaf thrown_into_pit_falls ("falls to its floor ... never anything thrown across a pit"; false pass "the
        /// stack lands on the pit rim"). The map (reading M02) found 401 of 2,200 flights that met a pit ending on the rim or
        /// past it: the game holds one stack a cell, and GenPlace's "near" then picked any neighbour, the far rim included. A
        /// landing on a pit cell that cannot take the stack now goes to the floor of that pit, and only with that floor full to the
        /// rim on the side it came from. `wouldBump` = a Direct placement would move a resident stack (never done).</summary>
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
        /// under `place`? `cell` is the path grid's reading of (x, z) for goods. PitFloor: an open floor cell of `pit`, the pit it
        /// came down in (PitAround). NearRim: open ground within RimSpread of the landing cell and no farther from where the leg began than
        /// the landing cell is (the side it came from). Never a wall, a door, water or sandbags: GenPlace's "near" takes even those when nothing
        /// better is offered.</summary>
        public static bool PlaceAllows(KbPlace place, int x, int z, int dx, int dz, int fromX, int fromZ, KbCell cell, HashSet<long> pit = null)
        {
            float ex = x - dx, ez = z - dz;
            float d2 = ex * ex + ez * ez;
            if (place == KbPlace.PitFloor)
            {
                return cell == KbCell.Pit && pit != null && pit.Contains(Key(x, z));
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
            if (s.intoPits)
            {
                nr = StopAtCrossedPit(grid, atX, atZ, nr);
            }
            next = new KbLeg { fromX = atX, fromZ = atZ, dx = rx, dz = rz, res = nr };
            return true;
        }
    }
}
