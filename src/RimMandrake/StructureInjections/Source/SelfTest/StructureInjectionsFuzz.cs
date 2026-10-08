// Approach B for StructureInjections: seeded fuzz over the plan reader (RimplacePlan.ParseLines) and RM_PlanKernel against independent models.
//   parse      random well-formed plans (every verb, comments, blank lines, CRLF, trailing blanks, unknown verbs) read back exactly, order kept
//   malformed  every truncation / non-number of every verb is refused with a FormatException naming the line; nothing else is ever thrown
//   offset     where a plan lands: the plan's centre goes to the anchor / the map centre, plus the offset; no footprint means offset only
//   run        a RUN against random blocked / already-built grids vs a brute-force walk (stops at the first blocker, never leaves the map)
//   order      transmitters first, original order kept in both groups
//   tables     direction / clear mode / pawn state / faction vocabulary, exhaustively
//   templates  the SHIPPED plans (--plans) parse, and their directive counts match a plain line count
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;

namespace RimMandrake.StructureInjections.SelfTest
{
    internal static class StructureInjectionsFuzz
    {
        public static long Cases, Steps, Lines, Unknown, Blocks, Already, Anchors;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        private static readonly string[] Verbs = { "FOOTPRINT", "CLEAR", "FOUNDATION", "TERRAIN", "THING", "RUN", "ROOF", "PAINT", "FLOORCOLOR", "PAWN" };
        private static readonly int[] Fields = { 5, 6, 4, 4, 6, 6, 4, 4, 4, 6 };   // including the verb
        private static readonly bool[] IntAt0 = null;

        // which field indexes are ints, per verb
        private static bool IsInt(string verb, int idx)
        {
            switch (verb)
            {
                case "FOOTPRINT": return idx >= 1 && idx <= 4;
                case "CLEAR": return idx >= 1 && idx <= 4;
                case "FOUNDATION": case "TERRAIN": case "ROOF": case "PAINT": case "FLOORCOLOR": return idx == 1 || idx == 2;
                case "THING": return idx >= 2 && idx <= 4;
                case "RUN": return idx == 1 || idx == 2;
                case "PAWN": return idx == 2 || idx == 3;
            }
            return false;
        }

        private static string Word(Random r) { string[] w = { "Wall", "RM_Thing", "StrawMatting", "Steel", "Granite", "A_b", "x" }; return w[r.Next(w.Length)]; }

        private static string MakeLine(Random r, string verb)
        {
            int n = Fields[Array.IndexOf(Verbs, verb)];
            var f = new List<string> { verb };
            for (int i = 1; i < n; i++) f.Add(IsInt(verb, i) ? r.Next(-50, 400).ToString() : Word(r));
            if (verb == "THING" && r.Next(3) == 0) f[5] = "-";
            if (verb == "RUN") { f[3] = "NESW"[r.Next(4)].ToString(); if (r.Next(3) == 0) f[5] = "-"; }
            if (verb == "CLEAR") f[5] = r.Next(2) == 0 ? "soft" : "all";
            return string.Join("\t", f);
        }

