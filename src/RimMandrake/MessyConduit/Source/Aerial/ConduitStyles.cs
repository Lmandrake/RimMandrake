// Verse-free (the SelfTest compiles this file): the per-build style rules of STAGE 2, conduit runs
// (design/RimMandrake/messyconduit_style_per_build_design.md section 2, owner decisions 2026-10-04).
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.MessyConduit.Aerial
{
    /// <summary>
    /// Stage 2: a RUN is a connected group of conduit cells, power switches and the poles / wall brackets wired into them
    /// (same cell or a cardinal neighbour), together with the overhead spans between those anchors. One run, one style.
    /// The style is stored on every member in the engine's own style field (ThingStyleDefs in Defs/Aerial/RM_ConduitStyles.xml,
    /// "markers" with no graphic for conduit); the run itself is never stored, it is worked out from the map.
    ///
    /// Owner decisions 2026-10-04: a piece bridging two runs -> the run with the MOST conduit cells wins and the smaller
    /// run is repainted, tie -> the older run (lowest member thing id); a free "Restyle this run" repaints a whole run;
    /// the Modern cord colour is picked per run in the build menu: one entry per colour, "multicolour" (one random colour
    /// per run, the look the old Mixed setting drew) and "random mix" (a MIXTURE of colours inside the run). Card
    /// CORD_COLOUR_PER_PIECE_1: the colour is stored per cord piece (the conduit cell's style def carries it; a mix run's
    /// cells carry the Mix marker; each cord piece of it, node to node, is one colour, varying piece to piece -- round 5),
    /// a merge keeps the larger run's.
    /// </summary>
    public static class ConduitStyles
    {
        /// <summary>Conduit defs styled in stage 2 (WaterproofConduit inherits the comp from PowerConduit).</summary>
        public static readonly string[] ConduitDefs = { "PowerConduit", "WaterproofConduit" };
        public static readonly string[] SwitchDefs = { "PowerSwitch" };

        /// <summary>Modern (extension cord) colours, in CordMaterials' strand order.</summary>
        public static readonly string[] Colours = { "Orange", "Green", "Brown", "Yellow", "Blue" };
        /// <summary>Industrial (Star Wars) cable kinds, in CordMaterials' strand order; picked per cord net (weights 6/2/2).</summary>
        public static readonly string[] IndustrialKinds = { "BlackRubber", "CorrugatedSteel", "CoiledBlack" };
        private static readonly int[] IndustrialWeights = { 6, 2, 2 };

        /// <summary>A mix run: the cells carry this marker; each cell's colour is a hash of its position.</summary>
        public const string Mix = "Mix";
        /// <summary>Menu-only: "one colour per run" (the old Mixed setting). It never reaches a building: the getter
        /// resolves it to a concrete colour and the adopt rule makes the run uniform.</summary>
        public const string Multi = "Multi";

        public static bool IsConduitDef(string d) => d != null && Array.IndexOf(ConduitDefs, d) >= 0;
        public static bool IsSwitchDef(string d) => d != null && Array.IndexOf(SwitchDefs, d) >= 0;
        public static bool IsColour(string c) => c != null && Array.IndexOf(Colours, c) >= 0;

        // ------------------------------------------------------------------ naming
        /// <summary>A style key is "Look" or, for Modern conduit, "Modern_Colour" / "Modern_Mix".</summary>
        public static string Key(string look, string colour) => colour == null ? look : look + "_" + colour;

        /// <summary>The ThingStyleDef defName: "PowerConduit_Industrial", "PowerConduit_Modern_Orange", "PowerSwitch_Modern".</summary>
        public static string StyleDefName(string def, string look, string colour = null) => def + "_" + Key(look, colour);

        /// <summary>Every style key a def carries: 4 looks for a switch; for conduit also the 5 colours and Mix
        /// ("Modern" alone = a Modern run whose colour was never stored: drawn like legacy, by the default colour mode).</summary>
        public static List<string> KeysFor(string def)
        {
            var l = new List<string>();
            foreach (string look in AerialStyles.Looks)
            {
                l.Add(look);
                if (look == "Modern" && IsConduitDef(def))
                {
                    foreach (string c in Colours) l.Add(Key(look, c));
                    l.Add(Key(look, Mix));
                }
            }
            return l;
        }

        public static IEnumerable<string> AllStyleDefNames()
        {
            foreach (string d in ConduitDefs) foreach (string k in KeysFor(d)) yield return d + "_" + k;
            foreach (string d in SwitchDefs) foreach (string k in KeysFor(d)) yield return d + "_" + k;
        }

        /// <summary>Split a key into look and colour (colour null for a plain look). False for anything not a key.</summary>
        public static bool TryParseKey(string key, out string look, out string colour)
        {
            look = null; colour = null;
            if (string.IsNullOrEmpty(key)) return false;
            if (AerialStyles.IsLook(key)) { look = key; return true; }
            int i = key.IndexOf('_');
            if (i <= 0) return false;
            string l = key.Substring(0, i), c = key.Substring(i + 1);
            if (l != "Modern" || !(IsColour(c) || c == Mix)) return false;
            look = l; colour = c;
            return true;
        }

        /// <summary>Parse one of OUR style defNames back to (def, look, colour). False for any other name.</summary>
        public static bool TryParseStyleDefName(string name, out string def, out string look, out string colour)
        {
            def = look = colour = null;
            if (string.IsNullOrEmpty(name)) return false;
            foreach (string d in ConduitDefs) if (TryDef(name, d, ref def, ref look, ref colour)) return true;
            foreach (string d in SwitchDefs) if (TryDef(name, d, ref def, ref look, ref colour)) return true;
            return false;
        }

        private static bool TryDef(string name, string d, ref string def, ref string look, ref string colour)
        {
            if (!name.StartsWith(d + "_", StringComparison.Ordinal)) return false;
            string key = name.Substring(d.Length + 1);
            if (!TryParseKey(key, out string l, out string c) || !KeysFor(d).Contains(key)) return false;
            def = d; look = l; colour = c;
            return true;
        }

        // ------------------------------------------------------------------ runs (pure graph)
        /// <summary>Connected components over the given ids, flood-filled through nbrs (ids not in the set are ignored).
        /// Deterministic: components are ordered by their smallest id, members ascending.</summary>
        public static List<List<int>> Components(IEnumerable<int> ids, Func<int, IEnumerable<int>> nbrs)
        {
            var set = new HashSet<int>(ids);
            var seen = new HashSet<int>();
            var res = new List<List<int>>();
            var order = new List<int>(set);
            order.Sort();
            foreach (int s in order)
            {
                if (seen.Contains(s)) continue;
                var comp = new List<int>();
                var stack = new Stack<int>();
                stack.Push(s);
                seen.Add(s);
                while (stack.Count > 0)
                {
                    int x = stack.Pop();
                    comp.Add(x);
                    foreach (int n in nbrs(x))
                        if (set.Contains(n) && seen.Add(n)) stack.Push(n);
                }
                comp.Sort();
                res.Add(comp);
            }
            return res;
        }

        /// <summary>One run as the rules see it.</summary>
        public sealed class Run
        {
            /// <summary>Number of conduit cells (the owner's "area"; switches and poles do not count).</summary>
            public int Area;
            /// <summary>Its oldest member's thing id (the tie-break: older wins).</summary>
            public int Oldest;
            /// <summary>Its look; null = legacy (no member stores a style).</summary>
            public string Look;
            /// <summary>Its Modern colour mode over its conduit cells: a colour (uniform), Mix, or null (never stored).</summary>
            public string Colour;
            public object Tag;
        }

        /// <summary>The run whose style survives a bridge (owner 2026-10-04): the most conduit cells; a tie goes to the older
        /// run (lowest member id). Returns the index into runs, -1 for none.</summary>
        public static int Winner(IList<Run> runs)
        {
            int best = -1;
            for (int i = 0; i < runs.Count; i++)
            {
                if (best < 0) { best = i; continue; }
                Run a = runs[i], b = runs[best];
                if (a.Area > b.Area || (a.Area == b.Area && a.Oldest < b.Oldest)) best = i;
            }
            return best;
        }

        /// <summary>The colour mode of a run from its conduit cells' stored colours (null entries = Modern with no colour).
        /// All the same colour -> that colour; any Mix, or two colours -> Mix; none stored -> null.</summary>
        public static string RunColour(IEnumerable<string> cellColours)
        {
            string one = null;
            bool any = false;
            foreach (string c in cellColours)
            {
                if (c == null) continue;
                if (c == Mix) return Mix;
                if (!any) { one = c; any = true; }
                else if (c != one) return Mix;
            }
            return one;
        }

        /// <summary>What one member is painted with when its run takes (look, colour mode): conduit keeps the colour mode
        /// (a concrete colour, Mix, or none); a switch or pole carries only the look.</summary>
        public static string KeyForMember(bool isConduit, string look, string colourMode) =>
            Key(look, isConduit && look == "Modern" && (IsColour(colourMode) || colourMode == Mix) ? colourMode : null);

        /// <summary>The placement plan for a new member touching zero or more existing runs (design 2.3).</summary>
        public sealed class Plan
        {
            /// <summary>The look / colour mode the new member and every repainted run end with; Look null = leave legacy.</summary>
            public string Look, Colour;
            /// <summary>Index of the winning run (-1: none).</summary>
            public int Winner = -1;
            /// <summary>Indices of runs to repaint to (Look, Colour).</summary>
            public readonly List<int> Repaint = new List<int>();
            /// <summary>The winner is legacy: the run ends in the default look with no stored colour (its own members stay
            /// unwritten, NeedsWrite; a Modern loser stores plain "Modern" and draws the winner's per-net colour).</summary>
            public bool MaterialiseWinner;
            /// <summary>Two different styles met (the player gets a message naming both).</summary>
            public bool StylesDiffered;
            public string LoserLook;
        }

        /// <summary>
        /// The rule a newly placed member runs once (design 2.3 + owner decisions):
        ///   * no neighbouring run: it keeps the style it was built with (none stays none = drawn in the default look);
        ///   * one run: it adopts that run's style whatever the button said;
        ///   * several runs: the largest wins (tie: older), every other run is repainted to it.
        /// A legacy run (nothing stored) counts as the default look it draws; an unstyled piece (another mod, a quest) joining
        /// only legacy runs writes nothing. Which members are actually written is NeedsWrite's call.
        /// </summary>
        public static Plan PlanPlacement(string ownLook, string ownColour, IList<Run> runs, string defaultLook)
        {
            var p = new Plan();
            if (runs == null || runs.Count == 0) { p.Look = ownLook; p.Colour = ownColour; return p; }
            int w = Winner(runs);
            p.Winner = w;
            Run win = runs[w];
            bool anyStyled = ownLook != null;
            foreach (Run r in runs) anyStyled |= r.Look != null;
            if (!anyStyled) return p;                       // all legacy + an unstyled piece: nothing is written
            if (win.Look == null)
            {
                p.MaterialiseWinner = true;
                p.Look = defaultLook;
                p.Colour = null;                            // no stored colour: the default colour setting draws it
            }
            else { p.Look = win.Look; p.Colour = win.Colour; }
            for (int i = 0; i < runs.Count; i++)
            {
                if (i == w) continue;
                Run r = runs[i];
                string rl = r.Look ?? defaultLook;
                if (rl != p.Look) { p.StylesDiffered = true; p.LoserLook = p.LoserLook ?? rl; }
                p.Repaint.Add(i);
            }
            return p;
        }

        /// <summary>A linked span between two anchors already in runs a and b (a manual link, or a restring): the same
        /// bridge rule. Returns 0 if a wins, 1 if b wins.</summary>
        public static int LinkWinner(Run a, Run b) => Winner(new List<Run> { a, b });

        /// <summary>The look a span between two anchors draws in (replaces stage 1's "older pole" stand-in): the run with the
        /// most conduit cells wins, a tie goes to the older (lower id). The rules keep a run uniform, so this only decides a
        /// span whose ends have not been resolved yet (the frame between a link and its run check). Symmetric.</summary>
        public static string SpanLook(string lookA, int areaA, int idA, string lookB, int areaB, int idB, string defaultLook)
        {
            string a = AerialStyles.IsLook(lookA) ? lookA : defaultLook, b = AerialStyles.IsLook(lookB) ? lookB : defaultLook;
            if (a == b) return a;
            if (areaA != areaB) return areaA > areaB ? a : b;
            return idA <= idB ? a : b;
        }

        // ------------------------------------------------------------------ colours and materials
        public static int ColourIndex(string c) => Array.IndexOf(Colours, c);

        /// <summary>
        /// Round 5 (owner 2026-10-04, station 5: "the multi-color should not have the colors change randomly along their length.
        /// Each run from one node to another stays a single color, but it varies through the whole nodal array"): the round-4
        /// 3x3-block colour change ALONG a cord is reverted. Every cord piece of a Modern "random mix" run (one node to the next)
        /// is ONE colour, and the colours vary piece to piece. Input: each mix piece's key (stable, from its geometry) and the
        /// node tokens it touches ("x,z"). Pieces are coloured in ordinal key order: a piece starts at a hash of its key and
        /// steps to the first colour no already-coloured piece sharing one of its nodes has, so neighbouring pieces differ
        /// wherever the 5 colours allow. Pure function of the stored cells (the pieces are rebuilt identically from them), so
        /// it survives save/load and never flickers.
        /// </summary>
        public static Dictionary<string, int> MixPieceColours(IEnumerable<KeyValuePair<string, string[]>> pieces)
        {
            var list = pieces.Where(kv => kv.Key != null).GroupBy(kv => kv.Key).Select(gr => gr.First()).OrderBy(kv => kv.Key, StringComparer.Ordinal).ToList();
            var res = new Dictionary<string, int>();
            var atNode = new Dictionary<string, List<int>>();
            int n = Colours.Length;
            foreach (KeyValuePair<string, string[]> kv in list)
            {
                var taken = new HashSet<int>();
                string[] nodes = kv.Value ?? new string[0];
                foreach (string t in nodes)
                    if (t != null && atNode.TryGetValue(t, out List<int> l)) foreach (int c in l) taken.Add(c);
                uint h = 2166136261u;
                foreach (char ch in kv.Key) h = unchecked((h ^ ch) * 16777619u);
                int start = (int)(h % (uint)n), pick = start;
                for (int k = 0; k < n; k++) { int c = (start + k) % n; if (!taken.Contains(c)) { pick = c; break; } }
                res[kv.Key] = pick;
                foreach (string t in nodes.Where(x => x != null).Distinct())
                {
                    if (!atNode.TryGetValue(t, out List<int> l)) atNode[t] = l = new List<int>();
                    l.Add(pick);
                }
            }
            return res;
        }

        /// <summary>A mix cell's colour before its piece is known (a fixed hash of the position): only a fallback, the
        /// cord graph replaces it per piece with <see cref="MixPieceColours"/>.</summary>
        public static int MixCellColour(int x, int z)
        {
            uint h = unchecked((uint)(x * 73856093) ^ (uint)(z * 19349663));
            return (int)(h % (uint)Colours.Length);
        }

        /// <summary>
        /// Minimal writes (live 2026-10-04, S8/S7: an unstyled mast auto-linked to a Scrapper run got Scrapper WRITTEN, so an
        /// older save's anchors changed): a member with no stored style is written only when what it draws would change --
        /// its run takes a look other than the default, or a Modern conduit cell takes a stored colour or the mix -- or when
        /// the player restyles the run (force). Otherwise it keeps drawing the default, storing nothing.
        /// </summary>
        public static bool NeedsWrite(bool hasStyle, bool isConduit, string look, string colourMode, string defaultLook, bool force)
        {
            if (force || hasStyle) return true;
            if (look != defaultLook) return true;
            return isConduit && look == "Modern" && (IsColour(colourMode) || colourMode == Mix);
        }

        /// <summary>The number of strand variants a look draws with (all of them, whatever the colour setting).</summary>
        public static int VariantsOf(string look)
        {
            switch (look)
            {
                case "Industrial": return IndustrialKinds.Length;
                case "Modern": return Colours.Length;
                default: return 1;
            }
        }

        /// <summary>The flat material index of (look, variant): looks in menu order, each look's variants in a block.</summary>
        public static int Global(string look, int variant)
        {
            int off = 0;
            foreach (string l in AerialStyles.Looks)
            {
                int n = VariantsOf(l);
                if (l == look) return off + Math.Max(0, Math.Min(n - 1, variant));
                off += n;
            }
            return 0;
        }

        public static int GlobalCount
        {
            get { int n = 0; foreach (string l in AerialStyles.Looks) n += VariantsOf(l); return n; }
        }

        /// <summary>(look, variant) of a flat index; the inverse of <see cref="Global"/>.</summary>
        public static void FromGlobal(int g, out string look, out int variant)
        {
            int off = 0;
            foreach (string l in AerialStyles.Looks)
            {
                int n = VariantsOf(l);
                if (g < off + n) { look = l; variant = g - off; return; }
                off += n;
            }
            look = AerialStyles.Looks[0]; variant = 0;
        }

        /// <summary>
        /// The pre-stage-2 per-net pick (CordMaterials.VariantFor before this stage, unchanged): the strand a LEGACY piece
        /// of this look drew, from its cord net's seed. Modern: the single setting colour, or uniform over the colours;
        /// Industrial: weighted 6/2/2 over the cable kinds; others: their one strand. Returned as the look's variant index.
        /// </summary>
        public static int LegacyVariant(string look, int netSeed, bool singleColour, int singleIndex)
        {
            if (look == "Modern" && singleColour) return Math.Max(0, Math.Min(Colours.Length - 1, singleIndex));
            int n = VariantsOf(look);
            if (n <= 1) return 0;
            uint h = unchecked((uint)netSeed * 2654435761u);
            h ^= h >> 15;
            if (look == "Industrial")
            {
                int r = (int)(h % 10u), acc = 0;
                for (int i = 0; i < n; i++) { acc += IndustrialWeights[i]; if (r < acc) return i; }
                return 0;
            }
            return (int)(h % (uint)n);
        }

        /// <summary>
        /// The strand variant one cord piece draws with, from the style of the conduit cell it is coloured by:
        ///   * Modern: the stored colour; a Mix piece's own colour (MixPieceColours; the cell hash only as a fallback); no stored colour (legacy or plain "Modern") -> the
        ///     legacy per-net pick under the default colour setting, exactly what it drew before stage 2;
        ///   * Industrial: the cable kind stays a per-cord-net pick (the owner chose colour per run for Modern only);
        ///   * Scrapper / Futuristic: their one strand.
        /// </summary>
        public static int PieceVariant(string look, string colour, int x, int z, int netSeed, bool singleColour, int singleIndex)
        {
            if (look == "Modern")
            {
                if (IsColour(colour)) return ColourIndex(colour);
                if (colour == Mix) return MixCellColour(x, z);
            }
            return LegacyVariant(look, netSeed, singleColour, singleIndex);
        }
    }
}
