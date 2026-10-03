// Fresh vs incremental determinism (lane F, 2026-10-02): the live D2_fresh_builder_same check went RED on
// every matrix board holding the RING topology. The runner builds a board one op type at a time and the map
// component rebuilds between the calls through ONE CordBuilder (its per-edge cache); the probe's `fresh`
// command lays the finished map with an empty cache. This replays matrix_det_scenes.json (written by
// northstar_matrix/det_export.py: every floor scene's cumulative world after each op type, game coords)
// the same way and requires the last incremental build to equal a fresh build, edge by edge.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using RimMandrake.MessyConduit.Core;

namespace RimMandrake.MessyConduit.SelfTest
{
    internal static class DeterminismChecks
    {
        private static Cell C(JsonElement a) => new Cell(a[0].GetInt32(), a[1].GetInt32());

        private static CordWorld StageWorld(int w, int h, JsonElement st, out HashSet<Cell> live)
        {
            var world = new CordWorld(w, h);
            foreach (JsonElement c in st.GetProperty("conduit").EnumerateArray()) world.SetConduit(C(c));
            foreach (JsonElement b in st.GetProperty("blocked").EnumerateArray())
            {
                string k = b[2].GetString();
                world.SetBlocked(C(b), k == "rock" ? BlockKind.Rock : k == "water" ? BlockKind.Water : BlockKind.Wall);
            }
            foreach (JsonElement d in st.GetProperty("doors").EnumerateArray()) world.SetDoor(C(d));
            foreach (JsonElement t in st.GetProperty("trees").EnumerateArray()) world.SetExtraCost(C(t), 1.5f);
            foreach (JsonElement m in st.GetProperty("machines").EnumerateArray())
            {
                string k = m.GetProperty("kind").GetString();
                world.Machines.Add(new MachineInfo
                {
                    Id = m.GetProperty("id").GetString(),
                    Kind = k == "source" ? MachineKind.Source : k == "battery" ? MachineKind.Battery :
                           k == "transmitter" ? MachineKind.Transmitter : MachineKind.Consumer,
                    X0 = m.GetProperty("x").GetInt32(), Z0 = m.GetProperty("z").GetInt32(),
                    W = m.GetProperty("w").GetInt32(), H = m.GetProperty("h").GetInt32(),
                    Hookups = m.GetProperty("hookups").EnumerateArray().Select(C).ToList()
                });
            }
            // live = the battery's conduit net once it is charged (the game's HasActivePowerSource)
            live = new HashSet<Cell>();
            if (st.GetProperty("charged").GetBoolean())
            {
                var stack = new Stack<Cell>();
                foreach (MachineInfo m in world.Machines.Where(x => x.Kind == MachineKind.Battery))
                    foreach (Cell hc in m.Hookups) stack.Push(hc);
                while (stack.Count > 0)
                {
                    Cell c = stack.Pop();
                    if (!world.IsConduit(c) || !live.Add(c)) continue;
                    foreach (Cell d in Cell.Dirs4) stack.Push(c + d);
                }
            }
            return world;
        }

        private static BuildOptions Options(JsonElement settings)
        {
            string S(string k, string d) => settings.TryGetProperty(k, out JsonElement v) ? v.GetString() : d;
            double F(string k, double d) => double.Parse(S(k, d.ToString(System.Globalization.CultureInfo.InvariantCulture)), System.Globalization.CultureInfo.InvariantCulture);
            // MessyConduitSettings defaults + BuildOptions() clamps
            var o = new BuildOptions { Tangles = S("tangles", "True") == "True", NeedlessLoops = true,
                                       TangleMin = Math.Max(6, Math.Min(20, (int)F("tangleMin", 9))) };
            o.Lay.SlackScale = Math.Max(0, Math.Min(2, F("slack", 1)));
            o.Lay.MaxExtra = Math.Max(2, Math.Min(40, F("sprawlCap", 16)));
            o.Lay.MinExtra = Math.Min(o.Lay.MinExtra, o.Lay.MaxExtra);
            o.Lay.CordsMax = Math.Max(1, Math.Min(3, (int)F("cordsPerConnection", 3)));
            return o;
        }

