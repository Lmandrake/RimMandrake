using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.ExplosiveKnockback;

// Offline kernel tests K-01..K-22 (design §8.1). Compiles the PRODUCTION RM_KnockbackMath.cs.
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

    private static KbSettings cs0() => new KbSettings();

    /// <summary>--frame-fixtures DIR: read every RM_FrameProbe-format CSV in DIR (row,ms,paused,in_air) through the production
    /// KbFrameStats with the barrage window (0.9-8.25 s) and print one FIXTURE line each
    /// (selftest_explosiveknockback_barrage_p99.py checks them against its own reading).</summary>
    private static int FrameFixtures(string dir)
    {
        var inv = System.Globalization.CultureInfo.InvariantCulture;
        foreach (string f in System.IO.Directory.GetFiles(dir, "*.csv").OrderBy(x => x, StringComparer.Ordinal))
        {
            var ms = new List<float>(); var pz = new List<bool>(); var air = new List<int>();
            foreach (string line in System.IO.File.ReadLines(f).Skip(1))
            {
                string[] c = line.Split(',');
                if (c.Length < 4) continue;
                ms.Add(float.Parse(c[1], inv)); pz.Add(c[2] == "1"); air.Add(int.Parse(c[3], inv));
            }
            KbFrameSummary g = KbFrameStats.Summarize(ms.ToArray(), pz.ToArray(), air.ToArray(), ms.Count, ms.Sum() / 1000f, 0.9f, 8.25f);
            bool ok = KbFrameStats.WithinBudget(g, 50f, out string why);
            Console.WriteLine("FIXTURE " + System.IO.Path.GetFileName(f) + " windowRows=" + g.windowRows + " p99=" + g.windowP99Ms.ToString("0.0###", inv)
                + " worst=" + g.worstMs.ToString("0.0###", inv) + " probeS=" + (g.sumMs / 1000f).ToString("0.000", inv) + " verdict=" + (ok ? "PASS" : "FAIL")
                + (why == null ? "" : " why=" + why));
        }
        return 0;
    }

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
        int ff = Array.IndexOf(args, "--frame-fixtures");
        if (ff >= 0)
        {
            return FrameFixtures(args[ff + 1]);
        }
        if (args.Any(a => a.StartsWith("--map")))
        {
            return KnockbackMap.RunMap(args);
        }
        if (args.Contains("--sweep"))
        {
            return KnockbackSweep.Run();
        }
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
        // K-23 goods fly wild (blind cycle 1/2): the kernel's unrounded throw x wild, rounded and capped; never short of the kernel
        Check("K-23 wild: mortar d1 70 kg good flies 4 (2.62 x 1.6)", RM_KnockbackMath.WildCells(1f, 2.9f, 1f, 70f, cs0(), 1.6f) == 4);
        Check("K-23 wild 1 = the kernel", RM_KnockbackMath.WildCells(1f, 2.9f, 1f, 70f, cs0(), 1f) == RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f, 70f, cs0()));
        Check("K-23 wild never past the cap", RM_KnockbackMath.WildCells(0f, 2.9f, 1f, 1f, cs0(), 1.6f) == 6);
        // K-24 a gas burst's goods cap is exact: scaleOwnCap false ignores the own-max scale; a weapon's own max is scaled
        Check("K-24 gas cap 2 under scale 0.25 stays 2", KbLookup.Apply(cs0(), new KbConfig { ownCap = 2, scaleOwnCap = false }, 6, 0.25f).maxCells == 2);
        Check("K-24 weapon own max 4 under scale 0.5 is 2", KbLookup.Apply(cs0(), new KbConfig { ownCap = 4 }, 6, 0.5f).maxCells == 2);
        // K-14 container throw (owner card 2026-11-14: closed containers are thrown, as built; the dead slide kernel removed)
        var cs = new KbSettings();
        Check("K-14 container: 30 kg 1x1 at mortar d1 is thrown the item kernel's cells",
            RM_KnockbackMath.ContainerThrowCells(true, 30f, 250f, 1f, 2.9f, 1f, cs) == RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f, 30f, cs)
            && RM_KnockbackMath.ContainerThrowCells(true, 30f, 250f, 1f, 2.9f, 1f, cs) >= 1);
        Check("K-14 container: at the 250 kg limit still thrown", RM_KnockbackMath.ContainerThrowCells(true, 250f, 250f, 0f, 2.9f, 2f, cs) >= 1);
        Check("K-14 container: over the limit jolts (0 cells)", RM_KnockbackMath.ContainerThrowCells(true, 251f, 250f, 0f, 2.9f, 2f, cs) == 0);
        Check("K-14 container: the limit is the container limit, not the 75 kg goods limit", RM_KnockbackMath.ContainerThrowCells(true, 100f, 250f, 0f, 2.9f, 1f, cs) >= 1);
        Check("K-14 container: 2x1 jolts", RM_KnockbackMath.ContainerThrowCells(false, 20f, 250f, 1f, 2.9f, 1f, cs) == 0);
        Check("K-14 container: shorter than the same mass loose (wild)", RM_KnockbackMath.ContainerThrowCells(true, 30f, 250f, 1f, 2.9f, 1f, cs)
            <= RM_KnockbackMath.WildCells(1f, 2.9f, 1f, 30f, cs, 1.6f));
        Check("K-14 container: never past the cap", RM_KnockbackMath.ContainerThrowCells(true, 1f, 250f, 0f, 2.9f, 3f, cs) == cs.maxCells);
        // K-14 the jolt's drawn offset: above zero mid-jolt, never past its amplitude, 0 outside the jolt
        bool joltBounded = true, joltMoves = false;
        for (int tk = -3; tk <= 25; tk++)
        {
            RM_KnockbackMath.JoltOffset(tk, 20, 0.15f, 1f, 1f, out float jx, out float jz);
            float mag = (float)Math.Sqrt(jx * jx + jz * jz);
            joltBounded &= mag <= 0.15f + 1e-5f && ((tk >= 0 && tk < 20) || mag == 0f);
            joltMoves |= mag > 0.01f;
        }
        Check("K-14 jolt offset bounded by its amplitude and 0 outside the jolt", joltBounded);
        Check("K-14 jolt offset is above zero mid-jolt", joltMoves);
        RM_KnockbackMath.JoltOffset(5, 20, 0.15f, 0f, 0f, out float ex, out float ez);
        Check("K-14 jolt at the epicentre still shakes", ex != 0f || ez != 0f);
        RM_KnockbackMath.JoltOffset(5, 0, 0.15f, 1f, 0f, out float zx, out _);
        Check("K-14 jolt of 0 ticks draws nothing", zx == 0f);
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
            // a covered pit ends a throw IN it, as an open pit (scene sc_pit_fall: "on the covered cell the colonist and the stack
            // fall through ... and the cover is broken"; RIMMANDRAKE_DROP_THROWS_INTO_COVERED_PITS_K08_MUST_FLIP: this read
            // "K-08 cover is ground", destX 4, before)
            var gc = new Grid(10, 3).Set(2, 1, KbCell.CoveredPit);
            KbResult rc = RM_KnockbackMath.Resolve(gc, 0, 1, 1f, 0f, 4, KbKind.Pawn, 60f, s);
            Check("K-08 a throw over a cover ends in it", rc.destX == 2 && rc.stop == KbStop.Pit);
            KbResult rci = RM_KnockbackMath.Resolve(gc, 0, 1, 1f, 0f, 4, KbKind.Item, 1f, s);
            Check("K-08 a stack thrown over a cover ends in it", rci.destX == 2 && rci.stop == KbStop.Pit);
            Check("K-08 cover with pits off is a wall", RM_KnockbackMath.Resolve(gc, 0, 1, 1f, 0f, 4, KbKind.Pawn, 60f, off).destX == 1);
            Check("K-08 a throw short of a cover lands short", RM_KnockbackMath.Resolve(gc, 0, 1, 1f, 0f, 1, KbKind.Pawn, 60f, s).destX == 1);
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

        // K-21 heavy goods knock people (RIMMANDRAKE_KNOCK_PEOPLE_HEAVY_GOODS, owner card d_c_heavy_knock): a flying stack of at
        // least heavyGoodsMinMass reaching a standing person's cell hits (Blunt heavyGoodsDamageMin..Max, a stagger) and stops;
        // a lighter one passes unhurt. Defaults: on, 10 kg, 2..5, 30 ticks.
        {
            bool Hk(bool on, KbKind k, bool person, float m, float roll, out float d, out int st, float lo = 2f, float hi = 5f)
                => RM_KnockbackMath.HeavyKnock(on, k, person, m, 10f, lo, hi, roll, 30, out d, out st);
            bool hit = Hk(true, KbKind.Item, true, 15f, 0.5f, out float d1, out int st1);
            Check("K-21 15 kg steel on a person: hits, 2..5 blunt, 30-tick stagger, stops", hit && d1 >= 2f && d1 <= 5f && st1 == 30, d1 + "/" + st1);
            Check("K-21 roll 0 gives the minimum", Hk(true, KbKind.Item, true, 15f, 0f, out float d0, out _) && d0 == 2f, d0.ToString());
            Check("K-21 roll near 1 stays at or under the maximum", Hk(true, KbKind.Item, true, 15f, 0.9999f, out float d9, out _) && d9 <= 5f && d9 > 4.9f, d9.ToString());
            Check("K-21 exactly 10 kg hits (the threshold is inclusive)", Hk(true, KbKind.Item, true, 10f, 0.5f, out _, out _));
            Check("K-21 9.9 kg cloth passes, no damage, no stagger", !Hk(true, KbKind.Item, true, 9.9f, 0.5f, out float dl, out int sl) && dl == 0f && sl == 0);
            Check("K-21 no person on the cell: no hit", !Hk(true, KbKind.Item, false, 50f, 0.5f, out float dn, out _) && dn == 0f);
            Check("K-21 heavyGoodsKnock off: a heavy stack passes", !Hk(false, KbKind.Item, true, 50f, 0.5f, out float doff, out _) && doff == 0f);
            Check("K-21 a corpse and a pawn never use the goods knock", !Hk(true, KbKind.Corpse, true, 50f, 0.5f, out _, out _)
                && !Hk(true, KbKind.Pawn, true, 50f, 0.5f, out _, out _));
            Check("K-21 a max under the min collapses to the min", Hk(true, KbKind.Item, true, 15f, 0.7f, out float dc, out _, 4f, 1f) && dc == 4f, dc.ToString());
            Check("K-21 heavier never passes where lighter hits", Hk(true, KbKind.Item, true, 75f, 0.5f, out _, out _) && Hk(true, KbKind.Item, true, 10.01f, 0.5f, out _, out _));
        }

        // K-22 the frame-time probe's reading (RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF; leaves frame_time_probe and
        // barrage_frame_budget): one row per rendered frame, the worst frame is the max (never an average), a paused row
        // never counts as smooth, and a probe that samples once a second or per tick fails its self-check.
        {
            float[] Ms(int n, float v) { var a = new float[n]; for (int i = 0; i < n; i++) a[i] = v; return a; }
            bool[] Pz(int n, bool v) { var a = new bool[n]; for (int i = 0; i < n; i++) a[i] = v; return a; }
            int[] Air(int n, int v) { var a = new int[n]; for (int i = 0; i < n; i++) a[i] = v; return a; }
            float[] ok = Ms(300, 16.7f); ok[120] = 104f;                 // 300 frames at 60 fps, one slept frame
            int[] air = Air(300, 0); air[150] = 12;
            KbFrameSummary g = KbFrameStats.Summarize(ok, Pz(300, false), air, 300, 5.10f);
            Check("K-22 worst frame is the max row, not the mean", g.worstMs == 104f && g.meanMs < 20f, g.worstMs + "/" + g.meanMs);
            Check("K-22 self-check passes one row per frame with the 100 ms sleep seen", KbFrameStats.SelfCheck(g, 100f, out string why) , why);
            Check("K-22 rows carry the count of things in the air", g.maxInAir == 12);
            float[] slow = Ms(5, 1000f);                                  // once a second over the same 5 s, 300 frames rendered
            KbFrameSummary gs = KbFrameStats.Summarize(slow, Pz(5, false), Air(5, 0), 300, 5.0f);
            Check("K-22 a once-a-second sampler fails the self-check", !KbFrameStats.SelfCheck(gs, 100f, out string w1), w1);
            float[] tick = Ms(600, 8.3f);                                 // per tick (two ticks a frame): more rows than frames
            KbFrameSummary gt = KbFrameStats.Summarize(tick, Pz(600, false), Air(600, 0), 300, 5.0f);
            Check("K-22 a per-tick recorder fails the self-check", !KbFrameStats.SelfCheck(gt, 100f, out string w2), w2);
            KbFrameSummary gp = KbFrameStats.Summarize(ok, Pz(300, true), air, 300, 5.10f);
            Check("K-22 an all-paused run fails the self-check", !KbFrameStats.SelfCheck(gp, 100f, out string w3) && gp.pausedRows == 300, w3);
            Check("K-22 an all-paused run never passes the budget", !KbFrameStats.WithinBudget(gp, 50f, out _));
            float[] noSleep = Ms(300, 16.7f);
            KbFrameSummary gn = KbFrameStats.Summarize(noSleep, Pz(300, false), air, 300, 5.01f);
            Check("K-22 a probe that missed the slept frame fails the self-check", !KbFrameStats.SelfCheck(gn, 100f, out string w4), w4);
            Check("K-22 a smooth run passes the 50 ms budget", KbFrameStats.WithinBudget(gn, 50f, out _));
            // the bar is the p99 frame in the window (owner 2026-11-15, "1 agree."): one random stall is reported, not judged
            float[] stall = Ms(300, 16.7f); stall[200] = 151f;
            KbFrameSummary g1 = KbFrameStats.Summarize(stall, Pz(300, false), air, 300, 5.14f, 0.9f, 4.5f);
            bool ok1 = KbFrameStats.WithinBudget(g1, 50f, out string w5);
            Check("K-22 one 151 ms stall in the window is the worst frame but passes the p99 budget",
                g1.worstMs == 151f && g1.windowP99Ms < 20f && ok1, g1.windowP99Ms + " " + w5);
            float[] sus = Ms(300, 16.7f); for (int i = 100; i < 115; i++) sus[i] = 75f;   // 15 slow frames, 5% of the run
            KbFrameSummary g2 = KbFrameStats.Summarize(sus, Pz(300, false), air, 300, 5.9f, 0.9f, 5.5f);
            bool ok2 = KbFrameStats.WithinBudget(g2, 50f, out string w6);
            Check("K-22 a sustained stall (15 frames at 75 ms) in the window fails the p99 budget",
                g2.windowP99Ms == 75f && !ok2, g2.windowP99Ms + " " + w6);
            KbFrameSummary g3 = KbFrameStats.Summarize(sus, Pz(300, false), air, 300, 5.9f, 4.0f, 5.5f);
            Check("K-22 the same stall outside the window does not count", g3.windowP99Ms < 20f && KbFrameStats.WithinBudget(g3, 50f, out _), g3.windowP99Ms.ToString());
            KbFrameSummary g4 = KbFrameStats.Summarize(Ms(300, 16.7f), Pz(300, false), air, 300, 5.0f, 0.9f, 8.25f);
            bool ok4 = KbFrameStats.WithinBudget(g4, 50f, out string w7);
            Check("K-22 a probe stopped before the window closed fails", !ok4 && w7 != null && w7.Contains("before the window closed"), w7);
            Check("K-22 nearest-rank p99: 100 values 1..100 give 99, 1 value gives itself, none gives 0",
                KbFrameStats.Percentile(Enumerable.Range(1, 100).Select(i => (float)i).ToList(), 99f) == 99f
                && KbFrameStats.Percentile(new List<float> { 7f }, 99f) == 7f && KbFrameStats.Percentile(new List<float>(), 99f) == 0f);
            bool[] half = Pz(300, false); half[200] = true; float[] st2 = Ms(300, 16.7f); st2[200] = 400f;
            Check("K-22 a paused row's long frame is not the worst (paused rows are reported apart)",
                KbFrameStats.Summarize(st2, half, air, 300, 5.4f).worstMs == 16.7f && KbFrameStats.Summarize(st2, half, air, 300, 5.4f).pausedRows == 1);
            Check("K-22 no rows: summary is empty and nothing passes", !KbFrameStats.WithinBudget(KbFrameStats.Summarize(new float[0], new bool[0], new int[0], 0, 0f), 50f, out _));
        }

        // K-23 the fire-at-half switch (sheet "off: fire throws nothing"; blind cycle 3): every fire type the def patch
        // reaches is zeroed with the switch off, including Anomaly's ElectricalBurn, which inherits Flame's force 0.5
        // through ParentName="Flame" but carries its own hediff; a projectile's or weapon's tuning and non-fire types stay.
        {
            Check("K-23 switch off zeroes Flame's own force", RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "Flame", "Burn"));
            Check("K-23 switch off zeroes Burn (ParentName Flame)", RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "Burn", "Burn"));
            Check("K-23 switch off zeroes Anomaly's ElectricalBurn (ParentName Flame, hediff ElectricalBurn)",
                RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "ElectricalBurn", "ElectricalBurn"));
            Check("K-23 switch on: fire keeps its half", !RM_KnockbackMath.FireSwitchedOff(true, "damageDef", "Flame", "Burn")
                && !RM_KnockbackMath.FireSwitchedOff(true, "damageDef", "ElectricalBurn", "ElectricalBurn"));
            Check("K-23 a projectile's or weapon's own tuning is not switched", !RM_KnockbackMath.FireSwitchedOff(false, "projectile", "Flame", "Burn")
                && !RM_KnockbackMath.FireSwitchedOff(false, "weapon", "Flame", "Burn") && !RM_KnockbackMath.FireSwitchedOff(false, "unpatched", "Flame", "Burn"));
            Check("K-23 bombs, EMP, smoke, thump and tox gas are not fire",
                !RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "Bomb", "Shredded") && !RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "BombSuper", "Shredded")
                && !RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "EMP", null) && !RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "Smoke", null)
                && !RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "Thump", "Crush") && !RM_KnockbackMath.FireSwitchedOff(false, "damageDef", "ToxGas", null));
        }

        // K-24 a thrown stack landing on a covered pit cell breaks the cover (RIMMANDRAKE_BREAK_COVER_UNDER_LANDING_STACK_STILL_WHOLE;
        // certified leaf thrown_into_pit_falls: "falls through and leaves the cover broken", any stack, no mass floor). A gas
        // burst's throw (negative id) never breaks one (gas bursts never break pit covers); a closed container lands on free cells only.
        {
            Check("K-24 a blast-thrown stack on a covered cell breaks it", RM_KnockbackMath.LandingBreaksCover(KbKind.Item, true, false, 7));
            Check("K-24 a blast-thrown corpse on a covered cell breaks it", RM_KnockbackMath.LandingBreaksCover(KbKind.Corpse, true, false, 7));
            Check("K-24 any stack, however light: explosion id 0 counts as a blast", RM_KnockbackMath.LandingBreaksCover(KbKind.Item, true, false, 0));
            Check("K-24 no cover under the landing: nothing to break", !RM_KnockbackMath.LandingBreaksCover(KbKind.Item, false, false, 7));
            Check("K-24 a gas burst's throw never breaks a cover", !RM_KnockbackMath.LandingBreaksCover(KbKind.Item, true, false, -3));
            Check("K-24 a closed container's landing never breaks one", !RM_KnockbackMath.LandingBreaksCover(KbKind.Item, true, true, 7));
            // flipped by RIMMANDRAKE_DROP_THROWS_INTO_COVERED_PITS_K08_MUST_FLIP (sc_pit_fall: the colonist falls through, cover broken)
            Check("K-24 a blast-thrown pawn on a covered cell breaks it", RM_KnockbackMath.LandingBreaksCover(KbKind.Pawn, true, false, 7));
            Check("K-24 a gas-shoved pawn never breaks a cover", !RM_KnockbackMath.LandingBreaksCover(KbKind.Pawn, true, false, -3));
        }

        // K-25 a pawn standing on a pit cover blocks a thrown pawn as on any ground (bar pawn_hits_pawn_stops; blind cycle 5,
        // RIMMANDRAKE_STOP_KNOCKBACK_THROW_AT_PAWN_ON_PIT_COVER: the grid answered CoveredPit before it looked for a pawn)
        {
            Check("K-25 a pawn on a cover blocks a thrown pawn", RM_KnockbackMath.PitCell(true, true, true) == KbCell.Pawn);
            Check("K-25 a pawn in an open pit blocks a thrown pawn", RM_KnockbackMath.PitCell(false, true, true) == KbCell.Pawn);
            Check("K-25 an empty cover is ground", RM_KnockbackMath.PitCell(true, true, false) == KbCell.CoveredPit);
            Check("K-25 an empty open pit is a pit", RM_KnockbackMath.PitCell(false, true, false) == KbCell.Pit);
            Check("K-25 goods pass a pawn on a cover", RM_KnockbackMath.PitCell(true, false, true) == KbCell.CoveredPit);
            Check("K-25 goods fall past a pawn in an open pit", RM_KnockbackMath.PitCell(false, false, true) == KbCell.Pit);
            var g = new Grid(10, 3).Set(3, 1, KbCell.Pawn);   // the grid's answer for a cover with a pawn on it
            var r = RM_KnockbackMath.Resolve(g, 1, 1, 1f, 0f, 3, KbKind.Pawn, 70f, new KbSettings());
            Check("K-25 the thrown pawn stops on the cell before, both hit", r.destX == 2 && r.stop == KbStop.Pawn && r.hitOther && r.impact > 0f);
        }

        // V-01..V-06 the proof scenes' verdict and plan arithmetic (RM_KnockbackVerdicts.cs; blind cycle 5,
        // RIMMANDRAKE_LIFT_PROOF_VERDICTS_INTO_TESTED_CODE_NINE_SLIPPED: nine faults planted in these lines stayed green
        // offline while they lived in the Verse scenes). Each verdict's pass edge and every way it must fail.
        {
            // V-01 sc_calibration: exactly 3 cells, straight away, alive, one launch line (bar people_thrown_three_cells)
            bool V1(int cells, bool spawned, int x, int z, bool alive, int launches) =>
                RM_KnockbackVerdicts.Calibration(cells, spawned, x, z, 10, 10, alive, launches, out _);
            Check("V-01 calibration passes at 3 cells straight away", V1(3, true, 13, 10, true, 1)
                && RM_KnockbackVerdicts.Calibration(3, true, 13, 10, 10, 10, true, 1, out bool away1) && away1);
            Check("V-01 calibration fails at 2 and at 4 cells, and at 0", !V1(2, true, 12, 10, true, 1) && !V1(4, true, 14, 10, true, 1) && !V1(0, true, 10, 10, true, 0));
            Check("V-01 calibration fails off the row, toward the blast, or unspawned",
                !V1(3, true, 13, 11, true, 1) && !V1(3, true, 7, 10, true, 1) && !V1(3, false, 13, 10, true, 1));
            Check("V-01 calibration fails dead, with no launch line or with two", !V1(3, true, 13, 10, false, 1) && !V1(3, true, 13, 10, true, 0) && !V1(3, true, 13, 10, true, 2));

            // V-02 goods plan (WantCells, WantCellsFrom, PlanGood): 0 over the light-goods mass limit, else WildCells at the wild factor
            KbSettings ks = cs0();
            Check("V-02 sanity: the kernel alone would throw a 76 kg good at d1", RM_KnockbackMath.WildCells(1f, 2.9f, 1f, ks.lightMassLimit + 1f, ks, 1.6f) > 0,
                "WildCells=" + RM_KnockbackMath.WildCells(1f, 2.9f, 1f, ks.lightMassLimit + 1f, ks, 1.6f));
            Check("V-02 a good over the mass limit is not planned", RM_KnockbackVerdicts.GoodCells(1f, 2.9f, ks.lightMassLimit + 1f, ks, 1.6f) == 0);
            Check("V-02 a good at the mass limit is planned by the kernel", RM_KnockbackVerdicts.GoodCells(1f, 2.9f, ks.lightMassLimit, ks, 1.6f)
                == RM_KnockbackMath.WildCells(1f, 2.9f, 1f, ks.lightMassLimit, ks, 1.6f) && RM_KnockbackVerdicts.GoodCells(1f, 2.9f, ks.lightMassLimit, ks, 1.6f) > 0);
            var ks10 = cs0();
            ks10.lightMassLimit = 10f;
            Check("V-02 the limit is the setting's: 11 kg over a 10 kg limit is not planned, 10 kg is",
                RM_KnockbackVerdicts.GoodCells(1f, 2.9f, 11f, ks10, 1.6f) == 0 && RM_KnockbackVerdicts.GoodCells(1f, 2.9f, 10f, ks10, 1.6f) > 0);
            Check("V-02 goods are planned wild: 70 kg at d1 flies 4, not the plain kernel's",
                RM_KnockbackVerdicts.GoodCells(1f, 2.9f, 70f, ks, 1.6f) == 4 && RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f, 70f, ks) != 4,
                "goods=" + RM_KnockbackVerdicts.GoodCells(1f, 2.9f, 70f, ks, 1.6f) + " kernel=" + RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f, 70f, ks));
            Check("V-02 the wild factor is the caller's", RM_KnockbackVerdicts.GoodCells(1f, 2.9f, 70f, ks, 1f) == RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f, 70f, ks));
            Check("V-02 out of reach is 0", RM_KnockbackVerdicts.GoodCells(5f, 2.9f, 1f, ks, 1.6f) == 0);

            // V-03 sc_goods_obstacles start assertion (obstacle column 13, origin 10)
            string V3(string lane, bool control, KbStop stop, int destX, int want, float keep = 70f) =>
                RM_KnockbackVerdicts.ObstaclePlan(lane, control, stop, destX, 13, 10, want, keep, out _);
            Check("V-03 control lane lands past the column on a full-distance flight", V3("D", true, KbStop.Distance, 14, 4) == null && V3("W", true, KbStop.Distance, 15, 5) == null);
            Check("V-03 control lane short of or on the column is refused", V3("D", true, KbStop.Distance, 13, 3) != null && V3("S", true, KbStop.Distance, 12, 2) != null);
            Check("V-03 control lane stopped by anything is refused", V3("D", true, KbStop.Door, 14, 4) != null && V3("W", true, KbStop.Water, 14, 4) != null
                && V3("S", true, KbStop.Wall, 15, 5) != null);
            Check("V-03 door lane with cells to rebound passes and reports them",
                RM_KnockbackVerdicts.ObstaclePlan("D", false, KbStop.Door, 12, 13, 10, 4, 70f, out int back4) == null && back4 == 2, "back=" + back4);
            Check("V-03 door lane with no cell left to rebound is refused", V3("D", false, KbStop.Door, 12, 1) != null && V3("D", false, KbStop.Door, 12, 2) != null
                && V3("D", false, KbStop.Door, 12, 4, 0f) != null);
            Check("V-03 door lane that never meets the door is refused", V3("D", false, KbStop.Distance, 14, 4) != null && V3("D", false, KbStop.Wall, 12, 4) != null);
            Check("V-03 sandbag lane past the column passes, short of it is refused", V3("S", false, KbStop.Distance, 14, 4) == null
                && V3("S", false, KbStop.Distance, 13, 3) != null && V3("S", false, KbStop.PartialCover, 12, 4) != null);
            Check("V-03 water lane: a Water stop on the last cell before it only", V3("W", false, KbStop.Water, 12, 4) == null
                && V3("W", false, KbStop.Water, 11, 4) != null && V3("W", false, KbStop.Distance, 12, 2) != null && V3("W", false, KbStop.Distance, 15, 5) != null);

            // V-04 sc_hose_drop_control: the blast alone never drops the hose (no launch, still carrying on the takeoff cell, hurt)
            Check("V-04 hose control passes still carrying, hurt, no launch", RM_KnockbackVerdicts.HoseControl(0, "Carrying", "p", "5,5", "5,5", true));
            Check("V-04 hose control fails on a launch line", !RM_KnockbackVerdicts.HoseControl(1, "Carrying", "p", "5,5", "5,5", true));
            Check("V-04 hose control fails dropped, carried by another or moved", !RM_KnockbackVerdicts.HoseControl(0, "Dropped", "p", "5,5", "5,5", true)
                && !RM_KnockbackVerdicts.HoseControl(0, "Carrying", "none", "5,5", "5,5", true) && !RM_KnockbackVerdicts.HoseControl(0, "Carrying", "p", "6,5", "5,5", true));
            Check("V-04 hose control fails unhurt (the blast did not land)", !RM_KnockbackVerdicts.HoseControl(0, "Carrying", "p", "5,5", "5,5", false));

            // V-05 sc_hose_drop: one launch that dropped the hose, the end on the takeoff cell, landing 3 cells out
            bool V5(int launches, bool flag, string carry, string carrier, string end, int cheb) =>
                RM_KnockbackVerdicts.HoseDrop(launches, flag, carry, carrier, end, "5,5", cheb, out _, out _, out _);
            Check("V-05 hose drop passes", V5(1, true, "Dropped", "none", "5,5", 3));
            Check("V-05 hose drop fails at 2 or 4 cells or with no landing cell", !V5(1, true, "Dropped", "none", "5,5", 2) && !V5(1, true, "Dropped", "none", "5,5", 4)
                && !V5(1, true, "Dropped", "none", "5,5", -1));
            Check("V-05 hose drop fails with no or two launches, or the launch not dropping it", !V5(0, true, "Dropped", "none", "5,5", 3)
                && !V5(2, true, "Dropped", "none", "5,5", 3) && !V5(1, false, "Dropped", "none", "5,5", 3));
            Check("V-05 hose drop fails still carried, or the end elsewhere", !V5(1, true, "Carrying", "p", "5,5", 3) && !V5(1, true, "Dropped", "none", "8,5", 3));

            // V-06 PitProbe's start gate: INVALID unless hauler there and spawned, steel there, a map current
            string V6(bool h, bool hs, bool st, bool map) => RM_KnockbackVerdicts.PitProbeMissing("pit_goods_fetch", h, hs, false, null, st, true, false, null, map);
            Check("V-06 pit probe runs with everything there", V6(true, true, true, true) == null);
            bool allInvalid = true;
            foreach (var c in new[] { (false, false, true, true), (true, false, true, true), (true, true, false, true), (true, true, true, false), (false, false, false, false) })
            {
                string v = V6(c.Item1, c.Item2, c.Item3, c.Item4);
                allInvalid &= v != null && v.StartsWith("INVALID pit_goods_fetch hauler or steel missing");
            }
            Check("V-06 pit probe reads INVALID for each missing piece", allInvalid);

            // V-07 sc_goods_fly_off (blind cycle 3's PF_PROOF_FLYOFF_SKIP_UNCHECKED): skipped flying_off, unmoved, never in the air
            Check("V-07 fly-off passes skipped, unmoved, whole", RM_KnockbackVerdicts.FlyOff(true, true, true, true, 0, 75, 75));
            Check("V-07 fly-off fails without the flying_off skip line", !RM_KnockbackVerdicts.FlyOff(false, true, true, true, 0, 75, 75));
            Check("V-07 fly-off fails moved, in the air, a cell off, gone or split", !RM_KnockbackVerdicts.FlyOff(true, false, true, true, 0, 75, 75)
                && !RM_KnockbackVerdicts.FlyOff(true, true, false, true, 0, 75, 75) && !RM_KnockbackVerdicts.FlyOff(true, true, true, true, 1, 75, 75)
                && !RM_KnockbackVerdicts.FlyOff(true, true, true, false, 0, 75, 75) && !RM_KnockbackVerdicts.FlyOff(true, true, true, true, 0, 74, 75));

            // V-08 sc_goods_obstacles' per-lane verdict (column 13, lane row 10); blind cycle 3's PF_GO_WALL_POSITION_UNCHECKED, PF_GO_WATER_UNCHECKED
            bool V8(string lane, bool control, int x, int z, bool rest = true, bool flew = true, int planX = 15, int planZ = 10, bool bounced = true,
                bool closed = true, bool dry = true, bool visible = true, int inWater = 0, int hops = 0, int hidden = 0) =>
                RM_KnockbackVerdicts.ObstacleLane(lane, control, rest, flew, x, z, planX, planZ, 13, 10, bounced, closed, dry, visible, inWater, hops, hidden);
            Check("V-08 control lane passes on its planned cell only", V8("D", true, 15, 10) && !V8("D", true, 14, 10) && !V8("D", true, 15, 11) && !V8("S", true, 16, 10));
            Check("V-08 control lane fails unflown or not at rest", !V8("W", true, 15, 10, flew: false) && !V8("W", true, 15, 10, rest: false));
            Check("V-08 door lane passes bounced back to the blast side, door shut", V8("D", false, 11, 10));
            Check("V-08 door lane fails unbounced, door open, through or on the door", !V8("D", false, 11, 10, bounced: false)
                && !V8("D", false, 11, 10, closed: false) && !V8("D", false, 13, 10) && !V8("D", false, 14, 10) && !V8("D", false, 11, 10, flew: false));
            Check("V-08 sandbag lane passes past the bags in its row", V8("S", false, 15, 10) && !V8("S", false, 13, 10) && !V8("S", false, 15, 11)
                && !V8("S", false, 15, 10, flew: false));
            Check("V-08 water lane passes dry on the last cell before it", V8("W", false, 12, 10));
            Check("V-08 water lane fails drawn on water even once, wet, fogged or off the cell", !V8("W", false, 12, 10, inWater: 1)
                && !V8("W", false, 12, 10, dry: false) && !V8("W", false, 12, 10, visible: false) && !V8("W", false, 11, 10) && !V8("W", false, 12, 9));
            Check("V-08 every lane fails on a hop or hidden, or still flying", !V8("S", false, 15, 10, hops: 1) && !V8("W", false, 12, 10, hidden: 1)
                && !V8("D", true, 15, 10, hops: 1) && !V8("D", false, 11, 10, rest: false));

            // V-09 lane D's rebound: off the door, ReboundCells(left, keep%) cells
            Check("V-09 door rebound reads the kernel's rebound", RM_KnockbackVerdicts.DoorBounced(1, "Door", 3, RM_KnockbackMath.ReboundCells(3, 70f), 70f)
                && !RM_KnockbackVerdicts.DoorBounced(1, "Door", 3, RM_KnockbackMath.ReboundCells(3, 70f) + 1, 70f)
                && !RM_KnockbackVerdicts.DoorBounced(1, "Wall", 3, RM_KnockbackMath.ReboundCells(3, 70f), 70f) && !RM_KnockbackVerdicts.DoorBounced(0, "Door", 3, 2, 70f));

            // V-10 sc_closed_containers, a thrown container (blind cycle 3's PF_ST3_CONTAINER_ZERO_CELLS_OK)
            Check("V-10 container thrown 1..cap cells away, held", RM_KnockbackVerdicts.ContainerThrown(1, 6, true, true, true) && RM_KnockbackVerdicts.ContainerThrown(6, 6, true, true, true));
            Check("V-10 container unmoved, past the cap or gone fails", !RM_KnockbackVerdicts.ContainerThrown(0, 6, true, true, true)
                && !RM_KnockbackVerdicts.ContainerThrown(7, 6, true, true, true) && !RM_KnockbackVerdicts.ContainerThrown(-1, 6, true, true, true));
            Check("V-10 container toward the blast, not journalled thrown or spilled fails", !RM_KnockbackVerdicts.ContainerThrown(2, 6, false, true, true)
                && !RM_KnockbackVerdicts.ContainerThrown(2, 6, true, false, true) && !RM_KnockbackVerdicts.ContainerThrown(2, 6, true, true, false));

            // V-11 sc_spared's start assertion (visit 4 2026-11-23: a carrier off the blast read FAIL; it says nothing, so INVALID)
            Check("V-11 a spared thing on its staged cell at the blast is in the scene", RM_KnockbackVerdicts.SparedOffCell("carrier", true, 5, 9, 5, 9) == null);
            Check("V-11 a spared thing one cell off either way, or gone, is named", RM_KnockbackVerdicts.SparedOffCell("carrier", true, 6, 9, 5, 9) == "carrier at 6,9, staged 5,9"
                && RM_KnockbackVerdicts.SparedOffCell("big", true, 5, 8, 5, 9) != null && RM_KnockbackVerdicts.SparedOffCell("pit", false, 5, 9, 5, 9) == "pit not on the map");
        }

        // ── 0.2.0 (RIMMANDRAKE_AUTOBUILD_EXPLOSIVEKNOCKBACK_SIX_BARS_LEFT): the four kernel bars of Stage 3. Each case is a
        // named check plus a sweep over its declared range; each sweep prints its cases read and its worst value.
        var inv = System.Globalization.CultureInfo.InvariantCulture;
        var q0 = new KbRules();
        Func<float, float, KbFacts> pawnAt = (x, m) => new KbFacts { kind = KbKind.Pawn, thingId = 11, x = (int)x, z = 2, mass = m };

        // K_CARRY_OWN_PLAN (bar carried_thing_own_arc): the carried thing gets a plan of its own, for its own mass, from the
        // carrier's cell; one too heavy to fly comes to rest on the carrier's start cell; the carrier's own plan is unchanged.
        {
            var w = new MWorld(30, 5);
            var b = new KbBlast { id = 7, cx = 2, cz = 2, radius = 2.9f, force = 1f };
            KbFacts carrier = pawnAt(3, 70f);
            KbPlan alone = KbPlanner.Decide(carrier, b, q0, new KbSettings(), w);
            KbPlan cp = KbPlanner.Carried(carrier, 12, KbKind.Item, 10f, b, q0, new KbSettings(), w);
            KbPlan with = KbPlanner.Decide(carrier, b, q0, new KbSettings(), w);
            Check("K_CARRY_OWN_PLAN a 10 kg stack carried by a thrown 70 kg colonist flies on its own plan",
                alone.act == KbAct.LaunchPawn && cp != null && cp.act == KbAct.ThrowGoods && cp != alone && cp.mass == 10f,
                "pawn " + alone.act + " stack " + cp?.act);
            Check("K_CARRY_OWN_PLAN the lighter stack flies farther than its carrier", cp.cells > alone.cells && cp.first.res.cellsTravelled > alone.res.cellsTravelled,
                "stack " + cp.cells + "/" + cp.first.res.cellsTravelled + " pawn " + alone.cells + "/" + alone.res.cellsTravelled);
            KbPlanner.CarriedRest(cp, carrier, out int rx, out int rz);
            Check("K_CARRY_OWN_PLAN the stack comes to rest where its own flight ends", rx == cp.first.res.destX && rz == cp.first.res.destZ && (rx != alone.res.destX || rz != alone.res.destZ),
                rx + "," + rz + " pawn " + alone.res.destX + "," + alone.res.destZ);
            KbPlan hv = KbPlanner.Carried(carrier, 13, KbKind.Item, 120f, b, q0, new KbSettings(), w);
            KbPlanner.CarriedRest(hv, carrier, out int hx, out int hz);
            Check("K_CARRY_OWN_PLAN a carried thing too heavy to fly drops on the carrier's start cell", !hv.Throws && hv.reason == "too_heavy" && hx == 3 && hz == 2,
                hv.act + " " + hv.reason + " at " + hx + "," + hz);
            Check("K_CARRY_OWN_PLAN the carrier plans as one who carries nothing", with.act == alone.act && with.cells == alone.cells
                && with.res.destX == alone.res.destX && with.res.destZ == alone.res.destZ && with.res.impact == alone.res.impact);
            KbPlan corpse = KbPlanner.Carried(carrier, 14, KbKind.Corpse, 40f, b, q0, new KbSettings(), w);
            Check("K_CARRY_OWN_PLAN a carried corpse flies as a corpse", corpse.act == KbAct.ThrowGoods && corpse.kind == KbKind.Corpse);
            KbPlan off = KbPlanner.Carried(carrier, 15, KbKind.Item, 10f, b, new KbRules { throwItems = false }, new KbSettings(), w);
            KbPlanner.CarriedRest(off, carrier, out int ox, out int oz);
            Check("K_CARRY_OWN_PLAN items switched off: the stack drops where the carrier stood", !off.Throws && ox == 3 && oz == 2, off.act + " " + off.reason);
            // the range: carrier 40-150 kg, 0-2.9 cells from a 2.9 or 1.9 blast, carried 0.1-200 kg, walls 1-8 cells out
            int cases = 0, bad = 0; string worst = "none";
            foreach (float rad in new[] { 1.9f, 2.9f })
            foreach (int d in new[] { 0, 1, 2 })
            foreach (float pm in new[] { 40f, 70f, 110f, 150f })
            foreach (float cm in new[] { 0.1f, 1f, 5f, 10f, 30f, 60f, 74f, 76f, 120f, 200f })
            foreach (int wall in new[] { 0, 1, 2, 4, 8 })
            {
                var ww = new MWorld(30, 5);
                if (wall > 0) for (int z = 0; z < 5; z++) ww.terr[2 + d + wall, z] = KbCell.Wall;
                var bb = new KbBlast { id = 9, cx = 2, cz = 2, radius = rad, force = 1f };
                KbFacts c = new KbFacts { kind = KbKind.Pawn, thingId = 21, x = 2 + d, z = 2, mass = pm };
                KbPlan pp = KbPlanner.Decide(c, bb, q0, new KbSettings(), ww);
                KbPlan tp = KbPlanner.Carried(c, 22, KbKind.Item, cm, bb, q0, new KbSettings(), ww);
                KbPlanner.CarriedRest(tp, c, out int qx, out int qz);
                cases++;
                bool eligible = RM_KnockbackMath.Eligible(KbKind.Item, cm, new KbSettings());
                string why = null;
                if (tp == null) why = "no plan";
                else if (!eligible && tp.Throws) why = "a thing over the light mass limit flew";
                else if (!tp.Throws && (qx != c.x || qz != c.z)) why = "an unthrown carried thing rests off the start cell";
                else if (tp.Throws && pp.act == KbAct.LaunchPawn && cm < pm && tp.kernelCells < pp.kernelCells) why = "a lighter carried thing planned shorter than its carrier";
                else if (tp.Throws && Math.Abs(qx - c.x) + Math.Abs(qz - c.z) > 30) why = "rest cell off the map";
                if (why != null) { bad++; worst = why + " (radius " + rad + " d " + d + " carrier " + pm + " carried " + cm + " wall " + wall + ")"; }
            }
            Check("K_CARRY_OWN_PLAN sweep", bad == 0, worst);
            Console.WriteLine("K_CARRY_OWN_PLAN sweep: " + cases + " cases read, " + bad + " failing, worst: " + worst + " (limit: 0 failing)");
        }

        // K_COLLISION_BRUISE (bar collision_bruise_by_size): each pawn's bruise follows the OTHER's mass against its own
        {
            var sb = new KbSettings();
            float like = RM_KnockbackMath.CollisionBruise(70f, 70f, sb);
            float oneCell = RM_KnockbackMath.ImpactFor(1, 70f, sb);
            Check("K_COLLISION_BRUISE a like pair bruise each other alike, lightly", like > 0f && like <= oneCell + 1e-4f,
                "70/70 = " + like.ToString("0.###", inv) + ", one cell of wall impact at 70 kg = " + oneCell.ToString("0.###", inv));
            float onRat = RM_KnockbackMath.CollisionBruise(1f, 70f, sb), onPerson = RM_KnockbackMath.CollisionBruise(70f, 1f, sb);
            Check("K_COLLISION_BRUISE a person on a rat: the rat is hurt many times more, the person nearly not",
                onRat >= 20f * onPerson && onPerson < 0.25f && onRat > like, "rat " + onRat.ToString("0.###", inv) + " person " + onPerson.ToString("0.###", inv));
            float dogHit = RM_KnockbackMath.CollisionBruise(30f, 70f, sb), personHit = RM_KnockbackMath.CollisionBruise(70f, 30f, sb);
            Check("K_COLLISION_BRUISE a person and a dog: the dog takes more", dogHit > personHit && personHit > 0f);
            float bigOnSmall = RM_KnockbackMath.CollisionBruise(1f, 2000f, sb), bigTakes = RM_KnockbackMath.CollisionBruise(2000f, 1f, sb);
            Check("K_COLLISION_BRUISE a rat on an elephant-sized creature: the big one has nothing to treat", bigTakes < 0.01f && bigOnSmall > like);
            Check("K_COLLISION_BRUISE no other pawn, or a bad mass, bruises nobody", RM_KnockbackMath.CollisionBruise(70f, 0f, sb) == 0f
                && RM_KnockbackMath.CollisionBruise(0f, 70f, sb) == 0f && RM_KnockbackMath.CollisionBruise(-5f, 70f, sb) == 0f
                && RM_KnockbackMath.CollisionBruise(float.NaN, 70f, sb) == 0f && RM_KnockbackMath.CollisionBruise(70f, float.NaN, sb) == 0f
                && RM_KnockbackMath.CollisionBruise(float.PositiveInfinity, 70f, sb) == 0f && RM_KnockbackMath.CollisionBruise(70f, float.PositiveInfinity, sb) == 0f);
            Check("K_COLLISION_BRUISE impact switched off, or a blast with no impact (palm thumper), bruises nobody",
                RM_KnockbackMath.CollisionBruise(1f, 70f, new KbSettings { impactEnabled = false }) == 0f
                && RM_KnockbackMath.CollisionBruise(1f, 70f, new KbSettings { impactFactor = 0f }) == 0f);
            // a throw stopped by a standing pawn: the same rule, both ways (leaf pawn_hits_pawn_stops keeps its hit)
            var g = new Grid(10, 3).Set(2, 1, KbCell.Pawn);
            KbResult r = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 4, KbKind.Pawn, 70f, sb);
            KbPlanner.Collide(ref r, 70f, 1f, sb);
            Check("K_COLLISION_BRUISE a person thrown into a rat: the rat takes the bruise by size, the person a scratch",
                r.hitOther && r.destX == 1 && r.otherImpact == RM_KnockbackMath.CollisionBruise(1f, 70f, sb) && r.impact == RM_KnockbackMath.CollisionBruise(70f, 1f, sb),
                "impact " + r.impact + " other " + r.otherImpact);
            KbResult r2 = RM_KnockbackMath.Resolve(g, 0, 1, 1f, 0f, 4, KbKind.Pawn, 70f, sb);
            KbPlanner.Collide(ref r2, 70f, 70f, sb);
            Check("K_COLLISION_BRUISE a person thrown into a person: both take an impact hit, alike", r2.impact > 0f && r2.impact == r2.otherImpact);
            KbResult r3 = RM_KnockbackMath.Resolve(new Grid(10, 3).Set(2, 1, KbCell.Wall), 0, 1, 1f, 0f, 4, KbKind.Pawn, 70f, sb);
            float wallHit = r3.impact;
            KbPlanner.Collide(ref r3, 70f, 70f, sb);
            Check("K_COLLISION_BRUISE a throw that met no pawn keeps its own hit and bruises nobody", !r3.hitOther && r3.otherImpact == 0f && r3.impact == wallHit);
            // the range: own and other mass 0.5-2000 kg (geometric, 41 steps each), the impact setting 0.5-3 x
            float[] ms = Enumerable.Range(0, 41).Select(i => (float)(0.5 * Math.Pow(4000.0, i / 40.0))).ToArray();
            int cases = 0, bad = 0; string worst = "none"; float worstLike = 0f;
            foreach (float ipc in new[] { 2f, 4f, 12f })
            {
                var st = new KbSettings { impactPerCell = ipc };
                for (int i = 0; i < ms.Length; i++)
                for (int j = 0; j < ms.Length; j++)
                {
                    cases++;
                    float a = RM_KnockbackMath.CollisionBruise(ms[i], ms[j], st);
                    string why = null;
                    if (!(a >= 0f) || float.IsInfinity(a)) why = "not a finite amount";
                    else if (j > 0 && a + 1e-5f < RM_KnockbackMath.CollisionBruise(ms[i], ms[j - 1], st)) why = "fell as the other's mass rose";
                    else if (i > 0 && a > RM_KnockbackMath.CollisionBruise(ms[i - 1], ms[j], st) + 1e-5f) why = "rose as its own mass rose";
                    else if (i == j && Math.Abs(a - RM_KnockbackMath.CollisionBruise(ms[j], ms[i], st)) > 1e-4f) why = "a like pair not alike";
                    if (i == j) worstLike = Math.Max(worstLike, a / RM_KnockbackMath.ImpactFor(1, 70f, st));
                    if (why != null) { bad++; worst = why + " (own " + ms[i] + " other " + ms[j] + " impactPerCell " + ipc + ")"; }
                }
            }
            Check("K_COLLISION_BRUISE sweep", bad == 0 && worstLike <= 1f + 1e-4f, worst + "; like pair at most " + worstLike + " of one cell's wall hit");
            Console.WriteLine("K_COLLISION_BRUISE sweep: " + cases + " cases read, " + bad + " failing, worst: " + worst + "; a like pair's bruise at most "
                + worstLike.ToString("0.###", inv) + " of one cell's wall hit at 70 kg (limit 1)");
        }

        // K_GAS_COVER_SHOVE (bar gas_shoves_pawn_on_pit_cover): a burning-gas burst shoves a person on an intact cover one cell,
        // as on any floor; a person down in an open pit is not shoved; a blast still skips them (its blast breaks the cover)
        {
            var w = new MWorld(20, 5);
            var gas = new KbBlast { id = -4, cx = 4, cz = 2, radius = 2.4f, force = 1f, gas = true };
            var blast = new KbBlast { id = 4, cx = 4, cz = 2, radius = 2.9f, force = 1f };
            KbFacts onCover = new KbFacts { kind = KbKind.Pawn, thingId = 31, x = 5, z = 2, mass = 70f, onSuperdeep = true, onCover = true };
            KbFacts inPit = new KbFacts { kind = KbKind.Pawn, thingId = 32, x = 5, z = 2, mass = 70f, onSuperdeep = true, onCover = false };
            KbFacts onFloor = new KbFacts { kind = KbKind.Pawn, thingId = 33, x = 5, z = 2, mass = 70f };
            KbPlan pc = KbPlanner.Decide(onCover, gas, q0, new KbSettings(), w), pf = KbPlanner.Decide(onFloor, gas, q0, new KbSettings(), w);
            Check("K_GAS_COVER_SHOVE a person on an intact cover is shoved one cell by burning gas", pc.act == KbAct.LaunchPawn && pc.res.cellsTravelled == 1,
                pc.act + " " + pc.reason + " " + pc.res.cellsTravelled);
            Check("K_GAS_COVER_SHOVE ... as on any floor", pc.res.destX == pf.res.destX && pc.res.destZ == pf.res.destZ && pc.res.impact == pf.res.impact && pc.res.impact == 0f);
            KbPlan pp = KbPlanner.Decide(inPit, gas, q0, new KbSettings(), w);
            Check("K_GAS_COVER_SHOVE a person down in an open pit is not shoved", pp.act == KbAct.Skip && pp.reason == "in_pit", pp.act + " " + pp.reason);
            KbPlan pb = KbPlanner.Decide(onCover, blast, q0, new KbSettings(), w);
            Check("K_GAS_COVER_SHOVE a blast still leaves a person on a cover to its broken cover", pb.act == KbAct.Skip && pb.reason == "in_pit", pb.act + " " + pb.reason);
            Check("K_GAS_COVER_SHOVE the shove's landing never breaks a cover", !RM_KnockbackMath.LandingBreaksCover(KbKind.Pawn, true, false, gas.id));
            // the range: the pawn 0-2 cells from the clump in 8 directions, on a cover / open pit / floor, cooldown in or out
            int cases = 0, bad = 0; string worst = "none";
            for (int ox = -2; ox <= 2; ox++)
            for (int oz = -2; oz <= 2; oz++)
            foreach (int ground in new[] { 0, 1, 2 })
            foreach (int ago in new[] { 10, 1000 })
            {
                var f = new KbFacts { kind = KbKind.Pawn, thingId = 40, x = 10 + ox, z = 10 + oz, mass = 70f, onSuperdeep = ground > 0, onCover = ground == 1, gasShovedAgo = ago };
                var floor = new KbFacts { kind = KbKind.Pawn, thingId = 40, x = 10 + ox, z = 10 + oz, mass = 70f, gasShovedAgo = ago };
                var g2 = new KbBlast { id = -5, cx = 10, cz = 10, radius = 2.4f, force = 1f, gas = true };
                var ww = new MWorld(21, 21);
                KbPlan a = KbPlanner.Decide(f, g2, q0, new KbSettings(), ww), c = KbPlanner.Decide(floor, g2, q0, new KbSettings(), ww);
                cases++;
                string why = null;
                if (ground == 2 && a.act != KbAct.Skip) why = "a person in an open pit was shoved";
                else if (ground != 2 && (a.act != c.act || a.reason != c.reason || a.res.destX != c.res.destX || a.res.destZ != c.res.destZ)) why = "on a cover the shove differs from the floor's";
                else if (a.Throws && a.res.cellsTravelled > 1) why = "a gas shove of more than one cell";
                if (why != null) { bad++; worst = why + " (" + ox + "," + oz + " ground " + ground + " ago " + ago + ": " + a.act + " " + a.reason + ")"; }
            }
            Check("K_GAS_COVER_SHOVE sweep", bad == 0, worst);
            Console.WriteLine("K_GAS_COVER_SHOVE sweep: " + cases + " cases read, " + bad + " failing, worst: " + worst + " (limit: 0 failing)");
        }

        // K_NO_CONTACT (bar no_impact_without_contact): a throw a sandbag stops before it reaches a pawn hits nobody
        {
            var sn = new KbSettings();
            var g = new Grid(12, 3).Set(5, 1, KbCell.Partial).Set(6, 1, KbCell.Pawn);
            KbResult r = RM_KnockbackMath.Resolve(g, 4, 1, 1f, 0f, 3, KbKind.Pawn, 70f, sn);
            KbPlanner.Collide(ref r, 70f, 70f, sn);
            Check("K_NO_CONTACT lane 4 | sandbag 5 | pawn 6: no hit, no bruise", !r.hitOther && r.otherImpact == 0f && r.destX == 4 && r.stop == KbStop.PawnBeyondCover,
                "hit " + r.hitOther + " other " + r.otherImpact + " dest " + r.destX + " stop " + r.stop);
            KbResult r2 = RM_KnockbackMath.Resolve(new Grid(12, 3).Set(5, 1, KbCell.Partial).Set(6, 1, KbCell.Pawn), 3, 1, 1f, 0f, 4, KbKind.Pawn, 70f, sn);
            Check("K_NO_CONTACT a cell short of the sandbag: still no hit", !r2.hitOther && r2.destX == 4 && r2.otherImpact == 0f, "hit " + r2.hitOther + " dest " + r2.destX);
            KbResult r3 = RM_KnockbackMath.Resolve(new Grid(12, 3).Set(6, 1, KbCell.Pawn), 4, 1, 1f, 0f, 3, KbKind.Pawn, 70f, sn);
            Check("K_NO_CONTACT control: no sandbag, the pawn is met", r3.hitOther && r3.destX == 5 && r3.otherImpact > 0f);
            KbResult r4 = RM_KnockbackMath.Resolve(new Grid(12, 3).Set(5, 1, KbCell.Partial).Set(7, 1, KbCell.Pawn), 4, 1, 1f, 0f, 4, KbKind.Pawn, 70f, sn);
            Check("K_NO_CONTACT control: over the sandbag to the cell before the pawn, the pawn is met", r4.hitOther && r4.destX == 6);
            // every lane of 1-6 cells of open / sandbag / pawn, thrown 1-6 cells, sandbags stopping or not: a hit only from the
            // cell next to the pawn, and never a bruise on a pawn not hit
            int cases = 0, bad = 0; string worst = "none";
            var kinds = new[] { KbCell.Open, KbCell.Partial, KbCell.Pawn };
            for (int len = 1; len <= 6; len++)
            {
                int combos = (int)Math.Pow(3, len);
                for (int code = 0; code < combos; code++)
                {
                    var lg = new Grid(10, 3);
                    int cc = code;
                    for (int k = 1; k <= len; k++) { lg.Set(k, 1, kinds[cc % 3]); cc /= 3; }
                    foreach (int cells in new[] { 1, 2, 3, 4, 5, 6 })
                    foreach (bool stopAt in new[] { false, true })
                    {
                        var st = new KbSettings { sandbagsStop = stopAt };
                        KbResult x = RM_KnockbackMath.Resolve(lg, 0, 1, 1f, 0f, cells, KbKind.Pawn, 70f, st);
                        KbPlanner.Collide(ref x, 70f, 70f, st);
                        cases++;
                        string why = null;
                        if (x.hitOther && Math.Max(Math.Abs(x.otherX - x.destX), Math.Abs(x.otherZ - x.destZ)) != 1) why = "hit a pawn it did not reach (dest " + x.destX + ", pawn " + x.otherX + ")";
                        else if (!x.hitOther && x.otherImpact != 0f) why = "a bruise with no hit";
                        else if (lg.At(x.destX, x.destZ) == KbCell.Partial && x.cellsTravelled > 0) why = "came to rest on a sandbag";
                        if (why != null) { bad++; worst = why + " (lane code " + code + " len " + len + " cells " + cells + " stop " + stopAt + ")"; }
                    }
                }
            }
            Check("K_NO_CONTACT sweep", bad == 0, worst);
            Console.WriteLine("K_NO_CONTACT sweep: " + cases + " cases read, " + bad + " failing, worst: " + worst + " (limit: 0 failing)");
        }

        Console.WriteLine("explosive knockback kernel: " + pass + "/" + (pass + fail) + " passed");
        return fail == 0 ? 0 : 1;
    }
}