        // ═════════════ parse ═════════════
        private static List<string> Parse(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = 0; s < n && fails.Count < 5; s++)
            {
                int seed = seed0 + s; var r = new Random(seed); Cases++;
                try
                {
                    var lines = new List<string>();
                    var want = new Dictionary<string, List<string[]>>();
                    var unknown = new Dictionary<string, int>();
                    int k = r.Next(0, 60);
                    for (int i = 0; i < k; i++)
                    {
                        int c = r.Next(100);
                        if (c < 8) lines.Add("# comment " + r.Next(99));
                        else if (c < 14) lines.Add("");
                        else if (c < 20) { string u = "FUTURE" + r.Next(3); lines.Add(u + "\t1\t2"); unknown[u] = (unknown.ContainsKey(u) ? unknown[u] : 0) + 1; Unknown++; }
                        else
                        {
                            string verb = Verbs[r.Next(Verbs.Length)];
                            string ln = MakeLine(r, verb);
                            if (!want.ContainsKey(verb)) want[verb] = new List<string[]>();
                            want[verb].Add(ln.Split('\t'));
                            if (r.Next(5) == 0) ln += "\r";
                            else if (r.Next(7) == 0) ln += "  ";
                            lines.Add(ln);
                        }
                        Lines++; Steps++;
                    }
                    var plan = RimplacePlan.ParseLines(lines);
                    Func<string, int> cnt = v => want.ContainsKey(v) ? want[v].Count : 0;
                    Check(plan.Foundation.Count == cnt("FOUNDATION") && plan.Terrain.Count == cnt("TERRAIN") && plan.Things.Count == cnt("THING") && plan.Roof.Count == cnt("ROOF")
                        && plan.Paint.Count == cnt("PAINT") && plan.FloorColor.Count == cnt("FLOORCOLOR") && plan.Clears.Count == cnt("CLEAR") && plan.Runs.Count == cnt("RUN") && plan.Pawns.Count == cnt("PAWN"),
                        "directive counts differ from the lines written");
                    for (int i = 0; i < plan.Things.Count; i++)
                    {
                        var w = want["THING"][i]; var t = plan.Things[i];
                        Check(t.DefName == w[1] && t.X == int.Parse(w[2]) && t.Z == int.Parse(w[3]) && t.Rot == int.Parse(w[4]) && t.Stuff == (w[5] == "-" ? null : w[5]), "THING " + i + " read back wrong");
                    }
                    for (int i = 0; i < plan.Runs.Count; i++)
                    {
                        var w = want["RUN"][i]; var t = plan.Runs[i];
                        Check(t.X == int.Parse(w[1]) && t.Z == int.Parse(w[2]) && t.Dir == w[3] && t.DefName == w[4] && t.Stuff == (w[5] == "-" ? null : w[5]), "RUN " + i + " read back wrong");
                    }
                    for (int i = 0; i < plan.Clears.Count; i++)
                    {
                        var w = want["CLEAR"][i]; var t = plan.Clears[i];
                        Check(t.X == int.Parse(w[1]) && t.Z == int.Parse(w[2]) && t.W == int.Parse(w[3]) && t.H == int.Parse(w[4]) && t.Mode == w[5], "CLEAR " + i + " read back wrong");
                    }
                    for (int i = 0; i < plan.Pawns.Count; i++)
                    {
                        var w = want["PAWN"][i]; var t = plan.Pawns[i];
                        Check(t.KindDef == w[1] && t.X == int.Parse(w[2]) && t.Z == int.Parse(w[3]) && t.Faction == w[4] && t.State == w[5], "PAWN " + i + " read back wrong");
                    }
                    foreach (var pair in new[] { Tuple.Create("TERRAIN", plan.Terrain), Tuple.Create("FOUNDATION", plan.Foundation), Tuple.Create("ROOF", plan.Roof), Tuple.Create("PAINT", plan.Paint), Tuple.Create("FLOORCOLOR", plan.FloorColor) })
                        for (int i = 0; i < pair.Item2.Count; i++)
                        {
                            var w = want[pair.Item1][i]; var c = pair.Item2[i];
                            Check(c.X == int.Parse(w[1]) && c.Z == int.Parse(w[2]) && c.DefName == w[3], pair.Item1 + " " + i + " read back wrong (order must be kept)");
                        }
                    if (want.ContainsKey("FOOTPRINT"))
                    {
                        var w = want["FOOTPRINT"].Last();
                        Check(plan.HasFootprint && plan.FootprintX == int.Parse(w[1]) && plan.FootprintZ == int.Parse(w[2]) && plan.FootprintW == int.Parse(w[3]) && plan.FootprintH == int.Parse(w[4]), "the last FOOTPRINT must win");
                    }
                    else Check(!plan.HasFootprint, "a footprint from nowhere");
                    Check(plan.UnknownDirectives.Count == unknown.Count && unknown.All(kv => plan.UnknownDirectives.ContainsKey(kv.Key) && plan.UnknownDirectives[kv.Key] == kv.Value), "unknown directives not counted once per line per verb");
                }
                catch (Exception ex) { fails.Add("parse seed " + seed + ": " + ex.Message); }
            }
            return fails;
        }

