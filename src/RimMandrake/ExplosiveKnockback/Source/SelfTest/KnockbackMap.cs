// The situation map of Explosive Knockback (RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX; instrument version below).
// It runs the SHIPPED decision (../RM_KnockbackPlan.cs over ../RM_KnockbackMath.cs) on a small model of the map and reads the
// mod's bars as properties of where every thing ends, over situations it enumerates:
//   lanes   every (thing, direction, distance, obstacle, obstacle distance, obstacle width, blast) combination, enumerated
//   spared  every spared state of the_spared beside each blast
//   rooms   seeded random storerooms: walls, doors, an open side, pit strips (some covered, some already holding a stack),
//           sandbags, shelves, closed containers, 3-25 stacks, 0-4 pawns, any blast anywhere inside; each run with both
//           tie orders of the game's "place near" search
//   cases   the mod's own scenes and the cases that used to fail, as fixed challenge cases
// The model outside the shipped code (each a stated assumption, with the game source it copies):
//   A1 a damaging blast springs every cover in its radius before the queue is flushed (FlowWorks RM_Patch_ExplosionBreaksPitCover)
//   A2 a thing landing on an open pit cell is in the pit (FlowWorks RM_Patch_PawnFlyer_LandInPit; goods rest on the floor)
//   A3 a stack lands by GenPlace: Direct when that bumps nobody, else Near the cell, else Near its origin (Verse.GenPlace,
//      TryFindPlaceSpotNear and PlaceSpotQualityAt copied: 9 cells, then radius 3, then radius 12.9; another room is Bad)
//   A4 one stack a cell, three on a shelf cell; two stacks merge only when both carry the same key and the resident is not full
//   A5 a blast and a gas burst reach what lies within their radius with no wall or closed door on the sight line
//      (Verse.DamageWorker.ExplosionCellsToHit and RM_MapComponent_Knockback.GasBurst: GenSight.LineOfSight, skipFirstCell;
//      the line is copied here). A thing standing in the wall or door cell itself is reached when its near side is seen
// NOT covered (named so nobody reads a green map as "every case"): two blasts in sequence (recovery, barrages, gas chains),
// covers wider than one cell, things that die or are destroyed by the blast, doors that open mid-flight, maps edges,
// multi-cell containers' footprints, the drawn arc, settings other than those the `settings` family flips, live save and load.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimMandrake.ExplosiveKnockback;

internal sealed class MThing
{
    public int id;
    public KbKind kind;
    public bool container, oneByOne = true;
    public float mass;
    public int x, z;
    public string key;          // goods merge only with the same key
    public bool full = true;    // a full stack absorbs nothing
    public bool dead, flying, inBed, carryingPawn, downed, animal, mech, shield, recovering;
    public int gasShovedAgo = int.MaxValue;
    public float damageTaken;
    public int stunTicks;
    public bool inPit;          // on a pit floor (under an intact cover: beneath the lid)
    public MThing rides;        // a good on a closed container's cell rides with it
    public string label;
    // outcome
    public int sx, sz;
    public bool startDeep, startInPit, reached, los, air, flew, merged;
    public KbPlan plan;
    public readonly List<(int x, int z)> route = new List<(int, int)>();
    public int bounces, placedVia;   // 0 not placed, 1 direct, 2 near the cell, 3 near the origin, 4 fallback
    public int firstLegCells;
    public bool heavyStopped, pitFloorFull, pinned, bounceMissed;
    public int legFromX, legFromZ, hitX, hitZ, hitLeft; public float hitDx, hitDz; public KbResult hitRes; public bool hitSolid;
    public (int x, int z)? contTo;
    public bool landedOnPawn, passedPawn, landedOnThing;
    public MThing boxAtStart;
    public float massAtStart;
}

internal sealed class MWorld : IKbWorld
{
    public const int Cap = 1, ShelfCap = 3;
    public readonly int W, H;
    public readonly KbCell[,] terr;
    public readonly bool[,] deep, cover, shelf;
    public readonly List<MThing> things = new List<MThing>();
    public bool reverseTies;
    public MThing self;
    private int[,] room, comp;

    public MWorld(int w, int h)
    {
        W = w; H = h;
        terr = new KbCell[w, h];
        deep = new bool[w, h];
        cover = new bool[w, h];
        shelf = new bool[w, h];
    }

    public bool In(int x, int z) => x >= 0 && z >= 0 && x < W && z < H;

    public MThing Add(MThing t)
    {
        t.id = things.Count + 1;
        t.sx = t.x; t.sz = t.z;
        things.Add(t);
        return t;
    }

    public IEnumerable<MThing> At(int x, int z) => things.Where(t => !t.air && !t.merged && t.x == x && t.z == z);

    private bool ContainerAt(int x, int z) => At(x, z).Any(t => t.container && t != self);

    // RM_MapKbGrid.At, in its order
    private sealed class G : IKbGrid
    {
        public MWorld w; public bool forPawn;
        public KbCell At(int x, int z)
        {
            if (!w.In(x, z)) return KbCell.OutOfBounds;
            KbCell t = w.terr[x, z];
            if (t == KbCell.Door) return KbCell.Door;
            if (t == KbCell.Wall) return KbCell.Wall;
            if (w.deep[x, z])
            {
                bool covered = w.cover[x, z];
                bool pawnThere = forPawn && w.At(x, z).Any(p => p.kind == KbKind.Pawn && !p.container && p != w.self && !(covered && p.inPit));
                return RM_KnockbackMath.PitCell(covered, forPawn, pawnThere);
            }
            if (t == KbCell.Partial || w.shelf[x, z] || w.ContainerAt(x, z)) return KbCell.Partial;
            if (t == KbCell.Water) return KbCell.Water;
            if (forPawn && w.At(x, z).Any(p => p.kind == KbKind.Pawn && !p.container && p != w.self)) return KbCell.Pawn;
            return KbCell.Open;
        }
    }

    public IKbGrid Grid(bool forPawn) => new G { w = this, forPawn = forPawn };
    public bool PawnAt(int x, int z) => At(x, z).Any(p => p.kind == KbKind.Pawn && !p.container);
    public bool Occupied(int x, int z) => !In(x, z) || shelf[x, z] || At(x, z).Any(t => t != self);
    public bool Superdeep(int x, int z) => In(x, z) && deep[x, z];

    // ── rooms (A3: PlaceSpotQualityAt compares rooms; doors are their own room; PassDoors reachability) ──
    private void Rooms()
    {
        if (room != null) return;
        room = new int[W, H]; comp = new int[W, H];
        int n = 0;
        for (int pass = 0; pass < 2; pass++)
        {
            int[,] lab = pass == 0 ? room : comp;
            for (int x = 0; x < W; x++) for (int z = 0; z < H; z++) lab[x, z] = 0;
            for (int x = 0; x < W; x++)
                for (int z = 0; z < H; z++)
                {
                    if (lab[x, z] != 0 || !Passable(x, z)) continue;
                    if (pass == 0 && terr[x, z] == KbCell.Door) { lab[x, z] = ++n; continue; }
                    var st = new Stack<(int, int)>();
                    st.Push((x, z)); lab[x, z] = ++n;
                    while (st.Count > 0)
                    {
                        (int cx, int cz) = st.Pop();
                        foreach ((int ax, int az) in new[] { (1, 0), (-1, 0), (0, 1), (0, -1) })
                        {
                            int nx = cx + ax, nz = cz + az;
                            if (!In(nx, nz) || lab[nx, nz] != 0 || !Passable(nx, nz)) continue;
                            if (pass == 0 && terr[nx, nz] == KbCell.Door) continue;
                            lab[nx, nz] = n; st.Push((nx, nz));
                        }
                    }
                }
        }
    }

    private bool Passable(int x, int z) => terr[x, z] != KbCell.Wall && terr[x, z] != KbCell.Water;
    public int RoomOf(int x, int z) { Rooms(); return In(x, z) ? room[x, z] : 0; }

    private static List<(int x, int z)> radial, radialRev;
    private static void Radial()
    {
        if (radial != null) return;
        var l = new List<(int x, int z)>();
        for (int x = -13; x <= 13; x++) for (int z = -13; z <= 13; z++) if (x * x + z * z <= 12.9 * 12.9) l.Add((x, z));
        radial = l.OrderBy(c => c.x * c.x + c.z * c.z).ThenBy(c => c.x).ThenBy(c => c.z).ToList();
        radialRev = l.OrderBy(c => c.x * c.x + c.z * c.z).ThenByDescending(c => c.x).ThenByDescending(c => c.z).ToList();
    }

    private int ItemCap(int x, int z) => shelf[x, z] ? ShelfCap : Cap;
    private List<MThing> ItemsAt(int x, int z, MThing t) => At(x, z).Where(h => h != t && !h.container && h.kind != KbKind.Pawn).ToList();
    private static bool Absorbs(MThing resident, MThing t) => resident.key != null && resident.key == t.key && !resident.full && resident.kind == KbKind.Item && t.kind == KbKind.Item;

    /// <summary>RM_MapComponent_Knockback.WouldBump.</summary>
    public bool WouldBump(MThing t, int x, int z)
    {
        if (!In(x, z)) return false;
        List<MThing> items = ItemsAt(x, z, t);
        return !items.Any(h => Absorbs(h, t)) && items.Count >= ItemCap(x, z);
    }

    // PlaceSpotQualityAt: 0 unusable, 1 awful, 2 bad, 3 okay, 4 perfect
    private int Quality(MThing t, int x, int z, int cx, int cz)
    {
        if (!In(x, z)) return 0;
        List<MThing> items = ItemsAt(x, z, t);
        bool stack = items.Any(h => Absorbs(h, t));
        if (!stack && items.Count >= ItemCap(x, z)) return 0;
        Rooms();
        if (room[x, z] != room[cx, cz] || room[x, z] == 0)
        {
            return comp[x, z] != 0 && comp[x, z] == comp[cx, cz] ? 2 : 1;
        }
        if (stack) return 4;
        if (terr[x, z] == KbCell.Door || At(x, z).Any(p => p.kind == KbKind.Pawn && p.downed)) return 2;
        return 4;
    }

    /// <summary>GenPlace.TryFindPlaceSpotNear.</summary>
    public bool Near(MThing t, int cx, int cz, Func<int, int, bool> allow, out int bx, out int bz)
    {
        Radial();
        List<(int x, int z)> pat = reverseTies ? radialRev : radial;
        int best = 0; bx = cx; bz = cz;
        foreach (int limit in new[] { 9, pat.Count(c => c.x * c.x + c.z * c.z <= 9), pat.Count })
        {
            for (int i = 0; i < limit; i++)
            {
                int x = cx + pat[i].x, z = cz + pat[i].z;
                if (allow != null && !allow(x, z)) continue;
                int q = Quality(t, x, z, cx, cz);
                if (q > best) { best = q; bx = x; bz = z; }
                if (best == 4) break;
            }
            if (best >= 3) return true;
        }
        return best > 0;
    }
}

internal static class KnockbackMap
{
    public const string Version = "map-6";
    private static KbRules Q = new KbRules();

    public sealed class Blast
    {
        public string name; public int cx, cz; public float radius, force; public bool gas; public int id = 7;
        public float strength = 1f;
        public KbConfig Config() => gas
            ? new KbConfig { force = 1f, ownCap = 2, impactFactor = 0f, source = "gas", scaleOwnCap = false }
            : new KbConfig { force = force };
    }