        /// <summary>(same, different, missing) of the last incremental build against a fresh one, by piece key
        /// and geometry hash (MessyConduitProbe.Fresh's comparison).</summary>
        internal static (int same, int diff, int missing, List<string> diffKeys) Compare(List<LaidPiece> incr, List<LaidPiece> fresh)
        {
            var cur = incr.Where(p => p.EndA != null).ToDictionary(p => p.Key, p => p.GeometryHash());
            int same = 0, diff = 0, missing = 0;
            var keys = new List<string>();
            foreach (LaidPiece p in fresh.Where(p => p.EndA != null))
            {
                if (!cur.TryGetValue(p.Key, out ulong h)) { missing++; keys.Add("missing " + p.EndA + "|" + p.EndB); }
                else if (h == p.GeometryHash()) same++;
                else { diff++; keys.Add(p.EndA + "|" + p.EndB); }
            }
            return (same, diff, missing, keys);
        }

        public static void Run(Action<bool, string> check, string path)
        {
            if (!File.Exists(path)) { check(false, "determinism: " + path + " missing (run northstar_matrix/det_export.py)"); return; }
            using JsonDocument doc = JsonDocument.Parse(File.ReadAllText(path));
            int scenes = 0, bad = 0, ring = 0;
            foreach (JsonElement s in doc.RootElement.GetProperty("scenes").EnumerateArray())
            {
                string id = s.GetProperty("id").GetString();
                int w = s.GetProperty("w").GetInt32(), h = s.GetProperty("h").GetInt32();
                BuildOptions opt = Options(s.GetProperty("settings"));
                var b = new CordBuilder();
                List<LaidPiece> incr = null;
                CordWorld last = null;
                HashSet<Cell> liveLast = null;
                foreach (JsonElement st in s.GetProperty("stages").EnumerateArray())
                {
                    last = StageWorld(w, h, st, out HashSet<Cell> live);
                    liveLast = live;
                    incr = b.Build(last, opt, c => live.Contains(c));
                }
                List<LaidPiece> fresh = new CordBuilder().Build(last, opt, c => liveLast.Contains(c));
                var r = Compare(incr, fresh);
                scenes++;
                if (s.GetProperty("topology").GetString() == "ring") ring++;
                bool ok = r.diff == 0 && r.missing == 0 && r.same > 0;
                if (!ok) bad++;
                check(ok, $"determinism {id}: incremental build (cache carried across every build call, trees, charge) == fresh: same {r.same}, different {r.diff} [{string.Join("; ", r.diffKeys)}], missing {r.missing}");
            }
            // negative control: the ring's pieces from the heater-only stage (before the lamp splits the ring) laid
            // against the finished world must read DIFFERENT, or the comparison above cannot see the defect it guards
            JsonElement f12 = doc.RootElement.GetProperty("scenes").EnumerateArray().First(x => x.GetProperty("id").GetString() == "F12_T3_S0");
            var st12 = f12.GetProperty("stages").EnumerateArray().ToList();
            int iHeater = st12.FindIndex(x => x.GetProperty("stage").GetString() == "Heater");
            BuildOptions o12 = Options(f12.GetProperty("settings"));
            CordWorld wh = StageWorld(f12.GetProperty("w").GetInt32(), f12.GetProperty("h").GetInt32(), st12[iHeater], out HashSet<Cell> lh);
            CordWorld wf = StageWorld(f12.GetProperty("w").GetInt32(), f12.GetProperty("h").GetInt32(), st12[st12.Count - 1], out HashSet<Cell> lf);
            var neg = Compare(new CordBuilder().Build(wh, o12, c => lh.Contains(c)), new CordBuilder().Build(wf, o12, c => lf.Contains(c)));
            check(iHeater >= 0 && neg.diff + neg.missing > 0, $"determinism control: heater-only ring vs finished ring reads different ({neg.diff} different, {neg.missing} missing)");
            check(scenes == 64 && ring == 4, $"determinism: replayed {scenes} floor scenes ({ring} ring), want 64 (4 ring)");
            Console.WriteLine($"determinism: {scenes - bad}/{scenes} floor scenes fresh == incremental");
        }
    }
}
