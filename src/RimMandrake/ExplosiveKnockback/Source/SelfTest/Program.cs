using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.ExplosiveKnockback;

// Offline kernel tests K-01..K-17 (design §8.1). Compiles the PRODUCTION RM_KnockbackMath.cs.
internal sealed class Grid : IKbGrid
{
    public readonly int W, H;
    private readonly KbCell[,] cells;

    public Grid(int w, int h)
    {
        W = w;
        H = h;
        cells = new KbCell[w, h];
    }

    public Grid Set(int x, int z, KbCell c)
    {
        cells[x, z] = c;
        return this;
    }

    public KbCell At(int x, int z)
    {
        if (x < 0 || z < 0 || x >= W || z >= H)
        {
            return KbCell.OutOfBounds;
        }
        return cells[x, z];
    }
}

internal static class Program
{
    private static int pass, fail;

    private static void Check(string id, bool ok, string detail = "")
    {
        if (ok)
        {
            pass++;
        }
        else
        {
            fail++;
            Console.WriteLine("FAIL " + id + " " + detail);
        }
    }

    private static int Main(string[] args)
    {
        if (args.Any(a => a.StartsWith("--fuzz")))
        {
            double scale = 1;
            int i = Array.IndexOf(args, "--fuzz-scale");
            if (i >= 0) scale = double.Parse(args[i + 1], System.Globalization.CultureInfo.InvariantCulture);
            int? one = null;
            i = Array.IndexOf(args, "--fuzz-seed");
            if (i >= 0) one = int.Parse(args[i + 1]);
            string only = null;
            i = Array.IndexOf(args, "--fuzz-only");
            if (i >= 0) only = args[i + 1];
            return KnockbackFuzz.Run(scale, one, only) ? 0 : 1;
        }
        var s = new KbSettings();

        // K-01 calibration (owner Q7: mortar shell beside a human throws 3 cells)
        Check("K-01 mortar d1 60kg", RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f, 60f, s) == 3, RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f, 60f, s).ToString());
        Check("K-01 mortar d1 clothed 68kg", RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f, 68f, s) == 3);
        Check("K-01 mortar d1 armoured 90kg", RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f, 90f, s) == 2);
        Check("K-01 frag d1", RM_KnockbackMath.ThrowCells(1f, 1.9f, 1f, 60f, s) == 2);
        Check("K-01 centre", RM_KnockbackMath.ThrowCells(0f, 2.9f, 1f, 60f, s) == 4);
        Check("K-01 10kg item", RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f, 10f, s) == 5);
        Check("K-01 force 0", RM_KnockbackMath.ThrowCells(0f, 2.9f, 0f, 60f, s) == 0);
        var s2 = new KbSettings { globalMultiplier = 2f };
        Check("K-01 strength x2", RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f, 60f, s2) == 6);
        var s0 = new KbSettings { globalMultiplier = 0f };
        Check("K-01 strength 0", RM_KnockbackMath.ThrowCells(0f, 2.9f, 1f, 60f, s0) == 0);
        Check("K-01 max cap", RM_KnockbackMath.ThrowCells(0f, 9f, 3f, 5f, s) == s.maxCells);

        // K-13 per-weapon cap (owner card 2026-10-06 "Let each weapon set it"): own cap replaces the global 6
        Check("K-13 no own cap = global", RM_KnockbackMath.CapFor(0, 6, 1f) == 6);
        Check("K-13 grav-ram own 10", RM_KnockbackMath.CapFor(10, 6, 1f) == 10);
        Check("K-13 own cap may be below global", RM_KnockbackMath.CapFor(5, 6, 1f) == 5);
        Check("K-13 scale 0.5", RM_KnockbackMath.CapFor(10, 6, 0.5f) == 5);
        Check("K-13 scale floor 1", RM_KnockbackMath.CapFor(1, 6, 0.25f) == 1);
        Check("K-13 scale ignored without own cap", RM_KnockbackMath.CapFor(0, 6, 2f) == 6);
        var sGr = new KbSettings { maxCells = RM_KnockbackMath.CapFor(10, 6, 1f) };
        Check("K-13 grav-ram force 4 centre throws 10", RM_KnockbackMath.ThrowCells(0f, 2.9f, 4f, 70f, sGr) == 10,
            RM_KnockbackMath.ThrowCells(0f, 2.9f, 4f, 70f, sGr).ToString());
        var sTh = new KbSettings { maxCells = RM_KnockbackMath.CapFor(8, 6, 1f) };
        Check("K-13 thump force 2.5 centre throws 8 (global would give 6)", RM_KnockbackMath.ThrowCells(0f, 1.9f, 2.5f, 70f, sTh) == 8
            && RM_KnockbackMath.ThrowCells(0f, 1.9f, 2.5f, 70f, s) == 6);

        // K-02 monotone in distance; 0 at the rim
        int prev = int.MaxValue;
        bool mono = true;
        for (float d = 0f; d <= 2.9f; d += 0.1f)
        {
            int c = RM_KnockbackMath.ThrowCells(d, 2.9f, 1f, 60f, s);
            mono &= c <= prev;
            prev = c;
        }
        Check("K-02 monotone", mono);
        Check("K-02 rim", RM_KnockbackMath.ThrowCells(2.9f, 2.9f, 1f, 60f, s) == 0);

        // K-03 heavier never farther; immune / mass limit
        bool heavy = true;
        for (float m = 1f; m < 400f; m += 3f)
        {
            heavy &= RM_KnockbackMath.ThrowCells(0.5f, 2.9f, 1f, m + 3f, s) <= RM_KnockbackMath.ThrowCells(0.5f, 2.9f, 1f, m, s);
        }
        Check("K-03 heavier never farther", heavy);
        Check("K-03 too heavy pawn", !RM_KnockbackMath.Eligible(KbKind.Pawn, 151f, s));
        Check("K-03 human pawn", RM_KnockbackMath.Eligible(KbKind.Pawn, 60f, s));
        Check("K-03 pawn at the limit still eligible", RM_KnockbackMath.Eligible(KbKind.Pawn, 150f, s));
        Check("K-03 heavy item", !RM_KnockbackMath.Eligible(KbKind.Item, 76f, s));
        Check("K-03 light item", RM_KnockbackMath.Eligible(KbKind.Item, 37.5f, s));
        Check("K-03 human corpse", RM_KnockbackMath.Eligible(KbKind.Corpse, 60f, s));
        Check("K-03 heavy corpse", !RM_KnockbackMath.Eligible(KbKind.Corpse, 150f, s));

        // K-14 storage (owner 2026-11-10/11, RIMMANDRAKE_LIMIT_KNOCKBACK_STORAGE_CLOSED): open shelves give no cover,
        // closed containers keep their goods, the old rule only behind its setting
        Check("K-14 floor good is not held", !RM_KnockbackMath.GoodsHeld(false, false, false));
        Check("K-14 open shelf does not hold", !RM_KnockbackMath.GoodsHeld(true, false, false));
        Check("K-14 closed container holds", RM_KnockbackMath.GoodsHeld(true, true, false));
        Check("K-14 old rule: open shelf holds when set", RM_KnockbackMath.GoodsHeld(true, false, true));
        Check("K-14 old rule never holds floor goods", !RM_KnockbackMath.GoodsHeld(false, false, true));
        Check("K-14 shove: 1x1 light free -> slide", RM_KnockbackMath.ContainerShove(true, true, 20f, 75f, true) == KbShove.Slide);
        Check("K-14 shove: at the limit -> slide", RM_KnockbackMath.ContainerShove(true, true, 75f, 75f, true) == KbShove.Slide);
        Check("K-14 shove: blocked -> jolt", RM_KnockbackMath.ContainerShove(true, true, 20f, 75f, false) == KbShove.Jolt);
        Check("K-14 shove: heavy -> jolt", RM_KnockbackMath.ContainerShove(true, true, 76f, 75f, true) == KbShove.Jolt);
        Check("K-14 shove: 2x1 -> jolt", RM_KnockbackMath.ContainerShove(true, false, 20f, 75f, true) == KbShove.Jolt);
        Check("K-14 shove off -> none", RM_KnockbackMath.ContainerShove(false, true, 20f, 75f, true) == KbShove.None);
        bool shoveCells = RM_KnockbackMath.ShoveCellFree(KbCell.Open, false) && !RM_KnockbackMath.ShoveCellFree(KbCell.Open, true);
        foreach (KbCell bad in new[] { KbCell.Wall, KbCell.Door, KbCell.Partial, KbCell.Pawn, KbCell.Pit, KbCell.CoveredPit, KbCell.Water, KbCell.OutOfBounds })
        {
            shoveCells &= !RM_KnockbackMath.ShoveCellFree(bad, false);
        }
        Check("K-14 shove never into pit, wall, door, pawn, water, edge", shoveCells);

        // K-04/K-05 property: random grids, never end on a blocked cell, never pass through a wall
        var rnd = new Random(1234);
        bool neverBlocked = true, neverThrough = true, cornerOk = true;
        for (int trial = 0; trial < 20000; trial++)
        {
            var g = new Grid(12, 12);
            for (int x = 0; x < 12; x++)
            {
                for (int z = 0; z < 12; z++)
                {
                    int r = rnd.Next(100);
                    g.Set(x, z, r < 12 ? KbCell.Wall : r < 15 ? KbCell.Door : r < 20 ? KbCell.Partial : r < 24 ? KbCell.Pawn
                        : r < 27 ? KbCell.Pit : r < 29 ? KbCell.Water : r < 31 ? KbCell.CoveredPit : KbCell.Open);
                }
            }
            int sx = rnd.Next(12), sz = rnd.Next(12);
            g.Set(sx, sz, KbCell.Open);
            double a = rnd.NextDouble() * Math.PI * 2;
            float dx = (float)Math.Cos(a), dz = (float)Math.Sin(a);
            int cells = 1 + rnd.Next(6);
            KbKind kind = (KbKind)rnd.Next(3);
            KbResult res = RM_KnockbackMath.Resolve(g, sx, sz, dx, dz, cells, kind, 60f, s);
            KbCell end = g.At(res.destX, res.destZ);
            bool endOk = (res.destX == sx && res.destZ == sz) || (end != KbCell.Wall && end != KbCell.Door && end != KbCell.OutOfBounds
                && end != KbCell.Water && !(end == KbCell.Pawn && kind == KbKind.Pawn) && end != KbCell.Partial);
            neverBlocked &= endOk;
            if (!endOk)
            {
                Console.WriteLine("  K-04 counterexample end=" + end + " kind=" + kind);
            }
            // walk the planned line up to cellsTravelled: no wall/door/OOB/water, nothing past a pit, no corner cut
            List<(int x, int z)> line = RM_KnockbackMath.Line(sx, sz, dx, dz, cells);
            int px = sx, pz = sz;
            for (int i = 0; i < res.cellsTravelled && i < line.Count; i++)
            {
                KbCell c = g.At(line[i].x, line[i].z);
                if (c == KbCell.Wall || c == KbCell.Door || c == KbCell.OutOfBounds || c == KbCell.Water)
                {
                    neverThrough = false;
                }
                if (c == KbCell.Pit && i != res.cellsTravelled - 1)
                {
                    neverThrough = false;
                }
                if (line[i].x != px && line[i].z != pz)
                {
                    KbCell a1 = g.At(line[i].x, pz), a2 = g.At(px, line[i].z);
                    if (a1 == KbCell.Wall || a1 == KbCell.Door || a2 == KbCell.Wall || a2 == KbCell.Door)
                    {
                        cornerOk = false;
                    }
                }
                px = line[i].x;
                pz = line[i].z;
            }
        }
        Check("K-04 never ends blocked", neverBlocked);
        Check("K-05 never through a wall / past a pit", neverThrough);
        Check("K-05 no corner cutting", cornerOk);

        // K-05 explicit diagonal corner
        {
            var g = new Grid(6, 6).Set(1, 0, KbCell.Wall);
            KbResult r = RM_KnockbackMath.Resolve(g, 0, 0, 1f, 1f, 3, KbKind.Pawn, 60f, s);
            Check("K-05 diagonal corner stops", r.cellsTravelled == 0 && r.stop == KbStop.Wall, r.stop + " " + r.cellsTravelled);
        }

        // K-06 partial cover crossed; stops when the setting is on; item never rests on it
        {
            var g = new Grid(10, 3).Set(2, 1, KbCell.Partial);
            KbResult r = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 3, KbKind.Pawn, 60f, s);
            Check("K-06 pawn over sandbags", r.destX == 3 && r.stop == KbStop.Distance, r.destX + " " + r.stop);
            KbResult ri = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 3, KbKind.Item, 60f, s);
            Check("K-06 item over sandbags", ri.destX == 3);
            KbResult ri2 = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 2, KbKind.Item, 60f, s);
            Check("K-06 item not resting on sandbag", ri2.destX == 1, ri2.destX.ToString());
            KbResult rp2 = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 2, KbKind.Pawn, 60f, s);
            Check("K-06 pawn not resting on sandbag (PassThroughOnly)", rp2.destX == 1);
            var sb = new KbSettings { sandbagsStop = true };
            KbResult rs = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 3, KbKind.Pawn, 60f, sb);
            Check("K-06 sandbagsStop", rs.destX == 1 && rs.stop == KbStop.PartialCover && rs.impact > 0f);
        }

        // K-07 wall impact / OOB / item
        {
            var g = new Grid(10, 3).Set(2, 1, KbCell.Wall);
            KbResult r = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 4, KbKind.Pawn, 60f, s);
            Check("K-07 wall stop", r.destX == 1 && r.stop == KbStop.Wall);
            Check("K-07 wall impact", Math.Abs(r.impact - 4f * 3 / (float)Math.Sqrt(Math.Sqrt(70.0 / 60.0))) < 1e-3, r.impact.ToString());
            KbResult ri = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 4, KbKind.Item, 60f, s);
            Check("K-07 item no impact", ri.impact == 0f && ri.destX == 1);
            KbResult ro = RM_KnockbackMath.Resolve(new Grid(3, 3), 1, 1, 1f, 0f, 4, KbKind.Pawn, 60f, s);
            Check("K-07 OOB no impact", ro.destX == 2 && ro.stop == KbStop.OutOfBounds && ro.impact == 0f);
            KbResult rheavy = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 4, KbKind.Pawn, 240f, s);
            Check("K-07 heavier hits harder", rheavy.impact > r.impact);
            var off = new KbSettings { impactEnabled = false };
            Check("K-07 impact off", RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 4, KbKind.Pawn, 60f, off).impact == 0f);
            var gd = new Grid(10, 3).Set(2, 1, KbCell.Door);
            KbResult rd = RM_KnockbackMath.Resolve(gd, 0, 1, 1f, 0f, 4, KbKind.Pawn, 60f, s);
            Check("K-07 door", rd.stop == KbStop.Door && rd.hitDoor && rd.doorX == 2 && rd.impact > 0f);
            var gw = new Grid(10, 3).Set(2, 1, KbCell.Water);
            KbResult rw = RM_KnockbackMath.Resolve(gw, 0, 1, 1f, 0f, 4, KbKind.Pawn, 60f, s);
            Check("K-07 water stops, no impact", rw.destX == 1 && rw.stop == KbStop.Water && rw.impact == 0f);
        }

        // K-08 open pit: stops IN the first pit cell; off = stops before it
        {
            var g = new Grid(10, 3).Set(2, 1, KbCell.Pit).Set(3, 1, KbCell.Pit);
            KbResult r = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 4, KbKind.Pawn, 60f, s);
            Check("K-08 into pit", r.destX == 2 && r.stop == KbStop.Pit);
            KbResult ri = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 4, KbKind.Corpse, 60f, s);
            Check("K-08 corpse into pit", ri.destX == 2 && ri.stop == KbStop.Pit);
            var g1 = new Grid(10, 3).Set(2, 1, KbCell.Pit);
            KbResult rn = RM_KnockbackMath.Resolve(g1, 0, 1, 1f, 0f, 4, KbKind.Pawn, 60f, s);
            Check("K-08 no_cross 1-wide", rn.destX == 2);
            var off = new KbSettings { intoPits = false };
            KbResult ro = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 4, KbKind.Pawn, 60f, off);
            Check("K-08 pits off", ro.destX == 1);
            var gc = new Grid(10, 3).Set(2, 1, KbCell.CoveredPit);
            Check("K-08 cover is ground", RM_KnockbackMath.Resolve(gc, 0, 1, 1f, 0f, 4, KbKind.Pawn, 60f, s).destX == 4);
        }

        // K-09 pawn-pawn split; item passes a pawn
        {
            var g = new Grid(10, 3).Set(2, 1, KbCell.Pawn);
            KbResult r = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 4, KbKind.Pawn, 60f, s);
            Check("K-09 pawn stop", r.destX == 1 && r.hitOther && r.otherX == 2 && r.impact > 0f && Math.Abs(r.impact - r.otherImpact) < 1e-4);
            KbResult ri = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 4, KbKind.Item, 60f, s);
            Check("K-09 item passes pawn", ri.destX == 4);
        }

        // K-10 epicentre deterministic
        {
            RM_KnockbackMath.EpicentreDir(77, 1234, out float a1, out float b1);
            RM_KnockbackMath.EpicentreDir(77, 1234, out float a2, out float b2);
            RM_KnockbackMath.EpicentreDir(78, 1234, out float a3, out float b3);
            Check("K-10 deterministic", a1 == a2 && b1 == b2);
            Check("K-10 differs by explosion", a1 != a3 || b1 != b3);
            Check("K-10 unit", Math.Abs(a1 * a1 + b1 * b1 - 1f) < 1e-4);
        }

        // K-11 caps
        {
            var all = new List<KbCandidate>();
            for (int i = 0; i < 30; i++)
            {
                all.Add(new KbCandidate { index = i, kind = KbKind.Item, distance = 30 - i });
            }
            all.Add(new KbCandidate { index = 100, kind = KbKind.Corpse, distance = 2f });
            all.Add(new KbCandidate { index = 101, kind = KbKind.Pawn, distance = 2.5f });
            List<KbCandidate> kept = RM_KnockbackMath.Prioritise(all, 5);
            Check("K-11 cap count", kept.Count == 5);
            Check("K-11 pawn first", kept[0].index == 101 && kept[1].index == 100);
            Check("K-11 nearest items", kept[2].distance <= kept[3].distance && kept[2].index == 29);
            Check("K-11 cap = all keeps all", RM_KnockbackMath.Prioritise(all, all.Count).Count == all.Count);
        }

        // K-12 dedupe
        {
            var d = new KbExplosionLedger();
            Check("K-12 first", d.TryAdd(5, 9, 100));
            Check("K-12 repeat", !d.TryAdd(5, 9, 101));
            Check("K-12 other explosion", d.TryAdd(6, 9, 101));
            // a wave straddling a rotation still remembers its pairs and its launch count (the old wholesale clear forgot both)
            d.AddLaunched(5, 650); d.AddLaunched(5, 651);
            Check("K-12 repeat after one rotation", !d.TryAdd(5, 9, 100 + 600 + 1) && d.Launched(5, 100 + 600 + 5) == 2);
            Check("K-12 launches still counted one generation on", d.Launched(5, 100 + 1300) == 2);
            Check("K-12 forgotten after two", d.TryAdd(5, 9, 100 + 1300) && d.Launched(5, 2000) == 0);
        }

        // K-13 lookup order (design §2.1): projectile -> weapon -> DamageDef -> unpatched; whole config, explicit 0 wins
        {
            var proj = new KbConfig { force = 0f };
            var weap = new KbConfig { force = 3f };
            var dmg = new KbConfig { force = 1f, ownCap = 9 };
            KbConfig c = KbLookup.Resolve(proj, weap, dmg, true, 0f);
            Check("K-13 projectile wins, explicit 0", c.force == 0f && c.source == "projectile");
            c = KbLookup.Resolve(null, new KbConfig { force = 3f }, dmg, true, 0f);
            Check("K-13 weapon next", c.force == 3f && c.source == "weapon" && c.ownCap == 0, "no field merge from DamageDef");
            c = KbLookup.Resolve(null, null, new KbConfig { force = 1f, ownCap = 9 }, true, 0f);
            Check("K-13 DamageDef next", c.force == 1f && c.ownCap == 9 && c.source == "damageDef");
            c = KbLookup.Resolve(null, null, null, true, 0.25f);
            Check("K-13 unpatched harmful", c.force == 0.25f && c.source == "unpatched");
            c = KbLookup.Resolve(null, null, null, false, 0.25f);
            Check("K-13 unpatched harmless", c.force == 0f && c.source == "none");
        }

        // K-14 per-request settings: own cap, impact factor, body-size override; the shared settings never change
        {
            var g = new KbSettings();
            KbSettings a = KbLookup.Apply(g, new KbConfig { force = 4f, ownCap = 10, impactFactor = 0f, massLimitOverride = 216f }, 6, 1f);
            Check("K-14 own cap", a.maxCells == 10);
            Check("K-14 global cap when unset", KbLookup.Apply(g, new KbConfig(), 6, 1f).maxCells == 6);
            Check("K-14 override", a.creatureMassLimit == 216f && g.creatureMassLimit == 150f);
            Check("K-14 centipede-weight 180 kg thrown by grav-ram", RM_KnockbackMath.Eligible(KbKind.Pawn, 180f, a));
            Check("K-14 180 kg spared under the global limit", !RM_KnockbackMath.Eligible(KbKind.Pawn, 180f, g));
            Check("K-14 a 240 kg pawn still spared", !RM_KnockbackMath.Eligible(KbKind.Pawn, 240f, a));
            Check("K-14 impact factor 0", RM_KnockbackMath.ImpactFor(5, 70f, a) == 0f && RM_KnockbackMath.ImpactFor(5, 70f, g) > 0f);
            var grid = new Grid(12, 3).Set(5, 1, KbCell.Wall);
            KbResult r0 = RM_KnockbackMath.Resolve(grid, 2, 1, 1f, 0f, 6, KbKind.Pawn, 70f, a);
            KbResult r1 = RM_KnockbackMath.Resolve(grid, 2, 1, 1f, 0f, 6, KbKind.Pawn, 70f, g);
            Check("K-14 wall stop, no impact with factor 0", r0.stop == KbStop.Wall && r0.impact == 0f && r1.impact > 0f,
                "impact " + r0.impact + " vs " + r1.impact);
            Check("K-14 factor scales linearly", Math.Abs(RM_KnockbackMath.ImpactFor(3, 70f, KbLookup.Apply(g, new KbConfig { impactFactor = 0.5f }, 6, 1f))
                - 0.5f * RM_KnockbackMath.ImpactFor(3, 70f, g)) < 1e-4f);
            // the thump cannon (force 2.5, cap 8) against the mortar (force 1) at d 0 / 1 for a 70 kg human (design §2.2)
            KbSettings th = KbLookup.Apply(g, new KbConfig { force = 2.5f, ownCap = 8 }, 6, 1f);
            Check("K-14 thump d0 = 8", RM_KnockbackMath.ThrowCells(0f, 1.9f, 2.5f, 70f, th) == 8);
            Check("K-14 thump d1 = 5 > mortar 3", RM_KnockbackMath.ThrowCells(1f, 1.9f, 2.5f, 70f, th) == 5
                && RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f, 70f, g) == 3);
        }

        // K-15 stun-lock guard (design §4, GPT #4)
        {
            Check("K-15 inside stun", !KbImmunity.CanLaunch(150, 100, 200, 120));
            Check("K-15 stun over, window running", !KbImmunity.CanLaunch(300, 100, 200, 120));
            Check("K-15 window over", KbImmunity.CanLaunch(320, 100, 200, 120));
            Check("K-15 window 0 = chain allowed", KbImmunity.CanLaunch(101, 100, 200, 0));
            Check("K-15 stun shorter than landing stamp", KbImmunity.CanLaunch(220, 100, 0, 120) && !KbImmunity.CanLaunch(219, 100, 0, 120));
        }

        // K-16 shield counter (owner Q4): debit force x per-force x loss-per-damage; a strong throw pops the belt
        {
            float e = KbShield.EnergyAfter(1.1f, 2.8f, 10f, 0.033f);
            Check("K-16 repulsor debit", Math.Abs(e - (1.1f - 0.924f)) < 1e-4f, "e=" + e);
            Check("K-16 grav-ram pops a 1.1 belt", KbShield.EnergyAfter(1.1f, 4f, 10f, 0.033f) < 0f);
            Check("K-16 zero debit setting", KbShield.EnergyAfter(1.1f, 4f, 0f, 0.033f) == 1.1f);
        }

        // K-17 flying goods rebound (RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD): the block cell, the reflection, the 70% rule
        {
            var kg = new KbSettings();
            var g1 = new Grid(12, 5).Set(6, 2, KbCell.Wall);
            KbResult w = RM_KnockbackMath.Resolve(g1, 2, 2, 1f, 0f, 6, KbKind.Item, 10f, kg);
            Check("K-17 wall block cell recorded", w.hasBlock && w.blockX == 6 && w.blockZ == 2 && w.blockFromX == 5
                && w.destX == 5 && w.cellsTravelled == 3, "block " + w.blockX + "," + w.blockZ + " dest " + w.destX);
            Check("K-17 straight hit flips x", RM_KnockbackMath.Reflect(g1, w, 1f, 0.2f, out float rx, out float rz)
                && rx == -1f && rz == 0.2f, rx + "," + rz);
            KbResult far = RM_KnockbackMath.Resolve(g1, 2, 2, 0f, 1f, 2, KbKind.Item, 10f, kg);
            Check("K-17 no solid hit, no block, no reflect", !far.hasBlock && far.stop == KbStop.Distance
                && !RM_KnockbackMath.Reflect(g1, far, 0f, 1f, out _, out _));
            var g2 = new Grid(10, 10);
            for (int x = 0; x < 10; x++) g2.Set(x, 6, KbCell.Wall);
            KbResult d = RM_KnockbackMath.Resolve(g2, 2, 2, 1f, 1f, 6, KbKind.Item, 10f, kg);
            RM_KnockbackMath.Reflect(g2, d, 1f, 1f, out float dx2, out float dz2);
            Check("K-17 diagonal into a long wall flips z only", d.hasBlock && dx2 == 1f && dz2 == -1f,
                "block " + d.blockX + "," + d.blockZ + " -> " + dx2 + "," + dz2);
            var g3 = new Grid(10, 10).Set(5, 5, KbCell.Wall);
            KbResult c = RM_KnockbackMath.Resolve(g3, 2, 2, 1f, 1f, 6, KbKind.Item, 10f, kg);
            RM_KnockbackMath.Reflect(g3, c, 1f, 1f, out float cx, out float cz);
            Check("K-17 bare corner flips both", c.hasBlock && cx == -1f && cz == -1f, cx + "," + cz);
            KbResult e = RM_KnockbackMath.Resolve(new Grid(6, 3), 2, 1, 1f, 0f, 6, KbKind.Item, 10f, kg);
            Check("K-17 map edge is a block", e.stop == KbStop.OutOfBounds && e.hasBlock && e.blockX == 6);
            Check("K-17 rebound 70% rounds down", RM_KnockbackMath.ReboundCells(5, 70f) == 3
                && RM_KnockbackMath.ReboundCells(3, 70f) == 2 && RM_KnockbackMath.ReboundCells(1, 70f) == 0
                && RM_KnockbackMath.ReboundCells(10, 70f) == 7);
            Check("K-17 rebound 0% / 100% / none left", RM_KnockbackMath.ReboundCells(5, 0f) == 0
                && RM_KnockbackMath.ReboundCells(5, 100f) == 5 && RM_KnockbackMath.ReboundCells(0, 70f) == 0
                && RM_KnockbackMath.ReboundCells(5, 150f) == 5);
            // a chain always ends: 8 cells at 70% -> 5, 3, 2, 1, 0
            int n = 8, legs = 0;
            while (n > 0 && legs < 50) { n = RM_KnockbackMath.ReboundCells(n, 70f); legs++; }
            Check("K-17 chain is finite", n == 0 && legs == 5, "legs " + legs);
            KbResult pit = RM_KnockbackMath.Resolve(new Grid(12, 3).Set(4, 1, KbCell.Pit), 2, 1, 1f, 0f, 6, KbKind.Item, 10f, kg);
            Check("K-17 a pit landing is no block", pit.stop == KbStop.Pit && !pit.hasBlock);
        }

        // K-18 creature mass limit (owner card 2026-11-13, "Cutoff -> A mass limit"; DEFAULTS.md rule 1): a living pawn heavier
        // than 150 kg is never thrown, whatever its body size; a corpse is weighed by the goods limit only
        {
            var g = new KbSettings();
            Check("K-18 a 144 kg pawn of body 2.4 thrown", RM_KnockbackMath.Eligible(KbKind.Pawn, 144f, g));
            Check("K-18 a 180 kg pawn of body 3.0 spared", !RM_KnockbackMath.Eligible(KbKind.Pawn, 180f, g));
            Check("K-18 a 240 kg pawn spared", !RM_KnockbackMath.Eligible(KbKind.Pawn, 240f, g));
            Check("K-18 a 300 kg pawn of body 1.0 spared (mass, not size)", !RM_KnockbackMath.Eligible(KbKind.Pawn, 300f, g));
            Check("K-18 a 100 kg pawn of body 3.0 thrown (size no longer counts)", RM_KnockbackMath.Eligible(KbKind.Pawn, 100f, g));
            Check("K-18 exactly 150 kg thrown (heavier than the limit is spared)", RM_KnockbackMath.Eligible(KbKind.Pawn, 150f, g));
            Check("K-18 a 60 kg corpse of body 3.0 thrown (goods limit only)", RM_KnockbackMath.Eligible(KbKind.Corpse, 60f, g));
            Check("K-18 a 76 kg corpse stays (goods limit)", !RM_KnockbackMath.Eligible(KbKind.Corpse, 76f, g));
        }

        // K-19 blast power = type force x this explosion's damage / the type's reference damage (owner card 2026-11-13,
        // "Blast power -> Type x damage"; DEFAULTS.md rule 2 and its showcase table: Bomb r 2.9, each creature 1 cell out)
        {
            var g = new KbSettings();
            Func<float, float, int> cellsAt = (mass, damage) =>
                RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f * RM_KnockbackMath.DamageRatio(damage, 50f, 100f, true), mass, g);
            Check("K-19 ratio at the type's own damage is 1", RM_KnockbackMath.DamageRatio(50f, 50f, 100f, true) == 1f);
            Check("K-19 ratio doubles with damage", RM_KnockbackMath.DamageRatio(100f, 50f, 100f, true) == 2f);
            Check("K-19 fire at its own damage keeps its half", RM_KnockbackMath.DamageRatio(10f, 10f, 100f, true) * 0.5f == 0.5f);
            Check("K-19 switch off = ratio 1", RM_KnockbackMath.DamageRatio(100f, 50f, 100f, false) == 1f
                && RM_KnockbackMath.DamageRatio(1f, 50f, 100f, false) == 1f);
            Check("K-19 no reference damage = ratio 1", RM_KnockbackMath.DamageRatio(100f, 0f, 100f, true) == 1f
                && RM_KnockbackMath.DamageRatio(100f, -3f, 100f, true) == 1f);
            Check("K-19 reference percent 200 halves the power", RM_KnockbackMath.DamageRatio(100f, 50f, 200f, true) == 1f);
            Check("K-19 reference percent 0 = ratio 1 (no divide by zero)", RM_KnockbackMath.DamageRatio(100f, 50f, 0f, true) == 1f);
            Check("K-19 negative damage is 0", RM_KnockbackMath.DamageRatio(-5f, 50f, 100f, true) == 0f);
            Check("K-19 rocket 24 of Bomb 50", Math.Abs(RM_KnockbackMath.DamageRatio(24f, 50f, 100f, true) - 0.48f) < 1e-5f);
            Check("K-19 a 12 kg pawn: 5 at 50, 6 (cap) at 100", cellsAt(12f, 50f) == 5 && cellsAt(12f, 100f) == 6, cellsAt(12f, 50f) + "/" + cellsAt(12f, 100f));
            Check("K-19 a 70 kg colonist: 3 at 50, 5 at 100", cellsAt(70f, 50f) == 3 && cellsAt(70f, 100f) == 5, cellsAt(70f, 50f) + "/" + cellsAt(70f, 100f));
            Check("K-19 a 144 kg pawn: 2 at 50, 4 at 100", cellsAt(144f, 50f) == 2 && cellsAt(144f, 100f) == 4, cellsAt(144f, 50f) + "/" + cellsAt(144f, 100f));
            Check("K-19 colonist band 64..76 kg keeps 12 kg > colonist > 144 kg", cellsAt(64f, 50f) == 3 && cellsAt(64f, 100f) == 5
                && cellsAt(76f, 50f) == 3 && cellsAt(76f, 100f) == 5);
            Check("K-19 a 240 kg pawn under a 250 limit: 1 at 50, 3 at 100", cellsAt(240f, 50f) == 1 && cellsAt(240f, 100f) == 3);
            Check("K-19 mortar beside a clothed colonist still 3 (calibration kept)", cellsAt(70f, 50f) == 3);
            Check("K-19 a 1-damage blast throws nothing", cellsAt(70f, 1f) == 0);
        }

        // K-20 the mass limit's per-weapon override (grav-ram 216 kg) and its setting
        {
            var g = new KbSettings();
            KbSettings gr = KbLookup.Apply(g, new KbConfig { force = 4f, ownCap = 10, massLimitOverride = 216f }, 6, 1f);
            Check("K-20 default limit 150 kg", g.creatureMassLimit == 150f);
            Check("K-20 override applied, shared untouched", gr.creatureMassLimit == 216f && g.creatureMassLimit == 150f);
            Check("K-20 grav-ram throws a 180 kg pawn", RM_KnockbackMath.Eligible(KbKind.Pawn, 180f, gr)
                && !RM_KnockbackMath.Eligible(KbKind.Pawn, 180f, g));
            Check("K-20 grav-ram throws a 216 kg pawn, never a 240 kg one", RM_KnockbackMath.Eligible(KbKind.Pawn, 216f, gr)
                && !RM_KnockbackMath.Eligible(KbKind.Pawn, 240f, gr));
            Check("K-20 unset override = the global limit", KbLookup.Apply(g, new KbConfig(), 6, 1f).creatureMassLimit == 150f);
            var hi = new KbSettings { creatureMassLimit = 250f };
            Check("K-20 limit 250 throws a 240 kg pawn", RM_KnockbackMath.Eligible(KbKind.Pawn, 240f, hi));
            Check("K-20 the override never touches goods", !RM_KnockbackMath.Eligible(KbKind.Item, 100f, gr)
                && !RM_KnockbackMath.Eligible(KbKind.Corpse, 100f, gr));
        }

        Console.WriteLine("explosive knockback kernel: " + pass + "/" + (pass + fail) + " passed");
        return fail == 0 ? 0 : 1;
    }
}