    private sealed class Ev { public double t; public int seq; public MThing th; public KbLeg leg; public int cellsLeft; public KbStop stop; public bool pawn, cont; public int toX, toZ; }

    private static int Ticks(double dist, double speed, int min) => Math.Max(min, (int)Math.Ceiling(dist / speed * 60.0));

    private static bool Los(MWorld w, int cx, int cz, int x, int z)
    {
        // Verse.GenSight.LineOfSight(start, end, map, skipFirstCell: true), copied: from cell to side neighbour, never diagonally
        bool flag = cx != x ? cx < x : cz < z;
        int dx = Math.Abs(x - cx), dz = Math.Abs(z - cz), px = cx, pz = cz, left = 1 + dx + dz, sx = x > cx ? 1 : -1, sz = z > cz ? 1 : -1;
        dx *= 4; dz *= 4;
        int err = dx / 2 - dz / 2;
        for (; left > 1; left--)
        {
            if ((px != cx || pz != cz) && (w.terr[px, pz] == KbCell.Wall || w.terr[px, pz] == KbCell.Door)) return false;
            if (err > 0 || err == 0 && flag) { px += sx; err -= dz; }
            else { pz += sz; err += dx; }
        }
        return true;
    }

    private static void BreakCover(MWorld w, int x, int z)
    {
        w.cover[x, z] = false;
        foreach (MThing t in w.At(x, z)) t.inPit = true;
    }

    private static KbFacts Facts(MWorld w, MThing t, bool gas)
    {
        MThing box = t.container ? null : w.At(t.x, t.z).FirstOrDefault(c => c.container);
        float mass = t.mass;
        if (t.container && Q.closedContainerGuard) mass += w.At(t.x, t.z).Where(g => g != t && g.kind != KbKind.Pawn && !g.container).Sum(g => g.mass);
        return new KbFacts
        {
            kind = t.kind, container = t.container, spawned = !t.air && !t.merged, thingId = t.id, x = t.x, z = t.z, mass = mass,
            dead = t.dead, flying = t.flying, inBed = t.inBed, carryingPawn = t.carryingPawn, downed = t.downed, animal = t.animal, mechanoid = t.mech,
            shieldAbsorbed = t.shield && !gas, recovering = t.recovering, gasShovedAgo = t.gasShovedAgo,
            onSuperdeep = w.deep[t.x, t.z], onCover = w.deep[t.x, t.z] && w.cover[t.x, t.z] && !t.inPit, onStorage = w.shelf[t.x, t.z] || box != null, onClosed = box != null, oneByOne = t.oneByOne,
        };
    }

    /// <summary>One blast on the model: the game side's part of a flush, the flights and the landings.</summary>
    public static void Run(MWorld w, Blast b)
    {
        foreach (MThing t in w.things)
        {
            t.startDeep = w.deep[t.x, t.z];
            t.startInPit = t.inPit || (t.startDeep && !w.cover[t.x, t.z]);
            t.inPit = t.startInPit;
            t.boxAtStart = t.container ? null : w.At(t.x, t.z).FirstOrDefault(c => c.container);
        }
        foreach (MThing t in w.things.Where(c => c.container))
            t.massAtStart = t.mass + w.At(t.x, t.z).Where(g => g != t && g.kind != KbKind.Pawn && !g.container).Sum(g => g.mass);
        if (!b.gas) // A1
        {
            for (int x = 0; x < w.W; x++) for (int z = 0; z < w.H; z++)
                if (w.cover[x, z] && Dist(x, z, b.cx, b.cz) <= b.radius && Los(w, b.cx, b.cz, x, z)) BreakCover(w, x, z);
        }
        var cands = new List<KbCandidate>();
        var reqs = new List<MThing>();
        foreach (MThing t in w.things)
        {
            double d = Dist(t.x, t.z, b.cx, b.cz);
            t.los = Los(w, b.cx, b.cz, t.x, t.z);
            t.reached = d <= b.radius && t.los;
            if (!t.reached || t.rides != null && false) continue;
            cands.Add(new KbCandidate { index = reqs.Count, kind = t.container ? KbKind.Item : t.kind, distance = (float)d });
            reqs.Add(t);
        }
        var evs = new List<Ev>();
        int seq = 0;
        KbConfig cfg = b.Config();
        var kb = new KbBlast { id = b.gas ? -3 : b.id, cx = b.cx, cz = b.cz, radius = b.radius, force = cfg.force, gas = b.gas };
        foreach (KbCandidate c in RM_KnockbackMath.Prioritise(cands, cands.Count))
        {
            MThing t = reqs[c.index];
            w.self = t;
            KbFacts f = Facts(w, t, b.gas); // a gas burst is no explosion: its requests carry no shield (GasBurst: shield = null)
            KbSettings s = KbLookup.Apply(new KbSettings { globalMultiplier = b.strength }, cfg, 6, 1f);
            t.plan = KbPlanner.Decide(f, kb, Q, s, w);
            w.self = null;
            KbPlan p = t.plan;
            t.pinned = p.act == KbAct.Blocked && t.kind != KbKind.Pawn && !t.container && Pinned(w, t, p);
            if (p.act == KbAct.LaunchPawn)
            {
                t.air = true; t.flew = true;
                t.route.AddRange(Walked(t.x, t.z, p.dx, p.dz, p.res.cellsPlanned, p.res.cellsTravelled));
                evs.Add(new Ev { t = Ticks(Dist(p.res.destX, p.res.destZ, t.x, t.z), 12, 18), seq = seq++, th = t, pawn = true, toX = p.res.destX, toZ = p.res.destZ });
            }
            else if (p.act == KbAct.ThrowGoods)
            {
                t.air = true; t.flew = true; t.firstLegCells = p.first.res.cellsTravelled;
                if (p.wallFirst) t.bounces = 1;
                Leg(w, evs, ref seq, t, p.first, 0, kb.id);
            }
            else if (p.act == KbAct.ContainerThrown)
            {
                if (Q.closedContainerGuard) foreach (MThing g in w.At(t.x, t.z).Where(g => g != t && g.kind != KbKind.Pawn && !g.container).ToList()) { g.rides = t; g.air = true; }
                t.air = true; t.flew = true;
                t.route.AddRange(Walked(t.x, t.z, p.dx, p.dz, p.planned, p.res.cellsTravelled)); t.contTo = (p.toX, p.toZ);
                t.passedPawn = t.route.TakeWhile(c => !(c.x == p.toX && c.z == p.toZ)).Any(c => w.PawnAt(c.x, c.z)); // read at takeoff
                evs.Add(new Ev { t = Ticks(Dist(p.toX, p.toZ, t.x, t.z), 14, 6), seq = seq++, th = t, cont = true, toX = p.toX, toZ = p.toZ });
            }
        }
        while (evs.Count > 0)
        {
            Ev e = evs.OrderBy(v => v.t).ThenBy(v => v.seq).First();
            evs.Remove(e);
            MThing t = e.th;
            if (e.pawn)
            {
                t.air = false; t.x = e.toX; t.z = e.toZ;
                Settle(w, t, kb.id, false);
            }
            else if (e.cont)
            {
                w.self = t;
                int ax = e.toX, az = e.toZ;
                if (!KbPlanner.ContainerCellFree(w, ax, az))
                {
                    (int x, int z)? alt = null;
                    for (int r = 1; r <= 2 && alt == null; r++)
                        for (int x = ax - r; x <= ax + r && alt == null; x++) for (int z = az - r; z <= az + r && alt == null; z++)
                            if (Dist(x, z, ax, az) <= 2.9 && w.In(x, z) && KbPlanner.ContainerCellFree(w, x, z)) alt = (x, z);
                    if (alt != null) { ax = alt.Value.x; az = alt.Value.z; } else { ax = t.sx; az = t.sz; }
                }
                w.self = null;
                t.landedOnPawn = w.PawnAt(ax, az) || t.passedPawn;
                t.landedOnThing = w.shelf[ax, az] || w.At(ax, az).Any(o => o != t);
                t.air = false; t.x = ax; t.z = az;
                foreach (MThing g in w.things.Where(g => g.rides == t)) { g.air = false; g.x = ax; g.z = az; }
            }
            else
            {
                // a flying stack's leg has ended at leg.res.dest
                int atX = e.leg.res.destX, atZ = e.leg.res.destZ;
                w.self = t;
                KbSettings s = KbLookup.Apply(new KbSettings(), null, 6, 1f); // RM_ThingFlyer_Knockback: a rebound walks on the global settings
                KbLeg next = default(KbLeg);
                bool again = !t.heavyStopped && KbPlanner.Rebound(w.Grid(false), e.stop, e.cellsLeft, t.bounces, e.leg.res, atX, atZ, e.leg.dx, e.leg.dz,
                    t.kind, t.mass, s, Q, out next);
                w.self = null;
                if (!again && !t.heavyStopped && (e.stop == KbStop.Wall || e.stop == KbStop.Door || e.stop == KbStop.OutOfBounds))
                {
                    w.self = t;
                    t.bounceMissed = !BounceBlocked(w.Grid(false), e.leg.res, atX, atZ, e.leg.dx, e.leg.dz, e.cellsLeft, t.bounces);
                    w.self = null;
                }
                if (again)
                {
                    t.bounces++;
                    Leg(w, evs, ref seq, t, next, e.t, kb.id);
                    continue;
                }
                Place(w, t, atX, atZ, b.gas ? t.plan.s.maxCells : 0);
                Settle(w, t, kb.id, true);
            }
        }
    }

    // the cells Resolve walked: the first `cells` of the PLANNED line (a shorter line is not its prefix off the eight compass rays)
    private static List<(int x, int z)> Walked(int fx, int fz, float dx, float dz, int planned, int cells)
    {
        return RM_KnockbackMath.Line(fx, fz, dx, dz, planned).Take(cells).ToList();
    }

    private static void Leg(MWorld w, List<Ev> evs, ref int seq, MThing t, KbLeg leg, double now, int explosionId)
    {
        KbResult res = leg.res;
        List<(int x, int z)> cells = Walked(leg.fromX, leg.fromZ, leg.dx, leg.dz, res.cellsPlanned, res.cellsTravelled);
        if (res.stop == KbStop.Pit && cells[cells.Count - 1] != (res.destX, res.destZ))
        {
            // The centre-to-centre flight found an open pit off the walk's rounded line.
            cells = RM_KnockbackMath.Line(leg.fromX, leg.fromZ, res.destX - leg.fromX, res.destZ - leg.fromZ, res.cellsTravelled);
        }
        KbStop stop = res.stop;
        int left = res.cellsPlanned - res.cellsTravelled;
        // RM_ThingFlyer_Knockback.HeavyHit: a heavy stack reaching a standing person's cell stops there
        for (int i = 0; i < cells.Count; i++)
        {
            MThing person = w.At(cells[i].x, cells[i].z).FirstOrDefault(p => p.kind == KbKind.Pawn && !p.container && !p.dead);
            if (RM_KnockbackMath.HeavyKnock(true, t.kind, person != null, t.mass, 10f, 2f, 5f, 0.5f, 30, out float damage, out int stun, explosionId))
            {
                person.damageTaken += damage; person.stunTicks = stun;
                cells = cells.Take(i + 1).ToList();
                res.destX = cells[i].x; res.destZ = cells[i].z;
                stop = KbStop.Pawn; left = 0; t.heavyStopped = true;
                break;
            }
        }
        t.route.AddRange(cells);
        leg.res = res;
        t.legFromX = leg.fromX; t.legFromZ = leg.fromZ;
        t.hitSolid = stop == KbStop.Wall || stop == KbStop.Door || stop == KbStop.OutOfBounds;
        t.hitX = res.destX; t.hitZ = res.destZ; t.hitLeft = left; t.hitDx = leg.dx; t.hitDz = leg.dz; t.hitRes = res;
        evs.Add(new Ev { t = now + Ticks(Dist(res.destX, res.destZ, leg.fromX, leg.fromZ), 14, 6), seq = seq++, th = t, leg = leg, cellsLeft = left, stop = stop });
    }

