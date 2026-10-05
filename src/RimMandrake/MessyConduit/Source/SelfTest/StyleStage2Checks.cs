// Per-build style, stage 2 (design/RimMandrake/messyconduit_style_per_build_design.md section 2, owner decisions
// 2026-10-04): the Verse-free run rules and material selection in ../Aerial/ConduitStyles.cs. Each property has a
// can-fail beside it.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.MessyConduit.Aerial;

namespace RimMandrake.MessyConduit.SelfTest
{
    internal static class StyleStage2Checks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "style2: " + msg);

        public static void Run()
        {
            Naming();
            Runs();
            Bridge();
            Split();
            Colours();
            Writes();
            Materials();
            Spans();
        }

        private static void Naming()
        {
            var names = ConduitStyles.AllStyleDefNames().ToList();
            bool round = names.All(n => ConduitStyles.TryParseStyleDefName(n, out string d, out string l, out string c) &&
                                        ConduitStyles.StyleDefName(d, l, c) == n);
            Check(names.Count == 24 && names.Distinct().Count() == 24 && round && ConduitStyles.KeysFor("PowerConduit").Count == 10 &&
                  ConduitStyles.KeysFor("PowerSwitch").Count == 4,
                  $"naming: 2 conduit defs x 10 keys (4 looks + 5 Modern colours + Mix) + switch x 4 looks = {names.Count} distinct style defs, each parses back");
            bool rejects = !ConduitStyles.TryParseStyleDefName("PowerSwitch_Modern_Orange", out _, out _, out _) &&
                           !ConduitStyles.TryParseStyleDefName("PowerConduit_Modern_Purple", out _, out _, out _) &&
                           !ConduitStyles.TryParseStyleDefName("RM_AerialMast_Modern", out _, out _, out _) &&
                           !ConduitStyles.TryParseStyleDefName("PowerConduit_Gold", out _, out _, out _) &&
                           !ConduitStyles.TryParseStyleDefName(null, out _, out _, out _) &&
                           !ConduitStyles.TryParseKey("Modern_Multi", out _, out _);
            Check(rejects, "can fail: a switch with a colour, an unknown colour, a pole style, a non-look and the menu-only Multi never parse as stored styles");
        }

        // a row of cells: id = x, neighbours = x +- 1 (a straight conduit line)
        private static IEnumerable<int> Line(int x) { yield return x - 1; yield return x + 1; }

        private static void Runs()
        {
            var cells = Enumerable.Range(1, 6).Concat(Enumerable.Range(8, 3)).ToList();
            List<List<int>> two = ConduitStyles.Components(cells, Line);
            List<List<int>> one = ConduitStyles.Components(cells.Concat(new[] { 7 }), Line);
            Check(two.Count == 2 && two[0].SequenceEqual(Enumerable.Range(1, 6)) && two[1].SequenceEqual(new[] { 8, 9, 10 }) && one.Count == 1 && one[0].Count == 10,
                  "runs: a gap splits a line into 2 runs (6 + 3 cells), the bridging cell joins them into 1");
            // the flood fill follows the neighbour function only: a battery between two runs is not a member, so it is no link
            List<List<int>> viaBattery = ConduitStyles.Components(new[] { 1, 2, 4, 5 }, Line);
            Check(viaBattery.Count == 2, "can fail: two runs touching only a non-member (a battery at 3) stay two runs");
        }

        private static ConduitStyles.Run R(int area, int oldest, string look, string colour = null) =>
            new ConduitStyles.Run { Area = area, Oldest = oldest, Look = look, Colour = colour };

        private static void Bridge()
        {
            const string D = "Scrapper";
            // owner 2026-10-04: the LARGEST run wins (conduit cells), a tie goes to the OLDER run
            int w1 = ConduitStyles.Winner(new[] { R(3, 1, "Modern", "Orange"), R(6, 50, "Industrial") });
            int w2 = ConduitStyles.Winner(new[] { R(4, 50, "Futuristic"), R(4, 9, "Industrial") });
            Check(w1 == 1 && w2 == 1, "bridge: 6 cells beat 3 although the 3-cell run is older; equal areas -> the older run (lower id)");
            Check(ConduitStyles.Winner(new[] { R(3, 1, "Modern"), R(6, 50, "Industrial") }) != 0, "can fail: an older-run-wins rule would keep the 3-cell Modern run");

            ConduitStyles.Plan none = ConduitStyles.PlanPlacement("Futuristic", null, new ConduitStyles.Run[0], D);
            ConduitStyles.Plan adopt = ConduitStyles.PlanPlacement("Futuristic", null, new[] { R(5, 3, "Industrial") }, D);
            Check(none.Look == "Futuristic" && none.Repaint.Count == 0 && adopt.Look == "Industrial" && adopt.Repaint.Count == 0 && !adopt.StylesDiffered,
                  "placement: alone it keeps the picked style; touching one run it adopts that run's, whatever the button said");
            ConduitStyles.Plan br = ConduitStyles.PlanPlacement("Futuristic", null, new[] { R(3, 1, "Modern", "Orange"), R(6, 50, "Industrial") }, D);
            Check(br.Look == "Industrial" && br.Winner == 1 && br.Repaint.SequenceEqual(new[] { 0 }) && br.StylesDiffered && br.LoserLook == "Modern",
                  "placement bridging Modern(3) and Industrial(6): Industrial, the Modern run repainted, a message naming Modern and Industrial");
            ConduitStyles.Plan mix = ConduitStyles.PlanPlacement("Industrial", null, new[] { R(8, 40, "Modern", ConduitStyles.Mix), R(2, 1, "Modern", "Blue") }, D);
            Check(mix.Look == "Modern" && mix.Colour == ConduitStyles.Mix && mix.Repaint.SequenceEqual(new[] { 1 }) && !mix.StylesDiffered,
                  "a merge keeps the larger run's colour (card CORD_COLOUR_PER_PIECE_1): the small blue run becomes the larger run's mix");
            ConduitStyles.Plan leg0 = ConduitStyles.PlanPlacement(null, null, new[] { R(4, 2, null), R(3, 9, null) }, D);
            ConduitStyles.Plan leg1 = ConduitStyles.PlanPlacement("Futuristic", null, new[] { R(4, 2, null) }, "Modern");
            ConduitStyles.Plan leg2 = ConduitStyles.PlanPlacement(null, null, new[] { R(9, 2, null), R(3, 1, "Futuristic") }, "Modern");
            Check(leg0.Look == null && leg0.Repaint.Count == 0 && leg1.Look == "Modern" && leg1.MaterialiseWinner &&
                  leg2.Look == "Modern" && leg2.MaterialiseWinner && leg2.Repaint.SequenceEqual(new[] { 1 }) && leg2.StylesDiffered,
                  "legacy: an unstyled piece joining legacy runs writes nothing; a styled piece joining one writes it for real in the default look; a larger legacy run wins as the default look");
            Check(ConduitStyles.KeyForMember(true, "Modern", "Orange") == "Modern_Orange" && ConduitStyles.KeyForMember(false, "Modern", "Orange") == "Modern" &&
                  ConduitStyles.KeyForMember(true, "Industrial", "Orange") == "Industrial" && ConduitStyles.KeyForMember(true, "Modern", ConduitStyles.Mix) == "Modern_Mix",
                  "a run's colour lands on its conduit cells only; switches and poles carry the look alone; a colour never rides a non-Modern look");
        }

        private static void Split()
        {
            // a run of 9 Industrial cells (ids 1..9); deconstructing cell 5 leaves 1..4 and 6..9; nothing is written, so each
            // half still reads Industrial and is uniform
            var style = Enumerable.Range(1, 9).ToDictionary(i => i, i => "Industrial");
            style.Remove(5);
            List<List<int>> halves = ConduitStyles.Components(style.Keys, Line);
            bool kept = halves.Count == 2 && halves.All(h => h.Select(i => style[i]).Distinct().Count() == 1 && style[h[0]] == "Industrial");
            Check(kept, "split: deconstructing the middle cell leaves 2 runs, each keeping Industrial with no decision needed");
            // can fail: a split that re-ran the bridge rule over the halves would 'repaint' the smaller one -- it must not
            ConduitStyles.Plan noBridge = ConduitStyles.PlanPlacement(null, null, new[] { R(4, 1, "Industrial") }, "Scrapper");
            Check(noBridge.Repaint.Count == 0, "can fail: a single run touched by nothing new is never repainted");
        }

        /// <summary>Pairs of pieces that share a node and have the same colour.</summary>
        private static int MixClashes(List<KeyValuePair<string, string[]>> ps, Dictionary<string, int> col)
        {
            int n = 0;
            for (int i = 0; i < ps.Count; i++)
                for (int j = i + 1; j < ps.Count; j++)
                    if (ps[i].Value.Intersect(ps[j].Value).Any() && col[ps[i].Key] == col[ps[j].Key]) n++;
            return n;
        }

        private static void Colours()
        {
            Check(ConduitStyles.RunColour(new[] { "Blue", "Blue", null }) == "Blue" && ConduitStyles.RunColour(new[] { "Blue", "Green" }) == ConduitStyles.Mix &&
                  ConduitStyles.RunColour(new[] { "Blue", ConduitStyles.Mix }) == ConduitStyles.Mix && ConduitStyles.RunColour(new string[] { null, null }) == null,
                  "run colour: one colour -> that colour; two colours or any mix cell -> mix; nothing stored -> none");
            var line = Enumerable.Range(0, 12).Select(x => ConduitStyles.PieceVariant("Modern", ConduitStyles.Mix, 40 + x, 70, 12345, false, 0)).ToList();
            Check(line.Distinct().Count() >= 3, $"random mix fallback cell hash (before pieces are known): 12 cells show {line.Distinct().Count()} colours");
            // round 5 (owner 2026-10-04, station 5): REVERTS the round-4 3-cell-block change along a cord. Each mix piece, node to
            // node, is ONE colour; colours vary piece to piece and pieces sharing a node differ where 5 colours allow.
            KeyValuePair<string, string[]> P(string k, string a, string b) => new KeyValuePair<string, string[]>(k, new[] { a, b });
            // a tree of degree <= 3 (battery - J1 - J2 - lamp, spurs off J1 and J2): every piece has <= 4 node neighbours < 5 colours
            var tree = new List<KeyValuePair<string, string[]>> { P("e:0,0|5,0", "0,0", "5,0"), P("e:5,0|9,0", "5,0", "9,0"), P("e:9,0|14,0", "9,0", "14,0"),
                                                                  P("e:5,0|5,4", "5,0", "5,4"), P("e:9,0|9,4", "9,0", "9,4") };
            Dictionary<string, int> tc = ConduitStyles.MixPieceColours(tree);
            Check(tc.Count == 5 && MixClashes(tree, tc) == 0 && tc.Values.Distinct().Count() >= 2,
                  $"mix per piece: a 5-piece nodal tree -> {tc.Values.Distinct().Count()} colours, {MixClashes(tree, tc)} pieces sharing a node with the same colour (want 0)");
            var shuffled = tree.AsEnumerable().Reverse().ToList();
            Check(ConduitStyles.MixPieceColours(shuffled).OrderBy(kv => kv.Key).SequenceEqual(tc.OrderBy(kv => kv.Key)),
                  "mix per piece: the colours do not depend on the order the pieces are listed (rebuild / save-load stable)");
            // a 4x4 node grid (24 pieces, + nodes): the colours spread through the whole array, almost no clashes
            var grid = new List<KeyValuePair<string, string[]>>();
            for (int x = 0; x < 4; x++)
                for (int z = 0; z < 4; z++)
                {
                    if (x < 3) grid.Add(P($"g:{x},{z}>", $"{x},{z}", $"{x + 1},{z}"));
                    if (z < 3) grid.Add(P($"g:{x},{z}^", $"{x},{z}", $"{x},{z + 1}"));
                }
            Dictionary<string, int> gc = ConduitStyles.MixPieceColours(grid);
            Check(gc.Values.Distinct().Count() >= 4 && MixClashes(grid, gc) <= 2,
                  $"mix per piece: a 4x4 nodal grid of 24 pieces shows {gc.Values.Distinct().Count()} colours, {MixClashes(grid, gc)} clashes (want >= 4, <= 2)");
            var planted = tc.ToDictionary(kv => kv.Key, kv => 0);
            Check(MixClashes(tree, planted) > 0, "can fail: a planted all-one-colour tree is reported as clashing");
            // a straight run between two nodes is one piece: one colour along its whole length (no per-cell change)
            var one = ConduitStyles.MixPieceColours(new[] { P("e:66,149|73,149", "66,149", "73,149") });
            Check(one.Count == 1 && one.Values.All(c => c >= 0 && c < 5), "mix per piece: a straight node-to-node cord gets exactly one colour");
            var uniform = Enumerable.Range(0, 12).Select(x => ConduitStyles.PieceVariant("Modern", "Brown", 40 + x, 70, x * 7919, false, 0)).Distinct().ToList();
            Check(uniform.Count == 1 && uniform[0] == ConduitStyles.ColourIndex("Brown"), "a single-colour run is that colour on every cell whatever its cord net seed");
            Check(ConduitStyles.PieceVariant("Modern", "Brown", 1, 1, 5, true, 4) != ConduitStyles.ColourIndex("Blue"),
                  "can fail: the global single-colour setting (Blue) no longer overrides a run's stored colour");
        }

        private static void Writes()
        {
            // live 2026-10-04 (S7/S8): an unstyled mast auto-linked into a Scrapper run had Scrapper WRITTEN. A member with no
            // stored style is written only when its drawing would change, or on a Restyle
            const string D = "Scrapper";
            bool keep = !ConduitStyles.NeedsWrite(false, false, "Scrapper", null, D, false) && !ConduitStyles.NeedsWrite(false, true, "Scrapper", null, D, false)
                        && !ConduitStyles.NeedsWrite(false, true, "Modern", null, "Modern", false);
            bool write = ConduitStyles.NeedsWrite(false, false, "Industrial", null, D, false) && ConduitStyles.NeedsWrite(false, true, "Modern", "Blue", "Modern", false)
                         && ConduitStyles.NeedsWrite(false, true, "Modern", ConduitStyles.Mix, "Modern", false) && ConduitStyles.NeedsWrite(false, false, "Scrapper", null, D, true)
                         && ConduitStyles.NeedsWrite(true, false, "Scrapper", null, D, false);
            Check(keep, "legacy kept: an unstyled pole / cell joining a default-look run (or a Modern run with no stored colour) stores nothing");
            Check(write, "can fail: a non-default look, a stored Modern colour or mix, a Restyle, or an already-styled member IS written");
        }

        /// <summary>The pre-stage-2 CordMaterials.VariantFor, copied verbatim as the reference (n = strands the global set had).</summary>
        private static int OldVariantFor(int netSeed, int n, bool starWars)
        {
            if (n <= 1) return 0;
            uint h = unchecked((uint)netSeed * 2654435761u);
            h ^= h >> 15;
            if (starWars && n == 3)
            {
                int[] w = { 6, 2, 2 };
                int r = (int)(h % 10u), acc = 0;
                for (int i = 0; i < n; i++) { acc += w[i]; if (r < acc) return i; }
                return 0;
            }
            return (int)(h % (uint)n);
        }

        private static void Materials()
        {
            int n = ConduitStyles.GlobalCount;
            bool round = true;
            var seen = new HashSet<int>();
            foreach (string look in AerialStyles.Looks)
                for (int v = 0; v < ConduitStyles.VariantsOf(look); v++)
                {
                    int g = ConduitStyles.Global(look, v);
                    ConduitStyles.FromGlobal(g, out string l2, out int v2);
                    round &= l2 == look && v2 == v && seen.Add(g);
                }
            Check(n == 10 && round && seen.Count == 10, "materials: one flat index per (look, strand) = 1 + 3 + 5 + 1, every index maps back to its look and strand");
            // legacy: a piece with no stored style draws the default look's OLD per-net pick (old strands: Scrapper 1,
            // Industrial 3 weighted, Modern 5 (Mixed) or the 1 chosen colour (Single), Futuristic 1)
            int bad = 0, total = 0;
            var rng = new Random(7);
            for (int i = 0; i < 400; i++)
            {
                int seed = rng.Next(int.MinValue, int.MaxValue);
                foreach (string look in AerialStyles.Looks)
                    foreach (bool single in new[] { false, true })
                    {
                        int oldN = look == "Modern" ? (single ? 1 : 5) : look == "Industrial" ? 3 : 1;
                        int oldV = OldVariantFor(seed, oldN, look == "Industrial");
                        // the old Single set's ONE strand is the chosen colour (index 2 here)
                        int oldStrand = look == "Modern" && single ? 2 : oldV;
                        int now = ConduitStyles.PieceVariant(look, null, i, 0, seed, single, 2);
                        total++;
                        if (ConduitStyles.Global(look, now) != ConduitStyles.Global(look, oldStrand)) bad++;
                    }
            }
            Check(bad == 0, $"legacy materials: {total} (seed, default look, colour mode) cases choose the same strand as before stage 2 ({bad} differ)");
            Check(ConduitStyles.PieceVariant("Industrial", "Orange", 0, 0, 99, false, 0) == OldVariantFor(99, 3, true),
                  "Industrial cable kind stays a per-cord-net pick (the owner chose colour per run for Modern only)");
            int wrong = Enumerable.Range(0, 200).Count(s => ConduitStyles.LegacyVariant("Industrial", s, false, 0) != OldVariantFor(s, 3, false));
            Check(wrong > 0, "can fail: an unweighted Industrial pick would differ from the 6/2/2 rule on some seeds");
        }

        private static void Spans()
        {
            const string D = "Scrapper";
            Check(ConduitStyles.SpanLook("Modern", 3, 1, "Industrial", 6, 50, D) == "Industrial" && ConduitStyles.SpanLook("Industrial", 6, 50, "Modern", 3, 1, D) == "Industrial",
                  "span (replaces stage 1's older-pole rule): the larger run's look, whichever end asks");
            Check(ConduitStyles.SpanLook("Modern", 3, 1, "Industrial", 6, 50, D) != "Modern", "can fail: the stage-1 older-pole rule would draw this span Modern");
        }
    }
}
