// JawaBenchStartFlowCore.cs - the Verse-free decisions behind the new-game start-flow tools
// (JawaBenchStartFlowTools.cs): which scenario a caller's string names, which file a .rid
// argument names, and which of several candidate start tiles to take.
//
// Kept free of RimWorld/Unity references ON PURPOSE: bridgetools/StartFlowSelfTest compiles
// THIS production file into a plain net8.0 harness (src/RimMandrake/Utils/selftest_start_flow_core.py),
// so a `using Verse;` here breaks that build - the guard rail working.
//
// Why each decision refuses rather than guesses: these tools run UNATTENDED in the world-remake
// conductor (design/RimMandrake/world_remake_2026-10-19/15_conductor_plan.md S4/S5/S10). A fuzzy
// scenario pick or a silently-substituted tile produces a world that looks right and is wrong.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;

namespace JawaBench.BridgeTools
{
    public static class JawaBenchStartFlowCore
    {
        // ---------------------------------------------------------------- scenarios

        public sealed class ScenarioEntry
        {
            public string DefName;   // null for a custom/workshop scenario (no def)
            public string Name;      // Scenario.name as the list shows it
            public string Category;  // ScenarioCategory as text
            public ScenarioEntry(string defName, string name, string category)
            { DefName = defName; Name = name; Category = category; }
        }

        /// <summary>
        /// Index into <paramref name="entries"/> of the scenario <paramref name="query"/> names, or -1
        /// with <paramref name="error"/> set. Order: exact defName (ordinal, case-SENSITIVE as defNames
        /// are), then exact display name (case-insensitive). Two entries matching at the same rung is
        /// AMBIGUOUS and refused. No substring pick: substring hits are only offered as suggestions.
        /// </summary>
        public static int MatchScenario(IList<ScenarioEntry> entries, string query, out string error)
        {
            error = null;
            if (string.IsNullOrWhiteSpace(query)) { error = "scenario is required (a ScenarioDef defName or the exact scenario name)."; return -1; }
            if (entries == null || entries.Count == 0) { error = "the scenario list is EMPTY - the instrument cannot see any scenario."; return -1; }
            string q = query.Trim();

            var byDef = new List<int>();
            for (int i = 0; i < entries.Count; i++)
                if (entries[i].DefName != null && string.Equals(entries[i].DefName, q, StringComparison.Ordinal)) byDef.Add(i);
            if (byDef.Count == 1) return byDef[0];
            if (byDef.Count > 1) { error = "AMBIGUOUS: " + byDef.Count + " scenarios share defName '" + q + "'."; return -1; }

            var byName = new List<int>();
            for (int i = 0; i < entries.Count; i++)
                if (entries[i].Name != null && string.Equals(entries[i].Name.Trim(), q, StringComparison.OrdinalIgnoreCase)) byName.Add(i);
            if (byName.Count == 1) return byName[0];
            if (byName.Count > 1)
            {
                error = "AMBIGUOUS: " + byName.Count + " scenarios are named '" + q + "' (" +
                        string.Join(", ", byName.Select(i => Describe(entries[i]))) + "). Pass the defName.";
                return -1;
            }

            var sugg = entries.Where(e => Contains(e.DefName, q) || Contains(e.Name, q)).Take(8).Select(Describe).ToList();
            error = "No scenario has defName or name '" + q + "'." +
                    (sugg.Count > 0 ? " Near: " + string.Join(", ", sugg) + "." : " (" + entries.Count + " listed; none contain that text.)");
            return -1;
        }

        private static bool Contains(string hay, string needle) =>
            hay != null && hay.IndexOf(needle, StringComparison.OrdinalIgnoreCase) >= 0;

        public static string Describe(ScenarioEntry e) =>
            (e.DefName ?? "(no def)") + " \"" + (e.Name ?? "") + "\" [" + (e.Category ?? "?") + "]";

        // ---------------------------------------------------------------- .rid paths