    /// <summary>RM_MapComponent_Knockback.PlaceLanding on the model (A3): the shipped order, each through the model's GenPlace.</summary>
    private static void Place(MWorld w, MThing t, int dx, int dz, int landingCap)
    {
        bool WithinCap(int x, int z) => KbPlanner.LandingWithinCap(x, z, t.sx, t.sz, landingCap);
        bool destWithinCap = WithinCap(dx, dz);
        int px = dx, pz = dz;
        bool deep = w.deep[dx, dz];
        foreach (KbPlanner.KbPlace place in KbPlanner.LandingOrder(w.WouldBump(t, dx, dz), deep))
        {
            t.placedVia = (int)place + 1;
            if (place == KbPlanner.KbPlace.Direct && !destWithinCap) continue;
            if (place == KbPlanner.KbPlace.Direct || place == KbPlanner.KbPlace.Fallback)
            {
                (px, pz) = destWithinCap ? (dx, dz) : (t.sx, t.sz);
                break;
            }
            int cx = place == KbPlanner.KbPlace.NearOrigin ? t.sx : dx, cz = place == KbPlanner.KbPlace.NearOrigin ? t.sz : dz;
            IKbGrid g = w.Grid(false);
            HashSet<long> pit = place == KbPlanner.KbPlace.PitFloor ? KbPlanner.PitAround(g, dx, dz) : null;
            Func<int, int, bool> allow = (x, z) => w.In(x, z) && WithinCap(x, z)
                && KbPlanner.PlaceAllows(place, x, z, dx, dz, t.legFromX, t.legFromZ, g.At(x, z), pit);
            if (w.Near(t, cx, cz, allow, out px, out pz)) break;
        }
        t.pitFloorFull = deep && t.placedVia > (int)KbPlanner.KbPlace.PitFloor + 1;
        t.air = false; t.x = px; t.z = pz;
    }

    /// <summary>What the landing does next: an open pit takes it (A2); a blast-thrown landing breaks a cover.</summary>
    private static void Settle(MWorld w, MThing t, int explosionId, bool goods)
    {
        if (!w.deep[t.x, t.z]) return;
        if (!w.cover[t.x, t.z]) { t.inPit = true; return; }
        if (RM_KnockbackMath.LandingBreaksCover(t.kind, true, false, explosionId)) BreakCover(w, t.x, t.z);
    }

    public static double Dist(int x, int z, int cx, int cz) => Math.Sqrt((double)(x - cx) * (x - cx) + (double)(z - cz) * (z - cz));

    // ════════════════════════ the bars, read off the end state ════════════════════════
    public sealed class Tally { public long applicable, violations, roomApplicable, roomViolations; public readonly List<string> examples = new List<string>(); public int roomExamples; }
    public static readonly SortedDictionary<string, Tally> Bars = new SortedDictionary<string, Tally>();
    public static readonly SortedDictionary<string, long[]> Regions = new SortedDictionary<string, long[]>();
    public static readonly string[] BarIds =
    {
        "M01 the_spared: a spared thing stays on its cell",
        "M02 thrown_into_pit_falls: a thing whose flight meets a pit ends on a pit floor, never on the rim or beyond",
        "M03 thrown_into_pit_falls: nothing a blast threw rests on an intact cover",
        "M04 every_good_moves: a loose good the blast reaches with a throw of a cell or more leaves its cell",
        "M05 rest: nothing comes to rest in a wall, a door, deep water or on sandbags",
        "M06 closed_container_holds: a container never rests in a pit, on a person or past one, and its goods stay with it",
        "M07 blast_breaks_pit_cover: a gas burst leaves every cover whole, and a pawn it shoves onto one stands on it",
        "M08 gas_goes_clump_by_clump: a gas shove moves a pawn one cell at most",
        "M09 reach: nothing moves that the blast could not reach (a wall or closed door between)",
        "M10 no wall crossed: a thing rests in the room its flight ended in",
        "M11 nothing lost: every thing is on the map at the end",
        "M12 wall_stops_dead / pawn_hits_pawn_stops: a pawn stopped by a wall, door or pawn rests on the cell before it",
        "M13 goods_arc_spin_rebound: a good that hits a wall or door with speed to spare bounces off it",
        "M15 thrown_into_pit_falls, the full pit: with every floor cell beside its landing taken, a stack is set down on the side it came from, within three cells of where it came down",
        "M16 (count only) goods held where they lie by the map itself: deep water behind them, or no line to rest on in any of the eight directions",
        "M17 (count only) full-pit landings with no free ground on the side they came from either: put back beside where they were thrown from",
        "M18 shield_belt_holds: a burning gas clump's one-cell shove still moves a belted pawn",
        "M19 closed_container_holds: what lay on a closed container's cell ends on that container's cell",
        "M20 closed_container_holds: a container bigger than one cell or over the container mass limit is never thrown",
        "M21 people keep the kernel: a pawn never flies farther than the kernel's throw for its mass, distance and blast",
        "M14 closed_container_holds: a thrown container comes down on a cell of the path its throw walked",
    };

    private static Tally T(string id)
    {
        string key = BarIds.First(b => b.StartsWith(id + " "));
        if (!Bars.TryGetValue(key, out Tally t)) Bars[key] = t = new Tally();
        return t;
    }

    private static void Read(string id, bool applies, bool ok, string region, Func<string> example)
    {
        if (!applies) return;
        Tally t = T(id);
        t.applicable++;
        if (region == null) { t.roomApplicable++; if (!ok) t.roomViolations++; }
        if (region != null)
        {
            string rk = id + " | " + region;
            if (!Regions.TryGetValue(rk, out long[] r)) Regions[rk] = r = new long[2];
            r[0]++;
            if (!ok) r[1]++;
        }
        if (ok) return;
        t.violations++;
        if (t.examples.Count < 2 || region == null && t.roomExamples++ < 3) t.examples.Add(example());
    }

    public static string Draw(MWorld w, Blast b, MThing focus)
    {
        var sb = new StringBuilder();
        int x0 = Math.Max(0, Math.Min(b.cx, focus?.sx ?? b.cx) - 9), x1 = Math.Min(w.W - 1, Math.Max(b.cx, focus?.sx ?? b.cx) + 9);
        int z0 = Math.Max(0, b.cz - 7), z1 = Math.Min(w.H - 1, b.cz + 7);
        for (int z = z1; z >= z0; z--)
        {
            for (int x = x0; x <= x1; x++)
            {
                char ch = w.terr[x, z] == KbCell.Wall ? '#' : w.terr[x, z] == KbCell.Door ? 'D' : w.terr[x, z] == KbCell.Water ? '~'
                    : w.deep[x, z] ? (w.cover[x, z] ? 'c' : 'o') : w.terr[x, z] == KbCell.Partial ? 's' : w.shelf[x, z] ? 'h' : '.';
                if (x == b.cx && z == b.cz) ch = '*';
                if (focus != null && x == focus.sx && z == focus.sz) ch = 'A';
                if (focus != null && x == focus.x && z == focus.z && !(focus.x == focus.sx && focus.z == focus.sz)) ch = 'B';
                sb.Append(ch);
            }
            sb.Append('\n');
        }
        return sb.ToString();
    }

    private static string Ex(string scene, MWorld w, Blast b, MThing t, string what)
    {
        return scene + ": " + t.label + " (" + t.sx + "," + t.sz + ")->(" + t.x + "," + t.z + ") " + (t.plan == null ? "no plan" : t.plan.act + (t.plan.reason != null ? ":" + t.plan.reason : "")
            + " cells " + t.plan.cells + " dir (" + t.plan.dx + "," + t.plan.dz + ") stop " + t.plan.res.stop + " block (" + t.plan.res.blockX + "," + t.plan.res.blockZ + ") from (" + t.plan.res.blockFromX + "," + t.plan.res.blockFromZ + ")") + " placed " + t.placedVia + " bounces " + t.bounces + " inPit " + t.inPit + " | " + what
            + "\n" + Draw(w, b, t);
    }

    // leaf the_spared, recovery_immunity, shield_belt_holds and the gas shove's "at most once every 2 seconds"
    private static bool Spared(MThing t, Blast b) => t.kind == KbKind.Pawn && !t.container
        ? (t.mass > 150f || t.startDeep || t.carryingPawn || t.flying || t.inBed || t.recovering || t.shield && !b.gas || b.gas && t.gasShovedAgo < 120)
        : !t.container && (t.mass > 75f || t.startDeep);

    // the rim (the_spared: "a thing at the rim whose throw is under one cell"): the kernel's own throw, computed apart from the plan
    private static bool UnderOneCell(MThing t, Blast b)
    {
        if (t.container) return false;
        KbSettings s = KbLookup.Apply(new KbSettings(), b.Config(), 6, 1f);
        return RM_KnockbackMath.ThrowCells((float)Dist(t.sx, t.sz, b.cx, b.cz), b.radius, b.Config().force, t.mass, s) < 1;
    }

