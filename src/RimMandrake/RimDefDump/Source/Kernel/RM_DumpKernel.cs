using System;
using System.Collections.Generic;
using System.Text;

namespace RimMandrake.RimDefDump
{
    // Engine-free decisions of the def dump: which directory names are captures, which captures retention drops, how a def type becomes a unique
    // file stem. DefDumper calls these; the seeded fuzz under Source/SelfTest compiles THIS file and JsonWriter.cs directly (no `using Verse;`).
    public static class RM_DumpKernel
    {
        public const int KeepNewest = 3;
        public const int CaptureIdLength = 20;

        /// <summary>yyyy-MM-ddTHH-mm-ssZ, and nothing else. Must agree EXACTLY with `game_paths.captures()`'s anchored pattern: a directory this
        /// rejects is invisible to every reader.</summary>
        public static bool IsCaptureId(string name)
        {
            if (name == null || name.Length != CaptureIdLength) return false;
            for (int i = 0; i < CaptureIdLength; i++)
            {
                char c = name[i];
                if (i == 4 || i == 7 || i == 13 || i == 16) { if (c != '-') return false; }
                else if (i == 10) { if (c != 'T') return false; }
                else if (i == 19) { if (c != 'Z') return false; }
                else if (c < '0' || c > '9') return false;
            }
            return true;
        }

        /// <summary>The captures retention deletes, oldest first: keep the newest `keepNewest` UNFROZEN captures. Frozen ones (holding the keep
        /// marker) and non-capture names are never chosen and never count. The id is fixed-width ISO-8601, so ordinal order is chronological.</summary>
        public static List<string> PruneVictims(IEnumerable<KeyValuePair<string, bool>> dirsWithFrozenFlag, int keepNewest)
        {
            var ids = new List<string>();
            foreach (var d in dirsWithFrozenFlag)
            {
                if (!IsCaptureId(d.Key)) continue;
                if (d.Value) continue;
                ids.Add(d.Key);
            }
            ids.Sort(StringComparer.Ordinal);
            var victims = new List<string>();
            int drop = ids.Count - keepNewest;
            for (int i = 0; i < drop; i++) victims.Add(ids[i]);
            return victims;
        }

        /// <summary>A type's full name is legal in a filename here (dots are fine), but nested types use '+' and generics use '`'.</summary>
        public static string SafeFileName(string s)
        {
            var sb = new StringBuilder(s.Length);
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                sb.Append(char.IsLetterOrDigit(c) || c == '.' || c == '_' || c == '-' ? c : '_');
            }
            return sb.ToString();
        }

        /// <summary>Claims a unique file stem in `assigned` (a CASE-INSENSITIVE set). The stem is returned untouched in the ordinary case; a clash gets
        /// an assembly suffix, then a counter, never an existing stem.</summary>
        public static string ReserveStem(HashSet<string> assigned, string stem, string assemblyName, out bool clashed)
        {
            clashed = false;
            if (assigned.Add(stem)) return stem;
            clashed = true;
            string asm = SafeFileName(assemblyName);
            string candidate = stem + "__" + asm;
            for (int i = 2; !assigned.Add(candidate); i++) candidate = stem + "__" + asm + "_" + i;
            return candidate;
        }
    }
}