        // ═════════════ malformed ═════════════
        private static List<string> Malformed(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = 0; s < n && fails.Count < 5; s++)
            {
                int seed = seed0 + s; var r = new Random(seed); Cases++;
                try
                {
                    string verb = Verbs[r.Next(Verbs.Length)];
                    string good = MakeLine(r, verb);
                    var f = good.Split('\t').ToList();
                    int mode = r.Next(3);
                    int bad = -1;
                    if (mode == 0) { f = f.Take(r.Next(1, f.Count)).ToList(); }   // truncated, keeping the verb
                    else
                    {
                        var ints = Enumerable.Range(1, f.Count - 1).Where(i => IsInt(verb, i)).ToList();
                        bad = ints[r.Next(ints.Count)];
                        f[bad] = new[] { "x", "1.5", "", "99999999999", "0x10" }[r.Next(5)];
                    }
                    string line = string.Join("\t", f);
                    var pre = new List<string> { "# header", "", MakeLine(r, "TERRAIN") };
                    pre.Add(line);
                    Steps++;
                    // TrimEnd eats a trailing blank field, which makes some "empty field" breaks into truncations: both must still throw
                    bool threw = false;
                    try { RimplacePlan.ParseLines(pre); }
                    catch (FormatException fe)
                    {
                        threw = true;
                        Check(fe.Message.Contains("plan line 4"), "the error does not name line 4: " + fe.Message);
                    }
                    Check(threw, "a malformed line was accepted: " + line.Replace("\t", "<TAB>"));
                }
                catch (Exception ex) { fails.Add("malformed seed " + seed + ": " + ex.Message); }
            }
            return fails;
        }

        // ═════════════ offset ═════════════
        private static List<string> Offset(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = 0; s < n && fails.Count < 5; s++)
            {
                int seed = seed0 + s; var r = new Random(seed); Cases++;
                try
                {
                    bool hasFp = r.Next(5) != 0, anchor = r.Next(3) == 0, center = r.Next(4) != 0;
                    int fx = r.Next(-3, 4), fz = r.Next(-3, 4), fw = r.Next(1, 40), fh = r.Next(1, 40);
                    int ax = r.Next(0, 250), az = r.Next(0, 250), mx = r.Next(50, 250), mz = r.Next(50, 250), ox = r.Next(-20, 21), oz = r.Next(-20, 21);
                    int dx, dz; Steps++;
                    RM_PlanKernel.Offset(hasFp, fx, fz, fw, fh, anchor, ax, az, center, mx, mz, ox, oz, out dx, out dz);
                    int pcx = fx + fw / 2, pcz = fz + fh / 2;
                    if (!hasFp) { Check(dx == ox && dz == oz, "no footprint must land at the explicit offset alone"); continue; }
                    if (anchor) { Anchors++; Check(pcx + dx == ax + ox && pcz + dz == az + oz, "the plan's centre must land on the anchor plus the offset"); }
                    else if (center) Check(pcx + dx == mx + ox && pcz + dz == mz + oz, "the plan's centre must land on the map centre plus the offset");
                    else Check(dx == ox && dz == oz, "neither anchor nor centring: the offset alone");
                    // anchor beats centring
                    int dx2, dz2;
                    RM_PlanKernel.Offset(hasFp, fx, fz, fw, fh, anchor, ax, az, !center, mx, mz, ox, oz, out dx2, out dz2);
                    if (anchor) Check(dx2 == dx && dz2 == dz, "centerOnMap changed an anchored plan");
                }
                catch (Exception ex) { fails.Add("offset seed " + seed + ": " + ex.Message); }
            }
            return fails;
        }

        // ═════════════ run ═════════════
        private static List<string> Run(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = 0; s < n && fails.Count < 5; s++)
            {
                int seed = seed0 + s; var r = new Random(seed); Cases++;
                try
                {
                    int w = r.Next(1, 30), h = r.Next(1, 30);
                    var grid = new RM_PlanKernel.RunProbe[w, h];
                    for (int x = 0; x < w; x++) for (int z = 0; z < h; z++) { int c = r.Next(100); grid[x, z] = c < 8 ? RM_PlanKernel.RunProbe.Blocked : c < 25 ? RM_PlanKernel.RunProbe.AlreadyThere : RM_PlanKernel.RunProbe.Free; }
                    int sx = r.Next(-4, w + 4), sz = r.Next(-4, h + 4), dir = r.Next(4);
                    var placed = new List<Tuple<int, int>>(); var probed = new List<Tuple<int, int>>();
                    int walked = RM_PlanKernel.WalkRun(sx, sz, dir, w, h, (x, z) => { probed.Add(Tuple.Create(x, z)); return grid[x, z]; }, (x, z) => placed.Add(Tuple.Create(x, z)));
                    Steps += probed.Count + 1;
                    // brute force
                    int[] vx = { 0, 1, 0, -1 }, vz = { 1, 0, -1, 0 };
                    var wantPlaced = new List<Tuple<int, int>>(); int wantWalked = 0; int cx = sx, cz = sz;
                    while (cx >= 0 && cz >= 0 && cx < w && cz < h)
                    {
                        if (grid[cx, cz] == RM_PlanKernel.RunProbe.Blocked) { Blocks++; break; }
                        if (grid[cx, cz] == RM_PlanKernel.RunProbe.Free) wantPlaced.Add(Tuple.Create(cx, cz)); else Already++;
                        wantWalked++; cx += vx[dir]; cz += vz[dir];
                    }
                    Check(walked == wantWalked, "walked " + walked + " cells, expected " + wantWalked);
                    Check(placed.SequenceEqual(wantPlaced), "placed cells differ from a brute-force walk");
                    Check(probed.All(p => p.Item1 >= 0 && p.Item2 >= 0 && p.Item1 < w && p.Item2 < h), "the run probed a cell outside the map");
                    Check(placed.All(p => grid[p.Item1, p.Item2] == RM_PlanKernel.RunProbe.Free), "the run placed on a cell that was blocked or already built");
                    Check(probed.Distinct().Count() == probed.Count, "the run revisited a cell");
                }
                catch (Exception ex) { fails.Add("run seed " + seed + ": " + ex.Message); }
            }
            return fails;
        }

        // ═════════════ order ═════════════
        private static List<string> Order(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = 0; s < n && fails.Count < 5; s++)
            {
                int seed = seed0 + s; var r = new Random(seed); Cases++;
                try
                {
                    var items = Enumerable.Range(0, r.Next(0, 40)).Select(i => Tuple.Create(i, r.Next(3) == 0)).ToList();
                    var got = RM_PlanKernel.TransmittersFirst(items, t => t.Item2);
                    Steps += items.Count;
                    Check(got.Count == items.Count && got.OrderBy(t => t.Item1).SequenceEqual(items), "the order step lost or duplicated an item");
                    var want = items.Where(t => t.Item2).Concat(items.Where(t => !t.Item2)).ToList();
                    Check(got.SequenceEqual(want), "transmitters must come first and each group keep its original order (a connector binds to a transmitter present AT SPAWN)");
                }
                catch (Exception ex) { fails.Add("order seed " + seed + ": " + ex.Message); }
            }
            return fails;
        }

        // ═════════════ tables ═════════════
        private static List<string> Tables()
        {
            var fails = new List<string>();
            try
            {
                Cases++;
                string[] dirs = { "N", "E", "S", "W", "", "n", "NE", "NESW", "ES", "SW", " N", "N ", "X", null };
                int[] want = { 0, 1, 2, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 };
                for (int i = 0; i < dirs.Length; i++) { Steps++; Check(RM_PlanKernel.DirIndex(dirs[i]) == want[i], "DirIndex(" + (dirs[i] ?? "null") + ") = " + RM_PlanKernel.DirIndex(dirs[i]) + " want " + want[i]); }
                int[] ex = { 0, 1, 0, -1 }, ez = { 1, 0, -1, 0 };
                for (int d = 0; d < 4; d++) { int a, b; RM_PlanKernel.DirStep(d, out a, out b); Steps++; Check(a == ex[d] && b == ez[d], "DirStep " + d + " (N is +z, E is +x)"); }
                bool threw = false; try { int a, b; RM_PlanKernel.DirStep(-1, out a, out b); } catch (ArgumentOutOfRangeException) { threw = true; }
                Check(threw, "DirStep(-1) must refuse, not guess a direction");
                Check(RM_PlanKernel.ParseClearMode("all") == RM_PlanKernel.ClearMode.All && RM_PlanKernel.ParseClearMode("soft") == RM_PlanKernel.ClearMode.Soft
                    && RM_PlanKernel.ParseClearMode("All") == RM_PlanKernel.ClearMode.Unknown && RM_PlanKernel.ParseClearMode("") == RM_PlanKernel.ClearMode.Unknown && RM_PlanKernel.ParseClearMode(null) == RM_PlanKernel.ClearMode.Unknown, "clear modes");
                Check(RM_PlanKernel.ParsePawnState("alive") == RM_PlanKernel.PawnState.Alive && RM_PlanKernel.ParsePawnState("dead") == RM_PlanKernel.PawnState.Dead
                    && RM_PlanKernel.ParsePawnState("dessicated") == RM_PlanKernel.PawnState.Dessicated && RM_PlanKernel.ParsePawnState("skeleton") == RM_PlanKernel.PawnState.Dessicated
                    && RM_PlanKernel.ParsePawnState("dead2") == RM_PlanKernel.PawnState.Unknown && RM_PlanKernel.ParsePawnState("") == RM_PlanKernel.PawnState.Unknown && RM_PlanKernel.ParsePawnState(null) == RM_PlanKernel.PawnState.Unknown, "pawn states (a typo must NOT read as dead)");
                Check(RM_PlanKernel.ClassifyFaction("player") == RM_PlanKernel.FactionKind.Refused && RM_PlanKernel.ClassifyFaction("wild") == RM_PlanKernel.FactionKind.Wild
                    && RM_PlanKernel.ClassifyFaction("") == RM_PlanKernel.FactionKind.Wild && RM_PlanKernel.ClassifyFaction(null) == RM_PlanKernel.FactionKind.Wild
                    && RM_PlanKernel.ClassifyFaction("Pirate") == RM_PlanKernel.FactionKind.Named && RM_PlanKernel.ClassifyFaction("Player") == RM_PlanKernel.FactionKind.Named, "factions (a mapgen template must never spawn a colonist)");
                Steps += 3;
            }
            catch (Exception ex) { fails.Add("tables: " + ex.Message); }
            return fails;
        }

        // ═════════════ templates ═════════════
        private static List<string> Templates(string dir)
        {
            var fails = new List<string>();
            try
            {
                Cases++;
                if (dir == null || !Directory.Exists(dir)) { fails.Add("templates: --plans folder missing (a template check that found nothing is not a pass): " + dir); return fails; }
                var files = Directory.GetFiles(dir, "*.txt");
                Check(files.Length >= 3, "only " + files.Length + " shipped plans found (sanity probe: the folder moved?)");
                foreach (string f in files)
                {
                    Steps++;
                    var lines = File.ReadAllLines(f);
                    var plan = RimplacePlan.ParseLines(lines);
                    string n = Path.GetFileName(f);
                    Func<string, int> c = v => lines.Count(l => l.StartsWith(v + "\t"));
                    Check(plan.HasFootprint, n + ": no FOOTPRINT");
                    Check(plan.UnknownDirectives.Count == 0, n + ": unknown directives " + string.Join(",", plan.UnknownDirectives.Keys));
                    Check(plan.Terrain.Count == c("TERRAIN") && plan.Things.Count == c("THING") && plan.Roof.Count == c("ROOF") && plan.Clears.Count == c("CLEAR") && plan.Runs.Count == c("RUN") && plan.Pawns.Count == c("PAWN"), n + ": directive counts differ from a plain line count");
                    Check(lines[0].StartsWith("# rimplace flat plan v2"), n + ": not a v2 plan header");
                    foreach (var cl in plan.Clears) Check(RM_PlanKernel.ParseClearMode(cl.Mode) != RM_PlanKernel.ClearMode.Unknown, n + ": CLEAR mode " + cl.Mode);
                    foreach (var ru in plan.Runs) Check(RM_PlanKernel.DirIndex(ru.Dir) >= 0, n + ": RUN dir " + ru.Dir);
                    foreach (var p in plan.Pawns) Check(RM_PlanKernel.ParsePawnState(p.State) != RM_PlanKernel.PawnState.Unknown && RM_PlanKernel.ClassifyFaction(p.Faction) != RM_PlanKernel.FactionKind.Refused, n + ": PAWN " + p.KindDef);
                    // everything the plan places sits inside its declared footprint's one-cell buffer
                    foreach (var t in plan.Things) Check(t.X >= plan.FootprintX - 1 && t.Z >= plan.FootprintZ - 1 && t.X <= plan.FootprintX + plan.FootprintW && t.Z <= plan.FootprintZ + plan.FootprintH, n + ": THING " + t.DefName + " at " + t.X + "," + t.Z + " lies outside the footprint");
                    foreach (var t in plan.Terrain) Check(t.X >= plan.FootprintX && t.Z >= plan.FootprintZ && t.X < plan.FootprintX + plan.FootprintW && t.Z < plan.FootprintZ + plan.FootprintH, n + ": TERRAIN at " + t.X + "," + t.Z + " lies outside the footprint");
                }
            }
            catch (Exception ex) { fails.Add("templates: " + ex.Message); }
            return fails;
        }

        public static bool Run(double scale, int? oneSeed, string only, string plans)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("parse", () => Parse(N(4000), S(1))),
                ("malformed", () => Malformed(N(6000), S(1))),
                ("offset", () => Offset(N(8000), S(1))),
                ("run", () => Run(N(6000), S(1))),
                ("order", () => Order(N(3000), S(1))),
                ("tables", () => Tables()),
                ("templates", () => Templates(plans)),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine($"fuzz {f.name}: {Cases - c0} cases, {Steps - s0} steps, {t.Elapsed.TotalSeconds:F2}s, {(fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES")}");
                foreach (var m in fails) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            Console.WriteLine($"reached: plan lines {Lines}, unknown verbs {Unknown}, anchored plans {Anchors}, runs stopped by a blocker {Blocks}, already-built cells {Already}");
            if (only == null && !oneSeed.HasValue && scale >= 1 && (Lines == 0 || Unknown == 0 || Anchors == 0 || Blocks == 0 || Already == 0)) { Console.WriteLine("FAIL fuzz never reached a path (blind)"); ok = false; }
            Console.WriteLine($"structureinjections fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