    public static void Judge(string scene, MWorld w, Blast b, string region)
    {
        foreach (MThing t in w.things)
        {
            bool moved = t.x != t.sx || t.z != t.sz;
            KbPlan p = t.plan;
            bool pawn = t.kind == KbKind.Pawn && !t.container, good = !pawn && !t.container;
            Func<string, Func<string>> ex = what => () => Ex(scene, w, b, t, what);
            Read("M11", true, !t.air && w.In(t.x, t.z), region, ex("lost"));
            Read("M01", t.reached && t.rides == null && (Spared(t, b) || UnderOneCell(t, b)), !moved && !t.flew, region, ex("a spared thing moved"));
            Read("M18", b.gas && pawn && t.shield && t.reached && !Spared(t, b) && !UnderOneCell(t, b) && p != null && p.act != KbAct.Blocked, t.flew, region, ex("a belted pawn was not shoved by burning gas"));
            Read("M09", !t.reached, !moved || t.rides != null && t.rides.reached, region, ex("moved though the blast could not reach it"));
            // closed_container_holds, read apart from the plan: what lay on a closed container's cell ends on that container's cell
            Read("M19", good && t.boxAtStart != null && Q.closedContainerGuard, t.boxAtStart != null && t.x == t.boxAtStart.x && t.z == t.boxAtStart.z, region, ex("a good left its closed container"));
            Read("M20", t.container && (!t.oneByOne || t.massAtStart > 250f), !moved, region, ex("a container bigger than one cell or over the container mass limit was thrown"));
            if (pawn && t.flew)
            {
                KbSettings ks = KbLookup.Apply(new KbSettings(), b.Config(), 6, 1f);
                int kernel = Math.Min(b.gas ? 1 : 99, RM_KnockbackMath.ThrowCells((float)Dist(t.sx, t.sz, b.cx, b.cz), b.radius, b.Config().force, t.mass, ks));
                Read("M21", true, t.route.Count <= kernel, region, ex("a pawn flew " + t.route.Count + " cells, the kernel's throw is " + kernel));
            }
            if (t.rides != null)
            {
                Read("M06", true, t.x == t.rides.x && t.z == t.rides.z, region, ex("a container's good left it"));
                continue;
            }
            if (!t.flew && !(p != null && p.act == KbAct.Blocked)) continue;
            int pitAt = t.route.FindIndex(c => w.deep[c.x, c.z]);
            bool restDeep = w.deep[t.x, t.z];
            if (!t.container)
            {
                (int lx0, int lz0) = t.route.Count > 0 ? t.route[t.route.Count - 1] : (t.sx, t.sz);
                bool nearSide = t.pitFloorFull && !restDeep && Dist(t.x, t.z, t.legFromX, t.legFromZ) <= Dist(lx0, lz0, t.legFromX, t.legFromZ);
                bool backHome = t.placedVia == (int)KbPlanner.KbPlace.NearOrigin + 1;
                Read("M17", pitAt >= 0 && t.pitFloorFull && backHome, true, region, ex(""));
                Read("M15", pitAt >= 0 && t.pitFloorFull && !backHome, nearSide && Dist(t.x, t.z, lx0, lz0) <= 2.9, region,
                    ex("the pit floor was full and it was not set down beside the pit on the side it came from"));
                Read("M02", pitAt >= 0 && !t.pitFloorFull, restDeep && (t.inPit || b.gas && w.cover[t.x, t.z]), region, ex("its flight met a pit at step " + (pitAt + 1) + " and it rests " + (restDeep ? "on a cover" : "off the pit")));
                Read("M03", !b.gas && t.flew && restDeep, !w.cover[t.x, t.z] && t.inPit, region, ex("rests on an intact cover"));
            }
            if (good)
            {
                if (region == null && p.act == KbAct.Blocked) { string rk = "M04 rooms by stop | " + p.res.stop; if (!Regions.TryGetValue(rk, out long[] rr)) Regions[rk] = rr = new long[2]; rr[0]++; rr[1]++; }
                bool pinned = t.pinned;
                Read("M16", pinned, true, region, ex(""));
                Read("M04", t.reached && p != null && p.kernelCells >= 1 && (p.act == KbAct.ThrowGoods || p.act == KbAct.Blocked) && !pinned, t.flew, region,
                    ex("the blast reached it with a throw of " + p.cells + " cells and it sat still (" + p.res.stop + ") " + Dbg));
                bool solid = p.res.stop == KbStop.Wall || p.res.stop == KbStop.Door || p.res.stop == KbStop.OutOfBounds;
                int back = RM_KnockbackMath.ReboundCells(p.res.cellsPlanned - p.res.cellsTravelled, Q.goodsReboundKeepPercent);
                Read("M13", t.bounceMissed, false, region,
                    ex("its last leg ended on a wall with " + t.hitLeft + " cells left, a bounce was possible and it did not bounce"));
                Read("M13", solid && back >= 1 && !t.heavyStopped, t.bounces >= 1 || pinned || t.flew, region,
                    ex("hit " + p.res.stop + " with " + (p.res.cellsPlanned - p.res.cellsTravelled) + " cells left (" + back + " after the loss) and did not bounce"));
            }
            KbCell rest = w.terr[t.x, t.z];
            // the game's "place near" may set a stack on sandbags or a shelf, as a hauler may; a flight never ends on them
            bool perch = rest == KbCell.Partial || w.shelf[t.x, t.z];
            Read("M05", t.flew, rest != KbCell.Wall && rest != KbCell.Door && rest != KbCell.Water && !(perch && (!good || t.placedVia <= 1)), region, ex("rests on " + rest));
            if (t.container)
            {
                Read("M14", t.flew && t.contTo != null, t.route.Contains(t.contTo.Value), region, ex("planned to rest at " + t.contTo + ", a cell its walk never read"));
                Read("M06", true, !w.deep[t.x, t.z] && !t.landedOnPawn && !t.landedOnThing && rest == KbCell.Open, region, ex("a container rests in a pit, on or past a person, on another thing, or off open ground"));
            }
            if (b.gas)
            {
                Read("M07", pawn && t.flew && restDeep && w.cover[t.x, t.z], !t.inPit, region, ex("shoved onto a cover and fell"));
                Read("M08", pawn && t.flew, Math.Max(Math.Abs(t.x - t.sx), Math.Abs(t.z - t.sz)) <= 1, region, ex("a gas shove of more than one cell"));
            }
            if (t.flew && t.route.Count > 0)
            {
                (int lx, int lz) = t.route[t.route.Count - 1];
                Read("M10", true, w.RoomOf(t.x, t.z) == w.RoomOf(lx, lz) || t.container, region, ex("landed at (" + lx + "," + lz + ") room " + w.RoomOf(lx, lz) + " and was placed in room " + w.RoomOf(t.x, t.z)));
            }
            if (pawn && p != null && (p.res.stop == KbStop.Wall || p.res.stop == KbStop.Door || p.res.stop == KbStop.Pawn))
            {
                List<(int x, int z)> full = RM_KnockbackMath.Line(t.sx, t.sz, p.dx, p.dz, p.res.cellsPlanned);
                (int ex0, int ez0) = p.res.cellsTravelled == 0 ? (t.sx, t.sz) : full[p.res.cellsTravelled - 1];
                Read("M12", true, t.x == ex0 && t.z == ez0, region, ex("stopped by " + p.res.stop + " but rests elsewhere"));
            }
        }
        for (int x = 0; x < w.W; x++) for (int z = 0; z < w.H; z++)
            if (b.gas) Read("M07", w.deep[x, z] && startCover != null && startCover[x, z], w.cover[x, z], region, () => scene + ": a gas burst broke the cover at (" + x + "," + z + ")");
    }

    private static bool[,] startCover;

    // an independent walker: can a good walking `cells` from (fx, fz) along (dx, dz) come to rest on a cell other than its own?
    private static bool CanRest(IKbGrid g, int fx, int fz, float dx, float dz, int cells)
    {
        int px = fx, pz = fz;
        foreach ((int x, int z) in RM_KnockbackMath.Line(fx, fz, dx, dz, cells))
        {
            KbCell c = g.At(x, z);
            Func<KbCell, bool> solid = k => k == KbCell.Wall || k == KbCell.Door || k == KbCell.OutOfBounds;
            if (solid(c) || c == KbCell.Water) return false;
            if (x != px && z != pz && (solid(g.At(x, pz)) || solid(g.At(px, z)))) return false;
            if (c != KbCell.Partial) return true;
            px = x; pz = z;
        }
        return false;
    }

    // a bounce is impossible when the throw keeps no cell after the loss, or the bounce's walk cannot come to rest anywhere
    private static bool BounceBlocked(IKbGrid g, KbResult hit, int atX, int atZ, float dx, float dz, int left, int bounces)
    {
        int back = RM_KnockbackMath.ReboundCells(left, Q.goodsReboundKeepPercent);
        if (back < 1 || bounces >= Q.maxBounces) return true;
        RM_KnockbackMath.Reflect(g, hit, dx, dz, out float rx, out float rz);
        return !CanRest(g, atX, atZ, rx, rz, back);
    }

    // the only goods a blast reaches and may leave lying (read independently of the plan's own branches): deep water is the
    // first thing on its line ("stop short of deep water"); or no line from its cell, in any of the eight directions, comes
    // to rest within its throw plus HopExtraCells (walls, doors, the edge or sandbags on every side). Leaf every_good_moves
    // spares nothing else: a good with a wall right behind it and a one-cell throw, or a bounce whose reflected line is
    // blocked, still leaves its cell (blind cycle 6, RIMMANDRAKE_MOVE_KNOCKBACK_GOODS_PINNED_AGAINST_WALLS_SHELVES).
    public static string Dbg = "";
    private static bool Pinned(MWorld w, MThing t, KbPlan p)
    {
        w.self = t;
        IKbGrid g = w.Grid(false);
        try
        {
            if (p.res.stop == KbStop.Water) return true;
            for (int ddx = -1; ddx <= 1; ddx++)
                for (int ddz = -1; ddz <= 1; ddz++)
                {
                    if (ddx == 0 && ddz == 0) continue;
                    for (int n = Math.Max(1, p.cells); n <= p.cells + KbPlanner.HopExtraCells; n++)
                    {
                        if (CanRest(g, t.sx, t.sz, ddx, ddz, n)) { Dbg = "free line (" + ddx + "," + ddz + ") n " + n; return false; }
                    }
                }
            return true;
        }
        finally { w.self = null; }
    }

    public static void RunJudge(string scene, MWorld w, Blast b, string region)
    {
        startCover = (bool[,])w.cover.Clone();
        Run(w, b);
        Judge(scene, w, b, region);
    }

    // ════════════════════════ situations ════════════════════════
    private static readonly (int x, int z)[] Dirs =
    {
        (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1),
        (2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2),
    };

    public static readonly Blast[] Blasts =
    {
        new Blast { name = "bomb r2.9", radius = 2.9f, force = 1f },
        new Blast { name = "bomb r5.9", radius = 5.9f, force = 1f },
        new Blast { name = "bomb r2.9 x2 damage", radius = 2.9f, force = 2f },
        new Blast { name = "fire r2.9 half", radius = 2.9f, force = 0.5f },
        new Blast { name = "gas clump r1.9", radius = 1.9f, force = 1f, gas = true },
    };

    private static MThing Make(string type)
    {
        switch (type)
        {
            case "colonist 70kg": return new MThing { kind = KbKind.Pawn, mass = 70f, label = type };
            case "rat 3kg": return new MThing { kind = KbKind.Pawn, mass = 3f, animal = true, label = type };
            case "muffalo 140kg": return new MThing { kind = KbKind.Pawn, mass = 140f, animal = true, label = type };
            case "stack 1kg": return new MThing { kind = KbKind.Item, mass = 1f, label = type };
            case "stack 20kg": return new MThing { kind = KbKind.Item, mass = 20f, label = type };
            case "stack 74kg": return new MThing { kind = KbKind.Item, mass = 74f, label = type };
            case "corpse 60kg": return new MThing { kind = KbKind.Corpse, mass = 60f, label = type };
            case "locker 30kg": return new MThing { kind = KbKind.Item, container = true, mass = 30f, label = type };
        }
        throw new Exception(type);
    }

    public static readonly string[] Types = { "colonist 70kg", "rat 3kg", "muffalo 140kg", "stack 1kg", "stack 20kg", "stack 74kg", "corpse 60kg", "locker 30kg" };
    public static readonly string[] Obstacles = { "open ground", "wall", "closed door", "sandbags", "deep water", "open pit", "covered pit", "standing pawn", "occupied cell", "open pit holding a stack", "open pit, wall behind" };

    public static long LaneCases, SparedCases, RoomCases, FixedCases;

