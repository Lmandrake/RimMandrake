// Gimme Some Slack core: Verse-free (see CordMath.cs header).
using System;
using System.IO;

namespace RimMandrake.GimmeSomeSlack.Core
{
    /// <summary>RIMMANDRAKE_TRACE_GSS_ILLEGAL_PATH_ONLY_ON_FIRST_START: "System.ArgumentException: Illegal characters in path" out of
    /// Verse.ContentFinder.TryFindAssetInModBundles (Path.Combine), with a frame of this mod in the stack, on one start in two and never
    /// since; which call handed it the path was never seen. Every texture this mod asks for by a path it builds goes through
    /// <see cref="SafeTex"/> now: a path no file system takes is refused here, where its text and the caller can be named, and never
    /// reaches Path.Combine.</summary>
    public static class TexPath
    {
        /// <summary>The first character of <paramref name="path"/> no path may hold (a control character, a quote, an angle bracket, a
        /// bar: Path.GetInvalidPathChars), or -1; -2 for no path at all.</summary>
        public static int BadAt(string path)
        {
            if (string.IsNullOrEmpty(path)) return -2;
            return path.IndexOfAny(Invalid);
        }

        /// <summary>The path for a log line: every character outside plain print shown by its code, so a NUL or a tab can be read.</summary>
        public static string Shown(string path)
        {
            if (path == null) return "(null)";
            var sb = new System.Text.StringBuilder(path.Length + 8);
            foreach (char c in path) sb.Append(c < 0x20 || c == 0x7f ? "\\u" + ((int)c).ToString("x4") : c.ToString());
            return sb.ToString();
        }

        // Path.GetInvalidPathChars differs by platform (Mono on Windows: the control characters, " < > |): the union, fixed here, so
        // the check reads the same under the selftest and in the game
        private static readonly char[] Invalid = BuildInvalid();

        private static char[] BuildInvalid()
        {
            var l = new System.Collections.Generic.List<char> { '"', '<', '>', '|' };
            for (int c = 0; c < 0x20; c++) l.Add((char)c);
            foreach (char c in Path.GetInvalidPathChars()) if (!l.Contains(c)) l.Add(c);
            return l.ToArray();
        }
    }
}
