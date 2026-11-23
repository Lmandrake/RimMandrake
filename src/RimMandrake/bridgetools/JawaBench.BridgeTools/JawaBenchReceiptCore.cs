// JawaBenchReceiptCore.cs - the PURE half of the loaded-build receipt (no Verse, no Unity, no Harmony).
// Page: design/specs/2026-11-23-loaded-receipt/boundary.md. Compiled into bridgetools/LiveToolsSelfTest too: a
// `using Verse;` here breaks that build. rimflow/loaded_build.py holds the Python twin of Fingerprint and HoldsMvid.
using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchReceiptCore
    {
        internal const string Loaded = "LOADED", FileChanged = "FILE_CHANGED", DllNotLoaded = "DLL_NOT_LOADED",
                              ForeignCopy = "FOREIGN_COPY", NoAssembly = "NO_ASSEMBLY", CouldNotRead = "COULD_NOT_READ";

        /// <summary>A packageId as every list compare here reads it: lower case, without RimWorld's `_steam` suffix.</summary>
        internal static string NormId(string id)
        {
            var p = (id ?? "").Trim().ToLowerInvariant();
            return p.EndsWith("_steam", StringComparison.Ordinal) ? p.Substring(0, p.Length - 6) : p;
        }

        /// <summary>sha256 over the normalised ids, one per line, in load order. Equal to loaded_build.fingerprint.</summary>
        internal static string Fingerprint(IEnumerable<string> ids)
        {
            var sb = new StringBuilder();
            foreach (var id in ids) sb.Append(NormId(id)).Append('\n');
            using (var h = SHA256.Create())
                return "sha256:" + Hex(h.ComputeHash(Encoding.UTF8.GetBytes(sb.ToString())));
        }

        internal static string Hex(byte[] b)
        {
            var sb = new StringBuilder(b.Length * 2);
            foreach (var x in b) sb.Append(x.ToString("x2"));
            return sb.ToString();
        }

        /// <summary>The bridge key of this game ("archmagi", "archmagi.b"), from the machine name and the two folders the
        /// game itself uses: game_instance.py's rule, the last two parts of the data folder, or an own install
        /// instances/letter/game. null when the machine name is unknown: never a default game.</summary>
        internal static string GameKey(string machine, string dataFolder, string installFolder)
        {
            var m = (machine ?? "").Trim().ToLowerInvariant();
            if (m.Length == 0) return null;
            var letter = InstanceLetter(dataFolder, 1) ?? InstanceLetter(installFolder, 2);
            return letter == null || letter == "a" ? m : m + "." + letter;
        }

        private static string InstanceLetter(string folder, int fromEnd)
        {
            if (string.IsNullOrEmpty(folder)) return null;
            var parts = folder.Replace('\\', '/').TrimEnd('/').ToLowerInvariant().Split('/');
            int i = parts.Length - fromEnd;
            if (i < 1 || parts[i - 1] != "instances" || parts[i].Length != 1 || parts[i][0] < 'a' || parts[i][0] > 'z') return null;
            if (fromEnd == 2 && parts[i + 1] != "game") return null;
            return parts[i];
        }

        /// <summary>Does this DLL file hold the module id of the loaded code? The id sits in the file's GUID heap as its 16
        /// bytes. null = could not read (no bytes or no id), never false.</summary>
        internal static bool? HoldsMvid(byte[] file, Guid mvid)
        {
            if (file == null || file.Length == 0 || mvid == Guid.Empty) return null;
            var want = mvid.ToByteArray();
            for (int i = 0; i + 16 <= file.Length; i++)
            {
                if (file[i] != want[0]) continue;
                int j = 1;
                while (j < 16 && file[i + j] == want[j]) j++;
                if (j == 16) return true;
            }
            return false;
        }

        internal sealed class AsmFact
        {
            internal string Name, Location;
            internal bool? FileHoldsLoaded;      // null: the file or the loaded id could not be read
        }

        /// <summary>The state of one mod, the first fault named. LOADED only when every DLL file of the mod is loaded from the
        /// mod's own folder and still holds the loaded code. dllFiles null = the mod's DLL list could not be read.</summary>
        internal static string JudgeMod(string folder, ICollection<string> dllFiles, ICollection<AsmFact> asms, out string why)
        {
            why = null;
            if (dllFiles == null || asms == null) { why = "the mod's DLL files or loaded assemblies could not be read"; return CouldNotRead; }
            if (dllFiles.Count == 0 && asms.Count == 0) { why = "the mod ships no DLL: its code cannot be identified"; return NoAssembly; }
            string root = Norm(folder);
            foreach (var a in asms)
            {
                if (string.IsNullOrEmpty(a.Location)) { why = a.Name + " has no file location"; return CouldNotRead; }
                if (root.Length == 0) { why = "the mod's folder is unknown"; return CouldNotRead; }
                if (!Norm(a.Location).StartsWith(root + "/", StringComparison.Ordinal))
                { why = a.Name + " was loaded from " + a.Location + ", outside " + folder; return ForeignCopy; }
            }
            var have = new HashSet<string>();
            foreach (var a in asms) have.Add(Norm(a.Location));
            foreach (var f in dllFiles)
                if (!have.Contains(Norm(f))) { why = f + " is in the mod and is not loaded"; return DllNotLoaded; }
            foreach (var a in asms)
            {
                if (a.FileHoldsLoaded == null) { why = a.Name + ": its file or its loaded id could not be read"; return CouldNotRead; }
                if (a.FileHoldsLoaded == false) { why = a.Name + ": the file on disk is not the code that is loaded"; return FileChanged; }
            }
            return Loaded;
        }

        private static string Norm(string p) => (p ?? "").Replace('\\', '/').TrimEnd('/').ToLowerInvariant();
    }
}