    private static void Lanes()
    {
        const int C = 15;
        foreach (string type in Types)
            foreach (Blast b0 in Blasts)
                foreach ((int dx, int dz) in Dirs)
                    for (int n = 1; n <= 3; n++)
                    {
                        int tx = C + dx * n, tz = C + dz * n;
                        if (Dist(tx, tz, C, C) > b0.radius) continue;
                        List<(int x, int z)> path = RM_KnockbackMath.Line(tx, tz, dx, dz, 8);
                        foreach (string ob in Obstacles)
                            for (int k = 1; k <= 7; k++)
                                for (int wide = 0; wide <= 1; wide++)
                                {
                                    if (ob == "open ground" && (k > 1 || wide > 0)) continue;
                                    if ((ob == "standing pawn" || ob == "occupied cell") && wide > 0) continue;
                                    var w = new MWorld(31, 31);
                                    var b = new Blast { name = b0.name, cx = C, cz = C, radius = b0.radius, force = b0.force, gas = b0.gas };
                                    MThing t = Make(type); t.x = tx; t.z = tz;
                                    var cells = new List<(int x, int z)> { path[k - 1] };
                                    if (wide == 1)
                                    {
                                        for (int ax = -1; ax <= 1; ax++) for (int az = -1; az <= 1; az++)
                                        {
                                            (int x, int z) c = (path[k - 1].x + ax, path[k - 1].z + az);
                                            bool before = (c.x == tx && c.z == tz) || (c.x == C && c.z == C) || path.Take(k - 1).Contains(c)
                                                || Dist(c.x, c.z, C, C) < Dist(path[k - 1].x, path[k - 1].z, C, C) - 0.01;
                                            if (!before && !cells.Contains(c)) cells.Add(c);
                                        }
                                    }
                                    foreach ((int x, int z) in cells)
                                    {
                                        switch (ob)
                                        {
                                            case "wall": w.terr[x, z] = KbCell.Wall; break;
                                            case "closed door": w.terr[x, z] = KbCell.Door; break;
                                            case "sandbags": w.terr[x, z] = KbCell.Partial; break;
                                            case "deep water": w.terr[x, z] = KbCell.Water; break;
                                            case "open pit": w.deep[x, z] = true; break;
                                            case "covered pit": w.deep[x, z] = true; w.cover[x, z] = true; break;
                                            case "standing pawn": w.Add(new MThing { kind = KbKind.Pawn, mass = 200f, x = x, z = z, label = "bystander 200kg" }); break;
                                            case "occupied cell": w.Add(new MThing { kind = KbKind.Item, mass = 90f, x = x, z = z, label = "resident stack 90kg" }); break;
                                            case "open pit holding a stack": w.deep[x, z] = true; w.Add(new MThing { kind = KbKind.Item, mass = 5f, x = x, z = z, inPit = true, label = "stack on the pit floor" }); break;
                                            case "open pit, wall behind": w.deep[x, z] = true; break;
                                        }
                                    }
                                    if (ob == "open pit, wall behind")
                                    {
                                        foreach ((int x, int z) in cells)
                                            for (int ax = -1; ax <= 1; ax++) for (int az = -1; az <= 1; az++)
                                            {
                                                int nx = x + ax, nz = z + az;
                                                if (!w.deep[nx, nz] && Dist(nx, nz, C, C) > Dist(x, z, C, C) + 0.01) w.terr[nx, nz] = KbCell.Wall;
                                            }
                                    }
                                    w.Add(t);
                                    LaneCases++;
                                    string scene = "lane " + type + " | " + b.name + " | dir (" + dx + "," + dz + ") x" + n + " | " + ob + " at step " + k + (wide == 1 ? " wide" : "");
                                    RunJudge(scene, w, b, type + " | " + ob + " | " + (b.gas ? "gas" : "blast"));
                                }
                    }
    }

    private static void SparedLanes()
    {
        const int C = 12;
        var states = new (string name, Action<MThing, MWorld> set)[]
        {
            ("thrumbo 400kg", (t, w) => t.mass = 400f),
            ("carrying a pawn", (t, w) => t.carryingPawn = true),
            ("airborne", (t, w) => t.flying = true),
            ("in bed", (t, w) => t.inBed = true),
            ("just landed, recovering", (t, w) => t.recovering = true),
            ("shield belt absorbed it", (t, w) => t.shield = true),
            ("shoved by gas one second ago", (t, w) => t.gasShovedAgo = 60),
            ("on a pit floor", (t, w) => { w.deep[t.x, t.z] = true; t.inPit = true; }),
            ("beneath a cover", (t, w) => { w.deep[t.x, t.z] = true; w.cover[t.x, t.z] = true; t.inPit = true; }),
            ("stack 80kg", (t, w) => { t.kind = KbKind.Item; t.mass = 80f; }),
            ("stack on a pit floor", (t, w) => { t.kind = KbKind.Item; t.mass = 5f; w.deep[t.x, t.z] = true; t.inPit = true; }),
            ("corpse on a pit floor", (t, w) => { t.kind = KbKind.Corpse; t.mass = 60f; w.deep[t.x, t.z] = true; t.inPit = true; }),
            ("corpse 400kg", (t, w) => { t.kind = KbKind.Corpse; t.mass = 400f; }),
        };
        foreach (var st in states)
            foreach (Blast b0 in Blasts)
                foreach ((int dx, int dz) in Dirs)
                    for (int n = 0; n <= 2; n++)
                    {
                        int tx = C + dx * n, tz = C + dz * n;
                        if (Dist(tx, tz, C, C) > b0.radius) continue;
                        var w = new MWorld(25, 25);
                        var b = new Blast { name = b0.name, cx = C, cz = C, radius = b0.radius, force = b0.force, gas = b0.gas };
                        var t = new MThing { kind = KbKind.Pawn, mass = 70f, x = tx, z = tz, label = st.name };
                        st.set(t, w);
                        w.Add(t);
                        SparedCases++;
                        RunJudge("spared " + st.name + " | " + b.name + " | (" + dx * n + "," + dz * n + ")", w, b, st.name + " | spared | " + (b.gas ? "gas" : "blast"));
                    }
    }

    private static void Rooms(int count, int seed0)
    {
        float[] masses = { 0.5f, 2f, 8f, 15f, 40f, 74f, 90f };
        for (int i = 0; i < count; i++)
        {
            for (int tie = 0; tie <= 1; tie++)
            {
                var r = new Random(seed0 + i);
                var w = new MWorld(27, 27) { reverseTies = tie == 1 };
                int rw = r.Next(5, 12), rh = r.Next(5, 12), x0 = 13 - rw / 2, z0 = 13 - rh / 2, x1 = x0 + rw - 1, z1 = z0 + rh - 1;
                int open = r.Next(10) < 3 ? r.Next(4) : -1;
                for (int x = x0 - 1; x <= x1 + 1; x++) for (int z = z0 - 1; z <= z1 + 1; z++)
                {
                    bool edge = x < x0 || x > x1 || z < z0 || z > z1;
                    if (!edge) continue;
                    bool side = open == 0 && z > z1 || open == 1 && z < z0 || open == 2 && x > x1 || open == 3 && x < x0;
                    if (!side || x < x0 && z < z0 || x > x1 && z > z1 || x < x0 && z > z1 || x > x1 && z < z0) w.terr[x, z] = KbCell.Wall;
                }
                for (int d = r.Next(3); d > 0; d--)
                {
                    int x = r.Next(x0, x1 + 1), z = r.Next(2) == 0 ? z0 - 1 : z1 + 1;
                    if (w.terr[x, z] == KbCell.Wall) w.terr[x, z] = KbCell.Door;
                }
                var free = new List<(int x, int z)>();
                for (int x = x0; x <= x1; x++) for (int z = z0; z <= z1; z++) free.Add((x, z));
                Func<(int x, int z)> take = () => { int j = r.Next(free.Count); var c = free[j]; free.RemoveAt(j); return c; };
                if (r.Next(2) == 0)
                {
                    int pw = r.Next(1, 3), pl = r.Next(2, 6), px = r.Next(x0 - 1, x1), pz = r.Next(z0 - 1, z1);
                    bool horiz = r.Next(2) == 0;
                    for (int a = 0; a < pl; a++) for (int c = 0; c < pw; c++)
                    {
                        int x = px + (horiz ? a : c), z = pz + (horiz ? c : a);
                        if (!w.In(x, z) || w.terr[x, z] != KbCell.Open) continue;
                        w.deep[x, z] = true;
                        w.cover[x, z] = r.Next(10) < 3;
                        free.Remove((x, z));
                        if (r.Next(10) < 2) w.Add(new MThing { kind = KbKind.Item, mass = 5f, x = x, z = z, inPit = true, label = "stack on the pit floor", key = "floor" + x + "_" + z });
                    }
                }
                for (int sgs = r.Next(4); sgs > 0 && free.Count > 0; sgs--) { var c = take(); w.terr[c.x, c.z] = KbCell.Partial; }
                for (int sh = r.Next(4); sh > 0 && free.Count > 0; sh--)
                {
                    var c = take(); w.shelf[c.x, c.z] = true;
                    for (int g = r.Next(1, 3); g > 0; g--) w.Add(new MThing { kind = KbKind.Item, mass = masses[r.Next(5)], x = c.x, z = c.z, label = "shelf stack" });
                }
                for (int bx = r.Next(3); bx > 0 && free.Count > 0; bx--)
                {
                    var c = take();
                    bool big = r.Next(4) == 0;
                    w.Add(new MThing { kind = KbKind.Item, container = true, mass = r.Next(3) == 0 ? 300f : 30f, oneByOne = !big, x = c.x, z = c.z, label = big ? "2x1 locker" : "locker" });
                    for (int g = r.Next(3); g > 0; g--) w.Add(new MThing { kind = KbKind.Item, mass = masses[r.Next(4)], x = c.x, z = c.z, label = "locker stack" });
                }
                for (int g = r.Next(3, 26); g > 0 && free.Count > 0; g--)
                {
                    var c = take();
                    bool steel = r.Next(10) < 3;
                    var th = new MThing { kind = r.Next(12) == 0 ? KbKind.Corpse : KbKind.Item, mass = masses[r.Next(masses.Length)], x = c.x, z = c.z, label = "stack" };
                    if (steel && th.kind == KbKind.Item) { th.key = "steel"; th.full = r.Next(2) == 0; th.mass = 10f; th.label = "steel stack"; }
                    th.label += " " + th.mass + "kg";
                    w.Add(th);
                }
                for (int pn = r.Next(5); pn > 0 && free.Count > 0; pn--)
                {
                    var c = take();
                    var th = new MThing { kind = KbKind.Pawn, mass = r.Next(8) == 0 ? 200f : (r.Next(6) == 0 ? 3f : 70f), x = c.x, z = c.z, label = "pawn" };
                    int st = r.Next(20);
                    if (st == 0) th.inBed = true; else if (st == 1) th.carryingPawn = true; else if (st == 2) th.shield = true; else if (st == 3) th.recovering = true; else if (st == 4) th.downed = true;
                    th.label += " " + th.mass + "kg";
                    w.Add(th);
                }
                Blast b0 = Blasts[r.Next(Blasts.Length)];
                var b = new Blast { name = b0.name, cx = r.Next(x0, x1 + 1), cz = r.Next(z0, z1 + 1), radius = b0.radius, force = b0.force, gas = b0.gas };
                if (w.terr[b.cx, b.cz] != KbCell.Open) continue;
                RoomCases++;
                RunJudge("room seed " + (seed0 + i) + (tie == 1 ? " (ties reversed)" : "") + " | " + b.name + " at (" + b.cx + "," + b.cz + ")", w, b, null);
            }
        }
    }

