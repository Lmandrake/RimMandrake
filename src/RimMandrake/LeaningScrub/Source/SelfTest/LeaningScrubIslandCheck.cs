using System;
using System.Collections.Generic;

namespace RimMandrake.LeaningScrub.SelfTest
{
    // VENOMVINE_BUILD_SCRUB_GROWS_TEETH: table and property checks of RM_IslandKernel (islands at 15%, creep capped at 22%).
    internal static class LeaningScrubIslandCheck
    {
        public static bool Run()
        {
            int bad = 0;
            void Eq(string n, object got, object want) { if (!Equals(got, want)) { bad++; Console.Error.WriteLine("FAIL island " + n + " " + got + " != " + want); } }
            void True(string n, bool ok) { if (!ok) { bad++; Console.Error.WriteLine("FAIL island " + n); } }

            // plan: 15% of 55000 open cells = 8250; at most 200 a body the rolled 8-14 is scaled up to 42
            Eq("target 15%", RM_IslandKernel.TargetCells(55000, 0.15f), 8250);
            Eq("target none", RM_IslandKernel.TargetCells(0, 0.15f), 0);
            Eq("count scaled up", RM_IslandKernel.IslandCount(8250, 10, 40, 200), 42);
            Eq("count kept", RM_IslandKernel.IslandCount(1500, 10, 40, 200), 10);
            Eq("count lowered for min body", RM_IslandKernel.IslandCount(200, 10, 40, 200), 5);
            Eq("count zero target", RM_IslandKernel.IslandCount(0, 10, 40, 200), 0);
            var rng = new Random(7);
            var sizes = new List<int>();
            RM_IslandKernel.SizeIslands(8250, 42, 40, 200, rng.NextDouble, sizes);
            int sum = 0;
            foreach (int s in sizes) { sum += s; True("size in bounds " + s, s >= 40 && s <= 200); }
            True("sizes reach target within 5% (" + sum + ")", Math.Abs(sum - 8250) <= 8250 * 0.05);

            // grow on an open 120x120 grid: size reached, contiguous, stretched along the wind (+x)
            int w = 120, h = 120;
            var allowed = new bool[w * h];
            var passable = new bool[w * h];
            var owner = new int[w * h];
            for (int i = 0; i < w * h; i++) { allowed[i] = true; passable[i] = true; owner[i] = -1; }
            var cells = new List<int>();
            int got = RM_IslandKernel.Grow(w, h, allowed, owner, 0, 60, 60, 150, 2, 1f, 0f, 1.6f, new Random(3).NextDouble, cells);
            Eq("grow reaches size", got, 150);
            int minX = 999, maxX = -1, minZ = 999, maxZ = -1;
            foreach (int c in cells) { minX = Math.Min(minX, c % w); maxX = Math.Max(maxX, c % w); minZ = Math.Min(minZ, c / w); maxZ = Math.Max(maxZ, c / w); }
            True("stretched downwind (" + (maxX - minX) + " x " + (maxZ - minZ) + ")", maxX - minX > maxZ - minZ);
            // gap: a second island may not touch the first within 2 cells
            var cells2 = new List<int>();
            int tip = -1;
            foreach (int c in cells) if (c % w == maxX) { tip = c; break; }
            RM_IslandKernel.Grow(w, h, allowed, owner, 1, maxX + 2, tip / w, 150, 2, 1f, 0f, 1.6f, new Random(4).NextDouble, cells2);
            Eq("seed inside gap refused", cells2.Count, 0);
            RM_IslandKernel.Grow(w, h, allowed, owner, 1, maxX + 10, 60, 100, 2, 1f, 0f, 1.6f, new Random(4).NextDouble, cells2);
            bool gapKept = true;
            foreach (int c in cells2) if (!RM_IslandKernel.GapOk(w, h, owner, 1, c % w, c / w, 2)) gapKept = false;
            True("gap kept between islands", gapKept && cells2.Count > 0);
            // disallowed seed
            allowed[5] = false;
            Eq("disallowed seed", RM_IslandKernel.Grow(w, h, allowed, owner, 2, 5, 0, 50, 2, 1f, 0f, 1.6f, new Random(1).NextDouble, new List<int>()), 0);

            // traversability: a wall island across a corridor map seals the far side
            int cw = 30, ch = 5;
            var cp = new bool[cw * ch];
            var co = new int[cw * ch];
            for (int i = 0; i < cw * ch; i++) { cp[i] = true; co[i] = -1; }
            int before = RM_IslandKernel.Reach(cw, ch, cp, co, 0, 2);
            Eq("reach whole corridor", before, 150);
            var wall = new List<int>();
            for (int z = 0; z < ch; z++) { co[z * cw + 15] = 0; wall.Add(z * cw + 15); }
            int after = RM_IslandKernel.Reach(cw, ch, cp, co, 0, 2);
            Eq("wall cuts reach", after, 75);
            True("sealing island refused", !RM_IslandKernel.KeepsTraversable(before, after, wall.Count, 3));
            RM_IslandKernel.Ungrow(co, wall);
            co[2 * cw + 15] = 0;
            True("plug island allowed", RM_IslandKernel.KeepsTraversable(before, RM_IslandKernel.Reach(cw, ch, cp, co, 0, 2), 1, 3));
            Eq("start inside island reaches nothing", RM_IslandKernel.Reach(cw, ch, cp, co, 15, 2), 0);

            // rooms
            Eq("tiny island no room", RM_IslandKernel.RoomCount(10, 0.9), 0);
            True("small island one room", RM_IslandKernel.RoomCount(40, 0.99) == 1);
            True("big island 1..3 rooms", RM_IslandKernel.RoomCount(180, 0.99) >= 1 && RM_IslandKernel.RoomCount(180, 0.99) <= 3);
            Eq("weighted pick first", RM_IslandKernel.PickWeighted(new[] { 1f, 1f, 2f }, 0.1), 0);
            Eq("weighted pick last", RM_IslandKernel.PickWeighted(new[] { 1f, 1f, 2f }, 0.9), 2);
            Eq("weighted empty", RM_IslandKernel.PickWeighted(new float[0], 0.5), -1);
            int heart = RM_IslandKernel.Heart(w, h, owner, 0, cells);
            True("heart is interior", heart >= 0 && RM_IslandKernel.RoleFits(RM_IslandKernel.RoleInterior, w, h, owner, 0, heart, 1f, 0f, minX, maxX));
            int edgeCell = -1;
            foreach (int c in cells) if (c % w == maxX) { edgeCell = c; break; }
            True("east tip is an edge", RM_IslandKernel.RoleFits(RM_IslandKernel.RoleEdge, w, h, owner, 0, edgeCell, 1f, 0f, minX, maxX));
            True("east tip is the downwind face", RM_IslandKernel.RoleFits(RM_IslandKernel.RoleDownwind, w, h, owner, 0, edgeCell, 1f, 0f, minX, maxX));
            int westCell = -1;
            foreach (int c in cells) if (c % w == minX) { westCell = c; break; }
            True("west tip not downwind", !RM_IslandKernel.RoleFits(RM_IslandKernel.RoleDownwind, w, h, owner, 0, westCell, 1f, 0f, minX, maxX));

            // creep: mean one runner per 10 days at a 6-hour sweep = 0.025 a sweep
            True("runner chance 10 days", Math.Abs(RM_IslandKernel.RunnerChance(15000, 10f) - 0.025) < 1e-9);
            Eq("runner chance capped at 1", RM_IslandKernel.RunnerChance(10000000, 10f), 1.0);
            Eq("cap room 22% of 10000", RM_IslandKernel.CapRoom(1500, 10000, 0.22f), 700);
            Eq("at cap", RM_IslandKernel.CapRoom(2200, 10000, 0.22f), 0);
            Eq("over cap", RM_IslandKernel.CapRoom(3000, 10000, 0.22f), 0);
            True("laid share sits under the cap", RM_IslandKernel.CapRoom(RM_IslandKernel.TargetCells(10000, 0.15f), 10000, 0.22f) > 0);
            int[] dx = { 1, 1, 0, -1, -1, -1, 0, 1 }, dz = { 0, 1, 1, 1, 0, -1, -1, -1 };
            var free = new bool[8];
            Eq("none free", RM_IslandKernel.PickNeighbour(dx, dz, free, 8, 1f, 0f, 0.75f, 0.1, 0.5), -1);
            for (int i = 0; i < 8; i++) free[i] = true;
            // downwind (+x) candidates are 0, 1, 7
            int pick = RM_IslandKernel.PickNeighbour(dx, dz, free, 8, 1f, 0f, 0.75f, 0.1, 0.0);
            True("downwind roll picks downwind", dx[pick] > 0);
            int downs = 0, total = 20000;
            var r = new Random(11);
            for (int t = 0; t < total; t++)
            {
                int k = RM_IslandKernel.PickNeighbour(dx, dz, free, 8, 1f, 0f, 0.75f, r.NextDouble(), r.NextDouble());
                if (dx[k] > 0) downs++;
            }
            double share = downs / (double)total; // 0.75 + 0.25 * 3/8 = 0.84375
            True("about 3 in 4 runners downwind (" + share.ToString("0.000") + ")", share > 0.82 && share < 0.87);
            Eq("no wind any free", RM_IslandKernel.PickNeighbour(dx, dz, free, 8, 0f, 0f, 0.75f, 0.1, 0.0), 0);
            for (int i = 0; i < 8; i++) free[i] = dx[i] < 0;
            int up = RM_IslandKernel.PickNeighbour(dx, dz, free, 8, 1f, 0f, 0.75f, 0.1, 0.5);
            True("blocked downwind falls back upwind", up >= 0 && dx[up] < 0);

            Console.WriteLine(bad == 0 ? "island checks: all pass" : "island checks: " + bad + " FAIL");
            return bad == 0;
        }
    }
}
