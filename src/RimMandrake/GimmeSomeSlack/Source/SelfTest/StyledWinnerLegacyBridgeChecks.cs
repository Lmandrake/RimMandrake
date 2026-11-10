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