    // ════════════════════════ the mod's own scenes and the cases that used to fail ════════════════════════
    public static int CasesRun, CasesFailed;
    private static void Case(string name, bool ok, string detail = "")
    {
        CasesRun++;
        if (ok) return;
        CasesFailed++;
        Console.WriteLine("CASE FAILED " + name + " " + detail);
    }

    private static string Where(MThing t) => "(" + t.x + "," + t.z + ")" + (t.inPit ? " in pit" : "");

    private static void Cases()
    {
        Blast Bomb(int x, int z, float r = 2.9f) => new Blast { name = "bomb", cx = x, cz = z, radius = r, force = 1f };
        Blast Gas(int x, int z) => new Blast { name = "gas", cx = x, cz = z, radius = 1.9f, force = 1f, gas = true };
        MThing Col(MWorld w, int x, int z) => w.Add(new MThing { kind = KbKind.Pawn, mass = 70f, x = x, z = z, label = "colonist" });
        MThing Stack(MWorld w, int x, int z, float m = 5f, string key = null) => w.Add(new MThing { kind = KbKind.Item, mass = m, x = x, z = z, label = "stack", key = key });
#if RM_KB_CARRIER_TEST
        {
            Blast mortar = Bomb(8, 9); mortar.strength = 3f;
            var w = new MWorld(30, 30);
            w.terr[14, 11] = KbCell.Wall;
            MThing control = Stack(w, 10, 10, 1f);
            Run(w, mortar);
            KbLeg clear = control.plan.first;
            Case("mortar control: the flight to (16,13) clears the wall", clear.res.destX == 16 && clear.res.destZ == 13
                && !new GoodsFlightProbe().Samples(clear).Any(p => p.cell == (14, 11)), Where(control));
            w = new MWorld(30, 30);
            w.terr[14, 11] = KbCell.Wall; w.deep[15, 12] = true;
            MThing goods = Stack(w, 10, 10, 1f);
            Run(w, mortar);
            var path = new GoodsFlightProbe().Samples(goods.plan.first).ToList();
            int wallTick = path.FindIndex(p => p.cell == (14, 11)) + 1;
            var end = path.Last();
            Case("diagonal pit flight clears the wall", goods.inPit && goods.x == 15 && goods.z == 12
                && end.cell == (15, 12) && end.x == 15f && end.z == 12.75f && wallTick == 0,
                $"wall (14,11) at tick {wallTick}; settled at {Where(goods)}");
        }
        {
            var legacy = new CorpsePoseProbe();
            var body = new CorpsePoseProbe.Corpse();
            legacy.Expose(new Dictionary<string, object> { ["spin0"] = 1f }, true);
            legacy.Tick(body);
            float airborne = body.angle;
            legacy.Land(body);
            Case("legacy corpse keeps its lying pose", airborne == 90f && body.angle == 90f,
                $"airborne angle {airborne}; landed angle {body.angle}");

            var fresh = new CorpsePoseProbe();
            fresh.Launch(body = new CorpsePoseProbe.Corpse());
            var save = new Dictionary<string, object>();
            fresh.Expose(save, false);
            fresh = new CorpsePoseProbe();
            fresh.Expose(save, true);
            fresh.Tick(body);
            airborne = body.angle;
            fresh.Land(body);
            Case("fresh corpse still spins after load and lands lying", airborne == 110f && body.angle == 90f,
                $"airborne angle {airborne}; landed angle {body.angle}");
        }
#endif
        {
            // sc_mortar_throw (people_thrown_three_cells): a mortar shell one cell from a clothed colonist throws them 3 cells straight away
            var w = new MWorld(30, 30); MThing c = Col(w, 11, 10);
            Run(w, Bomb(10, 10));
            Case("sc_mortar_throw: a colonist one cell from a mortar shell lands exactly three cells straight away", c.x == 14 && c.z == 10, Where(c));
        }
        {
            // sc_pit_fall, open lane: a colonist and a stack beside a 1-wide open pit, the planned landing beyond its far rim
            var w = new MWorld(30, 30); w.deep[12, 10] = true; MThing c = Col(w, 11, 10); MThing s = Stack(w, 11, 10);
            Run(w, Bomb(10, 10));
            Case("sc_pit_fall open: the colonist lands in the first pit cell", c.x == 12 && c.inPit && c.plan.cells >= 2, Where(c));
            Case("sc_pit_fall open: the stack lands in the first pit cell", s.x == 12 && s.inPit, Where(s));
        }
        {
            // Cell centres and the cast in Verse.IntVec3(Vector3) determine which cell the carrier enters.
            Blast b = Bomb(0, 0);
            var clear = new MWorld(30, 30); MThing control = Stack(clear, 2, 1, 1f);
            Run(clear, b);
            KbResult leg = control.plan.first.res;
            int ticks = Ticks(Dist(leg.destX, leg.destZ, control.sx, control.sz), 14, 6);
            float progress = 3f / ticks;
            float x = control.sx + 0.5f + (leg.destX - control.sx) * progress;
            float z = control.sz + 0.5f + (leg.destZ - control.sz) * progress;
            var w = new MWorld(30, 30); w.deep[3, 1] = true; MThing s = Stack(w, 2, 1, 1f);
            Run(w, b);
            Case("sc_pit_fall diagonal: the stack settles in the open pit", w.deep[(int)x, (int)z] && s.x == (int)x && s.z == (int)z && s.inPit,
                $"straight flight tick 3 is ({x},{z}), settled at {Where(s)}");
        }
        {
            // sc_pit_fall, covered lane (RIMMANDRAKE_DROP_THROWS_INTO_COVERED_PITS_K08_MUST_FLIP): the cover lies outside the blast
            var w = new MWorld(30, 30); w.deep[13, 10] = true; w.cover[13, 10] = true; MThing c = Col(w, 11, 10); MThing s = Stack(w, 11, 11);
            w.deep[13, 12] = true; w.cover[13, 12] = true;
            Run(w, Bomb(10, 10, 1.9f));
            Case("sc_pit_fall covered: the colonist falls through and the cover is broken", c.x == 13 && c.inPit && !w.cover[13, 10], Where(c));
            Case("sc_pit_fall covered: the stack thrown onto a covered cell falls through it (visit 3's miss)", !(w.deep[s.x, s.z] && w.cover[s.x, s.z]), Where(s));
        }
        {
            // blind cycle 5 (RIMMANDRAKE_STOP_KNOCKBACK_THROW_AT_PAWN_ON_PIT_COVER): a pawn on a cover's deck blocks a thrown pawn
            var w = new MWorld(30, 30); w.deep[13, 10] = true; w.cover[13, 10] = true; MThing c = Col(w, 11, 10);
            MThing d = w.Add(new MThing { kind = KbKind.Pawn, mass = 70f, x = 13, z = 10, label = "pawn on the deck" });
            Run(w, Bomb(10, 10, 1.9f));
            Case("cycle 5: thrown at a pawn on a pit cover, it stops before it and the cover holds", c.x == 12 && !c.inPit && w.cover[13, 10] && d.x == 13 && !d.inPit, Where(c));
        }
        {
            // sc_gas_shove_into_pit and blast_breaks_pit_cover's gas half
            var w = new MWorld(30, 30); w.deep[12, 10] = true; MThing c = Col(w, 11, 10);
            w.deep[10, 12] = true; w.cover[10, 12] = true; MThing e = Col(w, 10, 11);
            Run(w, Gas(10, 10));
            Case("sc_gas_shove_into_pit: the one-cell shove puts the colonist in the open pit", c.x == 12 && c.inPit, Where(c));
            Case("gas shove onto a cover: it stands on it, the cover whole", e.z == 12 && !e.inPit && w.cover[10, 12], Where(e));
        }
        {
            Blast shortBlast = Bomb(10, 10);
            shortBlast.force = 0.25f; // a real blast whose unblocked throw is two cells
            foreach (Blast b in new[] { Gas(10, 10), shortBlast })
            {
                var w = new MWorld(30, 30); w.terr[12, 10] = w.terr[13, 10] = KbCell.Partial;
                MThing s = Stack(w, 11, 10, 20f);
                Run(w, b);
                int displacement = Math.Max(Math.Abs(s.x - s.sx), Math.Abs(s.z - s.sz));
                string travel = $"path {s.route.Count} cells, displacement {displacement}, settled at {Where(s)}";
                if (b.gas)
                    Case("sc_gas_chain: sandbag scatter stays within the gas cap", s.flew && s.route.Count <= 2 && displacement <= 2, travel);
                else
                    Case("a real blast still hops over the sandbags", s.plan.hopped && s.flew && s.x == 14 && s.z == 10, travel);
            }
        }
        {
            var w = new MWorld(30, 30);
            for (int x = 0; x < w.W; x++) w.terr[x, 9] = w.terr[x, 11] = KbCell.Wall;
            MThing steel = Stack(w, 11, 10, 20f, "steel");
            MThing pawn = Col(w, 12, 10); pawn.downed = true;
            MThing wood = Stack(w, 13, 10, 5f, "wood");
            Run(w, Gas(10, 10));
            Case("gas landing stays within the cap beside a full destination",
                steel.flew && steel.plan.first.res.destX == 13 && steel.route.Contains((12, 10))
                && Math.Max(Math.Abs(steel.x - steel.sx), Math.Abs(steel.z - steel.sz)) <= 2
                && !pawn.reached && pawn.x == 12 && pawn.z == 10 && pawn.damageTaken == 0f && pawn.stunTicks == 0
                && !wood.reached && !wood.merged && wood.x == 13 && wood.z == 10,
                $"steel {Where(steel)}; pawn {Where(pawn)}, damage {pawn.damageTaken}, stun {pawn.stunTicks}; wood {Where(wood)}");
        }
        {
            var w = new MWorld(30, 30);
            MThing steel = Stack(w, 11, 10, 20f, "steel"); steel.air = true;
            for (int x = 9; x <= 13; x++)
                for (int z = 8; z <= 12; z++)
                    Stack(w, x, z, 5f, "wood");
            Place(w, steel, 14, 10, 2);
            Case("gas landing fallback returns to takeoff when the destination is outside the cap",
                steel.placedVia == (int)KbPlanner.KbPlace.Fallback + 1 && steel.x == 11 && steel.z == 10, Where(steel));
        }
        {
            foreach (Blast b in new[] { Gas(10, 10), Bomb(10, 10, 1.9f) })
            {
                var w = new MWorld(30, 30); MThing s = Stack(w, 11, 10, 20f); MThing c = Col(w, 13, 10);
                Run(w, b);
                Case("heavy steel from " + b.name + (b.gas ? " passes the pawn unharmed" : " hits the pawn"),
                    s.flew && s.route.Contains((c.sx, c.sz)) && !c.reached && s.heavyStopped == !b.gas,
                    $"heavy hit={s.heavyStopped}, pawn reached={c.reached}, steel settled at {Where(s)}");
            }
        }
        {
            // RIMMANDRAKE_STOP_GAS_SHOVE_PAST_WALL_CORNER_UNSEEN: a burst reaches only what it sees, like an explosion (A5)
            var w = new MWorld(30, 30); w.terr[11, 10] = KbCell.Wall; w.terr[10, 11] = KbCell.Wall; MThing s = Stack(w, 11, 11);
            MThing open = Stack(w, 9, 9, 5f, "open");
            Run(w, Gas(10, 10));
            Case("gas past a sealed wall corner: the stack behind it stays, the stack in the open moves", s.x == 11 && s.z == 11 && !s.flew && open.flew, Where(s) + " " + Where(open));
            var w2 = new MWorld(30, 30); w2.terr[11, 10] = KbCell.Wall; w2.terr[10, 11] = KbCell.Wall; MThing s2 = Stack(w2, 11, 11);
            Run(w2, Bomb(10, 10));
            Case("a bomb past a sealed wall corner: the stack behind it stays", s2.x == 11 && s2.z == 11 && !s2.flew, Where(s2));
        }
        {
            // the map's own first finding: a stack with a wall right behind it
            var w = new MWorld(30, 30); for (int z = 5; z <= 15; z++) w.terr[13, z] = KbCell.Wall; MThing s = Stack(w, 12, 10);
            Run(w, Bomb(10, 10));
            Case("a stack against a wall bounces off it", s.flew && s.bounces >= 1 && s.x < 12, Where(s));
        }
        {
            // the map's second finding: two unlike stacks thrown at one pit cell
            var w = new MWorld(30, 30); w.deep[13, 10] = true; MThing a = Stack(w, 12, 10, 5f, "a"); MThing b = Stack(w, 11, 10, 5f, "b");
            Run(w, Bomb(10, 10));
            Case("two stacks, one pit cell: neither rests past the pit", a.x <= 13 && b.x <= 13 && (a.inPit || b.inPit), Where(a) + " " + Where(b));
            var w2 = new MWorld(30, 30); w2.deep[13, 10] = true; w2.deep[13, 11] = true; a = Stack(w2, 12, 10, 5f, "a"); b = Stack(w2, 11, 10, 5f, "b");
            Run(w2, Bomb(10, 10));
            Case("two stacks, a two-cell pit: both end on the pit floor", a.inPit && b.inPit, Where(a) + " " + Where(b));
            // RIMMANDRAKE_LAND_KNOCKBACK_GOODS_IN_PIT_FIRST_BOUNCE_ONLY_WHEN_FULL (owner, 2026-11-22: "Always into the pit somewhere,
            // THEN bounced out of the pit if totally full"): a trench whose landing end is full takes the stack farther along its floor
            var w3 = new MWorld(40, 40); for (int z = 10; z <= 15; z++) w3.deep[13, z] = true;
            for (int z = 10; z <= 14; z++) Stack(w3, 13, z, 5f, "full" + z);
            MThing c = Stack(w3, 12, 10, 5f, "c");
            Run(w3, Bomb(10, 10));
            Case("a part-full pit: the thrown stack lands inside it", c.inPit && c.x == 13 && c.z == 15, Where(c));
            var w4 = new MWorld(40, 40); for (int z = 10; z <= 15; z++) w4.deep[13, z] = true;
            for (int z = 10; z <= 15; z++) Stack(w4, 13, z, 5f, "full" + z);
            MThing d = Stack(w4, 12, 10, 5f, "d");
            Run(w4, Bomb(10, 10));
            Case("a totally full pit: the thrown stack is bounced out on the side it came from", !d.inPit && d.x <= 13 && !w4.deep[d.x, d.z], Where(d));
            var w5 = new MWorld(40, 40); w5.deep[13, 10] = true; w5.deep[13, 13] = true; Stack(w5, 13, 10, 5f, "full");
            MThing e2 = Stack(w5, 12, 10, 5f, "e2");
            Run(w5, Bomb(10, 10));
            Case("a full pit beside another pit: the stack does not jump to the other pit", !w5.deep[e2.x, e2.z], Where(e2));
        }
        {
            // sc_closed_containers: a light 1x1 locker is thrown a short way with its goods; a heavy one jolts; never into a pit
            var w = new MWorld(30, 30); MThing box = w.Add(new MThing { kind = KbKind.Item, container = true, mass = 30f, x = 12, z = 10, label = "locker" });
            MThing g = Stack(w, 12, 10, 3f); w.deep[14, 10] = true;
            Run(w, Bomb(10, 10));
            Case("sc_closed_containers: the locker is thrown short of the pit with its goods", box.x == 13 && g.x == 13 && !box.inPit, Where(box));
            var w2 = new MWorld(30, 30); MThing heavy = w2.Add(new MThing { kind = KbKind.Item, container = true, mass = 260f, x = 12, z = 10, label = "locker" });
            Run(w2, Bomb(10, 10));
            Case("sc_closed_containers: a locker over the container mass limit jolts in place", heavy.x == 12 && heavy.plan.act == KbAct.ContainerJolt, Where(heavy));
        }
    }