        /// <summary>
        /// The Windows path the GAME must open for a .rid argument, or null with <paramref name="error"/>.
        /// Accepts: an absolute Windows path (C:\..., D:/..., \\server\...); a WSL drvfs path
        /// (/mnt/d/... -> D:\...); or a bare ideo name ("The Salvation" / "The Salvation.rid"), which
        /// <paramref name="absPathForName"/> resolves in the game's own Ideos folder (the game's
        /// GenFilePaths.AbsPathForIdeo appends ".rid" itself). Refuses a non-drvfs WSL path (the
        /// Windows game cannot see it), a relative path with folders (ambiguous: relative to what?)
        /// and any extension other than .rid.
        /// </summary>
        public static string ResolveRidPath(string arg, Func<string, string> absPathForName, out string error)
        {
            error = null;
            if (string.IsNullOrWhiteSpace(arg)) { error = "path is required (an absolute Windows path to a .rid, a /mnt/<drive>/ path, or a bare ideo file name in the game's Ideos folder)."; return null; }
            string a = arg.Trim().Trim('"');

            if (a.StartsWith("/mnt/", StringComparison.Ordinal) && a.Length >= 7 && char.IsLetter(a[5]) && a[6] == '/')
                a = char.ToUpperInvariant(a[5]) + ":\\" + a.Substring(7).Replace('/', '\\');
            else if (a.StartsWith("/", StringComparison.Ordinal))
            { error = "'" + arg + "' is a Linux-only path; the Windows game cannot open it. Use a /mnt/<drive>/ or X:\\ path."; return null; }

            bool winAbs = (a.Length >= 3 && char.IsLetter(a[0]) && a[1] == ':' && (a[2] == '\\' || a[2] == '/')) || a.StartsWith("\\\\", StringComparison.Ordinal);
            if (winAbs)
            {
                a = a.Replace('/', '\\');
                if (!a.EndsWith(".rid", StringComparison.OrdinalIgnoreCase))
                { error = "'" + arg + "' is not a .rid file (an ideoligion file ends in .rid)."; return null; }
                return a;
            }

            if (a.IndexOf('\\') >= 0 || a.IndexOf('/') >= 0)
            { error = "'" + arg + "' is a relative path; pass an absolute path or a bare file name."; return null; }
            string name = a.EndsWith(".rid", StringComparison.OrdinalIgnoreCase) ? a.Substring(0, a.Length - 4) : a;
            int dot = name.LastIndexOf('.');
            if (dot >= 0)
            {
                // "foo.xml" style: a known foreign extension. A dot mid-name ("St. Kira") is fine.
                string ext = name.Substring(dot);
                if (ForeignExtensions.Contains(ext))
                { error = "'" + arg + "' has extension '" + ext + "', not .rid."; return null; }
            }
            if (name.Length == 0) { error = "empty ideo file name."; return null; }
            return absPathForName(name);
        }

        private static readonly HashSet<string> ForeignExtensions = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        { ".xml", ".rws", ".rsc", ".rsc2", ".txt", ".json", ".xtp", ".rpc", ".zip", ".png" };

        // ---------------------------------------------------------------- start tiles

        /// <summary>"17007, 1621 ,17011" -> [17007,1621,17011]; null with error on anything else.</summary>
        public static List<int> ParseTileList(string s, out string error)
        {
            error = null;
            if (string.IsNullOrWhiteSpace(s)) { error = "tiles is required (one surface tile id, or several comma-separated in preference order)."; return null; }
            var outList = new List<int>();
            foreach (var raw in s.Split(','))
            {
                string t = raw.Trim();
                if (!int.TryParse(t, NumberStyles.None, CultureInfo.InvariantCulture, out int v))
                { error = "'" + t + "' is not a non-negative tile id."; return null; }
                if (outList.Contains(v)) { error = "tile " + v + " is listed twice."; return null; }
                outList.Add(v);
            }
            return outList;
        }

        public sealed class TilePick
        {
            public int Chosen = -1;                                      // -1 = none acceptable
            public List<KeyValuePair<int, string>> Refused = new List<KeyValuePair<int, string>>();
        }

        /// <summary>
        /// First candidate whose <paramref name="refusal"/> is null. Every earlier candidate's
        /// reason is kept, so a caller can see WHY its first choice was skipped - never a silent
        /// substitution. Candidates after the chosen one are not evaluated.
        /// </summary>
        public static TilePick PickFirstAcceptable(IList<int> candidates, Func<int, string> refusal)
        {
            var pick = new TilePick();
            foreach (int c in candidates)
            {
                string why = refusal(c);
                if (why == null) { pick.Chosen = c; return pick; }
                pick.Refused.Add(new KeyValuePair<int, string>(c, why));
            }
            return pick;
        }

        /// <summary>
        /// Run <paramref name="write"/>, then re-run it while <paramref name="readBackOk"/> is false,
        /// at most <paramref name="maxAttempts"/> writes in all. Returns the number of writes made
        /// when the read-back agreed, or -attempts when it never did. Why it exists (world remake,
        /// 2026-10-20): after start_site_select skipped refused candidates, the selection read back
        /// -1 while GameInitData.startingTile held the chosen tile; a second write of the same tile
        /// read back fine. Root cause UNMEASURED; the tool now re-asserts and REPORTS the count, so
        /// a second write is visible, never silent.
        /// </summary>
        public static int WriteUntilReadBack(Action write, Func<bool> readBackOk, int maxAttempts = 3)
        {
            if (maxAttempts < 1) maxAttempts = 1;
            for (int i = 1; i <= maxAttempts; i++)
            {
                write();
                if (readBackOk()) return i;
            }
            return -maxAttempts;
        }
    }
}
