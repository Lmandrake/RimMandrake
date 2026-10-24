// HOSE_DRAW_FIX_LEAKS_ONTO_WORLDMAP (owner 2026-10-23: "when I look at the worldmap, the hoses from the tile map show anyway!!!").
// A map component's MapComponentUpdate keeps running while the planet is shown and Find.CurrentMap stays the tile map, so a
// Graphics.DrawMesh reached from it draws over the globe. Static rule over every FlowWorks source file: a MapComponentUpdate /
// MapComponentOnGUI body that draws (DrawMesh, or a Draw* call) must skip the world view (WorldRendererUtility.WorldRendered,
// WorldSelected or DrawingMap). Sanity probe: the rule must see the hose component's and the suspension bridges' draw calls.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class WorldMapDrawGuardChecks
    {
        private static readonly Regex Head = new Regex(@"override\s+void\s+(MapComponentUpdate|MapComponentOnGUI)\s*\(\s*\)");
        private static readonly Regex Draws = new Regex(@"\bGraphics\.DrawMesh|\bDraw[A-Z]\w*\s*\(");
        private static readonly Regex Guard = new Regex(@"WorldRendererUtility\.(WorldRendered|WorldSelected|DrawingMap)");

        /// <summary>The body of the method whose header ends at <paramref name="at"/> (brace matched; comments and strings are
        /// not special-cased, which the FlowWorks bodies do not need).</summary>
        internal static string Body(string src, int at)
        {
            int open = src.IndexOf('{', at);
            if (open < 0) return "";
            int depth = 0;
            for (int i = open; i < src.Length; i++)
            {
                if (src[i] == '{') depth++;
                else if (src[i] == '}' && --depth == 0) return src.Substring(open, i - open + 1);
            }
            return src.Substring(open);
        }

        /// <summary>Every (file, method, draws, guarded) over the FlowWorks source tree.</summary>
        internal static List<(string file, string method, bool draws, bool guarded)> Scan()
        {
            string root = Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath(Path.Combine("Hose", "RM_MapComponent_Hoses.cs")));
            root = Directory.GetParent(root).FullName;
            var o = new List<(string, string, bool, bool)>();
            foreach (string f in Directory.EnumerateFiles(root, "*.cs", SearchOption.AllDirectories))
            {
                string rel = f.Substring(root.Length + 1).Replace('\\', '/');
                if (rel.StartsWith("SelfTest/") || rel.StartsWith("obj/") || rel.StartsWith("bin/") || rel.Contains("/obj/") || rel.Contains("/bin/")) continue;
                string src = File.ReadAllText(f);
                foreach (Match m in Head.Matches(src))
                {
                    string body = Body(src, m.Index + m.Length);
                    o.Add((rel, m.Groups[1].Value, Draws.IsMatch(body), Guard.IsMatch(body)));
                }
            }
            return o;
        }

        internal static void Run(Action<string, Action> Case)
        {
            var all = Scan();
            Case("WorldMapDrawGuard sees the hose and suspension draw updates (sanity probe)", () =>
            {
                foreach (string want in new[] { "Hose/RM_MapComponent_Hoses.cs", "Pits/Suspension/RM_MapComponent_SuspensionBridges.cs" })
                    if (!all.Any(e => e.file == want && e.draws))
                        throw new Exception("the scan does not see a drawing update in " + want + " (" + all.Count + " updates scanned)");
            });
            Case("WorldMapDrawGuard every drawing MapComponentUpdate/OnGUI skips the world view", () =>
            {
                var bad = all.Where(e => e.draws && !e.guarded).Select(e => e.file + ":" + e.method).ToList();
                if (bad.Count > 0) throw new Exception("draws over the planet: " + string.Join(", ", bad));
            });
        }
    }
}
