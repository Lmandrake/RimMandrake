// Units for the stage read-back (JawaBenchStageReadBack.cs: the PRODUCTION file, or a planted copy). One unit per promise of
// design/specs/2026-11-23-bridge-v2/boundary.md §THE STAGE READ-BACK. Prints "U <name> ok|FAIL why" and "U-count n".
// The rows are recorded replies: what each tool records for a write that the game answered as asked, or otherwise.
using System;
using System.Collections;
using System.Collections.Generic;
using R = JawaBench.BridgeTools.StageReadBack;

namespace JawaBench.BridgeTools
{
    internal static class Program
    {
        private static readonly string[] Tools = { "jawa/set_terrain_batch", "jawa/destroy_batch", "jawa/spawn_pawn", "jawa/build_batch" };

        private static object At(object o, params object[] path)
        {
            foreach (var p in path)
            {
                if (o == null) return null;
                if (p is string s) { var d = o as Dictionary<string, object>; object v = null; if (d == null || !d.TryGetValue(s, out v)) return null; o = v; }
                else { var l = o as IList; int i = (int)p; if (l == null || i >= l.Count) return null; o = l[i]; }
            }
            return o;
        }

        private static string Str(object o) { return o == null ? null : Convert.ToString(o); }
        private static int Count(object o) { var l = o as IList; return l == null ? -1 : l.Count; }
        private static bool Has(object list, string s) { var l = list as IList; if (l == null) return false; foreach (var x in l) if (Str(x) == s) return true; return false; }

        private static string Need(bool c, string why) { return c ? null : why; }

        private static string First(params string[] fails) { foreach (var f in fails) if (f != null) return "FAIL " + f; return "ok"; }

        private static string ReplyFromReadBack()
        {
            var rb = R.Open("jawa/set_terrain_batch", 7);
            rb.Made("terrain", null, 10, 20).Want("terrain", "Sand").Got("terrain", "Gravel");      // the game holds Gravel
            rb.Made("terrain", null, 11, 20).Want("terrain", "Sand").Got("terrain", "Sand");
            var o = R.Reply(rb, 7);
            var good = R.Open("jawa/build_batch", 7);
            good.Made("thing", "Wall123", 3, 4).Want("def", "Wall").Want("stuff", "Steel").Got("def", "Wall").Got("stuff", "Steel").Got("hp", "300");
            var g = R.Reply(good, 7);
            return First(
                Need(At(o, "ok") is bool b && !b, "a cell that read Gravel for Sand gave ok " + Str(At(o, "ok"))),
                Need(Has(At(o, "faults"), "read_back_wrong"), "no read_back_wrong fault"),
                Need(Str(At(o, "rowsWrong")) == "1", "rowsWrong " + Str(At(o, "rowsWrong")) + ", want 1"),
                Need(Str(At(o, "wrong", 0, "got", "terrain")) == "Gravel", "the wrong row's read value is " + Str(At(o, "wrong", 0, "got", "terrain")) + ", want Gravel"),
                Need(Str(At(o, "made", 0, "got", "terrain")) == "Gravel", "the made row says " + Str(At(o, "made", 0, "got", "terrain")) + ": it echoes the request"),
                Need(Str(At(o, "wrong", 0, "wrong", 0, "want")) == "Sand" && Str(At(o, "wrong", 0, "wrong", 0, "got")) == "Gravel", "the wrong key does not name want Sand and got Gravel"),
                Need(At(g, "ok") is bool gb && gb, "a build that read back as asked gave ok " + Str(At(g, "ok")) + " " + string.Join(",", (IEnumerable<string>)At(g, "faults") ?? new string[0])),
                Need(Str(At(g, "made", 0, "got", "hp")) == "300", "a read-only value (hp) is not on the reply"));
        }

        private static string ReplacedPawnKind()
        {
            var rb = R.Open("jawa/spawn_pawn", 9);
            rb.Made("pawn", "Human501", 5, 5).Want("kind", "RSW_JawaScavenger").Got("kind", "Colonist").Got("faction", "OutlanderCivil").Got("spawned", "True");
            var o = R.Reply(rb, 9);
            return First(
                Need(At(o, "ok") is bool b && !b, "a replaced kind gave ok " + Str(At(o, "ok"))),
                Need(Str(At(o, "made", 0, "got", "kind")) == "Colonist", "the pawn is reported as " + Str(At(o, "made", 0, "got", "kind")) + ", not the kind as made (Colonist)"),
                Need(Str(At(o, "wrong", 0, "wrong", 0, "key")) == "kind", "the wrong key is " + Str(At(o, "wrong", 0, "wrong", 0, "key")) + ", want kind"));
        }

        private static string OneFrame()
        {
            foreach (var t in Tools)
            {
                var rb = R.Open(t, 100);
                rb.Made("thing", "a", 1, 1).Want("def", "X").Got("def", "X");
                var same = R.Reply(rb, 100);
                var moved = R.Reply(rb, 101);
                var f = First(
                    Need(At(same, "ok") is bool a && a && At(same, "sameFrame") is bool s && s, t + ": the same frame gave ok " + Str(At(same, "ok"))),
                    Need(Str(At(same, "frameOpen")) == "100" && Str(At(same, "frameReply")) == "100", t + ": the frames are not on the reply"),
                    Need(At(moved, "ok") is bool m && !m && Has(At(moved, "faults"), "frame_moved"), t + ": a frame that moved between write and read gave ok " + Str(At(moved, "ok"))),
                    Need(Str(At(same, "tool")) == t, t + ": the reply names tool " + Str(At(same, "tool"))));
                if (f != "ok") return f;
            }
            return "ok";
        }

