using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Aerial;
using RimMandrake.GimmeSomeSlack.Core;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class StyledWinnerLegacyBridgeChecks
    {
        private const string Prefix = "I5_STYLED_WINNER_BRIDGE: ";

        private static void Check(bool ok, string message) =>
            Program.Check(ok, Prefix + message);

        private sealed class Node
        {
            internal readonly int Id;
            internal readonly bool Bridge;
            internal readonly List<Node> Adjacent = new List<Node>();
            internal string StoredLook;

            internal Node(int id, string storedLook = null, bool bridge = false)
            {
                Id = id;
                StoredLook = storedLook;
                Bridge = bridge;
            }
        }

        private static void Join(Node a, Node b)
        {
            a.Adjacent.Add(b);
            b.Adjacent.Add(a);
        }

        private static ConduitStyles.Run Describe(List<Node> run)
        {
            // Fixture nodes are conduit members or unstyleable bridge conduits.
            // This is Info's area, oldest-member and first-stored-look projection.
            return new ConduitStyles.Run
            {
                Area = run.Count(n => !n.Bridge),
                Oldest = run.Min(n => n.Id),
                Look = run.Select(n => n.StoredLook).FirstOrDefault(l => l != null)
            };
        }

        private static void Paint(Node node, string look, string defaultLook, bool force)
        {
            // A minimal style sink: the production NeedsWrite decides whether a
            // member stores the requested look. No drawing or Verse APIs are mocked.
            if (ConduitStyles.NeedsWrite(
                node.StoredLook != null, true, look, null, defaultLook, force))
                node.StoredLook = look;
        }

        public static void Run()
        {
            BatchSummaries();
            Check(
                !ConduitStyles.NeedsWrite(
                    false, true, "Industrial", null, "Industrial", false)
                && ConduitStyles.NeedsWrite(
                    false, true, "Industrial", null, "Industrial", true),
                "control: default-look legacy members require the force supplied by Apply");

            foreach (string look in new[] { "Industrial", "Modern", "Scrapper", "Futuristic" })
                foreach (bool bridge in new[] { false, true })
                    foreach (bool reverse in new[] { false, true })
                        foreach (bool styledWinner in new[] { false, true })
                            Placement(look, bridge, reverse, styledWinner);
        }

        private static void BatchSummaries()
        {
            foreach (int count in new[] { 1000, 2000 })
            {
                int reads = 0;
                ConduitStyles.Run DescribeOne(Node n)
                {
                    reads++;
                    return new ConduitStyles.Run { Area = 1, Oldest = n.Id, Look = n.StoredLook,
                        Colour = n.StoredLook == "Modern" ? (n.Id % 3 == 0 ? "Orange" : "Blue") : null };
                }
                ConduitStyles.Run Reference(List<Node> members)
                {
                    var ordered = members.OrderBy(n => n.Id).ToList();
                    string look = ordered.Select(n => n.StoredLook).FirstOrDefault(l => l != null);
                    return new ConduitStyles.Run { Area = ordered.Count, Oldest = ordered[0].Id, Look = look,
                        Colour = look == "Modern" ? ConduitStyles.RunColour(ordered.Where(n => n.StoredLook == "Modern")
                            .Select(n => n.Id % 3 == 0 ? "Orange" : "Blue")) : null };
                }
                void Equal(ConduitStyles.Run a, ConduitStyles.Run b, string why) =>
                    Check(a.Area == b.Area && a.Oldest == b.Oldest && a.Look == b.Look && a.Colour == b.Colour, why);
                var batch = new ConduitStyles.PlacementBatch<Node>();
                var members = new List<Node> { new Node(count * 2, "Industrial") };
                batch.Remember(members, DescribeOne);
                for (int i = 1; i < count; i++)
                {
                    // Reverse ids, mixed raw storage and colours exercise Info's oldest-styled rule.
                    var n = new Node(count * 2 - i, i % 5 == 0 ? null : i % 3 == 0 ? "Industrial" : "Modern");
                    var groups = batch.Groups(new[] { members[0], members[members.Count - 1] });
                    Check(groups != null && groups.Count == 1, "batch: repeated neighbours resolve one cached run");
                    batch.Merge(n, DescribeOne(n), groups);
                    members.Add(n);
                }
                Equal(batch.Groups(new[] { members[0] })[0].Info, Reference(members), "batch: extension matches sorted Info");
                Check(reads == count, "batch: " + count + " placements describe exactly " + count + " members, no growing-run scan");

                var island = new Node(1, "Modern");
                batch.Remember(new[] { island }, DescribeOne);
                var two = batch.Groups(new[] { members[0], island });
                var plan = ConduitStyles.PlanPlacement(null, null, two.Select(g => g.Info).ToList(), "Scrapper");
                Check(plan.Winner == 0, "batch: cached area keeps the larger run's style");
                // The actual style sink is read again after repaint, including a failed/missing-style write.
                island.StoredLook = "Industrial";
                batch.Refresh(two[1], DescribeOne);
                var bridge = new Node(0);
                batch.Merge(bridge, DescribeOne(bridge), two);
                members.Add(island); members.Add(bridge);
                Equal(batch.Groups(new[] { island, members[0], bridge })[0].Info, Reference(members),
                    "batch: repaint + small-to-large merge matches sorted Info");
                Check(batch.Groups(new[] { new Node(-1) }) == null, "batch: unknown neighbours require discovery");
                batch.Clear();
                Check(batch.Groups(new[] { members[0] }) == null, "batch: no run state survives the batch");

                // Each queued connector also touches a previously unknown old island.
                // Discovery must stop at the cached growing run instead of flooding it again.
                reads = 0;
                int visits = 0;
                var previous = new Node(count * 4 + 1, "Modern");
                members = new List<Node> { previous };
                batch.Remember(members, DescribeOne);
                for (int i = 0; i < count; i++)
                {
                    var old = new Node(i * 2 + 1, "Industrial");
                    var placed = new Node(i * 2 + 2, "Modern");
                    Join(previous, placed); Join(placed, old);
                    var groups = batch.Resolve(placed.Adjacent, n => n.Adjacent,
                        n => n == placed, n => n.Bridge, DescribeOne, () => visits++);
                    batch.Merge(placed, DescribeOne(placed), groups);
                    members.Add(old); members.Add(placed);
                    previous = placed;
                }
                Equal(batch.Groups(new[] { previous })[0].Info, Reference(members),
                    "batch: unknown islands preserve the full sorted run summary");
                Check(visits == count && reads == 2 * count + 1,
                    "batch: unknown islands visit only " + count + " old members, not the growing run");
                var external = new Node(-2, bridge: true);
                Check(batch.Resolve(new[] { external }, n => n.Adjacent, n => false, n => n.Bridge,
                    DescribeOne, null) == null && batch.Groups(new[] { previous }) == null,
                    "batch: external bridges clear the cache and retain the original flood rule");
            }
        }

        private static void Placement(
            string defaultLook, bool throughBridge, bool reverse, bool styledWinner)
        {
            string label = defaultLook
                + (throughBridge ? "/bridge" : "/direct")
                + (reverse ? "/reverse" : "/forward")
                + (styledWinner ? "/styled-winner" : "/legacy-only");

            // Spatially this is a straight line:
            //
            // winner(3 cells) -- [optional external bridge] -- newcomer -- legacy(2 cells)
            //
            // The bridge is traversable but cannot store a run style or count
            // toward its area. The newcomer is still pending during discovery.
            var winner = new[]
            {
                new Node(10, styledWinner ? defaultLook : null),
                new Node(11, styledWinner ? defaultLook : null),
                new Node(12, styledWinner ? defaultLook : null)
            };
            var legacy = new[] { new Node(1), new Node(2) };
            var newcomer = new Node(100);
            var externalBridge = new Node(50, bridge: true);

            Join(winner[0], winner[1]);
            Join(winner[1], winner[2]);
            Join(legacy[0], legacy[1]);
            Join(newcomer, legacy[0]);

            if (throughBridge)
            {
                Join(winner[2], externalBridge);
                Join(externalBridge, newcomer);
            }
            else Join(winner[2], newcomer);

            var neighbours = newcomer.Adjacent.ToList();
            if (reverse) neighbours.Reverse();

            var excluded = new HashSet<Node> { newcomer };
            var seen = new HashSet<Node>();
            var runs = new List<List<Node>>();

            foreach (Node neighbour in neighbours)
            {
                if (seen.Contains(neighbour)) continue;
                List<Node> run = ConduitStyles.RunMembers<Node>(
                    neighbour,
                    n => n.Adjacent,
                    excluded,
                    null,
                    null,
                    (a, b) => true, // all fixture edges are touching connections
                    new List<(Node, Node)>(),
                    n => n.Bridge,
                    (a, b) => a.Id.CompareTo(b.Id));
                seen.UnionWith(run);
                runs.Add(run);
            }

            var infos = runs.Select(Describe).ToList();
            bool valid = infos.Count == 2
                && infos.Select(r => r.Area).OrderBy(n => n)
                    .SequenceEqual(new[] { 2, 3 })
                && runs.All(r => !r.Contains(newcomer));

            Check(valid, label + ": production flood discovers separate 3-cell and 2-cell runs");
            if (!valid) return;

            ConduitStyles.Plan plan =
                ConduitStyles.PlanPlacement(null, null, infos, defaultLook);

            Check(
                plan.Winner >= 0
                && infos[plan.Winner].Area == 3
                && plan.Look == (styledWinner ? defaultLook : null)
                && (!styledWinner
                    || (!plan.MaterialiseWinner && plan.Repaint.Count == 1)),
                label + ": production planner selects the larger run and its stored-style policy");

            bool skip = ConduitPlacementGate.CanSkip(
                null,
                neighbours.Select(n => new ConduitPlacementGate.Neighbour(
                    n.StoredLook != null, n.Bridge)));

            // The assertion tests the actual extracted production gate against
            // the reachable runs found by the actual production flood.
            Check(
                !skip || infos.All(r => r.Look == null),
                label + ": fast path must not hide a reachable styled run");

            // Model only the style-storage effects after the gate. The force
            // values below are exactly those supplied by Apply and Place.
            if (!skip && plan.Look != null)
            {
                bool stored = !plan.MaterialiseWinner && plan.Look != null;
                foreach (int i in plan.Repaint)
                    foreach (Node node in runs[i].Where(n => !n.Bridge))
                    {
                        if (plan.MaterialiseWinner) node.StoredLook = null;
                        else Paint(node, plan.Look, defaultLook, stored);
                    }

                if (plan.MaterialiseWinner) newcomer.StoredLook = null;
                else Paint(newcomer, plan.Look, defaultLook, true);
            }

            var members = winner.Concat(legacy).Concat(new[] { newcomer }).ToList();

            Check(
                members.All(n => (n.StoredLook ?? defaultLook) == defaultLook),
                label + ": all members initially draw the same look");

            string changedDefault = defaultLook == "Modern" ? "Industrial" : "Modern";
            string expectedLook = styledWinner ? defaultLook : changedDefault;

            Check(
                members.All(n => (n.StoredLook ?? changedDefault) == expectedLook),
                label + ": changing the default preserves one look across the connected run");

            Check(
                styledWinner
                    ? members.All(n => n.StoredLook == defaultLook)
                    : members.All(n => n.StoredLook == null),
                label + ": styled winners persist their look; all-legacy runs remain legacy");
        }
    }
}
