using System;
using System.Collections.Generic;
using RimMandrake.ExplosiveKnockback;

// Offline kernel tests K-01..K-12 (design §8.1). Compiles the PRODUCTION RM_KnockbackMath.cs.
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

    private static int Main()
    {
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
        Check("K-03 immune pawn", !RM_KnockbackMath.Eligible(KbKind.Pawn, 60f, 2.5f, s));
        Check("K-03 human pawn", RM_KnockbackMath.Eligible(KbKind.Pawn, 60f, 1f, s));
        Check("K-03 heavy pawn still eligible", RM_KnockbackMath.Eligible(KbKind.Pawn, 300f, 1f, s));
        Check("K-03 heavy item", !RM_KnockbackMath.Eligible(KbKind.Item, 76f, 0f, s));
        Check("K-03 light item", RM_KnockbackMath.Eligible(KbKind.Item, 37.5f, 0f, s));
        Check("K-03 human corpse", RM_KnockbackMath.Eligible(KbKind.Corpse, 60f, 1f, s));
        Check("K-03 big corpse", !RM_KnockbackMath.Eligible(KbKind.Corpse, 60f, 3f, s));

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
            var budget = new KbTickBudget();
            int took = 0;
            for (int i = 0; i < 100; i++)
            {
                if (budget.TryTake(10, 60))
                {
                    took++;
                }
            }
            Check("K-11 tick cap", took == 60);
            Check("K-11 tick cap resets", budget.TryTake(11, 60));
        }

        // K-12 dedupe
        {
            var d = new KbDedupe();
            Check("K-12 first", d.TryAdd(5, 9));
            Check("K-12 repeat", !d.TryAdd(5, 9));
            Check("K-12 other explosion", d.TryAdd(6, 9));
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
            KbSettings a = KbLookup.Apply(g, new KbConfig { force = 4f, ownCap = 10, impactFactor = 0f, immuneOverride = 3.6f }, 6, 1f);
            Check("K-14 own cap", a.maxCells == 10);
            Check("K-14 global cap when unset", KbLookup.Apply(g, new KbConfig(), 6, 1f).maxCells == 6);
            Check("K-14 override", a.immuneBodySize == 3.6f && g.immuneBodySize == 2.5f);
            Check("K-14 3.5 body thrown under 3.6", RM_KnockbackMath.Eligible(KbKind.Pawn, 2000f, 3.5f, a));
            Check("K-14 3.5 body immune under global", !RM_KnockbackMath.Eligible(KbKind.Pawn, 2000f, 3.5f, g));
            Check("K-14 centipede 3.0 thrown by grav-ram", RM_KnockbackMath.Eligible(KbKind.Pawn, 1000f, 3.0f, a));
            Check("K-14 megasloth 4.0 still immune", !RM_KnockbackMath.Eligible(KbKind.Pawn, 2000f, 4.0f, a));
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

        Console.WriteLine("explosive knockback kernel: " + pass + "/" + (pass + fail) + " passed");
        return fail == 0 ? 0 : 1;
    }
}