    // each Mod Settings switch the plan reads, flipped alone on one scene: only the things it names may change (leaf
    // settings_scale_and_switch: "each part switches off cleanly with the rest still working")
    private static void Settings()
    {
        Func<Dictionary<string, string>> run = () =>
        {
            var w = new MWorld(30, 30);
            w.Add(new MThing { kind = KbKind.Pawn, mass = 70f, x = 12, z = 10, label = "colonist" });
            w.Add(new MThing { kind = KbKind.Pawn, mass = 70f, x = 8, z = 10, downed = true, label = "downed" });
            w.Add(new MThing { kind = KbKind.Pawn, mass = 40f, x = 11, z = 12, animal = true, label = "animal" });
            w.Add(new MThing { kind = KbKind.Pawn, mass = 90f, x = 10, z = 8, mech = true, label = "mech" });
            w.Add(new MThing { kind = KbKind.Pawn, mass = 70f, x = 11, z = 11, shield = true, label = "belted" });
            w.Add(new MThing { kind = KbKind.Item, mass = 5f, x = 9, z = 9, label = "floor stack" });
            w.Add(new MThing { kind = KbKind.Corpse, mass = 60f, x = 11, z = 9, label = "corpse" });
            w.shelf[9, 11] = true;
            w.Add(new MThing { kind = KbKind.Item, mass = 5f, x = 9, z = 11, label = "shelf stack" });
            w.Add(new MThing { kind = KbKind.Item, container = true, mass = 30f, x = 10, z = 11, label = "locker" });
            w.Add(new MThing { kind = KbKind.Item, mass = 5f, x = 10, z = 11, label = "locker stack" });
            Run(w, new Blast { name = "bomb", cx = 10, cz = 10, radius = 2.9f, force = 1f });
            // a container's goods are told apart from loose ones by where they end relative to it
            MThing box = w.things.First(t => t.container);
            return w.things.ToDictionary(t => t.label, t => (t.x - t.sx) + "," + (t.z - t.sz) + (t.label == "locker stack" ? (t.x == box.x && t.z == box.z ? " with it" : " apart") : ""));
        };
        Dictionary<string, string> def = run();
        var flips = new (string name, Action<KbRules> set, string[] changes)[]
        {
            ("throwDowned off", q => q.throwDowned = false, new[] { "downed" }),
            ("throwAnimals off", q => q.throwAnimals = false, new[] { "animal" }),
            ("throwMechanoids off", q => q.throwMechanoids = false, new[] { "mech" }),
            ("throwItems off", q => q.throwItems = false, new[] { "floor stack", "shelf stack" }),
            ("throwCorpses off", q => q.throwCorpses = false, new[] { "corpse" }),
            ("flyingGoods off", q => q.flyingGoods = false, new[] { "floor stack", "shelf stack", "corpse" }),
            ("closedContainerGuard off", q => q.closedContainerGuard = false, new[] { "locker stack" }),
            ("openStorageProtects on", q => q.openStorageProtects = true, new[] { "shelf stack" }),
            ("shoveClosedContainers off", q => q.shoveClosedContainers = false, new[] { "locker", "locker stack" }),
            ("shieldsAbsorbThrow off", q => q.shieldsAbsorbThrow = false, new[] { "belted" }),
        };
        Case("settings: at the defaults the colonist, the downed, the animal, the mech, the floor stack, the shelf stack, the corpse and the locker move; the belted pawn stays",
            new[] { "colonist", "downed", "animal", "mech", "floor stack", "shelf stack", "corpse", "locker" }.All(k => !def[k].StartsWith("0,0")) && def["belted"] == "0,0" && def["locker stack"].EndsWith("with it"),
            string.Join("; ", def.Select(kv => kv.Key + " " + kv.Value)));
        foreach (var f in flips)
        {
            Q = new KbRules();
            f.set(Q);
            Dictionary<string, string> got = run();
            Q = new KbRules();
            string[] changed = got.Where(kv => kv.Value != def[kv.Key]).Select(kv => kv.Key).OrderBy(k => k).ToArray();
            Case("settings: " + f.name + " changes only " + string.Join(", ", f.changes), changed.SequenceEqual(f.changes.OrderBy(k => k)), "changed: " + string.Join(", ", changed));
        }
    }

    // ════════════════════════ the live agreement set (proof/map_agreement.py runs it in the game) ════════════════════════
    // Only what RM_KnockbackProof.MapCase can stage: colonists pinned to 70 or 200 kg, Steel x2 (1 kg), Steel x40 (20 kg),
    // WoodLog x50 (20 kg), Uranium x74 (74 kg); walls, doors, sandbags, deep water, pits, covers; one bomb or one gas burst.
    private static readonly Dictionary<string, (KbKind kind, float mass, string key, bool full)> Palette = new Dictionary<string, (KbKind, float, string, bool)>
    {
        ["col"] = (KbKind.Pawn, 70f, null, true), ["big"] = (KbKind.Pawn, 200f, null, true),
        ["steel2"] = (KbKind.Item, 1f, "Steel", false), ["steel40"] = (KbKind.Item, 20f, "Steel", false),
        ["wood50"] = (KbKind.Item, 20f, "WoodLog", false), ["uran74"] = (KbKind.Item, 74f, "Uranium", false),
    };

    private const int SpecC = 15;
    private static MWorld FromSpec(string spec, bool reverse, out Blast b, out Dictionary<string, MThing> keys)
    {
        var w = new MWorld(31, 31) { reverseTies = reverse };
        b = null; keys = new Dictionary<string, MThing>();
        var inv = System.Globalization.CultureInfo.InvariantCulture;
        foreach (string tok in spec.Split(';'))
        {
            string[] p = tok.Split(':');
            if (p[0] == "c")
            {
                int x = SpecC + int.Parse(p[2]), z = SpecC + int.Parse(p[3]);
                switch (p[1])
                {
                    case "wall": w.terr[x, z] = KbCell.Wall; break;
                    case "door": w.terr[x, z] = KbCell.Door; break;
                    case "sandbag": w.terr[x, z] = KbCell.Partial; break;
                    case "water": w.terr[x, z] = KbCell.Water; break;
                    case "pit": w.deep[x, z] = true; break;
                    case "cover": w.deep[x, z] = true; w.cover[x, z] = true; break;
                }
            }
            else if (p[0] == "t")
            {
                var pal = Palette[p[2]];
                int x = SpecC + int.Parse(p[3]), z = SpecC + int.Parse(p[4]);
                keys[p[1]] = w.Add(new MThing { kind = pal.kind, mass = pal.mass, key = pal.key, full = pal.full, x = x, z = z, label = p[1] + " " + p[2],
                    inPit = w.deep[x, z] && !w.cover[x, z] });
            }
            else if (p[0] == "b")
            {
                b = new Blast { name = p[1], cx = SpecC, cz = SpecC, radius = float.Parse(p[2], inv), force = 1f, gas = p[1] == "gas" };
            }
        }
        return w;
    }