        private static string CleanNamesLeft()
        {
            var rb = R.Open("jawa/destroy_batch", 3);
            rb.Left("Corpse_Human", "Corpse_Human77", 12, 14, "still standing after Destroy", true);
            rb.Left("SteamGeyser", "SteamGeyser2", 13, 14, "not destroyable", false);
            var o = R.Reply(rb, 3);
            var kept = R.Open("jawa/destroy_batch", 3);
            kept.Left("SteamGeyser", "SteamGeyser2", 13, 14, "not destroyable", false);
            var k = R.Reply(kept, 3);
            return First(
                Need(At(o, "ok") is bool b && !b, "a clean that left a corpse gave ok " + Str(At(o, "ok"))),
                Need(Has(At(o, "faults"), "left_behind"), "no left_behind fault"),
                Need(Str(At(o, "left", 0, "def")) == "Corpse_Human" && Str(At(o, "left", 0, "x")) == "12", "the corpse is not named with its cell"),
                Need(Str(At(o, "leftBlocking")) == "1" && Str(At(o, "leftKept")) == "1", "leftBlocking/leftKept " + Str(At(o, "leftBlocking")) + "/" + Str(At(o, "leftKept"))),
                Need(At(k, "ok") is bool kb && kb, "a clean that kept only a thing it may not destroy gave ok " + Str(At(k, "ok"))),
                Need(Str(At(k, "left", 0, "def")) == "SteamGeyser", "the kept thing is not named"));
        }

        private static string RefusalMakesNothing()
        {
            var rb = R.Open("jawa/spawn_pawn", 4);
            rb.Refuse("NO_MAP", "no current map");
            var o = R.Reply(rb, 4);
            var late = R.Open("jawa/build_batch", 4);
            late.Made("thing", "a", 1, 1).Want("def", "Wall").Got("def", "Wall");
            late.Made("thing", "b", 2, 1).Want("def", "Wall").Got("def", "Wall");
            late.Refuse("CANCELLED", "the caller cancelled");
            var l = R.Reply(late, 4);
            return First(
                Need(At(o, "ok") is bool b && !b, "a refusal gave ok " + Str(At(o, "ok"))),
                Need(Str(At(o, "refusal", "name")) == "NO_MAP", "the refusal is named " + Str(At(o, "refusal", "name"))),
                Need(Str(At(o, "rows")) == "0" && Count(At(o, "made")) == 0 && Str(At(o, "refusal", "madeBefore")) == "0", "a refusal before the first write lists things made"),
                Need(At(l, "ok") is bool lb && !lb, "a late refusal gave ok " + Str(At(l, "ok"))),
                Need(Str(At(l, "refusal", "madeBefore")) == "2" && Count(At(l, "made")) == 2, "a late refusal hides what it made: madeBefore " + Str(At(l, "refusal", "madeBefore"))));
        }

        private static R Build(bool reversed, string idPrefix, string hp, int frame)
        {
            var rb = R.Open("jawa/build_batch", frame);
            var cells = new List<int[]> { new[] { 1, 1 }, new[] { 2, 1 }, new[] { 3, 1 } };
            if (reversed) cells.Reverse();
            foreach (var c in cells)
                rb.Made("thing", idPrefix + c[0], c[0], c[1]).Want("def", "Wall").Got("def", "Wall").Got("stuff", "Steel").Got("hp", c[0] == 2 ? hp : "300");
            rb.Left("Filth_Dirt", idPrefix + "f", 4, 1, "still standing", true);
            return rb;
        }

        private static string Digests()
        {
            var a = Str(At(R.Reply(Build(false, "Wall", "300", 10), 10), "digest"));
            var b = Str(At(R.Reply(Build(true, "Wall9", "300", 55), 55), "digest"));
            var c = Str(At(R.Reply(Build(false, "Wall", "299", 10), 10), "digest"));
            return First(
                Need(!string.IsNullOrEmpty(a), "no digest"),
                Need(a == b, "two builds of one request (other ids, other order, other frame) gave digests " + a + " and " + b),
                Need(a != c, "a different read value (hp 299) gave the same digest " + a));
        }

        private static int Main()
        {
            var units = new List<KeyValuePair<string, Func<string>>>
            {
                new KeyValuePair<string, Func<string>>("a_reply_is_built_from_the_read_back_never_the_request", ReplyFromReadBack),
                new KeyValuePair<string, Func<string>>("a_replaced_pawn_kind_is_reported_as_made", ReplacedPawnKind),
                new KeyValuePair<string, Func<string>>("the_write_and_the_read_back_share_one_frame", OneFrame),
                new KeyValuePair<string, Func<string>>("a_clean_that_left_a_thing_names_it", CleanNamesLeft),
                new KeyValuePair<string, Func<string>>("a_refusal_by_name_leaves_nothing_made", RefusalMakesNothing),
                new KeyValuePair<string, Func<string>>("two_builds_of_one_request_give_equal_digests", Digests),
            };
            foreach (var u in units)
            {
                string v;
                try { v = u.Value(); }
                catch (Exception e) { v = "FAIL threw " + e.GetType().Name + ": " + e.Message; }
                Console.WriteLine("U " + u.Key + " " + v);
            }
            Console.WriteLine("U-count " + units.Count);
            return 0;
        }
    }
}
