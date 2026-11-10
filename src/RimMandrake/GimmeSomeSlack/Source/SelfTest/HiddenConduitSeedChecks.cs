using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static partial class HiddenConduitSeedChecks
    {
        private const string Prefix = "I3_HIDDEN_SEED: ";

        // mirrors RM_MapComponent_CordGraph.ComputeNetSeeds (Verse-bound class, not compiled offline); the logic under test is RebuildTail.NetSeeds
        private static Dictionary<LaidPiece, int> ComputeNetSeeds(List<LaidPiece> ps, CordGraph g) => RebuildTail.NetSeeds(ps, g?.HiddenLinks);

        internal static void Run()
        {
            // A single contiguous conduit net, with two exposed runs joined
            // through four wall cells. No machines or style overrides.
            var world = new CordWorld(22, 12);
            for (int x = 2; x <= 18; x++)
                world.SetConduit(new Cell(x, 5));
            for (int x = 8; x <= 11; x++)
                world.SetBlocked(new Cell(x, 5), BlockKind.Wall);

            var builder = new CordBuilder();
            List<LaidPiece> pieces =
                builder.Build(world, new BuildOptions(), c => true);
            CordGraph graph = builder.Graph;
            var visible = pieces.Where(p => p.Strands.Count > 0).ToList();

            bool valid = graph != null
                && graph.Edges.Any(e => e.Hidden)
                && graph.CordEdges().Count() >= 2
                && visible.Any(p => p.Owner.X < 8)
                && visible.Any(p => p.Owner.X > 11);

            Program.Check(valid, Prefix
                + "fixture has exposed strands on both sides of a hidden wall connection");
            if (!valid) return;

            // This method is extracted from the production map component
            // during the build; see the csproj target.
            Dictionary<LaidPiece, int> seeds =
                ComputeNetSeeds(pieces, graph);

            bool complete = visible.All(p => seeds.ContainsKey(p));
            Program.Check(complete, Prefix
                + "production forwarding returns a seed for every visible strand piece");
            if (!complete) return;

            // Mutation control: the original omission must actually split
            // this fixture, rather than passing through a seed collision.
            Dictionary<LaidPiece, int> omitted =
                RebuildTail.NetSeeds(pieces, null);
            bool distinguishesOmission =
                visible.All(p => omitted.ContainsKey(p))
                && visible.Select(p => omitted[p]).Distinct().Count() > 1;

            Program.Check(distinguishesOmission, Prefix
                + "omitting hidden links splits the fixture into multiple seed components");

            int netCount = visible.Select(p => seeds[p]).Distinct().Count();
            Program.Check(netCount == 1, Prefix
                + "both exposed runs share one legacy seed and one StyleProbe seed component"
                + " (actual " + netCount + ")");

            var reversed = new List<LaidPiece>(pieces);
            reversed.Reverse();
            Dictionary<LaidPiece, int> reordered =
                ComputeNetSeeds(reversed, graph);

            Program.Check(
                visible.All(p => reordered.TryGetValue(p, out int seed)
                    && seed == seeds[p]),
                Prefix + "hidden-connected net seeds are independent of piece enumeration order");
        }
    }
}
