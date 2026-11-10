using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Aerial;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class BatchedLinkStyleMergeChecks
    {
        private static void Check(bool ok, string message) =>
            Program.Check(ok, "i2-batched-style-merge: " + message);

        private sealed class Member
        {
            internal int Id;
            internal bool Conduit;
            internal string Look, Colour;
            internal readonly List<Member> Neighbours = new List<Member>();
            internal readonly HashSet<Member> Touching = new HashSet<Member>();
        }

        private sealed class Graph
        {
            internal readonly List<Member> Members = new List<Member>();
            internal Member A, B, C;

            internal Member Add(int id, bool conduit, string look)
            {
                var m = new Member
                {
                    Id = id,
                    Conduit = conduit,
                    Look = look,
                    Colour = conduit && look == "Modern" ? "Orange" : null
                };
                Members.Add(m);
                return m;
            }

            internal void Connect(Member a, Member b, bool touching)
            {
                a.Neighbours.Add(b);
                b.Neighbours.Add(a);
                if (touching)
                {
                    a.Touching.Add(b);
                    b.Touching.Add(a);
                }
            }
        }

        private static Graph Scene()
        {
            var g = new Graph();
            var industrial = Enumerable.Range(1, 6)
                .Select(id => g.Add(id, true, "Industrial")).ToList();
            var modern = Enumerable.Range(7, 3)
                .Select(id => g.Add(id, true, "Modern")).ToList();

            g.A = g.Add(10, false, "Industrial");
            g.C = g.Add(11, false, "Industrial");
            g.B = g.Add(12, false, "Modern");

            for (int i = 1; i < industrial.Count; i++)
                g.Connect(industrial[i - 1], industrial[i], true);
            for (int i = 1; i < modern.Count; i++)
                g.Connect(modern[i - 1], modern[i], true);

            g.Connect(g.A, industrial[0], true);
            g.Connect(g.C, industrial[industrial.Count - 1], true);
            g.Connect(g.B, modern[0], true);

            // Both new spans already exist before either queued check runs.
            g.Connect(g.A, g.B, false);
            g.Connect(g.B, g.C, false);
            return g;
        }

        private static List<(Member, Member)> Queue(
            Graph g, bool reverseOrder, int reversedEndpoints)
        {
            var links = new List<(Member, Member)>
            {
                (g.A, g.B),
                (g.B, g.C)
            };
            for (int i = 0; i < links.Count; i++)
                if ((reversedEndpoints & (1 << i)) != 0)
                {
                    (Member a, Member b) = links[i];
                    links[i] = (b, a);
                }
            if (reverseOrder) links.Reverse();
            return links;
        }

        private static List<Member> Run(
            Member seed, List<(Member, Member)> pending,
            Member cutA = null, Member cutB = null,
            HashSet<Member> exclude = null)
        {
            return ConduitStyles.RunMembers(
                seed,
                m => m.Neighbours,
                exclude,
                cutA,
                cutB,
                (a, b) => a.Touching.Contains(b),
                pending,
                m => false,
                (a, b) => a.Id.CompareTo(b.Id));
        }

        private static ConduitStyles.Run Info(List<Member> members)
        {
            // Same inputs to the production placement rule as Info supplies:
            // conduit area, oldest id, oldest stored look, Modern run colour.
            string look = members.Select(m => m.Look).FirstOrDefault(l => l != null);
            return new ConduitStyles.Run
            {
                Area = members.Count(m => m.Conduit),
                Oldest = members.Min(m => m.Id),
                Look = look,
                Colour = look == "Modern"
                    ? ConduitStyles.RunColour(members
                        .Where(m => m.Conduit && m.Look == "Modern")
                        .Select(m => m.Colour))
                    : null
            };
        }

        private static int Drain(
            List<(Member, Member)> pending, bool hidePending)
        {
            int merges = 0;
            while (pending.Count > 0)
            {
                // Production ProcessPending removes the current pair FIRST.
                (Member a, Member b) = pending[0];
                pending.RemoveAt(0);
                var visiblePending = hidePending
                    ? pending
                    : new List<(Member, Member)>();

                List<Member> ra = Run(a, visiblePending, a, b);
                if (ra.Contains(b)) continue;
                List<Member> rb = Run(b, visiblePending, a, b);
                var runs = new List<List<Member>> { ra, rb };
                var infos = runs.Select(Info).ToList();
                ConduitStyles.Plan plan = ConduitStyles.PlanPlacement(
                    null, null, infos, "Scrapper");
                if (plan.Look == null) continue;

                // Pure style effect of Apply for these stored-style members.
                // Rendering, lamps and notification counters are outside this test.
                foreach (int loser in plan.Repaint)
                    foreach (Member m in runs[loser])
                    {
                        m.Look = plan.MaterialiseWinner ? null : plan.Look;
                        m.Colour = m.Conduit && m.Look == "Modern"
                            ? plan.Colour : null;
                    }
                merges++;
            }
            return merges;
        }

        public static void Run()
        {
            foreach (bool reverseOrder in new[] { false, true })
                for (int orientation = 0; orientation < 4; orientation++)
                {
                    string label = "order=" + reverseOrder
                        + ", reversed endpoints=" + orientation;
                    Graph g = Scene();
                    List<(Member, Member)> pending =
                        Queue(g, reverseOrder, orientation);

                    // Inspect the first Link's view after its pair is dequeued.
                    (Member a, Member b) = pending[0];
                    var later = pending.Skip(1).ToList();
                    List<Member> ra = Run(a, later, a, b);
                    List<Member> rb = Run(b, later, a, b);
                    Check(!ra.Contains(b) && !rb.Contains(a)
                        && !ra.Intersect(rb).Any()
                        && ra.Count + rb.Count == g.Members.Count,
                        label + ": first check sees two disjoint complete runs");
                    Check(new[] { Info(ra).Area, Info(rb).Area }
                        .OrderBy(n => n).SequenceEqual(new[] { 3, 6 }),
                        label + ": first check preserves the 6-versus-3 areas");

                    int merges = Drain(pending, true);
                    Check(merges == 1 && pending.Count == 0,
                        label + ": exactly one bridge is resolved");
                    Check(g.Members.All(m => m.Look == "Industrial"
                        && m.Colour == null),
                        label + ": the whole connected run takes Industrial");

                    // Negative control: permit later queued spans to be traversed.
                    // Both checks then find the alternate route and skip Apply.
                    Graph broken = Scene();
                    int skipped = Drain(
                        Queue(broken, reverseOrder, orientation), false);
                    Check(skipped == 0
                        && broken.Members.Select(m => m.Look).Distinct().Count() == 2,
                        label + ": allowing pending spans reproduces the finding");
                }

            Graph ordinary = Scene();
            var queued = Queue(ordinary, false, 0);
            Check(Run(ordinary.A, queued).Count == ordinary.Members.Count,
                "ordinary RunOf without a cut still sees pending spans");

            // A touching connection remains real even when the same pair also
            // names a current or pending aerial span.
            ordinary.A.Touching.Add(ordinary.B);
            ordinary.B.Touching.Add(ordinary.A);
            Check(Run(ordinary.A, queued, ordinary.A, ordinary.B)
                    .Contains(ordinary.B),
                "a current span cannot suppress a touching connection");
            Check(Run(ordinary.A, queued, ordinary.B, ordinary.C)
                    .Contains(ordinary.B),
                "a pending span cannot suppress a touching connection");
        }
    }
}