    private static int Export(string path)
    {
        var specs = new List<string>();
        string[] things = { "col", "steel2", "steel40", "uran74" };
        string[] obs = { "none", "wall", "door", "sandbag", "water", "pit", "cover", "big", "wood50", "pitfloor", "pitwall", "cover2" };
        (int x, int z)[] dirs = { (1, 0), (1, 1), (0, -1), (-1, 0), (2, 1), (-1, 2), (-1, -1), (1, -2) };
        int pick = 0;
        foreach (string blast in new[] { "b:bomb:2.9", "b:gas:1.9" })
            foreach (string th in things)
                foreach (string ob in obs)
                {
                    // one (direction, obstacle step) per combination, rotated so the set covers every direction and step
                    for (int tries = 0; tries < 24; tries++)
                    {
                        (int dx, int dz) = dirs[(pick + tries) % dirs.Length];
                        int k = 1 + (pick + tries / dirs.Length) % 3;
                        if (blast.Contains("gas") && Dist(dx, dz, 0, 0) > 1.9) continue;
                        List<(int x, int z)> ray = RM_KnockbackMath.Line(dx, dz, dx, dz, 6);
                        (int ox, int oz) = ray[k - 1];
                        var sb = new StringBuilder();
                        switch (ob)
                        {
                            case "none": break;
                            case "big": sb.Append("t:o:big:" + ox + ":" + oz + ";"); break;
                            case "wood50": sb.Append("t:o:wood50:" + ox + ":" + oz + ";"); break;
                            case "pitfloor": sb.Append("c:pit:" + ox + ":" + oz + ";t:o:wood50:" + ox + ":" + oz + ";"); break;
                            case "pitwall": sb.Append("c:pit:" + ox + ":" + oz + ";c:wall:" + ray[k].x + ":" + ray[k].z + ";"); break;
                            case "cover2": sb.Append("c:cover:" + ox + ":" + oz + ";t:o:col:" + ox + ":" + oz + ";"); break;
                            default: sb.Append("c:" + ob + ":" + ox + ":" + oz + ";"); break;
                        }
                        sb.Append("t:a:" + th + ":" + dx + ":" + dz + ";" + blast);
                        if (Fits(sb.ToString())) { specs.Add(sb.ToString()); break; }
                    }
                    pick++;
                }
        // the map's own findings and the mod's pit scenes, staged for the game
        specs.AddRange(new[]
        {
            "c:wall:3:-1;c:wall:3:0;c:wall:3:1;t:a:steel2:2:0;b:bomb:2.9",
            "c:wall:3:-1;c:wall:3:0;c:wall:3:1;c:wall:2:2;c:wall:1:2;c:wall:3:2;t:a:steel40:2:1;b:bomb:2.9",
            "c:wall:-1:3;c:wall:0:3;c:wall:1:3;t:a:wood50:0:2;t:b:steel2:0:1;b:bomb:2.9",
            "c:pit:3:0;t:a:steel2:2:0;t:b:wood50:1:0;b:bomb:2.9",
            "c:pit:3:0;c:pit:3:1;t:a:steel2:2:0;t:b:wood50:1:0;b:bomb:2.9",
            "c:pit:3:0;c:pit:3:1;c:pit:3:-1;t:a:steel2:2:0;t:b:wood50:1:0;t:c:uran74:1:1;b:bomb:2.9",
            "c:pit:0:-3;t:a:steel2:0:-2;t:b:wood50:0:-1;t:c:col:1:-1;b:bomb:2.9",
            "c:sandbag:2:0;t:a:uran74:1:0;b:bomb:2.9",
            "c:sandbag:2:0;c:sandbag:3:0;t:a:steel40:1:0;b:gas:1.9",
            "c:sandbag:0:2;t:a:col:0:1;b:gas:1.9",
            "c:cover:3:0;t:a:col:1:0;t:b:steel2:1:1;c:cover:3:2;b:bomb:1.9",
            "c:cover:2:0;t:a:col:1:0;b:gas:1.9",
            "c:pit:2:0;t:a:col:1:0;b:gas:1.9",
            "c:cover:3:0;t:o:col:3:0;t:a:col:1:0;b:bomb:1.9",
            "t:a:col:1:0;t:b:col:2:0;t:c:col:3:0;b:bomb:2.9",
            "t:a:steel40:1:0;t:b:col:3:0;b:bomb:2.9",
            "t:a:steel2:1:0;t:b:col:3:0;b:bomb:2.9",
            "c:door:3:0;c:wall:3:1;c:wall:3:-1;t:a:steel2:1:0;b:bomb:2.9",
            "c:water:3:0;c:water:4:0;t:a:steel2:1:0;b:bomb:2.9",
            "c:water:2:0;t:a:steel2:1:0;b:bomb:2.9",
            // reach (A5): a sealed corner, a door corner, half a corner from the side the sight line takes and from the other, a wall between
            "c:wall:1:0;c:wall:0:1;t:a:steel2:1:1;b:gas:1.9",
            "c:wall:-1:0;c:wall:0:-1;t:a:steel2:-1:-1;b:gas:1.9",
            "c:wall:1:0;c:door:0:1;t:a:col:1:1;b:gas:1.9",
            "c:wall:1:0;t:a:steel2:1:1;b:gas:1.9",
            "c:wall:0:1;t:a:steel2:1:1;b:gas:1.9",
            "c:sandbag:1:0;c:sandbag:0:1;t:a:steel2:1:1;b:gas:1.9",
            "c:wall:1:0;c:wall:0:1;t:a:steel2:1:1;b:bomb:2.9",
            "c:wall:1:0;t:a:steel2:2:0;b:bomb:2.9",
            // a taken pit cell (his card 2026-11-22): the far end of the trench takes the stack; a full trench bounces it out; a gas hop; a crossed pit
            "c:pit:3:0;c:pit:3:1;c:pit:3:2;c:pit:3:3;t:o:wood50:3:0;t:p:wood50:3:1;t:q:wood50:3:2;t:a:steel2:1:0;b:bomb:2.9",
            "c:pit:3:0;c:pit:3:1;t:o:wood50:3:0;t:p:wood50:3:1;t:a:steel2:1:0;b:bomb:2.9",
            "c:pit:2:1;t:a:steel2:1:1;b:bomb:2.9",
        });
        var inv = System.Globalization.CultureInfo.InvariantCulture;
        using (var f = new System.IO.StreamWriter(path))
        {
            foreach (string spec in specs.Distinct())
            {
                if (!Fits(spec)) continue;
                var ends = new List<Dictionary<string, string>>();
                var coversBoth = new List<string>();
                foreach (bool rev in new[] { false, true })
                {
                    MWorld w = FromSpec(spec, rev, out Blast b, out Dictionary<string, MThing> keys);
                    Run(w, b);
                    ends.Add(keys.ToDictionary(kv => kv.Key, kv => (kv.Value.x - SpecC) + "," + (kv.Value.z - SpecC) + "," + (kv.Value.inPit ? 1 : 0)));
                    var cv = new List<string>();
                    for (int x = 0; x < w.W; x++) for (int z = 0; z < w.H; z++) if (w.cover[x, z]) cv.Add((x - SpecC) + "," + (z - SpecC));
                    coversBoth.Add(string.Join("/", cv));
                }
                string expect = string.Join(",", ends[0].Keys.Select(k => "\"" + k + "\":[" + string.Join(",", new[] { ends[0][k], ends[1][k] }.Distinct().Select(v => "\"" + v + "\"")) + "]"));
                f.WriteLine("{\"spec\":\"" + spec + "\",\"expect\":{" + expect + "},\"covers\":\"" + coversBoth[0] + "\",\"map\":\"" + Version + "\"}");
            }
        }
        Console.WriteLine("exported " + specs.Distinct().Count(Fits) + " agreement cases to " + path);
        return 0;
    }

    // every cell and every end within 7 of the blast: RM_KnockbackProof's scene sites are 15x15
    private static bool Fits(string spec)
    {
        foreach (bool rev in new[] { false, true })
        {
            MWorld w = FromSpec(spec, rev, out Blast b, out _);
            if (w.things.Select(t => (t.x, t.z)).Distinct().Count() < w.things.Count(t => t.kind == KbKind.Pawn)) return false; // two staged pawns on one cell
            Run(w, b);
            foreach (MThing t in w.things)
                if (Math.Abs(t.x - SpecC) > 6 || Math.Abs(t.z - SpecC) > 6 || t.route.Any(c => Math.Abs(c.x - SpecC) > 6 || Math.Abs(c.z - SpecC) > 6)) return false;
        }
        for (int i = 0; i < 2; i++) { }
        return !spec.Split(';').Any(t => t.StartsWith("c:") && (Math.Abs(int.Parse(t.Split(':')[2])) > 6 || Math.Abs(int.Parse(t.Split(':')[3])) > 6));
    }

    public static int RunMap(string[] args)
    {
        int ex = Array.IndexOf(args, "--map-export");
        if (ex >= 0)
        {
            return Export(args[ex + 1]);
        }
        int rooms = 20000, seed = 20261117;
        int i = Array.IndexOf(args, "--map-rooms");
        if (i >= 0) rooms = int.Parse(args[i + 1]);
        i = Array.IndexOf(args, "--map-seed");
        if (i >= 0) seed = int.Parse(args[i + 1]);
        bool regions = args.Contains("--map-regions");
        foreach (string b in BarIds) T(b.Substring(0, 3));
        Lanes();
        SparedLanes();
        Rooms(rooms, seed);
        Cases();
        Settings();
        Console.WriteLine("KNOCKBACK MAP " + Version + ": lanes " + LaneCases + " (enumerated), spared " + SparedCases + " (enumerated), rooms " + RoomCases + " (seed " + seed + ", " + rooms + " layouts x 2 tie orders)");
        long bad = 0;
        foreach (KeyValuePair<string, Tally> kv in Bars)
        {
            Tally t = kv.Value;
            bad += t.violations;
            Console.WriteLine((t.violations == 0 ? "HOLDS " : "BREAKS ") + kv.Key + ": " + t.violations + " of " + t.applicable + " readings (rooms " + t.roomViolations + " of " + t.roomApplicable + ")");
            foreach (string e in t.examples.Take(args.Contains("--map-examples") ? 5 : 1)) Console.WriteLine("    e.g. " + e.Replace("\n", "\n         "));
        }
        if (regions)
        {
            foreach (KeyValuePair<string, long[]> kv in Regions.Where(k => k.Value[1] > 0))
                Console.WriteLine("REGION " + kv.Key + ": " + kv.Value[1] + " of " + kv.Value[0]);
        }
        Console.WriteLine("CASES " + (CasesRun - CasesFailed) + " of " + CasesRun + " fixed cases and settings flips as expected");
        bad += CasesFailed;
        Console.WriteLine("knockback map: " + (bad == 0 ? "every bar holds over the declared range (" + Version + ")" : bad + " readings break a bar (" + Version + ")"));
        return bad == 0 ? 0 : 1;
    }
}
